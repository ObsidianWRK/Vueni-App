---
name: shadcn-ui
description: Install and use shadcn/ui (Radix-based) components in React/Next.js/Vite projects with Tailwind, theming, and best-practice composition.
license: Apache-2.0 (see LICENSE.txt)
---

# shadcn/ui Skill

Use this skill when the user wants:
- shadcn/ui installed or configured (Next.js, Vite, Remix, etc.)
- Components added (Button, Dialog, Table, Form, etc.) and composed into screens
- Theme/token work (CSS variables, dark mode, brand theming)
- Guidance on best practices (accessibility, file structure, component patterns)

## Core facts (important)

- shadcn/ui is **not a typical component dependency**. You run a CLI that **copies** component source into the repo (usually `components/ui/*`), so the user owns the code and can edit it.
- Runtime dependencies are typically Radix primitives + utility deps (e.g. class-variance-authority, tailwind-merge, lucide-react), depending on chosen components.

## Install / initialize

1. Ensure Tailwind is set up and working (or set it up first).
2. Initialize shadcn/ui in the project root:

```bash
npx shadcn@latest init
```

Notes:
- Prefer `npx shadcn@latest ...` (or `pnpm dlx`, `bunx`) depending on the repo package manager.
- If the repo uses TypeScript path aliases, confirm `@/` is configured and matches `tsconfig.json`.

## Add components

Add a component (example: button):

```bash
npx shadcn@latest add button
```

Typical usage after install:

```tsx
import { Button } from "@/components/ui/button";

export function Example() {
  return <Button>Continue</Button>;
}
```

## Theming & tokens (quick guidance)

- Prefer **CSS variables** for color tokens so dark mode is easy.
- Keep a small token surface:
  - `--background`, `--foreground`
  - `--primary`, `--primary-foreground`
  - `--muted`, `--muted-foreground`
  - `--border`, `--ring`
- Keep `globals.css` authoritative for tokens; keep Tailwind config mostly for mapping tokens to utilities.

## Composition patterns to follow

- Wrap Radix primitives into project-specific components with:
  - Sensible defaults
  - Forwarded refs
  - `className` merging (tailwind-merge)
- Keep domain UI separate from primitives:
  - `components/ui/*` for primitives
  - `components/<feature>/*` or `features/<feature>/*` for feature-level components

## Accessibility checks (always)

- Focus ring visible (keyboard-only)
- Dialogs: focus trap works; close button labeled; escape closes
- Forms: labels associated; error text announced (`aria-describedby`)
- Color contrast: primary buttons + subtle text meet WCAG

## When unsure

Ask which stack the repo uses:
- Next.js App Router vs Pages Router
- Vite + React
- Tailwind already installed or not

