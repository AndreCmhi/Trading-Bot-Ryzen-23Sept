# Bot Evaluation Script
$BotDir = "C:\Users\Maria Oktavia\Documents\Trading-Bot-Ryzen"

$ErrorActionPreference = "Continue"
$logFile = Join-Path $BotDir "eval.log"
$tradesFile = Join-Path $BotDir "trades.json"
$errFile = Join-Path $BotDir "err.log"
$outFile = Join-Path $BotDir "out.log"

function Write-Log {
    param([string]$msg)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $logFile -Value "$timestamp - $msg"
    Write-Host "$timestamp - $msg"
}

# 1. Check bot process - cek Flask via HTTP + command line contains app.py
$botRunning = $false
$botProc = $null

# Method A: Cek Flask server via HTTP Ping
$result = $null
try {
    $result = Invoke-WebRequest -Uri "http://127.0.0.1:5000/login" -Method GET -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    if ($result.StatusCode -eq 200) { $botRunning = $true }
} catch { }

if ($botRunning) {
    $pythonProcs = Get-Process python -ErrorAction SilentlyContinue
    foreach ($proc in $pythonProcs) {
        try {
            $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $($proc.Id)" -ErrorAction SilentlyContinue).CommandLine
            if ($cmdLine -match "app\\.py") { $botProc = $proc; break }
        } catch { }
    }
    if (-not $botProc) {
        $checkProcs = @($pythonProcs | Where-Object { $_.WorkingSet64 -gt 10000000 })
        if ($checkProcs.Count -eq 1) { $botProc = $checkProcs[0] }
    }
}

if (-not $botRunning -or -not $botProc) {
    Write-Log "BOT DOWN - Restarting..."
    Start-Process python -ArgumentList "app.py" -WorkingDirectory $BotDir -WindowStyle Hidden
    Start-Sleep 8
    $retry = 0
    while ($retry -lt 3) {
        $retryRes = $null
        try { $retryRes = Invoke-WebRequest -Uri "http://127.0.0.1:5000/login" -Method GET -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop } catch { }
        if ($retryRes -and $retryRes.StatusCode -eq 200) { Write-Log "Bot restarted and reachable"; break }
        Start-Sleep 3
        $retry++
    }
    if ($retry -ge 3) { Write-Log "WARNING: Bot restart mungkin gagal" }
    exit 1
}

Write-Log "Bot running (PID: $($botProc.Id), Mem: $([math]::Round($botProc.WorkingSet64/1MB))MB)"

# 2. Check memory leak
if ($botProc.WorkingSet64 -gt 400MB) {
    Write-Log "WARNING: Memory high ($([math]::Round($botProc.WorkingSet64/1MB))MB)"
}

# 3. Check recent errors (within last 60 min)
if (Test-Path $errFile) {
    $errModified = (Get-Item $errFile).LastWriteTime
    $errAge = ((Get-Date) - $errModified).TotalMinutes
    $errSize = (Get-Item $errFile).Length
    
    if ($errAge -lt 60 -and $errSize -gt 0) {
        $errLines = Get-Content $errFile | Where-Object { $_ -match "ERROR|Traceback" }
        if ($errLines) {
            Write-Log "WARNING: Recent errors in err.log"
        }
    }
}

# 4. Check trade stats
if (Test-Path $tradesFile) {
    try {
        $tradesText = Get-Content $tradesFile -Raw
        $trades = $tradesText | ConvertFrom-Json -ErrorAction Stop
        $now = Get-Date
        $recentClosed = @($trades | Where-Object { 
            $_.status -eq "CLOSED" -and $_.time -and 
            ($now - [datetime]$_.time).TotalMinutes -le 35
        })
        $totalPnl = 0
        $winCount = 0
        $lossCount = 0
        foreach ($trade in $recentClosed) {
            $pnlVal = [double]($trade.pnl -replace '[,]' -replace '^\\$')
            $totalPnl += $pnlVal
            if ($pnlVal -gt 0) { $winCount++ }
            elseif ($pnlVal -le 0) { $lossCount++ }
        }
        if ($winCount -gt 0 -or $lossCount -gt 0) {
            Write-Log "Last 30min: $([math]::Round($totalPnl, 2)) USDT | Wins: $winCount | Losses: $lossCount"
        } else {
            Write-Log "No trades in last 30min"
        }
        $openPos = @($trades | Where-Object { $_.status -eq "OPEN" })
        Write-Log "Open positions: $($openPos.Count)"
        $allClosed = @($trades | Where-Object { $_.status -eq "CLOSED" })
        $overallPnl = 0
        foreach ($trade in $allClosed) {
            $overallPnl += [double]($trade.pnl -replace '[,]' -replace '^\\$')
        }
        Write-Log "Overall PnL: $([math]::Round($overallPnl, 2)) USDT (Total trades: $($allClosed.Count))"
    } catch {
        Write-Log "Error reading trades: $_"
    }
}

# 5. Check auto scan activity
if (Test-Path $outFile) {
    $lastScanLines = Select-String -Path $outFile -Pattern "AUTO SCAN|CANDIDATE|ENTRY" | Select-Object -Last 5
}

Write-Log "Evaluation complete"
