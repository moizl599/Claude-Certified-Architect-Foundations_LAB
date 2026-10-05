#!/usr/bin/env python3
"""
CCAR-F Labs — One-Click Deploy Script
======================================
Run this script to automatically build and launch the lab environment.

Usage:
    python deploy.py                  # Deploy with dry-run mode (no API key needed)
    python deploy.py --key sk-ant-... # Deploy with your Anthropic API key
    python deploy.py --stop           # Stop and remove containers
    python deploy.py --rebuild        # Force rebuild from scratch
    python deploy.py --status         # Check if labs are running
"""

import subprocess
import sys
import os
import shutil
import time
import argparse
import webbrowser
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────
APP_NAME = "ccar-f-labs"
PORT = 8000
URL = f"http://localhost:{PORT}"
COMPOSE_FILE = "docker-compose.yml"


def color(text, code):
    """ANSI color wrapper."""
    if not sys.stdout.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"


def green(t):  return color(t, "32")
def yellow(t): return color(t, "33")
def red(t):    return color(t, "31")
def cyan(t):   return color(t, "36")
def bold(t):   return color(t, "1")
def dim(t):    return color(t, "2")


def banner():
    print()
    print(cyan("  ╔═══════════════════════════════════════════════╗"))
    print(cyan("  ║") + bold("   CCAR-F Interactive Labs — Deploy Script    ") + cyan("║"))
    print(cyan("  ║") + dim("   Claude Certified Architect — Foundations    ") + cyan("║"))
    print(cyan("  ╚═══════════════════════════════════════════════╝"))
    print()


def check_docker():
    """Verify Docker and Docker Compose are available."""
    print(f"  {'Checking Docker...':<42}", end="", flush=True)
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            print(red("✗"))
            print(red("\n  Docker is not installed or not running."))
            print(dim("  Install from: https://docs.docker.com/get-docker/"))
            sys.exit(1)
        version = result.stdout.strip().split(",")[0]
        print(green(f"✓  {version}"))
    except FileNotFoundError:
        print(red("✗"))
        print(red("\n  Docker is not installed."))
        print(dim("  Install from: https://docs.docker.com/get-docker/"))
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print(red("✗  (timed out — is Docker Desktop running?)"))
        sys.exit(1)

    print(f"  {'Checking Docker Compose...':<42}", end="", flush=True)
    try:
        # Try `docker compose` (v2) first
        result = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(green(f"✓  {version}"))
            return "docker compose"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    try:
        # Fall back to `docker-compose` (v1)
        result = subprocess.run(
            ["docker-compose", "--version"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(green(f"✓  {version}"))
            return "docker-compose"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    print(red("✗"))
    print(red("\n  Docker Compose is not available."))
    print(dim("  It ships with Docker Desktop. Make sure Docker Desktop is running."))
    sys.exit(1)


def check_docker_running():
    """Verify the Docker daemon is actually running."""
    print(f"  {'Checking Docker daemon...':<42}", end="", flush=True)
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            print(red("✗"))
            print(red("\n  Docker daemon is not running."))
            print(dim("  Start Docker Desktop and try again."))
            sys.exit(1)
        print(green("✓  Running"))
    except subprocess.TimeoutExpired:
        print(red("✗  (timed out)"))
        print(dim("  Docker daemon may be starting up. Wait a moment and try again."))
        sys.exit(1)


def setup_env(api_key=None):
    """Create .env file with the API key."""
    project_dir = get_project_dir()
    env_file = project_dir / ".env"

    print(f"  {'Setting up .env...':<42}", end="", flush=True)

    if api_key:
        env_file.write_text(f"ANTHROPIC_API_KEY={api_key}\n")
        masked = api_key[:10] + "..." + api_key[-4:]
        print(green(f"✓  Key: {masked}"))
    elif env_file.exists():
        content = env_file.read_text().strip()
        if "xxxxx" not in content and "ANTHROPIC_API_KEY=" in content:
            print(green("✓  Existing key found"))
        else:
            env_file.write_text("ANTHROPIC_API_KEY=sk-ant-xxxxx\n")
            print(yellow("⚠  Dry-run mode (no API key)"))
    else:
        env_file.write_text("ANTHROPIC_API_KEY=sk-ant-xxxxx\n")
        print(yellow("⚠  Dry-run mode (no API key)"))


def get_project_dir():
    """Find the project directory."""
    # Script could be inside the project or the zip could be extracted
    script_dir = Path(__file__).resolve().parent

    # If we're already in the project directory
    if (script_dir / "docker-compose.yml").exists():
        return script_dir

    # If the project is a subdirectory
    sub = script_dir / APP_NAME
    if (sub / "docker-compose.yml").exists():
        return sub

    print(red(f"\n  Cannot find {COMPOSE_FILE} in {script_dir}"))
    print(dim(f"  Make sure deploy.py is inside the {APP_NAME}/ folder."))
    sys.exit(1)


def build_and_start(compose_cmd, rebuild=False):
    """Build Docker image and start the container."""
    project_dir = get_project_dir()

    # Build
    print()
    print(bold("  Building Docker image..."))
    print(dim("  (this may take a minute on first run)"))
    print()

    build_args = compose_cmd.split() + ["build"]
    if rebuild:
        build_args.append("--no-cache")

    result = subprocess.run(
        build_args,
        cwd=str(project_dir),
        timeout=300
    )
    if result.returncode != 0:
        print(red("\n  Build failed. Check the output above for errors."))
        sys.exit(1)

    # Start
    print()
    print(bold("  Starting containers..."))

    start_args = compose_cmd.split() + ["up", "-d"]
    result = subprocess.run(
        start_args,
        cwd=str(project_dir),
        timeout=60
    )
    if result.returncode != 0:
        print(red("\n  Failed to start containers."))
        sys.exit(1)


def wait_for_healthy():
    """Wait for the app to be ready."""
    print()
    print(f"  {'Waiting for app to start...':<42}", end="", flush=True)

    import urllib.request
    import urllib.error

    for attempt in range(30):
        try:
            req = urllib.request.Request(f"{URL}/api/health", method="GET")
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    import json
                    data = json.loads(resp.read())
                    has_key = data.get("api_key_configured", False)
                    print(green("✓  Ready"))
                    return has_key
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
        time.sleep(1)

    print(yellow("⚠  App may still be starting"))
    return False


def stop_containers(compose_cmd):
    """Stop and remove containers."""
    project_dir = get_project_dir()
    print(bold("  Stopping containers..."))
    subprocess.run(
        compose_cmd.split() + ["down"],
        cwd=str(project_dir),
        timeout=30
    )
    print(green("\n  ✓ Containers stopped and removed."))


def check_status(compose_cmd):
    """Check if the labs are currently running."""
    project_dir = get_project_dir()
    result = subprocess.run(
        compose_cmd.split() + ["ps", "--format", "table"],
        cwd=str(project_dir),
        capture_output=True, text=True, timeout=10
    )
    if result.returncode == 0 and "ccar" in result.stdout.lower():
        print(green("  ✓ Labs are running"))
        print(dim(f"  Open {URL} in your browser"))
        print()
        print(result.stdout)
    else:
        print(yellow("  ⚠ Labs are not running"))
        print(dim("  Run: python deploy.py"))


def open_browser():
    """Open the labs in the default browser."""
    print(f"  {'Opening browser...':<42}", end="", flush=True)
    try:
        webbrowser.open(URL)
        print(green(f"✓  {URL}"))
    except Exception:
        print(yellow(f"⚠  Open manually: {URL}"))


def summary(has_key):
    """Print final summary."""
    print()
    print(cyan("  ╔═══════════════════════════════════════════════╗"))
    print(cyan("  ║") + green("           ✓ Labs are running!                 ") + cyan("║"))
    print(cyan("  ╚═══════════════════════════════════════════════╝"))
    print()
    print(f"  {bold('URL:')}           {URL}")
    print(f"  {bold('Mode:')}          {'🟢 Live (API key configured)' if has_key else '🛡️  Dry Run (no API cost)'}")
    print(f"  {bold('Labs:')}          10 labs across 5 domains")
    print(f"  {bold('Steps:')}         31 guided steps")
    print()
    print(dim("  Commands:"))
    print(dim(f"    python deploy.py --stop      Stop the labs"))
    print(dim(f"    python deploy.py --rebuild   Rebuild from scratch"))
    print(dim(f"    python deploy.py --status    Check status"))
    print(dim(f"    python deploy.py --key KEY   Set API key"))
    print()

    if not has_key:
        print(yellow("  Tip: To enable live API calls, run:"))
        print(yellow(f"    python deploy.py --key sk-ant-your-key-here"))
        print()


def main():
    parser = argparse.ArgumentParser(
        description="CCAR-F Labs — One-Click Deploy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python deploy.py                    Build and launch (dry-run mode)
  python deploy.py --key sk-ant-...   Launch with API key for live mode
  python deploy.py --stop             Stop the running labs
  python deploy.py --rebuild          Force a clean rebuild
  python deploy.py --status           Check if labs are running
  python deploy.py --no-browser       Deploy without opening browser
        """
    )
    parser.add_argument("--key", help="Anthropic API key (sk-ant-...)")
    parser.add_argument("--stop", action="store_true", help="Stop and remove containers")
    parser.add_argument("--rebuild", action="store_true", help="Force rebuild (no cache)")
    parser.add_argument("--status", action="store_true", help="Check if labs are running")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser after deploy")
    args = parser.parse_args()

    banner()

    # Pre-flight checks
    print(bold("  Pre-flight checks"))
    print(dim("  ─────────────────────────────────────────────"))
    compose_cmd = check_docker()
    check_docker_running()

    # Handle --stop
    if args.stop:
        stop_containers(compose_cmd)
        return

    # Handle --status
    if args.status:
        check_status(compose_cmd)
        return

    # Setup
    setup_env(args.key)
    print()

    # Build & start
    print(bold("  Deployment"))
    print(dim("  ─────────────────────────────────────────────"))
    build_and_start(compose_cmd, rebuild=args.rebuild)

    # Wait for healthy
    has_key = wait_for_healthy()

    # Open browser
    if not args.no_browser:
        open_browser()

    # Done
    summary(has_key)


if __name__ == "__main__":
    main()
