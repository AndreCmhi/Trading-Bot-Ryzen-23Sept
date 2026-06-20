param(
    [string]$StateFile = ""
)

$ErrorActionPreference = 'Stop'
$Repo = Split-Path -Parent $MyInvocation.MyCommand.Path
if ([string]::IsNullOrWhiteSpace($StateFile)) { $StateFile = Join-Path $Repo 'watch_no_new_position_30m_state.json' }
$TradesFile = Join-Path $Repo 'trades.json'
$SettingsFile = Join-Path $Repo 'runtime_settings.json'
$LogFile = Join-Path $Repo 'watch_no_new_position_30m.log'

function Write-WatchLog {
    param([string]$Message)
    $stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    Add-Content -LiteralPath $LogFile -Value ("[{0}] {1}" -f $stamp, $Message)
}

function Get-Trades {
    if (-not (Test-Path -LiteralPath $TradesFile)) { return @() }
    try {
        $raw = Get-Content -LiteralPath $TradesFile -Raw
        if ([string]::IsNullOrWhiteSpace($raw)) { return @() }
        return @($raw | ConvertFrom-Json)
    } catch {
        Write-WatchLog "load_trades_error=$($_.Exception.Message)"
        return @()
    }
}

function Get-TradeTime {
    param($Trade)
    $value = [string]$Trade.time
    $parsed = [datetime]::MinValue
    if ([datetime]::TryParseExact($value, 'yyyy-MM-dd HH:mm:ss', $null, [System.Globalization.DateTimeStyles]::None, [ref]$parsed)) { return $parsed }
    if ([datetime]::TryParse($value, [ref]$parsed)) { return $parsed }
    return [datetime]::MinValue
}

function Apply-LooserStrategy {
    $settings = Get-Content -LiteralPath $SettingsFile -Raw | ConvertFrom-Json
    $settings.strategy_mode = 'AGGRESSIVE'
    $settings.min_score = 6
    $settings.max_open_positions = 4
    $settings.active_margin_balance_percent = 4.0
    $settings.high_confidence_only = $false
    $settings.high_confidence_threshold = 0.58
    $settings.min_adx = 12
    $settings.min_volume_ratio = 0.5
    $settings.disable_pullback_filter = $true
    $settings.disable_trend_filter = $false
    $settings.trailing_trigger_roi_percent = 1.0
    $settings.trailing_callback_roi_percent = 0.28
    $settings.fast_trailing_trigger_roi_percent = 0.5
    $settings.fast_trailing_callback_roi_percent = 0.16
    $settings | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $SettingsFile -Encoding utf8
    Write-WatchLog 'strategy_changed=AGGRESSIVE min_score=6 max_open_positions=4 min_adx=12 min_volume_ratio=0.5 disable_pullback_filter=true'
}

function Restart-Bot {
    $procs = Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -like '*app.py*' }
    foreach ($proc in $procs) {
        try { Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue } catch {}
    }
    Start-Sleep -Seconds 3
    Start-Process -FilePath (Join-Path $Repo 'run_background.bat') -WorkingDirectory $Repo -WindowStyle Hidden
    Write-WatchLog 'bot_restarted=true'
}

if (-not (Test-Path -LiteralPath $StateFile)) { throw "state file tidak ditemukan: $StateFile" }
$state = Get-Content -LiteralPath $StateFile -Raw | ConvertFrom-Json
$startedAt = [datetime]::Parse([string]$state.started_at)

$openTrades = @(Get-Trades | Where-Object { $_.status -eq 'OPEN' })
$newOpenTrades = @($openTrades | Where-Object { (Get-TradeTime $_) -ge $startedAt })

if ($newOpenTrades.Count -gt 0) {
    $symbols = ($newOpenTrades | ForEach-Object { $_.symbol }) -join ','
    Write-WatchLog ("new_open_found count={0} symbols={1} no_strategy_change" -f $newOpenTrades.Count, $symbols)
    exit 0
}

Write-WatchLog ("no_new_open_after_30m current_open={0} applying_strategy_change" -f $openTrades.Count)
Apply-LooserStrategy
Restart-Bot
