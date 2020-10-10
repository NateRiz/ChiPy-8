# ChiPy-8

Chip-8 Emulator written in Python 3

Index:
1. [About Chip-8](#About-Chip-8)
2. [Example ROMs](#Example-ROMs)
    - [Connect 4](#Connect-4)
    - [Space Invaders](#Space-Invaders)
3. [Usage](#Usage)
    - [Requirements](#Requirements)
5. [Testing](#Testing)
6. [Acknowledgements](#Acknowledgements)
7. [License](#License)

## About Chip-8
> CHIP-8 is an interpreted programming language, developed by Joseph Weisbecker. It was initially used on the COSMAC VIP and Telmac 1800 8-bit microcomputers in the mid-1970s. CHIP-8 programs are run on a CHIP-8 virtual machine. It was made to allow video games to be more easily programmed for these computers.

## Example ROMs

#### Connect 4

#### Space Invaders

## Debugger
This interpreter can use a debugger by passing in a command line argument with pause, step, and play

## Usage
```Python
python3 main.py {ROM_file_name.ch8}
# python3 "main.py pong (alt).ch8"
```

```Python
python3 main.py {ROM_file_name.ch8} debug
# to bring up the debugger
```

#### Requirements
```
pip3 install pygame
```

## Testing
The unit tests for ChiPy-8 uses the `unittest` module
```
python3 tests.py
```

## Acknowledgements
 * [BUILDING A CHIP-8 EMULATOR](https://austinmorlan.com/posts/chip8_emulator/)
 

## License
This project is available under the [GNU general public license](https://github.com/NateRiz/ChiPy-8/blob/master/LICENSE)

