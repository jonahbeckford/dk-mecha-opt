#Requires -Version 7
<#
  Reporting helpers for setup-dev-machine.ps1: Step, Ok, Warn, Note and the summary. The same
  vocabulary as dk-engine-opt's setup-common.ps1. Dot-sourced.
#>

Set-StrictMode -Off
$ErrorActionPreference = 'Continue'

$script:Missing = @()
function Step($n, $m) { Write-Host ""; Write-Host "[$n] $m" -ForegroundColor Cyan }
function Ok($m)   { Write-Host "  OK    $m" -ForegroundColor Green }
function Warn($m) { Write-Host "  TODO  $m" -ForegroundColor Yellow; $script:Missing += $m }
function Note($m) { Write-Host "        $m" -ForegroundColor DarkGray }

$script:SetupT0 = Get-Date

function Write-SetupSummary([string]$label, [string]$nextStep) {
  $wall = [math]::Round(((Get-Date) - $script:SetupT0).TotalSeconds, 1)
  Write-Host ""
  Write-Host "$label  ($($wall)s)" -ForegroundColor White
  if ($script:Missing.Count -eq 0) {
    Write-Host "  nothing needs attention" -ForegroundColor Green
  } else {
    Write-Host "  $($script:Missing.Count) item(s) need attention:" -ForegroundColor Yellow
    $script:Missing | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
  }
  if ($nextStep) {
    Write-Host ""
    Write-Host "NEXT STEP" -ForegroundColor White
    foreach ($l in ($nextStep -split "`n")) { Write-Host "  $l" }
  }
  return ([int]($script:Missing.Count -gt 0))
}
