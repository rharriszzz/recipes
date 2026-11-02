#!/usr/bin/env python3
"""Serve generated output at the production /recipes/ base path."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
class Preview(SimpleHTTPRequestHandler):
    def translate_path(self,path):
        if path=='/recipes': path='/recipes/'
        if path.startswith('/recipes/'): path=path[len('/recipes'):]
        return super().translate_path(path)
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(Path(__file__).resolve().parents[1]/'_site'),**kwargs)
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8000)
    args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Preview)
    print(f'Recipe preview: http://127.0.0.1:{server.server_port}/recipes/',flush=True)
    server.serve_forever()
