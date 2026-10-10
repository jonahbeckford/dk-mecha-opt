import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import *
f=sys.argv[1]; s=open(f).read()
start=s.index('<div style="overflow-x: auto; border: 1px solid {{c.line}}; border-radius: 6px"><table')
endm='Whatever the mecha may read is also shown to an LLM.</div>'
end=s.index(endm)+len(endm)
TD='padding: 6px 10px; vertical-align: middle'
MONO="font-family: 'Ubuntu Mono', monospace"
def acc(v):
    o={'c':['May change','May read'],'r':['May read','May change'],'o':['Produces']}[v]
    return sel(None,o,'0 0 auto',aria='The mecha')
def var(name): return f'<input aria-label="Variable" type="text" value="{name}" style="{FS}; width: 100%; min-width: 200px; {MONO}">'
def trow(item, kind, access, limits, v):
    return f'<tr style="border-top: 1px solid {{{{c.line}}}}"><td style="{TD}">{item}</td><td style="{TD}; color: {{{{c.mut}}}}">{kind}</td><td style="{TD}">{access}</td><td style="{TD}">{limits}</td><td style="{TD}">{var(v)}</td><td style="{TD}"><button type="button" style="{BTN}">Edit</button></td></tr>'
th=''.join(f'<th scope="col" style="{TD}; font-weight: 600">{h}</th>' for h in ['Item','Kind','The mecha','Limits','Variable'])
rows=[
 trow('<code>[github.com/owner/app]</code>','Repository, branch [main]',acc('c'),'Only <code>src/</code>, <code>train.py</code>','MECHA_REPO_APP'),
 trow('<code>[github.com/owner/spec]</code>','Repository, pinned to [v1.2]',acc('r'),'Whole repository','MECHA_REPO_SPEC'),
 trow('<code>description.md</code>','File in the project folder',acc('r'),'','MECHA_FILE_DESCRIPTION_MD'),
 trow('<code>[tasksource/ModernBERT-large-nli]</code>','Model, Hugging Face, revision [a1b2c3d]',acc('r'),'Downloaded once per executor, [1.6 GB]','MECHA_MODEL_MODERNBERT_LARGE_NLI'),
 trow('<code>[s3://bucket/train/]</code>','Dataset, object storage, version [v7], sha256 [9f2e…]',acc('r'),'[12 GB]','MECHA_DATA_TRAIN'),
 trow('Trained model','Output of each experiment, kept in [the project\'s artifact store]',acc('o'),'Kept for the [5] best versions','MECHA_OUT_MODEL'),
 trow('[Incubation temperature]','Parameter',acc('c'),'[30] to [40] [°C]','MECHA_PARAM_INCUBATION_TEMPERATURE'),
]
table=f'<div style="overflow-x: auto; border: 1px solid {{{{c.line}}}}; border-radius: 6px"><table style="width: 100%; min-width: 980px; border-collapse: collapse; font-size: 14px"><thead><tr style="text-align: left; color: {{{{c.mut}}}}">{th}<th scope="col" style="{TD}"><span style="position: absolute; left: -9999px">Actions</span></th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'
table+='\n        '+row(btn('Add repository'),btn('Add file or folder'),btn('Add model or dataset'),btn('Add an output'),btn('Add a parameter'),align='center')
table+=f'''
        <div style="font-size: 13px; color: {{{{c.mut}}}}; line-height: 1.45">Anything not listed is out of reach. Repositories here are the same list as <a href="Environment.dc.html" style="color: {{{{c.acc}}}}">Experiment environment</a>: one the mecha may change follows its branch, one it may only read is pinned. Whatever the mecha may read is also shown to an LLM.</div>
        <div style="font-size: 13px; color: {{{{c.mut}}}}; line-height: 1.45"><strong style="color: {{{{c.ink}}}}">Variable</strong>: each item reaches the experiment's scripts as an environment variable: a path for files, folders, models and data, the value for a parameter, the place to write for an output. The name is made from the kind and the item's name; change it if your scripts expect another.</div>
        <div style="font-size: 13px; color: {{{{c.mut}}}}; line-height: 1.45"><strong style="color: {{{{c.ink}}}}">Too large for git</strong>: a model or dataset is named by where it lives and pinned to a version or checksum: a Hugging Face model and revision, a web address with its sha256, an object-storage path with its version, or an MLflow registered model version. Each executor downloads it once into a cache and reuses it. A version of the project records the pin, not the bytes. An output, such as trained weights, is saved to the artifact store you choose (the project folder, object storage or MLflow), and each version records its checksum.</div>'''
s=s[:start]+table+s[end:]
# "How an experiment runs" block, inserted before Protocol of record block
H3='font-size: 15px; font-weight: 700; margin: 0'
SUB='font-size: 14px; color: {{c.mut}}; line-height: 1.45'
def step(title, desc, *fields):
    return f'<div style="display: flex; flex-direction: column; gap: 6px; padding: 10px 12px; border: 1px solid {{{{c.line}}}}; border-radius: 6px"><div style="font-size: 15px; font-weight: 600">{title}</div><div style="font-size: 13px; color: {{{{c.mut}}}}; line-height: 1.45">{desc}</div>{row(*fields)}</div>'
run=''.join([
 step('Where it runs','A container image every experiment starts from.', sel('Image',['Built from a Dockerfile in a repository','A published image','The executor\'s default image'],'1 1 260px'), inp('Dockerfile or image','[github.com/owner/app]/Dockerfile',flex='2 1 300px',mono=True), sel('Hardware',['CPU only','A GPU'],'0 1 160px')),
 step('Set up (optional)','Runs once per executor before the first experiment, to download or prepare inputs. The only step that may use the internet and the setup secrets.', inp('Command','[python prepare_data.py]',flex='1 1 100%',mono=True)),
 step('Run the experiment','Runs at every version the mecha tests: trains, builds or runs the program, then measures each case. It writes one line per case to the file in <code>MECHA_RESULTS</code>: <code>{"id", "passed"}</code> or <code>{"id", "value"}</code>.', inp('Command','[python train.py && python evaluate.py]',flex='1 1 100%',mono=True), sel('Time limit',['[2 hours]','[30 minutes]','[8 hours]'],'0 1 180px')),
 step('Grade out of sight (optional)','For hidden answers: runs in a separate container with the hidden data, and passes back only the result per case, never the answers or a score the mecha could tune against.', inp('Command','[python grade.py]',flex='1 1 100%',mono=True)),
 step('What the LLM is told','The task in words, read before proposing hypotheses and writing each experiment, and any standing instructions.', sel('Task description',['description.md','A file in a repository','None'],'1 1 220px'), inp('Standing instructions','[Build a sound validation before you trust any score.]',flex='2 1 320px')),
])
run+=f'''
        <div style="font-size: 13px; color: {{{{c.mut}}}}; line-height: 1.45">Mecha DK does the rest itself: it saves each version, fingerprints what changed, records every result and works out what it means. A template fills these in; the two benchmark templates come with working scripts.</div>
        <div style="display: flex; flex-wrap: wrap; gap: 10px; align-items: center">{btn('Check by measuring the starting version', True)}<span style="font-size: 13px; color: {{{{c.mut}}}}">Runs set up and one experiment on the starting version, before the first cycle. The project cannot start until this passes.</span></div>'''
blk=f'''      <div style="display: flex; flex-direction: column; gap: 8px; padding-top: 12px; border-top: 1px solid {{{{c.line}}}}">
        <h3 style="{H3}">How an experiment runs</h3>
        <div style="{SUB}">The scripts the mecha calls. Each runs inside the executor with the variables above.</div>
        {run}
      </div>
'''
anchor='      <div style="display: flex; flex-direction: column; gap: 8px; padding-top: 12px; border-top: 1px solid {{c.line}}">\n        <h3 style="font-size: 15px; font-weight: 700; margin: 0">Protocol of record</h3>'
assert s.count(anchor)==1
s=s.replace(anchor, blk+anchor)
# measure block: drop the duplicated command row (moved into "Run the experiment")
import re
m=re.search(r'\n        <div style="display: flex; flex-wrap: wrap; gap: 10px; align-items: flex-end"><label[^\n]*>Command<input[^\n]*</div>', s)
assert m, 'command row'
s=s[:m.start()]+s[m.end():]
# template card for fine-tuning
tc='[Your template]'
i=s.index('<label style="flex: 1 1 220px; display: flex; gap: 10px; align-items: flex-start; padding: 12px; border: 1px solid {{c.line}}; border-radius: 8px; background: {{c.surf}}; cursor: pointer"><input type="radio" name="tpl" style="width: 20px; height: 20px; margin: 2px 0 0; flex: none"><span style="display: flex; flex-direction: column; gap: 2px"><span style="font-size: 15px; font-weight: 600">[Your template]')
card='<label style="flex: 1 1 220px; display: flex; gap: 10px; align-items: flex-start; padding: 12px; border: 1px solid {{c.line}}; border-radius: 8px; background: {{c.surf}}; cursor: pointer"><input type="radio" name="tpl" style="width: 20px; height: 20px; margin: 2px 0 0; flex: none"><span style="display: flex; flex-direction: column; gap: 2px"><span style="font-size: 15px; font-weight: 600">Fine-tune a classifier</span><span style="font-size: 13px; color: {{c.mut}}; line-height: 1.4">From the Paper I refinement classifier: a ModernBERT model tuned with LoRA on a GPU, scored on a held-out test set.</span></span></label>'
s=s[:i]+card+s[i:]
open(f,'w').write(s)
