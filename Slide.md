# Presentation Content: VibeFinder 2.0

This file is not the slide deck itself. It is the full content that should go into a strong 5-7 minute presentation.

Recommended length: `7 slides`
Recommended time: about `5:30` to `6:30`
Recommended format: simple slides with large visuals, short bullets, and you speak the details

---

## Slide 1 - Title / Hook

### Slide title
`VibeFinder 2.0: An Explainable AI Music Recommendation System`

### On-slide subtitle
`Natural-language music requests -> retrieval -> ranking -> explanation -> reliability checks`

### On-slide bullets
- Extends my earlier transparent music recommender
- Adds natural-language understanding and retrieval
- Shows not just recommendations, but why they were chosen
- Includes reliability checks, trace logging, and evaluation

### Visuals to show
- App screenshot from the Streamlit frontend
- Or the architecture diagram in the repo

### What to say
“Hi, my project is VibeFinder 2.0. It started as a transparent content-based music recommender, and I extended it into a more complete applied AI system. The main idea is that a user can type a natural-language request like ‘Need calm music for late-night coding,’ and the system will interpret the request, retrieve supporting context, rank songs, explain the recommendation, and then check its own reliability.”

### Why this slide matters
This slide gives the audience the big picture immediately: what the system is, what makes it AI-enhanced, and why it is more than just a basic recommendation script.

---

## Slide 2 - Original Project and What I Extended

### Slide title
`Base Project -> Extended AI System`

### On-slide bullets
- Original project: transparent content-based music recommender
- Original input: structured preferences
  - genre
  - mood
  - target energy
  - acoustic preference
- Original output: ranked songs with explicit scoring reasons
- Limitation: it was explainable, but not conversational or context-aware

### New features added
- Natural-language query parsing
- Multi-source retrieval
- Agent-style intermediate trace
- Specialized explanation styles
- Reliability suite and evaluation harness

### What to say
“The base project was already a transparent recommender, which means it could rank songs using explicit scoring rules and explain those rules. But it relied on structured input. That meant a user had to already know how to express their request in the system’s format. My extension was to turn it into a more realistic AI system: it now handles natural-language requests, retrieves supporting evidence, exposes its reasoning steps, and checks whether the result is reliable.”

### Key phrase to include verbally
“I did not replace the original project. I extended it into a working AI pipeline.”

---

## Slide 3 - How the System Works

### Slide title
`System Architecture`

### On-slide bullets
- User enters a natural-language request
- Parser extracts:
  - genre
  - mood
  - target energy
  - activity tags
  - exclusions
- Retriever checks:
  - `song_knowledge_base.json`
  - `query_support_documents.json`
- Recommender scores songs using metadata + retrieval bonuses
- Reliability layer reruns the pipeline and checks consistency
- Output includes recommendations, evidence, warnings, and trace steps

### Visuals to show
- The architecture diagram from:
  - `assets/architecture/music-ai-system-architecture.svg`
  - or `.png`

### What to say
“This is the pipeline. First, the user types a request. Then the parser converts that into structured intent. After that, the retriever looks for supporting evidence from two sources: the song knowledge base and the support-document layer. Then the recommender combines metadata scoring with retrieval bonuses. Finally, the reliability layer checks whether the output is grounded and consistent. The important point is that retrieval actually changes the ranking, and the system can explain each step.”

### Good emphasis line
“This is a system, not just a model call.”

---

## Slide 4 - Live Demo

### Slide title
`System Demo`

### Best demo format
Use the Streamlit frontend:

```bash
streamlit run streamlit_app.py
```

### Demo plan
Show `2` strong examples and `1` edge case.

### Demo example 1
Input:
`Need calm music for late-night coding`

Expected points to mention:
- parser identifies calm/focus/late-night intent
- retrieval matches focus-oriented evidence
- recommendations include:
  - `Midnight Coding`
  - `Focus Flow`
  - `Library Rain`
- reliability status should be good

### Demo example 2
Input:
`Need high-energy music for the gym`

Expected points to mention:
- parser identifies intense/high-energy workout intent
- support-doc retrieval boosts workout interpretation
- recommendations include:
  - `Gym Hero`
  - `Storm Runner`
  - `Neon Pulse Circuit`
- specialized “Hype Trainer” style is a good visual feature here

### Demo example 3: edge case
Input:
`Need classical music for an intense workout`

Expected points to mention:
- this is intentionally contradictory
- top songs still reflect workout intensity
- `Glass Morning` is preserved by the genre safeguard
- reliability emits a warning about thin catalog support

### What to say during demo
“I want to show both a normal case and a difficult case. In the normal case, the system should feel smart and grounded. In the difficult case, I want it to be honest rather than overconfident. That is why the edge case matters: it proves the system can surface tradeoffs instead of hiding them.”

### If the UI fails
Use backup CLI command:

```bash
python -m src.main query "Need calm music for late-night coding" --show-trace --specialization auto
```

---

## Slide 5 - What Makes This an Applied AI System

### Slide title
`AI Features I Added`

### On-slide sections

#### 1. Multi-source retrieval
- Uses:
  - `data/song_knowledge_base.json`
  - `data/query_support_documents.json`
- Helps interpret synonym-heavy prompts
- Example:
  - `"spin class intervals"` is mapped to workout/cardio intent

#### 2. Agent-style workflow
- Intermediate steps are visible
- Examples of observable steps:
  - `parse_query`
  - `retrieve_support_docs`
  - `plan_with_support_docs`
  - `retrieve_song_evidence`
  - `rank_recommendations`
  - `self_check`

#### 3. Specialized behavior
- Style-card-based explanations
- Profiles include:
  - `focus_coach`
  - `hype_trainer`
  - `reflective_curator`
- This makes output measurably different from the baseline

#### 4. Reliability and evaluation
- Consistency rerun
- Warning system
- Evaluation harness
- Tests

### What to say
“The project goes beyond a recommender because it includes multiple AI system ideas working together. It has retrieval, planning-like intermediate steps, constrained specialized behavior, and reliability evaluation. That combination is what makes it feel like an applied AI system rather than a single algorithm.”

---

## Slide 6 - Results and Reliability

### Slide title
`How I Measured Whether It Works`

### On-slide bullets
- `18/18` tests passed
- Reliability suite passed all `4/4` benchmark scenarios
- Optional evaluation harness showed:
  - multi-source `hit@3` improved from `5/7` to `7/7`
  - average confidence: `0.95`
  - average trace steps: `7.00`
  - specialization compliance: `100%`

### Suggested chart/table
Small comparison table:

| Metric | Baseline | Enhanced |
|---|---:|---:|
| Hit@3 | 5/7 | 7/7 |
| Trace visibility | none | 7 steps average |
| Specialized style compliance | n/a | 100% |

### What to say
“I wanted to show measurable improvement, not just say the system felt better. The clearest improvement is in the optional evaluation harness, where multi-source retrieval improves hit@3 from 5 out of 7 to 7 out of 7. I also verified that reliability scenarios pass, and that the specialized explanation layer is actually being applied consistently.”

### Important framing
“The goal was not perfect recommendations. The goal was a system that is inspectable, testable, and more reliable than a basic baseline.”

---

## Slide 7 - What I Learned / Reflection

### Slide title
`What I Learned as an AI Engineer`

### On-slide bullets
- AI systems need more than “reasonable output”
- Retrieval quality matters as much as ranking logic
- Reliability and transparency increase trust
- Small data and lexical retrieval create clear limits
- Building guardrails is part of AI engineering, not an extra

### Include this short reflection paragraph
“This project shows that I approach AI engineering as systems work, not just model output work. I care about building tools that are explainable, testable, and honest about their limits. Instead of stopping at ‘it gives a reasonable answer,’ I focused on retrieval quality, observable reasoning steps, reliability checks, and clear documentation so another person can inspect, trust, and improve the system.”

### AI collaboration points to say
- Helpful AI suggestion:
  - structuring the project as a pipeline with separate stages
- Flawed AI suggestion:
  - early documentation drafts overstated what the system could do
- Lesson:
  - always verify AI-generated claims against real tests and outputs

### Strong closing line
“What I’m most proud of is not just that the system recommends songs, but that it explains itself, checks itself, and makes its limitations visible.”

---

## Optional Backup Slide - If There Is Time

### Slide title
`Why the UI Exists`

### On-slide bullets
- Streamlit app makes the system easier to demo live
- UI highlights:
  - query composer
  - recommendation spotlight
  - retrieval evidence
  - reliability side panel
  - benchmark/evaluation tabs
- Useful both for presentation and for grading

### What to say
“I also built a frontend so the project could be demonstrated more like a product and less like a terminal script. That made it easier to show the user request, the retrieved evidence, the final recommendations, and the reliability outputs in one place.”

---

## Recommended Presentation Flow

If you want a simple 6-minute structure, use this:

### 0:00 - 0:40
Slide 1
- Introduce the project and the big idea

### 0:40 - 1:20
Slide 2
- Explain the original project and what was extended

### 1:20 - 2:00
Slide 3
- Walk through the system architecture

### 2:00 - 3:45
Slide 4
- Live demo

### 3:45 - 4:40
Slide 5
- Highlight the major AI features you added

### 4:40 - 5:25
Slide 6
- Show measurable results and reliability outcomes

### 5:25 - 6:10
Slide 7
- End with reflection and what it says about you as an AI engineer

---

## Presenter Tips

- Do not put all the details on the slides. Keep the slides visually clean and use your speaking to add detail.
- For the demo, show only 2-3 prompts. Too many examples will waste time.
- Always include the contradictory example because it demonstrates responsibility and reliability.
- When discussing bonus features, mention both implementation and measurable impact.
- If you get nervous, memorize this one sentence:
  - “The main contribution of this project is turning a transparent recommender into a more complete AI system with retrieval, observable reasoning, and reliability checks.”

---

## Best Final Slide Message

If you want one final sentence to end on, use:

“VibeFinder 2.0 demonstrates the kind of AI engineering I want to do: practical systems that are useful, explainable, and honest about uncertainty.”
