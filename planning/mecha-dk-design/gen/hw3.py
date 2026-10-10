import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
from common import *
f=sys.argv[1]; s=open(f).read()
def grp(label):
    a=s.index(f'<div role="group" aria-label="{label}"')
    # group ends with '</div></div>' (inner flex + group)
    b=s.index('</div></div>',a)+len('</div></div>'); return a,b
def cut(label):
    global s; a,b=grp(label); g=s[a:b]; s=s[:a]+s[b:]; return g
inst=cut('Instance type'); spot=cut('Spot instances')
def S(opts, aria, first=0):
    o=''.join(f'<option{" selected" if k==first else ""}>{x}</option>' for k,x in enumerate(opts))
    return f'<select aria-label="{aria}" style="{FS}; width: 100%">{o}</select>'
def fld(title,key,inner,help_,flex='1 1 260px'):
    return f'<div role="group" aria-label="{title}" style="flex: {flex}; min-width: 0; display: flex; flex-direction: column; gap: 4px"><span style="font-size: 14px; font-weight: 600">{title} <code style="font-weight: 400; color: {{{{c.mut}}}}">{key}</code></span><div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: center">{inner}</div><span style="font-size: 12px; color: {{{{c.mut}}}}; line-height: 1.4">{help_}</span></div>'
# replace disk tier and network tier groups
a,b=grp('Disk tier')
s=s[:a]+fld('Disk speed','disk_tier',S(['medium (default): about 3,000 IOPS, 220 MB/s read and write','low: about 1,000 IOPS, 90 MB/s','high: about 6,000 IOPS, 400 MB/s','ultra: about 60,000 IOPS, 4,000 MB/s read, 3,000 MB/s write','best: the fastest disk the executor offers'],'Disk speed'),'How fast the system disk reads and writes. IOPS is reads and writes per second. Figures are SkyPilot\'s rough estimates.','1 1 100%')+s[b:]
a,b=grp('Network tier')
s=s[:a]+fld('Network speed','network_tier',S(['standard (default): the executor\'s usual network','best: the fastest network the executor offers, such as AWS EFA or GCP GPUDirect'],'Network speed'),'Matters when an experiment moves a lot of data between machines. Most projects leave it at standard.','1 1 100%')+s[b:]
vm_inst=fld('Instance type','instance_type',
  '<div role="radiogroup" aria-label="Instance type" style="display: flex; flex-direction: column; gap: 4px; width: 100%">'
  '<label style="display: flex; align-items: center; gap: 8px; min-height: 44px; font-size: 14px"><input type="radio" name="it" checked style="width: 20px; height: 20px; margin: 0"> Let the executor choose one that meets the choices above</label>'
  '<label style="display: flex; flex-wrap: wrap; align-items: center; gap: 8px; min-height: 44px; font-size: 14px"><input type="radio" name="it" style="width: 20px; height: 20px; margin: 0"> This one: <select aria-label="Instance type name" style="'+FS+'"><option>[p3.8xlarge, AWS]</option><option>[other types the executors offer]</option></select></label></div>',
  'A cloud machine type by its provider\'s name. When accelerators are chosen, the type is worked out from them.')
vm_spot=fld('Spot instances','use_spot',S(['No (default): on-demand machines','Yes: spot machines'],'Spot instances'),'Spot machines cost less, but the cloud can take them back during a run; the experiment then runs again.')
vm=(f'<details style="flex: 1 1 100%; border: 1px solid {{{{c.line}}}}; border-radius: 6px; padding: 0 10px">'
    f'<summary style="min-height: 44px; display: flex; flex-wrap: wrap; align-items: center; gap: 4px 10px; cursor: pointer"><span aria-hidden="true" style="color: {{{{c.acc}}}}; font-weight: 700">+</span><span style="font-size: 14px; font-weight: 600">Cloud virtual machines</span><span style="font-size: 13px; color: {{{{c.mut}}}}">Executor chooses, on-demand</span></summary>'
    f'<div style="display: flex; flex-wrap: wrap; gap: 10px; padding: 4px 0 10px">{vm_inst}{vm_spot}</div></details>')
k=s.index('<details style="flex: 1 1 100%; border: 1px solid {{c.line}}; border-radius: 6px; padding: 0 10px"><summary style="min-height: 44px; display: flex; flex-wrap: wrap; align-items: center; gap: 4px 10px; cursor: pointer"><span aria-hidden="true" style="color: {{c.acc}}; font-weight: 700">+</span><span style="font-size: 14px; font-weight: 600">GPUs, TPUs')
s=s[:k]+vm+s[k:]
# advisory note
old='What an executor must offer to run an experiment. Every choice is optional; left empty or "Any", it means any.'
assert s.count(old)==1
s=s.replace(old,'What an experiment needs from an executor. Every choice is optional; left empty, it means any.')
hdr='<div style="font-size: 15px; font-weight: 600">Hardware</div>'
assert s.count(hdr)==1
s=s.replace(hdr,hdr+f'<div style="font-size: 13px; line-height: 1.45; padding: 8px 10px; border-radius: 6px; border: 1px solid {{{{c.warn}}}}; background: {{{{c.att}}}}"><strong>Advisory for now.</strong> These choices are saved with the project and shown when an experiment is sent, but no executor is held to them until Diskuv SaaS provides the machines.</div>')
open(f,'w').write(s)
