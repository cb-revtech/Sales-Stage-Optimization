"""Salesforce administrator views of the approved process requirements."""
import html,re
E=lambda value:html.escape(str(value),quote=True)
GROUPS=[
 ('fields','New fields','Create or reuse the missing data capture on the correct object.','New / confirm reuse'),
 ('rename','Rename and reuse','Change labels and reuse existing storage; retain data and relationships.','Relabel / reuse'),
 ('move','Move and remove requirements','Move capture to the right point in the process and retire requiredness, not history.','Move / remove'),
 ('inputs','Picklists and input types','Update permitted inputs, dependencies and historical mappings.','Change inputs'),
 ('automation','Automations and integrations','Configure event-driven updates, notifications, calculations and handoffs.','Automation'),
 ('validation','Validations and stage gates','Enforce required evidence and allowed transitions across every write path.','Validation')]
EXPLICIT={
 'fields':[8,18,37,41,110,112,113,114,115,116,131],
 'rename':[21,30,118], 'move':[26,111], 'inputs':[33,39,119],
 'automation':[2,13,15,17,19,20,22,24,32,35,109,120,121,126,130,132],
 'validation':[3,4,5,6,7,9,10,11,23,25,34,104,122,123]}
RENAME_FROM={43:'Why DDN',44:'SE User',45:'Solution',47:'Economic Justification',48:'Procurement (Close Plan)',49:'Sharepoint Links',50:'IPG Finalized and submitted',51:'SE Next Steps',52:'Budget holder',56:'PO Processing Status',67:'Order No.',68:'Invoice #',69:'PS Case',72:'Primary Partner',77:'Partner',79:'Description (Influence)',80:'Partner Stage (Influence)',81:'Primary Contact (Partner)',82:'Technical Contact (Partner)',89:'Reason Lost',90:'Lost Reason Explanation',91:'If Primary Competition is Other, Fill:'}
LABELS={43:'Identify Pain',44:'Primary SE',45:'Technical Value',47:'Business Value',48:'Paper Process',49:'SharePoint Link',50:'IPG Finalized',51:'Sales Engineer Next Steps',52:'Economic Buyer',56:'Order Review Status',67:'Sales Order Reference',68:'Invoice Reference',69:'Deployment Case Link',72:'Transacting Partner',77:'Associated Account',79:'Association Description / Plan',80:'Association Engagement Status',81:'Association Sales Contact',82:'Association Technical Contact',89:'Loss Reason',90:'Loss Reason Details',91:'Competitor Detail (if Other)'}
def category(row):
 n=int(row[1].split('-')[-1]);req=row[3]
 for key,ids in EXPLICIT.items():
  if n in ids:return key
 if n in LABELS or req.startswith(('Change the existing field label','Relabel','Reuse/relabel')):return 'rename'
 if req.startswith('Change inputs:'):return 'inputs'
 if req.startswith(('Update calculation:','Calculate')):return 'automation'
 if req.startswith(('Add:','Add /','Add ·','Add only')):return 'fields'
 raise ValueError('Unclassified requirement '+row[1])

def title(row):
 n=int(row[1].split('-')[-1]);req=row[3]
 if n in LABELS:return LABELS[n]
 if n in {84,85,86,87,88}:return {84:'Resources Engaged',85:'Incumbent Vendor(s)',86:'OK to Interview (Win/Loss)?',87:'Contact for Win/Loss Interview',88:'WL Reason Cannot Approach'}[n]
 if row[2].startswith('Field definition'):
  if ': ' in req:return req.split(': ',1)[1].split('. ',1)[0].rstrip('.')
  return req.split('. ',1)[0]
 return row[2].split(' / ',1)[-1]

# A requirement can describe several fields; field subrequirements and umbrella
# requirements share the same display row instead of duplicating the field.
FIELD_REQUIREMENTS={
 8:['POC Status','POC Updates'],18:['Value Tracking Start Date','Value Realization Plan','Target Value Realization Date','Value Achieved?','Value Realization Context','Value Outcome Confirmed Date'],
 30:['Transacting Partner'],37:['Route to Market','Indirect Route Type'],41:['Primary GSS'],
 110:['Opportunity Conversion Lifecycle'],112:['Quote Purpose'],113:['Timing Urgency','Urgency Reason'],114:['Competitor Pricing'],
 115:['Account · Account Tier','Account · RevOps Notes','Account · Primary DDN Partner Account Manager','Account · Partner Technical Lead','Account · Partner Admin Contact'],
 116:['Pipeline Date','Pipeline Entry Amount'],
 131:[f'Stage {n} Date' for n in range(7)],
 132:['AE Next Steps'],
 118:['Transacting Partner','Association Sales Contact','Association Technical Contact'],
 119:['Opportunity Source','Technical Outcome','Indirect Route Type'],
 33:['Won Reason','Loss Reason','Competitor Lost To'],
}
# Inputs and current purpose for process changes (not assertions that the target
# automation is already deployed). Updated behavior comes from the requirements.
CONTROLS={
 2:('Stage; Forecast Category (Sales)','Existing sales forecast classification; current automation must be checked.'),
 3:('Intake origin, Opportunity Owner, SAL Status / AE, decision actor/time','Existing ownership and SAL controls support seller review.'),
 4:('Five existing CHAMPS answers; preserved intake origin','Existing qualification fields; ownership can change after inbound intake.'),
 5:('CHAMPS, Use Case, Route to Market, AE / SE, Contact Roles','Existing Discovery evidence and contacts support qualification.'),
 6:('Stage, Quote Purpose, configuration, commercial authority','Existing CPQ quoting and Primary Quote synchronization.'),
 7:('Identify Pain, Competitors, Technical Value, Champion, Decision Criteria, SharePoint Link, Description, POC decision','Existing technical-fit evidence and POC engagement.'),
 9:('Technical Outcome, selected configuration, Operational Value, Economic Buyer, Decision Process','Existing technical evaluation and buyer evidence.'),
 10:('Business Value, Primary Quote, Paper Process, Requested Install Date','Existing proposal evidence and CPQ-driven Amount / Products.'),
 11:('IPG, PO Secured, PO File, final agreements, shipping / delivery requests','Existing procurement and file capture; confirm mapped controls.'),
 13:('Order Review Status, Order, deployment Case, OM / GSS plan','Existing order reconciliation and OM booking authority.'),
 15:('Verified receipt for all in-scope items; Order / Case evidence','Existing Order delivery and invoice facts are distinct.'),
 17:('Stage 6; existing PS Case and Order Case(WO) relationships','Existing Case structures support deployment work.'),
 19:('Next Step, SE Next Step, Close Date, review actor/time','Existing seller and SE next actions and expected close date.'),
 20:('Case title, description, Opportunity link; Stage 2–5','Existing technical-risk fields and Case infrastructure.'),
 21:('Account, Opportunity, role, classification, plan and contacts','Partner Opportunity Influence currently records partner participation.'),
 22:('First qualifying association / registration; creation owner; booking event','Existing contribution logic and management override history.'),
 23:('Active NVIDIA association; NVIDIA Engagement / Status','Existing NVIDIA engagement fields on Opportunity.'),
 24:('Won Reason, Business Value, incumbent, recognition and interview inputs','Existing Win/Loss rollout; verify delivered fields and notifications.'),
 27:('Approved field labels, choice crosswalks, record types and dependent integrations','Existing historical records and downstream consumers use current metadata.'),
 28:('Approved requirements; allowed and denied UI / import / integration scenarios','Existing stages, CPQ, integrations and reporting need regression coverage.'),
 32:('POC Updates; prior text, author and timestamp','Existing field history capability must be checked for full-text retention.'),
 34:('Opportunity Type; win/loss event; interview Yes/No, Contact or reason','Existing Win/Loss interview capture may already be deployed.'),
 35:('Outcome, Amount, recipients, deadlines and outcome event ID','Existing Win/Loss notification rollout; implement only missing behavior.'),
 104:('Opportunity Source and applicable Sourcing User / Campaign / Partner','Existing source attribution and sourcing lookups.'),
 109:('MAP MQL or PAX.AI AQL event; Contact and episode ID','Existing Contact lifecycle; integration mappings require verification.'),
 120:('Active association; partner Account manager / technical lead; partner AND territory coverage','Existing account ownership and opportunity-team sharing.'),
 121:('Direct route, pricing event, sales manager and partner coverage','Existing commercial approvals; notification does not replace them.'),
 122:('Source / Sourcing Partner, acceptance, registration, Other choice and explanation','Source, registration and association roles are distinct existing concepts.'),
 123:('Budgetary / Best and Final; Stage; customer need, indicative scope and authority','Existing CPQ quote process and commercial authority matrix.'),
 124:('First Stage 1 Amount / At; Opportunity ID; linked enhancement Cases','Current Opportunity Amount changes as a deal develops; multiple Cases may reference one deal.'),
 125:('Nine business roles; object CRUD, record scope, field access and system entitlements','Existing Salesforce grants have not been audited against the target matrix.'),
 126:('Task Type, Subject, owner, Due Date, customer/deal, Status / disposition and Comments','Existing Task form supports activity capture; calendar sync remains outstanding.'),
 127:('Association and registration history; booked credit; NVIDIA / contact / logistics links','Existing contribution rules, multi-partner attribution and integrations.'),
 128:('Start, Work, Close and Grow the deal; 47 existing lessons','Existing reminders, scenarios, full lessons, practice and knowledge checks.'),
 130:('Requested stage; missing evidence; field permissions; crossed gates','Existing progression validation identifies incomplete evidence but does not provide a guided input screen.'),
 129:('Calendar ownership; Task mappings; source crosswalk; tier criteria; authority matrix','These mappings and the calendar integration remain unresolved dependencies.'),
}

def plain(value):
 return html.unescape(re.sub(r'<[^>]*>',' ',value)).strip()

def register(source,account_rows):
 fields={}
 for name,body in re.findall(r'<tr data-field="([^"]+)">(.*?)</tr>',source,re.S):
  cells=re.findall(r'<td[^>]*>(.*?)</td>',body,re.S)
  if len(cells)==5:fields.setdefault(html.unescape(name),[]).append(cells)
 for name,body in re.findall(r'<tr data-quote-field="([^"]+)">(.*?)</tr>',source,re.S):
  c=re.findall(r'<td[^>]*>(.*?)</td>',body,re.S)
  first=re.sub(r'<span class="change-tag.*?</span>','',c[0])+'<small>CPQ Quote</small>'
  fields[html.unescape(name)]=[[first,c[1],'New proposed Quote field.','<span class="change-tag added">New field</span>',c[2]+' '+c[3]]]
 for name,kind,inputs,purpose in account_rows:
  if 'Account · '+name in fields:continue
  fields['Account · '+name]=[['<strong>'+E(name)+'</strong><small>'+E(kind)+'</small>',E(inputs),'Not applicable — new proposed Account field.','<span class="change-tag added">New field</span>',E(purpose)]]
 return fields

def choose(fields,name,key):
 options=fields[name]
 # Prefer the actual new/relabel/input definition over an earlier "move away"
 # row. The stage source can describe a field in several lifecycle locations.
 words={'fields':('New','new'),'rename':('Relabel','relabel'),'inputs':('Change inputs',),'move':('Move','Moved','Remove','Consolidate'),'automation':('calculation','Calculated')}.get(key,())
 chosen=next((c for c in options if any(w in plain(c[3]) for w in words)),options[0])
 return list(chosen)

def entries(data,source,account_rows):
 fields=register(source,account_rows); groups={key:{} for key,*_ in GROUPS}
 def add(key,name,cells,number):
  entry=groups[key].setdefault(name,{'cells':cells,'refs':set()})
  entry['refs'].add(f'BR-SS-{number:03}')
 for row in data[1:]:
  n=int(row[1].split('-')[-1]);key=category(row)
  names=FIELD_REQUIREMENTS.get(n)
  if row[2].startswith('Field definition'):names=[title(row)]
  if n==26:
   # Use the actual moved/removed rows, including inputs and previous purpose.
   for name,options in fields.items():
    selected=next((c for c in options if any(w in plain(c[3]) for w in ['Move','Moved','Remove','Consolidate'])),None)
    if selected:add('move',name,list(selected),n)
   continue
  if n==111:
   for name in ['SAL AE','SAL Type','SAL Status','SAL Submission Date','SAL Start Date','SAL Completion Date','SAL Accepted Date','SAL Rejected Date','SAL Notes']:
    c=choose(fields,name,'move');c[3]='<span class="change-tag">Move / validate</span>'
    add('move',name,c,n)
   continue
  if names:
   for name in names:
    assert name in fields,(row[1],name)
    cells=choose(fields,name,key)
    if n==119 and name=='Opportunity Source':cells[3]='<span class="change-tag">Change inputs</span>'
    if n==119 and name=='Indirect Route Type':
     cells[3]='<span class="change-tag">Clarify CSP</span>';cells[4]+=' CSP includes hyperscalers; no new category is introduced.'
    if name in ['Pipeline Date','Pipeline Entry Amount']:cells[2]='New first-entry snapshot; verify suitable existing history/storage.'
    add(key,name,cells,n)
  else:
   if n==39:
    inputs='Retain the existing Product Type choices; allow multiple selections.';current='Existing single-select Opportunity Product Type.'
   elif n==25:
    inputs='Loss Reason, details, competitor, next action and conditional interview capture';current='Existing loss fields and Win/Loss review process.'
   else:
    assert n in CONTROLS,('Missing process context',row[1]);inputs,current=CONTROLS[n]
   label=title(row)
   if n==20:label='Product-feature request Cases'
   if n==21:label='Associated accounts'
   cells=['<strong>'+E(label)+'</strong><small>Process / configuration</small>',E(inputs),E(current),'<span class="change-tag">'+E(next(g[3] for g in GROUPS if g[0]==key))+'</span>',E(row[3])]
   add(key,label,cells,n)
 return groups

def change_log(data,source,account_rows):
 groups=entries(data,source,account_rows)
 out='<section class="stage" id="change-log"><header class="stagehead"><div><p class="label">Implementation by action</p><h2>Change log</h2></div></header><div class="body">'
 for key,label,description,tag in GROUPS:
  rows=groups[key]
  out+='<details class="audit-group change-group" id="changes-'+key+'"><summary>'+E(label)+'<span>'+str(len(rows))+' items</span></summary><div class="field-register-wrap"><table class="field-register"><thead><tr>'+''.join('<th scope="col">'+h+'</th>' for h in ['Field / type','Inputs','Current purpose','Change','Updated purpose / placement'])+'</tr></thead><tbody>'
  for name,entry in rows.items():
   c=list(entry['cells']);refs=sorted(entry['refs'])
   c[0]+='<small class="requirement-refs">'+', '.join('<a href="#requirement-'+ref+'">'+ref+'</a>' for ref in refs)+'</small>'
   out+='<tr data-change-item="'+E(name)+'" data-requirements="'+' '.join(refs)+'">'+''.join('<td>'+cell+'</td>' for cell in c)+'</tr>'
  out+='</tbody></table></div></details>'
 return out+'</div></section>'
