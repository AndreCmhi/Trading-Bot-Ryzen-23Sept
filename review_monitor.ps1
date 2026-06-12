param(
    [switch]$Once
)

$ErrorActionPreference = 'Stop'

$Repo = Split-Path -Parent $MyInvocation.MyCommand.Path
$BaseUrl = 'http://127.0.0.1:5000'
$OutLog = Join-Path $Repo 'review_30m.log'
$StateFile = Join-Path $Repo 'review_30m_latest.json'
$AlertFile = Join-Path $Repo 'review_30m_alerts.log'
$EnvFile = Join-Path $Repo '.env'

function Get-EnvValue {
    param(
        [string]$Name,
        [string]$Default
    )
    $value = [Environment]::GetEnvironmentVariable($Name)
    if ([string]::IsNullOrWhiteSpace($value)) { return $Default }
    return $value
}

$AlertTotalPnlLeq = [double](Get-EnvValue -Name 'REVIEW_ALERT_TOTAL_PNL_LEQ' -Default '-0.5')
$AlertRecentPnlLeq = [double](Get-EnvValue -Name 'REVIEW_ALERT_RECENT_PNL_LEQ' -Default '-0.25')
$AlertOpenPositionsGe = [int](Get-EnvValue -Name 'REVIEW_ALERT_OPEN_POSITIONS_GE' -Default '999999')

function Load-EnvFile {
    if (-not (Test-Path -LiteralPath $EnvFile)) { return }
    foreach ($raw in Get-Content -LiteralPath $EnvFile) {
        $line = $raw.Trim()
        if (-not $line -or $line.StartsWith('#') -or -not $line.Contains('=')) { continue }
        $parts = $line.Split('=', 2)
        $name = $parts[0].Trim()
        $value = $parts[1].Trim().Trim('"').Trim("'")
        if ($name) { [Environment]::SetEnvironmentVariable($name, $value) }
    }
}

function Get-CsrfToken {
    param([string]$Html)
    $match = [regex]::Match($Html, 'name="csrf_token" value="([^"]+)"')
    if (-not $match.Success) { throw 'CSRF token tidak ditemukan' }
    return $match.Groups[1].Value
}

function New-AppSession {
    $session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
    $loginPage = Invoke-WebRequest -Uri "$BaseUrl/login" -WebSession $session -UseBasicParsing -TimeoutSec 10
    $csrf = Get-CsrfToken -Html $loginPage.Content
    $body = @{
        username = [Environment]::GetEnvironmentVariable('APP_USERNAME')
        password = [Environment]::GetEnvironmentVariable('APP_PASSWORD')
        csrf_token = $csrf
        next = '/'
    }
    Invoke-WebRequest -Uri "$BaseUrl/login" -Method Post -WebSession $session -UseBasicParsing -TimeoutSec 10 -Body $body | Out-Null
    return $session
}

function Get-ErrorLines {
    $patterns = 'NameError|Traceback|LOAD TRADES ERROR|LOAD SETTINGS ERROR|Exception|CANDIDATE ERROR|monitor_error'
    $logFile = Join-Path $Repo 'out.log'
    if (-not (Test-Path -LiteralPath $logFile)) { return @() }
    return Get-Content -LiteralPath $logFile -Tail 200 | Where-Object { $_ -match $patterns } | Select-Object -Last 10
}

function Write-Alert {
    param([string]$Message)
    $stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    Add-Content -LiteralPath $AlertFile -Value ("[{0}] {1}" -f $stamp, $Message)
    Add-Content -LiteralPath $OutLog -Value ("[{0}] ALERT {1}" -f $stamp, $Message)
}

function Write-Review {
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $session = New-AppSession
    $snapshot = Invoke-WebRequest -Uri "$BaseUrl/api/dashboard_snapshot" -WebSession $session -UseBasicParsing -TimeoutSec 10 | Select-Object -ExpandProperty Content | ConvertFrom-Json
    $errors = @(Get-ErrorLines)

    $state = [pscustomobject]@{
        reviewed_at = $timestamp
        bot = $snapshot.bot_status.label
        running = [bool]$snapshot.bot_status.running
        open_positions = @($snapshot.open_positions).Count
        total_pnl = [double]$snapshot.stats.total_pnl
        winrate = [double]$snapshot.stats.winrate
        recent_pnl = [double]$snapshot.history_monitor.recent_pnl
        recent_winrate = [double]$snapshot.history_monitor.recent_winrate
        error_lines = $errors
    }

    $state | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $StateFile -Encoding utf8
    Add-Content -LiteralPath $OutLog -Value ("[{0}] bot={1} running={2} open={3} pnl={4} winrate={5}" -f $timestamp, $state.bot, $state.running, $state.open_positions, $state.total_pnl, $state.winrate)
    if ($errors.Count -gt 0) {
        Add-Content -LiteralPath $OutLog -Value ("[{0}] issues={1}" -f $timestamp, ($errors -join ' || '))
    }

    $alertReasons = @()
    if ($state.total_pnl -le $AlertTotalPnlLeq) { $alertReasons += "total_pnl=$($state.total_pnl) <= $AlertTotalPnlLeq" }
    if ($state.recent_pnl -le $AlertRecentPnlLeq) { $alertReasons += "recent_pnl=$($state.recent_pnl) <= $AlertRecentPnlLeq" }
    if ($state.open_positions -ge $AlertOpenPositionsGe) { $alertReasons += "open_positions=$($state.open_positions) >= $AlertOpenPositionsGe" }
    if ($errors.Count -gt 0) { $alertReasons += "runtime_errors=$($errors.Count)" }
    if ($alertReasons.Count -gt 0) { Write-Alert ("bot=$($state.bot) | " + ($alertReasons -join '; ')) }
}

Load-EnvFile
if (-not [Environment]::GetEnvironmentVariable('APP_USERNAME')) { [Environment]::SetEnvironmentVariable('APP_USERNAME', 'admin') }
if (-not [Environment]::GetEnvironmentVariable('APP_PASSWORD')) { throw 'APP_PASSWORD kosong. Isi .env dulu.' }

Add-Content -LiteralPath $OutLog -Value ("[{0}] monitor_started" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))

while ($true) {
    try {
        Write-Review
    } catch {
        Add-Content -LiteralPath $OutLog -Value ("[{0}] monitor_error={1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $_.Exception.Message)
    }

    if ($Once) {
        break
    }

    Start-Sleep -Seconds 1800
}



