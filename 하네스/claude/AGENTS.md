# `AlphaKR93/skills`

Collection of personal skills & instructions by [@AlphaKR93](https://alpha93.kr)

> [!WARNING]
> This is a private copy of [AlphaKR93/skills](https://github.com/AlphaKR93/skills.git) (which is also private).
> Permitted for personal, educational purposes only; refer to [LICENSE](./LICENSE).

> [!NOTE]
> This is a machine translation of `README.md` written in Korean into English; grammer or context may be incorrect.

## the "Philosophy"

These are the philosophy that the *"user"* should have:

**Know who you are talking to.**
- Models are models — *"mathematical"* models. Ultimately *calculated* based on input. Good input leads to good results.
- Models are not gods — even psychologists cannot know your intentions — explicitly define the context.

**Write for the reader.**
- Use Markdown and XML tags, not damn straight lines. — Fixing just this will double the response time.
- Files created "for" the agent must contain only essential information.
- The writing conventions must vary depending on the model.

**Provide appropriate resources.**
- The MCP must perform all static processing that does not require judgment and provide it to the agent.
- Utilize the project feature. Leave only the necessary instructions; unnecessary things only waste tokens.

**Everyone makes mistakes.**
- Treat the model as a "stranger." Do not give full access to your computer to the model — this must not be given to your friends or family either.
- Always perform tasks inside a container (WSLc, MXC) — This allows the problem to be easily reversed.
- Harden the permissions. Grant only necessary permissions. Differentiate between read and write. Use Regular Expressions for detailed conditions.

**Do not remain as a passive person.**
- Think of each other as tenured professors. You must have a willingness to learn for the conversation to move forward.

**Legally responsible party is You.**
- You make the final decision.
- You also bear legal responsibility.
- Models are subcontractors — do not forget that the responsibility always lies with you.

## Structure

### [`dotfiles.wiki-main`]

Part of dotfiles and Obsidian notes; contains main instruction and project instructions.

References:
- [Prompting best practices — Claude API Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- [Andrej Karpathy Guidelines](https://github.com/multica-ai/andrej-karpathy-skills)
- [caveman](https://github.com/JuliusBrussee/caveman)

### [`skills-main`]

Privately distributed personal skill repository.

## the "Harness"

This copy includes part of the primitive form of the harness.

- Main Agent *(the "Planner")*: Claude\.ai — responsible for organizing thoughts and writing the plan (always include defailed checklist).
- Code Agent(s) *(the "Implementer")*: Google Antigravity (CLI, WSLc) — responsible for the actual implementation.
  1. **Implementation:** (`/goal`) Implement according to the plan. Keep caveman ultra mode via `/caveman:caveman ultra`, `/planning` mode.
  2. **Verification:** Verify all items on the plan checklist.
  3. **Goal-driven Complete:** Run the actual code to verify whether the desired result is produced.
- Q/A Agent (Optional) *(the "Assurance")*: GitHub Copilot, Gemma (local) — executes the implementation using Devtools MCP, etc.

### Automated Updates

- Claude Plugin Marketplace is deployed via: `https://repo.alpha93.kr` (Authorization required)
- Automatically updated via GitHub CI/CD Actions.

### MCPs

- Public MCPs
  - GitHub MCP
- Local MCPs
  - JetBrains IDEs
  - DAP(Debugger Adapter Protocol)
  - LSP(Language Server Protocol)
- Private MCPs (Remote, deployed via FaaS)
  - Memories MCP — Used to organize detailed definitions for each concept; platform memories (known as "dreams") is used for summary, overview of brief concepts.
  - Document MCP — Used to read/access large PDFs and Obsidian notes on backend. Read Table of Contents, Bookmark PDFs, Manage annotations.
  - Search MCP — Used to perform platform-specific searches, returns structured results. Supports Google, NAVER, Print Archives(DBpia, KISTI ScienceOn, Google Scholar, FigShare, ResearchGate, arXiv), Books(교보문고, 알라딘, Yes24, 책이음, 독서로), Shopping(다나와, 11번가, 지마켓, 네이버플러스 스토어), Code(grep.app)
  - Dictionary MCP — Used to lookup lexical definitions and encyclopedic descriptions of terms or concepts. Supports `Word Definitions (via NAVER Dictionary)`, `Term Definitions (via NAVER Encyclopedia)`, `Concepts (via Wikipedia with MediaWiki families)`, `Folk Knowledges (via 나무위키 with 엔하계(-family) wikis)`, Internal document lookups.
  - Forums MCP — Used to read forum threads; useful for finding prior solutions. Supports StackExchange families (with StackOverflow for Agents support), Reddit, Quora, etc.
  - Collaborations MCP — Used to control external agent sessions (e.g., GitHub Agents, Claude Code Remote Agents).
  - (Skill) 약학정보원 MCP — Used to searching Korean pharmaceuticals.
  - (Skill, Forked) PubMed MCP — Used to lookup medical literature/research evidence.
  - (Skill, Forked) ICD-10 MCP — Used to clarify diagnosis terminology.
