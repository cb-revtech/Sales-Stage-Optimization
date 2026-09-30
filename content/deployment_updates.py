"""September 30 presentation edit and Stage 7 deployment Case decision."""
import html
import re


def replace_required(text, old, new):
    if old not in text:
        raise ValueError(f'Missing deployment wording: {old[:80]}')
    return text.replace(old, new)


def slide_fields(page):
    """Keep the field register intact; shorten only the one-slide field row."""
    row_pattern = r'(<tr><th scope="row" class="slide-row-label">Fields<small>.*?</tr>)'
    row = re.search(row_pattern, page, re.S)
    assert row, 'One-slide field row missing'
    cells = re.findall(r'<td class="slide-fields">.*?</td>', row[0], re.S)
    assert len(cells) == 11, 'Unexpected one-slide stage count'
    keep = [
        {'Opportunity Name', 'Type', 'Amount · Close Date', 'Opportunity Source', 'Opportunity Owner'},
        {'CHAMPS: Challenge, Authority, Money, Priority, Stack / Storage'},
        {'CHAMPS: Challenge, Authority, Money, Priority, Stack / Storage', 'Use Case', 'Additional Use Case Information', 'Route to Market', 'Opportunity Contact Roles (at least one)'},
        {'Identify Pain', 'Competitors', 'Technical Value', 'Champion', 'Decision Criteria', 'Description'},
        {'Technical Outcome', 'Technical Value', 'Operational Value', 'Economic Buyer', 'Decision Process'},
        {'Business Value', 'Primary Quote', 'Paper Process', 'Requested Install Date'},
        {'Estimated Shipping Date', 'Requested Delivery Date', 'IPG Finalized', 'PO Secured', 'PO Attachment', 'Final Agreements Received'},
        {'Order Review Status', 'Products · Amount', 'Won Reason', 'Business Value · win reason detail'},
        None, None, {'Closed Lost · Close Date', 'Loss Reason', 'Loss Reason Details', 'Lost — Next Step Recommendation'},
    ]
    item_pattern = r'(?:<a href="[^"]+">)?<span\b[^>]*>.*?</span>(?:</a>)?'
    for i in list(range(8)) + [10]:
        items = re.findall(item_pattern, cells[i], re.S)
        assert items and ''.join(items) == cells[i][len('<td class="slide-fields">'):-len('</td>')], i
        selected = []
        for item in items:
            label = html.unescape(re.sub(r'<[^>]+>', '', item))
            if label not in keep[i]:
                continue
            if i == 0 and label == 'Amount · Close Date':
                item = item.replace('Amount · Close Date', 'Amount')
            if i == 7 and label == 'Business Value · win reason detail':
                item = item.replace('Business Value · win reason detail', 'Win Reason Details')
                item = item.replace('class="field-existing"', 'class="field-existing" title="Captured in Business Value"', 1)
            selected.append(item)
        assert len(selected) == len(keep[i]), (i, len(selected), len(keep[i]))
        cells[i] = '<td class="slide-fields">' + ''.join(selected) + '</td>'
    updated = row[0]
    for original, reduced in zip(re.findall(r'<td class="slide-fields">.*?</td>', row[0], re.S), cells):
        updated = updated.replace(original, reduced, 1)
    return page.replace(row[0], updated, 1)


CASE_PLAN = ('Create or link the coordinating PS deployment Case on entry to Stage 7, using the existing Opportunity PS Case and Order Case(WO) relationships after confirming their targets. '
             'OM authorizes booking; the same controlled transition creates or links one Case. GSS owns the Case and records the deployment scope, workstreams, shipping, receiving and installation plan, dates, responsibilities and dependencies. '
             'Avoid duplicate Cases on retries or re-entry; associate later Orders with the same coordinating Case and retain subordinate workstream Cases where needed.')


def system(page, within):
    page = slide_fields(page)
    page = replace_required(page, '.ongoing-deployment{grid-column:8/span 3;', '.ongoing-deployment{grid-column:9/span 2;')
    page = replace_required(page, 'Deployment Case · Stages 6–8', 'Deployment Case · Stages 7–8')
    page = replace_required(page, 'Start at won decision; deployment + value continue on the Case after Stage 8.', 'Start at booking; deployment and value continue on the Case after Stage 8.')
    page = replace_required(page, 'Confirm the won decision; start the deployment Case and logistics plan.', 'Confirm the won decision and prepare the OM/GSS logistics handoff.')
    page = replace_required(page, 'Lock the booked PO; coordinate shipping, receiving and deployment.', 'Book the PO; start the deployment Case and coordinate delivery.')
    page = replace_required(page, '<span class="field-existing">GSS starts deployment Case</span>', '')
    page = replace_required(page, '<span class="field-existing">Maintain the linked Case plan</span>', '<span class="field-existing">Start and maintain the deployment Case</span>')
    page = replace_required(page, '<p class="label">Stages 6–8 · GSS + Order Management</p><h3>Deployment case</h3>', '<p class="label">Stages 7–8 · GSS + Order Management</p><h3>Deployment case</h3>')
    page = replace_required(page, 'Stage 6 · Case initiation, relationships and ownership', 'Stage 7 · Case initiation, relationships and ownership')
    page = replace_required(page, 'From Stage 6 · Deployment planning and execution', 'From Stage 7 · Deployment planning and execution')
    page = replace_required(page, 'Case planning · from Stage 6', 'Case planning · from Stage 7')
    page = replace_required(page, 'Begin planning from Stage 6 and continue after on-site delivery', 'Begin Case-based planning from Stage 7 and continue after on-site delivery')
    page = replace_required(page, 'Case creation date at Stage 6', 'Case creation date at Stage 7')
    page = replace_required(page, 'From Stage 6, maintain the detailed plan and responsibilities on the deployment Case', 'From Stage 7, maintain the detailed plan and responsibilities on the deployment Case')
    page = replace_required(page, '6 → 7 and initiate GSS deployment planning on the linked Case', '6 → 7 and initiate the linked deployment Case and GSS plan')
    page = replace_required(page, 'Initiate at Stage 6 · carry through Stage 8', 'Initiate at Stage 7 · carry through Stage 8')
    old_plan = ('Create or link the coordinating PS deployment Case at Won decision (6), using the existing Opportunity PS Case and Order Case(WO) relationships after confirming their targets. '
                'GSS starts deployment planning with Sales/SE and OM in Stage 6. Before booking at 7, identify the GSS case owner and document shipping, on-site receiving and installation/deployment plans, dates, responsibilities and dependencies on the Case and linked Order. '
                'Avoid duplicate cases on stage re-entry; associate later Orders with the same coordinating case and retain subordinate workstream cases where needed.')
    page = replace_required(page, old_plan, CASE_PLAN)
    # The field rows split their long purpose into a summary and disclosure,
    # so replace these clauses separately from the full narrative above.
    page = replace_required(page,
        'Create or link the coordinating PS deployment Case at Won decision (6), using the existing Opportunity PS Case and Order Case(WO) relationships after confirming their targets.',
        'Create or link one coordinating PS deployment Case on entry to Stage 7, using the existing Opportunity PS Case and Order Case(WO) relationships after confirming their targets.')
    page = replace_required(page,
        'GSS starts deployment planning with Sales/SE and OM in Stage 6. Before booking at 7, identify the GSS case owner and document shipping, on-site receiving and installation/deployment plans, dates, responsibilities and dependencies on the Case and linked Order.',
        'At Stage 7 booking, identify the GSS Case owner and document shipping, on-site receiving and installation/deployment plans, dates, responsibilities and dependencies on the Case and linked Order.')
    page = replace_required(page, 'Capture the won decision, reconcile the order and initiate the linked GSS deployment Case and logistics plan.', 'Capture the won decision, reconcile the order and prepare the GSS logistics handoff for booking.')
    def stage6(fragment):
        fragment = re.sub(r'<tr data-field="Deployment Case Link">.*?</tr>', '', fragment, flags=re.S)
        fragment = fragment.replace('<a href="#case-current-state">Deployment case</a>', '')
        fragment = fragment.replace('Entry requires Won Reason, Business Value win detail, incumbent capture and applicable recognition/interview inputs; initiate the coordinating deployment Case. ', 'Entry requires Won Reason, Business Value win detail, incumbent capture and applicable recognition/interview inputs. ')
        fragment = fragment.replace('<li>'+CASE_PLAN+'</li>', '')
        fragment = fragment.replace('GSS owns deployment Case work. Quote correction', 'GSS prepares the logistics handoff; Case work starts at Stage 7. Quote correction')
        return fragment
    page = within(page, 's6', stage6)
    return page


def requirements(data):
    rows = {int(row[1][-3:]): row for row in data[1:]}
    for row in (rows[n] for n in (13, 17, 18, 61, 69)):
        for i, value in enumerate(row):
            if 'deployment Case' in value or 'PS Case' in value or 'Case' in value and 'Stage 6' in value:
                value = value.replace('from Stage 6', 'from Stage 7')
                value = value.replace('at Stage 6', 'at Stage 7')
                value = value.replace('Stage 6 creates or links the Case', 'Stage 7 creates or links the Case')
                value = value.replace('at Won decision (6)', 'on entry to Closed won (7)')
                value = value.replace('at the won decision with one coordinating PS Case', 'at booking with one coordinating PS Case')
                value = value.replace('Start deployment planning at Stage 6', 'Start Case-based deployment planning at Stage 7')
                value = value.replace('OM/GSS planning is ready before booking', 'OM/GSS plan is handed to the Case at booking')
                row[i] = value
    rows[17][3] = 'Start one coordinating deployment Case when OM books the deal at Stage 7.'
    rows[17][8] = 'The 6 → 7 transition creates or links one Case after OM approval. Re-entry and retries reuse it; failed booking leaves no orphan Case.'
    rows[17][10] = 'Confirm the existing Opportunity and Order Case links and the process for deals without physical delivery.'
    rows[13][10] = rows[13][10].replace('Start deployment planning at Stage 6.', 'Prepare the OM/GSS logistics handoff in Stage 6; start the Case at Stage 7.')
    rows[61][8] = rows[61][8].replace('from Stage 6', 'from Stage 7')
    rows[69][8] = rows[69][8].replace('from Stage 6', 'from Stage 7')
    rows[69][2] = rows[69][2].replace('Stages 6–8', 'Stages 7–8')
    return data


def learning(modules, design, definitions, examples, stages):
    by_id = {m['id']: m for m in modules}
    won = by_id['won-decision']
    won['definition'] = 'Won decision records the customer’s win and prepares the reconciled order and GSS logistics handoff. Forecast remains Commit until OM books at Stage 7, when the deployment Case starts.'
    won['reminder'][2] = 'Prepare the OM/GSS handoff; the deployment Case starts at Stage 7 booking.'
    won['scenario'] = won['scenario'].replace('GSS begins deployment planning', 'GSS reviews the logistics handoff')
    won['steps'][3] = 'Prepare delivery handoff — Agree the logistics, receiving contacts and GSS ownership with OM. The coordinating Case is created or linked on entry to Stage 7.'
    design['won-decision']['model'] = design['won-decision']['model'].replace('and the coordinating deployment Case with GSS involvement', 'and the OM/GSS logistics handoff for Case creation at Stage 7')
    design['won-decision']['takeaway'] = design['won-decision']['takeaway'].replace('deployment handoff', 'Stage 7 deployment handoff')
    booking = by_id['booking']
    booking['steps'][2] = 'Confirm authority and handoff — OM controls entry to Stage 7 and confirms the GSS owner and delivery plan. The successful booking transition creates or links the coordinating deployment Case.'
    deployment = by_id['deployment']
    deployment['stages'] = ['s7', 's8', 'post', 'ongoing']
    deployment['definition'] = 'The coordinating deployment Case starts when OM books the deal at Stage 7. It holds the delivery plan, workstreams and responsibilities through Stage 8 and after the Opportunity ends.'
    deployment['reminder'][0] = 'Create or link one coordinating Case on entry to Stage 7.'
    deployment['reminder'][1] = 'At booking, confirm the GSS owner and shipping, receiving and installation plan.'
    deployment['steps'][0] = 'Initiate at booking — On the approved 6 → 7 transition, create or link one coordinating PS deployment Case and involve GSS. Reuse it on retries or re-entry.'
    deployment['steps'][1] = 'Establish ownership and scope — At Stage 7, identify the Case owner, in-scope workstreams, logistics dates, responsibilities and dependencies.'
    value = by_id['value-realization']
    value['stages'] = ['s7', 's8', 'post', 'ongoing']
    value['reminder'][0] = 'Plan on the Stage 7 Case using the agreed sales value case.'
    definitions['deployment'] = deployment['definition']
    definitions['term-deployment-case-link'] = 'The Opportunity link to the coordinating PS deployment Case started at Stage 7 booking; it remains available through Stage 8 and subsequent Case work.'
    definitions['term-value-realization-plan'] = 'The Case-based plan for validating the sales-defined operational and business outcomes, begun when the deployment Case starts at Stage 7.'
    examples['term-deployment-case-link'] = 'OM books the deal at Stage 7, and the same transition creates or links one coordinating Case for GSS.'
    for i, stage in enumerate(stages):
        if stage[0] == 's6':
            stage = list(stage)
            stage[6] = stage[6].replace('; coordinating deployment Case', '')
            stage[7] = stage[7].replace('identify the GSS owner and handoff plan before booking', 'prepare the GSS owner and logistics handoff before booking')
            stage[8] = [x for x in stage[8] if x != 'deployment']
            stages[i] = tuple(stage)
        elif stage[0] == 's7':
            stage = list(stage)
            stage[6] = stage[6].replace('linked Order/Case delivery plan', 'linked Order and newly started deployment Case plan')
            stages[i] = tuple(stage)
