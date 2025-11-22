# PowerShell script to install Dollar Assistant as Windows service
# Run as Administrator

$serviceName = "DollarAssistant"
$displayName = "Dollar AI Voice Assistant"
$description = "Always-running AI voice assistant with wake word detection"

# Get paths (update these to match your installation)
$pythonPath = "C:\path\to\venv\Scripts\python.exe"
$scriptPath = "C:\path\to\dollar\agent\main.py"

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "This script must be run as Administrator" -ForegroundColor Red
    exit 1
}

# Create service using NSSM (Non-Sucking Service Manager)
# Download NSSM from https://nssm.cc/download if not installed
$nssmPath = "C:\nssm\nssm.exe"

if (-not (Test-Path $nssmPath)) {
    Write-Host "NSSM not found. Please install from https://nssm.cc/download" -ForegroundColor Yellow
    Write-Host "Or use Task Scheduler method described in README.md" -ForegroundColor Yellow
    exit 1
}

# Install service
& $nssmPath install $serviceName $pythonPath "$scriptPath"
& $nssmPath set $serviceName DisplayName $displayName
& $nssmPath set $serviceName Description $description
& $nssmPath set $serviceName Start SERVICE_AUTO_START
& $nssmPath set $serviceName AppStdout "C:\logs\dollar-assistant.log"
& $nssmPath set $serviceName AppStderr "C:\logs\dollar-assistant.error.log"

Write-Host "Service installed successfully!" -ForegroundColor Green
Write-Host "Start with: net start $serviceName" -ForegroundColor Cyan
Write-Host "Stop with: net stop $serviceName" -ForegroundColor Cyan

