"""Approved October 19, 2026 net changes; pending designs are never active gates.

Existing BR IDs remain stable. Release metadata drives the log, table and CSV.
"""
import html
import re

DATE = '2026-10-19'
TITLE = 'New requirements as of Monday, October 19th'
E = lambda value: html.escape(str(value), quote=True)
NVIDIA = ('Require a NVIDIA Engagement dropdown selection on entry to Stage 2 and beyond, including stage skips. Reuse Amy’s validated values: Not Engaged, Referred, Technical Support, Solutioning, Direct End Customer Engagement and Partner Engagement. '
          'When anything other than Not Engaged is selected, require the NVIDIA contacts and their roles, GPU Type, GPU Quantity and Project Type. Enforce these dependent requirements when engagement is changed later, not only at stage advancement. '
          'Support multiple NVIDIA contacts, preferably through Opportunity Contact Roles; map NVIDIA Sales Representative, Technical Lead and Partner Lead to the existing role model before configuration. '
          'Keep NVIDIA Engagement, GPU Type, GPU Quantity and Project Type together in the Opportunity summary. GPU and project fields remain visible and editable when Not Engaged; preserve their values. '
          'Use the existing Associated accounts relationship for NVIDIA plans and next steps; an association is not the trigger for the new Stage 2 gate. No additional Amy approval is required.')
POC = ('Replace the proposed POC Status presentation with POC Approved. Notify both the AE Manager and SE Manager to review; check POC Approved only after both approve, retaining approvers and approval times. '
       'Keep separate completion/cancellation evidence: when POC Required? is Yes, only documented Completed or Cancelled permits advancement beyond Stage 2, including skips. Approval alone is not completion. '
       'Retain POC Required?, POC Engagement and POC Updates. The storage mapping for separate completion evidence is pending; do not remove the existing completion gate.')
COMMITMENT = ('Before leaving Stage 5, require an approved final quote marked Primary and matching customer commitment documents attached as Opportunity Files by Sales. '
              'A qualifying fully executed contract can satisfy the commitment without a PO unless the contract makes a PO a condition of the purchase obligation. A PO, contract or both must establish the binding commitment and match the approved Primary Quote. '
              'Prompt for the applicable file upload when the commitment is secured; replace PO-only requiredness and error messages so a valid contract-only submission can pass. Identify the governing quote and its matching documents; retain historical PO information.')
REJECTION = ('OM may reject an opportunity from Stage 6 — Won Decision back to Stage 5 — Procurement. Require rejection notes explaining the correction and notify the Opportunity team and RevOps team. '
             'Retain the rejection actor, time and notes. Resubmission passes the Stage 5 handoff requirements again. Use an explicit rejection action; changing an unrelated review status must not advance stages.')
PERMISSIONS = ('Sales and Sales Engineering continue their existing permitted forward stage actions after the applicable gates pass; routine forward progression does not require Sales Ops. OM retains booking acceptance for 6 → 7. '
               'Only System Administrators or Sales Ops may move opportunities backwards from Won Decision or Closed Won, except the authorized OM rejection from 6 → 5. '
               'A backward action does not unlock booked facts or authorize an unapproved post-booking commercial change.')
CLOSE_DATE = ('Order Management owns confirmation of Close Date. Lock it at Stage 7 — Closed Won; only a System Administrator may change it after locking, with an audit trail. '
              'Sales maintains expected timing while open through the existing forecasting process. Stage regression, delivery progression and integration updates must not bypass the booked Close Date lock. '
              'Close Date and the policy’s official Booking Date are distinct concepts; do not infer period eligibility from a stage change.')
MEDIA = ('Capture Digital or Physical documentation/media fulfillment separately from IPG. Digital requires a fulfillment email. Prompt in Stage 4 and require completion before leaving Stage 5. Replace the existing booking question rather than duplicating it.')
LOGISTICS = ('Keep Estimated Shipping Date and Requested Delivery Date in Stage 5 where applicable. Software-only deals are exempt from hardware-specific delivery requests. Hardware-containing deals require IPG Completed, subject to confirmed hardware exceptions; software-only may use Not Required. Do not invent shipping dates for software.')
TRANS = ('Transacting Partner is the expected DDN bill-to partner, captured before the order phase and reconciled against the final quote/order. That partner must also be represented in Associated accounts. '
         'Keep the existing Primary Partner → Transacting Partner rename dependency: replace the single-partner credit trigger first. Transacting Partner changes do not change Opportunity Source or erase other partner contributions.')
PARTNERS = ('Extend the existing Opportunity Partner Opportunity Influence / Associated accounts mechanism; preserve Account-level relationships. Maintain one account–opportunity association with structured, reportable primary and additional roles and contribution evidence for each partner. '
            'Keep account classification separate from role. Record who transacts, who originated or influenced the deal, and the evidence, timing, contacts, plan and next action for each participant. '
            'Represent distributor → reseller/downstream partner → customer relationships without inventing a distributor on direct-reseller deals. For NCP/service-provider motions, distinguish the contracting buyer from known underlying customers and single-/multi-tenant delivery. '
            'The Opportunity Account follows the actual commercial motion; it is not automatically the ultimate end customer. Reports must show partner-level participation and deduplicate company pipeline/bookings by opportunity. '
            'Existing source protection, booked-credit freeze, audited overrides and coverage permissions remain. Detailed replacement credit algorithms are pending; an association or registration alone does not prove sourcing.')
DEPLOY = ('Extend the existing Stage 7 coordinating deployment Case handoff: derive hardware/software/both from Opportunity Products and transfer it with applicable acceptance-testing requirements, support/start/end dates, logistics and licensing information. '
          'OM and GSS record confirmation that the in-scope delivery is on-site and working on the deployment Case. Keep receipt, working deployment, contractual acceptance and value realization distinct. '
          'Record actual events when they occur; later deployment evidence must not delay booking. Reuse the existing Case on retry/re-entry. Stage 8 remains in the approved model while its removal proposal is pending.')
STATUS = ('Use Order Review Status with default New Order (no sub-status); In Progress / In Progress; Rejected / PO Rejected, Incomplete Stage Information, Both PO & Stage Information, or Other with Comments; '
          'Booked / Booked with no Exceptions, Booked with Booking Policy Exceptions, or Booked with Exceptional Approvals. Adapt PO rejection labels to cover the customer commitment document on contract-only orders. '
          'Map historical values into the two-tier model. A Booked label does not replace OM reconciliation or exception approval. Only the explicit rejection action returns 6 → 5; other status edits do not automatically change stages.')
HISTORY_STOP = ['Tracking Number', 'Invoice Date', 'Last Modified by Owner', 'AE Next Steps', 'Description', 'Forecast Category (standard)', 'Stage', 'SAL Completion Date', 'SAL Influence', 'Lead Source', 'PO In-House', 'POC Status']
HISTORY = ('Stop future field-history tracking for: '+', '.join(HISTORY_STOP)+'. Keep the fields and all history already recorded. '
           'Retain tracking for Amount, Close Date, Opportunity Owner, Opportunity Name, Opportunity Source, SAL Status and Primary Quote. Add Technical Outcome, Transacting Partner (existing Primary Partner field) and Territory; confirm the exact Territory field. '
           'Stop Forecast Category (Sales) tracking only after proving its changes remain accessible in reporting. Keep the existing AE Next Steps dated log; do not add history slots for Next Step or first-entry/pipeline/SAL timestamps. '
           'Existing POC-update, route-change, override and Account/Case audit requirements remain; their storage choices are pending, not new audit requirements.')
PENDING_STAGE8 = ('Pending Salesforce review — remove Stage 8 and relocate its applicable fields to the Stage 7 OM section. Until approved, retain Stage 8 and its existing delivery milestone. '
                  'If approved, update software-only completion, GCP automation, forecast/stage mappings, permissions, reports, historical interpretation and the Case Value Tracking Start Date. Future receipt/deployment facts are captured when they occur, not as booking prerequisites.')
PENDING_PARTNER = ('Pending design — decide whether each partner independently carries Sourced, Influenced and Fulfilled credit and how multiple roles coexist; finalize any per-partner Partner-Led/Joint timing and its reconciliation with Partner-only/Sales-only, including GCP. '
                   'Resolve renewal attribution inheritance and any split-source credit separately. Do not automatically source a deal from registration, overwrite source when the transacting partner changes, or treat draft compensation rules as approved.')
PENDING_OTHER = ('Pending implementation mappings — decision-maker Contact Roles versus narrative fields; separate POC completion-evidence storage; hardware IPG exceptions; validation-bypass ownership and rule scope; remaining field-history storage choices; historical Opportunity Source crosswalk. '
                 'These are decisions within existing controls, not permission to create duplicate fields, bypass booking-policy approvals or remove existing audit evidence.')

# Updated requirement, acceptance, notes, net-change explanation. Existing IDs only.
REVISED = {
 8: ('Approve POCs through both managers while retaining separate evaluation completion evidence.', POC, 'Reuse existing POC controls and preserve history; completion storage mapping remains pending.', 'Add dual-manager approval; replace the proposed status presentation without removing completion evidence.'),
 11: ('Accept a complete, matched customer commitment and final Primary Quote before Won Decision.', COMMITMENT+' '+MEDIA+' '+LOGISTICS, 'Retain Stage 4 Primary Quote; change Stage 5 exit validation and upload prompts.', 'Allow qualifying contract-only commitments and tighten final quote/document matching.'),
 13: ('Give OM a reconciled order and an explicit rejection path before booking.', 'Only authorized OM accepts 6 → 7 after reconciliation. '+REJECTION, 'Booked protections and the existing Case handoff remain.', 'Add OM rejection 6 → 5, notes, audit and Opportunity team/RevOps notifications.'),
 17: ('Extend the Stage 7 deployment Case handoff with product and acceptance information.', DEPLOY, 'Case creation/linking and retry deduplication already exist; extend them.', 'Transfer product classification, testing and start/end information; record on-site and working confirmation.'),
 21: ('Make every participating account’s roles and contribution reportable on the existing association.', PARTNERS, 'Use the existing object; detailed credit algorithms remain pending.', 'Structure additional roles and per-partner contribution instead of relying only on narrative.'),
 23: ('Require NVIDIA engagement at Stage 2 and make GPU opportunity data visible and reportable.', NVIDIA, 'Add engagement, contact and GPU views to leader click-through, pipeline/forecast reports and the NVIDIA dashboard; show pipeline, bookings and GPU demand by type, region, segment and sales team.', 'Replace association-only requiredness with Stage 2/dropdown-driven validation; expand summary and reporting.'),
 26: ('Remove unnecessary legacy prompts while retaining the newly required decision-maker capture.', 'Keep the existing field moves except Technical Decision Maker is required at Stage 3 and Decision Maker at Stage 4. Preserve historical data.', 'Resolve Contact Role versus narrative mapping before adding storage; see BR-SS-133.', 'Reverse the proposed removal of the two decision-maker prompts.'),
 30: ('Clarify the early bill-to meaning of Transacting Partner after attribution migration.', TRANS, 'The rename and replacement attribution dependency already exist.', 'Specify expected DDN bill-to, associated-account representation and final quote/order reconciliation.'),
 33: ('Use the deployed win/loss taxonomy and map historical values without recreating live features.', 'Mark the already-live Won/Loss Reason changes as existing. Supply fields, current values and a proposed crosswalk for business mapping; preserve original historical values.', 'Do not commission duplicate fields or repeat the completed rollout.', 'Correct implementation status and make the historical-mapping handoff explicit.'),
 34: ('Capture conditional customer interview information for New and Existing Business only.', 'For New/Existing Business, eligibility is required at win/loss except Stage 0 misqualification. Yes requires a Contact; No requires a reason. Do not extend this rule to renewals.', 'Reuse deployed Win/Loss fields; renewal notification scope is not changed by the interview exemption.', 'Remove renewals from the interview-rule expansion.'),
 39: ('Populate multi-product context from deal products and update the Managed Lustre label.', 'Allow initial manual multi-selection; derive Product Types from Opportunity Products when available. Rename 1P Google to Managed Lustre, preserving data/history. Update affected reports, CPQ mappings and integrations without double-counting deals.', 'Multi-product selection itself is already in scope.', 'Add product-driven population and the Managed Lustre label change.'),
 50: ('Apply IPG requirements according to hardware/software scope.', 'Hardware-containing deals require Completed before Stage 6, subject to agreed hardware exceptions. Software-only deals may use Not Required.', 'Reuse the existing IPG disposition; hardware exceptions remain pending.', 'Resolve the software-only exemption and hardware completion requirement.'),
 54: ('Keep the Stage 5 shipping estimate only where physical shipment applies.', 'Estimated Shipping Date remains in Stage 5; software-only deals are exempt from hardware shipping-date requests.', 'Keep the original estimate distinct from Order shipping commitments.', 'Resolve software-only applicability; no additional date field.'),
 55: ('Keep the Stage 5 delivery request only where physical delivery applies.', 'Requested Delivery Date remains in Stage 5 and is reconciled with the Order. Software-only deals are exempt from hardware delivery-date requests.', 'Reuse the existing Order date.', 'Resolve software-only applicability; no duplicate Order field.'),
 56: ('Implement the approved two-tier Order Review Status model.', STATUS, 'Require OM reviewer in In Progress and rejection notes; see BR-SS-139 and BR-SS-013.', 'Replace the unresolved status mapping with the approved statuses and sub-statuses.'),
 68: ('Synchronize Oracle invoice numbers into the existing Invoice Reference.', 'Oracle updates the existing Invoice # / Invoice Reference field when issued, preserving history and multiple related invoice references as applicable.', 'The rename already exists; invoice issue does not control physical receipt.', 'Make Oracle synchronization explicit.'),
 69: ('Extend the existing deployment Case link with the agreed handoff information.', DEPLOY, 'Part of BR-SS-017; no second Case creation mechanism.', 'Add product/testing/start-date transfer to the existing linked Case.'),
 72: ('Identify the expected DDN bill-to partner before order creation.', TRANS, 'Part of BR-SS-030; ship-to remains independent.', 'Clarify bill-to semantics and reconciliation, without another partner lookup.'),
 74: ('Record POC Approved after both manager approvals.', POC, 'Part of BR-SS-008; retain separate Completed/Cancelled evidence.', 'Replace the proposed POC Status presentation with the approval checkbox.'),
 86: ('Capture interview eligibility for New and Existing Business without extending it to renewals.', 'New/Existing wins and losses require eligibility except Stage 0 misqualification. Renewals are excluded from this expansion.', 'Part of BR-SS-034; use the deployed field.', 'Remove renewal requiredness.'),
 87: ('Identify a customer interview Contact when eligible and in scope.', 'For in-scope New/Existing deals, Yes requires a linked Salesforce Contact. Do not extend this conditional interview rule to renewals.', 'Reuse the deployed interview Contact field.', 'Apply the renewal exemption to dependent Contact validation.'),
 88: ('Capture the reason outreach is declined when the interview rule applies.', 'For in-scope New/Existing deals, No requires WL Reason Cannot Approach. Do not extend this conditional interview rule to renewals.', 'Reuse the deployed reason field.', 'Apply the renewal exemption to dependent reason validation.'),
 100: ('Make primary and additional account roles separately reportable per opportunity.', 'Keep one account–opportunity association and classification; capture primary and additional roles in structured reportable form with per-partner contribution evidence.', 'Part of BR-SS-021. Detailed credit categories and timing remain pending.', 'Replace narrative-only secondary contributions with structured reporting.'),
 111: ('Retire Demand Gen intake and complete the existing Stage 0 SAL migration.', 'Marketing, BDR and partner teams create new inbound opportunities in Stage 0. Move the Demand Gen SAL process and records to Opportunity; preserve decisions, actors, dates, notes and submission history. Coordinate cutover and source/campaign mapping with MAP.', 'Keep the existing Stage 0 acceptance, qualification and seller-direct paths; no parallel SAL system.', 'Explicitly retire Demand Gen intake and define its migration/cutover.'),
}
# New IDs start after the existing maximum, 132. Pending items have no active gate.
NEW = [
 (133,'Stage decision-makers','Require the appropriate decision-makers at Stages 3 and 4.','Technical Decision Maker is required at Stage 3; Decision Maker is required at Stage 4. Reuse the existing contact/field model after confirming the mapping.','Confirmed'),
 (134,'Renewal procurement','Add Stage 5 Procurement to the renewal sales process.','Renewals can progress 4 → 5 → 6, with Stage 5 in Commit; retain valid renewal-specific gates.','Confirmed'),
 (135,'Backward stage authority','Restrict backward moves from Won Decision and Closed Won.',PERMISSIONS,'Confirmed'),
 (136,'Close Date ownership','Give OM Close Date ownership and restrict post-booking changes.',CLOSE_DATE,'Confirmed'),
 (137,'Quote installation location','Capture whether installation location differs from shipping.','On final quotes, require Installation Location when it differs from shipping. Budgetary quotes are exempt. Reuse existing location storage where suitable.','Confirmed'),
 (138,'Media/docs fulfillment','Capture Digital/Physical fulfillment separately from IPG.',MEDIA,'Confirmed'),
 (139,'OM review workspace','Provide a rep-visible OM section and an accountable reviewer.','Only authorized OM users edit OM review fields. Use a User lookup restricted to the OM group; require it when Order Review Status is In Progress. Reps can read the section.','Confirmed'),
 (140,'Booking turnaround','Report Stage 6 to Stage 7 turnaround against the 24-hour target.','Use transition history to measure 6 → 7 and show rejection/resubmission cycles. The operational target does not extend the booking-period cutoff.','Confirmed'),
 (141,'ERP status','Show read-only Oracle ERP Status on the opportunity.','Synchronize In Progress, Booked, Invoiced and Sync Error from Oracle; business users cannot edit the synchronized status.','Confirmed'),
 (142,'Support and revenue dates','Capture support and expected revenue dates and carry relevant context to the Case.','Reuse suitable fields for Support Start Date and Expected Revenue Recognition Date. Transfer applicable start-date and acceptance information into the deployment Case. Booking is distinct from revenue recognition.','Confirmed'),
 (143,'Deployment product classification','Derive hardware/software/both classification from Opportunity Products.','Carry the derived classification to the coordinating deployment Case to select the appropriate deployment and licensing workflow.','Confirmed'),
 (144,'MEDDPICC view','Provide a consolidated MEDDPICC view on the Opportunity.','Present existing MEDDPICC evidence and buying roles together; map Metrics and other gaps before adding duplicate storage.','Confirmed'),
 (145,'Partner transaction chains','Represent partner chains and NCP underlying customers.',PARTNERS,'Confirmed'),
 (146,'Field-history allocation','Apply the CB field-history decisions without deleting historical evidence.',HISTORY,'Confirmed'),
 (147,'Booking process reference','Add Booking an Order guidance to the website and enablement.','Publish the policy-based document paths, reconciliation checklist, approval responsibilities, cutoff, channel treatment and post-booking process as reference guidance. Only explicitly approved system changes become fields or stage gates.','Reference only'),
 (148,'Rollout preparation','Communicate the new requirements and backfill known data before enforcement.','RevOps populates reliable existing information, identifies remaining owner actions and communicates the changes to the field in advance. Do not fabricate missing evidence.','Process only'),
 (149,'Stage 8 removal proposal','Review Stage 8 removal and all dependent changes.',PENDING_STAGE8,'Pending'),
 (150,'Partner credit design','Finalize the detailed per-partner credit rules.',PENDING_PARTNER,'Pending'),
 (151,'Remaining implementation decisions','Resolve mappings and control ownership within the existing design.',PENDING_OTHER,'Pending'),
]

def revise(data):
    result=[data[0][:]]
    for original in data[1:]:
        row=original[:]; n=int(row[1][-3:])
        if n in REVISED:
            req,accept,notes,delta=REVISED[n]
            row[3],row[8],row[10]=req,accept,notes
        result.append(row)
    return result

def requirements(data):
    result=revise(data)
    for n,area,req,accept,status in NEW:
        result.append(['RevOps / Colin Brown',f'BR-SS-{n:03}',area,req,'October 19 consolidated review','','Pending decision' if status=='Pending' else 'Must Have','Relevant process owner',accept,'No live Salesforce configuration in this website release.','Pending proposals are not active stage gates.' if status=='Pending' else 'Reuse existing fields and mechanisms; implement only the gap.'])
    result[0] += ['Change type','Change date','Decision status','Net change']
    new={n:(req,status) for n,_,req,_,status in NEW}
    for row in result[1:]:
        n=int(row[1][-3:])
        if n in REVISED: row += ['Revised',DATE,'Confirmed',REVISED[n][3]]
        elif n in new: row += ['Added',DATE,new[n][1],new[n][0]]
        else: row += ['Existing','','Existing baseline','No October 19 scope change.']
    return result

def field(name,kind,inputs,purpose,previous='Existing capture / reuse to confirm',change='Revised · 19 Oct'):
    return '<tr data-field="'+E(name)+'"><td><strong>'+E(name)+'</strong><small>'+E(kind)+'</small></td><td>'+E(inputs)+'</td><td>'+E(previous)+'</td><td><span class="change-tag">'+E(change)+'</span></td><td>'+E(purpose)+'</td></tr>'

def update_field(page,name,kind,inputs,purpose,newname=None):
    pattern=r'<tr\b[^>]*data-field="'+re.escape(name)+r'"[^>]*>.*?</tr>'
    assert re.search(pattern,page,re.S), name
    return re.sub(pattern,lambda _:field(newname or name,kind,inputs,purpose),page,flags=re.S)

def append_to(page,id,body,tag='section'):
    start=page.index('id="'+id+'"'); end=page.index('</'+tag+'>',start)
    return page[:end]+body+page[end:]

def add_fields(page,id,rows):
    start=page.index('id="'+id+'"'); end=page.index('</tbody>',start)
    return page[:end]+''.join(rows)+page[end:]

def note(text): return '<p class="oct-note">'+E(text)+'</p>'

def block(id,title,text):
    return '<article class="ongoing-detail" id="'+id+'"><h3>'+E(title)+'</h3><p>'+E(text)+'</p></article>'

POLICY_ROWS = [
 ('What can be booked','An approved, binding customer purchase obligation with complete documents and approvals. Identify cancellation, reduction, return/refund rights, conditions precedent and acceptance terms; escalate their effect to the responsible Deal Desk, Legal and Finance owners. Undocumented side agreements are prohibited.'),
 ('Prepare the package','Sales supplies the approved final Primary Quote and the PO, fully executed contract or both as Opportunity Files. A contract can stand alone if a PO is not a condition. Reconcile customer legal entity, bill-to, ship-to/install details, products/SKUs, quantities, categories, prices, currency, payment terms, dates and applicable delivery/support terms across the package.'),
 ('PO formats','Itemized and category-subtotal POs must tie to the approved Primary Quote. A quote-referenced PO needs the quote reference and customer-returned quote PDF. A reference does not cure conflicting terms or incorrect details; obtain the required correction or written confirmation and any formal amendment.'),
 ('Approvals before submission','Complete applicable Deal Desk, Legal and Finance approvals before Won Decision submission. POC manager approval is not approval of customer acceptance language. Payment/prepayment terms must be agreed consistently; apply the separate Prepayment Policy. Complete applicable trade/partner compliance review.'),
 ('OM review and rejection','OM independently accepts, holds or rejects the package. Rejection returns Stage 6 to Stage 5 with notes to the Opportunity team and RevOps. Correct and resubmit the complete package; OM cannot waive another function’s approval.'),
 ('Booking value and currency','Finance determines eligible legally committed value; exclude uncommitted options, estimated consumption and other discretionary future purchases, and excluded taxes/freight/pass-through items under the policy. Committed multi-year amounts and phases qualify only to their binding extent. Quotes, bookings and invoices use USD; approved local-currency payment must satisfy the USD obligation and Deal Desk FX treatment.'),
 ('Channel orders','Assess the actual bill-to partner’s binding obligation and governing agreement, including return, stock rotation, price protection and cancellation rights. End-customer order/payment contingencies must be satisfied. Finance approval applies to qualifying unidentified-end-customer stocking and DDN-arranged/guaranteed financing. Follow supplemental Deal Desk channel requirements; otherwise obtain the specified agreement-rights confirmation.'),
 ('Support, subscriptions and acceptance','Shipment orders normally start support on shipment; software-only terms follow the approved quote and commitment. Renewals begin after the existing term; auto-renewals book only when the non-renewal window expires and the term is irrevocably committed. Nonstandard starts need Deal Desk approval. Acceptance-based starts require an approved event and contractual not-to-exceed date.'),
 ('Period-end cutoff','11:59 p.m. Pacific Time on the final calendar day of the reporting period; no grace period or backdating. The complete compliant package, required approvals and substantive conditions must be satisfied by cutoff. Later administrative OM processing does not change eligibility; later substantive completion or compliant resubmission belongs to the next open period. The 24-hour OM target is not a grace period.'),
 ('Booking Date versus Close Date','Official Booking Date and period attribution follow the complete compliant submission accepted by OM and Finance policy. Do not use the opportunity’s expected or locked Close Date as independent proof of eligibility. Booking is distinct from revenue recognition, billing and ARR.'),
 ('After booking','Commercial changes require appropriate customer documents, a revised Primary Quote and Deal Desk/other required approvals. OM determines correction, amendment, cancellation or de-book/rebook treatment. Preserve the original booking and audit trail; book only incremental eligible value, avoid double counting and record resulting value changes in the current open period unless Finance approves a correction.'),
 ('Exceptions and ownership','Each functional owner approves within delegated authority before booking; cross-functional exceptions need each owner. Definition, value and period exceptions require the specified senior Finance authority. Record approval, rationale and evidence in Salesforce. No exception permits an unenforceable commitment or backdating. A validation bypass is not a policy exception approval.'),
]
SCENARIOS = [
 ('Direct reseller · CDW / Aptiv','CDW is the bill-to reseller; Aptiv is the customer. Keep Direct source where DDN originated the deal. Do not add a distributor merely to fill a tier.'),
 ('Two-tier · Carahsoft / SHI or ABC / IMC','Identify Carahsoft as distributor/bill-to and the actual downstream reseller. Record the customer separately; source credit follows evidence, not the bill-to position.'),
 ('WWT UK / DSTL / NVIDIA','WWT is the transacting reseller, DSTL the customer and NVIDIA an additional contributor. Preserve Direct source where supported.'),
 ('OEM · SMC / NetZero; Lenovo / WWT / UCA','The OEM is DDN’s bill-to; retain the downstream reseller where present and the underlying customer. Do not replace the OEM bill-to with the end customer.'),
 ('SMC / HCL / STN / NVIDIA','Represent SMC as bill-to, HCL’s GSI/reseller role, STN as customer and NVIDIA’s participation independently.'),
 ('Bull / AQ Compute / NVIDIA','Capture Bull’s transacting and solution contribution, AQ Compute’s customer role and NVIDIA’s influence. A registration alone does not establish sourcing.'),
 ('Provider · Accenture / Perrigo / Cisco','Accenture can be the contracting buyer/provider, Perrigo the underlying customer and Cisco an influencer. Do not force the Opportunity Account to Perrigo.'),
 ('Multi-tenant NCP · TCS','TCS can be the buyer/provider serving multiple customers; associate known underlying customers without inventing tenants. Capture NVIDIA engagement separately when applicable.'),
 ('Hyperscaler · GCP / Jump Trading','GCP is the bill-to/hyperscaler and Jump Trading the underlying customer. Preserve the documented GCP motion; reconcile its Partner-only treatment in the pending credit design rather than forcing reseller logic.'),
]

def simple_table(headers,rows):
    return '<div class="field-register-wrap"><table class="field-register"><thead><tr>'+''.join('<th scope="col">'+E(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+E(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'

def policy_content():
    return '<p>Process reference based on DDN Global Bookings Policy v1 supplied for the October 19 review. This guidance does not turn every policy clause into a Salesforce field or stage gate. Finance owns policy interpretation; use the controlled policy and Bookings Procedure for execution.</p>'+simple_table(['Topic','Booking guidance'],POLICY_ROWS)+'<p>Related process references: Bookings Procedure, Prepayment Policy, Deal Desk Playbook, Revenue Recognition Policy and Sales Compensation Plan. Their controlled links and the final policy version/effective date should be supplied by their owners; the reviewed copy contains draft/version placeholders.</p>'

# Explicit replacements remove superseded wording rather than appending contradictions.
def normalize(text):
    replacements={
      'New Business, Existing Business and Renewal':'New Business and Existing Business (renewals excluded)',
      'if Yes, its status must be Completed or Cancelled':'if Yes, separate completion evidence must show Completed or Cancelled',
      'Identify the actual PO File using existing document-type metadata or an explicit PO File reference; Sales identifies it and OM verifies the content. A random attachment does not satisfy the PO requirement.':'Identify the governing PO/contract Files and matched approved final Primary Quote using existing document metadata or explicit links. Sales attaches the package and OM verifies it; an unrelated attachment does not satisfy customer commitment.',
      'Validate PO Secured AND a real attached PO; a checkbox alone cannot pass the gate.':'Validate binding customer commitment through a PO, qualifying executed contract or both, with matching Files and an approved final Primary Quote; a checkbox alone cannot pass the gate.',
      'the PO attachment is a required field above.':'the applicable customer commitment Files are required above.',
      'Existing relevance and status validation remains.':'Apply the Stage 2 engagement dropdown and conditional contact/GPU/project validation.',
      'Add NVIDIA through Associated accounts and maintain its account-specific plan and next steps there. Retain Nvidia Engagement and the specific NVIDIA engagement status in the Opportunity summary.':'Use the validated NVIDIA Engagement dropdown in the Opportunity summary alongside GPU Type, GPU Quantity and Project Type. Maintain NVIDIA account plans and next steps on its existing association.',
      'Track whether a POC is needed, its engagement type, status and concise updates.':'Track whether a POC is needed, its engagement type, manager approval, separate completion evidence and concise updates.',
      'Sales Engineering owns POC status and evaluation evidence.':'Sales Engineering maintains evaluation evidence; AE Manager and SE Manager approve the POC through the approval workflow.',
      'Yes with None, Planning, In Progress or Blocked cannot proceed.':'A required POC without Completed or Cancelled evidence cannot proceed.',

      'For New Business, Existing Business and Renewal, interview eligibility remains required':'For New Business and Existing Business, interview eligibility remains required',
      'New / Existing / Renewal':'New / Existing (renewals excluded)',
      'New/Existing/Renewal':'New/Existing (renewals excluded)',
      'Must be checked AND the actual PO attached before Stage 6. Equivalent-commitment wording in the baseline is superseded by the PO gate.':COMMITMENT,
      'Require a secured PO and the actual PO attachment before Stage 6.':COMMITMENT,
      'secured PO with the actual PO File':'binding PO/contract package matched to the approved final Primary Quote',
      'secured/attached PO':'binding PO/contract and approved final Primary Quote',
      'PO Secured and PO Attachment':'Customer Commitment Secured and Customer Commitment Files',
      'PO Secured':'Customer Commitment Secured',
      'PO Attachment':'Customer Commitment Files',
      'booked PO':'booked order',
      'Book the PO;':'Book the order;',
      'confirmed/booked PO':'confirmed/booked order',
      'secure the PO and final agreements':'secure the binding PO/contract and final agreements',
      'PO and final agreements':'PO/contract and final agreements',
      'Keep the existing choice list. Allow multiple selections on the opportunity.':'Allow initial manual multi-selection; derive Product Types from Opportunity Products when available. Update affected reports/integrations.',
      'Capture secondary contributions in Association Description / Plan; do not duplicate the Account–Opportunity association merely to add a role.':'Capture additional roles and contribution evidence in structured reportable form on the existing association; retain the plan and avoid duplicate account–opportunity records.',
      'not a universal stage gate':'required on entry to Stage 2',
      'Require a Yes/No decision before Stage 3.':'Require a Yes/No POC decision before Stage 3; manager approval and completion evidence are separate.',
    }
    for old,new in replacements.items():text=text.replace(old,new).replace(E(old),E(new))
    old=('An active Associated accounts record linked to the canonical NVIDIA Account makes NVIDIA relevant. On that association activation and on stage advancement, require the existing Opportunity Nvidia Engagement and its separately verified NVIDIA Engagement Status. After an association becomes inactive, preserve history and stop requiring new engagement input. Status choices and the Opportunity API mapping must be verified before enabling this rule; do not substitute the association Active/Inactive status.')
    text=text.replace(old,NVIDIA).replace(E(old),E(NVIDIA))
    return text

def system(page):
    page=normalize(page)
    # Remove the old removal-list occurrences; required rows are added in 3 and 4.
    for name in ['Technical Decision Maker','Decision Maker']:
        page=re.sub(r'<tr data-field="'+name+r'">.*?</tr>','',page,flags=re.S)
    # Replace current field definitions everywhere they appear in stage registers.
    specs=[
      ('NVIDIA Engagement','Existing picklist','Validated engagement values',NVIDIA,None),
      ('POC Status','Approval checkbox','Checked only after both managers approve',POC,'POC Approved'),
      ('Customer Commitment Secured','Existing PO control; adapt label/validation','PO, qualifying signed contract, or both',COMMITMENT,None),
      ('Customer Commitment Files','Salesforce Files','Sales uploads governing documents',COMMITMENT,None),
      ('Order Review Status','Status + sub-status','New Order / In Progress / Rejected / Booked',STATUS,None),
    ]
    for args in specs:page=update_field(page,*args)
    page=update_field(page,'NVIDIA Engagement Status','Legacy mapping to confirm','No additional approved gate','The October 19 requirement uses the validated NVIDIA Engagement dropdown. Do not create a second required status field. Confirm whether a separate legacy field exists and preserve its data; any separate validation requires an explicit mapping decision.')
    for name,kind in [('GPU Type','Existing picklist'),('GPU Quantity','Existing number'),('Project Type','Existing picklist')]:
        page=update_field(page,name,kind,'Required when NVIDIA engaged; otherwise available','Show in the Opportunity summary for every deal. Require when NVIDIA Engagement is anything other than Not Engaged, including later engagement changes; otherwise leave visible/editable and preserve the value.')
    page=update_field(page,'IPG Finalized','Existing disposition','Completed / Not Required',LOGISTICS)
    for name in ['Estimated Shipping Date','Requested Delivery Date']:
        page=update_field(page,name,'Existing/proposed date mapping','Stage 5 where physical shipment/delivery applies',LOGISTICS+' Reuse the existing date model and distinguish estimated/requested dates from actual events.')
    page=update_field(page,'Product Type','Multi-select; then product-derived','Existing choices; 1P Google → Managed Lustre','Allow initial manual multiple selections, then derive values from Opportunity Products when available. Preserve old selections/history through the Managed Lustre label change; update CPQ, reports and integrations without splitting the deal or double-counting its value.')
    old_applicability=('Applicability to confirm — OM and GSS must define the logistics dates, deployment-Case requirement and Stage 8 completion evidence for renewals, software/services, Internal Transfer, Non-Revenue and No Shipping required orders. The physical-delivery path applies where shipping/deployment is in scope. Do not invent delivery dates, create a dummy Case or treat shipment as receipt to satisfy it. Confirm the applicable alternative before enabling universal logistics/Case validation; no new exception status or field is approved here.')
    page=page.replace(old_applicability,'Software-only deals are exempt from hardware shipping/delivery requests and may use IPG Not Required. Confirm the appropriate Case/licensing/completion path for other non-shipping motions and remaining renewal, Internal Transfer and Non-Revenue cases. Do not invent physical delivery dates. Stage 8 removal remains pending.')
    # Reuse the live win/loss fields and choices; do not advertise duplicate development.
    for name in ['Won Reason','Loss Reason','OK to Interview (Win/Loss)?','Contact for Win/Loss Interview','WL Reason Cannot Approach']:
        pattern=r'<tr\b[^>]*data-field="'+re.escape(name)+r'"[^>]*>.*?</tr>'
        def deployed(match):
            row=match[0].replace('Proposed inputs','Live choices / approved mapping').replace('No existing field confirmed; proposed capture.','Existing Win/Loss rollout; reuse deployed field.')
            row=row.replace('New field</span>','Reuse deployed field</span>')
            row=row.replace('Reuse the corresponding Win/Loss rollout field if already deployed; confirm mapping before creating a field.','Reuse the deployed Win/Loss field; confirm the existing mapping and do not create a duplicate.')
            return row
        page=re.sub(pattern,deployed,page,flags=re.S)

    # Preserve the standalone historical status field only as historical context, not a new gate.
    page=page.replace('POC Status = Cancelled or Completed','separate POC completion evidence = Cancelled or Completed')
    page=page.replace('POC Status = Completed or Cancelled','separate POC completion evidence = Completed or Cancelled')
    page=page.replace('Add POC Status and POC Updates','Add POC Approved and retain POC Updates')
    for id,name in [('s3','Technical Decision Maker'),('s4','Decision Maker')]:
        page=add_fields(page,id,[field(name,'Existing mapping to confirm','Required in this stage','Record the appropriate decision authority. Reuse Contact Roles or existing fields after mapping; do not add duplicate storage.')])
    page=add_fields(page,'ongoing-nvidia-detail',[field('NVIDIA Contacts / Roles','Existing Opportunity Contact Roles preferred','Multiple contacts and NVIDIA-specific roles','Require when NVIDIA is engaged; support reporting across opportunities. Map Sales Representative, Technical Lead and Partner Lead into the existing role model before configuration.')])
    page=add_fields(page,'s2',[field('NVIDIA Engagement','Existing picklist','Required on entry to Stage 2',NVIDIA),field('POC Approved','Approval checkbox','AE Manager + SE Manager',POC)])
    for id in ['s4','s5']:
        page=add_fields(page,id,[field('Documentation / media fulfillment','Digital / Physical','Digital requires fulfillment email',MEDIA)])
    page=add_fields(page,'s5',[field('Final Primary Quote','Existing CPQ relationship','Approved final quote before exit',COMMITMENT)])
    page=add_fields(page,'s6',[field('OM Reviewer','User lookup restricted to OM','Required when In Progress','Only authorized OM edits review fields; reps can read the OM section.'),field('OM Rejection Notes','Text','Required on rejection',REJECTION),field('ERP Status','Read-only Oracle synchronization','In Progress / Booked / Invoiced / Sync Error','Display the Oracle-synchronized status; no manual edits.')])
    page=add_fields(page,'s7',[field('Support Start Date','Reuse suitable date field','Applicable support start','Carry the approved support-start and acceptance context to the deployment Case.'),field('Expected Revenue Recognition Date','Reuse suitable date field','Expected date; not actual recognition','Capture the expected date and carry relevant context; booking and recognition are distinct.')])
    page=add_fields(page,'s5',[field('Digital Fulfillment Email','Email; reuse suitable field','Required only when Digital','Prompt in Stage 4 and require before Stage 6 only for Digital documentation/media fulfillment.')])
    page=append_to(page,'ongoing-quoting-detail','<h4>Installation location on the final quote</h4>'+simple_table(['Field','Requirement'],[('Installation matches shipping','Capture on the quote; final quote requires an answer.'),('Installation Location','Required if different on a final quote. Budgetary quotes are exempt; reuse existing location fields.')]),'article')
    for id,extra in [('s1','On entry to Stage 2, require NVIDIA Engagement and conditional engaged details.'),('s2','Technical Decision Maker is required at Stage 3; POC manager approval is separate from completion.'),('s3','Decision Maker is required at Stage 4.'),('s4','Renewals can enter Procurement / Commit. Complete Digital/Physical fulfillment before leaving Stage 5.'),('s5','Require the approved final Primary Quote and applicable Digital email; apply the software-only logistics exemption.')]:
        start=page.index('id="'+id+'"');end=page.index('</section>',start)
        fragment=page[start:end]
        fragment=re.sub(r'(<div class="stage-gate">.*?<p>)(.*?)(</p>)',lambda m:m[1]+m[2]+' '+E(extra)+m[3],fragment,count=1,flags=re.S)
        page=page[:start]+fragment+page[end:]
    # Stage notices and gate summaries make timing visible, not buried in the log.
    for id,text in [('s1','On entry to Stage 2, require NVIDIA Engagement and the conditional engaged details.'),('s2',NVIDIA+' '+POC),('s3','Technical Decision Maker is required at Stage 3.'),('s4','Decision Maker is required at Stage 4. '+MEDIA),('s5',COMMITMENT+' '+LOGISTICS+' Renewals explicitly include Stage 5 Procurement / Commit before Won Decision.'),('s6',REJECTION+' '+STATUS),('s7',CLOSE_DATE+' '+DEPLOY),('s8',PENDING_STAGE8)]:page=append_to(page,id,note(text))
    for id,text in [('ongoing-nvidia-detail',NVIDIA+' Add engagement/contact/GPU reporting to leader click-through reports, forecast and pipeline views and the NVIDIA dashboard. Report pipeline, bookings and GPU demand by type, region, segment and sales team.'),('ongoing-poc-detail',POC),('ongoing-quoting-detail',COMMITMENT+' Final quotes capture whether installation location matches shipping; if different, require Installation Location. Budgetary quotes are exempt.'),('ongoing-primary-detail',TRANS),('ongoing-partners-detail',PARTNERS),('ongoing-contribution-detail',PENDING_PARTNER),('ongoing-logistics-detail',MEDIA+' '+LOGISTICS),('ongoing-ipg-detail',LOGISTICS),('ongoing-conversion-detail','Retire new Demand Gen opportunity intake. BDR, Marketing and partner teams use Stage 0. Migrate existing SAL records/process to Opportunity and coordinate cutover with MAP; retain history and the existing qualification paths.'),('ongoing-next-detail',CLOSE_DATE),('ongoing-buying-committee','Technical Decision Maker is required at Stage 3 and Decision Maker at Stage 4. Provide a consolidated Opportunity MEDDPICC view using existing evidence; contact/field and Metrics mappings remain pending.'),('case-current-state',DEPLOY)]:page=append_to(page,id,note(text),'article')
    page=append_to(page,'ongoing-partners-detail','<h4>Partner-flow examples</h4>'+simple_table(['Motion','How to represent the deal'],SCENARIOS),'article')
    page=append_to(page,'s7',note(PERMISSIONS))
    page=append_to(page,'s6',note('OM review fields are visible to reps and editable only by authorized OM. Require an OM-group reviewer when In Progress. Report Stage 6 → 7 against the 24-hour target using transition history; the policy cutoff remains separate.'))
    # Add the general knowledge and audit decisions before implementation.
    marker='<section class="stage" id="implementation-requirements">'
    sections='<section class="stage" id="booking-an-order"><header class="stagehead"><div><p class="label">Process reference · 19 October 2026</p><h2>Booking an Order</h2></div></header><div class="body">'+policy_content()+'</div></section>'
    sections+='<section class="stage" id="october-decisions"><header class="stagehead"><div><p class="label">Implementation preparation</p><h2>History, rollout and pending decisions</h2></div></header><div class="body"><h3>Field-history allocation</h3><p>'+E(HISTORY)+'</p><h3>Rollout</h3><p>Communicate the new requirements in advance. RevOps backfills trustworthy existing information, identifies owner actions and avoids fabricated evidence. Mark the deployed win/loss taxonomy as existing; provide fields and value crosswalks for historical mapping.</p><h3>Pending — not active stage changes</h3><ul>'+''.join('<li>'+E(x)+'</li>' for x in [PENDING_STAGE8,PENDING_PARTNER,PENDING_OTHER])+'</ul></div></section>'
    page=page.replace(marker,sections+marker,1)
    page=page.replace('<a href="#change-log">Change log</a>','<a href="#booking-an-order">Booking an Order</a><a href="#october-decisions">Pending decisions</a><a href="#change-log">Change log</a>',1)
    # One-slide summary: retain layout and link the new fields to their detail.
    row=re.search(r'<tr><th scope="row" class="slide-row-label">Fields<small>.*?</tr>',page,re.S)[0]
    cells=re.findall(r'<td class="slide-fields">.*?</td>',row,re.S)
    additions={3:[('NVIDIA Engagement · entry to 2','s2'),('GPU / project / NVIDIA contacts · if engaged','ongoing-nvidia-detail'),('POC approval + completion evidence','ongoing-poc-detail')],4:[('Technical Decision Maker','s3')],5:[('Decision Maker','s4'),('Digital / Physical fulfillment','s4')],6:[('Approved final Primary Quote','s5'),('Fulfillment email · if Digital','s5')],7:[('OM Reviewer · In Progress','s6'),('Rejection notes · if rejected','s6')]}
    for i,items in additions.items():
        cells[i]=cells[i].replace('</td>',''.join('<a class="october-slide-field" href="#'+anchor+'"><span class="field-existing">'+E(label)+'</span></a>' for label,anchor in items)+'</td>')
    revised=row
    for old,new in zip(re.findall(r'<td class="slide-fields">.*?</td>',row,re.S),cells):revised=revised.replace(old,new,1)
    page=page.replace(row,revised,1)
    page=page.replace('Finalize IPG, shipping / delivery timing, PO/contract and final agreements.', 'Complete the quote/commitment and applicable fulfillment. Renewals include Stage 5 / Commit.')
    page=page.replace('Opportunity summary: engagement + status when relevant.','Required at entry to 2; GPU/project/contact details if engaged.')
    return page

def release_log(data):
    rows=[r for r in data[1:] if r[12]==DATE]
    out='<details class="audit-group change-group release-group" id="changes-2026-10-19"><summary>'+TITLE+'<span>'+str(len(rows))+' added / revised requirements</span></summary><p>Compared with the pre-October 19 website scope. Existing BR IDs are retained; pending proposals are not approved gates. The implementation table and CSV carry the same date, change type, decision status and net-change description.</p>'
    out+='<div class="field-register-wrap"><table class="release-table"><thead><tr>'+''.join('<th scope="col">'+h+'</th>' for h in ['Requirement','Change','Decision','Net change'])+'</tr></thead><tbody>'
    for r in rows:
        out+='<tr class="'+row_class(r)+'" data-requirements="'+r[1]+'"><td><a href="#requirement-'+r[1]+'">'+r[1]+'</a> · '+E(r[2])+'</td><td>'+E(r[11])+'</td><td>'+E(r[13])+'</td><td>'+E(r[14])+'</td></tr>'
    return out+'</tbody></table></div></details>'

def row_class(row):
    return 'release-pending' if row[13]=='Pending' else ('release-'+row[11].lower())

def toolbar():
    return '<div class="release-tools"><p><strong>October 19 changes:</strong> <span class="release-key release-added">Added</span> <span class="release-key release-revised">Revised</span> <span class="release-key release-pending">Pending decision</span>. Unshaded rows are existing scope. Color is reinforced by the change/status columns.</p><label for="requirement-release-filter">Show requirements </label><select id="requirement-release-filter"><option value="all">All requirements</option><option value="latest">October 19 additions and revisions</option><option value="added">Added October 19</option><option value="revised">Revised October 19</option><option value="pending">Pending decisions</option></select><p id="requirement-release-count" role="status" aria-live="polite"></p><p><a href="downloads/october-19-requirements.csv" download="GTM-October-19-Requirements.csv">Download October 19 changes only (CSV)</a></p><p>CSV has no color formatting; both downloads include Change type, Change date, Decision status and Net change columns.</p></div>'

def assets(page):
    return page.replace('</head>','<link rel="stylesheet" href="assets/october.css"><script src="assets/october.js" defer></script></head>',1)


def learning(modules,design,definitions,examples,stages):
    """Update existing lessons and stage definitions, not a parallel course."""
    def walk(value):
        if isinstance(value,str): return normalize(value)
        if isinstance(value,list): return [walk(x) for x in value]
        if isinstance(value,tuple): return tuple(walk(x) for x in value)
        if isinstance(value,dict): return {k:walk(v) for k,v in value.items()}
        return value
    modules[:]=walk(modules)
    design.update(walk(design)); definitions.update(walk(definitions)); examples.update(walk(examples))
    by_id={m['id']:m for m in modules}
    def lesson(id,meaning,reminders,scenario,steps,weak,strong,question,answer,takeaway):
        m=by_id[id]
        m.update(definition=meaning,distinction=takeaway,reminder=reminders,scenario=scenario,steps=steps,weak=weak,strong=strong,questions=[question,'What evidence and owner are still needed?'],practice=scenario,check=question,answer=answer)
        design[id].update(goal=takeaway,practice=scenario,model=strong,question=question,answer=answer,takeaway=takeaway)
        definitions[id]=meaning; examples[id]=strong
    lesson('nvidia','NVIDIA Engagement is required on entry to Stage 2. Engaged selections require the people and GPU/project information; Not Engaged does not hide GPU data.',
      ['Select the validated engagement value by entry to Stage 2.','When engaged, capture multiple NVIDIA contacts/roles, GPU Type, GPU Quantity and Project Type.','Use the Opportunity summary; later engagement changes trigger the same dependent requirements.'],
      'A Stage 4 opportunity changes from Not Engaged to Technical Support. It already has GPU quantities but no NVIDIA contacts.',
      ['Choose engagement — Use the existing validated dropdown; no new Amy review is needed.','Complete engaged details — Add the NVIDIA contacts and roles, GPU Type, GPU Quantity and Project Type when engagement is selected.','Keep the summary useful — Leave GPU and project fields available for all deals, including Not Engaged; preserve existing values.','Inspect and report — Use leader pipeline/forecast views and the NVIDIA dashboard for engagement, contacts, GPU demand, pipeline and bookings.'],
      'NVIDIA helped; details will be added later.','Technical Support selected; NVIDIA technical and sales contacts linked with roles; GPU type, quantity and project type complete.',
      'Can the Stage 4 engagement change be saved without the NVIDIA contacts?','No. Selecting engagement later also requires the dependent information. Not Engaged deals may still record GPU/project data.','Keep engagement and GPU opportunity information complete and easy to inspect.')
    lesson('poc','POC Approved records dual-manager approval; separate completion evidence proves the evaluation is Completed or Cancelled.',
      ['Both AE Manager and SE Manager approve before the checkbox is checked.','Approval alone does not prove completion.','A required POC needs Completed or Cancelled evidence before progressing beyond Stage 2.'],
      'Both managers approve a POC, but the customer evaluation is still running.',
      ['Define the evaluation — Record POC Required?, engagement, success criteria and owner.','Request approval — Notify AE Manager and SE Manager; retain both decisions and approval times.','Record the outcome separately — Preserve completion/cancellation evidence and POC Updates; final storage mapping remains pending.','Apply the gate — A required unresolved evaluation cannot advance beyond Stage 2, even when approved.'],
      'Approved means done.','POC Approved is checked after both managers approve; evaluation remains open and blocks progression until Completed or Cancelled.',
      'Does POC Approved permit Stage 3 while testing continues?','No. Manager approval and evaluation completion are separate controls.','Use the approval checkbox without weakening the existing evaluation gate.')
    lesson('procurement','Procurement assembles the approved final Primary Quote and matching binding customer commitment before Won Decision.',
      ['A qualifying executed contract can satisfy commitment without a PO.','Sales attaches governing documents as Opportunity Files, matched to the final approved Primary Quote.','Renewals include Stage 5 Procurement and may remain in Commit.'],
      'A customer signs a binding contract matching the final approved Primary Quote. The contract does not require a PO.',
      ['Confirm the quote — Retain Stage 4 Primary Quote and require an approved final Primary Quote before leaving Stage 5.','Attach the commitment — Upload the PO, qualifying executed contract or both; identify the matching governing quote.','Complete applicable fulfillment — Record Digital/Physical and a Digital email, plus applicable IPG and delivery requests. Software-only is exempt from hardware logistics.','Submit or correct — Advance to Won Decision when complete. OM rejection returns to Procurement with notes for the Opportunity and RevOps teams.'],
      'The opportunity cannot advance until a PO exists.','The executed contract establishes the obligation without a PO condition; Sales uploads it and the matching approved final Primary Quote.',
      'Is a PO always required?','No. A qualifying executed contract can suffice if a PO is not a condition of the binding obligation; the approved final Primary Quote is still required.','Submit a complete matched commitment package, including the contract-only path.')
    lesson('booking','OM independently reviews the complete commitment package, accepts booking or returns a rejected submission from Stage 6 to Stage 5.',
      ['Review the matched approved quote and PO/contract package.','Reject with explanatory notes to the Opportunity team and RevOps.','OM owns Close Date confirmation; it locks at Closed Won and only a System Administrator can change it afterward.'],
      'OM finds the signed contract quantity differs from the approved Primary Quote near period end.',
      ['Review the package — Check the binding commitment, matching terms and applicable recorded approvals under Booking an Order guidance.','Accept or reject — OM accepts 6 → 7 only after reconciliation; reject 6 → 5 with notes, history and notifications.','Protect booking and hand off — Confirm OM reviewer, book, lock Close Date and start/link one coordinating Case for GSS.','Respect cutoff and later changes — Complete compliant submission must meet the policy cutoff; post-booking changes follow authorized treatment. The 24-hour target adds no grace period.'],
      'Mark Booked now and fix the documents later.','OM rejects to Stage 5, explains the quantity mismatch, notifies the Opportunity team and RevOps, then reviews the corrected complete resubmission.',
      'Does a rejected early submission preserve the closing period?','No. Period eligibility depends on the complete compliant resubmission, not the first attempt.','Keep booking review, correction and policy timing supported by evidence.')
    lesson('partner-accounts','The existing Associated accounts records show each participant’s commercial position, structured roles and contribution evidence on an opportunity.',
      ['Reuse the existing Opportunity association mechanism; preserve Account relationships.','Separate bill-to, downstream partner and underlying customer.','Make multiple contributions reportable without duplicating opportunity value.'],
      'Carahsoft transacts as distributor, SHI participates downstream, and a customer receives the solution with NVIDIA involvement.',
      ['Map the commercial chain — Identify DDN bill-to, downstream participants and the customer; do not invent a distributor where none exists.','Capture roles and evidence — Use one account–opportunity association with primary/additional reportable roles, contribution evidence, timing, contacts and plan.','Handle provider motions — For NCPs, distinguish the buyer/provider from known tenants; the Opportunity Account follows the actual motion.','Inspect without double counting — Report per-partner participation and deduplicate total pipeline/bookings. Apply approved credit rules while replacements remain pending.'],
      'Put the distributor in Primary Partner and give it all credit.','Carahsoft is bill-to, SHI has its evidenced downstream role, the customer is associated, and NVIDIA involvement is captured separately.',
      'Does the bill-to partner automatically get sourcing credit?','No. Transaction position, origin and contribution are distinct; source needs evidence.','Describe the whole partner flow on the existing records.')
    lesson('fulfillment','Transacting Partner identifies the expected DDN bill-to partner before the order exists and is reconciled with the final quote/order.',
      ['Use the existing Primary Partner field after its credit automation is replaced.','Represent the transacting partner in Associated accounts too.','Bill-to is distinct from ship-to, end customer and sourcing partner.'],
      'SMC buys from DDN for a solution ultimately used by NetZero.',
      ['Identify the bill-to — Capture the partner that is expected to buy from DDN.','Link its role — Ensure that account is associated with the opportunity and retains its transacting role.','Represent downstream parties — Keep NetZero and any downstream collaborators separately associated.','Reconcile at order — Match final quote/order bill-to; do not change source merely because the transacting partner changes.'],
      'Replace the transacting OEM with the ultimate customer.','SMC is the expected DDN bill-to; NetZero is the associated underlying customer.',
      'Should changing Transacting Partner change Opportunity Source?','No. Preserve origin and evidenced contribution independently.','Capture early commercial visibility without collapsing partner attribution.')
    # Explicitly replace instructional endorsement of unapproved draft algorithms.
    by_id['partner-credit']['reminder'][0]='Apply the existing approved contribution model until the replacement design is approved.'
    by_id['partner-credit']['reminder'][2]='Per-partner Sourced/Influenced/Fulfilled and timing rules are pending; booked-credit protection remains.'
    definitions['partner-credit'] += ' '+PENDING_PARTNER
    lesson('next-steps','Keep AE and SE next actions current and expected timing visible; OM owns Close Date confirmation and the booked date locks at Stage 7.',
      ['Continue the existing weekly AE and SE next-action reviews.','OM confirms Close Date at booking.','Only a System Administrator may change the locked Closed Won Close Date.'],
      'A delivery slips after booking and a seller proposes moving the booked Close Date.',
      ['Maintain open-deal actions — Record the next customer action and review expected timing through the existing forecast process.','Keep reviews distinct — AE and SE review their respective next actions; unrelated edits do not refresh the timestamps.','Confirm the booking date — OM confirms Close Date, which locks at Closed Won.','Record delivery changes correctly — Update authorized Order/Case logistics; do not move the locked date. Admin corrections retain audit evidence.'],
      'Move Close Date to the new delivery date.','Keep the booked Close Date locked and revise the delivery plan on the Order/Case.',
      'Can Sales Ops or OM edit Close Date after Closed Won?','Only a System Administrator can change it after the lock. OM owns its booking confirmation.','Keep forecast upkeep separate from protected booked dates.')
    # Extend existing lessons without duplicating their complete baseline content.
    additions={
      'buying-committee':'Require Technical Decision Maker at Stage 3 and Decision Maker at Stage 4. Reuse the confirmed Contact Role/field mapping. The Opportunity MEDDPICC view brings existing evidence together.',
      'quoting':COMMITMENT+' Final quotes require Installation Location if it differs from shipping; budgetary quotes are exempt.',
      'logistics':MEDIA+' '+LOGISTICS,
      'ipg':LOGISTICS,
      'deployment':DEPLOY,
      'forecast':'Renewals explicitly include Stage 5 Procurement / Commit between Stage 4 and Won Decision. Stage 8 removal is pending, so the current Stage 8 forecast mapping remains.',
      'sal-review':'Retire new Demand Gen intake; migrate its SAL process/history to the existing Stage 0 opportunity path with MAP cutover coordination.',
      'interviews':'Do not extend interview eligibility or dependent Contact/reason validation to renewals. The relevant Win/Loss fields and taxonomy are already live; reuse them.',
      'invoice':PENDING_STAGE8,
    }
    for id,extra in additions.items():
        by_id[id]['steps'][3]+=' '+extra
        design[id]['takeaway']+=' '+extra
        definitions[id]=by_id[id]['definition']+' '+extra
    # Remove contradictory wording from remaining legacy prompts.
    for m in modules:
        for k,v in list(m.items()):
            if isinstance(v,str):m[k]=v.replace('POC Status','separate POC completion evidence')
            elif isinstance(v,list):m[k]=[x.replace('POC Status','separate POC completion evidence') if isinstance(x,str) else x for x in v]
    for k,v in list(definitions.items()):definitions[k]=v.replace('POC Status','separate POC completion evidence')
    for i,stage in enumerate(stages):
        stage=list(walk(stage))
        if stage[0]=='s2':stage[6]+=' NVIDIA Engagement is required on entry; engaged details are conditional. POC approval and completion are separate.'
        if stage[0]=='s3':stage[6]+=' Technical Decision Maker is required at Stage 3.'
        if stage[0]=='s4':stage[6]+=' Decision Maker is required at Stage 4; prompt Digital/Physical fulfillment.'
        if stage[0]=='s5':stage[6]=COMMITMENT+' '+LOGISTICS;stage[7]+=' Renewals include this Procurement / Commit stage.'
        if stage[0]=='s6':stage[7]+=' '+REJECTION
        if stage[0]=='s7':stage[7]+=' '+CLOSE_DATE
        if stage[0]=='s8':stage[7]+=' Removal is pending Salesforce review; this stage remains until approved.'
        stages[i]=tuple(stage)
    definitions.update({
      'term-poc-status':'Legacy status capture is replaced in the presentation by POC Approved. Separate Completed/Cancelled evidence remains required for a required POC before progression beyond Stage 2; storage mapping is pending.',
      'term-po-secured-po-attachment':COMMITMENT,
      'term-nvidia-engagement-status':'Legacy mapping to confirm. The approved requirement uses NVIDIA Engagement; no separate required status field is added by the October 19 changes.',
      'term-ipg-finalized':LOGISTICS,
      'term-nvidia-engagement':NVIDIA,
      'term-transacting-partner':TRANS,
      'term-order-review-status':STATUS,
    })

EXTRA_DEFINITIONS=[
 ('POC Approved','poc',POC,None),
 ('Customer Commitment Document','procurement','A PO, fully executed contract or both establishing the binding purchase obligation. A qualifying contract needs no PO unless the contract makes one a condition. Match the document to the approved final Primary Quote.',None),
 ('OM rejection','booking',REJECTION,None),
 ('Renewal Procurement','forecast','Stage 5 Procurement is included in the renewal sales process, allowing Commit between Stage 4 and Stage 6 Won Decision.',None),
 ('MEDDPICC Opportunity view','buying-committee','A consolidated view of existing MEDDPICC fields and buying roles. Map Metrics and other gaps before creating additional storage.',None),
 ('Booking an Order','booking','Policy-based preparation, document matching, review, cutoff and post-booking guidance. General policy reference does not automatically create Salesforce fields or gates.',None),
 ('Per-partner contribution','partner-credit',PARTNERS+' '+PENDING_PARTNER,None),
]

def permissions_config(admin):
    admin.FIELDS.extend([
      ('Opportunity · stage movement','Existing Sales / SE progression; delegated operations',PERMISSIONS),
      ('Opportunity · Close Date','OM confirmation; System Administrator after lock',CLOSE_DATE),
      ('Opportunity · OM section','Authorized OM edits; reps read','Require an OM-group User reviewer in In Progress. Rejection notes are required and visible to the Opportunity team and RevOps; the OM rejection action returns 6 → 5.'),
      ('Opportunity · POC Approved','Approval workflow after AE Manager and SE Manager approve','Retain both approval actors/times. Sellers cannot self-check approval. Completion/cancellation evidence stays separate from approval.'),
      ('Opportunity · ERP Status / Invoice Reference','Designated Oracle integration','ERP Status is read-only for business users; synchronize invoice references without bypassing booked Close Date protection.'),
    ])
    admin.FIELDS=[(a,b,c.replace('Protect booked Close Date, Amount, Products and attribution.','Protect booked Amount, Products and attribution. Close Date uses the stricter System Administrator-only post-lock correction rule below.')) for a,b,c in admin.FIELDS]
    admin.RELATED=[(a,b.replace('PO, quote,','PO/contract, quote,'),c.replace('Confirm a real PO File is accessible to OM;','Sales attaches the governing PO/contract Files and matched approved Primary Quote; ensure OM can access the package;')) for a,b,c in admin.RELATED]
    admin.TESTS.extend([
      ('OM rejection / backward moves','OM can reject 6 → 5 only with notes and notifications to the Opportunity team and RevOps. Other backward moves from 6/7 require System Administrator or Sales Ops; normal permitted seller forward progression needs no Sales Ops handoff.'),
      ('Close Date lock','At Stage 7 only System Administrator can correct Close Date; OM, Sales Ops, sellers and ordinary integrations are denied. Regression must not bypass the lock; authorized invoice/delivery writes still work.'),
      ('POC approvals and NVIDIA changes','One manager approval cannot check POC Approved. Approved but incomplete required POC still blocks progression. Later engagement changes require NVIDIA contacts and GPU/project data; Not Engaged retains editable GPU fields.'),
      ('Contract-only package','A qualifying signed contract with a matching approved final Primary Quote can pass without a PO; a contract contingent on a PO cannot. Sales uploads Files and OM can inspect them.'),
    ])
