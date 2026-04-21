-- =============================================================================
-- SJ PROJECT PLANNER AGENT — SEED: plan_updates_draft
-- File: seed_plan_updates_draft.sql
-- Version: 1.0
-- Description: Inserts 25 representative draft rows into plan_updates_draft,
--              simulating what the Extraction + Delta Agent pipeline would
--              produce from the 50 source documents.
--
--              Coverage:
--                • All delta_type values : Update (15), New Task (6), Conflict (4)
--                • All approval states   : Pending Review (15), Approved (5),
--                                          Rejected (2), Escalated (3)
--                • Confidence range      : 0.40 – 1.00
--                • All changed_fields    : status, end_date, start_date, owner
--                • All technical_entity  : ETFE Cushion System, Edge Computing Nodes,
--                                          GSIMS Platform, Digital Twin Sync,
--                                          URLLC, Vibration Isolation Springs
--
-- Prerequisites (run first):
--   1. sj_planner_schema.sql       — creates tables, enums, indexes
--   2. seed_unstructured_sources.sql — populates unstructured_sources (source_id FKs)
--   3. The baseline_tasks SEED block inside sj_planner_schema.sql must have run
--      so that baseline_task_id FKs resolve correctly.
--
-- Usage:
--   psql -h <server>.postgres.database.azure.com \
--        -U <admin> -d sj_nexus \
--        -f seed_plan_updates_draft.sql
--
-- Notes:
--   • source_id values are resolved via sub-SELECT on file_name so this file
--     stays portable — no hard-coded serial IDs.
--   • baseline_task_id is NULL for New Task rows (task not yet in WBS).
--   • ON CONFLICT DO NOTHING is not applicable here (no UNIQUE constraint on
--     plan_updates_draft), so the file is intentionally not idempotent.
--     Drop and re-seed if you need a clean state.
-- =============================================================================


-- ---------------------------------------------------------------------------
-- SECTION 1 — STATUS CHANGES  (Blocked / On Track confirmations)
-- ---------------------------------------------------------------------------

-- Draft 01 ── Task 7.0 Blocked (structural steel port delay)
--             Source: Email_021 | Confidence: 0.95 | Pending Review
INSERT INTO plan_updates_draft (
    baseline_task_id, extracted_wbs_id, extracted_task_name,
    extracted_owner, extracted_end_date, extracted_status,
    delta_type, delta_description, changed_fields,
    baseline_snapshot, source_id, evidence_string, technical_entity,
    confidence_score, confidence_breakdown,
    human_approval_status
)
SELECT
    b.task_id,
    '7.0',
    'Procurement of High-Grade Structural Steel',
    'Sofia Rossi',
    '2026-09-26',
    'Blocked',
    'Update',
    'Status changed from Not Started to Blocked; estimated 4-week delay on structural steel delivery at port.',
    ARRAY['status', 'end_date'],
    '{"owner": "Sofia Rossi", "current_status": "Not Started", "planned_end_date": "2026-08-28"}'::jsonb,
    (SELECT source_id FROM unstructured_sources WHERE file_name = 'Email_021.txt'),
    'Task 7.0 (Procurement) is Blocked. I anticipate a 4-week delay.',
    NULL,
    0.950,
    '{"task_id_present": true, "date_explicit": false, "owner_named": true, "status_explicit": true, "vague_language_flag": false}'::jsonb,
    'Pending Review'
FROM baseline_tasks b WHERE b.wbs_id = '7.0';


-- Draft 02 ── Task 13.0 Blocked (monsoon flooding)
--             Source: Snippet_001 | Confidence: 1.00 | Pending Review
INSERT INTO plan_updates_draft (
    baseline_task_id, extracted_wbs_id, extracted_task_name,
    extracted_owner, extracted_status,
    delta_type, delta_description, changed_fields,
    baseline_snapshot, source_id, evidence_string, technical_entity,
    confidence_score, confidence_breakdown,
    human_approval_status
)
SELECT
    b.task_id,
    '13.0',
    'Foundation Piling - North Sector Execution',
    'Ben Richardson',
    'Blocked',
    'Update',
    'Status changed from Not Started to Blocked; excavation pits flooded by monsoon rains.',
    ARRAY['status'],
    '{"owner": "Ben Richardson", "current_status": "Not Started", "planned_end_date": "2026-12-18"}'::jsonb,
    (SELECT source_id FROM unstructured_sources WHERE file_name = 'Snippet_001.txt'),
    'Ben reported that the Foundation Piling - North Sector (Task 13.0) is officially Blocked. Heavy seasonal monsoon rains have flooded the excavation pits.',
    NULL,
    1.000,
    '{"task_id_present": true, "date_explicit": false, "owner_named": true, "status_explicit": true, "vague_language_flag": false}'::jsonb,
    'Pending Review'
FROM baseline_tasks b WHERE b.wbs_id = '13.0';


-- Draft 03 ── Task 13.0 Blocked again (unmapped water main — second incident)
--             Source: Snippet_006 | Confidence: 1.00 | Escalated
INSERT INTO plan_updates_draft (
    baseline_task_id, extracted_wbs_id, extracted_task_name,
    extracted_owner, extracted_status,
    delta_type, delta_description, changed_fields,
    baseline_snapshot, source_id, evidence_string, technical_entity,
    confidence_score, confidence_breakdown,
    human_approval_status, reviewer_notes
)
SELECT
    b.task_id,
    '13.0',
    'Foundation Piling - North Sector Execution',
    'Ben Richardson',
    'Blocked',
    'Update',
    'Task 13.0 Blocked again — second separate incident; unmapped 1950s water main discovered. All drilling suspended.',
    ARRAY['status'],
    '{"owner": "Ben Richardson", "current_status": "Blocked", "planned_end_date": "2026-12-18"}'::jsonb,
    (SELECT source_id FROM unstructured_sources WHERE file_name = 'Snippet_006.txt'),
    'Foundation Piling (Task 13.0) is further Blocked. Site crews hit an unmapped 1950s water main. All drilling is suspended until the utility company can bypass the line.',
    NULL,
    1.000,
    '{"task_id_present": true, "date_explicit": false, "owner_named": false, "status_explicit": true, "vague_language_flag": false}'::jsonb,
    'Escalated',
    'Second blocking event on same task within 30 days. Escalated to Samuel Lee and James Peterson for programme recovery review.'
FROM baseline_tasks b WHERE b.wbs_id = '13.0';


-- Draft 04 ── Task 19.0 Blocked (edge computing nodes in customs)
--             Source: Email_024 | Confidence: 1.00 | Pending Review
INSERT INTO plan_updates_draft (
    baseline_task_id, extracted_wbs_id, extracted_task_name,
    extracted_owner, extracted_status,
    delta_type, delta_description, changed_fields,
    baseline_snapshot, source_id, evidence_string, technical_entity,
    confidence_score, confidence_breakdown,
    human_approval_status
)
SELECT
    b.task_id,
    '19.0',
    '5G Node Hardware & Edge Node Install',
    'Daniel Kim',
    'Blocked',
    'Update',
    'Status changed from Not Started to Blocked; Edge Computing Nodes held in customs.',
    ARRAY['status'],
    '{"owner": "Daniel Kim", "current_status": "Not Started", "planned_end_date": "2027-01-29"}'::jsonb,
    (SELECT source_id FROM unstructured_sources WHERE file_name = 'Email_024.txt'),
    'The edge computing nodes are stuck in customs. Task 19.0 (5G Node Hardware install) is Blocked until further notice.',
    'Edge Computing Nodes',
    1.000,
    '{"task_id_present": true, "date_explicit": false, "owner_named": true, "status_explicit": true, "vague_language_flag": false}'::jsonb,
    'Pending Review'
FROM baseline_tasks b WHERE b.wbs_id = '19.0';


-- Draft 05 ── Task 9.0 Blocked (flooding, irrigation prep)
--             Source: Email_029 | Confidence: 0.95 | Pending Review
INSERT INTO plan_updates_draft (
    baseline_task_id, extracted_wbs_id, extracted_task_name,
    extracted_owner, extracted_status,
    delta_type, delta_description, changed_fields,
    baseline_snapshot, source_id, evidence_string, technical_entity,
    confidence_score, confidence_breakdown,
    human_approval_status
)
SELECT
    b.task_id,
    '9.0',
    'Rooftop Garden & Irrigation System Design',
    'Priya Lakshmi',
    'Blocked',
    'Update',
    'Status changed from Not Started to Blocked; site flooding has damaged irrigation prep work. Minimum 10-day delay.',
    ARRAY['status'],
    '{"owner": "Priya Lakshmi", "current_status": "Not Started", "planned_end_date": "2026-08-07"}'::jsonb,
    (SELECT source_id FROM unstructured_sources WHERE file_name = 'Email_029.txt'),
    'flooding has damaged the initial irrigation prep. Task 9.0 (Rooftop Garden Design) site prep is Blocked for at least 10 days.',
    NULL,
    0.950,
    '{"task_id_present": true, "date_explicit": false, "owner_named": true, "status_explicit": true, "vague_language_flag": false}'::jsonb,
    'Pending Review'
FROM baseline_tasks b WHERE b.wbs_id = '9.0';


-- Draft 06 ── Task 14.0 Blocked (smart-grid inverter modules)
--             Source: Email_036 | Confidence: 1.00 | Approved
INSERT INTO plan_updates_draft (
    baseline_task_id, extracted_wbs_id, extracted_task_name,
    extracted_owner, extracted_status,
    delta_type, delta_description, changed_fields,
    baseline_snapshot, source_id, evidence_string, technical_entity,
    confidence_score, confidence_breakdown,
    human_approval_status, reviewed_by, reviewed_at, reviewer_notes,
    promotion_run_id
)
SELECT
    b.task_id,
    '14.0',
    'Smart Grid & Renewable Energy Integration',
    'Fatima Zahra',
    'Blocked',
    'Update',
    'Status changed from Not Started to Blocked; smart-grid inverter modules unavailable due to supply chain shortage.',
    ARRAY['status'],
    '{"owner": "Fatima Zahra", "current_status": "Not Started", "planned_end_date": "2026-11-20"}'::jsonb,
    (SELECT source_id FROM unstructured_sources WHERE file_name = 'Email_036.txt'),
    'the smart-grid inverter modules are stuck. Task 14.0 (Smart Grid Integration) is officially Blocked due to supply chain shortages.',
    NULL,
    1.000,
    '{"task_id_present": true, "date_explicit": false, "owner_named": true, "status_explicit": true, "vague_language_flag": false}'::jsonb,
    'Approved',
    'Samuel Lee',
    '2026-08-26 09:00:00+00',
    'Confirmed with Fatima. Supplier escalation lodged. Baseline status updated.',
    'PA-RUN-20260826-001'
FROM baseline_tasks b WHERE b.wbs_id = '14.0';


-- Draft 07 ── Task 20.0 Blocked (soil stability post-rain)
--             Source: Email_031 | Confidence: 0.95 | Pending Review
INSERT INTO plan_updates_draft (
    baseline_task_id, extracted_wbs_id, extracted_task_name,
    extracted_owner, extracted_status,
    delta_type, delta_description, changed_fields,
    baseline_snapshot, source_id, evidence_string, technical_entity,
    confidence_score, confidence_breakdown,
    human_approval_status
)
SELECT
    b.task_id,
    '20.0',
    'Hydraulic & Stormwater Management',
    'Vikram Singh',
    'Blocked',
    'Update',
    'Status changed to Blocked; soil instability in South Sector post-rain. 2-week delay anticipated.',
    ARRAY['status'],
    '{"owner": "Vikram Singh", "current_status": "Not Started", "planned_end_date": "2027-02-12"}'::jsonb,
    (SELECT source_id FROM unstructured_sources WHERE file_name = 'Email_031.txt'),
    'soil stability issues post-rain mean Task 20.0 (Hydraulic Stormwater) is Blocked. Expecting a 2-week delay in the South Sector.',
    NULL,
    0.950,
    '{"task_id_present": true, "date_explicit": false, "owner_named": true, "status_explicit": true, "vague_language_flag": false}'::jsonb,
    'Pending Review'
FROM baseline_tasks b WHERE b.wbs_id = '20.0';


-- Draft 08 ── Task 16.0 Blocked (ETFE Cushion System on backorder)
--             Source: Email_028 | Confidence: 0.90 | Escalated
INSERT INTO plan_updates_draft (
    baseline_task_id, extracted_wbs_id, extracted_task_name,
    extracted_owner, extracted_status,
    delta_type, delta_description, changed_fields,
    baseline_snapshot, source_id, evidence_string, technical_entity,
    confidence_score, confidence_breakdown,
    human_approval_status, reviewer_notes
)
SELECT
    b.task_id,
    '16.0',
    'Façade & Atrium Structural Assembly',
    'Thomas Müller',
    'Blocked',
    'Update',
    'Status changed to Blocked; ETFE Cushion System on backorder. Façade assembly halted.',
    ARRAY['status'],
    '{"owner": "Thomas Müller", "current_status": "Not Started", "planned_end_date": "2027-01-15"}'::jsonb,
    (SELECT source_id FROM unstructured_sources WHERE file_name = 'Email_028.txt'),
    'the ETFE Cushion System (Task 16.0 related) is on backorder. We are officially Blocked on façade assembly for the atrium.',
    'ETFE Cushion System',
    0.900,
    '{"task_id_present": false, "date_explicit": false, "owner_named": true, "status_explicit": true, "vague_language_flag": false}'::jsonb,
    'Escalated',
    'Task ID not explicit in source ("Task 16.0 related"). Escalated for PM confirmation before baseline write.'
FROM baseline_tasks b WHERE b.wbs_id = '16.0';


-- ---------------------------------------------------------------------------
-- SECTION 2 — DATE REVISIONS
-- ---------------------------------------------------------------------------

-- Draft 09 ── Task 2.0 End Date extension +7 days (Geotechnical Assessment)
--             Source: Email_023 | Confidence: 1.00 | Approved
INSERT INTO plan_updates_draft (
    baseline_task_id, extracted_wbs_id, extracted_task_name,
    extracted_owner, extracted_end_date, extracted_status,
    delta_type, delta_description, changed_fields,
    baseline_snapshot, source_id, evidence_string, technical_entity,
    confidence_score, confidence_breakdown,
    human_approval_status, reviewed_by, reviewed_at, reviewer_notes,
    promotion_run_id
)
SELECT
    b.task_id,
    '2.0',
    'Geotechnical Site Assessment (Nexus Bridge)',
    'Hiroshi Tanaka',
    '2026-05-22',
    'On Track',
    'Update',
    'End Date extended from 2026-05-15 to 2026-05-22 (+7 days). Variable soil density in South Pier section.',
    ARRAY['end_date'],
    '{"owner": "Hiroshi Tanaka", "current_status": "Not Started", "planned_end_date": "2026-05-15"}'::jsonb,
    (SELECT source_id FROM unstructured_sources WHERE file_name = 'Email_023.txt'),
    'the soil density is more variable than expected. I need to extend the Geotechnical Site Assessment (Task 2.0) to an End Date of May 22, 2026.',
    NULL,
    1.000,
    '{"task_id_present": true, "date_explicit": true, "owner_named": true, "status_explicit": false, "vague_language_flag": false}'::jsonb,
    'Approved',
    'Samuel Lee',
    '2026-04-22 08:30:00+00',
    'Minor extension. Approved. Baseline end date updated.',
    'PA-RUN-20260422-001'
FROM baseline_tasks b WHERE b.wbs_id = '2.0';


-- Draft 10 ── Task 2.0 End Date — second update from Snippet_019 (May 29)
--             Source: Snippet_019 | Confidence: 1.00 | Pending Review
INSERT INTO plan_updates_draft (
    baseline_task_id, extracted_wbs_id, extracted_task_name,
    extracted_owner, extracted_end_date, extracted_status,
    delta_type, delta_description, changed_fields,
    baseline_snapshot, source_id, evidence_string, technical_entity,
    confidence_score, confidence_breakdown,
    human_approval_status
)
SELECT
    b.task_id,
    '2.0',
    'Geotechnical Site Assessment (Nexus Bridge)',
    'Hiroshi Tanaka',
    '2026-05-29',
    'On Track',
    'Update',
    'End Date extended further to 2026-05-29 (previously revised to 2026-05-22). South Pier final report delayed.',
    ARRAY['end_date'],
    '{"owner": "Hiroshi Tanaka", "current_status": "Not Started", "planned_end_date": "2026-05-22"}'::jsonb,
    (SELECT source_id FROM unstructured_sources WHERE file_name = 'Snippet_019.txt'),
    'Hiroshi updated the timeline for the Geotechnical Site Assessment (Task 2.0). Final report for the South Pier will now be delivered on May 29, 2026.',
    NULL,
    1.000,
    '{"task_id_present": true, "date_explicit": true, "owner_named": true, "status_explicit": false, "vague_language_flag": false}'::jsonb,
    'Pending Review'
FROM baseline_tasks b WHERE b.wbs_id = '2.0';


-- Draft 11 ── Task 11.0 Start Date rescheduled (Town Hall)
--             Source: Snippet_008 | Confidence: 1.00 | Approved
INSERT INTO plan_updates_draft (
    baseline_task_id, extracted_wbs_id, extracted_task_name,
    extracted_owner, extracted_start_date, extracted_status,
    delta_type, delta_description, changed_fields,
    baseline_snapshot, source_id, evidence_string, technical_entity,
    confidence_score, confidence_breakdown,
    human_approval_status, reviewed_by, reviewed_at, reviewer_notes,
    promotion_run_id
)
SELECT
    b.task_id,
    '11.0',
    'Public Stakeholder Town Hall Series',
    'Rachael Smythe',
    '2026-07-27',
    'On Track',
    'Update',
    'Start Date rescheduled from 2026-07-13 to 2026-07-27 to accommodate local council availability.',
    ARRAY['start_date'],
    '{"owner": "Rachael Smythe", "current_status": "Not Started", "planned_start_date": "2026-07-13"}'::jsonb,
    (SELECT source_id FROM unstructured_sources WHERE file_name = 'Snippet_008.txt'),
    'The Public Stakeholder Town Hall (Task 11.0) has a confirmed date change. It is moved from July 13 to July 27 to accommodate the local council members'' schedules.',
    NULL,
    1.000,
    '{"task_id_present": true, "date_explicit": true, "owner_named": true, "status_explicit": false, "vague_language_flag": false}'::jsonb,
    'Approved',
    'Samuel Lee',
    '2026-07-15 10:00:00+00',
    'Confirmed with Rachael and council. Baseline start date updated.',
    'PA-RUN-20260715-001'
FROM baseline_tasks b WHERE b.wbs_id = '11.0';


-- Draft 12 ── Task 5.0 Start Date pushed (5G URLLC Mapping)
--             Source: Email_030 | Confidence: 1.00 | Pending Review
INSERT INTO plan_updates_draft (
    baseline_task_id, extracted_wbs_id, extracted_task_name,
    extracted_owner, extracted_start_date, extracted_status,
    delta_type, delta_description, changed_fields,
    baseline_snapshot, source_id, evidence_string, technical_entity,
    confidence_score, confidence_breakdown,
    human_approval_status
)
SELECT
    b.task_id,
    '5.0',
    '5G Network Topology & URLLC Mapping',
    'Amina Al-Farsi',
    '2026-05-25',
    'On Track',
    'Update',
    'Start Date pushed from 2026-05-11 to 2026-05-25 to align with Digital Twin Sync protocol update.',
    ARRAY['start_date'],
    '{"owner": "Amina Al-Farsi", "current_status": "Not Started", "planned_start_date": "2026-05-11"}'::jsonb,
    (SELECT source_id FROM unstructured_sources WHERE file_name = 'Email_030.txt'),
    'let''s push the start of Task 5.0 (5G Network Topology) to May 25, 2026, to align with new digital twin sync protocols.',
    'Digital Twin Sync',
    1.000,
    '{"task_id_present": true, "date_explicit": true, "owner_named": true, "status_explicit": false, "vague_language_flag": false}'::jsonb,
    'Pending Review'
FROM baseline_tasks b WHERE b.wbs_id = '5.0';


-- Draft 13 ── Task 17.0 Start Date shifted +7 days (MEP Corridor)
--             Source: Email_035 | Confidence: 1.00 | Approved
INSERT INTO plan_updates_draft (
    baseline_task_id, extracted_wbs_id, extracted_task_name,
    extracted_owner, extracted_start_date, extracted_status,
    delta_type, delta_description, changed_fields,
    baseline_snapshot, source_id, evidence_string, technical_entity,
    confidence_score, confidence_breakdown,
    human_approval_status, reviewed_by, reviewed_at, reviewer_notes,
    promotion_run_id
)
SELECT
    b.task_id,
    '17.0',
    'MEP Utility Corridor Optimization',
    'Linda Ng',
    '2026-09-28',
    'On Track',
    'Update',
    'Start Date shifted from 2026-09-21 to 2026-09-28 (+7 days).',
    ARRAY['start_date'],
    '{"owner": "Linda Ng", "current_status": "Not Started", "planned_start_date": "2026-09-21"}'::jsonb,
    (SELECT source_id FROM unstructured_sources WHERE file_name = 'Email_035.txt'),
    'I need to move the Start Date for Task 17.0 (MEP Corridor Optimization) from September 21 to September 28, 2026.',
    NULL,
    1.000,
    '{"task_id_present": true, "date_explicit": true, "owner_named": true, "status_explicit": false, "vague_language_flag": false}'::jsonb,
    'Approved',
    'Samuel Lee',
    '2026-09-23 09:15:00+00',
    'Minor shift. No downstream dependency impact confirmed. Approved.',
    'PA-RUN-20260923-001'
FROM baseline_tasks b WHERE b.wbs_id = '17.0';


-- Draft 14 ── Task 27.0 Start Date pushed (Transport Flow Simulation)
--             Source: Email_047 | Confidence: 1.00 | Pending Review
INSERT INTO plan_updates_draft (
    baseline_task_id, extracted_wbs_id, extracted_task_name,
    extracted_owner, extracted_start_date, extracted_status,
    delta_type, delta_description, changed_fields,
    baseline_snapshot, source_id, evidence_string, technical_entity,
    confidence_score, confidence_breakdown,
    human_approval_status
)
SELECT
    b.task_id,
    '27.0',
    'Multi-Modal Transport Flow Simulation',
    'Omar Bakri',
    '2027-02-01',
    'On Track',
    'Update',
    'Start Date pushed from 2027-01-18 to 2027-02-01 due to extended traffic modelling time.',
    ARRAY['start_date'],
    '{"owner": "Omar Bakri", "current_status": "Not Started", "planned_start_date": "2027-01-18"}'::jsonb,
    (SELECT source_id FROM unstructured_sources WHERE file_name = 'Email_047.txt'),
    'traffic modeling is taking longer. I need to move the Start Date for Task 27.0 (Transport Flow Simulation) to February 1, 2027.',
    NULL,
    1.000,
    '{"task_id_present": true, "date_explicit": true, "owner_named": true, "status_explicit": false, "vague_language_flag": false}'::jsonb,
    'Pending Review'
FROM baseline_tasks b WHERE b.wbs_id = '27.0';


-- Draft 15 ── Task 14.0 Vague date (Smart Grid — monsoon-dependent)
--             Source: Snippet_017 | Confidence: 0.45 | Pending Review
INSERT INTO plan_updates_draft (
    baseline_task_id, extracted_wbs_id, extracted_task_name,
    extracted_owner, extracted_status,
    delta_type, delta_description, changed_fields,
    baseline_snapshot, source_id, evidence_string, technical_entity,
    confidence_score, confidence_breakdown,
    human_approval_status
)
SELECT
    b.task_id,
    '14.0',
    'Smart Grid & Renewable Energy Integration',
    'Fatima Zahra',
    'Not Started',
    'Update',
    'Start date vague — "probably sometime after the monsoon season." No specific date extractable.',
    ARRAY['start_date'],
    '{"owner": "Fatima Zahra", "current_status": "Not Started", "planned_start_date": "2026-08-24"}'::jsonb,
    (SELECT source_id FROM unstructured_sources WHERE file_name = 'Snippet_017.txt'),
    'Fatima mentioned the physical install will begin "probably sometime after the monsoon season clears up."',
    NULL,
    0.450,
    '{"task_id_present": true, "date_explicit": false, "owner_named": true, "status_explicit": false, "vague_language_flag": true}'::jsonb,
    'Pending Review'
FROM baseline_tasks b WHERE b.wbs_id = '14.0';


-- ---------------------------------------------------------------------------
-- SECTION 3 — OWNER REASSIGNMENTS
-- ---------------------------------------------------------------------------

-- Draft 16 ── Task 15.0 Owner → Sarah Chen (GSIMS Platform)
--             Source: Email_022 | Confidence: 0.95 | Pending Review
INSERT INTO plan_updates_draft (
    baseline_task_id, extracted_wbs_id, extracted_task_name,
    extracted_owner, extracted_status,
    delta_type, delta_description, changed_fields,
    baseline_snapshot, source_id, evidence_string, technical_entity,
    confidence_score, confidence_breakdown,
    human_approval_status
)
SELECT
    b.task_id,
    '15.0',
    'GSIMS Platform Spatial Data Mapping',
    'Sarah Chen',
    'Not Started',
    'Update',
    'Owner reassigned from Alice Thompson to Sarah Chen.',
    ARRAY['owner'],
    '{"owner": "Alice Thompson", "current_status": "Not Started"}'::jsonb,
    (SELECT source_id FROM unstructured_sources WHERE file_name = 'Email_022.txt'),
    'I''d like you to take the lead on the GSIMS Platform Spatial Data Mapping (Task 15.0). Please coordinate with the tech team.',
    'GSIMS Platform',
    0.950,
    '{"task_id_present": true, "date_explicit": false, "owner_named": true, "status_explicit": false, "vague_language_flag": false}'::jsonb,
    'Pending Review'
FROM baseline_tasks b WHERE b.wbs_id = '15.0';


-- Draft 17 ── Task 29.0 Owner → Jessica Low (Claims & Legal)
--             Source: Email_034 | Confidence: 1.00 | Approved
INSERT INTO plan_updates_draft (
    baseline_task_id, extracted_wbs_id, extracted_task_name,
    extracted_owner, extracted_status,
    delta_type, delta_description, changed_fields,
    baseline_snapshot, source_id, evidence_string, technical_entity,
    confidence_score, confidence_breakdown,
    human_approval_status, reviewed_by, reviewed_at, reviewer_notes,
    promotion_run_id
)
SELECT
    b.task_id,
    '29.0',
    'Claims & Legal Liability Review',
    'Jessica Low',
    'Not Started',
    'Update',
    'Owner reassigned from Geoffery Tan to Jessica Low by Samuel Lee.',
    ARRAY['owner'],
    '{"owner": "Geoffery Tan", "current_status": "Not Started"}'::jsonb,
    (SELECT source_id FROM unstructured_sources WHERE file_name = 'Email_034.txt'),
    'Jessica, I''d like you to take the lead on Task 29.0 (Claims & Legal Liability). Geoffery, please provide her with the files.',
    NULL,
    1.000,
    '{"task_id_present": true, "date_explicit": false, "owner_named": true, "status_explicit": false, "vague_language_flag": false}'::jsonb,
    'Approved',
    'Samuel Lee',
    '2027-02-03 08:00:00+00',
    'Confirmed. Baseline owner updated to Jessica Low.',
    'PA-RUN-20270203-001'
FROM baseline_tasks b WHERE b.wbs_id = '29.0';


-- Draft 18 ── Task 18.0 Co-ownership (VDC Simulation)
--             Source: Email_027 | Confidence: 0.85 | Pending Review
INSERT INTO plan_updates_draft (
    baseline_task_id, extracted_wbs_id, extracted_task_name,
    extracted_owner, extracted_status,
    delta_type, delta_description, changed_fields,
    baseline_snapshot, source_id, evidence_string, technical_entity,
    confidence_score, confidence_breakdown,
    human_approval_status
)
SELECT
    b.task_id,
    '18.0',
    'VDC Construction Sequence Simulation',
    'Kevin Zhang, Sarah Chen',
    'Not Started',
    'Update',
    'Co-ownership assigned. Both Kevin Zhang and Sarah Chen now responsible. Primary/secondary roles unconfirmed.',
    ARRAY['owner'],
    '{"owner": "Kevin Zhang", "current_status": "Not Started"}'::jsonb,
    (SELECT source_id FROM unstructured_sources WHERE file_name = 'Email_027.txt'),
    'both Kevin and Sarah will now be responsible for Task 18.0 (VDC Construction Sequence Simulation).',
    NULL,
    0.850,
    '{"task_id_present": true, "date_explicit": false, "owner_named": true, "status_explicit": false, "vague_language_flag": false}'::jsonb,
    'Pending Review'
FROM baseline_tasks b WHERE b.wbs_id = '18.0';


-- ---------------------------------------------------------------------------
-- SECTION 4 — CONFLICTS
-- ---------------------------------------------------------------------------

-- Draft 19 ── Task 17.0 Ownership conflict (Linda Ng vs. David O'Sullivan)
--             Source: Snippet_013 | Confidence: 1.00 | Escalated
INSERT INTO plan_updates_draft (
    baseline_task_id, extracted_wbs_id, extracted_task_name,
    extracted_owner, extracted_status,
    delta_type, delta_description, changed_fields,
    baseline_snapshot, source_id, evidence_string, technical_entity,
    confidence_score, confidence_breakdown,
    human_approval_status, reviewer_notes
)
SELECT
    b.task_id,
    '17.0',
    'MEP Utility Corridor Optimization',
    'CONFLICT: Linda Ng vs. David O''Sullivan',
    'Not Started',
    'Conflict',
    'Ownership conflict: Linda Ng claims lead; David O''Sullivan insists structural team owns heights. Requires PM resolution.',
    ARRAY['owner'],
    '{"owner": "Linda Ng", "current_status": "Not Started"}'::jsonb,
    (SELECT source_id FROM unstructured_sources WHERE file_name = 'Snippet_013.txt'),
    'A conflict arose regarding Task 17.0 (MEP Corridor Optimization). Linda claims she is leading the optimization, but David insists his structural team needs to own the heights.',
    NULL,
    1.000,
    '{"task_id_present": true, "date_explicit": false, "owner_named": true, "status_explicit": false, "vague_language_flag": false}'::jsonb,
    'Escalated',
    'Direct ownership dispute between two senior leads. Escalated to Samuel Lee for resolution before baseline can be updated.'
FROM baseline_tasks b WHERE b.wbs_id = '17.0';


-- Draft 20 ── Task 10.0 Ownership conflict (Emily Watson vs. Sarah Chen)
--             Source: Snippet_020 | Confidence: 1.00 | Escalated
INSERT INTO plan_updates_draft (
    baseline_task_id, extracted_wbs_id, extracted_task_name,
    extracted_owner, extracted_status,
    delta_type, delta_description, changed_fields,
    baseline_snapshot, source_id, evidence_string, technical_entity,
    confidence_score, confidence_breakdown,
    human_approval_status, reviewer_notes
)
SELECT
    b.task_id,
    '10.0',
    'BIM Model Coordination (Phase 1)',
    'CONFLICT: Emily Watson vs. Sarah Chen',
    'Not Started',
    'Conflict',
    'Heritage zone BIM ownership disputed. Emily Watson claims primary ownership; Sarah Chen insists all layers must stay under her management.',
    ARRAY['owner'],
    '{"owner": "Sarah Chen", "current_status": "Not Started"}'::jsonb,
    (SELECT source_id FROM unstructured_sources WHERE file_name = 'Snippet_020.txt'),
    'Conflict regarding Task 10.0 (BIM Coordination) for the heritage zone. Emily believes she should be the primary Owner, while Sarah insists all layers stay under her management.',
    NULL,
    1.000,
    '{"task_id_present": true, "date_explicit": false, "owner_named": true, "status_explicit": false, "vague_language_flag": false}'::jsonb,
    'Escalated',
    'Heritage-zone BIM ownership. Both parties present credible claims. Requires formal RACI review.'
FROM baseline_tasks b WHERE b.wbs_id = '10.0';


-- Draft 21 ── Task 6.0 Vague date conflict (Bridge Piling Plan — "late next month")
--             Source: Snippet_004 | Confidence: 0.60 | Pending Review
INSERT INTO plan_updates_draft (
    baseline_task_id, extracted_wbs_id, extracted_task_name,
    extracted_owner, extracted_status,
    delta_type, delta_description, changed_fields,
    baseline_snapshot, source_id, evidence_string, technical_entity,
    confidence_score, confidence_breakdown,
    human_approval_status
)
SELECT
    b.task_id,
    '6.0',
    'Bridge Piling - Structural Foundation Plan',
    'David O''Sullivan',
    'On Track',
    'Update',
    'Completion date vague — "sometime late next month" (approx. 2026-06-30). Requires explicit confirmation.',
    ARRAY['end_date'],
    '{"owner": "David O''Sullivan", "current_status": "Not Started", "planned_end_date": "2026-07-31"}'::jsonb,
    (SELECT source_id FROM unstructured_sources WHERE file_name = 'Snippet_004.txt'),
    'David mentioned it should be wrapped up "sometime late next month."',
    NULL,
    0.600,
    '{"task_id_present": true, "date_explicit": false, "owner_named": true, "status_explicit": false, "vague_language_flag": true}'::jsonb,
    'Pending Review'
FROM baseline_tasks b WHERE b.wbs_id = '6.0';


-- Draft 22 ── Task 19.0 Vague start (5G Node — "whenever North Sector is ready")
--             Source: Snippet_002 | Confidence: 0.40 | Pending Review
INSERT INTO plan_updates_draft (
    baseline_task_id, extracted_wbs_id, extracted_task_name,
    extracted_owner, extracted_status,
    delta_type, delta_description, changed_fields,
    baseline_snapshot, source_id, evidence_string, technical_entity,
    confidence_score, confidence_breakdown,
    human_approval_status
)
SELECT
    b.task_id,
    '19.0',
    '5G Node Hardware & Edge Node Install',
    'Daniel Kim',
    'Not Started',
    'Update',
    'Start dependency on North Sector completion — no specific date. "Maybe mid-November" noted but unconfirmed.',
    ARRAY['start_date'],
    '{"owner": "Daniel Kim", "current_status": "Not Started", "planned_start_date": "2026-10-19"}'::jsonb,
    (SELECT source_id FROM unstructured_sources WHERE file_name = 'Snippet_002.txt'),
    'Daniel noted that the 5G Node Hardware install (Task 19.0) might be delayed. He suggested we start "whenever the North Sector is ready, maybe mid-November?"',
    'Edge Computing Nodes',
    0.400,
    '{"task_id_present": true, "date_explicit": false, "owner_named": true, "status_explicit": false, "vague_language_flag": true}'::jsonb,
    'Pending Review'
FROM baseline_tasks b WHERE b.wbs_id = '19.0';


-- ---------------------------------------------------------------------------
-- SECTION 5 — NEW TASKS (baseline_task_id = NULL)
-- ---------------------------------------------------------------------------

-- Draft 23 ── New Task: Circular Economy Material Verification
--             Source: Snippet_005 | Confidence: 0.80 | Pending Review
INSERT INTO plan_updates_draft (
    baseline_task_id, extracted_wbs_id, extracted_task_name,
    extracted_owner, extracted_status,
    delta_type, delta_description,
    source_id, evidence_string, technical_entity,
    confidence_score, confidence_breakdown,
    human_approval_status
)
VALUES (
    NULL,
    NULL,
    'Circular Economy Material Verification',
    'Elena Rodriguez',
    'Not Started',
    'New Task',
    'New Task proposed by Elena Rodriguez; required by building council for LEED Gold status compliance. Not in baseline WBS.',
    (SELECT source_id FROM unstructured_sources WHERE file_name = 'Snippet_005.txt'),
    'Elena confirmed a New Task: "Circular Economy Material Verification." This is an urgent requirement from the building council to maintain the project''s LEED Gold status.',
    NULL,
    0.800,
    '{"task_id_present": false, "date_explicit": false, "owner_named": true, "status_explicit": false, "vague_language_flag": false}'::jsonb,
    'Pending Review'
);


-- Draft 24 ── New Task: Carbon Offset Verification (Phase A)
--             Source: Email_032 | Confidence: 0.80 | Rejected
INSERT INTO plan_updates_draft (
    baseline_task_id, extracted_wbs_id, extracted_task_name,
    extracted_owner, extracted_status,
    delta_type, delta_description,
    source_id, evidence_string, technical_entity,
    confidence_score, confidence_breakdown,
    human_approval_status, reviewed_by, reviewed_at, reviewer_notes
)
VALUES (
    NULL,
    NULL,
    'Carbon Offset Verification (Phase A)',
    'Elena Rodriguez',
    'Not Started',
    'New Task',
    'New Task proposed — "Carbon Offset Verification (Phase A)" to precede Task 22.0 (Sustainability Audit). Not in baseline WBS.',
    (SELECT source_id FROM unstructured_sources WHERE file_name = 'Email_032.txt'),
    'we must add a New Task: "Carbon Offset Verification (Phase A)" before the final Sustainability Audit (Task 22.0).',
    NULL,
    0.800,
    '{"task_id_present": false, "date_explicit": false, "owner_named": true, "status_explicit": false, "vague_language_flag": false}'::jsonb,
    'Rejected',
    'Samuel Lee',
    '2026-11-20 09:00:00+00',
    'Scope review confirmed this is already captured under Task 22.0 sub-deliverables. Separate task not required. Rejected.'
);


-- Draft 25 ── New Task: Smart Wayfinding Totem Placement Study
--             Source: Snippet_003 | Confidence: 0.70 | Pending Review
INSERT INTO plan_updates_draft (
    baseline_task_id, extracted_wbs_id, extracted_task_name,
    extracted_owner, extracted_status,
    delta_type, delta_description,
    source_id, evidence_string, technical_entity,
    confidence_score, confidence_breakdown,
    human_approval_status
)
VALUES (
    NULL,
    NULL,
    'Smart Wayfinding Totem Placement Study',
    'INFERRED: Arjun Mehta',
    'Not Started',
    'New Task',
    'New Task proposed by Arjun Mehta. Must precede Task 24.0 (Interior Public Space Ergonomics). Owner inferred as proposer.',
    (SELECT source_id FROM unstructured_sources WHERE file_name = 'Snippet_003.txt'),
    'Arjun requested a New Task: "Smart Wayfinding Totem Placement Study." This needs to be completed before the Interior Public Space Ergonomics (Task 24.0) begins.',
    NULL,
    0.700,
    '{"task_id_present": false, "date_explicit": false, "owner_named": false, "status_explicit": false, "vague_language_flag": false}'::jsonb,
    'Pending Review'
);


-- =============================================================================
-- VERIFICATION QUERY
-- Uncomment and run after executing this seed to confirm coverage.
-- =============================================================================
-- SELECT
--     COUNT(*)                                                              AS total_drafts,
--     COUNT(*) FILTER (WHERE delta_type = 'Update')                        AS updates,
--     COUNT(*) FILTER (WHERE delta_type = 'New Task')                      AS new_tasks,
--     COUNT(*) FILTER (WHERE delta_type = 'Conflict')                      AS conflicts,
--     COUNT(*) FILTER (WHERE human_approval_status = 'Pending Review')     AS pending,
--     COUNT(*) FILTER (WHERE human_approval_status = 'Approved')           AS approved,
--     COUNT(*) FILTER (WHERE human_approval_status = 'Rejected')           AS rejected,
--     COUNT(*) FILTER (WHERE human_approval_status = 'Escalated')          AS escalated,
--     ROUND(AVG(confidence_score)::numeric, 3)                             AS avg_confidence,
--     MIN(confidence_score)                                                 AS min_confidence,
--     MAX(confidence_score)                                                 AS max_confidence
-- FROM plan_updates_draft;
--
-- Expected result:
--   total | updates | new_tasks | conflicts | pending | approved | rejected | escalated | avg_conf
--   ------+---------+-----------+-----------+---------+----------+----------+-----------+---------
--     25  |   19    |     3     |     3     |   15    |    5     |    1     |     4     |  ~0.87