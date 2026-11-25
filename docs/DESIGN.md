# Design

## Film

**Title:** The Smile That Carried Him  
**Story:** A young man tries many paths in the city, feels invisible and exhausted, and keeps going when he remembers his promise to his mother.

## Audience and intent

(from `storyboard.json`)

| | |
|--|--|
| **Who** | Young Ethiopians and diaspora viewers on phones, early-career setbacks, distance from family |
| **Where** | Vertical-first (9:16), also 16:9 reframe |
| **Intent** | Encouragement when progress feels unseen; quiet joy in keeping faith with family |

**Visual:** Hand-painted gouache, warm palette, stylized faces (not photoreal, no real likenesses).  
**Audio:** Amharic narration (Gemini TTS), English burn-in subtitles, instrumental underscore ducked under voice.

## Shot intent

Every shot has a `reason` field in `storyboard.json` (e.g. establish the promise, show invisibility in the city, mother memory beat). Reviewers can trace story beats to those fields.

## Prototypes

### Radio cut (audio animatic)

**Goal:** Test story pacing before expensive visuals.

**How we produced it:** Gemini TTS per shot → `outputs/narration/*.wav` → concatenated `full.wav` + placeholder/mock music, then listened without picture (or black screen via `assemble` with stills omitted).

**User test 1 (≥3 people from audience):**  
*Record here before submission: names/roles (e.g. Slack cohort), what confused them, what landed, and **exact storyboard edits** (shot order, narration lines, durations). Do not invent feedback.*

| Tester | Reaction | Change made |
|--------|----------|-------------|
| | | |
| | | |
| | | |

### Near-final cut

**Artifact:** `outputs/final/heritage_vertical.mp4` / `heritage_horizontal.mp4`

**User test 2 (≥3 people):**  
*Record after a watchable assembly: sync, subtitle readability, emotional beat on mother/smile ending.*

| Tester | Reaction | Change made |
|--------|----------|-------------|
| | | |
| | | |
| | | |

## Known creative tensions (from edit)

- Shot `duration_seconds` were first estimated (~2.3 words/s); real Amharic TTS lengths differ → sync work by measuring WAV and updating the storyboard, then re-running `videos` + `assemble`.
- Ken Burns motion can feel repetitive or over-zoomed on some shots; simpler `camera_movement` in the storyboard helps.
- Character consistency relies on repeated `style_block` text, not FLUX reference-image conditioning (see `docs/EXPERIMENTS.md`).