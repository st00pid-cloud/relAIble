# Executive Summary Generator - Power BI "What Changed" Report

## 📋 Overview

The **Executive Summary Generator** transforms Delta Agent output into executive-friendly "What Changed" summaries formatted for Power BI text cards. Aligned with Surbana Jurong's **"Unlocking Excellence"** value by emphasizing precision, coordination, and specialist team acknowledgment.

### Position in Architecture

```
Extraction Agent → Delta Agent → [EXECUTIVE SUMMARY GENERATOR] → Power BI Dashboard
```

This component takes the technical change log from the Delta Agent and produces:
1. **Power BI Text Card**: Markdown-formatted summary for dashboard display
2. **Dashboard KPIs**: Metrics for gauge/card visuals
3. **Action Items**: Prioritized tasks for leadership
4. **Health Score**: 0-100 project health indicator

---

## 🎯 Core Objectives

### 1. **Precision** (Unlocking Excellence)
- Exact dates, quantified delays (e.g., "28 days", "4 weeks")
- Named owners and specialist teams
- Source evidence tracking
- Confidence scoring visible

### 2. **Coordination** (Team Excellence)
- Highlights cross-functional dependencies
- Flags conflicts requiring alignment
- Acknowledges collaborative resolutions
- Shows integrated planning

### 3. **Actionability** (Excellent Outcomes)
- Clear next steps with priorities (P1, P2, P3, P4)
- Assigned owners for each action
- Deadline expectations ("Within 48hrs", "Next steering meeting")
- Risk mitigation focus

---

## 📐 Output Format

### Power BI Text Card Format

The generator produces markdown-formatted text optimized for Power BI text cards:

```markdown
# SJ Nexus Project: What Changed
📊 Report Date: Aug 20, 2026
🔴 **Project Health: At Risk (55/100)**

## At a Glance
• **18** total updates tracked
• **2** new initiatives proposed
• **4** critical blockers
• **2** coordination issues
• **3** tasks confirmed on track

## Key Highlights
• 🚨 CRITICAL: 4 tasks now BLOCKED across infrastructure and procurement streams
• ✨ 2 new initiatives proposed by specialist teams to strengthen project delivery
• ⚠️ 2 coordination issues flagged, requiring cross-functional resolution
• 📅 6 tasks with revised timelines (avg. 21 days) - detailed mitigation plans attached

## Critical Alerts
• [7.0] Procurement of High-Grade Structural Steel: BLOCKED due to supply chain disruption
• [13.0] Foundation Piling - North Sector: BLOCKED due to environmental conditions
• [19.0] 5G Node Hardware Install: BLOCKED due to supply chain disruption
• [21.0] Acoustic Barrier Design: BLOCKED due to material procurement
• [17.0] MEP Utility Corridor: CONFLICT - Linda Ng vs. David O'Sullivan - requires executive mediation

## Executive Summary
This reporting period captured 18 project updates, including 4 critical items requiring immediate leadership attention. Our specialist teams have maintained meticulous tracking of evolving site conditions and procurement challenges...

## Required Actions
• [P1] Unblock Procurement of High-Grade Structural Steel (Task 7.0) - Escalate to procurement - Within 48hrs
• [P1] Unblock Foundation Piling - North Sector (Task 13.0) - Escalate to operations - Within 48hrs
• [P2] Resolve ownership dispute on MEP Utility Corridor (Task 17.0) - PMO mediation - Within 1 week
• [P3] Review new initiative: Carbon Offset Verification (Elena Rodriguez) - Governance review - Next steering

---
*Unlocking Excellence through precision tracking and specialist coordination*
Generated: 2026-08-20 14:30
```

### JSON Export for Power BI

```json
{
  "report_metadata": {
    "title": "SJ Integrated Urban Nexus - Project Update Summary",
    "generated_at": "2026-08-20T14:30:00",
    "reporting_period": "As of August 20, 2026",
    "format_version": "1.0"
  },
  "text_card_content": "[Full markdown text above]",
  "dashboard_kpis": {
    "total_changes": 18,
    "new_tasks": 2,
    "updates": 14,
    "blockers": 4,
    "conflicts": 2,
    "on_track": 3,
    "requires_approval": 14,
    "health_score": 55,
    "health_status": "At Risk"
  },
  "key_highlights": [...],
  "critical_alerts": [...],
  "action_items": [...],
  "full_narrative": "[Complete narrative]"
}
```

---

## 🔧 Usage

### Basic Usage

```python
from executive_summary_generator import ExecutiveSummaryGenerator

# Input: Delta Agent output (Plan Update Draft)
plan_update_draft = {
    "draft_metadata": {...},
    "summary": {...},
    "critical_items": [...],
    "detailed_change_log": [...]
}

# Initialize generator
generator = ExecutiveSummaryGenerator(plan_update_draft)

# Generate executive summary
summary = generator.generate_executive_summary()

# Access components
print(summary.powerbi_formatted_text)  # For Power BI text card
print(summary.metrics_snapshot)         # For dashboard KPIs
print(summary.key_highlights)           # Top 3-5 highlights
print(summary.action_items)             # Prioritized actions

# Export for Power BI
generator.export_for_powerbi("executive_summary.json")
```

### Integration with Delta Agent

```python
from delta_agent import DeltaAgent
from executive_summary_generator import ExecutiveSummaryGenerator

# Step 1: Delta Agent comparison
delta_agent = DeltaAgent(baseline_tasks)
deltas = delta_agent.compare_tasks(extracted_tasks)
plan_draft = delta_agent.generate_plan_update_draft(deltas)

# Step 2: Executive Summary generation
exec_generator = ExecutiveSummaryGenerator(plan_draft)
summary = exec_generator.generate_executive_summary()

# Step 3: Export for Power BI
exec_generator.export_for_powerbi("powerbi_summary.json")
```

---

## 📊 Key Features

### 1. **Health Score Calculation** (0-100)

**Formula:**
- Start at 100
- Deduct 15 points per blocked task
- Deduct 10 points per conflict
- Deduct 5 points per delay
- Add 5 points per acceleration
- Clamp to 0-100 range

**Health Status:**
- 85-100: 🟢 Excellent
- 70-84: 🟡 Good
- 50-69: 🟡 Fair
- 0-49: 🔴 At Risk

**Example:**
```python
Scenario: 4 blockers, 2 conflicts, 6 delays
Score = 100 - (4×15) - (2×10) - (6×5) = 100 - 60 - 20 - 30 = -10 → 0
Status = At Risk (clamped to 0)
```

### 2. **Change Categorization**

Automatically categorizes changes:
- **new_tasks**: Proposed initiatives not in baseline
- **blocked_tasks**: Tasks with "Blocked" status
- **delayed_tasks**: Date revisions pushing timelines out
- **owner_changes**: Reassignments between team members
- **schedule_accelerations**: Tasks ahead of schedule
- **on_track_confirmations**: Status confirmations
- **conflicts**: Ownership disputes, contradictions

### 3. **Key Highlights Generation**

Priority-ordered highlights (max 5):
1. **Critical blockers** (highest priority)
2. **New strategic initiatives**
3. **Conflicts requiring stakeholder alignment**
4. **Schedule delays** (with quantified impact)
5. **Positive progress** (if room, no critical issues)

**Example Highlights:**
```
🚨 CRITICAL: 4 tasks now BLOCKED across infrastructure and procurement streams
✨ 2 new initiatives proposed by specialist teams to strengthen project delivery
⚠️ Ownership conflict on MEP Utility Corridor needs executive alignment
📅 6 tasks with revised timelines (avg. 21 days) - detailed mitigation plans attached
✅ 3 tasks confirmed ON TRACK, maintaining project momentum
```

### 4. **Critical Alerts**

Specific, actionable alerts with:
- Task ID for traceability
- Task name
- Root cause (extracted from evidence)
- Impact statement

**Format:** `[Task ID] Task Name: Issue - Impact`

**Example:**
```
[7.0] Procurement of High-Grade Structural Steel: BLOCKED due to supply chain disruption - customs clearance delays
[17.0] MEP Utility Corridor Optimization: CONFLICT - Linda Ng vs. David O'Sullivan - requires executive mediation
```

### 5. **Action Items with Prioritization**

**Priority Levels:**
- **[P1]**: Immediate (blockers) - Within 48hrs
- **[P2]**: Urgent (conflicts) - Within 1 week
- **[P3]**: Important (new initiatives) - Next steering meeting
- **[P4]**: Moderate (major delays) - Within 2 weeks

**Format:** `[Priority] Action - Owner/Team - Deadline`

**Example:**
```
[P1] Unblock Procurement of High-Grade Structural Steel (Task 7.0) - Escalate to procurement/operations - Within 48hrs
[P2] Resolve ownership dispute on MEP Utility Corridor (Task 17.0): Linda vs. David - PMO mediation - Within 1 week
[P3] Review and approve new initiative: Carbon Offset Verification (proposed by Elena Rodriguez) - Governance review - Next steering meeting
```

### 6. **Executive Narrative**

Multi-section narrative emphasizing SJ values:

**Section Structure:**
1. **Opening Context**: Total changes, critical count, specialist team acknowledgment
2. **Critical Blockers**: Detailed description with owners and root causes
3. **New Initiatives**: Proposed scope enhancements
4. **Schedule Adjustments**: Validated timeline revisions
5. **Team Coordination**: Ownership transitions and conflicts
6. **Precision Tracking**: Evidence-based decisions emphasis

**SJ Values Language:**
- "specialist teams"
- "meticulous tracking"
- "exact coordination required"
- "maintaining excellence"
- "cross-functional alignment"
- "innovative approach"

---

## 📐 Power BI Integration Guide

### Step 1: Import JSON Data

In Power BI Desktop:
1. Get Data → JSON
2. Select `executive_summary.json`
3. Transform → Expand nested objects

### Step 2: Create Text Card Visual

1. Add visual → Text box
2. Format → Dynamic content
3. Bind to `text_card_content` field
4. Enable markdown rendering

### Step 3: Create KPI Cards

Create card visuals for:
- `health_score` (with conditional formatting)
- `total_changes`
- `blockers`
- `conflicts`
- `new_tasks`

### Step 4: Conditional Formatting

**Health Score Gauge:**
```dax
Health Color = 
SWITCH(
    TRUE(),
    [health_score] >= 85, "#4CAF50",  // Green
    [health_score] >= 70, "#FFC107",  // Yellow
    "#F44336"                          // Red
)
```

**Blocker Alert:**
```dax
Blocker Alert = 
IF([blockers] > 0, 
   "🚨 " & [blockers] & " CRITICAL", 
   "✅ No Blockers"
)
```

### Step 5: Refresh Schedule

Set automatic refresh:
- Frequency: Daily (or after Delta Agent runs)
- Source: Azure Blob Storage / File Share containing JSON exports
- Notifications: Alert on health_score < 70

---

## 🧪 Test Scenarios

The test suite (`test_executive_summary.py`) covers 3 scenarios:

### Scenario 1: Normal Operations
- **Changes**: 8 minor updates
- **Critical Items**: 0
- **Health Score**: ~85-90 (Good/Excellent)
- **Highlights**: Routine progress, minor date adjustments
- **Narrative**: Positive, focused on coordination

### Scenario 2: Crisis Mode
- **Changes**: 18 updates
- **Critical Items**: 6 (4 blockers, 2 conflicts)
- **Health Score**: ~45-55 (At Risk)
- **Highlights**: Multiple critical blockers, urgent interventions needed
- **Narrative**: Action-focused, emphasizes immediate needs

### Scenario 3: Growth Phase
- **Changes**: 12 updates
- **Critical Items**: 0
- **Health Score**: ~75-80 (Good)
- **Highlights**: 5 new initiatives, team evolution
- **Narrative**: Innovation-focused, specialist contributions

### Running Tests

```bash
python test_executive_summary.py
```

**Expected Output:**
- 3 scenarios executed
- Power BI formatted text displayed
- Metrics calculated
- JSON files exported

---

## 🎨 Customization Options

### Adjust Health Score Weights

```python
class ExecutiveSummaryGenerator:
    # Customize penalty/reward values
    BLOCKER_PENALTY = 15       # Default: -15 per blocker
    CONFLICT_PENALTY = 10      # Default: -10 per conflict
    DELAY_PENALTY = 5          # Default: -5 per delay
    ACCELERATION_BONUS = 5     # Default: +5 per acceleration
```

### Modify SJ Values Language

```python
SJ_VALUES_PHRASES = {
    'precision': [
        "with surgical precision",
        "down to the day",
        "meticulously tracked"
    ],
    'excellence': [
        "maintaining excellence",
        "specialist expertise deployed"
    ],
    'coordination': [
        "cross-functional alignment",
        "team synchronization"
    ]
}
```

### Change Text Card Length

```python
POWERBI_MAX_CHARS = 2500  # Adjust for your Power BI setup
```

### Customize Summary Style

```python
from executive_summary_generator import SummaryStyle

# Available styles
summary = generator.generate_executive_summary(
    style=SummaryStyle.CONCISE     # Brief bullet points
    # style=SummaryStyle.DETAILED  # Full narrative (default)
    # style=SummaryStyle.METRICS   # Statistics-focused
    # style=SummaryStyle.ACTIONABLE # Focus on actions
)
```

---

## 📈 Sample Outputs

### Example 1: Crisis Mode Output

```
# SJ Nexus Project: What Changed
📊 Report Date: Aug 20, 2026
🔴 **Project Health: At Risk (55/100)**

## At a Glance
• **18** total updates tracked
• **2** new initiatives proposed
• **4** critical blockers
• **2** coordination issues

## Key Highlights
• 🚨 CRITICAL: 4 tasks now BLOCKED across infrastructure and procurement streams
• ✨ NEW INITIATIVE: 'Carbon Offset Verification (Phase A)' proposed to enhance sustainability
• ⚠️ COORDINATION REQUIRED: Ownership conflict on MEP Utility Corridor needs alignment

## Critical Alerts
• [7.0] Procurement Steel: BLOCKED due to customs - 4-week delay
• [13.0] Foundation Piling: BLOCKED due to monsoon flooding
• [17.0] MEP Corridor: CONFLICT (Linda vs. David) - mediation needed

## Required Actions
• [P1] Unblock steel procurement - Escalate to supply chain - 48hrs
• [P1] Unblock foundation piling - Deploy pumps, wait for weather - 2 weeks
• [P2] Resolve MEP ownership - PMO mediation - 1 week
```

### Example 2: Normal Operations Output

```
# SJ Nexus Project: What Changed
📊 Report Date: Jul 15, 2026
🟢 **Project Health: Excellent (88/100)**

## At a Glance
• **8** total updates tracked
• **0** critical blockers
• **3** tasks confirmed on track

## Key Highlights
• ✅ 3 tasks confirmed ON TRACK, maintaining project momentum
• 📅 Minor timeline adjustments (avg. 5 days) for quality assurance
• 👤 2 ownership transitions to optimize specialist allocation

## Executive Summary
This reporting period reflects 8 project updates demonstrating ongoing coordination and proactive risk management aligned with SJ's commitment to excellence...
```

---

## 🔗 Related Documentation

- **Delta Agent**: See `DELTA_AGENT_README.md`
- **Extraction Agent**: See `extraction_agent_system_prompt.md`
- **System Architecture**: See `/mnt/project/System_Architecture_relAIble.pdf`
- **SJ Company Values**: See `/mnt/project/company_values.txt`

---

## 🛠️ Troubleshooting

### Issue: Text card appears truncated in Power BI

**Cause**: Content exceeds Power BI text card limits  
**Solution**: Reduce `POWERBI_MAX_CHARS` or enable scrolling in Power BI visual settings

### Issue: Health score always shows "At Risk"

**Cause**: Penalty weights too high for project context  
**Solution**: Adjust `BLOCKER_PENALTY`, `CONFLICT_PENALTY`, `DELAY_PENALTY` values

### Issue: Highlights missing critical blockers

**Cause**: Priority ordering logic needs adjustment  
**Solution**: Review `_generate_key_highlights()` method, ensure blockers are first priority

### Issue: Narrative too long/too short

**Cause**: Style setting or content volume  
**Solution**: Use `style=SummaryStyle.CONCISE` for brevity, or `DETAILED` for full context

---

## 👥 Contributors

**Project**: SJ Integrated Urban Nexus  
**Client**: Surbana Jurong Infrastructure Team  
**Challenge**: Code Without Barriers - Microsoft Foundry Track  
**Team**: relAIble AI Solutions

---

## 📄 Key Principles

1. **Precision First**: Always quantify (days, weeks, specific dates)
2. **Name the Specialists**: Acknowledge owners and teams
3. **Evidence-Based**: Reference source documents
4. **Action-Oriented**: Every summary ends with clear next steps
5. **SJ Values**: Language reflects Unlocking Excellence, coordination, innovation

---

**Last Updated**: 2026-04-02  
**Version**: 1.0  
**Status**: Ready for Power BI Integration

**Alignment Check:**
- ✅ Unlocking Excellence: Precision tracking, specialist acknowledgment
- ✅ Limitless Imagination: Highlights innovations, new initiatives
- ✅ Solutions at Scale: Handles 50+ changes, multi-stakeholder coordination
- ✅ Future Legacy: Creates permanent executive record with evidence trails
