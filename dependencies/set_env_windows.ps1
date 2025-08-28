Write-Host "Victoria environment variable setup"

$openRouter = Read-Host "Enter your OPENROUTER_API_KEY"
[Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY", $openRouter, "User")
Write-Host "OPENROUTER_API_KEY set."

$ans = Read-Host "Configure Snowflake variables? (y/N)"
if ($ans -match '^(y|Y)$') {
    $acct = Read-Host "SNOWFLAKE_ACCOUNT"
    $user = Read-Host "SNOWFLAKE_USER"
    $pass = Read-Host "SNOWFLAKE_PASSWORD"
    $wh = Read-Host "SNOWFLAKE_WAREHOUSE"
    $role = Read-Host "SNOWFLAKE_ROLE"
    [Environment]::SetEnvironmentVariable("SNOWFLAKE_ACCOUNT", $acct, "User")
    [Environment]::SetEnvironmentVariable("SNOWFLAKE_USER", $user, "User")
    [Environment]::SetEnvironmentVariable("SNOWFLAKE_PASSWORD", $pass, "User")
    [Environment]::SetEnvironmentVariable("SNOWFLAKE_WAREHOUSE", $wh, "User")
    [Environment]::SetEnvironmentVariable("SNOWFLAKE_ROLE", $role, "User")
    Write-Host "Snowflake variables set."
}

Write-Host "Done. Restart PowerShell to use the new variables."
