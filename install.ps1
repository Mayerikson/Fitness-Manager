param(
    [switch]$ClaudeCode,
    [switch]$Codex,
    [switch]$QwenCode,
    [switch]$Grok,
    [switch]$All,
    [string]$ProjectPath = (Get-Location).Path
)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
if ($All) { $ClaudeCode = $true; $Codex = $true; $QwenCode = $true; $Grok = $true }
if (-not ($ClaudeCode -or $Codex -or $QwenCode -or $Grok)) {
    throw 'Select at least one target: -ClaudeCode, -Codex, -QwenCode, -Grok or -All'
}

function Install-FitnessManager([string]$Target) {
    $Parent = Split-Path -Parent $Target
    New-Item -ItemType Directory -Force -Path $Parent | Out-Null
    if (Test-Path $Target) {
        $Stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
        $Backup = "$Target.backup-$Stamp"
        Copy-Item -Recurse -Force $Target $Backup
        Write-Host "Existing installation backed up to: $Backup"
    }
    New-Item -ItemType Directory -Force -Path $Target | Out-Null
    Copy-Item -Force (Join-Path $Root 'SKILL.md') (Join-Path $Target 'SKILL.md')
    $OptionalRequirements = Join-Path $Root 'requirements-backup-encryption.txt'
    if (Test-Path $OptionalRequirements) { Copy-Item -Force $OptionalRequirements (Join-Path $Target 'requirements-backup-encryption.txt') }
    foreach ($Directory in @('agents','workflows','governance','references','fitness_manager','scripts','docs')) {
        $Source = Join-Path $Root $Directory
        if (Test-Path $Source) {
            $Destination = Join-Path $Target $Directory
            if (Test-Path $Destination) { Remove-Item -Recurse -Force $Destination }
            Copy-Item -Recurse -Force $Source $Destination
        }
    }
    Write-Host "Installed Fitness Manager: $Target"
}

if ($ClaudeCode) { Install-FitnessManager (Join-Path $ProjectPath '.claude/skills/fitness-manager') }
if ($Codex) { Install-FitnessManager (Join-Path $ProjectPath '.agents/skills/fitness-manager') }
if ($QwenCode) { Install-FitnessManager (Join-Path $ProjectPath '.qwen/skills/fitness-manager') }
if ($Grok) { Install-FitnessManager (Join-Path $ProjectPath '.grok/skills/fitness-manager') }
