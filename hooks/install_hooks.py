"""
Install CONTEXTCORE git hooks into .git/hooks/
Run once: python hooks/install_hooks.py
"""
import shutil
import stat
import sys
from pathlib import Path


def install():
    hook_src = Path(__file__).parent / "post-commit"
    hook_dst = Path(".git") / "hooks" / "post-commit"

    if not Path(".git").exists():
        print("[FAIL] No .git directory found. Run from project root.")
        sys.exit(1)

    shutil.copy(hook_src, hook_dst)

    # Make executable on Unix
    hook_dst.chmod(
        hook_dst.stat().st_mode
        | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    )

    print("[PASS] Hook installed at .git/hooks/post-commit")
    print("[INFO] Every git commit will now trigger: contextcore index")


if __name__ == "__main__":
    install()
