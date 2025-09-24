#!/usr/bin/env pwsh
param(
    [switch] $Help,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $ExtraArgs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Info {
    param([string]$Message)
    Write-Host "[victoria-install] $Message"
}

function Show-Help {
    Write-Host @'
Usage: install_victoria.ps1

This helper validates Podman, prepares the shared Victoria workspace, and
installs a reusable `victoria` command in your PowerShell profile.
'@
}

if ($Help) {
    Show-Help
    exit 0
}

if ($null -eq $ExtraArgs) {
    $ExtraArgs = @()
}

if ($ExtraArgs.Count -gt 0) {
    Write-Error "This script does not accept arguments."
    Show-Help
    exit 1
}

if (-not (Get-Command podman -ErrorAction SilentlyContinue)) {
    Write-Error "Podman is not installed or not on PATH. Install Podman from https://podman.io and rerun this script."
}

$podmanVersion = (& podman --version) -split "`n" | Select-Object -First 1
Write-Info "Podman detected: $podmanVersion"

try {
    & podman info | Out-Null
} catch {
    Write-Info "Podman is installed but not ready. On Windows or macOS, run 'podman machine init' (first time only) and 'podman machine start' before launching Victoria."
}

$workspace = Join-Path $HOME 'Victoria'
if (-not (Test-Path $workspace)) {
    New-Item -ItemType Directory -Path $workspace -Force | Out-Null
}
Write-Info "Ensured shared workspace exists at $workspace"

$arch = $null
try {
    $arch = & podman info --format '{{.Host.Arch}}'
    if (-not [string]::IsNullOrWhiteSpace($arch)) {
        Write-Info "Detected Podman host architecture via podman info: $arch"
    }
} catch {
    $arch = $null
}

if ([string]::IsNullOrWhiteSpace($arch)) {
    $arch = [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture.ToString()
    Write-Info "Using .NET fallback for architecture detection: $arch"
}

switch ($arch.ToLowerInvariant()) {
    'arm64' { $imageTag = 'latest-arm64' }
    'aarch64' { $imageTag = 'latest-arm64' }
    'x86_64' { $imageTag = 'latest' }
    'amd64' { $imageTag = 'latest' }
    default {
        Write-Info "Unknown architecture '$arch'; defaulting to multi-arch 'latest' tag."
        $imageTag = 'latest'
    }
}
$image = "ghcr.io/elcanotek/victoria-terminal:$imageTag"
Write-Info "Using container image $image"

$profilePath = $PROFILE

$profileDir = Split-Path $profilePath -Parent
if (-not (Test-Path $profileDir)) {
    New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
}
if (-not (Test-Path $profilePath)) {
    New-Item -ItemType File -Path $profilePath -Force | Out-Null
}
Write-Info "Updating PowerShell profile at $profilePath"

$startMarker = '# >>> victoria-terminal helper >>>'
$endMarker = '# <<< victoria-terminal helper <<<'

$content = Get-Content -Path $profilePath -Raw -ErrorAction SilentlyContinue
if ($null -ne $content) {
    $pattern = [System.Text.RegularExpressions.Regex]::Escape($startMarker) + '.*?' + [System.Text.RegularExpressions.Regex]::Escape($endMarker)
    $newContent = [System.Text.RegularExpressions.Regex]::Replace($content, $pattern, '', 'Singleline')
    if ($newContent -ne $content) {
        Set-Content -Path $profilePath -Value $newContent
    }
}

$functionBlockLines = @(
    $startMarker,
    '',
    'function Invoke-Victoria {',
    '    param(',
    '        [Parameter(ValueFromRemainingArguments = $true)]',
    '        [string[]] $Args',
    '    )',
    "    & podman pull $image",
    '    if ($LASTEXITCODE -ne 0) {',
    "        Write-Warning `"Victoria setup: unable to pull $image. Make sure Podman is running (start 'podman machine' if applicable).`"",
    '        return',
    '    }',
    '    & podman run --rm -it `',
    '        --userns=keep-id `',
    '        --security-opt=no-new-privileges `',
    '        --cap-drop=all `',
    '        -e VICTORIA_HOME=/workspace/Victoria `',
    '        -v `"$env:USERPROFILE/Victoria:/workspace/Victoria`" `',
    "        $image @Args",
    '}',
    'Set-Alias victoria Invoke-Victoria',
    $endMarker
)
$functionBlock = ($functionBlockLines -join [Environment]::NewLine) + [Environment]::NewLine
Add-Content -Path $profilePath -Value $functionBlock

Write-Info "Added 'victoria' alias to $profilePath"

Write-Info "Pulling the latest container image (this may take a moment)..."
& podman pull $image
if ($LASTEXITCODE -ne 0) {
    Write-Info "Pull failed. Start Podman (or run 'podman machine start') and launch Victoria later with: victoria"
}

Write-Info "All set! Reload PowerShell (or run '. $profilePath') and start Victoria with: victoria"
