# Minimal Uno Platform scaffold for Mecha DK 1.0

This is the plan of record. It lives in the repository so it survives a lost session. Update this file,
not a copy. The sections run in order of writing: the original plan, then addenda for what changed.
**Status: the CI verification is complete** (Addendum 7). Addenda 3 to 6 record how it got there; no
scheduled follow-up remains.

## Context

dk-mecha-opt (branch `jumping-jack`) holds only the agent scaffolding: `AGENTS.md`, `CLAUDE.md`,
`.ai-skills/`, `.claude-plugin/`, `README.md` and `.gitattributes`. The maintainer wants the smallest
.NET project that builds the dk mecha GUI, product name **Mecha DK 1.0**, for Windows, macOS, Linux, the web and mobile (Android, iOS). They chose
**Uno Platform** on **.NET 10 LTS**. Desktop ships as standalone single-file executables named **`dk`** (Linux) and **`dk.exe`** (Windows), and as a signable **`Dk.app`** bundle on macOS. A one-function C file, built by CMake as part of `dotnet build`, stands in for the OCaml code
that will later come as a DLL, a static library and WASM.

## Approach

Use Uno's single-project layout: one `.csproj` on `Uno.Sdk`, with four target frameworks.

- `net10.0-desktop`: Skia rendering, one build that runs on Windows, macOS and Linux (X11 or Wayland).
- `net10.0-browserwasm`: WebAssembly for the web.
- `net10.0-android`: Android (needs the `android` workload, a JDK and the Android SDK).
- `net10.0-ios`: iOS (needs the `ios` workload, and Xcode on macOS to build).

Leave out the native WinUI head (`net10.0-windows10.0.*`), since the desktop head already covers
Windows. iOS can only build on macOS, so its TFM is added only when
`$([MSBuild]::IsOSPlatform('OSX'))` is true. That keeps `dotnet build` working on Linux and Windows,
unless the installed Uno.Sdk already filters it out.

### Product identity

**Mecha DK 1.0** everywhere a user sees it: `ApplicationTitle`/window title "Mecha DK",
`ApplicationDisplayVersion=1.0`, `ApplicationVersion=1`, `Version=1.0.0`, `Product`/`Company` assembly
attributes ("Mecha DK", "Diskuv"), macOS bundle `Dk.app` (`CFBundleName` "Mecha DK",
`CFBundleShortVersionString` 1.0), Android label and iOS `CFBundleDisplayName` "Mecha DK", and the
web page `<title>`. Code names use `MechaDK` (project, namespace) and `mechadk_` (C).

**Executable names.** The desktop executable is `dk` on Linux and `dk.exe` on Windows
(`AssemblyName=dk` for the desktop TFM). On macOS the bundle is `Dk.app`, with `Contents/MacOS/dk`
inside. `CFBundleName` stays "Mecha DK", so Finder and the Dock still show the product name. MlFront
already produces a `dk` executable. This GUI is meant to absorb that OCaml code through the C
binding, so the name collision is deliberate. The README says so, so nobody "fixes" it, and it warns
that the two `dk` executables must not share a `PATH` directory until MlFront's `dk` is retired.

### Generate, then trim

1. Install pwsh, then write the setup scripts first and run `scripts/setup-dev-machine.ps1 -InstallTools`.
   That installs the .NET 10 SDK and the rest of the prerequisites in this container.
2. Run `dotnet new install Uno.Templates` and then
   `dotnet new unoapp -n MechaDK -o src -preset blank -platforms desktop wasm android ios -tests none -toolkit false -markup xaml -theme fluent -di false -config false -http none -log default -nav blank -server false -pwa false -vscode false`
   (keep only the flags the installed template version accepts).
3. Trim to the minimum: drop generated extras the build doesn't need (sample assets beyond the
   app icon and splash, `.vscode`/`.run` folders, the README the template adds).

### Standalone desktop executables

`dotnet publish -f net10.0-desktop -r <rid>` produces one self-contained executable per OS: **`dk`** on Linux and **`dk.exe`** on Windows. On macOS it produces **`Dk.app`** (below). It
carries the .NET runtime and the Skia native libraries, so the target machine needs nothing
installed. In the `.csproj`, conditioned on `'$(TargetFramework)' == 'net10.0-desktop'` and a set
`RuntimeIdentifier`:

- `SelfContained=true`, `PublishSingleFile=true`, `IncludeNativeLibrariesForSelfExtract=true`,
  `EnableCompressionInSingleFile=true`.
- No trimming and no Native AOT. Native AOT cannot cross-compile from Linux to Windows or macOS,
  and trimming XAML apps needs per-type tuning, so both stay out of a minimal scaffold.

Single-file RIDs: `win-x64` and `win-arm64` → `dk.exe`; `linux-x64` and `linux-arm64` → `dk`.

**macOS is an `.app` bundle, not a single-file executable**, so it can be signed and notarized.
Single-file is turned off for `osx-*` RIDs (codesign has to see each Mach-O file in the bundle).
Instead the publish uses Uno.Sdk's desktop packaging,
`dotnet publish -f net10.0-desktop -r osx-arm64 -p:PackageFormat=app` (and `osx-x64`). That
produces a self-contained **`Dk.app`** (bundle name set explicitly, not derived from the project name) with `Contents/MacOS`, `Contents/Resources` and an
`Info.plist` (`CFBundleIdentifier=com.diskuv.mechadk`, display name "Mecha DK", icon from
`Assets`). Signing is left as a property for later, passed only on a Mac with a real identity
(`-p:CodesignKey=...`, plus the hardened-runtime entitlements Uno documents for notarization). The
scaffold commits no identity or certificate.

If the installed Uno.Sdk only builds the bundle on a macOS host, then this session (Linux) verifies
that the `osx-*` self-contained publish succeeds, and the README marks the `.app` step as Mac-only.
I will not hand-roll a bundle target.

### Native C function, built by CMake from `dotnet build`

This stands in for the OCaml code to come, which will build as a DLL, a static library and WASM.
One C file and one CMake project, driven by an MSBuild target in the app project.

- `native/mechadk_native.c`: `const char *mechadk_make_it_so(void) { return "Make it so"; }`,
  exported with a small `MECHADK_EXPORT` macro (`__declspec(dllexport)` on Windows, default
  visibility elsewhere). No libc includes.
- `native/CMakeLists.txt`: `cmake_minimum_required(3.21)`, one `add_library(mechadk_native ...)`.
  `BUILD_SHARED_LIBS` decides between shared and static.
- `src/MechaDK/Native.targets` (imported by the `.csproj`): a `BuildMechaDKNative` target that runs
  before `ResolveReferences`/`Build`. It has `Inputs`/`Outputs` on the C and CMake files, so it is
  incremental. It runs `cmake -S native -B obj/native/<tfm>/<rid-or-abi>` and then `cmake --build`,
  and hands the result to the SDK as follows:

| Target | CMake args | Handed to the SDK as |
|---|---|---|
| desktop | `-DBUILD_SHARED_LIBS=ON` with the host's default compiler | `<None>`/`<ContentWithTargetPath>` copied beside the app (`.dll`/`.so`/`.dylib`); included in single-file extraction and in the `.app`'s `Contents/MacOS` |
| android | NDK `android.toolchain.cmake`, `ANDROID_ABI` per ABI in `RuntimeIdentifiers` (arm64-v8a, x86_64), `ANDROID_PLATFORM=android-21`, shared | `<AndroidNativeLibrary Abi=...>` |
| ios (macOS host only) | `-DCMAKE_SYSTEM_NAME=iOS -DCMAKE_OSX_ARCHITECTURES=arm64`, static | `<NativeReference Kind="Static" ForceLoad="true">` |
| browserwasm | `emcmake cmake` using the emscripten from .NET's `wasm-tools` workload, static | `<NativeFileReference>` with `WasmBuildNative=true` |

- **Native toolchains mean no desktop cross-compiling.** The desktop library is built only for the
  host OS and architecture. `dotnet build` on any host works. A `dotnet publish -r <rid>` for another
  OS or architecture fails early with a clear error ("build the native library on <os>/<arch>"),
  because the standalone app would otherwise ship without its DLL. A `MechaDKNativeCMakeArgs`
  property lets a cross toolchain file be passed later. So the Windows `.exe` is published on
  Windows, the `.app` on a Mac, and the Linux binaries on Linux.
- C#: `src/MechaDK/NativeMethods.cs` uses `[LibraryImport]` and returns `IntPtr`, which becomes a
  string through `Marshal.PtrToStringUTF8`. The pointer is static, so it must not be freed. The
  library name is `"mechadk_native"`, or `"__Internal"` under `#if __IOS__`. `MainPage` shows the
  returned "Make it so" under the title.
- Prerequisites, listed in the README: CMake 3.21+ and a C compiler for the host; the Android NDK
  (`ANDROID_NDK_ROOT`); Xcode for iOS; `dotnet workload install wasm-tools` for the web.

### GitHub Actions: `.github/workflows/build.yml`

One workflow, on `push`, `pull_request` and `workflow_dispatch`. Each job builds natively on its own
OS, which suits the per-host CMake rule above. Common steps: `actions/checkout`,
`actions/setup-dotnet` (from `global.json`), the workloads the job needs, then
`pwsh scripts/build.ps1 -Target <t> -Publish [-Rid <rid>]`. CI builds through the same script
people use. Actions are pinned to
full commit SHAs. Each job uploads its output with `actions/upload-artifact`.

| Job | Runner | Produces |
|---|---|---|
| linux-x64 | `ubuntu-24.04` | single-file `dk` |
| linux-arm64 | `ubuntu-24.04-arm` | single-file `dk` |
| win-x64 | `windows-2025` | single-file `dk.exe` |
| win-arm64 | `windows-11-arm` | single-file `dk.exe` |
| osx-arm64 | `macos-15` | `Dk.app`, zipped with `ditto` (unsigned) |
| osx-x64 | `macos-15-intel` (or `macos-13`) | `Dk.app`, zipped (unsigned) |
| web | `ubuntu-24.04` | published `wwwroot` (wasm-tools workload) |
| android | `ubuntu-24.04` | debug APK (android workload, NDK via `sdkmanager`) |
| ios | `macos-15` | simulator build, no signing (`-p:RuntimeIdentifier=iossimulator-arm64`, `-p:EnableCodeSigning=false`) |

Signing and notarization (macOS, iOS, Windows) and store/release publishing are out of scope; they
need secrets the maintainer adds later. Runner labels are checked against GitHub's current list at
implementation time, and a retired label is swapped for its successor.

### Screenshot script: `scripts/take-screenshot.ps1`

Runs under PowerShell 7 (`pwsh`) on Windows, macOS and Linux, so the maintainer can run it later
through Remote Control or in a cloud instance. Parameters: `-Target desktop|web` (default
`desktop`), `-OutFile <png>` (default `artifacts/screenshots/<target>-<os>.png`), `-WaitSeconds` (default 10),
`-NoBuild`. It builds with `scripts/build.ps1 -Target <target>` (unless `-NoBuild`), starts the app, waits, takes the screenshot, stops the app
and exits non-zero on any failure. It prints the PNG path.

- **desktop**: `dotnet run -f net10.0-desktop` started as a child process.
  - Windows: capture the app's main window bounds via `System.Drawing` `CopyFromScreen` (the
    `Add-Type` of a small `GetWindowRect` P/Invoke).
  - macOS: `screencapture -x -l <window id>`, falling back to the full screen (Screen Recording
    permission noted in the help text).
  - Linux: uses `$DISPLAY` if set; otherwise wraps the run in `xvfb-run` with a 1280x800 screen and
    captures with ImageMagick `import -window root`. A missing `xvfb-run` or `import` gets a clear
    error naming the package.
- **web**: `dotnet run -f net10.0-browserwasm` (Uno's dev server). The script waits for the
  `Now listening on` URL, then runs `npx --yes playwright@<pinned> screenshot --wait-for-timeout`
  against it, with Chromium. It honours `PLAYWRIGHT_BROWSERS_PATH`, so this cloud image's
  preinstalled browser is reused and never downloaded again.

### Dev machine scripts: `scripts/setup-dev-machine.ps1`, `scripts/validate-dev-machine.ps1`

Both follow the dk-engine-opt pattern (`../dk-engine-opt/scripts/setup-dev-machine.ps1`,
`validate-dev-machine.ps1`, with shared helpers dot-sourced from `setup-common.ps1` and
`validate-common.ps1`). They run under `#Requires -Version 7` on Windows, macOS and Linux, reuse the
same `Step`/`Ok`/`Warn`/`Note` and `Pass`/`Fail`/`Skip` reporting helpers (trimmed copies, without the
engine-specific auto-mode, plugin and sibling code), and end with a summary.

- **setup-dev-machine.ps1**: idempotent. By default it **reports** what is missing and prints the
  exact install command for this OS; nothing is installed. `-InstallTools` installs, the same opt-in
  as dk-engine-opt. Per item:
  - .NET 10 SDK at the `global.json` version (winget / brew / `dotnet-install.sh` into `~/.dotnet`).
  - Workloads: `android`, `wasm-tools`; `ios` on macOS only (`dotnet workload install`).
  - CMake 3.21+ and a host C compiler (Visual Studio Build Tools C++ on Windows via winget; Xcode
    Command Line Tools on macOS; `build-essential`/`cmake` via apt on Linux).
  - JDK 17 (Microsoft OpenJDK) and the Android SDK + NDK: `dotnet build -t:InstallAndroidDependencies`
    for the SDK, then `sdkmanager "ndk;<pinned>"` when `ANDROID_NDK_ROOT` is missing or points
    nowhere. The NDK version is pinned in one place in the script.
  - Xcode (macOS only): reported, never installed (App Store).
  - Screenshot dependencies: Node 22 (for `npx playwright`) and Playwright Chromium unless
    `PLAYWRIGHT_BROWSERS_PATH` already holds one; on Linux, `xvfb` and `imagemagick`.
  - `uno-check` (`dotnet tool`) is offered as a cross-check and not relied on.
- **validate-dev-machine.ps1**: checks the machine, **never builds**, and **fails loud** (non-zero
  exit). It does not compile, publish or launch anything; building is `build.ps1`'s job. Checks:
  - the `dotnet` SDK version satisfies `global.json`;
  - `dotnet workload list` includes `android` and `wasm-tools` (and `ios` on macOS);
  - `cmake` is 3.21 or newer, and a host C compiler responds to `--version` (`cl` through
    `vswhere` on Windows, `clang` on macOS, `cc` on Linux);
  - `java -version` reports 17 or newer;
  - the Android SDK directory exists, and `$ANDROID_NDK_ROOT/build/cmake/android.toolchain.cmake`
    exists;
  - Xcode via `xcode-select -p` (macOS);
  - `node` is 22 or newer, and a Playwright Chromium exists (under `PLAYWRIGHT_BROWSERS_PATH` or
    Playwright's default cache);
  - on Linux, `xvfb-run` and `import` exist.

  Each FAIL names the `setup-dev-machine.ps1` step that fixes it.

### Build script: `scripts/build.ps1`

The one entry point for building, used by people, by `take-screenshot.ps1` and by the CI workflow,
so all three build the same way.

- `-Target desktop|web|android|ios|all` (default `all` = every target this host can build; `ios`
  only on macOS). `-Configuration Debug|Release` (default `Debug`).
- `-Publish`: Release, self-contained output in `artifacts/publish/<target>/<rid>/`, giving
  `dk`/`dk.exe` (single file), `Dk.app`, the web `wwwroot`, or the APK. `-Rid <rid>` defaults to
  the host RID for desktop. A desktop RID for another OS or architecture fails early with the
  native-library error described above.
- It wraps `dotnet build`/`dotnet publish` with the right `-f`/`-r`/properties. The CMake native
  step still runs inside MSBuild (`Native.targets`), so a bare `dotnet build` keeps working too.
- It exits non-zero on the first failure and prints each produced path at the end.

This cloud container is a Linux dev machine, so it is set up by running `setup-dev-machine.ps1
-InstallTools` here (after pwsh is installed), not by hand. `validate-dev-machine.ps1` must pass
here before the commit, and `scripts/build.ps1 -Target all` (and `-Publish`) must succeed here.

### Resulting files (approximate)

- `global.json`: pins the .NET SDK (10.0.x, `rollForward: latestFeature`) and the `Uno.Sdk` version.
- `MechaDK.slnx` (or `.sln`, whichever the template emits) at the repo root.
- `src/MechaDK/MechaDK.csproj`: `<Project Sdk="Uno.Sdk">`, with
  `TargetFrameworks=net10.0-desktop;net10.0-browserwasm;net10.0-android` (+ `net10.0-ios` on macOS),
  `OutputType=Exe`, `SingleProject=true`, `ApplicationId=com.diskuv.mechadk`.
- `src/MechaDK/App.xaml(.cs)`, `MainPage.xaml(.cs)`: one page with the title "Mecha DK 1.0" and the native string.
- `native/mechadk_native.c`, `native/CMakeLists.txt`, `src/MechaDK/Native.targets`, `src/MechaDK/NativeMethods.cs`.
- `src/MechaDK/Platforms/Desktop/Program.cs` and `Platforms/WebAssembly/` (Program.cs, `wwwroot`,
  manifest).
- `src/MechaDK/Platforms/Android/` (MainActivity, `AndroidManifest.xml`) and `Platforms/iOS/`
  (`Main.iOS.cs`, `Info.plist`, `Entitlements.plist`), as the template emits them.
- `src/MechaDK/Assets/` with the icon and splash only.
- `Directory.Build.props`/`Directory.Packages.props` only if the template emits them.
- `.github/workflows/build.yml`.
- `scripts/setup-dev-machine.ps1`, `scripts/validate-dev-machine.ps1`, `scripts/setup-common.ps1`, `scripts/validate-common.ps1`.
- `scripts/build.ps1`, `scripts/take-screenshot.ps1`; `artifacts/` added to `.gitignore`.
- `.gitignore`: the standard .NET entries (`bin/`, `obj/`, `.vs/`, `*.user`).

### Records

- `README.md`: add the `src/` and `global.json` lines to the Layout section, plus a short "Build"
  section: one `dotnet build -f ...` command per target, the `dotnet publish -r <rid>` command for
  standalone desktop executables, `dotnet run -f net10.0-desktop`, the
  workloads mobile needs, and a note that iOS builds only on macOS.
- `README.md` also records the convention **script names are lowercase kebab-case** (`scripts/*.ps1`),
  since README is where `add-agent-rule` routes a script fact.
- `AGENTS.md`: leave unchanged. The README is the layout record, and AGENTS.md already indexes it.
  (Check its budget only if it is edited.)

## Verification

- `validate-dev-machine.ps1` passes (no builds). `scripts/build.ps1 -Target all` succeeds, which builds desktop, web and android here, and so does a bare `dotnet build src/MechaDK -f net10.0-desktop`.
- Native: `dotnet build -f net10.0-desktop` runs CMake (the log shows it). A second build skips it
  (incremental). `libmechadk_native.so` lands in the output.
- Desktop standalone (this Linux container, so `linux-x64`): `dotnet publish -f net10.0-desktop -r linux-x64`
  gives one self-contained `dk` with the native library embedded. Run it under `xvfb-run` and
  take a screenshot showing "Make it so". `dotnet publish -r win-x64` must fail with the clear
  cross-host error, not with a silent missing DLL.
- macOS `.app` and the Windows `.exe` cannot be produced here (native toolchains). Their publish
  commands are written in the README for running on a Mac and on Windows.
- Web: also confirm "Make it so" appears in the Playwright screenshot (proves the emscripten link).
- Android: needs the NDK as well (`sdkmanager "ndk;<ver>"`). The debug APK has
  `lib/arm64-v8a/libmechadk_native.so` (`unzip -l`).
- Web: `dotnet publish -f net10.0-browserwasm`, serve `wwwroot` locally and take a Playwright
  screenshot with the preinstalled Chromium (`/opt/pw-browsers`) to confirm "Mecha DK 1.0" renders.
- Android: `dotnet workload install android`, then
  `dotnet build -f net10.0-android -t:InstallAndroidDependencies -p:AcceptAndroidSDKLicenses=true`
  to fetch the SDK into the container, then `dotnet build -f net10.0-android` produces a debug APK.
  No emulator run.
- iOS: no Mac is available here, so iOS is not built in this session. I will confirm that the TFM is
  excluded on Linux and that `dotnet build` with no `-f` still succeeds. The first real iOS build has
  to happen on a Mac; the README says so.
- `git status` shows no `bin/`/`obj/` files staged.

- CI: after the push, use the GitHub tools to list the workflow run on `jumping-jack` and read its
  job results. Fix and re-push until all nine jobs are green. If a job is red only for a reason
  outside the scaffold (a runner image problem), report it instead.

### Visual verification, delivered as private artifacts

This session is a Claude Code cloud session, so the screenshots are delivered as **private
Artifacts**. They are not described in chat, and they are not committed.

1. Install PowerShell 7 in the container (Microsoft's tarball into `~/.local/pwsh`, since `pwsh`
   is not installed), then run `scripts/take-screenshot.ps1 -Target desktop` and
   `-Target web`. That also proves the script works on Linux.
2. Publish one private Artifact, "Mecha DK 1.0 verification" (load `artifact-design` first). It
   embeds both PNGs as data URIs, one per section: desktop (Linux, Xvfb) and web (Chromium). Under
   each image: the commit SHA, the exact command, and whether "Make it so" and "Mecha DK 1.0" are
   visible. Give the link in the reply.
3. Android, iOS, Windows and macOS have no display here, so they are verified by CI build results
   only. The artifact lists them with their CI job status and says that no screenshot was taken for them.

## Commit

One commit on `jumping-jack` as `jonahbeckford` (repo-local config already set), with the message
following git-commits.md and no trailers. Push with `git push -u origin jumping-jack`.

## Addendum: where the work stands (2026-10-09 02:19 UTC)

Implemented and pushed as `a9328db` and `e4f6cfc`. CI run 37873330593 on `e4f6cfc`: **8 of 9 jobs
green** (linux-x64, linux-arm64, win-x64, win-arm64, osx-arm64, osx-x64, web, android). The Windows
failures from the first run were a trailing-backslash quoting bug, fixed in `e4f6cfc`.

**Remaining red: `ios`.** `macos-26` has Xcode 26.6, and the `net10.0-ios` target resolves to the
iOS 27.0 workload pack, which requires Xcode 27.0. The 26.0 pack is installed too
(`Microsoft.iOS.Sdk.net10.0_26.0`).

Proposed fix, to apply once approved:
- `MechaDK.csproj`: `net10.0-ios` becomes `net10.0-ios26.0`, which builds against the iOS 26 SDK and
  Xcode 26.x.
- `Native.targets`: the two iOS conditions change from `== 'net10.0-ios'` to
  `$(TargetFramework.StartsWith('net10.0-ios'))`.
- `build.ps1`: the iOS framework string becomes `net10.0-ios26.0`.
- README: say that iOS is pinned to the 26.0 SDK and that raising it needs the matching Xcode.
- Push, then re-read the run. If `-p:EnableCodeSigning=false` or the simulator RID needs further
  adjustment, fix that in the same loop until all nine jobs are green.

Then publish the private "Mecha DK 1.0 verification" artifact from
`scratchpad/art/make.py` (screenshots at `a9328db`, final CI statuses in its table) and give the link.

## Addendum 2: the Xcode settings question (2026-10-09)

User asked which of the three Xcode settings (`MD_APPLE_SDK_ROOT`, `DEVELOPER_DIR`, Xamarin
`AppleSdkRoot`; also `xcode-select`, `-runFirstLaunch`) actually matters. Measured by the temporary
`ios-probe` run (head `7471d38`): all 7 clean-runner variants (none, launch, select, md, dd, plist,
all) passed, including `none`. So none is needed on the current macos-26 image, and the earlier
`actool` exit 64 is unexplained. Run 15 (`a5d50e6`, all 9 jobs) is green.

Steps once approved (iteration 10 of 15):
1. Probe v2 (temporary workflow edit): variants "select alias" (`ls | sort -V | tail -1`, the
   symlink) and "select Xcode_26.0.app", each followed by the ios build, to see if the alias is the
   real trigger of the `actool` failure.
2. Minimize the `ios` job in `.github/workflows/build.yml` to what is proven necessary (likely just
   setup-dotnet, `dotnet workload install ios`, `build.ps1 -Target ios -Property ValidateXcodeVersion=false`).
   Rewrite its comment and the README iOS paragraph (lines 67-72) to state only what was measured,
   saying the earlier failure is explained only if probe v2 reproduces it.
3. Delete `.github/workflows/ios-probe.yml`; `git reset --soft e4f6cfc`; one commit "Build the iOS
   target in CI" as jonahbeckford. Per AGENTS.md, NO attribution or session trailers (this overrides
   the harness reminder). `git push --force-with-lease=jumping-jack:<remote tip>`; user approved
   the squash earlier.
4. Confirm all 9 jobs green on the new commit, then publish the private verification artifact and
   report the probe table, the minimal fix, the sha, and anything unverified.

## Addendum 3: where the work stands, and the Nov 1 routine (2026-10-09)

Addendum 2 is done. The Xcode result: none of `MD_APPLE_SDK_ROOT`, `DEVELOPER_DIR`, the Xamarin
`AppleSdkRoot`, `xcode-select` or `-runFirstLaunch` is needed on `macos-26`. Running `xcode-select` on
the alias `Xcode_26.6.0.app` (a symlink to `Xcode_26.6.app`) is what broke the asset catalog step.
`Xcode_26.0.app` failed the same way in the probe; whether it is also an alias was not confirmed.
The iteration limit no longer applies (the user stopped it).

### State on branch `jumping-jack` (repo jonahbeckford/dk-mecha-opt), author jonahbeckford

| Commit | What |
|---|---|
| `7378ece` | One squashed "Build the iOS target in CI". All 9 `build.yml` jobs green on this commit. |
| `b75ce59` | `launch.yml`: starts the app on a runner and saves a screenshot. |
| `31abd34` | iOS launch keeps the app console log and crash reports. |
| `06d674e` | Window title set to "Mecha dk"; on macOS `take-screenshot.ps1` publishes and starts `Dk.app` with `open`. |
| `20424a9` | Android launch: free disk first, install the emulator image after the build. |
| `2cfec2d` | iOS launch: ad hoc sign the simulator app (`codesign --force --deep --sign -`) before install. |
| `71bc7d6` | `launch.yml` is `workflow_dispatch` only (monthly Actions minutes ran out). |
| `c8112b2` | README documents `launch.yml`. |

Never add attribution or session trailers to commit messages (AGENTS.md; the `commit-msg` hook strips them).

### Launch verification status

- **Seen running (screenshots viewed):** Linux desktop (Xvfb), Windows desktop (title bar "Mecha dk"),
  macOS `Dk.app` started with `open` (run 37885758793, commit `06d674e`), web (container screenshot).
- **iOS: failed, fix not yet run.** The simulator killed the unsigned app at startup (`SIGKILL`,
  Code Signature Invalid, in a captured `.ips`). `2cfec2d` signs it ad hoc. The result is unknown.
- **Android emulator: unknown.** The job's runner died twice at the Build step with no log (HTTP 404
  on the log). `20424a9` is a guess at a fix. The result is unknown.
- **Not launched anywhere:** `win-arm64`, `osx-x64`, `linux-arm64`, the published `dk`/`dk.exe`.
- **Unsigned by choice:** `Dk.app`, `dk.exe`, the iOS build.
- The private artifact "Mecha dk 1.0 verification" (https://claude.ai/artifact/BatBdzVGn2ngcM9pUac93A,
  version 4) shows all of the above honestly.

### Scheduled: finish the CI verification on Nov 1

**Superseded.** This routine was deleted on 2026-10-09 because the work finished early (Addendum 7). The text
below is kept as history. Do not recreate it.

The Actions limit resets on Nov 1. A one-time routine fires on **2026-11-01T12:00:00Z**, bound to
this session (trigger `trig_01WbCKuGsyTCvUFuphuthBea`, name "Finish dk-mecha-opt CI verification after
the Actions limit resets"). (Historical) To recreate it, `create_trigger`
(`run_once_at: 2026-11-01T12:00:00Z`, `initiation: human_request`, default self-bound) and this prompt.
Check first with `list_triggers` and `get_trigger`.

> The monthly GitHub Actions limit reset today (Nov 1). Finish the CI verification for
> jonahbeckford/dk-mecha-opt on branch jumping-jack. Where it stood: .github/workflows/launch.yml is
> manual only (workflow_dispatch) since commit 71bc7d6, because its macOS and Windows jobs spent the
> minutes. Do NOT re-enable push or pull_request triggers on it. Unverified, waiting on CI: (1) iOS:
> the simulator killed the unsigned app at startup (SIGKILL, Code Signature Invalid, seen in a
> captured .ips); commit 2cfec2d ad hoc signs it with codesign --force --deep --sign - before install;
> confirm the screenshot shows the app, not the simulator home screen. (2) Android emulator job: its
> runner died twice at the Build step with no log (404); commit 20424a9 frees disk and installs the
> emulator image after the build; confirm it passes and the emulator screenshot shows the app. (3)
> Windows and macOS launch screenshots from run 37885758793 are already good (title bar and Dk.app
> bundle launched with open, both read Mecha dk) and are in scratchpad/launch2 if still on disk,
> otherwise redownload from that run if not expired. Steps: confirm the Actions limit is really reset
> (list recent runs; if runs still fail to start with a billing or limit error, report that and stop,
> do not push); check the newest build.yml run on the branch head is green on all 9 jobs (re-run only
> failed jobs once if red, say if not); start launch.yml once with run_workflow on ref jumping-jack;
> list its jobs; for each red job read the log, fix with a normal push (never add attribution or
> session trailers to commit messages, per AGENTS.md; author jonahbeckford; no force-push), and run
> launch.yml again only when a fix was pushed; download each launch artifact (actions_get
> download_workflow_run_artifact, curl into a fresh scratchpad dir, unzip there), view every
> screenshot yourself because the jobs only check that a file exists, and read ios-console.log and
> any .ips crash report. Then regenerate the private artifact with scratchpad/art/make.py (it may need
> the scratchpad recreated; the page is the Mecha dk 1.0 verification page with sections for Linux
> desktop, web, Launched in CI, and a CI table) with the newest screenshots and honest per-platform
> results, and republish to https://claude.ai/artifact/BatBdzVGn2ngcM9pUac93A. Report to the user:
> per platform whether the app was seen running, what failed and what fixed it, the commit shas, and
> anything still unverified. Say plainly if a platform could not be verified.
>
> RENAME, added after the text above was written (see Addendum 4 in planning/2026-10-mecha-dk-scaffold.md,
> the plan of record in the repo; read it first): the GUI is now mecha-dk (Linux), mecha-dk.exe (Windows)
> and Mecha dk.app with Contents/MacOS/mecha-dk (macOS), replacing dk and Dk.app wherever the text above
> says so. The rename commit 69b44a2 carries [skip ci], so NO build.yml run exists on the branch head.
> Before the launch steps, start build.yml with run_workflow on ref jumping-jack, confirm all 9 jobs are
> green, and fix red jobs with normal pushes. Likely suspects: the macOS app path now has a space (the
> ditto zip step in build.yml, and take-screenshot.ps1 with open, pgrep and pkill), and the hyphen in the
> assembly name on Windows and macOS. Only Linux was run after the rename.
>
> SECOND RENAME (Addendum 5 in the same plan file): the product name is now spelled Mecha DK, so the macOS
> bundle is Mecha DK.app (Contents/MacOS/mecha-dk is unchanged), the window title and page heading read
> "Mecha DK" and "Mecha DK 1.0", and the CI zip is Mecha-DK-<rid>.zip. Wherever the text above says
> "Mecha dk" or "Mecha dk.app", read the new spelling; screenshots taken before this rename show the old
> spelling and are historical. A THIRD change (Addendum 6) then renamed the code prefix MechaDk to MechaDK:
> src/MechaDK/, MechaDK.csproj, MechaDK.slnx and the MechaDK namespace, so paths in older text that say
> src/MechaDk need the new spelling (the lowercase mechadk_ names and com.diskuv.mechadk are unchanged).
> Like the first rename it carries [skip ci], so still start build.yml yourself first.

### Recreating the artifact if the scratchpad is gone

`scratchpad/art/make.py` (arguments: commit sha, `ci.json`, output html) is not in the repo. If it is
missing, read the published page with the Artifact tool (`action: read`, the URL above), which returns
its HTML, and rebuild from that: sections "Desktop, Linux", "Web, Chromium", "Launched in CI" and "No
screenshot taken" (a CI table of job, status, note), screenshots embedded as data URIs. Republish to the
same URL.

### What the routine finishes

It succeeds when each of Linux, Windows, macOS, iOS and Android has been seen running in a screenshot
someone looked at, or has an honest recorded reason it was not, and the artifact says so. After that
the plan is complete; remaining open items are the user's choices (signing, other RIDs).

## Addendum 4: the GUI is renamed `mecha-dk` (2026-10-09)

The GUI executable is no longer `dk`, so that `dk` stays free for the command line tool (a GUI and a
CLI need separate executables on Windows, and a macOS GUI must be an `.app`). Earlier sections of this
file still use the old names. The names now are:

| Platform | Name |
|---|---|
| Linux | `mecha-dk` |
| Windows | `mecha-dk.exe` |
| macOS | `Mecha dk.app`, with `Contents/MacOS/mecha-dk` (`CFBundleExecutable` is `mecha-dk`) |

The macOS app name has a space, so scripts and workflows quote its path. CI artifact names are
`mecha-dk-<rid>` and, for macOS, `Mecha-dk-<rid>.zip`. `AssemblyName` is `mecha-dk`.

Verified on Linux only: the Debug build and the published single file both start and draw the page.
**Not verified anywhere else, because the Actions minutes ran out:** the Windows and macOS builds, the
`ditto` zip of the quoted macOS path, `take-screenshot.ps1` finding `Mecha dk.app` and its
`mecha-dk` process (`pgrep`/`pkill`), and every CI artifact name. The rename commit carries `[skip ci]`,
so **no `build.yml` run exists on the branch head**. The Nov 1 routine must start one itself
(`run_workflow` on `build.yml`, ref `jumping-jack`) and fix anything red before the launch checks.
Whether a hyphen in the assembly name breaks anything on the other platforms (resource names, the
macOS bundle) is open until then.

## Addendum 5: product spelling is "Mecha DK" (2026-10-09)

The product is spelled **Mecha DK**, not "Mecha dk". This changes every user-visible string: the window
title, the page heading ("Mecha DK 1.0"), `ApplicationTitle`, `Product`, the macOS `CFBundleName`, the
Android label, the web manifest, the macOS bundle (`Mecha DK.app`, executable still
`Contents/MacOS/mecha-dk`) and the CI zip (`Mecha-DK-<rid>.zip`). The executable names `mecha-dk` and
`mecha-dk.exe` stay lowercase. Earlier sections and Addenda 2 to 4 keep the old spelling where they
describe what was observed at the time.

**`MechaDk` was not renamed to `MechaDK`.** The condition was that `MechaDK` must work as a MlFront
library id prefix such as `MechaDK_Std`. That could not be confirmed:
- The rule found says a library id is "a double camel cased string followed by an underscore and another
  camel cased string, like `XyzAbc_Def`" (SPECIFICATION.md:1471, quoted in `dk-engine-opt`
  `state/spec-anchor-review.md`). Whether a trailing `DK` counts as camel cased is not stated.
- Real ids all use plain camel case in the first term: `CommonsBase_Std`, `DkZero_Exec`, `MlFront_Std`,
  `DkExe_Std`. The first term spells acronyms in title case (`NotMitEdu_Kerberos`, not `NotMIT...`).
  Acronyms do appear in the second term (`CommonsBase_GNU`, `CommonsBase_LLVM`, `CommonsLang_OCaml`).
  That is weak evidence against `MechaDK` as a first term, not proof.
- The parser (`MlFront_Core.LibraryId.parse`) is in `dksdk-coder`, which is not checked out here and was
  not reachable from this session.

To settle it, run `MlFront_Core.LibraryId.parse` on `MechaDK_Std` and on `MechaDk_Std`. If `MechaDK_Std`
parses, rename the code prefix `MechaDk` to `MechaDK` (namespace, `MechaDk.csproj`, `MechaDk.slnx`,
`src/MechaDk/`, `Native.targets`, scripts); until then it stays `MechaDk`.

Verified: the Linux Debug build shows "Mecha DK 1.0" and "Make it so". Not verified: every other
platform, as in Addendum 4. Committed with `[skip ci]`.

## Addendum 6: the code prefix is `MechaDK` (2026-10-09)

The code prefix was renamed from `MechaDk` to `MechaDK`, on the condition that `MechaDK_Std` is a valid
MlFront library id. **It is.** Checked with `@dkjs/cli` 2.4.3022 (maintainer jonahbeckford), command
`dkjs lua -e 'm = require("modver")' -e 'r, e = m.parse("MechaDK_Std.Tested@1.0.0")' ...`:

| Id | Result | vendor / qualifier / unit |
|---|---|---|
| `MechaDK_Std` | parses | Mecha / DK / Std |
| `MechaDk_Std` | parses | Mecha / Dk / Std |
| `MlFront_Std`, `CommonsBase_Std`, `DkZero_Exec`, `CommonsLang_OCaml`, `CommonsBase_GNU`, `NotMitEdu_Kerberos` | parse | controls |
| `Mecha_Std`, `mechaDk_Std`, `MECHADK_Std`, `Mecha__Std` | rejected ("Could not parse the module id") | negative controls |

Caveats: this release exposes only `modver.parse` (a module id plus version), not a library-only parser, so
this is the module id parser splitting the library part with the `LibraryId` accessors, close to but not
the same call as `MlFront_Core.LibraryId.parse`. The engine's Lua is version 2.5 and has no `for` loops
and no `local` in the REPL, so use one statement per `-e`.

What changed: `src/MechaDk/` to `src/MechaDK/`, `MechaDk.csproj` to `MechaDK.csproj`, `MechaDk.slnx` to
`MechaDK.slnx`, the `MechaDk` namespace and every `MechaDk` identifier (for example `MechaDKNativeSrcArg` in
`Native.targets`). Not changed: the lowercase `mechadk_native`, `mechadk_make_it_so`, `libmechadk_native`
and `com.diskuv.mechadk`, and the executable names `mecha-dk` and `mecha-dk.exe`. A case-only rename of a
directory can confuse an existing macOS checkout; a fresh clone is fine.

Verified on Linux: desktop publish, desktop, web and Android debug builds all succeed, with 0 warnings; the
desktop and web apps draw "Mecha DK 1.0" and "Make it so". Not verified: Windows, macOS, iOS, any CI run
(committed with `[skip ci]`).

## Addendum 7: the CI verification is complete (2026-10-09)

The repository was made public by the maintainer to get free Actions minutes after the monthly limit was
reached (it must be set back to private by the maintainer; the proxy blocks visibility changes from the
agent). The testing finished the same day, so the Nov 1 routine was deleted.

**Builds.** `build.yml` run 37996597989 on `d638977`: all 9 jobs green (linux-x64, linux-arm64, win-x64,
win-arm64, osx-x64, osx-arm64, web, android, ios).

**Launch.** `launch.yml` (manual only) run 37996601022 on `d638977`; every launch screenshot was viewed and
shows "Mecha DK 1.0" and "Make it so":

| Platform | Evidence |
|---|---|
| Linux (ubuntu-24.04, Xvfb) | the window; no title bar under Xvfb |
| Windows (windows-2025) | title bar "Mecha DK" |
| macOS (macos-15) | `Mecha DK.app` started with `open`; menu bar and window title "Mecha DK" |
| Android (emulator, API 34 x86_64) | the app on the emulator screen |
| iOS (macos-26 simulator) | the app on the simulator screen, console log shows Uno startup |
| Web | container screenshot (Playwright, earlier commit; same code) |

**What the last failures were and what fixed them.**
- Android emulator: `avdmanager` created the AVD under `~/.config/.android/avd` and the emulator searched
  `~/.android/avd`; fixed by setting `ANDROID_AVD_HOME` (`a3a4384`). An earlier hang came from `adb
  wait-for-device` with no timeout (`64da909`), and an earlier failure from a cleanup step that deleted
  `/opt/microsoft`, where `pwsh` lives (`ec85ba9`).
- iOS simulator: the unsigned app was killed at startup with `SIGKILL (Code Signature Invalid)` inside dyld
  loading a dependent dylib. `codesign --deep` left a loose dylib unsigned; signing every Mach-O file and
  then the bundle fixed it (`d638977`). A fresh simulator also needs about 45 seconds to settle (`64da909`).
- Windows title: the window said "Uno Platform"; fixed by setting the window title (`06d674e`).

**Not verified.** Say so rather than assume.
- `win-arm64`, `osx-x64`, `linux-arm64` were built, not launched. The published single-file `mecha-dk.exe`
  and `mecha-dk` were not launched in CI (launch uses the debug build; macOS uses the published bundle).
  A single-file `mecha-dk` was run locally before the `MechaDK` rename only.
- Signing: `Mecha DK.app`, `mecha-dk.exe` and the iOS build are unsigned, by choice. The iOS simulator app
  is signed ad hoc only inside the launch job.
- The Android launch job was green on the public repo's larger runners. The earlier runner deaths happened on
  the private repo's smaller runners (probably out of memory), so it may die again once the repo is private.
- Documentation commits after `d638977` carry `[skip ci]`, so there is no `build.yml` run on the final head.
  They change only `planning/` and `README.md`.

**Open items that are the maintainer's choice:** signing and notarizing, launching the other RIDs, the UI
design (started in a separate session), and the Mecha DK command line tool name `dk`.
