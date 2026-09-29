# GTM Process

Static GitHub Pages site with four connected pages:

- `index.html`: system specification, lifecycle overview and implementation change log.
- `definitions.html`: compact GTM definitions with text, stage and alphabet filters.
- `enablement.html`: Start the deal, Work the deal, Close the deal and Grow the deal; 47 lessons with reminders, scenarios, methods, practice and knowledge checks.
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
