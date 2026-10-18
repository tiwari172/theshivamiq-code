# Bot ka naya CODE server par daalo (data / .env / Excel nahi chhuta)
# 1) server par purani files ka backup  ~/bot/backup_<time>/
# 2) nayi checker.py, tg_bot.py, answer_key.py, ig_api.py, textmatch.py bhejo
# 3) shivambot restart + log dikhao.  Gadbad ho to:  server_update.ps1 wapas
param([string]$mode = "update")
$ErrorActionPreference = "Stop"
$ip = "35.222.83.100"
$key = "$env:USERPROFILE\.ssh\shivam_gcp"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$files = "checker.py", "tg_bot.py", "answer_key.py", "ig_api.py", "textmatch.py"

function Check($code, $what) {
    if ($code -ne 0) {
        Write-Host ""
        Write-Host "!! $what FAIL hua (code $code). Internet / server / key check karo, phir dobara chalao." -ForegroundColor Red
        exit 1
    }
}
function Remote($cmd) { ssh -i "$key" -o BatchMode=yes -o ConnectTimeout=20 "shivam@$ip" $cmd }

if ($mode -eq "wapas") {
    Write-Host "Sabse naye backup se purana code wapas la raha hoon..."
    Remote "cd ~/bot && b=`$(ls -d backup_* | tail -1) && cp `$b/*.py . && echo Wapas: `$b && sudo systemctl restart shivambot"
    Check $LASTEXITCODE "Purana code wapas laana"
} else {
    Write-Host "1) Server par purani files ka backup..."
    $list = ($files -join " ")
    Remote "cd ~/bot && b=backup_`$(date +%Y%m%d_%H%M%S) && mkdir -p `$b && cp $list `$b/ && echo Backup: ~/bot/`$b"
    Check $LASTEXITCODE "Backup"

    Write-Host "2) Naya code bhej raha hoon..."
    $paths = $files | ForEach-Object { Join-Path $here $_ }
    scp -i "$key" -o BatchMode=yes $paths "shivam@${ip}:bot/"
    Check $LASTEXITCODE "Code bhejna"

    Write-Host "3) Code check (syntax)..."
    Remote "cd ~/bot && (./venv/bin/python -m py_compile $list || python3 -m py_compile $list) && echo Code theek hai"
    Check $LASTEXITCODE "Code check - kuch gadbad, 'wapas' chalao"

    Write-Host "4) Bot restart..."
    Remote "sudo systemctl restart shivambot"
    Check $LASTEXITCODE "Bot restart"
}
Start-Sleep -Seconds 6
Remote "systemctl is-active shivambot; sudo journalctl -u shivambot -n 12 --no-pager"
Write-Host ""
Write-Host "Upar 'active' aur 'Bot chalu' dikhe to sab theek. Telegram par bot ko /stats bhejo." -ForegroundColor Green
Write-Host "Kuch gadbad ho to: BOT PURANA WAPAS.bat"
