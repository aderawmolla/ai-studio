# Assignment Brief (Requirements Source)

> **Note:** No separate original assignment PDF or markdown was found in the repository at project start. Requirements below are extracted from `initial_prompt.txt` and the implementation specification. **Replace or append the official brief here unchanged when you receive it from your instructor.**

## Assignment title

**AI-Content Generation: The Heritage Short**

## Objective

Build a Python application that orchestrates an AI-powered film-production pipeline from a heritage topic and creative instructions to finished deliverables.

## Mandatory outputs

| Deliverable | Requirement |
|-------------|-------------|
| Film duration | 60–90 seconds |
| Vertical video | 9:16 MP4 |
| Horizontal video | 16:9 MP4, reframed (not stretched) |
| Narration | Selected language |
| Subtitles | English |
| Music | Original background music with narration ducking |
| End card | AI-generated |

## Workflow stages

1. Project configuration (topic, audience, languages, style, duration, aspect ratios)
2. Story and script generation (historical claims vs. creative interpretation)
3. Storyboard generation and validation
4. Reference and keyframe image generation
5. Video generation per shot
6. Audio (narration, music, subtitles)
7. Media validation
8. FFmpeg assembly (vertical + horizontal reframe)
9. Final validation report

## Technical expectations

- Reproducible pipeline with caching and selective regeneration
- Storyboard as central data contract (`storyboard.json` + JSON Schema)
- Provider abstraction (Gemini, FLUX, Wan, TTS, ACE-Step; mocks for testing)
- CLI for individual stages and full `generate`
- Resume from last successful stage on failure
- Documentation: README, architecture, design, experiments, failures, costs, ethics, submission checklist
- Tests without expensive model calls (mock pipeline)
- Audience testing: radio cut + near-final (≥3 people each); document changes

## Ethics and evidence

- No real likeness/voice without consent
- AI disclosure and model license awareness
- Do not fabricate experiments, costs, or consent records

## Ambiguities (to confirm with instructor)

1. Exact rubric weights and submission format (zip, repo link, video upload).
2. Whether heritage topic is fixed or student-chosen.
3. Required narration languages list and default.
4. Minimum resolution / codec for final MP4.
5. Whether Wan 2.2 must be self-hosted or API is acceptable.