# Ethics, consent, labelling, licences

## Story and consent

Film uses **fictional stylized characters** (young man “Biruk”, mother, illustrated settings). No real person’s face, likeness, or cloned voice (`storyboard.json` → `creative_direction`, `metadata.ethics_notes`).

**Consent record:** Not required for this film because no identifiable real individual is depicted or voiced. If you later use a relative’s photo or clone a voice, add signed consent here **before** generation.

## AI disclosure

- On-screen: end card includes **“Made with AI”** (`final.end_card_text` in storyboard).
- Distribution: enable the platform **AI / synthetic media** label when posting (YouTube, TikTok, Meta).
- Walkthrough and README state that visuals, voice, music, and end card are AI-assisted.

## Models and licences (this project)

| Component | Model / tool | Licence / terms |
|-----------|--------------|-------------------|
| Narration | Gemini TTS (`gemini-3.8-flash-tts`) | Google AI / Gemini API terms |
| Images | FLUX.1 schnell via Cloudflare Workers AI | BFL + Cloudflare usage terms |
| Video motion | FFmpeg Ken Burns (not Wan weights in-repo) | N/A |
| Music | Mock generator and/or imported WAV | If ACE-Step: MIT per project card; if mock: synthetic FFmpeg tones |
| Assembly | FFmpeg | LGPL/GPL per your build |

Check current terms before commercial use beyond this assignment.

## Privacy

Family-specific private details were kept out of Cloudflare/Gemini prompts where possible; story is fictionalized perseverance narrative.

## Data sent to APIs

Prompts include scene descriptions and Amharic narration text sent to Google and Cloudflare. Review each provider’s data-use policy for training/logging.