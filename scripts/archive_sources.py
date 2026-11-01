#!/usr/bin/env python3
"""Explicit, repeatable read-only crawl of the original recipe directory."""
import hashlib, json, re, shutil, subprocess
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://fiberwoman.com/recipes/'
class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]
    def handle_starttag(self, tag, attrs):
        for k,v in attrs:
            if k in ('href','src') and v: self.links.append(v)
    def handle_comment(self, data):
        self.links.extend(re.findall(r'(?:href|src)\s*=\s*[\"\']([^\"\']+)', data, re.I))
    def handle_startendtag(self, tag, attrs): self.handle_starttag(tag,attrs)

def main():
    queue=[BASE, BASE+'recipes.html']; seen=set(); records=[]
    while queue:
        url=queue.pop(0).split('#')[0]
        if url in seen: continue
        seen.add(url)
        rel=unquote(urlsplit(url).path.removeprefix('/recipes/')) or 'index.html'
        if '..' in Path(rel).parts: raise ValueError(rel)
        dest=ROOT/'archive/fiberwoman'/rel; dest.parent.mkdir(parents=True,exist_ok=True)
        record={'url':url,'archive':str(dest.relative_to(ROOT))}
        result=subprocess.run(['curl','-sSL','--max-time','45','-w','\n%{http_code}',url],capture_output=True)
        raw, _, status=result.stdout.rpartition(b'\n')
        record['status']=int(status or 0)
        if result.returncode==0 and record['status']==200:
            dest.write_bytes(raw); record['sha256']=hashlib.sha256(raw).hexdigest()
            if '.html' in rel:
                parser=Links(); parser.feed(raw.decode('utf-8'))
                record['links']=parser.links
                for link in parser.links:
                    target=urljoin(url,link).split('#')[0]
                    if target.startswith(BASE) and urlsplit(target).scheme in ('http','https'): queue.append(target)
        else:
            record['error']=result.stderr.decode() or f"HTTP {record['status']}"
        records.append(record)
    # Archival copies of the same family's website; only recipe material is copied.
    for name, source in [('xo-web-recipes',Path('/Users/rharris/xo/web/recipes')),('thornbackup-recipes',Path('/Users/rharris/thornbackup/xo/web/recipes'))]:
        if source.is_dir():
            for p in sorted(source.iterdir()):
                if p.suffix in ('.html','.css'):
                    out=ROOT/'archive/local'/name/p.name; out.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(p,out)
    for i,p in enumerate([Path('/Users/rharris/Downloads/recipes.html'),Path('/Users/rharris/Downloads/recipes (1).html')]):
        if p.is_file(): shutil.copyfile(p,ROOT/'archive/local'/f'downloads-index-{i+1}.html')
    (ROOT/'archive/retrieval.json').write_text(json.dumps({'retrieved':'2026-11-01','root':BASE,'resources':records},indent=2)+'\n')
    print(json.dumps([{k:r[k] for k in ('url','status')} for r in records],indent=2))
if __name__=='__main__': main()
