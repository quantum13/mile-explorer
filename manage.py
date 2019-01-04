import sys

from core.server import start

args = sys.argv[1:]

if len(args) == 1 and args[0] =='runserver':
    start()
