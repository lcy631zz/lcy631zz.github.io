---
name: vibewriting
description: Use when writing, drafting, editing, or reviewing blog posts for the Hugo website. Generates multiple options, critiques them, and picks the best. Triggers on: "写博客", "写文章", "write blog", "new post", "写一篇", "draft post", "写首诗", "write a poem".
---

# VibeWriting — Strategic Blog Writing

Adapted from the [vibewriting](https://github.com/rpiplewar/vibewriting) Cursor workspace methodology.

## Core principles

1. **Decompose before writing**. Break every writing request into smaller steps: clarify topic → outline → draft variants → critique → select best → polish.
2. **Never assume**. Ask clarifying questions about topic, audience, tone, and structure. Do not guess the user's intent.
3. **Generate, then critique**. For each key section, produce at least 3 variants. Evaluate each against the writing goals before selecting the strongest.
4. **Value-first content**. Every piece should give the reader something — insight, a new perspective, a useful framework, or an emotional experience. Never write filler.

## Workflow

### 1. Clarify

Before writing anything, confirm with the user:
- Topic or subject
- Target audience
- Desired tone (casual, scholarly, poetic, satirical, etc.)
- Approximate length
- Any specific framework or reference material to incorporate

### 2. Outline

Propose a section-by-section outline. Get explicit approval before drafting.

### 3. Generate variants

For each outline section, write 3 variants. For each variant, note its strengths and weaknesses. Present the best option for each section with a brief rationale.

### 4. Assemble the draft

Combine the selected sections into a complete draft. Ensure smooth transitions between sections.

### 5. Self-review

Critically read the final draft. Check for:
- Logical flow and narrative arc
- Engaging opening (first paragraph must hook)
- Satisfying conclusion (last paragraph should resonate)
- Natural Chinese prose — avoid machine-translation cadence; vary sentence length; use 四字短语 or classical allusions when appropriate for the user's style
- Accurate facts and framing
- Appropriate length — neither padded nor truncated

### 6. Output

Write the final post to `content/blog/<slug>/index.zh-Hans.md` using the frontmatter below.

## Hugo frontmatter

```yaml
---
title: "文章标题"
date: "2026-08-19"
period: "高三"          # or "高考后", "大学", etc. — life phase the post belongs to
description: ""         # short summary for SEO and listing previews
tags: [标签1, 标签2]
---
```

## Reference materials

- **Blog template** (`references/blog-template.md`): structural example demonstrating the problem → analysis → conclusion flow.
- **Writing frameworks** (`references/frameworks/`): methodology documents the user wants the AI to draw from when writing on specific topics.

Load reference materials when the user asks to write on a topic covered by an existing framework.

## State tracking

For complex, multi-session blog projects, record the current topic, outline, draft status, and revision notes in the conversation. Claude Code's persistent memory (`~/.claude/MEMORY.md`) retains key facts across sessions — use it for long-term blog direction, not ad-hoc draft state.

## After publishing

1. Build with `hugo` to verify no errors.
2. Preview with `hugo server` on localhost.
3. Commit and push to GitHub Pages.
4. Notify the user with the published URL.
