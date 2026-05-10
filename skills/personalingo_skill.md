# PersonaLingo Skill

> AI-powered personalized IELTS corpus generator and learning assistant

## Installation

```bash
npx skills add orzcls/personalingo-skill
```

## Overview

PersonaLingo is a full-stack AI system that generates **personalized IELTS speaking corpus** tailored to each learner's personality (MBTI), interests, background, and target band score. It employs a **Three-Stage Distillation Pipeline** (Research → Framework → Generation) to produce high-quality, export-ready Skill Packs that any AI Agent can consume for tutoring.

### Core Capabilities

- Personalized corpus generation via 7-step LLM distillation pipeline
- QMD RAG engine (Query-Match-Decide) for intelligent corpus retrieval
- Dynamic IELTS topic bank with seasonal auto-sync
- Conversational coaching with style learning
- Portable Skill Pack export (4 artifacts) for agent integration

## Usage Modes

### Mode A: Use Pre-built Skill Packs

For agents that need to quickly start tutoring without running the full pipeline.

**When to use**: You already have a generated corpus (corpus_id) and just need the skill artifacts.

#### Steps

1. **List available skills**
   ```
   GET /api/distill/skill/{corpus_id}/runnable
   ```
   Response:
   ```json
   {
     "data": {
       "corpus_id": "abc123",
       "path": "/path/to/output",
       "files": ["Skill.md", "corpus.json", "runtime_protocol.md", "prompts/README.md"]
     },
     "error": null
   }
   ```

2. **Download skill pack as zip**
   ```
   GET /api/distill/skill/{corpus_id}/runnable/download
   ```
   Returns: `personalingo_skill_{corpus_id}.zip`

3. **Preview Skill.md online**
   ```
   GET /api/distill/skill/{corpus_id}/runnable/preview?format=markdown
   ```

4. **Load the Skill Pack**
   - Read `corpus.json` for full corpus data + learner profile + capability framework
   - Follow `runtime_protocol.md` for RAG retrieval & response generation protocol
   - Use `prompts/` templates for conversation and assessment scenarios

### Mode B: Full Pipeline (End-to-End)

For agents that need to create a personalized corpus from scratch.

**When to use**: New learner onboarding — no existing corpus.

#### Step 1: Diagnose — Generate Questionnaire

```
POST /api/distill/diagnose
Content-Type: application/json

{
  "text": "I'm a college student preparing for IELTS, I want to get 7.0 in speaking but I'm not fluent..."
}
```

Response:
```json
{
  "data": {
    "questions": [
      {"id": "q1", "text": "How soon will you take IELTS?", "type": "single", "options": ["30 days", "3 months", "6 months", "No exam planned"]},
      {"id": "q2", "text": "Target score?", "type": "single", "options": ["6.0", "6.5", "7.0", "7.5+"]},
      {"id": "q3", "text": "Weakest area? (multi-select)", "type": "multi", "options": ["Vocabulary", "Fluency", "Pronunciation", "Logic"]}
    ],
    "suggested_score": "7.0",
    "rationale": "Based on self-description fluency concerns"
  },
  "error": null
}
```

#### Step 2: Guided Conversation (Optional)

Use conversation APIs to collect additional context from the learner:

```
POST /api/conversation/{corpus_id}/chat
Content-Type: application/json

{
  "message": "I'm interested in aviation and competitive programming",
  "context": []
}
```

#### Step 3: Trigger Distillation

```
POST /api/distill/run?questionnaire_id={id}&include_research=true
```

Response:
```json
{
  "data": {
    "questionnaire_id": "q_abc123",
    "include_research": true,
    "stages": ["research", "framework", "persona", "anchors", "bridges", "vocabulary", "patterns"],
    "stream_url": "/api/corpus/generate/q_abc123/stream"
  },
  "error": null
}
```

The 7-step pipeline runs in background:
1. **Research** — Aggregate questionnaire + materials + conversations → `learner_profile`
2. **Framework** — Ability × Scenario × Goal matrix distillation → `capability_framework`
3. **Persona** — MBTI dimension analysis + communication style inference
4. **Anchors** — 3-4 personal core stories
5. **Bridges** — 21-topic bridging connecting anchors to IELTS question bank
6. **Vocabulary** — Band-appropriate vocabulary list (25-30 items)
7. **Patterns** — MBTI-matched sentence patterns (8-10 templates)

> **Fallback**: Stage 1/2 failures do not block Stage 3. The system auto-degrades to legacy 5-step flow.

#### Step 4: Export Skill Pack

```
GET /api/distill/skill/{corpus_id}/runnable
```

#### Step 5: Download & Use

```
GET /api/distill/skill/{corpus_id}/runnable/download
```

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/distill/diagnose` | POST | Generate diagnostic questionnaire from free text |
| `/api/distill/run` | POST | Trigger 7-step distillation (background task) |
| `/api/distill/skill/{corpus_id}/runnable` | GET | Export runnable skill pack (4 artifacts) |
| `/api/distill/skill/{corpus_id}/runnable/download` | GET | Download skill pack as zip |
| `/api/distill/skill/{corpus_id}/runnable/preview` | GET | Preview Skill.md (markdown or HTML) |
| `/api/conversation/{corpus_id}/chat` | POST | Send message, get AI coach reply |
| `/api/conversation/{corpus_id}/history` | GET | Retrieve conversation history |
| `/api/conversation/{corpus_id}/extract` | POST | Extract new materials from conversation |
| `/api/conversation/{corpus_id}/merge` | POST | Merge extracted materials into corpus |
| `/api/conversation/{corpus_id}/style` | GET | Get learner style statistics |
| `/api/topics/meta` | GET | Current season, staleness flag, config status |
| `/api/topics/scrape` | POST | Run full topic bank sync pipeline |
| `/api/topics/backfill-p3?limit=N` | POST | Backfill linked P3 for existing P2 topics |

## Output Format

Each exported skill pack contains 4 artifacts:

```
{corpus_id}/
├── Skill.md              # Personalized learning skill document
├── corpus.json           # Full corpus data with QMD-tagged vocabulary
│   └── .skill_manifest   # { name, version, pipeline, stages[] }
├── runtime_protocol.md   # Agent runtime protocol (RAG retrieval, response generation)
└── prompts/
    └── README.md         # Prompt templates for conversation & assessment
```

### corpus.json Structure

```json
{
  "skill_manifest": {
    "name": "personalingo",
    "version": "3.0",
    "pipeline": "three_stage_distill",
    "stages": [
      {"name": "research", "status": "completed"},
      {"name": "framework", "status": "completed"},
      {"name": "persona", "status": "completed"},
      {"name": "anchors", "status": "completed"},
      {"name": "bridges", "status": "completed"},
      {"name": "vocabulary", "status": "completed"},
      {"name": "patterns", "status": "completed"}
    ]
  },
  "learner_profile": { "background": "...", "language_samples": [], "weakness_signals": [], "goal_vector": {} },
  "capability_framework": { "pain_points": [], "lift_paths": [] },
  "anchors": [],
  "bridges": [],
  "vocabulary": [],
  "patterns": []
}
```

## Example Workflow

Complete end-to-end example for an AI tutor agent:

```python
import httpx

BASE = "http://localhost:9849"

# Step 1: Diagnose the learner
resp = httpx.post(f"{BASE}/api/distill/diagnose", json={
    "text": "I'm an INTJ aviation student. I want IELTS 7.0 but struggle with fluency and topic variety."
})
questionnaire = resp.json()["data"]
questionnaire_id = "q_new_user"  # assigned by system or from prior step

# Step 2: (Optional) Guided conversation to enrich profile
httpx.post(f"{BASE}/api/conversation/{corpus_id}/chat", json={
    "message": "I competed in ICPC and I love system architecture design"
})

# Step 3: Run full distillation
resp = httpx.post(f"{BASE}/api/distill/run", params={
    "questionnaire_id": questionnaire_id,
    "include_research": True
})
stream_url = resp.json()["data"]["stream_url"]
# Monitor progress via stream_url...

# Step 4: Export skill pack
resp = httpx.get(f"{BASE}/api/distill/skill/{corpus_id}/runnable")
files = resp.json()["data"]["files"]

# Step 5: Download zip for offline use
httpx.get(f"{BASE}/api/distill/skill/{corpus_id}/runnable/download")

# Now load Skill.md + corpus.json + runtime_protocol.md to start tutoring!
```

## Dynamic Topic Bank Sync

The skill also supports automatic IELTS topic bank refresh:

```
POST /api/topics/scrape
```

This fetches latest P1/P2 topics for the current exam season and derives linked P3 questions. See the API Reference above for related endpoints.

## Requirements

- Python 3.11+ backend running at `http://localhost:9849`
- LLM API key configured (OpenAI or Anthropic)
- (Optional) Search provider key for topic bank sync
