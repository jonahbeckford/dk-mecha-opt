# Plan: dk0-learn-serves-the-mecha-dk-gui

**Status:** QUEUED 2026-10-09. The requests are recorded verbatim. None of the five threads is
gathered, so no cycle may treat this document as applicable. Promote it to PROPOSED by writing the
threads, never by editing this line alone.
**Window:** between cycles, after one ends and before the next begins. A plan in
`lifecycle/plans/` runs between cycles: after one ends, before the next begins.
**Request:** (verbatim, maintainer 2026-10-09, in the Mecha DK UI design session on
jonahbeckford/dk-mecha-opt)

> `dk0 learn report` should have an option to output `.typ` or `.pdf` or `.png` or `.svg`. We need a
> mechanism for you to update the dk-engine-opt design as we uncover things we need.

The other requests below come from the same session, quoted from the maintainer's own messages there.
They are gaps that the Mecha DK design found in `planning/2026-09-bayes/design.typ`.

## Origin

Mecha DK 1.0 is the .NET (Uno Platform) GUI in jonahbeckford/dk-mecha-opt for posing problems and
hypotheses and running `dk0 learn` cycles. It is meant to absorb the dk OCaml code through a C binding.
Its UI design (a private artifact, not committed anywhere) was built from Paper I section 2 and
design.typ part 4. While designing it, these points came up where the GUI needs something the design
document does not yet say. This QUEUED plan is the handoff. The Mecha DK session did not edit
design.typ or anything else in this repository.

## The requests

### R1. `dk0 learn report` chooses its output format

> `dk0 learn report` should have an option to output `.typ` or `.pdf` or `.png` or `.svg`.

Today design.typ says `dk0 learn report` renders "a Typst document deterministically from the state"
with `--kind cycle|frontier|scorecard|review|window` (the subcommand table, `@p1-s4-4-1`, about line
1297; C57 at about line 2446), and section `@p1-s4-14` describes the output as Typst "compiled to
PDF". The request adds a format option. Context from the Mecha DK session, for the threads to verify:

- The GUI shows reports as rendered pages, SVG or PNG (maintainer: "show the rendered SVG or PNG which
  should work in all the platforms"). Uno Platform documents SVG as supported on all its targets, and
  PNG works everywhere through its ordinary image control.
- Typst is a Rust library. `typst-svg` and `typst-render` (raster export, version 0.15.1, Apache-2.0)
  give SVG and PNG output. typst.ts compiles Typst to WebAssembly for the browser. typst_flutter shows
  Typst built from source for Android and iOS through Rust FFI. None of this was built or tested.
- **The determinism contract of `@p1-s4-14` must say what it covers for raster output.** A PNG depends on
  the rasterizer version and the resolution, as well as the data and the template. The threads should
  decide whether the contract pins the Typst version and the pixel density, or whether only `.typ` and
  `.pdf` (or `.svg`) are held to it.

### R2. Posing a hypothesis directly

> There are two primary task flows. The second is a human creates a project, poses hypotheses and
> cycles the mecha ... observing the progress of hypotheses (the first the primary task flow observed
> the progress of problems), authorizing decisions and reviewing outputs.

design.typ has `pose-dk-problem` for problems. It says a novel hypothesis "from reflection or a
revelation" still meets the refinement gate, and that the same check places a newly posed hypothesis
under the node it best refines. But the `dk0 learn` subcommand table has no operation by which a human
poses a hypothesis. The GUI needs one: a hypothesis entered by the human, placed by the matcher, and
checked at DROP like any other.

### R3. Run cycles until an attended stage

> Pacing: yes, cycles run back to back until an attended stage.

`dk0 learn cycle` runs one cycle, or one stage with `--stage`. The GUI's pacing is to run cycles back to
back and stop when a cycle reaches an attended stage (AUTHORIZE, REVIEW or SLEEP) in an attended window.
The threads should decide whether that is a `dk0 learn cycle` option, part of the unified driver
(`@p1-s4-5-4`), or GUI logic over single-cycle calls.

### R4. The engine, and so Typst, runs inside the app on every device

The Mecha DK session asked: "Does that engine run inside the app on every device, through the C
binding?" The maintainer answered (verbatim, 2026-10-09):

> Yes, through the C binding.

So `dk0 learn report` runs in-process on Windows, macOS, Linux, the web (WebAssembly), Android and iOS.

### R5. How `dk0 learn report` gets Typst: a spawned asset, and `.typ` only without spawn

The maintainer's design (verbatim, 2026-10-09):

> For all platforms that have a "spawn" (I think every platform except WASM), the dk0 build system can
> download a Typst asset (https://diskuv.com/dk/help/latest/specification/assets/) and spawn the Typst
> compiler ... similar to how there is an embedded GitHub CLI asset that is used for dk0 build system
> attestation verifications. For WASM any `dk0 learn report` option that is not `.typ` should just fail,
> since it has no spawn. The WASM Mecha UI should render the `.typ` into a SVG (preferred over PNG since
> partially accessible) itself using typst-wasm.

So the engine never links Typst. It writes `.typ`, and for `.pdf`, `.png` or `.svg` it spawns a Typst
compiler fetched as a dk asset (pinned by SHA-256, as the asset spec requires). Without spawn,
`--format` other than `typ` fails, and the GUI renders the `.typ` itself. "typst-wasm" in the quote
names the role. The maintained browser build found was typst.ts (`@myriaddreamin/typst-ts-web-compiler`
and `-renderer`), whose packages were release candidates when checked.

**Platforms that may lack spawn besides WASM, for the threads to verify.** Found by the Mecha DK session
from vendor sources, not tested on devices:

- **iOS: no spawn.** Apple DTS states that `posix_spawn`, `system()` and other child-process mechanisms
  are not supported for iOS apps (developer.apple.com/forums/thread/747499 and thread/87849). So iOS
  is in the same position as WASM: `.typ` only, rendered by the GUI. The GUI would need Typst linked as
  a library there (Rust, static, `aarch64-apple-ios`), unlike desktop.
- **Android: spawn exists, but not of a downloaded file.** Apps targeting API 29 or later cannot
  `execve()` files in their writable home directory, which is a W^X violation (Android 10 behavior
  changes, "removed execute permission for app home directory"). A downloaded Typst asset therefore
  cannot be spawned. A binary packaged inside the APK as a native library can be. So on Android the
  Typst compiler ships in the app, not as a downloaded asset, or Android also goes `.typ`-only.
- **macOS:** a sandboxed Mac App Store app may launch only helpers embedded in its bundle. `Mecha DK.app`
  is unsigned and not sandboxed today, so a downloaded asset can be spawned. That changes if it is
  ever distributed through the Mac App Store.
- **Windows and Linux:** no restriction found.

**Maintainer decision (2026-10-09).** Asked whether Android and iOS should be treated like the web (dk0
writes `.typ`, and the app renders it to SVG with a Typst library built into the app) or whether the
Typst binary should be packaged inside the Android app so dk0 can still spawn it, the maintainer chose
the first, answering:

> yes

So `dk0 learn report` spawns a Typst asset only on desktop (Windows, macOS, Linux). On the web, Android
and iOS, every `--format` other than `typ` fails, and Mecha DK renders the `.typ` to SVG itself.

The threads should decide the rule's shape: "has spawn" as a capability `dk0` detects at run time, or a
per-platform list. Either way the failure message for an unsupported `--format` should name the
platform and say to use `typ`.

### R6. DISPATCH can run its experiments inside MXC

> The DISPATCH stage should optionally be run with https://github.com/microsoft/mxc.

(verbatim, maintainer 2026-10-10.) MXC, the Microsoft eXecution Container, describes itself as
"Policy-driven, layered isolation and containment" for untrusted code such as model output, plugins and
tools. What the Mecha DK session read on its README (not tested):

- **Platforms:** Windows 11 (default backend `processcontainer`), Linux (`bubblewrap`) and macOS
  (`seatbelt`), x64 and ARM64. Android, iOS and the web are not mentioned. Other backends (Windows
  Sandbox, MicroVM, Hyperlight, IsolationSession) are marked experimental.
- **Interfaces:** SDKs for Rust (`mxc-sdk`), .NET (`Microsoft.Mxc.Sdk`) and Node (`@microsoft/mxc-sdk`), and
  per-platform executor binaries (such as `wxc-exec.exe`) that take a JSON container request.
- **Policy:** filesystem (read-only, read-write, denied paths), network (proxy and outbound controls) and
  UI (clipboard, display). MIT licensed. No release was listed when checked.

How it meets the design, for the threads to verify:

- design.typ already says DISPATCH runs each experiment "in its own isolated worktree", and that the
  unified driver enforces each SUO's boundary, "model-written code in a container or on a remote"
  (`@p1-s4-5-1`, `@p1-s4-5-4`). AGENTS.md says of this repository's execution boundary: "Nothing enforces
  this". MXC would be one enforcement, as an option per project.
- A worktree isolates files from other experiments. MXC would add process, filesystem and network
  policy. The SUO declaration (edit surface, boundary) is a natural source for the filesystem policy,
  and the boundary's "release credentials" exclusion maps to denied paths.
- dk0 is OCaml. The executor binaries with JSON requests fit a spawned dependency (like the Typst asset
  in R5, so a dk asset pinned by SHA-256); the Rust SDK would need a C interface.
- **Where DISPATCH runs without spawn.** R4 and R5 say the engine runs inside the app on the web,
  Android and iOS, where it cannot spawn. DISPATCH runs agents and builds, which need spawn and an OS
  sandbox, so it cannot run locally on those platforms, with or without MXC. The design has to say
  where an experiment runs when the app is on a phone or in a browser (a desktop or a remote the app
  hands the batch to, or DISPATCH unavailable there). The Mecha DK session asked the maintainer this on
  2026-10-10.

### R7. DISPATCH runs on remote executors through `dk0 remote`

The maintainer's answer to "where do experiments run on the web, Android and iOS" (verbatim,
2026-10-10):

> The experiments should be able to run on a remote executor: GitHub Actions, a Diskuv SaaS, etc. There
> is already a dk0 remote command ( https://diskuv.com/dk/help/latest/dk0/commands/ ) that supports
> GitHub Actions (but that will download and spawn the gh CLI), and more remote environments can be
> added. So there will need to be a login and forgotten password and usage flow for the SaaS remote
> executor. For GitHub Actions, there will need to be a repository selection/creation and auth screen
> (gh auth login). In all cases, the execution should be through dk0 remote command which will also be
> available through the C binding. Since failures are expected if the remote module requires spawning
> on platforms that cannot spawn, the platform itself should know which remote modules it is allowed to
> run.

What the public `dk0` command reference says today: `remote UI_MODULE@VERSION [REMOTE_OPTION=VALUE...]
[REPOSITORY] COMMAND...` runs on "a remote execution engine". `GitHub@0.1.0` expands to
`CommonsBase_Remote.GitHub@0.1.0` and `BuildBuddy.Cloud@0.1.0` to `BuildBuddy_Remote.Cloud@0.1.0`. The page
defines no remote options, does not say what `REPOSITORY` means, and does not describe authentication
or how results return. Requirements this puts on the design, for the threads:

- **DISPATCH targets an executor.** Local (this machine, optionally in MXC per R6) or any `dk0 remote`
  module. All go through `dk0 remote` (or the local path) behind the C binding, never through
  GUI-specific code.
- **A per-platform allow-list of remote modules.** The platform declares which modules it may run (the
  GitHub module spawns `gh`, so it is desktop-only; a SaaS module that speaks HTTPS only could run
  everywhere). The GUI reads this list and shows a module it cannot run as unavailable, with the reason,
  instead of letting the run fail.
- **Interactive auth through the binding.** `gh auth login` prints a one-time code and a URL in a
  terminal. Through the C binding there is no terminal, so `dk0 remote` must hand the code, the URL and
  the outcome back to the caller as data the GUI shows.
- **GitHub Enterprise.** The maintainer (verbatim, 2026-10-10): "Allow for GitHub Enterprise as well. I
  think that needs a domain name." `gh auth login` takes `--hostname` ("The hostname of the GitHub
  instance to authenticate with", default `github.com`; cli.github.com/manual/gh_auth_login). The
  GitHub remote module therefore needs a host option, presumably a `REMOTE_OPTION`, carried through
  sign-in, repository listing and creation, and every run. The manual does not say whether the device
  code flow works on every Enterprise version, so the sign-in screen must show whatever verification
  URL `gh` returns rather than assume `github.com/login/device`.
- **GitHub repository selection and creation** must be operations the binding exposes (list the user's
  repositories, create one), so the GUI can offer them. The `REPOSITORY` argument presumably carries the
  choice; the reference does not say.
- **The Diskuv SaaS executor needs account operations:** sign in, sign out, forgotten password and a
  usage query. None of these exist in the reference. Whether they live in `dk0 remote`, in the SaaS
  module, or in the `dk1 learn serve` backend (design.typ `@p1-s4-13`) is for the threads.
- **Progress and results** of a remote experiment must stream back so the cycle screen can fill its
  DISPATCH rows as results arrive, and failures must carry a log the GUI can open.

### R8. A human is a DISPATCH executor, so a mecha can run ordinary scientific experiments

> Another DISPATCH choice is to a human! One uber goal i have not mentioned, is that a mecha should be
> able to manage normal scientific experiments.

(verbatim, maintainer 2026-10-10.) How it meets the design, for the threads:

- Paper I §2 already defines an experiment as a prompt, "the instructions a model or agent runs to
  measure the loss", and the account is loss-general: any loss "for which a measurement apparatus
  exists". A person carrying out a protocol and reporting the measurement is such an apparatus. A
  wet-lab or field SUO then declares its edit surface (the protocol or materials it may change), its
  measured surface, and its boundary (what the person must never be asked to do).
- **Executor shape.** R7 says "in all cases, the execution should be through dk0 remote". A human
  executor fits as a `dk0 remote` module that delivers the experiment to a person and returns their
  reported outcome. Whether that is a module, a SaaS feature, or a local inbox is for the threads.
- **Latency.** A human experiment can take hours or weeks. DISPATCH must not block the cycle on it. Paper
  I already allows a result to land late ("The batch interactions become visible at the next cycle's
  UPDATE"), so an outstanding human experiment stays pending across cycles and its outcome is folded in
  at whichever UPDATE follows its arrival. The value-of-information and cost terms (`c(n)`) must carry
  the person's time and materials, not only compute.
- **The reported outcome must match the loss form.** For a binary per-case outcome (Beta-Bernoulli) the
  person reports pass or fail per case; for a continuous one (normal-inverse-gamma) a value per case
  with its unit. The GUI builds the entry form from the SUO's declared loss and case space.
- **Trust.** Paper I takes only revelation and discovery as true, and a model verdict is a proxy. A
  person's measurement is evidence, not a revelation: it updates the posterior and does not bypass DROP or
  the gate. Whether a human result carries its own noise model or reliability prior is for the threads.
- **Who the person is, and shared state.** The maintainer (verbatim, 2026-10-10), answering who
  receives an experiment and how:

  > The person is you and collaborators you invite.
  > How do they get the experiment? Inside Mecha DK. But that presumes there is a state shared between
  > collaborators. That is only possible with Diskuv SaaS.
  > should authorize gate every experiment sent to a person? Yes

  So a person executor of "the PI alone" works with local state, and inviting collaborators needs the
  Diskuv SaaS to hold the shared project state, the invitations, the assignment of each experiment to a
  person, and the returned results. design.typ already has local and SaaS state (`@p1-s4-8`); the threads
  should say what of the tree and the pending experiments the SaaS shares, and what a collaborator may
  see and do (run experiments only, or also pose). Every experiment sent to a person is parked at
  AUTHORIZE until the PI approves it and picks who runs it.
- **What a collaborator may do.** The maintainer (verbatim, 2026-10-10): "They can pose hypotheses and see
  the whole tree." So the SaaS shares the whole tree with collaborators, and posing a hypothesis (R2) must
  record who posed it. Who besides the PI may AUTHORIZE is not yet decided.
- **SaaS accounts.** The maintainer (verbatim, 2026-10-10): "Password reset? Through email." and "Create
  accounts in the app? Yes". So the SaaS account operations of R7 are: create an account, confirm it, sign
  in, sign out, reset a forgotten password by an emailed link, invite a collaborator by email, and query
  usage.
- **One wording for all projects.** The maintainer (verbatim, 2026-10-10), asked whether the PI wording
  should carry through the whole app: "Yes. In fact, it would be better if we can unify the new project
  and new study pages." The GUI has one New project form, worded for a PI, with examples that cover both
  software and laboratory work. So no project-kind field is needed for wording.
- **Scientific wording.** The maintainer asked that the GUI word a scientific project "from the
  perspective of a principal investigator (PI)". The engine terms stay as they are; the GUI maps them
  (edit surface: "what the mecha may vary"; measured surface: "what you measure"; public spec: "protocol
  of record"; boundary: "out of bounds"; objective function: "what counts as a better result";
  revelations: "revelation", kept as the word (the maintainer, 2026-10-10: "I want the word \"revelation\" instead" of "statement" or "what the project takes as given"); problem: "research question").
- **Safety.** A protocol sent to a person is an instruction to act in the physical world. The SUO
  boundary has to be able to exclude hazardous steps, and AUTHORIZE (a spend) is the natural gate
  before a human experiment is sent.

### R9. LLMs are optional per role, configured in settings, and reachable portably

The maintainer (verbatim, 2026-10-10), asked whether the three assistant roles must be LLMs:

> LLMs will require a settings page (research how we can portably across platforms interact with LLMs).
> So LLMs shouldn't be the default.

design.typ `@p1-s4-5-5` already has each project name "which model each spawned role uses" and "its
endpoint (a local server such as Ollama, llama.cpp or LM Studio, or an API)", and says the coordinator
"needs no configuration". Requirements for the threads:

- **Every role accepts a non-LLM filler.** Research (IDEATE fan-out): people on the project, an LLM, or
  both. Writing the experiment (DISPATCH's prompt): the PI, or an LLM or coding agent. Judging: measured
  directly with no judge (Paper I: any loss "for which a measurement apparatus exists"; a model verdict is
  "a re-derivable proxy"), a person, or an LLM. The default is no LLM. With no LLM at all, the cycle still
  runs: humans pose and write, and SELECT, UPDATE and DECIDE are closed-form (Paper I §4).
- **Connections belong to the driver, not to `dk0 learn`.** Superseded by R10: `dk0 learn` never calls an
  LLM. The GUI edits named connections and per-role choices, and the driver (in Mecha DK, the app) makes
  the calls.
- **Two wire protocols cover most endpoints:** OpenAI-compatible chat completions (Ollama serves it at
  `/v1/chat/completions`; llama.cpp, LM Studio and vLLM also speak it) and the Anthropic Messages API. A
  .NET-side alternative is Microsoft.Extensions.AI's `IChatClient`, which the official Anthropic C# SDK
  and an Ollama client implement; that only helps if the GUI, not the engine, makes calls. The threads
  decide which side owns calls; R10 settles it: the driver, so in Mecha DK the .NET side.
- **Browsers.** A key typed into the web app is readable by page code. Anthropic's API refuses browser
  calls unless the request sets `anthropic-dangerous-direct-browser-access: true`; Ollama refuses other
  origins unless `OLLAMA_ORIGINS` allows them. So on the web, LLM calls should go through the Diskuv SaaS
  (keys held server-side) by default.
- **Keys at rest.** Uno's `PasswordVault` covers Windows, Android, iOS and Mac Catalyst, but not the web,
  Linux desktop or AppKit macOS (Uno docs, platform.uno/docs/articles/features/PasswordVault.html). Mecha
  DK's macOS and Linux builds are the Skia desktop head, so a key store for them (macOS Keychain, Linux
  Secret Service) must come from elsewhere, perhaps the engine. Keys never go in the project state.
- **Coding agents need spawn.** A role that edits code and runs programs is an agent harness, not a chat
  call, so it runs where DISPATCH runs (R6, R7), never inside the browser or phone app.
- **On-device models** (Apple's Foundation Models framework, Android's Gemini Nano) are platform-specific
  APIs; out of scope for 1.0 unless the threads find a portable route.

### R10. No `dk0 learn` command calls an LLM

The maintainer (verbatim, 2026-10-10), correcting the Mecha DK session's reading that design.typ assigns
model calls to the engine:

> Then the design doc needs changing. No dk0 learn command will be calling an LLM. That set of commands
> updates the state and calculates Bayesian statistics and makes reports.

So `dk0 learn` is state, Bayesian statistics and reports only. Every LLM call belongs to the driver
(`@p1-s4-5-4`, which already "performs only the parts that need an LLM").

**Storing is not calling.** The per-role configuration (which connection and model, or which person,
fills each role) is project data, so `dk0 learn` keeps it as state: `dk0 learn init` (about line 1292),
C40 (about line 2429), C54 (about line 2443) and `@p1-s4-5-5` stay as they are, except that their wording
should say `dk0 learn` stores the configuration and the driver acts on it. The state names a connection and
a model, never an API key; keys stay in each device's key store. (An earlier draft of this plan wrongly
moved `dk0 learn init` and C40 to the driver; the maintainer corrected it: "I had explicitly said that
state is the responsibility of dk0 learn.")

Places in design.typ where `dk0 learn` itself would make a model call, found by the Mecha DK session with
grep (line numbers at commit 24a0702; the threads must read each in context):

- About line 1343, the symmetric matcher (`@p1-s4-4-2`): "The abstraction step itself is a small-model call
  configured per role". The driver must perform the abstraction and hand `dk0 learn` the abstracted text;
  `dk0 learn` keeps the deterministic embedding and matching, and stores the abstraction as node state.
- C90 (about line 2479): "a node's scope is a MEMBERSHIP PROMPT template a language model evaluates on a
  case". Whoever evaluates it must be the driver or an experiment, not `dk0 learn`.
- M17 (about line 2379) and `@p1-s4-10`: "the producer's own LLM classifies" whether a package is
  general-purpose. That classification is a driver step.
- The REGRET backtest and DOC judge (about line 346) are model calls in the dk-engine-opt harness's own
  measurement (`eval/`), run by experiments, so they stay outside `dk0 learn` already; the threads should
  confirm the wording does not suggest otherwise.

Non-LLM models stay where the design puts them: the static distilled embedder (`model2vec` class) and the
encoder instruments (ModernBERT, Laya) are not LLMs. The threads should say whether the encoders run inside
`dk0 learn` (for DROP and the refinement gate) or are also a driver step, and state the rule so it is not
re-litigated.

Consequence for Mecha DK: the app is the driver, so it makes the LLM calls in .NET. The settings page
configures the app, not the engine; the browser and key-storage limits in R9 apply to the app.

### R11. A desktop app in the background is the driver; other devices connect over iroh

The Mecha DK session described the driver as the code that runs the cycle: it calls `dk0 learn` stage by
stage, stops at attended stages, fills the language steps from whoever each role names (a person or an
LLM), dispatches experiments, folds results back, and renders reports. In dk-engine-opt the driver is an
LLM agent (Claude Code running `run-engine-cycles`); in Mecha DK it is deterministic .NET code in the app.
Asked what drives a project when no app is open, the maintainer answered (verbatim, 2026-10-10):

> A desktop app running in the background drives a project. Similar to claude code remote control. Use a
> iroh network for communication.

Requirements for the threads:

- **The driver is a role, not an agent.** `@p1-s4-5-4` should define the driver by what it does, so that an
  LLM agent (dk-engine-opt) and deterministic code (Mecha DK) both fill it. Nothing in the loop may assume
  the driver is an LLM; with R9 and R10, a project with no LLM at all must still cycle.
- **One driver per project, on a desktop.** Phones and browsers are remote views and controls of that
  desktop: they show progress, take AUTHORIZE, REVIEW and SLEEP decisions, pose questions and hypotheses,
  and record human experiment results, all sent to the desktop driver. This revisits R4 and R5: whether a
  phone or browser still runs `dk0 learn` in-process (for reports, or for a project with no desktop) is for
  the threads to settle.
- **Transport is iroh.** Devices dial the desktop by its public key; iroh tries a direct connection and
  falls back to a relay that cannot read the traffic. In a browser every iroh connection goes through a
  relay (iroh.computer/docs/wasm-browser-support). Official bindings are Rust, Swift, Kotlin, Python and
  JavaScript; a C API (iroh-c-ffi) exists, and the only .NET binding found is the unofficial `N0.IrohNet`
  over that C API. The threads should say whether iroh links into the same native library as the engine
  (one C binding for both) or is bound separately.
- **Pairing.** A one-time ticket from the desktop, shown as a QR code and as words, that a new device
  redeems and the desktop approves, as in Claude Code's Remote Control. Paired devices are listed and can
  be removed. Relay: the maintainer chose (verbatim, 2026-10-10) "one Diskuv runs", not n0's public relays.
- **Sync when the desktop is off.** A phone keeps the last synced view; decisions and results queue until
  the driver is reachable.
- **Collaborators.** R8 put shared state in the Diskuv SaaS. Whether a collaborator also reaches the PI's
  desktop driver over iroh, or only the SaaS, is open, and so is how the desktop driver and the SaaS share
  one project's state.
- **The desktop app needs a background mode** (system tray on Windows and Linux, menu bar on macOS, start at
  sign-in). WinUI and Uno have no cross-platform tray control, so Mecha DK needs a small per-platform one.

### R12. Remote access: full control for SaaS subscribers, read-only links for anyone

The maintainer (verbatim, 2026-10-10):

> The human gated stages like REVIEW should be doable from the phone and web as well, and the actions like
> add a problem, add a hypothesis, etc should be doable.
>
> For web, there should be a read-only mode should be available ... that is needed to do a public demo on
> diskuv.com (which will use the hypothesis tree for MlFront and needs to be hosted on an iroh-connected
> server).
>
> The desktop should display a QR code with the iroh key wrapped in a diskuv signed, time-limited envelope
> for phones, and should have a web link to a diskuv.com WASM app with the same key and envelope. Only SaaS
> subscribers can use those ... which implies that phones AND web are only for SaaS. But I want web to be
> allowed readonly browsing ... so the desktop can create a readonly command channel with a separate
> readonly iroh key (time-limited envelope but no diskuv signing) that can be given for readonly web access.

Requirements for the threads:

- **Every attended act works remotely.** AUTHORIZE, REVIEW and CALIBRATE decisions, and posing a research
  question, a hypothesis or a revelation, are commands a phone or browser sends to the desktop driver
  (R11). The driver applies the first answer and the other devices update. This needs a defined command set
  over the iroh channel, each command mapping to a driver action or a `dk0 learn` state change.
- **Two channels, two keys.** A full-control channel, reached with the desktop's iroh key inside a
  Diskuv-signed, time-limited envelope (QR code for phones, a diskuv.com WASM app link for browsers), usable
  only by Diskuv SaaS subscribers. A read-only channel with its own separate iroh key inside a time-limited,
  unsigned envelope, for anyone with the link. The read-only channel must accept only read commands, enforced
  by the driver on that channel, not by the web app hiding buttons.
- **What the Diskuv signature binds.** The maintainer (verbatim, 2026-10-10): "Yes also include the
  subscribers identity. Which means the subscriber's identity or public key has to be known." So the
  envelope binds the desktop's iroh key, the expiry, and the subscriber's identity, and the desktop
  checks all three before accepting a device. The Mecha DK session's suggestion, for the threads to
  confirm or replace: the identity is the Diskuv account; each device that signs in to Diskuv receives a
  Diskuv-signed device certificate binding its own iroh key to that account; the envelope is a Diskuv
  signature over the desktop's iroh key, the account, the expiry and a one-time nonce; on connect the
  desktop verifies the envelope with a pinned (rotatable) Diskuv public key, rejects a reused nonce, and
  requires the connecting device's certificate to name the same account. Verification then needs no call
  to Diskuv at connect time.
- **Roles on the channel (maintainer, 2026-10-10: "Yes, full control for PI").** Full control means every
  command the driver accepts remotely (posing, AUTHORIZE, REVIEW, CALIBRATE, recording results, measurement
  change requests, the settings that apply immediately, pausing, creating read-only links), never screen,
  file or shell access. Approving devices, entering secret values, LLM credentials and stopping the driver
  stay on the desktop. A collaborator holds the role already decided in R8 (whole tree, pose hypotheses, run
  assigned experiments, request measurement changes) and never AUTHORIZE, REVIEW or CALIBRATE decisions.
- **Lost devices (maintainer accepted the recommendation, 2026-10-10).** Remove on the desktop stops a
  device's key at once; the Diskuv account page revokes its certificate and can sign out everywhere;
  certificates are short-lived (about 30 days, renewed while signed in) and the desktop checks Diskuv's
  revocation list when online, so an offline desktop still stops trusting a lost device within days. A
  lost desktop is revoked from the account page, which lists the secrets it held so they can be rotated.
- **Read-only links (maintainer accepted the recommendation, 2026-10-10).** Each link has its own
  read-only key, so revoking one stops only it, at once. Default expiry one day, maximum 30 days. The public
  demo's link, served from Diskuv's demo server, renews itself with no maximum.
- **Questions for the threads.** Whether the desktop also requires a
  local approval per new device. How a read-only link is revoked before expiry (rotating the read-only key).
  What a read-only view must not send (private revelations and rulings; compare C80, which redacts the
  maintainer's private rulings before the MlFront tree is published).
- **The public demos.** There are two (the maintainer, verbatim, 2026-10-10: "Another demo is the
  RunBugRun/Defects4J seeded tree. Now that we will have two public demos, there should be an option to open
  the demos (and perhaps the demos should be part of the Welcome page)."). The second is the shared tree grown
  from RunBugRun repairs and used to seed Defects4J runs (`cycle/defects4j/seed/`, `runbugrun-seed-tree.json`).
  Both open read-only, with no account, from the first welcome step and from a Demos section on the Projects
  page. The first demo is a read-only view of the MlFront hypothesis tree, served by a driver on an
  iroh-connected server rather than a desktop. So the driver must also run headless on a server, and a demo
  link needs a long or renewable expiry. The maintainer settled which tree it shows (verbatim, 2026-10-10):
  "A new tree is being created by dk-engine-opt for publication in Paper I. It is the adhoc tree but
  reshaped and run through a new Python harness." So the demo serves that Paper I tree, and the threads
  should say how it is loaded into a driver's state for serving.

### R13. Harness amendments: where they come from, what happens when one fails, and SLEEP without an LLM

The maintainer (verbatim, 2026-10-10):

> For SLEEP in particular, what if one of the harness amendments fails? I don't think the design covers
> this, and I don't think the UI covers it. And harness amendments require a LLM so projects without LLMs
> should not have a SLEEP stage. Also, where do harness amendments get proposed? Give me some suggestions
> for these questions.

What exists today, found by the Mecha DK session:

- design.typ says SLEEP "researches the harness amendments and B_dev cases the cycle warrants; the
  maintainer approves what carries forward to a re-baseline", and that applying one is "a deliberate
  re-baseline, kept out of the measured loop" (`@p1-s4-2`). It lists `dk0 learn amend` as "Plan and apply
  a harness amendment" (`@p1-s4-4-1`). A search of design.typ for rollback, revert or a failed amendment
  found nothing, so the design does not say what happens when one fails.
- This repository's own process does cover part of it: `plan-harness-amendment` gives a plan the statuses
  QUEUED, PROPOSED, APPROVED, APPLIED, VERIFIED and ROLLED BACK, a verification block with a dated
  `grace_until`, and a rollback section that warns rolling back a metric change "is not symmetric" (a
  second re-baseline). `amend-harness` keeps agent proposals in `proposals/<name>/`, which `frontier`
  prints at SELECT. None of this is in design.typ for `dk0 learn`.
- R10 conflicts with "`dk0 learn amend`: plan and apply": planning an amendment needs an LLM, so `dk0
  learn amend` can record and apply an amendment as state, while the planning is a driver step.

**Decided by the maintainer (2026-10-10),** after asking (verbatim) of a hand-made request "Won't that need
a LLM to interpret that request?" and confirming that project settings edits "don't get applied
immediately ... they are requests for edits". The maintainer approved these three:

1. **One "Measurement changes" list per project, from four sources.** (1) SLEEP's research, only with an
   AI model. (2) The PI's direct edit in project settings or a patch to measurement code; no LLM is needed
   because the edit is the change itself. A free-text request is accepted only when an AI model is
   assigned, and SLEEP turns it into a proposal. (3) A REVIEW protocol gap: a note for the PI without an
   LLM, a proposal with one. (4) A failed verification of an earlier change: likewise. Every item follows
   requested, proposed, approved, applied between cycles, then verified or rolled back. The PI's own
   request is approved by making it; a collaborator's or SLEEP's waits for the PI.
2. **Failure handling.** Changes are applied only in a break between cycles: the driver pauses cycles,
   applies approved changes one at a time in a fixed order, and stops at the first failure, undoing only
   that one. Failing to apply changes nothing and is undone automatically (the PI may edit and retry, or
   drop it). A failed re-baseline leaves cycles paused and offers a cheap roll back, since no new baseline
   was recorded, or fix and re-run. A failed verification by its `grace_until` is the PI's call: roll back,
   at the cost of a second re-baseline with the interim scores kept as historical, or keep it with a
   recorded reason.
3. **SLEEP exists only when a project assigns an AI model to the role "proposes changes to how results are
   measured"** (default: no one). Without it the cycle has ten stages.

**Project settings follow the `amend-harness` classes.** Outcomes, cases, weights and the judge (Metric)
and what may vary and out of bounds (Policy) and the protocol of record (Knowledge, unless a judge reads
it) change only by request, applied between cycles. Revelations change on passing the
contradiction check (a revelation is not an amendment). Executors, helpers, collaborators and
LLMs change immediately, because they do not change how results are measured.

For design.typ: SLEEP becomes conditional; `dk0 learn amend` records and applies an amendment as state
while the driver plans it (R10); and the amendment lifecycle, failure handling and the between-cycles
apply window, which today live only in this repository's `plan-harness-amendment` and `amend-harness`
skills, need a home in the design for any SUO.

### R14. Re-baselining for `dk0 learn`

The maintainer asked (2026-10-10) how re-baselining works in Mecha DK and in the design, whether it needs
an LLM, and for suggestions if it is unspecified. What exists: `amend-harness` (bump
`eval/HARNESS-VERSION`, re-score trunk "before any further comparison", record old and new baselines side
by side, report what became historical); design.typ (trunk score cached and "recomputed only when trunk
moves or the harness re-baselines"; a checkpoint upgrade forces a re-baseline, re-scores soft priors and
re-runs recorded refusals; Paper I's paired node-against-baseline comparison). Not specified: what happens
to the tree's posteriors, which were measured under the old ruler.

Re-baselining needs no LLM of its own: it re-runs the measurement on the baseline, so it needs whatever the
measurement needs (nothing for direct measurement, an LLM for an LLM judge, a person's time for a person).

The maintainer approved (verbatim, 2026-10-10: "I agree with your R14 plan. 3a."):

1. **Recompute before re-measuring.** Paper I's loss is a weighted sum of terms and often a per-case mean,
   so `dk0 learn` stores per-case, per-term results. Then a weight change recomputes with no experiment;
   removing a case recomputes (per-case loss); adding a case measures only that case; changing a judge,
   its prompt, scoring code or a checkpoint re-measures the baseline in full. Policy and Knowledge
   changes need no re-baseline.
2. **Version the measurement.** Each Metric change bumps a measurement version in `dk0 learn` state, and
   every observation records the version it was measured under. This should share one mechanism with the
   apparatus signature of C79.
3. **(3a) Carry evidence forward.** A node measured under an older version keeps that evidence as history
   and starts the new version from an informative prior built from it, with widened uncertainty, the
   transfer the design already uses for commons nodes ("an informative prior on the delta over the
   project's own baseline"). The frontier re-ranks and value of information decides what is re-measured
   first. (Rejected: re-measure every open node at once; discard old evidence.)
4. **A costly re-baseline is a spend.** Its cost is shown when the change is requested, and a re-measurement
   that needs money or a person's time parks at AUTHORIZE.
5. Only a re-measurement can fail at the baseline step; a recompute cannot.

And a GUI rule (verbatim): "the UI should warn the user what will happen after a re-baseline (ex. the
uncertainty will be widened, in user friendly language) if it knows a re-baseline is required for an
action." So `dk0 learn` must be able to tell the driver, before a change is applied, which of the cases in
item 1 it falls in and what it will cost, so the warning is computed rather than guessed.

### R15. The GUI can show each posterior as a curve and as its formula

> Right now, the user interface shows a ninety percent interval. There should be an option to show the
> real distribution curve and the formula (ex. `Beta(0.5, 2.3)`) as well.

(verbatim, maintainer 2026-10-10.) The GUI keeps the interval bar as the compact default and adds a
"Distribution" view per hypothesis (density curve, shaded 90% interval, mean, and the formula), plus an
option to show curves in the tree list. For this `dk0 learn` must expose, per node and per measurement
version (R14), the posterior's family and parameters: Beta(a, b) for a proportion and the Student-t
marginal of the normal-inverse-gamma for a continuous loss (Paper I §4), and where a quantity is not a
named conjugate posterior (the option value `V(n)`, a moment-approximate backup), say so, so the GUI labels
it "approximately" rather than printing a formula that is not the real distribution. Drawing the curve is
the GUI's job (a custom chart control in Uno, from the family and parameters); `dk0 learn` need not sample.

### R16. Executor environments: repositories, secrets, environment variables, and agent credentials

The maintainer (verbatim, 2026-10-10):

> I don't know where "claude setup-token" fits in the UI. It should be there for desktops.
>
> I expect executors to need one or more git repositories, and maybe secrets, and maybe environment
> variables. Similar to how claude code cloud behaves.

GUI decisions in the Mecha DK design: a per-project "Experiment environment" page with one or more
repositories (each with a branch, tag or commit, and whether the mecha may change it or only read it),
secrets, and environment variables, applied to every machine executor (this computer, GitHub Actions,
Diskuv SaaS) and not to a person. Desktop Settings, LLMs, has a Claude Code entry whose "Get a token" runs
`claude setup-token` on the desktop (browser sign-in to a Claude Pro or Max subscription), keeps the token
in the desktop's key store, and hands it to experiments as the secret `CLAUDE_CODE_OAUTH_TOKEN` (the name
claude-code-action's docs use; one third-party source says the token lasts a year, unconfirmed).

Requirements for the threads:

- **The environment is project state, secrets are not.** Repositories and variables belong in `dk0 learn`
  state; secret values never do (only their names and which executors receive them). Each executor
  receives secrets its own way: the desktop key store locally, a repository's Actions secrets on GitHub
  (R7), the subscriber's vault on the Diskuv SaaS. `dk0 remote` needs a way to pass them.
- **Repositories and the SUO.** A repository the mecha may change is part of the edit surface, so adding
  one or switching it to changeable is a Policy request applied between cycles (R13); it follows its branch,
  since the mecha's adopted changes move it and the baseline tracks that. **Decided (maintainer accepted the
  recommendation, 2026-10-10):** a read-only repository is pinned to a tag or commit, and moving the pin is
  a measurement change (R13, R14). The maintainer declined (2026-10-10) an option to let a read-only repository
  follow a branch and refresh its pin between cycles: "I don't want that option."
- **Variables and measurement. Decided (maintainer accepted the recommendation, 2026-10-10):** each
  environment variable carries a "Can change results" flag, on by default. Changing a flagged variable is a
  measurement change (R13, R14); an unflagged one applies immediately; changing the flag is itself a
  request, so it cannot be used to slip a change past the rule. A variable has one value for every
  executor, so results from different executors stay comparable.
- **Agent credentials are the driver's.** Running `claude setup-token` needs spawn and a browser, so it is
  desktop-only, consistent with R5 and R11. Other coding agents' credentials follow the same pattern.

### R17. Rename SLEEP to CALIBRATE

The maintainer said SLEEP "does not fit the other stages" and, offered CALIBRATE, AMEND or RETOOL (with
ARRANGE, ORGANIZE and REFINE advised against), chose (verbatim, 2026-10-10): "I pick CALIBRATE." The other
ten stages name what the cycle does; this stage proposes changes to how results are measured, which is
calibrating the instrument. design.typ chose SLEEP deliberately, as a metaphor for memory consolidation
(`@p1-s4-2`: "the name is chosen, not a placeholder"), so this supersedes that decision.

The rename touches design.typ (`@p1-s4-2` stage table and its SLEEP paragraph, the attended-stages text, and
every later mention), Paper I (Algorithm 1 step 10 and §2's list of attended stages), this repository's
skills and `METHOD.md` where they name the stage, and the `dk0 learn` stage names (`--stage`). The threads
should list every occurrence and say whether `cycle/` (which ships verbatim in the paper) is affected.
Elsewhere in this plan, SLEEP means the stage now named CALIBRATE; quotations keep their original wording.

### R18. Collaborators can gain full control by prompt injection, and the PI must be told

The maintainer (verbatim, 2026-10-10):

> Also, for collaborators, they can gain full control through prompt injection attacks ... that must be
> made clear to the PI in the UI and elsewhere (security docs accessible through dk-engine-opt).

The path: text a collaborator writes (a hypothesis, a note, an experiment result) is read by the project's
LLM roles and coding agents (R9), which act with the PI's credentials, secrets (R16) and edit surface. Text
crafted to steer an LLM can make it act as if the PI asked, including wording a request so the PI approves
it. The role limits of R12 do not stop this.

Requirements:

- **A security document in dk-engine-opt**, reachable from the GUI's warnings, that states this threat
  plainly, lists what it can reach (secrets given to executors, repositories the mecha may change, the PI's
  approvals), and lists the mitigations that exist and what each does not stop: AUTHORIZE before every
  experiment, MXC sandboxing (R6), scoping secrets to executors (R16), the execution boundary. It must not
  imply the mitigations remove the risk.
- **The GUI warns in three places** (drawn on the canvas): the Collaborators page, Settings, LLMs, whenever a
  project has collaborators, and the invitation step. Each links to the security document.
- **For the threads:** whether the driver should mark collaborator-written text as untrusted when it hands
  it to an LLM, and whether a project with collaborators should require MXC (or another sandbox) for
  coding agents.

### R19. Diskuv SaaS: module name, credits, and LLM provider

The maintainer (verbatim, 2026-10-10): "Use your recommendation for saas usage unit. For SaaS module name,
use CommonsBase_Remote.DkCloud. for saas as a llm provider, yes."

- **Module:** `CommonsBase_Remote.DkCloud`, alongside `CommonsBase_Remote.GitHub` (R7).
- **Signing in (maintainer, verbatim, 2026-10-10: "Passkey first, NIST password. Also allow TOTP 2nd factor.
  Also email based auth like claude code.").** Passkeys first; a password allowed as an alternative under a
  NIST SP 800-63B style rule (at least 12 characters, any characters, checked against breached passwords, no
  forced composition or expiry); sign-in by a link emailed to the account; an optional TOTP authenticator as
  a second factor. Terms of service and privacy policy live on diskuv.com, but (maintainer, verbatim,
  2026-10-10) "Those terms need to be changed to include Mecha DK and the SaaS." That is a change to the
  site-diskuv-com repository, which dk-engine-opt can reach; the threads should record it as a dependency of
  the SaaS launch and hand it to that repository. Topics the Mecha DK session suggests the updated terms
  and privacy policy address, drawn from this plan (a list for the authors and a lawyer to settle, not
  legal advice):
  - **Scope.** Mecha DK (desktop, web and phone apps), the Diskuv SaaS executor `CommonsBase_Remote.DkCloud`,
    the Diskuv relay (R11), the diskuv.com web app, and read-only links (R12).
  - **Running experiments.** Experiments run on Diskuv's machines with repositories, environment variables
    and secrets the user supplies (R16); what Diskuv may and may not do with them; isolation between
    accounts; that the user is responsible for what experiments do and for anything they send to a person
    (R8).
  - **LLMs.** Prompts and outputs sent through the SaaS go to AWS Bedrock models (R19); which data leaves
    Diskuv, under whose terms, and whether any of it is used for training.
  - **Secrets and credentials.** How secrets and agent tokens such as `CLAUDE_CODE_OAUTH_TOKEN` are stored,
    who can read them, and that they are never placed in project state or reports (R16).
  - **Collaboration.** Content collaborators add to a shared project; who owns it; that the PI controls
    access; and the prompt-injection risk of R18, stated in the terms as well as in the app.
  - **Read-only links and the public demo.** Anyone holding a link can read the project until it expires;
    what is withheld (private rulings, C80).
  - **Device and account data.** Device certificates, pairing, passkeys, TOTP and recovery codes, emailed
    sign-in links, and the relay, which carries encrypted traffic it cannot read.
  - **Credits and billing.** Monthly credits for experiment minutes, LLM use and storage (R19); what happens
    at the limit; refunds.
  - **Retention and deletion.** How long project state, experiment logs, reports and uploaded files
    (photos and instrument exports from R8) are kept, and how a user deletes an account and its data.
  - **Model availability.** Offered models change as AWS retires them (R19), so a project's model may stop
    being offered.
  - **Research use.** Scientific studies may handle research or human-subject data; the user's own ethics
    and approval obligations remain theirs (the "Out of bounds" section of a project). Forgotten passwords reset by email (R8). **A second factor is never bypassed:** confirmed by the
  maintainer ("They still need TOTP if set, right?"), an emailed reset link or emailed sign-in link counts
  only as the first factor, so an account with TOTP set must also give its code, or one of the recovery
  codes shown when TOTP was set up, before a reset or sign-in completes. These are SaaS account operations, so they join R7's list.
- **Usage unit:** credits per month, broken down by experiment minutes, LLM use through Diskuv, and
  storage. Prices are not part of this plan.
- **LLM provider:** the SaaS offers LLMs to projects, the safe route in a browser because keys stay on the
  server (R9). Which models it offers (maintainer, verbatim, 2026-10-10): "All models from AWS Bedrock
  that have bedrock-runtime endpoints and have EOL no sooner than 3 months from project start/edit time
  and have text output modalities and have text input modalities and support reasoning". So the offered
  list is computed, not curated: the SaaS filters AWS Bedrock's model catalog by those five conditions.
  Because the end-of-life condition is measured from when a project is started or edited, the list a
  project sees can shrink over time; the threads should say what happens to a project whose chosen model
  later falls inside three months of end of life (a warning to the PI, and whether swapping the model is a
  measurement change under R14 when that LLM is a judge).

### R20. Supported coding agents

The maintainer (verbatim, 2026-10-10): "Claude Code, codex cli, gemini cli, aws bedrock cli, grok build,
goose cli." Each must run without a person present and authenticate from a stored secret, since experiments
run on executors (R7, R16). What the Mecha DK session found, not tested: Grok Build (xAI) has a headless
mode via `-p`; goose has `goose run` for non-interactive runs and can use configured providers, including
local ones; "aws bedrock cli" was withdrawn by the maintainer (verbatim, 2026-10-10: "That was a mistake; do not
include."), so the supported list is Claude Code, Codex CLI, Gemini CLI, Grok Build and goose. For Claude Code see R16. Codex CLI and Gemini CLI were not re-checked. The threads should
record each agent's headless invocation, its credential, and whether it can use the project's own LLM
connections (R9).

**Sign-in, decided (maintainer chose the recommendation, 2026-10-10):** each agent signs in its own way, on
the desktop: through the agent's own login where that yields a token that can be stored and reused
unattended (as `claude setup-token` does), otherwise with the agent's API key. The result is stored as a
secret and handed to executors (R16).

### R21. IDEATE draws on Zotero, web search and people, not only "the literature"

The maintainer (verbatim, 2026-10-10):

> I would like IDEATE to use https://www.zotero.org/support/dev/web_api/v3/basics with an LLM if both are
> configured.
>
> "Proposes hypotheses from the literature". That is too restrictive; the source can be literature or
> Zotera or a colleague or a web search, etc.

So the role is "proposes hypotheses", filled by people on the project, an LLM, or both (R9). People, including
colleagues, propose by posing hypotheses themselves (R2). An LLM always reads the project's own hypotheses and
results; that is not an option. On top of that it draws on the sources the project ticks: a Zotero library and
web search. The IDEATE research step is a driver step (R10), so the driver, not `dk0 learn`, calls Zotero.

Web search is not a separate provider. It is a tool the driver enables in the IDEATE prompt, run by the LLM
connection's own search tool where it has one (the maintainer, 2026-10-10: "Isn't that just a tool you enable for
the IDEATE prompt?"). The GUI offers it only for connections that have such a tool, and Mecha DK holds no search
key. The coding agents of R20 bring their own search tools, so the same rule covers them.

Two search APIs are offered besides (the maintainer, 2026-10-10: "For search, add options for Exa Search and
Semantic Scholar. Both have APIs. Both can use API keys, but Semantic Scholar does not a key for low frequency
rates."). The driver exposes each as a tool in the IDEATE prompt when the project ticks it. What their pages say
(read by the Mecha DK session, not tested):

- Exa: `POST https://api.exa.ai/search`, key in `x-api-key` (or `Authorization: Bearer`), a key is required;
  `query`, `numResults` (1 to 100), an optional `category` (see the options below), `includeDomains`,
  `startPublishedDate`, and `contents` for text or highlights. `429` on rate limit; billed by use.
- Semantic Scholar Academic Graph: `GET https://api.semanticscholar.org/graph/v1/paper/search` (also
  `/paper/search/bulk`, `/paper/search/match`, `/snippet/search`), with `query`, `fields`, `offset`, `limit`; an
  optional key in the `x-api-key` header. Without a key, "1000 requests per second shared among all
  unauthenticated users", which may be throttled; a key starts at 1 request per second. Keys come by email.

- Tavily (the maintainer, 2026-10-10: "Add Tavily and Brave Search. Mention both have free requests each month
  after signing up."): `POST https://api.tavily.com/search`, `Authorization: Bearer <key>`, a key is required;
  `query`, `search_depth` (`basic` costs 1 credit, `advanced` 2), `topic`, `max_results` (up to 20),
  `include_domains`. `429` carries `Retry-After`.
- Brave Search: `GET https://api.search.brave.com/res/v1/web/search`, key in `X-Subscription-Token`, a key is
  required; `q` (operators such as `site:` go inside it), `freshness`, `count` (up to 20), `offset`,
  `extra_snippets`.

Each source has the common options of its API under "Search options" (the maintainer, 2026-10-10: "I meant Exa
should have an option to pick categories. And any other search provider should have its common options as
well."). They are limits the LLM chooses within, not fixed values; empty means no limit. The driver passes the
limits into each tool's definition and rejects a call outside them.

The options on the LLMs page are the PI's defaults for every project. Each project can set its own per source,
and choose which connected sources it uses, in project settings under "Sources for hypotheses" (the maintainer,
2026-10-10, agreeing to the recommendation: "Add that."), because categories, fields of study and sites usually
follow the research question. The project override is stored with the project, so a driver on another device
uses it; keys are not, and stay in the key store of the device that holds them. A change applies from the next
IDEATE and is not a measurement change, since IDEATE only proposes hypotheses. Only the PI changes it.

- Zotero: `qmode` (titles and creators, or everything), collection, `tag`, `itemType`.
- Exa: the categories the LLM may pick (`company`, `publication`, `news`, `personal site`, `financial report`,
  `people`; Exa takes one per search, none ticked means any), `type`, `numResults`, `includeDomains`,
  `excludeDomains`, `startPublishedDate`, `endPublishedDate`.
- Semantic Scholar: `fieldsOfStudy`, `publicationTypes`, `publicationDateOrYear` (or `year`),
  `minCitationCount`, `openAccessPdf`, `limit`.
- Tavily: `search_depth`, `topic`, `max_results`, `time_range`, `include_domains`, `exclude_domains`,
  `language`, `country`.
- Brave Search: `freshness`, `count`, `country`, `search_lang`, `safesearch`, `extra_snippets`; sites through
  `site:` in `q`.

Tavily and Brave both give free requests each month after signing up; the pages read did not state the amounts,
so the GUI says "free requests each month" without a number. Every key goes in the key store like the Zotero
key, and like Zotero, none of the pages says whether browsers may call
it directly, so the web build may need the SaaS to relay.

What the Zotero Web API v3 basics page says (read by the Mecha DK session, not tested): base URL
`https://api.zotero.org` (the desktop Zotero app also serves a local API at `http://localhost:23119/api/`);
libraries are `/users/<userID>` or `/groups/<groupID>`; public libraries need no key, others take an API key in
the `Zotero-API-Key` header (or `Authorization: Bearer`); `q` searches titles and creators and `qmode=everything`
adds full text; `tag` and `itemType` filter; clients honour `Backoff` and `Retry-After` and keep to four
concurrent requests. The page does not cover browsers (CORS), so on the web Zotero access may need the SaaS
(compare R9).

Requirements for the threads: each hypothesis records the sources it came from (Zotero item keys, URLs, or the
person who posed it), so the explanation trace of C59 can cite them; the GUI asks for a read-only Zotero key and
keeps it in the key store, never in state (R16); the transcript records each search the LLM ran and the pages it cited; and papers, notes and web pages
are untrusted text an LLM reads, the same prompt-injection exposure as R18, so the security document should
cover them too. IDEATE's two streams (revelation-seeded and data-driven, design.typ `@p1-s3-14`) stay as they are;
the sources feed the data-driven stream.

### R22. Schedule unattended windows, working hours, and pause at once

The maintainer (verbatim, 2026-10-10):

> I need a way to schedule or switch to unattended windows. Needs to include working days and hours as well.
> And a way to pause the cycles immediately.

The GUI gets a Windows page and a "Pause now" button on every project header, phone included. It follows the
harness's own rules for windows (`declare-unattended-window`, `plan-unattended-window`), restated for a project:

- **A window is stored data, never a conversation**, so the desktop driver (R11) keeps running it with no device
  connected, and every device sees the same schedule. Cancelled and closed windows are kept as the record.
- **Every window has an end.** "Switch to unattended now" asks until when; the GUI never guesses an end time.
- **Working hours** are days, a start and end time and a time zone. Outside them the PI picks one of: run
  unattended, pause until working hours, or keep waiting (attended). With "run unattended", each evening and
  weekend is its own window ending when working hours start.
- **A window permits running, not spending.** Its limits are a cycle cap (default 6, the harness default) and a
  stop after N cycles in a row that learn nothing (default 2); spends and sending experiments to a person happen
  only when the window allows them. Anything else stays parked. Measurement changes and revelations are never
  made inside a window.
- **Before a window opens** the GUI lists what will stay parked (spends, REVIEW owed, revelations owed) and
  offers attended cycles first, the prep cycles of `plan-unattended-window`.
- **Pause** stops after the step in flight and starts no new outward act, the harness's cancel (condition 9).
  Running experiments finish and their results are kept; nothing done is undone. A paused project stays paused,
  even when a window would open, until the PI resumes it.
- **Pause from a phone** is a command over iroh (R11, R12). If the desktop cannot be reached it is queued and
  applied on contact.

Engine side: does `dk0 learn` hold the window record and the paused flag as project state (my recommendation,
since state is `dk0 learn`'s, R10), or does the driver? And the harness's condition 10, "a run that cannot hear its
cancel switch must not keep acting": the GUI equivalent is a driver that cannot reach the relay. Whether it should
then pause itself is a decision for the maintainer. Who may pause (PI only, or collaborators too) is also open.

### R23. Each project has a local folder, and the GUI opens folders

The maintainer (verbatim, 2026-10-10):

> The new project will need a local directory for dk0 learn init and PERSIST, etc. to store state.
>
> And a UI should be able to open a directory.

New project asks for a project folder on the computer that runs the project (the desktop driver of R11). `dk0
learn init` creates the project's state there, and every later `dk0 learn` call, PERSIST's included, reads and
writes it. The Projects page gets "Open project folder", which adds a project from an existing folder (copied
from another computer or checked out from git) and offers New project when the folder holds none. On the web,
Android and iOS, the folder picker browses the paired desktop over iroh (R11, R12), because those devices do not
hold project state.

Engine side: `dk0 learn` needs every command to take the project folder explicitly (as the harness passes
`--cwd state` today), a way to tell whether a folder holds a project, and its version, without changing it, and a
defined behaviour for a non-empty folder at `init`. Secrets stay out of the folder (R16). Open: whether init
should offer to make the folder a git repository, so "another machine can continue" (PERSIST) has a default
path; the design only says the folder can be copied, synced or kept in git.

### R24. A welcome wizard, an LLM in the New project flow, structured scope, and templates

The maintainer (verbatim, 2026-10-10):

> Configuring an LLM for the first time is not obvious and not an integral part of the flow. I suspect the
> majority of users will want an LLM (some of which will be more familiar with the word "agent" or "model").
> Perhaps a Welcome wizard, or a better new project page, can help?
>
> SUOs can be made into templates so that "Scope" and the next two sections of the new project page can be
> refilled.
>
> The "What the mecha may vary" question is freeform text; so are some of the other SUO fields. I'm not sure
> that is right. The code for example, is the mutable (git branch) git repositories that has been configured on
> some other pages. And perhaps "What the mecha can read" should also be a question. Look at the SUOs used in
> Paper I benchmarks and dk-engine-opt cycle/ for guidance.

**LLM.** A four-step welcome wizard on first launch (welcome, connect an LLM, this computer, first project), and
a box at the top of New project while no LLM is connected, with the same choices. The words are "an LLM, also
called an agent or a model". With an LLM connected, each role it can fill starts with it. No `dk0 learn` change:
connections are the driver's (R9, R10, R20).

**Structured scope.** What the session read: `cycle/common/suo.py` declares a SUO as a required root hypothesis,
a task adapter that runs and grades a candidate behind the boundary, prompt configuration, revelations, and
constraints (model, no network for the candidate program, the container boundary, a context budget). design.typ
`@p1-s4-5-1` names the edit surface, measured surface, public spec and boundary. The benchmark adapters make them
concrete: Defects4J edits `src/` and runs the relevant tests, one case per bug-revealing test plus one
regression case, never charging a test that already failed (`d4j_runner.py`); RunBugRun runs `cases.py`, one
case each; MLE-bench runs `submission.py` and a separate grader returns only validity and medal, never the score
(`case_runner_mle.py`). So section 1, "Scope", becomes:

- **Aim**, the root hypothesis, required, one sentence.
- **What the mecha may change and read**, one list: repositories (change on a branch, or read pinned; the same
  list as the experiment environment, R16), files and data in the project folder, and parameters with a range
  for experiments a person runs. Anything not listed is out of reach. This adds a *read surface* the design does
  not name today: the inputs an agent may see but not change (a task description, training data, a pinned
  dependency). Proposed: `dk0 learn init` records it beside the edit and measured surfaces.
- **What you measure**: where cases come from (a test command, a hidden grader, a person, a list of cases), what
  each case gives (pass or fail, or a number and its direction), the command and where it runs, and the two
  Defects4J rules as options (a regression case; leave out tests that already fail).
- **Protocol of record**: a list of files, each a file in a repository or an uploaded document, or none yet, in which
  case init poses the problem of drafting a specification (design.typ `@p1-s4-5-1`). It is a list because
  MlFront's public spec was several files (the maintainer, verbatim, 2026-10-10: "There can be multiple
  specification files (for MlFront it was SPECIFICATION.md, DK0-REFERENCE.md, Assumptions.ml, etc). So the
  Protocol of record is too limiting."); design.typ names `SPECIFICATION.md` with the per-engine references as
  the public spec REVIEW reads, and the checked-assumptions files (`Assumptions.ml`) that fail to compile when a
  symbol they name changes. An earlier draft gave each file a "kind" and a "checked how"; neither has a role in
  the design or `cycle/`, so they were dropped (the maintainer, 2026-10-10: "I also don't understand the Kind and
  "Checked how" ... where does that play a role?"). **Every change to these files is reviewed at REVIEW**
  (verbatim: "Any change to specifications (what you call the protocol of record) has to be reviewed in
  REVIEW."): a change the mecha's experiment makes, one a collaborator requests, and adding or removing a file
  in project settings all go to REVIEW for the PI's sign-off before they take effect. So `dk0 learn` must treat
  the public spec files as a surface whose every diff is a REVIEW item, not only the merged code changes.
- **Out of bounds** is the GUI's name for the SUO's *boundary*, design.typ `@p1-s4-5-1`: "the *boundary*, what
  is out of scope, which for every project includes the harness' own `eval/` and the host's release credentials
  (the execution boundary)"; R8 adopted "out of bounds" as the PI wording for it. In `cycle/` the closest
  pieces are `suo.py`'s `constraints` (no network for the candidate program, the container boundary) and the
  MLE-bench guard that refuses to stage test labels. Its choices and how each is kept (the maintainer, verbatim, 2026-10-10:
  "You still haven't said exactly HOW the choices will be used. "Hidden test data and answers, when a grader
  holds them", for example, has no mechanism to enforce it."; then: ""Secrets the experiment never gets." No,
  the secrets should be whitelisted not blacklisted. "How results are measured (always)". That is wasted space
  in a UI ... there are no options in this section! "The three rules are pinned by module and version, and the
  desktop refuses a run whose rule differs." I don't understand. The desktop runs the three rules each cycle,
  whatever they are. There is no "refuses". The "How it is kept" blurbs: these don't belong in the UI. They
  were for me to check the design makes sense. They belong in the design document and security documents."):
  - *Secrets each step may use*: a grid of the experiment environment's secrets against Set up, Run the
    experiment and Grade out of sight. A step receives only the secrets ticked for it; the driver writes every
    `dk0 run-function` request and adds those alone. Every other secret stays in the key store.
  - *How results are measured* has no options and no UI block. The driver runs the three rules the project
    names, each cycle. Changing a rule, or what it measures with, is a measurement change (R13). Before each
    run the driver compares the change under test with the edit surface's limits and rejects a change
    touching any other file (the tests, for example), recording it on the DISPATCH page.
  - *No internet for running and grading the experiment*, a checkbox, on by default. The driver starts both
    steps with networking off (the MXC sandbox's network policy on this computer, R6; the executor's own
    setting elsewhere) and uses only executors that can switch it off while the box is ticked. Set up keeps
    the internet.
  - *Grader only* is an access choice in the items list, with no block of its own. Such an item reaches only
    the grader's request, as `KIND[hidden][name]`, in its own run and folder. Before every run the driver
    checks, by path and by checksum, that no grader-only file is inside anything the experiment receives, and
    stops the cycle if one is (the analog of MLE-bench's `_assert_no_labels_reachable`). The grader returns
    one result per case.
  - *Anything else* is a Markdown text editor. People keep it: a person running an experiment sees it as "Stop
    if" and "Never", the PI approves each such experiment at AUTHORIZE, and the LLM reads it with the standing
    instructions. No program checks it.
  The explanations live in the security sections of a new user document, `MECHA-DK.md`, a sibling of
  `DK0-REFERENCE.md` in `dksdk-coder/ext/dk/docs/` (the maintainer: "Since we do have security sections in
  DK0-REFERENCE.md, start writing into security sections of a new sibling MECHA-DK.md (which documents how to
  use the Mecha DK UI)."). The form links to it with "How Mecha DK keeps these". It is also the security
  document R18 asks for. Open for the threads: whether MXC exposes a network switch the driver can set, which
  remote executors can switch networking off, and whether `dk0 learn` or the driver owns the pre-run checks.

**Templates.** "Start from" offers Blank, two templates drawn from the benchmarks (fix a program until its tests
pass; do well in an ML competition, with the MLE-bench revelations on leakage and a disclosed learner), and the
PI's own. A template fills sections 1 to 3 (scope, what counts as better, revelations) and never the folder,
people, executors or keys. "Save sections 1 to 3 as a template" is on the form and in project settings.
Proposed for `dk0 learn`: export and import a SUO, objective and revelations as one file, so a template is
portable and a benchmark's SUO can ship as one.

**Decided (the maintainer, verbatim, 2026-10-10):**

> Where templates are kept: on the computer and in the Diskuv account.
>
> The read surface: yes, adopt it as a SUO term.
>
> Export and import: The template should be a capnproto binary file with a well-defined capnproto schema.

So:

- **Templates are kept in both places.** A template saved on a computer stays usable offline; with a Diskuv
  account it is also stored there and appears on every device signed in to it. The threads should say which
  copy wins when both changed.
- **The read surface is a SUO term.** The SUO becomes five named things: the edit surface, the *read surface*
  (inputs the mecha may see and pass to an LLM but never change: a task description, training data, a pinned
  repository), the measured surface, the public spec and the boundary. This amends design.typ `@p1-s4-5-1`,
  which names four, and C47; the amendment goes through the usual record, not this plan. A read-surface item is
  also what the prompt-injection document (R18) must treat as untrusted text.
- **A template is a Cap'n Proto binary message with a published schema.** `dk0 learn` owns the schema file,
  versioned with the engine; the GUI reads and writes it through the C binding (R7) and does not define its
  own. A first draft for the threads to correct (the file ID is a placeholder until `capnp id` makes one):

```capnp
@0x0000000000000000;  # placeholder: generate with `capnp id`

struct ProjectTemplate {
  formatVersion @0 :UInt16;
  name @1 :Text;
  description @2 :Text;
  aim @3 :Text;                      # the root hypothesis; required
  editSurface @4 :List(SurfaceItem);
  readSurface @5 :List(SurfaceItem);
  measured @6 :Measurement;
  publicSpec @7 :PublicSpec;
  boundary @8 :Boundary;
  outcomes @9 :List(Outcome);        # what counts as a better result
  revelations @10 :List(Text);
}

struct SurfaceItem {
  union {
    repository @0 :Repository;
    path @1 :Text;                   # relative to the project folder
    parameter @2 :Parameter;
  }
}

struct Repository {
  url @0 :Text;
  paths @1 :List(Text);              # empty means the whole repository
  union {
    branch @2 :Text;                 # followed, for the edit surface
    pin @3 :Text;                    # tag or commit, for the read surface
  }
}

struct Parameter {
  name @0 :Text;
  unit @1 :Text;
  union {
    range @2 :Range;
    choices @3 :List(Text);
  }
}

struct Range { low @0 :Float64; high @1 :Float64; }

struct Measurement {
  source @0 :CaseSource;
  command @1 :Text;
  runIn @2 :Text;
  caseResult @3 :CaseResult;
  regressionCase @4 :Bool;
  excludeAlreadyFailing @5 :Bool;
}

enum CaseSource { testCommand @0; hiddenGrader @1; person @2; caseList @3; }
enum CaseResult { passFail @0; numberLowerBetter @1; numberHigherBetter @2; }

struct PublicSpec {
  union {
    files @0 :List(SpecFile);
    draftAtInit @1 :Void;
  }
}

struct SpecFile {
  union {
    fileInRepository @0 :Text;
    document @1 :Data;
  }
}

struct Boundary {
  noNetworkForCandidate @0 :Bool;
  noHiddenTestData @1 :Bool;
  other @2 :Text;                    # hazards, ethics, approvals, budgets
}

struct Outcome {
  name @0 :Text;
  source @1 :OutcomeSource;
  valueName @2 :Text;                # for a value or judge outcome: the key in each case's result
  higherIsBetter @3 :Bool;
  unit @4 :Text;
  typicalFrom @5 :Float64;           # scores 0; sets the scale for weighing
  typicalTo @6 :Float64;             # scores 1; values outside still count
  weight @7 :Float64;                # from the PI's order and ratings, not typed
  neverAdoptWorseThan @8 :Float64;   # optional; NaN when unset
}

enum OutcomeSource { casesThatPass @0; runRuleValue @1; judgeScore @2; }
```

  Secrets and the measuring apparatus are always out of bounds, so the schema has no field to switch them off.
  A template never carries the project folder, people, executors or keys, so the schema has no field for them
  either. The threads should settle how revelations carry their check status, and how the two benchmark
  templates are published (with the engine, or from Diskuv).

### R25. A connected model gets goose as its coding agent; Diskuv SaaS ships its own goose build

The maintainer (verbatim, 2026-10-10), on the wizard's "Connect an LLM" step:

> * The "Use an agent you already have" should be "Use a coding agent you already have"
> * "also called an agent or a model" should be "also called a coding agent or a model"
> * Remove "goose"
> * The "Or connect a model" should have "OpenAI (ChatGPT) | With your OpenAI API key."
> * I expect when you directly connect a model rather than a coding agent, the desktop should download and
>   configure `goose` to be the coding agent using dk0 assets. Configuring goose is documented in
>   https://github.com/aaif-goose/goose/blob/main/CUSTOM_DISTROS.md and
>   https://goose-docs.ai/docs/getting-started/providers#available-providers . For Diskuv SaaS, using a goose
>   Custom Distro with a Custom AI Provider will enforce a uniform layer for models and also give SaaS users a
>   direct coding agent option beyond Meta DK.

So goose is no longer a choice the PI makes. Connecting a model (Anthropic, OpenAI, Diskuv SaaS or an
OpenAI-compatible server) makes the desktop fetch goose as a dk0 asset, the same mechanism as the Typst asset
(R4), and configure it for that model. What the two goose pages say (read by the Mecha DK session, not tested):

- **Configuring a model without code.** goose reads `GOOSE_PROVIDER` and `GOOSE_MODEL` from the environment, then
  `config.yaml`, then defaults; `init-config.yaml` applies on first run when no config exists. Keys come from
  environment variables (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, with `OPENAI_HOST` and related settings) or the
  system keyring (`goose configure set-secret`); keys placed in `config.yaml` are ignored. For Mecha DK that fits
  R16: the driver passes the key from the key store as an environment variable to each goose run and never
  writes it to a file.
- **Custom providers.** A declarative provider is a JSON file in `custom_providers/` (`~/.config/goose/` on macOS
  and Linux, `%APPDATA%\Block\goose\config\` on Windows) with `name`, `engine` (`openai`, `anthropic` or
  `ollama`), `display_name`, `api_key_env`, `base_url`, `models`, `headers`, `supports_streaming` and
  `requires_auth`; an `auth` object can instead run a command that fetches a refreshable credential.
- **A custom distribution** may preconfigure providers, bundle extensions, change system prompts and branding,
  and ship recipes. It must keep the Apache 2.0 license and notices, mark its changes, and not use the goose
  marks to imply endorsement. Telemetry is off with `GOOSE_DISABLE_TELEMETRY=1`.
- **Running it headless.** `goose acp` serves the Agent Client Protocol over stdio, and `goose serve` over
  HTTP/WebSocket, so the driver can run a session, stream its tool calls into the DISPATCH log and cancel it
  (R22's pause).

For Diskuv SaaS the request is a Diskuv goose distribution whose custom AI provider is the SaaS model endpoint,
authenticated with the `auth` command from the Diskuv sign-in (so no long-lived key on the device), and limited
to the SaaS model list of R19. It is one uniform layer over the Bedrock models, and SaaS subscribers can use it as
a coding agent outside Mecha DK. Threads to settle: whether the per-model goose is the upstream release with
config or the Diskuv distribution for every model; telemetry off by default; where goose's own config lives
so it does not mix with a goose the PI already uses (a Mecha DK-owned config directory through goose's
environment); pinning and updating the asset; and the terms for the SaaS distribution (R19, site-diskuv-com).

### R26. Browse the SUO at the version a hypothesis made or was measured at

The maintainer (verbatim, 2026-10-10):

> Each hypothesis node should be linked to a particular instance of the SUO. (Confirm that is the design in
> Paper I and in cycle/). If so, the UI should be able to browse the parameters, files, images, code of the SUO
> through the hypothesis tree or anywhere a hypothesis is shown.

What the record says, checked by the Mecha DK session:

- `cycle/common/tree-schema.md` keeps a top-level ordered list `states`, "the ordered list of SUO states", each
  with `id`, `commit` ("the SUO commit sha at this state"), `created_by` ("the node whose fix attempt produced
  this state; `null` for the initial state"), `via` (`initial` or `fix-attempt`) and `created_at`. Every
  observation is `(state, outcome)` for one case. "A fix attempt changes the program, so it appends a new entry
  to `states` ... A measurement leaves `states` unchanged."
- Paper I: DISPATCH "tests each n in B's hypothesis in its own isolated worktree", "applying a node's hypothesis
  against the current baseline".

So the link exists but is not one node to one instance. A node *creates* zero or more states (one per fix
attempt; none for a measurement), and its evidence is observations at states that it or other nodes created.
The GUI therefore shows, wherever a hypothesis appears (tree panel, phone tree, DISPATCH rows, experiment
history), the versions it made and the versions it was measured at, and each opens a read-only browser of the
SUO at that state: the edit and read surfaces as a file tree with changes marked, a diff against the version it
started from (or any other), previews for images, PDFs and tables, the parameters' values, and the cases
measured there. "Open a copy on this computer" checks the state out into a separate folder.

Engine side, the gaps: a state is identified only by a `commit`, which covers one git repository. The SUO of
R24 can span several repositories (one changed, others pinned), project-folder files and parameters, so a
state needs to record the commit of each repository, the pins of the read surface, a content hash of the
project-folder files on the surfaces, and the parameter values. `dk0 learn` should also answer "list the
files of state S, with changed-since-state-T marks" and "read file F at state S" through the C binding, so the
GUI never reconstructs states itself. Lab parameters have no state record today at all: an experiment a person
runs (R8) must record the values used as the state it ran at.

### R27. Models and large data in the SUO, a variable per item, and the scripts that stand in for the adapter hooks

The maintainer (verbatim, 2026-10-10):

> Suggest how a SUO can include training a decision tree, a BERT or a LLM model. Are these files in the "What
> the mecha may change and read"? If they are too large to be part of a git repository, how would they be
> accessible?
>
> Also in "What the mecha may change and read": should each item have a environment variable? if so, provide a
> nice default for the environment variable name. more importantly, are there scripts, templates, etc. that must
> be provided so that the mecha can run a cycle? In `cycle/`each SUO had callback functions that need to be
> registered ... I don't see the analog in the UI yet.

**Training a model.** The training code and its configuration are the edit surface; the base model and the data
are the read surface; the trained weights are an *output* of each experiment, a third kind of item. A decision
tree is small enough for the project folder. A BERT-sized model follows `cycle/finetune/`: the base model
(`tasksource/ModernBERT-large-nli`) is fetched into a named cache volume (`HF_HOME=/hf`, "so model weights are
downloaded once"), training runs in a GPU container, and the run is tracked in MLflow
(`finetune_mlfront_mlflow.py`). An LLM is the same shape at a larger size, usually tuning adapters (LoRA, as
`run_finetune.py` does) rather than all weights. Hidden answers follow `cycle/mlebench/`: a separate grader
container holds them and returns only validity and medal.

**Too large for git.** A model or dataset is referenced, not copied: a Hugging Face model and revision, a URL
and sha256, an object-storage path and version, or an MLflow registered model version. Each executor fetches it
once into a cache. A SUO state (R26) records the pin, not the bytes. An output is saved to an artifact store the
PI chooses (the project folder, object storage or MLflow) and the state records its checksum, with a retention
rule ("keep the five best versions") so outputs do not grow without bound.

**Items are `dk0 run-function` parameters.** The maintainer's direction, verbatim,
2026-10-10, in order: "the Run the experiment command and the Grade out of sight command should be `dk0
run-object`. Parameters from the "What the mecha may change or read" should be provided to run-object, not
environment variables. One benefit of parameters is you can separate them by readonly/readwrite, and by kind.";
then "And run-object and run-function not just run-object. The syntax is at
https://diskuv.com/dk/help/latest/specification/values/#run-object-moduleversion--s-request_slot--c-command---m-member";
then "I want the kind to be first, then the optional read-only/read-write split. The latter is optional since
some kinds, like model outputs, should not be split further."; and last "Remove run-object. Use only
run-function." So both steps are Lua function rules run with `dk0 run-function`, and `run-object` is not used.

What the `dk0` reference and specification say (read by the Mecha DK session; the form document section is marked
"still under construction"): `run-function MODULE@VERSION (-f FILE | -d DIR/) -- CLI_FORM_DOC` runs the function
rule on a JSON request document built from the words after `--` in the W3C HTML JSON Forms style (`name=Jane`
gives `{"name":"Jane"}`, brackets nest keys, `[0]` makes a list, numeric-looking values become numbers), and
writes the resulting object to the file or directory. The rule reads the document as `request.user`; fields are
also available as `${PARAM.fieldname}` and `${PARAMFILE.fieldname}`. `add [-f unifiedscript.u] github-l2
[HOST/]OWNER/REPO[@TAG]` adds the latest or tagged GitHub release, which must carry a distribution with a SLSA
Level 2 attestation; `trust accept` records acceptance of a producer key and `trust grant` grants `--run` or
`--write` to an imported package.

Proposed convention, for the threads to settle with `dk0`: kind first, then `rw` or `ro` where the kind has
both: `KIND[rw][name]=value` or `KIND[ro][name]=value` for `repo`, `file`, `dir`, `model`, `data` and `param`,
and `output[name]=path` with no split; a grader-only item reaches only the grader, as `KIND[hidden][name]`. The rule receives `{"repo": {"rw": {...}, "ro": {...}}, "param": {"rw":
{...}}, ..., "output": {...}}`, so a read-only item can be enforced by the engine rather than by convention.
Each item's name defaults to its own name in lower case with every other character replaced by `_` (`app`,
`modernbert_large_nli`, `incubation_temperature`); the PI can rename it. The per-case results are the rule's
output (`-d DIR/`). Open: whether `trust grant --write` is how a read-only item is enforced, and the per-case
result format.

**Hardware.** The maintainer (verbatim, 2026-10-10): "For Hardware, replace it with the selectors: * Whether the
hardware is restricted to macos/linux/windows (or can run on some or all) * All the Hardware options
(accelerators to max_hourly_cost) from https://docs.skypilot.ai/en/stable/reference/yaml-spec.html". So the
"Hardware" step has the operating systems an experiment can run on (macOS, Linux, Windows; any subset, all
three meaning anywhere) and the SkyPilot task `resources` fields from `accelerators` to `max_hourly_cost`, as
that page lists them (read by the Mecha DK session): `accelerators` (`<name>:<count>`, a list or a set, e.g.
`H100:8`), `accelerator_args` (TPU only), `cpus` (`4+`), `memory` (GB, `32+`), `instance_type`, `use_spot`
(default `false`), `disk_size` (GB), `disk_tier` (`low`, `medium` default, `high`, `ultra`, `best`),
`network_tier` (`standard` default, `best`) and `max_hourly_cost` (USD per hour). None is free text (the maintainer,
verbatim, 2026-10-10: "The hardware fields should not be free-form text fields. Even the accelerator arguments
should be a list with Add and Delete ability."): accelerators are a list of catalog name and count rows, chosen
as "any one of these" (SkyPilot's set) or "the first available, in this order" (its list); accelerator arguments
are a list of key and value rows, keys from `runtime_version`, `tpu_name` and `tpu_vm`, values from the executor;
CPUs and memory are a number with "at least" or "exactly" (SkyPilot's `+`), memory and disk size carry a unit;
the instance type is picked from those that meet the other choices; tiers and spot are fixed choices; the hourly
cap is a number in USD or "No limit". So the GUI needs each executor's catalog (accelerator names, TPU runtime
versions, instance types) through the driver. Every choice is optional and empty means any. The operating systems default to all three, and
accelerators sit last, folded under "GPUs, TPUs, and other accelerators", showing "None needed" (the maintainer,
verbatim, 2026-10-10: "Default operating systems should be all three. The Accelerators section should be called
"GPUs, TPUs, and other accelerators". Right now it is too prominent. Most projects will not need
accelerators.").

Then (the maintainer, verbatim, 2026-10-10): "I don't understand your Instance type choices. And instance type
and spot instance fields should be grouped into virtual machines, since most users will not need it. The disk
tier and the network tier should have explanations from the SkyPilot documentation, since a user will not
understand what "medium" and "best" mean. All the Hardware fields are advisory until we have Diskuv SaaS
providing executor infrastructure." So:

- `instance_type`, `use_spot`, `max_hourly_cost`, `disk_tier` and `network_tier` sit under a closed "Cloud
  virtual machines" section (the maintainer, 2026-10-10: "The "Most per hour" belongs in the cloud virtual
  machines section." and "The disk speed and network speed also belong in cloud virtual machines."). Outside it
  stay the operating systems, CPUs, memory and disk size. The instance type is
  "Let the executor choose" (default) or one named type, and the help repeats SkyPilot's rule that with
  accelerators the type is inferred. Spot reads "No (default): on-demand machines" or "Yes: spot machines".
- Disk and network get SkyPilot's own explanations: `disk_tier` is the OS disk, with SkyPilot's rough figures
  (low about 1,000 IOPS and 90 MB/s; medium about 3,000 and 220 MB/s; high about 6,000 and 400 MB/s; ultra
  about 60,000 IOPS, 4,000 MB/s read and 3,000 MB/s write; best the best tier enabled); `network_tier` best
  is the best network on the infrastructure, which SkyPilot's examples give as AWS EFA or GCP GPUDirect.
- **Hardware is enforced, not advisory.** The maintainer corrected the above in the same exchange (verbatim):
  "Correction: They are not advisory. The desktop that runs the executor should check that rhe Hardware
  matches." So before each experiment the desktop driver (R11) checks that the chosen executor matches every
  hardware choice, and does not send the experiment if it does not, recording which choice failed on the
  DISPATCH page. The threads must say how the driver learns what an executor offers (this computer directly;
  GitHub Actions and Diskuv SaaS by what their runner reports), what happens when a remote runner turns out
  different once started (the run reports its hardware and the result is discarded on a mismatch), and
  whether changing a hardware choice is a re-baseline (a different machine can change measured results,
  R14). An executor (this computer, GitHub Actions, Diskuv SaaS, R7) is used only if it meets the
requirement; the threads must say how each executor reports what it offers, and whether `max_hourly_cost` feeds
the cost SELECT weighs. The Cap'n Proto `run` struct carries the OS set and these fields with SkyPilot's names.

**The adapter hooks.** `cycle/common/run_cycle_core.py` defines `RootedHooks`, "what the core loop needs from a
task adapter": `task_context`, `result_text`, `code_hash`, `measure`, `ingest`, `snapshot`, `now`, and an
optional `seed_hints`; `suo.py` adds `prompt_config` (the IDEATE and FIX framings and the validation discipline)
and `constraints`. In the GUI most of these become `dk0 learn`'s and the driver's own work, and the PI supplies
only what is task knowledge, as commands and files in a new "How an experiment runs" block of Scope:

| Hook in `cycle/` | In Mecha DK |
| --- | --- |
| `measure` (run and grade at a state) | "Run the experiment": `dk0 run-function` on the experiment rule, given the items as grouped parameters, returning per case whether it passed and each named outcome value (R28), with a time limit |
| the MLE grader container | optional "Grade out of sight": `dk0 run-function` on a separate grader rule, given only the hidden data and the experiment's output |
| the MLE loader and `emit` | optional "Set up": `dk0 run-function` on a setup rule, once per executor, given the same items; the only step with network and setup secrets (the maintainer, 2026-10-10: "The Set up command should be a run-function as well.") |
| `task_context`, `prompt_config` | "What the LLM is told": a task description file and standing instructions |
| `constraints` | "Where it runs": one or more `dk0 add github-l2 [HOST/]OWNER/REPO[@TAG]` (the maintainer, 2026-10-10: "Use one or more `dk0 import`", corrected: "I meant `dk0 add` not dk0 import"), each pinned to its tag; "Hardware" (below); out of bounds |
| `code_hash`, `snapshot`, `ingest`, `now`, `result_text` | done by `dk0 learn` and the driver from the surfaces; nothing for the PI |
| `seed_hints` | the shared seed, when a project starts from a seeded template |
| `check_prerequisites` | "Check by measuring the starting version", required before the first cycle |

Templates carry these scripts: the two benchmark templates ship working ones, and a third template, "Fine-tune a
classifier", comes from `cycle/finetune/`. The Cap'n Proto schema of R24 needs `outputs`, a parameter name on every
surface item (its parameter name), a large-item reference (source kind, address, pin, checksum, size), and a
`run` struct (the `dk0 add` packages, the hardware requirement, setup, the experiment and grader function rules for `dk0
run-function` as module and version, the setup rule likewise, the task description, standing instructions as
Markdown text, and time limits). The per-case result format belongs to the function rule's output and is versioned
with the schema. Standing instructions are edited in a multi-line Markdown editor with a preview (the maintainer,
2026-10-10: "The Standing instructions should be a text editor.").

### R28. Measurable outcomes and swing weighting for "What counts as a better result"

The maintainer (verbatim, 2026-10-10): "The "What counts as a better result" section. Tell me where in cycle/
these outcome measures are specified. I want to understand how to make that UI section actionable.", then
"Yes" to the redesign below.

**What `cycle/` does today.** One outcome, pass or fail, per case. `common/tree-schema.md` records each
observation as `(state, outcome)` with "outcome 1 means the case exhibits the failure"; each case runner maps
`exhibits_failure = 0 if passed else 1` (RunBugRun per test, Defects4J per bug-revealing test plus one
regression case, MLE-bench one case per competition where "passed is `any_medal`"). The loss is the Beta mean
of P(exhibits failure) with recency decay (`common/algorithms/posterior.py`: "mean() is the node loss"); SELECT
is Thompson on those Betas (`selection.py`). "Better" is prose in the root hypothesis (`suo.py`). No weights.

**Where weighted outcomes come from.** The dk-engine-opt harness scores several terms (design.typ: `NET =
FINAL - 0.002·(policy tokens/1000)`, `DOC = 0.4·DOC_MECH + 0.6·judge`). The design's replacement (C62, C63) is
an additive multi-attribute value function, its weights elicited by swing weighting and pairwise preferences,
carried as a Dirichlet with uncertainty and sensitivity-tested; the risk attitude stays in the decision
quantile (C2).

**The GUI.** Section 2 is a list of outcomes, each with a name, where it comes from (cases that pass, a value
the run rule returns by name, or a judge's score), the value name, which way is better, a unit, and the worst
and best values that matter. With two or more outcomes, "Weigh outcomes" runs swing weighting: the PI puts the outcomes
in order, the one they value most first, by dragging or with up and down buttons (the maintainer, 2026-10-10: "In
"Weigh outcomes", shouldn't the user be able to reorder the outcomes, even if there are more than two
outcomes?"), then values each outcome compared to the previous one on a slider from 1 to 100 (the maintainer:
"How much should each outcome be valued compared to the previous outcome?", "let the sliders be 1-100 for each
outcome", and "Use "outcomes" consistently"). Each outcome is valued over its range from worst to best. The
weights follow by chaining the ratings: the first outcome's raw weight is 1, each next one is the previous raw
weight times its rating over 100, and the raw weights are divided by their sum to add up to 1.00 (ratings 60
and 25 give 1, 0.60 and 0.15, so 0.57, 0.34 and 0.09). The New project form shows the
weights alone. An earlier draft also showed an interval per weight and a note such as "The best hypotheses
change order if Accuracy's weight falls below 0.25"; the maintainer did not understand either (verbatim,
2026-10-10: "I don't understand what "The best hypotheses change order if Accuracy's weight falls below [0.25]"
means on that page. And I don't understand what the intervals mean in that section"). The interval was the spread
of the Dirichlet the design carries over the weights (C62, C63), and the note was the sensitivity analysis; on a new
project there are no hypotheses to reorder. Both stay in the engine. The sensitivity result reaches the PI later,
once there are results, in project settings and in the slider's own terms, for example "If Accuracy were valued
below 40 compared to Tests pass, a different hypothesis would lead". A new weight later is a
measurement change that recalculates scores from recorded results; a new outcome is measured again (R13,
R14). "What you measure" keeps only where cases come from.

**Results outside the typical range** (the maintainer, verbatim, 2026-10-10: "What are you suggesting will
happen if accuracy is 51%, when the second outcome says "Accuracy, from 70% to 95%" ?", then "Option 3"). The
range sets the scale only; results outside it still count, below 0 or above 1, so a bad change and a terrible
one stay apart. Each outcome may also carry "Never adopt if worse than": DECIDE never merges a change whose
expected value for that outcome is worse than the limit, however good its other outcomes. The form shows each
outcome as a two-line card: name, source, value name and direction, then unit, typical range, the optional
limit and Delete.

**Engine requests.**

- **Result format.** A run rule returns, per case, `{"id", "passed", "values": {NAME: number, ...}}`, one entry
  per value or judge outcome. Defined and versioned by `dk0 learn` with the template schema (R24, R27).
- **One belief per outcome.** A Beta for "cases that pass" (as today) and a Student-t from the NIG for each
  numeric outcome, per hypothesis, with the same recency decay and state attribution (R26).
- **The value function.** Scale each outcome linearly so the start of its typical range is 0 and the end is 1,
  extending the line beyond the range (accuracy 51% on a 70% to 95% range scores (51 - 70) / (95 - 70) = -0.76),
  combine with the weights,
  and propagate the weights' Dirichlet uncertainty into each hypothesis's expected value. DECIDE also applies
  each outcome's never-adopt limit; the threads must say whether the limit applies to the posterior mean or to
  a credible bound, the same question as C2's decision quantile. SELECT and DECIDE use
  that combined value; with one outcome it reduces to today's failure rate.
- **Elicitation.** Turn the order and the chained ratings into Dirichlet parameters, and, once there are results, report a sensitivity
  check: the smallest change of each rating that changes which hypothesis leads, expressed as a rating. The GUI shows the result; the
  arithmetic is `dk0 learn`'s.

### R29. Revelations seed IDEATE as well as bound it

The maintainer (verbatim, 2026-10-10): "Revelations also are used in IDEATE to generate new hypotheses (confirm
that). If so, the Revelations section needs an updated description."

Confirmed from the record. design.typ (section 3, "A revelation is also a generator"): IDEATE places the
revelations in its context "with an explicit steer that logical applications of a revelation are good source
material for new hypotheses", and "each IDEATE deliberately runs *two streams*: revelation-seeded hypotheses
... and unseeded, data-driven hypotheses"; C31 resolves that both streams are always on, each with an elicited
minimum share. In `cycle/`, `suo.py` injects the revelations "into every IDEATE and FIX prompt, stated to
outrank the agent's own analysis". The seeding steer is design; `cycle/` uses revelations as constraints only.

The New project form now describes all four uses: seeding at IDEATE, dropping or flagging at DROP, the LLM
reading them first when it proposes or writes an experiment, and checking a new revelation against the others.
The PI sets the minimum share of each stream (the maintainer, 2026-10-10: "should the PI be able to set the minimum
share of revelation-seeded versus data-driven hypotheses? Yes"). Project settings, under "Sources for
hypotheses", has "Mix of new hypotheses": at least N% applying a revelation and at least M% drawn from the
results so far, 25% each by default, adding up to at most 100%, applied from the next IDEATE. Above the floors
the split follows C31: "an adaptive bandit allocation by each stream's recent value of information, the same
machinery as SELECT, shifting toward exploration when seeded nodes keep failing and toward the revelations when
the frontier drifts incoherent." Engine request: `dk0 learn` stores the two floors in project state and runs
that allocation; the default of 25% each is a proposal.

### R30. Uploading files into the project

The maintainer (verbatim, 2026-10-10): "In "Task description" where did description.md come from? If it is an
uploaded file, the UI needs to be able to upload files."

`description.md` came from MLE-bench: `cycle/mlebench/mlebench_task.py` stages "description.md, the competition
description" into each task, and `suo.py`'s `task_context` reads it into the IDEATE and FIX prompts. In the GUI it
was an example file in the project folder with no way to put it there. Now:

- The items list has "Upload files" and "Add from the project folder". An uploaded file is copied into the project
  folder (R23) and listed as an item, read-only by default.
- The task description is one of: a file the mecha may read, an uploaded file (saved to the project folder and
  added to the read list), text written in an editor (saved as `description.md`), or none.
- On the web and phones the upload goes to the desktop driver over iroh (R11, R12), since the project folder
  lives there. The protocol of record already offers "Upload a document" (R24) on the same path.

Engine side: nothing new for `dk0 learn` beyond the project folder; the driver needs a file-transfer command on the
iroh channel with a size limit, and the threads should say what that limit is and whether large files go through
the "model or dataset" references of R27 instead.

## Classification

Not yet applied. A first reading, for the threads to confirm or overturn: R1 to R3 change what the
engine does (the runner, not the ruler), so they are engine work in `dk0 learn` and design-document
edits, not `amend-harness` amendments (design.typ `@p1-s4-3`). design.typ is not in
`governanceCorpus()` in `eval/run-eval.mjs` (DECISIONS.md, REVELATION.md, the pose-dk-problem charter
and eval/fact-sheet.md), so editing it should move no score. Thread 1 must confirm that from the code,
not from this note.

## Evidence

Not gathered. QUEUED.

### 1 Metric impact
### 2 Knowledge impact
### 3 Verification in the next cycle
### 4 Rollback
### 5 The learning process

Thread 5 should also answer the meta-request: "We need a mechanism for you to update the dk-engine-opt
design as we uncover things we need." This document is the mechanism the Mecha DK session used. The
threads should say whether a QUEUED plan in `lifecycle/plans/` is the right inbound route for design
gaps found by a sibling project, or whether another route (a node with `challenges:`, a
record-maintainer-statement kind) fits better.

## Apply

Not written. QUEUED.

## Verify

Not written. QUEUED.

## Roll back

Not written. QUEUED.

## Decisions for the maintainer

Not written. QUEUED.
