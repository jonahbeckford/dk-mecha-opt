import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
from common import *
f=sys.argv[1]; s=open(f).read()
MONO="font-family: 'Ubuntu Mono', monospace"
k=s.index('Out of bounds</h3>'); a=s.rindex('      <div style="display: flex; flex-direction: column; gap: 8px; padding-top: 12px;',0,k); b=s.index('    </fieldset>',k)
def rule(title, control, how):
    return (f'<div style="display: flex; flex-direction: column; gap: 6px; padding: 10px 12px; border: 1px solid {{{{c.line}}}}; border-radius: 6px">'
            f'<div style="font-size: 15px; font-weight: 600">{title}</div>{control}'
            f'<div style="font-size: 13px; line-height: 1.45"><strong>How it is kept:</strong> {how}</div></div>')
chip=lambda t: f'<span style="display: inline-flex; align-items: center; gap: 6px; min-height: 36px; padding: 0 6px 0 10px; border: 1px solid {{{{c.line}}}}; border-radius: 18px; font-size: 14px; {MONO}">{t}<button type="button" aria-label="Remove {t}" style="min-width: 32px; min-height: 32px; border: 0; background: transparent; color: {{{{c.ink}}}}; font-size: 16px">×</button></span>'
secrets=rule('Secrets the experiment never gets',
  f'<div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: center">{chip("[RELEASE_SIGNING_KEY]")}{chip("[PYPI_TOKEN]")}<select aria-label="Add a secret" style="{FS}"><option>Add a secret from Experiment environment…</option></select></div>',
  'the desktop writes every <code>dk0 run-function</code> request itself and leaves these out of all three steps. Experiment environment cannot tick them for any executor. Other secrets reach only the executors ticked there.')
meas=rule('How results are measured (always)',
  '<div style="font-size: 13px; color: {{c.mut}}">The set up, run and grade function rules, and every file outside the "may change" limits, such as the tests.</div>',
  'the three rules are pinned by module and version in the project, and the desktop refuses a run whose rule differs. Before each run it compares the change with the "may change" limits above and rejects a change that touches any other file. Changing these is a <a href="MeasurementChanges.dc.html" style="color: {{c.acc}}">measurement change</a>.')
net=rule('No internet for the experiment and the grader',
  '<label style="display: flex; align-items: center; gap: 8px; min-height: 44px; font-size: 14px"><input type="checkbox" checked style="width: 20px; height: 20px; margin: 0"> Run them with networking switched off</label>',
  'the desktop starts the run and grade steps with networking off: in the MXC sandbox on this computer, and with the executor\'s own switch elsewhere. While this is ticked, an executor that cannot switch networking off is never used. Only Set up can reach the internet.')
hidden=rule('Hidden answers stay with the grader',
  '<div style="font-size: 13px; color: {{c.mut}}">Applies to items marked "Grader only" in the list above.</div>',
  'grader-only items go only into the grader\'s request, as <code>data[hidden][name]</code>, in its own run and folder. The experiment\'s request never names them. Before every run the desktop checks, by path and by checksum, that no grader-only file sits inside anything the experiment gets, and stops the cycle if one does. The grader returns one result per case and nothing else.')
other=rule('Anything else',
  f'<label style="display: flex; flex-direction: column; gap: 4px; font-size: 14px"><span style="color: {{{{c.mut}}}}">Hazards, ethics and approval limits, budget ceilings, in your own words.</span><textarea rows="3" style="box-sizing: border-box; width: 100%; padding: 8px 10px; font-size: 15px; border: 1px solid {{{{c.line}}}}; border-radius: 6px; background: {{{{c.bg}}}}; color: {{{{c.ink}}}}"></textarea></label>',
  'by people. A program cannot check this text. An experiment sent to a person shows it as "Stop if" and "Never", and you approve every such experiment at AUTHORIZE. The LLM also reads it with the standing instructions.')
new=f'''      <div style="display: flex; flex-direction: column; gap: 8px; padding-top: 12px; border-top: 1px solid {{{{c.line}}}}">
        <h3 style="font-size: 15px; font-weight: 700; margin: 0">Out of bounds</h3>
        <div style="font-size: 14px; color: {{{{c.mut}}}}; line-height: 1.45">What no experiment, person or program may touch. Each rule says how it is kept.</div>
        {secrets}{meas}{net}{hidden}{other}
      </div>
'''
s=s[:a]+new+s[b:]
# add a grader-only item row in the items table, after the dataset row
m=re.search(r'(<tr style="border-top: 1px solid \{\{c.line\}\}"><td[^>]*><code>\[s3://bucket/train/\]</code>.*?</tr>)',s)
assert m
row0=m.group(1)
hid=(row0.replace('[s3://bucket/train/]','[hidden/test_labels.csv]')
     .replace('Dataset, object storage, version [v7], sha256 [9f2e…]','Data in the project folder, kept away from the experiment')
     .replace('<option selected>May read</option><option>May change</option>','<option selected>Grader only</option><option>May read</option><option>May change</option>')
     .replace('[12 GB]','Never in the experiment\'s request')
     .replace('value="train"','value="test_labels"'))
assert hid!=row0
s=s.replace(row0,row0+hid,1)
open(f,'w').write(s)
