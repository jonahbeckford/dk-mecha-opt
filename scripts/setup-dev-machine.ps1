#Requires -Version 7
<#
.SYNOPSIS
  Prepare a machine to build Mecha dk 1.0 for Windows, macOS, Linux, the web, Android and iOS.

.DESCRIPTION
  Idempotent and re-runnable. By default it REPORTS what is missing and prints the exact install
  command for this OS; it changes nothing. -InstallTools installs what it can.

  It never builds anything; building is build.ps1. After this, run validate-dev-machine.ps1, which
  proves the machine is ready.

  What it covers: the .NET SDK named by global.json, the android and wasm-tools workloads (ios on
  macOS), CMake, Ninja and a C compiler, a JDK, the Android SDK and NDK, Xcode (reported only),
  Node and a Playwright Chromium for screenshots, and on Linux xvfb and ImageMagick.

.PARAMETER InstallTools
  Install what is missing. Without it nothing is installed.

.EXAMPLE
  pwsh -File scripts/setup-dev-machine.ps1
  pwsh -File scripts/setup-dev-machine.ps1 -InstallTools
  pwsh -File scripts/validate-dev-machine.ps1
#>
[CmdletBinding()]
param([switch]$InstallTools)

. "$PSScriptRoot/dev-common.ps1"
. "$PSScriptRoot/setup-common.ps1"

# Run an install, or print it. On Linux a non-root user gets sudo.
function Install-Or-Print([string]$What, [string]$Command) {
  if (-not $InstallTools) { Warn "$What is missing. Install it with: $Command"; return $false }
  Note "installing $What"
  & pwsh -NoProfile -Command $Command
  if ($LASTEXITCODE -ne 0) { Warn "$What install failed (exit $LASTEXITCODE): $Command"; return $false }
  return $true
}
$sudo = if ($IsLinux -and (id -u) -ne '0') { 'sudo ' } else { '' }
function Apt([string]$packages) { "${sudo}apt-get update -qq; ${sudo}apt-get install -y -qq $packages" }

# 1. .NET SDK ------------------------------------------------------------------------------------
Step 1 '.NET SDK'
$floor = Get-GlobalJsonSdkVersion
Use-RepoDotnet
$ver = if (Have dotnet) { Get-VersionFromText (& dotnet --version 2>$null) } else { $null }
if ($ver -and $ver -ge $floor) {
  Ok "dotnet $ver (global.json needs $floor or newer)"
} else {
  $cmd = if ($IsWindows) {
    "Invoke-WebRequest https://dot.net/v1/dotnet-install.ps1 -OutFile `$env:TEMP/dotnet-install.ps1; & `$env:TEMP/dotnet-install.ps1 -Channel 10.0 -InstallDir '$($script:DotnetInstallDir)'"
  } else {
    "curl -fsSL https://dot.net/v1/dotnet-install.sh -o /tmp/dotnet-install.sh; bash /tmp/dotnet-install.sh --channel 10.0 --install-dir '$($script:DotnetInstallDir)'"
  }
  if (Install-Or-Print "the .NET SDK $floor or newer" $cmd) {
    Use-RepoDotnet; Ok "dotnet $(& dotnet --version)"
    Note "add $($script:DotnetInstallDir) to PATH and set DOTNET_ROOT in your shell profile; build.ps1 does it for itself"
  }
}

# 2. Workloads -----------------------------------------------------------------------------------
Step 2 '.NET workloads'
if (Have dotnet) {
  $want = @('android', 'wasm-tools') + $(if ($IsMacOS) { 'ios' } else { @() })
  $have = (& dotnet workload list 2>$null) -join "`n"
  foreach ($w in $want) {
    if ($have -match "(?m)^$([regex]::Escape($w))\s") { Ok "workload $w" }
    elseif ($InstallTools) {
      & dotnet workload install $w
      if ($LASTEXITCODE -eq 0) { Ok "workload $w installed" } else { Warn "workload $w failed to install" }
    } else { Warn "workload $w is missing. Install it with: dotnet workload install $w" }
  }
} else { Warn 'dotnet is missing, so workloads cannot be checked' }

# 3. CMake, Ninja, C compiler ---------------------------------------------------------------------
Step 3 'CMake, Ninja and a C compiler'
$cm = if (Have cmake) { Get-VersionFromText (& cmake --version | Select-Object -First 1) } else { $null }
if ($cm -and $cm -ge $script:CMakeMin) { Ok "cmake $cm" } else {
  $c = if ($IsWindows) { 'winget install --id Kitware.CMake -e' } elseif ($IsMacOS) { 'brew install cmake' } else { Apt 'cmake' }
  [void](Install-Or-Print "CMake $($script:CMakeMin) or newer" $c)
}
if (Have ninja) { Ok 'ninja' } else {
  $c = if ($IsWindows) { 'winget install --id Ninja-build.Ninja -e' } elseif ($IsMacOS) { 'brew install ninja' } else { Apt 'ninja-build' }
  [void](Install-Or-Print 'Ninja' $c)
}
if ($IsWindows) {
  $vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio/Installer/vswhere.exe'
  $vc = if (Test-Path $vswhere) { & $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath } else { $null }
  if ($vc) { Ok "MSVC C++ tools at $vc" } else {
    [void](Install-Or-Print 'the Visual Studio C++ build tools' 'winget install --id Microsoft.VisualStudio.2022.BuildTools -e --override "--quiet --wait --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"')
  }
} elseif ($IsMacOS) {
  if (Have clang) { Ok 'clang' } else { [void](Install-Or-Print 'the Xcode command line tools' 'xcode-select --install') }
} else {
  if (Have cc) { Ok 'cc' } else { [void](Install-Or-Print 'a C compiler' (Apt 'build-essential')) }
}

# 4. JDK -------------------------------------------------------------------------------------------
Step 4 "JDK $($script:JavaMin) or newer"
$jv = Get-JavaVersion
if ($jv -and $jv.Major -ge $script:JavaMin) { Ok "java $jv" } else {
  $c = if ($IsWindows) { 'winget install --id Microsoft.OpenJDK.17 -e' } elseif ($IsMacOS) { 'brew install --cask microsoft-openjdk@17' } else { Apt 'openjdk-17-jdk-headless' }
  [void](Install-Or-Print "JDK $($script:JavaMin)" $c)
}

# 5. Android SDK and NDK ---------------------------------------------------------------------------
Step 5 'Android SDK and NDK'
$sdk = Get-AndroidSdkDir
$sdkmgr = Join-Path $sdk ('cmdline-tools/latest/bin/sdkmanager' + $(if ($IsWindows) { '.bat' } else { '' }))
if ((Test-Path $sdkmgr) -and (Test-Pinned-Ndk)) {
  Ok "Android SDK at $sdk, NDK $($script:NdkVersion)"
} elseif (-not $InstallTools) {
  Warn "the Android SDK or NDK $($script:NdkVersion) is missing under $sdk. Run this script with -InstallTools"
} elseif (-not ((Have dotnet) -and (Have java))) {
  Warn 'the Android SDK needs dotnet and a JDK first; fix the steps above and re-run'
} else {
  New-Item -ItemType Directory -Force -Path $sdk | Out-Null
  if (-not (Test-Path $sdkmgr)) {
    $osName = if ($IsWindows) { 'win' } elseif ($IsMacOS) { 'mac' } else { 'linux' }
    $zip = Join-Path ([IO.Path]::GetTempPath()) "cmdline-tools-$($script:AndroidCmdlineToolsBuild).zip"
    $url = "https://dl.google.com/android/repository/commandlinetools-$osName-$($script:AndroidCmdlineToolsBuild)_latest.zip"
    Note "downloading $url"
    Invoke-WebRequest $url -OutFile $zip
    $tmp = Join-Path ([IO.Path]::GetTempPath()) "cmdline-tools-$([guid]::NewGuid().ToString('N'))"
    Expand-Archive $zip -DestinationPath $tmp
    New-Item -ItemType Directory -Force -Path (Join-Path $sdk 'cmdline-tools') | Out-Null
    Move-Item (Join-Path $tmp 'cmdline-tools') (Join-Path $sdk 'cmdline-tools/latest') -Force
    if (-not $IsWindows) { chmod -R +x (Join-Path $sdk 'cmdline-tools/latest/bin') }
    Remove-Item $zip, $tmp -Recurse -Force -ErrorAction SilentlyContinue
  }
  if (Test-Path $sdkmgr) {
    # sdkmanager's progress bar floods a terminal, so its output is shown only if it fails.
    (1..30 | ForEach-Object { 'y' }) | & $sdkmgr "--sdk_root=$sdk" --licenses *> $null
    $out = & $sdkmgr "--sdk_root=$sdk" 'platform-tools' "platforms;$($script:AndroidPlatform)" "build-tools;$($script:AndroidBuildTools)" "ndk;$($script:NdkVersion)" 2>&1
    if ($LASTEXITCODE -ne 0) { $out | ForEach-Object { Note "$_" } }
    if (Test-Pinned-Ndk) { Ok "Android SDK and NDK $($script:NdkVersion) installed" } else { Warn "NDK $($script:NdkVersion) did not install" }
  } else { Warn "sdkmanager was not found at $sdkmgr after unpacking the command line tools" }
}
Note "build.ps1 sets ANDROID_NDK_ROOT itself; set it in your profile only for a bare dotnet build"

# 6. Xcode (macOS only) ----------------------------------------------------------------------------
if ($IsMacOS) {
  Step 6 'Xcode (iOS builds only)'
  if ((Have xcode-select) -and (& xcode-select -p 2>$null) -match 'Xcode') { Ok 'Xcode' }
  else { Warn 'Xcode is missing. Install it from the App Store; this script never installs it' }
}

# 7. Screenshot dependencies -------------------------------------------------------------------------
Step 7 'Screenshot dependencies'
$nv = if (Have node) { Get-VersionFromText (& node --version) } else { $null }
if ($nv -and $nv.Major -ge $script:NodeMin) { Ok "node $nv" } else {
  $c = if ($IsWindows) { 'winget install --id OpenJS.NodeJS -e' } elseif ($IsMacOS) { 'brew install node' } else { 'curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -; sudo apt-get install -y nodejs' }
  [void](Install-Or-Print "Node $($script:NodeMin) or newer" $c)
}
function Get-PlaywrightBrowserDir {
  if ($env:PLAYWRIGHT_BROWSERS_PATH -and (Test-Path $env:PLAYWRIGHT_BROWSERS_PATH)) { return $env:PLAYWRIGHT_BROWSERS_PATH }
  if ($IsWindows) { return (Join-Path $env:LOCALAPPDATA 'ms-playwright') }
  if ($IsMacOS) { return (Join-Path $HOME 'Library/Caches/ms-playwright') }
  return (Join-Path $HOME '.cache/ms-playwright')
}
$pw = Get-PlaywrightBrowserDir
if ((Test-Path $pw) -and (Get-ChildItem $pw -Directory -Filter 'chromium*' -ErrorAction SilentlyContinue)) { Ok "Playwright Chromium under $pw" }
elseif ((Have npx) -and $InstallTools) {
  & npx --yes "playwright@$($script:PlaywrightVersion)" install chromium
  if ($LASTEXITCODE -eq 0) { Ok 'Playwright Chromium installed' } else { Warn 'Playwright Chromium failed to install' }
} else { Warn "Playwright Chromium is missing. Install it with: npx --yes playwright@$($script:PlaywrightVersion) install chromium" }
if ($IsLinux) {
  foreach ($p in @(@('xvfb-run', 'xvfb'), @('import', 'imagemagick'))) {
    if (Have $p[0]) { Ok $p[0] } else { [void](Install-Or-Print $p[1] (Apt $p[1])) }
  }
}

Note 'uno-check (dotnet tool install -g uno.check) is an optional cross-check; nothing here relies on it'
$next = "pwsh -File scripts/validate-dev-machine.ps1`npwsh -File scripts/build.ps1 -Target all"
exit (Write-SetupSummary 'setup-dev-machine' $next)
