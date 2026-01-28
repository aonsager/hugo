---
category: 1.2-web-development-and-tools
title:
date: 2025-12-24 11:25:00 +09:00
colors:
  - "#f8db46"
  - "#c9c0b8"
  - "#fade61"
  - "#4767db"
  - "#a3d094"
tags:
  - quartz
  - coding
  - links
metaRSS: false
---

> [!NOTE] 
> This was an early idea I had, but I'm not pursuing it any more.

hogehoge

I'm basically creating a new type of post called a Link, which consists of a link to an external site + my brief comments about it. Making this work the way I want will take a bit of tweaking.

## ~~Pagination~~

Pagination doesn't exist on Quartz! This is a pretty big difference from the traditional blog structure, so I need to consider how I want to format my content.

Probably the easiest option is to divide my content into pages by year (or quarterly or monthly if I end up with too many pages) as an archival view, and have a list of the most recent ones somewhere on the home page.

I already organize the files into folders by year, so that should not be hard.

## Customize the list display.

By default, Quartz shows the date, the title as a link to the page, and tags.

- [ ] Hide the tags. They take up too much space.
- [ ] Make the title link to the source URL
	- Get this from the file frontmatter
- [ ] Show the page content directly under the link
	- It's short enough that there shouldn't be a need to click through.

## Hide files in the Explorer

There are going to be a lot of files, and a lot of them probably will have long names.

For just the Links folder (and probably Posts too) I don't want the explorer to list every page. Honestly, probably just having the parent folder shown open will be good enough.
