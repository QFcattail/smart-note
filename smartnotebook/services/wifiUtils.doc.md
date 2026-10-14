# wifiUtils.py — 联网检测与 WiFi 连接

供主界面状态图标与设置页使用：

- `get_webPage()`：2 秒超时访问 `https://www.baidu.com`，能打开返回 `True`；`main.py` 的后台线程每 2 秒调用一次，据此切换 `wifi.png` / `wifi-close.png` 图标
- `set_profile(ssid, password)` / `connet_wifi(interface, profile)`：pywifi 组网并尝试连接（设置页「保存」时触发，按 WPA2-PSK 配置）
- `is_connected(interface)`：查询网卡连接状态（当前界面未使用）

## 坑点

- 图标只反映「能否访问百度」，与设置页填的 SSID 无关；代理、防火墙或访问百度慢都会显示未联网
- pywifi 在部分无线网卡/虚拟网卡上枚举失败，`main.py` 已 try/except 兜底为不干扰主流程

---

## English

Connectivity check and Wi-Fi connection: `get_webPage()` tries `https://www.baidu.com` with a 2-second timeout; a background thread in `main.py` calls it every 2 seconds to toggle the status icon. `set_profile`/`connet_wifi` build and apply a WPA2-PSK pywifi profile when settings are saved; `is_connected` is currently unused. Pitfalls: the icon only reflects whether Baidu is reachable — unrelated to the configured SSID, so proxies or firewalls show "offline"; pywifi can fail to enumerate some adapters — `main.py` wraps calls in try/except so it never blocks the app.
