---
category: 1.2-web-development-and-tools
title:
date: 2025-12-24 11:29:00 +09:00
colors:
  - "#5f33e5"
  - "#f4af73"
  - "#ae7de1"
  - "#f6f6f6"
  - "#c6c7c7"
tags:
  - blog
  - website
  - quartz
---


> [!NOTE]
> This is an old todo file I used when building my site with Quartz. It's left here for posterity.


In addition to using this site as a general wiki for my thoughts, I'm eyeing the possibility of migrating my entire blog to this format. I Currently make my site with [Jekyll](https://jekyllrb.com) (a great product!) but I have a lot of customization living in each post's frontmatter, and while I do have a variety of convenience scripts set up, I kind of need to be sitting at my desktop machine in order to create and publish posts. 

With Quartz, I just add a new file somewhere, slap on a few words, and it's already a part of my website. I want to see if there is a way to stay within this dead-simple workflow, and somehow recreate the functionality of my current site.

## Todos

- General
	- [x] Set up automatic deploys (rsync) in Github Actions
	- [x] [[Disable Folder Listings for certain index pages]]
	- [x] Stop committing public/
	- [ ] Make a section for Haiku?
	- [ ] Decide how much I want to change the site's layout/CSS
	- [ ] Set up automatic importing of micro posts from [[gotosocial]]
	- [x] Revisit design of [links](/links) page
- Game wiki section 
	- [x] Start writing things about games I am playing
	- [ ] Micro-posts
		- [x] Start writing micro-posts for my thoughts while playing
		- [x] Set up a workflow to easily write/save new files with the correct name and location (Obsidian script, or Shortcuts?)
		- [ ] Display a game's micro posts on that game's top page
		- [ ] Enable hover hover-over links for only certain links
			- Just definitions would be ideal
- RSS
	- [x] Set up an RSS feed, for only notes that I set #metaRSS in the frontmatter
	- [x] A feed for links
	- [x] A feed that combines both
- Blog
	- [x] Migrate old posts over
	- [x] Check all posts to make sure nothing is broken
	- [x] Resurface `link` frontmatter
		- [x] Add a new /links section based on this. 
			- Overlap with /posts is ok
	- [ ] See how things feel with a tag-based organization
	- [ ] Add the five-color display to the design
- Micro posts
	- [ ] Make image display smarter. Probably put all images inline.
