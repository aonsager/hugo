---
title:
date: 2026-01-16 22:51:00 +09:00
colors:
tags:
  - hugo
  - blog
  - coding
  - customization
  - wikilinks
  - markdown
metaRSS: false
draft: false
---

I write my notes in Obsidian, and the support for wiki-style links is very convenient for linking notes, and even setting up links to notes before actually creating them. I wanted to enable these links on my generated site, without changing my current workflow in Obsidian.

The strategy is pretty straightforward. 

- Use regex matching to find a wikilink (`[‎[ page title]‎]`)
	- Support alias syntax (`[‎[ page-title | Link text ]‎]`)
- Look through all existing pages to find a page that has a filename or `title` property that matches.
- Replace the wikilink with a link to the page's full URL.
	- If the wikilink uses an alias, show that as a link text
	- Style it as an [[Customize display of internal and external links | internal link]]
- If the page doesn't exist, show it as a red disabled link, like Wikipedia.

The full source is below, and you can see it on [github](https://github.com/aonsager/hugo/blob/main/themes/invisible/layouts/_partials/content-wikilinks.html), too

### Caveats

This is a fairly stupid implementation, and it has some big gotchas.

Because regex is applied to the entire page content, this will grab double square brackets anywhere they appear, even if you have them in code blocks or the like.

Maybe the correct way to get around this is to parse the document in blocks, and skip over any segments like code blocks that you want to ignore. 

I current get around this by adding a [[zero width-character]] between the two brackets if I want to avoid detection. This works but is very hacky, so I might get around to fixing it at some point.


```html
<!-- Forked from https://github.com/milafrerichs/hugo-wikilinks/blob/main/partials/content-wikilinks.html -->
{{ $firstBracket := "\\[\\[" }}
{{ $lastBracket := "\\]\\]" }}

{{ $wikiregex := "\\[\\[([^/]+?)\\]\\]" }}

{{ $wikilinks := .Content | findRE $wikiregex }}

{{ $content := .Content }}
{{ $foundPage := "" }}

{{ range $wikilinks }}

	{{ $rawContent := . | replaceRE $wikiregex "$1" }}

	<!-- Parse target and display text (supports [‎[target | display]‎] syntax) -->
	{{ $target := $rawContent }}
	{{ $displayText := $rawContent }}
	{{ if strings.Contains $rawContent "|" }}
		{{ $parts := split $rawContent "|" }}
		{{ $target = index $parts 0 | strings.TrimSpace }}
		{{ $rest := after 1 $parts }}
		{{ $displayText = delimit $rest "|" | strings.TrimSpace }}
	{{ end }}

	<!-- Escape special regex characters for wikilink pattern -->
	{{ $escapedContent := $rawContent | replaceRE "([\\\\.*+?|^$()\\[\\]{}])" "\\$1" }}
	{{ $wikilink := printf "%s%s%s" $firstBracket $escapedContent $lastBracket }}
	{{ $anchorized := $target | anchorize }}

	<!-- Search all pages for matching filename or title -->
	{{ $foundPage = "" }}
	{{ range site.RegularPages }}
		{{ if eq $foundPage "" }}
			{{ $fileBaseName := "" }}
			{{ with .File }}
				{{ $fileBaseName = .ContentBaseName | anchorize }}
			{{ end }}
			{{ $titleAnchorized := .Title | anchorize }}
			{{ if or (eq $fileBaseName $anchorized) (eq $titleAnchorized $anchorized) }}
				{{ $foundPage = . }}
			{{ end }}
		{{ end }}
	{{ end }}

	{{ if ne $foundPage "" }}
		{{ $rel := $foundPage.RelPermalink }}
		{{ $link := printf "<a href=\"%s\" class=\"internal\">%s</a>" $rel $displayText }}
		{{ $content =  $content | replaceRE $wikilink $link }}
	{{ else }}
		<!-- Page not found - show as plain text without brackets -->
		{{ warnidf "content-wikilinks" "Page not found: %s" $target }}
		{{ $content = $content | replaceRE $wikilink $displayText }}
	{{ end }}
{{ end }}


{{ $content | markdownify }}
```