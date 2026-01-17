---
title: CSS ideas
date: 2025-12-24 11:22:00 +09:00
colors:
tags:
  - css
  - oklch
  - colors
  - design
---


## Colors

First define your basic colors using [OKLCH](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/color_value/oklch).

```css
:root {
  /* Raw LCH values: Lightness, Chroma, Hue */
  --lch-blue: 54% 0.15 255;
  --lch-red: 51% 0.2 31;
  --lch-green: 65% 0.23 142;

  /* Semantic colors built on primitives */
  --color-link: oklch(var(--lch-blue));
  --color-negative: oklch(var(--lch-red));
  --color-positive: oklch(var(--lch-green));
}

@media (prefers-color-scheme: dark) {
  :root {
    --lch-blue: 72% 0.16 248;   /* Lighter, slightly desaturated */
    --lch-red: 74% 0.18 29;
    --lch-green: 75% 0.20 145;
  }
}
```

Then, you can use native CSS functions like `color-mix()` to modify these base colors:

```css
.card {
  --card-color: oklch(var(--lch-blue-dark));

  /* Derive an entire color palette from one variable */
  --card-bg: color-mix(in srgb, var(--card-color) 4%, var(--color-canvas));
  --card-text: color-mix(in srgb, var(--card-color) 30%, var(--color-ink));
  --card-border: color-mix(in srgb, var(--card-color) 33%, transparent);
}
```

This feels much more intuitive, and more controlled, than coming up with various hex values and sprinkling them throughout your stylesheets.

## Spacing

Use character width for horizontal spacing, and `rem` for vertical spacing

```css
:root {
  --inline-space: 1ch;      /* Horizontal: one character width */
  --block-space: 1rem;      /* Vertical: one root em */
}

.component {
  padding-inline: var(--inline-space);
  margin-block: var(--block-space);
}
```

## References

- [Vanilla CSS is all you need](https://www.zolkos.com/2025/12/03/vanilla-css-is-all-you-need)
- [Modern CSS patterns in Campfire](https://dev.37signals.com/modern-css-patterns-and-techniques-in-campfire/)
