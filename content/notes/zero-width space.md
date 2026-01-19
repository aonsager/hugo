---
title: Zero-width space
date: '2026-01-19 10:22:00 +09:00'
colors:
tags: 
- html
- hack
metaRSS: false
draft: false
---

There is a special unicode character that does not display visually, but exists to affect text formatting and layout.

It can be written in a number of different ways:

```
&#8203;
&#x200B;
<wbr>
```

If you want to use it in a document, there are tools that allow you to copy the character to your clipboard. You won't see anything when you paste it in, but when moving the cursor you'll notice it pausing at that point to skip over the invisible character.

I use this in a hacky way to prevent strings from matching a regex filter. For example, to circumvent my [[Supporting wikilinks in Hugo | wikilinks matching]] I can add a zero-width space between two square brackets. Visually it is identical, but the extra character prevents regex matching.