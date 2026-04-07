---
name: using-rtk
description: Use when running CLI commands that consume many tokens (git, tests, cargo, npm, docker, kubectl) — RTK reduces output by 60-90% automatically via the PreToolUse hook
---

# RTK — Rust Token Killer

RTK is a token-optimization proxy for CLI commands. The Superpowers PreToolUse hook transparently rewrites common commands (e.g. `git status` → `rtk git status`) before they execute. You do not need to prefix commands manually.

## Meta Commands (always run directly)

```bash
rtk gain              # Show token savings analytics
rtk gain --history    # Show per-command savings history
rtk discover          # Analyze Claude Code history for missed optimization opportunities
rtk proxy <cmd>       # Execute raw command without filtering (use when you need full output)
```

## How the Hook Works

1. You issue a command (e.g. `git status`)
2. The PreToolUse hook calls `rtk rewrite "git status"`
3. RTK returns `rtk git status` (or passes through unchanged if no filter exists)
4. The rewritten command executes transparently — you see compressed output

You do not need to think about this. It happens automatically.

## When to Bypass RTK

Use `rtk proxy <cmd>` when:
- A filter is hiding output you need (e.g. debugging a build failure)
- You need the raw exit code or full stderr

## Verifying Installation

```bash
rtk --version         # Should show: rtk X.Y.Z
which rtk             # Verify binary is on PATH
rtk gain              # Should not error
```

If `rtk` is not found, the hook exits cleanly and commands run unmodified — no breakage.

## Installation (if not present)

```bash
cargo install rtk
rtk init -g           # Registers the Claude Code hook (already in Superpowers hooks.json)
```

⚠️ **Name collision**: `reachingforthejack/rtk` (Rust Type Kit) is a different binary. If `rtk gain` errors, check `which rtk`.
