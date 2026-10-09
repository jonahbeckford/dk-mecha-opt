#Requires -Version 7
<#
.SYNOPSIS
  Build, start Mecha DK 1.0, take a screenshot of it, stop it. Runs on Windows, macOS and Linux.

.DESCRIPTION
  For checking a change visually from Remote Control or a cloud instance, where nobody is looking at
  a screen. Exits non-zero if the app does not start or no screenshot is written. Prints the PNG path.

  desktop  Starts the desktop build and captures it.
             Windows  the app window (System.Drawing), else the primary screen
             macOS    the screen (screencapture); grant Screen Recording to your terminal first
             Linux    uses $DISPLAY if set; otherwise re-runs itself under xvfb-run (1280x800) and
                      captures with ImageMagick import
  web      Starts the WebAssembly build's dev server and screenshots it with Playwright Chromium.
           A Chromium under PLAYWRIGHT_BROWSERS_PATH is reused and never downloaded again.

.PARAMETER Target
  desktop (default) or web.

.PARAMETER OutFile
  Default artifacts/screenshots/<target>-<os>.png

.PARAMETER WaitSeconds
  How long to let the app draw before capturing. Default 10 for desktop and 30 for web, whose
  WebAssembly runtime takes longer to start.

.PARAMETER NoBuild
  Use the existing Debug build instead of running build.ps1 first.

.EXAMPLE
  pwsh -File scripts/take-screenshot.ps1
  pwsh -File scripts/take-screenshot.ps1 -Target web -OutFile web.png
#>
[CmdletBinding()]
param(
  [ValidateSet('desktop', 'web')][string]$Target = 'desktop',
  [string]$OutFile,
  [int]$WaitSeconds = 0,
  [int]$Port = 5000,
  [switch]$NoBuild
)

. "$PSScriptRoot/dev-common.ps1"
$ErrorActionPreference = 'Stop'
Use-RepoDotnet
if ($WaitSeconds -le 0) { $WaitSeconds = if ($Target -eq 'web') { 30 } else { 10 } }
if (-not $OutFile) { $OutFile = Join-Path $script:ArtifactsDir "screenshots/$Target-$($script:HostOs).png" }
$OutFile = [IO.Path]::GetFullPath($OutFile)
New-Item -ItemType Directory -Force -Path (Split-Path $OutFile) | Out-Null
if (Test-Path $OutFile) { Remove-Item $OutFile -Force }

# On a Linux machine with no display, run the whole script again under a virtual one.
if ($Target -eq 'desktop' -and $IsLinux -and -not $env:DISPLAY) {
  if (-not (Have xvfb-run)) { throw 'No $DISPLAY and no xvfb-run. Install xvfb (setup-dev-machine.ps1 -InstallTools).' }
  $self = @('-NoProfile', '-File', $PSCommandPath, '-Target', $Target, '-OutFile', $OutFile, '-WaitSeconds', $WaitSeconds)
  if ($NoBuild) { $self += '-NoBuild' }
  & xvfb-run -a -s '-screen 0 1280x800x24' pwsh @self
  exit $LASTEXITCODE
}

# On a Mac the desktop app is the Mecha DK.app bundle that build.ps1 -Publish assembles, started the way a
# person starts it, not through dotnet. That is the artifact that will be signed, so that is the one to look at.
$macApp = Join-Path $script:ArtifactsDir "publish/desktop/$($script:HostRid)/Mecha DK.app"
$useBundle = $Target -eq 'desktop' -and $IsMacOS

if (-not $NoBuild) {
  $buildArgs = @('-NoProfile', '-File', (Join-Path $PSScriptRoot 'build.ps1'), '-Target', $Target)
  if ($useBundle) { $buildArgs += '-Publish' }
  & pwsh @buildArgs
  if ($LASTEXITCODE -ne 0) { throw "build.ps1 failed with exit code $LASTEXITCODE" }
}

function Save-DesktopScreenshot([System.Diagnostics.Process]$proc, [string]$path) {
  if ($IsLinux) {
    if (-not (Have import)) { throw 'ImageMagick import is missing. Install imagemagick (setup-dev-machine.ps1 -InstallTools).' }
    & import -window root $path
  } elseif ($IsMacOS) {
    & screencapture -x $path
  } else {
    Add-Type -AssemblyName System.Drawing
    Add-Type -Namespace Win32 -Name Native -MemberDefinition @'
[System.Runtime.InteropServices.DllImport("user32.dll")] public static extern bool GetWindowRect(System.IntPtr hWnd, out RECT r);
[System.Runtime.InteropServices.StructLayout(System.Runtime.InteropServices.LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
'@
    $proc.Refresh()
    $r = New-Object Win32.Native+RECT
    $ok = ($proc.MainWindowHandle -ne [IntPtr]::Zero) -and [Win32.Native]::GetWindowRect($proc.MainWindowHandle, [ref]$r)
    if (-not $ok -or ($r.Right - $r.Left) -lt 10) {
      $b = [System.Windows.Forms.SystemInformation]::VirtualScreen
      $r = [pscustomobject]@{ Left = $b.Left; Top = $b.Top; Right = $b.Right; Bottom = $b.Bottom }
    }
    $w = $r.Right - $r.Left; $h = $r.Bottom - $r.Top
    $bmp = New-Object System.Drawing.Bitmap $w, $h
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($r.Left, $r.Top, 0, 0, $bmp.Size)
    $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bmp.Dispose()
  }
}

$proc = $null
try {
  if ($useBundle) {
    if (-not (Test-Path $macApp)) { throw "No app bundle at $macApp. Run without -NoBuild." }
    & open -n $macApp
    if ($LASTEXITCODE -ne 0) { throw "open failed with exit code $LASTEXITCODE" }
    Start-Sleep -Seconds $WaitSeconds
    & pgrep -f "$macApp/Contents/MacOS/mecha-dk" | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "The app exited early: no process is running from $macApp." }
    Save-DesktopScreenshot $null $OutFile
  } elseif ($Target -eq 'desktop') {
    $dll = Join-Path $script:ProjectDir 'bin/Debug/net10.0-desktop/mecha-dk.dll'
    if (-not (Test-Path $dll)) { throw "No desktop build at $dll. Run without -NoBuild." }
    $proc = Start-Process dotnet -ArgumentList @("`"$dll`"") -PassThru
    Start-Sleep -Seconds $WaitSeconds
    if ($proc.HasExited) { throw "The app exited early with code $($proc.ExitCode)." }
    Save-DesktopScreenshot $proc $OutFile
  } else {
    $log = Join-Path ([IO.Path]::GetTempPath()) "mechadk-web-$PID.log"
    $env:ASPNETCORE_URLS = "http://127.0.0.1:$Port"
    $proc = Start-Process dotnet -ArgumentList @('run', '--project', "`"$($script:ProjectDir)`"", '-f', 'net10.0-browserwasm', '--no-build', '--no-launch-profile') `
      -PassThru -RedirectStandardOutput $log -RedirectStandardError "$log.err"
    # Ready means the page answers, whatever the dev server chooses to print.
    $url = "http://127.0.0.1:$Port/"
    $deadline = (Get-Date).AddSeconds(90)
    $up = $false
    while ((Get-Date) -lt $deadline -and -not $up) {
      if ($proc.HasExited) { throw "The dev server exited early: $(Get-Content $log, "$log.err" -Raw -ErrorAction SilentlyContinue)" }
      try { $up = (Invoke-WebRequest $url -TimeoutSec 3 -SkipHttpErrorCheck).StatusCode -eq 200 } catch { Start-Sleep -Milliseconds 500 }
    }
    if (-not $up) { throw "The dev server did not answer at $url within 90 seconds." }
    if (-not (Have npx)) { throw 'npx is missing. Install Node (setup-dev-machine.ps1 -InstallTools).' }
    & npx --yes "playwright@$($script:PlaywrightVersion)" screenshot --browser chromium --viewport-size '1280,800' `
      --wait-for-timeout ($WaitSeconds * 1000) "http://127.0.0.1:$Port/" $OutFile
    if ($LASTEXITCODE -ne 0) { throw "playwright screenshot failed with exit code $LASTEXITCODE" }
  }
} finally {
  # Kill the whole tree: dotnet run starts the dev server as a child.
  if ($proc -and -not $proc.HasExited) { try { $proc.Kill($true) } catch { } }
  if ($useBundle) { & pkill -f "$macApp/Contents/MacOS/mecha-dk" 2>$null }
}

if (-not (Test-Path $OutFile) -or (Get-Item $OutFile).Length -lt 1024) { throw "No usable screenshot was written to $OutFile" }
Write-Host $OutFile
