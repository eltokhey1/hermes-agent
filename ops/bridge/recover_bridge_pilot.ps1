param([switch]$Recover)
# Read-only diagnostics by default. -Recover starts only the existing pinned, AST-only supervisor.
$ErrorActionPreference = 'Stop'
$folder = Join-Path $env:LOCALAPPDATA 'HermesBridgePilot'
$state = Join-Path $folder 'status.json'
$worker = Join-Path $folder 'hermes_bridge_v1.py'
$supervisor = Join-Path $folder 'hermes_bridge_supervisor_v1.py'
$workerHash = 'f85bf5021fa2e05fc06abb52502932d09952a19fb0c1fcf6f83106158ac4278f'
$supervisorHash = 'e5e861db8a73811f7621706431e58a7e9b5547b90232652235d83811bbdd0d65'

Write-Host 'PRODUCTION=HOLD'
Write-Host 'G0=NO-GO G-CODE=NO-GO G1=NO-GO'

if (Test-Path -LiteralPath $state -PathType Leaf) {
    try {
        $snapshot = Get-Content -LiteralPath $state -Raw | ConvertFrom-Json
        Write-Host "LOCAL_LAST_STATE=$($snapshot.state)"
        Write-Host "LOCAL_LAST_SCAN=$($snapshot.timestamp_utc)"
        Write-Host "LOCAL_LAST_RESULT=$($snapshot.last_scan)"
        $last = [DateTimeOffset]::Parse($snapshot.timestamp_utc)
        $age = [math]::Round(([DateTimeOffset]::UtcNow - $last).TotalSeconds)
        Write-Host "STATUS_AGE_SECONDS=$age"
    } catch {
        Write-Host 'LOCAL_STATUS=INVALID_OR_UNREADABLE'
    }
} else {
    Write-Host 'LOCAL_STATUS=NOT_FOUND'
}

$active = @(Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" | Where-Object {
    $_.CommandLine -and (
        ($_.CommandLine -match 'hermes_bridge_supervisor_v1\.py' -and $_.CommandLine -match '--poll') -or
        ($_.CommandLine -match 'hermes_bridge_v1_verified\.py' -and $_.CommandLine -match '--poll')
    )
})
Write-Host "ACTIVE_BRIDGE_PROCESSES=$($active.Count)"
$active | Select-Object ProcessId,ParentProcessId,CreationDate | Format-Table -AutoSize

foreach ($name in @('supervisor.stderr.log','supervisor.stdout.log')) {
    $log = Join-Path $folder $name
    if (Test-Path -LiteralPath $log -PathType Leaf) {
        Write-Host "=== $name ==="
        Get-Content -LiteralPath $log -Tail 8
    }
}

if ($active.Count -gt 0) {
    Write-Host 'BRIDGE_PROCESS=ACTIVE_NOT_HEALTH_PROOF'
    if ($age -gt 120) { Write-Host 'WARNING=LAST_SUPERVISOR_STATUS_STALE' }
    exit 0
}
if (-not $Recover) {
    Write-Host 'BRIDGE_PROCESS=STOPPED; OPTIONAL_RECOVERY_REQUIRES_-Recover'
    exit 3
}

foreach ($pair in @(@($worker, $workerHash), @($supervisor, $supervisorHash))) {
    $path, $hash = $pair
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "PINNED_FILE_MISSING: $path" }
    $actual = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $hash) { throw "PINNED_FILE_HASH_MISMATCH: $path" }
}

$python = (Get-Command python -ErrorAction Stop).Source
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$stdout = Join-Path $folder "recovery_$stamp.stdout.log"
$stderr = Join-Path $folder "recovery_$stamp.stderr.log"
$argsText = '-I -B -S "' + $supervisor + '" --worker "' + $worker + '" --poll --interval 30'
$process = Start-Process -FilePath $python -ArgumentList $argsText -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
Start-Sleep -Seconds 3
$process.Refresh()
if ($process.HasExited) {
    Write-Host "RECOVERY_FAILED_EXIT=$($process.ExitCode)"
    if (Test-Path $stderr) { Get-Content $stderr -Tail 20 }
    exit 5
}
Write-Host "RECOVERY_PROCESS_STARTED_PID=$($process.Id)"
Write-Host 'RECOVERY_HEALTH=UNVERIFIED_UNTIL_SUCCESSFUL_SCAN'
Write-Host "RECOVERY_STDOUT=$stdout"
Write-Host "RECOVERY_STDERR=$stderr"
