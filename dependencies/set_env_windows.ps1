param(
    [switch]$SkipOpenRouter
)

Write-Host "Victoria environment variable setup"

$victoriaHome = "$env:USERPROFILE\Victoria"
$envFile = "$victoriaHome\.env"
if (-not (Test-Path $victoriaHome)) {
    New-Item -ItemType Directory -Path $victoriaHome | Out-Null
}

function Set-EnvVarInFile {
    param(
        [string]$key,
        [string]$value
    )
    # Remove existing key
    if (Test-Path $envFile) {
        (Get-Content $envFile) | Where-Object { $_ -notmatch "^$key=" } | Set-Content $envFile
    }
    # Add new key
    Add-Content -Path $envFile -Value "$key=`"$value`""
}

if (-not $SkipOpenRouter) {
    $openRouter = Read-Host "Enter your OPENROUTER_API_KEY (leave blank to skip)"
    if ($openRouter) {
        Set-EnvVarInFile "OPENROUTER_API_KEY" $openRouter
        Write-Host "OPENROUTER_API_KEY saved to $envFile"
    } else {
        Write-Host "Skipping OpenRouter API key configuration."
    }
} else {
    Write-Host "Skipping OpenRouter API key setup."
}

$ans = Read-Host "Configure Snowflake variables? (y/N)"
if ($ans -match '^(y|Y)$') {
    $acct = Read-Host "SNOWFLAKE_ACCOUNT"
    $user = Read-Host "SNOWFLAKE_USER"
    $pass = Read-Host "SNOWFLAKE_PASSWORD"
    $wh = Read-Host "SNOWFLAKE_WAREHOUSE"
    $role = Read-Host "SNOWFLAKE_ROLE"
    Set-EnvVarInFile "SNOWFLAKE_ACCOUNT" $acct
    Set-EnvVarInFile "SNOWFLAKE_USER" $user
    Set-EnvVarInFile "SNOWFLAKE_PASSWORD" $pass
    Set-EnvVarInFile "SNOWFLAKE_WAREHOUSE" $wh
    Set-EnvVarInFile "SNOWFLAKE_ROLE" $role
    Write-Host "Snowflake variables saved to $envFile"
}

Write-Host "Done. Environment variables are configured for Victoria."
