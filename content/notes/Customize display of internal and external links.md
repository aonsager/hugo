---
title:
date: 2026-01-20 15:29:00 +09:00
colors:
tags:
  - hugo
  - style
metaRSS: false
draft: false
---
I really liked how Quartz gave external links and internal links different styles, and I wanted to do something similar here.

This is an [external link](https://invisibleparade.com).
This is an [internal link](/).

To do this, I overwrote `/layouts/_markup/render-link.html` with code that looks like this:

```html
{{- $u := urls.Parse .Destination -}}
<a href="{{ .Destination | safeURL }}"
  {{- with .Title }} title="{{ . }}"{{ end -}}
  {{- if $u.IsAbs }} rel="external"{{- else }} class="internal"{{ end -}}
>
  {{- with .Text }}{{ . }}{{ end -}}
</a>
```

`$u.IsAbs` is a really convenient function that does most of the work for me. I just use it to toggle a CSS class that changes the styling.

My hacky, manual [[Supporting wikilinks in Hugo|wikilinks support]] doesn't pass through this function, but since wikilinks will all be internal I simply added the `class="internal"` to all wikilinks.