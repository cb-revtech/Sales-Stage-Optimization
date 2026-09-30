"""End-to-end consistency corrections. Preserve approved business decisions."""
import html,re
E=lambda s:html.escape(s,quote=True)
GATES={
 'creation':('Create with a valid origin','Resolve the Account and originating Contact, required core fields and source-dependent sourcing reference. Inbound intake starts at Stage 0; only the assigned seller-self-qualified path can start at Stage 1. Seller assignment and source attribution are separate.'),
 's0':('Advance to 1 · Discovery','The assigned AE has accepted the handoff and all five inbound CHAMPS answers plus the originating Contact are complete. Creating a SAL is not acceptance. Seller-self-qualified direct Stage 1 creation follows the separate documented path.'),
 's1':('Advance to 2 · Solution design','Complete discovery and all five CHAMPS answers, confirm AE and Primary SE, record Route to Market and any indirect subtype, and assign at least one Opportunity Contact Role. SQL is recorded at qualified pipeline entry, including valid skips; this exit does not duplicate it.'),
 's2':('Advance to 3 · Buyer alignment','Complete pain, competition, Technical Value, Champion, Decision Criteria, SharePoint Link and Description. Record POC Required?; if Yes, its status must be Completed or Cancelled. A completed POC alone does not establish Technical Win.'),
 's3':('Advance to 4 · Proposal / negotiate','Confirm customer-supported Technical Win and one selected configuration, plus Operational Value, Economic Buyer and Decision Process. Blank, In Progress or Technical Loss cannot pass.'),
 's4':('Advance to 5 · Procurement','Complete Business Value and Paper Process, select the single Primary Quote, and capture Requested Install Date. Current Amount follows the quote; the first pipeline-entry snapshot stays fixed.'),
 's5':('Advance to 6 · Won decision','Complete the shipping/delivery requests, IPG disposition, secured PO with the actual PO File, final agreements and delivery notes. Also satisfy the Stage 6 win and conditional interview inputs before the transition saves.'),
 's6':('On entry to 6 · Before booking at 7','Entry requires Won Reason, Business Value win detail, incumbent capture and applicable recognition/interview inputs. OM then reconciles the order and confirms the OM/GSS logistics handoff before booking. Stage 6 remains open/Commit. Quote corrections return to 5 and revalidate without duplicate win notifications.'),
 's7':('On entry to 7 · Advance to 8','OM confirms booking and starts or links one coordinating deployment Case with GSS. Complete on-site receipt of all non-cancelled booked items is required for Stage 8; partial delivery stays at 7. Booked facts and Close Date stay locked while the authorized delivery transition remains possible. Pending financial invoicing does not block Stage 8.'),
 's8':('Final Opportunity stage','Retain the Invoice label and the agreed delivery-led completion rule. The deal stays closed/won. Invoice reconciliation continues on the Order; deployment and value assessment continue on the Case without reopening the deal.'),
 'lost':('Record the loss decision','Require reason, explanation, actual loss date and next-step recommendation. Competitor capture is optional for the three approved noncompetitive reasons; selecting Other still requires detail. Interview eligibility is optional only for Stage 0 misqualification. Loss uses its own gates, not every earlier sales-stage gate.')}
FLOW_BUILD='Collect inputs in flow variables before the final confirmation. Re-read the current record and recheck permissions and prerequisite gates at save. Perform the final evidence, stage and timestamp writes in one transaction; route faults through Roll Back Records before displaying an error screen. Do not place a Screen, Pause or other transaction boundary between dependent writes. Cancelling a later screen cannot undo changes already committed by an earlier transaction. Keep notifications and integration effects after successful commit and deduplicate retries.'
CONTACT_TRANSACTION='In the creation action, resolve the originating Contact before inserting the Opportunity, then create or link the designated Contact relationship in the same controlled transaction. If using Opportunity Contact Roles, the parent Opportunity ID must exist before its child role record can be created. Do not implement a before-insert child-existence check that makes valid creation impossible. Roll back failed parent/link creation and retain equivalent controls for integration paths.'
CASE_TRANSACTION='For entry to Stage 7, find or provision the coordinating deployment Case and its supported relationship as part of the same controlled booking transition. Do not require a Case link before the action can create it or leave an orphan Case after a failed transition. Use scoped system automation where OM lacks Case-create rights; verify the writable relationship and Case assignment. Retries and Stage 7 re-entry reuse the existing coordinating Case.'
STAGE_TYPES='Configure the numbered sales Stage values with Open type for 0–6, Closed/Won for 7–8, and Closed/Lost for the lost outcome. IsClosed / IsWon follow Stage configuration; do not create duplicate checkbox fields. Stage 6 customer selection is not booking. Keep the existing administrative outcomes and standard forecasting configuration separately mapped; Forecast Category (Sales) is the distinct business field described here.'
COVERAGE_CONTROL='Evaluate partner and geography coverage together before assigning the partner Account owners to the Opportunity Team. Reconcile active dates, transfers and multiple association reasons; remove only the derived grant that no longer applies. Confirm both role/territory hierarchies and other shares so broad independent access does not defeat the intended scope. Keep Account ownership, Opportunity ownership, territory assignment and booked attribution distinct.'
ACTIVITY_CONTROL='Confirm Access Activities, Edit Tasks, Activity sharing and both Name (Who) / Related To (What) access for meeting Tasks. Opportunity team membership alone does not guarantee the ability to edit someone else’s Task. Use assigned follow-up Tasks or an explicitly authorized correction action where native access is insufficient; do not widen commercial record access to fix a Task edit.'
BOOKING_LOCK='Protect booked Close Date, Amount, Products and attribution from routine edits while permitting the authorized 7 → 8 delivery transition, verified invoice/reference synchronization and approved booked-correction workflow. Do not implement a whole-record lock that blocks required post-booking updates. Case updates never rewrite booked sales facts.'
ORIGIN='Required for Direct or BDR. Populate Direct from the verified originating seller User and BDR from the originating BDR User. Use the creator only when that person is the verified originating seller; never default to an integration user or the current owner.'
ROUTING='An Opportunity must retain a valid User owner. Route pending assignment to a Sales Ops review list or an assigned Task; do not assign the Opportunity itself to a Salesforce queue. Notify the accountable seller when assigned, and record acceptance separately.'
SQL_RULE='Record SQL once for the Opportunity and linked Contact episode on its first valid entry into numbered Stages 1–8 after the applicable assignment, acceptance and qualification gates pass. This includes permitted skips and seller-self-qualified direct Stage 1 creation. Use the same successful transition as Pipeline Date. Completing qualification while still in Stage 0 does not by itself record SQL. A skipped Stage 1 Date stays blank; do not invent a Discovery visit, duplicate SQL on re-entry, or fabricate MQL/AQL history.'
PAIRS=[
 ('System-maintained · SAL at creation / SQL at Stage 1','System-maintained · SAL at creation / SQL at qualified pipeline entry'),
 ('New Opportunity-level conversion milestone: SAL on creation; SQL on entry to Stage 1 or seller-direct Stage 1 creation.','New Opportunity-level conversion milestone: SAL on creation; SQL at first qualified pipeline entry, including permitted skips and seller-direct Stage 1 creation.'),
 ('SQL on first Stage 1 entry.','SQL on first qualified entry to Stages 1–8, including permitted skips.'),
 ('Entry to Stage 1 records SQL (Sales Qualified Lead) after acceptance and the source-dependent CHAMPS gate.','First valid entry into Stages 1–8 records SQL (Sales Qualified Lead) after the applicable acceptance and source-dependent CHAMPS gate, including permitted skips.'),
 ('The later 0 → 1 handoff checks acceptance, assignment and CHAMPS before recording SQL.','The first qualified entry to Stages 1–8 checks acceptance, assignment, CHAMPS and every crossed gate before recording SQL, including permitted skips.'),
 ('On Stage 0 → 1, after acceptance, assignment and CHAMPS pass, stamp SQL for this Opportunity and linked Contact episode; sync the approved Account view.','On first valid entry from Stage 0 into Stages 1–8, after acceptance, assignment, CHAMPS and all crossed gates pass, stamp SQL for this Opportunity and linked Contact episode; sync the approved Account view.'),
 ('Block Stage 1 entry until the assigned AE has accepted and the intake-path CHAMPS gate is satisfied; record SQL only at the handoff.','Block inbound entry to Stages 1–8 until the assigned AE has accepted and all applicable qualification and crossed gates pass; record SQL at the successful transition, including permitted skips.'),
 ('Record the SQL conversion milestone and complete business-fit discovery before quoting.','Record SQL at qualified pipeline entry and complete business-fit discovery before Stage 2. Controlled Budgetary quoting is available here.'),
 ('Entry to Discovery is the SQL milestone.','Qualified pipeline entry records SQL, including a permitted skip past Discovery; a skipped Stage 1 Date remains blank.'),
 ('Stage 1: SQL','Qualified pipeline entry: SQL'),
 ('Promote to SQL on entry to Stage 1.','Record SQL at qualified pipeline entry, including valid skips.'),
 ('System-stamped on entry to Discovery.','System-stamped at qualified pipeline entry, including valid skips.'),
 ('Stage 1 entry records SQL for the linked Contact/Opportunity episode.','First qualified entry to Stages 1–8 records SQL for the linked Contact/Opportunity episode, including permitted skips.'),
 ('a contact-linked SAL / SQL event trail from creation through Discovery.','a contact-linked SAL / SQL event trail from creation through qualified pipeline entry, including valid skips.'),
 ('For inbound records, prevent entry to Stage 1 while pending or rejected;','For inbound records, prevent entry to Stages 1–8 while pending or rejected;'),

 ('Required for Direct or BDR. Default Direct to the creating User; populate BDR from the originating BDR User.',ORIGIN),
 ('Route unassigned opportunities to the appropriate review queue; notify the assigned seller.',ROUTING),
 ('Required for every other nonblank source; deal registration supplies its partner.','Required for verified Partner origin; registration alone does not establish the source.'),
 ('Sourcing Partner · Other sources','Sourcing Partner · Partner'),
 ('After attribution migration; connect to Order shipping.','Commercial transacting account; verify ship-to separately.'),
 ('Then connect Transacting Partner to the Order shipping workflow; OM confirms the ship-to account/address.','Then carry the Transacting Partner into the Order’s commercial context; OM independently confirms the actual ship-to account/address.'),
 ('propagate the selected account reference to the Order shipping workflow.','carry the selected account reference into Order commercial context; independently verify ship-to rather than defaulting it from the transacting account.'),
 ('Keep quoting within Stages 2–5; retain the Stage 4 Primary Quote.','Allow Budgetary-only quoting in Stages 0–1 and regular quoting in Stages 2–5; retain the Stage 4 Primary Quote and Best and Final gates.'),
 ('Handle configuration and quoting alignment in the Quoting activity during Stages 2–5.','Handle quoting alignment in the Quoting activity: controlled Budgetary in 0–1 and regular quoting in 2–5, with technical/commercial gates.'),
 ('including permitted creation in that stage.','including creation only when that stage is an allowed starting stage (0 or seller-qualified 1).'),
]

def text_rules(s):
 for old,new in PAIRS:
  s=s.replace(old,new)
  s=s.replace(E(old),E(new))
 return s

def system(s,within,auto):
 s=text_rules(s)
 s=within(s,'creation',lambda v:v.replace('Forecast: Pre-pipeline</div>','Forecast: Pre-pipeline · Pipeline for direct Stage 1</div>',1))
 s=within(s,'stage-update-flow',lambda v:v.replace('</p>','</p><details class="rule-detail"><summary>Salesforce flow configuration</summary><p>'+E(FLOW_BUILD)+'</p><p><a href="https://architect.salesforce.com/docs/architect/decision-guides/guide/build-forms">Salesforce transaction guidance</a></p></details>',1),'article')
 s=within(s,'stage-update-flow',lambda v:re.sub(r'<p>(.*?)</p>',lambda m:'<ol><li>Choose the destination stage and review the prepopulated evidence.</li><li>Complete missing inputs for every gate crossed; route protected technical or approval evidence to its responsible owner.</li><li>Save only when validation passes. Cancellation or failure leaves the stage and entry dates unchanged.</li></ol><details class="rule-detail"><summary>Complete progression rule</summary><p>'+m[1]+'</p></details>',v,count=1,flags=re.S),'article')
 s=s.replace('<header class="specification-title"><h1>GTM Process</h1></header>','<header class="specification-title"><h1>GTM Process</h1><p class="reading-guide">Read the progression summary first, then the field timing. <strong>Before Stage</strong> marks an exit gate; <strong>On entry</strong> is required for that transition. System-maintained fields are stamped by automation, not filled in by the seller. Current inputs describe the captured inventory; proposed inputs describe the target change.</p></header>')
 for id,(label,body) in GATES.items():
  def stage(v):
   intro='<div class="stage-gate"><h3>'+E(label)+'</h3><p>'+E(body)+'</p></div>'
   return v.replace('<div class="body">','<div class="body">'+intro,1).replace('<h3>Required fields</h3>','<h3>Fields and timing</h3>',1)
  s=within(s,id,stage)
 s=auto(s,'ongoing-conversion-detail',SQL_RULE,'article')
 s=auto(s,'creation',STAGE_TYPES)
 s=auto(s,'creation',CONTACT_TRANSACTION)
 s=auto(s,'s7',CASE_TRANSACTION)
 s=auto(s,'s7',BOOKING_LOCK)
 s=auto(s,'s8',BOOKING_LOCK)
 s=auto(s,'ongoing-meetings-detail',ACTIVITY_CONTROL,'article')
 # Compact the most repetitive, non-protected field descriptions while retaining
 # their complete rules in an accessible native disclosure.
 long_fields={'Conversion Contact','Opportunity Conversion Lifecycle','Deployment Case Link','Forecast Category (Sales)'}
 def compact(m):
  if html.unescape(m[1]) not in long_fields:return m[0]
  cells=re.findall(r'<td[^>]*>(.*?)</td>',m[2],re.S)
  if len(cells)!=5:return m[0]
  body=cells[4]
  if len(re.sub('<[^>]+>','',body))<650:return m[0]
  split=body.find('. ',body.find('</span>')+7 if '</span>' in body else 0)
  if split<0:return m[0]
  cells[4]=body[:split+1]+'<details class="rule-detail"><summary>Full rule</summary><p>'+body[split+2:]+'</p></details>'
  return '<tr data-field="'+m[1]+'">'+''.join('<td>'+c+'</td>' for c in cells)+'</tr>'
 s=re.sub(r'<tr data-field="([^"]+)">(.*?)</tr>',compact,s,flags=re.S)
 return s

def requirements(data):
 by_id={int(r[1][-3:]):r for r in data[1:]}
 for r in data[1:]:r[:]=[text_rules(c) for c in r]
 additions={2:STAGE_TYPES,3:ROUTING,13:BOOKING_LOCK,15:BOOKING_LOCK,17:CASE_TRANSACTION,110:CONTACT_TRANSACTION+' '+SQL_RULE,120:COVERAGE_CONTROL,126:ACTIVITY_CONTROL,130:FLOW_BUILD}
 for n,rule in additions.items():
  by_id[n][3]+=' '+rule
  by_id[n][10]+=' End-to-end audit: clarified implementation mechanics; approved stage behavior retained.'
 by_id[110][8]+=' Test valid 0 → 4: SQL and Pipeline Date record the same successful event, Stage 4 Date stamps, and never-visited Stage 1–3 Dates stay blank. Missing qualification blocks all writes; re-entry does not duplicate SQL. Completing CHAMPS in Stage 0 without advancing does not record SQL.'
 by_id[110][8]+=' Test creation with an existing resolved Contact: Opportunity and its designated relationship commit together; a link failure rolls back the creation. Do not require a child role before the Opportunity ID exists.'
 by_id[17][8]+=' Test first entry, re-entry, an existing Case and a failed final stage save; no missing relationship or duplicate/orphan Case is left behind.'
 by_id[120][8]+=' Test correct partner/wrong region, correct region/wrong partner, expired coverage, multiple associations and independent shares. Validate removal after transfer without deleting separately justified access.'
 by_id[130][8]+=' Test cancellation on each input screen, a stale-record update, and a fault on the final dependent write: no partial evidence/stage/date commit. Notifications occur only after successful commit.'
 by_id[13][8]+=' Booked-value edits fail, but the authorized delivery completion and invoice-reference update still succeed without unlocking booked facts.'
 return data

def learning(modules,design,definitions,examples):
 m={v['id']:v for v in modules}
 m['fulfillment']['steps'][1]='Separate the relationships — Keep the originating partner, transacting partner and physical delivery destination distinct.'
 m['fulfillment']['steps'][2]='Connect the transaction — Carry the transacting account reference into the Order’s commercial context. Do not use it as an automatic ship-to destination.'
 design['fulfillment']['practice']='Partner A originated the deal, reseller B transacts the purchase and the customer’s lab receives the equipment. Identify the three distinct relationships.'
 design['fulfillment']['model']='Record A as Sourcing Partner, B as Transacting Partner and the lab as the independently verified ship-to destination. Do not substitute one relationship for another.'
 m['partner-accounts']['steps'][2]+=' Team access requires both partner and approved geographic coverage; ask Partner Ops to resolve a mismatch instead of assuming the Account owner gets every associated deal.'
 m['account-context']['steps'][2]+=' Confirm geographic scope and reconcile active deal teams when coverage changes; Account Tier alone does not determine access.'
 m['booking']['steps'][3]+=' Booked-value protection still permits the authorized delivery transition and verified invoice/reference updates; it must not be implemented as a blanket record lock.'

 m['conversion']['stages']=['creation']+[f's{i}' for i in range(9)]+['ongoing']
 m['conversion']['definition']='MQL and AQL are distinct Contact qualification paths. Opportunity creation records SAL; first qualified pipeline entry records SQL, including valid skips past Discovery.'
 definitions['conversion']=m['conversion']['definition']
 definitions['term-sql-sales-qualified-lead']='The sales qualification milestone recorded on first valid entry into Stages 1–8 after the applicable acceptance and qualification gates pass. It includes permitted skips and seller-self-qualified direct Stage 1 creation.'
 definitions['term-opportunity-conversion-lifecycle']='The opportunity’s last conversion milestone: SAL at creation or SQL at first qualified pipeline entry, including valid skips. It is separate from the numbered sales stage.'
 examples['term-sql-sales-qualified-lead']='A valid Stage 0 → 4 transition records SQL and Pipeline Date, plus Stage 4 Date. Stage 1 Date stays blank because Discovery was not visited.'
 m['conversion']['reminder'][1]='Record SAL at creation and SQL at first qualified pipeline entry, including valid skips.'
 m['conversion']['steps'][2]='Follow the milestones — For inbound intake, acceptance and all applicable qualification gates must pass before the first valid entry to Stages 1–8 records SQL. Valid skips count. Seller-self-qualified direct Stage 1 creation records SAL and SQL together under its documented path.'
 m['conversion']['steps'][3]='Protect reporting — Capture SQL, Pipeline Date and Pipeline Entry Amount at the same successful first pipeline entry. Stamp Stage 0–6 Dates only for actual visits; skipped stages stay blank and re-entry never resets first dates or duplicates SQL. Keep transition history for revisits. Do not fabricate MQL/AQL or downgrade existing customer lifecycle states.'
 design['conversion']['model']='Stamp SQL, Stage 4 Date and Pipeline Date at the same successful event, plus Pipeline Entry Amount and currency. Keep Stage 0 Date and leave never-visited Stage 1–3 Dates blank. All crossed gates must pass. Regression, retries and later pricing changes do not create another SQL or reset the pipeline snapshot.'
 design['conversion']['question']='A deal validly skips from Stage 0 to Stage 4. Does SQL require a Stage 1 Date?'
 design['conversion']['answer']='No. Record SQL when the qualified transition succeeds, together with Pipeline Date and Stage 4 Date. Stage 1 Date remains blank because Discovery was not visited. Filling CHAMPS while staying in Stage 0 alone does not record SQL.'
