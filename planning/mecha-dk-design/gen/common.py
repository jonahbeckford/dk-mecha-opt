import os
src=open(os.path.join(os.path.dirname(__file__),'stages.py')).read()
ns={}
exec(src.split("DONE = lambda")[0].replace("OUT = sys.argv[1]","OUT = None"), ns)
globals().update({k:ns[k] for k in ['HEAD','TAIL','btn','a','section','p','tag','table','ul','BTN','PRI']})
FS='min-height: 44px; box-sizing: border-box; padding: 0 10px; font-size: 15px; border: 1px solid {{c.line}}; border-radius: 6px; background: {{c.bg}}; color: {{c.ink}}'
LB='display: flex; flex-direction: column; gap: 4px; flex: 1 1 200px; font-size: 14px; font-weight: 600'
def sel(label, opts, flex='1 1 200px', aria=None):
    o=''.join(f'<option{" selected" if i==0 else ""}>{x}</option>' for i,x in enumerate(opts))
    if aria: return f'<select aria-label="{aria}" style="{FS}; flex: {flex}">{o}</select>'
    return f'<label style="{LB.replace("1 1 200px",flex)}">{label}<select style="{FS}">{o}</select></label>'
def inp(label, val='', typ='text', flex='1 1 200px', mono=False, ph=''):
    m="; font-family: 'Ubuntu Mono', monospace" if mono else ''
    return f'<label style="{LB.replace("1 1 200px",flex)}">{label}<input type="{typ}" value="{val}" placeholder="{ph}" style="{FS}{m}"></label>'
def chk(label, on=False, locked=False):
    return f'<label style="display: flex; align-items: center; gap: 8px; flex: 1 1 100%; min-height: 44px; font-size: 14px"><input type="checkbox"{" checked" if on or locked else ""}{" disabled" if locked else ""} style="width: 20px; height: 20px; margin: 0; flex: none"> {label}</label>'
def row(*x, align='flex-end'): return f'<div style="display: flex; flex-wrap: wrap; gap: 10px; align-items: {align}">' + ''.join(x) + '</div>'
def sub(f,o,n,c=1):
    s=open(f).read(); assert s.count(o)==c,(f,o[:80],s.count(o)); open(f,'w').write(s.replace(o,n))
