# 口才训练营 - 开放Flask端口防火墙规则
# 右键此文件 -> 使用PowerShell运行（需管理员权限）

try {
    $rule = Get-NetFirewallRule -DisplayName "Flask-Port-5000" -ErrorAction SilentlyContinue
    if ($rule) {
        Write-Host "Firewall rule already exists" -ForegroundColor Green
        Remove-NetFirewallRule -DisplayName "Flask-Port-5000"
        Write-Host "Removed old rule"
    }

    New-NetFirewallRule -DisplayName "Flask-Port-5000" `
        -Direction Inbound `
        -Protocol TCP `
        -LocalPort 5000 `
        -Action Allow `
        -Profile Any

    Write-Host "Firewall port 5000 opened" -ForegroundColor Green
    Write-Host "Now refresh WeChat DevTools" -ForegroundColor Yellow
} catch {
    Write-Host "Need admin privileges. Right-click -> Run as Administrator" -ForegroundColor Red
}

pause
