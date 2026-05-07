# PersonaLingo

> AI-Powered Personalized IELTS Speaking Corpus Generator with Agent Skill Export

PersonaLingo transforms your personality (MBTI), interests, and IELTS goals into a tailored speaking corpus — complete with anchor stories, topic bridges, vocabulary upgrades, and sentence patterns. Export the entire workflow as an AI Agent Skill for any platform.

## Features

- **MBTI-Driven Personalization** — 12-question assessment or direct type selection shapes your communication style
- **Smart Anchor Strategy** — Generates 3-4 personal stories that bridge to 20+ IELTS topics
- **Vocabulary & Pattern Engine** — Upgrades basic words with interest-specific advanced alternatives
- **AI Agent Skill Export** — Package the entire workflow as a reusable skill for Trae, Cursor, GPTs, Coze, Dify, or any LLM agent
- **Multiple Export Formats** — Markdown, JSON Schema, OpenAPI specification

## Architecture

```
Frontend (Vue 3 + Tailwind)  ←→  Backend (FastAPI)  ←→  LLM API (OpenAI/GLM-4)
     │                                │
     └── Questionnaire Flow           ├── MBTI Analysis
     └── Corpus Visualization         ├── Corpus Generation (5 modules)
     └── Skill Export UI              └── Skill Export (3 formats)
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue 3, Vite, Tailwind CSS, Pinia, Vue Router |
| Backend | FastAPI, Pydantic, OpenAI SDK |
| LLM | GPT-4o / GLM-4 (configurable) |
| Export | Markdown, JSON Schema, OpenAPI 3.0 |

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- OpenAI API key (or compatible endpoint)

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API key
python run.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` to start generating your personalized corpus.

### Docker (One-command)
```bash
docker-compose up --build
```

## How It Works

1. **Questionnaire** — Complete MBTI assessment + interest profiling + IELTS preferences
2. **AI Generation** — LLM creates personalized anchors, bridges, vocabulary, and patterns
3. **Visualization** — Interactive dark-theme corpus display with filtering and practice mode
4. **Export** — Download corpus as HTML/JSON, or export workflow as an Agent Skill

## Agent Skill Export

The unique feature of PersonaLingo is the ability to export the entire corpus generation workflow as a reusable AI Agent Skill:

- **Markdown Skill** — Drop into Trae, Cursor, or any IDE with agent support
- **JSON Schema** — Import into GPTs, Coze, Dify as a structured workflow
- **OpenAPI Spec** — Enable any agent with HTTP capabilities to call the API directly

See `skills/` directory for example exports.

## Project Structure

```
PersonaLingo/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   ├── routers/
│   │   ├── services/
│   │   └── templates/
│   ├── requirements.txt
│   └── .env.example
├── frontend/          # Vue 3 frontend
│   ├── src/
│   │   ├── views/
│   │   ├── components/
│   │   ├── stores/
│   │   ├── api/
│   │   └── router/
│   └── package.json
├── skills/            # Example skill exports
├── docs/              # Documentation & screenshots
├── docker-compose.yml
├── README.md
└── LICENSE
```

## Screenshots

_Coming soon_

## Author

**Xiangbo Cheng** — CS graduate with competitive programming background (ICPC, National contests) and hands-on experience in AI systems, recommendation engines, and platform engineering.

## License

MIT License - see [LICENSE](LICENSE) for details.
