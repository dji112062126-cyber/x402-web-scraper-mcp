# Write virtual memory setting to registry
$regPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management"
$value = "C:\pagefile.sys 16384 32768"

Write-Host "Writing PagingFiles to registry..." -ForegroundColor Yellow
try {
    Set-ItemProperty -Path $regPath -Name "PagingFiles" -Value $value -Type MultiString -Force
    Write-Host "SUCCESS: PagingFiles set to: $value" -ForegroundColor Green
} catch {
    Write-Host "FAILED: $_" -ForegroundColor Red
}

# Read back
$readback = Get-ItemProperty -Path $regPath -Name "PagingFiles"
Write-Host "Readback: $($readback.PagingFiles)" -ForegroundColor Cyan

Write-Host "`nYou MUST reboot for changes to take effect." -ForegroundColor Red
Read-Host "Press Enter"
