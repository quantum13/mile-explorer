import sys

from dotenv import load_dotenv
load_dotenv('.env')


from apps.explorer.indexer import start as start_indexer
from core.server import start as start_server


args = sys.argv[1:]

if len(args) == 1:
    if args[0] == 'runserver':
        start_server()
    elif args[0] == 'runindexer':
        start_indexer()
