"""
watch_site.py - Real-time File Watcher for Gabriele Antonini's Website.

Watches the 'notes/' directory for any new or modified HTML files,
and automatically rebuilds the site index in real-time.

Usage:
    python watch_site.py
"""

import time
from pathlib import Path
from build_site import build_site_manifest, NOTES_DIR

def get_dir_snapshot(directory: Path) -> dict:
    """Returns a dictionary of {file_path: mtime} for all files in the directory."""
    snapshot = {}
    if not directory.exists():
        return snapshot
    for p in directory.rglob("*"):
        if p.is_file() and not p.name.startswith("."):
            try:
                snapshot[str(p)] = p.stat().st_mtime
            except OSError:
                pass
    return snapshot

def watch():
    print(f"[*] Watching '{NOTES_DIR}' for changes...")
    print("    Create, edit, or delete any HTML file/folder inside 'notes/' to auto-update.")
    print("    Press Ctrl+C to stop.\n")

    # Initial build
    build_site_manifest()
    last_snapshot = get_dir_snapshot(NOTES_DIR)

    try:
        while True:
            time.sleep(1.0)
            current_snapshot = get_dir_snapshot(NOTES_DIR)
            if current_snapshot != last_snapshot:
                print("\n[+] Change detected in notes directory! Rebuilding site index...")
                build_site_manifest()
                last_snapshot = current_snapshot
                print("[*] Rebuilt successfully. Waiting for next change...")
    except KeyboardInterrupt:
        print("\n[*] Stopped watcher.")

if __name__ == "__main__":
    watch()
