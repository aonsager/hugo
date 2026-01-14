---
title: Overview Quartz plugin
date: 2025-12-24 11:25:00 +09:00
colors:
  - "#ffffff"
  - "#c5c5c7"
  - "#412c2b"
  - "#b9b9bc"
  - "#192f58"
tags:
  - plugin
  - javascript
  - website
  - overview
  - interface
  - quartz
  - colophon
metaRSS: false
---

> [!NOTE] 
> I'm actually not using this plugin anymore, but I'm leaving this page for reference.


I created a custom plugin to show a static list of the main sections of the site.

(The options aren't used, but I left them in so that I would remember how)

```javascript
interface Options {
  favouriteNumber: number
}
 
const defaultOptions: Options = {
  favouriteNumber: 42,
}
 
export default ((userOpts?: Options) => {
  const opts = { ...userOpts, ...defaultOptions }
  function Overview(props: QuartzComponentProps) {
 
	  return (
			<div class="overview">
				<div class="section">
			   	<h3>
					<a href="/about/">About</a>
				</h3>
				<p class="meta">About me and this site</p>
			</div>
			<div class="section">
			<h3>
					<a href="/posts/">Posts</a>
				</h3>
				<p class="meta">Longer things I wrote</p>
			</div>
			<div class="section">
			<h3>
					<a href="/games/">Games</a>
				</h3>
				<p class="meta">Thoughts and reference</p>
			</div>
			<div class="section">
			<h3>
					<a href="/micro/">Micro</a>
				</h3>
				<p class="meta">My <del>tweets</del> toots</p>
			</div>
			<div class="section">
			<h3>
					<a href="/links/">Links</a>
				</h3>
				<p class="meta">Things I liked</p>
			</div>
			<div class="section">
			<h3>
					<a href="/notes/">Notes</a>
				</h3>
				<p class="meta">Assorted information</p>
			</div>
		</div>
    )
    
  }
  
  Overview.css = `
    .overview p.meta {
    	opacity: .6;
      margin: 0 0 1rem;
      font-style: italic;
    }
  `
 
  return Overview
}) satisfies QuartzComponentConstructor


```
