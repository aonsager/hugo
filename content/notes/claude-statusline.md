---
title: Claude Code statusLine
date: 2026-01-06 10:30:00 +09:00
colors:
tags:
metaRSS: false
draft: false
---
## The output

![Claude Code statusLine](images/cc-statusline.png)

This statusLine shows:

- Current directory
- Current git branch
- Model being used
- 5 hour limit's usage and reset time
- 7 day limit's usage and reset time
- Size of the context window

The script was taken and modified from [this gist by jeremyronking](https://gist.github.com/jeremyronking/7dc1978531b36a4d3741d2faef553a8e)

## Tell Claude Code to run a script to display

Add the following to `~/.claude/settings.json`

```json
{
...
"statusLine": {
    "type": "command",
    "command": "/Users/MYUSERNAME/.claude/statusline-command.sh"
  },
...
}
```


## Creae the script

This is the contents of /Users/MYUSERNAME/.claude/statusline-command.sh

```bash
#!/bin/bash
# ==============================================================================
# Claude Code Status Line
# ==============================================================================
# This script creates a rich status line for Claude Code showing:
# - Current model being used
# - Mode (if in plan/edit mode)
# - Context window usage percentage
# - API usage limits (5-hour and 7-day windows) with time until reset
# - Current git branch
#
# Usage: Configure this script in your Claude Code settings as a statusline hook
# Requirements: jq, curl, git (optional)
#
# The script expects JSON input from Claude Code via stdin
# 
# This script was taken and modified from:
# https://gist.github.com/jeremyronking/7dc1978531b36a4d3741d2faef553a8e 
# ==============================================================================
  
input=$(cat)
  
# ==============================================================================
# Extract Model Information
# ==============================================================================
MODEL=$(echo "$input" | jq -r '.model.display_name // "Unknown"')
  
# ==============================================================================
# API Usage Limits Fetching (with caching)
# ==============================================================================
# Fetches usage data from Anthropic API and caches it to avoid rate limiting
# Cache expires after 60 seconds to keep data reasonably fresh
CACHE_FILE="/tmp/claude-usage-cache"
CACHE_MAX_AGE=60
  
fetch_usage_limits() {
    # Retrieves OAuth credentials from macOS Keychain and fetches usage data
    # Note: This uses macOS 'security' command - may need adjustment for Linux
    local creds token
    creds=$(security find-generic-password -s "Claude Code-credentials" -w 2>/dev/null)
    if [ -z "$creds" ]; then
        echo ""
        return
    fi
  
    # Extract OAuth access token from credentials JSON
    token=$(echo "$creds" | jq -r '.claudeAiOauth.accessToken // empty')
    if [ -z "$token" ]; then
        echo ""
        return
    fi
  
    # Query Anthropic API for usage statistics (5-hour and 7-day windows)
    curl -s --max-time 2 -H "Authorization: Bearer $token" \
         -H "anthropic-beta: oauth-2025-04-20" \
         https://api.anthropic.com/api/oauth/usage
}
  
get_usage_limits() {
    # Returns cached usage data if fresh, otherwise fetches new data
    # This prevents hammering the API on every statusline refresh
    if [ -f "$CACHE_FILE" ]; then
        local cache_age=$(($(date +%s) - $(stat -f %m "$CACHE_FILE" 2>/dev/null || echo 0)))
        if [ "$cache_age" -lt "$CACHE_MAX_AGE" ]; then
            cat "$CACHE_FILE"
            return
        fi
    fi
  
    # Cache is stale or missing - fetch fresh data
    local data
    data=$(fetch_usage_limits)
    if [ -n "$data" ]; then
        echo "$data" > "$CACHE_FILE"
        echo "$data"
    fi
}
  
# ==============================================================================
# Time Formatting Helper
# ==============================================================================
# Converts ISO 8601 timestamp to human-readable relative time
# Examples: "2h30m", "3d5h", "45m", "now"
format_time_until() {
    local reset_at="$1"
    if [ -z "$reset_at" ] || [ "$reset_at" = "null" ]; then
        echo ""
        return
    fi
  
    # Parse ISO timestamp (e.g., "2025-12-31T23:59:59.000Z") and convert to epoch
    # Note: Uses macOS 'date -j' format - may need adjustment for GNU date
    local reset_epoch now_epoch diff
    reset_epoch=$(TZ=UTC date -j -f "%Y-%m-%dT%H:%M:%S" "${reset_at%%.*}" "+%s" 2>/dev/null)
    if [ -z "$reset_epoch" ]; then
        echo ""
        return
    fi
    now_epoch=$(date +%s)
    diff=$((reset_epoch - now_epoch))
  
    if [ "$diff" -le 0 ]; then
        echo "now"
        return
    fi
  
    # Calculate days, hours, and minutes
    local days hours mins
    days=$((diff / 86400))
    hours=$(((diff % 86400) / 3600))
    mins=$(((diff % 3600) / 60))
  
    # Format output based on magnitude (show top 2 units)
    if [ "$days" -gt 0 ]; then
        echo "${days}d${hours}h"
    elif [ "$hours" -gt 0 ]; then
        echo "${hours}h${mins}m"
    else
        echo "${mins}m"
    fi
}
  
# Fetch usage limits from API
USAGE_LIMITS=$(get_usage_limits)
  
# ==============================================================================
# Extract Mode Information
# ==============================================================================
# Mode shows if Claude is in a special state (e.g., "plan", "edit")
MODE=$(echo "$input" | jq -r '.mode // empty')
if [ -z "$MODE" ]; then
    MODE_DISPLAY=""
else
    MODE_DISPLAY=" | ${MODE} |"
fi
  
# ==============================================================================
# Color Coding Helper
# ==============================================================================
# Returns ANSI color code based on usage percentage
# Green (0-59%), Yellow (60-79%), Red (80-100%)
get_color() {
    local pct=$1
    if [ "$pct" -ge 80 ]; then
        echo "\033[31m"  # Red
    elif [ "$pct" -ge 60 ]; then
        echo "\033[33m"  # Yellow
    else
        echo "\033[32m"  # Green
    fi
}
  
# ==============================================================================
# Bar Drawing Helper
# ==============================================================================
# Returns a graphical progress bar based on numerical percentage
draw_bar() {
  local percent=$1
  local width=5
  # Sanitize input: remove decimals and force 0 if empty
  percent="${percent%.*}"
  [ -z "$percent" ] && percent=0
  
  # Clamp range between 0 and 100
  if [ "$percent" -lt 0 ]; then percent=0; fi
  if [ "$percent" -gt 100 ]; then percent=100; fi
  
  # Calculate filled blocks (5 total steps)
  # Math: (percent * 5) / 100
  local filled_blocks=$(( (percent * width) / 100 ))
  local bar=""
  # 1. Add solid blocks (█)
  for ((i=0; i<filled_blocks; i++)); do bar+="█"; done
  # 2. Add track (░)
  local remaining=$((width - filled_blocks))
  for ((i=0; i<remaining; i++)); do bar+="░"; done
  echo "$bar"
}
  
# ==============================================================================
# ANSI Color Codes
# ==============================================================================
RESET="\033[37m"
DIM="\033[90m"
CYAN="\033[36m"
MAGENTA="\033[35m"
WHITE="\033[97m"
  
# ==============================================================================
# Context Window Usage Calculation
# ==============================================================================
# Calculate percentage of context window used (including cache tokens)
CONTEXT_SIZE=$(echo "$input" | jq -r '.context_window.context_window_size // 200000')
USAGE=$(echo "$input" | jq '.context_window.current_usage // null')
  
if [ "$USAGE" != "null" ]; then
    # Sum all token types: regular input, cache creation, and cache reads
    CURRENT=$(echo "$USAGE" | jq '.input_tokens + .cache_creation_input_tokens + .cache_read_input_tokens')
    CTX_PERCENT=$((CURRENT * 100 / CONTEXT_SIZE))
else
    CTX_PERCENT=0
fi
  
CTX_COLOR=$(get_color "$CTX_PERCENT")
  
CTX_DISPLAY="Context ${CTX_COLOR}${CTX_PERCENT}%${RESET}"
  
# ==============================================================================
# Parse API Usage Limits
# ==============================================================================
# Anthropic enforces two rate limit windows:
# - 5-hour rolling window
# - 7-day rolling window
# This section displays both usage percentages with time until reset
if [ -n "$USAGE_LIMITS" ]; then
    # Extract utilization percentages (strip decimal places)
    FIVE_HOUR=$(echo "$USAGE_LIMITS" | jq -r '.five_hour.utilization // empty' | cut -d. -f1)
    SEVEN_DAY=$(echo "$USAGE_LIMITS" | jq -r '.seven_day.utilization // empty' | cut -d. -f1)
    FIVE_RESET=$(echo "$USAGE_LIMITS" | jq -r '.five_hour.resets_at // empty')
    SEVEN_RESET=$(echo "$USAGE_LIMITS" | jq -r '.seven_day.resets_at // empty')
  
    if [ -n "$FIVE_HOUR" ] && [ -n "$SEVEN_DAY" ]; then
    # Get bar view for each limit
      FIVE_BAR=$(draw_bar $FIVE_HOUR)
       SEVEN_BAR=$(draw_bar $SEVEN_DAY)
        # Apply color coding to each limit
        FIVE_COLOR=$(get_color "$FIVE_HOUR")
        SEVEN_COLOR=$(get_color "$SEVEN_DAY")
  
        # Convert reset timestamps to human-readable format
        FIVE_TIME=$(format_time_until "$FIVE_RESET")
        SEVEN_TIME=$(format_time_until "$SEVEN_RESET")
  
        # Build display strings with colored percentages and reset times
        FIVE_DISPLAY="${FIVE_COLOR}${FIVE_BAR} ${FIVE_HOUR}%${RESET}"
        [ -n "$FIVE_TIME" ] && FIVE_DISPLAY="${FIVE_DISPLAY} ${DIM}(${FIVE_TIME})${RESET}"
  
        SEVEN_DISPLAY="${SEVEN_COLOR}${SEVEN_BAR} ${SEVEN_DAY}%${RESET}"
        [ -n "$SEVEN_TIME" ] && SEVEN_DISPLAY="${SEVEN_DISPLAY} ${DIM}(${SEVEN_TIME})${RESET}"
  
        LIMITS_DISPLAY="${FIVE_DISPLAY} • ${SEVEN_DISPLAY}"
    else
        LIMITS_DISPLAY=""
    fi
else
    LIMITS_DISPLAY=""
fi
  
# ==============================================================================
# Git Branch Detection
# ==============================================================================
# Shows current git branch if working directory is in a git repository
GIT_BRANCH=""
if git rev-parse --git-dir > /dev/null 2>&1; then
    BRANCH=$(git branch --show-current 2>/dev/null)
    if [ -n "$BRANCH" ]; then
        GIT_BRANCH="${BRANCH}"
    fi
fi
  
  
# ==============================================================================
# Current directory
# ==============================================================================
# Shows current directory's basename
CURRENT_DIR=$(echo "$input" | jq -r '.workspace.current_dir')
DIR_NAME=$(basename "$CURRENT_DIR")
  
# ==============================================================================
# Final Output
# ==============================================================================
# Assemble all components into final statusline
# Format: current_dir branch [Model] | mode • ██░░░ XX% (XhXm) • █░░░░ XX% (XdXh) • Context XX%
echo -e "${RESET}${DIR_NAME} ${CYAN}${GIT_BRANCH}${RESET} ${DIM}[${MODEL}${MODE_DISPLAY}]${RESET} • ${LIMITS_DISPLAY} • ${CTX_DISPLAY}"
```