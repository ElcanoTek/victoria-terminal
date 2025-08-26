#Requires -Version 5.1
<#
.SYNOPSIS
  Victoria - AdTech Data Navigation (Windows PowerShell)

.DESCRIPTION
  Minimal launcher for Victoria + crush.
  - No dependency installer
  - No environment variable setup
  - Auto-detects Snowflake env; falls back to local if incomplete
  - Fetches VICTORIA.md via SSH clone (private repo)

.PARAMETER Local
  Force local-only mode (ignore Snowflake)

.PARAMETER SkipChecks
  Skip preflight checks (crush, git, OPENROUTER_API_KEY)

.NOTES
  Author: ElcanoTek
  Version: 3.1 (minimal + SSH for VICTORIA.md)
#>

param(
  [switch]$Local,
  [switch]$SkipChecks
)

# ---------- Constants ----------
$VictoriaRepoSsh = "git@github.com:ElcanoTek/victoria-main.git"
$VictoriaBranch  = "main"
$VictoriaFile    = "VICTORIA.md"

# ---------- Helpers ----------
function Write-Info    { param([string]$m) Write-Host $m -ForegroundColor Cyan }
function Write-Good    { param([string]$m) Write-Host $m -ForegroundColor Green }
function Write-Warn    { param([string]$m) Write-Host $m -ForegroundColor Yellow }
function Write-ErrorMsg{ param([string]$m) Write-Host $m -ForegroundColor Red }

function Test-Command { param([string]$Name)
  try { Get-Command $Name -ErrorAction Stop | Out-Null; $true } catch { $false }
}

function Test-SnowflakeEnv {
  $req = "SNOWFLAKE_ACCOUNT","SNOWFLAKE_USER","SNOWFLAKE_PASSWORD","SNOWFLAKE_WAREHOUSE","SNOWFLAKE_ROLE"
  $missing = @()
  foreach ($v in $req) {
    if (-not (Get-Item "env:$v" -ErrorAction SilentlyContinue)) { $missing += $v }
  }
  return $missing
}

function Generate-CrushConfig {
  param(
    [bool]$IncludeSnowflake,
    [string]$OutputFile = "crush.json"
  )
  try {
    if (-not (Test-Path "crush.template.json")) {
      Write-ErrorMsg "crush.template.json not found."
      return $false
    }
    $template = Get-Content "crush.template.json" -Raw

    if ($IncludeSnowflake) {
      if (-not (Test-Path "snowflake.mcp.json")) {
        Write-ErrorMsg "snowflake.mcp.json not found."
        return $false
      }
      $snowflake = Get-Content "snowflake.mcp.json" -Raw
      # Strip outer braces and indent
      $lines = ($snowflake -split "`n").Where({$_ -ne ""})
      if ($lines.Count -lt 2) { Write-ErrorMsg "snowflake.mcp.json is not valid JSON."; return $false }
      $core = $lines[1..($lines.Count-2)] | ForEach-Object { "    $_" }
      $snowflakeBlock = ",`n" + ($core -join "`n")
      $final = $template -replace '\{\{SNOWFLAKE_MCP\}\}', $snowflakeBlock
    } else {
      $final = $template -replace '\{\{SNOWFLAKE_MCP\}\}', ''
    }

    $final | Out-File -FilePath $OutputFile -Encoding UTF8
    return $true
  } catch {
    Write-ErrorMsg "Generate-CrushConfig: $($_.Exception.Message)"
    return $false
  }
}

function Ensure-VictoriaMd {
  # Fetch VICTORIA.md from private repo via SSH clone; silent if already present
  if (Test-Path $VictoriaFile) { return $true }

  if (-not (Test-Command "git")) {
    Write-ErrorMsg "Missing 'git'. Install Git for Windows and retry: https://git-scm.com/download/win"
    return $false
  }

  $tempDir = Join-Path $env:TEMP ("victoria_clone_{0}" -f (Get-Random))
  try {
    Write-Info "Cloning victoria-main (SSH)…"
    git clone --depth 1 --branch $VictoriaBranch $VictoriaRepoSsh $tempDir 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
      Write-ErrorMsg "Git clone failed. Ensure your SSH key can access GitHub."
      Write-Warn     "Test with: ssh -T git@github.com"
      return $false
    }

    $src = Join-Path $tempDir $VictoriaFile
    if (-not (Test-Path $src)) {
      Write-ErrorMsg "VICTORIA.md not found in repo."
      return $false
    }

    Copy-Item $src (Join-Path (Get-Location) $VictoriaFile) -Force
    Write-Good "VICTORIA.md downloaded."
    return $true
  } catch {
    Write-ErrorMsg "Ensure-VictoriaMd: $($_.Exception.Message)"
    return $false
  } finally {
    if (Test-Path $tempDir) { Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue }
  }
}

# ---------- Preflight ----------
if (-not $SkipChecks) {
  if (-not (Test-Command "crush")) {
    Write-ErrorMsg "Missing 'crush'. Install from https://github.com/charmbracelet/crush"
    exit 1
  }
  if (-not (Test-Command "git")) {
    Write-ErrorMsg "Missing 'git'. Install from https://git-scm.com/download/win"
    exit 1
  }
  if (-not (Get-Item env:OPENROUTER_API_KEY -ErrorAction SilentlyContinue)) {
    Write-ErrorMsg "OPENROUTER_API_KEY not set. Set it and re-run."
    Write-Host 'Example (persistent):' -ForegroundColor DarkGray
    Write-Host '[Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY","your_api_key_here","User")' -ForegroundColor DarkGray
    exit 1
  }
}

# Try to fetch VICTORIA.md (non-blocking failure)
Ensure-VictoriaMd | Out-Null

# Decide mode
$useSnowflake = $false
if (-not $Local) {
  $missing = Test-SnowflakeEnv
  if ($missing.Count -eq 0) {
    $useSnowflake = $true
    Write-Good "Snowflake environment detected."
  } else {
    Write-Warn ("Snowflake incomplete, missing: {0}. Falling back to local mode." -f ($missing -join ", "))
  }
} else {
  Write-Info "Local mode forced."
}

# Generate config
if ($useSnowflake) {
  Write-Info "Generating crush.json (with Snowflake)…"
  if (-not (Generate-CrushConfig -IncludeSnowflake:$true -OutputFile "crush.json")) { exit 1 }
} else {
  Write-Info "Generating crush.json (local only)…"
  if (-not (Generate-CrushConfig -IncludeSnowflake:$false -OutputFile "crush.json")) { exit 1 }
}

# Launch crush
try {
  Write-Info "Launching crush…"
  & crush
  $code = $LASTEXITCODE
  if ($code -ne 0) { Write-ErrorMsg "crush exited with code $code"; exit $code }
} catch {
  Write-ErrorMsg "Failed to launch crush: $($_.Exception.Message)"
  exit 1
}
