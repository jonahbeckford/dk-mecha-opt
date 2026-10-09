#Requires -Version 7
<#
.SYNOPSIS
  Prove this machine can build and screenshot Mecha DK 1.0. Fails loud (non-zero exit).

.DESCRIPTION
  Checks the machine and NEVER builds: it does not compile, publish or launch anything. Building is
  build.ps1. Every FAIL names the setup-dev-machine.ps1 step that fixes it.

  Checks: the .NET SDK against global.json, the workloads, CMake, Ninja, a C compiler, the JDK, the
  Android SDK and NDK, Xcode (macOS), Node, a Playwright Chromium, and on Linux xvfb-run and
  ImageMagick.

.EXAMPLE
  pwsh -File scripts/validate-dev-machine.ps1
#>
[CmdletBinding()]
param()

. "$PSScriptRoot/dev-common.ps1"
. "$PSScriptRoot/validate-common.ps1"
Use-RepoDotnet

Section 1 '.NET SDK and workloads (setup step 1, 2)'
$floor = Get-GlobalJsonSdkVersion
$ver = if (Have dotnet) { Get-VersionFromText (& dotnet --version 2>$null) } else { $null }
if ($ver -and $ver -ge $floor) { Pass "dotnet $ver satisfies global.json ($floor or newer)" }
else { Fail "dotnet $ver does not satisfy global.json ($floor or newer); fix with setup step 1" }
if ($ver) {
  $have = (& dotnet workload list 2>$null) -join "`n"
  foreach ($w in @('android', 'wasm-tools') + $(if ($IsMacOS) { 'ios' } else { @() })) {
    if ($have -match "(?m)^$([regex]::Escape($w))\s") { Pass "workload $w" } else { Fail "workload $w is missing; fix with setup step 2" }
  }
}

Section 2 'Native toolchain (setup step 3)'
$cm = if (Have cmake) { Get-VersionFromText (& cmake --version | Select-Object -First 1) } else { $null }
if ($cm -and $cm -ge $script:CMakeMin) { Pass "cmake $cm" } else { Fail "cmake $cm is older than $($script:CMakeMin) or missing; fix with setup step 3" }
if (Have ninja) { Pass 'ninja' } else { Fail 'ninja is missing; fix with setup step 3' }
if ($IsWindows) {
  $vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio/Installer/vswhere.exe'
  $vc = if (Test-Path $vswhere) { & $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath } else { $null }
  if ($vc) { Pass "MSVC C++ tools at $vc" } else { Fail 'MSVC C++ tools are missing; fix with setup step 3' }
} else {
  $cc = if ($IsMacOS) { 'clang' } else { 'cc' }
  if ((Have $cc) -and ((& $cc --version 2>&1 | Select-Object -First 1) -match '\d')) { Pass "$cc responds" } else { Fail "$cc is missing; fix with setup step 3" }
}

Section 3 'Android (setup step 4, 5)'
$jv = Get-JavaVersion
if ($jv -and $jv.Major -ge $script:JavaMin) { Pass "java $jv" } else { Fail "java $jv is older than $($script:JavaMin) or missing; fix with setup step 4" }
$sdk = Get-AndroidSdkDir
if (Test-Path $sdk) { Pass "Android SDK at $sdk" } else { Fail "Android SDK not found at $sdk; fix with setup step 5" }
if (Test-Pinned-Ndk) { Pass "Android NDK at $(Get-AndroidNdkDir)" } else { Fail "Android NDK $($script:NdkVersion) is missing (needs build/cmake/android.toolchain.cmake); fix with setup step 5" }

if ($IsMacOS) {
  Section 4 'Xcode (setup step 6)'
  if ((Have xcode-select) -and (& xcode-select -p 2>$null) -match 'Xcode') { Pass 'Xcode' } else { Fail 'Xcode is missing; install it from the App Store' }
}

Section 5 'Screenshots (setup step 7)'
$nv = if (Have node) { Get-VersionFromText (& node --version) } else { $null }
if ($nv -and $nv.Major -ge $script:NodeMin) { Pass "node $nv" } else { Fail "node $nv is older than $($script:NodeMin) or missing; fix with setup step 7" }
$pw = if ($env:PLAYWRIGHT_BROWSERS_PATH -and (Test-Path $env:PLAYWRIGHT_BROWSERS_PATH)) { $env:PLAYWRIGHT_BROWSERS_PATH }
      elseif ($IsWindows) { Join-Path $env:LOCALAPPDATA 'ms-playwright' }
      elseif ($IsMacOS) { Join-Path $HOME 'Library/Caches/ms-playwright' }
      else { Join-Path $HOME '.cache/ms-playwright' }
if ((Test-Path $pw) -and (Get-ChildItem $pw -Directory -Filter 'chromium*' -ErrorAction SilentlyContinue)) { Pass "Playwright Chromium under $pw" }
else { Fail "no Playwright Chromium under $pw; fix with setup step 7" }
if ($IsLinux) {
  foreach ($t in 'xvfb-run', 'import') { if (Have $t) { Pass $t } else { Fail "$t is missing; fix with setup step 7" } }
}

exit (Write-ValidateSummary 'validate-dev-machine')
