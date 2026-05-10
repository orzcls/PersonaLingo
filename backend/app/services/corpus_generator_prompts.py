"""
语料生成引擎 - LLM Prompt 模板集合
所有5步生成的 prompt 在此集中管理，便于维护和调优
"""


PERSONA_SYSTEM = """You are an expert IELTS speaking coach who specializes in personality-based learning. 
You analyze students' MBTI personality type and personal interests to create a speaking persona profile.
Always respond in valid JSON format."""

PERSONA_USER = """Based on the following comprehensive student profile, create a detailed speaking persona analysis.

## Student Profile
- MBTI Type: {mbti_type}
- MBTI Dimensions: {mbti_dimensions}
- Interests/Tags: {interests_tags}
- Interest Descriptions: {interests_descriptions}
- Target Band Score: {target_score}

## Band Strategy
- Level: {band_label}
- Vocabulary Level: {vocab_level}
- Grammar Complexity: {grammar_complexity}
- Fluency Style: {fluency_style}

## Additional Context (Real Life Experiences)
{persona_context}

## Task
Analyze this student's speaking tendencies based on their MBTI dimensions:
- E/I: Extraverted speakers tend to be expansive and energetic; Introverted speakers are more reflective and precise
- S/N: Sensing speakers use concrete details; Intuitive speakers use abstract connections and metaphors
- T/F: Thinking speakers are logical and analytical; Feeling speakers are empathetic and value-driven
- J/P: Judging speakers are structured and conclusive; Perceiving speakers are flexible and exploratory

IMPORTANT: Incorporate the student's real experiences with people, objects, and places into the persona.
Use their background for authentic storytelling anchors.

Generate a JSON response with this exact structure:
{{
    "mbti_type": "{mbti_type}",
    "speaking_style": {{
        "tone": "description of their natural speaking tone",
        "structure_preference": "how they naturally organize answers",
        "detail_type": "what kind of details they gravitate toward",
        "emotional_expression": "how they express feelings in speech"
    }},
    "strengths": ["strength1", "strength2", "strength3"],
    "challenges": ["challenge1", "challenge2"],
    "recommended_strategies": ["strategy1", "strategy2", "strategy3"],
    "interest_connections": {{
        "primary_themes": ["theme1", "theme2"],
        "story_angles": ["angle1", "angle2", "angle3"],
        "vocabulary_domains": ["domain1", "domain2"]
    }},
    "band_adaptation": {{
        "target": "{target_score}",
        "focus_areas": ["area1", "area2"],
        "natural_fit": "description of how personality aligns with target band requirements"
    }}
}}"""


ANCHORS_SYSTEM = """You are an expert IELTS speaking coach specializing in the "4-Anchor Method" - 
a technique where students develop 3-4 personal stories that can be flexibly connected to any IELTS topic.
Each anchor should be a vivid, emotionally resonant personal story from different life domains.
Always respond in valid JSON format."""

ANCHORS_USER = """Create 4 personal anchor stories for this student based on their persona profile.

## Student Persona
{persona_json}

## Band Strategy
- Target: {target_score}
- Vocabulary Level: {vocab_level}
- Grammar Complexity: {grammar_complexity}
- Timing: P1 target {p1_target_seconds}s, safe stop strategy: {safe_stop_strategy}

## Requirements for Anchor Stories
1. Each anchor must feel authentic and personal (based on their interests and personality)
2. Cover different life domains: academic/work, hobby/passion, relationship/social, growth/challenge
3. Each anchor should be connectable to at least 5-8 different IELTS topics
4. Include specific sensory details and emotional moments
5. Language complexity must match the target band:
   - Band 6.0: Simple, direct language with basic connectors
   - Band 6.5: Some variety in vocabulary, occasional complex sentences
   - Band 7.0: Wide range of vocabulary, varied sentence structures
   - Band 7.5+: Sophisticated language, natural idiomatic expressions

Generate a JSON array with exactly 4 anchor stories:
[
    {{
        "id": "anchor_1",
        "label": "short descriptive label (2-4 words)",
        "story": "The full anchor story (150-200 words at target band level). Include specific details, emotions, and a clear narrative arc. Mark <!-- SAFE_STOP --> at a natural pause point around {p1_target_seconds} seconds.",
        "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
        "emotion": "primary emotion (e.g., pride, curiosity, determination)",
        "connectable_topics": ["topic1", "topic2", "topic3", "topic4", "topic5", "topic6"]
    }}
]

IMPORTANT: The stories should reflect the student's MBTI personality in how they tell stories:
- E types: More animated, social context emphasized
- I types: More reflective, inner experience emphasized  
- S types: Rich in concrete sensory details
- N types: Focus on meanings, connections, and possibilities
- T types: Logical progression, cause-effect highlighted
- F types: Emotional journey, personal values highlighted
- J types: Clear structure, decisive conclusions
- P types: Open-ended exploration, multiple perspectives"""


BRIDGES_SYSTEM = """You are an expert IELTS speaking coach specializing in the "21-Topic Bridge Method".
This technique teaches students to connect any IELTS topic back to their personal anchor stories using a 3-step bridge:
1. Bridge Sentence (引入句): A natural transition from the topic to the personal story
2. Sample Answer (回答主体): The main response incorporating the anchor story
3. Safe Stop Point (安全停止点): A natural conclusion point within time limits

Always respond in valid JSON format."""

BRIDGES_USER = """Create bridge connections between the student's anchors and these IELTS topics.

## Student's Anchor Stories
{anchors_json}

## Topics to Bridge (select the most relevant 8-10 to bridge)
{topics_json}

## Band Strategy
- Target: {target_score}
- P1 Target Time: {p1_target_seconds} seconds
- P1 Max Time: {p1_max_seconds} seconds
- Safe Stop Strategy: {safe_stop_strategy}
- Grammar Structures to Use: {grammar_structures}
- Vocabulary Upgrade Ratio: {upgrade_ratio}
- Fluency Fillers: {filler_strategy}

## Requirements
1. For each topic, find the BEST matching anchor and create a natural bridge
2. Bridge sentence must feel spontaneous, not forced
3. Sample answer must:
   - Stay within {p1_max_seconds} seconds when read at natural pace (~150 words/min for speaking)
   - Include a <!-- SAFE_STOP --> marker at approximately {p1_target_seconds} seconds
   - Use grammar structures appropriate for {target_score}
   - Feel natural for this student's MBTI speaking style
4. Include 2-3 techniques used (e.g., "personal anecdote", "comparison", "sensory detail")

Generate a JSON array:
[
    {{
        "topic_id": "original topic id",
        "topic_title": "topic title",
        "category": "topic category",
        "anchor_id": "best matching anchor id",
        "bridge_sentence": "A natural 1-2 sentence transition from the topic to the anchor story",
        "sample_answer": "Full answer (80-120 words for P1, 200-250 words for P2). Include <!-- SAFE_STOP --> marker.",
        "safe_stop_point": "The exact phrase/sentence where the student can naturally stop if interrupted",
        "techniques_used": ["technique1", "technique2"]
    }}
]

CRITICAL - 25-Second Rule:
- P1 answers MUST have a natural stopping point before 25 seconds
- After <!-- SAFE_STOP --> provide a brief wrap-up phrase (1 sentence max)
- If examiner interrupts, the answer should still sound complete at the SAFE_STOP point"""


VOCABULARY_SYSTEM = """You are an expert IELTS vocabulary coach who specializes in personalized vocabulary upgrades.
You help students replace basic words with more sophisticated alternatives that match their personality and target band.
Always respond in valid JSON format."""

VOCABULARY_USER = """Generate personalized vocabulary upgrades for this student.

## Student Persona
{persona_json}

## Anchor Stories (for context)
{anchors_json}

## Band Strategy
- Target: {target_score}
- Vocabulary Level: {vocab_level}
- Upgrade Ratio: {upgrade_ratio} (proportion of words to upgrade)
- Words to AVOID: {vocab_avoid}

## Requirements
1. Generate 15-20 vocabulary upgrades
2. Each upgrade should:
   - Replace a commonly overused basic word
   - The upgrade word must feel NATURAL for this student's personality and interests
   - Include a specific usage context from their anchor stories or interest areas
   - Match the target band level (don't over-upgrade for lower bands)
3. Categories should include: emotions, actions, descriptions, connectors, opinions
4. Upgrade ratio of {upgrade_ratio} means: for every 10 words in speech, approximately {upgrade_count} should be upgraded

Generate a JSON array:
[
    {{
        "basic_word": "the common/overused word",
        "upgrade": "the better alternative",
        "context": "A specific sentence using the upgrade word in the student's context",
        "category": "emotions|actions|descriptions|connectors|opinions"
    }}
]

IMPORTANT for different bands:
- 6.0: Upgrades should be common "less common" words (interesting→fascinating, good→beneficial)
- 6.5: Mix of less common and topic-specific terms (difficult→daunting, help→facilitate)
- 7.0: Include some idiomatic expressions and precise word choices (very important→paramount, understand→grasp the nuance)
- 7.5+: Sophisticated collocations and nuanced vocabulary (think about→contemplate, show→epitomize)"""


PATTERNS_SYSTEM = """You are an expert IELTS speaking coach who creates personalized sentence patterns.
You design templates that match the student's MBTI communication style so they sound natural, not memorized.
Always respond in valid JSON format."""

PATTERNS_USER = """Generate MBTI-matched sentence patterns for this student.

## Student Persona
{persona_json}

## Band Strategy
- Target: {target_score}
- Grammar Complexity: {grammar_complexity}
- Grammar Structures: {grammar_structures}
- Fluency Fillers: {filler_strategy}

## Requirements
1. Generate 10-12 sentence patterns
2. Each pattern must:
   - Match the student's MBTI communication style
   - Be appropriate for the target band's grammar complexity level
   - Include a formula (with blanks), an example, and when to use it
   - Feel natural and unrehearsed when spoken
3. Pattern categories should cover:
   - Opening (how to start an answer)
   - Development (how to expand with details)
   - Transition (how to shift between points)
   - Conclusion (how to wrap up naturally)
   - Opinion (how to express views)
   - Comparison (how to contrast ideas)

Generate a JSON array:
[
    {{
        "name": "Pattern Name (descriptive)",
        "formula": "The sentence template with [BLANKS] for variable parts",
        "example": "A complete example using the pattern with the student's context",
        "when_to_use": "Specific IELTS situations where this pattern works best"
    }}
]

MBTI-specific pattern design:
- E types: Patterns that invite elaboration and social stories ("That reminds me of when...")
- I types: Patterns that allow reflective depth ("What I find particularly meaningful is...")
- S types: Patterns anchored in concrete experience ("The thing I remember most vividly is...")
- N types: Patterns that draw abstract connections ("It's interesting how [X] connects to...")
- T types: Analytical patterns ("The reason behind this is...", "If I analyze it logically...")
- F types: Value-driven patterns ("What matters most to me is...", "I deeply believe that...")
- J types: Structured patterns ("There are [X] main reasons...", "To sum up,...")
- P types: Exploratory patterns ("On one hand... but then again...", "It depends on...")"""


PRACTICES_SYSTEM = """You are an expert IELTS speaking practice designer. 
You create guided practice exercises that help students internalize their personal corpus.
Each practice includes thinking guides, step-by-step approach, and a model answer.
Always respond in valid JSON format."""

PRACTICES_USER = """Design practice exercises for this student based on their corpus.

## Student Persona
{persona_json}

## Anchor Stories
{anchors_json}

## Available Bridges (sample)
{bridges_sample_json}

## Band Strategy
- Target: {target_score}
- P1 Target Time: {p1_target_seconds}s
- Safe Stop Strategy: {safe_stop_strategy}

## Requirements
1. Generate 5-6 practice exercises
2. Each exercise should:
   - Use a real IELTS topic (different from bridged ones if possible)
   - Include thinking guide questions to help the student connect to their anchors
   - Provide step-by-step approach for structuring the answer
   - Include a model answer at the target band level
   - Have a self-check checklist
3. Vary difficulty: 2 easier (familiar topics), 2 medium, 2 challenging (unexpected topics)

Generate a JSON array:
[
    {{
        "topic_title": "The IELTS question",
        "thinking_guide": [
            "Which of your anchors connects to this topic?",
            "What specific detail/emotion can you use?",
            "What bridge sentence will you use?"
        ],
        "steps": [
            "Step 1: Start with [specific opening pattern]",
            "Step 2: Bridge to your [anchor] using...",
            "Step 3: Add detail about...",
            "Step 4: Conclude with..."
        ],
        "model_answer": "Full model answer at target band level (with <!-- SAFE_STOP --> marker)",
        "checklist": [
            "Did I stay within {p1_target_seconds} seconds?",
            "Did I use at least one upgraded vocabulary item?",
            "Did I connect naturally to my anchor story?",
            "Did I use a pattern from my corpus?"
        ]
    }}
]"""
