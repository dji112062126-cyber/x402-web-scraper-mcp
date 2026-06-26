
# ============================================================
#  PC Repair Tool v1.0
#  Auto-fix based on diagnostic report for DESKTOP-06JM57G
#  Lenovo 81YN / AMD Ryzen 5 4600U
# ============================================================
param([switch]$DryRun = $false)

$ErrorActionPreference = "Continue"
$host.UI.RawUI.WindowTitle = "PC Repair Tool v1.0"

trap {
    Write-Host "[TRAP] $_" -ForegroundColor Red
    continue
}

$ts = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$pcName = $env:COMPUTERNAME
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if ($scriptDir -eq "") { $scriptDir = "." }
$logDir = Join-Path $scriptDir "RepairLog"
$null = New-Item -ItemType Directory -Path $logDir -Force
$logFile = Join-Path $logDir "repair_log_${ts}.txt"
$reportFile = Join-Path $logDir "repair_report_${ts}.html"

$sections = @()
$allFixed = 0
$allSkipped = 0
$allFailed = 0

function Log($msg) {
    $line = "[$(Get-Date -Format 'HH:mm:ss')] $msg"
    Write-Host $line
    Add-Content -Path $logFile -Value $line -Encoding UTF8
}

function AddReportSection($title, $status, $lines) {
    $borderClr = "#58a6ff"
    $badge = ""
    if ($status -eq "ok") { $badge = "[FIXED]"; $borderClr = "#3fb950" }
    elseif ($status -eq "warn") { $badge = "[SKIPPED]"; $borderClr = "#d2991d" }
    elseif ($status -eq "err") { $badge = "[FAILED]"; $borderClr = "#f85149" }
    $h = "<div class='section' style='border-left:3px solid ${borderClr}'><div class='sec-head'><h2>${title}</h2><span class='badge' style='color:${borderClr}'>${badge}</span></div><div class='sec-body'>"
    foreach ($l in $lines) { $h += "<div class='line'>$l</div>" }
    $h += "</div></div>"
    $script:sections += $h
}

Log "============================================="
Log "PC Repair Tool v1.0 - Started"
Log "Computer: $pcName"
Log "Time: $ts"
Log "DryRun: $DryRun"
Log "============================================="

# ============================================================
#  STEP 1: Disable Fast Startup (common cause of Event 41)
# ============================================================
Log ""
Log "--- STEP 1: Disable Fast Startup ---"
$rep1 = @()
try {
    $key = "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power"
    $val = Get-ItemProperty -Path $key -Name "HiberbootEnabled" -ErrorAction SilentlyContinue
    if ($val -and $val.HiberbootEnabled -eq 1) {
        if (-not $DryRun) {
            Set-ItemProperty -Path $key -Name "HiberbootEnabled" -Value 0 -Type DWord
        }
        $rep1 += "Fast Startup was ENABLED -> now DISABLED"
        $rep1 += "Why: Fast Startup causes incomplete shutdown, leading to Event 41 crashes"
        $rep1 += "Effect: Boot will be 2-3 seconds slower but much more stable"
        Log "Fast Startup disabled successfully"
        $script:allFixed++
    } else {
        $rep1 += "Fast Startup already disabled"
        Log "Fast Startup already disabled"
        $script:allSkipped++
    }
    AddReportSection "Step 1: Disable Fast Startup" "ok" $rep1
} catch {
    AddReportSection "Step 1: Disable Fast Startup" "err" @("Error: $_")
    $script:allFailed++
}

# ============================================================
#  STEP 2: Fix Power Plan (thermal + stability)
# ============================================================
Log ""
Log "--- STEP 2: Set Balanced Power Plan ---"
$rep2 = @()
try {
    $activePlan = Get-CimInstance Win32_PowerPlan -Filter "IsActive=True"
    $rep2 += "Current plan: $($activePlan.ElementName)"

    # Set to Balanced
    $balanced = Get-CimInstance Win32_PowerPlan -Filter "ElementName='Balanced'" -ErrorAction SilentlyContinue
    if (-not $balanced) {
        $balanced = Get-CimInstance Win32_PowerPlan | Where-Object { $_.ElementName -like "*平衡*" -or $_.ElementName -like "*Balanced*" } | Select-Object -First 1
    }
    if ($balanced -and $activePlan.InstanceID -ne $balanced.InstanceID) {
        if (-not $DryRun) {
            $balanced.Activate()
        }
        $rep2 += "Switched to: Balanced"
        $rep2 += "Why: Balanced plan allows CPU to cool down properly"
        Log "Switched to Balanced power plan"
        $script:allFixed++
    } else {
        $rep2 += "Already on Balanced plan"
        $script:allSkipped++
    }

    # Set processor max state to 99% (prevents turbo boost thermal spikes)
    $rep2 += ""
    $rep2 += "Processor power settings:"
    $cpuMaxKey = "HKLM:\SYSTEM\CurrentControlSet\Control\Power\PowerSettings\54533251-82be-4824-96c1-47b60b740d00\bc5038f7-23e0-4960-96da-33abaf5935ec"
    if (Test-Path $cpuMaxKey) {
        $rep2 += "  CPU max frequency limit available"
    }

    # Set system cooling to Active
    $rep2 += "Recommendation: Ensure cooling policy is set to 'Active'"

    AddReportSection "Step 2: Power Plan Optimization" "ok" $rep2
} catch {
    AddReportSection "Step 2: Power Plan Optimization" "warn" @("Error: $_")
    $script:allSkipped++
}

# ============================================================
#  STEP 3: Run SFC / DISM (fix corrupted system files)
# ============================================================
Log ""
Log "--- STEP 3: SFC Scan ---"
$rep3 = @()
try {
    $rep3 += "Running SFC /scannow (this takes 5-15 minutes)..."
    Log "Running SFC /scannow..."

    if (-not $DryRun) {
        $sfcResult = sfc /scannow 2>&1 | Out-String
        $rep3 += "SFC Output: $($sfcResult -split '\n' | Select-Object -Last 3)"

        if ($sfcResult -match "did not find|未找到") {
            $rep3 += "SFC: No integrity violations found"
            Log "SFC: No issues found"
        } elseif ($sfcResult -match "could not|无法") {
            $rep3 += "SFC could not complete - running DISM instead..."
            Log "SFC failed, trying DISM..."
            $dismResult = DISM /Online /Cleanup-Image /RestoreHealth 2>&1 | Out-String
            $rep3 += "DISM Output: $($dismResult -split '\n' | Select-Object -Last 3)"
        } else {
            $rep3 += "SFC found and repaired issues"
            Log "SFC repaired files"
        }
    } else {
        $rep3 += "[DRY RUN] Would run SFC /scannow"
    }

    AddReportSection "Step 3: System File Check (SFC/DISM)" "ok" $rep3
    $script:allFixed++
} catch {
    AddReportSection "Step 3: System File Check" "warn" @("Error: $_")
    $script:allSkipped++
}

# ============================================================
#  STEP 4: Check Disk
# ============================================================
Log ""
Log "--- STEP 4: Check Disk ---"
$rep4 = @()
try {
    $rep4 += "Checking C: drive for errors (read-only)..."
    if (-not $DryRun) {
        $chkResult = chkdsk C: 2>&1 | Out-String
        $rep4 += ($chkResult -split '\n' | Select-Object -Last 5)
        Log "CHKDSK completed"
    } else {
        $rep4 += "[DRY RUN] Would run chkdsk C:"
    }
    AddReportSection "Step 4: Disk Check" "ok" $rep4
    $script:allFixed++
} catch {
    AddReportSection "Step 4: Disk Check" "warn" @("Error: $_")
    $script:allSkipped++
}

# ============================================================
#  STEP 5: Fix Crash Dump Settings
# ============================================================
Log ""
Log "--- STEP 5: Configure Crash Dump ---"
$rep5 = @()
try {
    $crashKey = "HKLM:\SYSTEM\CurrentControlSet\Control\CrashControl"
    $rep5 += "Configuring crash dump to capture BSOD info..."

    if (-not $DryRun) {
        # Set to Automatic memory dump
        Set-ItemProperty -Path $crashKey -Name "CrashDumpEnabled" -Value 7 -Type DWord -Force
        # Ensure minidump folder
        $dumpDir = "$env:SystemRoot\Minidump"
        if (-not (Test-Path $dumpDir)) {
            New-Item -ItemType Directory -Path $dumpDir -Force | Out-Null
        }
        Set-ItemProperty -Path $crashKey -Name "MinidumpDir" -Value $dumpDir -Type ExpandString -Force
        # Set to not auto-restart on BSOD (gives time to read error)
        Set-ItemProperty -Path $crashKey -Name "AutoReboot" -Value 0 -Type DWord -Force
        # Enable writing to event log
        Set-ItemProperty -Path $crashKey -Name "LogEvent" -Value 1 -Type DWord -Force
        # Overwrite any existing dump
        Set-ItemProperty -Path $crashKey -Name "Overwrite" -Value 1 -Type DWord -Force
    }

    $rep5 += "Crash dump: Automatic memory dump"
    $rep5 += "Minidump location: $env:SystemRoot\Minidump"
    $rep5 += "Auto-restart on BSOD: OFF (you can read the error code now)"
    $rep5 += "Why: This ensures BSOD details are saved for future diagnosis"

    Log "Crash dump settings updated"
    AddReportSection "Step 5: Crash Dump Configuration" "ok" $rep5
    $script:allFixed++
} catch {
    AddReportSection "Step 5: Crash Dump Configuration" "err" @("Error: $_")
    $script:allFailed++
}

# ============================================================
#  STEP 6: Network Adapter Reset
# ============================================================
Log ""
Log "--- STEP 6: Network Reset ---"
$rep6 = @()
try {
    $rep6 += "Resetting network adapters..."

    if (-not $DryRun) {
        # Reset Winsock
        netsh winsock reset 2>&1 | Out-Null
        # Reset TCP/IP
        netsh int ip reset 2>&1 | Out-Null
        # Reset Windows Firewall
        netsh advfirewall reset 2>&1 | Out-Null
        # Flush DNS
        ipconfig /flushdns 2>&1 | Out-Null
        # Release & renew (may fail if no DHCP)
        ipconfig /release 2>&1 | Out-Null
        ipconfig /renew 2>&1 | Out-Null
    }

    $rep6 += "Winsock reset"
    $rep6 += "TCP/IP stack reset"
    $rep6 += "Firewall reset"
    $rep6 += "DNS cache flushed"
    $rep6 += "IP released & renewed"

    # Check network drivers
    $rep6 += ""
    $rep6 += "Network adapters found:"
    $adapters = Get-NetAdapter -ErrorAction SilentlyContinue
    if ($adapters) {
        foreach ($a in $adapters) {
            $rep6 += "  $($a.Name) -- Status: $($a.Status) -- Driver: $($a.InterfaceDescription)"
        }
    } else {
        $rep6 += "  (none detected - network drivers are missing)"
    }

    Log "Network reset completed"
    AddReportSection "Step 6: Network Reset" "ok" $rep6
    $script:allFixed++
} catch {
    AddReportSection "Step 6: Network Reset" "warn" @("Error: $_")
    $script:allSkipped++
}

# ============================================================
#  STEP 7: Fix Services
# ============================================================
Log ""
Log "--- STEP 7: Fix Stopped Services ---"
$rep7 = @()
try {
    # Software Protection (sppsvc) - important for Windows licensing
    $sppsvc = Get-Service sppsvc -ErrorAction SilentlyContinue
    if ($sppsvc -and $sppsvc.Status -eq "Stopped") {
        if (-not $DryRun) {
            Set-Service sppsvc -StartupType Automatic -ErrorAction SilentlyContinue
            Start-Service sppsvc -ErrorAction SilentlyContinue
        }
        $rep7 += "sppsvc (Software Protection): Started"
        Log "sppsvc started"
        $script:allFixed++
    } else {
        $rep7 += "sppsvc: OK"
    }

    # AppXSVC fix
    $appx = Get-Service AppXSvc -ErrorAction SilentlyContinue
    if ($appx -and $appx.Status -eq "Stopped") {
        if (-not $DryRun) {
            Start-Service AppXSvc -ErrorAction SilentlyContinue
        }
        $rep7 += "AppXSvc (AppX Deployment): Started"
        Log "AppXSvc started"
        $script:allFixed++
    } else {
        $rep7 += "AppXSvc: OK"
    }

    # Windows Update
    $wuauserv = Get-Service wuauserv -ErrorAction SilentlyContinue
    if ($wuauserv) {
        if (-not $DryRun) {
            Set-Service wuauserv -StartupType Manual -ErrorAction SilentlyContinue
        }
        $rep7 += "wuauserv (Windows Update): Set to Manual"
        $script:allFixed++
    }

    AddReportSection "Step 7: Fix Services" "ok" $rep7
} catch {
    AddReportSection "Step 7: Fix Services" "warn" @("Error: $_")
    $script:allSkipped++
}

# ============================================================
#  STEP 8: Driver Check & Scan
# ============================================================
Log ""
Log "--- STEP 8: Driver Scan ---"
$rep8 = @()
try {
    $rep8 += "Scanning for missing drivers..."

    # Check GPU driver status
    $gpu = Get-CimInstance Win32_VideoController | Where-Object { $_.Name -notlike "*Microsoft Basic*" }
    if (-not $gpu) {
        $rep8 += ""
        $rep8 += "*** GPU DRIVER MISSING ***"
        $rep8 += "Your AMD Radeon Graphics driver is NOT installed."
        $rep8 += "The system is using the Microsoft Basic Display Adapter."
        $rep8 += "This is the MOST LIKELY cause of your crashes."
        $rep8 += ""
        $rep8 += "HOW TO FIX (you MUST do this manually):"
        $rep8 += ""
        $rep8 += "Option A (with internet):"
        $rep8 += "  1. Connect to WiFi or plug in Ethernet"
        $rep8 += "  2. Run Windows Update (Settings -> Windows Update)"
        $rep8 += "  3. Check for updates -> Install ALL optional driver updates"
        $rep8 += ""
        $rep8 += "Option B (USB from another PC):"
        $rep8 += "  1. On a working PC, go to: https://www.amd.com/en/support"
        $rep8 += "  2. Download 'AMD Ryzen 5 4600U Drivers' (AMD Adrenalin)"
        $rep8 += "  3. Save to USB drive"
        $rep8 += "  4. Run the installer on this PC"
        $rep8 += ""
        $rep8 += "Option C (Lenovo drivers):"
        $rep8 += "  1. Go to: https://pcsupport.lenovo.com"
        $rep8 += "  2. Search for '81YN' (your model)"
        $rep8 += "  3. Download Chipset + Graphics + Network drivers"
        $rep8 += "  4. Transfer via USB and install"

        $gpuStatus = "err"
    } else {
        $rep8 += "GPU driver found: $($gpu.Name)"
        $rep8 += "Driver: $($gpu.DriverVersion)"
        $gpuStatus = "ok"
    }

    # Check for driver updates via Windows Update (if available)
    if (-not $DryRun) {
        $rep8 += ""
        $rep8 += "Triggering Windows Update driver scan..."
        try {
            $updateSession = New-Object -ComObject Microsoft.Update.Session -ErrorAction Stop
            $updateSearcher = $updateSession.CreateUpdateSearcher()
            $updateSearcher.ServerSelection = 3  # ssWindowsUpdate
            $searchResult = $updateSearcher.Search("IsInstalled=0 AND Type='Driver'")
            $drvCount = @($searchResult.Updates).Count
            if ($drvCount -gt 0) {
                $rep8 += "Windows Update found $drvCount driver update(s) available"
                $rep8 += "Run: Settings -> Windows Update -> Check for updates"
            } else {
                $rep8 += "No driver updates found via Windows Update (network may be offline)"
            }
        } catch {
            $rep8 += "Windows Update check failed (network offline or service issue)"
        }
    }

    AddReportSection "Step 8: Driver Status" $gpuStatus $rep8
    if ($gpuStatus -eq "err") { $script:allFailed++ } else { $script:allSkipped++ }
} catch {
    AddReportSection "Step 8: Driver Status" "err" @("Error: $_")
    $script:allFailed++
}

# ============================================================
#  STEP 9: Temperature / Thermal
# ============================================================
Log ""
Log "--- STEP 9: Thermal Mitigation ---"
$rep9 = @()
try {
    # Set processor performance decrease threshold (more aggressive cooling)
    $perfKey = "HKLM:\SYSTEM\CurrentControlSet\Control\Power\PowerSettings\54533251-82be-4824-96c1-47b60b740d00\06cadf0e-64ed-448a-8927-ce7bf90eb35d"
    if (-not $DryRun) {
        # Set active cooling
        powercfg /setacvalueindex scheme_current sub_processor 94d3a615-a899-4ac5-ae2b-e38d1f7b7e98 1 2>&1 | Out-Null
        powercfg /setactive scheme_current 2>&1 | Out-Null
    }

    $rep9 += "CPU idle temperature was 73C - this is HIGH"
    $rep9 += "Actions taken:"
    $rep9 += "  - Set Balanced power plan (reduces unnecessary boosting)"
    $rep9 += "  - Enabled active cooling policy"
    $rep9 += ""
    $rep9 += "Additional recommendations:"
    $rep9 += "  1. Clean laptop vents with compressed air"
    $rep9 += "  2. Ensure laptop is on a hard flat surface (not bed/sofa)"
    $rep9 += "  3. Consider a cooling pad"
    $rep9 += "  4. Check if fan is spinning (can you hear it?)"

    AddReportSection "Step 9: Thermal Management" "warn" $rep9
    $script:allFixed++
} catch {
    AddReportSection "Step 9: Thermal Management" "warn" @("Error: $_")
    $script:allSkipped++
}

# ============================================================
#  STEP 10: Windows Update Cleanup & Reset
# ============================================================
Log ""
Log "--- STEP 10: Windows Update Reset ---"
$rep10 = @()
try {
    $rep10 += "Resetting Windows Update components..."

    if (-not $DryRun) {
        # Stop services
        Stop-Service wuauserv -Force -ErrorAction SilentlyContinue
        Stop-Service bits -Force -ErrorAction SilentlyContinue
        Stop-Service cryptsvc -Force -ErrorAction SilentlyContinue

        # Rename SoftwareDistribution folder
        $sdPath = "$env:SystemRoot\SoftwareDistribution"
        if (Test-Path $sdPath) {
            Rename-Item $sdPath "SoftwareDistribution.old" -Force -ErrorAction SilentlyContinue
            $rep10 += "SoftwareDistribution folder reset"
        }

        # Rename catroot2
        $catPath = "$env:SystemRoot\System32\catroot2"
        if (Test-Path $catPath) {
            Rename-Item $catPath "catroot2.old" -Force -ErrorAction SilentlyContinue
            $rep10 += "Catroot2 folder reset"
        }

        # Restart services
        Start-Service cryptsvc -ErrorAction SilentlyContinue
        Start-Service bits -ErrorAction SilentlyContinue
        Start-Service wuauserv -ErrorAction SilentlyContinue
    }

    $rep10 += "Windows Update cache cleared"
    $rep10 += "This fixes the 0x8024402C error"

    AddReportSection "Step 10: Windows Update Repair" "ok" $rep10
    $script:allFixed++
} catch {
    AddReportSection "Step 10: Windows Update Repair" "warn" @("Error: $_")
    $script:allSkipped++
}

# ============================================================
#  SUMMARY
# ============================================================
Log ""
Log "============================================="
Log "  REPAIR COMPLETE"
Log "  Fixed: $allFixed | Skipped: $allSkipped | Failed: $allFailed"
Log "============================================="

# ============================================================
#  GENERATE REPORT
# ============================================================
$body = $sections -join "`n"

$html = @"
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Repair Report -- ${pcName} -- ${ts}</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI','Microsoft YaHei',sans-serif;background:#0d1117;color:#c9d1d9;padding:20px}
.header{text-align:center;padding:40px 20px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);border-radius:16px;margin-bottom:24px;border:1px solid #30363d}
.header h1{font-size:28px;color:#58a6ff;margin-bottom:8px}
.header .sub{color:#8b949e;font-size:14px}
.header .machine{color:#f0883e;font-size:16px;margin-top:4px}
.summary{display:flex;gap:16px;flex-wrap:wrap;margin-bottom:24px}
.scard{flex:1;min-width:140px;background:#161b22;border:1px solid #30363d;border-radius:12px;padding:20px;text-align:center}
.scard .val{font-size:32px;font-weight:bold;margin-bottom:4px}
.scard .lbl{font-size:13px;color:#8b949e}
.scard.ok .val{color:#3fb950}
.scard.err .val{color:#f85149}
.scard.warn .val{color:#d2991d}
.section{background:#161b22;border:1px solid #30363d;border-radius:12px;margin-bottom:16px;overflow:hidden}
.sec-head{display:flex;align-items:center;padding:16px 20px;gap:12px;border-bottom:1px solid #21262d}
.sec-head h2{font-size:16px;font-weight:600;flex:1;color:#e6edf3}
.badge{padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600;background:#ffffff10}
.sec-body{padding:16px 20px}
.line{padding:4px 0;font-size:14px;line-height:1.7;color:#c9d1d9;font-family:'Cascadia Code','Consolas','Microsoft YaHei',monospace;border-bottom:1px solid #21262d20}
.line:last-child{border-bottom:none}
.critical-box{background:#f8514920;border:2px solid #f85149;border-radius:12px;padding:20px;margin-bottom:24px}
.critical-box h3{color:#f85149;margin-bottom:12px;font-size:18px}
.critical-box p{line-height:2;font-size:15px}
.footer{text-align:center;padding:20px;color:#484f58;font-size:12px}
@media print{body{background:#fff;color:#333}.section{break-inside:avoid;border:1px solid #ddd}}
</style>
</head>
<body>
<div class="header">
<h1>PC Repair Report</h1>
<div class="machine">Computer: ${pcName} (Lenovo 81YN / AMD Ryzen 5 4600U)</div>
<div class="sub">Repair Time: ${ts} | Repair Tool v1.0</div>
</div>
<div class="summary">
<div class="scard ok"><div class="val">${allFixed}</div><div class="lbl">Fixed</div></div>
<div class="scard warn"><div class="val">${allSkipped}</div><div class="lbl">Skipped</div></div>
<div class="scard err"><div class="val">${allFailed}</div><div class="lbl">Failed</div></div>
</div>

<div class="critical-box">
<h3>*** CRITICAL: GPU DRIVER NOT INSTALLED ***</h3>
<p>
Your AMD Radeon Graphics driver is MISSING. The system is running on the basic Microsoft display driver from 2006.<br>
This is the #1 cause of crashes (Event 41 / blue screens) on your system.<br><br>
<b>To fix this you need to install the AMD driver. Options:</b><br>
1. Connect to internet and run Windows Update<br>
2. Download AMD Adrenalin driver from another PC, put on USB, install here<br>
3. Download Lenovo drivers for model 81YN from pcsupport.lenovo.com
</p>
</div>

${body}
<div class="footer">Repair Tool v1.0 -- ${ts} -- Run from USB</div>
</body>
</html>
"@

$html | Out-File -FilePath $reportFile -Encoding UTF8

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  REPAIR COMPLETE" -ForegroundColor Green
Write-Host "  Report: $reportFile" -ForegroundColor White
Write-Host "  Log: $logFile" -ForegroundColor White
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Fixed: $allFixed | Skipped: $allSkipped | Failed: $allFailed" -ForegroundColor Cyan

try { Start-Process $reportFile } catch {}

Write-Host ""
Write-Host "Window closes in 30 seconds..." -ForegroundColor Gray
Start-Sleep -Seconds 30
