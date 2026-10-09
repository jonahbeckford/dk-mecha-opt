# dk-mecha-opt

Coordinator's record for the dk mecha optimization harness, and the **Mecha dk 1.0** app it works on.
dk mecha is a .NET GUI for submitting and solving problems with a "mecha": an assistant guided by a
human. Agent instructions are in `AGENTS.md` (`CLAUDE.md` imports it).

## Layout

- `AGENTS.md` - the lean agent index, loaded every session.
- `CLAUDE.md` - `@AGENTS.md`, so Claude Code loads the same index.
- `.ai-skills/` - agent skills, also the Claude Code plugin root (see `.ai-skills/README.md`).
- `.claude-plugin/marketplace.json` - the marketplace entry, `source: "./.ai-skills"`.
- `src/MechaDk/` - the Uno Platform app (single project, XAML, Skia renderer).
- `native/` - one C function, `mechadk_make_it_so`, built by CMake. It stands in for the OCaml code
  to come, which will be built as a DLL, a static library and WebAssembly.
- `global.json` - pins the .NET SDK floor and the Uno SDK version.
- `scripts/` - setup, validation, build and screenshot scripts, all PowerShell 7.
- `.github/workflows/build.yml` - builds every platform. `launch.yml` starts the app (manual, see CI).
- `planning/` - plans of record. `2026-10-mecha-dk-scaffold.md` is the scaffold plan, with the current
  state and the scheduled follow-up at its end.

Script names are lowercase kebab-case (`scripts/*.ps1`).

## Targets

| Target | Framework | Output |
|---|---|---|
| Windows, macOS, Linux | `net10.0-desktop` | `mecha-dk.exe`, `Mecha dk.app`, `mecha-dk` |
| Web | `net10.0-browserwasm` | `wwwroot` |
| Android | `net10.0-android` | APK |
| iOS | `net10.0-ios26.0` | app (macOS only) |

Desktop publishes to a self-contained single file: **`mecha-dk`** on Linux, **`mecha-dk.exe`** on Windows. On
macOS it is the bundle **`Mecha dk.app`**, with `Contents/MacOS/mecha-dk` (not a single file, so it can be signed); `build.ps1` assembles
the bundle itself, because Uno.Sdk has no packaging step for the desktop head. The app is shown to
people as "Mecha dk".

**The GUI is `mecha-dk`, so that `dk` stays free for the command line tool.** MlFront already produces a
`dk` executable, and this app is meant to absorb that OCaml code through the C binding. A GUI and a CLI
need separate executables on Windows (the console and GUI subsystems are fixed in the executable), and a
macOS GUI has to be an `.app`, so the GUI has its own name. Do not rename the GUI back to `dk`.

## Set up a machine

```sh
pwsh -File scripts/setup-dev-machine.ps1                 # reports what is missing, installs nothing
pwsh -File scripts/setup-dev-machine.ps1 -InstallTools   # installs it
pwsh -File scripts/validate-dev-machine.ps1              # proves the machine is ready; never builds
```

It covers the .NET SDK, the `android` and `wasm-tools` workloads (`ios` on macOS), CMake, Ninja and a
C compiler, JDK 17, the Android SDK and NDK, Node and a Playwright Chromium, and on Linux `xvfb` and
ImageMagick. Xcode is only reported, never installed. Versions are pinned in `scripts/dev-common.ps1`.

## Build

```sh
pwsh -File scripts/build.ps1 -Target desktop            # also: web, android, ios, all
pwsh -File scripts/build.ps1 -Target desktop -Publish   # mecha-dk, mecha-dk.exe or Mecha dk.app under artifacts/publish/
pwsh -File scripts/build.ps1 -Target all -Publish
```

`-Target all` is every target the host can build; iOS builds only on macOS. A bare
`dotnet build src/MechaDk -f net10.0-desktop` also works, and runs CMake.

**The native library is built for the host only.** Each desktop runtime identifier is therefore
published on its own OS and architecture: `win-*` on Windows, `osx-*` on a Mac, `linux-*` on Linux.
Publishing another RID fails early with a message saying where to build it. CI has a runner for each.

**iOS is pinned to the iOS 26.0 SDK** (`net10.0-ios26.0`). Plain `net10.0-ios` resolves to the newest
workload pack, which needs the newest Xcode. Raise the pin in `MechaDk.csproj`, `Native.targets` and
`build.ps1` together. The 26.0 SDK checks the Xcode version to the minor release; CI builds with the
image's default (newest) Xcode and `-Property ValidateXcodeVersion=false`, and that is the only combination
verified. CI needs no Xcode setup. Measured on `macos-26`: the build passes with no `xcode-select`,
`DEVELOPER_DIR`, `MD_APPLE_SDK_ROOT`, Xamarin `AppleSdkRoot` or `-runFirstLaunch`, each alone and all
together. It fails if `xcode-select` is pointed at the alias `Xcode_26.6.0.app` (a symlink to
`Xcode_26.6.app`): the asset catalog step then cannot locate the SDK under the alias path. Selecting
`Xcode_26.0.app` also failed in the probe; its error was not read.

**Signing and notarizing are not done.** `Mecha dk.app`, the Windows executable and the iOS build are
unsigned, and no certificate or identity is committed.

## Look at it

```sh
pwsh -File scripts/take-screenshot.ps1                  # desktop; on Linux with no display it uses xvfb
pwsh -File scripts/take-screenshot.ps1 -Target web
```

On macOS the desktop screenshot launches the `Mecha dk.app` bundle that `build.ps1 -Publish` assembles, with `open`, not `dotnet run`.
Writes `artifacts/screenshots/<target>-<os>.png` and prints the path, so it works over Remote Control
or in a cloud instance. It builds first through `build.ps1` unless `-NoBuild`.

## CI

`.github/workflows/build.yml` runs `build.ps1` on a runner per platform: six desktop RIDs, web,
Android, and an unsigned iOS simulator build.

`.github/workflows/launch.yml` starts the app and saves a screenshot as a workflow artifact: the
desktop app on Linux, Windows and macOS (through `take-screenshot.ps1`, which on macOS launches the
`Mecha dk.app` bundle), the Android build in an emulator, and the iOS build in a simulator. **It runs only
on request** (Actions tab, Run workflow), because the macOS and Windows jobs are billed at a multiple
of Linux minutes and used up a month of them when it ran on every push. A job passes when a
screenshot file of at least 1 KB exists, so look at the images: a pass does not show the app on
screen. The iOS simulator kills an unsigned app at startup (`Code Signature Invalid`), so that job
signs the bundle ad hoc, with no identity, before installing it.
