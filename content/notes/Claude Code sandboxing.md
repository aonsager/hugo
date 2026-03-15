---
category: 1.3-ai-and-automation
title:
date: 2026-03-09 12:01:00 +09:00
colors:
  - "#adaba8"
  - "#cac8c2"
  - "#424353"
  - "#a76f5e"
  - "#363633"
tags:
  - sandboxing
  - claude-code
  - permissions
  - security
  - macos
  - ripgrep
  - bug-fix
metaRSS: false
---
Enable sandboxing in Claude Code! It seems counterintuitive, but having sandboxing enabled actually makes things go faster, because the stricter guardrails allows it to skip requesting permissions for commands that work within them.

[The official blog post](https://www.anthropic.com/engineering/claude-code-sandboxing) outlines how one bit motivator for this function is explicitly the reduction of permission prompts, because "approval fatigue" is very real and is a security risk.

Note that as time of writing (2026/03/09) there is a bug in the latest version that prevents sandbox from enabling on MacOS. It seems like it is [incorrectly assuming a Linux environment](https://github.com/anthropics/claude-code/issues/32275) and one quick fix is to install [ripgrep](https://github.com/BurntSushi/ripgrep) since this missing dependency is the root cause of the error. 

Or just wait for a patch, probably.