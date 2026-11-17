# auto-mouse-mover

During the work hours you set, this script nudges the mouse 1 pixel and back once a minute, so your computer and Microsoft Teams don't switch to "Away". It opens Teams when the work period starts and quits it when the period ends.

[中文說明在下方](#中文說明)

## Features

- **Randomized daily schedule.** You give a start range and a stop range (for example, start between 08:30 and 08:40, stop between 16:20 and 16:40). Each day the script picks a random minute inside each range, so it doesn't start at the exact same time every day.
- **Workdays only.** It runs only on the weekdays you list. Outside work hours and on days off it waits quietly and prints when the next work period begins.
- **Teams open/quit.** Teams opens at the start of the work period and quits at the end. You can turn this off.
- **Installs its own dependency.** The first time you run it, it installs [`pyautogui`](https://pypi.org/project/PyAutoGUI/) with pip, so there's nothing to set up beforehand except Python.
- **macOS and Windows.**

## Requirements

- Python 3
  - **macOS:** usually already there. If not, running `python3` in Terminal will offer to install the Command Line Developer Tools, which include it.
  - **Windows:** install it from [python.org](https://www.python.org/downloads/). On the first installer screen, tick **Add python.exe to PATH**.
- Microsoft Teams, only if you keep the Teams open/quit feature on.

## Getting started

### macOS

1. Download [`auto_mouse_mover.py`](auto_mouse_mover.py).
2. Open Terminal (press `Command + Space`, type `Terminal`, press Enter).
3. Type `python3 ` (with a space after it), drag the file into the Terminal window, and press Enter. Or run:

   ```bash
   python3 path/to/auto_mouse_mover.py
   ```

4. The first run installs `pyautogui`. This takes about a minute.
5. Give Terminal permission to control the mouse: **System Settings → Privacy & Security → Accessibility**, then switch on **Terminal**. Without this, the script runs but the mouse never moves.
6. Quit Terminal completely (`Command + Q`), open it again, and repeat step 3. The permission only takes effect after a restart of Terminal.

### Windows

1. Download [`auto_mouse_mover.py`](auto_mouse_mover.py).
2. Press the Start key, type `cmd`, and open **Command Prompt**.
3. Type `python ` (with a space after it), drag the file into the window, and press Enter. Or run:

   ```bash
   python path\to\auto_mouse_mover.py
   ```

4. The first run installs `pyautogui`. This takes about a minute.

### Stopping it

Keep the window open while you want the script to work; minimizing it is fine. To stop, press `Ctrl + C` in the window or just close it. If Teams was opened by the script, it gets quit when you stop with `Ctrl + C`.

## Settings

Open `auto_mouse_mover.py` in any text editor (TextEdit on macOS, Notepad on Windows) and change only the settings block at the top. The variable names are in Chinese; here's what each one means:

| Variable | Default | Meaning |
|---|---|---|
| `上班_最早` | `"08:30"` | Earliest start time |
| `上班_最晚` | `"08:40"` | Latest start time |
| `下班_最早` | `"16:20"` | Earliest stop time |
| `下班_最晚` | `"16:40"` | Latest stop time |
| `上班日` | `"一二三四五"` | Days to run, as Chinese numerals: `一` Mon, `二` Tue, `三` Wed, `四` Thu, `五` Fri, `六` Sat, `日` Sun. For Mon–Sat, write `"一二三四五六"`. |
| `滑鼠間隔秒數` | `60` | Seconds between mouse nudges |
| `自動開關Teams` | `True` | `True` opens and quits Teams automatically; `False` leaves Teams alone |

Times use the 24-hour `"HH:MM"` format. The latest start time must be earlier than the earliest stop time. If a setting is invalid, the script prints what's wrong and exits instead of running with bad values.

Save the file and run it again for changes to take effect.

## How it works

- Once a minute during work hours, the script reads the current mouse position, moves 1 pixel to the right, and moves back. You won't notice it while using the computer.
- Outside work hours it checks the clock every 60 seconds and does nothing else.
- At midnight it picks new random start and stop times for the new day.
- Teams is opened with `open -a "Microsoft Teams"` on macOS and the `msteams:` link on Windows. It's quit with AppleScript on macOS and `taskkill` on Windows.

## Notes

- **Check your employer's IT policy before using this.** Some workplaces don't allow tools like this.
- `pyautogui` blocks mouse movement while the pointer sits in a screen corner (a built-in safety feature). When that happens the script skips that nudge and carries on.
- The Windows Teams open/quit code hasn't been tested on a real Windows machine yet. If it doesn't work for you, please [open an issue](../../issues).

## License

[MIT](LICENSE)

---

## 中文說明

在你設定的上班時段內，每分鐘把滑鼠移動 1 像素再移回來，讓電腦和 Teams 不會變成「離開」。上班時自動開 Teams，下班自動關。每天的上下班時間會在你設定的範圍內隨機挑選。

**使用方式**

- **Mac**：打開「終端機」，輸入 `python3 `（後面空一格），把檔案拖進去按 Enter。第一次使用要到「系統設定 → 隱私權與安全性 → 輔助使用」打開「終端機」，再重開終端機執行一次。
- **Windows**：先到 [python.org](https://www.python.org/downloads/) 安裝 Python（勾選 **Add python.exe to PATH**），打開「命令提示字元」，輸入 `python `，把檔案拖進去按 Enter。

**修改設定**：用文字編輯器打開檔案，只改最上面「設定區」裡的值。檔案內有中文註解說明每一項。

**停止**：按 `Ctrl + C` 或直接關掉視窗。

使用前請先確認公司規定。
