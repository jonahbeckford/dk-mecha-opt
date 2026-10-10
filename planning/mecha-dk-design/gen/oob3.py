import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
from common import *
f=sys.argv[1]; s=open(f).read()
MONO="font-family: 'Ubuntu Mono', monospace"
k=s.index('Out of bounds</h3>'); a=s.rindex('      <div style="display: flex; flex-direction: column; gap: 10px; padding-top: 12px;',0,k); b=s.index('    </fieldset>',k)
TD='padding: 6px 10px; vertical-align: middle'
cb=lambda on,aria: f'<input type="checkbox"{" checked" if on else ""} aria-label="{aria}" style="width: 20px; height: 20px; margin: 0">'
def srow(name, su, run, gr):
    return f'<tr style="border-top: 1px solid {{{{c.line}}}}"><th scope="row" style="{TD}; text-align: left; font-weight: 400"><code>{name}</code></th><td style="{TD}; text-align: center">{cb(su,name+", Set up")}</td><td style="{TD}; text-align: center">{cb(run,name+", Run the experiment")}</td><td style="{TD}; text-align: center">{cb(gr,name+", Grade out of sight")}</td></tr>'
th=''.join(f'<th scope="col" style="{TD}; font-weight: 600; text-align: {al}">{h}</th>' for h,al in [('Secret','left'),('Set up','center'),('Run the experiment','center'),('Grade out of sight','center')])
secrets=(f'<div style="display: flex; flex-direction: column; gap: 6px"><span style="font-size: 15px; font-weight: 600">Secrets each step may use</span>'
 f'<div style="overflow-x: auto; border: 1px solid {{{{c.line}}}}; border-radius: 6px"><table style="width: 100%; min-width: 520px; border-collapse: collapse; font-size: 14px"><thead><tr style="color: {{{{c.mut}}}}">{th}</tr></thead><tbody>'
 + srow('[HF_TOKEN]',True,False,False) + srow('[KAGGLE_API_KEY]',True,False,False) + srow('CLAUDE_CODE_OAUTH_TOKEN',False,True,False)
 + f'</tbody></table></div><span style="font-size: 13px; color: {{{{c.mut}}}}">A step gets only the secrets ticked for it. The list comes from <a href="Environment.dc.html" style="color: {{{{c.acc}}}}">Experiment environment</a>.</span></div>')
net='<label style="display: flex; align-items: center; gap: 8px; min-height: 44px; font-size: 15px"><input type="checkbox" checked style="width: 20px; height: 20px; margin: 0"> No internet for running and grading the experiment</label>'
tb=lambda t,aria: f'<button type="button" aria-label="{aria}" style="min-height: 36px; min-width: 36px; padding: 0 8px; font-size: 13px; border: 1px solid {{{{c.line}}}}; border-radius: 4px; background: transparent; color: {{{{c.ink}}}}">{t}</button>'
other=(f'<div style="display: flex; flex-direction: column; gap: 4px"><label for="oob" style="font-size: 15px; font-weight: 600">Anything else</label><span style="font-size: 13px; color: {{{{c.mut}}}}">Hazards, ethics and approval limits, budget ceilings, in your own words. People running an experiment see this as "Stop if" and "Never".</span>'
 f'<div style="border: 1px solid {{{{c.line}}}}; border-radius: 6px; overflow: hidden"><div role="toolbar" aria-label="Formatting" style="display: flex; flex-wrap: wrap; gap: 4px; padding: 4px; border-bottom: 1px solid {{{{c.line}}}}; background: {{{{c.surf}}}}">{tb("<b>B</b>","Bold")}{tb("<i>I</i>","Italic")}{tb("•","Bulleted list")}{tb("1.","Numbered list")}{tb("Preview","Preview")}</div>'
 f'<textarea id="oob" rows="6" style="display: block; box-sizing: border-box; width: 100%; padding: 10px 12px; font-size: 15px; line-height: 1.5; border: 0; background: {{{{c.bg}}}}; color: {{{{c.ink}}}}; resize: vertical">[Stop if the sample temperature passes 45 °C.\n\nNever use more than [amount] of reagent [name] in one experiment.]</textarea></div></div>')
H='      <div style="display: flex; flex-direction: column; gap: 10px; padding-top: 12px; border-top: 1px solid {{c.line}}">\n'
secrets=secrets.replace('<span style="font-size: 15px; font-weight: 600">Secrets each step may use</span>','<h3 style="font-size: 15px; font-weight: 700; margin: 0">Secrets each step may use</h3>',1)
other=other.replace('<label for="oob" style="font-size: 15px; font-weight: 600">Anything else</label>','<label for="oob" style="font-size: 14px; font-weight: 600">Anything else no one may do</label>',1)
new=(H+'        '+secrets+'\n      </div>\n'+H+'        <h3 style="font-size: 15px; font-weight: 700; margin: 0">Out of bounds</h3>\n        '+net+'\n        '+other+'\n      </div>\n')
s=s[:a]+new+s[b:]
open(f,'w').write(s)
