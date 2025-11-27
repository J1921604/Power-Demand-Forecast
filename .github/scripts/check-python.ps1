# ================================================================
# Python 3.10.11 Environment Check Script
# ================================================================
# 
# Purpose:
#   - Verify Python 3.10.11 is installed
#   - Check all dependencies from requirements.txt
#   - Validate import functionality
#
# Usage:
#   .\.github\scripts\check-python.ps1
#
# Exit Codes:
#   0: Success (Python 3.10.11 detected)
#   1: Python 3.10.11 not found
#   2: Dependencies missing
#
# ================================================================

param(
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

# Colors for output
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Failure { Write-Host $args -ForegroundColor Red }
function Write-Info { Write-Host $args -ForegroundColor Cyan }

Write-Info "================================================================"
Write-Info "  Python 3.10.11 Environment Check"
Write-Info "================================================================"
Write-Host ""

# ================================================================
# Step 1: Detect Python 3.10.11
# ================================================================

Write-Info "[1/4] Detecting Python 3.10.11..."

$pythonCmd = $null
$pythonVersion = $null
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
        
        if ($version -match "Python 3\.10\.(\d+)") {
            $patchVersion = $Matches[1]
            if ($testArgs) {
                $pythonCmd = "$testCmd $testArgs"
            } else {
                $pythonCmd = $testCmd
            }
            $pythonVersion = $version
            Write-Success "✓ Python detected: $version"
            
            if ($patchVersion -ne "11") {
                Write-Warning "  Warning: Expected Python 3.10.11, found $version"
                Write-Warning "  This may cause compatibility issues."
            }
            break
        }
    } catch {
        continue
    }
}

if (-not $pythonCmd) {
    Write-Failure "✗ Python 3.10.11 not found."
    Write-Host ""
    Write-Info "Installation Instructions:"
    Write-Host "  1. Download Python 3.10.11: https://www.python.org/downloads/release/python-31011/"
    Write-Host "  2. Run installer and check 'Add Python to PATH'"
    Write-Host "  3. Verify: py -3.10 --version"
    Write-Host ""
    exit 1
}

# ================================================================
# Step 2: Check Python executable path
# ================================================================

Write-Info "[2/4] Checking Python executable path..."

try {
    if ($pythonCmd -match " ") {
        $parts = $pythonCmd -split " ", 2
        $pythonPath = & $parts[0] $parts[1] -c "import sys; print(sys.executable)" 2>&1
    } else {
        $pythonPath = & $pythonCmd -c "import sys; print(sys.executable)" 2>&1
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✓ Python executable: $pythonPath"
    } else {
        Write-Failure "✗ Failed to get Python executable path"
        exit 1
    }
} catch {
    Write-Failure "✗ Error getting Python path: $_"
    exit 1
}

# ================================================================
# Step 3: Check dependencies (requirements.txt)
# ================================================================

Write-Info "[3/4] Checking dependencies..."

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)
$requirementsFile = Join-Path $repoRoot "AI\requirements.txt"

if (-not (Test-Path $requirementsFile)) {
    Write-Warning "✗ requirements.txt not found: $requirementsFile"
    Write-Warning "  Skipping dependency check."
} else {
    Write-Info "  Checking packages from: AI\requirements.txt"
    
    # Parse requirements.txt
    $packages = Get-Content $requirementsFile | Where-Object { 
        $_ -match "^\s*[a-zA-Z]" -and $_ -notmatch "^\s*#" 
    } | ForEach-Object {
        if ($_ -match "^([a-zA-Z0-9\-_]+)==(.+)$") {
            @{name=$Matches[1]; version=$Matches[2]}
        }
    }
    
    $missingPackages = @()
    $versionMismatches = @()
    
    foreach ($pkg in $packages) {
        try {
            if ($pythonCmd -match " ") {
                $parts = $pythonCmd -split " ", 2
                $installedVersion = & $parts[0] $parts[1] -m pip show $pkg.name 2>&1 | Select-String "Version:" | ForEach-Object { $_ -replace "Version:\s*", "" }
            } else {
                $installedVersion = & $pythonCmd -m pip show $pkg.name 2>&1 | Select-String "Version:" | ForEach-Object { $_ -replace "Version:\s*", "" }
            }
            
            if ($LASTEXITCODE -ne 0 -or -not $installedVersion) {
                $missingPackages += $pkg.name
                if ($Verbose) {
                    Write-Warning "  ✗ Missing: $($pkg.name)"
                }
            } elseif ($installedVersion -ne $pkg.version) {
                $versionMismatches += @{
                    name=$pkg.name
                    expected=$pkg.version
                    actual=$installedVersion
                }
                if ($Verbose) {
                    Write-Warning "  ! Version mismatch: $($pkg.name) (expected: $($pkg.version), actual: $installedVersion)"
                }
            } else {
                if ($Verbose) {
                    Write-Success "  ✓ $($pkg.name)==$installedVersion"
                }
            }
        } catch {
            $missingPackages += $pkg.name
        }
    }
    
    if ($missingPackages.Count -eq 0 -and $versionMismatches.Count -eq 0) {
        Write-Success "✓ All dependencies installed and versions match"
    } else {
        if ($missingPackages.Count -gt 0) {
            Write-Warning "✗ Missing packages ($($missingPackages.Count)): $($missingPackages -join ', ')"
        }
        if ($versionMismatches.Count -gt 0) {
            Write-Warning "! Version mismatches ($($versionMismatches.Count)):"
            foreach ($mismatch in $versionMismatches) {
                Write-Host "    $($mismatch.name): expected $($mismatch.expected), actual $($mismatch.actual)" -ForegroundColor Yellow
            }
        }
        Write-Host ""
        Write-Info "To install/update dependencies:"
        Write-Host "  cd AI"
        Write-Host "  py -3.10 -m pip install -r requirements.txt"
        Write-Host ""
        exit 2
    }
}

# ================================================================
# Step 4: Test critical imports
# ================================================================

Write-Info "[4/4] Testing critical imports..."

$criticalImports = @(
    "pandas",
    "numpy",
    "sklearn",
    "lightgbm",
    "tensorflow",
    "pycaret"
)

$importErrors = @()

foreach ($module in $criticalImports) {
    try {
        if ($pythonCmd -match " ") {
            $parts = $pythonCmd -split " ", 2
            $result = & $parts[0] $parts[1] -c "import $module" 2>&1
        } else {
            $result = & $pythonCmd -c "import $module" 2>&1
        }
        
        if ($LASTEXITCODE -eq 0) {
            if ($Verbose) {
                Write-Success "  ✓ import $module"
            }
        } else {
            $importErrors += $module
            Write-Warning "  ✗ Failed to import $module"
        }
    } catch {
        $importErrors += $module
        Write-Warning "  ✗ Failed to import $module"
    }
}

if ($importErrors.Count -eq 0) {
    Write-Success "✓ All critical modules can be imported"
} else {
    Write-Failure "✗ Import errors: $($importErrors -join ', ')"
    Write-Host ""
    Write-Info "Some modules failed to import. Please check:"
    Write-Host "  1. Dependencies are installed: py -3.10 -m pip install -r AI\requirements.txt"
    Write-Host "  2. No conflicting versions"
    Write-Host "  3. Python environment is clean"
    Write-Host ""
    exit 2
}

# ================================================================
# Success
# ================================================================

Write-Host ""
Write-Success "================================================================"
Write-Success "  ✓ Python 3.10.11 environment check passed"
Write-Success "================================================================"
Write-Host ""
Write-Info "Summary:"
Write-Host "  Python: $pythonVersion"
Write-Host "  Executable: $pythonPath"
Write-Host "  Dependencies: All installed"
Write-Host "  Imports: All successful"
Write-Host ""

exit 0
