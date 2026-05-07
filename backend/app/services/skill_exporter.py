import json
import yaml


class SkillExporter:
    """AI Agent Skill 导出服务"""

    SUPPORTED_FORMATS = ["markdown", "json", "openapi"]

    def export(self, format: str, corpus_data: dict = None) -> dict:
        """
        根据格式导出 Skill 文件
        返回: {"filename": "...", "content": "...", "mime_type": "..."}
        """
        if format == "markdown":
            return self._export_markdown(corpus_data)
        elif format == "json":
            return self._export_json(corpus_data)
        elif format == "openapi":
            return self._export_openapi()
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_markdown(self, corpus_data: dict = None) -> dict:
        """生成 Markdown Skill 文件（适用于 Trae/Cursor/类IDE Agent）"""
        content = self._build_markdown_content(corpus_data)
        return {
            "filename": "personalingo_skill.md",
            "content": content,
            "mime_type": "text/markdown",
        }

    def _export_json(self, corpus_data: dict = None) -> dict:
        """生成 JSON Schema Skill 文件（适用于 GPTs/Coze/Dify）"""
        schema = self._build_json_schema(corpus_data)
        return {
            "filename": "personalingo_skill.json",
            "content": json.dumps(schema, indent=2, ensure_ascii=False),
            "mime_type": "application/json",
        }

    def _export_openapi(self) -> dict:
        """生成 OpenAPI 文档（适用于有后端调用能力的 Agent）"""
        spec = self._build_openapi_spec()
        return {
            "filename": "personalingo_openapi.yaml",
            "content": yaml.dump(spec, default_flow_style=False, allow_unicode=True, sort_keys=False),
            "mime_type": "application/x-yaml",
        }

    # ──────────────────────────────────────────────
    #  Markdown Builder
    # ──────────────────────────────────────────────
    def _build_markdown_content(self, corpus_data: dict = None) -> str:
        sections = [
            self._md_header(),
            self._md_trigger(),
            self._md_workflow(),
            self._md_output_format(),
            self._md_quality_guidelines(),
        ]
        if corpus_data:
            sections.append(self._md_corpus_snapshot(corpus_data))
        return "\n\n".join(sections)

    @staticmethod
    def _md_header() -> str:
        return """# PersonaLingo - Personalized IELTS Speaking Corpus Generator

## Skill Description
This skill enables you to generate a personalized IELTS speaking corpus for any student by conducting a structured questionnaire and applying AI-driven corpus generation.

The workflow combines MBTI personality profiling, interest analysis, and IELTS exam preferences to produce a fully personalized speaking corpus including anchor stories, topic bridges, vocabulary upgrades, sentence patterns, and practice exercises."""

    @staticmethod
    def _md_trigger() -> str:
        return """## Trigger Conditions
Activate this skill when the user:
- Asks for IELTS speaking preparation materials
- Wants a personalized speaking corpus or vocabulary list
- Mentions IELTS oral exam preparation
- Asks for speaking practice exercises
- Requests help with IELTS Part 1, Part 2, or Part 3 topics"""

    @staticmethod
    def _md_workflow() -> str:
        return """## Workflow

### Step 1: Collect MBTI Profile
Ask the user to either:
- **Option A:** State their known MBTI type (e.g., "I'm an INTP")
- **Option B:** Answer 12 quick questions to determine their type

If Option B, ask these questions one by one:

1. At a party, do you: (a) interact with many people, including strangers, or (b) interact with a few people you know well?
2. When learning something new, do you prefer: (a) hands-on experience and examples, or (b) theoretical concepts and ideas?
3. When making decisions, do you: (a) prioritize logic and consistency, or (b) consider people's feelings and circumstances?
4. Do you prefer to: (a) have things decided and settled, or (b) keep options open and flexible?
5. In social situations, do you: (a) feel energized by being around others, or (b) need time alone to recharge?
6. Do you tend to focus on: (a) concrete facts and details, or (b) patterns and possibilities?
7. Which is more important: (a) being truthful even if it hurts, or (b) being tactful and considerate?
8. Do you prefer to: (a) follow a schedule and plan, or (b) be spontaneous and adaptable?
9. When meeting new people, do you: (a) easily start conversations, or (b) wait for others to approach you?
10. When reading, do you prefer: (a) literal and straightforward writing, or (b) figurative and symbolic writing?
11. In a conflict, do you: (a) analyze the problem objectively, or (b) empathize with everyone involved?
12. Is your workspace usually: (a) neat and organized, or (b) flexible with multiple projects spread out?

Calculate the result:
- Questions 1, 5, 9 → E (option a) vs I (option b)
- Questions 2, 6, 10 → S (option a) vs N (option b)
- Questions 3, 7, 11 → T (option a) vs F (option b)
- Questions 4, 8, 12 → J (option a) vs P (option b)
- For each dimension, the option selected more determines the letter

### Step 2: Collect Interest Profile
Ask the user to:
1. Select 3-8 interests from: Photography, Music, Coding, Gaming, Reading, Travel, Sports, Cooking, Art, Film, Nature, Writing, Dance, Fitness, Technology, Science, History, Philosophy, Fashion, Animals
2. Describe their top 3 hobbies/experiences in 2-3 sentences each (include what they do, why they love it, a memorable moment)

### Step 3: Collect IELTS Preferences
Ask the user:
1. Which topic types concern you most? (People, Places, Events, Objects, Abstract)
2. What's your target band score? (6.0, 6.5, 7.0, 7.5+)
3. When is your exam? (month/year)

### Step 4: Generate Personal Profile
Based on collected information, create a student persona:
- MBTI type and communication style implications
- Core interests and experiences that can become "anchor stories"
- Target performance level

### Step 5: Generate Anchor Stories (3-4)
Create 3-4 personal "anchor stories" based on the student's experiences. Each anchor:
- Is based on their REAL interests
- Can connect to 5+ different IELTS topics
- Includes sensory details and emotional elements
- Matches their natural communication style

### Step 6: Generate Topic Bridges
For common IELTS P1/P2 topics, create bridge responses that:
- Naturally connect each topic to one of their anchors
- Use their preferred communication style
- Are 25-35 seconds when spoken (4-6 sentences)
- Target their specified band score level

### Step 7: Generate Vocabulary Upgrades
Create 25-30 vocabulary upgrades:
- Interest-specific advanced vocabulary
- General high-frequency word replacements
- Connector upgrades
- Emotion/description upgrades

### Step 8: Generate Sentence Patterns
Create 8-10 sentence patterns matching their MBTI communication style."""

    @staticmethod
    def _md_output_format() -> str:
        return """## Output Format
Present the complete corpus in a structured format with clear sections:
1. **Student Profile Summary** — MBTI type, interests, target score
2. **Anchor Stories** — Each with keywords and versatility topics list
3. **Topic Bridges** — Grouped by category (People/Places/Events/Objects/Abstract), each with bridge sentence + sample answer
4. **Vocabulary Upgrades** — Table with basic word → advanced alternatives + example sentence
5. **Sentence Patterns** — Template + example + when to use
6. **Practice Exercises** — 5 exercises with thinking guides and model answers"""

    @staticmethod
    def _md_quality_guidelines() -> str:
        return """## Quality Guidelines
- All content must feel personal and authentic to the student
- Answers should sound natural, not rehearsed or formulaic
- Vocabulary should match the target band score
- Communication style should consistently reflect their MBTI preferences
- Each anchor must be versatile enough to bridge to multiple topics
- Bridge sentences should feel like natural conversation transitions
- Practice exercises should progressively build confidence"""

    @staticmethod
    def _md_corpus_snapshot(corpus_data: dict) -> str:
        lines = ["## Embedded Corpus Data (for reference)"]
        if "user_profile" in corpus_data:
            profile = corpus_data["user_profile"]
            lines.append(f"- **MBTI:** {profile.get('mbti', 'N/A')}")
            lines.append(f"- **Interests:** {', '.join(profile.get('interests', []))}")
        if "anchors" in corpus_data:
            lines.append(f"- **Anchor stories:** {len(corpus_data['anchors'])}")
        if "bridges" in corpus_data:
            lines.append(f"- **Topic bridges:** {len(corpus_data['bridges'])}")
        if "vocabulary" in corpus_data:
            lines.append(f"- **Vocabulary upgrades:** {len(corpus_data['vocabulary'])}")
        return "\n".join(lines)

    # ──────────────────────────────────────────────
    #  JSON Schema Builder
    # ──────────────────────────────────────────────
    def _build_json_schema(self, corpus_data: dict = None) -> dict:
        schema = {
            "skill_name": "PersonaLingo",
            "version": "1.0.0",
            "description": "AI-powered personalized IELTS speaking corpus generator",
            "author": "Xiangbo Cheng",
            "repository": "https://github.com/username/PersonaLingo",
            "workflow": {
                "steps": [
                    {
                        "id": "collect_mbti",
                        "name": "Collect MBTI Profile",
                        "type": "user_input",
                        "description": "Determine the student's MBTI personality type via test or direct input",
                        "input_schema": {
                            "mode": {"type": "string", "enum": ["test", "direct"], "description": "Whether to run the 12-question test or accept a known type"},
                            "answers": {"type": "object", "description": "Map of question_id to 'a'/'b' (required when mode=test)"},
                            "type_code": {"type": "string", "pattern": "^[EI][SN][TF][JP]$", "description": "4-letter MBTI code (required when mode=direct)"},
                        },
                    },
                    {
                        "id": "collect_interests",
                        "name": "Collect Interest Profile",
                        "type": "user_input",
                        "description": "Gather the student's interest tags and personal hobby descriptions",
                        "input_schema": {
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "minItems": 3,
                                "maxItems": 8,
                                "description": "Selected interest tags from the predefined list",
                            },
                            "descriptions": {
                                "type": "array",
                                "items": {"type": "string"},
                                "minItems": 1,
                                "maxItems": 3,
                                "description": "2-3 sentence descriptions of top hobbies",
                            },
                        },
                    },
                    {
                        "id": "collect_ielts",
                        "name": "Collect IELTS Preferences",
                        "type": "user_input",
                        "description": "Gather exam-specific preferences including topics, target score, and date",
                        "input_schema": {
                            "topic_types": {
                                "type": "array",
                                "items": {"type": "string", "enum": ["People", "Places", "Events", "Objects", "Abstract"]},
                                "description": "Topic categories the student is most concerned about",
                            },
                            "target_score": {
                                "type": "string",
                                "enum": ["6.0", "6.5", "7.0", "7.5+"],
                                "description": "Target IELTS band score",
                            },
                            "exam_date": {
                                "type": "string",
                                "description": "Planned exam date (month/year)",
                            },
                        },
                    },
                    {
                        "id": "generate_corpus",
                        "name": "Generate Personalized Corpus",
                        "type": "llm_generation",
                        "description": "Use all collected data to generate a complete personalized speaking corpus",
                        "depends_on": ["collect_mbti", "collect_interests", "collect_ielts"],
                        "output_schema": {
                            "persona": {"type": "object", "description": "Student profile summary"},
                            "anchors": {"type": "array", "description": "3-4 anchor stories"},
                            "bridges": {"type": "array", "description": "Topic bridge responses"},
                            "vocabulary": {"type": "array", "description": "25-30 vocabulary upgrades"},
                            "patterns": {"type": "array", "description": "8-10 sentence patterns"},
                            "practice": {"type": "array", "description": "5 practice exercises"},
                        },
                    },
                ],
            },
            "prompts": {
                "anchor_generation": "You are an expert IELTS speaking coach. Based on the student's MBTI type ({mbti_type}) and their personal interests/experiences, create {count} anchor stories. Each anchor should be a vivid personal narrative that can naturally connect to at least 5 different IELTS topics. Include sensory details, emotional elements, and match the student's communication style.",
                "bridge_generation": "For each IELTS topic below, create a natural bridge response that connects the topic to one of the student's anchor stories. The bridge should feel conversational, be 4-6 sentences (25-35 seconds spoken), and target band {target_score}.",
                "vocabulary_generation": "Create a personalized vocabulary upgrade list for an IELTS candidate with interests in {interests}. Include: interest-specific advanced vocabulary, general high-frequency replacements, connector upgrades, and emotion/description upgrades. Target band {target_score}.",
                "pattern_generation": "Create sentence patterns that match the {mbti_type} communication style. Each pattern should include a template, an example using the student's interests, and guidance on when to use it.",
                "practice_generation": "Create 5 deliberate practice exercises for an IELTS speaking candidate. Each exercise should include a prompt, a thinking guide, and a model answer using the student's anchor stories and vocabulary.",
            },
            "interest_tags": [
                "Photography", "Music", "Coding", "Gaming", "Reading",
                "Travel", "Sports", "Cooking", "Art", "Film",
                "Nature", "Writing", "Dance", "Fitness", "Technology",
                "Science", "History", "Philosophy", "Fashion", "Animals",
            ],
        }
        if corpus_data:
            schema["embedded_corpus"] = corpus_data
        return schema

    # ──────────────────────────────────────────────
    #  OpenAPI Spec Builder
    # ──────────────────────────────────────────────
    def _build_openapi_spec(self) -> dict:
        return {
            "openapi": "3.0.3",
            "info": {
                "title": "PersonaLingo API",
                "description": "AI-powered personalized IELTS speaking corpus generator. This API allows agents to conduct questionnaires, generate corpora, and export skill files.",
                "version": "1.0.0",
                "contact": {
                    "name": "Xiangbo Cheng",
                },
            },
            "servers": [
                {"url": "http://localhost:8000", "description": "Local development"},
            ],
            "paths": {
                "/api/questionnaire/mbti-questions": {
                    "get": {
                        "operationId": "getMBTIQuestions",
                        "summary": "Get MBTI test questions and type list",
                        "tags": ["Questionnaire"],
                        "responses": {
                            "200": {
                                "description": "MBTI questions and type list",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "questions": {"type": "array", "items": {"$ref": "#/components/schemas/MBTIQuestion"}},
                                                "types": {"type": "array", "items": {"$ref": "#/components/schemas/MBTIType"}},
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
                "/api/questionnaire/interest-tags": {
                    "get": {
                        "operationId": "getInterestTags",
                        "summary": "Get available interest tags",
                        "tags": ["Questionnaire"],
                        "responses": {
                            "200": {
                                "description": "List of interest tag strings",
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "array", "items": {"type": "string"}},
                                    },
                                },
                            },
                        },
                    },
                },
                "/api/questionnaire/submit": {
                    "post": {
                        "operationId": "submitQuestionnaire",
                        "summary": "Submit complete questionnaire",
                        "tags": ["Questionnaire"],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/QuestionnaireSubmission"},
                                },
                            },
                        },
                        "responses": {
                            "200": {
                                "description": "Submission result with questionnaire ID",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/QuestionnaireResponse"},
                                    },
                                },
                            },
                        },
                    },
                },
                "/api/corpus/generate": {
                    "post": {
                        "operationId": "generateCorpus",
                        "summary": "Generate personalized corpus from questionnaire",
                        "tags": ["Corpus"],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "questionnaire_id": {"type": "string"},
                                        },
                                        "required": ["questionnaire_id"],
                                    },
                                },
                            },
                        },
                        "responses": {
                            "200": {
                                "description": "Generated corpus data",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/Corpus"},
                                    },
                                },
                            },
                        },
                    },
                },
                "/api/corpus/{corpus_id}": {
                    "get": {
                        "operationId": "getCorpus",
                        "summary": "Get corpus by ID",
                        "tags": ["Corpus"],
                        "parameters": [
                            {
                                "name": "corpus_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                            },
                        ],
                        "responses": {
                            "200": {
                                "description": "Corpus data",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/Corpus"},
                                    },
                                },
                            },
                        },
                    },
                },
                "/api/skill/formats": {
                    "get": {
                        "operationId": "getSkillFormats",
                        "summary": "Get available skill export formats",
                        "tags": ["Skill Export"],
                        "responses": {
                            "200": {
                                "description": "List of export formats",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "formats": {
                                                    "type": "array",
                                                    "items": {"$ref": "#/components/schemas/ExportFormat"},
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
                "/api/skill/export": {
                    "post": {
                        "operationId": "exportSkill",
                        "summary": "Export skill file in specified format",
                        "tags": ["Skill Export"],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "format": {"type": "string", "enum": ["markdown", "json", "openapi"]},
                                            "corpus_id": {"type": "string", "description": "Optional corpus ID to embed data"},
                                        },
                                        "required": ["format"],
                                    },
                                },
                            },
                        },
                        "responses": {
                            "200": {
                                "description": "Exported skill file",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "filename": {"type": "string"},
                                                "content": {"type": "string"},
                                                "mime_type": {"type": "string"},
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            "components": {
                "schemas": {
                    "MBTIQuestion": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "dimension": {"type": "string"},
                            "question": {"type": "string"},
                            "option_a": {"type": "string"},
                            "option_b": {"type": "string"},
                        },
                    },
                    "MBTIType": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string"},
                            "description": {"type": "string"},
                        },
                    },
                    "QuestionnaireSubmission": {
                        "type": "object",
                        "properties": {
                            "mbti": {
                                "type": "object",
                                "properties": {
                                    "mode": {"type": "string", "enum": ["test", "direct"]},
                                    "answers": {"type": "object"},
                                    "type_code": {"type": "string"},
                                },
                            },
                            "interests": {
                                "type": "object",
                                "properties": {
                                    "tags": {"type": "array", "items": {"type": "string"}},
                                    "descriptions": {"type": "array", "items": {"type": "string"}},
                                },
                            },
                            "ielts": {
                                "type": "object",
                                "properties": {
                                    "topic_types": {"type": "array", "items": {"type": "string"}},
                                    "target_score": {"type": "string"},
                                    "exam_date": {"type": "string"},
                                },
                            },
                        },
                    },
                    "QuestionnaireResponse": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "mbti_result": {"type": "object"},
                            "interests": {"type": "object"},
                            "ielts": {"type": "object"},
                            "created_at": {"type": "string"},
                        },
                    },
                    "Corpus": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "user_profile": {"type": "object"},
                            "anchors": {"type": "array"},
                            "bridges": {"type": "array"},
                            "vocabulary": {"type": "array"},
                            "patterns": {"type": "array"},
                            "created_at": {"type": "string"},
                        },
                    },
                    "ExportFormat": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "extension": {"type": "string"},
                            "icon": {"type": "string"},
                        },
                    },
                },
            },
        }
