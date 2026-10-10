import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
from common import *
f=sys.argv[1]; s=open(f).read()
MONO="font-family: 'Ubuntu Mono', monospace"
# 1. Variable column -> Passed as
s=s.replace('font-weight: 600">Variable</th>','font-weight: 600">Passed as</th>',1)
names={'MECHA_REPO_APP':'app','MECHA_REPO_SPEC':'spec','MECHA_FILE_DESCRIPTION_MD':'description','MECHA_MODEL_MODERNBERT_LARGE_NLI':'modernbert_large_nli','MECHA_DATA_TRAIN':'train','MECHA_OUT_MODEL':'model','MECHA_PARAM_INCUBATION_TEMPERATURE':'incubation_temperature'}
for k,v in names.items():
    o=f'<input aria-label="Variable" type="text" value="{k}"'
    assert s.count(o)==1,k
    s=s.replace(o,f'<input aria-label="Passed as" type="text" value="{v}"')
# 2. explanation
i=s.index('<div style="font-size: 13px; color: {{c.mut}}; line-height: 1.45"><strong style="color: {{c.ink}}">Variable</strong>')
j=s.index('</div>',i)+len('</div>')
grp=lambda title, items: f'<div style="flex: 1 1 200px; display: flex; flex-direction: column; gap: 2px"><span style="font-size: 12px; font-weight: 700; color: {{{{c.mut}}}}">{title}</span>' + ''.join(f'<span style="{MONO}; font-size: 13px">{x}</span>' for x in items) + '</div>'
preview=f'''<div style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border: 1px solid {{{{c.line}}}}; border-radius: 6px; background: {{{{c.bg}}}}"><span style="font-size: 13px; font-weight: 600">What <code>dk0 run-object</code> is given</span><div style="display: flex; flex-wrap: wrap; gap: 10px 20px">{grp('MAY CHANGE: REPOSITORY',['app'])}{grp('MAY CHANGE: PARAMETER',['incubation_temperature'])}{grp('MAY READ: REPOSITORY, FILE',['spec','description'])}{grp('MAY READ: MODEL, DATA',['modernbert_large_nli','train'])}{grp('OUTPUT',['model'])}</div><span style="font-size: 12px; color: {{{{c.mut}}}}">[The exact parameter form follows <code>dk0 run-object</code>.]</span></div>'''
s=s[:i]+'<div style="font-size: 13px; color: {{c.mut}}; line-height: 1.45"><strong style="color: {{c.ink}}">Passed as</strong>: each item is given to <code>dk0 run-object</code> as a parameter, not an environment variable, grouped by whether the mecha may change it or only read it, and by kind. So an object can tell what it may write, and a read-only item stays read-only. The name is made from the item\'s name; change it if your object expects another.</div>\n        '+preview+s[j:]
# 3. steps
def step_re(title):
    k=s.index(f'<div style="font-size: 15px; font-weight: 600">{title}</div>')
    a0=s.rindex('<div style="display: flex; flex-direction: column; gap: 6px; padding: 10px 12px;',0,k)
    # find end: matching closing of step: steps end with '</div></div>' sequence; use next step start or block end
    nxt=s.find('<div style="display: flex; flex-direction: column; gap: 6px; padding: 10px 12px;',k)
    if nxt==-1: nxt=s.index('\n        <div style="font-size: 13px; color: {{c.mut}}; line-height: 1.45">Mecha DK does the rest itself',k)
    return a0,nxt
def step(title, desc, *fields):
    return f'<div style="display: flex; flex-direction: column; gap: 6px; padding: 10px 12px; border: 1px solid {{{{c.line}}}}; border-radius: 6px"><div style="font-size: 15px; font-weight: 600">{title}</div><div style="font-size: 13px; color: {{{{c.mut}}}}; line-height: 1.45">{desc}</div>{row(*fields)}</div>'
imp=lambda v: f'<label style="display: flex; flex-direction: column; gap: 4px; flex: 1 1 100%; font-size: 14px; font-weight: 600"><span style="position: absolute; left: -9999px">Import</span><span style="display: flex; gap: 8px; align-items: center"><code style="flex: none; font-size: 14px">dk0 import</code><input type="text" value="{v}" style="{FS}; flex: 1 1 auto; {MONO}"></span></label>'
new_where=step('Where it runs','What each experiment needs, brought in with one or more <code>dk0 import</code>. Each is pinned, so every version runs on the same tools.', imp('[first import]'), imp('[second import]'), btn('Add an import'), sel('Hardware',['CPU only','A GPU'],'0 1 180px'))
ro=lambda v: f'<label style="display: flex; flex-direction: column; gap: 4px; flex: 2 1 320px; font-size: 14px; font-weight: 600">Object<span style="display: flex; gap: 8px; align-items: center"><code style="flex: none; font-size: 14px; font-weight: 400">dk0 run-object</code><input type="text" value="{v}" style="{FS}; flex: 1 1 auto; {MONO}"></span></label>'
new_run=step('Run the experiment','Runs at every version the mecha tests: trains, builds or runs the program, then measures each case. It is given the items above as parameters and returns one result per case: passed, or a value.', ro('[experiment object]'), sel('Time limit',['[2 hours]','[30 minutes]','[8 hours]'],'0 1 180px'))
new_grade=step('Grade out of sight (optional)','For hidden answers: a separate object, run apart from the experiment with only the hidden data and the experiment\'s output. It returns the result per case, never the answers or a score the mecha could tune against.', ro('[grader object]'))
for title,new in [('Where it runs',new_where),('Run the experiment',new_run),('Grade out of sight (optional)',new_grade)]:
    a0,b0=step_re(title); s=s[:a0]+new+s[b0:]
s=s.replace('The scripts the mecha calls. Each runs inside the executor with the variables above.','What the mecha calls. Each step runs inside the executor.',1)
open(f,'w').write(s)
