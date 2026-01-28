---
category: 1.2-web-development-and-tools
title:
date: 2026-01-16 22:41:00 +09:00
colors:
tags:
  - hugo
  - goldmark
  - markdown
  - regex
metaRSS: false
---

By default Hugo uses [goldmark](https://github.com/yuin/goldmark) to parse Markdown into HTML. There are a number of goldmark extensions that come included, but if you want to extend this functionality you will need to patch and rebuild Hugo from source. 

Instead of doing that, I – like a lunatic – decided to use templates to run the post body through a series of regex filters, and hope that it comes out pretty on the other side.

Partials are mainly used to reuse often-used snippets of code, but you can do a lot with them. While partials look like an HTML file, you can treat them as functions that take input and output text.

In any place in my layout that output the page content as `{{ .Content }}`, I've replaced that with the function 

```
{{ partial "custom-content" . }}
```

This file can then be used to run the content through a series of regex filters, to do whatever custom processing I need:

```
{{ $customContent := .Content }}
{{ $customContent = partial "content-wikilinks" (dict "Content" $customContent "Page" .) }}
{{ $customContent }}
```

And here are the regex filters that I use now:

- [[Supporting wikilinks in Hugo]]
