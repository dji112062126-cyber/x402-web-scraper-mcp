# Virtual memory adjustment script - must run as admin
$computer = Get-WmiObject Win32_ComputerSystem
$computer.AutomaticManagedPagefile = $false
$computer.Put() | Out-Null
Write-Host "Disabled auto pagefile management"

# Modify C: pagefile
$pf = Get-WmiObject Win32_PageFileSetting | Where-Object { $_.SettingID -like "*C:*" }
if ($pf) {
    $pf.InitialSize = 16384
    $pf.MaximumSize = 32768
    $pf.Put() | Out-Null
    Write-Host "Pagefile updated: InitialSize=16384 MB, MaximumSize=32768 MB"
} else {
    # Create new pagefile on C:
    $pf = [wmiclass]"Win32_PageFileSetting"
    $pf.InitialSize = 16384
    $pf.MaximumSize = 32768
    $pf.Name = "C:\pagefile.sys"
    $pf.Put() | Out-Null
    Write-Host "Created new pagefile on C: 16384-32768 MB"
}

# Verify
Get-WmiObject Win32_PageFileUsage | ForEach-Object {
    Write-Host "Verification - Name: $($_.Name), AllocatedBaseSize: $($_.AllocatedBaseSize) MB"
}
