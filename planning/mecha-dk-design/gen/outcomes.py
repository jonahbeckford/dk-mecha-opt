import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
from common import *
f=sys.argv[1]; s=open(f).read()
MONO="font-family: 'Ubuntu Mono', monospace"
k=s.index('2. What counts as a better result</legend>')
a=s.rindex('    <fieldset',0,k); b=s.index('    </fieldset>',k)+len('    </fieldset>')
TD='padding: 6px 8px; vertical-align: middle'
def S(opts,aria,first=0,w='auto'):
    return f'<select aria-label="{aria}" style="{FS}; width: {w}">'+''.join(f'<option{" selected" if i==first else ""}>{o}</option>' for i,o in enumerate(opts))+'</select>'
def I(v,aria,w='100%',mono=False,typ='text'):
    return f'<input type="{typ}" aria-label="{aria}" value="{v}" style="{FS}; width: {w}{"; "+MONO if mono else ""}">'
src=['Cases that pass','A value the run rule returns','A judge\'s score']
def orow(name, srci, key, better, unit, worst, best):
    keycell=I(key,'Value name',mono=True) if key else f'<span style="color: {{{{c.mut}}}}">none</span>'
    return (f'<tr style="border-top: 1px solid {{{{c.line}}}}"><td style="{TD}">{I(name,"Outcome")}</td><td style="{TD}">{S(src,"Comes from",srci)}</td><td style="{TD}">{keycell}</td>'
            f'<td style="{TD}">{S(["Higher","Lower"],"Better is",0 if better=="h" else 1)}</td><td style="{TD}">{I(unit,"Unit",w="90px")}</td><td style="{TD}">{I(worst,"Worst that matters",w="90px",typ="number")}</td><td style="{TD}">{I(best,"Best that matters",w="90px",typ="number")}</td>'
            f'<td style="{TD}"><button type="button" style="{BTN}">Delete</button></td></tr>')
th=''.join(f'<th scope="col" style="{TD}; font-weight: 600; text-align: left">{h}</th>' for h in ['Outcome','Comes from','Value name','Better is','Unit','Worst that matters','Best that matters'])
table=(f'<div style="overflow-x: auto; border: 1px solid {{{{c.line}}}}; border-radius: 6px"><table style="width: 100%; min-width: 980px; border-collapse: collapse; font-size: 14px"><thead><tr style="color: {{{{c.mut}}}}">{th}<th scope="col" style="{TD}"><span style="position: absolute; left: -9999px">Actions</span></th></tr></thead><tbody>'
       + orow('Tests pass',0,'','h','%','0','100') + orow('Accuracy',1,'accuracy','h','%','70','95') + orow('Training time',1,'train_minutes','l','minutes','120','10')
       + '</tbody></table></div>')
def swing(label, on=False):
    return f'<label style="display: flex; align-items: center; gap: 8px; min-height: 44px; font-size: 14px"><input type="radio" name="sw"{" checked" if on else ""} style="width: 20px; height: 20px; margin: 0"> {label}</label>'
def rate(label, v):
    return (f'<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px 12px"><span style="flex: 1 1 260px; font-size: 14px">{label}</span>'
            f'<input type="range" min="0" max="100" value="{v}" aria-label="{label}, compared with the first" style="flex: 2 1 200px; min-height: 44px"><span style="width: 40px; text-align: right; font-size: 14px">{v}</span></div>')
def wbar(name, w, lo, hi):
    return (f'<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px 12px"><span style="flex: 0 0 140px; font-size: 14px">{name}</span>'
            f'<span role="img" aria-label="{name}: weight {w}, likely between {lo} and {hi}" style="position: relative; flex: 1 1 200px; height: 12px; border-radius: 6px; background: {{{{c.track}}}}">'
            f'<span style="position: absolute; left: {int(lo*100)}%; width: {int((hi-lo)*100)}%; top: 0; bottom: 0; border-radius: 6px; background: {{{{c.wide}}}}"></span>'
            f'<span style="position: absolute; left: {int(w*100)}%; width: 3px; top: -3px; bottom: -3px; background: {{{{c.ink}}}}"></span></span>'
            f'<span style="font-size: 13px; {MONO}">{w:.2f} ({lo:.2f} to {hi:.2f})</span></div>')
weigh=f'''<details open style="border: 1px solid {{{{c.line}}}}; border-radius: 6px; padding: 0 12px">
          <summary style="min-height: 44px; display: flex; flex-wrap: wrap; align-items: center; gap: 4px 10px; cursor: pointer"><span aria-hidden="true" style="color: {{{{c.acc}}}}; font-weight: 700">+</span><span style="font-size: 15px; font-weight: 600">Weigh outcomes</span><span style="font-size: 13px; color: {{{{c.mut}}}}">Shown when there are two or more outcomes</span></summary>
          <div style="display: flex; flex-direction: column; gap: 12px; padding: 4px 0 12px">
            <fieldset style="min-width: 0; margin: 0; padding: 0; border: 0; display: flex; flex-direction: column; gap: 2px"><legend style="font-size: 14px; font-weight: 600; padding: 0 0 4px">1. Which one move would you want most?</legend>{swing("Tests pass from 0 to 100%",True)}{swing("Accuracy from 70% to 95%")}{swing("Training time from 120 to 10 minutes")}</fieldset>
            <div style="display: flex; flex-direction: column; gap: 4px"><span style="font-size: 14px; font-weight: 600">2. Compared with that move (100), how much is each other move worth?</span>{rate("Accuracy from 70% to 95%",60)}{rate("Training time from 120 to 10 minutes",15)}</div>
            <div style="display: flex; flex-direction: column; gap: 6px"><span style="font-size: 14px; font-weight: 600">The weights the mecha will use</span>{wbar("Tests pass",0.57,0.47,0.66)}{wbar("Accuracy",0.34,0.25,0.43)}{wbar("Training time",0.09,0.04,0.15)}
              <div style="font-size: 13px; line-height: 1.45; padding: 8px 10px; border-radius: 6px; background: {{{{c.att}}}}; border: 1px solid {{{{c.warn}}}}">The best hypotheses change order if Accuracy's weight falls below [0.25]. Answer that comparison with care.</div></div>
          </div>
        </details>'''
new=f'''    <fieldset style="min-width: 0; margin: 0; background: {{{{c.surf}}}}; border: 1px solid {{{{c.line}}}}; border-radius: 8px; padding: 18px; display: flex; flex-direction: column; gap: 12px">
      <legend style="font-size: 17px; font-weight: 600; padding: 0 6px">2. What counts as a better result</legend>
      <div style="font-size: 14px; color: {{{{c.mut}}}}; line-height: 1.45">The outcomes the experiment reports for each case, and which way is better. A value outcome is one the run rule returns by name for every case.</div>
      {table}
      <div>{btn("Add outcome")}</div>
      {weigh}
      <div style="font-size: 13px; color: {{{{c.mut}}}}; line-height: 1.45">After the project starts, a change here is a <a href="MeasurementChanges.dc.html" style="color: {{{{c.acc}}}}">measurement change</a>. A new weight recalculates scores from recorded results; a new outcome is measured again.</div>
    </fieldset>'''
s=s[:a]+new+s[b:]
# What you measure: drop "Each case gives" (now per outcome)
m=re.search(r'<label[^>]*>Each case gives<select[^<]*(<option[^>]*>[^<]*</option>)*</select></label>',s); assert m
s=s[:m.start()]+s[m.end():]
s=s.replace('Where the cases come from and what each one reports. Outcomes you care about, and how they trade off, are in section 2.','Where the cases come from. What each case reports, and how outcomes trade off, are in section 2.',1)
s=s.replace('returns one result per case: passed, or a value.','returns, for each case, whether it passed and the value of each outcome named in section 2.',1)
open(f,'w').write(s)
