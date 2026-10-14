# 锚定仓库根（脚本位于 script/ 子目录，数据与启动路径均相对仓库根）
$currentDir = Split-Path -Parent $PSScriptRoot
Set-Location $currentDir

# 设置虚拟环境目录为当前目录下的venv文件夹
$envPath = Join-Path -Path $currentDir -ChildPath "venv"

# 创建虚拟环境
python -m venv $envPath

# 激活虚拟环境
. "$envPath\Scripts\Activate.ps1"

# 安装依赖（仅本次使用清华镜像，不改全局 pip 配置；海外网络可去掉 -i 参数）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 完成后保持窗口打开
Read-Host -Prompt "ending"
