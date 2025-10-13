#!/usr/bin/env python3
import json, re, csv, os, datetime
from datetime import datetime, timedelta, timezone

def extract_times(issues, since_date=None):
    """Extracts time per user. If since_date is given, filters closed issues after it."""
    pattern = re.compile(r'@([\w-]+)\s+(\d+)')
    user_data = {}

    for issue in issues:
        closed_at = issue.get("closed_at")
        if not closed_at:
            continue

        closed_at_dt = datetime.strptime(closed_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        if since_date and closed_at_dt < since_date:
            continue

        body = issue.get("body", "")
        if not body:
            continue

        estimated_section = re.search(r"Estimated Time \(minutes\)\s*\n+([^\n#]+)", body)
        actual_section = re.search(r"Actual Time \(minutes\)\s*\n+([^\n#]+)", body)

        if estimated_section:
            for username, minutes in pattern.findall(estimated_section.group(1)):
                user = username.lower()
                user_data.setdefault(user, {"expected": 0, "actual": 0})
                user_data[user]["expected"] += int(minutes)

        if actual_section:
            for username, minutes in pattern.findall(actual_section.group(1)):
                user = username.lower()
                user_data.setdefault(user, {"expected": 0, "actual": 0})
                user_data[user]["actual"] += int(minutes)

    return user_data


def write_csv(path, user_data, user_names, header):
    """Writes a CSV report with real names mapped."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for user, times in sorted(user_data.items()):
            real_name = user_names.get(user.lower(), user.lower())
            writer.writerow([real_name, times["expected"], times["actual"]])


def main():
    issues_path = "reports/issues.json"
    users_path = "reports/user_names.json"
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)

    if not os.path.exists(issues_path):
        raise FileNotFoundError(f"{issues_path} not found")

    with open(issues_path) as f:
        issues = json.load(f)
    with open(users_path) as f:
        user_names = json.load(f)

    now = datetime.now(timezone.utc)
    days_since_monday = now.weekday()

    # Get Monday of this week
    this_monday = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)

    # Get Monday of previous week
    last_monday = this_monday - timedelta(weeks=1)

    # --- WEEKLY REPORT ---
    weekly_data = extract_times(issues, since_date=last_monday)
    weekly_filename = f"{now.year}_{now.month:02d}_{now.day:02d}_weekly_report.csv"
    weekly_path = os.path.join(reports_dir, weekly_filename)

    write_csv(
        weekly_path,
        weekly_data,
        user_names,
        ["Name (Real names)", "Expected Time (min)", "Actual Time (min)"]
    )
    print(f"✅ Weekly report created: {weekly_path}")

    # --- TOTAL REPORT ---
    total_data = extract_times(issues, since_date=None)
    total_path = os.path.join(reports_dir, "total_time_report.csv")

    write_csv(
        total_path,
        total_data,
        user_names,
        ["Name (Real names)", "Total Expected Time (min)", "Total Actual Time (min)"]
    )
    print(f"📊 Total time report generated: {total_path}")


if __name__ == "__main__":
    main()
