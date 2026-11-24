param(
  [string]$Python = "python",
  [string]$TaskName = "FitnessManagerDailyBackup",
  [string]$Time = "20:00"
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Script = Join-Path $Root "scripts\fitness_manager.py"
$PythonCmd = Get-Command $Python -ErrorAction Stop
$Action = New-ScheduledTaskAction -Execute $PythonCmd.Source -Argument "`"$Script`" backup" -WorkingDirectory $Root
$Trigger = New-ScheduledTaskTrigger -Daily -At $Time
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Fitness Manager: backup SQLite local e diretório Google Drive sincronizado." -Force | Out-Null
Write-Host "Tarefa diária instalada: $TaskName às $Time"
Write-Host "Ela usa a configuração de backup local e Google Drive já salva em ~/.fitness-manager/config.json."
