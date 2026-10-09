#Requires -Version 7
<#
  Pins and host helpers shared by build.ps1, setup-dev-machine.ps1, validate-dev-machine.ps1
  and take-screenshot.ps1. Dot-sourced, so the four scripts cannot disagree about a version.
  Defines no reporting helpers; setup-common.ps1 and validate-common.ps1 own those.
#>

Set-StrictMode -Off

$script:RepoRoot = Split-Path -Parent $PSScriptRoot
$script:ProjectDir = Join-Path $script:RepoRoot 'src/MechaDK'
$script:ArtifactsDir = Join-Path $script:RepoRoot 'artifacts'

# Minimum versions. Raise one here and setup and validate both move.
$script:CMakeMin = [version]'3.21'
$script:JavaMin = 17
$script:NodeMin = 22
$script:NdkVersion = '27.2.12479018'
$script:PlaywrightVersion = '1.56.0'
# Google's command line tools, which provide sdkmanager. The .NET android workload has its own
# installer (dotnet build -t:InstallAndroidDependencies), but it does its own certificate validation
# and fails behind a TLS-intercepting proxy, so setup uses the plain sdkmanager route.
$script:AndroidCmdlineToolsBuild = '13114758'
$script:AndroidPlatform = 'android-36'
$script:AndroidBuildTools = '36.0.0'
$script:DotnetInstallDir = Join-Path $HOME '.dotnet'

$script:HostOs = if ($IsWindows) { 'win' } elseif ($IsMacOS) { 'osx' } else { 'linux' }
$script:HostArch = [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture.ToString().ToLowerInvariant()
$script:HostRid = "$($script:HostOs)-$($script:HostArch)"

function Have($name) { [bool](Get-Command $name -ErrorAction SilentlyContinue) }

# The SDK floor is global.json's, so there is one place to change it.
function Get-GlobalJsonSdkVersion {
  $g = Get-Content (Join-Path $script:RepoRoot 'global.json') -Raw | ConvertFrom-Json
  return [version]($g.sdk.version)
}

# Prefer the SDK that dotnet-install.sh put in ~/.dotnet over a distro one. A distro SDK ships
# runtime packs at its own patch level, and nuget.org does not carry those (measured 2026-10-09:
# Ubuntu's 10.0.12 asked for a Mono runtime pack that does not exist).
function Use-RepoDotnet {
  if (Test-Path (Join-Path $script:DotnetInstallDir (($IsWindows) ? 'dotnet.exe' : 'dotnet'))) {
    $env:DOTNET_ROOT = $script:DotnetInstallDir
    $sep = [IO.Path]::PathSeparator
    if (($env:PATH -split $sep)[0] -ne $script:DotnetInstallDir) { $env:PATH = "$($script:DotnetInstallDir)$sep$($env:PATH)" }
  }
  $env:DOTNET_CLI_TELEMETRY_OPTOUT = '1'
  $env:DOTNET_NOLOGO = '1'
}

function Get-AndroidSdkDir {
  foreach ($v in $env:ANDROID_HOME, $env:ANDROID_SDK_ROOT) { if ($v -and (Test-Path $v)) { return $v } }
  if ($IsWindows) { return (Join-Path $env:LOCALAPPDATA 'Android/Sdk') }
  if ($IsMacOS) { return (Join-Path $HOME 'Library/Android/sdk') }
  return (Join-Path $HOME 'Android/Sdk')
}

function Get-AndroidNdkDir {
  foreach ($v in $env:ANDROID_NDK_ROOT, $env:ANDROID_NDK_HOME) {
    if ($v -and (Test-Path (Join-Path $v 'build/cmake/android.toolchain.cmake'))) { return $v }
  }
  return (Join-Path (Get-AndroidSdkDir) "ndk/$($script:NdkVersion)")
}

function Test-Pinned-Ndk { Test-Path (Join-Path (Get-AndroidNdkDir) 'build/cmake/android.toolchain.cmake') }

# Run a native command, echo it, and return its exit code.
function Invoke-Native([string]$Exe, [string[]]$Arguments) {
  Write-Host "  > $Exe $($Arguments -join ' ')" -ForegroundColor DarkGray
  & $Exe @Arguments
  return $LASTEXITCODE
}

function Get-VersionFromText([string]$text) {
  $m = [regex]::Match($text, '\d+(\.\d+){1,3}')
  if ($m.Success) { return [version]$m.Value }
  return $null
}

# `java -version` writes to stderr and may be preceded by a "Picked up JAVA_TOOL_OPTIONS" line whose
# value can contain version-shaped text (an IP address), so match the `version "x.y"` line only.
function Get-JavaVersion {
  if (-not (Have java)) { return $null }
  $text = (& java -version 2>&1 | ForEach-Object { "$_" }) -join "`n"
  $m = [regex]::Match($text, '(?:openjdk|java) version "(\d+(?:\.\d+)*)')
  if ($m.Success) { return [version]($m.Groups[1].Value -replace '^(\d+)$', '$1.0') }
  return $null
}
