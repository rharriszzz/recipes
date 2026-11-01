#!/usr/bin/env python3
"""Validate recipe metadata, faithful migration, generated links and formatting."""
import argparse, hashlib, json, re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote
from build import ROOT, load_recipes

def compact(text): return re.sub(r'\s+','',text)
class Text(HTMLParser):
    def __init__(self): super().__init__(); self.text=[]
    def handle_data(self,data): self.text.append(data)
class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.ids=set(); self.content=[]; self.depth=0; self.strong=0; self.em=0; self.h1=0; self.lang=False; self.viewport=False
    def handle_starttag(self,t,attrs):
        a=dict(attrs)
        if t=='html': self.lang=a.get('lang')=='en'
        if t=='meta' and a.get('name')=='viewport': self.viewport=True
        if t=='h1': self.h1+=1
        if 'id' in a: assert a['id'] not in self.ids, f'Duplicate ID: {a["id"]}'; self.ids.add(a['id'])
        if t in ('a','link','script','img'):
            target=a.get('href') if t in ('a','link') else a.get('src')
            if target: self.links.append(target)
        if t=='img': assert a.get('alt'), 'Photo needs alt text'
        if t=='div' and 'recipe-content' in a.get('class','').split(): self.depth=1
        elif t=='div' and self.depth: self.depth+=1
        if self.depth:
            self.strong+=t=='strong'; self.em+=t=='em'
    def handle_endtag(self,t):
        if t=='div' and self.depth: self.depth-=1
    def handle_data(self,data):
        if self.depth: self.content.append(data)

def validate(base='/recipes/'):
    recipes=load_recipes(); assert recipes, 'No recipes'
    slugs=set(); sources=set(); recipe_stats=[]
    for r in recipes:
        slug=r['slug']; assert re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',slug),slug
        assert slug not in slugs; slugs.add(slug)
        assert (ROOT/'recipes'/f'{slug}.json').is_file(), f'Filename must match slug: {slug}'
        assert r['schema_version']==1 and r['title'] and r['categories'],slug
        assert urlsplit(r['source_url']).scheme in ('http','https'),slug
        for part in r['attribution']:
            assert part['type'] in ('text','link') and part['text']
        source=ROOT/r['metadata']['source_file']; assert source.is_file(),source
        assert hashlib.sha256(source.read_bytes()).hexdigest()==r['metadata']['source_sha256'],f'Changed archive {source}'
        sources.add(source.name)
        ingredients=instructions=0
        for block in r['blocks']:
            assert block['type'] in ('line','break','section','note'),slug
            if block['type']=='line':
                assert block['parts']
                for part in block['parts']:
                    assert part['type'] in ('ingredient','instruction') and part['text'].strip(),slug
                    ingredients+=part['type']=='ingredient';instructions+=part['type']=='instruction'
                    if part.get('href'): assert urlsplit(part['href']).scheme in ('http','https'),part
        assert ingredients and instructions,slug
        for photo in r['photos']:
            assert photo['alt'] and (ROOT/'static'/photo['src']).is_file(),photo
        generated=ROOT/'_site'/slug/'index.html'; assert generated.exists()
        p=Page();p.feed(generated.read_text()); assert p.strong==ingredients and p.em==instructions,f'Ingredient/instruction styling mismatch: {slug}'
        content=''.join(p.content)
        expected=''.join(part['text'] for b in r['blocks'] for part in (b['parts'] if b['type']=='line' else [{'text':b.get('text','')}]))
        assert compact(content)==compact(expected),f'Rendered content changed: {slug}'
        if r['metadata']['origin'] in ('live website','local backup'):
            raw=source.read_text(); after_heading=re.split(r'</h3\s*>',raw,flags=re.I)[1]; body=re.split(r'</body',after_heading,flags=re.I)[0]
            text=Text();text.feed(body)
            imported=''.join(part['text'] for part in r['attribution'])+expected
            assert compact(''.join(text.text))==compact(imported),f'Original content changed: {slug}'
        elif slug in ('dolsot-bibimbap-for-two','musaengchae'):
            raw=source.read_text().split('<body>',1)[1].split('</body>',1)[0]
            if slug=='musaengchae':
                raw=raw.split('<h2>Daikon Radish Salad (Musaengchae)</h2>',1)[1].split('</section>',1)[0]
                imported=expected
            else:
                raw=raw.split('</h1>',1)[1]
                imported=''.join(part['text'] for part in r['attribution'])+expected
            text=Text();text.feed(raw)
            assert compact(''.join(text.text))==compact(imported),f'ChatGPT HTML changed: {slug}'
        elif slug=='cod-and-potato-chowder':
            raw=source.read_text().split('You already have:\n',1)[1]
            imported=''.join(part['text'] for b in r['blocks'] if b['type']!='section' for part in (b['parts'] if b['type']=='line' else [{'text':b.get('text','')}]))
            assert compact(raw)==compact(imported), 'Cod source wording/order changed'
        elif slug=='smoked-salmon-potato-chowder':
            raw=source.with_suffix('.extracted.txt').read_text().split('2 or 3 servings',1)[1]
            assert compact(raw)==compact(expected), 'Salmon PDF wording/order changed'
        elif slug=='fish-chowder':
            # Extraction was generated once with pypdf from the archived PDF and reviewed visually.
            raw=source.with_suffix('.extracted.txt').read_text()
            source_lines=[x.strip() for x in raw.splitlines() if x.strip() and x.strip()!='\x7f']
            headings={'Fish Chowder','Ingredients (2–3 servings)','Day 1 – Build the Base','Day 2 – Finish','Notes'}
            source_content=[compact(x) for x in source_lines if x not in headings]
            imported=[compact(part['text']) for b in r['blocks'] if b['type']!='section' for part in (b['parts'] if b['type']=='line' else [{'text':b.get('text','')}])]
            from collections import Counter
            assert Counter(source_content)==Counter(imported), 'Fish PDF contents changed or omitted'
            original_steps=source_lines[source_lines.index('Day 1 – Build the Base')+1:source_lines.index('Notes')]
            original_steps=[compact(x) for x in original_steps if x not in headings]
            rendered_steps=[compact(part['text']) for b in r['blocks'] if b['type']=='line' for part in b['parts'] if part['type']=='instruction']
            assert original_steps==rendered_steps, 'Fish instruction order changed'
        recipe_stats.append({'slug':slug,'ingredient_fragments':ingredients,'instruction_fragments':instructions,'source':str(source.relative_to(ROOT))})
    # Independent discovery coverage against links in the archived index, including comments.
    index=(ROOT/'archive/fiberwoman/recipes.html').read_text()
    discovered=set(re.findall(r'href="([^"]+\.html)"',index)); assert discovered<=sources,f'Missing originals: {discovered-sources}'
    pages={}
    for f in (ROOT/'_site').rglob('*.html'):
        if 'archive' in f.relative_to(ROOT/'_site').parts: continue
        p=Page();p.feed(f.read_text());pages[f]=p
        assert p.h1==1 and p.lang and p.viewport, f'Page metadata {f}'
    for f,p in pages.items():
        url=base+str(f.relative_to(ROOT/'_site'))
        for link in p.links:
            target=urlsplit(urljoin('https://example.test'+url,link))
            if target.netloc!='example.test':
                assert target.scheme in ('http','https','mailto'),link
                continue
            assert target.path.startswith(base),f'Wrong base path: {link} in {f}'
            rel=unquote(target.path[len(base):]); dest=ROOT/'_site'/rel
            if dest.is_dir(): dest=dest/'index.html'
            assert dest.is_file(),f'Broken link {link} in {f}'
            if target.fragment and dest in pages: assert unquote(target.fragment) in pages[dest].ids,f'Unknown anchor {link}'
    report={'recipes':len(recipes),'originals_accounted_for':len(discovered),'generated_html_pages':len(pages),'recipes_checked':recipe_stats,'checks':['archive SHA-256','metadata','original full text and order','rendered full text','bold ingredients and italic instructions','base path','internal links, assets, anchors','viewport and language']}
    print(json.dumps(report,indent=2))
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--base-path',default='/recipes/');p.add_argument('--report');args=p.parse_args();report=validate(args.base_path)
    if args.report: Path(args.report).write_text(json.dumps(report,indent=2)+'\n')
