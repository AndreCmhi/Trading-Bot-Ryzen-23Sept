param(
    [string]$Repo,
    [string]$BackupDir,
    [string]$StartedAt,
    [int]$Hours = 4
)

Set-Location $Repo
$start = [datetime]::ParseExact($StartedAt, 'yyyy-MM-dd HH:mm:ss', $null)
$deadline = $start.AddHours($Hours)
$log = Join-Path $Repo 'inverse_experiment_monitor.log'
"[2026-08-05 13:26:21] inverse experiment started. deadline=$deadline backup=$BackupDir" | Add-Content $log

while((Get-Date) -lt $deadline){ Start-Sleep -Seconds 60 }

$reportPath = Join-Path $Repo 'inverse_experiment_report.json'
$py = @'
import json, pathlib, sys
from datetime import datetime
repo=pathlib.Path(sys.argv[1])
started=datetime.strptime(sys.argv[2], '%Y-%m-%d %H:%M:%S')
trades_path=repo/'trades.json'
trades=json.loads(trades_path.read_text(encoding='utf-8')) if trades_path.exists() else []
closed=[]
for trade in trades:
    if str(trade.get('status','')).upper()!='CLOSED':
        continue
    stamp=trade.get('closed_time') or trade.get('time')
    try:
        dt=datetime.strptime(str(stamp), '%Y-%m-%d %H:%M:%S')
    except Exception:
        continue
    if dt>=started and (trade.get('inverse_experiment') or 'inverse on' in str(trade.get('strategy_reason','')).lower()):
        closed.append(trade)
pnl=sum(float(t.get('pnl') or 0) for t in closed)
wins=sum(1 for t in closed if float(t.get('pnl') or 0)>0)
losses=sum(1 for t in closed if float(t.get('pnl') or 0)<0)
winrate=(wins/len(closed)*100) if closed else 0
bad=(len(closed)==0 or pnl<=0 or winrate<50)
print(json.dumps({'closed':len(closed),'wins':wins,'losses':losses,'winrate':round(winrate,2),'pnl':round(pnl,4),'bad':bad}, indent=2))
'@
$report = $py | python - $Repo $StartedAt
$report | Set-Content $reportPath -Encoding UTF8
"[2026-08-05 13:26:21] result=$report" | Add-Content $log
$result = $report | ConvertFrom-Json

if($result.bad){
    Copy-Item -LiteralPath (Join-Path $BackupDir 'app.py') -Destination (Join-Path $Repo 'app.py') -Force
    Copy-Item -LiteralPath (Join-Path $BackupDir 'runtime_settings.json') -Destination (Join-Path $Repo 'runtime_settings.json') -Force
    "[2026-08-05 13:26:21] bad result; restored app.py and runtime_settings.json" | Add-Content $log
}
else {
    $settingsPath = Join-Path $Repo 'runtime_settings.json'
    $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json
    if($settings.PSObject.Properties.Name -contains 'inverse_experiment_enabled'){ $settings.inverse_experiment_enabled = $false }
    $settings | ConvertTo-Json -Depth 5 | Set-Content $settingsPath -Encoding UTF8
    "[2026-08-05 13:26:21] good result; kept code and disabled experiment flag" | Add-Content $log
}

$procs = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'app\.py' }
foreach($proc in $procs){ taskkill.exe /PID $proc.ProcessId /T /F | Out-Null }
Start-Sleep -Seconds 2
Start-Process -FilePath (Join-Path $Repo 'run_background.bat') -WorkingDirectory $Repo -WindowStyle Hidden
"[2026-08-05 13:26:21] bot restarted after experiment" | Add-Content $log
