@echo off
chcp 65001 >nul
title Driver Downloader - Lenovo 81YN / AMD Ryzen 5 4600U

echo.
echo ================================================
echo   Driver Downloader
echo   For: Lenovo 81YN + AMD Ryzen 5 4600U
echo ================================================
echo.
echo This will open driver download pages.
echo Save all files to this USB drive when downloaded.
echo.
echo Opening driver pages...
echo ================================================
echo.

:: Open AMD driver page
start https://www.amd.com/en/support/downloads/drivers.html/processors/ryzen/ryzen-4000-series/amd-ryzen-5-4600u.html

:: Open Lenovo support page
start https://pcsupport.lenovo.com/us/en/products/laptops-and-netbooks/ideapad-s-series-netbooks/ideapad-s145-15api/downloads/driver-list

:: Open Intel WiFi driver (common in this model)
start https://www.intel.com/content/www/us/en/download/19351/windows-10-and-windows-11-wi-fi-drivers-for-intel-wireless-adapters.html

echo.
echo ================================================
echo   Pages opened in browser:
echo   1. AMD Ryzen 5 4600U Driver (Adrenalin)
echo   2. Lenovo 81YN Support Page
echo   3. Intel WiFi Driver
echo.
echo   Download these and save to USB:
echo   - AMD Adrenalin (Auto-Detect or Ryzen 5 4600U)
echo   - Lenovo Chipset Driver for 81YN
echo   - Lenovo WiFi/Network Driver
echo   - Intel WiFi Driver (if Intel card)
echo ================================================
echo.
pause
