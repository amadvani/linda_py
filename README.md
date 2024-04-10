# linda_py

Laser Interface Networking Doohickey for AMSAT -- MicroPython Implementation

## Overview

The Laser Interface Networking Doohickey for AMSAT (LINDA) is a subsystem which implements proof-of-concept laser communications for the [AMSAT CubeSatSim](https://github.com/alanbjohnston/CubeSatSim). It is designed around a Sparkfun Thing Plus RP2040 microcontroller, and uses a generic 650nm laser pointer and laser sensor to implement a basic free-space optical communication link between two LINDA subsystems.

### Block Diagram

![Linda Block Diagram](./doc/LINDA%20Block%20Diagram.jpeg)

### Wiring Diagram

Wiring diagram... use your imagination

### Laser Submodule Flowchart

![LINDA Laser Submodule Flowchart](./doc/LINDA%20Laser%20Flowchart.jpeg)

### Installation

This should be able to be run on any RP2040-based microcontroller, although I could only get reliable timer usage from Sparkfun boards: [Sparkfun Pro Micro RP2040](https://www.sparkfun.com/products/18288) and [Sparkfun Thing Plus RP2040](https://www.sparkfun.com/products/17745).

#### Micropython

There are plenty of tutorials on how to set up your microcontroller for Micropython, so I won't do that here. Go to the [MicroPython downloads page](https://micropython.org/download/?mcu=rp2040) and get your microcontroller's firmware, flash it, etc etc.

I found that flashing the Sparkfun Thing Plus RP2040 firmware caused intermittant issues, which were remedied by flashing the normal Raspberry Pi Pico version instead.

#### VS Code Environment

I developed all of the LINDA codebase using VS Code as an IDE. Install:

* [MicroPico](https://marketplace.visualstudio.com/items?itemName=paulober.pico-w-go)

Follow the instructions to install the MicroPico extension, including the "Getting started" section. This should configure VS Code to have various MicroPico-related buttons on the bottom bar, including "Pico Connected/Disconnected", "Run", and "Reset".

#### Loading LINDA Software

Connect the RP2040 microcontroller to your computer and wait for the VS Code bottom bar to change to "Pico Connected". You should be able to click "Run" and interct with the microcontroller using the MicroPython REPL.

In ```libraries/gpio.py```, define the pin numbers for each component for your specific setup.

With the file explorer selected, right-click on main.py and choose "Upload project to Pico". Depending on the specific configuration of your MicroPico extension, this will either upload the entire project .py files to the microcontroller, or just the main.py. Either way, you should be able to monitor which files are being loaded on the bottom status bar. Make sure that main.py and the entire libraries/ diretory are uploded. This process writes the files to the RP2040 flash memory.

MicroPython will run code found in main.py upon boot, whether attached through USB to a computer or a power supply. When connected to a computer, you can press the physical reset button on the board to have it connect to VS Code and provide access to the REPL.