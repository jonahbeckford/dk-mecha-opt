# Derive PIProjectDescribe: the New project form after the LLM drafted it from the PI's description.
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from starting import *
OUT=sys.argv[1]
s=open(os.path.join(OUT,'PIProject.dc.html')).read()
def sub(o,n,c=1):
    global s; assert s.count(o)==c,(o[:70],s.count(o)); s=s.replace(o,n)
MUT='font-size: 13px; color: {{c.mut}}; line-height: 1.45'
# the LLM box shrinks to one line: drafting needs a connected LLM
a=s.index('<section aria-labelledby="llm"'); b=s.index('</section>',a)+len('</section>')
s=s[:a]+'<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px 12px; font-size: 15px"><span>LLM: <b>[Claude Code]</b></span><a href="LLMs.dc.html" style="min-height: 44px; display: inline-flex; align-items: center; font-size: 14px; color: {{c.acc}}">Change</a></div>'+s[b:]
# select Describe it
sub('border: 2px solid {{c.acc}}; border-radius: 8px; background: {{c.surf}}; cursor: pointer"><input type="radio" name="tpl" checked',
    'border: 1px solid {{c.line}}; border-radius: 8px; background: {{c.surf}}; cursor: pointer"><input type="radio" name="tpl"')
k=s.index('Describe it</span>'); lab=s.rindex('<label style="flex: 1 1 220px;',0,k)
seg=s[lab:k].replace('border: 1px solid {{c.line}}','border: 2px solid {{c.acc}}',1).replace('<input type="radio" name="tpl"','<input type="radio" name="tpl" checked',1)
s=s[:lab]+seg+s[k:]
# the description panel, after Start from
desc=('Our churn model in github.com/acme/churn overfits: training AUC is 0.97, holdout AUC is 0.78. Try stronger '
      'regularization and dropping weak features. Keep holdout AUC up, keep training under an hour on one GPU, and stop '
      'any run that costs more than $20. Never use the customer email column; legal forbids it.')
need=lambda t: '<li style="margin: 2px 0">'+t+'</li>'
panel=('\n    <section aria-labelledby="dsc" style="display: flex; flex-direction: column; gap: 10px; padding: 16px; border: 2px solid {{c.acc}}; border-radius: 8px; background: {{c.surf}}">\n'
 '      <h2 id="dsc" style="margin: 0; font-size: 17px">Describe the project</h2>\n'
 '      <div style="font-size: 14px; line-height: 1.5">Say what you want to improve, where it lives, how you will tell a result is better, and what the mecha must never do. Name any questions or changes you already have in mind. The LLM drafts sections 1 to 4 and 6, and suggests who runs the experiments. You choose where the LLM looks. When the description matches a template, the draft starts from that template, says which one, and the LLM drafts only what the template leaves open.</div>\n'
 '      <label for="dtx" style="position: absolute; left: -9999px">Description</label>\n'
 '      <textarea id="dtx" rows="5" style="box-sizing: border-box; width: 100%; padding: 10px 12px; font: inherit; font-size: 15px; line-height: 1.5; border: 1px solid {{c.line}}; border-radius: 6px; background: {{c.bg}}; color: {{c.ink}}; resize: vertical">'+desc+'</textarea>\n'
 '      <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 10px">'+btn('Add files')+'<span style="display: inline-flex; align-items: center; gap: 6px; min-height: 32px; padding: 0 10px; border: 1px solid {{c.line}}; border-radius: 16px; font-size: 14px">churn-metrics.csv <button type="button" aria-label="Remove churn-metrics.csv" style="min-width: 32px; min-height: 32px; border: 0; background: transparent; color: {{c.ink}}">×</button></span>'
 '<span style="flex: 1 1 auto"></span><button type="button" style="min-height: 44px; padding: 0 18px; font-size: 15px; font-weight: 600; border: 0; border-radius: 6px; background: {{c.acc}}; color: {{c.accInk}}">Draft again</button></div>\n'
 '      <div style="'+MUT+'">Drafted [2 minutes ago] from this description and 1 file. No template matched it. Draft again keeps every field you changed. The description and files go to [Claude Code]; they stay in the project folder as the project\'s first note.</div>\n'
 '      <div role="note" style="display: flex; flex-direction: column; gap: 4px; padding: 12px; border-radius: 6px; background: {{c.att}}; font-size: 14px; line-height: 1.5"><b>Before you start the project</b><ul style="margin: 0; padding-left: 20px">'
 + need('Choose the project folder.')
 + need('Review the run and grade rules the LLM wrote, under How an experiment runs. Neither runs until you approve it.')
 + need('Tick the secrets each step may use. A draft leaves every secret unticked.')
 + need('Check the order and ratings under Weigh outcomes. They are your preferences, guessed from your words.')
 + need('Text you paste from someone else, and files you add, can steer the draft. Check What the mecha may change and Out of bounds line by line.')
 + '</ul></div>\n'
 '    </section>\n')
k=s.index('</fieldset>',s.index('A template fills sections 1 to 4.'))+len('</fieldset>\n')
s=s[:k]+panel+s[k:]
sub('<input id="t" type="text" placeholder="[Project title]"','<input id="t" type="text" value="Churn model overfitting"')
# sections 1 to 3 fold into a drafted summary
a=s.rindex('    <fieldset',0,s.index('1. Scope</legend>'))
b=s.rindex('    <fieldset',0,s.index('4. Problems and hypotheses to start with</legend>'))
def r(title, body, need_=False, act=''):
    return ('<li style="display: flex; flex-wrap: wrap; align-items: flex-start; gap: 6px 14px; padding: 12px 0; border-top: 1px solid {{c.line}}">'
      '<span style="flex: 0 0 220px; display: flex; flex-direction: column; align-items: flex-start; gap: 4px"><span style="font-size: 15px; font-weight: 600">'+title+'</span>'+badge('Needs you' if need_ else 'Drafted',need_)+'</span>'
      '<span style="flex: 1 1 320px; min-width: 0; font-size: 14px; line-height: 1.5">'+body+'</span>'+(btn(act) if act else '')+'</li>')
C=lambda t: '<code>'+t+'</code>'
rows=''.join([
 r('Task description','Holdout AUC has fallen to 0.78 while training AUC is 0.97. Improve holdout AUC by reducing overfitting. Saved as '+C('task.md')+'.'),
 r('What the mecha may change and read','Changes '+C('train.py')+' and '+C('features/')+' in '+C('github.com/acme/churn')+'. Reads '+C('data/train.parquet')+'. Grader only: '+C('data/holdout.parquet')+'.'),
 r('How an experiment runs','The LLM wrote a run rule and a grade rule in the project folder. Run: trains on the training data and saves the model. Grade: scores holdout AUC and reports training minutes. Neither runs until you approve it.',True,'Review rules'),
 r('Hardware','Linux, macOS or Windows. 1 GPU with at least 16 GB of memory.'),
 r('Protocol of record','None found in the description. Add a file such as a data contract if the project has one.'),
 r('Secrets each step may use','All unticked.',True,'Tick secrets'),
 r('Out of bounds','No internet for running and grading the experiment: ticked. Stop any run that costs more than $20.'),
 r('Standing instructions','Edit only '+C('train.py')+' and '+C('features/')+'. Never read or derive a feature from the customer email column.'),
 r('What counts as a better result','Holdout AUC, higher is better, typical range 0.70 to 0.90. Training time, lower is better, typical range 60 to 10 minutes, never adopt if worse than 60. Weights 0.77 and 0.23: holdout AUC first, training time rated 30.',True,'Check the weights'),
 r('Revelations','The model never uses the customer email column. Legal forbids it.'),
]).replace('border-top: 1px solid {{c.line}}','',1)
summary=('    <section aria-labelledby="fd" style="background: {{c.surf}}; border: 1px solid {{c.line}}; border-radius: 8px; padding: 18px; display: flex; flex-direction: column; gap: 10px">\n'
 '      <div style="display: flex; flex-wrap: wrap; align-items: baseline; gap: 6px 14px"><h2 id="fd" style="margin: 0; font-size: 17px; flex: 1 1 auto">1 to 3. Drafted from your description</h2>'+btn('Show all settings')+'</div>\n'
 '      <ul style="list-style: none; margin: 0; padding: 0">'+rows+'</ul>\n'
 '      <div style="'+MUT+'">"Show all settings" opens the full sections 1 to 3, every drafted field marked. Change anything; it is yours once you change it.</div>\n'
 '    </section>\n')
s=s[:a]+summary+s[b:]
# section 4 drafted from the description
a=s.rindex('    <fieldset',0,s.index('4. Problems and hypotheses to start with</legend>')); b=s.index('</fieldset>',a)+len('</fieldset>\n')
D='From your description'
s=s[:a]+section([(1,'Problem','Why does the churn model overfit, with training AUC at 0.97 and holdout AUC at 0.78?',D),
                 (2,'Hypothesis','Stronger L2 regularization raises holdout AUC.',D),
                 (3,'Hypothesis','Dropping the weakest features raises holdout AUC and shortens training.',D)],
                'Saved with the template when you save sections 1 to 4. A project started from that template begins with them.')+s[b:]
# section 5: a suggestion, not a draft
k=s.index('<div style="font-size: 14px; color: {{c.mut}}">This device lists only what it is allowed to run.</div>')
s=s[:k]+'<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px 10px; font-size: 14px">'+badge('Suggested')+'<span>This computer. Your description asks for one GPU, and this computer has one.</span></div>\n      '+s[k:]
g=s.index('aria-label="Who runs the experiments"'); e=s.index('</div>',g)
grp=s[g:e]
grp=grp.replace('border: 2px solid {{c.acc}}','border: 1px solid {{c.line}}',1).replace('<input type="radio" name="w" checked','<input type="radio" name="w"',1)
t=grp.index('<span>This computer</span>'); l=grp.rindex('<label',0,t)
grp=grp[:l]+grp[l:t].replace('border: 1px solid {{c.line}}','border: 2px solid {{c.acc}}',1).replace('<input type="radio" name="w"','<input type="radio" name="w" checked',1)+grp[t:]
s=s[:g]+grp+s[e:]
# section 6: drafted roles
sub('<option selected>People on the project</option><option>An LLM: [connection / model]</option><option>Both</option>',
    '<option>People on the project</option><option>An LLM: [connection / model]</option><option selected>Both</option>')
sub('<option selected>You</option><option>An LLM or coding agent: [connection / model]</option>',
    '<option>You</option><option selected>An LLM or coding agent: [connection / model]</option>')
k=s.index('6. Who helps the mecha</legend>')+len('6. Who helps the mecha</legend>')
s=s[:k]+'\n      <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px 10px; font-size: 14px">'+badge('Drafted')+'<span>From your description. Where the LLM looks is yours to choose.</span></div>'+s[k:]
s=s.replace('<title>New project</title>','<title>New project from a description</title>',1)
open(os.path.join(OUT,'PIProjectDescribe.dc.html'),'w').write(s)
d=json.load(open(os.path.join(OUT,'canvas.json')))
d['boards']['PIProjectDescribe.dc.html']={'x':2880,'y':2820,'w':1360,'h':1500,'expand':'fill','title':'Web: new project drafted from a description'}
if 'PIProjectDescribe.dc.html' not in d['order']: d['order'].insert(d['order'].index('PIProjectTemplate.dc.html')+1,'PIProjectDescribe.dc.html')
json.dump(d,open(os.path.join(OUT,'canvas.json'),'w'),indent=2)
