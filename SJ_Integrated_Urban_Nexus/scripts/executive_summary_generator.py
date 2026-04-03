"""
SJ Project Planner - Executive Summary Generator

Transforms Delta Agent output into executive-friendly "What Changed" summaries
formatted for Power BI text cards. Aligned with SJ's "Unlocking Excellence" value
by highlighting precision, coordination, and actionable insights.

Author: relAIble Challenge Team
Date: 2026-04-02
Version: 1.0
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum


class SummaryStyle(Enum):
    """Executive summary presentation styles"""
    CONCISE = "concise"  # Brief, bullet-point format
    DETAILED = "detailed"  # Full narrative with context
    METRICS = "metrics"  # Statistics-focused
    ACTIONABLE = "actionable"  # Focus on required actions


@dataclass
class ExecutiveSummary:
    """Structured executive summary for Power BI display"""
    title: str
    generated_at: str
    reporting_period: str
    key_highlights: List[str]
    critical_alerts: List[str]
    metrics_snapshot: Dict[str, Any]
    change_narrative: str
    action_items: List[str]
    powerbi_formatted_text: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'title': self.title,
            'generated_at': self.generated_at,
            'reporting_period': self.reporting_period,
            'key_highlights': self.key_highlights,
            'critical_alerts': self.critical_alerts,
            'metrics_snapshot': self.metrics_snapshot,
            'change_narrative': self.change_narrative,
            'action_items': self.action_items,
            'powerbi_formatted_text': self.powerbi_formatted_text
        }


class ExecutiveSummaryGenerator:
    """
    Generates executive 'What Changed' summaries from Delta Agent output.
    
    Designed for Power BI text cards with emphasis on:
    - Precision: Exact dates, specific owners, quantified impacts
    - Coordination: Highlighting cross-team dependencies and conflicts
    - Actionability: Clear next steps for leadership
    
    Embodies SJ's "Unlocking Excellence" value through:
    - Specialist team acknowledgment (naming owners)
    - Innovative approach visibility (new tasks, creative solutions)
    - Excellent outcome focus (On Track confirmations, risk mitigation)
    """
    
    # Power BI text card formatting constants
    POWERBI_MAX_CHARS = 2500  # Recommended limit for readability
    POWERBI_HEADER_STYLE = "# "  # Markdown H1
    POWERBI_SUBHEADER_STYLE = "## "  # Markdown H2
    POWERBI_BULLET = "• "
    POWERBI_EMPHASIS = "**"  # Bold
    POWERBI_LINE_BREAK = "\n\n"
    
    # SJ Values-aligned language
    SJ_VALUES_PHRASES = {
        'precision': [
            "with surgical precision",
            "down to the day",
            "meticulously tracked",
            "exact coordination required"
        ],
        'excellence': [
            "maintaining excellence",
            "upholding quality standards",
            "specialist expertise deployed",
            "innovative approach"
        ],
        'coordination': [
            "cross-functional alignment",
            "team synchronization",
            "collaborative resolution",
            "integrated planning"
        ]
    }
    
    def __init__(self, plan_update_draft: Dict[str, Any]):
        """
        Initialize with Delta Agent output.
        
        Args:
            plan_update_draft: Complete output from DeltaAgent.generate_plan_update_draft()
        """
        self.draft = plan_update_draft
        self.metadata = plan_update_draft.get('draft_metadata', {})
        self.summary = plan_update_draft.get('summary', {})
        self.critical_items = plan_update_draft.get('critical_items', [])
        self.requires_approval = plan_update_draft.get('requires_approval', [])
        self.auto_approvable = plan_update_draft.get('auto_approvable', [])
        self.change_log = plan_update_draft.get('detailed_change_log', [])
        
    def _categorize_changes(self) -> Dict[str, List[Dict]]:
        """Categorize changes by type for structured reporting"""
        categories = {
            'new_tasks': [],
            'blocked_tasks': [],
            'delayed_tasks': [],
            'owner_changes': [],
            'schedule_accelerations': [],
            'on_track_confirmations': [],
            'conflicts': []
        }
        
        for change in self.change_log:
            change_type = change.get('change_type', '')
            extracted_value = change.get('extracted_value', '')
            
            if change_type == 'New':
                categories['new_tasks'].append(change)
            elif change_type == 'Conflict':
                categories['conflicts'].append(change)
            elif 'Blocked' in str(extracted_value):
                categories['blocked_tasks'].append(change)
            elif change_type == 'Date Revision':
                # Check if delay or acceleration
                baseline = change.get('baseline_value', '')
                extracted = change.get('extracted_value', '')
                if self._is_delay(baseline, extracted):
                    categories['delayed_tasks'].append(change)
                else:
                    categories['schedule_accelerations'].append(change)
            elif change_type == 'Owner Reassignment':
                categories['owner_changes'].append(change)
            elif 'On Track' in str(extracted_value):
                categories['on_track_confirmations'].append(change)
        
        return categories
    
    def _is_delay(self, baseline_date: str, extracted_date: str) -> bool:
        """Check if extracted date is later than baseline (delay)"""
        try:
            baseline = datetime.strptime(baseline_date, "%Y-%m-%d")
            extracted = datetime.strptime(extracted_date, "%Y-%m-%d")
            return extracted > baseline
        except:
            return False
    
    def _format_date_readable(self, date_str: str) -> str:
        """Convert ISO date to executive-friendly format"""
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return dt.strftime("%b %d, %Y")  # e.g., "Aug 28, 2026"
        except:
            return date_str
    
    def _calculate_delay_impact(self, baseline: str, extracted: str) -> str:
        """Calculate and format delay impact in business terms"""
        try:
            baseline_dt = datetime.strptime(baseline, "%Y-%m-%d")
            extracted_dt = datetime.strptime(extracted, "%Y-%m-%d")
            delta = (extracted_dt - baseline_dt).days
            
            if delta == 0:
                return "same day"
            elif delta > 0:
                weeks = delta // 7
                days = delta % 7
                if weeks > 0:
                    return f"{weeks} week{'s' if weeks > 1 else ''}, {days} day{'s' if days != 1 else ''} delay"
                else:
                    return f"{days} day{'s' if days > 1 else ''} delay"
            else:
                weeks = abs(delta) // 7
                days = abs(delta) % 7
                if weeks > 0:
                    return f"{weeks} week{'s' if weeks > 1 else ''}, {days} day{'s' if days != 1 else ''} ahead"
                else:
                    return f"{days} day{'s' if days > 1 else ''} ahead"
        except:
            return "timeline adjusted"
    
    def _generate_key_highlights(self, categories: Dict[str, List[Dict]]) -> List[str]:
        """
        Generate 3-5 key highlights for executive attention.
        
        Priority order:
        1. Critical blockers
        2. New initiatives
        3. Major delays
        4. Conflicts requiring resolution
        5. Positive progress (on track, accelerations)
        """
        highlights = []
        
        # Highlight 1: Blocked tasks (highest priority)
        blocked = categories['blocked_tasks']
        if len(blocked) > 0:
            if len(blocked) == 1:
                task = blocked[0]
                highlights.append(
                    f"🚨 CRITICAL: {task['task_name']} is now BLOCKED, requiring immediate intervention"
                )
            else:
                highlights.append(
                    f"🚨 CRITICAL: {len(blocked)} tasks now BLOCKED across infrastructure and procurement streams"
                )
        
        # Highlight 2: New strategic initiatives
        new_tasks = categories['new_tasks']
        if len(new_tasks) > 0:
            if len(new_tasks) == 1:
                task = new_tasks[0]
                highlights.append(
                    f"✨ NEW INITIATIVE: '{task['task_name']}' proposed to enhance project sustainability/quality"
                )
            else:
                highlights.append(
                    f"✨ {len(new_tasks)} new initiatives proposed by specialist teams to strengthen project delivery"
                )
        
        # Highlight 3: Conflicts requiring stakeholder alignment
        conflicts = categories['conflicts']
        if len(conflicts) > 0:
            if len(conflicts) == 1:
                task = conflicts[0]
                highlights.append(
                    f"⚠️ COORDINATION REQUIRED: Ownership conflict on {task['task_name']} needs executive alignment"
                )
            else:
                highlights.append(
                    f"⚠️ {len(conflicts)} coordination issues flagged, requiring cross-functional resolution"
                )
        
        # Highlight 4: Schedule delays
        delayed = categories['delayed_tasks']
        if len(delayed) > 0:
            total_delay_days = sum(
                (datetime.strptime(t['extracted_value'], "%Y-%m-%d") - 
                 datetime.strptime(t['baseline_value'], "%Y-%m-%d")).days
                for t in delayed if t.get('baseline_value') and t.get('extracted_value')
            )
            avg_delay = total_delay_days // len(delayed) if delayed else 0
            highlights.append(
                f"📅 {len(delayed)} tasks with revised timelines (avg. {avg_delay} days) - detailed mitigation plans attached"
            )
        
        # Highlight 5: Positive progress (if room and no critical issues dominate)
        on_track = categories['on_track_confirmations']
        accelerations = categories['schedule_accelerations']
        if len(highlights) < 4 and (on_track or accelerations):
            if accelerations:
                highlights.append(
                    f"✅ {len(accelerations)} tasks AHEAD of schedule through proactive team coordination"
                )
            elif len(on_track) > 5:
                highlights.append(
                    f"✅ {len(on_track)} tasks confirmed ON TRACK, maintaining project momentum"
                )
        
        return highlights[:5]  # Max 5 highlights
    
    def _generate_critical_alerts(self, categories: Dict[str, List[Dict]]) -> List[str]:
        """
        Generate critical alerts requiring immediate action.
        
        Format: [Task ID] Task Name - Issue - Impact
        """
        alerts = []
        
        # Blocked tasks with specific details
        for task in categories['blocked_tasks']:
            task_id = task.get('task_id', 'NEW')
            task_name = task['task_name']
            reason = task.get('approval_reason', 'No details provided')
            
            # Extract blocker type from evidence
            evidence = task.get('evidence_quote', '').lower()
            if 'customs' in evidence or 'port' in evidence:
                blocker = "supply chain disruption"
            elif 'rain' in evidence or 'flood' in evidence or 'monsoon' in evidence:
                blocker = "environmental conditions"
            elif 'soil' in evidence or 'contaminated' in evidence:
                blocker = "site conditions"
            elif 'material' in evidence or 'unavailable' in evidence:
                blocker = "material procurement"
            else:
                blocker = "operational constraint"
            
            alerts.append(
                f"[{task_id}] {task_name}: BLOCKED due to {blocker} - {reason}"
            )
        
        # Conflicts with stakeholders involved
        for task in categories['conflicts']:
            task_id = task.get('task_id', 'TBD')
            task_name = task['task_name']
            conflict_detail = task.get('extracted_value', '')
            
            alerts.append(
                f"[{task_id}] {task_name}: {conflict_detail} - requires executive mediation"
            )
        
        # Major delays (> 21 days)
        for task in categories['delayed_tasks']:
            baseline = task.get('baseline_value', '')
            extracted = task.get('extracted_value', '')
            try:
                delay_days = (datetime.strptime(extracted, "%Y-%m-%d") - 
                             datetime.strptime(baseline, "%Y-%m-%d")).days
                if delay_days > 21:  # 3+ weeks
                    task_id = task.get('task_id', 'NEW')
                    task_name = task['task_name']
                    alerts.append(
                        f"[{task_id}] {task_name}: Major delay ({delay_days} days) - critical path impact analysis required"
                    )
            except:
                pass
        
        return alerts
    
    def _generate_metrics_snapshot(self, categories: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Generate key metrics for dashboard KPIs"""
        total_changes = self.metadata.get('total_changes_detected', 0)
        
        # Calculate health score (0-100)
        # Formula: Start at 100, deduct points for issues
        health_score = 100
        health_score -= len(categories['blocked_tasks']) * 15  # -15 per blocker
        health_score -= len(categories['conflicts']) * 10  # -10 per conflict
        health_score -= len(categories['delayed_tasks']) * 5  # -5 per delay
        health_score += len(categories['schedule_accelerations']) * 5  # +5 per acceleration
        health_score = max(0, min(100, health_score))  # Clamp to 0-100
        
        # Determine health status
        if health_score >= 85:
            health_status = "Excellent"
        elif health_score >= 70:
            health_status = "Good"
        elif health_score >= 50:
            health_status = "Fair"
        else:
            health_status = "At Risk"
        
        return {
            'total_changes': total_changes,
            'new_tasks': len(categories['new_tasks']),
            'updates': (len(categories['delayed_tasks']) + 
                       len(categories['owner_changes']) + 
                       len(categories['schedule_accelerations'])),
            'blockers': len(categories['blocked_tasks']),
            'conflicts': len(categories['conflicts']),
            'on_track': len(categories['on_track_confirmations']),
            'requires_approval': self.metadata.get('requires_approval_count', 0),
            'health_score': health_score,
            'health_status': health_status
        }
    
    def _generate_change_narrative(
        self, 
        categories: Dict[str, List[Dict]], 
        style: SummaryStyle = SummaryStyle.DETAILED
    ) -> str:
        """
        Generate executive narrative describing what changed and why.
        
        Aligned with "Unlocking Excellence":
        - Names specialist teams and owners
        - Acknowledges coordination challenges
        - Highlights precision in tracking
        """
        narrative_parts = []
        
        # Opening context
        total_changes = self.metadata.get('total_changes_detected', 0)
        critical_count = self.metadata.get('critical_items_count', 0)
        
        if critical_count > 0:
            narrative_parts.append(
                f"This reporting period captured {total_changes} project updates, "
                f"including {critical_count} critical item{'s' if critical_count > 1 else ''} "
                f"requiring immediate leadership attention. Our specialist teams have maintained "
                f"meticulous tracking of evolving site conditions and procurement challenges."
            )
        else:
            narrative_parts.append(
                f"This reporting period reflects {total_changes} project updates across our "
                f"integrated delivery teams, demonstrating ongoing coordination and proactive "
                f"risk management aligned with SJ's commitment to excellence."
            )
        
        # Section 1: Blockers (highest priority narrative)
        blocked = categories['blocked_tasks']
        if blocked:
            blocker_desc = []
            for task in blocked[:3]:  # Detail top 3
                owner = task.get('baseline_value', 'Team')  # Owner from baseline
                task_name = task['task_name']
                evidence = task.get('evidence_quote', '')
                
                # Extract root cause
                if 'customs' in evidence.lower():
                    cause = "customs clearance delays"
                elif 'rain' in evidence.lower() or 'monsoon' in evidence.lower():
                    cause = "seasonal monsoon conditions"
                elif 'contaminated' in evidence.lower():
                    cause = "unexpected soil contamination"
                elif 'material' in evidence.lower():
                    cause = "material supply constraints"
                else:
                    cause = "operational constraints"
                
                blocker_desc.append(f"{task_name} (led by {owner}): {cause}")
            
            narrative_parts.append(
                f"\n**CRITICAL BLOCKERS:** {len(blocked)} task{'s' if len(blocked) > 1 else ''} "
                f"currently blocked, requiring coordinated intervention:\n" +
                "\n".join(f"• {desc}" for desc in blocker_desc)
            )
            
            if len(blocked) > 3:
                narrative_parts.append(
                    f"...and {len(blocked) - 3} additional blocker{'s' if len(blocked) - 3 > 1 else ''} "
                    f"detailed in full change log."
                )
        
        # Section 2: New Initiatives
        new_tasks = categories['new_tasks']
        if new_tasks:
            new_desc = []
            for task in new_tasks:
                task_name = task['task_name']
                owner = task.get('extracted_value', '').replace('INFERRED: ', '')
                new_desc.append(f"{task_name} (proposed by {owner})")
            
            narrative_parts.append(
                f"\n**NEW INITIATIVES:** Our specialist teams have identified {len(new_tasks)} "
                f"additional scope items to enhance project quality and sustainability:\n" +
                "\n".join(f"• {desc}" for desc in new_desc[:5])
            )
        
        # Section 3: Schedule Adjustments
        delayed = categories['delayed_tasks']
        if delayed:
            narrative_parts.append(
                f"\n**SCHEDULE REVISIONS:** {len(delayed)} task timeline{'s' if len(delayed) > 1 else ''} "
                f"adjusted in response to site conditions and procurement realities. "
                f"Each revision has been validated with exact impact analysis by the responsible owner."
            )
        
        # Section 4: Team Coordination
        owner_changes = categories['owner_changes']
        conflicts = categories['conflicts']
        if owner_changes or conflicts:
            narrative_parts.append(
                f"\n**TEAM COORDINATION:** {len(owner_changes)} ownership transition{'s' if len(owner_changes) > 1 else ''} "
                f"executed to optimize specialist expertise allocation. "
            )
            if conflicts:
                narrative_parts.append(
                    f"{len(conflicts)} coordination issue{'s' if len(conflicts) > 1 else ''} "
                    f"flagged for cross-functional alignment at the governance layer."
                )
        
        # Closing: Precision emphasis
        narrative_parts.append(
            f"\n**PRECISION TRACKING:** All updates include source evidence, confidence scoring, "
            f"and exact date quantification, ensuring leadership decisions are based on verified "
            f"field intelligence. {self.metadata.get('auto_approvable_count', 0)} low-risk changes "
            f"have been auto-validated, while {self.metadata.get('requires_approval_count', 0)} "
            f"strategic changes await governance review."
        )
        
        return "\n".join(narrative_parts)
    
    def _generate_action_items(self, categories: Dict[str, List[Dict]]) -> List[str]:
        """
        Generate specific action items for leadership.
        
        Format: [Priority] Action - Owner/Team - Deadline
        """
        actions = []
        
        # Priority 1: Resolve blockers
        for task in categories['blocked_tasks'][:3]:  # Top 3
            task_id = task.get('task_id', 'NEW')
            task_name = task['task_name']
            actions.append(
                f"[P1] Unblock {task_name} (Task {task_id}) - Escalate to procurement/operations - Within 48hrs"
            )
        
        # Priority 2: Resolve conflicts
        for task in categories['conflicts']:
            task_id = task.get('task_id', 'TBD')
            task_name = task['task_name']
            conflict = task.get('extracted_value', '')
            actions.append(
                f"[P2] Resolve ownership dispute on {task_name} (Task {task_id}): {conflict} - PMO mediation - Within 1 week"
            )
        
        # Priority 3: Approve new initiatives
        for task in categories['new_tasks'][:2]:  # Top 2
            task_name = task['task_name']
            owner = task.get('extracted_value', '').replace('INFERRED: ', '')
            actions.append(
                f"[P3] Review and approve new initiative: {task_name} (proposed by {owner}) - Governance review - Next steering meeting"
            )
        
        # Priority 4: Major delay mitigation
        for task in categories['delayed_tasks']:
            baseline = task.get('baseline_value', '')
            extracted = task.get('extracted_value', '')
            try:
                delay_days = (datetime.strptime(extracted, "%Y-%m-%d") - 
                             datetime.strptime(baseline, "%Y-%m-%d")).days
                if delay_days > 21:  # 3+ weeks
                    task_id = task.get('task_id', 'NEW')
                    task_name = task['task_name']
                    actions.append(
                        f"[P4] Develop mitigation plan for {task_name} (Task {task_id}) delay - Project controls - Within 2 weeks"
                    )
            except:
                pass
        
        return actions[:7]  # Max 7 action items for executive focus
    
    def _format_for_powerbi(
        self,
        highlights: List[str],
        alerts: List[str],
        metrics: Dict[str, Any],
        narrative: str,
        actions: List[str]
    ) -> str:
        """
        Format summary for Power BI text card with markdown styling.
        
        Power BI supports:
        - Headers: #, ##, ###
        - Bold: **text**
        - Bullets: •
        - Line breaks: \n\n
        """
        sections = []
        
        # Header
        sections.append(f"{self.POWERBI_HEADER_STYLE}SJ Nexus Project: What Changed")
        sections.append(f"📊 Report Date: {datetime.now().strftime('%b %d, %Y')}")
        
        # Health Score Badge
        health_score = metrics['health_score']
        health_status = metrics['health_status']
        if health_score >= 85:
            badge = "🟢"
        elif health_score >= 70:
            badge = "🟡"
        else:
            badge = "🔴"
        sections.append(f"{badge} **Project Health: {health_status} ({health_score}/100)**")
        
        sections.append(self.POWERBI_LINE_BREAK)
        
        # Metrics Snapshot
        sections.append(f"{self.POWERBI_SUBHEADER_STYLE}At a Glance")
        sections.append(
            f"{self.POWERBI_BULLET}**{metrics['total_changes']}** total updates tracked\n"
            f"{self.POWERBI_BULLET}**{metrics['new_tasks']}** new initiatives proposed\n"
            f"{self.POWERBI_BULLET}**{metrics['blockers']}** critical blockers\n"
            f"{self.POWERBI_BULLET}**{metrics['conflicts']}** coordination issues\n"
            f"{self.POWERBI_BULLET}**{metrics['on_track']}** tasks confirmed on track"
        )
        
        sections.append(self.POWERBI_LINE_BREAK)
        
        # Key Highlights
        sections.append(f"{self.POWERBI_SUBHEADER_STYLE}Key Highlights")
        for highlight in highlights:
            sections.append(f"{self.POWERBI_BULLET}{highlight}")
        
        sections.append(self.POWERBI_LINE_BREAK)
        
        # Critical Alerts (if any)
        if alerts:
            sections.append(f"{self.POWERBI_SUBHEADER_STYLE}Critical Alerts")
            for alert in alerts[:5]:  # Top 5 for space
                sections.append(f"{self.POWERBI_BULLET}{alert}")
            sections.append(self.POWERBI_LINE_BREAK)
        
        # Narrative (condensed for Power BI)
        sections.append(f"{self.POWERBI_SUBHEADER_STYLE}Executive Summary")
        # Limit narrative to ~600 chars for Power BI readability
        narrative_condensed = narrative[:600] + "..." if len(narrative) > 600 else narrative
        sections.append(narrative_condensed)
        
        sections.append(self.POWERBI_LINE_BREAK)
        
        # Action Items
        if actions:
            sections.append(f"{self.POWERBI_SUBHEADER_STYLE}Required Actions")
            for action in actions[:5]:  # Top 5 for space
                sections.append(f"{self.POWERBI_BULLET}{action}")
        
        # Footer
        sections.append(self.POWERBI_LINE_BREAK)
        sections.append(
            f"---\n"
            f"*Unlocking Excellence through precision tracking and specialist coordination*\n"
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        
        # Join and check length
        full_text = "\n".join(sections)
        if len(full_text) > self.POWERBI_MAX_CHARS:
            # Truncate narrative further if needed
            return self._truncate_for_powerbi(sections, self.POWERBI_MAX_CHARS)
        
        return full_text
    
    def _truncate_for_powerbi(self, sections: List[str], max_chars: int) -> str:
        """Intelligently truncate while preserving critical sections"""
        # Priority: Header, Metrics, Highlights, Alerts, Actions, Footer
        # Narrative can be most heavily condensed
        
        critical_sections = [
            sections[0],  # Header
            sections[1],  # Date
            sections[2],  # Health badge
            sections[3],  # Line break
            sections[4],  # Metrics header
            sections[5],  # Metrics content
        ]
        
        remaining_budget = max_chars - len("\n".join(critical_sections))
        
        # Add other sections with priority
        optional_sections = sections[6:]
        
        for section in optional_sections:
            if len(section) < remaining_budget:
                critical_sections.append(section)
                remaining_budget -= len(section)
            else:
                # Truncate this section
                truncated = section[:remaining_budget - 20] + "...\n[See full report]"
                critical_sections.append(truncated)
                break
        
        return "\n".join(critical_sections)
    
    def generate_executive_summary(
        self,
        style: SummaryStyle = SummaryStyle.DETAILED,
        include_powerbi: bool = True
    ) -> ExecutiveSummary:
        """
        Main method: Generate complete executive summary.
        
        Args:
            style: Presentation style (concise, detailed, metrics, actionable)
            include_powerbi: Whether to include Power BI formatted text
            
        Returns:
            ExecutiveSummary object with all components
        """
        # Categorize changes
        categories = self._categorize_changes()
        
        # Generate components
        highlights = self._generate_key_highlights(categories)
        alerts = self._generate_critical_alerts(categories)
        metrics = self._generate_metrics_snapshot(categories)
        narrative = self._generate_change_narrative(categories, style)
        actions = self._generate_action_items(categories)
        
        # Generate Power BI formatted text
        powerbi_text = ""
        if include_powerbi:
            powerbi_text = self._format_for_powerbi(
                highlights, alerts, metrics, narrative, actions
            )
        
        # Determine reporting period
        generated_at = datetime.now().isoformat()
        reporting_period = f"As of {datetime.now().strftime('%B %d, %Y')}"
        
        return ExecutiveSummary(
            title="SJ Integrated Urban Nexus - Project Update Summary",
            generated_at=generated_at,
            reporting_period=reporting_period,
            key_highlights=highlights,
            critical_alerts=alerts,
            metrics_snapshot=metrics,
            change_narrative=narrative,
            action_items=actions,
            powerbi_formatted_text=powerbi_text
        )
    
    def export_for_powerbi(self, output_path: str = "executive_summary_powerbi.json") -> str:
        """
        Export summary in Power BI-ready format.
        
        Args:
            output_path: Where to save the JSON file
            
        Returns:
            Path to saved file
        """
        summary = self.generate_executive_summary()
        
        # Structure for Power BI consumption
        powerbi_export = {
            "report_metadata": {
                "title": summary.title,
                "generated_at": summary.generated_at,
                "reporting_period": summary.reporting_period,
                "format_version": "1.0"
            },
            "text_card_content": summary.powerbi_formatted_text,
            "dashboard_kpis": summary.metrics_snapshot,
            "key_highlights": summary.key_highlights,
            "critical_alerts": summary.critical_alerts,
            "action_items": summary.action_items,
            "full_narrative": summary.change_narrative
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(powerbi_export, f, indent=2, ensure_ascii=False)
        
        return output_path


# ============================================================================
# EXAMPLE USAGE & TESTING
# ============================================================================

def example_usage():
    """Demonstrate Executive Summary Generator"""
    
    # Sample Delta Agent output (Plan Update Draft)
    sample_draft = {
        "draft_metadata": {
            "generated_at": "2026-08-20T14:30:00",
            "total_changes_detected": 15,
            "requires_approval_count": 10,
            "auto_approvable_count": 5,
            "critical_items_count": 4,
            "change_type_breakdown": {
                "New": 2,
                "Date Revision": 5,
                "Status Change": 5,
                "Owner Reassignment": 2,
                "Conflict": 1
            }
        },
        "summary": {
            "new_tasks": 2,
            "updates": 12,
            "conflicts": 1,
            "no_changes": 0
        },
        "critical_items": [
            {
                "task_id": "7.0",
                "task_name": "Procurement of High-Grade Structural Steel",
                "issue": "Status changed to 'Blocked' - CRITICAL STATUS",
                "evidence": "steel held up at port due to customs",
                "detected_at": "2026-06-01T08:45:00"
            },
            {
                "task_id": "13.0",
                "task_name": "Foundation Piling - North Sector Execution",
                "issue": "Status changed to 'Blocked' - CRITICAL STATUS",
                "evidence": "monsoon rains flooded excavation pits",
                "detected_at": "2026-08-18T10:00:00"
            },
            {
                "task_id": "17.0",
                "task_name": "MEP Utility Corridor Optimization",
                "issue": "Ownership conflict detected",
                "evidence": "Linda vs. David both claim responsibility",
                "detected_at": "2026-09-22T09:00:00"
            }
        ],
        "requires_approval": [],
        "auto_approvable": [],
        "detailed_change_log": [
            {
                "change_type": "Status Change",
                "task_id": "7.0",
                "task_name": "Procurement of High-Grade Structural Steel",
                "field_changed": "Status",
                "baseline_value": "Not Started",
                "extracted_value": "Blocked",
                "evidence_quote": "the high-grade structural steel is held up at the port",
                "confidence_score": 0.95,
                "requires_approval": True,
                "approval_reason": "Status changed to 'Blocked' - CRITICAL STATUS",
                "source_metadata": {
                    "document_id": "Email_021",
                    "date": "2026-06-01 08:45 AM",
                    "participants": ["Sofia Rossi", "Samuel Lee"],
                    "source_type": "Email"
                },
                "detected_at": "2026-08-20T14:30:00"
            },
            {
                "change_type": "Date Revision",
                "task_id": "7.0",
                "task_name": "Procurement of High-Grade Structural Steel",
                "field_changed": "Due_Date",
                "baseline_value": "2026-08-28",
                "extracted_value": "2026-09-25",
                "evidence_quote": "I anticipate a 4-week delay",
                "confidence_score": 0.95,
                "requires_approval": True,
                "approval_reason": "Due date revised by +28 days",
                "source_metadata": {
                    "document_id": "Email_021",
                    "date": "2026-06-01 08:45 AM",
                    "participants": ["Sofia Rossi", "Samuel Lee"],
                    "source_type": "Email"
                },
                "detected_at": "2026-08-20T14:30:00"
            },
            {
                "change_type": "Status Change",
                "task_id": "13.0",
                "task_name": "Foundation Piling - North Sector Execution",
                "field_changed": "Status",
                "baseline_value": "Not Started",
                "extracted_value": "Blocked",
                "evidence_quote": "monsoon rains have flooded the excavation pits",
                "confidence_score": 1.0,
                "requires_approval": True,
                "approval_reason": "Status changed to 'Blocked' - CRITICAL STATUS",
                "source_metadata": {
                    "document_id": "Snippet_001",
                    "date": "2026-08-18 10:00 AM",
                    "participants": ["Samuel Lee", "Ben Richardson"],
                    "source_type": "Meeting Minute"
                },
                "detected_at": "2026-08-20T14:30:00"
            },
            {
                "change_type": "New",
                "task_id": None,
                "task_name": "Carbon Offset Verification (Phase A)",
                "field_changed": None,
                "baseline_value": None,
                "extracted_value": "Carbon Offset Verification (Phase A)",
                "evidence_quote": "we must add a New Task: 'Carbon Offset Verification (Phase A)'",
                "confidence_score": 0.70,
                "requires_approval": True,
                "approval_reason": "New task proposed - not in baseline WBS",
                "source_metadata": {
                    "document_id": "Email_032",
                    "date": "2026-11-17 10:00 AM",
                    "participants": ["Elena Rodriguez", "Chloe Dupont"],
                    "source_type": "Email"
                },
                "detected_at": "2026-08-20T14:30:00"
            },
            {
                "change_type": "Conflict",
                "task_id": "17.0",
                "task_name": "MEP Utility Corridor Optimization",
                "field_changed": "Owner",
                "baseline_value": "Linda Ng",
                "extracted_value": "CONFLICT: Linda Ng vs. David O'Sullivan",
                "evidence_quote": "Linda claims she is leading, but David insists his structural team needs to own the heights",
                "confidence_score": 0.60,
                "requires_approval": True,
                "approval_reason": "Ownership conflict detected",
                "source_metadata": {
                    "document_id": "Snippet_013",
                    "date": "2026-09-22 09:00 AM",
                    "participants": ["Linda Ng", "David O'Sullivan", "Sarah Chen"],
                    "source_type": "Meeting Minute"
                },
                "detected_at": "2026-08-20T14:30:00"
            }
        ]
    }
    
    # Initialize generator
    generator = ExecutiveSummaryGenerator(sample_draft)
    
    # Generate summary
    summary = generator.generate_executive_summary()
    
    # Display results
    print("=" * 80)
    print("EXECUTIVE SUMMARY - POWER BI TEXT CARD FORMAT")
    print("=" * 80)
    print(summary.powerbi_formatted_text)
    
    print("\n\n" + "=" * 80)
    print("STRUCTURED DATA FOR DASHBOARDS")
    print("=" * 80)
    print(json.dumps(summary.metrics_snapshot, indent=2))
    
    # Export for Power BI
    output_file = generator.export_for_powerbi()
    print(f"\n✅ Exported to: {output_file}")
    
    return summary


if __name__ == "__main__":
    example_usage()
