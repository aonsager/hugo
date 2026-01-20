---
title:
date: 2026-01-20 15:18:00 +09:00
colors:
tags:
  - hugo
  - blog
  - customization
  - links
  - micros
metaRSS: false
draft: false
---
[Links](/links) and [micro posts](/micro) are short enough that rather than displaying just their title with a link to the full post, I should simply display the full post contents on the folder's root.

To override the default display for a section, I created these files: 

```
/layouts/links/section.html
/layouts/micros/section.html
```

Along with styling and code to [[Supporting wikilinks in Hugo|display wikilinks]], my output for Links looks something like this:

```html
<ul class="section-ul">
        {{ $pages := .Pages.ByPublishDate.Reverse }}
        {{ range (.Paginate $pages).Pages }}
            <li class="border-top">
                <h3>
                    <a href="{{ .Page.Params.link }}">{{ .Title }}</a>&nbsp;
                    <span class="meta">({{ partial "funcs/tld.html" .Page.Params.link }})</span>
                </h3>
                {{ partial "custom-content" . }}
                {{ partial "date-link.html" . }}
            </li>
        {{ end }}
    </ul>
```