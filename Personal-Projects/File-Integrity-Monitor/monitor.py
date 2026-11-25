
import hashlib
import json
import os
import tempfile

from datetime import datetime, timezone
from pathlib import Path

# Project configuration
TEST_DIR = Path("test_files")
REPORT_DIR = Path("reports")

BASELINE_FILE = REPORT_DIR / "baseline.json"
REPORT_FILE = REPORT_DIR / "integrity_report.txt"

HASH_ALGORITHM = "sha256"
CHUNK_SIZE = 65536


def calculate_hash(file_path):
    """Calculate the SHA-256 hash of a file."""

    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        while chunk := file.read(CHUNK_SIZE):
            sha256.update(chunk)

    return sha256.hexdigest()


def collect_hashes():
    """Collect hashes of all regular files in the test directory."""

    if not TEST_DIR.is_dir():
        raise FileNotFoundError(
            f"Test directory not found: {TEST_DIR}"
        )

    file_hashes = {}

    for file_path in sorted(TEST_DIR.rglob("*")):
        if file_path.is_symlink():
            continue

        if file_path.is_file():
            relative_path = str(
                file_path.relative_to(TEST_DIR)
            )

            file_hashes[relative_path] = calculate_hash(file_path)

    return file_hashes


def save_json_safely(destination, data):
    """Write JSON using a temporary file and atomic replacement."""

    destination.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=destination.parent,
            delete=False
        ) as temporary_file:

            temporary_path = Path(temporary_file.name)

            json.dump(data, temporary_file, indent=4)
            temporary_file.write("\n")

        os.replace(temporary_path, destination)

    finally:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()


def create_baseline():
    """Create a baseline containing the current file hashes."""

    try:
        hashes = collect_hashes()

        baseline = {
            "algorithm": HASH_ALGORITHM,
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "files": hashes
        }

        save_json_safely(BASELINE_FILE, baseline)

        print(f"[SUCCESS] Baseline created.")
        print(f"[INFO] Files recorded: {len(hashes)}")
        print(f"[INFO] Saved to: {BASELINE_FILE}")

    except (OSError, ValueError) as error:
        print(f"[ERROR] Could not create baseline: {error}")


def load_baseline():
    """Load and validate the saved baseline."""

    try:
        baseline = json.loads(
            BASELINE_FILE.read_text(encoding="utf-8")
        )

        if not isinstance(baseline, dict):
            raise ValueError("Baseline must be a JSON object.")

        if baseline.get("algorithm") != HASH_ALGORITHM:
            raise ValueError("Unsupported hashing algorithm.")

        if not isinstance(baseline.get("files"), dict):
            raise ValueError("Invalid baseline file records.")

        for file_path, file_hash in baseline["files"].items():
            if (
                not isinstance(file_path, str)
                or not isinstance(file_hash, str)
                or len(file_hash) != 64
                or any(c not in "0123456789abcdef" for c in file_hash)
            ):
                raise ValueError("Invalid file hash entry.")

        return baseline["files"]

    except FileNotFoundError:
        raise FileNotFoundError(
            "No baseline found. Create one first."
        )

    except json.JSONDecodeError:
        raise ValueError("Baseline JSON is corrupted.")


def generate_report(results):
    """Display and save the integrity report."""

    timestamp = datetime.now(timezone.utc).isoformat()

    lines = [
        "FILE INTEGRITY MONITOR REPORT",
        "=" * 50,
        f"Scan time (UTC): {timestamp}",
        "",
        f"Modified files: {len(results['modified'])}",
        f"New files: {len(results['new'])}",
        f"Deleted files: {len(results['deleted'])}",
        f"Unreadable files: {len(results['unreadable'])}",
        ""
    ]

    for category, files in [
        ("MODIFIED", results["modified"]),
        ("NEW", results["new"]),
        ("DELETED", results["deleted"]),
        ("UNREADABLE", results["unreadable"])
    ]:
        for file_path in files:
            lines.append(f"[{category}] {file_path}")

    if not any(results.values()):
        lines.append("[OK] No changes detected.")

    report = "\n".join(lines)

    print("\n" + report)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(
        report + "\n",
        encoding="utf-8"
    )

    print(f"\n[SUCCESS] Report saved to: {REPORT_FILE}")


def verify_integrity():
    """Compare current files against the saved baseline."""

    try:
        original = load_baseline()
        current = collect_hashes()

    except (OSError, ValueError) as error:
        print(f"[ERROR] {error}")
        return

    modified = []
    new_files = []
    deleted = []
    unreadable = []

    for file_path, old_hash in original.items():

        if file_path not in current:
            deleted.append(file_path)

        elif current[file_path] != old_hash:
            modified.append(file_path)

    for file_path in current:

        if file_path not in original:
            new_files.append(file_path)

    results = {
        "modified": modified,
        "new": new_files,
        "deleted": deleted,
        "unreadable": unreadable
    }

    generate_report(results)


def main():
    print("=" * 50)
    print("       FILE INTEGRITY MONITOR")
    print("=" * 50)

    print("1. Create baseline")
    print("2. Verify file integrity")

    choice = input("\nSelect an option (1 or 2): ").strip()

    if choice == "1":
        create_baseline()

    elif choice == "2":
        verify_integrity()

    else:
        print("[ERROR] Invalid option. Choose 1 or 2.")


if __name__ == "__main__":
    main()
