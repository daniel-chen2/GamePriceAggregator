#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    os.system("pip install virtualenv")
    os.system('python -m venv myvenv')
    os.system('source myvenv/Scripts/activate')
    #!/myvenv/Scripts/activate
    os.system("pip install requirements.txt")

if __name__ == '__main__':
    main()
