# ==============================================================================
# Doc2MD - Windows Shortcut Creator
# Membuat pintasan (shortcut) di Start Menu (agar muncul di Windows Search) & Desktop
# ==============================================================================

$WshShell = New-Object -ComObject WScript.Shell

$TargetExe = "D:\coding\www\doc-to-markdown\dist\app\app.exe"
$WorkingDir = "D:\coding\www\doc-to-markdown\dist\app"
$IconLocation = "D:\coding\www\doc-to-markdown\dist\app\app.exe,0"

# 1. Start Menu Shortcut (Indexed by Windows Search)
$StartMenuDir = [System.IO.Path]::Combine($env:APPDATA, "Microsoft\Windows\Start Menu\Programs")
if (-not (Test-Path -Path $StartMenuDir)) {
    New-Item -ItemType Directory -Path $StartMenuDir -Force | Out-Null
}
$StartMenuShortcutPath = [System.IO.Path]::Combine($StartMenuDir, "Doc2MD.lnk")
$Shortcut1 = $WshShell.CreateShortcut($StartMenuShortcutPath)
$Shortcut1.TargetPath = $TargetExe
$Shortcut1.WorkingDirectory = $WorkingDir
$Shortcut1.IconLocation = $IconLocation
$Shortcut1.Description = "Doc2MD - Document to Markdown Studio"
$Shortcut1.Save()

Write-Host "✅ Shortcut Start Menu berhasil dibuat: $StartMenuShortcutPath" -ForegroundColor Green

# 2. Desktop Shortcut
$DesktopDir = [Environment]::GetFolderPath("Desktop")
$DesktopShortcutPath = [System.IO.Path]::Combine($DesktopDir, "Doc2MD.lnk")
$Shortcut2 = $WshShell.CreateShortcut($DesktopShortcutPath)
$Shortcut2.TargetPath = $TargetExe
$Shortcut2.WorkingDirectory = $WorkingDir
$Shortcut2.IconLocation = $IconLocation
$Shortcut2.Description = "Doc2MD - Document to Markdown Studio"
$Shortcut2.Save()

Write-Host "✅ Shortcut Desktop berhasil dibuat: $DesktopShortcutPath" -ForegroundColor Green
Write-Host "💡 Sekarang Anda bisa menekan tombol Windows, lalu mengetik 'Doc2MD' untuk membuka aplikasi langsung!" -ForegroundColor Cyan
