$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[ai-game-dev-agent] $Message"
}

function Get-FreePort {
    param([int[]]$Candidates)

    foreach ($port in $Candidates) {
        $listener = $null
        try {
            $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $port)
            $listener.Start()
            $listener.Stop()
            return $port
        }
        catch {
            if ($listener) {
                $listener.Stop()
            }
            Write-Step "Port $port is busy, trying next candidate."
        }
    }

    throw "No free port available in 8000-8003."
}

function Install-Micromamba {
    param(
        [string]$MambaDir,
        [string]$MambaExe
    )

    if (Test-Path $MambaExe) {
        Write-Step "Portable micromamba already exists."
        return
    }

    Write-Step "Downloading portable micromamba for Windows."
    $archivePath = Join-Path $MambaDir "micromamba.tar.bz2"
    $url = "https://micro.mamba.pm/api/micromamba/win-64/latest"
    Invoke-WebRequest -Uri $url -OutFile $archivePath

    Write-Step "Extracting micromamba."
    tar -xf $archivePath -C $MambaDir
    $found = Get-ChildItem $MambaDir -Recurse -Filter micromamba.exe | Select-Object -First 1
    if (-not $found) {
        throw "Downloaded micromamba archive did not contain micromamba.exe."
    }
    Copy-Item $found.FullName $MambaExe -Force
}

function Ensure-RuntimeEnvironment {
    param(
        [string]$MambaExe,
        [string]$EnvDir,
        [string]$RequirementsFile
    )

    $pythonExe = Join-Path $EnvDir "python.exe"
    if (Test-Path $pythonExe) {
        Write-Step "Runtime environment already exists."
        return
    }

    if (Test-Path $EnvDir) {
        Write-Step "Found incomplete runtime environment. Removing it before retry."
        Remove-Item -LiteralPath $EnvDir -Recurse -Force
    }

    Write-Step "Creating Python runtime with conda-forge only. This can take several minutes on first launch."
    & $MambaExe create -y -p $EnvDir -c conda-forge --override-channels python=3.11 pip
    if ($LASTEXITCODE -ne 0) {
        throw "micromamba failed to create the Python runtime."
    }

    Write-Step "Installing Python packages from requirements.txt."
    & $MambaExe run -p $EnvDir python -m pip install -r $RequirementsFile
    if ($LASTEXITCODE -ne 0) {
        throw "pip failed to install project dependencies."
    }
}

try {
    $Root = Split-Path -Parent $PSScriptRoot
    $RuntimeDir = Join-Path $Root "runtime"
    $MambaDir = Join-Path $RuntimeDir "micromamba"
    $MambaExe = Join-Path $MambaDir "micromamba.exe"
    $EnvRoot = Join-Path $RuntimeDir "envs"
    $EnvDir = Join-Path $EnvRoot "ai-game-dev-agent"
    $RequirementsFile = Join-Path $Root "requirements.txt"

    Write-Step "Project root: $Root"
    New-Item -ItemType Directory -Force -Path $RuntimeDir, $MambaDir, $EnvRoot | Out-Null

    Install-Micromamba -MambaDir $MambaDir -MambaExe $MambaExe
    Ensure-RuntimeEnvironment -MambaExe $MambaExe -EnvDir $EnvDir -RequirementsFile $RequirementsFile

    $Port = Get-FreePort -Candidates @(8000, 8001, 8002, 8003)
    $Url = "http://127.0.0.1:$Port"
    Write-Step "Starting FastAPI on $Url"
    Start-Process $Url

    Set-Location $Root
    & $MambaExe run -p $EnvDir python -m uvicorn app.main:app --host 127.0.0.1 --port $Port --app-dir $Root
}
catch {
    Write-Host ""
    Write-Host "[ai-game-dev-agent] Startup failed:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host "If startup was interrupted, delete the runtime folder and run start_windows.cmd again." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to close this window."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}
