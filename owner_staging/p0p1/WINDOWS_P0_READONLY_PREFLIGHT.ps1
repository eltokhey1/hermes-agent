# Hermes Open Builder — Windows P0-01 read-only inventory.
# Windows PowerShell 5.1-compatible. No downloads, installs, git fetch/checkout,
# service changes, privilege escalation, or production file changes.
# The only write is a redacted JSON receipt to the chosen directory (TEMP by default).
[CmdletBinding()]
param(
    [string]$RepoPath = '',
    [string]$OutputFile = '',
    [switch]$ProbeDocker,
    [string]$BackupDirectory = ''
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'
$stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
if ([string]::IsNullOrWhiteSpace($OutputFile)) {
    $OutputFile = Join-Path ([System.IO.Path]::GetTempPath()) ('Hermes_P0_Readonly_' + $stamp + '.json')
}

function Is-ToolPresent([string]$name) {
    return [bool](Get-Command -Name $name -CommandType Application -ErrorAction SilentlyContinue)
}

$receipt = [ordered]@{
    schema_version = 1
    project = 'Hermes Open Builder'
    scope = 'P0-01 inventory only'
    collected_utc = ([DateTime]::UtcNow.ToString('o'))
    windows = ($env:OS -eq 'Windows_NT')
    ps_version = $PSVersionTable.PSVersion.ToString()
    # Never collect account identifiers, usernames, paths, environment contents or secrets.
    git_on_path = (Is-ToolPresent 'git.exe')
    docker_on_path = (Is-ToolPresent 'docker.exe')
    wsl_on_path = (Is-ToolPresent 'wsl.exe')
    python_on_path = ((Is-ToolPresent 'python.exe') -or (Is-ToolPresent 'py.exe'))
    repo_detected = $false
    repo_head_sha = $null
    repo_tracked_dirty_count = $null
    repo_read_ok = $false
    docker_daemon_reachable = 'NOT_PROBED'
    backup_directory_present = 'NOT_PROVIDED'
    backup_functional_restore_verified = $false
    estop_isolation_verified = $false
    local_git_mutations = $false
    G0 = 'NO-GO'
    G_CODE = 'NO-GO'
    G1 = 'NO-GO'
    production = 'HOLD'
    acceptance = 'HOST_INVENTORY_ONLY_UNREVIEWED'
}

# A small, bounded list of likely paths; intentionally NO full-drive scan.
$folders = New-Object System.Collections.Generic.List[string]
if (-not [string]::IsNullOrWhiteSpace($RepoPath)) {
    [void]$folders.Add($RepoPath)
} else {
    [void]$folders.Add((Get-Location).Path)
    [void]$folders.Add((Join-Path $HOME 'hermes-agent'))
    [void]$folders.Add((Join-Path $HOME 'source\repos\hermes-agent'))
    [void]$folders.Add((Join-Path $HOME 'Documents\hermes-agent'))
    [void]$folders.Add((Join-Path $HOME 'Desktop\hermes-agent'))
}

# Always disable optional index locks and fsmonitor hooks; no repo hooks or external command execution.
if ($receipt.git_on_path) {
    $git = (Get-Command -Name git.exe -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1).Source
    $previousLocks = [Environment]::GetEnvironmentVariable('GIT_OPTIONAL_LOCKS', 'Process')
    [Environment]::SetEnvironmentVariable('GIT_OPTIONAL_LOCKS', '0', 'Process')
    try {
        foreach ($candidate in $folders) {
            if (-not (Test-Path -LiteralPath $candidate -PathType Container)) { continue }
            $inside = @(& $git -c core.fsmonitor=false -c core.hooksPath=NUL -C $candidate rev-parse --is-inside-work-tree 2>$null)
            if ($LASTEXITCODE -ne 0 -or $inside.Count -eq 0 -or $inside[0].Trim() -ne 'true') { continue }
            $receipt.repo_detected = $true
            $sha = @(& $git -c core.fsmonitor=false -c core.hooksPath=NUL -C $candidate rev-parse --verify HEAD 2>$null)
            if ($LASTEXITCODE -ne 0 -or $sha.Count -eq 0 -or $sha[0] -notmatch '^[0-9a-fA-F]{40}$') { break }
            $receipt.repo_head_sha = $sha[0]
            $dirty = @(& $git -c core.fsmonitor=false -c core.hooksPath=NUL -C $candidate status --porcelain=v1 --untracked-files=no 2>$null)
            if ($LASTEXITCODE -ne 0) { break }
            $receipt.repo_tracked_dirty_count = @($dirty | Where-Object { $_ -ne '' }).Count
            $receipt.repo_read_ok = $true
            break
        }
    } catch {
        # An inaccessible directory or Git error must not become a passing gate.
        $receipt.repo_read_ok = $false
    } finally {
        [Environment]::SetEnvironmentVariable('GIT_OPTIONAL_LOCKS', $previousLocks, 'Process')
    }
}

if ($ProbeDocker -and $receipt.docker_on_path) {
    try {
        $docker = (Get-Command -Name docker.exe -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1).Source
        $null = & $docker info --format '{{.ServerVersion}}' 2>$null
        $receipt.docker_daemon_reachable = ($LASTEXITCODE -eq 0)
    } catch {
        $receipt.docker_daemon_reachable = $false
    }
}

if (-not [string]::IsNullOrWhiteSpace($BackupDirectory)) {
    $receipt.backup_directory_present = (Test-Path -LiteralPath $BackupDirectory -PathType Container)
    # Mere existence NEVER proves encryption, integrity, or functional recovery.
}

if (-not $receipt.windows) {
    $receipt.acceptance = 'NOT_WINDOWS_NO_HOST_CLAIM'
}

$fullOut = [System.IO.Path]::GetFullPath($OutputFile)
$parent = [System.IO.Path]::GetDirectoryName($fullOut)
if (-not [System.IO.Directory]::Exists($parent)) {
    throw 'Output directory must exist. Will not create arbitrary directories.'
}
if ([System.IO.File]::Exists($fullOut)) {
    throw 'OutputFile already exists. Refusing overwrite.'
}
$json = ConvertTo-Json -InputObject $receipt -Depth 5
[System.IO.File]::WriteAllText($fullOut, $json + [Environment]::NewLine, (New-Object System.Text.UTF8Encoding($false)))
Write-Output $json
Write-Output '--- Receipt was saved locally. Its file path is intentionally omitted from the report. ---'
Write-Output '--- G0/G-CODE/G1: NO-GO; PRODUCTION: HOLD pending independent acceptance. ---'
