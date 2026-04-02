# Delta Agent - Plan Update Draft Generator

## Delta Agent
- Second component in SJ's AI-powered project management pipeline.
- Compares task updates extracted by the Extraction Agent against the PostgreSQL baseline WBS, detecting New tasks, Updates, and Conflicts. 
- The output is a "Plan Update Draft" ready for governance layer review.
- Acts as the **comparison engine** that transforms raw extractions into actionable change reports.

```
Extraction Agent → [DELTA AGENT] → Priority Agent → Governance Layer → Power BI
```

The Delta Agent 

## Core Responsibilities

### 1. **Task Matching**
Match extracted tasks to baseline tasks using:
- Task ID extraction (e.g., "Task 7.0" → `7.0`)
- Exact task name matching
- Normalized fuzzy matching (lowercase, punctuation-stripped)

### 2. **Change Detection**
Identify changes in:
- **Due Dates**: New end dates, delays, schedule compressions
- **Owners**: Reassignments, conflicts, unassigned tasks
- **Status**: Blocked, Delayed, At Risk, On Track transitions
- **New Tasks**: Proposals not in baseline WBS

### 3. **Conflict Resolution**
Flag conflicts requiring human intervention:
- Ownership disputes (multiple claimants)
- Unassigned/NULL owners
- Vague/TBD dates
- Contradictory status reports

### 4. **Output Generation**
Produce structured "Plan Update Draft" with:
- Summary statistics
- Critical items (Blocked tasks, conflicts)
- Approval queue (flagged changes)
- Auto-approvable changes (high confidence, low risk)
- Detailed change log with evidence trails

---

## Comparison Logic

### Rule 1: Task Exists in Baseline, Due Date Differs → `UPDATE` (Date Revision)

```python
Baseline:  Task 7.0, End Date: 2026-08-28
Extracted: Task 7.0, Due Date: 2026-09-25

Result:
  Change Type: DATE_REVISION
  Field Changed: Due_Date
  Baseline Value: 2026-08-28
  Extracted Value: 2026-09-25
  Approval Reason: "Due date revised by +28 days"
  Requires Approval: True (delay > 14 days)
```

### Rule 2: Task Exists, Owner Differs → `UPDATE` (Owner Reassignment)

```python
Baseline:  Task 15.0, Owner: Alice Thompson
Extracted: Task 15.0, Owner: Sarah Chen

Result:
  Change Type: OWNER_REASSIGNMENT
  Field Changed: Owner
  Baseline Value: Alice Thompson
  Extracted Value: Sarah Chen
  Approval Reason: "Owner reassignment from Alice Thompson to Sarah Chen"
  Requires Approval: False (confidence 0.95)
```

### Rule 3: Task Exists, Status Differs → `UPDATE` (Status Change)

```python
Baseline:  Task 13.0, Status: Not Started
Extracted: Task 13.0, Status: Blocked

Result:
  Change Type: STATUS_CHANGE
  Field Changed: Status
  Baseline Value: Not Started
  Extracted Value: Blocked
  Approval Reason: "Status changed to 'Blocked' - CRITICAL STATUS"
  Requires Approval: True (critical status)
```

### Rule 4: TaskID is New → `NEW`

```python
Baseline:  [No matching task]
Extracted: "Carbon Offset Verification (Phase A)"

Result:
  Change Type: NEW
  Task ID: None
  Task Name: Carbon Offset Verification (Phase A)
  Approval Reason: "New task proposed - not in baseline WBS"
  Requires Approval: True (all new tasks flagged)
```

### Rule 5: Owner is Unassigned/NULL → `CONFLICT`

```python
Baseline:  Task 14.0, Owner: Fatima Zahra
Extracted: Task 14.0, Owner: NULL

Result:
  Change Type: CONFLICT
  Field Changed: Owner
  Baseline Value: Fatima Zahra
  Extracted Value: UNASSIGNED
  Approval Reason: "Owner is unassigned or unclear in source communication"
  Requires Approval: True
```

### Rule 6: Ownership Dispute → `CONFLICT`

```python
Baseline:  Task 17.0, Owner: Linda Ng
Extracted: Task 17.0, Owner: "CONFLICT: Linda Ng vs. David O'Sullivan"

Result:
  Change Type: CONFLICT
  Field Changed: Owner
  Extracted Value: CONFLICT: Linda Ng vs. David O'Sullivan
  Approval Reason: "Ownership conflict detected. Requires stakeholder alignment."
  Requires Approval: True
```

---

## 🔧 Usage

### Basic Usage

```python
from delta_agent import DeltaAgent

# Load baseline tasks from PostgreSQL
baseline_tasks = [
    {
        "Task ID": "7.0",
        "Task Name": "Procurement of High-Grade Structural Steel",
        "Owner": "Sofia Rossi",
        "Start Date": "2026-06-01",
        "End Date": "2026-08-28",
        "Current Status": "Not Started"
    },
    # ... more tasks
]

# Initialize Delta Agent
agent = DeltaAgent(baseline_tasks)

# Extracted tasks from Extraction Agent
extracted_tasks = [
    {
        "task_name": "Procurement of High-Grade Structural Steel",
        "owner": "Sofia Rossi",
        "due_date": "2026-09-25",
        "status": "Blocked",
        "evidence_quote": "Task 7.0 is Blocked at the port. 4-week delay.",
        "confidence_score": 0.95,
        "needs_clarification": False,
        "clarification_reason": None,
        "source_metadata": {
            "document_id": "Email_021",
            "date": "2026-06-01 08:45 AM",
            "participants": ["Sofia Rossi", "Samuel Lee"],
            "source_type": "Email"
        }
    }
]

# Compare and detect changes
deltas = agent.compare_tasks(extracted_tasks)

# Generate Plan Update Draft
draft = agent.generate_plan_update_draft(deltas)

# Export for Power BI
agent.export_for_powerbi(deltas, "plan_update_draft.json")
```

### Advanced: Load from CSV

```python
import csv

def load_baseline_from_csv(csv_path: str):
    tasks = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tasks.append(row)
    return tasks

baseline = load_baseline_from_csv("SJ_Nexus_Baseline.csv")
agent = DeltaAgent(baseline)
```

---

## Output Schema: Plan Update Draft

```json
{
  "draft_metadata": {
    "generated_at": "2026-06-01T14:30:00",
    "total_changes_detected": 12,
    "requires_approval_count": 8,
    "auto_approvable_count": 4,
    "critical_items_count": 3,
    "change_type_breakdown": {
      "New": 2,
      "Date Revision": 4,
      "Status Change": 3,
      "Owner Reassignment": 2,
      "Conflict": 1
    }
  },
  "summary": {
    "new_tasks": 2,
    "updates": 9,
    "conflicts": 1,
    "no_changes": 0
  },
  "critical_items": [
    {
      "task_id": "13.0",
      "task_name": "Foundation Piling - North Sector Execution",
      "issue": "Status changed to 'Blocked' - CRITICAL STATUS",
      "evidence": "Foundation Piling is Blocked due to monsoon rains...",
      "detected_at": "2026-08-18T10:00:00"
    }
  ],
  "requires_approval": [
    {
      "change_type": "Date Revision",
      "task_id": "7.0",
      "task_name": "Procurement of High-Grade Structural Steel",
      "field_changed": "Due_Date",
      "baseline_value": "2026-08-28",
      "extracted_value": "2026-09-25",
      "evidence_quote": "Task 7.0 is Blocked. 4-week delay.",
      "confidence_score": 0.95,
      "requires_approval": true,
      "approval_reason": "Due date revised by +28 days",
      "source_metadata": {...},
      "detected_at": "2026-06-01T14:30:00"
    }
  ],
  "auto_approvable": [...],
  "detailed_change_log": [...]
}
```

### Key Sections

#### 1. `draft_metadata`
High-level statistics for dashboard display:
- Total changes detected
- How many need approval vs. auto-approvable
- Critical item count
- Breakdown by change type

#### 2. `summary`
Simplified counts for executives:
- New tasks
- Updates (all types combined)
- Conflicts

#### 3. `critical_items`
**Immediate attention required:**
- Blocked tasks
- Conflicts
- High-risk changes

#### 4. `requires_approval`
Changes flagged for human review before database update:
- Low confidence extractions (< 0.8)
- Large date shifts (> 14 days)
- Ownership conflicts
- All new tasks
- Critical status changes (Blocked, Delayed, At Risk)

#### 5. `auto_approvable`
High-confidence, low-risk changes:
- Minor date adjustments (< 14 days, confidence > 0.9)
- Status confirmations ("On Track" → "On Track")
- Expected owner reassignments (confidence > 0.8)

#### 6. `detailed_change_log`
Complete audit trail with evidence quotes for every detected change.

---

## Approval Logic

### When `requires_approval = True`

**Automatic Triggers:**
1. **Confidence < 0.8**: Extraction uncertainty
2. **New Tasks**: Not in baseline WBS
3. **Conflicts**: Ownership disputes, contradictory info
4. **Critical Status**: "Blocked", "Delayed", "At Risk"
5. **Large Delays**: Date shift > 14 days
6. **NULL/Vague Data**: TBD dates, unassigned owners
7. **Inferred Fields**: Owner/dates inferred from context

### When `requires_approval = False`

**Auto-Approvable:**
1. Confidence ≥ 0.9
2. Small date adjustments (≤ 14 days)
3. Non-critical status changes
4. Explicit owner reassignments (high confidence)

**Example Auto-Approvable:**
```json
{
  "change_type": "Date Revision",
  "task_id": "2.0",
  "baseline_value": "2026-05-15",
  "extracted_value": "2026-05-22",
  "confidence_score": 1.0,
  "requires_approval": false,
  "approval_reason": "Due date revised by +7 days"
}
```

---

## Test Coverage

The test suite (`test_delta_agent.py`) includes 15 scenarios:

| Test ID | Scenario | Change Type | Critical? |
|---------|----------|-------------|-----------|
| TC-DELTA-001 | Task 7.0 Blocked + 4-week delay | Date Revision + Status Change | ✅ Yes (Blocked) |
| TC-DELTA-002 | Task 13.0 Monsoon blocker | Status Change | ✅ Yes (Blocked) |
| TC-DELTA-003 | Task 2.0 Date extension (+7 days) | Date Revision | ❌ No |
| TC-DELTA-004 | Task 11.0 Town Hall reschedule | Date Revision | ❌ No |
| TC-DELTA-005 | Task 17.0 Ownership conflict | Conflict | ✅ Yes (Dispute) |
| TC-DELTA-006 | New: Carbon Offset Verification | New Task | ❌ No |
| TC-DELTA-007 | Task 15.0 Owner → Sarah Chen | Owner Reassignment | ❌ No |
| TC-DELTA-008 | Task 5.0 Start date push | Date Revision | ❌ No |
| TC-DELTA-009 | Task 19.0 Blocked (customs) | Status Change | ✅ Yes (Blocked) |
| TC-DELTA-010 | Task 21.0 Blocked (material) | Status Change | ✅ Yes (Blocked) |
| TC-DELTA-011 | Task 29.0 Owner → Jessica Low | Owner Reassignment | ❌ No |
| TC-DELTA-012 | Task 27.0 Start delay | Date Revision | ❌ No |
| TC-DELTA-013 | Task 18.0 Co-ownership | No Change (same owner) | ❌ No |
| TC-DELTA-014 | Task 9.0 Blocked (flooding) | Status Change | ✅ Yes (Blocked) |
| TC-DELTA-015 | New: 5G Latency Stress Test | New Task | ❌ No |

### Running Tests

```bash
python test_delta_agent.py
```

Expected output:
- 15 scenarios executed
- ~20+ delta detections
- 6-8 critical items flagged
- Plan Update Draft JSON generated

---

## Integration Points

### Input: From Extraction Agent

**Required Fields:**
- `task_name`: String
- `owner`: String (may contain "CONFLICT:", "INFERRED:", "NULL")
- `due_date`: ISO 8601 date or "NULL"/"TBD"/"VAGUE:"
- `status`: Enum (On Track, Blocked, Delayed, etc.)
- `evidence_quote`: Verbatim source text
- `confidence_score`: Float 0.0-1.0
- `needs_clarification`: Boolean
- `clarification_reason`: String or null
- `source_metadata`: Object with document_id, date, participants, source_type

### Output: To Governance Layer

**Plan Update Draft JSON** containing:
- Summary statistics
- Critical items for immediate review
- Approval queue
- Auto-approvable changes
- Complete change log

### Output: To Power BI

**Formatted for visualization:**
- Gantt chart updates (date changes)
- "What Changed" summaries (human-readable)
- Dashboard metrics (total changes, critical count)

---

## Configuration Options

### Approval Thresholds

Customize in `DeltaAgent` class:

```python
class DeltaAgent:
    # Confidence threshold for auto-approval
    CONFIDENCE_THRESHOLD = 0.8
    
    # Date shift threshold (days) for flagging
    DATE_SHIFT_THRESHOLD = 14
    
    # Critical statuses that require approval
    CRITICAL_STATUSES = ["Blocked", "Delayed", "At Risk"]
```

### Matching Strategy

Adjust fuzzy matching in `_normalize_task_name()`:

```python
def _normalize_task_name(self, name: str) -> str:
    """Customize normalization rules"""
    return name.lower() \
               .replace('-', ' ') \
               .replace('&', 'and') \
               .replace('phase 1', 'phase i') \
               .strip()
```

---

## Performance Metrics

### Expected Performance

- **Precision**: >95% for matched tasks
- **Recall**: >90% for change detection
- **False Positive Rate**: <5% for conflicts
- **Processing Time**: <100ms for 30 tasks

### Monitoring

Track these metrics:
1. **Match Rate**: % of extracted tasks matched to baseline
2. **Approval Rate**: % of changes requiring human review
3. **Critical Rate**: % of changes flagged as critical
4. **Confidence Distribution**: Histogram of confidence scores

---
---

##  Related Documentation

- **Extraction Agent**: See `extraction_agent_system_prompt.md`
- **Priority Agent**: (Next in pipeline - to be developed)
- **System Architecture**: See `/mnt/project/System_Architecture_relAIble.pdf`
- **Baseline WBS**: Sample at document index 18

---

## Troubleshooting

### Issue: No matches found for extracted tasks

**Cause**: Task name doesn't match baseline format  
**Solution**: Check `_normalize_task_name()` logic, add custom normalization rules

### Issue: Too many changes flagged for approval

**Cause**: Thresholds too strict  
**Solution**: Adjust `CONFIDENCE_THRESHOLD` or `DATE_SHIFT_THRESHOLD`

### Issue: Ownership conflicts not detected

**Cause**: Extraction Agent not marking with "CONFLICT:" prefix  
**Solution**: Review Extraction Agent system prompt, ensure conflict detection rules

### Issue: Date calculations incorrect

**Cause**: Date format mismatch (expecting YYYY-MM-DD)  
**Solution**: Validate date formats in extracted tasks, add parsing fallbacks

---

## Usage
Designed for internal project management operations. The comparison logic and change detection rules may be adapted for similar infrastructure tracking systems. Every change must have evidence trail. Never update baseline without human approval for high-risk changes.

---

