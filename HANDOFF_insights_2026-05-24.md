# Handoff — Insights Report Followups (2026-05-24)

Source: `/Users/d.edens/.claude/usage-data/report-2026-05-24-133221.html`

## Done this chat
- Saved 4 feedback + 1 project memory under `/Users/d.edens/.claude/projects/-Users-d-edens-lab-madness-interactive/memory/`
  - `feedback_todo_tools.md`
  - `feedback_verify_before_resume.md`
  - `feedback_theme_translations.md`
  - `feedback_subagent_delegation.md`
  - `project_madnessvr.md` (preserved prior MEMORY.md content as proper memory file)
  - Rewrote `MEMORY.md` as index
- Inserted 4 lessons into `swarmonomicon.lessons_learned` via `ssh eaws` mongosh
  - IDs: `6a134c9d4cd3b3dcbe69e328` through `..32b`
  - Topics: complete_todo vs update_todo, verify-before-resume, theme translation atomicity, subagent scope claims

## Remaining — needs proper toolkit
Move to whichever folder/session has the right tools for these:

### 1. File audit/consolidation todo in Omnispindle
- Project: `madness_interactive` (or wherever cross-cutting work belongs)
- Description: "Audit old memory/lessons/todos for overlap with new insights-derived entries; consolidate duplicates; verify against current git state"
- Tags: `audit`, `consolidation`, `memory`, `lessons`, `housekeeping`
- Tool: `mcp__omnispindle__add_todo` (available in current folder, but user wants to defer)

### 2. Lessons should have a proper add tool
- Current Omnispindle MCP exposes `get_lesson` + `search_lessons` only — no `add_lesson`/`create_lesson`
- Had to fall back to mongosh on eaws (works but bypasses service layer)
- Either: add `add_lesson` MCP tool to Omnispindle, OR document the REST endpoint (`lessonsService.addLesson`) as the canonical path for AI sessions
- Architecturally: per CLAUDE.md, MCP is for AI chat → tools. AI adding lessons IS an AI-to-tool flow, so an MCP tool fits

### 3. Optional infra additions from insights report
Not started — evaluate later:
- **PostToolUse hook** for `tsc --noEmit` on `.ts`/`.tsx` edits (catches Invalid Date / dupe field bugs cheaply)
- **`/sync-themes` skill** codifying the 12-locale atomic propagation
- **GitHub MCP + Stripe MCP** servers (would help current subscription/webhook work)

## Lesson IDs inserted (for verification/edits)
```
6a134c9d4cd3b3dcbe69e328  complete_todo vs update_todo
6a134c9d4cd3b3dcbe69e329  verify state before resume
6a134c9d4cd3b3dcbe69e32a  12-locale atomic translations
6a134c9d4cd3b3dcbe69e32b  subagent scope claims
```
