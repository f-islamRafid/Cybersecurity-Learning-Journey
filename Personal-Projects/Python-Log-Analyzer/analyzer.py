
import re
import ipaddress
from collections import Counter
from pathlib import Path
from datetime import datetime

# Project configuration
LOG_FILE = Path("logs/sample_auth.log")
REPORT_DIR = Path("reports")
REPORT_FILE = REPORT_DIR / "analysis_report.txt"
ALERT_THRESHOLD = 3

# Expected log format
LOG_PATTERN = re.compile(
    r"^(\d{4}-\d{2}-\d{2}) "
    r"(\d{2}:\d{2}:\d{2}) "
    r"(FAILED|SUCCESS) LOGIN from "
    r"(\S+)$"
)


def analyze_logs():
    total_attempts = 0
    successful_logins = 0
    failed_logins = 0
    malformed_records = 0

    failed_by_ip = Counter()

    if not LOG_FILE.exists():
        print(f"[ERROR] Log file not found: {LOG_FILE}")
        return None

    with LOG_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            match = LOG_PATTERN.fullmatch(line)

            if not match:
                malformed_records += 1
                continue

            date, time, status, ip = match.groups()

            # Validate date and time
            try:
                datetime.strptime(
                    f"{date} {time}", "%Y-%m-%d %H:%M:%S"
                )
            except ValueError:
                malformed_records += 1
                continue

            # Validate IP address
            try:
                ipaddress.ip_address(ip)
            except ValueError:
                malformed_records += 1
                continue

            total_attempts += 1

            if status == "FAILED":
                failed_logins += 1
                failed_by_ip[ip] += 1

            elif status == "SUCCESS":
                successful_logins += 1

    # Identify repeated failed login activity
    alerts = {
        ip: count
        for ip, count in failed_by_ip.items()
        if count >= ALERT_THRESHOLD
    }

    return {
        "total": total_attempts,
        "successful": successful_logins,
        "failed": failed_logins,
        "malformed": malformed_records,
        "failed_by_ip": failed_by_ip,
        "alerts": alerts,
    }


def generate_report(results):
    lines = [
        "=" * 48,
        "             PYTHON LOG ANALYZER",
        "=" * 48,
        "",
        f"Total login attempts : {results['total']}",
        f"Successful logins    : {results['successful']}",
        f"Failed logins        : {results['failed']}",
        f"Malformed records    : {results['malformed']}",
        "",
        "FAILED LOGIN ATTEMPTS BY IP",
        "-" * 48,
    ]

    if results["failed_by_ip"]:
        for ip, count in sorted(results["failed_by_ip"].items()):
            lines.append(f"{ip:<25} {count} failures")
    else:
        lines.append("No failed login attempts found.")

    lines.extend([
        "",
        f"REPEATED FAILURE ALERTS (Threshold: {ALERT_THRESHOLD})",
        "-" * 48,
    ])

    if results["alerts"]:
        for ip, count in sorted(results["alerts"].items()):
            lines.append(f"[ALERT] {ip} - {count} failed attempts")
    else:
        lines.append("No repeated failure alerts.")

    lines.extend(["", "=" * 48])

    report = "\n".join(lines)

    print(report)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(report + "\n", encoding="utf-8")

    print(f"\n[+] Report saved to: {REPORT_FILE}")


def main():
    print("[*] Starting Python Log Analyzer...\n")

    results = analyze_logs()

    if results is not None:
        generate_report(results)


if __name__ == "__main__":
    main()
