# Riffkit skills — named by what you want to make

[![Live skill](https://img.shields.io/badge/skill-riffkit.ai%2FSKILL.md-6d4ae0)](https://riffkit.ai/SKILL.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-3b82f6)](LICENSE)

**Don't copy. Riff.** [Riffkit](https://riffkit.ai) takes a winning short video, studies its *formula* — the hook, the pacing, the emotional beats — and generates a brand-new video around your product, your character, and your story. The source clip is never re-uploaded; what comes out is your own original.

This repo holds **entry points named after the job**, so your agent finds the skill from how you actually phrase the request. Each one is the same skill under a different name: the body is identical to [`riffkit.ai/SKILL.md`](https://riffkit.ai/SKILL.md) and is **generated daily**, so it can't drift from the live product.

## The skills

| Skill | Ask it when you'd say | |
| --- | --- | --- |
| **`ugc-ad-creative`** | *"Make a UGC ad for my product."* | [`ugc-ad-creative/SKILL.md`](ugc-ad-creative/SKILL.md) |
| **`riff-viral-tiktok`** | *"Turn this winning TikTok into mine."* | [`riff-viral-tiktok/SKILL.md`](riff-viral-tiktok/SKILL.md) |

## Install

```
npx skills add riffkit/skills
```

Then just ask, in plain language:

```
riff https://www.tiktok.com/@user/video/123 into an ad for my product, in Spanish
```

Your agent handles the rest: source → formula → new footage → your product & character → captions, cover, hashtags. Riffkit is hosted, so there's no MCP server, no local GPU, and no models to download — **generating videos needs a [Riffkit account](https://riffkit.ai)**, billed by the second of finished video.

## How these files are made

`scripts/render_variants.py` fetches the canonical `SKILL.md` from riffkit.ai and writes one `<name>/SKILL.md` per entry in [`variants.json`](variants.json) — the canonical body verbatim, under the variant's own name and description. A [daily workflow](.github/workflows/sync-skills.yml) reruns it and commits any change.

So: **never edit a generated `<name>/SKILL.md`.** Change [`variants.json`](variants.json) for naming, or the canonical skill for the body. Dropping an entry from `variants.json` deletes its directory on the next run. Each variant's one-click sign-in sends `client=<skill name>`, used only for attribution.

There is intentionally **no `SKILL.md` at this repo's root** — the skills CLI stops at a root `SKILL.md` and never scans subdirectories, which would hide every variant from default discovery.

## Canonical skill

The full product under its own name — plus the docs, examples, and demo — lives in **[riffkit/skill](https://github.com/riffkit/skill)**. The source of truth for all of it is [`riffkit.ai/SKILL.md`](https://riffkit.ai/SKILL.md), which your agent reads live.

## Links

- App & sign-up — https://riffkit.ai
- Pricing — https://riffkit.ai/pricing
- Base skill & docs — https://github.com/riffkit/skill
- Live skill (source of truth) — https://riffkit.ai/SKILL.md

---

Don't copy. Riff.

## License

[MIT](LICENSE) — covers this repo's files (the skill's integration spec + docs). The Riffkit service itself is a hosted product.
