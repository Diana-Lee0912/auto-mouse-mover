# =====================================================================
#   auto-mouse-mover
#   Keeps your computer and Microsoft Teams from going idle during work hours.
#   https://github.com/Diana-Lee0912/auto-mouse-mover
# =====================================================================
#
#  WHAT IT DOES
#   During work hours, it moves the mouse 1 pixel and back every minute,
#   so your computer and Teams don't switch to "Away".
#   It opens Teams when work starts and quits Teams when work ends.
#   Each day, the start and stop times are picked at random from the
#   ranges you set.
#
# ---------------------------------------------------------------------
#  QUICK INSTALL (recommended)
#   Paste one line into Terminal (macOS) or PowerShell (Windows).
#   The installer asks for your work hours, then starts the program.
#
#   macOS:
#     curl -fsSL https://raw.githubusercontent.com/Diana-Lee0912/auto-mouse-mover/main/install.sh | bash
#   Windows (PowerShell):
#     irm https://raw.githubusercontent.com/Diana-Lee0912/auto-mouse-mover/main/install.ps1 | iex
#
# ---------------------------------------------------------------------
#  MANUAL SETUP: macOS
#   1. Open Terminal: press Command + Space, type "Terminal", press Enter.
#   2. Type  python3  (with a space after it), drag this file into the
#      Terminal window, and press Enter.
#      -> If a window asks to install "Command Line Developer Tools",
#         click Install, then do step 2 again when it finishes.
#   3. The first run installs what it needs. Wait for it (about 1 minute).
#   4. Give permission (without it, the mouse won't move):
#      System Settings -> Privacy & Security -> Accessibility -> turn on Terminal.
#      Then quit Terminal completely (Command + Q) and repeat steps 1 and 2.
#
#  MANUAL SETUP: Windows
#   1. Download and install Python from https://www.python.org/downloads/
#      IMPORTANT: tick "Add python.exe to PATH" at the bottom of the installer.
#   2. Press the Start key, type "cmd", and open Command Prompt.
#   3. Type  python  (with a space after it), drag this file into the
#      window, and press Enter.
#
#  HOW TO STOP
#   Press  Ctrl + C  in the window, or just close the window.
#
#  CHANGING THE SETTINGS
#   Easiest: run the program with --setup and answer the questions:
#     python3 auto_mouse_mover.py --setup      (Windows: python instead of python3)
#   (If you used the quick installer, just double-click "Change settings".)
#   Your answers are saved in config.json next to this file.
#
#   You can also edit the SETTINGS block below. But if config.json exists,
#   it takes priority over the block, so delete config.json first.
# =====================================================================


# ┌──────────────────────────── SETTINGS ────────────────────────────────┐

# Start time: each day, a random time between these two is picked.
# Use 24-hour "HH:MM" format.
START_EARLIEST = "08:30"
START_LATEST   = "08:40"

# Stop time: each day, a random time between these two is picked.
STOP_EARLIEST  = "16:20"
STOP_LATEST    = "16:40"

# Which days to run. Separate days with commas.
# Example: to include Saturday, write "Mon,Tue,Wed,Thu,Fri,Sat"
WORKDAYS = "Mon,Tue,Wed,Thu,Fri"

# How many seconds between mouse moves (60 = once a minute; usually fine as is)
MOUSE_INTERVAL_SECONDS = 60

# Open and quit Teams automatically? True = yes, False = no (capital T / F)
AUTO_OPEN_CLOSE_TEAMS = True

# └──────────────────────────────────────────────────────────────────────┘
#              Everything below is the program itself. No need to edit.


import sys
import os
import json
import time
import datetime
import subprocess
import random
import importlib
import platform

IS_MAC = platform.system() == "Darwin"
IS_WINDOWS = platform.system() == "Windows"
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def _exit_with(message, code=1):
    print(message)
    try:
        input("Press Enter to exit...")
    except EOFError:
        pass
    sys.exit(code)


# ── Install pyautogui (the library that moves the mouse) if missing ──
def _install_pyautogui():
    print("First run: installing the required package. This takes about a minute...\n")
    base = [sys.executable, "-m", "pip", "install", "pyautogui"]
    # Try a per-user install first. Some macOS Python setups block that, so
    # retry with an extra flag. Virtual environments don't allow --user at all,
    # so finally try a plain install.
    attempts = (
        base + ["--user"],
        base + ["--user", "--break-system-packages"],
        base,
    )
    for cmd in attempts:
        if subprocess.call(cmd) == 0:
            return True
    return False


try:
    import pyautogui
except ModuleNotFoundError:
    if not _install_pyautogui():
        _exit_with("\n[Error] Automatic install failed. Please take a screenshot of the "
                   "messages above and open an Issue on the GitHub project page.")
    import site
    user_site = site.getusersitepackages()
    if user_site not in sys.path:
        sys.path.append(user_site)
    importlib.invalidate_caches()
    try:
        import pyautogui
    except ModuleNotFoundError:
        _exit_with("\n[Done] Install finished! Close this window and run the program again.", 0)


# ── Reading and checking settings ───────────────────────────────────
DAY_NAMES = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def parse_time(text):
    """'08:30' -> minutes since midnight. Raises ValueError with a friendly message."""
    try:
        h, m = str(text).strip().split(":")
        h, m = int(h), int(m)
    except ValueError:
        raise ValueError(f'{text!r} is not a time. Use "HH:MM", like 08:30.')
    if not (0 <= h <= 23 and 0 <= m <= 59):
        raise ValueError(f'{text!r} is not a valid time. Use 24-hour "HH:MM", like 17:30.')
    return h * 60 + m


def parse_days(text):
    """'Mon,Tue' -> {0, 1}"""
    days = set()
    for part in str(text).replace(" ", ",").split(","):
        part = part.strip().lower()
        if not part:
            continue
        if part[:3] not in DAY_NAMES:
            raise ValueError(f"{part!r} is not a day. Use Mon, Tue, Wed, Thu, Fri, Sat, Sun.")
        days.add(DAY_NAMES.index(part[:3]))
    if not days:
        raise ValueError("List at least one day, like Mon,Tue,Wed,Thu,Fri.")
    return days


def parse_yes_no(value):
    # Also accepts "False" written in quotes, since that's an easy mistake
    if isinstance(value, bool):
        return value
    v = str(value).strip().lower()
    if v in ("y", "yes", "true", "1"):
        return True
    if v in ("n", "no", "false", "0"):
        return False
    raise ValueError(f"{value!r} should be y (yes) or n (no).")


def parse_interval(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 1:
        raise ValueError(f"MOUSE_INTERVAL_SECONDS should be a number of seconds, "
                         f"1 or more (no quotes). Got: {value!r}")
    return value


def build_settings(raw):
    """Check every setting and turn it into the form the program uses."""
    s = {
        "start": (parse_time(raw["start_earliest"]), parse_time(raw["start_latest"])),
        "stop": (parse_time(raw["stop_earliest"]), parse_time(raw["stop_latest"])),
        "workdays": parse_days(raw["workdays"]),
        "teams": parse_yes_no(raw["auto_open_close_teams"]),
        "interval": parse_interval(raw["mouse_interval_seconds"]),
    }
    if s["start"][0] > s["start"][1]:
        raise ValueError("The earliest start time must be at or before the latest start time.")
    if s["stop"][0] > s["stop"][1]:
        raise ValueError("The earliest stop time must be at or before the latest stop time.")
    if s["start"][1] >= s["stop"][0]:
        raise ValueError("The latest start time must be before the earliest stop time.")
    return s


def settings_from_block():
    return {
        "start_earliest": START_EARLIEST,
        "start_latest": START_LATEST,
        "stop_earliest": STOP_EARLIEST,
        "stop_latest": STOP_LATEST,
        "workdays": WORKDAYS,
        "auto_open_close_teams": AUTO_OPEN_CLOSE_TEAMS,
        "mouse_interval_seconds": MOUSE_INTERVAL_SECONDS,
    }


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        print(f"[Warning] Couldn't read {CONFIG_FILE}; using the SETTINGS block instead.")
        return {}


def save_config(raw):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(raw, f, indent=2)
        print(f"\nSaved to {CONFIG_FILE}")
        print("To change these later, run this program with --setup.\n")
    except OSError as e:
        print(f"\n[Warning] Couldn't save your answers ({e}). They'll be used this time only.\n")


# ── Interactive setup (python3 auto_mouse_mover.py --setup) ─────────
def _ask(question, default, check):
    while True:
        answer = input(f"{question} [{default}]: ").strip()
        value = answer or str(default)
        try:
            check(value)
            return value
        except ValueError as e:
            print(f"  -> {e} Please try again.")


def run_setup(raw):
    print("\n=== Setup ===")
    print("Each day, the program starts at a random time between the earliest and latest")
    print("start time, and stops at a random time between the earliest and latest stop time.")
    print("Press Enter to keep the value shown in [brackets].\n")
    def ask_time(question, default):
        minutes = parse_time(_ask(question, default, parse_time))
        return f"{minutes // 60:02d}:{minutes % 60:02d}"  # store 9:00 as 09:00

    while True:
        new = dict(raw)
        new["start_earliest"] = ask_time("Earliest start time (HH:MM)", raw["start_earliest"])
        new["start_latest"] = ask_time("Latest start time   (HH:MM)", raw["start_latest"])
        new["stop_earliest"] = ask_time("Earliest stop time  (HH:MM)", raw["stop_earliest"])
        new["stop_latest"] = ask_time("Latest stop time    (HH:MM)", raw["stop_latest"])
        new["workdays"] = _ask("Workdays (e.g. Mon,Tue,Wed,Thu,Fri)", raw["workdays"], parse_days)
        try:
            teams_default = "y" if parse_yes_no(raw["auto_open_close_teams"]) else "n"
        except ValueError:
            teams_default = "y"
        new["auto_open_close_teams"] = parse_yes_no(
            _ask("Open and quit Microsoft Teams automatically? (y/n)", teams_default, parse_yes_no))
        try:
            build_settings(new)
            break
        except ValueError as e:
            print(f"\n  -> {e} Let's go through it again.\n")
            raw = new  # keep the answers as the new defaults
    save_config(new)
    return new


def load_settings(force_setup=False):
    raw = settings_from_block()
    config = load_config()
    raw.update({k: v for k, v in config.items() if k in raw})
    if force_setup:
        raw = run_setup(raw)
    try:
        return build_settings(raw)
    except ValueError as e:
        where = "config.json" if os.path.exists(CONFIG_FILE) else "the SETTINGS block"
        _exit_with(f"[Error] Problem in {where}: {e}\n"
                   f"Run this program with --setup to fix it.")


S = None  # the checked settings; filled in by main()


# ── Pick today's random start and stop times ────────────────────────
def new_daily_schedule():
    s = random.randint(*S["start"])
    e = random.randint(*S["stop"])
    return s // 60, s % 60, e // 60, e % 60


TODAY_START_H = TODAY_START_M = TODAY_STOP_H = TODAY_STOP_M = 0


def at(day, hour, minute):
    return day.replace(hour=hour, minute=minute, second=0, microsecond=0)


def in_work_time(now):
    if now.weekday() not in S["workdays"]:
        return False
    return at(now, TODAY_START_H, TODAY_START_M) <= now < at(now, TODAY_STOP_H, TODAY_STOP_M)


def next_work_start(now):
    """Find when the next work period starts (skips days that aren't workdays)."""
    for i in range(8):
        day = now + datetime.timedelta(days=i)
        if day.weekday() in S["workdays"]:
            start = at(day, TODAY_START_H, TODAY_START_M)
            if start > now:
                return start
    return now + datetime.timedelta(minutes=1)


# ── Open / quit Teams (macOS and Windows) ───────────────────────────
def open_teams():
    if not S["teams"]:
        return
    print("[Teams] Opening Microsoft Teams...")
    try:
        if IS_MAC:
            subprocess.Popen(["open", "-a", "Microsoft Teams"])
        elif IS_WINDOWS:
            subprocess.Popen('start "" msteams:', shell=True)
        time.sleep(5)  # give Teams a moment to start
    except Exception as e:
        print(f"[Teams] Couldn't open Teams (the mouse mover still works): {e}")


def close_teams():
    if not S["teams"]:
        return
    print("[Teams] Quitting Microsoft Teams...")
    try:
        if IS_MAC:
            subprocess.run(["osascript", "-e", 'quit app "Microsoft Teams"'],
                           capture_output=True)
        elif IS_WINDOWS:
            for exe in ("ms-teams.exe", "Teams.exe"):  # new and classic Teams
                subprocess.run(["taskkill", "/IM", exe, "/F"], capture_output=True)
    except Exception as e:
        print(f"[Teams] Couldn't quit Teams: {e}")


# ── Move the mouse ─────────────────────────────────────────────────
def move_mouse():
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    try:
        x, y = pyautogui.position()
        pyautogui.moveTo(x + 1, y, duration=0.1)
        pyautogui.moveTo(x, y, duration=0.1)
        print(f"[{now_str}] Mouse moved")
    except pyautogui.FailSafeException:
        # pyautogui refuses to move while the pointer is in a screen corner
        # (a safety feature), so skip this round.
        print(f"[{now_str}] Mouse is in a screen corner, skipping this time")


# ── Main loop ──────────────────────────────────────────────────────
def main():
    global S, TODAY_START_H, TODAY_START_M, TODAY_STOP_H, TODAY_STOP_M

    S = load_settings(force_setup="--setup" in sys.argv[1:])
    TODAY_START_H, TODAY_START_M, TODAY_STOP_H, TODAY_STOP_M = new_daily_schedule()

    print("=== auto-mouse-mover started ===")
    print(f"Today's schedule: start {TODAY_START_H:02d}:{TODAY_START_M:02d} / "
          f"stop {TODAY_STOP_H:02d}:{TODAY_STOP_M:02d}")
    print("To stop, press Ctrl+C or close this window\n")

    active = False
    last_date = datetime.date.today()
    shown_next_start = None

    while True:
        try:
            # New day: pick new random start and stop times
            today = datetime.date.today()
            if today != last_date:
                TODAY_START_H, TODAY_START_M, TODAY_STOP_H, TODAY_STOP_M = new_daily_schedule()
                last_date = today
                shown_next_start = None
                print(f"\n[New day] Today's schedule: start {TODAY_START_H:02d}:{TODAY_START_M:02d} / "
                      f"stop {TODAY_STOP_H:02d}:{TODAY_STOP_M:02d}")

            now = datetime.datetime.now()
            working = in_work_time(now)

            if working and not active:
                print(f"\n[{now.strftime('%H:%M')}] > Work period started")
                shown_next_start = None
                open_teams()
                active = True
            elif not working and active:
                print(f"\n[{now.strftime('%H:%M')}] # Work period ended, pausing")
                close_teams()
                active = False

            if active:
                move_mouse()
                time.sleep(S["interval"])
            else:
                next_start = next_work_start(now)
                if next_start != shown_next_start:
                    print(f"Next work period: {next_start.strftime('%a %m/%d %H:%M')} "
                          f"(waiting quietly until then)")
                    shown_next_start = next_start
                # Check the clock every 60 seconds so we never oversleep
                time.sleep(max(1, min((next_start - now).total_seconds(), 60)))

        except KeyboardInterrupt:
            print("\n\n[Stopped] Stopped by user.")
            if active:
                close_teams()
            sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C (or a closed input) during setup
        print("\n\n[Stopped] Setup cancelled; nothing was changed.")
        sys.exit(0)
