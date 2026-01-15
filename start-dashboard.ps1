# ================================================================
# Power-Demand-Forecast Dashboard One-Command Startup Script
# ================================================================
# 
# Features:
#   1. Start HTTP Server (Python server.py)
#   2. Auto-launch Browser (http://localhost:8002/)
#   3. Auto-close PowerShell
#
# Usage:
#   .\start-dashboard.ps1
#
# ================================================================

# Error handling configuration
$ErrorActionPreference = "Stop"

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$aiDir = Join-Path $scriptDir "AI"

# Check AI directory exists
if (-not (Test-Path $aiDir)) {
    Write-Host "Error: AI directory not found: $aiDir" -ForegroundColor Red
    Write-Host "Please run this script from the project root." -ForegroundColor Yellow
    pause
    exit 1
}

# Detect Python executable
$pythonCmd = $null
$pythonCandidates = @(
    @{cmd="py"; args="-3.10"},
    @{cmd="python3.10"; args=$null},
    @{cmd="python"; args=$null}
)

foreach ($candidate in $pythonCandidates) {
    try {
        if ($candidate.args) {
            $version = & $candidate.cmd $candidate.args --version 2>&1
            $testCmd = $candidate.cmd
            $testArgs = $candidate.args
        } else {
            $version = & $candidate.cmd --version 2>&1
            $testCmd = $candidate.cmd
            $testArgs = $null
        }
        
        if ($version -match "Python 3\.10") {
            if ($testArgs) {
                $pythonCmd = "$testCmd $testArgs"
            } else {
                $pythonCmd = $testCmd
            }
            Write-Host "Python detected: $version" -ForegroundColor Green
            break
        }
    } catch {
        continue
    }
}

if (-not $pythonCmd) {
    Write-Host "Error: Python 3.10 not found." -ForegroundColor Red
    Write-Host "Please install Python 3.10.11." -ForegroundColor Yellow
    pause
    exit 1
}

# Check server.py exists
$serverScript = Join-Path $aiDir "server.py"
if (-not (Test-Path $serverScript)) {
    Write-Host "Error: server.py not found: $serverScript" -ForegroundColor Red
    pause
    exit 1
}

# Check dependencies (requirements.txt)
$requirementsFile = Join-Path $aiDir "requirements.txt"
if (Test-Path $requirementsFile) {
    Write-Host "Checking dependencies..." -ForegroundColor Cyan
    try {
        if ($pythonCmd -match " ") {
            # Command with arguments (e.g., "py -3.10")
            $parts = $pythonCmd -split " ", 2
            $pipCheck = & $parts[0] $parts[1] -m pip show pandas 2>&1
        } else {
            # Simple command (e.g., "python")
            $pipCheck = & $pythonCmd -m pip show pandas 2>&1
        }
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Warning: Dependencies may be missing." -ForegroundColor Yellow
            Write-Host "Recommended: pip install -r AI\requirements.txt" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "Warning: Dependency check failed." -ForegroundColor Yellow
    }
}

# Server startup message
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Power-Demand-Forecast Dashboard Starting..." -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "HTTP Server: http://localhost:8002/dashboard/" -ForegroundColor Green
Write-Host "Stop: Ctrl+C" -ForegroundColor Yellow
Write-Host "Browser will auto-launch in 1 second..." -ForegroundColor Cyan
Write-Host ""

# Start HTTP server (foreground)
# Note: server.py automatically launches browser
try {
    Set-Location $aiDir
    if ($pythonCmd -match " ") {
        # Command with arguments (e.g., "py -3.10")
        $parts = $pythonCmd -split " ", 2
        & $parts[0] $parts[1] server.py
    } else {
        # Simple command (e.g., "python")
        & $pythonCmd server.py
    }
} catch {
    Write-Host ""
    Write-Host "Error: Failed to start server." -ForegroundColor Red
    Write-Host "Details: $_" -ForegroundColor Red
    pause
    exit 1
} finally {
    Set-Location $scriptDir
}

# Normal termination message (when stopped by Ctrl+C)
Write-Host ""
Write-Host "Dashboard stopped successfully." -ForegroundColor Green
Write-Host ""

# Auto-close PowerShell (optional: comment out to disable)
# exit 0
