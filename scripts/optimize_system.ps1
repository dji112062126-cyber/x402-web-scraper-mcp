# ============================================
# System Optimization Script - Run as Admin
# ============================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SYSTEM OPTIMIZATION FOR AI WORKLOADS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# ---- 1. Power Plan ----
Write-Host "`n[1/3] Setting Ultimate Performance power plan..." -ForegroundColor Yellow
$guid = "e9a42b02-d5df-448d-aa00-03f14749eb61"

# Try to duplicate the Ultimate Performance scheme
powercfg -duplicatescheme $guid 2>&1 | Out-Null

# Set it as active
powercfg /setactive $guid 2>&1 | Out-Null

# Verify
$active = powercfg /getactivescheme 2>&1
Write-Host "Active power plan: $active" -ForegroundColor Green

# Also set the CPU min/max to 100%
powercfg -setacvalueindex $guid sub_processor PROCTHROTTLEMIN 100 2>&1 | Out-Null
powercfg -setacvalueindex $guid sub_processor PROCTHROTTLEMAX 100 2>&1 | Out-Null
powercfg -setdcvalueindex $guid sub_processor PROCTHROTTLEMIN 100 2>&1 | Out-Null
powercfg -setdcvalueindex $guid sub_processor PROCTHROTTLEMAX 100 2>&1 | Out-Null
powercfg -setactive $guid 2>&1 | Out-Null

Write-Host "CPU min/max state set to 100%" -ForegroundColor Green

# ---- 2. Virtual Memory ----
Write-Host "`n[2/3] Setting virtual memory to 16GB - 32GB..." -ForegroundColor Yellow

# Set via registry
$regPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management"
Set-ItemProperty -Path $regPath -Name "PagingFiles" -Value "C:\pagefile.sys 16384 32768" -Force
Set-ItemProperty -Path $regPath -Name "ExistingPageFiles" -Value "\??\C:\pagefile.sys" -Force

# Verify
$pf = Get-CimInstance Win32_PageFileUsage | Where-Object { $_.Name -eq "C:\pagefile.sys" }
if ($pf) {
    Write-Host "Current pagefile - Allocated: $($pf.AllocatedBaseSize) MB, Peak: $($pf.PeakUsage) MB" -ForegroundColor Green
}

# ---- 3. Disable non-essential startup services ----
Write-Host "`n[3/3] Disabling non-essential services..." -ForegroundColor Yellow

$services = @(
    "Dell.TechHub",           # Dell telemetry
    "Killer Network Service", # Killer network manager
    "AlienFX",                # AlienFX lights
    "Steam Client Service",   # Steam
    "SysMain",                # Superfetch (useless with SSD)
    "DiagTrack",              # Diagnostic tracking
    "WSearch"                 # Windows Search indexing
)

foreach ($svcName in $services) {
    $svc = Get-Service -Name $svcName -ErrorAction SilentlyContinue
    if ($svc) {
        try {
            Stop-Service $svcName -Force -ErrorAction SilentlyContinue
            Set-Service $svcName -StartupType Disabled -ErrorAction SilentlyContinue
            Write-Host "  Disabled: $svcName" -ForegroundColor Gray
        } catch {
            Write-Host "  Could not disable: $svcName" -ForegroundColor DarkYellow
        }
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  OPTIMIZATION COMPLETE!" -ForegroundColor Green
Write-Host "  Virtual memory change needs REBOOT to apply." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

Read-Host "`nPress Enter to exit"
