# main.py — 入口与主菜单调度

`app.py` 建 QApplication，本文件挂主窗口（`mainui.py` 布局）并接线：

- `menubtn1~4_clicked`：研学笔记（noteui）/ 实时问答（qaui）/ 录课整理（courseui）三个子窗口的显示与主窗隐藏，设置页在堆栈页内切换
- `savebtn_clicked`：保存设置——收件邮箱经 `function.change_email_account` 落 `case.yaml`；WiFi 名/密码只更新 `function.py` 内存变量并立即尝试 pywifi 连接（不落盘，重启需重填）
- `datehandel` / `wifihandel`：`QTimer` 每秒刷新时钟；后台线程每 2 秒检测能否访问百度并刷新联网图标（`wifiUtils.get_webPage`）
- `button` / `button_2` / `button_3`：设置页左侧「邮箱 / WIFI名称 / WIFI密码」按钮，进入 `settinginputuic` 扫码录入

## 坑点

- 子窗口「返回主菜单」负责把主窗再 show 回来；新增页面要同时接线返回路径，否则窗口「消失」

---

## English

Entry point wiring the main menu (layout in `mainui.py`): `menubtn1~4_clicked` show the note/QA/course sub-windows and hide the main one; the settings page swaps inside a stacked widget. `savebtn_clicked` persists the receiving mailbox into `case.yaml` via `function.change_email_account`, while WiFi credentials only update in-memory globals and trigger an immediate pywifi connection attempt (not persisted). Timers refresh the clock and connectivity icon. Pitfall: every new page needs a wired "back to menu" path or the window seems to vanish.
