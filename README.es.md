[English (Auto-translated)](README.en.md) | [Español (Auto-translated)](README.es.md) | [हिंदी (Auto-translated)](README.hi.md) | [中文 (Auto-translated)](README.zh-CN.md) | [Русский](README.md)

> **Note**: This is an automatically translated version of the README file. The original Russian version is the source of truth. Translation is done using Google Translate API via GitHub Actions.

# Convertidor CRSF a PWM para STC15F104W.

Convertidor de protocolo CRSF (Crossfire) en señales PWM para el microcontrolador STC15F104W. El proyecto está destinado al uso de modelos en RC, donde la transformación del protocolo Digital CRSF se requiere en señales PWM analógicas para la gestión de unidades de servo.

## Características del software.

- Apoye hasta 5 canales PWM
- Recepción del protocolo CRSF a través de UART a una velocidad de 115200 BOD
- Generación PWM con un ancho de pulso establecido
- Validación básica de señales de entrada y procesamiento de fallas
- Trabajar a la frecuencia de la interna 22.1184 MHz

## Equipo requerido.

- Microcontrolador STC15F104W
-Aptator Classic USB-Jart (CH340, PL2101, FT232 y otros, no puede escribir WCH-Link estándar)
- Transmisor con soporte para el protocolo CRSF
- Servir para las pruebas

## conexión.

- Canales PWM:
  - P3.1 -> PWM Channel 1
  - P3.2 -> PWM Channel 2
  - P3.3 -> PWM Channel 3
  - P3.4 -> PWM Channel 4
  - P3.5 -> canal PWM 5
- Actualización de CRSF/firmware:
  - P3.0 (RXD) <- CRSF RX
  - P3.1 (TXD) -> CRSF TX (no utilizado)
- Fuente de alimentación:
  - gnd <- gnd
  - VCC <- +5V

## ensamblaje del proyecto.

1. Instalar [Código de Visual Studio](https://code.visualstudio.com/)
2. Establezca la expansión [Platformio IDE](https://platformio.org/install/ide?install=vscode)
3. Clon el repositorio:
```
Clon git https://github.com/chagin0leg/crsf2pwm_stc15.git
CD CRSF2PWM_STC15
```
4. Abra el proyecto en VS Code
5. Espere la instalación de adicciones Plataforma
6. Presione el botón de compilación (✓) en el panel de plataforma inferior o use la combinación de teclas Ctrl+Alt+B

## Software de carga.

1. Conecte el programador al microcontrolador a los mismos pines que CRSF (P3.0 (RXD) y P3.1 (TXD))
2. Presione el botón de carga (→) en el panel inferior de la plataforma o use la combinación de teclas Ctrl+Alt+U
3. Siga las instrucciones (generalmente pide una nutrición) y espere a que el firmware se complete

## Uso del dispositivo.

1. Conecte el transmisor con soporte CRSF a Pina P3.0 (RXD)
2. Conecte el servo unidades a los alfileres P3.1 - P3.5
3. Sirva la potencia del microcontrolador
4. Configure el transmisor para trabajar en modo CRSF

## Licencia.

El proyecto se distribuye bajo la licencia MIT. Detalles en el archivo [Licencia](Licencia).

## Autor.

- ** Chagin O.S. ** - [GitHub](https://github.com/chagin0leg)

## Contribución al proyecto.

1. Cree repositorio de bifurcaciones a través de la interfaz GitHub
2. Clon Fork localmente:
```
Git clon https://github.com/your_username/crsf2pwm_stc15.git
CD CRSF2PWM_STC15
```
3. Cree una nueva rama de desarrollo:
```
Git Checkout -B función/Nombre de su característica
```
4. Haga los cambios necesarios en el código
5. Arregle los cambios con un mensaje informativo:
```
Git Agregar.
Git commit -m "hazaña: agregue la nueva característica descripción"
```
6. Envíe cambios a un repositorio remoto:
```
Git Push Origin Feature/Your-Feature-Name
```
7. Cree solicitud de extracción en el repositorio principal a través de la interfaz GitHub