import glob
P=[
("Each link has its own key, separate from full control and from every other link, so revoking one stops only that one, at once.","Each link has its own key, separate from full control and from every other link. Revoking a link stops that link at once."),
("used only when a direct connection is not possible; it cannot read the traffic.","used only when the devices cannot connect directly; it cannot read the traffic."),
("A read-only repository is pinned to a tag or commit, so results stay comparable; moving the pin is a measurement change,","A read-only repository is pinned to a tag or commit. Results stay comparable from cycle to cycle. Moving the pin is a measurement change,"),
("an LLM or coding agent reads what your collaborators write, so a collaborator can steer it with a prompt injection and, through it, act with your full control.","an LLM or coding agent reads what your collaborators write. A collaborator can steer it with a prompt injection and, through it, act with your full control."),
("Papers, notes and web pages are text an LLM reads, so they can carry a prompt injection, just like a collaborator's text.","Papers, notes and web pages are text an LLM reads. Like a collaborator's text, they can carry a prompt injection."),
("Writing a code change needs an agent that edits files and runs programs, not just a model. It runs where the experiment runs: this computer, GitHub Actions or Diskuv SaaS, never inside a browser or phone app.","Writing a code change needs a coding agent, which edits files and runs programs. It runs where the experiment runs: this computer, GitHub Actions or Diskuv SaaS."),
("No key on this device, and the safe choice in a browser.","Keeps no key on this device, and suits a browser."),
("and are not retired within 3 months.","and stay available for at least 3 more months."),
("On a dark background it is only 2.0:1, so dark mode uses the white mark or the purple tile.","On a dark background it is only 2.0:1. Dark mode uses the white mark or the purple tile."),
("stay on record under a version that no longer applies.","stay on record under the version they were measured with."),
("Each is pinned to its tag, so every version runs on the same tools.","Each is pinned to its tag. Every version runs on the same tools."),
("Leave out tests that already fail before any change, so they are never charged to one","Leave out tests that already fail on the starting version; no change is ever charged for them"),
("If it does not, the experiment is not sent, and the DISPATCH page says which choice failed.","On a mismatch the desktop holds the experiment back, and the DISPATCH page says which choice failed."),
("You weigh them by answering a few comparisons, not by typing weights.","You weigh them by answering a few comparisons."),
("Changes here are not applied right away. They become a request on","Changes here become a request on"),
("marked as measured the old way, and are not compared directly with new ones.","marked as measured the old way. The mecha compares them only with results measured the same way."),
("change immediately, because they do not change how results are measured.","change immediately. How results are measured stays the same."),
("Changes apply from the next IDEATE and do not change how results are measured.","Changes apply from the next IDEATE. How results are measured stays the same."),
("Options not shown here keep your defaults from","Other options keep your defaults from"),
("No Pose, Authorize, Sign off or Approve buttons appear in a read-only view. Private details the owner has excluded are not sent.","A read-only view shows no Pose, Authorize, Sign off or Approve buttons. Private details the owner excluded are never sent."),
("That did not work. Try again, or use another way to sign in.","Sign-in failed. Try again, or use another way to sign in."),
("A change that is better than the current best is merged, one that is not worth more testing is pruned, and the rest stay open.","A change better than the current best is merged. A hypothesis whose next test would cost more than it could tell us is pruned. The rest stay open."),
("A dropped hypothesis stays in the tree, marked dropped, so you can see it was considered.","A dropped hypothesis stays in the tree, marked dropped. You can see it was considered."),
("Check a hypothesis whose source you do not recognise before you authorize spend on it.","Check a hypothesis from an unfamiliar source before you authorize spend on it."),
("Each failure is matched to the hypothesis it belongs to, so the tree learns from it instead of losing it.","Each failure is matched to the hypothesis it belongs to. The tree keeps it as evidence."),
("researched at CALIBRATE, so another device can pick up the project where this one stopped.","researched at CALIBRATE. Another device can then pick up the project where this one stopped."),
("What moves is the full belief, not a summary, so nothing measured is lost.","What moves is the full belief. Every measurement is kept."),
("On the web and on phones, the agents are not offered here (they run on a desktop or an executor), so step 2 starts with Diskuv SaaS.","On the web and on phones, step 2 starts with Diskuv SaaS. Coding agents run on a desktop or an executor."),
("Invited, not yet joined","Invited, waiting to join"),
("which the mecha reads as evidence about the protocol, not about the hypothesis.","which the mecha reads as evidence about the protocol."),
]
files=glob.glob('canvas/project/*.dc.html')+glob.glob('gen/*.py')
for a,b in P:
    n=0
    for f in files:
        if f.endswith('docpass.py') or f.endswith('scan.py'): continue
        s=open(f).read()
        for x,y in [(a,b),(a.replace("'","\\'"),b.replace("'","\\'"))]:
            if x in s: n+=s.count(x); s=s.replace(x,y)
        open(f,'w').write(s)
    if n==0: print('MISSING',a[:70])
print('done')
