$ErrorActionPreference = "Stop"
function Get-FreePort { param([int[]]$Candidates) foreach ($port in $Candidates) { $l=$null; try { $l=[System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback,$port); $l.Start(); $l.Stop(); return $port } catch { if ($l) {$l.Stop()} } } throw "No free port available in 8000-8003" }
$Root = Split-Path -Parent $PSScriptRoot
$RuntimeDir = Join-Path $Root "runtime"; $MambaDir = Join-Path $RuntimeDir "micromamba"; $MambaExe = Join-Path $MambaDir "micromamba.exe"; $EnvDir = Join-Path $RuntimeDir "envs/ai-game-dev-agent"
New-Item -ItemType Directory -Force -Path $RuntimeDir,$MambaDir,(Split-Path -Parent $EnvDir) | Out-Null
if (-not (Test-Path $MambaExe)) { Invoke-WebRequest -Uri "https://micro.mamba.pm/api/micromamba/win-64/latest" -OutFile (Join-Path $MambaDir "micromamba.zip"); Expand-Archive -Path (Join-Path $MambaDir "micromamba.zip") -DestinationPath $MambaDir -Force; Copy-Item (Get-ChildItem $MambaDir -Recurse -Filter micromamba.exe|Select-Object -First 1).FullName $MambaExe -Force }
if (-not (Test-Path (Join-Path $EnvDir "python.exe"))) { & $MambaExe create -y -p $EnvDir -f (Join-Path $Root "environment.yml") }
$Port = Get-FreePort -Candidates @(8000,8001,8002,8003); $Url = "http://127.0.0.1:$Port"; Start-Process $Url; & $MambaExe run -p $EnvDir python -m uvicorn app.main:app --host 127.0.0.1 --port $Port --app-dir $Root
