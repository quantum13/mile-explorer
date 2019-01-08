import sys

from dotenv import load_dotenv
load_dotenv('.env')

args = sys.argv[1:]

if len(args) == 1:
    if args[0] == 'runserver':
        from core.server import start as start_server
        start_server()
    elif args[0] == 'runproxy':
        from core.proxy import start as start_proxy
        start_proxy()
    elif args[0] == 'runindexer':
        from apps.explorer.indexer import start as start_indexer
        start_indexer()
