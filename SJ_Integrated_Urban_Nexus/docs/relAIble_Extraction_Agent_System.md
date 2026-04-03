# relAIble: Extraction Agent System

## 📋 Overview
**Extraction Agent** 
- first component for the AI-powered project management system
- converts unstructured project communications into structured JSON data that feeds into the project tracking pipeline.

### System Architecture Context

```
┌─────────────────────────────────────────────────────────────────┐
│                      INGESTION LAYER                             │
│  Azure AI Search indexing raw text files (meetings, emails)     │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ORCHESTRATION LAYER                            │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │ EXTRACTION AGENT │→ │   DELTA AGENT    │→ │ PRIORITY     │  │
│  │  (LLM-based)     │  │  (Comparison)    │  │  AGENT       │  │
│  │                  │  │                  │  │              │  │
│  │ Parses text →    │  │ Compares vs.     │  │ Re-ranks by  │  │
│  │ JSON extractions │  │ PostgreSQL       │  │ urgency      │  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     GOVERNANCE LAYER                             │
│        "Review-before-update" workflow for flagged items         │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                       OUTPUT LAYER                               │
│  Power BI: Real-time Gantt Charts + "What Changed" Summaries    │
└─────────────────────────────────────────────────────────────────┘
```
**This repository focuses on the EXTRACTION AGENT component.**
---

## Purpose & Goals

The Extraction Agent must:

1. **Parse** unstructured text into structured task updates
2. **Extract** 9 required fields: Task Name, Owner, Due Date, Status, Evidence Quote, Confidence Score, Clarification Flag, Clarification Reason, Source Metadata
3. **Detect** conflicts, ambiguities, and new task proposals
4. **Flag** items that need human review before database update
5. **Maintain** evidence trail for audit and traceability

### Importance

Large infrastructure projects has multiple, unstructured functions. The Extraction Agent automates the first step which is converting conversations into database-ready updates.
- **50+ stakeholders** communicate via meetings, emails, chat
- **30+ concurrent tasks** with interdependencies
- **Vague language** ("ASAP", "end of summer", "whenever ready") is common
- **Conflicts** arise when multiple owners claim same task
- **Manual tracking** is error-prone and time-consuming

## Function

### Input Format

The agent receives text chunks from various sources: Meeting Notes, Emails and Chat Messages.

**Meeting Notes:**
```
Date: 2026-08-18 10:00 AM | Attendees: Samuel Lee, Ben Richardson | Source: Meeting Minute
**Snippet 001: Weekly Progress Review**
* Discussion: Ben reported that Foundation Piling (Task 13.0) is Blocked due to monsoon rains.
```

**Emails:**
```
From: Sofia Rossi | To: Samuel Lee | Subject: Task 7.0 Update
The structural steel is held up at the port. Task 7.0 is Blocked. I anticipate a 4-week delay.
```

**Chat Messages:**
```
[10:23 AM] Marcus Wong: @Sarah, can you take the lead on Task 15.0 (GSIMS Mapping)?
```

### Output Schema

For each extractable task update, the agent returns:

```json
{
  "task_name": "Procurement of High-Grade Structural Steel",
  "owner": "Sofia Rossi",
  "due_date": "2026-09-25",
  "status": "Blocked",
  "evidence_quote": "the structural steel is held up at the port. Task 7.0 is Blocked. I anticipate a 4-week delay.",
  "confidence_score": 0.95,
  "needs_clarification": false,
  "clarification_reason": null,
  "source_metadata": {
    "document_id": "Email_021",
    "date": "2026-06-01 08:45 AM",
    "participants": ["Sofia Rossi", "Samuel Lee"],
    "source_type": "Email"
  }
}
```

### Key Features

#### 1. **Conflict Detection**
When multiple stakeholders claim ownership:
```json
{
  "owner": "CONFLICT: Linda Ng vs. David O'Sullivan",
  "needs_clarification": true,
  "clarification_reason": "Both Linda Ng and David O'Sullivan claim responsibility for Task 17.0."
}
```

#### 2. **Vague Date Handling**
Phrases like "sometime after monsoon season":
```json
{
  "due_date": "TBD",
  "confidence_score": 0.5,
  "needs_clarification": true,
  "clarification_reason": "Due date is weather-dependent ('after monsoon season'). Requires specific date."
}
```

#### 3. **New Task Proposals**
When tasks not in baseline are mentioned:
```json
{
  "task_name": "5G Mesh Latency Stress Test",
  "owner": "INFERRED: Amina Al-Farsi",
  "status": "Not Started",
  "needs_clarification": true,
  "clarification_reason": "New task proposed - not in baseline WBS. Requires approval."
}
```

#### 4. **Evidence Trail**
Every extraction includes verbatim quote:
```json
{
  "evidence_quote": "Ben reported that Foundation Piling (Task 13.0) is Blocked due to monsoon rains."
}
```
This ensures traceability and audit compliance.

---

## 🧪 Test Cases

The test suite (`extraction_agent_test_suite.py`) covers:

| Test ID | Scenario | Key Challenge |
|---------|----------|---------------|
| TC001 | Explicit Blocked Status | Straightforward extraction |
| TC002 | Vague Timeline | "after monsoon season" → needs clarification |
| TC003 | Ownership Conflict | Two people claiming same task |
| TC004 | New Task Proposal | Not in baseline WBS |
| TC005 | Date Change | Explicit date revision |
| TC006 | Multiple Owners | Co-ownership structure |
| TC007 | Dependency-Based Date | "whenever North Sector is ready" |
| TC008 | Status Confirmation | "On Track" verification |
| TC009 | No Extractable Info | Noise filtering (company picnic discussion) |
| TC010 | Blocked Task | Environmental blocker (flooding) |

### Running the Tests

```bash
python extraction_agent_test_suite.py
```

This displays each test case with:
- Input text
- Expected JSON output
- Key extraction features explained

---

## 📐 Design Principles

### 1. **Accuracy Over Speed**
Better to flag for human review than propagate errors into the database.

### 2. **Evidence-Based Extraction**
Every claim must be traceable to a verbatim quote from the source text.

### 3. **Conservative Inference**
When inferring missing information:
- Mark as `"INFERRED: [Value]"` with lower confidence score
- Flag for clarification if confidence < 0.7

### 4. **Conflict-Aware**
Detect and explicitly label contradictions rather than arbitrarily choosing one version.

### 5. **Noise Rejection**
Return an empty array rather than fabricating extractions from irrelevant text.

---

## Integration with Downstream Agents

### Delta Agent (Next in Pipeline)
- Compares extracted JSON against PostgreSQL baseline (`SJ_Nexus_Baseline.csv`)
- Detects: New tasks, Status changes, Date revisions, Owner changes
- Outputs: "What Changed" report for Power BI

### Priority Agent
- Re-ranks tasks based on:
  - Urgency (Blocked > Delayed > At Risk > On Track)
  - Dependencies (critical path analysis)
  - Stakeholder escalations

### Governance Layer
- Human reviewers see items where `needs_clarification = true`
- Can approve, reject, or request more info
- Approved items update PostgreSQL baseline

---

## Implementation Notes

### LLM Requirements
- Model: GPT-4, Claude Opus, or equivalent
- Context window: 8K+ tokens (for long meeting transcripts)
- Function calling: Optional (can be pure text-in/JSON-out)

### Prompt Engineering Strategy
The system prompt is structured as:
1. **Role Definition** (who you are, what you do)
2. **Output Schema** (9 required fields with detailed rules)
3. **Extraction Logic** (8 decision rules for edge cases)
4. **Examples** (5 detailed examples showing expected behavior)
5. **Error Handling** (what to do when information is missing/conflicting)

This structure ensures:
- Consistency across different input types
- Clear handling of ambiguous cases
- Traceability through evidence quotes

### Personas Integration
The system prompt references `Project_Personas.json` which contains:
- 30 stakeholder profiles with communication styles
- Technical entity definitions (URLLC, GSIMS, BIM, etc.)
- Project-specific jargon glossary

This helps the agent:
- Recognize names and roles automatically
- Interpret domain-specific language
- Infer context from communication patterns

---




## Reference Documentation

- **SJ Company Values**: See `/mnt/project/company_values.txt`
- **Case Studies**: See `/mnt/project/case_study_summary_relAIble.pdf`
- **System Architecture**: See `/mnt/project/System_Architecture_relAIble.pdf`
- **Baseline WBS**: See documents index 18 (SJ_Nexus_Baseline.csv)
- **Ground Truth**: See documents index 47 (validation/ground_truth.json)


**Core Values Alignment:**
-  **Unlocking Excellence**: Precise, auditable extractions
-  **Limitless Imagination**: Intelligent inference from partial data
-  **Solutions at Scale**: Handles 50+ stakeholders, 30+ tasks
- **Future Legacy**: Creates permanent, traceable project records

---

## Contact & Support

For questions about this agent:
- Technical Implementation: See `extraction_agent_system_prompt.md`
- Testing: Run `extraction_agent_test_suite.py`
- Integration: Refer to System Architecture diagram above

**Next Steps:**
1. Review system prompt for completeness
2. Run test suite to validate logic
3. Integrate with Azure AI Search (ingestion)
4. Connect to Delta Agent (downstream)
5. Set up Governance UI for flagged items

---

The prompt engineering techniques and schema design may be adapted for similar infrastructure tracking use cases. Always maintain evidence trail. Never compromise on traceability.

