"""Approved Sales Ops decisions; decimal IDs are separate from the earlier review."""
import html, re
APPROVED = {'1.1', '1.2', '1.3', '1.5', '3'}
REJECTED = {'1.4', '2.1', '2.2', '4', '5', '6'}
PIPELINE = ('Exclude Stage 0 from qualified pipeline totals and pipeline-generation credit. Pipeline Date records the first valid entry into any numbered Stage 1–8, including allowed seller-qualified creation directly in Stage 1. Capture Pipeline Entry Amount and currency context on that same event. Stamp once; preserve the timestamp and entry amount on regression, re-entry, retries and later Amount/quote changes. A permitted 0 → 4 move stamps Pipeline Date equal to Stage 4 Date; skipped Stage 1 Date remains blank. Closed lost and administrative statuses do not trigger pipeline entry. Reuse the previously proposed first-entry snapshot design; do not create a second credit mechanism. Current Amount and Created Date remain separate. Deduplicate by Opportunity ID and event. Existing creation paths, all crossed gates and booked-record locks still apply. Backfill only from trustworthy history; never substitute current Amount for missing historical entry value.')
STAGE_DATES = ('Provide Stage 0 Date through Stage 6 Date as system-maintained Date/Time fields for first actual entry to each stage. Stamp the applicable field once on a successful transition or permitted creation directly in that stage. Leave never-visited stages blank, including stages crossed by a skip; do not reset on regression or re-entry. Use the same event timestamp for the destination Stage Date and Pipeline Date when both first qualify. Retain transition history for time spent across repeated visits; first-entry differences alone are not total stage duration. Backfill only from trustworthy history and reuse a verified equivalent field instead of duplicating storage. Business users cannot edit these values; failed or cancelled transitions stamp nothing.')
FLOW = ('Provide an Update Stage screen flow that prepopulates existing evidence and presents the missing required inputs for the requested destination and every prerequisite gate crossed. Identify each missing field, its requirement and where to complete it. Respect field permissions; for technical evidence, related-record work or approval outside the user’s authority, identify the responsible owner and next action. Validate all evidence before committing the stage and associated evidence together; a failed save or cancellation must not advance the stage or stamp entry dates. Keep equivalent gates on direct edits, imports, integrations and automation. Fallback errors must name the missing inputs and provide navigation where the interface supports it. Preserve valid existing values, source-specific qualification, loss-specific rules, the Stage 6 → 5 correction path and booked locks.')
AE_LOG = ('Keep the existing AE Next Steps history read-only to business users. Authorized users edit Next Step; the existing logging automation appends dated entries when that value changes. Preserve prior log entries and the automation’s write access; unrelated edits and unchanged-value saves create no false change entries. Verify the existing logger and field mapping before changing access; do not create a second log. Weekly AE/SE review actions and their Reviewed At timestamps remain separate and unchanged.')
COMPETITOR = ('Competitor Lost To is optional when Loss Reason is Opportunity Misqualified, Project Cancelled / Budget Lost or No Decision / Went Dark; it remains required for other loss reasons. Preserve any supplied competitor values and do not infer a winner or default Not lost to competitor. Competitor Detail (if Other) is required only when Other is explicitly selected in Competitors or Competitor Lost To; retain that rule even for an exempt loss reason.')
INTERVIEW = ('For New Business, Existing Business and Renewal, interview eligibility remains required at won decision and loss, except Opportunity Misqualified from prior Stage 0, where it is optional. Cancelled/budget-lost and went-dark losses still require eligibility. If eligibility is blank under the Stage 0 exemption, neither interview Contact nor cannot-approach reason is required. If Yes is supplied, require Contact; if No is supplied, require WL Reason Cannot Approach. Preserve existing values and never validate the inactive branch.')
LOSS = ('Require Loss Reason, Loss Reason Details and Lost — Next Step Recommendation. Opportunity Misqualified is allowed only from prior Stage 0. ' + COMPETITOR + ' ' + INTERVIEW)
OLD_LOSS = 'Require Loss Reason, Loss Reason Details, Competitor Lost To and Lost — Next Step Recommendation. Allow Not lost to competitor; require Competitor Detail (if Other) when either competitor field uses Other. Opportunity Misqualified is allowed only when the prior stage was 0. Capture interview eligibility and its conditional contact/reason.'
OLD_COMPETITOR = 'Required at loss; align vendor choices with Competitors and add Not lost to competitor. Keep the membership validation against Competitors switched off at launch per the guide.'
OLD_INTERVIEW = 'Required at won decision / loss for New Business, Existing Business and Renewal. Can the team approach a customer contact for feedback?'

def field_update(s, name, purpose, change=None):
    def update(m):
        cells = re.findall(r'<td[^>]*>.*?</td>', m[0], re.S)
        assert len(cells) == 5, name
        if change:
            cells[3] = '<td><span class="change-tag">' + html.escape(change) + '</span></td>'
        cells[4] = '<td>' + html.escape(purpose) + '</td>'
        return '<tr data-field="' + html.escape(name, quote=True) + '">' + ''.join(cells) + '</tr>'
    return re.sub(r'<tr data-field="' + re.escape(name) + r'">.*?</tr>', update, s, flags=re.S)

def system(s, within, auto, activity_register):
    for old, new in [(OLD_LOSS, LOSS), (OLD_COMPETITOR, COMPETITOR + ' Align choices with Competitors; retain Not lost to competitor and keep membership validation off at launch.'), (OLD_INTERVIEW, INTERVIEW)]:
        # Visible markup and canonical JSON have different escaping.
        for a, b in [(html.escape(old), html.escape(new)), (old, new)]:
            s = s.replace(a, b)
    s = field_update(s, 'AE Next Steps', AE_LOG, 'Read-only history')
    # Show the history beside the current action, as well as in the full inventory.
    log_row = re.search(r'<tr data-field="AE Next Steps">.*?</tr>', s, re.S)[0]
    s = within(s, 'ongoing-next-detail', lambda x: x.replace('</tbody>', log_row + '</tbody>', 1), 'article')
    s = auto(s, 'ongoing-next-detail', AE_LOG, 'article')
    for n in range(7):
        name = f'Stage {n} Date'
        rows = activity_register([(name, name, 'Opportunity · Date/Time', 'System-maintained; blank until first actual entry.', 'No complete first-entry date set specified.', 'New field', f'Stamp once on first actual entry to Stage {n}, including permitted creation in that stage. Skipped stages stay blank; regression and re-entry do not reset it. Backfill only from trustworthy history. Use transition history for repeat-visit duration.')])
        row = re.search(r'<tbody>(.*?)</tbody>', rows, re.S)[1]
        s = within(s, f's{n}', lambda x: x.replace('</tbody>', row + '</tbody>', 1))
        s = auto(s, f's{n}', f'On successful first entry, stamp {name}; on first entry to Stages 1–8 also stamp Pipeline Date and Pipeline Entry Amount once. Use Update Stage to complete missing evidence before progressing. Skipped stages stay blank; re-entry never resets first-entry values.')
    for n in [7, 8]:
        s = auto(s, f's{n}', 'On first valid pipeline entry, stamp Pipeline Date and Pipeline Entry Amount once. Preserve prior snapshots and enforce all prerequisite gates and existing booking/delivery authority.')
    flow = '<article id="stage-update-flow"><h3>Update Stage</h3><p>' + html.escape(FLOW) + '</p></article>'
    s = within(s, 'creation', lambda x: x.replace('<div class="body">', '<div class="body">' + flow, 1))
    s = auto(s, 'ongoing-conversion-detail', STAGE_DATES, 'article')
    # Keep the compact stage overview consistent with the detailed registers.
    overview, rest = s.split('<main', 1)
    cell_number = -1
    def overview_cell(match):
        nonlocal cell_number
        cell_number += 1
        cell = match[0]
        if 1 <= cell_number <= 7:
            n = cell_number - 1
            cell = cell.replace('</td>', f'<span class="field-new" title="System-stamped on first actual entry; skipped stages stay blank.">Stage {n} Date</span></td>')
        if cell_number == 2:
            cell = cell.replace('</td>', '<span class="field-new" title="First valid entry to any numbered Stage 1–8; capture once, including allowed stage skips.">Pipeline Date · Entry Amount</span></td>')
        if 'Closed Lost · Close Date' in cell:
            cell = cell.replace('>Competitor Lost To</span>', '>Competitor Lost To · conditional</span>')
            cell = cell.replace('Interview eligibility + conditional Contact / reason', 'Interview eligibility · Stage 0 exemption')
        return cell
    overview = re.sub(r'<td class="slide-fields">.*?</td>', overview_cell, overview, flags=re.S)
    s = overview + '<main' + rest
    return s

def requirements(data):
    by_id = {int(r[1].split('-')[-1]): r for r in data[1:]}
    by_id[25][3] = 'Update loss-entry validation with noncompetitive-outcome exceptions. ' + LOSS + ' Retain existing loss-review thresholds, notifications, Close Date and booked-result controls.'
    by_id[25][8] += ' Test each exempt reason with blank competitor fields, a deliberately selected Other with missing detail, Stage 0 misqualification with blank eligibility, and Yes/No with its missing dependent input. Non-exempt losses still require a competitive outcome; cancelled/budget-lost and went-dark losses still require eligibility.'
    by_id[34][3] = 'Apply conditional interview capture using the existing rollout fields. ' + INTERVIEW
    by_id[34][8] = INTERVIEW
    by_id[86][8] += ' Test Stage 0 misqualification with blank eligibility; test all other applicable won/lost cases with eligibility required.'
    by_id[97][8] += ' Test all three exempt reasons with blank competition, a non-exempt reason with blank competition, and Other requiring detail even for exempt reasons.'
    by_id[116][2] = 'New fields / Pipeline entry snapshot'
    by_id[116][3] = 'Use Pipeline Date and Pipeline Entry Amount for the single first-qualified-entry snapshot, evolving the earlier proposed First Stage 1 At / Amount design. ' + PIPELINE
    by_id[116][8] = 'Allowed direct Stage 1 creation stamps Pipeline Date equal to Stage 1 Date. A valid 0 → 4 move stamps Pipeline Date equal to Stage 4 Date, leaves never-visited Stage 1–3 dates blank, and captures entry Amount/currency once. Regression, re-entry and later quotes preserve credit. Loss, failed transitions and retries create no new credit. No new creation path or bypass is introduced.'
    by_id[116][10] = 'Approved original item 24, refined by Sales Ops 1.3. One pipeline snapshot mechanism; separate actual-stage dates under BR-SS-131. Verify field mapping and trustworthy historical evidence before configuration.'
    new = [
        (130, 'Automations / Guided stage progression', FLOW, 'An incomplete deal displays missing evidence in the flow; existing values are retained. Unauthorized technical/approval inputs show the responsible owner. A valid save commits evidence and stage; failed/cancelled saves stamp no dates and do not advance. Direct edits, imports and integrations enforce the same gates, including skips.', '1.1'),
        (131, 'New fields / Stage entry dates', STAGE_DATES, 'Creation in Stage 0 stamps only Stage 0 Date. Allowed direct Stage 1 creation stamps Stage 1 Date and Pipeline Date together. A valid 0 → 4 skip stamps Stage 4 Date, leaves Stage 1–3 blank, and does not reset Stage 0. Regression/re-entry preserve first dates; cancelled/failed moves stamp nothing. Preserve transition history for revisits.', '1.2'),
        (132, 'Automations / AE Next Steps history', AE_LOG, 'A seller can change Next Step but cannot directly rewrite AE Next Steps through UI, imports or API. The designated logger appends dated history and retains prior entries. Unrelated edits and unchanged-value saves add no false entries. Existing weekly review behavior remains intact.', '1.5'),
    ]
    for number, title, req, acceptance, decision in new:
        data.append(['RevOps / Colin Brown', f'BR-SS-{number:03}', title, req, 'Approved Sales Ops feedback · 29 September 2026', '', 'Must Have', 'Salesforce Admin / process owner', acceptance, '', 'Approved Sales Ops item ' + decision + '. Specification only; verify existing configuration and implement only the gap.'])
    for n in [25, 34, 86, 97]:
        by_id[n][10] += ' Sales Ops item 3 approved: optional competition for the three named reasons; optional interview eligibility only for Stage 0 misqualification; Other detail remains conditional.'
    return data

def learning(modules, design, definitions, examples):
    m = {x['id']: x for x in modules}
    m['conversion']['reminder'][2] = 'Pipeline Date and entry Amount stamp once at first valid entry to Stages 1–8. Stage Dates record actual visits only.'
    m['conversion']['steps'][3] = 'Protect reporting — Keep each opportunity episode and originating Contact. Pipeline Date and Pipeline Entry Amount capture first valid entry to Stages 1–8, including allowed direct Stage 1 creation. Stage 0–6 Dates stamp only actual visits; skipped stages stay blank and re-entry never resets first dates. Use transition history for time across revisits. Do not fabricate MQL, AQL or SQL events for skipped stages or downgrade an existing customer lifecycle.'
    design['conversion'].update(practice='An opportunity moves from Stage 0 directly to Stage 4 after all crossed gates pass. Which dates and amount should the system capture?', model='Stamp Stage 4 Date and Pipeline Date with the same event time, plus Pipeline Entry Amount and currency. Keep Stage 0 Date, leave never-visited Stage 1–3 Dates blank, and do not fabricate a Stage 1 visit or SQL event. Regression or later pricing changes do not reset the pipeline snapshot.', question='A deal re-enters Stage 2 after a regression. Should Stage 2 Date or Pipeline Date reset?', answer='No. Both are first-entry values. Retain individual transitions to calculate time across repeated visits; current Amount can change without rewriting Pipeline Entry Amount.')
    m['forecast']['steps'][3] = m['forecast']['steps'][3].replace('First Stage 1 Amount', 'Pipeline Entry Amount')
    m['sal-review']['steps'][2] += ' When requesting the next stage, the proposed Update Stage flow presents missing evidence and retains existing values. Complete what you are authorized to supply; ask the named owner for protected technical or approval evidence. The stage advances only when all gates pass.'
    design['sal-review']['answer'] += ' Use Update Stage to supply the missing evidence; cancelling or failing validation leaves the stage and entry dates unchanged.'
    m['next-steps']['reminder'][0] = 'Edit Next Step with a dated customer action; AE Next Steps is the read-only history.'
    m['next-steps']['steps'][0] += ' Edit Next Step, not AE Next Steps. Existing automation appends dated changes to that read-only log; preserve its history.'
    design['next-steps']['takeaway'] += ' Edit the current Next Step; let automation maintain AE Next Steps history.'
    m['loss']['reminder'][1] = 'Reason, details and next-step recommendation are required; competitor capture has three named exemptions.'
    m['loss']['steps'][1] = 'Record a specific explanation — Complete Loss Reason, Loss Reason Details and Lost — Next Step Recommendation. Competitor Lost To is optional for Opportunity Misqualified, Project Cancelled / Budget Lost and No Decision / Went Dark. Other reasons still require it. Never guess a winner; if Other is selected in either competitor field, name it in Competitor Detail. Opportunity Misqualified remains limited to prior Stage 0.'
    m['loss']['steps'][2] = 'Capture feedback access — For New Business, Existing Business and Renewal, capture interview eligibility except for Stage 0 Opportunity Misqualified, where it is optional. Cancelled/budget-lost and went-dark losses still require it. Blank eligibility under the exemption requires no dependent input; Yes requires Contact and No requires the cannot-approach reason. Preserve existing values.'
    m['loss']['scenario'] = 'A customer cancels a project after funding is withdrawn. The AE records Project Cancelled / Budget Lost, explains the decision and recommends a funding check next quarter. Competitor Lost To is left blank because no vendor selection was established. The AE still completes interview eligibility and the applicable Contact or cannot-approach reason.'
    design['loss']['model'] += ' Competitor Lost To can remain blank for Project Cancelled / Budget Lost. Interview eligibility still needs a Yes or No and its applicable dependent field.'
    design['loss']['takeaway'] = 'Record the supported reason, learning and next action. Check competitor and interview applicability separately; selecting Other still requires its name.'
    m['interviews']['reminder'][0] = 'New / Existing / Renewal: eligibility is required at win or loss, except Stage 0 Opportunity Misqualified.'
    m['interviews']['steps'][0] = 'Confirm applicability — Capture eligibility at Won decision or Closed lost for New Business, Existing Business and Renewal. Only Opportunity Misqualified from Stage 0 makes it optional; cancelled/budget-lost and went-dark losses still require it.'
    m['interviews']['steps'][2] += ' If eligibility is left blank under the Stage 0 misqualification exemption, neither dependent field is required.'
    design['interviews'].update(practice='Compare a Stage 0 Opportunity Misqualified loss with a Stage 3 Project Cancelled / Budget Lost loss. What interview information is required?', model='Stage 0 misqualification may leave eligibility and both dependent fields blank. The cancelled-project loss still needs Yes with a Salesforce Contact, or No with WL Reason Cannot Approach. If eligibility is supplied voluntarily on the exempt loss, its Yes/No branch applies.', question='Can No Decision / Went Dark omit interview eligibility because it can omit Competitor Lost To?', answer='No. The competitor exemption and interview exemption differ. Went-dark losses still need eligibility for applicable business types; only Stage 0 Opportunity Misqualified makes it optional.')
    m['competition']['steps'][3] += ' Competitor Lost To can be blank for misqualification, cancelled/budget-lost or went-dark losses; Other still requires detail and unknown outcomes must not default to Not lost to competitor.'
    m['competition']['answer'] = 'No. Use Not lost to competitor only when supported by the actual outcome. The three exempt loss reasons can leave Competitor Lost To blank; do not guess.'
    design['competition']['model'] += ' For Project Cancelled / Budget Lost, Competitor Lost To may also remain blank; do not auto-populate an outcome without evidence.'
    definitions['term-competitor-lost-to'] = 'The competitive outcome at loss. Optional for Opportunity Misqualified, Project Cancelled / Budget Lost and No Decision / Went Dark; required for other reasons. Record only a supported outcome.'
    definitions['term-ok-to-interview-win-loss'] = 'Whether the Win/Loss team may approach a customer Contact. Required for applicable New / Existing / Renewal outcomes, except Stage 0 Opportunity Misqualified. Yes needs a Contact; No needs a cannot-approach reason.'
    examples['term-competitor-lost-to'] = 'The project is cancelled without a confirmed vendor selection. Competitor Lost To can remain blank; the loss reason and explanation are still recorded.'
