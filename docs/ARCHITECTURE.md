# PersonaLingo Architecture

## System Overview

PersonaLingo is a full-stack web application that generates personalized IELTS speaking corpora using Large Language Models, driven by MBTI personality analysis and user interest profiling.

## High-Level Architecture

```
┌─────────────────────┐     ┌─────────────────────┐     ┌──────────────────┐
│    Frontend          │     │    Backend           │     │   LLM Provider   │
│    (Vue 3 SPA)      │────▶│    (FastAPI)         │────▶│  (OpenAI/GLM-4)  │
│                     │◀────│                     │◀────│                  │
└─────────────────────┘     └─────────────────────┘     └──────────────────┘
        :5173                       :8000
```

## Backend Architecture

### Layer Structure

```
app/
├── main.py          # FastAPI app initialization, CORS, router registration
├── config.py        # Environment configuration (Pydantic Settings)
├── storage.py       # In-memory session storage
├── models/          # Pydantic data models
│   ├── questionnaire.py  # MBTI questions, interest tags, user profile
│   └── corpus.py         # Corpus modules (anchor, bridge, vocabulary, etc.)
├── routers/         # API endpoint handlers
│   ├── questionnaire.py  # /api/questionnaire/* endpoints
│   ├── corpus.py         # /api/corpus/* endpoints
│   └── skill.py          # /api/skill/* endpoints
├── services/        # Business logic
│   ├── mbti_analyzer.py      # MBTI type calculation from answers
│   ├── corpus_generator.py   # LLM-powered corpus generation
│   └── skill_exporter.py     # Agent Skill export (MD/JSON/OpenAPI)
└── templates/       # Jinja2 templates for skill export
```

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/questionnaire/mbti-questions` | Get MBTI assessment questions |
| GET | `/api/questionnaire/interest-tags` | Get interest category tags |
| POST | `/api/questionnaire/submit` | Submit questionnaire & get profile |
| POST | `/api/corpus/generate` | Generate personalized corpus |
| GET | `/api/corpus/{session_id}` | Retrieve generated corpus |
| GET | `/api/skill/formats` | List available export formats |
| POST | `/api/skill/export` | Export workflow as Agent Skill |

### Data Flow

1. User completes questionnaire → Profile created (MBTI + interests + IELTS prefs)
2. Profile submitted to corpus generator → LLM generates 5 corpus modules
3. Generated corpus stored in session → Frontend displays visualization
4. User requests skill export → Skill exporter packages workflow

## Frontend Architecture

### Component Structure

```
src/
├── views/              # Page-level components (route targets)
│   ├── Home.vue            # Landing page
│   ├── Questionnaire.vue   # Multi-step questionnaire flow
│   ├── Generating.vue      # Generation progress display
│   ├── Corpus.vue          # Corpus visualization (5 modules)
│   └── Export.vue           # Skill export interface
├── components/
│   ├── questionnaire/      # Questionnaire step components
│   │   ├── MBTIStep.vue
│   │   ├── InterestStep.vue
│   │   └── IELTSStep.vue
│   ├── corpus/             # Corpus display components
│   │   ├── PersonaCard.vue
│   │   ├── AnchorSection.vue
│   │   ├── BridgeSection.vue
│   │   ├── VocabularySection.vue
│   │   └── PatternSection.vue
│   ├── Layout.vue          # App shell layout
│   ├── LoadingSpinner.vue
│   └── ProgressBar.vue
├── stores/
│   └── questionnaire.js    # Pinia store for app state
├── api/
│   └── index.js            # Axios API client
└── router/
    └── index.js            # Vue Router configuration
```

### State Management (Pinia)

The `questionnaire` store manages the full application state:
- User profile (MBTI answers, interests, IELTS preferences)
- Generation status and progress
- Generated corpus data
- Export state

## Corpus Generation Pipeline

The corpus consists of 5 interconnected modules:

1. **Persona Card** — Summarizes user's communication style based on MBTI
2. **Anchor Stories** — 3-4 deeply personal stories with topic mapping
3. **Bridge Strategies** — Techniques to connect anchors to any IELTS topic
4. **Vocabulary Upgrades** — Interest-specific advanced word alternatives
5. **Sentence Patterns** — Reusable grammatical structures for fluency

## Agent Skill Export

Three export formats are supported:

| Format | Target Platform | Structure |
|--------|----------------|-----------|
| Markdown | Trae, Cursor, IDE agents | Structured prompt with workflow steps |
| JSON Schema | GPTs, Coze, Dify | Machine-readable workflow definition |
| OpenAPI 3.0 | HTTP-capable agents | Full API specification |

## Deployment

### Development
- Backend: `uvicorn` with hot-reload on port 8000
- Frontend: `vite` dev server on port 5173

### Production (Docker)
- Backend: Python 3.11-slim container
- Frontend: Multi-stage build (Node → Nginx)
- Nginx reverse proxy handles `/api/` routing to backend

## Security Considerations

- API keys stored in environment variables, never committed
- CORS configured for specific origins
- No user authentication required (single-session tool)
- Session data stored in-memory (ephemeral)
