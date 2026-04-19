Title: Every Claude Code Concept You Need to Know
Date: 2026-04-11
Category: GenAI
Tags: GenAI, Claude-Code, LLM, agents, developer-tools, local-AI
Slug: every-claude-code-concept-you-need-to-know

Claude Code is not a chatbot. It lives in your terminal, reads your actual files, writes code, runs commands, and executes multi-step workflows — all with your permission. Here are 30 concepts you need to understand it properly. No fluff, no hand-holding.

## The 30 Concepts

**1. The Terminal** — Claude Code doesn't run in a browser. It runs in the terminal, the same text-based interface developers use daily. If you've never opened a terminal before, that's your first homework assignment.

**2. Installation + Pricing** — Install with a single command via npm. Pricing is token-based through your Anthropic account. There's no flat monthly fee tied to a UI — you pay for what you use, which means costs scale with how hard you push it.

**3. File Access** — Claude Code reads and edits files directly on your machine, with your permission. Not "paste your doc into a chat window." It opens the actual file, modifies it in-place, and saves it. This is the concept that makes it useful.

**4. Image + PDF Reading** — Claude Code can ingest images and PDFs as inputs. Point it at a PDF proposal or a screenshot and it processes the content directly — no manual copy-paste required.

**5. Tool Use** — Claude Code has built-in tools: file reading, file writing, shell execution, and more. These are the primitives it uses to act on your computer. You see each tool call as it happens in real time.

**6. Prompting Techniques** — Vague prompts produce garbage results. "Help me with my marketing" is useless. "Write a 3-email welcome sequence for my dog walking business targeting first-time pet owners, 150 words each" is not. Specificity is the skill.

**7. CLAUDE.md** — A markdown file you create in your project directory that tells Claude Code the rules, context, and conventions for that project. Think of it as a standing system prompt that persists across sessions. Every serious Claude Code user has one.

**8. Plan Mode** — Before Claude Code executes anything, you can ask it to plan first. It outputs what it intends to do, step by step, and waits for your approval. Run in plan mode for anything non-trivial. Review before you let it touch anything.

**9. Context Window** — The amount of text Claude can "hold in mind" at once during a session. Long conversations, large files, and extensive histories eat into it. When context fills up, older information gets dropped. This affects result quality.

**10. Tokens + Costs** — Everything processed by Claude Code — your prompts, the files it reads, its responses — is measured in tokens. Tokens drive cost. Reading a 50-page PDF burns tokens. Keep context lean and targeted to control spend.

**11. Model Selection** — You can choose which Claude model backs your session. Faster, cheaper models work for routine tasks. Heavier models are worth it for complex reasoning or production-grade code. Pick the right tool for the job.

**12. /compact** — A slash command that compresses your current conversation history into a shorter summary, freeing up context window space without wiping the session. Use it mid-task when context gets bloated.

**13. /clear** — Wipes the entire conversation and starts fresh. Every new task should start with a clean context. Don't carry leftover noise from a previous task into the next one. Use this more than you think you need to.

**14. Session Management** — Claude Code has no persistent memory between sessions by default. Start each session with your CLAUDE.md re-read to restore project context. Design your workflow around this statelessness rather than fighting it.

**15. Permission Modes** — By default, Claude Code asks for approval before running any shell command. This gets tedious fast. You can pre-approve safe, non-destructive commands (ls, cat, grep, mkdir, git status) in your settings.local.json. Destructive operations should always require explicit confirmation.

**16. Effort Levels** — You can signal how much effort you want Claude to apply. Quick answers for exploration, thorough analysis for production decisions. Matching effort level to task type saves time and tokens.

**17. Interrupt + Redirect** — While Claude Code is running a task, you can interrupt it mid-execution and redirect it. If it starts going down the wrong path, stop it early. Don't let it burn tokens on a wrong approach when you can see it happening.

**18. Visual Studio Code** — Claude Code integrates directly with VS Code. You can run it inside the VS Code terminal and see file changes reflected in your editor in real time. If you're not a terminal-native developer, this is the recommended setup.

**19. Memory** — Claude Code supports memory files that persist across sessions. Unlike CLAUDE.md (project-specific), memory files can store user-level preferences and context. Useful for encoding your personal conventions once and never repeating them.

**20. Project vs Global** — Configuration can be scoped at the project level (CLAUDE.md, settings.local.json) or at the global level (applies to all Claude Code sessions on your machine). Know which scope a setting lives in before you modify it.

**21. Slash Commands** — Built-in commands prefixed with `/` that control Claude Code's behavior: /clear, /compact, /help, and more. You can also define custom slash commands (skills) that map to your own workflows.

**22. Skills** — Custom slash commands you define once and reuse indefinitely. A skill is a markdown file that describes a reusable workflow. You build it once, invoke it with `/skill-name`, and Claude follows the instructions every time. Hundreds of community-built skills already exist on GitHub in repos like `anthropics/skills` and `hesreallyhim/awesome-claude-code`.

**23. Hooks** — Scripts that run automatically before or after Claude Code actions. Quality gate hooks, for example, can intercept Claude's output before it's committed and check it against defined standards. Hooks are how you enforce consistency without relying on Claude to self-police.

**24. Web Browsing** — Claude Code can browse the web when given the appropriate tool access. It can fetch pages, read documentation, and pull in live information as part of a task — not just work from static local files.

**25. MCP Servers** — Model Context Protocol servers extend Claude Code's tool access to external services: Airtable, Google Drive, Slack, GitHub, and more. Tools handle what Claude does on your computer. MCP extends that to the internet and third-party APIs. This is the integration layer.

**26. Perplexity MCP** — A specific MCP integration that gives Claude Code access to Perplexity's search capabilities. Useful when a task requires real-time research as part of a larger automated workflow.

**27. Subagents** — Multiple Claude Code instances running simultaneously, each handling a distinct subtask. Instead of processing platforms one at a time, you spin up parallel agents and run them concurrently. Subagents are how you turn Claude Code from a sequential tool into a parallel workflow engine.

**28. Remote Control** — Claude Code can be configured for remote access, meaning you can trigger and manage sessions from another machine or interface. Relevant for server automation and scheduled background tasks.

**29. Scheduled Tasks** — Claude Code workflows can be scheduled to run automatically at defined intervals. Combine this with skills and hooks and you have a self-operating workflow system that runs without manual invocation.

**30. Git Version Control** — Claude Code integrates with git. Every change it makes can be committed, branched, and rolled back through standard git workflows. This is your undo button. Always have Claude Code working inside a git-tracked project. Before: changes happen and you hope nothing breaks. After: every change is versioned, documented, and reversible.

## The One Rule That Matters

Master five concepts before you touch the next five. The shiny object trap — jumping from MCP to subagents to hooks before understanding CLAUDE.md and context windows — is the single biggest waste of time. The gap between people getting real results and people falling behind is not talent. It is reps. Start with file access, prompting, CLAUDE.md, plan mode, and /clear. Everything else builds on those five.