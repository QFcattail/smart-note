# 锚定仓库根（脚本位于 script/ 子目录，数据与启动路径均相对仓库根）
$currentDir = Split-Path -Parent $PSScriptRoot
Set-Location $currentDir

# 虚拟环境目录
$envPath = Join-Path -Path $currentDir -ChildPath "venv"

# 激活虚拟环境
. "$envPath\Scripts\Activate.ps1"
$env:QT_PLUGIN_PATH = "$envPath\Lib\site-packages\PyQt5\Qt\plugins"
# 运行main.py
python smartnotebook\main.py

# 脚本执行完毕后保持窗口打开，可以根据需要移除或保留这一行
Read-Host -Prompt "ending"