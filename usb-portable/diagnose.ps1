
# ============================================================
#  PC Diagnostic Tool v2.1 - BSOD Specialist
#  Run as Administrator on the problem PC
# ============================================================
param(
    [string]$OutputDir = "",
    [switch]$SkipSlow = $false
)

$ErrorActionPreference = "Continue"

# Trap all errors to prevent sudden exit
trap {
    Write-Host "[TRAP] $_" -ForegroundColor Red
    continue
}

# --- Init ---
if ($OutputDir -eq "") {
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    if ($scriptDir -eq "") { $scriptDir = "." }
    $OutputDir = Join-Path $scriptDir "Report"
}
$null = New-Item -ItemType Directory -Path $OutputDir -Force -ErrorAction SilentlyContinue
$ts = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$pcName = $env:COMPUTERNAME
$ReportPath = Join-Path $OutputDir "${pcName}_Report_${ts}.html"

# Defaults
$ram_gb_global = "?"
$bsod_count = 0
$bsod_status = "info"
$disk_overall = "info"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  PC Diagnostic Tool v2.1" -ForegroundColor Cyan
Write-Host "  Computer: $pcName" -ForegroundColor Cyan
Write-Host "  Time: $ts" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$sections = @()

function Add-Section($title, $status, $lines) {
    $badge = ""
    $borderClr = "#58a6ff"
    if ($status -eq "ok") { $badge = "[OK]"; $borderClr = "#3fb950" }
    elseif ($status -eq "warn") { $badge = "[WARN]"; $borderClr = "#d2991d" }
    elseif ($status -eq "err") { $badge = "[ERROR]"; $borderClr = "#f85149" }
    $h = "<div class='section' style='border-left:3px solid ${borderClr}'><div class='sec-head'><h2>${title}</h2><span class='badge' style='color:${borderClr}'>${badge}</span></div><div class='sec-body'>"
    foreach ($l in $lines) { $h += "<div class='line'>$l</div>" }
    $h += "</div></div>"
    $script:sections += $h
}

# ============================================================
#  1. System Overview
# ============================================================
Write-Host "[1/10] System Overview..." -ForegroundColor Yellow
$sys = @()
try {
    $cs = Get-CimInstance Win32_ComputerSystem
    $os = Get-CimInstance Win32_OperatingSystem
    $bios = Get-CimInstance Win32_BIOS
    $mb = Get-CimInstance Win32_BaseBoard
    $uptime = (Get-Date) - $os.LastBootUpTime
    $sys += "Computer: $($cs.Name)"
    $sys += "Make/Model: $($cs.Manufacturer) / $($cs.Model)"
    $sys += "Motherboard: $($mb.Manufacturer) $($mb.Product) (BIOS: $($bios.Manufacturer) $($bios.SMBIOSBIOSVersion), Date: $($bios.ReleaseDate.ToString('yyyy-MM-dd')))"
    $sys += "OS: $($os.Caption) (Version $($os.Version), Build $($os.BuildNumber))"
    $sys += "Architecture: $($os.OSArchitecture) | Install Date: $($os.InstallDate.ToString('yyyy-MM-dd'))"
    $sys += "Last Boot: $($os.LastBootUpTime.ToString('yyyy-MM-dd HH:mm')) | Uptime: $([math]::Floor($uptime.TotalDays))d $($uptime.Hours)h $($uptime.Minutes)m"
    $sys += "CPU: $($cs.Name -replace '\s+', ' ')"
    $ram_gb_global = [math]::Round($cs.TotalPhysicalMemory / 1GB, 1)
    $sys += "RAM: ${ram_gb_global} GB (Free: $([math]::Round($os.FreePhysicalMemory / 1MB, 1)) GB)"
    Add-Section "System Overview" "ok" $sys
} catch {
    Add-Section "System Overview" "err" @("Failed: $_")
}

# ============================================================
#  2. CPU & Temperature
# ============================================================
Write-Host "[2/10] CPU & Temperature..." -ForegroundColor Yellow
$cpu_lines = @()
try {
    $cpus = Get-CimInstance Win32_Processor
    foreach ($cpu in $cpus) {
        $cpu_lines += "CPU: $($cpu.Name -replace '\s+', ' ')"
        $cpu_lines += "  Cores: $($cpu.NumberOfCores) | Logical: $($cpu.NumberOfLogicalProcessors) | Threads: $($cpu.ThreadCount)"
        $cpu_lines += "  Max Speed: $($cpu.MaxClockSpeed) MHz | Current: $($cpu.CurrentClockSpeed) MHz"
        $cpu_lines += "  L2 Cache: $([math]::Round($cpu.L2CacheSize/1024,1)) MB | L3: $([math]::Round($cpu.L3CacheSize/1024,1)) MB"
        if ($cpu.VirtualizationFirmwareEnabled) { $virt = "YES" } else { $virt = "NO" }
        $cpu_lines += "  Socket: $($cpu.SocketDesignation) | Virtualization: $virt"
    }
    $temps = Get-CimInstance MSAcpi_ThermalZoneTemperature -Namespace "root/wmi" -ErrorAction SilentlyContinue
    if ($temps) {
        foreach ($t in $temps) {
            $c = ($t.CurrentTemperature / 10) - 273.15
            $cpu_lines += "Temperature (ACPI): $([math]::Round($c, 1)) deg C"
        }
    } else {
        $cpu_lines += "Temperature: Not available (common on desktop/newer CPUs)"
    }
    $load = (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
    $cpu_lines += "Current CPU Load: ${load}%"
    Add-Section "CPU & Temperature" "ok" $cpu_lines
} catch {
    Add-Section "CPU & Temperature" "warn" @("CPU check error: $_")
}

# ============================================================
#  3. Memory
# ============================================================
Write-Host "[3/10] Memory..." -ForegroundColor Yellow
$mem_lines = @()
try {
    $mems = Get-CimInstance Win32_PhysicalMemory
    $idx = 1
    foreach ($m in $mems) {
        $sz = [math]::Round($m.Capacity / 1GB, 1)
        $mem_lines += "Slot #${idx}: $($m.Manufacturer) $($m.PartNumber) -- ${sz} GB, $($m.Speed) MHz, Type=$($m.MemoryType), FF=$($m.FormFactor)"
        $idx++
    }
    $totalRam = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1)
    $os2 = Get-CimInstance Win32_OperatingSystem
    $freeRam = [math]::Round($os2.FreePhysicalMemory / 1MB, 1)
    $usedPct = [math]::Round(($totalRam - $freeRam) / $totalRam * 100, 1)
    $mem_lines += "Total: ${totalRam} GB | Used: ${usedPct}% | Free: ${freeRam} GB"
    $mem_lines += "Virtual Memory: Total $([math]::Round($os2.TotalVirtualMemorySize/1MB,1)) GB | Free $([math]::Round($os2.FreeVirtualMemory/1MB,1)) GB"
    Add-Section "Memory" "ok" $mem_lines
} catch {
    Add-Section "Memory" "warn" @("Memory check error: $_")
}

# ============================================================
#  4. Disks
# ============================================================
Write-Host "[4/10] Disk Health..." -ForegroundColor Yellow
$disk_lines = @()
try {
    $disks = Get-PhysicalDisk -ErrorAction SilentlyContinue
    if (-not $disks) { $disks = Get-CimInstance Win32_DiskDrive }
    foreach ($d in $disks) {
        $model = if ($d.Model) { $d.Model } elseif ($d.Caption) { $d.Caption } else { "Unknown" }
        $sz = [math]::Round($d.Size / 1GB, 1)
        $hlth = if ($d.HealthStatus) { $d.HealthStatus } elseif ($d.Status) { $d.Status } else { "Unknown" }
        $md = if ($d.MediaType) { $d.MediaType } else { "Unknown" }
        $disk_lines += "[${model}] ${sz} GB | Type: ${md} | Health: ${hlth}"
        if ($hlth -ne "Healthy" -and $hlth -ne "OK") { $script:disk_overall = "err" }
    }
    $vols = Get-Volume | Where-Object { $_.DriveLetter }
    foreach ($v in $vols) {
        $free = [math]::Round($v.SizeRemaining / 1GB, 1)
        $tot = [math]::Round($v.Size / 1GB, 1)
        $pct = if ($tot -gt 0) { [math]::Round($free / $tot * 100, 1) } else { 0 }
        $fsOk = if ($v.HealthStatus -eq "Healthy") { "OK" } else { "WARN: $($v.HealthStatus)" }
        $disk_lines += "  $($v.DriveLetter):\ [$($v.FileSystem)] ${free} GB free / ${tot} GB total (${pct}%) -- $fsOk"
    }
    $chk = Get-WinEvent -LogName Application -MaxEvents 3 -FilterXPath "*[System[Provider[@Name='Chkdsk']]]" -ErrorAction SilentlyContinue
    if ($chk) {
        $disk_lines += "Recent disk checks:"
        foreach ($c in $chk) {
            $msg = ($c.Message -split "`n")[0]
            if ($msg.Length -gt 200) { $msg = $msg.Substring(0, 200) }
            $disk_lines += "  [$($c.TimeCreated.ToString('MM-dd HH:mm'))] $msg"
        }
    }
    Add-Section "Disks" $script:disk_overall $disk_lines
} catch {
    Add-Section "Disks" "warn" @("Disk check error: $_")
}

# ============================================================
#  5. GPU
# ============================================================
Write-Host "[5/10] GPU..." -ForegroundColor Yellow
$gpu_lines = @()
try {
    $gpus = Get-CimInstance Win32_VideoController | Where-Object { $_.Name -notlike "*Microsoft Basic*" }
    foreach ($g in $gpus) {
        $vram = if ($g.AdapterRAM) { [math]::Round($g.AdapterRAM / 1MB, 0) } else { "?" }
        $gpu_lines += "GPU: $($g.Name)"
        $gpu_lines += "  VRAM: ${vram} MB | Driver: $($g.DriverVersion) | Date: $($g.DriverDate.ToString('yyyy-MM-dd'))"
        $gpu_lines += "  Resolution: $($g.CurrentHorizontalResolution)x$($g.CurrentVerticalResolution) @ $($g.CurrentRefreshRate)Hz ($($g.CurrentBitsPerPixel)bit)"
        $gpu_lines += "  Status: $($g.Status)"
    }
    if (-not $gpus) { $gpu_lines += "No dedicated GPU detected" }
    Add-Section "GPU" "ok" $gpu_lines
} catch {
    Add-Section "GPU" "warn" @("GPU check error: $_")
}

# ============================================================
#  6. BLUE SCREEN ANALYSIS (Core)
# ============================================================
Write-Host "[6/10] Blue Screen Analysis..." -ForegroundColor Yellow
$bsod_lines = @()
try {
    $dumpDir = "$env:SystemRoot\Minidump"
    $bsod_count = 0
    if (Test-Path $dumpDir) {
        $dumps = Get-ChildItem $dumpDir -Filter "*.dmp" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
        $bsod_count = @($dumps).Count
        if ($bsod_count -gt 0) {
            $script:bsod_status = "err"
            $bsod_lines += "*** FOUND ${bsod_count} BLUE SCREEN DUMP FILE(S)! ***"
            $bsod_lines += ""
            $show = [Math]::Min($bsod_count, 10)
            for ($i = 0; $i -lt $show; $i++) {
                $d = $dumps[$i]
                $szKB = [math]::Round($d.Length / 1KB, 1)
                $bsod_lines += "Dump #$($i+1): $($d.Name) -- Time: $($d.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss')) -- Size: ${szKB} KB"
            }
            if ($bsod_count -gt 10) { $bsod_lines += "  ... and $($bsod_count - 10) more dump files" }

            # Try to analyze with built-in tools
            $bsod_lines += ""
            $bsod_lines += "--- Analysis Attempt ---"

            # Method 1: Check for windbg/cdb
            $cdbPaths = @(
                "${env:ProgramFiles(x86)}\Windows Kits\10\Debuggers\x64\cdb.exe",
                "${env:ProgramFiles}\Windows Kits\10\Debuggers\x64\cdb.exe",
                "C:\Debuggers\x64\cdb.exe"
            )
            $cdb = $null
            foreach ($p in $cdbPaths) { if (Test-Path $p) { $cdb = $p; break } }
            if ($cdb -and $dumps.Count -gt 0) {
                $latest = $dumps[0].FullName
                $bsod_lines += "Analyzing with cdb.exe..."
                $sym = "srv*C:\Symbols*https://msdl.microsoft.com/download/symbols"
                $output = & $cdb -z $latest -y $sym -c "!analyze -v; q" 2>&1 | Out-String
                $lines = $output -split "`n"
                $bsod_lines += "--- cdb output (first 40 lines) ---"
                for ($j = 0; $j -lt [Math]::Min(40, $lines.Count); $j++) {
                    $bsod_lines += $lines[$j]
                }
            } else {
                $bsod_lines += "Note: Install WinDbg Preview from Microsoft Store for full dump analysis"
            }
        } else {
            $bsod_lines += "Minidump folder is empty -- no blue screen dumps"
        }
    } else {
        $bsod_lines += "No Minidump folder found (no BSODs yet, or dump not configured)"
    }

    # Crash dump settings
    $cr = Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\CrashControl" -ErrorAction SilentlyContinue
    if ($cr) {
        $dt = switch ($cr.CrashDumpEnabled) {
            0 { "None" }; 1 { "Full memory dump" }; 2 { "Kernel memory dump" }
            3 { "Minidump" }; 7 { "Automatic memory dump" }; default { "Unknown($($cr.CrashDumpEnabled))" }
        }
        $bsod_lines += ""
        $bsod_lines += "Current dump setting: $dt"
        if ($cr.AutoReboot -eq 1) { $bsod_lines += "Auto-restart after BSOD: YES" } else { $bsod_lines += "Auto-restart after BSOD: NO" }
    }

    Add-Section "Blue Screen Analysis" $script:bsod_status $bsod_lines
} catch {
    Add-Section "Blue Screen Analysis" "warn" @("BSOD analysis error: $_")
}

# ============================================================
#  7. System Event Log
# ============================================================
Write-Host "[7/10] System Events..." -ForegroundColor Yellow
$evt_lines = @()
try {
    # Crashes (EventID 41 = unexpected shutdown, 1001 = bugcheck)
    $crashes = Get-WinEvent -LogName System -MaxEvents 10 -FilterXPath "*[System[(EventID=1001 or EventID=41)]]" -ErrorAction SilentlyContinue
    if ($crashes) {
        $evt_lines += "Recent system crashes/unexpected shutdowns:"
        foreach ($c in $crashes) {
            $eid = $c.Id
            $msg = ($c.Message -split "`n")[0]
            if ($msg.Length -gt 250) { $msg = $msg.Substring(0, 250) + "..." }
            $evt_lines += "  [$($c.TimeCreated.ToString('MM-dd HH:mm:ss'))] EventID=${eid} -- $msg"
        }
    } else { $evt_lines += "No system crash events found" }

    # BugCheck events
    $bugs = Get-WinEvent -LogName System -MaxEvents 5 -FilterXPath "*[System[Provider[@Name='Microsoft-Windows-WER-SystemErrorReporting'] and (EventID=1001)]]" -ErrorAction SilentlyContinue
    if ($bugs) {
        $evt_lines += ""
        $evt_lines += "BugCheck records:"
        foreach ($b in $bugs) {
            $msg = $b.Message
            $bc = if ($msg -match 'BugcheckCode\s+(\d+)') { $matches[1] } else { "?" }
            $bp1 = if ($msg -match 'BugcheckParameter1\s+(0x[0-9a-fA-F]+)') { $matches[1] } else { "?" }
            $evt_lines += "  [$($b.TimeCreated.ToString('MM-dd HH:mm:ss'))] BugCheckCode=$bc, Param1=$bp1"
        }
    }

    # Critical + Error events
    $crit = Get-WinEvent -LogName System -MaxEvents 10 -FilterXPath "*[System[(Level=1 or Level=2)]]" -ErrorAction SilentlyContinue
    if ($crit) {
        $evt_lines += ""
        $evt_lines += "Recent critical/error events (Level 1-2):"
        foreach ($e in $crit) {
            $src = $e.ProviderName
            $eid = $e.Id
            $msg = ($e.Message -split "`n")[0]
            if ($msg.Length -gt 200) { $msg = $msg.Substring(0, 200) + "..." }
            $evt_lines += "  [$($e.TimeCreated.ToString('MM-dd HH:mm:ss'))] ${src} / ID:${eid} -- $msg"
        }
    }

    $es = if ($bugs) { "err" } elseif ($crashes) { "warn" } else { "ok" }
    Add-Section "System Events" $es $evt_lines
} catch {
    Add-Section "System Events" "warn" @("Event log error: $_")
}

# ============================================================
#  8. Drivers
# ============================================================
Write-Host "[8/10] Drivers..." -ForegroundColor Yellow
$drv_lines = @()
try {
    $bad = Get-CimInstance Win32_PnPSignedDriver | Where-Object { $_.DeviceName -and $_.Status -ne "OK" -and $_.Status -ne $null }
    if ($bad) {
        $drv_lines += "*** PROBLEM DEVICE DRIVERS ***"
        foreach ($d in $bad) {
            $drv_lines += "  FAIL: $($d.DeviceName) -- Status: $($d.Status) -- Driver: $($d.DriverVersion)"
        }
    } else { $drv_lines += "All device drivers: OK" }

    $drv_lines += ""
    $drv_lines += "3rd-party kernel drivers (potential conflicts):"
    $nonMs = Get-CimInstance Win32_SystemDriver | Where-Object {
        $_.StartMode -ne "Disabled" -and
        $_.PathName -notmatch "system32\\\\drivers" -and
        $_.PathName -notmatch "System32\\\\drivers" -and
        $_.PathName -notmatch "C:\\\\Windows"
    }
    if ($nonMs -and @($nonMs).Count -gt 0) {
        $show = [Math]::Min(@($nonMs).Count, 20)
        $nonMs | Sort-Object Name | Select-Object -First $show | ForEach-Object {
            $name = $_.Name
            $disp = $_.DisplayName
            $state = $_.State
            $sm = $_.StartMode
            $drv_lines += "  $name -- $disp -- State: $state, Start: $sm"
        }
        if (@($nonMs).Count -gt 20) { $drv_lines += "  ... and $($nonMs.Count - 20) more" }
    } else { $drv_lines += "  (none)" }

    Add-Section "Drivers" "ok" $drv_lines
} catch {
    Add-Section "Drivers" "warn" @("Driver check error: $_")
}

# ============================================================
#  9. Windows Updates
# ============================================================
Write-Host "[9/10] Windows Updates..." -ForegroundColor Yellow
$wu_lines = @()
try {
    $sess = New-Object -ComObject Microsoft.Update.Session -ErrorAction SilentlyContinue
    if ($sess) {
        $srch = $sess.CreateUpdateSearcher()
        $hist = $srch.QueryHistory(0, 15)
        $wu_lines += "Recent updates (last 15):"
        foreach ($h in $hist) {
            $res = if ($h.ResultCode -eq 2) { "OK" } elseif ($h.ResultCode -eq 0) { "Pending" } else { "FAIL($($h.ResultCode))" }
            $wu_lines += "  [$($h.Date.ToString('yyyy-MM-dd'))] $($h.Title) -- $res"
        }
        $pend = $srch.Search("IsInstalled=0 and IsHidden=0").Updates
        if ($pend -and @($pend).Count -gt 0) {
            $wu_lines += ""
            $wu_lines += "*** PENDING UPDATES ($(@($pend).Count)) ***"
            foreach ($u in $pend) { $wu_lines += "  - $($u.Title)" }
        } else { $wu_lines += ""; $wu_lines += "No pending updates" }
    } else {
        $wu_lines += "Windows Update COM not available"
        $hf = Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 10
        $wu_lines += "Recent hotfixes:"
        foreach ($h in $hf) { $wu_lines += "  [$($h.InstalledOn)] $($h.HotFixID) -- $($h.Description)" }
    }
    Add-Section "Windows Updates" "ok" $wu_lines
} catch {
    Add-Section "Windows Updates" "warn" @("Update check error: $_")
}

# ============================================================
#  10. Network + Summary
# ============================================================
Write-Host "[10/10] Network & Summary..." -ForegroundColor Yellow
$net_lines = @()
try {
    $adps = Get-NetAdapter -ErrorAction SilentlyContinue | Where-Object { $_.Status -eq "Up" }
    if ($adps) {
        foreach ($a in $adps) {
            $net_lines += "Adapter: $($a.Name) -- Status: $($a.Status) -- Speed: $($a.LinkSpeed)"
            $ips = Get-NetIPAddress -InterfaceIndex $a.InterfaceIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue
            foreach ($ip in $ips) {
                $dhcp = if ($ip.PrefixOrigin -eq 'Dhcp') { "DHCP" } else { "Static" }
                $net_lines += "  IP: $($ip.IPAddress)/$($ip.PrefixLength) ($dhcp)"
            }
        }
    } else { $net_lines += "No active network adapters" }
    try {
        $dns = Resolve-DnsName "www.baidu.com" -ErrorAction Stop
        $net_lines += "DNS: OK (www.baidu.com -> $($dns.IPAddress))"
    } catch { $net_lines += "DNS: FAIL -- Cannot resolve hostnames" }

    # Stopped auto-start services
    $badSvc = Get-CimInstance Win32_Service | Where-Object { $_.State -eq "Stopped" -and $_.StartMode -eq "Auto" }
    if ($badSvc) {
        $net_lines += ""
        $net_lines += "*** AUTO-START SERVICES THAT ARE STOPPED ***"
        foreach ($s in $badSvc | Select-Object -First 15) { $net_lines += "  STOPPED: $($s.Name) -- $($s.DisplayName)" }
    }
    Add-Section "Network & Services" "ok" $net_lines
} catch {
    Add-Section "Network & Services" "warn" @("Network check error: $_")
}

# ============================================================
#  GENERATE HTML REPORT
# ============================================================
Write-Host ""
Write-Host "Generating HTML report..." -ForegroundColor Green

$body = $sections -join "`n"

$html = @"
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PC Diagnostic Report -- ${pcName} -- ${ts}</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI','Microsoft YaHei',sans-serif;background:#0d1117;color:#c9d1d9;padding:20px}
.header{text-align:center;padding:40px 20px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);border-radius:16px;margin-bottom:24px;border:1px solid #30363d}
.header h1{font-size:28px;color:#58a6ff;margin-bottom:8px}
.header .sub{color:#8b949e;font-size:14px}
.header .machine{color:#f0883e;font-size:16px;margin-top:4px}
.summary{display:flex;gap:16px;flex-wrap:wrap;margin-bottom:24px}
.scard{flex:1;min-width:150px;background:#161b22;border:1px solid #30363d;border-radius:12px;padding:20px;text-align:center}
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
.footer{text-align:center;padding:20px;color:#484f58;font-size:12px}
@media print{body{background:#fff;color:#333}.section{break-inside:avoid;border:1px solid #ddd}}
</style>
</head>
<body>
<div class="header">
<h1>PC Diagnostic Report</h1>
<div class="machine">Computer: ${pcName}</div>
<div class="sub">Generated: ${ts} | Diagnostic Tool v2.1 | BSOD Specialist</div>
</div>
<div class="summary">
<div class="scard ok"><div class="val">${pcName}</div><div class="lbl">Computer Name</div></div>
<div class="scard ${bsod_status}"><div class="val">${bsod_count}</div><div class="lbl">BSOD Count</div></div>
<div class="scard ${disk_overall}"><div class="val">$((Get-PhysicalDisk -ErrorAction SilentlyContinue | Select-Object -First 1).HealthStatus)</div><div class="lbl">Disk Health</div></div>
<div class="scard ok"><div class="val">${ram_gb_global} GB</div><div class="lbl">Total RAM</div></div>
</div>
${body}
<div class="footer">PC Diagnostic Tool v2.1 -- Generated ${ts} -- Run from USB: E:\dad.bat</div>
</body>
</html>
"@

try {
    $html | Out-File -FilePath $ReportPath -Encoding UTF8
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "  REPORT SAVED" -ForegroundColor Green
    Write-Host "  $ReportPath" -ForegroundColor White
    Write-Host "================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Opening report in browser..." -ForegroundColor Cyan
    Start-Process $ReportPath -ErrorAction SilentlyContinue
} catch {
    Write-Host "ERROR saving report: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Diagnostic complete. Window will close in 10 seconds..." -ForegroundColor Gray
Start-Sleep -Seconds 10
