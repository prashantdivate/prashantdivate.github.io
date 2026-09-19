param(
  [int]$Port = 1313,
  [string]$Bind = "127.0.0.1",
  [switch]$Drafts
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$Version = (Get-Content -Raw (Join-Path $Root ".hugo-version")).Trim()
$LocalHugo = Join-Path $Root ".tools\hugo-$Version\hugo.exe"

if (Test-Path $LocalHugo) {
  $Hugo = $LocalHugo
} else {
  $Command = Get-Command hugo -ErrorAction SilentlyContinue
  if (-not $Command) {
    throw "Hugo $Version was not found. Install Hugo or place it at $LocalHugo."
  }
  $Hugo = $Command.Source
}

$BaseUrl = "http://${Bind}:$Port/"
$Args = @("server", "--bind", $Bind, "--baseURL", $BaseUrl, "--port", "$Port", "--disableFastRender")
if ($Drafts) {
  $Args += "-D"
}

Write-Host "Serving Edge Systems Lab at $BaseUrl"
& $Hugo @Args
