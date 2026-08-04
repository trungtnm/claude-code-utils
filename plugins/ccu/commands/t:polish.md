---
description: Scrutinize UI/UX and implementation; polish to premium, Stripe-level quality
argument-hint: [scope]
---

Scrutinize every aspect of the application's UI/UX and implementation. Find things that are sub-optimal, wrong, or could obviously be improved. Polish the interface to be slicker, more visually appealing, more intuitive, and premium-feeling — Stripe-level quality. Use extended thinking.

**Scope: `$ARGUMENTS`**

If a bead ID, epic ID, or specific area/component is provided above, focus your polish pass on that scope. Use `br show <id>` if a bead/epic ID is given to understand context. If no argument is provided, sweep the entire application.

## Steps

1. **Determine scope** — Check whether `$ARGUMENTS` specifies a target:
   - **If a bead/epic ID is given**: Run `br show <id>` to understand the task. Find the relevant components, screens, or features and focus your polish there.
   - **If a component/area name is given**: Locate that area in the codebase and focus there.
   - **If no argument is given**: Walk the full application — go through every screen, interaction, and workflow.

2. **Walk the user flow** — Read the component code, styles, and state management for the target scope. Experience the app as a user would.

3. **Identify friction** — Look for things that would make a user pause, feel confused, or feel annoyed:
   - Unclear labels, confusing terminology, or ambiguous actions
   - Missing feedback (no loading states, no success confirmation, no error messages)
   - Jarring transitions or layout shifts
   - Inconsistent patterns (buttons that look different in different places, inconsistent spacing)
   - Dead ends or confusing navigation
   - Too many clicks to accomplish common tasks

4. **Evaluate visual quality** — Compare against premium standards (Stripe, Linear, Vercel):
   - **Typography** — hierarchy, readability, consistent sizing, proper line heights
   - **Spacing** — consistent padding/margins, breathing room, alignment grid
   - **Color** — intentional palette, proper contrast, consistent usage of accent colors
   - **Micro-interactions** — hover states, transitions, focus indicators, animations
   - **Empty states** — what does the user see when there's no data?
   - **Error states** — do they look designed or like afterthoughts?

5. **Check responsiveness and edge cases** — What happens with long text? Many items? No items? Small screens? Dark mode if applicable?

6. **Prioritize improvements** — Rank by impact: things that feel broken > things that feel awkward > things that feel unpolished.

7. **Implement the polish** — Make the changes. Focus on:
   - Tightening spacing and alignment
   - Adding missing micro-interactions (hover, focus, active states)
   - Improving copy and labels for clarity
   - Adding loading, empty, and error states where missing
   - Smoothing transitions
   - Ensuring visual consistency across the entire app

## Rules

- **Be opinionated** — Don't ask permission for obvious improvements. If a button has no hover state, add one.
- **Sweat the details** — Premium feel comes from hundreds of tiny things done right, not one big feature.
- **Consistency over creativity** — A cohesive, consistent UI beats a flashy but inconsistent one.
- **Don't redesign** — Polish what's there. Improve spacing, states, feedback, and consistency. Don't change the fundamental layout or design direction.
- **Match existing design system** — Use the project's existing colors, fonts, and component patterns. Extend them, don't replace them.
