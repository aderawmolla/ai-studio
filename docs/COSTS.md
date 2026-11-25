# Costs and measurement

Measured from **`logs/runs.jsonl`** on the production run for *The Smile That Carried Him* (Nov 2025). Dollar cost on used APIs: **$0** (free tiers). List-price equivalents are indicative only.

## Model API summary

| Metric | Value |
|--------|------:|
| `model_call` lines | 88 |
| Successful | 87 |
| Failed | 1 (early TTS schema test) |
| Total API wall time (sum of `latency_ms`) | ~483 s (~8 min) |

| Model | Calls | Stage (typical) |
|-------|------:|-----------------|
| `gemini-3.8-flash-tts` | 45 | narration |
| `@cf/black-forest-labs/flux-1-schnell` | 42 | image (refs, keyframes, end card) |
| `gemini-2.5-flash-preview-tts` | 1 | narration (failed) |

## Per-stage notes

| Stage | Where it ran | GPU? | Notes |
|-------|--------------|------|-------|
| Storyboard | Local JSON | No | Authored + validated in repo |
| References + keyframes | Cloudflare Workers AI | No (hosted) | ~3–17 s per image in logs |
| Narration | Gemini API | No | 5–45 s per line observed |
| Video (Ken Burns) | Local FFmpeg | No | CPU only |
| Music | Local mock or imported WAV | No* | *Kaggle ACE would add GPU minutes if used |
| Assembly | Local FFmpeg | No | Concat, duck, subs, loudnorm |

## GPU minutes (open models)

| Model | Used in repo? | GPU minutes |
|-------|---------------|-------------|
| Wan 2.2 TI2V | No API wired | 0 logged |
| ACE-Step 1.5 | No API wired; optional manual file | 0 logged |

If you ran Kaggle notebooks off-repo, add a row here with session length and what files you copied into `outputs/`.

## Frontier comparison

No paid Omni Flash / Lyria access in this project. Open/free stack: FLUX schnell + Gemini TTS + FFmpeg Ken Burns.

## How to refresh this file

```bash
source .venv/bin/activate
python3 -c "
import json
from collections import Counter
models=Counter(); n=0; ms=0
for line in open('logs/runs.jsonl'):
    r=json.loads(line)
    ex=r.get('extra') or {}
    if ex.get('type')!='model_call': continue
    n+=1
    models[ex.get('model','?')]+=1
    ms+=ex.get('latency_ms') or 0
print('calls',n,'models',dict(models),'total_s',round(ms/1000,1))
"
```