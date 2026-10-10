import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
from common import *
f=sys.argv[1]; s=open(f).read()
MONO="font-family: 'Ubuntu Mono', monospace"
# 1 remove judge role
m=re.search(r'\n\s*<div style="display: flex; flex-direction: column; gap: 4px; flex: 1 1 240px; min-width: 0"><label for="m3".*?</select></div>',s); assert m
s=s[:m.start()]+s[m.end():]
# 2 add judge outcome card after Accuracy card
L=lambda t,inner,flex: f'<label style="display: flex; flex-direction: column; gap: 4px; flex: {flex}; min-width: 0; font-size: 13px; font-weight: 600">{t}{inner}</label>'
def S(opts,first=0): return f'<select style="{FS}; width: 100%">'+''.join(f'<option{" selected" if i==first else ""}>{o}</option>' for i,o in enumerate(opts))+'</select>'
def I(v,mono=False,typ='text',ph=''): return f'<input type="{typ}" value="{v}" placeholder="{ph}" style="{FS}; width: 100%{"; "+MONO if mono else ""}">'
tb=lambda t,aria: f'<button type="button" aria-label="{aria}" style="min-height: 36px; min-width: 36px; padding: 0 8px; font-size: 13px; border: 1px solid {{{{c.line}}}}; border-radius: 4px; background: transparent; color: {{{{c.ink}}}}">{t}</button>'
judge=(f'<div role="group" aria-label="Judge" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-left: 3px solid {{{{c.acc}}}}; background: {{{{c.bg}}}}; border-radius: 0 6px 6px 0">'
  f'<span style="font-size: 14px; font-weight: 600">Judge</span>'
  f'<div style="display: flex; flex-wrap: wrap; gap: 8px 10px; align-items: flex-end">'
  + L('Judged by',S(['An LLM: [connection / model]','A person']),'2 1 220px')
  + L('How many judges',f'<span style="display: flex; align-items: center; gap: 6px"><input type="number" min="1" value="3" style="{FS}; width: 80px"><span style="font-weight: 400; font-size: 13px; color: {{{{c.mut}}}}">the median counts</span></span>','1 1 200px')
  + L('Looks at',S(['The change','The experiment\'s output','Both']),'1 1 180px')
  + L('Score from',f'<span style="display: flex; align-items: center; gap: 6px"><input type="number" value="0" aria-label="Lowest score" style="{FS}; width: 70px"><span aria-hidden="true" style="font-weight: 400">to</span><input type="number" value="100" aria-label="Highest score" style="{FS}; width: 70px"></span>','1 1 180px')
  + '</div>'
  + f'<div style="display: flex; flex-direction: column; gap: 4px"><div style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px 10px"><span style="font-size: 13px; font-weight: 600">Judge\'s instructions</span><span style="font-size: 12px; font-weight: 600; padding: 2px 8px; border-radius: 10px; background: {{{{c.sel}}}}">Saved with the template</span></div>'
  + f'<div style="border: 1px solid {{{{c.line}}}}; border-radius: 6px; overflow: hidden; background: {{{{c.surf}}}}"><div role="toolbar" aria-label="Formatting" style="display: flex; flex-wrap: wrap; gap: 4px; padding: 4px; border-bottom: 1px solid {{{{c.line}}}}">{tb("<b>B</b>","Bold")}{tb("<i>I</i>","Italic")}{tb("•","Bulleted list")}{tb("1.","Numbered list")}{tb("Preview","Preview")}</div>'
  + f'<textarea aria-label="Judge\'s instructions" rows="4" style="display: block; box-sizing: border-box; width: 100%; padding: 8px 10px; font-size: 14px; line-height: 1.5; border: 0; background: {{{{c.bg}}}}; color: {{{{c.ink}}}}; resize: vertical">[Score from 0 to 100 how well the change explains itself to a reader of the documentation: which inputs it affects and what happens at the edges.]</textarea></div></div>'
  + f'<span style="font-size: 12px; color: {{{{c.mut}}}}; line-height: 1.4">The score range becomes this outcome\'s typical range unless you change it. A judge reads text the mecha produced, so it can be steered by a prompt injection; changing the instructions is a measurement change.</span></div>')
card=(f'<li style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-top: 1px solid {{{{c.line}}}}">'
  f'<div style="display: flex; flex-wrap: wrap; gap: 8px 10px; align-items: flex-end">{L("Outcome",I("Documentation quality"),"2 1 160px")}{L("Comes from",S(["Cases that pass","A named value","A judge&#39;s score"],2),"2 1 170px")}{L("Value name",I("doc_quality",True),"1 1 150px")}{L("Better is",S(["Higher","Lower"]),"1 1 100px")}</div>'
  + judge +
  f'<div style="display: flex; flex-wrap: wrap; gap: 8px 10px; align-items: flex-end">{L("Unit",I("points"),"1 1 90px")}<div role="group" aria-label="Typical range" style="display: flex; flex-direction: column; gap: 4px; flex: 2 1 220px; min-width: 0; font-size: 13px; font-weight: 600">Typical range<span style="display: flex; align-items: center; gap: 6px"><input type="number" aria-label="Typical range, from" value="0" style="{FS}; width: 100%"><span aria-hidden="true" style="font-weight: 400">to</span><input type="number" aria-label="Typical range, to" value="100" style="{FS}; width: 100%"></span></div>{L("Never adopt if worse than",I("",typ="number",ph="No limit"),"1 1 160px")}<button type="button" style="{BTN}">Delete</button></div></li>')
k=s.index('value="Training time"'); li=s.rindex('<li style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px;',0,k)
s=s[:li]+card+s[li:]
# 3 weighing: rank list, ratings, weights for 4 outcomes
moves=['Tests pass, from 0 to 100%','Accuracy, from 70% to 95%','Documentation quality, from 0 to 100 points','Training time, from 120 to 10 minutes']
SB='min-width: 44px; min-height: 44px; padding: 0 10px; font-size: 15px; border: 1px solid {{c.line}}; border-radius: 6px; background: transparent; color: {{c.ink}}'
def item(n,label,first,last):
    up=f'<button type="button" aria-label="Move up: {label}"{" disabled" if first else ""} style="{SB}{"; opacity: 0.4" if first else ""}">↑</button>'
    dn=f'<button type="button" aria-label="Move down: {label}"{" disabled" if last else ""} style="{SB}{"; opacity: 0.4" if last else ""}">↓</button>'
    return (f'<li style="display: flex; flex-wrap: wrap; align-items: center; gap: 8px 12px; min-height: 52px; padding: 4px 10px; border-top: 1px solid {{{{c.line}}}}">'
            f'<span aria-hidden="true" style="cursor: grab; color: {{{{c.mut}}}}; font-size: 18px">⠿</span><span style="width: 24px; font-weight: 700">{n}.</span><span style="flex: 1 1 240px; font-size: 14px">{label}</span>{up}{dn}</li>')
lst=''.join(item(i+1,m,i==0,i==3) for i,m in enumerate(moves)).replace('border-top: 1px solid {{c.line}}','',1)
a=s.index('<ol aria-label="Outcomes in order of importance"'); a=s.index('>',a)+1; b=s.index('</ol>',a)
s=s[:a]+lst+s[b:]
def rate(name, prev, v):
    return (f'<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px 12px"><span style="flex: 1 1 260px; font-size: 14px">{name}, compared to {prev}</span>'
            f'<input type="range" min="1" max="100" value="{v}" aria-label="{name}, valued compared to {prev}, 1 to 100" style="flex: 2 1 200px; min-height: 44px"><span style="width: 40px; text-align: right; font-size: 14px">{v}</span></div>')
a=s.index('1 means almost nothing by comparison.</span>')+len('1 means almost nothing by comparison.</span>')
b=s.index('</div>\n',s.index('Training time, compared to Accuracy',a))
b=s.rindex('<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px 12px"><span style="flex: 1 1 260px; font-size: 14px">Training time, compared to Accuracy',a)
e=s.index('</span></div>',b)+len('</span></div>')
start=s.index('<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px 12px"><span style="flex: 1 1 260px; font-size: 14px">Accuracy, compared to Tests pass',a)
s=s[:start]+rate('Accuracy','Tests pass',60)+rate('Documentation quality','Accuracy',50)+rate('Training time','Documentation quality',50)+s[e:]
raw=[1,0.6,0.3,0.15]; tot=sum(raw); w=[round(x/tot,2) for x in raw]
w[-1]=round(1-sum(w[:-1]),2)
def wbar(name,v):
    return (f'<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px 12px"><span style="flex: 0 0 160px; font-size: 14px">{name}</span>'
            f'<span role="img" aria-label="{name}: weight {v:.2f}" style="position: relative; flex: 1 1 200px; height: 12px; border-radius: 6px; background: {{{{c.track}}}}"><span style="position: absolute; left: 0; width: {round(v*100)}%; top: 0; bottom: 0; border-radius: 6px; background: {{{{c.acc}}}}"></span></span>'
            f'<span style="width: 40px; text-align: right; font-size: 14px; {MONO}">{v:.2f}</span></div>')
a=s.index('The weights the mecha will use (they add up to 1.00)</span>')+len('The weights the mecha will use (they add up to 1.00)</span>')
b=s.index('</div></div>',s.index('Training time: weight',a))
b=s.index('</div>',s.index('Training time: weight',a))+len('</div>')
s=s[:a]+''.join(wbar(n,v) for n,v in zip(['Tests pass','Accuracy','Documentation quality','Training time'],w))+s[b:]
print(w,sum(w))
open(f,'w').write(s)
