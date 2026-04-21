-- =============================================================================
-- SJ PROJECT PLANNER AGENT — AZURE DATABASE FOR POSTGRESQL
-- Schema: relAIble — SJ Integrated Urban Nexus
-- Version: 1.0
-- Description: Supports delta detection between the WBS baseline and AI-extracted
--              plan updates from unstructured Meeting Minutes and Emails.
--              Review-before-update workflow enforced via Human_Approval_Status.
-- =============================================================================


-- ---------------------------------------------------------------------------
-- ENUM TYPES
-- ---------------------------------------------------------------------------

-- Task lifecycle status, aligned to values used across all source documents.
CREATE TYPE task_status AS ENUM (
    'Not Started',
    'On Track',
    'Blocked',
    'In Review',
    'Completed'
);

-- Categorises the delta detected between a new extraction and the baseline.
CREATE TYPE delta_type AS ENUM (
    'New Task',     -- Task is not present in SJ_Nexus_Baseline.csv
    'Update',       -- A field value has changed from the baseline
    'Conflict'      -- Two sources report contradictory values (e.g. ownership disputes)
);

-- Governs the Review-before-update workflow before any baseline write.
CREATE TYPE approval_status AS ENUM (
    'Pending Review',   -- Freshly extracted; awaiting human triage
    'Approved',         -- Project Director confirmed; safe to promote to baseline
    'Rejected',         -- Extraction deemed incorrect or out-of-scope
    'Escalated'         -- Flagged for senior review (e.g. Conflict deltas)
);

-- Source document types ingested by the extraction pipeline.
CREATE TYPE source_type AS ENUM (
    'Meeting Minute',
    'Email'
);


-- ---------------------------------------------------------------------------
-- TABLE: baseline_tasks
-- ---------------------------------------------------------------------------
-- Mirrors SJ_Nexus_Baseline.csv (SJ_Nexus_WBS).
-- Read-mostly; updated only after an Approved plan_updates_draft record is
-- promoted by the Power Automate workflow.
-- ---------------------------------------------------------------------------

CREATE TABLE baseline_tasks (
    task_id             SERIAL          PRIMARY KEY,

    -- WBS identifier — e.g. "13.0", "19.0". Unique across the project schedule.
    wbs_id              VARCHAR(10)     NOT NULL UNIQUE,

    -- Full task name matching the SJ Integrated Urban Nexus WBS.
    -- Examples drawn from real baseline data:
    --   'Foundation Piling - North Sector Execution'
    --   '5G Node Hardware & Edge Node Install'
    --   'Geotechnical Site Assessment (Nexus Bridge)'
    --   'GSIMS Platform Spatial Data Mapping'
    --   'Acoustic Barrier Design for Rail Link'
    --   'Cyber-Physical Threat Modeling (5G Sec)'
    task_name           VARCHAR(255)    NOT NULL,

    -- Primary responsible person. Sourced from persona_technical_entities.json.
    -- Examples: 'Ben Richardson', 'Amina Al-Farsi', 'Hiroshi Tanaka'
    owner               VARCHAR(100)    NOT NULL,

    -- Planned schedule from the approved WBS.
    planned_start_date  DATE            NOT NULL,
    planned_end_date    DATE            NOT NULL,

    -- Current execution status.
    current_status      task_status     NOT NULL DEFAULT 'Not Started',

    -- Reference project from SJ case studies that this task archetype mirrors.
    -- Drawn from case_study_summary_relAIble.pdf:
    --   'Kai Tak Sports Park'   → multi-stakeholder precision / DBO timelines
    --   'Banora Point Upgrade'  → infrastructure dependencies
    --   '5G Command Centre'     → Digital Twin & 5G lifecycle tasks
    --   'Google King''s Cross'  → regenerative urban design tasks
    reference_project   VARCHAR(100),

    -- Audit columns.
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- Indexes for delta detection joins and status dashboards.
CREATE INDEX idx_baseline_wbs_id     ON baseline_tasks (wbs_id);
CREATE INDEX idx_baseline_owner      ON baseline_tasks (owner);
CREATE INDEX idx_baseline_status     ON baseline_tasks (current_status);
CREATE INDEX idx_baseline_end_date   ON baseline_tasks (planned_end_date);

COMMENT ON TABLE  baseline_tasks IS
    'Approved WBS baseline. Mirrors SJ_Nexus_Baseline.csv. '
    'Only updated via the Power Automate promotion workflow after human approval.';
COMMENT ON COLUMN baseline_tasks.wbs_id IS
    'WBS decimal identifier, e.g. ''13.0''. Used as the join key for delta detection.';
COMMENT ON COLUMN baseline_tasks.reference_project IS
    'SJ case-study archetype. Drawn from case_study_summary_relAIble.pdf.';


-- ---------------------------------------------------------------------------
-- TABLE: unstructured_sources
-- ---------------------------------------------------------------------------
-- Registry of every raw document ingested by the extraction pipeline.
-- Provides the audit trail required by CLAUDE.md: every update must carry
-- a Source reference and Evidence string.
-- ---------------------------------------------------------------------------

CREATE TABLE unstructured_sources (
    source_id           SERIAL          PRIMARY KEY,

    -- Filename as it exists in /data/raw/ or /data/processed/.
    -- Examples: 'Snippet_016.txt', 'Email_021.txt'
    file_name           VARCHAR(255)    NOT NULL UNIQUE,

    -- 'Meeting Minute' or 'Email' — drives pipeline routing in Power Automate.
    source_type         source_type     NOT NULL,

    -- Date/time stamped in the document header (where present).
    document_date       TIMESTAMPTZ,

    -- Comma-separated attendees or recipients parsed from the document header.
    -- Examples: 'Samuel Lee, Ben Richardson, David O''Sullivan'
    --           'Sofia Rossi, Samuel Lee'
    participants        TEXT,

    -- Subject line (Emails) or snippet title (Meeting Minutes).
    -- Examples: 'Supply Chain Update: Task 7.0'
    --           'MEP & Structural Coordination'
    subject             VARCHAR(500),

    -- Full raw text body of the source document, preserved for re-extraction.
    raw_content         TEXT            NOT NULL,

    -- SHA-256 hash of raw_content. Prevents duplicate ingestion.
    content_hash        CHAR(64)        NOT NULL UNIQUE,

    -- Pipeline processing state.
    processing_status   VARCHAR(50)     NOT NULL DEFAULT 'Pending'
                            CHECK (processing_status IN ('Pending', 'Processed', 'Failed', 'Skipped')),

    -- Audit columns.
    ingested_at         TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    processed_at        TIMESTAMPTZ
);

CREATE INDEX idx_sources_type        ON unstructured_sources (source_type);
CREATE INDEX idx_sources_date        ON unstructured_sources (document_date);
CREATE INDEX idx_sources_status      ON unstructured_sources (processing_status);

COMMENT ON TABLE  unstructured_sources IS
    'Registry of raw Meeting Minutes and Emails ingested by the extraction pipeline. '
    'Provides the mandatory Source audit trail per CLAUDE.md spec.';
COMMENT ON COLUMN unstructured_sources.content_hash IS
    'SHA-256 of raw_content. Enforces idempotent ingestion — no document processed twice.';


-- ---------------------------------------------------------------------------
-- TABLE: plan_updates_draft
-- ---------------------------------------------------------------------------
-- Staging table for AI-extracted plan updates before human approval.
-- Implements the full schema from CLAUDE.md:
--   Task | Owner | Due Date | Status | Source | Confidence
-- Adds delta classification and the Review-before-update approval workflow.
-- ---------------------------------------------------------------------------

CREATE TABLE plan_updates_draft (
    draft_id                SERIAL          PRIMARY KEY,

    -- -----------------------------------------------------------------------
    -- EXTRACTED FIELDS — values as parsed from the source document.
    -- -----------------------------------------------------------------------

    -- Nullable FK — NULL when delta_type = 'New Task' (not yet in baseline).
    baseline_task_id        INTEGER         REFERENCES baseline_tasks (task_id)
                                                ON DELETE SET NULL,

    -- WBS ID as extracted. Used for baseline lookup even before FK resolves.
    -- Example: '13.0', '7.0', NULL (for new tasks)
    extracted_wbs_id        VARCHAR(10),

    -- Full task name from the source.
    -- SJ-grounded examples from real source data:
    --   'Foundation Piling - North Sector Execution'
    --   'Procurement of High-Grade Structural Steel'
    --   'Acoustic Barrier Design for Rail Link'
    -- New Task examples from source corpus:
    --   'Migratory Bird Flight Path Audit'
    --   'Carbon Offset Verification (Phase A)'
    --   'Greywater Filtration System Integration'
    --   '5G Mesh Latency Stress Test'
    --   'Intrusion Detection System (IDS) Calibration'
    --   'Smart Wayfinding Totem Placement Study'
    --   'Underwater Drone Piling Inspection'
    --   'Public Art Installation Structural Review'
    --   'Employee Phishing Simulation'
    --   'Circular Economy Material Verification'
    extracted_task_name     VARCHAR(255)    NOT NULL,

    -- Owner as extracted. May differ from baseline (ownership transfer or conflict).
    -- Example: 'Jessica Low' reassigned from 'Geoffery Tan' on Task 29.0
    extracted_owner         VARCHAR(100),

    -- Extracted start/end dates. NULL if the source uses vague language
    -- (e.g. "sometime after the monsoon season clears up" → low confidence).
    extracted_start_date    DATE,
    extracted_end_date      DATE,

    -- Status as extracted from the source document.
    extracted_status        task_status,

    -- -----------------------------------------------------------------------
    -- DELTA DETECTION — comparison against baseline_tasks.
    -- -----------------------------------------------------------------------

    -- Classification of the change detected.
    delta_type              delta_type      NOT NULL,

    -- Human-readable summary of what changed vs. the baseline.
    -- Examples:
    --   'End Date extended from 2026-05-15 to 2026-05-22 (Geotechnical Assessment)'
    --   'Status changed from Not Started to Blocked (Foundation Piling - contaminated soil)'
    --   'Owner conflict: Linda Ng vs. David O''Sullivan for MEP Corridor Optimization'
    --   'New Task not in baseline: Carbon Offset Verification (Phase A)'
    delta_description       TEXT,

    -- Specific field(s) that changed. NULL for New Tasks.
    -- Examples: 'end_date', 'status', 'owner', 'start_date,end_date'
    changed_fields          TEXT[],

    -- Snapshot of the baseline values before this update.
    -- Stored as JSONB for flexibility across all field types.
    -- Example: {"owner": "Alice Thompson", "current_status": "Not Started",
    --           "planned_end_date": "2026-10-30"}
    baseline_snapshot       JSONB,

    -- -----------------------------------------------------------------------
    -- PROVENANCE — mandatory per CLAUDE.md ("Source" + "Evidence" fields).
    -- -----------------------------------------------------------------------

    -- FK to the source document that yielded this extraction.
    source_id               INTEGER         NOT NULL
                                REFERENCES unstructured_sources (source_id)
                                ON DELETE RESTRICT,

    -- Verbatim sentence(s) from the source that support the extraction.
    -- Examples:
    --   'Task 7.0 (Procurement) is Blocked. I anticipate a 4-week delay.'
    --   'I need to extend the Geotechnical Site Assessment (Task 2.0) to
    --    an End Date of May 22, 2026.'
    --   'Foundation Piling (Task 13.0) is further Blocked. Site crews hit
    --    an unmapped 1950s water main.'
    evidence_string         TEXT            NOT NULL,

    -- Technical entity referenced in the evidence, where applicable.
    -- Drawn from persona_technical_entities.json (large_scale_sports_and_infrastructure
    -- and 5g_and_digital_command_centres entity catalogues).
    -- Examples: 'ETFE Cushion System', 'Edge Computing Nodes',
    --           'GSIMS Platform', 'Digital Twin Sync', 'URLLC'
    technical_entity        VARCHAR(150),

    -- -----------------------------------------------------------------------
    -- CONFIDENCE SCORING — from CLAUDE.md schema requirement.
    -- -----------------------------------------------------------------------

    -- Model-assigned confidence: 0.00–1.00.
    -- Scoring guidance:
    --   >= 0.85  → Explicit date/status/owner with named task ID
    --   0.60–0.84 → Inferred from context; task ID present but date vague
    --   < 0.60   → Ambiguous language ("sometime next month", "after monsoon")
    --              or no task ID; requires human review before any action
    confidence_score        NUMERIC(4,3)    NOT NULL
                                CHECK (confidence_score BETWEEN 0.000 AND 1.000),

    -- Structured breakdown of factors driving the confidence score.
    -- Example: {"task_id_present": true, "date_explicit": false,
    --           "owner_named": true, "status_explicit": true,
    --           "vague_language_flag": true}
    confidence_breakdown    JSONB,

    -- -----------------------------------------------------------------------
    -- REVIEW-BEFORE-UPDATE WORKFLOW — per CLAUDE.md architectural requirement.
    -- -----------------------------------------------------------------------

    -- Current approval state. Starts as 'Pending Review' on every extraction.
    human_approval_status   approval_status NOT NULL DEFAULT 'Pending Review',

    -- Identity of the reviewer (SJ project team member).
    -- NULL until a human acts on this draft.
    reviewed_by             VARCHAR(100),

    -- Timestamp of the approval/rejection decision.
    reviewed_at             TIMESTAMPTZ,

    -- Free-text annotation from the reviewer. Mandatory when status = 'Rejected'.
    reviewer_notes          TEXT,

    -- When Approved: the Power Automate run ID that promoted this to the baseline.
    -- Provides an end-to-end audit trail from extraction → approval → promotion.
    promotion_run_id        VARCHAR(100),

    -- -----------------------------------------------------------------------
    -- AUDIT COLUMNS
    -- -----------------------------------------------------------------------
    extracted_at            TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- Indexes supporting the primary query patterns:
--   1. Dashboard: all Pending Review drafts, sorted by confidence descending.
--   2. Conflict queue: all Conflict deltas awaiting escalation.
--   3. Task history: all drafts for a given baseline task.
--   4. Source audit: all extractions from a given document.
CREATE INDEX idx_drafts_approval_status ON plan_updates_draft (human_approval_status);
CREATE INDEX idx_drafts_delta_type      ON plan_updates_draft (delta_type);
CREATE INDEX idx_drafts_confidence      ON plan_updates_draft (confidence_score DESC);
CREATE INDEX idx_drafts_baseline_task   ON plan_updates_draft (baseline_task_id);
CREATE INDEX idx_drafts_source          ON plan_updates_draft (source_id);
CREATE INDEX idx_drafts_extracted_wbs   ON plan_updates_draft (extracted_wbs_id);

-- Partial index: fast retrieval of the active review queue.
CREATE INDEX idx_drafts_pending_review
    ON plan_updates_draft (extracted_at DESC)
    WHERE human_approval_status = 'Pending Review';

-- Partial index: fast retrieval of conflict escalations.
CREATE INDEX idx_drafts_conflicts
    ON plan_updates_draft (extracted_at DESC)
    WHERE delta_type = 'Conflict';

COMMENT ON TABLE  plan_updates_draft IS
    'Staging area for AI-extracted plan updates. Implements the full CLAUDE.md schema: '
    'Task | Owner | Due Date | Status | Source | Confidence. '
    'No change propagates to baseline_tasks until human_approval_status = ''Approved''.';
COMMENT ON COLUMN plan_updates_draft.confidence_score IS
    'Model confidence 0.000–1.000. Scores below 0.60 flag vague language '
    '(e.g. ''sometime after monsoon'') and require mandatory human review.';
COMMENT ON COLUMN plan_updates_draft.evidence_string IS
    'Verbatim quote from the source document supporting this extraction. '
    'Mandatory per CLAUDE.md audit trail requirement.';
COMMENT ON COLUMN plan_updates_draft.baseline_snapshot IS
    'JSONB snapshot of baseline_tasks values at time of extraction. '
    'Enables point-in-time diffing for the Power BI Gantt dashboard.';
COMMENT ON COLUMN plan_updates_draft.promotion_run_id IS
    'Power Automate run ID recorded when an Approved draft is promoted to baseline. '
    'Closes the end-to-end audit loop.';


-- ---------------------------------------------------------------------------
-- DELTA DETECTION VIEW
-- ---------------------------------------------------------------------------
-- Joins plan_updates_draft → baseline_tasks → unstructured_sources to produce
-- the side-by-side delta report consumed by the Power BI dashboard.
-- ---------------------------------------------------------------------------

CREATE VIEW vw_delta_report AS
SELECT
    d.draft_id,
    d.delta_type,

    -- Baseline (before)
    b.wbs_id                        AS baseline_wbs_id,
    b.task_name                     AS baseline_task_name,
    b.owner                         AS baseline_owner,
    b.planned_start_date            AS baseline_start_date,
    b.planned_end_date              AS baseline_end_date,
    b.current_status                AS baseline_status,

    -- Extracted (after)
    d.extracted_wbs_id,
    d.extracted_task_name,
    d.extracted_owner,
    d.extracted_start_date,
    d.extracted_end_date,
    d.extracted_status,

    -- Delta metadata
    d.delta_description,
    d.changed_fields,
    d.confidence_score,
    d.evidence_string,
    d.technical_entity,

    -- Provenance
    s.file_name                     AS source_file,
    s.source_type,
    s.document_date                 AS source_date,
    s.participants                  AS source_participants,

    -- Workflow state
    d.human_approval_status,
    d.reviewed_by,
    d.reviewed_at,
    d.reviewer_notes,
    d.promotion_run_id,
    d.extracted_at

FROM
    plan_updates_draft      d
    LEFT JOIN baseline_tasks         b ON d.baseline_task_id = b.task_id
    JOIN  unstructured_sources  s ON d.source_id       = s.source_id;

COMMENT ON VIEW vw_delta_report IS
    'Side-by-side baseline vs. extracted delta report. '
    'Primary data source for the Power BI Gantt and approval dashboards.';


-- ---------------------------------------------------------------------------
-- TRIGGER: updated_at auto-maintenance
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION fn_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_baseline_tasks_updated_at
    BEFORE UPDATE ON baseline_tasks
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

CREATE TRIGGER trg_plan_updates_draft_updated_at
    BEFORE UPDATE ON plan_updates_draft
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();


-- ---------------------------------------------------------------------------
-- SEED: baseline_tasks from SJ_Nexus_Baseline.csv
-- ---------------------------------------------------------------------------
-- Full 30-task WBS. Task names, owners, dates, and reference projects sourced
-- directly from SJ_Nexus_Baseline.csv and case_study_summary_relAIble.pdf.
-- ---------------------------------------------------------------------------

INSERT INTO baseline_tasks
    (wbs_id, task_name, owner, planned_start_date, planned_end_date, current_status, reference_project)
VALUES
    ('1.0',  'Project Charter & Scope Finalization',           'Samuel Lee',       '2026-04-06', '2026-04-17', 'On Track',    'Kai Tak Sports Park'),
    ('2.0',  'Geotechnical Site Assessment (Nexus Bridge)',     'Hiroshi Tanaka',   '2026-04-20', '2026-05-15', 'Not Started', 'Banora Point Upgrade'),
    ('3.0',  'Environmental Impact & Biodiversity Study',       'Chloe Dupont',     '2026-04-20', '2026-06-12', 'Not Started', 'Banora Point Upgrade'),
    ('4.0',  'Digital Twin Framework & Sync Protocol',         'Marcus Wong',      '2026-05-04', '2026-06-26', 'Not Started', '5G Command Centre'),
    ('5.0',  '5G Network Topology & URLLC Mapping',            'Amina Al-Farsi',   '2026-05-11', '2026-07-03', 'Not Started', '5G Command Centre'),
    ('6.0',  'Bridge Piling - Structural Foundation Plan',     'David O''Sullivan', '2026-05-18', '2026-07-31', 'Not Started', 'Kai Tak Sports Park'),
    ('7.0',  'Procurement of High-Grade Structural Steel',     'Sofia Rossi',      '2026-06-01', '2026-08-28', 'Not Started', 'Kai Tak Sports Park'),
    ('8.0',  'Heritage Site Vibration Protection Strategy',    'Emily Watson',     '2026-06-08', '2026-07-10', 'Not Started', 'Google King''s Cross'),
    ('9.0',  'Rooftop Garden & Irrigation System Design',      'Priya Lakshmi',    '2026-06-15', '2026-08-07', 'Not Started', 'Google King''s Cross'),
    ('10.0', 'BIM Model Coordination (Phase 1)',               'Sarah Chen',       '2026-07-06', '2026-09-18', 'Not Started', 'Kai Tak Sports Park'),
    ('11.0', 'Public Stakeholder Town Hall Series',            'Rachael Smythe',   '2026-07-13', '2026-10-02', 'Not Started', 'Banora Point Upgrade'),
    ('12.0', 'Site Safety & Access Protocol',                  'James Peterson',   '2026-08-03', '2026-08-14', 'Not Started', 'Kai Tak Sports Park'),
    ('13.0', 'Foundation Piling - North Sector Execution',     'Ben Richardson',   '2026-08-17', '2026-12-18', 'Not Started', 'Banora Point Upgrade'),
    ('14.0', 'Smart Grid & Renewable Energy Integration',      'Fatima Zahra',     '2026-08-24', '2026-11-20', 'Not Started', '5G Command Centre'),
    ('15.0', 'GSIMS Platform Spatial Data Mapping',            'Alice Thompson',   '2026-09-07', '2026-10-30', 'Not Started', '5G Command Centre'),
    ('16.0', 'Façade Thermal Performance Analysis',            'Thomas Müller',    '2026-09-14', '2026-11-06', 'Not Started', 'Kai Tak Sports Park'),
    ('17.0', 'MEP Utility Corridor Optimization',              'Linda Ng',         '2026-09-21', '2026-11-27', 'Not Started', 'Banora Point Upgrade'),
    ('18.0', 'VDC Construction Sequence Simulation',           'Kevin Zhang',      '2026-10-05', '2026-11-13', 'Not Started', '5G Command Centre'),
    ('19.0', '5G Node Hardware & Edge Node Install',           'Daniel Kim',       '2026-10-19', '2027-01-29', 'Not Started', '5G Command Centre'),
    ('20.0', 'Hydraulic Stormwater Drainage Systems',          'Vikram Singh',     '2026-11-02', '2027-02-12', 'Not Started', 'Banora Point Upgrade'),
    ('21.0', 'Acoustic Barrier Design for Rail Link',          'Isabella Varga',   '2026-11-09', '2026-12-18', 'Not Started', 'Kai Tak Sports Park'),
    ('22.0', 'Sustainability & Carbon Neutrality Audit',       'Elena Rodriguez',  '2026-11-16', '2027-03-26', 'Not Started', 'Google King''s Cross'),
    ('23.0', 'Urban Nexus Masterplan Alignment',               'Arjun Mehta',      '2026-12-01', '2027-01-22', 'Not Started', 'Google King''s Cross'),
    ('24.0', 'Interior Public Space Ergonomics',               'Zoe Castellano',   '2026-12-07', '2027-02-19', 'Not Started', 'Google King''s Cross'),
    ('25.0', 'Cyber-Physical Threat Modeling (5G Sec)',        'Robert Kwok',      '2027-01-04', '2027-02-26', 'Not Started', '5G Command Centre'),
    ('26.0', 'Urban Lighting & Nightscape Design',             'Hassan Meer',      '2027-01-11', '2027-03-05', 'Not Started', 'Google King''s Cross'),
    ('27.0', 'Multi-Modal Transport Flow Simulation',          'Omar Bakri',       '2027-01-18', '2027-03-12', 'Not Started', 'Banora Point Upgrade'),
    ('28.0', 'Contract Variation & Budget Realignment',        'Jessica Low',      '2027-02-01', '2027-03-19', 'Not Started', 'Kai Tak Sports Park'),
    ('29.0', 'Claims & Legal Liability Review',                'Geoffery Tan',     '2027-03-01', '2027-04-16', 'Not Started', 'Kai Tak Sports Park'),
    ('30.0', 'Final Document Archival & Baseline Lock',        'Siti Nurhaliza',   '2027-04-19', '2027-04-30', 'Not Started', 'Kai Tak Sports Park');