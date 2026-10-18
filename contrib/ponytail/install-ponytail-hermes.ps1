# Official Ponytail Hermes installer. Opt-in, pinned, no policy bypass.
param([switch]$AuditOnly,[switch]$InstallOnly)
$ErrorActionPreference='Stop'
$source='https://github.com/DietrichGebert/ponytail.git'
$pin='09c434ab73ca43761c5d8b0c5d341926c2fba710'
$target=Join-Path $HOME '.hermes\plugins\ponytail'
$parent=Split-Path -Parent $target
$stage=Join-Path $parent ("ponytail.stage."+$PID)
if(-not (Get-Command git -ErrorAction SilentlyContinue)){throw 'GIT_NOT_FOUND'}
if(-not (Get-Command hermes -ErrorAction SilentlyContinue)){throw 'HERMES_NOT_FOUND'}
if(Test-Path -LiteralPath $target){throw 'ALREADY_INSTALLED: refusing overwrite'}
if($AuditOnly){Write-Host 'READINESS_PASS: no changes made';return}
New-Item -ItemType Directory -Force -Path $parent | Out-Null
if(Test-Path -LiteralPath $stage){throw 'STAGING_CONFLICT'}
$moved=$false
try {
 & git clone --quiet --no-checkout $source $stage
 if($LASTEXITCODE -ne 0){throw 'GIT_CLONE_FAILED'}
 & git -C $stage checkout --quiet --detach $pin
 if($LASTEXITCODE -ne 0){throw 'PIN_UNAVAILABLE'}
 if((& git -C $stage rev-parse HEAD).Trim() -ne $pin){throw 'PIN_MISMATCH'}
 foreach($file in @('plugin.yaml','package.json','LICENSE','skills/ponytail/SKILL.md')){
   if(-not (Test-Path -LiteralPath (Join-Path $stage $file) -PathType Leaf)){throw "MISSING_FILE: $file"}
 }
 $package=Get-Content -LiteralPath (Join-Path $stage 'package.json') -Raw | ConvertFrom-Json
 if($package.name -ne '@dietrichgebert/ponytail' -or $package.version -ne '5.3.2'){throw 'UNEXPECTED_PACKAGE'}
 $plugin=Get-Content -LiteralPath (Join-Path $stage 'plugin.yaml') -Raw
 if($plugin -notmatch '(?m)^name:\s*ponytail\s*$' -or $plugin -notmatch '(?m)^version:\s*5\.3\.2\s*$'){throw 'UNEXPECTED_MANIFEST'}
 if(@(Get-ChildItem -LiteralPath $stage -Recurse -File | Where-Object { $_.Extension -in @('.exe','.dll') }).Count -gt 0){throw 'UNEXPECTED_BINARY'}
 Move-Item -LiteralPath $stage -Destination $target
 $moved=$true
 Write-Host 'SOURCE_VERIFIED_AND_INSTALLED=YES'
 if($InstallOnly){Write-Host 'ENABLED=NO. Review hooks; run hermes plugins enable ponytail';return}
 & hermes plugins enable ponytail
 if($LASTEXITCODE -ne 0){throw 'ENABLE_NOT_CONFIRMED'}
 Write-Host 'ENABLED=YES. Restart Hermes and test /ponytail-help.'
} finally {
 if(-not $moved -and (Test-Path -LiteralPath $stage)){Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue}
}