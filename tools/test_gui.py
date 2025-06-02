import sys
import subprocess
import serial.tools.list_ports

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Проверка и установка необходимых пакетов
try:
    import psutil
except ImportError:
    print("Установка пакета psutil...")
    install_package("psutil")
    import psutil

try:
    import serial
except ImportError:
    print("Установка пакета pyserial...")
    install_package("pyserial")
    import serial

import time

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    print("Установка пакета tkinter...")
    if sys.platform.startswith('win'):
        print("Для Windows tkinter обычно устанавливается с Python")
    else:
        install_package("python3-tk")
    import tkinter as tk
    from tkinter import ttk

import struct
import threading

# Константы протокола CRSF
CRSF_ADDRESS = 0xC8   # Адрес приемника
CRSF_TYPE_RC = 0x16   # Тип пакета (RC Channels)

# Доступные скорости
BAUD_RATES = [9600, 19200, 38400, 57600, 115200, 230400, 420000]

class CRSFTransmitter:
    def __init__(self):
        self.ser = None
        self.channels = [992] * 16  # Нейтральное положение (992 из 2047)
        self.connected = False
        self.last_packet = None  # Для отслеживания изменений
        self.temporarily_disconnected = False  # Флаг временного отключения
        self.last_port = None
        self.last_baud = None
        
    def connect(self, port, baud_rate):
        try:
            if self.ser:
                self.ser.close()
            self.ser = serial.Serial(port, baud_rate, timeout=1)
            self.connected = True
            self.temporarily_disconnected = False
            self.last_port = port
            self.last_baud = baud_rate
            return True
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            self.connected = False
            return False
            
    def disconnect(self):
        if self.ser:
            self.ser.close()
            self.ser = None
        self.connected = False
        self.temporarily_disconnected = False

    def temporarily_disconnect(self):
        """Временно освобождает порт"""
        if self.ser and self.connected:
            try:
                self.ser.close()
            except:
                pass
            self.ser = None
            self.temporarily_disconnected = True
            return True
        return False

    def reconnect(self):
        """Восстанавливает соединение после временного отключения"""
        if self.temporarily_disconnected and not self.ser and self.last_port and self.last_baud:
            try:
                self.ser = serial.Serial(self.last_port, self.last_baud, timeout=1)
                self.connected = True
                self.temporarily_disconnected = False
                return True
            except Exception as e:
                print(f"Ошибка переподключения: {e}")
                return False
        return False

    def pack_channels(self):
        channels = self.channels
        if len(channels) != 16:
            raise ValueError("Должно быть ровно 16 каналов")
        for ch in channels:
            if not (0 <= ch < 2048):
                raise ValueError(f"Значение канала {ch} выходит за диапазон 0..2047")

        bit_buffer = 0
        bits_in_buffer = 0
        payload = bytearray()

        for ch in channels:
            bit_buffer |= (ch << bits_in_buffer)
            bits_in_buffer += 11

            while bits_in_buffer >= 8:
                payload.append(bit_buffer & 0xFF)
                bit_buffer >>= 8
                bits_in_buffer -= 8

        # Остаток битов
        if bits_in_buffer > 0:
            payload.append(bit_buffer & 0xFF)

        # Убедимся, что длина ровно 22 байта
        while len(payload) < 22:
            payload.append(0)

        return payload

    def calculate_crc(self, data):
        """Вычисляет CRC8 для пакета"""
        crc = 0
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ 0xD5
                else:
                    crc = crc << 1
                crc &= 0xFF
        return crc

    def send_packet(self):
        """Формирует и отправляет CRSF пакет"""
        if not self.ser or not self.connected or self.temporarily_disconnected:
            return
            
        try:
            payload = self.pack_channels()
            # Длина пакета = длина payload + 2 (тип + CRC)
            length = len(payload) + 2
            header = bytes([CRSF_ADDRESS, length, CRSF_TYPE_RC])
            
            # Собираем пакет без CRC
            packet = header + payload
            
            # Добавляем CRC
            crc = self.calculate_crc(bytes([CRSF_TYPE_RC]) + payload)
            packet += bytes([crc])
            
            # Выводим пакет в консоль только если он изменился
            if packet != self.last_packet:
                print(f"Отправка пакета: {' '.join([f'{b:02X}' for b in packet])}")
                self.last_packet = packet
            
            # Отправка через UART
            if self.ser and self.ser.is_open:
                self.ser.write(packet)
        except Exception as e:
            print(f"Ошибка отправки пакета: {e}")
            self.connected = False
            self.ser = None

    def update_channel(self, channel, value):
        """Обновляет значение канала (0-15)"""
        self.channels[channel] = int(value)

class ControlApp:
    def __init__(self, master):
        self.master = master
        self.transmitter = CRSFTransmitter()
        master.title("CRSF Channel Controller")

        self.active_channels = 4  # Начальное количество каналов (по умолчанию 4)

        # --- Фрейм подключения ---
        connection_frame = tk.Frame(master)
        connection_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(connection_frame, text="Порт:").pack(side=tk.LEFT, padx=5)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(connection_frame, textvariable=self.port_var)
        self.port_combo.pack(side=tk.LEFT, padx=5)
        self.update_ports()

        tk.Label(connection_frame, text="Скорость:").pack(side=tk.LEFT, padx=5)
        self.baud_var = tk.StringVar(value=str(BAUD_RATES[4]))
        self.baud_combo = ttk.Combobox(connection_frame, textvariable=self.baud_var, values=BAUD_RATES)
        self.baud_combo.pack(side=tk.LEFT, padx=5)

        self.connect_button = tk.Button(connection_frame, text="Подключить", command=self.toggle_connection)
        self.connect_button.pack(side=tk.LEFT, padx=5)

        # Статус подключения
        self.status_label = tk.Label(connection_frame, text="")
        self.status_label.pack(side=tk.LEFT, padx=5)

        # --- Добавляем кнопки изменения количества каналов ---
        self.minus_button = tk.Button(connection_frame, text="-", command=self.decrease_channels, state=tk.DISABLED)
        self.minus_button.pack(side=tk.LEFT, padx=2)

        self.channel_count_label = tk.Label(connection_frame, text=str(self.active_channels))
        self.channel_count_label.pack(side=tk.LEFT, padx=2)

        self.plus_button = tk.Button(connection_frame, text="+", command=self.increase_channels, state=tk.DISABLED)
        self.plus_button.pack(side=tk.LEFT, padx=2)

        # --- Создаем 16 ползунков, но покажем только первые active_channels ---
        self.sliders = []
        self.labels = []
        self.sliders_frames = []

        for i in range(16):
            frame = tk.Frame(master)
            frame.pack(fill=tk.X, padx=10, pady=5)
            self.sliders_frames.append(frame)

            label = tk.Label(frame, text=f"Channel {i+1}: 992")
            label.pack(side=tk.LEFT, padx=5)
            self.labels.append(label)

            slider = tk.Scale(
                frame,
                from_=172,
                to=1811,
                orient=tk.HORIZONTAL,
                length=400,
                showvalue=False,
                command=lambda v, idx=i: self.on_slider_change(idx, v)
            )
            slider.set(992)
            slider.pack(fill=tk.X, expand=True)
            self.sliders.append(slider)

        self.update_sliders_visibility()

        # Старт потока отправки пакетов
        self.running = True
        self.thread = threading.Thread(target=self.send_loop, daemon=True)
        self.thread.start()

        master.protocol("WM_DELETE_WINDOW", self.on_close)

        self.update_ports_periodically()

    def update_sliders_visibility(self):
        for i in range(16):
            if i < self.active_channels:
                self.sliders_frames[i].pack(fill=tk.X, padx=10, pady=5)
                self.sliders[i].config(state=tk.NORMAL if self.transmitter.connected else tk.DISABLED)
            else:
                self.sliders_frames[i].pack_forget()

    def increase_channels(self):
        if self.active_channels < 16:
            self.active_channels += 1
            self.channel_count_label.config(text=str(self.active_channels))
            self.update_sliders_visibility()

    def decrease_channels(self):
        if self.active_channels > 1:
            self.active_channels -= 1
            self.channel_count_label.config(text=str(self.active_channels))
            self.update_sliders_visibility()

    def toggle_connection(self):
        if not self.transmitter.connected:
            port = self.port_var.get()
            baud = int(self.baud_var.get())
            if self.transmitter.connect(port, baud):
                self.connect_button.config(text="Отключить")
                self.status_label.config(text="Подключено")
                self.minus_button.config(state=tk.NORMAL)
                self.plus_button.config(state=tk.NORMAL)
                for i in range(self.active_channels):
                    self.sliders[i].config(state=tk.NORMAL)
                # Запускаем проверку PlatformIO
                self.check_platformio()
        else:
            self.transmitter.disconnect()
            self.connect_button.config(text="Подключить")
            self.status_label.config(text="")
            self.minus_button.config(state=tk.DISABLED)
            self.plus_button.config(state=tk.DISABLED)
            for slider in self.sliders:
                slider.config(state=tk.DISABLED)

    def toggle_temporary_disconnect(self):
        if not self.transmitter.temporarily_disconnected:
            if self.transmitter.temporarily_disconnect():
                self.temp_disconnect_button.config(text="Восстановить")
                for slider in self.sliders:
                    slider.config(state=tk.DISABLED)
        else:
            if self.transmitter.reconnect():
                self.temp_disconnect_button.config(text="Освободить порт")
                for i in range(self.active_channels):
                    self.sliders[i].config(state=tk.NORMAL)

    def on_slider_change(self, channel, value):
        if self.transmitter.connected and channel < self.active_channels:
            self.transmitter.update_channel(channel, value)
            self.labels[channel].config(text=f"Channel {channel+1}: {int(value)}")

    def send_loop(self):
        while self.running:
            if self.transmitter.connected and not self.transmitter.temporarily_disconnected:
                try:
                    # Передаем только active_channels каналов, остальные - 992
                    for i in range(16):
                        if i >= self.active_channels:
                            self.transmitter.channels[i] = 992
                    self.transmitter.send_packet()
                except Exception as e:
                    print(f"Ошибка в send_loop: {e}")
            threading.Event().wait(0.04)
    
    def update_ports(self):
        """Обновляет список доступных COM-портов"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports and not self.port_var.get():
            self.port_var.set(ports[0])
    
    def update_ports_periodically(self):
        """Периодическое обновление списка портов"""
        self.update_ports()
        self.master.after(2000, self.update_ports_periodically)
        
    def on_close(self):
        """Обработчик закрытия приложения"""
        self.running = False
        self.thread.join(timeout=0.5)
        self.transmitter.disconnect()
        self.master.destroy()

    def check_platformio(self):
        """Проверяет наличие процесса PlatformIO и управляет подключением"""
        platformio_running = False
        for proc in psutil.process_iter(['name']):
            try:
                if 'platformio' in proc.info['name'].lower():
                    platformio_running = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        if platformio_running and self.transmitter.connected and not self.transmitter.temporarily_disconnected:
            self.transmitter.temporarily_disconnect()
            self.status_label.config(text="Порт освобожден (PlatformIO)")
            for slider in self.sliders:
                slider.config(state=tk.DISABLED)
        elif not platformio_running and self.transmitter.temporarily_disconnected:
            if self.transmitter.reconnect():
                self.status_label.config(text="Подключено")
                for i in range(self.active_channels):
                    self.sliders[i].config(state=tk.NORMAL)
            else:
                self.status_label.config(text="Ошибка переподключения")

        # Проверяем каждые 500 мс
        self.master.after(500, self.check_platformio)

# Инициализация и запуск приложения
root = tk.Tk()
app = ControlApp(root)
root.mainloop()