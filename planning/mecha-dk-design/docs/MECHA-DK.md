# Mecha DK

Mecha DK is the desktop, web and phone app for running a project with the mecha: an assistant that
proposes hypotheses, runs experiments in cycles and keeps track of what each result means, while you,
the principal investigator (PI), decide what goes ahead.

This document describes how to use the Mecha DK app. The engine underneath it, `dk0`, is described in
`DK0-REFERENCE.md`.

## Security

A Mecha DK project runs code, spends money and reads text written by other people. This section
describes who can act on a project, what each experiment receives, and how Mecha DK keeps the choices
you make in the Scope section of the New project form and in project settings.

### Who controls a project

The desktop that runs a project holds its state, its secrets and its connections to executors. That
desktop has full control of the project.

You, the PI, have full control from any device you have paired with that desktop: a phone, a tablet or a
browser signed in to your Diskuv account. Pairing uses a code from the desktop's Devices page. The code
carries the desktop's key in an envelope that Diskuv signs for your account. It works once and expires
after a few minutes, and the desktop asks you to approve each new device.

Collaborators you invite can see the whole hypothesis tree, pose hypotheses, run experiments you send
them, and request measurement changes for you to approve. Only you approve experiments, reviews and
calibrations, and only you authorize a run that waits for approval. A collaborator can ask you to.

#### A collaborator can gain your full control

Read this before you invite anyone.

The LLMs and coding agents a project uses read what collaborators write: hypotheses, notes, experiment
results. Text written to steer an LLM, called a prompt injection, can make it act as if you had asked.
Through it, a collaborator can run code with the secrets a step may use, change files the mecha may
change, or word a request so that you approve it.

Invite only people you would trust with the desktop that runs the project.

The same risk comes from every other text an LLM reads: papers and notes from Zotero, web pages from
search, and anything on the project's read-only list. Check a hypothesis from an unfamiliar source before you
authorize a run of it.

### Secrets

A secret is a value such as an API key or a sign-in token. Secrets live in the desktop's key store:
Windows Credential Manager, the macOS Keychain or the Linux Secret Service. A project file, a template,
a report and a read-only link never contain a secret.

Each project lists, under **Secrets each step may use**, which secrets each step may use:

- **Set up**, which runs once per executor and is the only step with internet access.
- **Run the experiment**.
- **Grade out of sight**.

A step receives only the secrets ticked for it. The desktop writes every `dk0 run-function` request
itself and adds the ticked secrets for that step. Every other secret stays in the key store.

The Experiment environment page decides which executors receive a copy of a secret: this computer,
GitHub Actions (as an Actions secret of the repository that runs the experiments) or Diskuv SaaS (in your account's vault).
A secret cannot be read back once saved.

### Runs that wait for your approval

Mecha DK itself creates every authorization request: the desktop that runs the project, when it plans a run.
No LLM creates one, and no function rule's response does.

At SELECT, for each hypothesis it chooses, the desktop plans the run: which executor runs it, which steps run
(Set up, Run the experiment, Grade out of sight), and which secrets each step receives. It writes every
`dk0 run-function` request itself, so it knows all three before anything runs. It parks the run at AUTHORIZE,
instead of sending it to DISPATCH, when the plan has any of these:

- **A paid executor**: Diskuv SaaS, or a cloud virtual machine. The request shows the most the run can cost,
  the executor's hourly price times the steps' time limits, with the calculation.
- **A secret you marked Approve each use** in Experiment environment, received by any step. Mark every secret
  that can publish, release or pay for something.
- **An experiment for a person.**

"Start the project" applies the same check to its setup check, before the first cycle.

Each approval releases one run of one hypothesis, and is recorded with who gave it and when. An unattended window
can carry pre-approvals you set when you schedule it: paid runs up to an amount, counted in total across the
window, and sending experiments to a person. A run that uses a secret you marked Approve each use always waits
until you return. Parked hypotheses stay in the tree, and the mecha keeps proposing hypotheses like them.

The check reads only the run plan. An LLM that writes an experiment cannot add or remove a request: it cannot
choose the executor or the secrets a step receives. A function rule that calls a paid service needs that
service's secret, so marking the secret Approve each use is what puts such a run in front of you.

### What the mecha may change

The list **What the mecha may change and read** names every repository, file, folder, model, dataset
and parameter the mecha works with, and whether it may change it, only read it, or never see it
(grader only). Anything missing from the list is out of reach.

Before each run, the desktop compares the change under test with the "may change" items and their
limits, for example "only `src/` and `train.py`". A change that touches any other file is rejected and
recorded on the DISPATCH page. The tests and the scoring code sit outside the limits.

Each item reaches the step as an argument after `--`, grouped by kind and then by access:
`repo[rw][app]=...`, `data[ro][train]=...`, `output[model]=...`. A function rule can tell from the
argument which items it may write.

### How results are measured

The set up, run and grade function rules, and the files outside the "may change" limits, decide how
results are measured. The desktop runs the rules named in the project each cycle. Changing a rule, or
anything it measures with, is a measurement change: it waits for the next break between cycles and is
applied with a fresh baseline. See Measurement changes in project settings.

### Projects drafted from a description

With **Describe it**, the LLM you choose reads your description and any files you add, then drafts the New project
form. The description and files go to that LLM's provider. A draft never ticks a secret; you tick each one.

The LLM can write run and grade rules for the project. Each waits for you: no rule runs until you open it and
approve it, and the desktop runs only the approved version of a rule. A rule changed after approval waits for you
again.

Text and files from someone else can carry a prompt injection that steers the draft, for example by widening what
the mecha may change or by dropping a line from Out of bounds. Read those two parts of a draft line by line before
you start the project.

### Problems and hypotheses from a template

A template can carry problems and hypotheses for a project to start with. The LLM reads them like any posed
problem or hypothesis. Read them before you start a project from a template someone else made.

### Judged outcomes

An outcome can come from a judge's score: an LLM or a person rates each result against the judge's
instructions, and the median of the judges' scores counts. A judge reads text the mecha produced, and that
text can carry a prompt injection aimed at the judge. Use more than one judge, and read a sample of judged
results when a score jumps.

The judge's instructions, model and number of judges decide how the outcome is measured. Changing any of them
is a measurement change.

### Hidden answers

An item marked **Grader only** goes into the grader's request alone, as `data[hidden][name]`, in a run
and folder of its own. The experiment's request never names it.

Before every run, the desktop checks by path and by checksum that no grader-only file sits inside any
item the experiment receives. If one does, the desktop stops the cycle and shows the file.

The grader returns one result per case: passed, or a value. The answers and any other output of the
grader stay with the grader.

### Internet access

With **No internet for running and grading the experiment** ticked under **Out of bounds**, the desktop starts the run and
grade steps with networking switched off: in the MXC sandbox on this computer, and with the executor's
own setting on GitHub Actions or Diskuv SaaS. While the box is ticked, the desktop uses only executors
that can switch networking off. Set up keeps its internet access.

### Hardware

Before each experiment, the desktop checks that the executor offers the hardware the project asks for:
operating system, CPUs, memory, disk, accelerators and any cloud virtual machine settings. On a
mismatch the desktop holds the experiment back, and the DISPATCH page names the choice that failed.

### Out of bounds text

The **Out of bounds** text covers hazards, ethics and approval limits, and budget ceilings, in your own
words. People keep these rules:

- A person running an experiment sees the text as "Stop if" and "Never" on the experiment's page.
- You approve every experiment sent to a person at AUTHORIZE.
- The LLM reads the text with the standing instructions.

No program checks this text.

### Changes to the protocol of record

The protocol of record is the set of files that say what the project must do: a specification,
references, a protocol or pre-registration, checked assumptions. Every change to these files waits at
REVIEW for your sign-off: a change an experiment makes, a change a collaborator requests, and adding or
removing a file in project settings. A rejected change is undone.

### Read-only links and the public demos

A read-only link lets anyone browse a project in a web browser, with no account, until the link
expires. Each link has its own key, separate from full control and from every other link. Revoking a
link stops that link at once. Links last up to 30 days. A read-only view leaves out the private details
you exclude.

The two public demos are read-only projects served by Diskuv.

### Lost devices

If you lose a phone or tablet, remove it on the desktop's Devices page, and revoke it on your Diskuv
account page. The account page works while the desktop is off. A device's certificate expires after 30
days unless the device stays signed in.

If you lose the desktop that runs a project, revoke it on your Diskuv account page. Then replace every
secret it held, in each service that issued one.

### Connections between devices

Devices reach the desktop directly when they can. When they cannot, the connection passes through
Diskuv's relay. The relay carries the traffic end to end encrypted and cannot read it.
