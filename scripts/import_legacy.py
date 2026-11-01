#!/usr/bin/env python3
"""One-time deterministic conversion; review before overwriting edited recipe files."""
import argparse, hashlib, json, re
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def clean(text): return re.sub(r'\s+',' ',text).strip()
class Legacy(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title=''; self.heading=''; self.intro=[]; self.lines=[]; self.line=[]
        self.in_title=False; self.in_heading=False; self.after_heading=False; self.in_recipe=False; self.italic=0; self.href=None
    def flush(self):
        parts=[]
        for kind,text,href in self.line:
            text=clean(text)
            if text:
                part={'type':kind,'text':text}
                if href: part['href']=href
                if parts and parts[-1]['type']==kind and parts[-1].get('href')==href:
                    parts[-1]['text']+=' '+text
                else: parts.append(part)
        if parts: self.lines.append({'type':'line','parts':parts})
        elif self.lines and self.lines[-1]['type']!='break': self.lines.append({'type':'break'})
        self.line=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='title': self.in_title=True
        if tag=='h3': self.in_heading=True
        if tag=='a': self.href=attrs.get('href')
        if tag=='p' and self.after_heading: self.in_recipe=True
        if tag=='i': self.italic+=1
        if tag=='br' and self.in_recipe: self.flush()
    def handle_endtag(self,tag):
        if tag=='title': self.in_title=False
        if tag=='h3': self.in_heading=False; self.after_heading=True
        if tag=='i': self.italic=max(0,self.italic-1)
        if tag=='a': self.href=None
        if tag=='body' and self.in_recipe and any(clean(x[1]) for x in self.line): self.flush()
    def handle_data(self,text):
        if self.in_title: self.title+=text
        elif self.in_heading: self.heading+=text
        elif self.in_recipe: self.line.append(('instruction' if self.italic else 'ingredient',text,self.href))
        elif self.after_heading and clean(text):
            p={'type':'link' if self.href else 'text','text':clean(text)}
            if self.href: p['href']=self.href
            self.intro.append(p)

CATEGORIES={
'cauliflower-peas-and-potatoes-in-sauce':['Vegetables','Indian'],
'chicken-with-cabbage-and-peanuts':['Meat','Chinese'],
'sausage-squash-and-posole-soup':['Soups','Meat'],
'enchiladas-and-posole-soup':['Soups','Meat','Mexican'],
'chicken-corn-chowder':['Soups','Meat'],
'pot-pie':['Soups','Meat'],
'potatoes-in-green-sauce':['Vegetables','Spanish'],
'red-lentil-soup':['Soups','Vegetables','Turkish'],
'tuna-egg-and-potato-salad':['Seafood','Salads','Spanish'],
'tuna-pasta':['Seafood','Pasta'],
'waffles':['Breakfast']}
TAGS={'chicken-with-cabbage-and-peanuts':['cabbage','peanuts'], 'red-lentil-soup':['lentils','kale'], 'waffles':['whole wheat']}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--overwrite',action='store_true'); args=ap.parse_args()
    for slug,categories in CATEGORIES.items():
        path=ROOT/'archive/fiberwoman'/f'{slug}.html'
        if not path.exists(): path=ROOT/'archive/local/xo-web-recipes'/f'{slug}.html'
        raw=path.read_bytes(); parser=Legacy(); parser.feed(raw.decode('utf-8'))
        while parser.lines and parser.lines[-1]['type']=='break': parser.lines.pop()
        record={'schema_version':1,'slug':slug,'title':clean(parser.title) if slug=='tuna-egg-and-potato-salad' else clean(parser.heading),'subtitle':None,'categories':categories,'tags':TAGS.get(slug,[]),'source_url':f'https://fiberwoman.com/recipes/{slug}.html','attribution':parser.intro,'servings':'Makes enough to fill a 3 1/2 qt. pot.' if slug=='chicken-corn-chowder' else None,'blocks':parser.lines,'notes':[],'variations':[],'photos':[],'metadata':{'imported':'2026-11-01','revised':None,'source_file':str(path.relative_to(ROOT)),'source_sha256':hashlib.sha256(raw).hexdigest(),'original_heading':clean(parser.heading),'origin':'local backup' if slug=='waffles' else 'live website'}}
        out=ROOT/'recipes'/f'{slug}.json'
        if out.exists() and not args.overwrite: raise SystemExit(f'Refusing to overwrite {out}; review changes and pass --overwrite explicitly.')
        out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
        print(f'{record["title"]}: {len(parser.lines)} blocks')
if __name__=='__main__': main()
