#!/usr/bin/env python3
"""Serve generated output at the production /recipes/ base path."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
class Preview(SimpleHTTPRequestHandler):
    def translate_path(self,path):
        if path=='/recipes': path='/recipes/'
        if path.startswith('/recipes/'): path=path[len('/recipes'):]
        return super().translate_path(path)
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(Path(__file__).resolve().parents[1]/'_site'),**kwargs)
if __name__=='__main__':
    print('Recipe preview: http://127.0.0.1:8000/recipes/',flush=True)
    ThreadingHTTPServer(('127.0.0.1',8000),Preview).serve_forever()
