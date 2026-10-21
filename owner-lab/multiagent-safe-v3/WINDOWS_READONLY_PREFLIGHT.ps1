# Hermes owner Windows inventory v2 — read-only, JSON-only, Windows PowerShell 5.1 compatible.
# Do not output profiles, absolute paths, environment values, secrets, hostnames, or file contents.
# Running this file does NOT attest backup restore, ACL denial, approvals or P1 acceptance.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Test-HermesFile {
    param([string]$Path)
    try { return [bool](Test-Path -LiteralPath $Path -PathType Leaf -ErrorAction Stop) }
    catch { return $false }
}

function Test-HermesDirectory {
    param([string]$Path)
    try { return [bool](Test-Path -LiteralPath $Path -PathType Container -ErrorAction Stop) }
    catch { return $false }
}

function Test-HermesTool {
    param([string]$Name)
    try { return [bool](Get-Command -Name $Name -ErrorAction SilentlyContinue) }
    catch { return $false }
}

$tools = [ordered]@{}
foreach ($name in @('hermes', 'kilo', 'opencode', 'ollama', 'python', 'docker')) {
    $tools[$name] = Test-HermesTool -Name $name
}

$homeWasSpecified = -not [string]::IsNullOrWhiteSpace($env:HERMES_HOME)
$profileRoot = if ($homeWasSpecified) {
    [Environment]::ExpandEnvironmentVariables($env:HERMES_HOME)
} else {
    Join-Path -Path $env:USERPROFILE -ChildPath '.hermes'
}

$portListening = $false
$socket = $null
$waitHandle = $null
try {
    $socket = New-Object System.Net.Sockets.TcpClient
    $pending = $socket.BeginConnect('127.0.0.1', 11434, $null, $null)
    $waitHandle = $pending.AsyncWaitHandle
    if ($waitHandle.WaitOne(600, $false)) {
        try { $socket.EndConnect($pending); $portListening = $socket.Connected }
        catch { $portListening = $false }
    }
} catch {
    $portListening = $false
} finally {
    if ($null -ne $waitHandle) { $waitHandle.Close() }
    if ($null -ne $socket) { $socket.Close() }
}

# A listening port may belong to a different process: this does not establish Ollama identity.
# A backup directory is NOT evidence of a protected, successfully restored backup.
$receipt = [ordered]@{
    schema_version = 2
    audit_kind = 'OWNER_WINDOWS_P0_READ_ONLY_INVENTORY'
    collected_at_utc = [DateTimeOffset]::UtcNow.ToString('o')
    collection_mode = 'READ_ONLY_NO_INSTALL_NO_CREDENTIAL_ACCESS'
    tools_found = $tools
    profile_markers = [ordered]@{
        hermes_home_env_set = [bool]$homeWasSpecified
        home_directory_present = Test-HermesDirectory -Path $profileRoot
        config_yaml_present = Test-HermesFile -Path (Join-Path $profileRoot 'config.yaml')
        state_db_present = Test-HermesFile -Path (Join-Path $profileRoot 'state.db')
        backup_directory_present = Test-HermesDirectory -Path (Join-Path $profileRoot 'backups')
    }
    local_loopback = [ordered]@{
        port_11434_listening = [bool]$portListening
        process_identity_verified = $false
        models_verified = $false
    }
    acceptance = [ordered]@{
        protected_backup_and_isolated_restore = 'NOT_TESTED'
        windows_acl_write_deny = 'NOT_TESTED'
        secrets_redaction_and_isolation = 'NOT_TESTED'
        independent_ledger_anchor = 'NOT_TESTED'
        authenticated_human_approval = 'NOT_TESTED'
        real_p1_crash_recovery = 'NOT_TESTED'
        local_coder_end_to_end = 'NOT_TESTED'
    }
    production_ready = $false
}
$receipt | ConvertTo-Json -Depth 8 -Compress
