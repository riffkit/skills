# Riffkit skills — named by what you want to make

[![Live skill](https://img.shields.io/badge/skill-riffkit.ai%2FSKILL.md-6d4ae0)](https://riffkit.ai/SKILL.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-3b82f6)](LICENSE)

**Don't copy. Riff.** [Riffkit](https://riffkit.ai) changes the outfit, place, product or person in your video: your shots, cuts and timing stay. Or it turns a winning short video into yours: same formula (the hook, the pacing, the emotional beats), your story, your product and your character. Riffkit never re-uploads the source clip: your video is a new render, though flat graphics from the source (cards, stickers) can carry over into it.

This repo holds **entry points named after the job**, so your agent finds the skill from how you actually phrase the request. Each one is the same skill under a different name: the body is identical to [`riffkit.ai/SKILL.md`](https://riffkit.ai/SKILL.md) and is **generated daily**, so it can't drift from the live product.

## The skills

| Skill | Ask it when you'd say | |
| --- | --- | --- |
| **`change-outfit-in-video`** | *"Change the outfit (or background, person, product) in my video."* | [`change-outfit-in-video/SKILL.md`](change-outfit-in-video/SKILL.md) |
| **`ugc-ad-creative`** | *"Make a UGC ad for my product."* | [`ugc-ad-creative/SKILL.md`](ugc-ad-creative/SKILL.md) |
| **`riff-viral-tiktok`** | *"Turn this winning TikTok into mine."* | [`riff-viral-tiktok/SKILL.md`](riff-viral-tiktok/SKILL.md) |

Real Swap results: [a new outfit](https://riffkit.ai/blog/change-outfit-in-video-ai), [a new background](https://riffkit.ai/blog/change-video-background-ai).

## Install

```
npx skills add riffkit/skills
```

Then just ask, in plain language:

```
change the outfit in ./my-video.mp4 to a white linen suit, keep every shot
riff https://www.tiktok.com/@user/video/123 into an ad for my product, in Spanish
```

A Swap re-renders your video shot for shot and changes only what you name; an Adapt makes new footage of the winning formula, in any of 10 languages. Your agent quotes the price before it spends credits, then hands you a link to the finished video, plus a caption and hashtags. Riffkit is hosted, so there's no local GPU and no models to download. ChatGPT has Riffkit in its [plugin directory](https://chatgpt.com/plugins/plugin_asdk_app_6ac1d83b7c0081918475085dec6634c5); Claude and other MCP apps add the connector `https://mcp.riffkit.ai/mcp` ([setup](https://riffkit.ai/mcp#set-up)). **Generating videos needs a [Riffkit account](https://riffkit.ai)**, billed in credits by the second of video.

## How these files are made

`scripts/render_variants.py` fetches the canonical `SKILL.md`, its `HEARTBEAT.md` and the reference files [`SKILL.json`](https://riffkit.ai/SKILL.json) lists from riffkit.ai, and writes `<name>/SKILL.md`, `HEARTBEAT.md` and `references/` for each entry in [`variants.json`](variants.json) — the canonical body verbatim, under the variant's own name and description. A [daily workflow](.github/workflows/sync-skills.yml) reruns it and commits any change.

So: **never edit a generated `<name>/` file.** Change [`variants.json`](variants.json) for naming, or the canonical skill for the body. Dropping an entry from `variants.json` deletes its directory on the next run. Without the Riffkit CLI, each variant's one-click sign-in sends `client=<skill name>`, used only for attribution (`riffkit login` labels its sign-ins `cli`).

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
