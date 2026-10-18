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

if ($mode -eq "up" -or $mode -eq "both") {
    Write-Host "Scripts server par bhej raha hoon..."
    $list = Join-Path $env:TEMP "shivam_scripts_list.txt"
    Push-Location $stories
    $files = Get-ChildItem -Path "Category *\Story *\SCRIPT_*.txt" | ForEach-Object {
        (Resolve-Path -Relative $_.FullName).Substring(2).Replace("\", "/")
    }
    [IO.File]::WriteAllText($list, (($files -join "`n") + "`n"))
    cmd /c "tar -cf - -T `"$list`" | $ssh `"cd ~/bot/scripts && tar -xf - && find . -name 'SCRIPT_*' | wc -l`""
    Pop-Location
    Remove-Item $list -ErrorAction SilentlyContinue
}
if ($mode -eq "up") {
    Write-Host "answer_key.xlsx + reel_case_fix.txt server par bhej raha hoon..."
    scp -i "$key" -o BatchMode=yes "$here\answer_key.xlsx" "$here\reel_case_fix.txt" "shivam@${ip}:bot/"
}
if ($mode -eq "down" -or $mode -eq "both") {
    Write-Host "Server se leaderboard.xlsx, verified.txt, answer_key.xlsx la raha hoon..."
    scp -i "$key" -o BatchMode=yes "shivam@${ip}:bot/leaderboard.xlsx" "shivam@${ip}:bot/verified.txt" "shivam@${ip}:bot/answer_key.xlsx" "$here"
}
Write-Host "Ho gaya."
