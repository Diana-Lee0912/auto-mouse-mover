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
#   ranges you set below.
#
# ---------------------------------------------------------------------
#  FIRST-TIME SETUP: macOS
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
#  FIRST-TIME SETUP: Windows
#   1. Download and install Python from https://www.python.org/downloads/
#      IMPORTANT: tick "Add python.exe to PATH" at the bottom of the installer.
#   2. Press the Start key, type "cmd", and open Command Prompt.
#   3. Type  python  (with a space after it), drag this file into the
#      window, and press Enter.
#
#  EVERY DAY AFTER THAT
#   Just repeat the "drag the file in and press Enter" step.
#   Keep the window open while it runs (minimizing it is fine).
#
#  HOW TO STOP
#   Press  Ctrl + C  in the window, or just close the window.
#
#  CHANGING THE SETTINGS
#   Open this file in TextEdit (macOS) or Notepad (Windows).
#   Only change the values in the SETTINGS block below; leave the rest alone.
#   Save, then run the file again.
# =====================================================================


# ┌──────────────────── SETTINGS (only change these) ────────────────────┐

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
import time
import datetime
import subprocess
import random
import importlib
import platform

IS_MAC = platform.system() == "Darwin"
IS_WINDOWS = platform.system() == "Windows"


# ── Install pyautogui (the library that moves the mouse) if missing ──
def _install_pyautogui():
    print("First run: installing the required package. This takes about a minute...\n")
    base = [sys.executable, "-m", "pip", "install", "--user", "pyautogui"]
    # Try a normal install first; some macOS Python setups block that,
    # so retry with an extra flag if needed.
    for cmd in (base, base + ["--break-system-packages"]):
        if subprocess.call(cmd) == 0:
            return True
    return False


def _exit_with(message, code=1):
    print(message)
    input("Press Enter to exit...")
    sys.exit(code)


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
        _exit_with("\n[Done] Install finished! Close this window and run the file again.", 0)


# ── Check the settings for mistakes ─────────────────────────────────
def _parse_time(text, name):
    try:
        h, m = text.strip().split(":")
        h, m = int(h), int(m)
        assert 0 <= h <= 23 and 0 <= m <= 59
        return h * 60 + m
    except Exception:
        _exit_with(f'[Error] {name} in SETTINGS has the wrong format: {text!r}. '
                   f'It should look like "08:30".')


START_MIN_1 = _parse_time(START_EARLIEST, "START_EARLIEST")
START_MIN_2 = _parse_time(START_LATEST, "START_LATEST")
STOP_MIN_1 = _parse_time(STOP_EARLIEST, "STOP_EARLIEST")
STOP_MIN_2 = _parse_time(STOP_LATEST, "STOP_LATEST")

if START_MIN_1 > START_MIN_2 or STOP_MIN_1 > STOP_MIN_2 or START_MIN_2 >= STOP_MIN_1:
    _exit_with("[Error] The times in SETTINGS don't make sense. Each EARLIEST must be "
               "at or before its LATEST, and START_LATEST must be before STOP_EARLIEST.")

DAY_NAMES = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
_unknown_days = []
WORKDAY_SET = set()
for _day in WORKDAYS.replace(" ", ",").split(","):
    _day = _day.strip().lower()[:3]
    if not _day:
        continue
    if _day in DAY_NAMES:
        WORKDAY_SET.add(DAY_NAMES.index(_day))
    else:
        _unknown_days.append(_day)
if _unknown_days or not WORKDAY_SET:
    _exit_with(f'[Error] WORKDAYS in SETTINGS should look like "Mon,Tue,Wed,Thu,Fri". '
               f'Got: {WORKDAYS!r}')


# ── Pick today's random start and stop times ────────────────────────
def new_daily_schedule():
    s = random.randint(START_MIN_1, START_MIN_2)
    e = random.randint(STOP_MIN_1, STOP_MIN_2)
    return s // 60, s % 60, e // 60, e % 60


TODAY_START_H, TODAY_START_M, TODAY_STOP_H, TODAY_STOP_M = new_daily_schedule()


def at(day, hour, minute):
    return day.replace(hour=hour, minute=minute, second=0, microsecond=0)


def in_work_time(now):
    if now.weekday() not in WORKDAY_SET:
        return False
    return at(now, TODAY_START_H, TODAY_START_M) <= now < at(now, TODAY_STOP_H, TODAY_STOP_M)


def next_work_start(now):
    """Find when the next work period starts (skips days that aren't workdays)."""
    for i in range(8):
        day = now + datetime.timedelta(days=i)
        if day.weekday() in WORKDAY_SET:
            start = at(day, TODAY_START_H, TODAY_START_M)
            if start > now:
                return start
    return now + datetime.timedelta(minutes=1)


# ── Open / quit Teams (macOS and Windows) ───────────────────────────
def open_teams():
    if not AUTO_OPEN_CLOSE_TEAMS:
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
    if not AUTO_OPEN_CLOSE_TEAMS:
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
    global TODAY_START_H, TODAY_START_M, TODAY_STOP_H, TODAY_STOP_M

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
                time.sleep(MOUSE_INTERVAL_SECONDS)
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
    main()
