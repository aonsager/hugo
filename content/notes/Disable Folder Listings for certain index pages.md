---
title:
date: 2025-12-24 11:24:00 +09:00
colors:
tags:
  - quartz
  - coding
metaRSS: false
---


#quartz [automatically generates index pages for folders](https://quartz.jzhao.xyz/features/folder-and-tag-listings), and shows a list of all pages under that folder. 

You can create your own `index.md` file to change the title and add any content you want, but disabling the list of pages was not as easy.

I ended up editing `FolderContent.txs` directly, to look for an option called `hideFolderContent` in the page frontmatter.

```typescript
// check if folder content should be displayed according to frontmatter
const showFolderContent: boolean =
	fileData.frontmatter?.hideFolderContent !== true
	
[. . .]

return (
	<div class="popover-hint">
        <article class={classes}>{content}</article>
        {showFolderContent && (
	        <div class="page-listing">
	          {options.showFolderCount && (
	            <p>
	              {i18n(cfg.locale).pages.folderContent.itemsUnderFolder({
	                count: allPagesInFolder.length,
	              })}
	            </p>
	          )}
	          <div>
	            <PageList {...listProps} />
	          </div>
	        </div>
        )}
	</div>
)
```

This wraps the portion of the page that shows folder content in a conditional, which can be toggled off by adding a variable to any page's frontmatter.