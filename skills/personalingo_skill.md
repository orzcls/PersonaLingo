# PersonaLingo - Personalized IELTS Speaking Corpus Generator

## Skill Description
This skill enables you to generate a personalized IELTS speaking corpus for any student by conducting a structured questionnaire and applying AI-driven corpus generation.

The workflow combines MBTI personality profiling, interest analysis, and IELTS exam preferences to produce a fully personalized speaking corpus including anchor stories, topic bridges, vocabulary upgrades, sentence patterns, and practice exercises.

## Trigger Conditions
Activate this skill when the user:
- Asks for IELTS speaking preparation materials
- Wants a personalized speaking corpus or vocabulary list
- Mentions IELTS oral exam preparation
- Asks for speaking practice exercises
- Requests help with IELTS Part 1, Part 2, or Part 3 topics

## Workflow

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
Create 8-10 sentence patterns matching their MBTI communication style.

## Output Format
Present the complete corpus in a structured format with clear sections:
1. **Student Profile Summary** — MBTI type, interests, target score
2. **Anchor Stories** — Each with keywords and versatility topics list
3. **Topic Bridges** — Grouped by category (People/Places/Events/Objects/Abstract), each with bridge sentence + sample answer
4. **Vocabulary Upgrades** — Table with basic word → advanced alternatives + example sentence
5. **Sentence Patterns** — Template + example + when to use
6. **Practice Exercises** — 5 exercises with thinking guides and model answers

## Quality Guidelines
- All content must feel personal and authentic to the student
- Answers should sound natural, not rehearsed or formulaic
- Vocabulary should match the target band score
- Communication style should consistently reflect their MBTI preferences
- Each anchor must be versatile enough to bridge to multiple topics
- Bridge sentences should feel like natural conversation transitions
- Practice exercises should progressively build confidence
