# 注册 Windows 每日定时任务 — 每天早上 8:00 执行
# 以管理员身份运行此脚本

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$serverDir = Split-Path -Parent $scriptDir
$batPath = Join-Path $scriptDir "run.bat"

$action = New-ScheduledTaskAction -Execute "cmd.exe" `
    -Argument "/c `"$batPath`"" `
    -WorkingDirectory $serverDir

$trigger = New-ScheduledTaskTrigger -Daily -At "08:00AM"

$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew

$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" `
    -LogonType ServiceAccount `
    -RunLevel Highest

try {
    Register-ScheduledTask -TaskName "EloquenceDailyMaterial" `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Description "口才训练营 — 每日自动获取和加工训练素材" `
        -Force
    Write-Host "✅ 定时任务已注册：每天早上 8:00 自动执行"
    Write-Host "   任务名称：EloquenceDailyMaterial"
    Write-Host "   查看：taskschd.msc → 任务计划程序库"
} catch {
    Write-Host "❌ 注册失败：$($_.Exception.Message)"
    Write-Host "   请以管理员身份运行 PowerShell 后重试"
}
