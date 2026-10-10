import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
from common import *
f=sys.argv[1]
s=open(f).read()
start=s.index('    <fieldset style="min-width: 0; margin: 0; background: {{c.surf}}; border: 1px solid {{c.line}}; border-radius: 8px; padding: 18px; display: flex; flex-direction: column; gap: 14px">\n      <legend style="font-size: 17px; font-weight: 600; padding: 0 6px">1. Scope</legend>')
end=s.index('    </fieldset>', start)+len('    </fieldset>')
H3='font-size: 15px; font-weight: 700; margin: 0'
SUB='font-size: 14px; color: {{c.mut}}; line-height: 1.45'
def blk(title, desc, body):
    return f'''      <div style="display: flex; flex-direction: column; gap: 8px; padding-top: 12px; border-top: 1px solid {{{{c.line}}}}">
        <h3 style="{H3}">{title}</h3>
        <div style="{SUB}">{desc}</div>
        {body}
      </div>
'''
TD='padding: 6px 10px; vertical-align: middle'
def trow(item, kind, access, limits):
    return f'<tr style="border-top: 1px solid {{{{c.line}}}}"><td style="{TD}">{item}</td><td style="{TD}; color: {{{{c.mut}}}}">{kind}</td><td style="{TD}">{access}</td><td style="{TD}">{limits}</td><td style="{TD}"><button type="button" aria-label="Edit" style="{BTN}">Edit</button></td></tr>'
def acc(v): return sel(None,['May change','May read'] if v=='c' else ['May read','May change'],'0 0 auto',aria='The mecha may')
items=f'''<div style="overflow-x: auto; border: 1px solid {{{{c.line}}}}; border-radius: 6px"><table style="width: 100%; min-width: 700px; border-collapse: collapse; font-size: 14px"><thead><tr style="text-align: left; color: {{{{c.mut}}}}"><th scope="col" style="{TD}; font-weight: 600">Item</th><th scope="col" style="{TD}; font-weight: 600">Kind</th><th scope="col" style="{TD}; font-weight: 600">The mecha</th><th scope="col" style="{TD}; font-weight: 600">Limits</th><th scope="col" style="{TD}"><span style="position: absolute; left: -9999px">Actions</span></th></tr></thead><tbody>'''+''.join([
 trow('<code>[github.com/owner/app]</code>','Repository, branch [main]',acc('c'),'Only <code>src/</code> and <code>build.gradle</code>'),
 trow('<code>[github.com/owner/spec]</code>','Repository, pinned to [v1.2]',acc('r'),'Whole repository'),
 trow('<code>description.md</code>','File in the project folder',acc('r'),''),
 trow('<code>data/train.csv</code>','Data in the project folder',acc('r'),''),
 trow('[Incubation temperature]','Parameter',acc('c'),'[30] to [40] [°C]'),
])+'</tbody></table></div>'
items+='\n        '+row(btn('Add repository'),btn('Add file or folder'),btn('Add a parameter'),align='center')
items+=f'\n        <div style="font-size: 13px; color: {{{{c.mut}}}}; line-height: 1.45">Anything not listed is out of reach. Repositories here are the same list as <a href="Environment.dc.html" style="color: {{{{c.acc}}}}">Experiment environment</a>: one the mecha may change follows its branch, one it may only read is pinned. A parameter is something a person sets in an experiment, such as a temperature or a dose, with the range the mecha may choose from. Whatever the mecha may read is also shown to an LLM.</div>'
measure=row(sel('Cases come from',['Tests run by a command: each test is a case','A grader the mecha cannot see: only the result comes back','A person, following each experiment\'s protocol','A list of cases you provide'],'2 1 320px'),
            sel('Each case gives',['Pass or fail','A number, lower is better','A number, higher is better'],'1 1 200px'))
measure+='\n        '+row(inp('Command','[./gradlew test]',flex='2 1 260px',mono=True),sel('Run in',['[github.com/owner/app]','The project folder'],'1 1 220px'))
measure+='\n        '+chk('Also check nothing else broke: one more case that fails if any test that passed before now fails',on=True)
measure+='\n        '+chk('Leave out tests that already fail on the starting version; no change is ever charged for them',on=True)
proto=row(sel('Protocol of record',['A file in a repository','A document you upload','None yet: the mecha drafts one at the start, for your review'],'1 1 320px'),inp('File','[github.com/owner/spec]/SPECIFICATION.md',flex='2 1 300px',mono=True))
oob='<div style="display: flex; flex-direction: column">'+''.join([
 chk('Secrets, keys and sign-ins (always)',locked=True),
 chk('How results are measured: the test command, the grader and their data (always; change them in project settings)',locked=True),
 chk('Internet access for the program being tested',on=True),
 chk('Hidden test data and answers, when a grader holds them',on=True)])+'</div>'
oob+=f'\n        <label style="display: flex; flex-direction: column; gap: 4px; font-size: 14px; font-weight: 600">Anything else<span style="font-weight: 400; color: {{{{c.mut}}}}">Hazards, ethics and approval limits, budget ceilings. Experiments sent to a person show these as "Stop if" and "Never".</span><textarea rows="2" style="box-sizing: border-box; width: 100%; padding: 8px 10px; font-size: 15px; border: 1px solid {{{{c.line}}}}; border-radius: 6px; background: {{{{c.bg}}}}; color: {{{{c.ink}}}}"></textarea></label>'
new=f'''    <fieldset style="min-width: 0; margin: 0; background: {{{{c.surf}}}}; border: 1px solid {{{{c.line}}}}; border-radius: 8px; padding: 18px; display: flex; flex-direction: column; gap: 14px">
      <legend style="font-size: 17px; font-weight: 600; padding: 0 6px">1. Scope</legend>
      <label style="display: flex; flex-direction: column; gap: 4px; font-size: 15px; font-weight: 600">Aim<span style="{SUB}; font-weight: 400">The broad aim every hypothesis refines, in a sentence. For example "Every test of the program passes" or "Yield rises without lowering purity". Required.</span><textarea rows="2" style="box-sizing: border-box; width: 100%; padding: 8px 10px; font-size: 16px; border: 1px solid {{{{c.line}}}}; border-radius: 6px; background: {{{{c.bg}}}}; color: {{{{c.ink}}}}"></textarea></label>
''' + blk('What the mecha may change and read','Repositories, files and data it works with, and the parameters it may set. For each, choose whether it may change it or only read it.', items) \
    + blk('What you measure','Where the cases come from and what each one reports. Outcomes you care about, and how they trade off, are in section 2.', measure) \
    + blk('Protocol of record','The specification, protocol or pre-registration. When a change is adopted, you review it against this.', proto) \
    + blk('Out of bounds','What no one, person or program, may touch or be asked to do.', oob) + '    </fieldset>'
s=s[:start]+new+s[end:]
# templates picker before Project title
tcard=lambda t,d,on=False: f'<label style="flex: 1 1 220px; display: flex; gap: 10px; align-items: flex-start; padding: 12px; border: {"2px solid {{c.acc}}" if on else "1px solid {{c.line}}"}; border-radius: 8px; background: {{{{c.surf}}}}; cursor: pointer"><input type="radio" name="tpl"{" checked" if on else ""} style="width: 20px; height: 20px; margin: 2px 0 0; flex: none"><span style="display: flex; flex-direction: column; gap: 2px"><span style="font-size: 15px; font-weight: 600">{t}</span><span style="font-size: 13px; color: {{{{c.mut}}}}; line-height: 1.4">{d}</span></span></label>'
tpl=f'''    <fieldset style="min-width: 0; margin: 0; padding: 0; border: 0; display: flex; flex-direction: column; gap: 8px">
      <legend style="font-size: 15px; font-weight: 600; padding: 0 0 6px">Start from</legend>
      <div style="display: flex; flex-wrap: wrap; gap: 10px">{tcard('Blank','Fill in every section yourself.',True)}{tcard('Fix a program until its tests pass','From the RunBugRun and Defects4J benchmarks. Each test is a case; a regression case catches breakage.')}{tcard('Do well in an ML competition','From the MLE-bench benchmark. A hidden grader scores each submission; revelations forbid leaking features.')}{tcard('[Your template]','Saved from [project], [date].')}</div>
      <div style="font-size: 13px; color: {{{{c.mut}}}}">A template fills sections 1 to 3. You can change anything it fills. Folder, people, executors and keys are never part of a template.</div>
    </fieldset>

'''
anchor='    <div style="display: flex; flex-direction: column; gap: 6px">\n      <label for="t"'
assert s.count(anchor)==1
s=s.replace(anchor,tpl+anchor)
# save as template after section 3
n3=s.index('3. Revelations</legend>'); e3=s.index('    </fieldset>',n3)+len('    </fieldset>')
s=s[:e3]+f'''
    <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 10px; margin-top: -8px">{btn('Save sections 1 to 3 as a template')}<span style="font-size: 13px; color: {{{{c.mut}}}}">For the next project like this one. Also in project settings.</span></div>'''+s[e3:]
open(f,'w').write(s)
