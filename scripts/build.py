#!/usr/bin/env python3
"""Build static companion pages. No third-party packages or server required."""
from pathlib import Path
import html
import csv
import json
import re
import sys
import unicodedata
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'content'))
from learning import MODULES
from industry import INDUSTRY_TERMS
from course_design import DESIGN, CAVEATS
from reference import STAGES, TERMS, TERM_TITLES, TERM_EXAMPLES, DEFINITION_TEXT, DEFINITION_EXAMPLES
from process_updates import system, EXTRA_DEFINITIONS
from admin_views import permissions_page
from enablement_updates import apply, STREAMS, STREAM_OVERVIEWS
from deployment_updates import learning as apply_deployment_timing
apply(MODULES, DESIGN, CAVEATS, TERM_TITLES, DEFINITION_TEXT, DEFINITION_EXAMPLES)
apply_deployment_timing(MODULES, DESIGN, DEFINITION_TEXT, DEFINITION_EXAMPLES, STAGES)
E=lambda s:html.escape(str(s),quote=True)
M={m['id']:m for m in MODULES}
S={s[0]:s for s in STAGES}
STREAM_NAMES={mid:title for _,title,_,ids in STREAMS for mid in ids}
def slug(s):
    return re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()).strip('-')
def nav(page):
    return '<nav class="gtm-nav" aria-label="GTM pages">'+''.join(f'<a href="{url}"'+(' aria-current="page"' if key==page else '')+f'>{label}</a>' for key,url,label in [('stages','index.html','Sales Stages'),('definitions','definitions.html','GTM Definitions'),('enablement','enablement.html','Enablement'),('permissions','permissions.html','Access & Permissions')])+'</nav>'
def header(page):
    return '<header class="topbar"><span class="brand">GTM Process</span>'+nav(page)+'</header>'
def scope(m):
    return ' · '.join('Stage '+S[x][1] if x.startswith('s') and x[1:].isdigit() else S[x][2] for x in m['stages'] if x!='ongoing')
def stage_options():
    return ''.join(f'<option value="{s[0]}">{E(("Stage "+s[1]+" · " if s[0].startswith("s") and s[0][1:].isdigit() else "")+s[2])}</option>' for s in STAGES)+'<option value="ongoing">Ongoing activities</option>'
def filters(page,count,letters):
    label='definitions' if page=='definitions' else 'courses'
    result=f'''<div class="filters js-only" id="find"><div class="filter-grid"><div class="search-field"><label for="search">Search {label}</label><input type="search" id="search" placeholder="Try operational value, SAL, partner…" autocomplete="off" aria-controls="items"></div><div><label for="stage-filter">Stage or activity</label><select id="stage-filter"><option value="all">All stages &amp; activities</option>{stage_options()}</select></div><button type="button" id="reset">Reset</button></div>'''
    if page=='definitions':
        result+='<div class="alphabet" role="group" aria-label="Filter by first letter"><button type="button" data-letter="all" aria-pressed="true">All</button>'+''.join(f'<button type="button" data-letter="{l}" aria-pressed="false">{l}</button>' for l in letters)+'</div>'
        return result+'<p id="result-count" class="sr-only" role="status" aria-live="polite"></p></div>'
    return result+'<p id="result-count" class="sr-only" role="status" aria-live="polite"></p></div>'


def course(m):
    id=m['id']; d=DESIGN[id]
    out=f'<article class="lesson item" id="{id}" data-search="{E(STREAM_NAMES[id])}" data-stages="{" ".join(m["stages"])}" aria-labelledby="{id}-title"><header class="lesson-head"><h2 id="{id}-title">{E(m["title"])}</h2><p class="lesson-description">{E(DEFINITION_TEXT.get(id,m["definition"]))}</p></header><div class="lesson-body"><div class="lesson-overview">'
    out+='<section class="quick" aria-label="At a glance"><h3>At a glance</h3><ul>'+''.join('<li>'+E(r)+'</li>' for r in m['reminder'])+'</ul></section>'
    out+=f'<section class="scenario" aria-label="Scenario"><div class="scenario-heading"><h3>Scenario</h3><span>Illustrative</span></div><p>{E(m["scenario"])}</p></section></div>'
    out+=f'<details class="course" id="{id}-course"><summary><span>Full lesson</span></summary><div class="course-content"><div class="learning-goal"><span>What you’ll be able to do</span><p>{E(d["goal"])}</p></div><p class="key-point">{E(m["distinction"])}</p><h3>How to do it</h3><ol class="method">'
    for step in m['steps']:
        title,body=step.split(' — ',1)
        out+=f'<li><strong>{E(title)}</strong><p>{E(body)}</p></li>'
    out+='</ol>'
    if id in CAVEATS:out+=f'<p class="application-note">{E(CAVEATS[id])}</p>'
    out+='<h3>Questions to use</h3><div class="prompts">'+''.join('<p>“'+E(q)+'”</p>' for q in m['questions'])+'</div>'
    out+=f'<h3>What good looks like</h3><div class="examples"><div class="example"><strong>Too vague or unsupported</strong><p>{E(m["weak"])}</p></div><div class="example good"><strong>Specific and supported</strong><p>{E(m["strong"])}</p></div></div>'
    out+=f'<section class="practice" aria-labelledby="{id}-practice"><h3 id="{id}-practice">Put it into practice</h3><p>{E(d["practice"])}</p><details class="answer worked-answer"><summary>Compare your answer</summary><p>{E(d["model"])}</p></details></section>'
    out+=f'<section class="knowledge-check" aria-labelledby="{id}-check"><h3 id="{id}-check">Knowledge check</h3><p>{E(d["question"])}</p><details class="answer"><summary>Show answer and why</summary><p>{E(d["answer"])}</p></details></section>'
    out+=f'<div class="takeaway"><h3>Use this on your next deal</h3><p>{E(d["takeaway"])}</p></div></div></details></div></article>'
    return out

entries=[]
for m in MODULES:
    entries.append(dict(id=m['id'],title=TERM_TITLES[m['id']],meaning=m['definition'],distinction=m['distinction'],module=m,example=m['strong']))
for title,mid,meaning,distinction in TERMS:
    entries.append(dict(id='term-'+slug(title),title=title,meaning=meaning,distinction=distinction,module=M[mid],example=TERM_EXAMPLES[title]))
for s in STAGES:
    m=M[s[8][0]].copy();m['stages']=[s[0]];m['owner']=s[3];m['source']=s[0] if s[0]!='post' else 'case-value-realization'
    entries.append(dict(id='stage-'+s[0],title=('Stage '+s[1]+' — ' if s[0].startswith('s') else '')+s[2],meaning=s[5]+' '+s[6],distinction=s[7]+' Sales forecast: '+s[4]+'.',module=m,example=M[s[8][0]]['strong']))
for title,mid,meaning,example,aliases,source in INDUSTRY_TERMS:
    entries.append(dict(id='industry-'+slug(title),title=title,meaning=meaning,module=M[mid],example=example,aliases=aliases))
for title,mid,meaning,example in EXTRA_DEFINITIONS:
    id='term-'+slug(title)
    module=M[mid]
    if re.fullmatch(r'Stage [0-6] Date',title):module={**module,'stages':['s'+title.split()[1],'ongoing']}
    elif title in ['Pipeline Date','Pipeline Entry Amount']:module={**module,'stages':[f's{n}' for n in range(1,9)]+['ongoing']}
    if not any(e['id']==id for e in entries):entries.append(dict(id=id,title=title,meaning=meaning,module=module,example=example))
    DEFINITION_TEXT[id]=meaning
    if example:DEFINITION_EXAMPLES[id]=example
entries.sort(key=lambda e:e['title'].casefold())
assert len({e['id'] for e in entries})==len(entries)

def term(e):
    m=e['module'];id=e['id']
    example=e.get('example') if id.startswith('industry-') else DEFINITION_EXAMPLES.get(id)
    return f'''<article class="term item" id="{id}" data-stages="{' '.join(m['stages'])}" data-search="{E(e.get('aliases',''))}" data-letter="{e['title'][0].upper()}" aria-labelledby="{id}-title"><h2 id="{id}-title">{E(e['title'])}</h2><p class="meaning">{E(DEFINITION_TEXT.get(id,e['meaning']))}</p>'''+(f'<p class="definition-example"><span>Example</span> {E(example)}</p>' if example else '')+'</article>'

def definitions_page():
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Go-to-market definitions for sales stages, AI infrastructure and DDN terminology."><title>GTM Definitions · GTM Process</title><link rel="stylesheet" href="assets/navigation.css"><link rel="stylesheet" href="assets/learning.css"><script src="assets/learning.js" defer></script></head><body id="top" data-page="definitions"><a class="skip" href="#main">Skip to content</a>'''+header('definitions')+'''<div class="definitions-shell"><main id="main"><h1>GTM Definitions</h1><section id="library" aria-label="Definitions">'''+filters('definitions',len(entries),sorted(set(e['title'][0].upper() for e in entries)))+'''<div id="empty" class="empty" hidden><h2>No matching definitions</h2><button type="button" data-reset>Reset filters</button></div><div id="items">'''+''.join(term(e) for e in entries)+'''</div></section></main></div><a class="backtop" href="#top" aria-label="Back to top"><span aria-hidden="true">↑</span> Back to top</a></body></html>'''

def streams():
    out=''
    for i,(id,title,description,ids) in enumerate(STREAMS,1):
        overview=STREAM_OVERVIEWS[id]
        intro='<section class="stream-overview" aria-labelledby="'+id+'-overview"><h2 id="'+id+'-overview">Course overview</h2><p>'+E(overview['overview'])+'</p><div class="stream-outcomes"><div><h3>What you’ll learn</h3><ul>'+''.join('<li>'+E(x)+'</li>' for x in overview['learn'])+'</ul></div><div class="stream-takeaway"><h3>What you’ll take away</h3><p>'+E(overview['takeaway'])+'</p><h3>When to use it</h3><p>'+E(overview['apply'])+'</p></div></div></section>'
        out+=f'<details class="deal-stream" id="{id}"><summary><span class="stream-number">0{i}</span><span><strong>{E(title)}</strong><span class="stream-description">{E(description)}</span></span><span class="stream-toggle" aria-hidden="true">+</span></summary><div class="stream-lessons">'+intro+''.join(course(M[mid]) for mid in ids)+'</div></details>'
    return out

def page(kind):
    if kind=='definitions':return definitions_page()
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Practical sales enablement: at-a-glance reminders, illustrative scenarios and full courses."><title>Sales Enablement · GTM Process</title><link rel="stylesheet" href="assets/navigation.css"><link rel="stylesheet" href="assets/learning.css"><script src="assets/learning.js" defer></script></head><body id="top" data-page="enablement"><a class="skip" href="#main">Skip to content</a>'''+header('enablement')+'''<div class="enablement-shell"><main id="main"><h1>Sales Enablement</h1><section id="library" aria-label="Courses">'''+filters('enablement',len(MODULES),[])+'''<div id="empty" class="empty" hidden><h2>No matching courses</h2><button type="button" data-reset>Reset filters</button></div><div id="items">'''+streams()+'''</div></section></main></div><a class="backtop" href="#top" aria-label="Back to top"><span aria-hidden="true">↑</span> Back to top</a></body></html>'''

for kind in ['definitions','enablement']:(ROOT/(kind+'.html')).write_text(page(kind))
# Apply shared navigation and approved presentation changes; preserve system rules. Idempotent.
p=ROOT/'index.html';text=system((ROOT/'content/system-base.html').read_text())
text=re.sub(r'<nav class="gtm-nav".*?</nav>',lambda m:nav('stages'),text,count=1)
if 'assets/navigation.css' not in text:text=text.replace('</head>','<link rel="stylesheet" href="assets/navigation.css"></head>',1)
if 'class="gtm-nav"' not in text:
    marker='<span class="brand">Sales Stage Optimization</span>'
    assert text.count(marker)==1
    text=text.replace(marker,marker+nav('stages'),1)
text=text.replace('<span class="brand">Sales Stage Optimization</span>','<span class="brand">GTM Process</span>',1)
text=text.replace('<h1>Sales Stage Optimization</h1>','<h1>GTM Process</h1>',1)
text=text.replace('<title>Sales stage optimizations · FY27 H2 · Draft 02</title>','<title>Sales Stages · GTM Process</title>',1)
text=text.replace('<span class="tag">DRAFT 02 · FOR REVIEW · 18 SEP 2026</span>','',1)
text=text.replace('<span class="slide-draft">DRAFT FOR REVIEW</span>','',1)
p.write_text(text)
requirements=json.loads(re.search(r'<script[^>]*id="requirements-data"[^>]*>(.*?)</script>',text,re.S)[1])
(ROOT/'downloads').mkdir(exist_ok=True)
with (ROOT/'downloads/implementation-requirements.csv').open('w',encoding='utf-8-sig',newline='') as output:
    csv.writer(output).writerows(requirements)
(ROOT/'permissions.html').write_text(permissions_page(header))
print(f'Built 4 courses with {len(MODULES)} lessons and {len(entries)} definitions. Approved process updates and role permissions applied.')
