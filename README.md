# auto-mouse-mover

在你設定的上班時段內，每分鐘把滑鼠移動 1 像素再移回原位，讓電腦和 Microsoft Teams 不會因為閒置而變成「離開」。上班時自動開啟 Teams，下班時自動關閉。

[English below](#english)

## 功能

- 每天在你給的範圍內隨機挑上下班時間（例如 08:30–08:40 之間開始），不會每天都在同一分鐘啟動
- 只在你指定的星期幾運作，週末或下班後會安靜等待
- 上班自動開 Teams、下班自動關（可以關掉這個功能）
- 第一次執行會自動安裝需要的套件 `pyautogui`
- 支援 macOS 和 Windows

## 使用方式

### Mac

1. 下載 [`auto_mouse_mover.py`](auto_mouse_mover.py)
2. 打開「終端機」：按 `Command + 空白鍵`，輸入 `Terminal`，按 Enter
3. 輸入 `python3 `（後面空一格），把檔案拖進終端機視窗，按 Enter
   - 如果跳出要安裝「指令列開發者工具」，按「安裝」，裝好後再做一次這步
4. 第一次執行時，到 **系統設定 → 隱私權與安全性 → 輔助使用**，把「終端機」打開。沒開的話滑鼠不會動。開完後把終端機完全關掉（`Command + Q`）再執行一次

### Windows

1. 到 [python.org](https://www.python.org/downloads/) 安裝 Python，安裝畫面最下方的 **Add python.exe to PATH** 要打勾
2. 按開始鍵，輸入 `cmd`，打開「命令提示字元」
3. 輸入 `python `（後面空一格），把檔案拖進視窗，按 Enter

程式執行時視窗要保持開著（可以縮小）。要停止就按 `Ctrl + C` 或直接關掉視窗。

## 設定

用任何文字編輯器打開 `auto_mouse_mover.py`，只改最上面「設定區」：

| 設定 | 預設值 | 說明 |
|---|---|---|
| `上班_最早` / `上班_最晚` | `"08:30"` / `"08:40"` | 每天在這段時間內隨機挑一個時間開始 |
| `下班_最早` / `下班_最晚` | `"16:20"` / `"16:40"` | 每天在這段時間內隨機挑一個時間結束 |
| `上班日` | `"一二三四五"` | 要運作的星期幾，週六也要就寫 `"一二三四五六"` |
| `滑鼠間隔秒數` | `60` | 多久動一次滑鼠 |
| `自動開關Teams` | `True` | 不想自動開關 Teams 就改成 `False` |

## 注意事項

- 使用前請先確認公司的規定。有些公司的 IT 政策不允許這類工具。
- 滑鼠停在螢幕角落時，`pyautogui` 的安全機制會擋下移動，程式會跳過那一次，繼續執行。
- Windows 版的 Teams 開關功能還沒有在實機上測過，如果不正常請開 Issue 回報。

---

<a id="english"></a>

## English

During the work hours you set, this script nudges the mouse 1 pixel and back once a minute, so your computer and Microsoft Teams don't switch to "Away". It opens Teams when the work period starts and quits it when the period ends.

Start and stop times are picked at random each day from a range you choose (for example, start somewhere between 08:30 and 08:40). Works on macOS and Windows. On first run it installs its one dependency, `pyautogui`, with pip.

### Run it

```bash
python3 auto_mouse_mover.py
```

(On Windows, use `python` instead of `python3`.)

On macOS, give your terminal app Accessibility permission (System Settings → Privacy & Security → Accessibility), then quit and reopen the terminal. Without it the mouse won't move.

Press `Ctrl + C` to stop.

### Settings

Edit the block at the top of the file. The variable names are in Chinese:

- `上班_最早` / `上班_最晚`: earliest / latest start time
- `下班_最早` / `下班_最晚`: earliest / latest stop time
- `上班日`: active weekdays, written as Chinese numerals (`一` = Mon … `五` = Fri, `六` = Sat, `日` = Sun)
- `滑鼠間隔秒數`: seconds between mouse nudges
- `自動開關Teams`: `True` to open/quit Teams automatically, `False` to leave it alone

Check your employer's IT policy before using this. The Windows Teams open/quit code hasn't been tested on a real machine yet; please open an issue if it misbehaves.

## License

[MIT](LICENSE)
