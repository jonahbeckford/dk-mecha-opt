import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
from common import *
f=sys.argv[1]; s=open(f).read()
MONO="font-family: 'Ubuntu Mono', monospace"
i=s.index('<div style="display: flex; flex-direction: column; gap: 6px; padding: 10px 12px; border: 1px solid {{c.line}}; border-radius: 6px"><div style="font-size: 15px; font-weight: 600">Hardware</div>')
j=s.index('<div style="display: flex; flex-direction: column; gap: 6px; padding: 10px 12px; border: 1px solid {{c.line}}; border-radius: 6px"><div style="font-size: 15px; font-weight: 600">Set up (optional)</div>')
old=s[i:j]
osf=old[old.index('<fieldset'):old.index('</fieldset>')+len('</fieldset>')]
def S(opts, aria, w='auto', first=0):
    o=''.join(f'<option{" selected" if k==first else ""}>{x}</option>' for k,x in enumerate(opts))
    return f'<select aria-label="{aria}" style="{FS}; width: {w}">{o}</select>'
def N(val, aria, w='96px', step='1', mn='0'):
    return f'<input type="number" aria-label="{aria}" value="{val}" min="{mn}" step="{step}" style="{FS}; width: {w}">'
DEL=lambda what: f'<button type="button" aria-label="Delete {what}" style="{BTN}; padding: 0 12px">Delete</button>'
def lab(title, key): return f'<span style="font-size: 14px; font-weight: 600">{title} <code style="font-weight: 400; color: {{{{c.mut}}}}">{key}</code></span>'
def fld(title,key,inner,flex='1 1 220px'):
    return f'<div role="group" aria-label="{title}" style="flex: {flex}; min-width: 0; display: flex; flex-direction: column; gap: 4px">{lab(title,key)}<div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: center">{inner}</div></div>'
LISTBOX='display: flex; flex-direction: column; gap: 6px; padding: 8px; border: 1px solid {{c.line}}; border-radius: 6px'
accrow=lambda name,count: f'<div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: center">{S(["H100","A100-80GB","A100","L4","T4","[TPU type]","[the executors\x27 catalog]"],"Accelerator",first=["H100","A100-80GB","A100","L4","T4"].index(name))}<span style="font-size: 14px">×</span>{N(count,"Count",w="80px",mn="1")}{DEL("accelerator")}</div>'
acc=(f'<div style="{LISTBOX}; width: 100%">'
     + f'<div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: center"><span style="font-size: 13px">Use</span>{S(["any one of these","the first available, in this order"],"How to choose")}</div>'
     + accrow('H100',8) + accrow('A100-80GB',8)
     + f'<div>{btn("Add an accelerator")}</div></div>')
argrow=lambda k,v: f'<div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: center">{S(["runtime_version","tpu_name","tpu_vm"],"Argument",first=["runtime_version","tpu_name","tpu_vm"].index(k))}{S(v,"Value")}{DEL("argument")}</div>'
args=(f'<div style="{LISTBOX}; width: 100%">'
      + argrow('runtime_version',['[tpu-vm-base]','[other runtime versions]'])
      + argrow('tpu_vm',['true','false'])
      + f'<div>{btn("Add an argument")}</div><span style="font-size: 12px; color: {{{{c.mut}}}}">Shown only when a TPU is chosen. Values come from the executor.</span></div>')
atleast=lambda aria: S(['at least','exactly'],aria)
fields=[
 fld('Accelerators','accelerators',acc,'1 1 100%'),
 fld('Accelerator arguments','accelerator_args',args,'1 1 100%'),
 fld('CPUs','cpus',atleast('CPUs: at least or exactly')+N('4','CPUs')),
 fld('Memory','memory',atleast('Memory: at least or exactly')+N('32','Memory')+S(['GB','TB','MB'],'Memory unit')),
 fld('Instance type','instance_type',S(['Any that fits','[instance types that meet the choices above]'],'Instance type',w='100%'),'1 1 260px'),
 fld('Spot instances','use_spot',S(['No (default)','Yes'],'Spot instances')),
 fld('Disk size','disk_size',N('256','Disk size')+S(['GB','TB'],'Disk unit')),
 fld('Disk tier','disk_tier',S(['medium (default)','low','high','ultra','best'],'Disk tier')),
 fld('Network tier','network_tier',S(['standard (default)','best'],'Network tier')),
 fld('Most per hour','max_hourly_cost','<span style="font-size: 14px">USD</span>'+N('10.00','Most per hour, USD',step='0.01')+'<label style="display: inline-flex; align-items: center; gap: 6px; min-height: 44px; font-size: 13px"><input type="checkbox" style="width: 20px; height: 20px; margin: 0"> No limit</label>'),
]
new=f'<div style="display: flex; flex-direction: column; gap: 10px; padding: 10px 12px; border: 1px solid {{{{c.line}}}}; border-radius: 6px"><div style="font-size: 15px; font-weight: 600">Hardware</div><div style="font-size: 13px; color: {{{{c.mut}}}}; line-height: 1.45">What an executor must offer to run an experiment. Every choice is optional; left empty or "Any", it means any. The choices follow the SkyPilot task <code>resources</code> settings, and the lists come from the executors\' catalogs.</div>{row(osf)}{row(*fields, align="flex-start")}</div>'
s=s[:i]+new+s[j:]
open(f,'w').write(s)
