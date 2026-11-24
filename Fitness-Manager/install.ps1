param(
  [switch]$ClaudeCode,
  [switch]$QwenCode,
  [switch]$Codex,
  [switch]$Grok,
  [switch]$All,
  [string]$ProjectPath = ""
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Name = "fitness-manager"
$Targets = @()
if ($All) { $Targets = @("ClaudeCode", "QwenCode", "Codex", "Grok") }
else {
  if ($ClaudeCode) { $Targets += "ClaudeCode" }
  if ($QwenCode) { $Targets += "QwenCode" }
  if ($Codex) { $Targets += "Codex" }
  if ($Grok) { $Targets += "Grok" }
}
if ($Targets.Count -eq 0) { Write-Host "Use -ClaudeCode, -QwenCode, -Codex, -Grok or -All [-ProjectPath DIR]"; exit 2 }
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss_fff"
foreach ($Target in $Targets) {
  $Base = switch ($Target) { "ClaudeCode" { ".claude/skills" } "QwenCode" { ".agents/skills" } "Codex" { ".agents/skills" } "Grok" { ".grok/skills" } }
  $HomeBase = if ($ProjectPath) { $ProjectPath } else { $HOME }
  $Dest = Join-Path (Join-Path $HomeBase $Base) $Name
  $Parent = Split-Path -Parent $Dest
  New-Item -ItemType Directory -Force -Path $Parent | Out-Null
  $Stage = "$Dest.__staging_$Stamp"
  $BackupRoot = Join-Path $HOME ".fitness-manager-install-backups\$Target"
  New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null
  $Backup = Join-Path $BackupRoot "$Name`_$Stamp"
  try {
    New-Item -ItemType Directory -Force -Path $Stage | Out-Null
    Copy-Item -Path (Join-Path $Root "*") -Destination $Stage -Recurse -Force
    if (Test-Path $Dest) { Move-Item -Path $Dest -Destination $Backup }
    try { Move-Item -Path $Stage -Destination $Dest }
    catch {
      if ((Test-Path $Backup) -and -not (Test-Path $Dest)) { Move-Item -Path $Backup -Destination $Dest }
      throw
    }
    Write-Host "Installed $Target -> $Dest"
    if (Test-Path $Backup) { Write-Host "Previous installation preserved -> $Backup" }
  } catch {
    if (Test-Path $Stage) { Remove-Item -Recurse -Force $Stage }
    throw
  }
}
