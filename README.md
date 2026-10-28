# GTM Process

Static GitHub Pages site with five connected pages:

- `index.html`: system specification, lifecycle overview and implementation change log.
- `definitions.html`: compact GTM definitions with text, stage and alphabet filters.
- `enablement.html`: Start the deal, Work the deal, Close the deal and Grow the deal; 47 lessons with reminders, scenarios, methods, practice and knowledge checks.
- `processes.html`: GTM operations working draft with lifecycle process groups, inspection/handoff procedures and an open-question register.
- `permissions.html`: nine business roles with Salesforce object, field/action and system permissions matrices.

## Edit and build

Run `python3 scripts/build.py`, then `python3 scripts/check.py`. Preview with `python3 -m http.server 8765`. No third-party packages or runtime framework are required. Commit generated HTML with its content sources.

`content/system-base.html` retains the pre-review system baseline. `content/process_updates.py` applies the September 29 approved changes, renders new activities and maintains the canonical requirements. `content/change_log.py` renders the six collapsed action groups using the same field tables as the stage sections; it reuses field definitions and links each row to its full requirement. `content/admin_views.py` renders the Salesforce administrator permissions reference. The build exports the same requirements to `downloads/implementation-requirements.csv`, also available through the restored Download requirements CSV button. The Implementation requirements menu item is last and opens the complete scrollable table in its own final card. Do not edit generated HTML directly.

`content/learning.py`, `course_design.py` and `reference.py` hold baseline learning material. `enablement_updates.py` applies approved content changes and assigns each lesson to exactly one of the four courses, with an overview, learning outcomes, a practical takeaway and application guidance for each stream. `industry.py` retains DDN/industry terminology with references in `terminology-sources.md`.

## Approved scope

Incorporated review items: 1–5, 7–11, 13–14, 23–24, 26, 29–34. Excluded: 6, 12, 15–22, 25, 27–28, 35–36. Additional user requests: access page and local permissions rules; change log; customer meeting Tasks and Synergy voice guidance; Account Tier and RevOps Notes; four enablement courses. Synergy UAT expansion is excluded; the explicit voice-Task guidance is included.

These are website/process-specification changes, not live Salesforce configuration. Task labels and Type/Status values were inspected read-only through Computer Use on September 29; no Task was saved. Disposition dependencies, API/storage mappings and record-type permissions require implementation verification. Calendar sync remains outstanding. Account-tier criteria, legacy source crosswalk and existing commercial authority mappings remain explicit dependencies.

## Validation

`check.py` verifies unique IDs and internal links, full lesson/stream coverage, the permission roles, CSV/table/canonical-data parity, complete change-log coverage, collapsed groups and item counts, source/quoting consistency, approval-number coverage and unchanged protected fields (including CHAMPS, Type, Business Value timing and win-recognition/incumbent inputs). Browser review covers course expansion, filtering, knowledge checks, deep links activity-grid collisions, the implementation menu/table/download, collapsed change-log groups, the permissions matrices and the new course overviews.

Search is a progressive enhancement; all content works as static HTML. Printing expands visible course/answer disclosures and restores their prior state. Back-to-top controls remain on all companion pages.

The Access and reporting and Migration and release implementation groups, including their seven requirement rows (BR-SS-027, 028, 124, 125, 127, 128, 129), were removed at user request. Their removal applies to the change log, requirements table and CSV; it does not remove existing process content or the permissions/enablement pages. Remaining BR IDs are stable.

Account-management additions are classified as New field. Meeting Tasks retain their existing fields, with explicit validation or mapping changes where specified. The proposed meeting start/end fields and BR-SS-117 were removed at user request; use Task Due Date and the calendar for scheduling.

## End-to-end audit · 29 September 2026

`content/sales_ops_updates.py` applies the later Sales Ops decisions: 1.1, 1.2, 1.3, 1.5 and 3 approved; 1.4, 2.1, 2.2, 4, 5 and 6 rejected. These numbers are separate from the earlier review above. `content/audit_updates.py` then corrects cross-page inconsistencies and clarifies platform mechanics without changing the protected business gates.

The confirmed SQL rule includes valid skips: record SQL on first qualified entry to Stages 1–8, at the same successful transition as Pipeline Date. Stage 0–6 Dates describe actual visits only. A valid 0 → 4 move therefore records SQL and Stage 4 Date while leaving Stage 1–3 Dates blank. Seller-self-qualified direct Stage 1 creation retains its documented qualification timing. No new SQL Date field is introduced.

The administrator page now covers geographic/segment, named/global, deal/technical, partner plus region, temporary and operational coverage; territory configuration; additive grants; dual-role controls; activity access; related objects; and allow/deny acceptance scenarios. Official Salesforce documentation supports platform mechanics. No live Salesforce configuration was inspected or changed during this audit.

See `audit-review.md` for findings, verification and the remaining implementation mappings.

`content/requirement_summaries.py` provides short, business-focused wording for Requirement statement, Acceptance criteria and Rev Ops refinement notes in the implementation table and CSV. The stage/activity specifications and detailed change log retain the full rules. Edit these summaries alongside substantive process changes.

## September 30 update

`content/deployment_updates.py` shortens only the one-slide field lists; the detailed field register retains those inputs. The coordinating deployment Case now starts on the authorized Stage 6 → 7 booking transition, covers Stages 7–8 and continues afterward. Stage 6 prepares the OM/GSS logistics handoff. The build applies this timing to the stage details, ongoing activity, definitions, enablement, change log and requirements export.


## October 21 consolidated review

`content/october_updates.py` and `content/october21_updates.py` apply the consolidated October requirements after the earlier approved updates. The original `content/system-base.html` remains the historical baseline. These changes specify target behavior; they do not configure Salesforce.

The release removes Stage 8 and consolidates its invoice, delivery and Case content into Stage 7. OM and GSS own Stages 6 and 7; OM alone controls stage changes out of either stage. Stage 7 can only be entered from Stage 6 after OM reconciliation and Booked review status. Win wire notifications and the deployment Case handoff occur on successful Stage 7 booking. Delivery, invoice issuance and value realization continue on the Order/Case without delaying booking or reopening the opportunity. Value tracking starts from verified actual customer receipt, not booking.

Close Date is Booking Date, set to OM acceptance at booking and editable only by OM from Stage 6 onward. Customer Commitment accepts actual PO, signed-contract or combined Opportunity Files with the approved final Primary Quote. Rejections notify the owner and Sales Ops; resubmissions reset New Order and notify the OM group/reviewer. The release expands review sub-statuses, installation/end-user contacts, hardware shipping and packaging requirements, and the Salesforce/Oracle support-date handoff. Existing hardware IPG exceptions are unchanged.

Booking policy guidance now lives inside **Confirm order** under Ongoing activities. The standalone History and rollout section is removed; approved field-history and preparation requirements remain in the implementation register. The one-slide, stage details, definitions, enablement and permissions reflect the same decisions.

The change log includes a collapsed **New requirements as of Wednesday, October 21st** group. This consolidates all October 19 additions and subsequent decisions against the pre-October 19 baseline; it is not a separate incremental release. Stable BR IDs are retained, including reserved withdrawn IDs 149 and 151. There are 118 requirements: 20 added, 31 revised and 67 unchanged. Added rows are green and revised rows blue, with explicit metadata and filtering.

Both `downloads/implementation-requirements.csv` and `downloads/october-21-requirements.csv` begin with **October 21 change** (`New`, `Revised`, `Unchanged`), **Net change**, **Change date**, and **Decision status**, followed by the original requirement columns. The previously shared October 19 download remains a byte-identical compatibility alias of the current changes-only export, and the old release anchor remains reachable within the consolidated group.

Run `python3 scripts/build.py` and `python3 scripts/check.py`. Checks cover table/CSV parity, release metadata, unchanged baseline guards, unique IDs and links, removed Stage 8, OM authority, commitment evidence, notification timing, hardware applicability and delivery-based value tracking. Browser review covers release filters, deep links, downloads, responsive layout and the updated slide. No policy source document is published.

## October 28 GTM operating playbook · working draft

`content/gtm_processes.py` supplies `processes.html`, the new **GTM Processes** global navigation item. It contains 34 process drafts across Start, Work, Close, Grow, Lost and shared GTM Operations, with 49 stable question IDs. Each process includes trigger, suggested operating lead, connected teams, approved foundation, input-quality checks, draft procedure, inspection timing, exception recovery, completion/handoff, suggested measures and source links. Process/question cross-links make handoffs traceable.

The approved October 21 stage specification and requirements exports retain their scope. The four existing pages only gain the global navigation item; their remaining content and requirement downloads are unchanged. New operating procedures and suggested owners are clearly working drafts. The page separately records the October 28 confirmed weekly CRO/sales-leader forecast calls, weekly leader/team reviews, fortnightly pipeline reviews at both levels, weekly partner reviews and weekly opportunity updates. Historical closed-record update scope is explicitly open rather than silently overriding booked protections. Pure renewal forecast separation is carried forward from the user's prior direction; renewal-plus-expansion allocation remains an operating question.

`assets/processes.js` supports search/group filtering, collapsed lifecycle/process disclosures, process/question deep links, copying all questions and print-state restoration. `assets/processes.css` adapts the existing site palette and enablement layout. Native details remain usable without JavaScript. Question answers are maintained through reviewed source edits in this conversation; the page does not imply local form entries are saved.

Run the normal build/check commands. Checks cover source anchors, process and question traceability, draft scope and navigation. Browser verification covers filtering, questions copied exactly once, hash navigation from filtered views, printing, mobile overflow and navigation from the sales-stage page.
