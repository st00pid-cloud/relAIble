"""
SJ Project Planner - Delta Agent Module

This module implements the comparison logic between Extraction Agent output
and the PostgreSQL baseline_tasks table. It detects New tasks, Updates,
and Conflicts, outputting a "Plan Update Draft" for human review.

Author: relAIble Challenge Team
Date: 2026-04-02
Version: 1.0
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class ChangeType(Enum):
    """Types of changes detected by the Delta Agent"""
    NEW = "New"
    UPDATE = "Update"
    CONFLICT = "Conflict"
    NO_CHANGE = "No Change"
    OWNER_REASSIGNMENT = "Owner Reassignment"
    STATUS_CHANGE = "Status Change"
    DATE_REVISION = "Date Revision"


class FieldType(Enum):
    """Fields that can be compared"""
    DUE_DATE = "Due_Date"
    OWNER = "Owner"
    STATUS = "Status"
    TASK_NAME = "Task_Name"
    START_DATE = "Start_Date"


@dataclass
class BaselineTask:
    """Represents a task from the baseline WBS (PostgreSQL)"""
    task_id: str
    task_name: str
    owner: str
    start_date: Optional[str]
    end_date: str
    current_status: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaselineTask':
        """Create BaselineTask from database row"""
        return cls(
            task_id=data.get('Task ID', data.get('task_id', '')),
            task_name=data.get('Task Name', data.get('task_name', '')),
            owner=data.get('Owner', data.get('owner', '')),
            start_date=data.get('Start Date', data.get('start_date')),
            end_date=data.get('End Date', data.get('end_date', '')),
            current_status=data.get('Current Status', data.get('current_status', ''))
        )


@dataclass
class ExtractedTask:
    """Represents a task from Extraction Agent output"""
    task_name: str
    owner: str
    due_date: str
    status: str
    evidence_quote: str
    confidence_score: float
    needs_clarification: bool
    clarification_reason: Optional[str]
    source_metadata: Dict[str, Any]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExtractedTask':
        """Create ExtractedTask from Extraction Agent JSON"""
        return cls(
            task_name=data['task_name'],
            owner=data['owner'],
            due_date=data['due_date'],
            status=data['status'],
            evidence_quote=data['evidence_quote'],
            confidence_score=data['confidence_score'],
            needs_clarification=data['needs_clarification'],
            clarification_reason=data.get('clarification_reason'),
            source_metadata=data['source_metadata']
        )


@dataclass
class DeltaDetection:
    """Represents a detected change between baseline and extraction"""
    change_type: ChangeType
    task_id: Optional[str]  # None for new tasks
    task_name: str
    field_changed: Optional[FieldType]
    baseline_value: Optional[str]
    extracted_value: str
    evidence_quote: str
    confidence_score: float
    requires_approval: bool
    approval_reason: str
    source_metadata: Dict[str, Any]
    detected_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'change_type': self.change_type.value,
            'task_id': self.task_id,
            'task_name': self.task_name,
            'field_changed': self.field_changed.value if self.field_changed else None,
            'baseline_value': self.baseline_value,
            'extracted_value': self.extracted_value,
            'evidence_quote': self.evidence_quote,
            'confidence_score': self.confidence_score,
            'requires_approval': self.requires_approval,
            'approval_reason': self.approval_reason,
            'source_metadata': self.source_metadata,
            'detected_at': self.detected_at
        }


class DeltaAgent:
    """
    Core Delta Agent: Compares Extraction Agent output against baseline tasks.
    
    Responsibilities:
    1. Match extracted tasks to baseline tasks (by task name/ID)
    2. Detect changes: New tasks, Updates (date/owner/status), Conflicts
    3. Generate "Plan Update Draft" for governance layer review
    4. Flag high-risk changes for mandatory approval
    """
    
    def __init__(self, baseline_tasks: List[Dict[str, Any]]):
        """
        Initialize Delta Agent with baseline WBS from PostgreSQL.
        
        Args:
            baseline_tasks: List of task dictionaries from database
        """
        self.baseline_tasks = [BaselineTask.from_dict(t) for t in baseline_tasks]
        self.task_index = self._build_task_index()
        
    def _build_task_index(self) -> Dict[str, BaselineTask]:
        """Build lookup index for fast task matching"""
        index = {}
        
        # Index by Task ID (e.g., "1.0", "7.0", "13.0")
        for task in self.baseline_tasks:
            if task.task_id:
                index[task.task_id] = task
        
        # Also index by normalized task name for fuzzy matching
        for task in self.baseline_tasks:
            normalized_name = self._normalize_task_name(task.task_name)
            if normalized_name not in index:  # Don't overwrite ID matches
                index[normalized_name] = task
        
        return index
    
    def _normalize_task_name(self, name: str) -> str:
        """Normalize task name for matching (lowercase, remove special chars)"""
        return name.lower().replace('-', ' ').replace('&', 'and').strip()
    
    def _find_baseline_task(self, extracted_task: ExtractedTask) -> Optional[BaselineTask]:
        """
        Find matching baseline task for an extracted task.
        
        Matching strategy:
        1. Try to extract Task ID from task_name (e.g., "Task 7.0: Procurement...")
        2. Try exact task name match
        3. Try normalized (fuzzy) task name match
        
        Args:
            extracted_task: Task from Extraction Agent
            
        Returns:
            Matching BaselineTask or None if not found (new task)
        """
        # Strategy 1: Extract Task ID from name
        import re
        task_id_match = re.search(r'Task (\d+\.\d+)', extracted_task.task_name)
        if task_id_match:
            task_id = task_id_match.group(1)
            if task_id in self.task_index:
                return self.task_index[task_id]
        
        # Strategy 2: Exact name match
        if extracted_task.task_name in self.task_index:
            return self.task_index[extracted_task.task_name]
        
        # Strategy 3: Normalized fuzzy match
        normalized_name = self._normalize_task_name(extracted_task.task_name)
        if normalized_name in self.task_index:
            return self.task_index[normalized_name]
        
        # No match found - this is a new task
        return None
    
    def _detect_owner_change(
        self, 
        baseline: BaselineTask, 
        extracted: ExtractedTask
    ) -> Optional[DeltaDetection]:
        """Detect if owner has changed or is in conflict"""
        
        # Handle CONFLICT markers from Extraction Agent
        if extracted.owner.startswith("CONFLICT:"):
            return DeltaDetection(
                change_type=ChangeType.CONFLICT,
                task_id=baseline.task_id,
                task_name=extracted.task_name,
                field_changed=FieldType.OWNER,
                baseline_value=baseline.owner,
                extracted_value=extracted.owner,
                evidence_quote=extracted.evidence_quote,
                confidence_score=extracted.confidence_score,
                requires_approval=True,
                approval_reason=f"Ownership conflict detected: {extracted.clarification_reason}",
                source_metadata=extracted.source_metadata,
                detected_at=datetime.now().isoformat()
            )
        
        # Handle NULL/unassigned owner
        if extracted.owner in ["NULL", "", None]:
            return DeltaDetection(
                change_type=ChangeType.CONFLICT,
                task_id=baseline.task_id,
                task_name=extracted.task_name,
                field_changed=FieldType.OWNER,
                baseline_value=baseline.owner,
                extracted_value="UNASSIGNED",
                evidence_quote=extracted.evidence_quote,
                confidence_score=extracted.confidence_score,
                requires_approval=True,
                approval_reason="Owner is unassigned or unclear in source communication",
                source_metadata=extracted.source_metadata,
                detected_at=datetime.now().isoformat()
            )
        
        # Handle INFERRED owners (lower confidence)
        if extracted.owner.startswith("INFERRED:"):
            actual_owner = extracted.owner.replace("INFERRED:", "").strip()
            if actual_owner != baseline.owner:
                return DeltaDetection(
                    change_type=ChangeType.OWNER_REASSIGNMENT,
                    task_id=baseline.task_id,
                    task_name=extracted.task_name,
                    field_changed=FieldType.OWNER,
                    baseline_value=baseline.owner,
                    extracted_value=actual_owner,
                    evidence_quote=extracted.evidence_quote,
                    confidence_score=extracted.confidence_score,
                    requires_approval=True,
                    approval_reason=f"Owner inferred (not explicit). Confidence: {extracted.confidence_score}",
                    source_metadata=extracted.source_metadata,
                    detected_at=datetime.now().isoformat()
                )
        
        # Normal owner change
        if extracted.owner != baseline.owner:
            return DeltaDetection(
                change_type=ChangeType.OWNER_REASSIGNMENT,
                task_id=baseline.task_id,
                task_name=extracted.task_name,
                field_changed=FieldType.OWNER,
                baseline_value=baseline.owner,
                extracted_value=extracted.owner,
                evidence_quote=extracted.evidence_quote,
                confidence_score=extracted.confidence_score,
                requires_approval=extracted.confidence_score < 0.8,
                approval_reason=f"Owner reassignment from {baseline.owner} to {extracted.owner}",
                source_metadata=extracted.source_metadata,
                detected_at=datetime.now().isoformat()
            )
        
        return None
    
    def _detect_date_change(
        self,
        baseline: BaselineTask,
        extracted: ExtractedTask
    ) -> Optional[DeltaDetection]:
        """Detect if due date has changed"""
        
        # Handle vague/TBD dates
        if extracted.due_date in ["NULL", "TBD", "", None] or extracted.due_date.startswith("VAGUE:"):
            return DeltaDetection(
                change_type=ChangeType.UPDATE,
                task_id=baseline.task_id,
                task_name=extracted.task_name,
                field_changed=FieldType.DUE_DATE,
                baseline_value=baseline.end_date,
                extracted_value=extracted.due_date,
                evidence_quote=extracted.evidence_quote,
                confidence_score=extracted.confidence_score,
                requires_approval=True,
                approval_reason=f"Due date is vague or TBD: {extracted.clarification_reason}",
                source_metadata=extracted.source_metadata,
                detected_at=datetime.now().isoformat()
            )
        
        # Handle CONFLICT dates
        if extracted.due_date.startswith("CONFLICT:"):
            return DeltaDetection(
                change_type=ChangeType.CONFLICT,
                task_id=baseline.task_id,
                task_name=extracted.task_name,
                field_changed=FieldType.DUE_DATE,
                baseline_value=baseline.end_date,
                extracted_value=extracted.due_date,
                evidence_quote=extracted.evidence_quote,
                confidence_score=extracted.confidence_score,
                requires_approval=True,
                approval_reason=f"Multiple conflicting dates mentioned: {extracted.clarification_reason}",
                source_metadata=extracted.source_metadata,
                detected_at=datetime.now().isoformat()
            )
        
        # Normal date comparison
        if extracted.due_date != baseline.end_date:
            # Calculate delay in days
            try:
                baseline_date = datetime.strptime(baseline.end_date, "%Y-%m-%d")
                extracted_date = datetime.strptime(extracted.due_date, "%Y-%m-%d")
                delay_days = (extracted_date - baseline_date).days
                delay_str = f"{delay_days:+d} days" if delay_days != 0 else "same day"
            except:
                delay_str = "unknown"
            
            return DeltaDetection(
                change_type=ChangeType.DATE_REVISION,
                task_id=baseline.task_id,
                task_name=extracted.task_name,
                field_changed=FieldType.DUE_DATE,
                baseline_value=baseline.end_date,
                extracted_value=extracted.due_date,
                evidence_quote=extracted.evidence_quote,
                confidence_score=extracted.confidence_score,
                requires_approval=extracted.confidence_score < 0.9 or abs(delay_days) > 14,
                approval_reason=f"Due date revised by {delay_str} (from {baseline.end_date} to {extracted.due_date})",
                source_metadata=extracted.source_metadata,
                detected_at=datetime.now().isoformat()
            )
        
        return None
    
    def _detect_status_change(
        self,
        baseline: BaselineTask,
        extracted: ExtractedTask
    ) -> Optional[DeltaDetection]:
        """Detect if task status has changed"""
        
        # Handle CONFLICT status
        if extracted.status.startswith("CONFLICT:"):
            return DeltaDetection(
                change_type=ChangeType.CONFLICT,
                task_id=baseline.task_id,
                task_name=extracted.task_name,
                field_changed=FieldType.STATUS,
                baseline_value=baseline.current_status,
                extracted_value=extracted.status,
                evidence_quote=extracted.evidence_quote,
                confidence_score=extracted.confidence_score,
                requires_approval=True,
                approval_reason=f"Status conflict detected: {extracted.clarification_reason}",
                source_metadata=extracted.source_metadata,
                detected_at=datetime.now().isoformat()
            )
        
        # NULL status
        if extracted.status in ["NULL", "", None]:
            return None  # Skip NULL statuses - not enough info to update
        
        # Normal status change
        if extracted.status != baseline.current_status:
            # High-priority status changes (require immediate attention)
            critical_statuses = ["Blocked", "Delayed", "At Risk"]
            is_critical = extracted.status in critical_statuses
            
            return DeltaDetection(
                change_type=ChangeType.STATUS_CHANGE,
                task_id=baseline.task_id,
                task_name=extracted.task_name,
                field_changed=FieldType.STATUS,
                baseline_value=baseline.current_status,
                extracted_value=extracted.status,
                evidence_quote=extracted.evidence_quote,
                confidence_score=extracted.confidence_score,
                requires_approval=is_critical or extracted.confidence_score < 0.8,
                approval_reason=f"Status changed from '{baseline.current_status}' to '{extracted.status}'" + 
                               (" - CRITICAL STATUS" if is_critical else ""),
                source_metadata=extracted.source_metadata,
                detected_at=datetime.now().isoformat()
            )
        
        return None
    
    def compare_tasks(
        self,
        extracted_tasks: List[Dict[str, Any]]
    ) -> List[DeltaDetection]:
        """
        Main comparison function: Compares extracted tasks against baseline.
        
        Logic:
        - If TaskID exists but fields differ → mark as 'Update' (Date Revision, Status Change, Owner Reassignment)
        - If TaskID is new → mark as 'New'
        - If Owner is unassigned/conflict → mark as 'Conflict'
        - Multiple changes in same task → multiple DeltaDetection objects
        
        Args:
            extracted_tasks: List of task dictionaries from Extraction Agent
            
        Returns:
            List of DeltaDetection objects representing all detected changes
        """
        deltas = []
        
        for extracted_dict in extracted_tasks:
            extracted = ExtractedTask.from_dict(extracted_dict)
            baseline = self._find_baseline_task(extracted)
            
            # Case 1: NEW TASK (not in baseline)
            if baseline is None:
                deltas.append(DeltaDetection(
                    change_type=ChangeType.NEW,
                    task_id=None,
                    task_name=extracted.task_name,
                    field_changed=None,
                    baseline_value=None,
                    extracted_value=extracted.task_name,
                    evidence_quote=extracted.evidence_quote,
                    confidence_score=extracted.confidence_score,
                    requires_approval=True,  # All new tasks require approval
                    approval_reason=f"New task proposed: '{extracted.task_name}'. Not in baseline WBS.",
                    source_metadata=extracted.source_metadata,
                    detected_at=datetime.now().isoformat()
                ))
                continue
            
            # Case 2: EXISTING TASK - Check for changes
            
            # Check owner change/conflict
            owner_delta = self._detect_owner_change(baseline, extracted)
            if owner_delta:
                deltas.append(owner_delta)
            
            # Check date change
            date_delta = self._detect_date_change(baseline, extracted)
            if date_delta:
                deltas.append(date_delta)
            
            # Check status change
            status_delta = self._detect_status_change(baseline, extracted)
            if status_delta:
                deltas.append(status_delta)
            
            # If no changes detected, optionally log as NO_CHANGE (for audit trail)
            if not (owner_delta or date_delta or status_delta):
                # Uncomment below to track "no change" confirmations
                # deltas.append(DeltaDetection(
                #     change_type=ChangeType.NO_CHANGE,
                #     task_id=baseline.task_id,
                #     task_name=extracted.task_name,
                #     field_changed=None,
                #     baseline_value=None,
                #     extracted_value=None,
                #     evidence_quote=extracted.evidence_quote,
                #     confidence_score=extracted.confidence_score,
                #     requires_approval=False,
                #     approval_reason="No changes detected - confirmation only",
                #     source_metadata=extracted.source_metadata,
                #     detected_at=datetime.now().isoformat()
                # ))
                pass
        
        return deltas
    
    def generate_plan_update_draft(
        self,
        deltas: List[DeltaDetection],
        include_no_changes: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a "Plan Update Draft" for governance layer review.
        
        Structure:
        - Summary statistics
        - Changes requiring approval (flagged items)
        - Auto-approvable changes (high confidence, low risk)
        - Detailed change log
        
        Args:
            deltas: List of detected changes
            include_no_changes: Whether to include NO_CHANGE items in output
            
        Returns:
            Structured JSON draft for Power BI and human review
        """
        # Separate by approval requirement
        requires_approval = [d for d in deltas if d.requires_approval]
        auto_approvable = [d for d in deltas if not d.requires_approval]
        
        # Count by change type
        change_type_counts = {}
        for delta in deltas:
            change_type = delta.change_type.value
            change_type_counts[change_type] = change_type_counts.get(change_type, 0) + 1
        
        # Identify critical items (Blocked status, conflicts)
        critical_items = [
            d for d in deltas 
            if d.change_type == ChangeType.CONFLICT or 
               (d.extracted_value and "Blocked" in str(d.extracted_value))
        ]
        
        draft = {
            "draft_metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_changes_detected": len(deltas),
                "requires_approval_count": len(requires_approval),
                "auto_approvable_count": len(auto_approvable),
                "critical_items_count": len(critical_items),
                "change_type_breakdown": change_type_counts
            },
            "summary": {
                "new_tasks": change_type_counts.get("New", 0),
                "updates": sum([
                    change_type_counts.get("Date Revision", 0),
                    change_type_counts.get("Status Change", 0),
                    change_type_counts.get("Owner Reassignment", 0)
                ]),
                "conflicts": change_type_counts.get("Conflict", 0),
                "no_changes": change_type_counts.get("No Change", 0)
            },
            "critical_items": [
                {
                    "task_id": d.task_id,
                    "task_name": d.task_name,
                    "issue": d.approval_reason,
                    "evidence": d.evidence_quote,
                    "detected_at": d.detected_at
                }
                for d in critical_items
            ],
            "requires_approval": [d.to_dict() for d in requires_approval],
            "auto_approvable": [d.to_dict() for d in auto_approvable],
            "detailed_change_log": [d.to_dict() for d in deltas]
        }
        
        return draft
    
    def export_for_powerbi(
        self,
        deltas: List[DeltaDetection],
        output_path: str = "plan_update_draft_powerbi.json"
    ) -> str:
        """
        Export delta detections in Power BI-friendly format.
        
        Args:
            deltas: List of detected changes
            output_path: Where to save the JSON file
            
        Returns:
            Path to saved file
        """
        draft = self.generate_plan_update_draft(deltas)
        
        # Add Power BI specific formatting
        powerbi_data = {
            "dataset_version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "plan_update_draft": draft,
            "powerbi_visuals": {
                "gantt_chart_updates": self._format_for_gantt(deltas),
                "what_changed_summary": self._format_what_changed(deltas)
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(powerbi_data, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def _format_for_gantt(self, deltas: List[DeltaDetection]) -> List[Dict[str, Any]]:
        """Format date revisions for Gantt chart visualization"""
        gantt_updates = []
        
        for delta in deltas:
            if delta.change_type == ChangeType.DATE_REVISION:
                gantt_updates.append({
                    "task_id": delta.task_id,
                    "task_name": delta.task_name,
                    "old_end_date": delta.baseline_value,
                    "new_end_date": delta.extracted_value,
                    "status": delta.extracted_value if delta.field_changed == FieldType.STATUS else None,
                    "is_delayed": self._is_delayed(delta.baseline_value, delta.extracted_value)
                })
        
        return gantt_updates
    
    def _format_what_changed(self, deltas: List[DeltaDetection]) -> List[Dict[str, Any]]:
        """Format human-readable 'What Changed' summary"""
        summaries = []
        
        for delta in deltas:
            if delta.change_type == ChangeType.NEW:
                summary = f"🆕 New task added: {delta.task_name}"
            elif delta.change_type == ChangeType.CONFLICT:
                summary = f"⚠️ Conflict: {delta.approval_reason}"
            elif delta.change_type == ChangeType.DATE_REVISION:
                summary = f"📅 Date changed: {delta.task_name} ({delta.baseline_value} → {delta.extracted_value})"
            elif delta.change_type == ChangeType.STATUS_CHANGE:
                summary = f"📊 Status updated: {delta.task_name} → {delta.extracted_value}"
            elif delta.change_type == ChangeType.OWNER_REASSIGNMENT:
                summary = f"👤 Owner reassigned: {delta.task_name} ({delta.baseline_value} → {delta.extracted_value})"
            else:
                summary = f"Changed: {delta.task_name}"
            
            summaries.append({
                "task_id": delta.task_id,
                "summary": summary,
                "evidence": delta.evidence_quote[:100] + "..." if len(delta.evidence_quote) > 100 else delta.evidence_quote,
                "requires_approval": delta.requires_approval,
                "confidence": delta.confidence_score,
                "detected_at": delta.detected_at
            })
        
        return summaries
    
    def _is_delayed(self, baseline_date: str, extracted_date: str) -> bool:
        """Check if new date is later than baseline (delay)"""
        try:
            baseline = datetime.strptime(baseline_date, "%Y-%m-%d")
            extracted = datetime.strptime(extracted_date, "%Y-%m-%d")
            return extracted > baseline
        except:
            return False


# ============================================================================
# EXAMPLE USAGE & TESTING
# ============================================================================

def load_baseline_from_csv(csv_path: str = "SJ_Nexus_Baseline.csv") -> List[Dict[str, Any]]:
    """Load baseline tasks from CSV file"""
    import csv
    
    tasks = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tasks.append(row)
    
    return tasks


def example_usage():
    """Demonstrate Delta Agent with sample data"""
    
    # Sample baseline (from SJ_Nexus_Baseline.csv)
    baseline_tasks = [
        {
            "Task ID": "7.0",
            "Task Name": "Procurement of High-Grade Structural Steel",
            "Owner": "Sofia Rossi",
            "Start Date": "2026-06-01",
            "End Date": "2026-08-28",
            "Current Status": "Not Started"
        },
        {
            "Task ID": "13.0",
            "Task Name": "Foundation Piling - North Sector Execution",
            "Owner": "Ben Richardson",
            "Start Date": "2026-08-17",
            "End Date": "2026-12-18",
            "Current Status": "Not Started"
        },
        {
            "Task ID": "2.0",
            "Task Name": "Geotechnical Site Assessment (Nexus Bridge)",
            "Owner": "Hiroshi Tanaka",
            "Start Date": "2026-04-20",
            "End Date": "2026-05-15",
            "Current Status": "Not Started"
        }
    ]
    
    # Sample extracted tasks (from Extraction Agent)
    extracted_tasks = [
        # Task 7.0 - Blocked with delay
        {
            "task_name": "Procurement of High-Grade Structural Steel",
            "owner": "Sofia Rossi",
            "due_date": "2026-09-25",  # Delayed by 4 weeks
            "status": "Blocked",
            "evidence_quote": "the high-grade structural steel is held up at the port. Task 7.0 is Blocked. I anticipate a 4-week delay.",
            "confidence_score": 0.95,
            "needs_clarification": False,
            "clarification_reason": None,
            "source_metadata": {
                "document_id": "Email_021",
                "date": "2026-06-01 08:45 AM",
                "participants": ["Sofia Rossi", "Samuel Lee"],
                "source_type": "Email"
            }
        },
        # Task 13.0 - Blocked (status change)
        {
            "task_name": "Foundation Piling - North Sector Execution",
            "owner": "Ben Richardson",
            "due_date": "2026-12-18",  # Same date
            "status": "Blocked",
            "evidence_quote": "Ben reported that Foundation Piling (Task 13.0) is Blocked due to monsoon rains.",
            "confidence_score": 1.0,
            "needs_clarification": False,
            "clarification_reason": None,
            "source_metadata": {
                "document_id": "Snippet_001",
                "date": "2026-08-18 10:00 AM",
                "participants": ["Samuel Lee", "Ben Richardson", "David O'Sullivan"],
                "source_type": "Meeting Minute"
            }
        },
        # Task 2.0 - Date revision
        {
            "task_name": "Geotechnical Site Assessment (Nexus Bridge)",
            "owner": "Hiroshi Tanaka",
            "due_date": "2026-05-22",  # Extended by 7 days
            "status": "On Track",
            "evidence_quote": "I need to extend the Geotechnical Site Assessment (Task 2.0) to an End Date of May 22, 2026.",
            "confidence_score": 1.0,
            "needs_clarification": False,
            "clarification_reason": None,
            "source_metadata": {
                "document_id": "Email_023",
                "date": "2026-04-21 10:30 AM",
                "participants": ["Hiroshi Tanaka", "David O'Sullivan"],
                "source_type": "Email"
            }
        },
        # NEW TASK - Carbon Offset Verification
        {
            "task_name": "Carbon Offset Verification (Phase A)",
            "owner": "INFERRED: Elena Rodriguez",
            "due_date": "NULL",
            "status": "Not Started",
            "evidence_quote": "we must add a New Task: 'Carbon Offset Verification (Phase A)' before the final Sustainability Audit.",
            "confidence_score": 0.70,
            "needs_clarification": True,
            "clarification_reason": "New task proposed - not in baseline WBS. Owner inferred. No due date specified.",
            "source_metadata": {
                "document_id": "Email_032",
                "date": "2026-11-17 10:00 AM",
                "participants": ["Elena Rodriguez", "Chloe Dupont"],
                "source_type": "Email"
            }
        }
    ]
    
    # Initialize Delta Agent
    agent = DeltaAgent(baseline_tasks)
    
    # Compare tasks
    deltas = agent.compare_tasks(extracted_tasks)
    
    # Generate Plan Update Draft
    draft = agent.generate_plan_update_draft(deltas)
    
    # Print results
    print("=" * 80)
    print("PLAN UPDATE DRAFT - DELTA AGENT OUTPUT")
    print("=" * 80)
    print(json.dumps(draft, indent=2))
    
    # Export for Power BI
    output_file = agent.export_for_powerbi(deltas)
    print(f"\n✅ Exported to: {output_file}")
    
    return draft, deltas


if __name__ == "__main__":
    example_usage()
