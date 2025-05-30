[English (Auto-translated)](README.en.md) | [Español (Auto-translated)](README.es.md) | [हिंदी (Auto-translated)](README.hi.md) | [中文 (Auto-translated)](README.zh-CN.md) | [Русский](README.md)

> **Note**: This is an automatically translated version of the README file. The original Russian version is the source of truth. Translation is done using Google Translate API via GitHub Actions.

# CRSF To PWM Converter for StC15F104W.

CRSF (Crossfire) protocol converter in PWM signals for the microcontroller STC15F104W. The project is intended for the use of models in RC, where the transformation of the CRSF digital protocol is required into analog PWM signals for managing servo drives.

## Features of software.

- support up to 5 PWM channels
- Reception of CRSF protocol through UART at a speed of 115200 BOD
- PWM generation with a set -up pulse width
- basic validation of input signals and failure processing
- Work at the frequency of the internal 22.1184 MHz

## required equipment.

- microcontroller STC15F104W
-Classic USB-JART adapter (CH340, PL2101, FT232 and others, you can not standard type WCH-Link)
- transmitter with support for CRSF Protocol
- serving for testing

## connection.

- PWM channels:
  - P3.1 -> PWM Channel 1
  - P3.2 -> PWM Channel 2
  - P3.3 -> PWM Channel 3
  - P3.4 -> PWM Channel 4
  - P3.5 -> PWM Channel 5
- CRSF/Firmware update:
  - P3.0 (RXD) <- CRSF RX
  - P3.1 (TXD) -> CRSF TX (not used)
- Power supply:
  - GND <- GND
  - VCC <- +5V

## Assembly of the project.

1. Install [Visual Studio Code](https://code.visualstudio.com/)
2. Set the expansion [Platformio IDE](https://platformio.org/install/ide?install=vscode)
3. Clon the repository:
```
Git Clone https://github.com/chagin0leg/crsf2pwm_stc15.git
CD CRSF2PWM_STC15
```
4. Open the project in VS Code
5. Wait for the installation of addictions Platformio
6. Press the Build button (✓) in the lower Platformio panel or use the key combination Ctrl+Alt+B

## Loading software.

1. Connect the programmer to the microcontroller to the same pins as CRSF (P3.0 (RXD) and P3.1 (TXD))
2. Press the Upload (→) button in the lower Platformio panel or use the key combination Ctrl+Alt+U
3. Follow the instructions (usually asks for a nutrition) and wait for the firmware to complete

## Use of the device.

1. Connect the transmitter with CRSF support to Pina P3.0 (RXD)
2. Connect servo drives to pins p3.1 - P3.5
3. Serve the power to the microcontroller
4. Set up the transmitter for work in CRSF mode

## License.

The project is distributed under the MIT license. Details in the [license](license) file.

## Author.

- ** Chagin O.S. ** - [github](https://github.com/chagin0leg)

## contribution to the project.

1. Create Fork repository through the Github interface
2. Clon fork locally:
```
Git Clone https://github.com/your_username/crsf2pwm_stc15.git
CD CRSF2PWM_STC15
```
3. Create a new development branch:
```
Git Checkout -b Feature/Your-Feature-Name
```
4. Make the necessary changes to the code
5. Fix changes with an informative message:
```
Git Add.
GIT COMMIT -M "Feat: Add New Feature Description"
```
6. Send changes to a remote repository:
```
GIT PUSH Origin Feature/Your-Feature-Name
```
7. Create Pull Request in the main repository through the Github interface