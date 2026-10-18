# Laptop <-> Server sync (Detective Shivam bot)
# 1) Naye SCRIPT_*.txt + answer_key.xlsx + reel_case_fix.txt server par bhejo  (mode: up)
# 2) leaderboard.xlsx + verified.txt + answer_key.xlsx server se laptop par lao   (mode: down)
param([string]$mode = "both")
$ErrorActionPreference = "Stop"
$ip = "35.222.83.100"
$key = "$env:USERPROFILE\.ssh\shivam_gcp"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$stories = "C:\Users\Hp\Desktop\reels story\category"
$ssh = "ssh -i `"$key`" -o BatchMode=yes -o ConnectTimeout=20 shivam@$ip"

# ssh / scp / tar fail ho to PowerShell khud nahi rukta - isliye har command ke baad check
function Check($code, $what) {
    if ($code -ne 0) {
        Write-Host ""
        Write-Host "!! $what FAIL hua (code $code). Internet / server / key check karo, phir dobara chalao." -ForegroundColor Red
        exit 1
    }
}

if ($mode -eq "up" -or $mode -eq "both") {
    Write-Host "Scripts server par bhej raha hoon..."
    $list = Join-Path $env:TEMP "shivam_scripts_list.txt"
    Push-Location $stories
    $files = Get-ChildItem -Path "Category *\Story *\SCRIPT_*.txt" | ForEach-Object {
        (Resolve-Path -Relative $_.FullName).Substring(2).Replace("\", "/")
    }
    [IO.File]::WriteAllText($list, (($files -join "`n") + "`n"))
    cmd /c "tar -cf - -T `"$list`" | $ssh `"cd ~/bot/scripts && tar -xf - && find . -name 'SCRIPT_*' | wc -l`""
    $code = $LASTEXITCODE
    Pop-Location
    Remove-Item $list -ErrorAction SilentlyContinue
    Check $code "Scripts bhejna"
}
if ($mode -eq "up") {
    Write-Host "answer_key.xlsx + reel_case_fix.txt server par bhej raha hoon..."
    # server wali answer_key ki ek copy (answer_key.prev.xlsx) - galti se purani file chali jaaye to wapas mil sake
    cmd /c "$ssh `"cp -f bot/answer_key.xlsx bot/answer_key.prev.xlsx 2>/dev/null; true`""
    scp -i "$key" -o BatchMode=yes "$here\answer_key.xlsx" "$here\reel_case_fix.txt" "$here\answers_extra.txt" "shivam@${ip}:bot/"
    Check $LASTEXITCODE "answer_key bhejna"
}
if ($mode -eq "down" -or $mode -eq "both") {
    # laptop wali answer_key mein bina bheje badlaav ho sakte hain - overwrite se pehle backup (last 10)
    $ak = Join-Path $here "answer_key.xlsx"
    if (Test-Path $ak) {
        $bk = Join-Path $here "answer_key_backup"
        New-Item -ItemType Directory -Force -Path $bk | Out-Null
        Copy-Item $ak (Join-Path $bk ("answer_key_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".xlsx"))
        Get-ChildItem $bk -Filter "answer_key_*.xlsx" | Sort-Object Name -Descending | Select-Object -Skip 10 | Remove-Item
    }
    Write-Host "Server se leaderboard.xlsx, verified.txt, answer_key.xlsx la raha hoon..."
    scp -i "$key" -o BatchMode=yes "shivam@${ip}:bot/leaderboard.xlsx" "shivam@${ip}:bot/verified.txt" "shivam@${ip}:bot/answer_key.xlsx" "$here"
    Check $LASTEXITCODE "Server se file laana (leaderboard.xlsx Excel mein khuli ho to band karo)"
}
Write-Host "Ho gaya."
