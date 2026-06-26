# Set virtual memory to 16GB-32GB
Write-Host "Setting virtual memory to 16384 MB - 32768 MB on C:" -ForegroundColor Green

$path = "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management"
Set-ItemProperty -Path $path -Name "PagingFiles" -Value "C:\pagefile.sys 16384 32768" -Force

# Verify
$pf = Get-CimInstance Win32_PageFileUsage | Where-Object { $_.Name -like "*C:*" }
Write-Host "Current: AllocatedBaseSize = $($pf.AllocatedBaseSize) MB" -ForegroundColor Yellow
Write-Host "`nReboot required for changes to take effect." -ForegroundColor Red
Read-Host "Press Enter to close"
