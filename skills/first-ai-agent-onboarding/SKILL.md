---
name: first-ai-agent-onboarding
description: Guide someone through building their first AI agent end-to-end with a small, clear scope - pick one problem, choose a base LLM, define tools, build the model-tool-result loop, add memory only when needed, wrap it in an interface, iterate, and keep scope tight. Use when asked to onboard someone to AI agents, build a first agent, scaffold a starter agent project, or when a new agent project is drifting into a "universal agent".
---

# First AI agent onboarding

Build one specific agent, end to end, before anything general. The second agent is ten times easier because the full pipeline is already understood.

## Steps

1. **Pick one small, clear job.** One sentence, one outcome. Good: book a doctor's appointment from a hospital site, monitor job boards and send matches, summarise unread email. If the user says "general assistant", narrow it before writing code.
2. **Choose a base LLM.** Use a hosted model (Claude, GPT, Gemini) or an open-source one (Llama, Mistral) if self-hosting. Do not train anything. Check it handles reasoning and structured output, since agents depend on both.
3. **Decide the tools.** An agent is a chatbot plus tools. List the few APIs or actions the job needs: browsing or scraping (Playwright, Puppeteer, or an API), email API, calendar API, file read/write and PDF parsing. Fewer is better.
4. **Build the skeleton loop, no framework yet.**
   - Take the task or goal as input
   - Send it to the model with a system prompt
   - The model picks the next step
   - If a tool is needed, run it
   - Feed the result back to the model
   - Repeat until done or a final output is produced

   This model -> tool -> result -> model loop is the core of every agent. Add a max-step cap so it cannot run forever.
5. **Add memory carefully.** Start with short-term context (the last few messages). For cross-run memory, use a JSON file or a small database. Add vector search only when retrieval is a proven need.
6. **Wrap it in an interface.** CLI first. Then a small web dashboard (Flask, FastAPI, Next.js), a Slack or Discord bot, or a script on a schedule. Use it in a real workflow to see how it behaves.
7. **Iterate in small cycles.** Run real tasks, find where it breaks, patch, rerun. Expect dozens of cycles. Log every model call and tool result so failures are debuggable.
8. **Keep scope under control.** Resist extra tools and features. One agent that reliably does one job beats a universal agent that keeps failing.

## How to run the onboarding

- Ask for the single job first. Do not proceed until it fits in one sentence.
- Scaffold the smallest project: one file with the loop, one tool, one system prompt, one test task.
- After each step, run it for real before moving on.
- Hand over a short checklist of what exists (job, model, tools, loop, memory, interface) and what is deliberately left out.

## Gotchas

- Jumping to agent frameworks before the raw loop works hides where bugs come from.
- Too many tools make the model pick badly. Start with one or two.
- Tool errors must go back to the model as results, not crash the loop.
- Never put API keys in the repo or the prompt. Use environment variables.
- Vector databases and multi-agent setups are step-two problems, not step-one.

## Source

Based on the Reddit post "Building your first AI Agent; A clear path!" (r/AgentsOfAI, Oct 2026). Paraphrased and extended.
