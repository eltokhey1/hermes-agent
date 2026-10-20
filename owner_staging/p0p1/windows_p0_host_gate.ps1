#requires -Version 5.1
<#
Hermes P0 read-only Windows host gate. Never starts Hermes, changes configuration,
collects secrets, modifies ACLs, extracts archives or declares production ready.
#>
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Emit-Safe([string]$status, [string]$stage) {
    [pscustomobject]@{
        schema='hermes.p0.windows.readonly.v1'
        status=$status
        stage=$stage
        G0='NO-GO'
        G_CODE='NO-GO'
        G1='NO-GO'
        production='HOLD'
        host_acceptance_verified=$false
    } | ConvertTo-Json -Depth 5
}

try {
    if (-not $env:LOCALAPPDATA -or -not $env:USERPROFILE) {
        Emit-Safe 'SAFE_STOP' 'MISSING_WINDOWS_CONTEXT'
        exit 2
    }
    $homeDir = Join-Path $env:LOCALAPPDATA 'hermes'
    $backupDir = Join-Path $env:USERPROFILE 'Hermes_Private_Backups'
    $nativeRepo = Join-Path $homeDir 'hermes-agent'
    $pending = Join-Path $homeDir 'pending_messages'
    $config = Join-Path $homeDir 'config.yaml'
    $expected = @(
        @{label='development_legacy_partial';file='Hermes_P0_20261019T233125Z.tar.gz.gpg';sha='4e00f7e30b9c5a9b4f62bf27cbf83a259a1beab163c01950c3741ab14fdef369'},
        @{label='native_critical_partial';file='Hermes_Critical_V3_20261020T010946Z.tar.gz.gpg';sha='e2d139900db2b0841ff63e5f6bd2bef3b039732e72f014f27e7dad5ae97da2ec'}
    )
    $backupProof = @()
    foreach($item in $expected) {
        $result='MISSING'
        $file=Join-Path $backupDir $item.file
        try {
            $f=Get-Item -LiteralPath $file -Force -ErrorAction Stop
            if (($f.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                $result='LINK_REFUSED'
            } elseif(-not $f.PSIsContainer) {
                $observed=(Get-FileHash -LiteralPath $file -Algorithm SHA256 -ErrorAction Stop).Hash.ToLowerInvariant()
                $result=if ($observed -eq $item.sha) {'SHA256_MATCH'} else {'SHA256_MISMATCH'}
            } else { $result='NOT_REGULAR_FILE' }
        } catch [System.Management.Automation.ItemNotFoundException] {
            $result='MISSING'
        } catch { $result='READ_FAILED' }
        $backupProof+=@{type=$item.label;status=$result}
    }
    $pendingStatus='ABSENT_OR_NOT_VISIBLE'
    try {
        $folder=Get-Item -LiteralPath $pending -Force -ErrorAction Stop
        if (($folder.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            $pendingStatus='LINK_REFUSED'
        } elseif($folder.PSIsContainer) {
            # Check listing only. Never read contents or alter permissions.
            Get-ChildItem -LiteralPath $pending -Force -ErrorAction Stop | Select-Object -First 1 | Out-Null
            $pendingStatus='LISTABLE_NOT_BACKED_UP'
        } else { $pendingStatus='NOT_DIRECTORY' }
    } catch [System.UnauthorizedAccessException] {
        $pendingStatus='ACCESS_DENIED'
    } catch { $pendingStatus='UNVERIFIED_OR_ACCESS_DENIED' }
    $dockerStatus='UNAVAILABLE'
    $dockerVersion=$null
    try {
        $dockerCmd=Get-Command docker -ErrorAction Stop
        if($dockerCmd) {
            $dockerInfo = & docker info --format '{{.ServerVersion}}' 2>$null
            if($LASTEXITCODE -eq 0 -and $dockerInfo) {
                $dockerStatus='ENGINE_REACHABLE_NOT_ISOLATION_PROOF'
                $dockerVersion=($dockerInfo | Select-Object -First 1).ToString().Trim()
            }
        }
    } catch { $dockerStatus='UNAVAILABLE' }
    $repoStatus='UNKNOWN'
    $repoHead=$null
    try {
        if(Test-Path -LiteralPath (Join-Path $nativeRepo '.git') -PathType Container) {
            $headOut = & git -C $nativeRepo rev-parse HEAD 2>$null
            if($LASTEXITCODE -eq 0 -and $headOut -match '^[a-f0-9]{40}$') {
                $repoStatus='LOCAL_CHECKOUT_READABLE_NOT_ACCEPTED'
                $repoHead=($headOut | Select-Object -First 1).Trim()
            }
        }
    } catch { $repoStatus='UNKNOWN' }
    $configStatus=if (Test-Path -LiteralPath $config -PathType Leaf) {'EXISTS_NOT_EFFECTIVE_RUNTIME_PROOF'} else {'UNAVAILABLE'}
    $markerStatuses=@()
    foreach($marker in @((Join-Path $homeDir 'ESTOP'),(Join-Path (Join-Path $env:USERPROFILE '.hermes') 'ESTOP'))) {
        $mark='NOT_FOUND_OR_NOT_VISIBLE'
        try {
            # Explicit stat() equivalent; do not trust pathlib.exists on 3.14.
            $stat=Get-Item -LiteralPath $marker -Force -ErrorAction Stop
            if($stat) {$mark='MARKER_PRESENT_NEW_WORK_ONLY'}
        } catch [System.UnauthorizedAccessException] { $mark='INACCESSIBLE_TREAT_AS_HOLD' }
          catch { $mark='UNVERIFIED_TREAT_AS_HOLD' }
        $markerStatuses += $mark
    }
    $result=[ordered]@{
        schema='hermes.p0.windows.readonly.v1'
        status='EVIDENCE_INSPECTED_NOT_ACCEPTED'
        backups=$backupProof
        pending_messages=$pendingStatus
        docker_engine=$dockerStatus
        docker_version=$dockerVersion
        local_repo=$repoStatus
        local_head=$repoHead
        native_config=$configStatus
        estop_markers=$markerStatuses
        native_full_backup_verified=$false
        functional_restore_verified=$false
        estop_inflight_verified=$false
        hermes_docker_runtime_isolation_verified=$false
        estop_patch_integrated_on_host_verified=$false
        independent_acceptance=$false
        notes=@('Snapshot-only: partial archives do not cover native installation', 'No secrets or config contents printed', 'No Windows changes performed')
        G0='NO-GO';G_CODE='NO-GO';G1='NO-GO';production='HOLD'
    }
    $result | ConvertTo-Json -Depth 8
} catch {
    Emit-Safe 'SAFE_STOP' 'UNEXPECTED_READONLY_FAILURE'
    exit 2
}
