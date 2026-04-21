"""
sj_search_ingestor.py
─────────────────────────────────────────────────────────────────────────────
SJ Project Planner Agent — Azure AI Search Simulation Layer
─────────────────────────────────────────────────────────────────────────────

PURPOSE
    Simulates the Azure AI Search Ingestion Layer described in the
    SJ Project Planner Agentic Architecture:

        SJ_Input_Samples/ (.txt / .pdf)
            └── [Azure AI Search indexing]
                    └── Extraction Agent (LLM parser)
                            └── Delta Agent → PostgreSQL Baseline
                                    └── Draft Review → Power BI

    This script handles everything up to — and including — preparing the
    LLM extraction prompt payload. It does NOT call the LLM; it produces
    a list of DocumentChunk objects that the Extraction Agent consumes.

ARCHITECTURE FIT (from System_Architecture_relAIble.pdf)
    • Ingestion Layer  : read_source_files()  — scans the input folder
    • Chunking         : chunk_document()     — semantic paragraph chunking
    • Index simulation : build_search_index() — in-memory index by source/chunk
    • Retrieval        : retrieve_chunks()    — keyword-based ranked retrieval
    • Prompt assembly  : build_extraction_prompt() — formats payload for the LLM

AUDIBILITY CONTRACT (CLAUDE.md — "Every update must include a Source
    reference and Evidence string")
    Every DocumentChunk carries:
        .source_file   — original filename (e.g. "Email_021.txt")
        .source_type   — 'Meeting Minute' | 'Email'
        .chunk_index   — position within the document
        .document_date — parsed from the processed/ header when present
    These fields propagate into the LLM prompt so the model can populate
    the mandatory Source + Evidence columns in plan_updates_draft.

USAGE
    # Index and extract from the default project input folder:
    python sj_search_ingestor.py

    # Point at a custom folder:
    python sj_search_ingestor.py --input-dir path/to/SJ_Input_Samples

    # Dry-run: print chunks without calling any downstream agent:
    python sj_search_ingestor.py --dry-run

    # Save the prompt payloads to disk for inspection / unit testing:
    python sj_search_ingestor.py --save-prompts

DEPENDENCIES
    Standard library only — no pip installs required.
    Designed to be dropped into the Microsoft Foundry pipeline alongside
    the Power Automate connector and the PostgreSQL baseline writer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Iterator
import urllib.request

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

# Default input folder mirrors the Azure AI Search index source in the
# project architecture.  Adjust to your local clone path or Foundry mount.
DEFAULT_INPUT_DIR = Path("SJ_Integrated_Urban_Nexus/data")

# Azure AI Search imposes a 32 KB field limit; keep chunks well inside that.
# Paragraph-aware chunking means real chunks are usually 200–600 characters.
MAX_CHUNK_CHARS = 1_200

# Minimum chunk size — discard slivers that carry no signal for the LLM.
MIN_CHUNK_CHARS = 40

# Number of top-ranked chunks included in a single LLM extraction prompt.
# Mirrors the Azure AI Search "top=N" retrieval parameter.
TOP_K_CHUNKS = 8

# Output folder for optional prompt payload files (--save-prompts).
PROMPT_OUTPUT_DIR = Path("sj_prompt_payloads")

# Recognised source-type markers in processed-file headers.
_MEETING_MARKERS = {"meeting minute", "meeting minutes", "snippet"}
_EMAIL_MARKERS   = {"email"}

# Task-ID pattern: matches "Task 13.0", "Task 7.0", etc.
_TASK_ID_RE = re.compile(r"\bTask\s+(\d+\.\d+)\b", re.IGNORECASE)

# Date header pattern in processed/ files:
# "Date: 2026-06-01 08:45 AM | ..."
_DATE_HEADER_RE = re.compile(
    r"Date:\s*(\d{4}-\d{2}-\d{2})\s+(\d{1,2}:\d{2}\s*(?:AM|PM)?)",
    re.IGNORECASE,
)

# SJ project personas (from persona_technical_entities.json) used to boost
# retrieval ranking when a chunk names a known team member.
SJ_PERSONAS = {
    "Samuel Lee", "Ben Richardson", "David O'Sullivan", "Sofia Rossi",
    "Hiroshi Tanaka", "Amina Al-Farsi", "Marcus Wong", "Daniel Kim",
    "Linda Ng", "Priya Lakshmi", "Elena Rodriguez", "Sarah Chen",
    "Alice Thompson", "Arjun Mehta", "Fatima Zahra", "Rachael Smythe",
    "James Peterson", "Chloe Dupont", "Kevin Zhang", "Thomas Müller",
    "Isabella Varga", "Omar Bakri", "Jessica Low", "Vikram Singh",
    "Robert Kwok", "Zoe Castellano", "Hassan Meer", "Emily Watson",
    "Geoffery Tan", "Siti Nurhaliza",
}

# SJ technical entities (from persona_technical_entities.json) used for the
# same ranking boost.
SJ_TECHNICAL_ENTITIES = {
    "ETFE Cushion System", "Digital Twin Sync", "GSIMS Platform", "URLLC",
    "Edge Computing Nodes", "Network Slicing", "Lidar Point Cloud Mesh",
    "BIM-to-FM Handover Protocol", "Vibration Isolation Springs",
    "Crowd Flow Heatmaps", "Turf Management Sensors", "AI-Driven Predictive Maintenance",
    "C-V2X", "Holographic Telepresence",
}

# ─────────────────────────────────────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("sj_ingestor")


# ─────────────────────────────────────────────────────────────────────────────
# DATA MODELS
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class DocumentChunk:
    """
    The atomic unit of the search index.

    Every field here maps directly to a column in the PostgreSQL schema:
        source_file   → unstructured_sources.file_name
        source_type   → unstructured_sources.source_type
        document_date → unstructured_sources.document_date
        chunk_text    → the evidence the LLM will quote in evidence_string
        content_hash  → unstructured_sources.content_hash (dedup key)

    The chunk is intentionally immutable after creation — mutations should
    produce new chunks, preserving the audit trail.
    """
    # ── Provenance (audibility contract) ────────────────────────────────────
    source_file:    str          # e.g. "Email_021.txt"
    source_path:    str          # absolute path for downstream writers
    source_type:    str          # "Meeting Minute" | "Email" | "Unknown"
    document_date:  str | None   # ISO-8601 date string or None

    # ── Content ─────────────────────────────────────────────────────────────
    chunk_index:    int          # 0-based position within this document
    chunk_text:     str          # the actual text passed to the LLM

    # ── Derived signals (used for retrieval ranking) ─────────────────────────
    task_ids:       list[str] = field(default_factory=list)   # ["13.0", "7.0"]
    personas_found: list[str] = field(default_factory=list)   # ["Ben Richardson"]
    entities_found: list[str] = field(default_factory=list)   # ["ETFE Cushion System"]
    relevance_score: float = 0.0  # computed by score_chunk()

    # ── Deduplication ────────────────────────────────────────────────────────
    content_hash:   str = field(init=False)

    def __post_init__(self) -> None:
        self.content_hash = hashlib.sha256(
            self.chunk_text.encode("utf-8")
        ).hexdigest()

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SearchIndex:
    """
    In-memory simulation of an Azure AI Search index.

    Azure AI Search builds an inverted index over document fields.
    This class simulates that with a simple dict keyed on content_hash
    (deduplication) plus a flat list for ranked retrieval.
    """
    _store: dict[str, DocumentChunk] = field(default_factory=dict)

    def add(self, chunk: DocumentChunk) -> bool:
        """Returns True if the chunk was new, False if it was a duplicate."""
        if chunk.content_hash in self._store:
            return False
        self._store[chunk.content_hash] = chunk
        return True

    def all_chunks(self) -> list[DocumentChunk]:
        return list(self._store.values())

    def __len__(self) -> int:
        return len(self._store)


# ─────────────────────────────────────────────────────────────────────────────
# INGESTION — read_source_files()
# ─────────────────────────────────────────────────────────────────────────────

def read_source_files(input_dir: Path) -> Iterator[tuple[Path, str]]:
    """
    Recursively walk *input_dir* and yield (path, raw_text) for every .txt file.

    Mirrors the Azure AI Search data-source connector that scans
    SJ_Input_Samples/ for indexable documents.  Only .txt files are handled
    here; a production version would add a PDF extraction step using the
    pdf-reading skill.
    """
    if not input_dir.exists():
        log.warning("Input directory not found: %s — using demo fixtures.", input_dir)
        yield from _demo_fixtures()
        return

    txt_files = sorted(input_dir.rglob("*.txt"))
    if not txt_files:
        log.warning("No .txt files found in %s — using demo fixtures.", input_dir)
        yield from _demo_fixtures()
        return

    log.info("Found %d .txt file(s) in %s", len(txt_files), input_dir)
    for path in txt_files:
        try:
            text = path.read_text(encoding="utf-8", errors="replace").strip()
            if text:
                yield path, text
        except OSError as exc:
            log.error("Could not read %s: %s", path, exc)


def _demo_fixtures() -> Iterator[tuple[Path, str]]:
    """
    Inline fixtures drawn verbatim from the project's source corpus.
    Used when the input directory is absent — e.g. during CI or demo runs.
    Each fixture reproduces a real document from the SJ Integrated Urban Nexus
    dataset so the chunker and prompt builder can be exercised end-to-end.
    """
    fixtures = [
        (
            "data/processed/Emails_with_metadata_header/Email_021.txt",
            (
                "Date: 2026-06-01 08:45 AM | Recipients: Sofia Rossi, Samuel Lee "
                "| Source: Email\n"
                "From: Sofia Rossi | To: Samuel Lee | Subject: Supply Chain Update: Task 7.0\n"
                "Samuel, the high-grade structural steel for the Nexus Bridge is held up at "
                "the port. Task 7.0 (Procurement) is Blocked. I anticipate a 4-week delay."
            ),
        ),
        (
            "data/processed/Emails_with_metadata_header/Email_023.txt",
            (
                "Date: 2026-04-21 10:30 AM | Recipients: Hiroshi Tanaka, David O'Sullivan "
                "| Source: Email\n"
                "From: Hiroshi Tanaka | To: David O'Sullivan | Subject: RE: Nexus Bridge Soils\n"
                "David, the soil density is more variable than expected. I need to extend the "
                "Geotechnical Site Assessment (Task 2.0) to an End Date of May 22, 2026."
            ),
        ),
        (
            "data/processed/Emails_with_metadata_header/Email_001.txt",
            (
                "Date: 2026-08-18 10:00 AM | Attendees: Samuel Lee, Ben Richardson, "
                "David O'Sullivan | Source: Meeting Minute\n"
                "**Snippet 001: Weekly Progress Review (Infrastructure)**\n"
                "* Discussion: Ben reported that the Foundation Piling - North Sector "
                "(Task 13.0) is officially Blocked. Heavy seasonal monsoon rains have "
                "flooded the excavation pits. Work cannot resume until the pumps clear the site."
            ),
        ),
        (
            "data/processed/Emails_with_metadata_header/Email_042.txt",
            (
                "Date: 2026-11-10 10:10 AM | Recipients: Isabella Varga, Sofia Rossi "
                "| Source: Email\n"
                "From: Isabella Varga | To: Sofia Rossi | Subject: Acoustic Barrier Lead Times\n"
                "Sofia, specialized foam for the rail links is unavailable. Task 21.0 "
                "(Acoustic Barrier Design) is Blocked regarding material spec."
            ),
        ),
        (
            "data/processed/Emails_with_metadata_header/Email_013.txt",
            (
                "Date: 2026-09-22 09:00 AM | Attendees: Linda Ng, David O'Sullivan, "
                "Sarah Chen | Source: Meeting Minute\n"
                "**Snippet 013: MEP & Structural Coordination**\n"
                "* Discussion: A conflict arose regarding Task 17.0 (MEP Corridor "
                "Optimization). Linda claims she is leading the optimization, but David "
                "insists his structural team needs to own the heights."
            ),
        ),
        (
            "data/processed/Emails_with_metadata_header/Email_010.txt",
            (
                "Date: 2026-04-21 10:00 AM | Attendees: Chloe Dupont, Samuel Lee "
                "| Source: Meeting Minute\n"
                "**Snippet 010: Environmental Oversight**\n"
                "* Discussion: Chloe flagged a New Task: \"Migratory Bird Flight Path "
                "Audit.\" Recent environmental surveys near the Nexus Bridge site indicate "
                "a protected species nesting nearby."
            ),
        ),
        (
            "data/processed/Emails_with_metadata_header/Email_028.txt",
            (
                "Date: 2026-09-15 03:40 PM | Recipients: Thomas Müller, Sofia Rossi "
                "| Source: Email\n"
                "From: Thomas Müller | To: Sofia Rossi | Subject: ETFE Cushion Delivery\n"
                "Sofia, the ETFE Cushion System (Task 16.0 related) is on backorder. "
                "We are officially Blocked on façade assembly for the atrium."
            ),
        ),
        (
            "data/processed/Emails_with_metadata_header/Email_032.txt",
            (
                "Date: 2026-11-17 10:00 AM | Recipients: Elena Rodriguez, Chloe Dupont "
                "| Source: Email\n"
                "From: Elena Rodriguez | To: Chloe Dupont | Subject: Mandatory Carbon "
                "Offset Verification\n"
                "Chloe, we must add a New Task: \"Carbon Offset Verification (Phase A)\" "
                "before the final Sustainability Audit (Task 22.0)."
            ),
        ),
    ]
    for rel_path, content in fixtures:
        yield Path(rel_path), content


# ─────────────────────────────────────────────────────────────────────────────
# PARSING HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _parse_source_type(text: str) -> str:
    """
    Infer 'Meeting Minute' or 'Email' from the document header.

    Processed files carry an explicit '| Source: Email' or
    '| Source: Meeting Minute' marker.  Raw files are classified by
    whether they contain '**Snippet' (meeting) or 'From:' (email).
    """
    lower = text.lower()
    for marker in _MEETING_MARKERS:
        if marker in lower:
            return "Meeting Minute"
    for marker in _EMAIL_MARKERS:
        if marker in lower:
            return "Email"
    return "Unknown"


def _parse_document_date(text: str) -> str | None:
    """
    Extract the ISO-8601 date from the processed-file header line, e.g.:
        'Date: 2026-06-01 08:45 AM | Recipients: ...'
    Returns None for raw files that lack a header.
    """
    match = _DATE_HEADER_RE.search(text)
    return match.group(1) if match else None


def _extract_task_ids(text: str) -> list[str]:
    """Return all WBS IDs mentioned in *text*, e.g. ['13.0', '7.0']."""
    return list(dict.fromkeys(_TASK_ID_RE.findall(text)))


def _extract_personas(text: str) -> list[str]:
    """Return any known SJ team member names found in *text*."""
    return [p for p in SJ_PERSONAS if p in text]


def _extract_technical_entities(text: str) -> list[str]:
    """Return any known SJ technical entity names found in *text*."""
    return [e for e in SJ_TECHNICAL_ENTITIES if e in text]


# ─────────────────────────────────────────────────────────────────────────────
# CHUNKING — chunk_document()
# ─────────────────────────────────────────────────────────────────────────────

def chunk_document(
    path: Path,
    raw_text: str,
    max_chars: int = MAX_CHUNK_CHARS,
    min_chars: int = MIN_CHUNK_CHARS,
) -> list[DocumentChunk]:
    """
    Split a source document into semantically coherent chunks.

    STRATEGY
    ────────
    The SJ source documents are short (typically 3–10 sentences) and
    structured around a single task event — a status change, a date update,
    a new task request, or an ownership conflict.  A paragraph-aware
    chunking strategy (split on blank lines first, then on sentences if a
    paragraph exceeds max_chars) preserves that semantic unit intact so the
    LLM receives the full context for each event in one chunk.

    This mirrors the Azure AI Search "skillset" chunking step that splits
    documents before embedding them into the vector index.

    AUDIBILITY
    ──────────
    Every produced DocumentChunk carries the original source_file name so
    that the Extraction Agent can populate the mandatory Source + Evidence
    fields in plan_updates_draft without any additional lookup.

    Args:
        path      : Filesystem path of the source file (for provenance).
        raw_text  : Full text content of the file.
        max_chars : Hard ceiling per chunk (Azure AI Search field limit proxy).
        min_chars : Discard slivers below this length.

    Returns:
        Ordered list of DocumentChunk objects, one per semantic paragraph.
    """
    source_file   = path.name
    source_path   = str(path.resolve())
    source_type   = _parse_source_type(raw_text)
    document_date = _parse_document_date(raw_text)

    # ── Step 1: isolate the header line (metadata) from the body ────────────
    # The header pattern is: "Date: YYYY-MM-DD HH:MM ... | Source: ..."
    # We preserve it as its own chunk so the LLM always sees full provenance.
    lines = raw_text.splitlines()
    header_lines: list[str] = []
    body_lines:   list[str] = []

    for i, line in enumerate(lines):
        if i == 0 and line.startswith("Date:"):
            header_lines.append(line.strip())
        else:
            body_lines.append(line)

    header_text = " ".join(header_lines).strip()
    body_text   = "\n".join(body_lines).strip()

    # ── Step 2: split body on blank lines (paragraph boundary) ──────────────
    raw_paragraphs: list[str] = [
        p.strip()
        for p in re.split(r"\n{2,}", body_text)
        if p.strip()
    ]

    # ── Step 3: further split any paragraph that exceeds max_chars ──────────
    # Use sentence boundaries (. ! ?) as fallback split points so we never
    # truncate mid-sentence.
    paragraphs: list[str] = []
    for para in raw_paragraphs:
        if len(para) <= max_chars:
            paragraphs.append(para)
        else:
            sentences = re.split(r"(?<=[.!?])\s+", para)
            current   = ""
            for sent in sentences:
                if len(current) + len(sent) + 1 <= max_chars:
                    current = (current + " " + sent).strip() if current else sent
                else:
                    if current:
                        paragraphs.append(current)
                    current = sent
            if current:
                paragraphs.append(current)

    # ── Step 4: assemble DocumentChunk objects ───────────────────────────────
    chunks: list[DocumentChunk] = []
    chunk_index = 0

    # Header chunk: always first — gives the LLM full provenance context.
    if header_text and len(header_text) >= min_chars:
        chunks.append(DocumentChunk(
            source_file    = source_file,
            source_path    = source_path,
            source_type    = source_type,
            document_date  = document_date,
            chunk_index    = chunk_index,
            chunk_text     = header_text,
            task_ids       = _extract_task_ids(header_text),
            personas_found = _extract_personas(header_text),
            entities_found = _extract_technical_entities(header_text),
        ))
        chunk_index += 1

    # Body chunks.
    for para in paragraphs:
        if len(para) < min_chars:
            continue
        chunks.append(DocumentChunk(
            source_file    = source_file,
            source_path    = source_path,
            source_type    = source_type,
            document_date  = document_date,
            chunk_index    = chunk_index,
            chunk_text     = para,
            task_ids       = _extract_task_ids(para),
            personas_found = _extract_personas(para),
            entities_found = _extract_technical_entities(para),
        ))
        chunk_index += 1

    return chunks


# ─────────────────────────────────────────────────────────────────────────────
# INDEXING — build_search_index()
# ─────────────────────────────────────────────────────────────────────────────

def build_search_index(input_dir: Path) -> SearchIndex:
    """
    Read all .txt files from *input_dir*, chunk them, and load into the index.

    Simulates the Azure AI Search indexer run:
        1. Data-source connector scans SJ_Input_Samples/
        2. Skillset applies chunking + entity-recognition enrichments
        3. Index push uploads each chunk as a search document

    Deduplication is enforced via SHA-256 hash of chunk text — matching the
    content_hash column in unstructured_sources.
    """
    index      = SearchIndex()
    total_docs = 0
    total_dup  = 0

    for path, raw_text in read_source_files(input_dir):
        chunks = chunk_document(path, raw_text)
        total_docs += 1
        for chunk in chunks:
            added = index.add(chunk)
            if not added:
                total_dup += 1
                log.debug("Duplicate chunk skipped: %s[%d]", chunk.source_file, chunk.chunk_index)

    log.info(
        "Index built: %d chunks from %d document(s). %d duplicate(s) skipped.",
        len(index), total_docs, total_dup,
    )
    return index


# ─────────────────────────────────────────────────────────────────────────────
# RETRIEVAL — score_chunk() + retrieve_chunks()
# ─────────────────────────────────────────────────────────────────────────────

def score_chunk(chunk: DocumentChunk) -> float:
    """
    Compute a relevance score for a chunk.

    Simulates the Azure AI Search BM25 + semantic ranking hybrid score.
    Signals weighted here reflect what the Extraction Agent needs:

        +2.0  per WBS Task ID found          — direct task reference
        +1.5  per known SJ persona found     — ownership / assignment signal
        +1.0  per known technical entity     — domain-specific evidence
        +0.5  if chunk contains 'Blocked'    — high-priority status signal
        +0.5  if chunk contains 'New Task'   — scope change signal
        +0.3  if chunk contains a year ref   — temporal grounding

    Scores are intentionally simple floats rather than normalised vectors —
    the goal is relative ranking, not semantic similarity.
    """
    score = 0.0
    text  = chunk.chunk_text

    score += len(chunk.task_ids)       * 2.0
    score += len(chunk.personas_found) * 1.5
    score += len(chunk.entities_found) * 1.0

    if re.search(r"\bBlocked\b",  text, re.IGNORECASE): score += 0.5
    if re.search(r"\bNew Task\b", text, re.IGNORECASE): score += 0.5
    if re.search(r"\b20\d{2}\b",  text):                score += 0.3

    return round(score, 3)


def retrieve_chunks(index: SearchIndex, top_k: int = TOP_K_CHUNKS) -> list[DocumentChunk]:
    """
    Score every chunk and return the top-k by relevance.

    Simulates the Azure AI Search query execution step:
        SELECT TOP @top_k FROM index ORDER BY @score DESC

    In production this would also accept a natural-language query string
    and perform vector similarity search against chunk embeddings.
    Here we use the signal-based scorer as an equivalent proxy.
    """
    chunks = index.all_chunks()
    for chunk in chunks:
        chunk.relevance_score = score_chunk(chunk)

    ranked = sorted(chunks, key=lambda c: c.relevance_score, reverse=True)
    selected = ranked[:top_k]

    log.info(
        "Retrieved %d/%d chunks (top-%d). Score range: %.1f – %.1f",
        len(selected), len(chunks), top_k,
        selected[-1].relevance_score if selected else 0,
        selected[0].relevance_score  if selected else 0,
    )
    return selected


# ─────────────────────────────────────────────────────────────────────────────
# PROMPT ASSEMBLY — build_extraction_prompt()
# ─────────────────────────────────────────────────────────────────────────────

# System prompt for the Extraction Agent.
# Aligns with CLAUDE.md schema: Task | Owner | Due Date | Status | Source | Confidence
_SYSTEM_PROMPT = """\
You are the Extraction Agent for the SJ Project Planner — the relAIble system \
built on the SJ Integrated Urban Nexus project.

Your task is to extract structured planning updates from the provided document \
chunks and output a JSON array.  Each element must conform exactly to this schema:

{
  "task_id":        "<WBS decimal ID, e.g. '13.0', or null for new tasks>",
  "task_name":      "<Full task name>",
  "owner":          "<Person responsible, or 'CONTRADICTION: A vs. B' for conflicts>",
  "start_date":     "<ISO-8601 date or null if not mentioned>",
  "due_date":       "<ISO-8601 date or null if not mentioned>",
  "status":         "<One of: Not Started | On Track | Blocked | In Review | Completed>",
  "delta_type":     "<One of: New Task | Update | Conflict>",
  "source_file":    "<Filename from the Source field below — mandatory>",
  "evidence_string":"<Verbatim sentence(s) from the chunk that support this extraction>",
  "confidence":     <Float 0.0–1.0 — use < 0.60 for vague language like 'sometime next month'>
}

RULES
• Output a raw JSON array only — no prose, no markdown fences.
• Include source_file and evidence_string on every record — these are mandatory \
  audit fields that feed the plan_updates_draft table.
• Set confidence < 0.60 when the source uses vague language \
  (e.g. "after the monsoon", "sometime late next month", "late Q1").
• If two chunks contradict each other on the same field, emit ONE record with \
  delta_type = "Conflict" and owner = "CONTRADICTION: <person A> vs. <person B>".
• Do not invent facts.  If a field cannot be determined from the chunk, use null.
"""

def build_extraction_prompt(chunks: list[DocumentChunk]) -> dict:
    """
    Assemble the full LLM extraction prompt from the retrieved chunks.

    Returns a dict with:
        'system'   — the system prompt string
        'user'     — the user message string (chunks formatted as a numbered list)
        'metadata' — provenance dict for logging / Power Automate pass-through

    The returned dict is ready to be serialised and sent to the LLM via the
    Microsoft Foundry / Azure AI Foundry chat completion endpoint.

    AUDIBILITY
    ──────────
    Each chunk block includes its Source filename, type, date, and chunk index
    so the model can populate source_file without inference.
    """
    chunk_blocks: list[str] = []

    for i, chunk in enumerate(chunks, start=1):
        block = (
            f"--- CHUNK {i} ---\n"
            f"Source      : {chunk.source_file}\n"
            f"Source Type : {chunk.source_type}\n"
            f"Date        : {chunk.document_date or 'Unknown'}\n"
            f"Chunk Index : {chunk.chunk_index}\n"
            f"Relevance   : {chunk.relevance_score}\n"
            f"Task IDs    : {', '.join(chunk.task_ids) or 'None detected'}\n"
            f"Personas    : {', '.join(chunk.personas_found) or 'None detected'}\n"
            f"\n"
            f"{chunk.chunk_text}\n"
        )
        chunk_blocks.append(block)

    user_message = (
        "Extract all planning updates from the following document chunks.\n"
        "Remember: every output record MUST include source_file and evidence_string.\n\n"
        + "\n".join(chunk_blocks)
    )

    metadata = {
        "chunk_count":    len(chunks),
        "source_files":   sorted({c.source_file for c in chunks}),
        "source_types":   sorted({c.source_type for c in chunks}),
        "task_ids_seen":  sorted({tid for c in chunks for tid in c.task_ids}),
        "generated_at":   datetime.now(tz=__import__("datetime").timezone.utc).isoformat(),
    }

    return {
        "system":   _SYSTEM_PROMPT,
        "user":     user_message,
        "metadata": metadata,
    }


# ─────────────────────────────────────────────────────────────────────────────
# PIPELINE ENTRY POINT — run_pipeline()
# ─────────────────────────────────────────────────────────────────────────────

def run_pipeline(
    input_dir:    Path  = DEFAULT_INPUT_DIR,
    top_k:        int   = TOP_K_CHUNKS,
    dry_run:      bool  = False,
    save_prompts: bool  = False,
) -> dict | None:
    """
    End-to-end ingestion pipeline.

    Stages:
        1. read_source_files  — scan input folder for .txt documents
        2. chunk_document     — paragraph-aware semantic chunking
        3. build_search_index — dedup + load into in-memory index
        4. retrieve_chunks    — rank and select top-k chunks
        5. build_extraction_prompt — assemble LLM payload

    Returns the prompt dict, or None on failure.
    The caller (Power Automate connector / Foundry agent) sends this payload
    to the LLM and writes the response into plan_updates_draft.
    """
    log.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    log.info("SJ Project Planner Agent — Azure AI Search Simulation")
    log.info("Input   : %s", input_dir.resolve())
    log.info("Top-K   : %d", top_k)
    log.info("Dry-run : %s", dry_run)
    log.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # Stage 1–3: Index
    index = build_search_index(input_dir)
    all_chunks = index.all_chunks()
    for chunk in all_chunks:
        chunk.relevance_score = score_chunk(chunk)

    if not dry_run:
        push_chunks_to_azure(all_chunks)

    if len(index) == 0:
        log.error("No chunks indexed. Aborting pipeline.")
        return None

    # Stage 4: Retrieve
    top_chunks = retrieve_chunks(index, top_k=top_k)

    import urllib.request

def push_chunks_to_azure(chunks: list[DocumentChunk]) -> None:
    """
    Upload all chunks from the in-memory index to Azure AI Search.
    Mirrors the Azure AI Search index push API:
    POST /indexes/sj-nexus-chunks/docs/index?api-version=2023-11-01
    """
    endpoint  = os.environ["AZURE_SEARCH_ENDPOINT"]
    api_key   = os.environ["AZURE_SEARCH_API_KEY"]
    index     = "sj-nexus-chunks"
    url       = f"{endpoint}/indexes/{index}/docs/index?api-version=2023-11-01"

    # Azure Search requires a unique key per document — use content_hash
    actions = [
        {
            "@search.action": "mergeOrUpload",   # idempotent — safe to re-run
            "id":              chunk.content_hash,
            "source_file":     chunk.source_file,
            "source_type":     chunk.source_type,
            "document_date":   chunk.document_date,
            "chunk_index":     chunk.chunk_index,
            "chunk_text":      chunk.chunk_text,
            "task_ids":        chunk.task_ids,
            "personas_found":  chunk.personas_found,
            "entities_found":  chunk.entities_found,
            "relevance_score": chunk.relevance_score,
            "content_hash":    chunk.content_hash,
        }
        for chunk in chunks
    ]

    # Azure accepts up to 1000 documents per batch
    batch_size = 100
    for i in range(0, len(actions), batch_size):
        batch   = actions[i : i + batch_size]
        payload = json.dumps({"value": batch}).encode("utf-8")

        req = urllib.request.Request(
            url,
            data    = payload,
            headers = {
                "Content-Type": "application/json",
                "api-key":      api_key,
            },
            method  = "POST",
        )
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            log.info("Uploaded batch %d: %d docs", i // batch_size + 1,
                     len(result.get("value", [])))

    # Stage 5: Prompt assembly
    prompt = build_extraction_prompt(top_chunks)

    # ── Dry-run output ───────────────────────────────────────────────────────
    if dry_run:
        log.info("DRY-RUN — printing top chunks and prompt metadata only.\n")
        print("\n" + "═" * 70)
        print("TOP CHUNKS SELECTED FOR EXTRACTION")
        print("═" * 70)
        for i, chunk in enumerate(top_chunks, 1):
            print(f"\n[{i}] {chunk.source_file}  |  chunk {chunk.chunk_index}"
                  f"  |  score {chunk.relevance_score}  |  {chunk.source_type}"
                  f"  |  date {chunk.document_date}")
            print(f"    Task IDs : {chunk.task_ids}")
            print(f"    Personas : {chunk.personas_found}")
            print(f"    Text     : {chunk.chunk_text[:120]}{'…' if len(chunk.chunk_text) > 120 else ''}")
        print("\n" + "═" * 70)
        print("PROMPT METADATA")
        print("═" * 70)
        print(json.dumps(prompt["metadata"], indent=2))
        return prompt

    # ── Save prompt payloads ─────────────────────────────────────────────────
    if save_prompts:
        PROMPT_OUTPUT_DIR.mkdir(exist_ok=True)
        ts   = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        out  = PROMPT_OUTPUT_DIR / f"extraction_prompt_{ts}.json"
        out.write_text(json.dumps(prompt, indent=2, ensure_ascii=False), encoding="utf-8")
        log.info("Prompt payload saved to %s", out)

    # ── Print summary ────────────────────────────────────────────────────────
    meta = prompt["metadata"]
    print("\n" + "═" * 70)
    print("EXTRACTION PROMPT — READY FOR LLM")
    print("═" * 70)
    print(f"  Chunks in prompt  : {meta['chunk_count']}")
    print(f"  Source files      : {', '.join(meta['source_files'])}")
    print(f"  Source types      : {', '.join(meta['source_types'])}")
    print(f"  Task IDs covered  : {', '.join(meta['task_ids_seen']) or 'none'}")
    print(f"  Generated at      : {meta['generated_at']}")
    print("═" * 70)
    print("\nSYSTEM PROMPT (first 300 chars):")
    print(prompt["system"][:300] + "…")
    print("\nUSER MESSAGE (first 500 chars):")
    print(prompt["user"][:500] + "…")
    print()

    return prompt


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="SJ Project Planner Agent — Azure AI Search Simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python sj_search_ingestor.py\n"
            "  python sj_search_ingestor.py --input-dir SJ_Input_Samples\n"
            "  python sj_search_ingestor.py --dry-run\n"
            "  python sj_search_ingestor.py --top-k 12 --save-prompts\n"
        ),
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        metavar="DIR",
        help="Root folder to scan for .txt source files (default: %(default)s)",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=TOP_K_CHUNKS,
        metavar="N",
        help="Number of top-ranked chunks to include in the LLM prompt (default: %(default)s)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print chunk summaries and prompt metadata without full prompt output",
    )
    parser.add_argument(
        "--save-prompts",
        action="store_true",
        help=f"Save prompt payloads as JSON to ./{PROMPT_OUTPUT_DIR}/",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args   = _parse_args(argv)
    result = run_pipeline(
        input_dir    = args.input_dir,
        top_k        = args.top_k,
        dry_run      = args.dry_run,
        save_prompts = args.save_prompts,
    )
    return 0 if result is not None else 1


if __name__ == "__main__":
    sys.exit(main())
