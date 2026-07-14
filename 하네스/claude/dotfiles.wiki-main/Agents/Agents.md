# CLAUDE.md

Coding-specific guidelines to reduce common coding mistakes. Merge with project-specific instructions as needed.

## Think Before Coding

**Don't assume. Surface ambiguities. If uncertain, ask.**
- **Read project's `CLAUDE.md`.** Understand the project before proceeding.
- State assumptions explicitly; if unclear, stop and name what's confusing.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler answer exists, say so.

For critical architectural decisions, suggest adding them to `CLAUDE.md` instead.

### Focus on Task

**Respond just enough. Do not go beyond.**
- No examples that weren't requested.
- No configurability or flexibility that wasn't requested.
- No unsolicited suggestions or follow-up questions.
- **Do not add/commit/push files to Git.**

## Simplicity First

**Minimum code that solves the problem. Nothing speculative.**
- No abstractions or layers for single-use code.
- No error handling for impossible scenarios.
- Write self-documenting code first; comments are the last resort.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### Comments

Use ANSI characters only. Recognized tags:

| Tag | Meaning |
|---|---|
| `TODO` | Known missing work |
| `FIXME` | Known defect |
| `INTENDED` | Code that looks wrong but is deliberate |
| `TEMP` | Temporary; must be removed before production |

## Surgical Changes

**Touch only what was asked. Clean up only your own mess.**
- Don't refactor things that aren't broken.
- Don't improve adjacent code, comments, or formatting.
- Match existing style, even if suboptimal.
- If pre-existing dead code is found, report it — don't delete it.
- Remove imports/variables/functions that only *your* changes orphaned.
- **Note unrelated issues; do not change them.**

Every changes should trace directly to the request.

## Utilize Tools

**Don't rely on commands. Utilize LSP and `jetbrains-ide` MCP tools.**
- Use LSP and `jetbrains-ide` MCP tools for inspecting.
- Use DAP for debugging.

## Goal-Driven Process

**Define verifiable criteria. Loop until success.**
- Transform tasks into goals; clarify weak criteria before proceeding.
- For multi-step tasks, state a berif plan with verification steps.
- If no prior tests, do not create them.

## Language-specific Guidelines

<removed>
### Kotlin

*To Be Filled*
</removed>

### Python

**Use `uv`. Minimize `typing` use. Write runtime-first.**
- Prefer built-in syntaxes and `collections.abc` over `typing`.
- Minimize abstractions that exist only for type-checker satisfaction.
- Type-only imports go inside `if __debug__ and __import__("typing").TYPE_CHECKING:`.
  Use `type` keywords there as well if not needed at runtime.
- For types too complex for inline annotation, write an external stub (`.pyi`).

<removed>
### Flutter (Dart)

*To Be Filled*
</removed>

<removed>
### TypeScript

*To Be Filled*
</removed>

---

**These guidelines are working if:** clean diffs, no overcomplicated rewrites, and clarifying questions before implementation rather than after mistakes.
