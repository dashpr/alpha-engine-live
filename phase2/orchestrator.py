"""
PHASE-2 INSTITUTIONAL ORCHESTRATOR (GITHUB PAGES READY)
------------------------------------------------------

Runs full allocator pipeline,
generates dashboard JSON,
and ensures it is committed for GitHub Pages hosting.
"""

import os
import subprocess
from phase2.signal_engine import build_signals
from phase2.dashboard_builder import build_dashboard


def git_commit_dashboard():
    """
    Commits updated dashboard/data.json so GitHub Pages can serve it.
    Safe in CI environment.
    """
    try:
        subprocess.run(["git", "config", "--global", "user.name", "github-actions"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"], check=True)

        subprocess.run(["git", "add", "dashboard/data.json"], check=True)
        subprocess.run(
            ["git", "commit", "-m", "Auto-update dashboard data [CI]"],
            check=False,
        )

        subprocess.run(["git", "push"], check=False)

        print("[ORCHESTRATOR] Dashboard JSON committed to repo.")

    except Exception as e:
        print(f"[ORCHESTRATOR] Git commit skipped: {e}")


def main():
    print("=== NEW PHASE-2 ORCHESTRATOR START ===")

    # Step-1: Build signals
    build_signals()

    # Step-2: Build dashboard JSON
    build_dashboard()

    # Step-3: Commit JSON for GitHub Pages
    git_commit_dashboard()

    print("=== PHASE-2 RUN COMPLETE ===")


if __name__ == "__main__":
    main()
