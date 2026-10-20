#requires -Version 5.1
<#
Hermes P0 - local AI coding preflight (Windows PowerShell 5.1+).
Read-only inspection of tools, editor extensions and Ollama's loopback model list.
Does NOT run agents, install software, download models, edit credentials or touch Hermes state.
The only file write is a sanitized JSON report under %TEMP%, unless -NoReport is used.
#>
[CmdletBinding()]
param([switch]$NoReport)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Has-Command([string]$name) {
    return [bool](Get-Command -Name $name -ErrorAction SilentlyContinue)
}

function Has-KiloExtension([string]$extensionRoot) {
    if (-not (Test-Path -LiteralPath $extensionRoot -PathType Container)) {
        return $false
    }
    try {
        $hit = Get-ChildItem -LiteralPath $extensionRoot -Directory -ErrorAction Stop |
            Where-Object { $_.Name -match '(?i)(^|[.-])kilocode([.-]|$)|kilo-org' } |
            Select-Object -First 1
        return [bool]$hit
    } catch {
        return $false
    }
}

$ollamaCli = Has-Command 'ollama'
$kiloCli = Has-Command 'kilo'
$openCodeCli = Has-Command 'opencode'
$cursorCli = Has-Command 'cursor'
$codeCli = Has-Command 'code'

$userHome = $env:USERPROFILE
$cursorKilo = $false
$vsCodeKilo = $false
if (-not [string]::IsNullOrWhiteSpace($userHome)) {
    $cursorKilo = Has-KiloExtension (Join-Path $userHome '.cursor\extensions')
    $vsCodeKilo = Has-KiloExtension (Join-Path $userHome '.vscode\extensions')
}

$ollamaReachable = $false
$localModels = @()
$ollamaError = 'LOCAL_SERVICE_NOT_REACHABLE'
try {
    # Deliberately use ONLY IPv4 loopback, never OLLAMA_HOST or remote endpoints.
    $apiResult = Invoke-RestMethod -Method Get -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 3 -ErrorAction Stop
    $ollamaReachable = $true
    $ollamaError = 'NONE'
    if ($null -ne $apiResult.models) {
        $localModels = @($apiResult.models | ForEach-Object { [string]$_.name } |
            Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    }
}
catch {
    # Do not emit the error text (may contain machine-specific information).
    $ollamaError = 'LOCAL_SERVICE_NOT_REACHABLE_OR_INVALID_RESPONSE'
}

$kiloDetected = $kiloCli -or $cursorKilo -or $vsCodeKilo
$next = 'VERIFY_KILO_INSTALLATION'
if (-not $ollamaCli -and -not $ollamaReachable) {
    $next = 'OLLAMA_NOT_DETECTED_REQUEST_INSTALL_APPROVAL'
}
elseif (-not $ollamaReachable) {
    $next = 'START_OR_DIAGNOSE_OLLAMA_LOCALLY'
}
elseif ($localModels.Count -eq 0) {
    $next = 'NO_LOCAL_MODELS_REQUEST_MODEL_DOWNLOAD_APPROVAL'
}
elseif ($kiloDetected) {
    $next = 'CONFIGURE_KILO_OLLAMA_PROVIDER_NO_API_KEY'
}
else {
    $next = 'INSTALL_OR_CONNECT_KILO_EXTENSION_WITH_APPROVAL'
}

$result = [ordered]@{
    schema = 'hermes.local_ai.preflight.v1'
    run_mode = 'READ_ONLY_TOOL_DISCOVERY'
    ollama_cli = $ollamaCli
    ollama_loopback_api = $ollamaReachable
    ollama_model_count = $localModels.Count
    ollama_model_names = $localModels
    ollama_api_status = $ollamaError
    kilo_cli = $kiloCli
    kilo_cursor_extension = $cursorKilo
    kilo_vscode_extension = $vsCodeKilo
    cursor_cli = $cursorCli
    vscode_cli = $codeCli
    opencode_cli = $openCodeCli
    kilo_detected = [bool]$kiloDetected
    local_ai_ready_for_configuration = [bool]($ollamaReachable -and $localModels.Count -gt 0 -and $kiloDetected)
    recommended_next_step = $next
    external_api_key_required_for_local_ollama = $false
    hermes_runtime_changed = $false
    hermes_host_acceptance_verified = $false
    G0 = 'NO-GO'
    production = 'HOLD'
}

$json = $result | ConvertTo-Json -Depth 8

if (-not $NoReport) {
    $tempDir = $env:TEMP
    if ([string]::IsNullOrWhiteSpace($tempDir)) {
        throw 'TEMP_NOT_CONFIGURED'
    }
    $reportDir = Join-Path $tempDir 'Hermes_Local_AI_Diagnostic'
    New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
    $reportPath = Join-Path $reportDir 'preflight.json'
    [System.IO.File]::WriteAllText(
        $reportPath,
        $json + [Environment]::NewLine,
        (New-Object System.Text.UTF8Encoding($false))
    )
    Write-Host ('REPORT_SAVED: ' + $reportPath)
}
Write-Output $json
