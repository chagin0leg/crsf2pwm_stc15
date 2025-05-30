[English (Auto-translated)](README.en.md) | [Español (Auto-translated)](README.es.md) | [हिंदी (Auto-translated)](README.hi.md) | [中文 (Auto-translated)](README.zh-CN.md) | [Русский](README.md)

> **Note**: This is an automatically translated version of the README file. The original Russian version is the source of truth. Translation is done using Google Translate API via GitHub Actions.

＃CRSF到PWM转换器，用于STC15F104W。

Microcontroller STC15F104W中的PWM信号中的CRSF（Crossfire）协议转换器。该项目旨在在RC中使用模型，在此中，CRSF数字协议的转换需要用于模拟PWM信号以管理伺服驱动器。

##软件功能。

 - 最多支持5个PWM频道
 - 通过UART以115200 BOD的速度接收CRSF协议
-PWM生成具有set -up脉冲宽度的生成
 - 输入信号和故障处理的基本验证
 - 以内部22.1184 MHz的频率工作

##所需设备。

 - 微控制器STC15F104W
-Classic USB-JART适配器（CH340，PL2101，FT232等，您无法标准类型的wch-link）
 - 发射器支持CRSF协议
 - 用于测试

＃＃ 联系。

```
STC15F104W
    |
    |-- P3.1 -> PWM Channel 1
    |-- P3.2 -> PWM Channel 2
    |-- P3.3 -> PWM Channel 3
    |-- P3.4 -> PWM Channel 4
    |-- P3.5 -> PWM Channel 5
    |
    |-- P3.0 (RXD) <- CRSF RX
    |-- P3.1 (TXD) -> CRSF TX (не используется)
    |
    |-- GND <- GND от источника питания
    |-- VCC <- +5V от источника питания
```

##项目组装。

1。安装[Visual Studio Code]（https://code.visualstudio.com/）
2。设置扩展[Platformio IDE]（https://platformio.org/install/ide?install = vscode）
3。存储库克隆：
```
git clone https://github.com/chagin0leg/crsf2pwm_stc15.git
cd crsf2pwm_stc15
```
4。用VS代码打开项目
5。等待成瘾平台的安装
6。按下较低平台面板中的构建按钮（✓）或使用键组合Ctrl+Alt+b

##加载软件。

1。将程序员连接到微控制器与CRSF（P3.0（RXD）和P3.1（TXD））相同的引脚
2。按下较低平台面板中的上传（→）按钮或使用键组合Ctrl+Alt+U
3。按照说明（通常要求营养）并等待固件完成

##使用设备。

1。将发射器与CRSF支持连接到PITA P3.0（RXD）
2。将伺服驱动器连接到销钉p3.1 -p3.5
3。将电源提供给微控制器
4。设置在CRSF模式下工作的发射器

＃＃ 执照。

该项目是根据麻省理工学院许可证分发的。 [许可]（许可证）文件中的详细信息。

＃＃ 作者。

 -  ** Chagin O.S. **  -  [github]（https://github.com/chagin0leg）

##对该项目的贡献。

1。通过github接口创建叉子存储库
2。克隆叉本地：
```
git clone https://github.com/YOUR_USERNAME/crsf2pwm_stc15.git
cd crsf2pwm_stc15
```
3。创建一个新的开发分支：
```
git checkout -b feature/your-feature-name
```
4.对代码进行必要的更改
5。通过信息丰富的消息进行修复更改：
```
git add .
git commit -m "feat: add new feature description"
```
6。将更改发送到远程存储库：
```
git push origin feature/your-feature-name
```
7。通过GitHub接口在主存储库中创建拉力请求