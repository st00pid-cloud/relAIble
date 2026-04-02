# SJ Project Planner Agent - Development Guide

## Tech Stack
- [cite_start]**Primary:** Microsoft Foundry, Azure AI Search, Azure Database for PostgreSQL [cite: 78-79].
- [cite_start]**Automation:** Power Automate.
- [cite_start]**Visualization:** Power BI (Gantt & Dashboard).

## Project Core Logic
- [cite_start]**Goal:** Convert unstructured conversations (Meeting Notes/Emails) into structured planning updates[cite: 31, 48].
- [cite_start]**Schema:** Task, Owner, Due Date, Status, Source, Confidence[cite: 57].
- [cite_start]**Delta Detection:** Compare extracted data vs. `SJ_Baseline_WBS.csv` to identify New, Update, or Conflict [cite: 58-61].

## Code Style & Standards
- Functional programming for data extraction pipelines.
- [cite_start]Every update must include a "Source" reference and "Evidence" string[cite: 57, 62].
- [cite_start]Implement a "Review-before-update" workflow[cite: 76].