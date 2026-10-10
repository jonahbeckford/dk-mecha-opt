import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import *
f=sys.argv[1]; s=open(f).read()
MONO="font-family: 'Ubuntu Mono', monospace"
def rep(a,b,c=1):
    global s; assert s.count(a)==c,(a[:80],s.count(a)); s=s.replace(a,b)
# Where it runs
rep('What each experiment needs, brought in with one or more <code>dk0 import</code>. Each is pinned, so every version runs on the same tools.',
    'The packages each experiment needs, added with <code>dk0 add</code> from a GitHub release. Each is pinned to its tag, so every version runs on the same tools. A release must carry a distribution with a SLSA Level 2 attestation, and you accept each producer\'s key once.')
rep('<code style="flex: none; font-size: 14px">dk0 import</code>','<code style="flex: none; font-size: 14px">dk0 add github-l2</code>',2)
rep('value="[first import]"','value="[owner/repo@tag]"'); rep('value="[second import]"','value="[host/owner/repo@tag]"')
rep('<span style="position: absolute; left: -9999px">Import</span>','<span style="position: absolute; left: -9999px">Package</span>',2)
rep(btn('Add an import'),btn('Add a package'))
# run-object fields: replace single Object field with module, slot, command
def ro(prefix):
    return (f'<label style="{LB.replace("1 1 200px","2 1 260px")}">Object<span style="display: flex; gap: 8px; align-items: center"><code style="flex: none; font-size: 14px; font-weight: 400">dk0 run-object</code><input type="text" value="[{prefix}MODULE@VERSION]" style="{FS}; flex: 1 1 auto; {MONO}"></span></label>'
            + inp('Slot','[slot]',flex='1 1 160px',mono=True)
            + sel('Runs',['A command (-c)','A member (-m)'],'0 1 180px')
            + inp('Command or member','[run.sh]',flex='1 1 200px',mono=True))
import re
for prefix,ph in [('','[experiment object]'),('Grader_','[grader object]')]:
    pat=re.compile(r'<label style="display: flex; flex-direction: column; gap: 4px; flex: 2 1 320px; font-size: 14px; font-weight: 600">Object<span[^>]*><code[^>]*>dk0 run-object</code><input type="text" value="'+re.escape(ph)+r'"[^>]*></span></label>')
    m=pat.search(s); assert m, ph
    s=s[:m.start()]+ro(prefix)+s[m.end():]
# preview box
i=s.index('<div style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border: 1px solid {{c.line}}; border-radius: 6px; background: {{c.bg}}"><span style="font-size: 13px; font-weight: 600">What <code>dk0 run-object</code> is given</span>')
j=s.index('[The exact parameter form follows <code>dk0 run-object</code>.]</span></div>',i)+len('[The exact parameter form follows <code>dk0 run-object</code>.]</span></div>')
lines=['dk0 run-object [MODULE@VERSION] -s [slot] -c [run.sh] --','  --rw-repo app=[path]','  --rw-param incubation_temperature=[37]','  --ro-repo spec=[path]','  --ro-file description=[path]','  --ro-model modernbert_large_nli=[path]','  --ro-data train=[path]','  --out model=[path]','  --results [path]']
pre='<pre style="margin: 0; overflow-x: auto; font-size: 13px; line-height: 1.5; '+MONO+'">'+'\n'.join(lines)+'</pre>'
box=f'<div style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border: 1px solid {{{{c.line}}}}; border-radius: 6px; background: {{{{c.bg}}}}"><span style="font-size: 13px; font-weight: 600">What the experiment is given, after <code>--</code></span>{pre}<span style="font-size: 12px; color: {{{{c.mut}}}}">Proposed: <code>--rw-KIND</code> for what the mecha may change, <code>--ro-KIND</code> for what it may only read, <code>--out</code> for outputs, where KIND is repo, file, dir, model, data or param. To be settled with <code>dk0</code>.</span></div>'
s=s[:i]+box+s[j:]
rep('each item is given to <code>dk0 run-object</code> as a parameter, not an environment variable,','each item is given to <code>dk0 run-object</code> as an argument after <code>--</code>, not an environment variable,')
open(f,'w').write(s)
