#Requires -Version 7
<#
.SYNOPSIS
  Build Mecha dk 1.0. The one entry point for building: people, take-screenshot.ps1 and CI all use it.

.DESCRIPTION
  Wraps dotnet build and dotnet publish with the right target framework, runtime identifier and
  properties. The native C function is built by CMake inside MSBuild (src/MechaDk/Native.targets), so
  a bare `dotnet build` works too.

  Desktop is built for the HOST only, because the native library is. A desktop -Rid for another OS or
  architecture fails early, naming the OS to build it on.

.PARAMETER Target
  desktop, web, android, ios or all. all is every target this host can build; ios only on macOS.

.PARAMETER Configuration
  Debug (default) or Release. -Publish implies Release.

.PARAMETER Publish
  Produce the deliverable under artifacts/publish/<target>/...:
    desktop  mecha-dk (Linux), mecha-dk.exe (Windows), Mecha dk.app (macOS), single file except macOS
    web      the published wwwroot
    android  the APK
    ios      a simulator build, unsigned (macOS only)

.PARAMETER Rid
  Desktop runtime identifier for -Publish. Default is the host's.

.PARAMETER Property
  Extra MSBuild properties, as Name=Value, passed to every dotnet build or publish as -p:Name=Value.
  No leading dash, so pwsh -File does not mistake it for a parameter name.
  Example: -Property ValidateXcodeVersion=false

.EXAMPLE
  pwsh scripts/build.ps1 -Target desktop
  pwsh scripts/build.ps1 -Target desktop -Publish
  pwsh scripts/build.ps1 -Target all -Publish
#>
[CmdletBinding()]
param(
  [ValidateSet('desktop', 'web', 'android', 'ios', 'all')][string]$Target = 'all',
  [ValidateSet('Debug', 'Release')][string]$Configuration = 'Debug',
  [switch]$Publish,
  [string]$Rid,
  [string[]]$Property = @()
)

. "$PSScriptRoot/dev-common.ps1"
$ErrorActionPreference = 'Stop'
Use-RepoDotnet
if ($Publish) { $Configuration = 'Release' }
if (-not $Rid) { $Rid = $script:HostRid }

# Native.targets reads the NDK from the environment, so a machine needs no persistent variable.
if (-not $env:ANDROID_NDK_ROOT -and (Test-Pinned-Ndk)) { $env:ANDROID_NDK_ROOT = Get-AndroidNdkDir }
if (-not $env:ANDROID_HOME -and (Test-Path (Get-AndroidSdkDir))) { $env:ANDROID_HOME = Get-AndroidSdkDir }

$proj = Join-Path $script:ProjectDir 'MechaDk.csproj'
$publishRoot = Join-Path $script:ArtifactsDir 'publish'
$produced = [System.Collections.Generic.List[string]]::new()

# One target framework per build. Restore then touches only that framework, so a desktop build needs
# neither the android nor the wasm-tools workload (CI installs only what a job uses), and -r cannot
# leak into restore of the other frameworks, which would ask for runtime packs that do not exist.
function Get-TfmArg([string]$Tfm) { "-p:TargetFrameworks=$Tfm" }

function Invoke-Dotnet([string[]]$DotnetArgs) {
  $DotnetArgs = $DotnetArgs + @($Property | ForEach-Object { "-p:$_" })
  Write-Host "> dotnet $($DotnetArgs -join ' ')" -ForegroundColor Cyan
  & dotnet @DotnetArgs
  if ($LASTEXITCODE -ne 0) { throw "dotnet $($DotnetArgs[0]) failed with exit code $LASTEXITCODE" }
}

function New-MacApp([string]$PublishDir, [string]$AppPath) {
  # Uno.Sdk has no bundle packaging for the desktop head, so the bundle is assembled here: a
  # directory layout plus Info.plist. Signing and notarizing are left to the maintainer's Mac.
  if (Test-Path $AppPath) { Remove-Item $AppPath -Recurse -Force }
  $macos = Join-Path $AppPath 'Contents/MacOS'
  New-Item -ItemType Directory -Force -Path $macos, (Join-Path $AppPath 'Contents/Resources') | Out-Null
  Copy-Item (Join-Path $PublishDir '*') $macos -Recurse -Force
  $plist = @'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key><string>mecha-dk</string>
  <key>CFBundleIdentifier</key><string>com.diskuv.mechadk</string>
  <key>CFBundleName</key><string>Mecha dk</string>
  <key>CFBundleDisplayName</key><string>Mecha dk</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>1.0</string>
  <key>CFBundleVersion</key><string>1</string>
  <key>LSMinimumSystemVersion</key><string>11.0</string>
  <key>NSHighResolutionCapable</key><true/>
</dict>
</plist>
'@
  Set-Content -Path (Join-Path $AppPath 'Contents/Info.plist') -Value $plist -Encoding utf8NoBOM
}

function Build-Desktop {
  if (-not $Publish) {
    Invoke-Dotnet @('build', $proj, '-f', 'net10.0-desktop', (Get-TfmArg 'net10.0-desktop'), '-c', $Configuration)
    $produced.Add((Join-Path $script:ProjectDir "bin/$Configuration/net10.0-desktop")); return
  }
  $stage = Join-Path $publishRoot "desktop/$Rid/stage"
  if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
  Invoke-Dotnet @('publish', $proj, '-f', 'net10.0-desktop', (Get-TfmArg 'net10.0-desktop'), '-r', $Rid, '-c', 'Release', '-o', $stage)
  $out = Join-Path $publishRoot "desktop/$Rid"
  if ($Rid.StartsWith('osx')) {
    $app = Join-Path $out 'Mecha dk.app'
    New-MacApp -PublishDir $stage -AppPath $app
    $produced.Add($app)
  } else {
    # Uno's content (icons, fonts) is published beside the executable but is not needed to run it.
    # The deliverable is the one file.
    $exe = if ($Rid.StartsWith('win')) { 'mecha-dk.exe' } else { 'mecha-dk' }
    Copy-Item (Join-Path $stage $exe) (Join-Path $out $exe) -Force
    $produced.Add((Join-Path $out $exe))
  }
  Remove-Item $stage -Recurse -Force
}

function Build-Web {
  if (-not $Publish) {
    Invoke-Dotnet @('build', $proj, '-f', 'net10.0-browserwasm', (Get-TfmArg 'net10.0-browserwasm'), '-c', $Configuration)
    $produced.Add((Join-Path $script:ProjectDir "bin/$Configuration/net10.0-browserwasm")); return
  }
  $out = Join-Path $publishRoot 'web'
  if (Test-Path $out) { Remove-Item $out -Recurse -Force }
  Invoke-Dotnet @('publish', $proj, '-f', 'net10.0-browserwasm', (Get-TfmArg 'net10.0-browserwasm'), '-c', 'Release', '-o', $out)
  $produced.Add((Join-Path $out 'wwwroot'))
}

function Build-Android {
  if (-not $env:ANDROID_NDK_ROOT) { throw 'The Android NDK was not found. Run scripts/setup-dev-machine.ps1 -InstallTools.' }
  if (-not $Publish) {
    Invoke-Dotnet @('build', $proj, '-f', 'net10.0-android', (Get-TfmArg 'net10.0-android'), '-c', $Configuration)
    $produced.Add((Join-Path $script:ProjectDir "bin/$Configuration/net10.0-android")); return
  }
  $out = Join-Path $publishRoot 'android'
  if (Test-Path $out) { Remove-Item $out -Recurse -Force }
  Invoke-Dotnet @('publish', $proj, '-f', 'net10.0-android', (Get-TfmArg 'net10.0-android'), '-c', 'Release', '-p:AndroidPackageFormat=apk', '-o', $out)
  Get-ChildItem $out -Filter *.apk | ForEach-Object { $produced.Add($_.FullName) }
}

function Build-Ios {
  if (-not $IsMacOS) { throw 'iOS builds only on macOS.' }
  # Simulator, unsigned: no certificate or profile is committed or assumed.
  $iosArgs = @('-f', 'net10.0-ios26.0', (Get-TfmArg 'net10.0-ios26.0'), '-c', $Configuration, '-p:RuntimeIdentifier=iossimulator-arm64', '-p:EnableCodeSigning=false')
  if ($Publish) { Invoke-Dotnet (@('publish', $proj) + $iosArgs) } else { Invoke-Dotnet (@('build', $proj) + $iosArgs) }
  $produced.Add((Join-Path $script:ProjectDir "bin/$Configuration/net10.0-ios26.0"))
}

$targets = if ($Target -eq 'all') { @('desktop', 'web', 'android') + $(if ($IsMacOS) { 'ios' } else { @() }) } else { @($Target) }
foreach ($t in $targets) {
  switch ($t) {
    'desktop' { Build-Desktop }
    'web'     { Build-Web }
    'android' { Build-Android }
    'ios'     { Build-Ios }
  }
}

Write-Host ''
Write-Host 'Produced:' -ForegroundColor Green
$produced | ForEach-Object { Write-Host "  $_" }
