"""October 21 approved OM decisions, folded into the consolidated October release."""
import html
import re

DELIVERY = ('Stage 7 — Closed Won is the final won Opportunity stage. OM and GSS coordinate fulfillment, invoice reconciliation, deployment and customer receipt from Stage 7 through the linked Order and deployment Case. '
            'Record shipping, partial and complete receipt, installation, on-site/working confirmation and contractual acceptance as distinct actual events. '
            'Invoice Reference and Invoice Date are populated when issued; neither future delivery nor invoice issuance is a prerequisite for booking. Keep Forecast Category (Sales) = Won. '
            'Deployment and value realization continue on the Case without advancing or reopening the Opportunity. Preserve booked facts and authorized post-booking updates.')
VALUE_START = ('Store Value Tracking Start Date on the coordinating PS Case from the first verified complete on-site receipt of the in-scope order, using the actual Order/Case delivery evidence. '
               'Preserve it on retries, re-entry and reassignment. Do not stamp it from Stage 7 booking, Case creation or financial Invoice Date. '
               'Calculate Time to Value only when Value Achieved? = Yes and Value Outcome Confirmed Date is on or after that start; pending/No stays blank. Missing evidence is an integration exception, not a reason to reopen the Opportunity.')
WIN = ('Keep win evidence and applicable recognition/interview inputs at Stage 6. Trigger the Win wire notification only on successful OM booking from Stage 6 to Stage 7. '
       'Above $1M notify the Sales Manager and copy the AE; the manager submits the reviewed Win wire to Enablement / #win-wire within two business days of booking. '
       'Above $2M also require the full Deal Team Win Report. Resources Engaged remains required at ≥$1M on entry to Stage 6. '
       'Do not send on Stage 6 entry, failed booking, retry or re-entry; preserve the existing recipients and deduplicate the booked-win event. Interview capture remains New/Existing Business only, excluding renewals.')
INSTALL = ('On final quotes, capture whether installation matches shipping; require Installation Location when different. Budgetary quotes are exempt. '
           'Capture installation address, end-user legal entity, PS contact name and PS contact phone or email, and transfer them to Oracle and the deployment Case. '
           'Keep installation, bill-to and ship-to distinct. Reuse suitable existing fields; the added contact/entity fields do not acquire a new universal stage gate without an agreed requiredness mapping.')
SHIPPING = ('Before a hardware or mixed opportunity exits Stage 5, require Shipping Instructions and Logistics Coordinator contact name plus phone or email. '
            'Software-only opportunities are exempt. Reuse Delivery Notes where it can support the instruction separately and reliably; avoid duplicate storage. Carry the information to OM/Oracle and the deployment Case.')
PACKAGING = ('Before a hardware or mixed opportunity exits Stage 5, require Packaging Instructions and Customer Logistics contact name plus phone or email. '
             'Software-only opportunities are exempt. Keep these distinct from the logistics coordinator where the contacts differ; carry the information to OM/Oracle and the deployment Case.')
SUPPORT = ('Reuse Support Start Date and Expected Revenue Recognition Date. Synchronize the approved Support Start Date between Salesforce and Oracle and carry applicable dates and acceptance context to the deployment Case. '
           'Use shipment for the standard support start and the Deal Desk-approved CPQ/contract start where applicable; preserve the agreed source precedence and avoid a circular overwrite. '
           'Keep expected revenue recognition separate from booking; confirm the existing integration mapping before configuration.')


def walk(value, fn):
    if isinstance(value,str): return fn(value)
    if isinstance(value,list): return [walk(v,fn) for v in value]
    if isinstance(value,tuple): return tuple(walk(v,fn) for v in value)
    if isinstance(value,dict): return {k:walk(v,fn) for k,v in value.items()}
    return value


def normalize(text):
    preserved=['Remove Stage 8','removing Stage 8','existing Stage 8 records','former Stage 8']
    for i,value in enumerate(preserved):text=text.replace(value,f'__RETIRED_STAGE_{i}__')
    replacements={
      'Lock Close Date on entry to Closed won (7), preserving it throughout post-sales.':'Only OM may edit Close Date from Stage 6 onward; at booking it equals the OM acceptance/booking date. Preserve it through subsequent stage and integration changes.',
      'AE reviews and updates next steps and expected Close Date at least weekly;':'AE reviews next steps and expected Close Date at least weekly; date edits are owner/Sales Ops before Stage 6 and OM-only thereafter;',
      'first Stage 8 entry / verified on-site-delivery milestone from the linked Opportunity':'first verified complete on-site-delivery milestone from the linked Order/Case',
      'first Stage 8 delivery milestone':'first verified complete on-site-delivery milestone',
      'first verified Stage 8/on-site-delivery milestone':'first verified complete on-site-delivery milestone',
      'first Stage 8/on-site-delivery milestone':'first verified complete on-site-delivery milestone',
      'Case system stamp · first Opportunity Stage 8 entry':'Case system stamp · verified complete on-site receipt',
      'authorized 7 → 8 delivery transition':'authorized Order/Case delivery updates',
      'verified delivery transition':'verified Order/Case delivery update',
      'authorized delivery transition':'authorized Order/Case delivery update',
      'Closed/Won for 7–8':'Closed/Won for 7',
      'Stage 1–8':'Stage 1–7',
      'authorized 7 → 8 delivery progression':'authorized Order/Case delivery updates',
      'confirm the decision date at closure and lock it at Closed won (7).':'before Stage 6, the owner and Sales Ops maintain expected Close Date; from Stage 6 onward OM alone edits it and sets it to the booking date at Closed Won.',
      'Stages 1–8':'Stages 1–7','Stages 0–8':'Stages 0–7',
      'Stages 7–8':'Stage 7','Stages 6–8':'Stages 6–7',
      'Stage 7–8':'Stage 7','Stage 8/on-site':'verified on-site',
      'Stage 8 Invoice':'Stage 7 Closed Won',
      'Stage 8':'Stage 7','stage 8':'stage 7',
      'after Stage 7 rather than adding an Opportunity stage':'after booking rather than adding an Opportunity stage',
      'carry through Stage 7':'continue through delivery on the Case',
      'Only a System Administrator can change it after the lock. OM owns its booking confirmation.':'Only OM may edit Close Date from Stage 6 onward, including after booking; preserve the audit trail.',
      'only a System Administrator can change it afterward':'only OM may edit it from Stage 6 onward',
      'Only a System Administrator may change the locked Closed Won Close Date.':'Only OM may edit Close Date from Stage 6 onward.',
      'OM controls booking confirmation and locks Close Date at Stage 7':'OM controls booking confirmation and Close Date from Stage 6 onward',
      'Lock Close Date at Closed won.':'Close Date is OM-only from Stage 6.',
      'At booking the Close Date locks':'Close Date is OM-only from Stage 6',
      'OM owns Close Date confirmation and the booked date locks at Stage 7':'only OM may edit Close Date from Stage 6 onward',
      'OM confirms Close Date, which locks at Closed Won.':'OM sets Close Date to the acceptance/booking date at Closed Won.',
      'OM confirms Close Date at booking.':'OM sets Close Date to its acceptance/booking date.',
      'Close Date stays locked at Stage 7':'Close Date remains protected from non-OM edits',
      'Customer Commitment Secured':'Customer Commitment',
      'Opportunity team and RevOps':'opportunity owner and Sales Ops',
      'Opportunity and RevOps teams':'opportunity owner and Sales Ops',
      'Include Renewals in interview capture':'Exclude renewals from interview capture',
      'Sales owns the customer won decision; Order Management retains booking authority.':'OM and GSS own Stage 6; Sales supplies the customer win evidence and OM controls booking authority.',
      'Above $1M notify the Sales Manager and copy the AE;':'On successful booking at Stage 7, above $1M notify the Sales Manager and copy the AE;',
      'Above $1M, the Sales Manager receives the notification':'On successful booking at Stage 7, above $1M the Sales Manager receives the notification',
      'Capture at entry to Won decision (6), distinct from booking at 7.':'Capture evidence at Won decision (6); send the Win wire notification only after booking at Stage 7.',
    }
    for old,new in replacements.items():
        text=text.replace(old,new).replace(html.escape(old,quote=True),html.escape(new,quote=True))
    for i,value in enumerate(preserved):text=text.replace(f'__RETIRED_STAGE_{i}__',value)
    return text


def within(page,id,fn,tag='section'):
    pattern=r'(<'+tag+r'\b[^>]*id="'+re.escape(id)+r'"[^>]*>)(.*?)(</'+tag+'>)'
    page,n=re.subn(pattern,lambda m:m[1]+fn(m[2])+m[3],page,count=1,flags=re.S)
    assert n==1,id
    return page


def system(page,ns):
    # Consolidate detailed field registers before removing the obsolete stage.
    s8=re.search(r'<section class="stage" id="s8">.*?</section>',page,re.S)[0]
    rows=re.findall(r'<tr data-field="([^"]+)">(.*?)</tr>',s8,re.S)
    stage7=re.search(r'<section class="stage" id="s7">.*?</section>',page,re.S)[0]
    additions=['<tr data-field="'+name+'">'+row+'</tr>' for name,row in rows if 'data-field="'+name+'"' not in stage7]
    page=ns['add_fields'](page,'s7',additions)
    page=page.replace(s8,'')
    # Remove the Stage 8 column from each unmerged slide row, retaining invoice fields at 7.
    def slide(table):
        def row(m):
            cells=re.findall(r'<t[hd]\b[^>]*>.*?</t[hd]>',m[0],re.S)
            if len(cells)==12:
                if 'slide-fields' in m[0]:
                    invoices=re.findall(r'<span\b[^>]*>.*?</span>',cells[10],re.S)[:2]
                    cells[9]=cells[9].replace('</td>',''.join(invoices)+'</td>')
                del cells[10]
                return re.sub(r'(<tr[^>]*>).*?(</tr>)',lambda r:r[1]+''.join(cells)+r[2],m[0],flags=re.S)
            return m[0]
        table=re.sub(r'<tr\b[^>]*>.*?</tr>',row,table,flags=re.S)
        table=table.replace('<col span="11">','<col span="10">').replace('colspan="11"','colspan="10"')
        table=table.replace('colspan="2" scope="colgroup" class="phase-grow"','colspan="1" scope="colgroup" class="phase-grow"').replace('<td colspan="2">Won</td>','<td>Won</td>')
        table=table.replace('<td colspan="6">Sales + Sales Engineering</td>','<td colspan="5">Sales + Sales Engineering</td>')
        table=table.replace('Confirm the won decision and prepare the OM/GSS logistics handoff.','OM reviews and confirms booking with GSS handoff support.')
        table=table.replace('Book the order; start the deployment Case and coordinate delivery.','Closed Won: trigger Win wire and deployment Case; maintain delivery and invoice evidence.')
        table=table.replace('Closed Won · Actual Close Date','Close Date = Booking Date')
        table=table.replace('pending billing does not block delivery-led Stage 8 entry','Invoice evidence is captured when issued')
        return table
    page=re.sub(r'<table class="slide-matrix">.*?</table>',lambda m:slide(m[0]),page,count=1,flags=re.S)
    # Remove navigation card for Stage 8, then redirect surviving legacy contextual links.
    page=re.sub(r'<a[^>]*href="#s8"[^>]*>.*?</a>','',page,flags=re.S)
    page=page.replace('repeat(11,minmax(0,1fr))','repeat(10,minmax(0,1fr))')
    page=page.replace('.ongoing-confirmorder{grid-column:9/span 2;','.ongoing-confirmorder{grid-column:8/span 2;')
    page=page.replace('.ongoing-deployment{grid-column:9/span 2;','.ongoing-deployment{grid-column:9;')
    page=page.replace('Confirm order · Stages 7–8','Confirm order · Stages 6–7')
    page=page.replace('Win wire · Stages 6–7','Win wire · Notify at Stage 7').replace('AE captures win fields; manager reviews. &gt;$1M: two-day Win wire.','Capture at 6; notify after booking at 7. &gt;$1M: manager reviews within two business days.')
    # Replace superseded lifecycle paragraphs, including their repeated ongoing activity copies.
    page=re.sub(r'Order Management and GSS coordinate shipping, receiving and deployment through Stages 7–8\..*?Do not create a new Opportunity deployment-status or completion-date field\.',html.escape(DELIVERY),page,flags=re.S)
    page=re.sub(r'Verified complete on-site delivery controls entry to Stage 8;.*?milestone\.',html.escape('Record verified complete receipt on the Order/Case while the Opportunity remains Closed Won at Stage 7. Invoice Reference and Invoice Date are required when issued; do not enter placeholders. '+VALUE_START),page,flags=re.S)
    page=re.sub(r'OM must confirm order reconciliation before 6 → 7;.*?invent new picklist choices\.',html.escape(ns['STATUS']),page,flags=re.S)
    page=ns['update_field'](page,'Value Tracking Start Date','Date/time · PS Case','First verified complete on-site receipt',VALUE_START)
    page=ns['update_field'](page,'Time to Value','Calculated days · PS Case','Confirmed Yes with valid outcome date',VALUE_START)
    for id in ['s6','s7']:
        def stage(fragment):
            fragment=re.sub(r'(<div class="owner">).*?(</div>)',r'\1Owner · Order Management + GSS · Forecast: '+('Commit' if id=='s6' else 'Won')+r'\2',fragment,count=1,flags=re.S)
            gate=('OM reviews the complete customer commitment and approved Primary Quote in Stage 6. '+ns['STATUS']+' '+ns['PERMISSIONS']) if id=='s6' else ('Only OM can book from Stage 6 with Order Review Status = Booked and a reconciled package. '+ns['CLOSE_DATE']+' Create or link the deployment Case and trigger Win wire on the successful booking transition. '+DELIVERY)
            fragment=re.sub(r'<div class="stage-gate">.*?</div>','<div class="stage-gate"><h3>'+('OM review · Book to 7 or reject to 5' if id=='s6' else 'Closed Won · Final won Opportunity stage')+'</h3><p>'+html.escape(gate)+'</p></div>',fragment,count=1,flags=re.S)
            return fragment
        page=within(page,id,stage)
    page=ns['append_to'](page,'s6',ns['note'](ns['CLOSE_DATE']))
    page=ns['append_to'](page,'stage-update-flow',ns['note'](ns['PERMISSIONS']),'article')
    page=ns['append_to'](page,'win-wire',ns['note'](WIN),'article')
    page=ns['append_to'](page,'s7',ns['note'](WIN+' '+VALUE_START))
    page=ns['append_to'](page,'ongoing-next-detail',ns['note'](ns['CLOSE_DATE']),'article')
    page=within(page,'order-current-state',lambda s:s.replace('Stages 7–8 · Order Management','Stages 6–7 · Order Management').replace('approved PO, quote','approved PO/contract commitment, final Primary Quote'),'article')
    # OM workspace includes all former Stage 8 fields, without premature invoice/delivery gates.
    for name,kind,inputs,purpose in [
      ('Installation address','Address / existing field','Final quote; required when different from shipping',INSTALL),
      ('End-user legal entity','Existing account/entity reference','Actual end user',INSTALL),
      ('PS contact name','Existing Contact / name','Installation contact',INSTALL),
      ('PS contact phone or email','Phone / email','Installation contact channel',INSTALL),
    ]:page=ns['add_fields'](page,'ongoing-quoting-detail',[ns['field'](name,kind,inputs,purpose)])
    for name,purpose in [('Shipping Instructions',SHIPPING),('Logistics Coordinator name',SHIPPING),('Logistics Coordinator phone or email',SHIPPING),('Packaging Instructions',PACKAGING),('Customer Logistics contact name',PACKAGING),('Customer Logistics phone or email',PACKAGING)]:
        page=ns['add_fields'](page,'s5',[ns['field'](name,'Text / existing contact fields','Required before exit for hardware/mixed; software-only exempt',purpose,change='Added · 21 Oct')])
    page=ns['append_to'](page,'s5',ns['note'](SHIPPING+' '+PACKAGING))
    page=within(page,'s5',lambda s:s.replace('<h3>Advance to 6 · Won decision</h3>','<h3>Advance to 6 · Won decision</h3>').replace('</p></div><h3>Fields and timing',' '+html.escape(SHIPPING+' '+PACKAGING)+'</p></div><h3>Fields and timing',1))
    page=ns['update_field'](page,'Support Start Date','Existing date; Salesforce ↔ Oracle','Shipment or approved CPQ/contract start',SUPPORT)
    page=ns['update_field'](page,'Actual Close Date','Existing Close Date; not a new field','Close Date = Booking Date',ns['CLOSE_DATE'])
    page=ns['update_field'](page,'Invoice Reference','Existing Invoice # / Oracle synchronization','When issued; not a booking prerequisite','Synchronize Oracle invoice numbers into the existing Invoice Reference at Stage 7; preserve history and multiple invoice references. Receipt and financial invoicing remain distinct.')
    page=ns['update_field'](page,'Invoice Date','Existing related Order date','When issued; not a booking prerequisite','Expose the related Order financial Invoice Date in the Stage 7 OM workspace. Do not create a duplicate date or use it as the delivery/value-tracking milestone.')
    def stage_choices(m):
        return m[0].replace('<li>8. Invoiced</li>','').replace('Dropdown inputs · 14 choices','Dropdown inputs · 13 choices')
    page=re.sub(r'<tr data-field="[^"]+">.*?</tr>',stage_choices,page,flags=re.S)

    page=ns['append_to'](page,'order-current-state',ns['note']('OM review workspace: Order Review Status/sub-status, rejection reason and notes, OM Reviewer, ERP Status, Close Date / Booking Date, Support Start Date, invoice references/dates and Deployment Case Link. Reps can read OM review information; only OM edits review fields. Oracle-owned fields remain read-only. '+ns['REJECTION']),'article')
    # New logistics requirements are discoverable on the one-slide view.
    row=re.search(r'<tr><th scope="row" class="slide-row-label">Fields<small>.*?</tr>',page,re.S)[0]
    cells=re.findall(r'<td class="slide-fields">.*?</td>',row,re.S)
    extra=''.join('<a class="october-slide-field" href="#s5"><span class="field-new">'+x+'</span></a>' for x in ['Shipping + coordinator · hardware','Packaging + customer logistics · hardware'])
    page=page.replace(row,row.replace(cells[6],cells[6].replace('</td>',extra+'</td>'),1),1)
    page=normalize(page)
    return page


def configure(ns):
    # Keep BR identifiers stable; the baseline remains pre-October 19.
    revised=ns['REVISED']
    from requirement_summaries import SUMMARIES
    for n in (110,116):
        req,accept,notes=SUMMARIES[n]
        revised[n]=(normalize(req),normalize(accept),normalize(notes),'Update the eligible stage range to 1–7 after removing Stage 8; preserve qualification and first-entry snapshots.')
    revised.update({
      2:('End the won Opportunity lifecycle at Stage 7.', 'Configure Open stages 0–6, Closed/Won at 7 and Closed/Lost for the lost outcome. Remove Stage 8 from active stages, views, filters and mappings; map existing Stage 8 records to Closed Won without resetting dates, credits or triggering duplicate notifications/Cases.', 'Update dependent reports and integrations; retain history.', 'Remove Stage 8 and consolidate its content under Stage 7.'),
      15:('Maintain fulfillment and invoice evidence at Stage 7 after booking.',DELIVERY,'Move the former Stage 8 fields into Stage 7 / OM; use Order and Case actual-event evidence.','Move Invoice Reference, Invoice Date, Case link and final Won state into Stage 7; remove the delivery-based stage transition.'),
      18:('Continue deployment and value realization on the Case after booking.',DELIVERY+' '+VALUE_START,'Retain existing value plan, outcome and evidence fields; do not reopen the booked Opportunity.','Remove Stage 8 dependencies while preserving actual delivery-based value tracking.'),
      24:('Send Win wire notifications on booking at Stage 7.',WIN,'Keep existing win-evidence capture at Stage 6 and existing amount thresholds.','Move notification trigger from Stage 6 to Stage 7; deduplicate successful booked-win events.'),
      58:('Start value tracking from verified customer receipt.',VALUE_START,'Part of BR-SS-018; reuse the existing Order/Case event and field.','Replace the Stage 8 trigger with verified complete on-site receipt; do not use booking as delivery.'),
    })
    # The new combined release retains October 19 additions and incorporates their refinements.
    replacements={
      135:('Stage change authority','Give OM exclusive stage-change authority from Stages 6 and 7.',ns['PERMISSIONS'],'Confirmed'),
      136:('Close Date / Booking Date','Use Close Date as Booking Date, with OM control from Stage 6.',ns['CLOSE_DATE'],'Confirmed'),
      137:('Installation and end-user details','Capture installation location, end-user entity and PS contacts.',INSTALL,'Confirmed'),
      139:('OM review workspace','Extend the OM workspace with review, booking and fulfillment details.','Only authorized OM edits review fields; reps can read. Require an OM-group User reviewer when In Progress. Include status/sub-status, rejection reason/notes, ERP Status, invoice references/dates, Close Date / Booking Date, support start and the deployment Case link. Preserve read-only Oracle fields.','Confirmed'),
      142:('Support and revenue dates','Synchronize approved Support Start Date and carry dates to the deployment Case.',SUPPORT,'Confirmed'),
      147:('Booking process reference','Include Booking an Order guidance within Confirm order.', 'Move the booking policy reference into Confirm order under Ongoing activities and align enablement links. Keep policy guidance separate from explicitly approved system gates. Close Date represents OM acceptance/booking date.','Reference only'),
    }
    ns['NEW']=[(n,*replacements[n]) if n in replacements else row for row in ns['NEW'] for n in [row[0]]]
    ns['NEW'] += [
      (152,'Shipping instructions and coordinator','Require hardware shipping instructions and logistics coordinator details before Stage 6.',SHIPPING,'Confirmed'),
      (153,'Packaging and customer logistics','Require hardware packaging instructions and customer logistics contact details before Stage 6.',PACKAGING,'Confirmed'),
      (154,'Order resubmission notifications','Reset review status and notify OM on resubmission from Stage 5 to Stage 6.',ns['REJECTION'],'Confirmed'),
    ]
    oldnormalize=ns['normalize']
    ns['normalize']=lambda text:normalize(oldnormalize(text))
    # Transform changed scope labels too, without altering untouched canonical baseline summaries.
    oldrevise=ns['revise']
    def revise(data):
        result=oldrevise(data)
        for r in result[1:]:
            if int(r[1][-3:]) in ns['REVISED']:
                r[2]=normalize(r[2])
        return result
    ns['revise']=revise
    oldsystem=ns['system']
    def build_system(page):
        current=ns['normalize'];ns['normalize']=oldnormalize
        try: page=oldsystem(page)
        finally: ns['normalize']=current
        return system(page,ns)
    ns['system']=build_system
    oldlearning=ns['learning']
    def learning(modules,design,definitions,examples,stages):
        oldlearning(modules,design,definitions,examples,stages)
        modules[:]=walk(modules,normalize);design.update(walk(design,normalize));definitions.update(walk(definitions,normalize));examples.update(walk(examples,normalize))
        for m in modules:
            m['stages']=list(dict.fromkeys('s7' if x=='s8' else x for x in m['stages']))
            if m['source']=='s8':m['source']='order-current-state'
        by={m['id']:m for m in modules}
        def lesson(id,meaning,reminders,scenario,steps,question,answer):
            m=by[id];m.update(definition=meaning,distinction=answer,reminder=reminders,scenario=scenario,steps=steps,questions=[question,'Which evidence and owner are required?'],practice=scenario,check=question,answer=answer,strong=answer)
            design[id].update(goal=meaning,practice=scenario,model=answer,question=question,answer=answer,takeaway=meaning)
            definitions[id]=meaning;examples[id]=answer
        lesson('invoice',DELIVERY,['Stage 7 is the final won Opportunity stage.','Verify actual receipt with GSS on the Order/Case.','Capture invoice references and dates when issued.'],
          'Nine of ten booked units arrive. The Opportunity remains Closed Won at Stage 7 while OM and GSS record partial receipt. When the last unit arrives, they record complete receipt on the Order/Case; no Opportunity stage changes.',
          ['Confirm booking — OM accepts the complete reconciled package at Stage 7.','Track actual receipt — Verify each non-cancelled booked item with GSS.','Reconcile invoices — Populate invoice references and dates when issued; never use placeholder values.','Continue on the Case — Record deployment and value outcomes without reopening the Opportunity.'],
          'Does pending delivery or invoicing block Closed Won?', 'No. OM booking completes the won Opportunity at Stage 7; delivery and invoicing continue through the Order and Case.')
        by['invoice']['source']='order-current-state'
        lesson('booking','OM reviews Stage 6 with GSS and accepts booking or rejects the package.', ['Only OM may move out of Stages 6 or 7.','Rejected submissions return to 5 with a reason and notes to owner/Sales Ops.','Close Date equals OM acceptance/booking date; OM controls it from 6 onward.'],
          'OM finds a contract/quote mismatch, rejects to Stage 5 and notifies the owner and Sales Ops. A corrected resubmission resets New Order and notifies OM.',
          ['Review the package — Check the Customer Commitment Files, final Primary Quote and approvals.','Record the review — Use the approved status/sub-status and an OM reviewer when In Progress.','Accept or reject — Book 6 → 7 only with Booked status and reconciliation, or reject 6 → 5 with reason and notes.','Book and hand off — Set Close Date to OM acceptance date, trigger Win wire and create/link one Case; retain the audit trail.'],
          'Who may correct Close Date after booking?', 'Only OM may edit Close Date from Stage 6 onward. Booking Date and Close Date are synonymous; later stage or integration updates cannot reset the date.')
        by['booking']['steps'][0]+=' Booking an Order: full process reference is under Confirm order.'
        by['won-decision']['owner']='Order Management · GSS'
        by['won-decision']['definition']='OM and GSS own Stage 6: review the complete customer commitment and approved Primary Quote, confirm booking readiness and prepare the deployment handoff. Forecast remains Commit until OM books 6 → 7.'
        by['won-decision']['steps'][3]='Prepare the handoff — GSS supports OM review; the deployment Case and Win wire notification start only on successful booking at Stage 7.'
        by['win-wire']['reminder'][2]='On successful Stage 7 booking, above $1M notify the manager/AE; the manager has two business days. Above $2M also require the full report.'
        by['win-wire']['steps'][2]='Review and route — '+WIN
        definitions['win-wire']=WIN;definitions['won-decision']=by['won-decision']['definition']
        by['next-steps']['steps'][0]+=' Before Stage 6, the owner and Sales Ops may edit expected Close Date; from Stage 6 onward request OM to make any date change.'
        by['quoting']['steps'][3]+=' '+INSTALL
        by['logistics']['steps'][3]+=' '+SHIPPING+' '+PACKAGING
        by['procurement']['steps'][2]+=' '+SHIPPING+' '+PACKAGING
        by['deployment']['steps'][3]+=' '+SUPPORT
        stages[:]=[tuple(walk(s,normalize)) for s in stages if s[0]!='s8']
        for i,s in enumerate(stages):
            row=list(s)
            if row[0]=='s6':row[3]='Order Management · GSS';row[5]='Review and confirm booking readiness.';row[7]=ns['PERMISSIONS']
            if row[0]=='s7':row[5]='Complete booking; coordinate delivery and invoice evidence.';row[6]=ns['CLOSE_DATE'];row[7]=DELIVERY;row[8]=list(dict.fromkeys(row[8]+['win-wire','value-realization','time-to-value']))
            stages[i]=tuple(row)
        definitions.pop('stage-s8',None);examples.pop('stage-s8',None)
        definitions['stage-s7']=DELIVERY;definitions['stage-s6']=by['won-decision']['definition']
        definitions['term-value-tracking-start-date']=VALUE_START
        definitions['term-close-date']=ns['CLOSE_DATE']
        examples['term-invoice-reference-invoice-date']='The Opportunity is Closed Won at Stage 7; OM records invoice evidence when issued and verifies actual delivery separately on the Order/Case.'
    ns['learning']=learning
