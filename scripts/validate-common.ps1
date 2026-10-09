#Requires -Version 7
<#
  Reporting helpers for validate-dev-machine.ps1: Pass, Fail, Skip, Warn, Note, Section and the
  summary. The same vocabulary as dk-engine-opt's validate-common.ps1, so output means the same
  thing in both repositories. Dot-sourced.
#>

Set-StrictMode -Off
$ErrorActionPreference = 'Continue'

$script:Failures = @()
$script:Warnings = @()

function Pass($m) { Write-Host "  PASS  $m" -ForegroundColor Green }
function Fail($m) { Write-Host "  FAIL  $m" -ForegroundColor Red; $script:Failures += $m }
function Skip($m) { Write-Host "  SKIP  $m" -ForegroundColor Yellow }
function Note($m) { Write-Host "        $m" -ForegroundColor DarkGray }
# WARN names something that will cost later while the machine still works now. It is reprinted in
# the summary and does not change the exit code.
function Warn($m) { Write-Host "  WARN  $m" -ForegroundColor Yellow; $script:Warnings += $m }

$script:ScriptT0 = Get-Date
function Section($n, $m) { Write-Host ""; Write-Host "[$n] $m" -ForegroundColor Cyan }

function Write-ValidateSummary([string]$label) {
  $wall = [math]::Round(((Get-Date) - $script:ScriptT0).TotalSeconds, 1)
  Write-Host ""
  if ($script:Warnings.Count -gt 0) {
    Write-Host "$label WARNINGS - $($script:Warnings.Count):" -ForegroundColor Yellow
    $script:Warnings | ForEach-Object { Write-Host "  ! $_" -ForegroundColor Yellow }
    Write-Host ""
  }
  if ($script:Failures.Count -eq 0) {
    Write-Host "$label OK - all checks passed ($($wall)s)." -ForegroundColor Green
    return 0
  }
  Write-Host "$label FAILED - $($script:Failures.Count) check(s):" -ForegroundColor Red
  $script:Failures | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
  return 1
}
