import sys, os, re, json
sys.path.insert(0, os.path.dirname(__file__))
from common import *
OUT=sys.argv[1]
s=open(os.path.join(OUT,'PIProject.dc.html')).read()
MONO="font-family: 'Ubuntu Mono', monospace"
# select the repair template
s=s.replace('<input type="radio" name="tpl" checked','<input type="radio" name="tpl"',1)
s=s.replace('border: 2px solid {{c.acc}}; border-radius: 8px; background: {{c.surf}}; cursor: pointer"><input type="radio" name="tpl"','border: 1px solid {{c.line}}; border-radius: 8px; background: {{c.surf}}; cursor: pointer"><input type="radio" name="tpl"',1)
k=s.index('Fix a program until its tests pass</span>'); lab=s.rindex('<label style="flex: 1 1 220px;',0,k)
seg=s[lab:k]
seg2=seg.replace('border: 1px solid {{c.line}}','border: 2px solid {{c.acc}}',1).replace('<input type="radio" name="tpl"','<input type="radio" name="tpl" checked',1)
s=s[:lab]+seg2+s[k:]
# cut sections 1..3 and the save line
a=s.index('    <fieldset',s.index('Project folder'))
a=s.rindex('    <fieldset',0,s.index('1. Scope</legend>'))
b=s.rindex('    <fieldset',0,s.index('4. Problems and hypotheses to start with</legend>'))
sv=s.index('    <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 10px; margin-top: -8px"><button type="button"')
sve=s.index('Also in project settings.</span></div>',sv)+len('Also in project settings.</span></div>')
s=s[:sv]+s[sve:]
from starting import section as start_section
s4a=s.index('    <fieldset',b); s4b=s.index('</fieldset>',s4a)+len('</fieldset>\n')
s=s[:s4a]+start_section([(1,'Problem','Find a change that makes the failing tests pass without breaking a passing test.','From the template'),(2,'Hypothesis','[A change to try, and what it should do]','',True)],
  'The template\'s problems and hypotheses are a starting point. Delete any you do not want for this project; the template keeps them.')+s[s4b:]
row_=lambda title, body, act: (f'<li style="display: flex; flex-wrap: wrap; align-items: flex-start; gap: 6px 14px; padding: 12px 0; border-top: 1px solid {{{{c.line}}}}">'
    f'<span style="flex: 0 0 200px; font-size: 15px; font-weight: 600">{title}</span><span style="flex: 1 1 320px; font-size: 14px; line-height: 1.5">{body}</span>{act}</li>')
ext=lambda t: f'<button type="button" style="{BTN}">{t}</button>'
rows=''.join([
 row_('Aim','Make the failing tests pass by editing the program, without breaking any test that passes now.',''),
 row_('What the mecha works on','Changes the repository you name above, only in its source folder. Tests and build files are read-only.',ext('Add items')),
 row_('How an experiment runs','<code>[Repair_Run@1.0]</code> runs the tests; each test is a case, plus one case for any test that broke. No internet.',''),
 row_('What counts as better','Tests pass, higher is better.',ext('Add an outcome')),
 row_('Revelations','[n] from the template.',ext('Add a revelation')),
 row_('Out of bounds','[Template text, if any.]',ext('Add to it')),
]).replace('border-top: 1px solid {{c.line}}','',1)
tb=lambda t: f'<span style="display: inline-flex; align-items: center; justify-content: center; min-width: 32px; min-height: 32px; font-size: 13px; color: {{{{c.mut}}}}">{t}</span>'
instr=(f'<div style="display: flex; flex-direction: column; gap: 4px"><div style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px 10px"><span style="font-size: 15px; font-weight: 600">Standing instructions</span><span style="font-size: 12px; font-weight: 600; padding: 2px 8px; border-radius: 10px; background: {{{{c.sel}}}}">From the template, read-only</span></div>'
       f'<div role="document" aria-label="Standing instructions, read-only" style="padding: 10px 12px; border: 1px dashed {{{{c.line}}}}; border-radius: 6px; background: {{{{c.bg}}}}; font-size: 14px; line-height: 1.5"><p style="margin: 0 0 6px">[You are repairing a buggy program. Edit only the source folder; never edit a test.]</p><p style="margin: 0">[A change is good when more failing tests pass and no passing test starts to fail.]</p></div>'
       f'<span style="font-size: 13px; color: {{{{c.mut}}}}">To change them, start from Blank, edit them, and save the result as a new template.</span></div>')
fill=(f'<div style="display: flex; flex-direction: column; gap: 10px; padding: 12px; border: 2px solid {{{{c.acc}}}}; border-radius: 8px">'
      f'<span style="font-size: 15px; font-weight: 600">Fill in for this project</span>'
      + row(f'<label style="{LB.replace("1 1 200px","2 1 300px")}">Repository with the program<select style="{FS}"><option>[github.com/owner/app]</option><option>Add a repository…</option></select></label>',
            inp('Source folder','src/',flex='1 1 160px',mono=True), inp('Branch','main',flex='1 1 140px',mono=True))
      + f'<fieldset style="min-width: 0; margin: 0; padding: 0; border: 0; display: flex; flex-direction: column; gap: 4px"><legend style="font-size: 14px; font-weight: 600; padding: 0 0 4px">Task description</legend><span style="font-size: 13px; color: {{{{c.mut}}}}">Facts about this task: the bug, how it shows. Optional for this template.</span>'
      + f'<div style="display: flex; flex-wrap: wrap; gap: 8px">{ext("Upload a file")}{ext("Write it here")}{ext("Choose a file the mecha may read")}</div></fieldset></div>')
summary=f'''    <section aria-labelledby="ft" style="background: {{{{c.surf}}}}; border: 1px solid {{{{c.line}}}}; border-radius: 8px; padding: 18px; display: flex; flex-direction: column; gap: 14px">
      <div style="display: flex; flex-wrap: wrap; align-items: baseline; gap: 6px 14px"><h2 id="ft" style="margin: 0; font-size: 17px; flex: 1 1 auto">1 to 3. From the template: Fix a program until its tests pass</h2>{ext("Show all settings")}</div>
      {fill}
      <ul style="list-style: none; margin: 0; padding: 0">{rows}</ul>
      {instr}
      <div style="font-size: 13px; color: {{{{c.mut}}}}; line-height: 1.45">The template's own settings stay as they are. You can add to sections 1 to 3; additions are saved with this project only. "Show all settings" opens the full sections, with the template's entries locked.</div>
    </section>
'''
s=s[:a]+summary+s[b:]
s=s.replace('<title>New project</title>','<title>New project from a template</title>',1)
open(os.path.join(OUT,'PIProjectTemplate.dc.html'),'w').write(s)
d=json.load(open(os.path.join(OUT,'canvas.json')))
d['boards']['PIProjectTemplate.dc.html']={'x':1440,'y':2480,'w':1360,'h':1500,'expand':'fill','title':'Web: new project from a template (sections 1 to 3 folded, 4 from the template)'}
if 'PIProjectTemplate.dc.html' not in d['order']: d['order'].insert(d['order'].index('PIProject.dc.html')+1,'PIProjectTemplate.dc.html')
json.dump(d,open(os.path.join(OUT,'canvas.json'),'w'),indent=2)
