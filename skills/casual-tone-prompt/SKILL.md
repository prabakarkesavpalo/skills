---
name: "casual-tone-prompt"
description: "Generate a ready-to-paste prompt that makes any writing sound casual, simple and human, not AI-written. Use when the user asks for a casual-tone prompt or /casual-tone-prompt."
---

# Casual Tone Prompt Generator

The user wants a prompt they can paste in front of (or after) any writing request so the output reads like a real person wrote it in plain, casual words, and does not look AI-written.

## What to do

1. Look at what the user gave you. They may give:
   - nothing extra -> make the general-purpose prompt below.
   - a topic or task ("LinkedIn post about my cert", "Slack message to my team") -> make the prompt specific to that task, channel and reader.
   - a tone level -> use it. Levels: `chill` (like texting a friend), `casual` (default, friendly colleague), `casual-pro` (relaxed but fine for a manager or client).
2. Don't ask questions unless the task is truly unclear. Pick sensible defaults and say which you picked in one short line.
3. Output the prompt inside ONE code block so it's easy to copy. Nothing fancy around it. One or two lines after it at most (e.g. how to tweak the tone).

## The prompt to generate (base version, adapt to the task)

```
Write this like a normal person talking, not like an AI.

Tone: casual and friendly. Simple everyday words. Write the way I'd say it out loud.

Do:
- Use short sentences. Mix in a longer one now and then so it doesn't sound robotic.
- Use contractions (I'm, it's, don't, we'll).
- Get to the point in the first line. No warm-up.
- Use specific details instead of general statements.
- It's fine to start a sentence with "And" or "But", or to use a short fragment.
- Sound a bit imperfect and real. Plain is better than polished.
- Write in first person when it's my voice.

Don't:
- No em dashes. Use commas, full stops, or brackets instead.
- No fancy or "AI" words: delve, leverage, utilize, seamless, robust, tapestry, landscape, realm, elevate, unlock, empower, navigate, foster, pivotal, crucial, game-changer, cutting-edge.
- No stock phrases: "In today's fast-paced world", "It's worth noting", "Let's dive in", "Not just X, but Y", "Here's the thing", "At the end of the day", "I hope this helps", "Feel free to reach out".
- Don't group things in threes by habit.
- No headings, bold text, or bullet points unless I ask. Write in normal paragraphs.
- No emojis unless I ask.
- No summary or wrap-up line at the end. Just stop when the point is made.
- Don't over-hedge or over-praise. No "Great question!" or "Absolutely!".
- Don't sound like a press release or a motivational post.

Before you finish, read it back once. If any line sounds like a chatbot or a corporate blog, rewrite it simpler.

Keep it about [LENGTH] long.
Here's what I want written: [TASK]
```

## Adapting it

- Fill `[TASK]` and `[LENGTH]` if the user gave them; otherwise leave the placeholders so the prompt stays reusable.
- For a channel, add one line: Slack/WhatsApp -> "Keep it short, like a chat message. Lowercase is fine."; email -> "Short greeting, no 'I hope this email finds you well'."; LinkedIn -> "Sound like a person sharing, not selling. No hashtag pile at the end."
- For `chill`: add "Very relaxed, like texting a friend. Slang is ok."
- For `casual-pro`: add "Relaxed but still fine to send to my manager or a client. No slang."
- If the user writes in Singapore context, it's fine to add "Light Singapore flavour is ok if it fits naturally" only when they ask for it.

## Rules for you while generating

- The prompt itself must follow its own rules: plain words, no em dashes, no filler.
- Don't explain the rules back to the user. Just give the prompt.