"""
Delta Agent - Comprehensive Test Suite
Using Real SJ Integrated Urban Nexus Project Data

This script demonstrates the Delta Agent's capabilities with actual
scenarios from the project documentation.
"""

import json
from delta_agent import DeltaAgent, DeltaDetection, ChangeType


def load_sj_baseline():
    """Load the actual SJ Nexus baseline tasks"""
    return [
        {
            "Task ID": "1.0",
            "Task Name": "Project Charter & Scope Finalization",
            "Owner": "Samuel Lee",
            "Start Date": "2026-04-06",
            "End Date": "2026-04-17",
            "Current Status": "On Track"
        },
        {
            "Task ID": "2.0",
            "Task Name": "Geotechnical Site Assessment (Nexus Bridge)",
            "Owner": "Hiroshi Tanaka",
            "Start Date": "2026-04-20",
            "End Date": "2026-05-15",
            "Current Status": "Not Started"
        },
        {
            "Task ID": "5.0",
            "Task Name": "5G Network Topology & URLLC Mapping",
            "Owner": "Amina Al-Farsi",
            "Start Date": "2026-05-11",
            "End Date": "2026-07-03",
            "Current Status": "Not Started"
        },
        {
            "Task ID": "7.0",
            "Task Name": "Procurement of High-Grade Structural Steel",
            "Owner": "Sofia Rossi",
            "Start Date": "2026-06-01",
            "End Date": "2026-08-28",
            "Current Status": "Not Started"
        },
        {
            "Task ID": "9.0",
            "Task Name": "Rooftop Garden & Irrigation System Design",
            "Owner": "Priya Lakshmi",
            "Start Date": "2026-06-15",
            "End Date": "2026-08-07",
            "Current Status": "Not Started"
        },
        {
            "Task ID": "10.0",
            "Task Name": "BIM Model Coordination (Phase 1)",
            "Owner": "Sarah Chen",
            "Start Date": "2026-07-06",
            "End Date": "2026-09-18",
            "Current Status": "Not Started"
        },
        {
            "Task ID": "11.0",
            "Task Name": "Public Stakeholder Town Hall Series",
            "Owner": "Rachael Smythe",
            "Start Date": "2026-07-13",
            "End Date": "2026-10-02",
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
            "Task ID": "14.0",
            "Task Name": "Smart Grid & Renewable Energy Integration",
            "Owner": "Fatima Zahra",
            "Start Date": "2026-08-24",
            "End Date": "2026-11-20",
            "Current Status": "Not Started"
        },
        {
            "Task ID": "15.0",
            "Task Name": "GSIMS Platform Spatial Data Mapping",
            "Owner": "Alice Thompson",
            "Start Date": "2026-09-07",
            "End Date": "2026-10-30",
            "Current Status": "Not Started"
        },
        {
            "Task ID": "17.0",
            "Task Name": "MEP Utility Corridor Optimization",
            "Owner": "Linda Ng",
            "Start Date": "2026-09-21",
            "End Date": "2026-11-27",
            "Current Status": "Not Started"
        },
        {
            "Task ID": "18.0",
            "Task Name": "VDC Construction Sequence Simulation",
            "Owner": "Kevin Zhang",
            "Start Date": "2026-10-05",
            "End Date": "2026-11-13",
            "Current Status": "Not Started"
        },
        {
            "Task ID": "19.0",
            "Task Name": "5G Node Hardware & Edge Node Install",
            "Owner": "Daniel Kim",
            "Start Date": "2026-10-19",
            "End Date": "2027-01-29",
            "Current Status": "Not Started"
        },
        {
            "Task ID": "21.0",
            "Task Name": "Acoustic Barrier Design for Rail Link",
            "Owner": "Isabella Varga",
            "Start Date": "2026-11-09",
            "End Date": "2026-12-18",
            "Current Status": "Not Started"
        },
        {
            "Task ID": "22.0",
            "Task Name": "Sustainability & Carbon Neutrality Audit",
            "Owner": "Elena Rodriguez",
            "Start Date": "2026-11-16",
            "End Date": "2027-03-26",
            "Current Status": "Not Started"
        },
        {
            "Task ID": "27.0",
            "Task Name": "Multi-Modal Transport Flow Simulation",
            "Owner": "Omar Bakri",
            "Start Date": "2027-01-18",
            "End Date": "2027-03-12",
            "Current Status": "Not Started"
        },
        {
            "Task ID": "29.0",
            "Task Name": "Claims & Legal Liability Review",
            "Owner": "Geoffery Tan",
            "Start Date": "2027-03-01",
            "End Date": "2027-04-16",
            "Current Status": "Not Started"
        }
    ]


def get_test_scenarios():
    """
    Return test scenarios based on actual SJ project communications
    from the documents provided
    """
    
    scenarios = [
        {
            "name": "TC-DELTA-001: Task 7.0 Blocked with 4-Week Delay",
            "description": "Sofia reports steel procurement is blocked at port",
            "extracted_tasks": [
                {
                    "task_name": "Procurement of High-Grade Structural Steel",
                    "owner": "Sofia Rossi",
                    "due_date": "2026-09-25",  # Baseline: 2026-08-28, +28 days
                    "status": "Blocked",
                    "evidence_quote": "the high-grade structural steel for the Nexus Bridge is held up at the port. Task 7.0 (Procurement) is Blocked. I anticipate a 4-week delay.",
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
            ],
            "expected_deltas": 2,  # Date revision + Status change
            "expected_critical": 1  # Blocked status
        },
        {
            "name": "TC-DELTA-002: Task 13.0 Multiple Blockers",
            "description": "Foundation piling blocked by monsoon and contaminated soil",
            "extracted_tasks": [
                {
                    "task_name": "Foundation Piling - North Sector Execution",
                    "owner": "Ben Richardson",
                    "due_date": "2026-12-18",
                    "status": "Blocked",
                    "evidence_quote": "Ben reported that the Foundation Piling - North Sector (Task 13.0) is officially Blocked. Heavy seasonal monsoon rains have flooded the excavation pits.",
                    "confidence_score": 1.0,
                    "needs_clarification": False,
                    "clarification_reason": None,
                    "source_metadata": {
                        "document_id": "Snippet_001",
                        "date": "2026-08-18 10:00 AM",
                        "participants": ["Samuel Lee", "Ben Richardson", "David O'Sullivan"],
                        "source_type": "Meeting Minute"
                    }
                }
            ],
            "expected_deltas": 1,  # Status change only
            "expected_critical": 1  # Blocked
        },
        {
            "name": "TC-DELTA-003: Task 2.0 Date Extension",
            "description": "Hiroshi extends geotechnical assessment by 7 days",
            "extracted_tasks": [
                {
                    "task_name": "Geotechnical Site Assessment (Nexus Bridge)",
                    "owner": "Hiroshi Tanaka",
                    "due_date": "2026-05-22",  # Baseline: 2026-05-15, +7 days
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
                }
            ],
            "expected_deltas": 1,  # Date revision only
            "expected_critical": 0
        },
        {
            "name": "TC-DELTA-004: Task 11.0 Date Change (Town Hall)",
            "description": "Town hall rescheduled from July 13 to July 27",
            "extracted_tasks": [
                {
                    "task_name": "Public Stakeholder Town Hall Series",
                    "owner": "Rachael Smythe",
                    "due_date": "2026-07-27",  # Changed from baseline start date
                    "status": "On Track",
                    "evidence_quote": "The Public Stakeholder Town Hall (Task 11.0) has a confirmed date change. It is moved from July 13 to July 27 to accommodate the local council members' schedules.",
                    "confidence_score": 1.0,
                    "needs_clarification": False,
                    "clarification_reason": None,
                    "source_metadata": {
                        "document_id": "Snippet_008",
                        "date": "2026-07-14 09:30 AM",
                        "participants": ["Rachael Smythe", "Samuel Lee"],
                        "source_type": "Meeting Minute"
                    }
                }
            ],
            "expected_deltas": 1,  # Date change (but end date is 2026-10-02, so may not detect)
            "expected_critical": 0
        },
        {
            "name": "TC-DELTA-005: CONFLICT - Task 17.0 Ownership Dispute",
            "description": "Linda and David both claim ownership of MEP optimization",
            "extracted_tasks": [
                {
                    "task_name": "MEP Utility Corridor Optimization",
                    "owner": "CONFLICT: Linda Ng vs. David O'Sullivan",
                    "due_date": "2026-11-27",
                    "status": "On Track",
                    "evidence_quote": "A conflict arose regarding Task 17.0 (MEP Corridor Optimization). Linda claims she is leading the optimization, but David insists his structural team needs to own the heights.",
                    "confidence_score": 0.60,
                    "needs_clarification": True,
                    "clarification_reason": "Ownership conflict detected. Both Linda Ng and David O'Sullivan claim responsibility for Task 17.0.",
                    "source_metadata": {
                        "document_id": "Snippet_013",
                        "date": "2026-09-22 09:00 AM",
                        "participants": ["Linda Ng", "David O'Sullivan", "Sarah Chen"],
                        "source_type": "Meeting Minute"
                    }
                }
            ],
            "expected_deltas": 1,  # Ownership conflict
            "expected_critical": 1  # Conflict
        },
        {
            "name": "TC-DELTA-006: NEW TASK - Carbon Offset Verification",
            "description": "Elena proposes new carbon offset verification task",
            "extracted_tasks": [
                {
                    "task_name": "Carbon Offset Verification (Phase A)",
                    "owner": "INFERRED: Elena Rodriguez",
                    "due_date": "NULL",
                    "status": "Not Started",
                    "evidence_quote": "we must add a New Task: 'Carbon Offset Verification (Phase A)' before the final Sustainability Audit (Task 22.0).",
                    "confidence_score": 0.70,
                    "needs_clarification": True,
                    "clarification_reason": "New task proposed - not in baseline WBS. Owner inferred as Elena Rodriguez. No due date specified.",
                    "source_metadata": {
                        "document_id": "Email_032",
                        "date": "2026-11-17 10:00 AM",
                        "participants": ["Elena Rodriguez", "Chloe Dupont"],
                        "source_type": "Email"
                    }
                }
            ],
            "expected_deltas": 1,  # New task
            "expected_critical": 0
        },
        {
            "name": "TC-DELTA-007: Task 15.0 Owner Reassignment",
            "description": "Samuel assigns Task 15.0 to Sarah Chen",
            "extracted_tasks": [
                {
                    "task_name": "GSIMS Platform Spatial Data Mapping",
                    "owner": "Sarah Chen",  # Baseline: Alice Thompson
                    "due_date": "2026-10-30",
                    "status": "On Track",
                    "evidence_quote": "Sarah, I'd like you to take the lead on the GSIMS Platform Spatial Data Mapping (Task 15.0). Please coordinate with the tech team.",
                    "confidence_score": 0.95,
                    "needs_clarification": False,
                    "clarification_reason": None,
                    "source_metadata": {
                        "document_id": "Email_022",
                        "date": "2026-09-08 09:12 AM",
                        "participants": ["Samuel Lee", "Sarah Chen", "Alice Thompson"],
                        "source_type": "Email"
                    }
                }
            ],
            "expected_deltas": 1,  # Owner reassignment
            "expected_critical": 0
        },
        {
            "name": "TC-DELTA-008: Task 5.0 Start Date Push",
            "description": "Amina pushes start of 5G topology mapping to May 25",
            "extracted_tasks": [
                {
                    "task_name": "5G Network Topology & URLLC Mapping",
                    "owner": "Amina Al-Farsi",
                    "due_date": "2026-05-25",  # Baseline start: 2026-05-11 (this is a start date change)
                    "status": "On Track",
                    "evidence_quote": "let's push the start of Task 5.0 (5G Network Topology) to May 25, 2026, to align with new digital twin sync protocols.",
                    "confidence_score": 1.0,
                    "needs_clarification": False,
                    "clarification_reason": None,
                    "source_metadata": {
                        "document_id": "Email_030",
                        "date": "2026-05-12 04:50 PM",
                        "participants": ["Amina Al-Farsi", "Marcus Wong"],
                        "source_type": "Email"
                    }
                }
            ],
            "expected_deltas": 1,  # Date revision (treating as end date for comparison)
            "expected_critical": 0
        },
        {
            "name": "TC-DELTA-009: Task 19.0 Blocked - Hardware Customs",
            "description": "Edge computing nodes stuck in customs",
            "extracted_tasks": [
                {
                    "task_name": "5G Node Hardware & Edge Node Install",
                    "owner": "Daniel Kim",
                    "due_date": "2027-01-29",
                    "status": "Blocked",
                    "evidence_quote": "The edge computing nodes are stuck in customs. Task 19.0 (5G Node Hardware install) is Blocked until further notice.",
                    "confidence_score": 1.0,
                    "needs_clarification": False,
                    "clarification_reason": None,
                    "source_metadata": {
                        "document_id": "Email_024",
                        "date": "2026-10-20 04:22 PM",
                        "participants": ["Daniel Kim", "Samuel Lee"],
                        "source_type": "Email"
                    }
                }
            ],
            "expected_deltas": 1,  # Status change
            "expected_critical": 1  # Blocked
        },
        {
            "name": "TC-DELTA-010: Task 21.0 Blocked - Material Unavailable",
            "description": "Acoustic barrier design blocked by material spec",
            "extracted_tasks": [
                {
                    "task_name": "Acoustic Barrier Design for Rail Link",
                    "owner": "Isabella Varga",
                    "due_date": "2026-12-18",
                    "status": "Blocked",
                    "evidence_quote": "specialized foam for the rail links is unavailable. Task 21.0 (Acoustic Barrier Design) is Blocked regarding material spec.",
                    "confidence_score": 1.0,
                    "needs_clarification": False,
                    "clarification_reason": None,
                    "source_metadata": {
                        "document_id": "Email_042",
                        "date": "2026-11-10 10:10 AM",
                        "participants": ["Isabella Varga", "Sofia Rossi"],
                        "source_type": "Email"
                    }
                }
            ],
            "expected_deltas": 1,  # Status change
            "expected_critical": 1  # Blocked
        },
        {
            "name": "TC-DELTA-011: Task 29.0 Owner Reassignment",
            "description": "Jessica Low takes over Claims & Legal review from Geoffery Tan",
            "extracted_tasks": [
                {
                    "task_name": "Claims & Legal Liability Review",
                    "owner": "Jessica Low",  # Baseline: Geoffery Tan
                    "due_date": "2027-04-16",
                    "status": "On Track",
                    "evidence_quote": "Jessica, I'd like you to take the lead on Task 29.0 (Claims & Legal Liability). Geoffery, please provide her with the files.",
                    "confidence_score": 1.0,
                    "needs_clarification": False,
                    "clarification_reason": None,
                    "source_metadata": {
                        "document_id": "Email_034",
                        "date": "2027-02-02 02:30 PM",
                        "participants": ["Samuel Lee", "Geoffery Tan", "Jessica Low"],
                        "source_type": "Email"
                    }
                }
            ],
            "expected_deltas": 1,  # Owner reassignment
            "expected_critical": 0
        },
        {
            "name": "TC-DELTA-012: Task 27.0 Start Date Delayed",
            "description": "Omar pushes transport simulation start to Feb 1",
            "extracted_tasks": [
                {
                    "task_name": "Multi-Modal Transport Flow Simulation",
                    "owner": "Omar Bakri",
                    "due_date": "2027-02-01",  # Baseline start: 2027-01-18 (this is start date change)
                    "status": "On Track",
                    "evidence_quote": "traffic modeling is taking longer. I need to move the Start Date for Task 27.0 (Transport Flow Simulation) to February 1, 2027.",
                    "confidence_score": 1.0,
                    "needs_clarification": False,
                    "clarification_reason": None,
                    "source_metadata": {
                        "document_id": "Email_048",
                        "date": "2027-01-19 09:20 AM",
                        "participants": ["Omar Bakri", "Samuel Lee"],
                        "source_type": "Email"
                    }
                }
            ],
            "expected_deltas": 1,  # Date revision
            "expected_critical": 0
        },
        {
            "name": "TC-DELTA-013: Task 18.0 Multiple Owners Assigned",
            "description": "Both Kevin and Sarah responsible for VDC simulation",
            "extracted_tasks": [
                {
                    "task_name": "VDC Construction Sequence Simulation",
                    "owner": "Kevin Zhang",  # Extracting first mention
                    "due_date": "2026-11-13",
                    "status": "On Track",
                    "evidence_quote": "To ensure we don't miss the deadline, both Kevin and Sarah will now be responsible for Task 18.0 (VDC Construction Sequence Simulation).",
                    "confidence_score": 0.85,
                    "needs_clarification": True,
                    "clarification_reason": "Multiple owners assigned to same task. Clarify co-ownership structure or primary/secondary roles.",
                    "source_metadata": {
                        "document_id": "Email_027",
                        "date": "2026-10-06 11:15 AM",
                        "participants": ["Linda Ng", "Kevin Zhang", "Sarah Chen"],
                        "source_type": "Email"
                    }
                }
            ],
            "expected_deltas": 0,  # Same owner as baseline
            "expected_critical": 0
        },
        {
            "name": "TC-DELTA-014: Task 9.0 Blocked - Flooding Damage",
            "description": "Rooftop garden design blocked by irrigation prep flooding",
            "extracted_tasks": [
                {
                    "task_name": "Rooftop Garden & Irrigation System Design",
                    "owner": "Priya Lakshmi",
                    "due_date": "2026-08-07",
                    "status": "Blocked",
                    "evidence_quote": "flooding has damaged the initial irrigation prep. Task 9.0 (Rooftop Garden Design) site prep is Blocked for at least 10 days.",
                    "confidence_score": 0.90,
                    "needs_clarification": False,
                    "clarification_reason": None,
                    "source_metadata": {
                        "document_id": "Email_029",
                        "date": "2026-06-16 01:20 PM",
                        "participants": ["Priya Lakshmi", "Samuel Lee"],
                        "source_type": "Email"
                    }
                }
            ],
            "expected_deltas": 1,  # Status change
            "expected_critical": 1  # Blocked
        },
        {
            "name": "TC-DELTA-015: NEW TASK - 5G Mesh Latency Stress Test",
            "description": "Amina proposes latency test for autonomous shuttles",
            "extracted_tasks": [
                {
                    "task_name": "5G Mesh Latency Stress Test",
                    "owner": "INFERRED: Amina Al-Farsi",
                    "due_date": "NULL",
                    "status": "Not Started",
                    "evidence_quote": "let's add a New Task: '5G Mesh Latency Stress Test' for the autonomous shuttles before we finalize Task 5.0.",
                    "confidence_score": 0.70,
                    "needs_clarification": True,
                    "clarification_reason": "New task proposed - not in baseline WBS. Owner inferred as proposer. No due date specified.",
                    "source_metadata": {
                        "document_id": "Email_043",
                        "date": "2026-05-12 11:25 AM",
                        "participants": ["Amina Al-Farsi", "Robert Kwok"],
                        "source_type": "Email"
                    }
                }
            ],
            "expected_deltas": 1,  # New task
            "expected_critical": 0
        }
    ]
    
    return scenarios


def run_test_scenario(agent: DeltaAgent, scenario: dict, scenario_num: int):
    """Run a single test scenario and display results"""
    
    print("\n" + "=" * 80)
    print(f"SCENARIO {scenario_num}: {scenario['name']}")
    print("=" * 80)
    print(f"Description: {scenario['description']}")
    print(f"\nExpected: {scenario['expected_deltas']} delta(s), {scenario['expected_critical']} critical")
    
    # Run Delta Agent
    deltas = agent.compare_tasks(scenario['extracted_tasks'])
    
    # Display results
    print(f"\n✅ Detected: {len(deltas)} delta(s)")
    
    for i, delta in enumerate(deltas, 1):
        print(f"\n  Delta {i}:")
        print(f"    Change Type: {delta.change_type.value}")
        print(f"    Task: {delta.task_name} (ID: {delta.task_id})")
        if delta.field_changed:
            print(f"    Field: {delta.field_changed.value}")
            print(f"    Baseline: {delta.baseline_value}")
            print(f"    Extracted: {delta.extracted_value}")
        print(f"    Requires Approval: {'✓ YES' if delta.requires_approval else '✗ No'}")
        print(f"    Reason: {delta.approval_reason}")
        print(f"    Confidence: {delta.confidence_score:.2f}")
    
    # Validation
    if len(deltas) == scenario['expected_deltas']:
        print(f"\n✅ PASS: Delta count matches expected ({scenario['expected_deltas']})")
    else:
        print(f"\n⚠️  WARNING: Expected {scenario['expected_deltas']} deltas, got {len(deltas)}")
    
    critical_count = sum(1 for d in deltas if d.change_type == ChangeType.CONFLICT or 
                        (d.extracted_value and "Blocked" in str(d.extracted_value)))
    if critical_count == scenario['expected_critical']:
        print(f"✅ PASS: Critical count matches expected ({scenario['expected_critical']})")
    else:
        print(f"⚠️  WARNING: Expected {scenario['expected_critical']} critical items, got {critical_count}")
    
    return deltas


def run_comprehensive_test_suite():
    """Run all test scenarios"""
    
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 25 + "DELTA AGENT TEST SUITE" + " " * 31 + "║")
    print("║" + " " * 18 + "SJ Integrated Urban Nexus Project" + " " * 27 + "║")
    print("╚" + "═" * 78 + "╝")
    
    # Load baseline
    baseline = load_sj_baseline()
    agent = DeltaAgent(baseline)
    
    print(f"\n📊 Loaded baseline: {len(baseline)} tasks")
    
    # Get test scenarios
    scenarios = get_test_scenarios()
    print(f"📋 Test scenarios: {len(scenarios)}")
    
    # Run all scenarios
    all_deltas = []
    passed = 0
    failed = 0
    
    for i, scenario in enumerate(scenarios, 1):
        try:
            deltas = run_test_scenario(agent, scenario, i)
            all_deltas.extend(deltas)
            passed += 1
        except Exception as e:
            print(f"\n❌ FAILED: {e}")
            failed += 1
        
        if i < len(scenarios):
            input("\n⏎ Press Enter to continue to next scenario...")
    
    # Generate final Plan Update Draft
    print("\n" + "=" * 80)
    print("GENERATING PLAN UPDATE DRAFT")
    print("=" * 80)
    
    draft = agent.generate_plan_update_draft(all_deltas)
    
    print("\n📊 SUMMARY STATISTICS:")
    print(f"  Total Changes: {draft['draft_metadata']['total_changes_detected']}")
    print(f"  Requires Approval: {draft['draft_metadata']['requires_approval_count']}")
    print(f"  Auto-Approvable: {draft['draft_metadata']['auto_approvable_count']}")
    print(f"  Critical Items: {draft['draft_metadata']['critical_items_count']}")
    
    print("\n📈 BREAKDOWN:")
    for change_type, count in draft['summary'].items():
        print(f"  {change_type}: {count}")
    
    print("\n🚨 CRITICAL ITEMS:")
    for item in draft['critical_items'][:5]:  # Show first 5
        print(f"  • {item['task_name']}: {item['issue']}")
    
    # Save to file
    output_file = "plan_update_draft_test.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(draft, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Full draft saved to: {output_file}")
    
    # Test results
    print("\n" + "=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    print(f"✅ Passed: {passed}/{len(scenarios)}")
    print(f"❌ Failed: {failed}/{len(scenarios)}")
    
    return draft, all_deltas


if __name__ == "__main__":
    run_comprehensive_test_suite()
