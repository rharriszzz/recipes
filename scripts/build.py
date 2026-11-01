#!/usr/bin/env python3
"""Dependency-free recipe site generator. All content is escaped by default."""
import argparse, html, json, os, re, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
E=lambda value: html.escape(str(value),quote=True)

def load_recipes():
    return sorted((json.loads(p.read_text()) for p in (ROOT/'recipes').glob('*.json')),key=lambda r:r['title'].casefold())

def inline(parts):
    rendered=[]
    for p in parts:
        text=E(p['text'])
        if p.get('href'): text=f'<a href="{E(p["href"])}">{text}</a>'
        rendered.append(text)
    # Intro links follow the original punctuation, without adding gaps before periods.
    return re.sub(r'\s+([.,;:])',r'\1',' '.join(rendered))

def render_block(b):
    kind=b['type']
    if kind=='break': return '<div class="recipe-break" aria-hidden="true"></div>'
    if kind=='section': return f'<h2 class="section-title">{E(b["text"])}</h2>'
    if kind=='note': return f'<p class="recipe-note">{E(b["text"])}</p>'
    if kind=='line':
        parts=[]
        for p in b['parts']:
            tag='strong' if p['type']=='ingredient' else 'em'
            text=E(p['text'])
            if p.get('href'): text=f'<a href="{E(p["href"])}">{text}</a>'
            parts.append(f'<{tag}>{text}</{tag}>')
        role='instruction' if all(p['type']=='instruction' for p in b['parts']) else 'ingredient'
        content = ''.join(('' if i == 0 or b['parts'][i]['text'][0] in ',.;:' else ' ') + part for i, part in enumerate(parts))
        return f'<p class="recipe-line {role}">'+content+'</p>'
    raise ValueError(f'Unknown block {kind}')

def page(title,body,base,description,recipe=False):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)} · Recipes</title><meta name="description" content="{E(description)}">
<meta name="theme-color" content="#fffff0"><link rel="icon" href="{base}favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{base}style.css"><script src="{base}site.js" defer></script></head>
<body class="{'recipe-page' if recipe else 'index-page'}"><a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><a class="wordmark" href="{base}">Recipes<span class="wordmark-dot">.</span></a><span class="header-note">From our kitchen</span>
<button class="contrast-toggle" type="button" aria-pressed="false" hidden>Higher contrast</button></header>
{body}
<footer class="site-footer"><p>Here are some recipes that we like.</p><a href="{base}">All recipes</a><a href="https://github.com/rharriszzz/recipes">Recipe sources &amp; maintenance</a></footer>
</body></html>'''

def recipe_page(r,base):
    tags=''.join(f'<a class="tag" href="{base}?category={E(c)}">{E(c)}</a>' for c in r['categories'])
    intro=f'<p class="attribution">{inline(r["attribution"])}</p>' if r['attribution'] else ''
    subtitle=f'<p class="subtitle">{E(r["subtitle"])}</p>' if r.get('subtitle') else ''
    servings=f'<p class="servings">{E(r["servings"])}</p>' if r.get('servings') and r['servings'] not in inline(r['attribution']) else ''
    photos=''.join(f'<figure><img src="{base}{E(p["src"])}" alt="{E(p["alt"])}"><figcaption>{E(p.get("caption",""))}</figcaption></figure>' for p in r.get('photos',[]))
    notes=''.join(f'<p class="recipe-note">{E(n)}</p>' for n in r.get('notes',[]))
    variations=''.join(f'<section><h2>{E(v["title"])}</h2>'+''.join(render_block(b) for b in v['blocks'])+'</section>' for v in r.get('variations',[]))
    local=r['metadata']['origin']=='local backup'
    provenance=('Recovered from the original local website backup. The original web page is unavailable.' if local else 'Recovered from your ChatGPT recipe source.' if r['metadata']['origin']=='ChatGPT source artifact' else 'Preserved from the original recipe website.')
    body=f'''<main id="main" class="recipe-main"><nav class="recipe-nav" aria-label="Recipe navigation"><a href="{base}">← All recipes</a><button type="button" class="print-button" hidden>Print recipe</button></nav>
<article><header class="recipe-heading"><div class="tags">{tags}</div><h1>{E(r['title'])}</h1>{subtitle}{intro}{servings}</header>
{photos}<div class="recipe-content">{''.join(render_block(b) for b in r['blocks'])}</div>{notes}{variations}
<aside class="provenance"><p>{provenance} <a href="{E(r['source_url'])}">Original URL</a> · <a href="{base}{E(r['metadata']['source_file'])}">Archived source</a></p></aside></article>
<a class="back-bottom" href="{base}">← Back to all recipes</a></main>'''
    return page(r['title'],body,base,f'{r["title"]}. Ingredients and instructions in the order you use them.',True)

def index(recipes,base):
    categories=sorted({c for r in recipes for c in r['categories']})
    filters=''.join(f'<button type="button" class="filter" data-category="{E(c)}" aria-pressed="false">{E(c)}</button>' for c in categories)
    letters=sorted({r['title'][0].upper() for r in recipes})
    alphabet=''.join(f'<a href="#letter-{c}">{c}</a>' for c in letters)
    groups=[]
    for letter in letters:
        cards=[]
        for r in recipes:
            if r['title'][0].upper()!=letter: continue
            title=E(r['title']); cats=E(' · '.join(r['categories']))
            search=E(r['title'].casefold())
            cards.append(f'''<li class="recipe-card" data-title="{search}" data-categories="{E(json.dumps(r['categories']))}"><a href="{base}{r['slug']}/"><span class="card-title">{title}</span><span class="card-meta">{cats}</span><span class="card-arrow" aria-hidden="true">↗</span></a></li>''')
        groups.append(f'<section class="letter-group" id="letter-{letter}" aria-labelledby="heading-{letter}"><h2 id="heading-{letter}">{letter}</h2><ul class="recipe-list">{"".join(cards)}</ul></section>')
    body=f'''<main id="main" class="index-main"><div class="intro"><p class="eyebrow">A collection of favorites</p><h1>Good food,<br>kept simple.</h1><p class="intro-text">Our recipes, gathered in one place. Ingredients and instructions together, just as you need them.</p><span class="collection-count">{len(recipes)} recipes</span></div>
<section class="browse" aria-label="Find a recipe"><div class="search-wrap" hidden><label for="search">Find a recipe</label><div class="search-field"><span aria-hidden="true">⌕</span><input id="search" type="search" placeholder="Search recipe titles…" autocomplete="off" aria-controls="recipe-results"><button type="button" id="clear-search" hidden>Clear</button></div></div>
<div class="filters" hidden aria-label="Filter by category"><button type="button" class="filter" data-category="" aria-pressed="true">All recipes</button>{filters}</div>
<div class="browse-heading"><p id="result-count" role="status" aria-live="polite">{len(recipes)} recipes · A–Z</p><nav class="alphabet" aria-label="Jump to a letter">{alphabet}</nav></div>
<div id="recipe-results">{''.join(groups)}</div><div id="empty-state" hidden><h2>No recipes found</h2><p>Try a shorter title or choose another category.</p><button type="button" id="reset-filters">Show all recipes</button></div>
<noscript><p>Browse every recipe alphabetically above. Title search and category filters are available when JavaScript is enabled.</p></noscript></section></main>'''
    return page('Home',body,base,'Family recipes with ingredients and instructions together, in order of use. Browse alphabetically, search titles, and print recipes.')

def build(base='/recipes/'):
    if not re.fullmatch(r'/[A-Za-z0-9_/-]*/',base) and base!='/': raise ValueError('Use an absolute base path ending in /')
    out=ROOT/'_site'; out.mkdir(exist_ok=True)
    # Only remove generated output inside this project.
    for p in out.iterdir():
        if p.is_dir(): shutil.rmtree(p)
        else: p.unlink()
    for p in (ROOT/'static').iterdir():
        if p.is_dir(): shutil.copytree(p,out/p.name)
        else: shutil.copyfile(p,out/p.name)
    recipes=load_recipes()
    for r in recipes:
        folder=out/r['slug']; folder.mkdir(); (folder/'index.html').write_text(recipe_page(r,base))
        # Bookmarks from the old site also work under /recipes/.
        (out/f'{r["slug"]}.html').write_text(recipe_page(r,base))
    (out/'index.html').write_text(index(recipes,base))
    (out/'recipes.html').write_text(index(recipes,base))
    (out/'.nojekyll').touch()
    (out/'404.html').write_text(page('Page not found',f'<main id="main" class="recipe-main"><h1>Recipe not found</h1><p><a href="{base}">Browse all recipes</a></p></main>',base,'Find a recipe in the collection.'))
    # Publish only recipe archives, never private local search results or other documents.
    shutil.copytree(ROOT/'archive',out/'archive')
    (out/'build-info.json').write_text(json.dumps({'recipe_count':len(recipes),'base_path':base,'revision':os.environ.get('GITHUB_SHA')})+'\n')
    print(f'Built {len(recipes)} recipes at {out} (base {base})')
if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--base-path',default='/recipes/'); args=parser.parse_args(); build(args.base_path)
