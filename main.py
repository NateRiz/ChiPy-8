import sys
import os
from Debugger import Debugger
from Interpreter import Interpreter


def main():
    print(sys.argv)
    path = os.path.join(os.getcwd(), "Roms", sys.argv[1])
    if "debug" in sys.argv:
        interpreter = Interpreter(path, True)
        Debugger(interpreter).execute()
    else:
        interpreter = Interpreter(path, False)
        while True:
            interpreter.tick()

if __name__ == '__main__':
    main()
