// Test the shipped script against a small DOM fixture, including storage failure.
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const vm = require('node:vm');
// Fixed fixtures keep future recipe additions from requiring test edits.
const recipes = [
  {title:'Cod Chowder',categories:['Soups','Seafood']},
  {title:'Chicken Chowder',categories:['Soups','Meat']},
  {title:'Fish Chowder',categories:['Soups','Seafood']},
  {title:'Dolsot Bibimbap',categories:['Korean','Meat']},
  {title:'Musaengchae',categories:['Korean','Vegetables']},
  {title:'Waffles',categories:['Breakfast']},
  {title:'Crème Soup',categories:['Soups']}
];
class Element {
  constructor(dataset={}) { this.dataset=dataset; this.hidden=false; this.value=''; this.attributes={}; this.listeners={}; }
  addEventListener(type,fn) { this.listeners[type]=fn; }
  setAttribute(k,v) { this.attributes[k]=v; }
  focus() { this.focused=true; }
  fire(type) { this.listeners[type]?.(); }
}
function fixture(query='', storageFails=false) {
  const cards=recipes.map(r=>new Element({title:r.title.toLowerCase(),categories:JSON.stringify(r.categories)}));
  const letters=[...new Set(recipes.map(r=>r.title[0]))];
  const groups=letters.map(letter=>{const e=new Element();e.id=`letter-${letter}`;e.querySelectorAll=()=>cards.filter((_,i)=>recipes[i].title[0]===letter);return e;});
  const filters=['',...new Set(recipes.flatMap(r=>r.categories))].map(category=>new Element({category}));
  const selectors=Object.fromEntries(['.contrast-toggle','.print-button','#search','#result-count','#clear-search','.search-wrap','.filters','#empty-state','#reset-filters'].map(k=>[k,new Element()]));
  const doc={documentElement:{classList:{toggle(){}}},querySelector(s){return selectors[s]||new Element();},querySelectorAll(s){return s==='.recipe-card'?cards:s==='.letter-group'?groups:filters;}};
  const history={replaceState(_a,_b,url){this.url=url;}};
  vm.runInNewContext(readFileSync('static/site.js','utf8'), {document:doc,location:{href:`https://example.com/recipes/${query}`,search:query},URL,URLSearchParams,history,window:{print(){}},localStorage:{getItem(){if(storageFails)throw Error('blocked');return null;},setItem(){if(storageFails)throw Error('blocked');}}});
  return {cards,filters,selectors,history};
}
let f=fixture('',true);assert.equal(f.cards.filter(e=>!e.hidden).length,recipes.length);
f.selectors['#search'].value='CHOWDER';f.selectors['#search'].fire('input');assert.equal(f.cards.filter(e=>!e.hidden).length,3);
f.filters.find(e=>e.dataset.category==='Seafood').fire('click');assert.equal(f.cards.filter(e=>!e.hidden).length,2);
f.selectors['#search'].value='no-such-recipe';f.selectors['#search'].fire('input');assert.equal(f.cards.filter(e=>!e.hidden).length,0);assert.equal(f.selectors['#empty-state'].hidden,false);
f.selectors['#reset-filters'].fire('click');assert.equal(f.cards.filter(e=>!e.hidden).length,recipes.length);assert.equal(f.selectors['#search'].focused,true);
f=fixture('?category=Korean');assert.equal(f.cards.filter(e=>!e.hidden).length,2);
f=fixture('?category=unknown&q=waffles');assert.equal(f.cards.filter(e=>!e.hidden).length,1);assert.ok(!f.history.url.searchParams.has('category'));
f=fixture('?q=creme');assert.equal(f.cards.filter(e=>!e.hidden).length,1);
console.log('Search: title matching, category intersection, URL initialization, empty state, reset, and blocked storage passed.');
