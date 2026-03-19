#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>true</swiftbar.hideSwiftBar>
# <swiftbar.refreshOnOpen>true</swiftbar.refreshOnOpen>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>

import json
import os
import subprocess
import time
import urllib.request
from datetime import datetime, timezone

KEYCHAIN_SERVICE = "Claude Code-credentials"
API_URL = "https://api.anthropic.com/api/oauth/usage"
CACHE_FILE = os.path.expanduser("~/.local/state/claude-usage-cache.json")
CACHE_TTL = 1800  # 30 分钟，避免 429
BAR_WIDTH = 20
NOOP = "bash=/usr/bin/true terminal=false"

PLAN_NAMES = {
    "max": "Claude Max",
    "claude_max_5x": "Claude Max 5x",
    "claude_max_20x": "Claude Max 20x",
    "claude_pro": "Claude Pro",
}


def get_token():
    result = subprocess.run(
        ["security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-w"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Keychain 读取失败: {result.stderr.strip()}")
    creds = json.loads(result.stdout.strip())
    oauth = creds.get("claudeAiOauth", {})
    token = oauth.get("accessToken")
    if not token:
        raise RuntimeError("credentials 里没有 accessToken")
    return token, oauth


def fetch_usage(token):
    req = urllib.request.Request(
        API_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "anthropic-beta": "oauth-2025-04-20",
            "Accept": "application/json",
        }
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def load_cache():
    try:
        with open(CACHE_FILE) as f:
            cache = json.load(f)
        age = time.time() - cache.get("ts", 0)
        if age < CACHE_TTL:
            return cache.get("usage"), cache.get("oauth"), age
    except Exception:
        pass
    return None, None, None


def save_cache(usage, oauth):
    safe_oauth = {
        "subscriptionType": oauth.get("subscriptionType", ""),
        "rateLimitTier": oauth.get("rateLimitTier", ""),
    }
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    tmp = CACHE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump({"ts": time.time(), "usage": usage, "oauth": safe_oauth}, f)
    os.replace(tmp, CACHE_FILE)


def progress_bar(value, width=BAR_WIDTH):
    value = min(max(value, 0.0), 1.0)
    filled = round(value * width)
    return "█" * filled + " " * (width - filled)


def usage_color(value):
    if value < 0.20:
        return "#22C55E"  # 绿: 充裕
    if value < 0.40:
        return "#3B82F6"  # 蓝: 正常
    if value < 0.60:
        return "#EAB308"  # 黄: 过半
    if value < 0.80:
        return "#F97316"  # 橙: 吃紧
    return "#EF4444"      # 红: 危险


def remaining_str(resets_at_str):
    try:
        dt = datetime.fromisoformat(resets_at_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        remaining = (dt - now).total_seconds()
        if remaining <= 0:
            return "已重置"
        mins = int(remaining / 60)
        days = mins // (60 * 24)
        hours = (mins % (60 * 24)) // 60
        minutes = mins % 60
        if days > 0:
            return f"{days}d {hours}h"
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    except Exception:
        return "?"


def time_progress(total_hours, resets_at_str):
    try:
        dt = datetime.fromisoformat(resets_at_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        total_secs = total_hours * 3600
        elapsed = total_secs - (dt - now).total_seconds()
        return min(max(elapsed / total_secs, 0.0), 1.0)
    except Exception:
        return 0.0


def print_section(title, resets_at, utilization, total_hours, extra_label=None):
    util = min(max(utilization / 100, 0.0), 1.0)
    tprog = time_progress(total_hours, resets_at)
    remain = remaining_str(resets_at)
    label = extra_label if extra_label is not None else f"剩余 {remain}"

    title_line = f"{title}  {label}".strip() if label else title
    print(f"{title_line} | size=11 {NOOP}")
    print(f"  用量  {progress_bar(util)} {int(utilization):3d}% | font=Menlo size=11 color={usage_color(util)} {NOOP}")
    print(f"  时间  {progress_bar(tprog)} {int(tprog*100):3d}% | font=Menlo size=11 color={usage_color(tprog)} {NOOP}")


def render(usage, oauth, cache_age=None):
    weekly = usage.get("seven_day") or {}
    weekly_util = weekly.get("utilization", 0)
    bar_color = usage_color(weekly_util / 100)

    plan_raw = oauth.get("subscriptionType", "")
    plan = PLAN_NAMES.get(plan_raw, plan_raw or "Claude")
    tier_raw = oauth.get("rateLimitTier", "")
    tier = "5x" if "5x" in tier_raw else ("20x" if "20x" in tier_raw else "")
    plan_str = plan if tier and tier in plan else f"{plan} {tier}".strip()

    print(f"◆ {int(weekly_util)}% | color={bar_color} font=Menlo")
    print("---")
    print(f"{plan_str} | size=12 {NOOP}")
    print("---")

    if weekly and weekly.get("resets_at"):
        print_section("📅 Weekly (7d)", weekly["resets_at"], weekly.get("utilization", 0), 168)
        print("---")

    sonnet = usage.get("seven_day_sonnet") or {}
    if sonnet and sonnet.get("resets_at"):
        print_section("📅 Sonnet (7d)", sonnet["resets_at"], sonnet.get("utilization", 0), 168, extra_label="")
        print("---")

    opus = usage.get("seven_day_opus") or {}
    if opus and opus.get("resets_at"):
        print_section("📅 Opus (7d)", opus["resets_at"], opus.get("utilization", 0), 168, extra_label="")
        print("---")

    burst = usage.get("five_hour") or {}
    if burst and burst.get("resets_at"):
        print_section("⏱ 5-Hour Burst", burst["resets_at"], burst.get("utilization", 0), 5)
        print("---")

    extra = usage.get("extra_usage") or {}
    if extra.get("is_enabled") and extra.get("monthly_limit"):
        used = extra.get("used_credits", 0) or 0
        limit = extra.get("monthly_limit", 1) or 1
        util_val = (extra.get("utilization") or 0) / 100
        used_str = f"${used/100:.2f} / ${limit/100:.0f}"
        print(f"💳 超额用量  {used_str} | size=11 {NOOP}")
        print(f"  用量  {progress_bar(util_val)} {int(util_val*100):3d}% | font=Menlo size=11 color={usage_color(util_val)} {NOOP}")
        print("---")

    if cache_age is not None:
        if cache_age < 60:
            age_str = "刚刚"
        elif cache_age < 3600:
            age_str = f"{int(cache_age / 60)}m 前"
        else:
            age_str = f"{int(cache_age / 3600)}h 前"
        print(f"缓存 ({age_str}) | size=10 {NOOP}")
    else:
        print(f"已更新 {datetime.now().strftime('%H:%M')} | size=10 {NOOP}")
    print("立即刷新 | refresh=true")


def main():
    cached_usage, cached_oauth, cache_age = load_cache()

    # 缓存有效且未过期，直接渲染
    if cached_usage is not None:
        render(cached_usage, cached_oauth, cache_age)
        return

    # 缓存过期或不存在，调 API
    try:
        token, oauth = get_token()
        usage = fetch_usage(token)
        save_cache(usage, oauth)
        render(usage, oauth)
    except Exception as e:
        print("◆ ! | color=#f44336")
        print("---")
        print("加载失败 | color=#f44336")
        print(str(e))
        print("---")
        print("立即重试 | refresh=true")


if __name__ == "__main__":
    main()
