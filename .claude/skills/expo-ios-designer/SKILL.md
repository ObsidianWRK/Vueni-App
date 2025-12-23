---
name: expo-ios-designer
description: Design iOS-first UIs for Expo/React Native apps: layout, typography, safe areas, motion, haptics, and accessibility aligned with iOS conventions.
---

# Expo iOS Designer Skill

Use this skill when the user wants to design or polish an iOS app built with Expo (React Native), especially:
- iOS-native navigation patterns (tabs, stacks, modals, sheets)
- Layout that respects safe areas + notches + Dynamic Island
- iOS typography, spacing, and motion
- Haptics, blur, and platform affordances
- Accessibility and “feels native” QA

## Design principles (practical)

- Prefer **clarity** over decoration; iOS UIs tend to be content-first.
- Use **8pt grid** spacing, but allow iOS-friendly irregularities (e.g., 12/20 for touch targets + list padding).
- Keep tap targets ≥ 44pt height.
- Use subtle elevation; prefer separators, blur, and translucency over heavy shadows.

## Expo/React Native implementation guidance (high level)

- Safe areas:
  - Use `react-native-safe-area-context` and apply insets for top/bottom bars.
- Navigation:
  - Prefer `expo-router` (or React Navigation) with a clear stack/tab structure.
  - Use modals/sheets for transient tasks; full screens for deep flows.
- Motion:
  - Keep transitions short (150–250ms), easing out.
  - Use `react-native-reanimated` for smooth interactions when needed.
- Haptics:
  - Use `expo-haptics` for confirmation, selection, and error feedback (sparingly).
- Visual effects:
  - Use `expo-blur` for iOS-like frosted surfaces when appropriate.

## iOS UI checklists

### Layout & spacing
- Safe area respected on:
  - iPhone SE / small screens
  - Notched devices
  - Landscape
- Scroll views don’t hide under headers/tab bars
- Headers don’t jump when content loads

### Typography
- Use a consistent type scale (3–5 sizes max)
- Support Dynamic Type where possible (avoid hard-coded tiny fonts)
- Avoid ultra-thin weights for body text

### Components
- Lists: consistent row height, separators aligned, large hit areas
- Buttons: clear hierarchy (primary/secondary/tertiary)
- Inputs: labels, helper/error text, correct keyboard types

### Accessibility
- Screen reader labels for icon-only buttons
- Logical focus order
- Sufficient contrast in light and dark mode
- Motion reduced when “Reduce Motion” is enabled (where feasible)

## Questions to ask up front (so we don’t guess)

- Are we matching iOS-only styling, or shared cross-platform design?
- What navigation model: tabs, stack-only, or mixed?
- Brand constraints: colors, typography, imagery?
- Target devices: iPhone only, iPad, both?
