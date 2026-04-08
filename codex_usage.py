import json
import os
import time

SESSIONS_DIR = os.path.expanduser("~/.codex/sessions")

PLAN_NAMES = {
    "free": "Codex Free",
    "plus": "Codex Plus",
    "pro": "Codex Pro",
    "max": "Codex Max",
}


def get_usage():
    """Return the most recent rate_limits dict from Codex session files, or None."""
    if not os.path.isdir(SESSIONS_DIR):
        return None

    session_files = []
    for root, _dirs, files in os.walk(SESSIONS_DIR):
        for fname in files:
            if fname.startswith("rollout-") and fname.endswith(".jsonl"):
                session_files.append(os.path.join(root, fname))

    if not session_files:
        return None

    session_files.sort(reverse=True)  # Most recent first (timestamp in filename)

    for path in session_files[:20]:
        last_rate_limits = None
        try:
            with open(path) as f:
                for line in f:
                    try:
                        ev = json.loads(line)
                        if (ev.get("type") == "event_msg"
                                and ev.get("payload", {}).get("type") == "token_count"):
                            rl = ev["payload"].get("rate_limits")
                            if rl:
                                last_rate_limits = rl
                    except (json.JSONDecodeError, KeyError):
                        continue
        except Exception:
            continue
        if last_rate_limits:
            return last_rate_limits

    return None


def weekly_util(rate_limits):
    """Return the weekly utilization percent (0-100), or None if unavailable."""
    secondary = rate_limits.get("secondary") or {}
    val = secondary.get("used_percent")
    return val if val is not None else None


def render(rate_limits, progress_bar, usage_color, noop):
    """Print Codex sections in SwiftBar format (caller provides shared helpers).

    Prints a plan header and one section per available limit window,
    each followed by '---'. Does not print a title bar line.
    """
    plan_type = rate_limits.get("plan_type", "")
    plan = PLAN_NAMES.get(plan_type, f"Codex {plan_type.title()}".strip())

    print(f"{plan} | size=12 {noop}")
    print("---")

    secondary = rate_limits.get("secondary")
    if secondary and secondary.get("used_percent") is not None:
        _print_limit(secondary, progress_bar, usage_color, noop)
        print("---")

    primary = rate_limits.get("primary")
    if primary and primary.get("used_percent") is not None:
        _print_limit(primary, progress_bar, usage_color, noop)
        print("---")


def _print_limit(limit, progress_bar, usage_color, noop):
    util = limit["used_percent"] / 100
    window_mins = limit.get("window_minutes", 0)
    resets_at = limit.get("resets_at", 0)
    remain = _remaining_str(resets_at)
    tprog = _time_progress(window_mins, resets_at)

    if window_mins >= 1440:
        days = window_mins // (60 * 24)
        icon, label = "📅", f"Weekly ({days}d)"
    else:
        hours = window_mins // 60
        icon, label = "⏱", f"{hours}-Hour Burst"

    print(f"{icon} {label}  剩余 {remain} | size=11 {noop}")
    print(f"  用量  {progress_bar(util)} {int(limit['used_percent']):3d}% | font=Menlo size=11 color={usage_color(util)} {noop}")
    print(f"  时间  {progress_bar(tprog)} {int(tprog*100):3d}% | font=Menlo size=11 color={usage_color(tprog)} {noop}")


def _remaining_str(resets_at_unix):
    try:
        remaining = resets_at_unix - time.time()
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


def _time_progress(total_minutes, resets_at_unix):
    try:
        total_secs = total_minutes * 60
        elapsed = total_secs - (resets_at_unix - time.time())
        return min(max(elapsed / total_secs, 0.0), 1.0)
    except Exception:
        return 0.0
