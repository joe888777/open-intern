---
description: Retrospective — review what just happened, extract lessons, save to memory
---

## User Input

```text
$ARGUMENTS
```

Run a retrospective on the work just completed in this conversation. Review at TWO levels.

## Level 1: Execution — 做事方法問題

How well was the work executed? Focus on process, decisions, and mistakes.

1. **Trace the timeline** — List what happened chronologically:
   - What was the original request?
   - What approach was taken?
   - What worked? What didn't?
   - Were there any pivots or surprises?

2. **Identify issues** — For each problem encountered:
   - **What happened**: factual description
   - **Root cause**: why it happened (dig deeper than surface level)
   - **Impact**: time wasted, production affected, user blocked?
   - **Was it avoidable?**: with what action?

3. **Assess risk** — Did any "fix" or "improvement" cause more harm than the original problem? This is the most important question.

4. **Extract actionable lessons** — For each insight, filter through:
   - Is it **non-obvious**? (Don't save "test before deploy")
   - Is it **reusable**? (Will it help in future conversations?)
   - Is it **specific enough** to act on? (Not vague platitudes)

5. **Save to memory** — Save only lessons that pass all 3 filters. Use feedback-type memories with clear Why/How-to-apply structure.

## Level 2: Capability — 能力升級機會

What tools, skills, or knowledge gaps were exposed? How can we level up?

6. **Skill gaps** — Were there tasks that were slow, manual, or error-prone that could be automated?
   - Should a new `/skill` be created? (e.g., a `/db-diagnose` skill for production DB issues)
   - Should an existing skill be improved? (e.g., add a pre-flight check to `/dev-test`)
   - Should CLAUDE.md be updated with new conventions?

7. **Knowledge gaps** — Were there areas where better knowledge would have saved time?
   - Search the web for best practices, tools, or patterns others use for similar problems
   - Check if there are existing tools/libraries that solve the problem better
   - Look at how other teams handle the same workflow (e.g., alembic migration strategies, zero-downtime deploys)

8. **Tooling gaps** — Are there missing integrations or automations?
   - MCP servers that could help (e.g., direct Zeabur API access instead of browser clicking)
   - CI/CD improvements (e.g., alembic head check in pre-push hook)
   - Monitoring/alerting gaps (e.g., health check after deploy)

9. **Propose improvements** — For each gap identified:
   - **What**: specific tool, skill, or knowledge to add
   - **Why**: what problem it solves, with example from this session
   - **Effort**: quick (< 30 min), medium (1-2 hours), or large (needs planning)
   - **Priority**: do now / next session / backlog
   - Ask user which ones to pursue

## Output Format

```
## Retrospective

### Timeline
[chronological summary]

### Level 1: Execution
#### What went well
- ...
#### What went wrong
- ...
#### Key lesson
[single most important takeaway]

### Level 2: Capability
#### Skills to add/improve
| Skill | Why | Effort | Priority |
|-------|-----|--------|----------|
| ...   | ... | ...    | ...      |

#### Knowledge to acquire
- [topic] — search for [specific query]

#### Tooling improvements
- [improvement description]

### Actions taken
- Memories saved: [list]
- Skills created/updated: [list]
- Research done: [list]
```
