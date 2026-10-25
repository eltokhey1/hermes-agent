param(
    [switch]$Poll
)
$ErrorActionPreference = "Stop"
$repo = "eltokhey1/hermes-agent"
$branch = "sandbox%2Fhermes-transport-smoke-20261025"
$folder = Join-Path $env:LOCALAPPDATA "HermesBridgePilot"
$python = (Get-Command python -ErrorAction Stop).Source
New-Item -ItemType Directory -Force -Path $folder | Out-Null

function Get-PinnedFile {
    param([string]$Path, [string]$Hash, [string]$Name)
    $endpoint = "repos/$repo/contents/$($Path)?ref=$branch"
    $response = & gh api $endpoint
    if ($LASTEXITCODE -ne 0) { throw "GitHub fetch failed: $Name" }
    $data = $response | ConvertFrom-Json
    if ($data.type -ne "file" -or $data.encoding -ne "base64") { throw "Invalid response: $Name" }
    $bytes = [Convert]::FromBase64String(($data.content -replace "\s", ""))
    $sha = [BitConverter]::ToString([Security.Cryptography.SHA256]::Create().ComputeHash($bytes)).Replace("-", "").ToLowerInvariant()
    if ($sha -ne $Hash) { throw "HASH_MISMATCH: $Name" }
    $target = Join-Path $folder $Name
    [IO.File]::WriteAllBytes($target, $bytes)
    Write-Host "PIN_VERIFIED=$Name"
    return $target
}

$worker = Get-PinnedFile "ops/bridge/hermes_bridge_v1.py" "f85bf5021fa2e05fc06abb52502932d09952a19fb0c1fcf6f83106158ac4278f" "hermes_bridge_v1.py"
$supervisor = Get-PinnedFile "ops/bridge/hermes_bridge_supervisor_v1.py" "c3b6faf883408797cdc36a5a7bc1414b37001e14124b4f566fa47b8217140277" "hermes_bridge_supervisor_v1.py"
$testA = Get-PinnedFile "ops/bridge/test_bridge_v1.py" "2a200312893d19d74cd19def74ecc8e652b4ade9600e93321376235e6e1e9ac3" "test_bridge_v1.py"
$testB = Get-PinnedFile "ops/bridge/test_supervisor_v1.py" "2c2475723cd10965230afb68a58d8acb62eb83c37ad5a6ddc4945b535b3af3fe" "test_supervisor_v1.py"

Write-Host "=== OFFLINE TESTS ==="
$testOut = Join-Path $folder "tests.stdout.log"
$testErr = Join-Path $folder "tests.stderr.log"
$testArgs = @("-B", "-m", "unittest", "discover", "-s", "`"$folder`"", "-p", "test_*.py", "-v")
$test = Start-Process -FilePath $python -ArgumentList $testArgs -PassThru -Wait -RedirectStandardOutput $testOut -RedirectStandardError $testErr
Write-Host "TEST_EXIT_CODE=$($test.ExitCode)"
Get-Content -LiteralPath $testErr -Tail 6
if ($test.ExitCode -ne 0) { throw "TESTS_FAILED: read $testErr" }

$running = @(Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" | Where-Object {
    $_.CommandLine -and $_.CommandLine -match "(hermes_bridge_v1_verified.py.*--poll|hermes_bridge_supervisor_v1.py.*--poll)"
})
if ($running.Count -gt 0) {
    Write-Host "EXISTING_BRIDGE_ACTIVE=$($running.Count); no new process started"
    Write-Host "PRODUCTION=HOLD"
    return
}

Write-Host "=== ONE VERIFIED SCAN ==="
$scanOut = Join-Path $folder "scan.stdout.log"
$scanErr = Join-Path $folder "scan.stderr.log"
$scanArgs = @("-I", "-B", "-S", "`"$supervisor`"", "--worker", "`"$worker`"")
$scan = Start-Process -FilePath $python -ArgumentList $scanArgs -PassThru -Wait -RedirectStandardOutput $scanOut -RedirectStandardError $scanErr
Get-Content -LiteralPath $scanOut -Tail 3
if ($scan.ExitCode -ne 0) { throw "FIRST_SCAN_FAILED: $scanErr" }
Write-Host "SCAN_VERIFIED=PASS"

if ($Poll) {
    Write-Host "=== POLLING ENABLED (OPT-IN) ==="
    $outLog = Join-Path $folder "supervisor.stdout.log"
    $errLog = Join-Path $folder "supervisor.stderr.log"
    $argsPoll = @("-I", "-B", "-S", "`"$supervisor`"", "--worker", "`"$worker`"", "--poll", "--interval", "30")
    $process = Start-Process -FilePath $python -ArgumentList $argsPoll -PassThru -RedirectStandardOutput $outLog -RedirectStandardError $errLog
    Write-Host "SUPERVISOR_PID=$($process.Id)"
    Write-Host "STATUS_FILE=$(Join-Path $folder 'status.json')"
}
Write-Host "G0=NO-GO; G-CODE=NO-GO; G1=NO-GO; PRODUCTION=HOLD"
