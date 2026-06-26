Write-Host "=== SYSTEM INFO ==="
Get-CimInstance Win32_ComputerSystem | ForEach-Object {
    Write-Host "Model: $($_.Model)"
    Write-Host "Total RAM GB: $([math]::Round($_.TotalPhysicalMemory/1GB, 1))"
}

Write-Host "`n=== DISK SPACE ==="
Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' | ForEach-Object {
    Write-Host "$($_.DeviceID) Total: $([math]::Round($_.Size/1GB,1))GB, Free: $([math]::Round($_.FreeSpace/1GB,1))GB"
}

Write-Host "`n=== POWER PLAN ==="
Get-CimInstance -ClassName Win32_PowerPlan -Namespace 'root\cimv2\power' | Where-Object { $_.IsActive } | ForEach-Object {
    Write-Host "Active: $($_.ElementName)"
}

Write-Host "`n=== TOP 25 PROCESSES BY MEMORY ==="
Get-Process | Sort-Object WS -Descending | Select-Object -First 25 | ForEach-Object {
    $memMB = [math]::Round($_.WS/1MB, 1)
    $cpuSec = $_.TotalProcessorTime.TotalSeconds
    Write-Host "$($_.ProcessName) (PID $($_.Id)): ${memMB}MB, CPU: $([math]::Round($cpuSec,0))s"
}

Write-Host "`n=== VIRTUAL MEMORY ==="
Get-CimInstance Win32_PageFileUsage | ForEach-Object {
    Write-Host "Name: $($_.Name)"
    Write-Host "AllocatedBaseSize MB: $($_.AllocatedBaseSize)"
    Write-Host "CurrentUsage MB: $($_.CurrentUsage)"
    Write-Host "PeakUsage MB: $($_.PeakUsage)"
}

Write-Host "`n=== GPU DETAILS ==="
Get-CimInstance Win32_VideoController | ForEach-Object {
    Write-Host "Name: $($_.Name)"
    Write-Host "Driver Version: $($_.DriverVersion)"
    Write-Host "VRAM MB: $([math]::Round($_.AdapterRAM/1MB,0))"
    Write-Host "---"
}

Write-Host "`n=== NVIDIA-SMI ==="
nvidia-smi --query-gpu=name,driver_version,memory.total,memory.used,memory.free,temperature.gpu,utilization.gpu --format=csv,noheader 2>&1
