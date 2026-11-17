# =====================================================================
#   防閒置小工具（自動輕移滑鼠 + 定時開關 Teams）
# =====================================================================
#
#  【這是做什麼的？】
#   上班時間內，每隔一段時間把滑鼠輕輕移動 1 格再移回來，
#   讓電腦和 Teams 不會變成「離開」狀態。
#   上班時會自動打開 Teams，下班時自動關掉。
#   每天的上下班時間，會在你設定的範圍內隨機挑一個。
#
# ---------------------------------------------------------------------
#  【第一次使用：Mac】
#   1. 打開「終端機」：按 Command + 空白鍵，輸入 Terminal，按 Enter。
#   2. 在終端機輸入  python3  （後面要空一格），
#      再把這個檔案用滑鼠「拖進」終端機視窗，然後按 Enter。
#      → 如果跳出視窗說要安裝「指令列開發者工具」，按「安裝」，
#        裝好之後再做一次步驟 2。
#   3. 第一次執行會自動安裝需要的東西，等它跑完就好（約 1 分鐘）。
#   4. 給權限（不給的話滑鼠不會動）：
#      系統設定 → 隱私權與安全性 → 輔助使用 → 把「終端機」打開。
#      打開後，把終端機完全關掉（Command + Q），再重新做步驟 1、2。
#
#  【第一次使用：Windows】
#   1. 到 https://www.python.org/downloads/ 下載並安裝 Python。
#      ⚠ 安裝畫面最下方「Add python.exe to PATH」一定要打勾！
#   2. 按開始鍵，輸入 cmd，打開「命令提示字元」。
#   3. 輸入  python  （後面要空一格），把這個檔案拖進視窗，按 Enter。
#
#  【之後每天怎麼用？】
#   重複上面「拖檔案進去、按 Enter」那一步就好。
#   視窗要一直開著程式才會運作（可以縮小，但不要關掉）。
#
#  【怎麼停止？】
#   在那個視窗裡按  Ctrl + C ，或直接把視窗關掉。
#
#  【想改時間或設定？】
#   用「文字編輯」(Mac) 或「記事本」(Windows) 打開這個檔案，
#   只改下面「設定區」裡引號或等號後面的值就好，其他地方都不用動。
#   改完存檔，重新執行一次即可。
# =====================================================================


# ┌───────────────────────── 設定區（只要改這裡）─────────────────────────┐

# 上班時間：每天會在這兩個時間之間隨機挑一個開始（24 小時制，格式 "時:分"）
上班_最早 = "08:30"
上班_最晚 = "08:40"

# 下班時間：每天會在這兩個時間之間隨機挑一個結束
下班_最早 = "16:20"
下班_最晚 = "16:40"

# 哪幾天要上班：週一到週五就寫 "一二三四五"
# 例如週六也要，就改成 "一二三四五六"
上班日 = "一二三四五"

# 每隔幾秒動一次滑鼠（60 = 每分鐘一次，通常不用改）
滑鼠間隔秒數 = 60

# 要不要自動開關 Teams？要就寫 True，不要就寫 False（注意大小寫）
自動開關Teams = True

# └────────────────────────────────────────────────────────────────────┘
#                  ↓↓↓ 以下是程式本體，不需要修改 ↓↓↓


import sys
import os
import time
import datetime
import subprocess
import random
import importlib
import platform

IS_MAC = platform.system() == "Darwin"
IS_WINDOWS = platform.system() == "Windows"


# ── 自動安裝 pyautogui（控制滑鼠用的套件）──────────────────────────
def _install_pyautogui():
    print("第一次使用，正在自動安裝需要的套件，請稍等（約 1 分鐘）…\n")
    base = [sys.executable, "-m", "pip", "install", "--user", "pyautogui"]
    # 先正常安裝；某些 Mac 的 Python 會擋，就加參數再試一次
    for cmd in (base, base + ["--break-system-packages"]):
        if subprocess.call(cmd) == 0:
            return True
    return False


try:
    import pyautogui
except ModuleNotFoundError:
    if not _install_pyautogui():
        print("\n❌ 自動安裝失敗。請把上面的錯誤訊息截圖，到 GitHub 專案頁面開一個 Issue 回報。")
        input("按 Enter 結束…")
        sys.exit(1)
    import site
    user_site = site.getusersitepackages()
    if user_site not in sys.path:
        sys.path.append(user_site)
    importlib.invalidate_caches()
    try:
        import pyautogui
    except ModuleNotFoundError:
        print("\n✅ 安裝完成！請把視窗關掉，再重新執行一次這個檔案。")
        input("按 Enter 結束…")
        sys.exit(0)


# ── 檢查設定有沒有寫錯 ─────────────────────────────────────────────
def _parse_time(text, name):
    try:
        h, m = text.strip().split(":")
        h, m = int(h), int(m)
        assert 0 <= h <= 23 and 0 <= m <= 59
        return h * 60 + m
    except Exception:
        print(f"❌ 設定區的「{name}」格式不對：{text!r}，應該像 \"08:30\" 這樣。")
        input("按 Enter 結束…")
        sys.exit(1)


START_MIN_1 = _parse_time(上班_最早, "上班_最早")
START_MIN_2 = _parse_time(上班_最晚, "上班_最晚")
STOP_MIN_1 = _parse_time(下班_最早, "下班_最早")
STOP_MIN_2 = _parse_time(下班_最晚, "下班_最晚")

if START_MIN_1 > START_MIN_2 or STOP_MIN_1 > STOP_MIN_2 or START_MIN_2 >= STOP_MIN_1:
    print("❌ 設定區的時間不合理：要「最早 ≤ 最晚」，而且上班最晚要早於下班最早。")
    input("按 Enter 結束…")
    sys.exit(1)

WEEK_CHARS = "一二三四五六日"
WORKDAYS = {WEEK_CHARS.index(c) for c in 上班日 if c in WEEK_CHARS}
if not WORKDAYS:
    print("❌ 設定區的「上班日」沒有填任何一天，例如應該寫 \"一二三四五\"。")
    input("按 Enter 結束…")
    sys.exit(1)


# ── 每天隨機決定上下班時間 ─────────────────────────────────────────
def new_daily_schedule():
    s = random.randint(START_MIN_1, START_MIN_2)
    e = random.randint(STOP_MIN_1, STOP_MIN_2)
    return s // 60, s % 60, e // 60, e % 60


TODAY_START_H, TODAY_START_M, TODAY_STOP_H, TODAY_STOP_M = new_daily_schedule()


def at(day, hour, minute):
    return day.replace(hour=hour, minute=minute, second=0, microsecond=0)


def in_work_time(now):
    if now.weekday() not in WORKDAYS:
        return False
    return at(now, TODAY_START_H, TODAY_START_M) <= now < at(now, TODAY_STOP_H, TODAY_STOP_M)


def next_work_start(now):
    """找出下一次上班開始的時間（會自動跳過不上班的日子）"""
    for i in range(8):
        day = now + datetime.timedelta(days=i)
        if day.weekday() in WORKDAYS:
            start = at(day, TODAY_START_H, TODAY_START_M)
            if start > now:
                return start
    return now + datetime.timedelta(minutes=1)


# ── Teams 開關（Mac / Windows 都支援）──────────────────────────────
def open_teams():
    if not 自動開關Teams:
        return
    print("[Teams] 開啟 Microsoft Teams…")
    try:
        if IS_MAC:
            subprocess.Popen(["open", "-a", "Microsoft Teams"])
        elif IS_WINDOWS:
            subprocess.Popen('start "" msteams:', shell=True)
        time.sleep(5)  # 給 Teams 一點啟動時間
    except Exception as e:
        print(f"[Teams] 開啟失敗（不影響滑鼠功能）：{e}")


def close_teams():
    if not 自動開關Teams:
        return
    print("[Teams] 關閉 Microsoft Teams…")
    try:
        if IS_MAC:
            subprocess.run(["osascript", "-e", 'quit app "Microsoft Teams"'],
                           capture_output=True)
        elif IS_WINDOWS:
            for exe in ("ms-teams.exe", "Teams.exe"):
                subprocess.run(["taskkill", "/IM", exe, "/F"], capture_output=True)
    except Exception as e:
        print(f"[Teams] 關閉失敗：{e}")


# ── 移動滑鼠 ─────────────────────────────────────────────────────
def move_mouse():
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    try:
        x, y = pyautogui.position()
        pyautogui.moveTo(x + 1, y, duration=0.1)
        pyautogui.moveTo(x, y, duration=0.1)
        print(f"[{now_str}] 滑鼠移動 ✓")
    except pyautogui.FailSafeException:
        # 滑鼠停在螢幕角落時 pyautogui 會保護性停止，這次就跳過
        print(f"[{now_str}] 滑鼠在螢幕角落，這次先跳過")


# ── 主程式 ───────────────────────────────────────────────────────
def main():
    global TODAY_START_H, TODAY_START_M, TODAY_STOP_H, TODAY_STOP_M

    print("=== 防閒置小工具 已啟動 ===")
    print(f"今日排程：{TODAY_START_H:02d}:{TODAY_START_M:02d} 開始 ／ "
          f"{TODAY_STOP_H:02d}:{TODAY_STOP_M:02d} 結束")
    print("要停止請按 Ctrl+C，或直接關掉這個視窗\n")

    active = False
    last_date = datetime.date.today()
    shown_next_start = None

    while True:
        try:
            # 跨日：重新抽今天的上下班時間
            today = datetime.date.today()
            if today != last_date:
                TODAY_START_H, TODAY_START_M, TODAY_STOP_H, TODAY_STOP_M = new_daily_schedule()
                last_date = today
                shown_next_start = None
                print(f"\n[新的一天] 今日排程：{TODAY_START_H:02d}:{TODAY_START_M:02d} 開始 ／ "
                      f"{TODAY_STOP_H:02d}:{TODAY_STOP_M:02d} 結束")

            now = datetime.datetime.now()
            working = in_work_time(now)

            if working and not active:
                print(f"\n[{now.strftime('%H:%M')}] ▶ 上班時段開始")
                shown_next_start = None
                open_teams()
                active = True
            elif not working and active:
                print(f"\n[{now.strftime('%H:%M')}] ■ 下班時段，暫停")
                close_teams()
                active = False

            if active:
                move_mouse()
                time.sleep(滑鼠間隔秒數)
            else:
                next_start = next_work_start(now)
                if next_start != shown_next_start:
                    print(f"下次上班時段：{next_start.strftime('%m/%d %H:%M')}（在那之前會安靜等待）")
                    shown_next_start = next_start
                # 每 60 秒檢查一次，避免睡過頭
                time.sleep(max(1, min((next_start - now).total_seconds(), 60)))

        except KeyboardInterrupt:
            print("\n\n[停止] 已手動停止。")
            if active:
                close_teams()
            sys.exit(0)


if __name__ == "__main__":
    main()
