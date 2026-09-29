# GTM process audit · 29 September 2026

Completed a specification and local-site audit across opportunity creation, Stages 0–8, Closed lost, ongoing activities, definitions, all four enablement streams, the implementation table/CSV and the administrator access page. Corrected the issues below. No live Salesforce configuration was inspected or changed; platform guidance is a target design, not a certification of the current org.

## Corrections made

| Area | Finding and correction |
| --- | --- |
| Stage readability | Added a compact progression summary to creation and every numbered/lost stage. Renamed “Required fields” to “Fields and timing” so system-maintained fields are not mistaken for seller inputs. Long repeated rules remain available in expandable details. |
| SQL and skipped stages | Applied the confirmed decision: first qualified entry to Stages 1–8 records SQL, including valid skips. A valid 0 → 4 move records SQL, Pipeline Date/Entry Amount and Stage 4 Date; Stage 1–3 Dates remain blank. Completing qualification without leaving Stage 0 alone does not record SQL. Re-entry does not duplicate events. |
| Source attribution | Removed the unconditional Direct-source default to the record creator. Identify the verified originating seller; integration creators and later owners are not automatically the source. Corrected the overview’s Sourcing Partner label to match verified Partner origin. |
| Assignment | Replaced ambiguous Opportunity queue routing with a User-owned Opportunity and an operational review list or assigned Task. |
| Quoting | Removed stale Stage 2–5-only wording. Controlled Budgetary quotes are allowed in 0–1; regular quoting remains in 2–5, with existing technical and commercial gates. |
| Transacting partner | Separated the originating partner, commercial transacting account and actual ship-to destination in the process, requirements and course. A transacting account must not automatically become the shipping destination. |
| Guided stage changes | Clarified collection of missing evidence, final permission/gate checks, atomic dependent writes, fault rollback and post-commit notifications. Screen boundaries must not leave partially saved evidence or stage dates. |
| Contact linkage | Explained the parent/child save sequence for Opportunity and Contact Role creation. A before-insert requirement for an already-existing child role would make valid creation impossible. |
| Stage 6 deployment Case | Explained how the controlled transition provisions or reuses the coordinating Case, including appropriate automation context, relationship validation, rollback and retry protection. |
| Booking and delivery | Protected booked sales facts while permitting authorized 7 → 8 delivery progression and invoice/reference synchronization. Clarified Salesforce Stage types: 0–6 open, 7–8 closed/won, loss closed/lost. |
| Partner coverage | Explicitly require both the partner association and approved geography before derived team access. Added transfer/expiry reconciliation that preserves independently justified grants. |
| Meeting Tasks | Clarified native Activity/Task access, related records, ownership and hierarchy. Opportunity team membership alone does not grant editing of another user’s Task. |
| Admin handoff | Expanded coverage models, territory setup, object/field/action/system matrices, related-object dependencies and practical allow/deny checks. Distinguished job personas from hierarchy roles and permission sets from record coverage. |

## Stage and boundary review

| Scope | Confirmed behavior |
| --- | --- |
| Creation / Stage 0 | Source and originating Contact required; inbound review remains separate from SAL creation. Only the documented assigned seller-self-qualified path starts directly in Stage 1. Account Owner and Opportunity Owner remain separate. |
| Stage 1 | Inbound qualification applies at entry; all five CHAMPS answers and the documented discovery requirements apply before Stage 2. Early Budgetary quoting does not confer qualification or progression. |
| Stage 2 | Technical discovery and the POC decision/status gates remain intact. Completing a POC does not automatically establish Technical Win. |
| Stage 3 | Customer-supported Technical Win and one selected configuration are required for progression. Operational Value, Economic Buyer and Decision Process remain in this stage. |
| Stage 4 | Business Value, Paper Process, Primary Quote and Requested Install Date retain their timing. Current Amount changes do not rewrite the first pipeline-entry snapshot. |
| Stage 5 | Shipping/delivery requests, IPG, actual PO File, final agreement and handoff inputs remain required. The rejected optional/default-date proposal was not reintroduced. |
| Stage 6 | Customer selection remains open/Commit, not booked. Win/interview inputs and the coordinating Case are handled on entry; OM reconciliation precedes Stage 7. Correction to 5 revalidates without duplicate notices. |
| Stage 7 / 8 | Booking protects sales facts. Full on-site receipt drives Stage 8; partial delivery remains at 7. Invoice reconciliation continues on the Order; deployment/value work continues on the Case. The Invoice label is retained. |
| Closed lost | Preserved the three approved competitor exemptions and the narrower Stage 0 misqualification interview exemption. “Other” still requires competitor detail. Yes/No interview choices retain their dependent fields. Loss uses its own gates. |
| Ongoing work | Reviewed source/conversion, quoting, contact roles, partner attribution/coverage, next steps, logistics, risks, POCs, product requests, IPG, meetings, account context, win/loss reporting and post-sale Case work against the stages. |

## Administrator access design

The page covers nine personas and six coverage patterns: geography/segment, named/global accounts, opportunity/technical coverage, partner plus region, temporary/specialist cover, and operations/service coverage. It distinguishes Account ownership, Opportunity ownership, Account territory membership, the single Opportunity Territory, and Account/Opportunity Teams.

The implementation guidance explains that grants combine: partner sharing plus regional sharing would create a union, not the required intersection. Field permissions apply to a user across records, so a dual Sales/overlay user also needs record-specific authorization for commercial changes. Layouts and record types are not record security. Broad inherited access must be reconciled at its source; standard Restriction Rules do not solve Account/Contact/Opportunity scope.

Eight acceptance scenarios cover territory, partner intersection, hierarchy/overlap, dual roles, removal/expiry, protected fields/actions, Tasks/Cases/Files and UI/API/integration writes. These are administrator validation instructions, not claims that tests ran in the live org.

## Verification

- Build and automated checks passed for all four pages, 47 complete lessons and 215 definitions.
- Canonical requirements, the visible implementation table and CSV agree across 98 requirements. All are represented in the six collapsed change-log groups, with verified item counts and the requested five-column structure.
- Internal links, unique IDs, stage/activity coverage, role coverage and all protected/rejected fields passed checks. Removed access/reporting/migration implementation groups remain absent.
- Local browser checks covered stage navigation, definitions search/stage/alphabet filters and empty results, enablement filtering/reset, full-lesson expansion, knowledge answers, back-to-top and permissions coverage. The administrator page fits the inspected desktop width, with wide tables in scrollable regions.
- No live Salesforce access tests or mobile-device certification were performed.

## Remaining implementation mappings

These require the administrator and accountable business owner to confirm against the org before configuration; no additional policy is silently assumed.

- **RevOps / Salesforce admin:** actual field API names, existing lifecycle history and Contact-link storage, SAL choice/date meanings, automation inventory and supported relationship mappings.
- **Sales Ops / Partner Ops / leadership:** authoritative coverage roster, geography basis, named/global account exceptions, active dates, current territory feature/license availability and inherited grants.
- **OM / Finance / GSS:** writable Case/Order/invoice relationships, integration ownership and approved correction rights. Preserve the existing delivery-date requirements; confirm applicability within their current process rather than introducing a blanket optional/default rule.
- **Marketing / RevOps:** legacy source crosswalk, PAX qualification-channel mapping and the separately planned MAP migration.
- **Commercial/process owners:** existing approval matrix, Account Tier criteria and currency interpretation of report thresholds where not yet mapped.
- **Activity owner:** calendar synchronization remains outstanding. Synergy voice creation of follow-up Tasks remains documented; no meeting start/end fields were added.

## Primary platform references

The access guidance follows Salesforce’s [sharing architecture](https://architect.salesforce.com/docs/architect/fundamentals/guide/platform-sharing-architecture.html) and [object, field and record access model](https://help.salesforce.com/s/articleView?id=security_data_access.htm&language=en_US&type=5).

Territory configuration references Salesforce’s [Account assignment setup](https://help.salesforce.com/s/articleView?id=tm2_assign_accounts_to_territories.htm&language=en_US&type=5), [Opportunity assignment considerations](https://help.salesforce.com/s/articleView?id=sales.tm2_assign_territory_to_opportunity_considerations.htm&language=en_US&type=5) and [territory administrator permissions](https://help.salesforce.com/s/articleView?id=sf.tm2_how_access_permissions_work.htm&language=en_US&type=5).

Task guidance uses Salesforce’s [activity access rules](https://help.salesforce.com/s/articleView?id=sales.activities_view.htm&language=en_US&type=5). Restriction guidance uses the [supported-object list](https://help.salesforce.com/s/articleView?id=005167057&language=en_US&type=1). Stage-flow transaction guidance uses Salesforce’s [form-building decision guide](https://architect.salesforce.com/docs/architect/decision-guides/guide/build-forms).
