-- =============================================================================
-- SJ PROJECT PLANNER AGENT — SEED: unstructured_sources
-- File: seed_unstructured_sources.sql
-- Version: 1.0
-- Description: Inserts all 50 source documents (20 Meeting Minute Snippets +
--              30 Email Threads) into unstructured_sources.
--              All rows default to processing_status = 'Pending', ready for
--              the Extraction Agent pipeline to consume.
--
-- Usage:
--   psql -h <server>.postgres.database.azure.com \
--        -U <admin> -d sj_nexus \
--        -f seed_unstructured_sources.sql
--
-- Notes:
--   • content_hash is computed inline by PostgreSQL using sha256().
--   • ON CONFLICT DO NOTHING makes the script safe to re-run (idempotent).
--   • Single quotes inside raw_content are escaped as '' (two single quotes).
-- =============================================================================

-- ---------------------------------------------------------------------------
-- MEETING MINUTE SNIPPETS (Snippet_001 – Snippet_020)
-- ---------------------------------------------------------------------------

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Snippet_001.txt',
    'Meeting Minute',
    '2026-08-18',
    'Samuel Lee, Ben Richardson, David O''Sullivan',
    'Weekly Progress Review (Infrastructure)',
    'Date: 2026-08-18 10:00 AM | Attendees: Samuel Lee, Ben Richardson, David O''Sullivan | Source: Meeting Minute
**Snippet 001: Weekly Progress Review (Infrastructure)**
* Discussion: Ben reported that the Foundation Piling - North Sector (Task 13.0) is officially Blocked. Heavy seasonal monsoon rains have flooded the excavation pits. Work cannot resume until the pumps clear the site.',
    encode(sha256('Date: 2026-08-18 10:00 AM | Attendees: Samuel Lee, Ben Richardson, David O''Sullivan | Source: Meeting Minute
**Snippet 001: Weekly Progress Review (Infrastructure)**
* Discussion: Ben reported that the Foundation Piling - North Sector (Task 13.0) is officially Blocked. Heavy seasonal monsoon rains have flooded the excavation pits. Work cannot resume until the pumps clear the site.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Snippet_002.txt',
    'Meeting Minute',
    '2026-10-20',
    'Marcus Wong, Daniel Kim, Robert Kwok',
    'Digital Command Centre Sync',
    'Date: 2026-10-20 02:00 PM | Attendees: Marcus Wong, Daniel Kim, Robert Kwok | Source: Meeting Minute
**Snippet 002: Digital Command Centre Sync**
* Discussion: Daniel noted that the 5G Node Hardware install (Task 19.0) might be delayed. He suggested we start "whenever the North Sector is ready, maybe mid-November?"',
    encode(sha256('Date: 2026-10-20 02:00 PM | Attendees: Marcus Wong, Daniel Kim, Robert Kwok | Source: Meeting Minute
**Snippet 002: Digital Command Centre Sync**
* Discussion: Daniel noted that the 5G Node Hardware install (Task 19.0) might be delayed. He suggested we start "whenever the North Sector is ready, maybe mid-November?"'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Snippet_003.txt',
    'Meeting Minute',
    '2026-12-08',
    'Arjun Mehta, Priya Lakshmi, Zoe Castellano',
    'Urban Design Workshop',
    'Date: 2026-12-08 11:30 AM | Attendees: Arjun Mehta, Priya Lakshmi, Zoe Castellano | Source: Meeting Minute
**Snippet 003: Urban Design Workshop**
* Discussion: Arjun requested a New Task: "Smart Wayfinding Totem Placement Study." This needs to be completed before the Interior Public Space Ergonomics (Task 24.0) begins.',
    encode(sha256('Date: 2026-12-08 11:30 AM | Attendees: Arjun Mehta, Priya Lakshmi, Zoe Castellano | Source: Meeting Minute
**Snippet 003: Urban Design Workshop**
* Discussion: Arjun requested a New Task: "Smart Wayfinding Totem Placement Study." This needs to be completed before the Interior Public Space Ergonomics (Task 24.0) begins.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Snippet_004.txt',
    'Meeting Minute',
    '2026-05-19',
    'David O''Sullivan, Sarah Chen, Hiroshi Tanaka',
    'Structural Integrity Briefing',
    'Date: 2026-05-19 09:00 AM | Attendees: David O''Sullivan, Sarah Chen, Hiroshi Tanaka | Source: Meeting Minute
**Snippet 004: Structural Integrity Briefing**
* Discussion: Regarding Task 6.0 (Bridge Piling Plan), David mentioned it should be wrapped up "sometime late next month."',
    encode(sha256('Date: 2026-05-19 09:00 AM | Attendees: David O''Sullivan, Sarah Chen, Hiroshi Tanaka | Source: Meeting Minute
**Snippet 004: Structural Integrity Briefing**
* Discussion: Regarding Task 6.0 (Bridge Piling Plan), David mentioned it should be wrapped up "sometime late next month."'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Snippet_005.txt',
    'Meeting Minute',
    '2026-06-16',
    'Elena Rodriguez, Chloe Dupont, Fatima Zahra',
    'Sustainability Committee',
    'Date: 2026-06-16 04:00 PM | Attendees: Elena Rodriguez, Chloe Dupont, Fatima Zahra | Source: Meeting Minute
**Snippet 005: Sustainability Committee**
* Discussion: Elena confirmed a New Task: "Circular Economy Material Verification." This is an urgent requirement from the building council to maintain the project''s LEED Gold status.',
    encode(sha256('Date: 2026-06-16 04:00 PM | Attendees: Elena Rodriguez, Chloe Dupont, Fatima Zahra | Source: Meeting Minute
**Snippet 005: Sustainability Committee**
* Discussion: Elena confirmed a New Task: "Circular Economy Material Verification." This is an urgent requirement from the building council to maintain the project''s LEED Gold status.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Snippet_006.txt',
    'Meeting Minute',
    '2026-08-10',
    'James Peterson, Ben Richardson',
    'Site Safety Audit',
    'Date: 2026-08-10 10:00 AM | Attendees: James Peterson, Ben Richardson | Source: Meeting Minute
**Snippet 006: Site Safety Audit**
* Discussion: Foundation Piling (Task 13.0) is further Blocked. Site crews hit an unmapped 1950s water main. All drilling is suspended until the utility company can bypass the line.',
    encode(sha256('Date: 2026-08-10 10:00 AM | Attendees: James Peterson, Ben Richardson | Source: Meeting Minute
**Snippet 006: Site Safety Audit**
* Discussion: Foundation Piling (Task 13.0) is further Blocked. Site crews hit an unmapped 1950s water main. All drilling is suspended until the utility company can bypass the line.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Snippet_007.txt',
    'Meeting Minute',
    '2026-05-05',
    'Marcus Wong, Sarah Chen',
    'Tech Integration Sync',
    'Date: 2026-05-05 02:00 PM | Attendees: Marcus Wong, Sarah Chen | Source: Meeting Minute
**Snippet 007: Tech Integration Sync**
* Discussion: Marcus proposed a New Task: "Cyber-Physical Stress Test." This must occur immediately before the Digital Twin Sync (Task 4.0) to ensure the 5G nodes can handle the data load.',
    encode(sha256('Date: 2026-05-05 02:00 PM | Attendees: Marcus Wong, Sarah Chen | Source: Meeting Minute
**Snippet 007: Tech Integration Sync**
* Discussion: Marcus proposed a New Task: "Cyber-Physical Stress Test." This must occur immediately before the Digital Twin Sync (Task 4.0) to ensure the 5G nodes can handle the data load.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Snippet_008.txt',
    'Meeting Minute',
    '2026-07-14',
    'Rachael Smythe, Samuel Lee',
    'Stakeholder Briefing',
    'Date: 2026-07-14 09:30 AM | Attendees: Rachael Smythe, Samuel Lee | Source: Meeting Minute
**Snippet 008: Stakeholder Briefing**
* Discussion: The Public Stakeholder Town Hall (Task 11.0) has a confirmed date change. It is moved from July 13 to July 27 to accommodate the local council members'' schedules.',
    encode(sha256('Date: 2026-07-14 09:30 AM | Attendees: Rachael Smythe, Samuel Lee | Source: Meeting Minute
**Snippet 008: Stakeholder Briefing**
* Discussion: The Public Stakeholder Town Hall (Task 11.0) has a confirmed date change. It is moved from July 13 to July 27 to accommodate the local council members'' schedules.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Snippet_009.txt',
    'Meeting Minute',
    '2026-09-14',
    'Fatima Zahra, Marcus Wong, Daniel Kim',
    'Smart Infrastructure Review',
    'Date: 2026-09-14 03:00 PM | Attendees: Fatima Zahra, Marcus Wong, Daniel Kim | Source: Meeting Minute
**Snippet 009: Smart Infrastructure Review**
* Discussion: Task 14.0 (Smart Grid Integration) is Blocked. The inverter modules were not delivered. Fatima estimates a 3-week delay minimum.',
    encode(sha256('Date: 2026-09-14 03:00 PM | Attendees: Fatima Zahra, Marcus Wong, Daniel Kim | Source: Meeting Minute
**Snippet 009: Smart Infrastructure Review**
* Discussion: Task 14.0 (Smart Grid Integration) is Blocked. The inverter modules were not delivered. Fatima estimates a 3-week delay minimum.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Snippet_010.txt',
    'Meeting Minute',
    '2026-04-21',
    'Chloe Dupont, Samuel Lee',
    'Environmental Oversight',
    'Date: 2026-04-21 10:00 AM | Attendees: Chloe Dupont, Samuel Lee | Source: Meeting Minute
**Snippet 010: Environmental Oversight**
* Discussion: Chloe flagged a New Task: "Migratory Bird Flight Path Audit." Recent environmental surveys near the Nexus Bridge site indicate a protected species nesting nearby.',
    encode(sha256('Date: 2026-04-21 10:00 AM | Attendees: Chloe Dupont, Samuel Lee | Source: Meeting Minute
**Snippet 010: Environmental Oversight**
* Discussion: Chloe flagged a New Task: "Migratory Bird Flight Path Audit." Recent environmental surveys near the Nexus Bridge site indicate a protected species nesting nearby.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Snippet_011.txt',
    'Meeting Minute',
    '2026-10-12',
    'Isabella Varga, Ben Richardson, David O''Sullivan',
    'Acoustics & Structural Coordination',
    'Date: 2026-10-12 02:30 PM | Attendees: Isabella Varga, Ben Richardson, David O''Sullivan | Source: Meeting Minute
**Snippet 011: Acoustics & Structural Coordination**
* Discussion: Isabella confirmed that the Acoustic Barrier Design for Rail Link (Task 21.0) is On Track. Test panels passed ISO 717 requirements at the mockup stage.',
    encode(sha256('Date: 2026-10-12 02:30 PM | Attendees: Isabella Varga, Ben Richardson, David O''Sullivan | Source: Meeting Minute
**Snippet 011: Acoustics & Structural Coordination**
* Discussion: Isabella confirmed that the Acoustic Barrier Design for Rail Link (Task 21.0) is On Track. Test panels passed ISO 717 requirements at the mockup stage.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Snippet_012.txt',
    'Meeting Minute',
    '2026-07-07',
    'Alice Thompson, Marcus Wong',
    'GIS & Digital Platform Review',
    'Date: 2026-07-07 11:00 AM | Attendees: Alice Thompson, Marcus Wong | Source: Meeting Minute
**Snippet 012: GIS & Digital Platform Review**
* Discussion: Alice updated that the GSIMS Platform Spatial Data Mapping (Task 15.0) is On Track. All utility layer uploads are complete and verified.',
    encode(sha256('Date: 2026-07-07 11:00 AM | Attendees: Alice Thompson, Marcus Wong | Source: Meeting Minute
**Snippet 012: GIS & Digital Platform Review**
* Discussion: Alice updated that the GSIMS Platform Spatial Data Mapping (Task 15.0) is On Track. All utility layer uploads are complete and verified.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Snippet_013.txt',
    'Meeting Minute',
    '2026-09-22',
    'Linda Ng, David O''Sullivan, Sarah Chen',
    'MEP & Structural Coordination',
    'Date: 2026-09-22 09:00 AM | Attendees: Linda Ng, David O''Sullivan, Sarah Chen | Source: Meeting Minute
**Snippet 013: MEP & Structural Coordination**
* Discussion: A conflict arose regarding Task 17.0 (MEP Corridor Optimization). Linda claims she is leading the optimization, but David insists his structural team needs to own the heights.',
    encode(sha256('Date: 2026-09-22 09:00 AM | Attendees: Linda Ng, David O''Sullivan, Sarah Chen | Source: Meeting Minute
**Snippet 013: MEP & Structural Coordination**
* Discussion: A conflict arose regarding Task 17.0 (MEP Corridor Optimization). Linda claims she is leading the optimization, but David insists his structural team needs to own the heights.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Snippet_014.txt',
    'Meeting Minute',
    '2026-11-24',
    'Omar Bakri, Arjun Mehta, Samuel Lee',
    'Transport & Mobility Workshop',
    'Date: 2026-11-24 10:00 AM | Attendees: Omar Bakri, Arjun Mehta, Samuel Lee | Source: Meeting Minute
**Snippet 014: Transport & Mobility Workshop**
* Discussion: Omar confirmed the Multi-Modal Transport Flow Simulation (Task 27.0) is On Track. Preliminary traffic modelling results have been submitted to the council.',
    encode(sha256('Date: 2026-11-24 10:00 AM | Attendees: Omar Bakri, Arjun Mehta, Samuel Lee | Source: Meeting Minute
**Snippet 014: Transport & Mobility Workshop**
* Discussion: Omar confirmed the Multi-Modal Transport Flow Simulation (Task 27.0) is On Track. Preliminary traffic modelling results have been submitted to the council.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Snippet_015.txt',
    'Meeting Minute',
    '2026-12-02',
    'Arjun Mehta, Rachael Smythe',
    'Urban Nexus Masterplan Review',
    'Date: 2026-12-02 02:00 PM | Attendees: Arjun Mehta, Rachael Smythe | Source: Meeting Minute
**Snippet 015: Urban Nexus Masterplan Review**
* Discussion: Arjun requested a New Task: "Public Realm Shade Analysis" to simulate heat islands following feedback from the town hall.',
    encode(sha256('Date: 2026-12-02 02:00 PM | Attendees: Arjun Mehta, Rachael Smythe | Source: Meeting Minute
**Snippet 015: Urban Nexus Masterplan Review**
* Discussion: Arjun requested a New Task: "Public Realm Shade Analysis" to simulate heat islands following feedback from the town hall.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Snippet_016.txt',
    'Meeting Minute',
    '2026-06-02',
    'Sofia Rossi, Ben Richardson',
    'Logistics & Procurement Briefing',
    'Date: 2026-06-02 03:00 PM | Attendees: Sofia Rossi, Ben Richardson | Source: Meeting Minute
**Snippet 016: Logistics & Procurement Briefing**
* Discussion: Sofia noted that the Structural Steel Procurement (Task 7.0) is still Blocked. Customs has flagged the alloy composition for additional testing.',
    encode(sha256('Date: 2026-06-02 03:00 PM | Attendees: Sofia Rossi, Ben Richardson | Source: Meeting Minute
**Snippet 016: Logistics & Procurement Briefing**
* Discussion: Sofia noted that the Structural Steel Procurement (Task 7.0) is still Blocked. Customs has flagged the alloy composition for additional testing.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Snippet_017.txt',
    'Meeting Minute',
    '2026-08-25',
    'Fatima Zahra, Samuel Lee',
    'Smart Grid & Energy Strategy',
    'Date: 2026-08-25 10:00 AM | Attendees: Fatima Zahra, Samuel Lee | Source: Meeting Minute
**Snippet 017: Smart Grid & Energy Strategy**
* Discussion: Regarding the Smart Grid Integration (Task 14.0), Fatima mentioned the physical install will begin "probably sometime after the monsoon season clears up."',
    encode(sha256('Date: 2026-08-25 10:00 AM | Attendees: Fatima Zahra, Samuel Lee | Source: Meeting Minute
**Snippet 017: Smart Grid & Energy Strategy**
* Discussion: Regarding the Smart Grid Integration (Task 14.0), Fatima mentioned the physical install will begin "probably sometime after the monsoon season clears up."'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Snippet_018.txt',
    'Meeting Minute',
    '2027-01-05',
    'Robert Kwok, Daniel Kim',
    'Operational Technology (OT) Security',
    'Date: 2027-01-05 04:00 PM | Attendees: Robert Kwok, Daniel Kim | Source: Meeting Minute
**Snippet 018: Operational Technology (OT) Security**
* Discussion: Robert mandated a New Task: "Intrusion Detection System (IDS) Calibration." This must be performed on the 5G nodes before syncing to the GSIMS platform.',
    encode(sha256('Date: 2027-01-05 04:00 PM | Attendees: Robert Kwok, Daniel Kim | Source: Meeting Minute
**Snippet 018: Operational Technology (OT) Security**
* Discussion: Robert mandated a New Task: "Intrusion Detection System (IDS) Calibration." This must be performed on the 5G nodes before syncing to the GSIMS platform.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Snippet_019.txt',
    'Meeting Minute',
    '2026-05-18',
    'Hiroshi Tanaka, David O''Sullivan',
    'Geotechnical & Foundation Close-out',
    'Date: 2026-05-18 11:00 AM | Attendees: Hiroshi Tanaka, David O''Sullivan | Source: Meeting Minute
**Snippet 019: Geotechnical & Foundation Close-out**
* Discussion: Hiroshi updated the timeline for the Geotechnical Site Assessment (Task 2.0). Final report for the South Pier will now be delivered on May 29, 2026.',
    encode(sha256('Date: 2026-05-18 11:00 AM | Attendees: Hiroshi Tanaka, David O''Sullivan | Source: Meeting Minute
**Snippet 019: Geotechnical & Foundation Close-out**
* Discussion: Hiroshi updated the timeline for the Geotechnical Site Assessment (Task 2.0). Final report for the South Pier will now be delivered on May 29, 2026.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Snippet_020.txt',
    'Meeting Minute',
    '2026-07-07',
    'Emily Watson, Arjun Mehta, Sarah Chen',
    'Heritage & Conservation Oversight',
    'Date: 2026-07-07 09:00 AM | Attendees: Emily Watson, Arjun Mehta, Sarah Chen | Source: Meeting Minute
**Snippet 020: Heritage & Conservation Oversight**
* Discussion: Conflict regarding Task 10.0 (BIM Coordination) for the heritage zone. Emily believes she should be the primary Owner, while Sarah insists all layers stay under her management.',
    encode(sha256('Date: 2026-07-07 09:00 AM | Attendees: Emily Watson, Arjun Mehta, Sarah Chen | Source: Meeting Minute
**Snippet 020: Heritage & Conservation Oversight**
* Discussion: Conflict regarding Task 10.0 (BIM Coordination) for the heritage zone. Emily believes she should be the primary Owner, while Sarah insists all layers stay under her management.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;


-- ---------------------------------------------------------------------------
-- EMAIL THREADS (Email_021 – Email_050)
-- ---------------------------------------------------------------------------

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_021.txt',
    'Email',
    '2026-06-01',
    'Sofia Rossi, Samuel Lee',
    'Supply Chain Update: Task 7.0',
    'Date: 2026-06-01 08:45 AM | Recipients: Sofia Rossi, Samuel Lee | Source: Email
From: Sofia Rossi | To: Samuel Lee | Subject: Supply Chain Update: Task 7.0
Samuel, the high-grade structural steel for the Nexus Bridge is held up at the port. Task 7.0 (Procurement) is Blocked. I anticipate a 4-week delay.',
    encode(sha256('Date: 2026-06-01 08:45 AM | Recipients: Sofia Rossi, Samuel Lee | Source: Email
From: Sofia Rossi | To: Samuel Lee | Subject: Supply Chain Update: Task 7.0
Samuel, the high-grade structural steel for the Nexus Bridge is held up at the port. Task 7.0 (Procurement) is Blocked. I anticipate a 4-week delay.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_022.txt',
    'Email',
    '2026-09-08',
    'Samuel Lee, Sarah Chen, Alice Thompson',
    'GSIMS Platform Oversight',
    'Date: 2026-09-08 09:12 AM | Recipients: Samuel Lee, Sarah Chen, Alice Thompson | Source: Email
From: Samuel Lee | To: Sarah Chen, Alice Thompson | Subject: GSIMS Platform Oversight
Sarah, I''d like you to take the lead on the GSIMS Platform Spatial Data Mapping (Task 15.0). Please coordinate with the tech team.',
    encode(sha256('Date: 2026-09-08 09:12 AM | Recipients: Samuel Lee, Sarah Chen, Alice Thompson | Source: Email
From: Samuel Lee | To: Sarah Chen, Alice Thompson | Subject: GSIMS Platform Oversight
Sarah, I''d like you to take the lead on the GSIMS Platform Spatial Data Mapping (Task 15.0). Please coordinate with the tech team.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_023.txt',
    'Email',
    '2026-04-21',
    'Hiroshi Tanaka, David O''Sullivan',
    'RE: Nexus Bridge Soils',
    'Date: 2026-04-21 10:30 AM | Recipients: Hiroshi Tanaka, David O''Sullivan | Source: Email
From: Hiroshi Tanaka | To: David O''Sullivan | Subject: RE: Nexus Bridge Soils
David, the soil density is more variable than expected. I need to extend the Geotechnical Site Assessment (Task 2.0) to an End Date of May 22, 2026.',
    encode(sha256('Date: 2026-04-21 10:30 AM | Recipients: Hiroshi Tanaka, David O''Sullivan | Source: Email
From: Hiroshi Tanaka | To: David O''Sullivan | Subject: RE: Nexus Bridge Soils
David, the soil density is more variable than expected. I need to extend the Geotechnical Site Assessment (Task 2.0) to an End Date of May 22, 2026.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_024.txt',
    'Email',
    '2026-10-20',
    'Daniel Kim, Samuel Lee',
    'Hardware Logistics',
    'Date: 2026-10-20 04:22 PM | Recipients: Daniel Kim, Samuel Lee | Source: Email
From: Daniel Kim | To: Samuel Lee | Subject: Hardware Logistics
The edge computing nodes are stuck in customs. Task 19.0 (5G Node Hardware install) is Blocked until further notice.',
    encode(sha256('Date: 2026-10-20 04:22 PM | Recipients: Daniel Kim, Samuel Lee | Source: Email
From: Daniel Kim | To: Samuel Lee | Subject: Hardware Logistics
The edge computing nodes are stuck in customs. Task 19.0 (5G Node Hardware install) is Blocked until further notice.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_025.txt',
    'Email',
    '2026-11-10',
    'David O''Sullivan, Vikram Singh',
    'Acoustic Barrier Design',
    'Date: 2026-11-10 08:05 AM | Recipients: David O''Sullivan, Vikram Singh | Source: Email
From: David O''Sullivan | To: Vikram Singh | Subject: Acoustic Barrier Design
Vikram, are you handling the Acoustic Barrier Design (Task 21.0)? I need the specs for the rail link interface.',
    encode(sha256('Date: 2026-11-10 08:05 AM | Recipients: David O''Sullivan, Vikram Singh | Source: Email
From: David O''Sullivan | To: Vikram Singh | Subject: Acoustic Barrier Design
Vikram, are you handling the Acoustic Barrier Design (Task 21.0)? I need the specs for the rail link interface.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_026.txt',
    'Email',
    '2027-01-05',
    'Robert Kwok, Samuel Lee',
    'URGENT: Security Protocol',
    'Date: 2027-01-05 09:00 AM | Recipients: Robert Kwok, Samuel Lee | Source: Email
From: Robert Kwok | To: Samuel Lee | Subject: URGENT: Security Protocol
Samuel, we need to add a New Task: "Employee Phishing Simulation" for all staff accessing the 5G Command Centre before Task 25.0 begins.',
    encode(sha256('Date: 2027-01-05 09:00 AM | Recipients: Robert Kwok, Samuel Lee | Source: Email
From: Robert Kwok | To: Samuel Lee | Subject: URGENT: Security Protocol
Samuel, we need to add a New Task: "Employee Phishing Simulation" for all staff accessing the 5G Command Centre before Task 25.0 begins.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_027.txt',
    'Email',
    '2026-10-06',
    'Linda Ng, Kevin Zhang, Sarah Chen',
    'VDC Coordination',
    'Date: 2026-10-06 11:15 AM | Recipients: Linda Ng, Kevin Zhang, Sarah Chen | Source: Email
From: Linda Ng | To: Kevin Zhang, Sarah Chen | Subject: VDC Coordination
To ensure we don''t miss the deadline, both Kevin and Sarah will now be responsible for Task 18.0 (VDC Construction Sequence Simulation).',
    encode(sha256('Date: 2026-10-06 11:15 AM | Recipients: Linda Ng, Kevin Zhang, Sarah Chen | Source: Email
From: Linda Ng | To: Kevin Zhang, Sarah Chen | Subject: VDC Coordination
To ensure we don''t miss the deadline, both Kevin and Sarah will now be responsible for Task 18.0 (VDC Construction Sequence Simulation).'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_028.txt',
    'Email',
    '2026-09-15',
    'Thomas Müller, Sofia Rossi',
    'ETFE Cushion Delivery',
    'Date: 2026-09-15 03:40 PM | Recipients: Thomas Müller, Sofia Rossi | Source: Email
From: Thomas Müller | To: Sofia Rossi | Subject: ETFE Cushion Delivery
Sofia, the ETFE Cushion System (Task 16.0 related) is on backorder. We are officially Blocked on façade assembly for the atrium.',
    encode(sha256('Date: 2026-09-15 03:40 PM | Recipients: Thomas Müller, Sofia Rossi | Source: Email
From: Thomas Müller | To: Sofia Rossi | Subject: ETFE Cushion Delivery
Sofia, the ETFE Cushion System (Task 16.0 related) is on backorder. We are officially Blocked on façade assembly for the atrium.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_029.txt',
    'Email',
    '2026-06-16',
    'Priya Lakshmi, Samuel Lee',
    'Task 9.0 Status',
    'Date: 2026-06-16 01:20 PM | Recipients: Priya Lakshmi, Samuel Lee | Source: Email
From: Priya Lakshmi | To: Samuel Lee | Subject: Task 9.0 Status
Samuel, flooding has damaged the initial irrigation prep. Task 9.0 (Rooftop Garden Design) site prep is Blocked for at least 10 days.',
    encode(sha256('Date: 2026-06-16 01:20 PM | Recipients: Priya Lakshmi, Samuel Lee | Source: Email
From: Priya Lakshmi | To: Samuel Lee | Subject: Task 9.0 Status
Samuel, flooding has damaged the initial irrigation prep. Task 9.0 (Rooftop Garden Design) site prep is Blocked for at least 10 days.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_030.txt',
    'Email',
    '2026-05-12',
    'Amina Al-Farsi, Marcus Wong',
    'URLLC Mapping',
    'Date: 2026-05-12 04:50 PM | Recipients: Amina Al-Farsi, Marcus Wong | Source: Email
From: Amina Al-Farsi | To: Marcus Wong | Subject: URLLC Mapping
Marcus, let''s push the start of Task 5.0 (5G Network Topology) to May 25, 2026, to align with new digital twin sync protocols.',
    encode(sha256('Date: 2026-05-12 04:50 PM | Recipients: Amina Al-Farsi, Marcus Wong | Source: Email
From: Amina Al-Farsi | To: Marcus Wong | Subject: URLLC Mapping
Marcus, let''s push the start of Task 5.0 (5G Network Topology) to May 25, 2026, to align with new digital twin sync protocols.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_031.txt',
    'Email',
    '2026-11-03',
    'Vikram Singh, Samuel Lee',
    'Field Report: Task 20.0',
    'Date: 2026-11-03 08:30 AM | Recipients: Vikram Singh, Samuel Lee | Source: Email
From: Vikram Singh | To: Samuel Lee | Subject: Field Report: Task 20.0
Samuel, soil stability issues post-rain mean Task 20.0 (Hydraulic Stormwater) is Blocked. Expecting a 2-week delay in the South Sector.',
    encode(sha256('Date: 2026-11-03 08:30 AM | Recipients: Vikram Singh, Samuel Lee | Source: Email
From: Vikram Singh | To: Samuel Lee | Subject: Field Report: Task 20.0
Samuel, soil stability issues post-rain mean Task 20.0 (Hydraulic Stormwater) is Blocked. Expecting a 2-week delay in the South Sector.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_032.txt',
    'Email',
    '2026-11-17',
    'Elena Rodriguez, Chloe Dupont',
    'Mandatory Carbon Offset Verification',
    'Date: 2026-11-17 10:00 AM | Recipients: Elena Rodriguez, Chloe Dupont | Source: Email
From: Elena Rodriguez | To: Chloe Dupont | Subject: Mandatory Carbon Offset Verification
Chloe, we must add a New Task: "Carbon Offset Verification (Phase A)" before the final Sustainability Audit (Task 22.0).',
    encode(sha256('Date: 2026-11-17 10:00 AM | Recipients: Elena Rodriguez, Chloe Dupont | Source: Email
From: Elena Rodriguez | To: Chloe Dupont | Subject: Mandatory Carbon Offset Verification
Chloe, we must add a New Task: "Carbon Offset Verification (Phase A)" before the final Sustainability Audit (Task 22.0).'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_033.txt',
    'Email',
    '2026-06-17',
    'Priya Lakshmi, Arjun Mehta',
    'Task 9.0 Status',
    'Date: 2026-06-17 09:15 AM | Recipients: Priya Lakshmi, Arjun Mehta | Source: Email
From: Priya Lakshmi | To: Arjun Mehta | Subject: Task 9.0 Status
Arjun, the design phase for the Rooftop Garden (Task 9.0) remains On Track. We are finalizing the irrigation schematics this week.',
    encode(sha256('Date: 2026-06-17 09:15 AM | Recipients: Priya Lakshmi, Arjun Mehta | Source: Email
From: Priya Lakshmi | To: Arjun Mehta | Subject: Task 9.0 Status
Arjun, the design phase for the Rooftop Garden (Task 9.0) remains On Track. We are finalizing the irrigation schematics this week.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_034.txt',
    'Email',
    '2027-02-02',
    'Samuel Lee, Geoffery Tan, Jessica Low',
    'Claims & Legal Review Oversight',
    'Date: 2027-02-02 02:30 PM | Recipients: Samuel Lee, Geoffery Tan, Jessica Low | Source: Email
From: Samuel Lee | To: Geoffery Tan, Jessica Low | Subject: Claims & Legal Review Oversight
Jessica, I''d like you to take the lead on Task 29.0 (Claims & Legal Liability). Geoffery, please provide her with the files.',
    encode(sha256('Date: 2027-02-02 02:30 PM | Recipients: Samuel Lee, Geoffery Tan, Jessica Low | Source: Email
From: Samuel Lee | To: Geoffery Tan, Jessica Low | Subject: Claims & Legal Review Oversight
Jessica, I''d like you to take the lead on Task 29.0 (Claims & Legal Liability). Geoffery, please provide her with the files.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_035.txt',
    'Email',
    '2026-09-22',
    'Linda Ng, Sarah Chen',
    'RE: MEP Utility Corridor Optimization',
    'Date: 2026-09-22 08:00 AM | Recipients: Linda Ng, Sarah Chen | Source: Email
From: Linda Ng | To: Sarah Chen | Subject: RE: MEP Utility Corridor Optimization
Sarah, I need to move the Start Date for Task 17.0 (MEP Corridor Optimization) from September 21 to September 28, 2026.',
    encode(sha256('Date: 2026-09-22 08:00 AM | Recipients: Linda Ng, Sarah Chen | Source: Email
From: Linda Ng | To: Sarah Chen | Subject: RE: MEP Utility Corridor Optimization
Sarah, I need to move the Start Date for Task 17.0 (MEP Corridor Optimization) from September 21 to September 28, 2026.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_036.txt',
    'Email',
    '2026-08-25',
    'Fatima Zahra, Sofia Rossi',
    'Task 14.0 Component Issues',
    'Date: 2026-08-25 11:20 AM | Recipients: Fatima Zahra, Sofia Rossi | Source: Email
From: Fatima Zahra | To: Sofia Rossi | Subject: Task 14.0 Component Issues
Sofia, the smart-grid inverter modules are stuck. Task 14.0 (Smart Grid Integration) is officially Blocked due to supply chain shortages.',
    encode(sha256('Date: 2026-08-25 11:20 AM | Recipients: Fatima Zahra, Sofia Rossi | Source: Email
From: Fatima Zahra | To: Sofia Rossi | Subject: Task 14.0 Component Issues
Sofia, the smart-grid inverter modules are stuck. Task 14.0 (Smart Grid Integration) is officially Blocked due to supply chain shortages.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_037.txt',
    'Email',
    '2027-01-12',
    'Hassan Meer, Zoe Castellano',
    'Task 26.0 Progress',
    'Date: 2027-01-12 04:00 PM | Recipients: Hassan Meer, Zoe Castellano | Source: Email
From: Hassan Meer | To: Zoe Castellano | Subject: Task 26.0 Progress
Zoe, just confirming the Nightscape Design (Task 26.0) is On Track. Light-spill simulations look excellent.',
    encode(sha256('Date: 2027-01-12 04:00 PM | Recipients: Hassan Meer, Zoe Castellano | Source: Email
From: Hassan Meer | To: Zoe Castellano | Subject: Task 26.0 Progress
Zoe, just confirming the Nightscape Design (Task 26.0) is On Track. Light-spill simulations look excellent.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_038.txt',
    'Email',
    '2026-08-18',
    'Hiroshi Tanaka, Ben Richardson',
    'Sub-surface Inspection',
    'Date: 2026-08-18 08:10 AM | Recipients: Hiroshi Tanaka, Ben Richardson | Source: Email
From: Hiroshi Tanaka | To: Ben Richardson | Subject: Sub-surface Inspection
Ben, we need to add a New Task: "Underwater Drone Piling Inspection" to get clear footage before sign-off on the foundation.',
    encode(sha256('Date: 2026-08-18 08:10 AM | Recipients: Hiroshi Tanaka, Ben Richardson | Source: Email
From: Hiroshi Tanaka | To: Ben Richardson | Subject: Sub-surface Inspection
Ben, we need to add a New Task: "Underwater Drone Piling Inspection" to get clear footage before sign-off on the foundation.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_039.txt',
    'Email',
    '2026-08-04',
    'James Peterson, Samuel Lee',
    'Emergency Access Protocol',
    'Date: 2026-08-04 03:45 PM | Recipients: James Peterson, Samuel Lee | Source: Email
From: James Peterson | To: Samuel Lee | Subject: Emergency Access Protocol
Samuel, the Site Safety Access Protocol (Task 12.0) will be ready "at some point mid-August."',
    encode(sha256('Date: 2026-08-04 03:45 PM | Recipients: James Peterson, Samuel Lee | Source: Email
From: James Peterson | To: Samuel Lee | Subject: Emergency Access Protocol
Samuel, the Site Safety Access Protocol (Task 12.0) will be ready "at some point mid-August."'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_040.txt',
    'Email',
    '2026-10-27',
    'Thomas Müller, Samuel Lee',
    'Retractable Roof Progress',
    'Date: 2026-10-27 10:00 AM | Recipients: Thomas Müller, Samuel Lee | Source: Email
From: Thomas Müller | To: Samuel Lee | Subject: Retractable Roof Progress
Samuel, the Retractable Roof Segment installation (Task 16.0) is On Track. Motor synchronisation tests passed last Friday.',
    encode(sha256('Date: 2026-10-27 10:00 AM | Recipients: Thomas Müller, Samuel Lee | Source: Email
From: Thomas Müller | To: Samuel Lee | Subject: Retractable Roof Progress
Samuel, the Retractable Roof Segment installation (Task 16.0) is On Track. Motor synchronisation tests passed last Friday.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_041.txt',
    'Email',
    '2026-12-15',
    'Kevin Zhang, Samuel Lee',
    'VDC Simulation Update',
    'Date: 2026-12-15 09:30 AM | Recipients: Kevin Zhang, Samuel Lee | Source: Email
From: Kevin Zhang | To: Samuel Lee | Subject: VDC Simulation Update
Samuel, the VDC Construction Sequence Simulation (Task 18.0) is On Track. Clash detection complete for all MEP zones.',
    encode(sha256('Date: 2026-12-15 09:30 AM | Recipients: Kevin Zhang, Samuel Lee | Source: Email
From: Kevin Zhang | To: Samuel Lee | Subject: VDC Simulation Update
Samuel, the VDC Construction Sequence Simulation (Task 18.0) is On Track. Clash detection complete for all MEP zones.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_042.txt',
    'Email',
    '2026-07-20',
    'Rachael Smythe, Samuel Lee',
    'Town Hall Series Confirmation',
    'Date: 2026-07-20 11:00 AM | Recipients: Rachael Smythe, Samuel Lee | Source: Email
From: Rachael Smythe | To: Samuel Lee | Subject: Town Hall Series Confirmation
Samuel, the Public Stakeholder Town Hall Series (Task 11.0) is confirmed On Track for the rescheduled July 27 date.',
    encode(sha256('Date: 2026-07-20 11:00 AM | Recipients: Rachael Smythe, Samuel Lee | Source: Email
From: Rachael Smythe | To: Samuel Lee | Subject: Town Hall Series Confirmation
Samuel, the Public Stakeholder Town Hall Series (Task 11.0) is confirmed On Track for the rescheduled July 27 date.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_043.txt',
    'Email',
    '2026-05-12',
    'Amina Al-Farsi, Robert Kwok',
    '5G Mesh Latency Stress Test',
    'Date: 2026-05-12 11:25 AM | Recipients: Amina Al-Farsi, Robert Kwok | Source: Email
From: Amina Al-Farsi | To: Robert Kwok | Subject: 5G Mesh Latency Stress Test
Robert, I am proposing a New Task: "5G Mesh Latency Stress Test" to validate URLLC thresholds across all node clusters before go-live.',
    encode(sha256('Date: 2026-05-12 11:25 AM | Recipients: Amina Al-Farsi, Robert Kwok | Source: Email
From: Amina Al-Farsi | To: Robert Kwok | Subject: 5G Mesh Latency Stress Test
Robert, I am proposing a New Task: "5G Mesh Latency Stress Test" to validate URLLC thresholds across all node clusters before go-live.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_044.txt',
    'Email',
    '2026-12-01',
    'Arjun Mehta, Samuel Lee',
    'Urban Nexus Masterplan Alignment',
    'Date: 2026-12-01 02:00 PM | Recipients: Arjun Mehta, Samuel Lee | Source: Email
From: Arjun Mehta | To: Samuel Lee | Subject: Urban Nexus Masterplan Alignment
Samuel, the Urban Nexus Masterplan Alignment (Task 23.0) is progressing On Track. Final council submission is scheduled for January 22.',
    encode(sha256('Date: 2026-12-01 02:00 PM | Recipients: Arjun Mehta, Samuel Lee | Source: Email
From: Arjun Mehta | To: Samuel Lee | Subject: Urban Nexus Masterplan Alignment
Samuel, the Urban Nexus Masterplan Alignment (Task 23.0) is progressing On Track. Final council submission is scheduled for January 22.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_045.txt',
    'Email',
    '2026-06-08',
    'Emily Watson, David O''Sullivan',
    'Heritage Vibration Protection',
    'Date: 2026-06-08 03:15 PM | Recipients: Emily Watson, David O''Sullivan | Source: Email
From: Emily Watson | To: David O''Sullivan | Subject: Heritage Vibration Protection
David, the Heritage Site Vibration Protection Strategy (Task 8.0) is On Track. Vibration Isolation Springs have been approved by the heritage authority.',
    encode(sha256('Date: 2026-06-08 03:15 PM | Recipients: Emily Watson, David O''Sullivan | Source: Email
From: Emily Watson | To: David O''Sullivan | Subject: Heritage Vibration Protection
David, the Heritage Site Vibration Protection Strategy (Task 8.0) is On Track. Vibration Isolation Springs have been approved by the heritage authority.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_046.txt',
    'Email',
    '2026-06-02',
    'David O''Sullivan, Arjun Mehta',
    'Public Art Installation',
    'Date: 2026-06-02 11:50 AM | Recipients: David O''Sullivan, Arjun Mehta | Source: Email
From: David O''Sullivan | To: Arjun Mehta | Subject: Public Art Installation
Arjun, we need to include a New Task: "Public Art Installation Structural Review." The sculpture is heavier than initially scoped.',
    encode(sha256('Date: 2026-06-02 11:50 AM | Recipients: David O''Sullivan, Arjun Mehta | Source: Email
From: David O''Sullivan | To: Arjun Mehta | Subject: Public Art Installation
Arjun, we need to include a New Task: "Public Art Installation Structural Review." The sculpture is heavier than initially scoped.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_047.txt',
    'Email',
    '2027-01-19',
    'Omar Bakri, Samuel Lee',
    'Task 27.0 Timeline',
    'Date: 2027-01-19 09:20 AM | Recipients: Omar Bakri, Samuel Lee | Source: Email
From: Omar Bakri | To: Samuel Lee | Subject: Task 27.0 Timeline
Samuel, traffic modeling is taking longer. I need to move the Start Date for Task 27.0 (Transport Flow Simulation) to February 1, 2027.',
    encode(sha256('Date: 2027-01-19 09:20 AM | Recipients: Omar Bakri, Samuel Lee | Source: Email
From: Omar Bakri | To: Samuel Lee | Subject: Task 27.0 Timeline
Samuel, traffic modeling is taking longer. I need to move the Start Date for Task 27.0 (Transport Flow Simulation) to February 1, 2027.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_048.txt',
    'Email',
    '2026-10-19',
    'Ben Richardson, Samuel Lee',
    'Foundation Piling Resumption',
    'Date: 2026-10-19 08:00 AM | Recipients: Ben Richardson, Samuel Lee | Source: Email
From: Ben Richardson | To: Samuel Lee | Subject: Foundation Piling Resumption
Samuel, pumps have cleared the site. Task 13.0 (Foundation Piling) is Blocked until the remediation team clears the area.',
    encode(sha256('Date: 2026-10-19 08:00 AM | Recipients: Ben Richardson, Samuel Lee | Source: Email
From: Ben Richardson | To: Samuel Lee | Subject: Foundation Piling Resumption
Samuel, pumps have cleared the site. Task 13.0 (Foundation Piling) is Blocked until the remediation team clears the area.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_049.txt',
    'Email',
    '2027-04-20',
    'Siti Nurhaliza, Samuel Lee',
    'Task 30.0 Readiness',
    'Date: 2027-04-20 08:00 AM | Recipients: Siti Nurhaliza, Samuel Lee | Source: Email
From: Siti Nurhaliza | To: Samuel Lee | Subject: Task 30.0 Readiness
Samuel, everything for the final Archival & Lock (Task 30.0) is On Track. Folders are pre-organized for the April handover.',
    encode(sha256('Date: 2027-04-20 08:00 AM | Recipients: Siti Nurhaliza, Samuel Lee | Source: Email
From: Siti Nurhaliza | To: Samuel Lee | Subject: Task 30.0 Readiness
Samuel, everything for the final Archival & Lock (Task 30.0) is On Track. Folders are pre-organized for the April handover.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO unstructured_sources
    (file_name, source_type, document_date, participants, subject, raw_content, content_hash)
VALUES (
    'Email_050.txt',
    'Email',
    '2027-02-02',
    'Jessica Low, Samuel Lee',
    'Task 28.0',
    'Date: 2027-02-02 04:55 PM | Recipients: Jessica Low, Samuel Lee | Source: Email
From: Jessica Low | To: Samuel Lee | Subject: Task 28.0
Samuel, the Contract Variation (Task 28.0) is On Track. I''ve incorporated costs for the new drone inspections and carbon verification.',
    encode(sha256('Date: 2027-02-02 04:55 PM | Recipients: Jessica Low, Samuel Lee | Source: Email
From: Jessica Low | To: Samuel Lee | Subject: Task 28.0
Samuel, the Contract Variation (Task 28.0) is On Track. I''ve incorporated costs for the new drone inspections and carbon verification.'::bytea), 'hex')
)
ON CONFLICT (content_hash) DO NOTHING;


-- ---------------------------------------------------------------------------
-- VERIFICATION QUERY
-- Run this immediately after executing the seed to confirm all rows landed.
-- ---------------------------------------------------------------------------
-- SELECT
--     COUNT(*)                                        AS total_rows,
--     COUNT(*) FILTER (WHERE source_type = 'Meeting Minute') AS meeting_minutes,
--     COUNT(*) FILTER (WHERE source_type = 'Email')          AS emails,
--     COUNT(*) FILTER (WHERE processing_status = 'Pending')  AS pending
-- FROM unstructured_sources;
--
-- Expected result:
--   total_rows | meeting_minutes | emails | pending
--   -----------+-----------------+--------+---------
--          50  |       20        |   30   |    50