#!/usr/bin/env python3
"""Import verified ChatGPT source artifacts. Never invent missing material."""
import hashlib,json
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def line(kind,text): return {'type':'line','parts':[{'type':kind,'text':text}]}
def section(text): return {'type':'section','text':text}
def save(slug,title,categories,source,url,blocks,attribution,servings=None,**metadata):
    p=ROOT/source
    record={'schema_version':1,'slug':slug,'title':title,'subtitle':None,'categories':categories,'tags':[],'source_url':url,'attribution':[{'type':'text','text':attribution}] if attribution else [],'servings':servings,'blocks':blocks,'notes':[],'variations':[],'photos':[],'metadata':{'imported':'2026-11-01','revised':None,'source_file':source,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'origin':'ChatGPT source artifact',**metadata}}
    out=ROOT/'recipes'/f'{slug}.json'
    if out.exists(): raise SystemExit(f'Refusing to overwrite {out}')
    out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
class Bibimbap(HTMLParser):
    def __init__(self): super().__init__();self.active=None;self.text='';self.blocks=[];self.attribution=''
    def handle_starttag(self,t,attrs):
        if t=='h2':self.active='section';self.text=''
        if t=='p':
            self.active={'ingredient':'ingredient','step':'instruction','subtitle':'attribution'}.get(dict(attrs).get('class'));self.text=''
    def handle_endtag(self,t):
        if t in ('h2','p') and self.active:
            if self.active=='attribution':self.attribution=self.text
            elif self.active=='section':self.blocks.append(section(self.text))
            else:self.blocks.append(line(self.active,self.text))
            self.active=None
    def handle_data(self,d):
        if self.active:self.text+=d

def main():
    source='archive/chatgpt/dolsot_bibimbap_2_servings.html';p=Bibimbap();p.feed((ROOT/source).read_text())
    save('dolsot-bibimbap-for-two','Dolsot Bibimbap for Two',['Korean','Meat'],source,'https://chatgpt.com/library/file/libfile_57991992614481918a550c99cfa2441e',p.blocks,p.attribution,'2 servings',source_filename='dolsot_bibimbap_2_servings.html',version='2026-08-22 final recovered HTML; oven-heated bowls; no fernbrake or bellflower root')
    start=next(i for i,b in enumerate(p.blocks) if b.get('text')=='Daikon Radish Salad (Musaengchae)')
    end=next(i for i in range(start+1,len(p.blocks)) if p.blocks[i]['type']=='section')
    save('musaengchae','Musaengchae (Daikon Radish Salad)',['Korean','Vegetables'],source,'https://chatgpt.com/library/file/libfile_57991992614481918a550c99cfa2441e',p.blocks[start+1:end],p.attribution,None,source_filename='dolsot_bibimbap_2_servings.html',source_section='Daikon Radish Salad (Musaengchae)',version='Exact side dish from the bibimbap source; not an independently revised recipe')
    source='archive/chatgpt/cod-and-potato-chowder.txt';text=(ROOT/source).read_text();lines=text.splitlines()
    first=lines.index('6 stalks celery + 1 large Vidalia onion + 1 leek, chopped and softened in ½ stick (4 Tbsp) butter');last=lines.index('Remove the bay leaf and taste before adding much salt, particularly if you used broth or Better Than Bouillon.')
    ingredient_indices={0,2,4,5,6,7,9,11,12,15,16,18,20,21,22}
    blocks=[line('ingredient' if i in ingredient_indices else 'instruction',s) for i,s in enumerate(lines[first:last+1])]
    blocks.extend([section('Notes'),{'type':'note','text':lines[last+2]}])
    save('cod-and-potato-chowder','Cod and Potato Chowder',['Soups','Seafood'],source,'https://chatgpt.com/c/6ac2adea-17a0-83ea-a7f4-1102d70f26aa',blocks,lines[6],'About 4 generous servings',version='Only complete response in the recovered 2026-10-04 conversation; no explicit final approval visible',source_format='Rendered conversation transcription')
    source='archive/chatgpt/fish_chowder_final.pdf'
    # All wording below comes from the downloaded PDF. Ingredients are moved beside
    # their first use; the instruction sequence and quantities remain unchanged.
    ingredients=['2–3 strips bacon, chopped','1 tbsp butter','1 cup onion, finely chopped','½ cup celery, finely chopped','1 tbsp flour','1¼ cups water','¾ tsp Better Than Bouillon vegetable base','1 bay leaf','¼–½ tsp dried thyme','1½ cups potatoes, peeled and diced small','0.6 lb haddock, cut in bite-size pieces','¾ cup half-and-half','Black pepper, to taste']
    steps=['Cook bacon until crisp; remove pieces and leave the fat in the pot.','Add butter, then onion and celery; cook 10–12 min until lightly browned.','Sprinkle in flour; stir and cook 1 minute.','Add water, bouillon, bay leaf, and thyme.','Add potatoes; simmer 12–15 min until just tender.','Simmer uncovered 3–5 min to concentrate the base.','Cool and refrigerate overnight.','Reheat gently, 5–10 min.','Add haddock; simmer 3–4 min.','Add half-and-half; heat gently. Do not boil.','Return bacon; remove bay leaf.','Taste; add pepper and salt only if needed.']
    blocks=[section('Day 1 – Build the Base')]
    uses={0:[0],1:[1,2,3],2:[4],3:[5,6,7,8],4:[9],8:[10],9:[11],11:[12]}
    for i,s in enumerate(steps):
        if i==7:blocks.append(section('Day 2 – Finish'))
        blocks.extend(line('ingredient',ingredients[j]) for j in uses.get(i,[]));blocks.append(line('instruction',s))
    blocks.append(section('Notes'))
    blocks.extend({'type':'note','text':s} for s in ['Bouillon plus bacon may provide enough salt already.','Mash a few potatoes into the broth if you want it thicker.','Optional at the end: a tiny splash of lemon juice or a pinch of paprika.'])
    save('fish-chowder','Fish Chowder',['Soups','Seafood'],source,'https://chatgpt.com/library/file/libfile_ef048449ed208191acbffe574b1c591c',blocks,'Developed with ChatGPT. Haddock and bacon; prepare the base the day before.','2–3 servings',source_filename='fish_chowder_final.pdf',version='Final titled artifact; haddock with bacon, two-day method',ingredient_relayout=True)
if __name__=='__main__':main()
