# auto-mouse-mover

![Python 3.7+](https://img.shields.io/badge/python-3.7%2B-3776AB?logo=python&logoColor=white)
![Platform: macOS | Windows](https://img.shields.io/badge/platform-macOS%20%7C%20Windows-lightgrey)
[![License: MIT](https://img.shields.io/github/license/Diana-Lee0912/auto-mouse-mover)](LICENSE)
[![Last commit](https://img.shields.io/github/last-commit/Diana-Lee0912/auto-mouse-mover)](https://github.com/Diana-Lee0912/auto-mouse-mover/commits/main)

During the work hours you set, this script nudges the mouse 1 pixel and back once a minute, so your computer and Microsoft Teams don't switch to "Away". It opens Teams when the work period starts and quits it when the period ends.

<p align="center">
  <img src="docs/screenshot.svg" alt="Terminal output: setup asks for work hours and saves them, then the script waits until the work period, opens Teams, moves the mouse every minute, and quits Teams when stopped with Ctrl+C" width="640">
</p>

[中文說明在下方](#中文說明)

## Features

- **One-line install.** Paste one command; it asks for your work hours and starts running.
- **Randomized daily schedule.** You give a start range and a stop range (for example, start between 08:30 and 08:40, stop between 16:20 and 16:40). Each day the script picks a random minute inside each range, so it doesn't start at the exact same time every day.
- **Workdays only.** It runs only on the weekdays you choose. Outside work hours and on days off it waits quietly and prints when the next work period begins.
- **Teams open/quit.** Teams opens at the start of the work period and quits at the end. You can turn this off.
- **Installs its own dependency.** The first time you run it, it installs [`pyautogui`](https://pypi.org/project/PyAutoGUI/) with pip, so there's nothing to set up beforehand except Python.
- **macOS and Windows.**

## Requirements

- Python 3
  - **macOS:** usually already there. If not, running `python3` in Terminal will offer to install the Command Line Developer Tools, which include it.
  - **Windows:** install it from [python.org](https://www.python.org/downloads/). On the first installer screen, tick **Add python.exe to PATH**.
- Microsoft Teams, only if you keep the Teams open/quit feature on.

## Quick install (recommended)

### macOS

Open Terminal (press `Command + Space`, type `Terminal`, press Enter), paste this line, and press Enter:

```bash
curl -fsSL https://raw.githubusercontent.com/Diana-Lee0912/auto-mouse-mover/main/install.sh | bash
```

### Windows

Open PowerShell (press the Start key, type `PowerShell`, press Enter), paste this line, and press Enter:

```powershell
irm https://raw.githubusercontent.com/Diana-Lee0912/auto-mouse-mover/main/install.ps1 | iex
```

### What the installer does

1. Downloads `auto_mouse_mover.py` into an `auto-mouse-mover` folder in your home folder.
2. Adds two files to that folder that you can double-click later:
   - **Start auto-mouse-mover**: starts the program
   - **Change settings**: asks for your work hours again
3. Asks you a few questions (start time range, stop time range, workdays, whether to open/quit Teams). Press Enter to accept the value shown in brackets.
4. Saves your answers and starts the program. The first run also installs `pyautogui`, which takes about a minute.

Running the installer again updates the program and keeps your saved settings.

**macOS, first time only:** give Terminal permission to control the mouse in **System Settings → Privacy & Security → Accessibility** (switch on **Terminal**). Without this, the script runs but the mouse never moves. After switching it on, quit Terminal (`Command + Q`) and double-click **Start auto-mouse-mover**.

You can read [`install.sh`](install.sh) and [`install.ps1`](install.ps1) before running them. It's a good habit with any install command you paste from the internet.

## Manual install

If you'd rather not use the installer, download the script and run it yourself.

### macOS

1. Download [`auto_mouse_mover.py`](auto_mouse_mover.py).
2. Open Terminal (press `Command + Space`, type `Terminal`, press Enter).
3. Type `python3 ` (with a space after it), drag the file into the Terminal window, and press Enter. Or run:

   ```bash
   python3 path/to/auto_mouse_mover.py
   ```

4. The first run installs `pyautogui`. This takes about a minute.
5. Give Terminal permission to control the mouse: **System Settings → Privacy & Security → Accessibility**, then switch on **Terminal**.
6. Quit Terminal completely (`Command + Q`), open it again, and repeat step 3. The permission only takes effect after a restart of Terminal.

### Windows

1. Download [`auto_mouse_mover.py`](auto_mouse_mover.py).
2. Press the Start key, type `cmd`, and open **Command Prompt**.
3. Type `python ` (with a space after it), drag the file into the window, and press Enter. Or run:

   ```bash
   python path\to\auto_mouse_mover.py
   ```

4. The first run installs `pyautogui`. This takes about a minute.

## Stopping it

Keep the window open while you want the script to work; minimizing it is fine. To stop, press `Ctrl + C` in the window or just close it. If Teams was opened by the script, it gets quit when you stop with `Ctrl + C`.

## Settings

### Change settings by answering questions

- **Quick install:** double-click **Change settings** in the `auto-mouse-mover` folder.
- **Manual install:** run the script with `--setup`:

  ```bash
  python3 auto_mouse_mover.py --setup
  ```

  (On Windows, use `python` instead of `python3`.)

Each question shows your current value in brackets; press Enter to keep it. If an answer doesn't make sense (for example, a time like `25:00`, or a start time after the stop time), it tells you what's wrong and asks again. Your answers are saved in `config.json` next to the script, and the program starts right after.

### Change settings by editing the file

You can also open `auto_mouse_mover.py` in any text editor (TextEdit on macOS, Notepad on Windows) and change the `SETTINGS` block at the top. If a `config.json` file exists next to the script, it takes priority over this block, so delete `config.json` first.

| Variable | Default | Meaning |
|---|---|---|
| `START_EARLIEST` | `"08:30"` | Earliest start time |
| `START_LATEST` | `"08:40"` | Latest start time |
| `STOP_EARLIEST` | `"16:20"` | Earliest stop time |
| `STOP_LATEST` | `"16:40"` | Latest stop time |
| `WORKDAYS` | `"Mon,Tue,Wed,Thu,Fri"` | Days to run, separated by commas. For Mon–Sat, write `"Mon,Tue,Wed,Thu,Fri,Sat"`. |
| `MOUSE_INTERVAL_SECONDS` | `60` | Seconds between mouse nudges (only changeable here, not in setup) |
| `AUTO_OPEN_CLOSE_TEAMS` | `True` | `True` opens and quits Teams automatically; `False` leaves Teams alone |

Times use the 24-hour `"HH:MM"` format. The latest start time must be earlier than the earliest stop time. If a setting is invalid, the script prints what's wrong and exits instead of running with bad values.

## How it works

- Once a minute during work hours, the script reads the current mouse position, moves 1 pixel to the right, and moves back. You won't notice it while using the computer.
- Outside work hours it checks the clock every 60 seconds and does nothing else.
- At midnight it picks new random start and stop times for the new day.
- Teams is opened with `open -a "Microsoft Teams"` on macOS and the `msteams:` link on Windows. It's quit with AppleScript on macOS and `taskkill` on Windows.

## Notes

- **Check your employer's IT policy before using this.** Some workplaces don't allow tools like this.
- `pyautogui` blocks mouse movement while the pointer sits in a screen corner (a built-in safety feature). When that happens the script skips that nudge and carries on.
- The Windows installer and the Windows Teams open/quit code haven't been tested on a real Windows machine yet. If something doesn't work for you, please [open an issue](../../issues).

## License

[MIT](LICENSE)

---

## 中文說明

在你設定的上班時段內，這個程式每分鐘把滑鼠往右移 1 像素再移回原位，讓電腦和 Microsoft Teams 不會因為閒置而變成「離開」。上班時段開始時會自動開啟 Teams，結束時自動關閉。

### 功能

- **一行指令安裝**：貼上一行指令，程式會問你上下班時間，回答完就開始運作。
- **每天隨機的上下班時間**：你設定一個開始範圍和一個結束範圍（例如 08:30–08:40 之間開始、16:20–16:40 之間結束），程式每天會在範圍內各隨機挑一分鐘，不會每天都在同一時間啟動。
- **只在上班日運作**：只在你選的星期幾執行。下班後和休假日會安靜等待，並顯示下一次上班時段什麼時候開始。
- **自動開關 Teams**：上班時段開始時開啟 Teams，結束時關閉。這個功能可以關掉。
- **自動安裝套件**：第一次執行時會用 pip 自動安裝 [`pyautogui`](https://pypi.org/project/PyAutoGUI/)，除了 Python 之外不需要事先準備任何東西。
- **支援 macOS 和 Windows**。

### 需要的環境

- Python 3（3.7 以上）
  - **macOS**：通常已經內建。如果沒有，在終端機輸入 `python3` 時會跳出視窗，詢問是否安裝「指令列開發者工具」，裡面就包含 Python。
  - **Windows**：到 [python.org](https://www.python.org/downloads/) 下載安裝。安裝程式第一個畫面最下方的 **Add python.exe to PATH** 一定要打勾。
- Microsoft Teams（只有在開啟自動開關 Teams 功能時才需要）

### 快速安裝（推薦）

#### macOS

打開「終端機」（按 `Command + 空白鍵`，輸入 `Terminal`，按 Enter），貼上這行，按 Enter：

```bash
curl -fsSL https://raw.githubusercontent.com/Diana-Lee0912/auto-mouse-mover/main/install.sh | bash
```

#### Windows

打開 PowerShell（按開始鍵，輸入 `PowerShell`，按 Enter），貼上這行，按 Enter：

```powershell
irm https://raw.githubusercontent.com/Diana-Lee0912/auto-mouse-mover/main/install.ps1 | iex
```

#### 安裝程式會做什麼

1. 把 `auto_mouse_mover.py` 下載到你個人資料夾裡的 `auto-mouse-mover` 資料夾。
2. 在那個資料夾裡放兩個之後可以直接雙擊的檔案：
   - **Start auto-mouse-mover**：啟動程式
   - **Change settings**：重新設定上下班時間
3. 問你幾個問題（開始時間範圍、結束時間範圍、上班日、要不要自動開關 Teams）。直接按 Enter 就會使用中括號裡的值。
4. 把你的答案存起來並啟動程式。第一次執行還會自動安裝 `pyautogui`，大約需要 1 分鐘。

之後再執行一次安裝指令，會更新程式並保留你存好的設定。

**macOS 第一次使用：** 到 **系統設定 → 隱私權與安全性 → 輔助使用**，把 **終端機** 打開，讓它可以控制滑鼠。沒有開這個權限的話，程式會照常執行，但滑鼠完全不會動。打開後把終端機完全關掉（`Command + Q`），再雙擊 **Start auto-mouse-mover**。

執行前可以先看看 [`install.sh`](install.sh) 和 [`install.ps1`](install.ps1) 的內容。從網路上貼安裝指令之前先看一下內容，是個好習慣。

### 手動安裝

不想用安裝程式的話，也可以自己下載程式來執行。

#### macOS

1. 下載 [`auto_mouse_mover.py`](auto_mouse_mover.py)。
2. 打開「終端機」：按 `Command + 空白鍵`，輸入 `Terminal`，按 Enter。
3. 輸入 `python3 `（後面要空一格），把檔案拖進終端機視窗，按 Enter。也可以直接輸入：

   ```bash
   python3 檔案路徑/auto_mouse_mover.py
   ```

4. 第一次執行會自動安裝 `pyautogui`，大約需要 1 分鐘。
5. 讓終端機可以控制滑鼠：打開 **系統設定 → 隱私權與安全性 → 輔助使用**，把 **終端機** 打開。
6. 把終端機完全關掉（`Command + Q`），重新打開，再做一次步驟 3。權限要在終端機重開之後才會生效。

#### Windows

1. 下載 [`auto_mouse_mover.py`](auto_mouse_mover.py)。
2. 按開始鍵，輸入 `cmd`，打開 **命令提示字元**。
3. 輸入 `python `（後面要空一格），把檔案拖進視窗，按 Enter。也可以直接輸入：

   ```bash
   python 檔案路徑\auto_mouse_mover.py
   ```

4. 第一次執行會自動安裝 `pyautogui`，大約需要 1 分鐘。

### 停止程式

想讓程式運作時，視窗要保持開著（縮小沒關係）。要停止的話，在視窗裡按 `Ctrl + C`，或直接把視窗關掉。如果 Teams 是由程式開啟的，用 `Ctrl + C` 停止時會一併把 Teams 關掉。

### 設定

#### 用問答的方式修改設定

- **快速安裝的人**：雙擊 `auto-mouse-mover` 資料夾裡的 **Change settings**。
- **手動安裝的人**：執行程式時加上 `--setup`：

  ```bash
  python3 auto_mouse_mover.py --setup
  ```

  （Windows 請把 `python3` 換成 `python`。）

每個問題的中括號裡會顯示目前的設定，直接按 Enter 就是保留不變。如果答案不合理（例如時間打成 `25:00`，或開始時間比結束時間晚），程式會告訴你哪裡有問題並請你重新輸入。答案會存在程式旁邊的 `config.json`，存好後程式就會開始運作。

#### 直接修改檔案

也可以用任何文字編輯器（macOS 用「文字編輯」，Windows 用「記事本」）打開 `auto_mouse_mover.py`，修改最上面的 `SETTINGS` 區塊。注意：如果程式旁邊有 `config.json`，會以 `config.json` 為準，所以要先把它刪掉。

| 變數 | 預設值 | 說明 |
|---|---|---|
| `START_EARLIEST` | `"08:30"` | 最早開始時間 |
| `START_LATEST` | `"08:40"` | 最晚開始時間 |
| `STOP_EARLIEST` | `"16:20"` | 最早結束時間 |
| `STOP_LATEST` | `"16:40"` | 最晚結束時間 |
| `WORKDAYS` | `"Mon,Tue,Wed,Thu,Fri"` | 要運作的星期幾，用逗號分隔。`Mon` 週一、`Tue` 週二、`Wed` 週三、`Thu` 週四、`Fri` 週五、`Sat` 週六、`Sun` 週日。週一到週六就寫 `"Mon,Tue,Wed,Thu,Fri,Sat"`。 |
| `MOUSE_INTERVAL_SECONDS` | `60` | 每隔幾秒移動一次滑鼠（只能在這裡改，問答設定不會問） |
| `AUTO_OPEN_CLOSE_TEAMS` | `True` | `True` 會自動開關 Teams；`False` 則完全不動 Teams |

時間使用 24 小時制的 `"時:分"` 格式。最晚開始時間必須早於最早結束時間。如果設定填錯，程式會顯示哪裡有問題並直接結束，不會用錯誤的設定繼續跑。

### 運作方式

- 上班時段內，程式每分鐘讀取一次目前的滑鼠位置，往右移 1 像素再移回來。你正在用電腦時幾乎感覺不到。
- 上班時段以外，程式每 60 秒看一次時間，其他什麼都不做。
- 每天午夜過後，會重新隨機挑選當天的開始和結束時間。
- 開啟 Teams：macOS 用 `open -a "Microsoft Teams"`，Windows 用 `msteams:` 連結。關閉 Teams：macOS 用 AppleScript，Windows 用 `taskkill`。

### 注意事項

- **使用前請先確認公司的 IT 規定。** 有些公司不允許使用這類工具。
- 滑鼠停在螢幕四個角落時，`pyautogui` 的安全機制會擋住滑鼠移動。遇到這種情況，程式會跳過那一次，繼續執行。
- Windows 的安裝程式和開關 Teams 功能還沒有在實際的 Windows 電腦上測試過。如果無法正常運作，歡迎[開 Issue 回報](../../issues)。

### 授權

[MIT](LICENSE)
