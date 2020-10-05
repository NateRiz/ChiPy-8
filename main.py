import sys
import os
from Interpreter import Interpreter

def main():
    print(sys.argv)
    path = os.path.join(os.getcwd(), "Roms", sys.argv[1])
    interpreter = Interpreter(path)
    while True:
        interpreter.tick()

if __name__ == '__main__':
    main()
