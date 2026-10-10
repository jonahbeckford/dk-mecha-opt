import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
from common import *
f=sys.argv[1]; s=open(f).read()
def rep(a,b,c=1):
    global s; assert s.count(a)==c,(a[:80],s.count(a)); s=s.replace(a,b)
rep(' after <code>--</code>, not as an environment variable,',' after <code>--</code>,')
# remove Hardware select in Where it runs
m=re.search(r'<label style="display: flex; flex-direction: column; gap: 4px; flex: 0 1 180px; font-size: 14px; font-weight: 600">Hardware<select[^<]*(<option[^>]*>[^<]*</option>)*</select></label>',s)
assert m; s=s[:m.start()]+s[m.end():]
MONO="font-family: 'Ubuntu Mono', monospace"
osbox=''.join(f'<label style="display: inline-flex; align-items: center; gap: 8px; min-height: 44px; padding: 0 12px; border: 1px solid {{{{c.line}}}}; border-radius: 6px; font-size: 14px"><input type="checkbox"{" checked" if o!="Windows" else ""} style="width: 20px; height: 20px; margin: 0"> {o}</label>' for o in ['macOS','Linux','Windows'])
osf=f'<fieldset style="min-width: 0; flex: 1 1 100%; margin: 0; padding: 0; border: 0; display: flex; flex-direction: column; gap: 6px"><legend style="font-size: 14px; font-weight: 600; padding: 0 0 4px">Operating systems it can run on</legend><div style="display: flex; flex-wrap: wrap; gap: 8px">{osbox}</div><span style="font-size: 12px; color: {{{{c.mut}}}}">Tick all three if it runs anywhere; an executor on another system is never chosen.</span></fieldset>'
def k(label, key, val, flex='1 1 180px', typ='text'):
    return f'<label style="{LB.replace("1 1 200px",flex)}">{label} <code style="font-weight: 400; color: {{{{c.mut}}}}">{key}</code><input type="{typ}" value="{val}" style="{FS}; {MONO}"></label>'
def ks(label, key, opts, flex='1 1 180px'):
    o=''.join(f'<option{" selected" if i==0 else ""}>{x}</option>' for i,x in enumerate(opts))
    return f'<label style="{LB.replace("1 1 200px",flex)}">{label} <code style="font-weight: 400; color: {{{{c.mut}}}}">{key}</code><select style="{FS}">{o}</select></label>'
fields=[k('Accelerators','accelerators','[H100:8]'),
        k('Accelerator arguments (TPU only)','accelerator_args','[runtime_version: tpu-vm-base]','1 1 260px'),
        k('CPUs','cpus','[4+]'), k('Memory, GB','memory','[32+]'),
        k('Instance type','instance_type','[p3.8xlarge]'),
        ks('Spot instances','use_spot',['No (default)','Yes']),
        k('Disk size, GB','disk_size','[256]'),
        ks('Disk tier','disk_tier',['medium (default)','low','high','ultra','best']),
        ks('Network tier','network_tier',['standard (default)','best']),
        k('Most per hour, USD','max_hourly_cost','[10.0]')]
step=f'<div style="display: flex; flex-direction: column; gap: 6px; padding: 10px 12px; border: 1px solid {{{{c.line}}}}; border-radius: 6px"><div style="font-size: 15px; font-weight: 600">Hardware</div><div style="font-size: 13px; color: {{{{c.mut}}}}; line-height: 1.45">What an executor must offer to run an experiment. Every field is optional; empty means any. The fields follow the SkyPilot task <code>resources</code> settings.</div>{row(osf)}{row(*fields)}</div>'
anchor='<div style="display: flex; flex-direction: column; gap: 6px; padding: 10px 12px; border: 1px solid {{c.line}}; border-radius: 6px"><div style="font-size: 15px; font-weight: 600">Set up (optional)</div>'
rep(anchor, step+anchor)
open(f,'w').write(s)
