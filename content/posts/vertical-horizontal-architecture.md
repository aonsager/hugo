---
title: Vertical and horizontal architectures for websites
date: 2026-01-22 16:16:00 +09:00
colors:
  - "#b5bbc2"
  - "#548235"
  - "#bfc6cd"
  - "#96b286"
  - "#1b2a4f"
tags:
  - website
  - design
  - blog
  - organization
metaRSS: false
draft: false
---
I recently rebuilt my site, and this gave me an opportunity to rethink how to organize its contents.

## Vertical architecture

Most websites have what I consider to be a "vertical" architecture. This is probably based on early websites being essentially public file servers with files contained in various folders. 

With a vertical architecture, the "index page" or the "top page" (see the analogy at work already?) gives an overview of the site's organization and where you can find everything. You decide what you want to see, and start drilling down.

![Navigating to a post on a vertical blog](vertical_1.png)

If you want to visit a different page, you _navigate back up_, pick a different spot, and drill down again.

![Navigating to a different post on a vertical blog](vertical_2.png)

Moving to a completely different area of the site (in terms of where the file is saved) requires a lot of backtracking, so it's pretty common for all pages to have a quick shortcut back to the very top.

![Navigating to a different area of a vertical blog](vertical_3.png)

## Horizontal architecture

A completely different way of organizing content is what I consider to be a "horizontal" architecture. Rather than arrange everything in meaningful folders, you instead create connections between pages and end up with something like a graph of linked nodes. This is something that you see a lot in wikis.

![A horizontal content graph](horizontal_1.png)

This is different from the vertical architecture because there is no concept of "going back up". You traverse the graph by following links to adjacent pages, exploring the natural connections between their contents.

There will probably be a home page to give some overview of what you can expect to find, but you most likely will not be returning to it with any regularity.

With this method, the connections between ideas are organic, and the site as a whole feels very cohesive. Moving to an adjacent page has minimal friction, and the browsing experience is intuitive. You also have the benefit that you don't need to do any organization up-front.

## Taking horizontal a step further

I'm really drawn to the horizontal approach. Having a site with this kind of organization motivates me to write more, to publish more, to cultivate this space that some describe as a [digital garden](https://maggieappleton.com/garden-history).

Wikis, Obsidian, and most implementations of this architecture consider mainly links and backlinks – explicit mentions of notes in other notes. I think there is potential for a lot more. One thing I want to explore is the _nature of the connection_ between notes.

The core idea is that you want to surface a list of notes that are related to the current one. Notes that the reader might be interested in reading next. There ought to be ways to reveal not just the explicit connections, but more implicit connections as well. And that gives us the opportunity to describe these connections, and explain why we think they are interesting.

_"Look at this note. It shares these three tags in common."_

*"This is another book review, about another book in the History genre."*

*"This note has a contradictory message to the current one. The author is still trying to reconcile these different perspectives."*

*"This note was written on the same day as this one. They reveal the author's state of mind."*

I think connections like these would be fascinating to explore, and I want to play around with some ideas here to see what's possible.

## What I've done so far

For now, I have surfaced related notes based on tags that they have in common. When displaying a page's [[related-posts|related posts]], I rank them by how many tags they have in common, since that is probably a good indicator of how related the contents are.

On an [[tag-pages|individual tag's page]], I also order the results by the number of other tags they have in common. In a sense, it's not showing a list of *pages* that have the tag. It's showing a list of *tags* that are related to the current tag, along with the pages that represent that relation. I think that's a lot more interesting.

This is all I've done so far because it was pretty easy to implement, but I will see what else I can come up with.