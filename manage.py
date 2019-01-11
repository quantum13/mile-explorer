import sys

from dotenv import load_dotenv
load_dotenv('.env')

args = sys.argv[1:]

if len(args) > 0:
    if args[0] == 'runserver':
        from core.server import start as start_server
        start_server()
    elif args[0] == 'runproxy':
        from core.proxy import start as start_proxy
        start_proxy()
    elif args[0] == 'runindexer':
        from apps.explorer.indexer import start as start_indexer
        if len(args)==2 and args[1] == 'stage1':
            start_indexer(1)
        else:
            start_indexer(2)
