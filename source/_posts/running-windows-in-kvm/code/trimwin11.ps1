<#
.SYNOPSIS
  Disable unneeded services and scheduled tasks in a build-only Windows 11 VM.

.DESCRIPTION
  This script turns off background services and tasks that aren’t needed for
  a development/build VM, freeing CPU, RAM, and I/O.

.NOTES
  Must be run in an elevated (Admin) PowerShell session.
#>

# Ensure we’re running as Admin
if (-not ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent() `
    ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "Please run this script as Administrator."
    exit 1
}

# 1) Disable & stop unneeded services
$services = @(
    "Spooler",       # Print Spooler
    "SysMain",       # Superfetch / memory prefetch
    "WSearch",       # Windows Search Indexer
    "BITS",          # Background Intelligent Transfer Service
    "wuauserv",      # Windows Update
    "DiagTrack",     # Connected User Experiences & Telemetry
    "WerSvc",        # Windows Error Reporting Service
    "XPSFLSvc"       # XPS Print Filter (if present)
)

foreach ($svc in $services) {
    $s = Get-Service -Name $svc -ErrorAction SilentlyContinue
    if ($s) {
        Write-Verbose "Disabling service $svc"
        Set-Service -Name $svc -StartupType Disabled
        if ($s.Status -ne 'Stopped') {
            Write-Verbose "Stopping service $svc"
            Stop-Service -Name $svc -Force
        }
        Write-Output "Service '$svc' disabled/stopped."
    }
    else {
        Write-Warning "Service '$svc' not found, skipping."
    }
}

# 2) Disable groups of scheduled tasks by path
#    These folders contain telemetry, update scans, compatibility checks, etc.
$taskPaths = @(
    "\Microsoft\Windows\Application Experience\",
    "\Microsoft\Windows\Customer Experience Improvement Program\",
    "\Microsoft\Windows\UpdateOrchestrator\",
    "\Microsoft\Windows\Windows Defender\"
    "\Microsoft\Windows\Defrag\"
)

foreach ($path in $taskPaths) {
    Write-Verbose "Disabling all tasks under $path"
    try {
        Get-ScheduledTask -TaskPath $path -ErrorAction Stop |
          ForEach-Object {
              Disable-ScheduledTask -TaskPath $_.TaskPath -TaskName $_.TaskName
              Write-Output "Disabled task '$($_.TaskName)' in '$($path)'."
          }
    }
    catch {
        Write-Warning "No tasks found under '$path'."
    }
}

# 3) Disable any OneDrive-related scheduled tasks (root-level)
Write-Verbose "Disabling OneDrive tasks"
Get-ScheduledTask |
  Where-Object { $_.TaskName -like "OneDrive*" } |
  ForEach-Object {
      Disable-ScheduledTask -TaskPath $_.TaskPath -TaskName $_.TaskName
      Write-Output "Disabled OneDrive task '$($_.TaskName)'."
  }

Write-Output "Service & scheduled task trimming complete."
