# LOCAL/READ-ONLY INFORMATION ONLY - no installation, credentials or configuration writes.
# To avoid publishing private paths, this script returns executable names and Boolean presence.
$names = @('hermes','kilo','opencode','ollama','python','docker')
foreach ($name in $names) {
    [pscustomobject]@{ Tool = $name; Installed = [bool](Get-Command $name -ErrorAction SilentlyContinue) }
}
$ollama = Get-Command 'ollama' -ErrorAction SilentlyContinue
if ($null -ne $ollama) {
    Write-Output '=== Locally installed model identifiers ==='
    & $ollama.Source list
} else {
    Write-Output 'Ollama is not in PATH; no installation attempted.'
}
Write-Output '=== Local Ollama port only (no remote connection) ==='
try {
    $client = New-Object System.Net.Sockets.TcpClient
    $result = $client.BeginConnect('127.0.0.1', 11434, $null, $null)
    $connected = $result.AsyncWaitHandle.WaitOne(1000, $false)
    if ($connected) { try { $client.EndConnect($result) } catch { $connected = $false } }
    $client.Close()
    [pscustomobject]@{ LocalOllamaPort = 11434; Listening = [bool]$connected }
} catch {
    [pscustomobject]@{ LocalOllamaPort = 11434; Listening = $false }
}
