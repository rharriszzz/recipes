#!/usr/bin/env python3
"""Check every generated page and linked local asset against a served deployment."""
import argparse, concurrent.futures, hashlib, json, subprocess
from datetime import datetime,timezone
from urllib.parse import urlsplit,urljoin,unquote
from build import ROOT,load_recipes
from validate import Page

def main():
    ap=argparse.ArgumentParser();ap.add_argument('url');ap.add_argument('--revision');ap.add_argument('--report');args=ap.parse_args()
    base=args.url.rstrip('/')+'/';prefix=urlsplit(base).path
    files={}
    for p in (ROOT/'_site').rglob('*.html'):
        rel=p.relative_to(ROOT/'_site')
        if 'archive' in rel.parts: continue
        files[str(rel)]=p
        parser=Page();parser.feed(p.read_text())
        for link in parser.links:
            u=urlsplit(urljoin(base+str(rel),link))
            if u.netloc!=urlsplit(base).netloc:continue
            assert u.path.startswith(prefix),u.path
            r=unquote(u.path[len(prefix):]);target=ROOT/'_site'/r
            if target.is_dir(): target=target/'index.html'
            files[str(target.relative_to(ROOT/'_site'))]=target
    def check(item):
        rel,p=item
        result=subprocess.run(['curl','-sSL','--retry','2','--max-time','30','-w','\n%{http_code}',base+rel],capture_output=True)
        raw,_,status=result.stdout.rpartition(b'\n')
        if result.returncode or status!=b'200': raise RuntimeError(f'{rel}: HTTP {status.decode()} {result.stderr.decode()}')
        if raw!=p.read_bytes(): raise RuntimeError(f'Published bytes differ: {rel}')
        return rel
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool: checked=sorted(pool.map(check,files.items()))
    raw=subprocess.check_output(['curl','-sSL','--fail','--max-time','30',base+'build-info.json']);info=json.loads(raw)
    assert info['recipe_count']==len(load_recipes()) and info['base_path']==prefix,info
    if args.revision: assert info['revision']==args.revision,info
    report={'url':base,'verified_at':datetime.now(timezone.utc).isoformat(),'build_info':info,'checked_files':len(checked),'paths':checked,'result':'passed'}
    if args.report: (ROOT/args.report).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
