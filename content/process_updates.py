"""Approved September 29 review. System specification only; no live CRM changes."""
import html, re, json
from change_log import change_log
import sales_ops_updates as sales_ops
import audit_updates as audit
from requirement_summaries import simplify
E=lambda s:html.escape(str(s),quote=True)
APPROVED=[1,2,3,4,5,7,8,9,10,11,13,14,23,24,26,29,30,31,32,33,34]
EXCLUDED=[6,12,15,16,17,18,19,20,21,22,25,27,28,35,36]
# Removed from the implementation register at user request; existing process
# content and companion pages are not rolled back. Keep the remaining BR IDs.
REMOVED_IMPLEMENTATION_IDS={27,28,117,124,125,127,128,129}
SOURCE='Populate attribution from verified origin: Direct → originating seller User; BDR → originating BDR User; Marketing → originating Campaign; Partner → originating Partner Account. A registration may be linked for any source and does not itself prove partner origination. Partner source does not require a registration. Never use the integration user, current owner or Transacting Partner as a substitute for origin evidence.'
SOURCE_LOCK='Protect accepted partner-originated Opportunity Source and Sourcing Partner from ordinary AE or overlay edits. Corrections require an explicitly authorized RevOps / Partner Ops action with evidence, reason, prior/new values, actor and timestamp. This is separate from Partner Contribution (Mgt). Apply the restriction to UI, imports and integrations.'
EARLY='Allow Budgetary CPQ quotes in Stages 0–1 with a linked Account and Opportunity, assigned seller, customer need, indicative scope/configuration, estimate assumptions and existing commercial authority. Capture Route to Market before early release; Direct requires the route notification. Early pricing does not confer SAL acceptance, SQL, Technical Win or stage advancement. Stages 2–5 retain quoting access; Best and Final requires Technical Win, selected configuration and applicable commercial approvals before customer release. Preserve Stage 6 → 5 correction and booked-record locks. Confirm the existing approval matrix; no new numeric approval threshold is specified.'
TEAM='On creation or activation of a partner association, resolve the partner Account’s Primary DDN Partner Account Manager and Partner Technical Lead. Add each active user to the opportunity team only when the partner AND approved geography/territory coverage match. Send missing or mismatched coverage to Partner Ops; do not silently broaden access. Deduplicate membership across associations, and reconcile owner changes, coverage transfers, deactivation and expiry using the recorded grant reason. Remove only access derived from the changed assignment; preserve independently authorized grants. Stage 1 checks partner assignments when a partner is present; a partner is not required on every opportunity.'
SCOPE='Partner overlays receive access only for their assigned partner and geo/territory coverage. Broader direct-pipeline visibility needs an explicit entitlement. Team membership does not grant forecast, Amount, commercial approval, registration approval or validation-bypass rights. Recalculate derived access when coverage changes and preserve audit history.'
PIPELINE=sales_ops.PIPELINE
TECH='Technical fit means the solution meets the requirements. Technical Win additionally records customer-confirmed preference for DDN against the agreed decision criteria, subject to commercial agreement, supported by the selected configuration and SE evidence. A completed POC or valid configuration alone is not a win. Use In Progress while evaluation or preference remains unresolved; record the blocker, owner and next action in existing technical risk / SE Next Step fields. Blank, In Progress and Technical Loss cannot pass the Stage 3 → 4 gate or bypass it by skipping to Commit.'
DIRECT='On Direct route selection or change, notify the sales manager and relevant partner coverage owner before customer-facing pricing. Record the notification against the opportunity and resolve missing coverage through Partner Ops. Capture the route during Stage 1, or earlier for a Stage 0–1 quote. This notification is not a new blanket approval gate; existing commercial approvals still apply.'
OTHER='Require a nonblank explanation in Association Description / Plan when Role On Deal or Account Classification is Other. CSP includes hyperscalers; retain the current classification set. Marketplace-specific categories remain deferred.'
CONTRIBUTION='Retain the documented partner contribution rules until an approved replacement is implemented; no automatic sunset. Keep original attribution evidence, management override audit and booked-credit freeze. Partner associations may be added throughout the lifecycle; association after booking does not rewrite booked credit and partner presence is not a universal stage gate.'
ENHANCEMENTS='Product and RevOps report enhancement demand by capability, affected accounts, unique opportunities, stage and linked Amount. Deduplicate Opportunity IDs before aggregating revenue exposure, including when several Cases relate to one deal. Separate open demand from booked outcomes and avoid presenting associated Amount as committed or incremental revenue.'
ACCESS_LINK='<p class="access-reference">Access: <a href="permissions.html">role permissions and automation controls</a>.</p>'

def table(headers,rows):
 return '<div class="table-scroll"><table><thead><tr>'+''.join('<th scope="col">'+E(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+E(c)+'</td>' for c in row)+'</tr>' for row in rows)+'</tbody></table></div>'

ACCOUNT_ROWS=[
 ('Account Tier','Account · single-select','Tier 1 / Tier 2 / Tier 3; no default','Sales proposes/maintains for owned accounts; Sales Ops and RevOps govern assignments. Track prior/new tier, actor and time. Tier definitions and initial population rules must be agreed before backfill; do not infer a tier from revenue.'),
 ('RevOps Notes','Account · long text','Open text; length set at configuration','RevOps edits; RevOps and explicitly entitled Sales Ops read. Other teams have no access by default. Operational account context, separate from seller notes; audit updates.'),
 ('Primary DDN Partner Account Manager','Partner Account · User lookup','Active internal user','Partner Ops maintains the accountable commercial partner owner; bulk populate from the validated coverage list.'),
 ('Partner Technical Lead','Partner Account · User lookup','Active internal user','Partner Ops maintains with Sales Engineering; drives technical team assignment.'),
 ('Partner Admin Contact','Partner Account · Contact lookup','Contact associated with that partner account','Partner Ops maintains the partner’s administrative point of contact. This does not grant portal, approval or CRM administration rights.')]
TASK_ROWS=[
 ('Type','Observed picklist','Reuse Meeting: Phone / Meeting: Face to Face / Meeting: Video Conference.'),
 ('Subject','Observed combobox','Meeting — customer — purpose. Record a clear customer objective.'),
 ('Assigned To','Observed user lookup','One accountable meeting owner; follow-up Tasks get their own accountable owners.'),
 ('Name / Related To','Observed relationship controls','Link the customer Contact and the Opportunity when one exists; otherwise the Account. Contacts and Accounts were visible defaults; confirm Opportunity availability and multi-contact mapping during configuration.'),
 ('Due Date','Observed date','Scheduled meeting date; reschedule the existing Task rather than creating a duplicate.'),
 ('Status','Observed picklist','Not Started / In Progress / Completed / Waiting on someone else / Deferred / Cancelled / Archived. Complete only after the meeting occurred and its outcome is recorded.'),
 ('Priority','Observed picklist; default Normal','Reuse existing priority. Full choice list was not inspected.'),
 ('Activity Disposition','Observed dependent picklist; initially disabled','Confirm status dependencies and existing values. Map Held / No-show / Cancelled outcomes where supported; add only missing values after validation. Never count a no-show as a held meeting.'),
 ('First Meeting Scheduled','Observed checkbox','Use for the first customer meeting in the relevant opportunity/handoff. Confirm existing automation and reporting before changing its behavior; do not set it on every follow-up.'),
 ('Comments','Observed multiline text','Before: objective, agenda and participants. After: outcome, decisions, risks, and each action with owner + due date. Reuse this field; no new meeting-notes field.'),
 ('Completed Date/Time','Observed display','Preserve system completion evidence; do not use completion time as scheduled meeting time.'),
 ('Integration context','Observed sections','Clari Copilot: attendees, topics, competitors. SalesLoft: call/email/cadence metadata. Schedule Once: DDN Activity Id. Preserve mappings and provenance; do not make integration metadata seller-required.')]
# Five-column field register shared with the other ongoing activity tables.
TASK_CONTEXT={
 'Type':('Observed meeting choices: Meeting: Phone / Meeting: Face to Face / Meeting: Video Conference.','Classifies the activity. These meeting choices already exist.','Unchanged'),
 'Subject':('Existing combobox; descriptive text. Full suggestion list and storage limit unverified.','Identifies the activity in lists and activity history.','Unchanged'),
 'Assigned To':('Existing user lookup.','Identifies the accountable Task owner.','Unchanged'),
 'Name / Related To':('Existing relationship controls; Contact and Account were visible defaults. Opportunity availability and multi-contact mapping unverified.','Links the activity to a person and a related business record.','Unchanged'),
 'Due Date':('Existing date input.','Records the Task due date; does not capture a meeting time window.','Unchanged'),
 'Status':('Observed choices: Not Started / In Progress / Completed / Waiting on someone else / Deferred / Cancelled / Archived.','Records the Task work/completion state.','Validation change'),
 'Priority':('Existing picklist; observed default Normal. Full choice list not inspected.','Prioritizes the Task.','Unchanged'),
 'Activity Disposition':('Existing dependent picklist; disabled when inspected. Values and dependency rules unverified.','Additional activity disposition; exact outcome mapping requires confirmation.','Update mapping'),
 'First Meeting Scheduled':('Existing checkbox.','Indicates first-meeting scheduling; current automation and reporting mapping unverified.','Unchanged'),
 'Comments':('Existing multiline text input; storage limit unverified.','Captures activity notes and context.','Validation change'),
 'Completed Date/Time':('Observed display; system completion evidence.','Records when the Task was completed.','Unchanged'),
 'Integration context':('Observed Clari Copilot, SalesLoft and Schedule Once sections; individual metadata inputs vary.','Holds integration-provided activity context and source identifiers.','Unchanged')}

def activity_register(rows):
 headers=['Field / type','Inputs','Current purpose','Change','Updated purpose / placement']
 out='<div class="field-register-wrap"><table class="field-register"><thead><tr>'+''.join('<th scope="col">'+E(h)+'</th>' for h in headers)+'</tr></thead><tbody>'
 for key,name,kind,inputs,current,change,purpose in rows:
  css='unchanged' if change=='Unchanged' else 'added' if change=='New field' else ''
  out+='<tr data-field="'+E(key)+'"><td><strong>'+E(name)+'</strong><small>'+E(kind)+'</small></td><td>'+E(inputs)+'</td><td>'+E(current)+'</td><td><span class="change-tag '+css+'">'+E(change)+'</span></td><td>'+E(purpose)+'</td></tr>'
 return out+'</tbody></table></div>'

def account_register():
 return activity_register([('Account · '+name,name,kind,'Proposed inputs: '+inputs,'Not applicable — new proposed Account field.', 'New field',purpose) for name,kind,inputs,purpose in ACCOUNT_ROWS])

def meeting_register():
 rows=[]
 for name,kind,purpose in TASK_ROWS:
  inputs,current,change=TASK_CONTEXT[name]
  rows.append(('Task · '+name,name,'Task · '+kind,inputs,current,change,purpose))
 return activity_register(rows)

TASK_PROCESS=[
 'Create one meeting Task: choose the existing meeting Type, set a specific Subject, owner and Due Date, link the customer and deal, and put the meeting objective in Comments. Keep the meeting time and invitation in the existing calendar process.',
 'Update the same Task when the meeting moves. Keep it open until it occurs; record cancellations and no-shows distinctly using the validated Status / Activity Disposition mapping.',
 'After the meeting, record the outcome, decisions and agreed actions in Comments, then complete the held-meeting Task. Create separate follow-up Tasks with owners and due dates, and update the opportunity’s Next Step or SE Next Step when the agreed next action changes.',
 'Synergy provides a voice interface for creating meeting follow-up Tasks. Review the suggested owner, date, customer/deal link and action before saving. Voice-created Tasks follow the same permissions, validation and duplicate controls as manually created Tasks.'
]
TASK_AUTOMATION='Use a meeting-specific Task layout/action showing only the relevant fields. Validate meeting Type, Subject, owner, date and customer/deal link; completion of a held meeting requires outcome notes. Enforce edit rights for the Task owner and authorized deal collaborators, with Sales Ops / RevOps correction rights. Do not grant access to a private opportunity through a Task. Preserve integration metadata and deduplicate retries using the source activity ID where available. Report scheduled, held, cancelled/no-show and overdue follow-up separately; meetings do not advance sales stages automatically.'

# Tight implementation delta: requirement text plus meaningful acceptance check.
CHANGES=[
 ('New fields','Account coverage and segmentation','Add Account Tier, RevOps Notes, Primary DDN Partner Account Manager, Partner Technical Lead and Partner Admin Contact as specified in Account management.','Tier choices are exact; notes are restricted; inactive/wrong-account lookups fail; validated owner imports populate teams.', 'account-management',[1,13]),
 ('New fields','Pipeline entry snapshot','Use Pipeline Date and Pipeline Entry Amount as the single first-qualified-entry snapshot, retaining currency context.', 'Allowed direct Stage 1 creation and first valid entry to any numbered Stage 1–8 stamp once; re-entry and later CPQ changes never reset credit.', 's1',[24]),
 # Reserved BR-SS-117 slot: removed at user request; do not renumber later requirements.
 ('Removed','Meeting time capture','Use the existing Task Due Date; separate time fields are not required.','', 'ongoing-meetings-detail',[]),
 ('Label changes','Transacting Partner and contacts','Rename Primary Partner to Transacting Partner after attribution migration; use Association Sales Contact alongside Association Technical Contact. Retain Associated accounts.', 'History survives; sourcing and actual ship-to remain separate; existing IDs and relationship links remain intact.', 'ongoing-primary-detail',[5,10,13]),
 ('Picklists','Source and technical state','Use Direct / BDR / Marketing / Partner for Opportunity Source; add In Progress to Technical Outcome; CSP includes hyperscalers.', 'Legacy source crosswalk preserves provenance; ambiguous origins are reviewed; In Progress cannot pass the Technical Win gate.', 'creation',[7,14,29,30]),
 ('Automations','Partner team and access','Apply partner-account owners to the opportunity team on active association, with partner/territory scope and explicit direct-pipeline entitlements.', 'Creation, activation, owner change and deactivation reconcile membership; duplicate membership is avoided and independent grants remain.', 'ongoing-partners-detail',[2,3,32]),
 ('Automations','Direct route notification','Notify the manager and relevant partner coverage before customer pricing on a Direct route, including early budgetary quotes.', 'Notification is evidenced once per relevant route/pricing change; missing coverage is routed to Partner Ops; existing commercial approvals remain.', 's1',[33]),
 ('Validations','Origin protection and association detail','Separate registration from origin; protect accepted partner source; require explanation for Other role/classification.', 'A direct-origin registered deal stays Direct; a verified unregistered partner-origin deal can be Partner; unauthorized corrections fail with UI/API/import parity.', 'creation',[8,9,11]),
 ('Validations','Controlled quoting','Permit Budgetary in Stages 0–1 with context and existing commercial authority; retain Stages 2–5 quoting and Best and Final technical/commercial gates.', 'Early Budgetary can pass; early Best and Final fails; missing context/authority fails; Stage 6 correction and booked locks still work.', 'ongoing-quoting-detail',[26]),
 ('Reporting','Pipeline and enhancement demand','Exclude Stage 0 from qualified pipeline; credit first Stage 1 Amount once; aggregate enhancement demand by unique opportunity.', 'Stage regression, retries and multiple feature Cases do not duplicate credit or revenue; associated revenue is identified as exposure.', 'ongoing-product-detail',[23,24,31]),
 ('Access & permissions','Role ownership','Implement the Access and Permissions matrices for Sales, Sales Engineering, partner overlays, Sales Ops, Partner Ops, RevOps, Finance, Product and GSS. Configure Accounts, Opportunities, Contacts, Tasks and Cases; separate object permissions, record scope, field/action controls and general system entitlements.', 'Test allowed and denied records, fields and actions for every team across UI/import/integration, including combined permission-set grants, hierarchy/implicit access, partner AND territory scope and revocation. Commercial, booking, source-correction and bypass rights must not follow automatically from team membership. Apply the system-access matrix: export, import, API and setup require separate entitlements; broad View All / Modify All Data is excluded from base personas.', 'permissions.html',[3,9]),
 ('Activities','Customer meeting Tasks','Reuse inspected Task fields and meeting types; use existing Due Date and configure the disposition mapping; add Synergy voice follow-up guidance.', 'Scheduled/held/no-show reporting differs; outcomes and owned follow-ups are captured; no duplicate on retry; no meeting creates a stage advance.', 'ongoing-meetings-detail',[]),
 ('Retained controls','Contribution and existing integrations','Retain contribution rules until an approved replacement, existing multi-partner history, booked-credit freeze, and NVIDIA/contact/logistics controls.', 'Associations remain possible across the cycle without a universal partner gate; booked source/contribution history and existing integrations remain protected.', 'ongoing-contribution-detail',[4,32,34]),
 ('Enablement','Four deal courses','Organize existing lessons under Start the deal, Work the deal, Close the deal and Grow the deal; add a course overview, learning outcomes, practical takeaway and when-to-use guidance to each stream. Retain reminders, scenarios, practice and knowledge checks.', 'All 47 lessons appear once. Each of the four streams has an overview, learning outcomes, takeaway and application guidance. Search/stage filters, course expansion, knowledge checks and existing deep links work across all four streams.', 'enablement.html',[]),
 ('Open dependencies','Calendar and mappings','Calendar sync for meetings remains outstanding. Confirm Task disposition mappings, source crosswalk, account-tier criteria and current commercial approval entitlements before CRM configuration.', 'No calendar sync is described as delivered; no new approval thresholds or unsupported Task API/type claims are introduced.', 'ongoing-meetings-detail',[])
]

def replace_rules(s):
 pairs=[
 ('Given any stage outside 2–5, when quote creation/revision is attempted via UI, API or automation, then it is rejected; existing quote references remain readable.', 'Given Stage 0 or 1, controlled Budgetary quote creation/revision can pass with the required context and authority; Best and Final is blocked. Stages 2–5 retain regular quoting, with Technical Win, configuration and commercial checks before Best and Final release. Quote creation/revision at Stage 6 and after booking is blocked; use the Stage 6 → 5 correction path and preserve booked locks. Test UI, API and automation; existing quote references remain readable.'),
 ('Keep quoting disabled and Forecast Category (Sales) at Pre-pipeline.','Allow controlled Budgetary quotes and keep Forecast Category (Sales) at Pre-pipeline.'),
 ('Keep quoting disabled until Stage 2; forecast remains Pipeline.','Allow controlled Budgetary quotes in Stage 1; forecast remains Pipeline.'),
 ('Quoting · Stages 2–5 only','Quoting · Budgetary 0–1 / full 2–5'),
 ('Stages 2–5 · Sales + Sales Engineering</p><h3>Quoting','Stages 0–1 Budgetary / 2–5 broader quoting · Sales + Sales Engineering</p><h3>Quoting'),
 ('Separate fulfillment from partner credit.','Separate the commercial transacting partner from partner credit and physical delivery.'),
 ('Fulfillment Partner','Transacting Partner'),('fulfillment partner','transacting partner'),('Association Primary Contact','Association Sales Contact'),
 ('every other nonblank source → Sourcing Partner','Partner → Sourcing Partner'),
 ('Required for all other nonblank Opportunity Source selections. Populate from the registering Partner Account for deal registration, or the originating partner on other partner-source paths.','Required when Opportunity Source = Partner. Populate from verified originating Partner Account evidence; registration alone does not establish origin.'),
 ('At creation · Other nonblank sources','At creation · Partner'),
 ('Retain Opportunity Source choices;','Consolidate Opportunity Source to Direct / BDR / Marketing / Partner with an audited historical crosswalk;'),
 ('Populate attribution before creation validation: Direct → the User creating the opportunity; BDR → the originating BDR User; Marketing → the originating Campaign; deal registration → the registering Partner Account. Other partner-source paths copy the originating Partner Account when available. For deal registration, use the mapped partner-related Opportunity Source, not Direct or BDR. For BDR and Marketing origins set the matching Opportunity Source. Use origin-record references, not a background integration user, current owner or transacting partner, to identify the sourcing BDR, Campaign or Partner.',SOURCE),
 ('Disable quote creation and revision. Default the creation flow to Pre-pipeline;', 'Allow controlled Budgetary quoting under the Quoting activity rules. Default the creation flow to Pre-pipeline;'),
 ('Quote creation/revision stays blocked outside Stages 2–5.','Quote creation/revision is allowed in Stages 2–5, with controlled Budgetary-only access in Stages 0–1; it remains blocked at Stage 6 and after booking.'),
 ('Allow quote creation / revision only in Stages 2–5, across the UI, CPQ and automated paths.','Allow quote creation / revision in Stages 2–5 and controlled Budgetary-only quoting in Stages 0–1, across UI, CPQ and automated paths.'),
 ('keep quote creation/revision restricted to Stages 2–5.','apply controlled Budgetary access in Stages 0–1 and regular quoting in Stages 2–5, with Best and Final subject to technical and commercial gates.'),
 ('Proposed creation gate: linked Opportunity must be in Stages 2–5.','Creation gate: linked Opportunity must be in Stages 2–5, or Stages 0–1 for controlled Budgetary quoting only.'),
 ('Restrict existing CPQ quote creation/revision to Stages 2–5 and implement','Allow controlled Budgetary CPQ quoting in Stages 0–1 and regular quoting in Stages 2–5; implement'),
 ('Enable quote creation and revision only while the opportunity remains in Stages 2–5.','Enable quote creation and revision in Stages 2–5; controlled Budgetary access is also available in Stages 0–1.'),
 ('revise quotes only within Stages 2–5.','use controlled Budgetary quotes in Stages 0–1 and regular quote creation/revision in Stages 2–5.'),
 ('Technical Outcome is blank / Technical Loss','Technical Outcome is blank / In Progress / Technical Loss'),
 ('Technical Outcome is blank or Technical Loss','Technical Outcome is blank, In Progress or Technical Loss'),
 ('Require existing Technical Outcome = Technical Win before Stage 4; Technical Loss does not pass the gate. Retain the current picklist.','Require Technical Outcome = Technical Win before Stage 4; blank, In Progress and Technical Loss do not pass. Add In Progress to the existing picklist.'),
 ('Records the result of technical evaluation: Technical Win or Technical Loss.','Records technical evaluation state: In Progress, Technical Win or Technical Loss.'),
 ('reuse the existing Technical Outcome picklist.','reuse the existing Technical Outcome picklist and add In Progress.'),
 ('Use it for the fulfillment account rather than overall partner credit.','Use it for the primary partner through which the commercial transaction is conducted; keep source and contribution credit separate.'),
 ('Select the transacting partner and carry its account reference to the Order shipping workflow;','Select the primary partner through which the commercial transaction is conducted and carry its account reference to the Order workflow;'),
 ('Primary contact for the associated account.','Sales contact for the associated account; maintain the technical contact separately.'),
 ]
 for a,b in pairs:s=s.replace(a,b)
 return s

def within(s,id,fn,tag='section'):
 a=s.index('id="'+id+'"');b=s.index('</'+tag+'>',a)
 return s[:a]+fn(s[a:b])+s[b:]
def auto(s,id,text,tag='section'):
 if tag=='section':
  return within(s,id,lambda x:x.replace('<h3>Automations and validations</h3><ul>','<h3>Automations and validations</h3><ul><li>'+E(text)+' <a href="permissions.html">Access rules</a>.</li>',1),tag)
 return within(s,id,lambda x:x+ '<h4>Automations and permissions</h4><p>'+E(text)+'</p>'+ACCESS_LINK,tag)

def system(base):
 # Transform both the visible text and the structured CSV with the same rules.
 s=replace_rules(base)
 s=re.sub(r'(<tr data-field="Opportunity Source">.*?<td>)(<details.*?</details>)(</td>)',lambda m:m[1]+'<p>Proposed choices: Direct / BDR / Marketing / Partner.</p><details class="field-inputs"><summary>Historical choices and migration</summary><p>Current: Direct, Channel Partners, Server Vendors, BDR, Cloud, GSI, Marketing. Crosswalk validated partner-origin histories to Partner; retain original values, source evidence and Sourcing Partner. Resolve ambiguous records before migration. Partner identity/classification remains on the partner relationship; Route to Market stays separate.</p></details>'+m[3],s,flags=re.S)
 s=re.sub(r'(<tr data-field="Technical Outcome">.*?)</tr>',lambda m:m[1].replace('Dropdown inputs · 3 choices','Proposed choices · existing picklist + In Progress').replace('<li>Technical Win</li>','<li>In Progress</li><li>Technical Win</li>').replace('<span class="change-tag unchanged">Unchanged</span>','<span class="change-tag">Change inputs</span>')+'</tr>',s,flags=re.S)
 s=auto(s,'creation',SOURCE_LOCK+' '+TEAM)
 s=auto(s,'s0',PIPELINE+' '+EARLY)
 s=auto(s,'s1',PIPELINE+' '+TEAM+' '+DIRECT+' Sales owns commercial and qualification fields; assigned SEs maintain technical evidence. Partner overlays follow scoped collaboration rights.')
 s=auto(s,'s2',TECH+' Sales Engineering maintains technical validation; Product owns enhancement disposition, without forecast or commercial edit rights.')
 s=auto(s,'s3',TECH+' Sales Engineering owns the evidence; authorized Sales advances only when the gate passes.')
 for id,txt in [('s4','Sales owns Business Value and Paper Process in Stage 4. Finance and Sales Ops act only within delegated commercial authority; SEs maintain technical evidence. '+EARLY),('s5','Sales maintains procurement evidence; Finance and delegated commercial approvers validate their own controls. Access alone never grants approval authority.'),('s6','Sales owns the customer won decision; Order Management retains booking authority. Sales Ops coordinates discrepancies and GSS owns deployment Case work. Quote correction follows Stage 6 → 5.'),('s7','Only authorized Order Management confirms booking. Finance maintains authorized order/invoice facts; GSS maintains Case delivery and deployment evidence. Protect booked opportunity facts.'),('s8','GSS and Finance maintain their Case/order evidence under their respective entitlements. Stage 8 automation uses verified delivery evidence and preserves booked locks.'),('lost','Sales records the loss decision and evidence; Sales Ops / RevOps correct only within delegated authority with history retained.')]:s=auto(s,id,txt)
 for id,txt in [('ongoing-quoting-detail',EARLY+' '+DIRECT),('ongoing-partners-detail',TEAM+' '+SCOPE+' '+OTHER+' '+CONTRIBUTION),('ongoing-contribution-detail',CONTRIBUTION+' '+SOURCE_LOCK),('ongoing-primary-detail','Sales and assigned partner overlays may maintain the Transacting Partner within their deal scope. Partner Ops governs partner-account data. Commercial and ship-to authority remain separate.'),('ongoing-conversion-detail',PIPELINE+' RevOps owns lifecycle mappings; sellers cannot edit system event timestamps.'),('ongoing-product-detail',ENHANCEMENTS+' Product maintains feature disposition; Sales supplies customer context; RevOps owns reporting logic.'),('ongoing-next-detail','Sales maintains customer actions; Sales Engineering maintains technical next actions. Task completion does not reset review timestamps unless an explicit review action is performed.'),('ongoing-risk-detail','Assigned Sales Engineering maintains technical risk, blocker and next action. Sales and authorized overlays contribute evidence within deal scope.'),('ongoing-buying-committee','Sales and authorized deal collaborators maintain customer Contact Roles; record visibility and field permissions still apply.'),('ongoing-poc-detail','Sales Engineering owns POC status and evaluation evidence. Collaborators cannot bypass the existing POC or Technical Win gates.'),('ongoing-nvidia-detail','Sales, Sales Engineering and assigned NVIDIA partner coverage maintain permitted engagement information; Partner Ops owns account coverage. Existing relevance and status validation remains.'),('ongoing-logistics-detail','Sales gathers customer logistics; Order Management verifies booking and ship-to facts; GSS owns Case deployment evidence.'),('ongoing-ipg-detail','Existing IPG and commercial approvers retain their delegated authority; opportunity-team membership grants no additional approval right.'),('win-wire','Sales maintains existing win inputs; existing internal recipients and recognition scope remain. Sales Ops coordinates corrections within scope.')]:s=auto(s,id,txt,'article')
 s=auto(s,'order-current-state','Order Management controls booking and order reconciliation; Finance maintains authorized invoice facts. Sales, partner overlays and GSS receive only the order context needed for their duties. Booked opportunity facts stay locked.','article')
 s=auto(s,'case-current-state','GSS owns deployment status, completion and value-realization evidence on the PS Case. Sales and SEs contribute customer/technical context; Finance reconciles authorized order facts. Case access and updates do not reopen or edit booked opportunity results.','article')
 # Account management and meeting activities follow the same visual vocabulary.
 accounts='<article class="ongoing-detail" id="account-management"><header><p class="label">Account object · Sales / Partner Ops / RevOps</p><h3>Account management</h3></header><h4>Process</h4><p>Maintain account tier, operational notes and named partner coverage at the Account level.</p><h4>Connected fields</h4>'+account_register()+'<h4>Automations and permissions</h4><p>'+E(TEAM+' '+SCOPE)+'</p>'+ACCESS_LINK+'<a href="#ongoing">All ongoing activities ↑</a></article>'
 meetings='<article class="ongoing-detail" id="ongoing-meetings-detail"><header><p class="label">Across the lifecycle · Customer-facing teams</p><h3>Customer meetings and follow-up Tasks</h3></header><h4>Process</h4><ol>'+''.join('<li>'+E(x)+'</li>' for x in TASK_PROCESS)+'</ol><h4>Connected fields</h4><p>Inspected in Salesforce’s New Task: Default form on 29 September 2026 using Computer Use. Field labels and the listed Type/Status values were observed; API names, storage limits, record-type permissions and dependency mappings still require configuration verification. No Task was saved.</p>'+meeting_register()+'<details><summary>Additional fields observed</summary><p>Type(R); MQL Campaign; Call Duration, Call Type, Call Object Identifier, Call Disposition, Call Sentiment and Call Result; Task Subtype; Task Record Type (Default); Lead; Contact; Lead Status when Activity Logged; SalesLoft call-to, replies, bounce, email-template, cadence, click/view counts and step/ID metadata. Retain these mappings; they are not extra meeting-entry requirements.</p></details><h4>Automations and permissions</h4><p>'+E(TASK_AUTOMATION)+'</p>'+ACCESS_LINK+'<p class="open-dependency"><strong>Outstanding: calendar sync.</strong> Task creation does not send or synchronize calendar invitations. Calendar ownership, invite/update/cancellation behavior and duplicate matching remain to be designed.</p><a href="#ongoing">All ongoing activities ↑</a></article>'
 s=s.replace('<div class="activity-jump-list">','<div class="activity-jump-list"><a href="#ongoing-meetings-detail">Customer meetings</a><a href="#account-management">Account management</a>',1)
 s=s.replace('<article class="ongoing-detail" id="ongoing-quoting-detail">',meetings+accounts+'<article class="ongoing-detail" id="ongoing-quoting-detail">',1)
 # Surface the new activities in navigation and the lifecycle overview.
 s=s.replace('<a href="#implementation-requirements">Implementation requirements</a>','<a href="#change-log">Change log</a><a href="#implementation-requirements">Implementation requirements</a>',1)
 s=s.replace('<div id="ongoing-submenu"', '<div id="ongoing-submenu"',1)
 marker='<a href="#ongoing-quoting-detail" data-activity-link>'
 s=s.replace(marker,'<a href="#ongoing-meetings-detail" data-activity-link><b aria-hidden="true">•</b>Customer meetings</a><a href="#account-management" data-activity-link><b aria-hidden="true">•</b>Account management</a>'+marker,1)
 s=s.replace('<div class="ongoing-grid">','<div class="ongoing-grid"><a href="#ongoing-meetings-detail" class="ongoing-band ongoing-meetings"><b>Customer meetings · Lifecycle</b><span>Task → outcome → owned follow-up. Synergy voice; calendar sync outstanding.</span></a><a href="#account-management" class="ongoing-band ongoing-accounts"><b>Account management</b><span>Tier 1 / 2 / 3, partner coverage and RevOps Notes.</span></a>',1)
 # First-entry snapshot shown in the stage field register, not just implementation notes.
 s=within(s,'s1',lambda x:x.replace('</tbody>', ''.join('<tr data-field="'+E(n)+'"><td><strong>'+E(n)+'</strong><small>'+E(t)+'</small></td><td>System-maintained</td><td>First qualified pipeline entry</td><td>New field</td><td>'+E('Stamp once at first valid entry to any numbered Stage 1–8, including allowed direct Stage 1 creation and permitted skips. Capture date/time and Amount with currency on the same event. Preserve on regression, re-entry and later quote changes; current Amount and actual-stage dates remain separate.')+'</td></tr>' for n,t in [('Pipeline Date','Date/Time'),('Pipeline Entry Amount','Currency + currency context')])+'</tbody>',1))
 s=sales_ops.system(s,within,auto,activity_register)
 s=audit.system(s,within,auto)
 # New change log and complete CSV parity.
 data=json.loads(re.search(r'<script[^>]*id="requirements-data"[^>]*>(.*?)</script>',s,re.S)[1])
 for i,(kind,title,req,accept,target,nums) in enumerate(CHANGES,115):
  data.append(['RevOps / Colin Brown',f'BR-SS-{i:03}',kind+' / '+title,req,'Approved process review · 29 September 2026','','Must Have','Relevant owners in Access and Permissions',accept,'','Approved items: '+(', '.join(map(str,nums)) if nums else 'Additional user request')+'. Specification only; verify existing configuration and implement only the gap.'])
 data=[data[0]]+[row for row in data[1:] if int(row[1].split('-')[-1]) not in REMOVED_IMPLEMENTATION_IDS]
 # Assemble complete rules before rendering the detailed log and concise export.
 refinements={9:TECH,115:' '.join(name+': '+kind+'. Inputs: '+inputs+'. '+purpose for name,kind,inputs,purpose in ACCOUNT_ROWS),116:PIPELINE,120:TEAM+' '+SCOPE,121:DIRECT,122:SOURCE+' '+SOURCE_LOCK+' '+OTHER,123:EARLY,124:PIPELINE+' '+ENHANCEMENTS,126:TASK_AUTOMATION+' Synergy provides voice creation of follow-up Tasks; users review proposed details before saving. Calendar sync remains outstanding.'}
 for row in data[1:]:
  n=int(row[1].split('-')[-1])
  if n==5:row[4]='Establish business fit and discovery evidence before solution design; early Budgetary quoting does not bypass qualification.'
  if n==6:row[4]='Permit controlled early budgetary estimates while preserving discovery, technical/commercial gates and booked-record locks.'
  if n in refinements:row[10]+=' '+refinements[n]
 data=sales_ops.requirements(data)
 data=audit.requirements(data)
 start=s.index('<section class="stage" id="implementation-requirements">')
 end=s.index('<script id="requirements-data"',start)
 # Keep the detailed action log intact; summarize only the requirements table/export.
 action_log=change_log(data,s[:start],ACCOUNT_ROWS)
 data=simplify(data)
 # Restore the original card and scrollable table with the current complete data.
 requirements=s[start:end]
 requirements=requirements.replace('<button type="button" id="download-requirements">Download requirements CSV</button>', '<a id="download-requirements" href="downloads/implementation-requirements.csv" download="GTM-Implementation-Requirements.csv">Download requirements CSV</a>')
 register='<table id="requirements-table"><thead><tr>'+''.join('<th scope="col">'+E(x)+'</th>' for x in data[0])+'</tr></thead><tbody>'+''.join('<tr id="requirement-'+row[1]+'" data-requirement="'+row[1]+'">'+''.join('<td>'+E(c)+'</td>' for c in row)+'</tr>' for row in data[1:])+'</tbody></table>'
 requirements=re.sub(r'<table id="requirements-table">.*?</table>',lambda m:register,requirements,count=1,flags=re.S)
 s=s[:start]+action_log+requirements+s[end:]
 s=re.sub(r'<script>document.getElementById\("download-requirements"\).*?</script>','',s,flags=re.S)
 s=re.sub(r'(<script[^>]*id="requirements-data"[^>]*>).*?(</script>)',lambda m:m[1]+json.dumps(data,ensure_ascii=False).replace('</','<\\/')+m[2],s,count=1,flags=re.S)
 return s

ROLE_ROWS=[
 ('Sales','Owned opportunities/accounts and explicitly shared deal teams.','Qualification, customer meetings, buying roles, commercial next steps, Route to Market, Account Tier and stage requests after gates pass.','No accepted partner-source rewrite; no system forecast/snapshot edit, approval-by-membership or OM booking right.'),
 ('Sales Engineering','Assigned technical coverage and shared deal teams.','Technical Value, configuration/evaluation evidence, Technical Outcome, POCs, technical risks, SE Next Step and technical meeting Tasks.','No independent commercial, Amount, source-correction or booking authority. Technical Win needs customer preference evidence.'),
 ('Partner overlays','Assigned partner plus geo/territory coverage; direct-pipeline access only by explicit entitlement.','Association sales/technical contacts, plans, permitted partner relationships and scoped meeting/technical collaboration.','No forecast or Amount edit, registration approval, source correction or commercial approval by default.'),
 ('Sales Ops','Assigned operating regions/process queues; explicit support access.','Account-tier governance, routing/data-quality support, approved imports and operational corrections. RevOps Notes read only when explicitly entitled.','No blanket bypass, partner-source correction, commercial approval or booking authority. Each privileged action requires its own entitlement.'),
 ('Partner Ops','Partner accounts, coverage and associated deal records within remit.','Partner coverage owners, Partner Admin Contact, partner data and association quality. Authorized registration reviewers approve registrations.','Source corrections require a separate explicit correction entitlement and audit. Registration approval does not prove origination or grant price authority.'),
 ('RevOps','Cross-functional process/reporting scope under approved administrative entitlements.','Lifecycle/reporting mappings, source-correction governance, controlled imports, Account Tier policy, RevOps Notes and permission administration.','Administrative access is not blanket commercial/booking approval. Bypass remains rule-specific, authorized and audited.'),
 ('Finance','Commercial approval, order, invoice and revenue records needed for assigned duties.','Delegated commercial approvals; authorized order/invoice facts and financial reconciliation.','No seller qualification, technical evaluation or partner attribution editing by default. OM retains booking transition authority.'),
 ('Product','Linked enhancement Cases and permitted customer/deal context; aggregate demand reporting.','Enhancement triage, disposition and approved roadmap communication; read deduplicated opportunity exposure.','No opportunity stage, forecast, Amount, pricing or attribution edit by default; no implied roadmap commitment from a Case.'),
 ('GSS','Assigned deployment/support Cases, orders and necessary customer/deal context.','Deployment planning, delivery/receipt evidence, Case progress, value realization and Time to Value.','No booked opportunity rewrite, commercial approval or source edit. Deployment proceeds on Cases after opportunity completion.')]

EXTRA_DEFINITIONS=[
 ('Account Tier','account-context','The account-level segmentation choice: Tier 1, Tier 2 or Tier 3. Apply the agreed tier criteria rather than inferring a tier from a single opportunity amount.',None),
 ('RevOps Notes','account-context','Restricted open-text operational context maintained by RevOps on the Account.',None),
 ('Primary DDN Partner Account Manager','account-context','The internal commercial owner of a partner relationship, maintained on the partner Account and used for scoped opportunity-team assignment.',None),
 ('Partner Technical Lead','account-context','The internal technical coverage owner on a partner Account, brought into relevant opportunities through active partner associations.',None),
 ('Partner Admin Contact','account-context','The partner’s administrative point of contact on its Account. This relationship does not grant system or approval permissions.',None),
 ('Pipeline Entry Amount','conversion','The Amount and currency context captured at first valid entry into any numbered Stage 1–8. It stays fixed for pipeline-generation reporting while current Amount may change.', 'A deal enters Stage 1 at $300,000 and is later quoted at $400,000. First-entry credit remains $300,000; current Amount reflects the later quote.'),
 ('Pipeline Date','conversion','The first valid entry into any numbered Stage 1–8, including allowed direct Stage 1 creation. It differs from Created Date and does not reset on regression or re-entry.','A permitted 0 → 4 move sets Pipeline Date equal to Stage 4 Date; Stage 1 Date stays blank until that stage is actually visited.'),
 ('Technical fit','technical-value','Evidence that the proposed solution meets the customer’s requirements. Customer preference for DDN is additionally needed for Technical Win.',None),
 ('In Progress — Technical Outcome','technical-outcome','Technical evaluation or customer preference is not yet resolved. Record blockers and next actions; this state cannot pass the Stage 3 exit gate.',None),
 ('Meeting Task','meetings','A Task that records a customer meeting’s purpose, owner, scheduled date, customer/deal relationship and outcome. Follow-up actions are separate owned Tasks.',None),
 ('Synergy voice follow-up','meetings','The Synergy voice interface for creating meeting follow-up Tasks. Review owner, due date and customer/deal links before saving. Calendar sync remains outstanding.',None),
 ('Association Sales Contact','partner-accounts','The sales contact for the account associated with a deal, distinct from its technical contact.',None),
 ('Association Technical Contact','partner-accounts','The technical contact for the account associated with a deal, distinct from its sales contact.',None),
 ('Deal registration','source','A partner registration linked to a deal. It can apply regardless of who originated the opportunity and does not automatically determine Opportunity Source.', 'A seller-originated deal can retain Direct source when a transacting partner later registers it.')]

EXTRA_DEFINITIONS += [(f"Stage {n} Date", "conversion", f"The system-maintained date and time of first actual entry to Stage {n}. Skipped stages stay blank and re-entry does not reset the value. Use transition history to measure time across repeated visits.", None) for n in range(7)]
EXTRA_DEFINITIONS.append(("AE Next Steps", "next-steps", "The read-only dated history of changes to the editable Next Step. Existing automation maintains the log; a weekly review is recorded separately.", None))
