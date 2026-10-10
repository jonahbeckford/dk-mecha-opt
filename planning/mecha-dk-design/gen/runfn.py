import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
from common import *
f=sys.argv[1]; s=open(f).read()
MONO="font-family: 'Ubuntu Mono', monospace"
def rep(a,b,c=1):
    global s; assert s.count(a)==c,(a[:80],s.count(a)); s=s.replace(a,b)
old_sel='<label style="display: flex; flex-direction: column; gap: 4px; flex: 0 1 180px; font-size: 14px; font-weight: 600">Runs<select style="'+FS+'"><option selected>A command (-c)</option><option>A member (-m)</option></select></label>'
new_sel='<label style="display: flex; flex-direction: column; gap: 4px; flex: 1 1 260px; font-size: 14px; font-weight: 600">Runs<select style="'+FS+'"><option selected>dk0 run-function: a function rule</option><option>dk0 run-object: a command (-c)</option><option>dk0 run-object: a member (-m)</option></select></label>'
rep(old_sel,new_sel,2)
rep('<code style="flex: none; font-size: 14px; font-weight: 400">dk0 run-object</code>','<code style="flex: none; font-size: 14px; font-weight: 400">dk0 run-…</code>',2)
rep('>Slot<input type="text" value="[slot]"','>Slot (run-object only)<input type="text" value="[slot]"',2)
rep('>Command or member<input type="text" value="[run.sh]"','>Command or member (run-object only)<input type="text" value="[run.sh]"',2)
# preview
i=s.index('<span style="font-size: 13px; font-weight: 600">What the experiment is given, after <code>--</code></span>')
j=s.index('To be settled with <code>dk0</code>.</span></div>',i)+len('To be settled with <code>dk0</code>.</span></div>')
words=['rw[repo][app]=[path]','rw[param][incubation_temperature]=37','ro[repo][spec]=[path]','ro[file][description]=[path]','ro[model][modernbert_large_nli]=[path]','ro[data][train]=[path]','out[model]=[path]']
pre1='dk0 run-function [MODULE@VERSION] -d [results]/ --\n  '+'\n  '.join(words)
pre2='dk0 run-object [MODULE@VERSION] -s [slot] -c [run.sh] --\n  '+'\n  '.join(words)
P=lambda t: '<pre style="margin: 0; overflow-x: auto; font-size: 13px; line-height: 1.5; '+MONO+'">'+t+'</pre>'
doc='{"rw": {"repo": {"app": …}, "param": {"incubation_temperature": 37}},\n "ro": {"repo": {"spec": …}, "file": {…}, "model": {…}, "data": {…}},\n "out": {"model": …}}'
new=('<span style="font-size: 13px; font-weight: 600">What the experiment is given, after <code>--</code></span>'
 + '<span style="font-size: 13px">As a function rule, the words form its request document:</span>'+P(pre1)
 + '<span style="font-size: 13px">which the rule reads as <code>request.user</code>:</span>'+P(doc)
 + '<span style="font-size: 13px">As an object, the same words are its arguments:</span>'+P(pre2)
 + '<span style="font-size: 12px; color: {{c.mut}}">Read-write items sit under <code>rw</code>, read-only items under <code>ro</code>, outputs under <code>out</code>, each grouped by kind. Proposed; to be settled with <code>dk0</code>.</span></div>')
s=s[:i]+new+s[j:]
rep('each item is given to <code>dk0 run-object</code> as an argument after <code>--</code>, not an environment variable,','each item is given to <code>dk0 run-function</code> or <code>dk0 run-object</code> after <code>--</code>, not as an environment variable,')
open(f,'w').write(s)
