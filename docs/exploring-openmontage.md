# Exploring OpenMontage

**Repository:** https://github.com/calesthio/OpenMontage  
**Explored:** 2026-04-16

## What It Is

OpenMontage is an open-source, agentic video production system that transforms plain-language descriptions into complete edited videos. It runs on top of AI coding assistants (Claude Code, Cursor, Copilot, Windsurf, Codex) and orchestrates the full production lifecycle: research, scripting, asset generation, editing, and rendering.

The key distinction from simpler AI video tools: it produces genuinely edited videos from real motion footage and generated clips, not slideshows or animated stills. A purpose-built slideshow risk scorer (6 dimensions) actively prevents the latter.

**Stats:** 2.2k stars, 413 forks, Python 91.4%, AGPLv3 license, active Discussions community.

## Architecture

### Three-Layer Knowledge Model

```
Layer 1: Tool registry        — what exists, availability, costs (queried at runtime)
Layer 2: Skills (skills/)     — 124+ Markdown files for conventions and quality standards
Layer 3: Tech packs (.agents/skills/) — provider-specific generation techniques
```

Agents read Layer 3 skills *before* calling generation tools — these contain techniques that measurably improve output quality per provider.

### 12 Production Pipelines (YAML manifests in pipeline_defs/)

| Pipeline | Purpose |
|---|---|
| animated-explainer | Research-based explainers with narration and generated visuals |
| animation | Pure generative animation sequences |
| avatar-spokesperson | Talking head with avatar generation |
| cinematic | Cinematic trailers and teasers |
| clip-factory | High-volume short-form clip production |
| documentary-montage | Real-footage montages from free stock and open archives |
| hybrid | Mixed generative and real-footage workflows |
| localization-dub | Language localization and dubbing |
| podcast-repurpose | Podcast-to-video repurposing |
| screen-demo | Screen recording with narration |
| talking-head | Direct-to-camera video production |
| framework-smoke | Internal test pipeline |

Each manifest defines: budget, timeout, stages with director skills, tool requirements, checkpoint (human approval) gates, success criteria per stage, and supported playbooks.

### 52 Production Tools

Organized across video generation, audio, images, and post-production. Key integrations:

- **Video:** Kling, Runway Gen-4, Veo 3, Grok, local GPU (WAN 2.1, Hunyuan, CogVideo, LTX-Video), Pexels/Pixabay/Wikimedia stock
- **Images:** FLUX, Imagen, DALL-E 3, Recraft, local diffusion, free stock
- **Audio/TTS:** ElevenLabs, Google TTS, OpenAI TTS, Piper (local/free)
- **Music:** Suno AI, ElevenLabs Music
- **Post:** FFmpeg, Remotion (React-based programmatic composition)

Provider selection is scored across 7 dimensions: task fit, quality, control, reliability, cost, latency, continuity.

## Agent Operating Contract (AGENT_GUIDE.md)

**Rule Zero:** Every video production request goes through the pipeline system. No exceptions.

The agent workflow:
1. Read `AGENT_GUIDE.md` before any response (enforced via `CLAUDE.md`)
2. Run `registry.discover()` and present capability menu (configured vs. available)
3. Identify pipeline, read manifest, run preflight checks
4. Execute stage by stage, reading director skills before any tool call
5. Announce decisions before execution (tool name, provider, model, reasoning)
6. Request approval before material changes to production path
7. Checkpoint at defined gates — human approval required before asset generation

All outputs go to `projects/<project-name>/` with subdirectories for artifacts, images, video, audio, and renders.

## Quality and Governance

- **Pre-compose validation:** Prevents rendering broken plans
- **Post-render self-review:** ffprobe checks, frame sampling, audio analysis
- **Slideshow risk scoring:** 6-dimension check to prevent animation-over-stills
- **Decision audit trail:** Logs all creative and technical choices with alternatives
- **Budget controls:** Estimation, reserves, approval thresholds (default $2 for explainer)
- **Revision cycles:** Up to 3 per stage

## Skill Organization

```
skills/
  INDEX.md          — runtime reference, architecture overview
  core/             — FFmpeg, Remotion, WhisperX, subtitles, color grading
  creative/         — editing, enhancement, data viz, Sora/VEO/LTX prompting, music, face restoration, lip-sync
  pipelines/        — stage director skills for each pipeline
  meta/             — onboarding, self-review, dynamic skill creation
```

Skill content is instructional Markdown — agents read skills before executing their corresponding stage. The meta/onboarding skill classifies user intent and presents a capability menu; meta/self-review runs post-production quality checks.

## Notable Design Patterns

**Reference-video-driven creation:** Users paste a YouTube/TikTok/Reels URL and the system analyzes structure and pacing, then generates differentiated variants — not copies.

**Zero-API-key path:** Many workflows run fully with free stock sources and local models (Piper TTS, local diffusion). Typical cost when using commercial APIs: $0.15–$3.00 per video.

**Dynamic skill creation:** The meta layer supports creating new skills during a session to extend capabilities without modifying source files.

**Platform-neutral core:** The `AGENT_GUIDE.md` and `PROJECT_CONTEXT.md` are shared. Platform-specific files (`CLAUDE.md`, `CURSOR.md`, `COPILOT.md`) are thin wrappers that simply mandate reading the shared guide.

## Relation to Superpowers

OpenMontage's skill architecture is conceptually adjacent to Superpowers but domain-specific to video production. Key similarities:

- Skill files are Markdown instructions for agents
- Skills are read before acting (not recalled from training)
- Multi-stage workflows with human checkpoint gates
- Quality self-review built into the process

Key differences:
- OpenMontage skills are domain-specific (video production conventions, provider techniques)
- Pipeline manifests are declarative YAML, not agent-invoked skill chains
- The tool registry is a runtime query rather than installed plugins
- Superpowers is zero-dependency; OpenMontage requires Python, FFmpeg, Node.js, and provider API keys

An OpenMontage integration for Superpowers would fit best as a standalone plugin (per Superpowers contributor guidelines) rather than core, given its tool dependencies and domain specificity.
