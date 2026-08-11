---
name: opinion
description: Give a candid assessment of the target's usefulness, design, and architecture
argument-hint: [target]
---

**Opinion target: `$ARGUMENTS`**

Now tell me what you actually THINK of the target above — is it even a good idea? Is it useful? Is it well designed and architected? Pragmatic? What could we do to make it more useful and compelling and intuitive/user-friendly to both humans AND to AI coding agents?

**If `$ARGUMENTS` is empty, the target is the whole project.** Otherwise scope your opinion to exactly what was named — it might be a specific file, module, feature, command, skill, design decision, abstraction, dependency, or workflow. Evaluate *that thing* on its own merits and in the context of the project it lives in; don't drift into opining on the whole project unless the argument is the whole project.

## What to evaluate

1. **Is this even a good idea?** -- Does it solve a real problem? Is the problem worth solving? Are there better alternatives that already exist?

2. **Is it useful?** -- Would real users (humans and AI agents) actually benefit from this? What's the value proposition? Is it solving a pain point or creating busywork?

3. **Is it well designed and architected?** -- Is it clean, consistent, and maintainable? Are the abstractions right? Is the complexity justified? Are there architectural smells or over-engineering?

4. **Is it pragmatic?** -- Does it make practical tradeoffs well? Is it building the right things at the right level of quality? Or is it gold-plating, yak-shaving, or solving theoretical problems?

5. **How intuitive is it?** -- For humans: is it easy to discover, learn, and use? For AI agents: is it easy to invoke correctly with minimal context? Are the interfaces and naming self-explanatory?

6. **What would make it more compelling?** -- Concrete suggestions to increase usefulness, usability, and adoption. What's missing? What should be cut? What should be redesigned?

## Rules

- **Be honest** -- Do not flatter. If something is bad, say so and explain why. Genuine criticism is more valuable than encouragement.
- **Be specific** -- Back opinions with concrete examples from the code. "The architecture is messy" is useless. "The X module mixes concerns Y and Z, which makes it hard to..." is useful.
- **Be constructive** -- Every criticism should come with a suggestion for improvement.
- **Consider both audiences** -- Evaluate usability for human developers AND for AI coding agents. These audiences have different needs.
- **Read the target first** -- You must have explored what you're opining on before giving opinions.
  - **If opining on the whole project:** read AGENTS.md, CLAUDE.md, and README.md, then explore the code directly until you understand the architecture and purpose.
  - **If opining on a specific target (`$ARGUMENTS`):** locate and read it and its immediate collaborators (callers, callees, tests, docs) so your opinion rests on how it actually behaves and fits in — not just its name. Do not opine on code you haven't read.
