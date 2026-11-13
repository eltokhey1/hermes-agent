# Disposable GitHub-hosted Windows runner ONLY. Never run on owner machine.
# Creates one temporary non-admin test identity, checks that it cannot write
# a checkpoint owned by runneradmin/SYSTEM/Administrators, then removes it.
# This does NOT prove actual owner-device ACLs or a deployable trust boundary.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($env:GITHUB_ACTIONS -ne 'true' -or $env:RUNNER_OS -ne 'Windows' -or
    [string]::IsNullOrWhiteSpace($env:RUNNER_TEMP)) {
    throw 'HOSTED_WINDOWS_RUNNER_ONLY'
}
if ($env:RUNNER_ENVIRONMENT -and $env:RUNNER_ENVIRONMENT -ne 'github-hosted') {
    throw 'SELF_HOSTED_RUNNERS_FORBIDDEN'
}

$username = 'HermesAcl' + ([guid]::NewGuid().ToString('N').Substring(0, 9))
$root = Join-Path $env:RUNNER_TEMP ('hermes-research-acl-' + [guid]::NewGuid().ToString('N'))
$passwordText = ([guid]::NewGuid().ToString('N') + 'aZ9!')
$password = ConvertTo-SecureString -String $passwordText -AsPlainText -Force
$userCreated = $false
$rootCreated = $false
try {
    New-LocalUser -Name $username -Password $password -AccountNeverExpires -PasswordNeverExpires | Out-Null
    $userCreated = $true
    $null = New-Item -ItemType Directory -Path $root -Force
    $rootCreated = $true
    $checkpoint = Join-Path $root 'nonproduction-checkpoint.json'
    Set-Content -LiteralPath $checkpoint -Encoding UTF8 -NoNewline -Value '{"test":"readonly"}'
    $before = (Get-FileHash -Algorithm SHA256 -LiteralPath $checkpoint).Hash

    $acl = Get-Acl -LiteralPath $root
    $acl.SetAccessRuleProtection($true, $false)
    $currentSid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User
    $sids = @(
        $currentSid,
        (New-Object System.Security.Principal.SecurityIdentifier('S-1-5-18')),
        (New-Object System.Security.Principal.SecurityIdentifier('S-1-5-32-544'))
    )
    foreach ($sid in $sids) {
        $rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
            $sid,
            [System.Security.AccessControl.FileSystemRights]::FullControl,
            ([System.Security.AccessControl.InheritanceFlags]::ContainerInherit -bor
             [System.Security.AccessControl.InheritanceFlags]::ObjectInherit),
            [System.Security.AccessControl.PropagationFlags]::None,
            [System.Security.AccessControl.AccessControlType]::Allow
        )
        $null = $acl.AddAccessRule($rule)
    }
    Set-Acl -LiteralPath $root -AclObject $acl

    # The child is non-admin. No credentials are written to disk or logs.
    $literal = $checkpoint.Replace("'", "''")
    $command = @"
try {
  Set-Content -LiteralPath '$literal' -Value 'tampered' -ErrorAction Stop
  exit 3
} catch [System.UnauthorizedAccessException] {
  exit 17
} catch {
  exit 19
}
"@
    $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($command))
    $credential = New-Object System.Management.Automation.PSCredential(
        ($env:COMPUTERNAME + '\\' + $username), $password
    )
    $proc = Start-Process -FilePath 'powershell.exe' -Credential $credential -NoNewWindow -Wait -PassThru -ArgumentList @(
        '-NoProfile', '-NonInteractive', '-EncodedCommand', $encoded
    )
    $after = (Get-FileHash -Algorithm SHA256 -LiteralPath $checkpoint).Hash
    if ($after -ne $before) { throw 'ACL_TEST_CHECKPOINT_MODIFIED' }
    if ($proc.ExitCode -ne 17) {
        throw ('ACL_TEST_WRITE_DENY_UNPROVEN: child_exit=' + $proc.ExitCode)
    }
    Write-Output 'WINDOWS_DISPOSABLE_DISTINCT_PRINCIPAL_ACL_WRITE_DENY=PASS'
    Write-Output 'WINDOWS_HOSTED_RUNNER_ONLY=true'
    Write-Output 'OWNER_DEVICE_ACL=NOT_TESTED'
} finally {
    # Purge only the exact scratch identity/directory created by this job.
    if ($userCreated) {
        try { Remove-LocalUser -Name $username -ErrorAction Stop } catch {
            Write-Warning 'TEST_USER_CLEANUP_NEEDS_RUNNER_DISPOSAL'
        }
    }
    if ($rootCreated -and (Test-Path -LiteralPath $root)) {
        try { Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction Stop } catch {
            Write-Warning 'SCRATCH_CLEANUP_NEEDS_RUNNER_DISPOSAL'
        }
    }
}
