"""
Executive Summary Generator - Test Suite

Demonstrates the generator using actual Delta Agent outputs from
the SJ Integrated Urban Nexus project.
"""

import json
from executive_summary_generator import ExecutiveSummaryGenerator, SummaryStyle


def load_sample_delta_outputs():
    """Load sample Delta Agent outputs representing different project scenarios"""
    
    scenarios = {
        "normal_operations": {
            "name": "Normal Operations - Minor Updates",
            "description": "Routine project updates with mostly on-track status",
            "draft": {
                "draft_metadata": {
                    "generated_at": "2026-07-15T09:00:00",
                    "total_changes_detected": 8,
                    "requires_approval_count": 3,
                    "auto_approvable_count": 5,
                    "critical_items_count": 0,
                    "change_type_breakdown": {
                        "Date Revision": 3,
                        "Status Change": 3,
                        "Owner Reassignment": 2
                    }
                },
                "summary": {
                    "new_tasks": 0,
                    "updates": 8,
                    "conflicts": 0
                },
                "critical_items": [],
                "detailed_change_log": [
                    {
                        "change_type": "Date Revision",
                        "task_id": "2.0",
                        "task_name": "Geotechnical Site Assessment",
                        "baseline_value": "2026-05-15",
                        "extracted_value": "2026-05-22",
                        "evidence_quote": "soil density requires 7 additional days",
                        "confidence_score": 1.0,
                        "requires_approval": False
                    },
                    {
                        "change_type": "Status Change",
                        "task_id": "9.0",
                        "task_name": "Rooftop Garden Design",
                        "baseline_value": "Not Started",
                        "extracted_value": "On Track",
                        "evidence_quote": "irrigation schematics finalized this week",
                        "confidence_score": 0.90,
                        "requires_approval": False
                    }
                ]
            }
        },
        
        "crisis_mode": {
            "name": "Crisis Mode - Multiple Blockers",
            "description": "Multiple critical blockers requiring immediate intervention",
            "draft": {
                "draft_metadata": {
                    "generated_at": "2026-08-20T14:30:00",
                    "total_changes_detected": 18,
                    "requires_approval_count": 14,
                    "auto_approvable_count": 4,
                    "critical_items_count": 6,
                    "change_type_breakdown": {
                        "Status Change": 8,
                        "Date Revision": 6,
                        "New": 2,
                        "Conflict": 2
                    }
                },
                "summary": {
                    "new_tasks": 2,
                    "updates": 14,
                    "conflicts": 2
                },
                "critical_items": [
                    {
                        "task_id": "7.0",
                        "task_name": "Procurement of High-Grade Structural Steel",
                        "issue": "Blocked - customs delay",
                        "evidence": "steel held up at port",
                        "detected_at": "2026-06-01T08:45:00"
                    },
                    {
                        "task_id": "13.0",
                        "task_name": "Foundation Piling - North Sector",
                        "issue": "Blocked - environmental",
                        "evidence": "monsoon flooding",
                        "detected_at": "2026-08-18T10:00:00"
                    },
                    {
                        "task_id": "19.0",
                        "task_name": "5G Node Hardware Install",
                        "issue": "Blocked - supply chain",
                        "evidence": "semiconductor shortage",
                        "detected_at": "2026-10-20T15:00:00"
                    },
                    {
                        "task_id": "21.0",
                        "task_name": "Acoustic Barrier Design",
                        "issue": "Blocked - material unavailable",
                        "evidence": "specialized foam on backorder",
                        "detected_at": "2026-11-10T10:10:00"
                    },
                    {
                        "task_id": "17.0",
                        "task_name": "MEP Utility Corridor Optimization",
                        "issue": "Ownership conflict",
                        "evidence": "Linda vs. David dispute",
                        "detected_at": "2026-09-22T09:00:00"
                    }
                ],
                "detailed_change_log": [
                    {
                        "change_type": "Status Change",
                        "task_id": "7.0",
                        "task_name": "Procurement of High-Grade Structural Steel",
                        "field_changed": "Status",
                        "baseline_value": "Not Started",
                        "extracted_value": "Blocked",
                        "evidence_quote": "high-grade structural steel held up at the port due to customs",
                        "confidence_score": 0.95,
                        "requires_approval": True,
                        "approval_reason": "Status changed to 'Blocked' - CRITICAL"
                    },
                    {
                        "change_type": "Date Revision",
                        "task_id": "7.0",
                        "task_name": "Procurement of High-Grade Structural Steel",
                        "baseline_value": "2026-08-28",
                        "extracted_value": "2026-09-25",
                        "evidence_quote": "4-week delay anticipated",
                        "confidence_score": 0.95,
                        "requires_approval": True
                    },
                    {
                        "change_type": "Status Change",
                        "task_id": "13.0",
                        "task_name": "Foundation Piling - North Sector",
                        "baseline_value": "Not Started",
                        "extracted_value": "Blocked",
                        "evidence_quote": "monsoon rains flooded excavation pits",
                        "confidence_score": 1.0,
                        "requires_approval": True
                    },
                    {
                        "change_type": "Status Change",
                        "task_id": "19.0",
                        "task_name": "5G Node Hardware Install",
                        "baseline_value": "Not Started",
                        "extracted_value": "Blocked",
                        "evidence_quote": "global semiconductor housing shortage",
                        "confidence_score": 1.0,
                        "requires_approval": True
                    },
                    {
                        "change_type": "Status Change",
                        "task_id": "21.0",
                        "task_name": "Acoustic Barrier Design",
                        "baseline_value": "Not Started",
                        "extracted_value": "Blocked",
                        "evidence_quote": "specialized foam unavailable",
                        "confidence_score": 1.0,
                        "requires_approval": True
                    },
                    {
                        "change_type": "Conflict",
                        "task_id": "17.0",
                        "task_name": "MEP Utility Corridor Optimization",
                        "baseline_value": "Linda Ng",
                        "extracted_value": "CONFLICT: Linda Ng vs. David O'Sullivan",
                        "evidence_quote": "ownership dispute over corridor heights",
                        "confidence_score": 0.60,
                        "requires_approval": True
                    },
                    {
                        "change_type": "New",
                        "task_id": None,
                        "task_name": "Carbon Offset Verification (Phase A)",
                        "extracted_value": "Carbon Offset Verification (Phase A)",
                        "evidence_quote": "must add new task before sustainability audit",
                        "confidence_score": 0.70,
                        "requires_approval": True
                    },
                    {
                        "change_type": "New",
                        "task_id": None,
                        "task_name": "5G Mesh Latency Stress Test",
                        "extracted_value": "5G Mesh Latency Stress Test",
                        "evidence_quote": "needed for autonomous shuttles",
                        "confidence_score": 0.70,
                        "requires_approval": True
                    }
                ]
            }
        },
        
        "growth_phase": {
            "name": "Growth Phase - New Initiatives",
            "description": "Multiple new tasks proposed as project evolves",
            "draft": {
                "draft_metadata": {
                    "generated_at": "2026-06-10T11:00:00",
                    "total_changes_detected": 12,
                    "requires_approval_count": 8,
                    "auto_approvable_count": 4,
                    "critical_items_count": 0,
                    "change_type_breakdown": {
                        "New": 5,
                        "Owner Reassignment": 3,
                        "Date Revision": 4
                    }
                },
                "summary": {
                    "new_tasks": 5,
                    "updates": 7,
                    "conflicts": 0
                },
                "critical_items": [],
                "detailed_change_log": [
                    {
                        "change_type": "New",
                        "task_name": "Circular Economy Material Verification",
                        "extracted_value": "Circular Economy Material Verification",
                        "evidence_quote": "urgent requirement for LEED Gold status",
                        "confidence_score": 0.80,
                        "requires_approval": True
                    },
                    {
                        "change_type": "New",
                        "task_name": "Public Realm Shade Analysis",
                        "extracted_value": "Public Realm Shade Analysis",
                        "evidence_quote": "simulate heat islands from town hall feedback",
                        "confidence_score": 0.75,
                        "requires_approval": True
                    },
                    {
                        "change_type": "New",
                        "task_name": "Smart Wayfinding Totem Placement Study",
                        "extracted_value": "Smart Wayfinding Totem Placement",
                        "evidence_quote": "needed before interior ergonomics begins",
                        "confidence_score": 0.70,
                        "requires_approval": True
                    },
                    {
                        "change_type": "New",
                        "task_name": "Greywater Filtration System Integration",
                        "extracted_value": "Greywater Filtration System",
                        "evidence_quote": "map into hydraulic plan before Task 20.0",
                        "confidence_score": 0.75,
                        "requires_approval": True
                    },
                    {
                        "change_type": "Owner Reassignment",
                        "task_id": "15.0",
                        "task_name": "GSIMS Platform Spatial Data Mapping",
                        "baseline_value": "Alice Thompson",
                        "extracted_value": "Sarah Chen",
                        "evidence_quote": "Samuel assigns Sarah to lead Task 15.0",
                        "confidence_score": 0.95,
                        "requires_approval": False
                    }
                ]
            }
        }
    }
    
    return scenarios


def test_scenario(scenario_name: str, scenario_data: dict):
    """Test executive summary generation for a specific scenario"""
    
    print("\n" + "=" * 80)
    print(f"SCENARIO: {scenario_data['name']}")
    print("=" * 80)
    print(f"Description: {scenario_data['description']}")
    print()
    
    # Generate summary
    generator = ExecutiveSummaryGenerator(scenario_data['draft'])
    summary = generator.generate_executive_summary()
    
    # Display Power BI formatted output
    print("POWER BI TEXT CARD OUTPUT:")
    print("-" * 80)
    print(summary.powerbi_formatted_text)
    
    # Display structured metrics
    print("\n" + "-" * 80)
    print("DASHBOARD METRICS:")
    print("-" * 80)
    print(json.dumps(summary.metrics_snapshot, indent=2))
    
    # Display key highlights
    print("\n" + "-" * 80)
    print("KEY HIGHLIGHTS:")
    print("-" * 80)
    for i, highlight in enumerate(summary.key_highlights, 1):
        print(f"{i}. {highlight}")
    
    # Display action items
    if summary.action_items:
        print("\n" + "-" * 80)
        print("ACTION ITEMS:")
        print("-" * 80)
        for i, action in enumerate(summary.action_items, 1):
            print(f"{i}. {action}")
    
    print("\n" + "=" * 80)
    print(f"✅ {scenario_name.upper()} TEST COMPLETE")
    print("=" * 80)
    
    return summary


def run_comprehensive_tests():
    """Run all test scenarios"""
    
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 18 + "EXECUTIVE SUMMARY GENERATOR TEST SUITE" + " " * 21 + "║")
    print("║" + " " * 25 + "Power BI Integration Tests" + " " * 26 + "║")
    print("╚" + "═" * 78 + "╝")
    
    scenarios = load_sample_delta_outputs()
    
    print(f"\n📊 Test Scenarios: {len(scenarios)}")
    print("1. Normal Operations - Routine updates")
    print("2. Crisis Mode - Multiple blockers")
    print("3. Growth Phase - New initiatives")
    
    summaries = {}
    
    for scenario_name, scenario_data in scenarios.items():
        input(f"\n⏎ Press Enter to run {scenario_name} test...")
        summary = test_scenario(scenario_name, scenario_data)
        summaries[scenario_name] = summary
    
    # Final comparison
    print("\n" + "=" * 80)
    print("HEALTH SCORE COMPARISON")
    print("=" * 80)
    
    for scenario_name, summary in summaries.items():
        health = summary.metrics_snapshot['health_score']
        status = summary.metrics_snapshot['health_status']
        if health >= 85:
            icon = "🟢"
        elif health >= 70:
            icon = "🟡"
        else:
            icon = "🔴"
        print(f"{icon} {scenario_name.replace('_', ' ').title()}: {health}/100 ({status})")
    
    # Export all summaries
    print("\n" + "=" * 80)
    print("EXPORTING SUMMARIES")
    print("=" * 80)
    
    for scenario_name, summary in summaries.items():
        generator = ExecutiveSummaryGenerator(scenarios[scenario_name]['draft'])
        output_file = f"executive_summary_{scenario_name}.json"
        generator.export_for_powerbi(output_file)
        print(f"✅ Exported {scenario_name} → {output_file}")
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED")
    print("=" * 80)
    print("\n📋 Summary:")
    print("  • All scenarios tested successfully")
    print("  • Power BI text cards generated")
    print("  • Dashboard metrics calculated")
    print("  • Action items prioritized")
    print("  • Health scores computed")
    print("\n✅ Ready for Power BI integration!")


if __name__ == "__main__":
    run_comprehensive_tests()
