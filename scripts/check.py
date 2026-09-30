#!/usr/bin/env python3
"""Validate source preservation, content completeness and internal references."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import hashlib,re,sys,json,csv,html
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'content'))
from learning import MODULES
from industry import INDUSTRY_TERMS
from course_design import DESIGN, CAVEATS
from reference import STAGES,TERMS,TERM_EXAMPLES,TERM_TITLES,DEFINITION_TEXT,DEFINITION_EXAMPLES
from process_updates import APPROVED,EXCLUDED,ROLE_ROWS,EXTRA_DEFINITIONS,CHANGES
from enablement_updates import apply,STREAMS,STREAM_OVERVIEWS
apply(MODULES,DESIGN,CAVEATS,TERM_TITLES,DEFINITION_TEXT,DEFINITION_EXAMPLES)
class Scan(HTMLParser):
    def __init__(self): super().__init__(); self.ids=[]; self.links=[]; self.assets=[]; self.layers=[]
    def handle_starttag(self,t,a):
        a=dict(a)
        if 'id' in a:self.ids.append(a['id'])
        if t=='a' and 'href' in a:self.links.append(a['href'])
        if t=='script' and 'src' in a:self.assets.append(a['src'])
        if t=='link' and 'href' in a:self.assets.append(a['href'])
        if 'class' in a:self.layers.extend(c for c in a['class'].split() if c in ['quick','scenario','course'])
scans={}
for f in ROOT.glob('*.html'):
    scan=Scan();scan.feed(f.read_text());scans[f.name]=scan
    assert len(scan.ids)==len(set(scan.ids)),f'Duplicate IDs in {f.name}'
for name,scan in scans.items():
    for link in scan.links+scan.assets:
        u=urlsplit(link)
        if u.scheme or u.netloc:continue
        dest=u.path or name
        if u.path:assert (ROOT/u.path).exists(),f'Missing {link} in {name}'
        if dest in scans and u.fragment and not u.fragment.startswith('filter-'):
            assert unquote(u.fragment) in scans[dest].ids,f'Missing anchor {link} in {name}'
    for link in scan.links:
        if link.startswith('#filter-'):assert link[8:] in {s[0] for s in STAGES}|{'ongoing'},link
index=(ROOT/'index.html').read_text()
# Check protected parts of the original specification, rather than disallow approved edits.
base=(ROOT/'content/system-base.html').read_text()
def field_rows(text,name):
    return re.findall(r'<tr data-field="'+re.escape(name)+r'">.*?</tr>',text,re.S)
for name in ['Type','Business Value','CHAMPS · Challenge','CHAMPS · Authority','CHAMPS · Money','CHAMPS · Priority','CHAMPS · Stack / Storage','Incumbent Vendor(s)','Resources Engaged','Partner Contribution (Mgt)']:
    assert field_rows(base,name),f'Baseline guard missing: {name}'
    assert field_rows(base,name)==field_rows(index,name),f'Excluded/stable field altered: {name}'
assert set(APPROVED)=={n for change in CHANGES for n in change[5]},'Approved changes not traced to implementation'
assert set(APPROVED).isdisjoint(EXCLUDED) and set(APPROVED)|set(EXCLUDED)==set(range(1,37))
for stale in ['Fulfillment Partner','Keep quoting disabled until Stage 2','Keep quoting disabled and Forecast','Quoting · Stages 2–5 only','every other nonblank source → Sourcing Partner','For deal registration, use the mapped partner-related Opportunity Source']:
    assert stale not in index,stale
for phrase in ['Pipeline Entry Amount','Pipeline Date','Account Tier','RevOps Notes','Partner Admin Contact','Primary DDN Partner Account Manager','Partner Technical Lead','Association Sales Contact','customer-confirmed preference','Calendar sync','Synergy']:
    assert phrase.lower() in index.lower(),phrase
for id in ['ongoing-meetings-detail','account-management','change-log']:assert id in scans['index.html'].ids
# The restored table, CSV and canonical data must agree; every requirement must be represented in the collapsed action log.
data=json.loads(re.search(r'<script[^>]*id="requirements-data"[^>]*>(.*?)</script>',index,re.S)[1])
with (ROOT/'downloads/implementation-requirements.csv').open(encoding='utf-8-sig',newline='') as f:
    assert list(csv.reader(f))==data,'Export differs from canonical requirements'
ids=re.findall(r'data-requirement="([^"]+)"',index)
assert len(ids)==len(set(ids))==len(data)-1 and set(ids)=={r[1] for r in data[1:]},'Changelog coverage'
table=re.search(r'<table id="requirements-table">(.*?)</table>',index,re.S)[1]
actual=[[html.unescape(re.sub(r'<[^>]+>','',c)) for c in re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>',r,re.S)] for r in re.findall(r'<tr[^>]*>(.*?)</tr>',table,re.S)]
assert actual==data,'Visible requirements table differs from export'
assert 'id="download-requirements" href="downloads/implementation-requirements.csv" download="GTM-Implementation-Requirements.csv"' in index
nav=re.search(r'<nav[^>]*aria-label="Document sections"[^>]*>(.*?)</nav>',index,re.S)[1]
assert re.findall(r'<a[^>]*href="([^"]+)"',nav)[-2:]==['#change-log','#implementation-requirements'],'Implementation menu order / target'
assert index.index('<section class="stage" id="change-log">')<index.index('<section class="stage" id="implementation-requirements">')
assert '<section ' not in index[index.index('<section class="stage" id="implementation-requirements">')+70:],'Requirements card must be last'
from change_log import GROUPS,entries
from process_updates import ACCOUNT_ROWS,REMOVED_IMPLEMENTATION_IDS
from admin_views import OBJECT_ROWS,SYSTEM_ROWS,ROLE_DEFS
log=index[index.index('<section class="stage" id="change-log">'):index.index('<section class="stage" id="implementation-requirements">')]
refs={ref for ids in re.findall(r'data-requirements="([^"]+)"',log) for ref in ids.split()}
assert refs=={r[1] for r in data[1:]},'A requirement is missing from the action log'
assert 'admin-change-card' not in log and 'admin-buckets' not in log
for key,*_ in GROUPS:
    assert f'<details class="audit-group change-group" id="changes-{key}">' in log,'Groups must start collapsed'
    group=log.split(f'id="changes-{key}">',1)[1].split('<details class="audit-group change-group"',1)[0]
    count=int(re.search(r'<summary>.*?<span>(\d+) items</span>',group,re.S)[1])
    assert count==group.count('data-change-item='),f'Count mismatch: {key}'
    assert '<table class="field-register">' in group
    assert re.findall(r'<th scope="col">(.*?)</th>',group)[:5]==['Field / type','Inputs','Current purpose','Change','Updated purpose / placement']
assert 'Given any stage outside 2–5' not in index,'Stale quoting acceptance criterion'
by_id={r[1]:r for r in data[1:]}
assert 'controlled Budgetary' in by_id['BR-SS-006'][8]
assert 'customer-confirmed preference' in by_id['BR-SS-009'][10]
assert len(GROUPS)==6
assert all(f'BR-SS-{n:03}' not in by_id for n in REMOVED_IMPLEMENTATION_IDS)
assert 'changes-access' not in log and 'changes-release' not in log
assert 'Access and reporting' not in log and 'Migration and release' not in log

assert len(OBJECT_ROWS)==len(SYSTEM_ROWS)==len(ROLE_DEFS)==9
assert {r[0] for r in OBJECT_ROWS}=={r[0] for r in ROLE_DEFS}
assert all(len(r)==7 for r in OBJECT_ROWS+SYSTEM_ROWS)
for id in ['object-matrix','field-access','system-matrix','configuration']:assert id in scans['permissions.html'].ids
assigned=[id for _,_,_,ids in STREAMS for id in ids]
assert len(assigned)==len(set(assigned)) and set(assigned)=={m['id'] for m in MODULES},'Four-stream coverage'
assert len(STREAMS)==4
assert set(STREAM_OVERVIEWS)=={s[0] for s in STREAMS}
for overview in STREAM_OVERVIEWS.values():assert len(overview['learn'])==3 and all(overview[k] for k in ['overview','takeaway','apply'])
for role,*_ in ROLE_ROWS:assert role in (ROOT/'permissions.html').read_text(),role
for page in ['index.html','definitions.html','enablement.html','permissions.html']:
    assert 'permissions.html' in (ROOT/page).read_text(),page
for layer in ['quick','scenario','course']:assert scans['enablement.html'].layers.count(layer)==len(MODULES)
assert len({m['id'] for m in MODULES})==len(MODULES)
for m in MODULES:
    assert len(m['steps'])==4 and all(' — ' in s for s in m['steps']),m['id']
    assert len(m['questions'])>=2 and len(m['reminder'])==3,m['id']
    assert all(m[k] for k in ['definition','distinction','scenario','weak','strong','practice','check','answer']),m['id']
    assert m['source'] in scans['index.html'].ids,m['source']
assert set(DESIGN)=={m['id'] for m in MODULES},'Course design coverage'
assert all(all(d[k] for k in ['goal','practice','model','question','answer','takeaway']) for d in DESIGN.values()),'Incomplete learning design'
assert set(CAVEATS)=={m['id'] for m in MODULES if m['note']},'Missing applicability guidance'
for s in STAGES:assert any(s[0] in m['stages'] for m in MODULES),f'Uncovered stage: {s[0]}'
assert set(t[0] for t in TERMS)==set(TERM_EXAMPLES),'Definition example coverage'
activities={'ongoing-quoting-detail','ongoing-conversion-detail','ongoing-primary-detail','ongoing-partners-detail','ongoing-next-detail','ongoing-logistics-detail','ongoing-risk-detail','ongoing-nvidia-detail','ongoing-contribution-detail','ongoing-buying-committee','ongoing-poc-detail','ongoing-product-detail','ongoing-ipg-detail','win-wire','case-current-state','case-value-realization'}
assert activities <= {m['source'] for m in MODULES},'Missing ongoing activity'
assert any(m['id']=='invoice' for m in MODULES),'Confirm order coverage'
print(f'PASS: 4 courses / {len(MODULES)} complete lessons, {len(MODULES)+len(TERMS)+len(STAGES)+len(INDUSTRY_TERMS)+len(EXTRA_DEFINITIONS)} definitions, all stage/activity coverage, unique IDs, internal links/assets and approved scope / protected baseline fields.')

# Approved Sales Ops decisions propagate to the process, learning and export.
from sales_ops_updates import APPROVED as OPS_APPROVED,REJECTED as OPS_REJECTED
assert OPS_APPROVED=={'1.1','1.2','1.3','1.5','3'}
assert OPS_REJECTED=={'1.4','2.1','2.2','4','5','6'}
for n in [130,131,132]:assert f'BR-SS-{n:03}' in by_id
for n in range(7):
    stage=index.split(f'id="s{n}"',1)[1].split('</section>',1)[0]
    assert f'data-field="Stage {n} Date"' in stage
assert 'id="stage-update-flow"' in index and 'missing required inputs' in index
assert 'Read-only history' in field_rows(index,'AE Next Steps')[0]
assert 'blank eligibility' in (ROOT/'enablement.html').read_text().lower()
assert 'Project Cancelled / Budget Lost' in by_id['BR-SS-025'][10]
assert 'except Stage 0 misqualification' in by_id['BR-SS-034'][8]
assert 'Stage 4 Date' in by_id['BR-SS-116'][8]
assert 'Required at loss; align vendor choices' not in index
assert 'Require Loss Reason, Loss Reason Details, Competitor Lost To and' not in index
for name in ['Requested Delivery Date','Estimated Shipping Date','Next Step Reviewed At','SE Next Step Reviewed At']:
    assert field_rows(base,name)==field_rows(index,name),f'Rejected change altered {name}'
for phrase in ['Advanced Stage Date','Invoice Status','Meeting Start','Meeting End']:
    assert phrase not in index,phrase
print('PASS: approved Sales Ops decisions, rejected field protections and implementation/export consistency.')

for n in range(7):
    assert f'id="term-stage-{n}-date" data-stages="s{n} ongoing"' in (ROOT/'definitions.html').read_text()

# Audit regressions: preserve approved skipped-stage conversion and platform-safe guidance.
for stale in ['SQL on first Stage 1 entry.', 'SQL on entry to Stage 1 or seller-direct',
              'complete business-fit discovery before quoting', 'Default Direct to the creating User',
              'connect Transacting Partner to the Order shipping workflow']:
    assert stale not in index, stale
assert '0 → 4 records SQL and Pipeline Date' in by_id['BR-SS-110'][8]
conversion=next(m for m in MODULES if m['id']=='conversion')
assert 'including valid skips' in conversion['reminder'][1]
assert 'Stage 1 Date remains blank' in DESIGN['conversion']['answer']
assert 'Stage 1 Date stays blank' in (ROOT/'definitions.html').read_text()
assert index.count('class="stage-gate"')==11
assert 'Roll Back Records' in index.split('id="implementation-requirements"')[0]
assert 'parent Opportunity ID' in index.split('id="implementation-requirements"')[0]
assert 'whole-record lock' in index.split('id="implementation-requirements"')[0]
assert 'both partner and geographic coverage' in by_id['BR-SS-120'][8]
for section in ['coverage-model','territory-setup','related-access','access-tests']:
    assert section in scans['permissions.html'].ids, section
permissions=(ROOT/'permissions.html').read_text()
for rule in ['one Territory assignment','union, not the required intersection',
             'FLS is per user/field, not per record', 'Edit Tasks', 'Dual-role user']:
    assert rule in permissions, rule
print('PASS: audit consistency, valid-skip SQL, stage readability and Salesforce coverage safeguards.')

# The slide is intentionally a shorter view of the unchanged detailed field set.
slide=re.search(r'<tr><th scope="row" class="slide-row-label">Fields<small>.*?</tr>',index,re.S)[0]
slide_cells=re.findall(r'<td class="slide-fields">.*?</td>',slide,re.S)
assert len(slide_cells)==11
labels=[[html.unescape(re.sub(r'<[^>]+>','',item)) for item in re.findall(r'<span\b[^>]*>.*?</span>',cell,re.S)] for cell in slide_cells]
assert labels[0]==['Opportunity Name','Type','Amount','Opportunity Source','Opportunity Owner']
assert labels[1]==['CHAMPS: Challenge, Authority, Money, Priority, Stack / Storage']
assert 'Pipeline Entry Amount' in labels[2] and not any('Pipeline Date' in x for x in labels[2])
assert not any(x.startswith('Stage ') and x.endswith(' Date') for cell in labels[:8] for x in cell)
assert not any('Deployment Case' in x for x in labels[7])
assert 'Deployment Case Link' in labels[8] and 'Deployment Case Link' in labels[9]
assert 'Deployment Case · Stages 7–8' in index and '.ongoing-deployment{grid-column:9/span 2;' in index
stage6=index.split('id="s6"',1)[1].split('id="s7"',1)[0]
stage7=index.split('id="s7"',1)[1].split('id="s8"',1)[0]
assert 'data-field="Deployment Case Link"' not in stage6
assert 'Create or link the coordinating PS deployment Case' not in stage6
assert 'data-field="Deployment Case Link"' in stage7
assert 'For entry to Stage 7, find or provision the coordinating deployment Case' in stage7
assert 'Stage 7' in by_id['BR-SS-017'][3] and 'Stage 7' in by_id['BR-SS-069'][8]
assert 'from Stage 7' in by_id['BR-SS-061'][8]
assert 'Create or link one coordinating Case on entry to Stage 7.' in (ROOT/'enablement.html').read_text()
print('PASS: simplified slide and Stage 7 deployment timing across process, learning and requirements.')
