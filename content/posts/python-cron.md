---
category: 1.1-software-development
title: Python script failing via cron
date: 2025-02-26 15:11:00 +0900
colors:
  - "#d0c5aa"
  - "#5bc8d5"
  - "#3a5d63"
  - "#2d3a33"
  - "#343434"
tags:
  - python
  - cron
  - debugging
  - openai
  - best-practices
  - scripts
blurb: Debugging a Python script that silently failed only when executed via cron.
metaRSS: true
---

## The issue

I had setup a cron task to run my [[squirrel-archive-webpages | Squirrel archiver]] script once per day, but for some reason the task was not executing. Nothing, including any errors, was showing up in any logs. At first I thought there was something wrong with my crontab, but other scripts set up to run in the same way were running without issue.

Copying the commands in crontab to the terminal and running it manually worked. It was only when cron was triggering the run that it failed.

Just to be sure, I changed my script to just `print('hey')`, and this worked! So there must have been something wrong inside the script, and I started the tried and true debugging process of _deleting chunks of code until something works_.

Side note: Since the script had to run via cron, while I was debugging it was set to run once per minute on the dot. I had to rush to make changes in time, but I also had to wait to see results, which made for an interesting experience.

## The culprit

I had been declaring `openai_client = OpenAI()` as a global variable, outside of any function. This worked fine when running the script manually, but when cron triggered it, it failed silently. 

"_Why?_"  
I have no idea.  

"_Is initializing objects outside of functions commonly known to be a bad practice?_"  
Probably. 

I wish I knew more about the reasons, but moving the declaration inside a function fixed the issue.

So, maybe to many it is obvious that "_yes of course you shouldn't do that_", but I'm recording it here in case anybody else out there is like me.
