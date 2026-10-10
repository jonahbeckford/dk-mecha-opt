# One list of what the mecha may change and read: settings page mirrors New project; Environment keeps secrets and executors.
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from starting import btn
P=sys.argv[1]
def rd(f): return open(os.path.join(P,f)).read()
def wr(f,s): open(os.path.join(P,f),'w').write(s)
def sub(s,o,n):
    assert s.count(o)==1,(o[:70],s.count(o)); return s.replace(o,n)
pi=rd('PIProject.dc.html')
pi=sub(pi,'Repositories here are the same list as','In a running project, this list is')
# find the old link and following sentence
i=pi.index('In a running project, this list is'); j=pi.index('Whatever the mecha may read is also shown to an LLM.',i)
pi=pi[:i]+'In a running project, this list is in <a href="SettingsSurface.dc.html" style="color: {{c.acc}}">project settings</a>, and a change to it waits for the next break between cycles. A repository the mecha may change follows its branch; one it may only read is pinned. '+pi[j:]
wr('PIProject.dc.html',pi)
i=pi.index('What the mecha may change and read</h3>'); a=pi.rindex('      <div style="display: flex; flex-direction: column; gap: 8px; padding-top: 12px; border-top',0,i)
b=pi.rindex('      <div style="display: flex; flex-direction: column; gap: 8px; padding-top: 12px; border-top',0,pi.index('What you measure</h3>'))
block=pi[a:b].replace('padding-top: 12px; border-top: 1px solid {{c.line}}','padding: 20px; background: {{c.surf}}; border: 1px solid {{c.line}}; border-radius: 8px',1)
block=block.replace('<h3 style="font-size: 15px; font-weight: 700; margin: 0">What the mecha may change and read</h3>','<h2 style="margin: 0; font-size: 18px">Items</h2>',1)
block=block.replace('In a running project, this list is in <a href="SettingsSurface.dc.html" style="color: {{c.acc}}">project settings</a>, and a change to it waits for the next break between cycles. ','')
# settings page
ps=rd('ProjectSettings.dc.html')
ps=sub(ps,'<a href="#m" style="min-height: 44px; display: flex; align-items: center; padding: 0 12px; border-radius: 6px; font-size: 15px; text-decoration: none">What the mecha may vary</a>',
          '<a href="SettingsSurface.dc.html" style="min-height: 44px; display: flex; align-items: center; padding: 0 12px; border-radius: 6px; font-size: 15px; text-decoration: none">What the mecha may change and read</a>')
wr('ProjectSettings.dc.html',ps)
ss=ps.replace('<title>Project settings</title>','<title>What the mecha may change and read</title>',1)
ss=sub(ss,'<a href="#m" aria-current="page" style="min-height: 44px; display: flex; align-items: center; padding: 0 12px; border-radius: 6px; background: {{c.sel}}; font-size: 15px; font-weight: 600; text-decoration: none">What you measure</a>',
          '<a href="ProjectSettings.dc.html" style="min-height: 44px; display: flex; align-items: center; padding: 0 12px; border-radius: 6px; font-size: 15px; text-decoration: none">What you measure</a>')
ss=sub(ss,'<a href="SettingsSurface.dc.html" style="min-height: 44px; display: flex; align-items: center; padding: 0 12px; border-radius: 6px; font-size: 15px; text-decoration: none">What the mecha may change and read</a>',
          '<a href="SettingsSurface.dc.html" aria-current="page" style="min-height: 44px; display: flex; align-items: center; padding: 0 12px; border-radius: 6px; background: {{c.sel}}; font-size: 15px; font-weight: 600; text-decoration: none">What the mecha may change and read</a>')
a=ss.index('      <h1 style="margin: 0; font-size: 26px">What you measure</h1>'); b=ss.index('      <div style="display: flex; flex-direction: column; gap: 6px">\n        <label for="why"')
head=('      <h1 style="margin: 0; font-size: 26px">What the mecha may change and read</h1>\n'
 '      <div style="font-size: 15px; color: {{c.mut}}; line-height: 1.5">The same list as in New project: repositories, files, models, data, outputs and parameters, with what the mecha may do with each, its limits and the name it is passed as.</div>\n'
 '      <div style="border: 2px solid {{c.warn}}; background: {{c.att}}; border-radius: 6px; padding: 12px 14px; font-size: 15px; line-height: 1.5; display: flex; flex-direction: column; gap: 8px">\n'
 '        <div>Changes here become a request on <a href="MeasurementChanges.dc.html" style="color: {{c.acc}}">Measurement changes</a>, applied in the next break between cycles.</div>\n'
 '        <div><strong>What this draft will do</strong> (it moves the pin of <code>[github.com/owner/spec]</code> to [v1.3]):</div>\n'
 '        <ul style="margin: 0; padding-left: 20px"><li>The mecha will measure the current best version again with the new pin, run by [executor]. Estimated cost: [cost].</li><li>Results from before the change stay on record, marked as measured the old way.</li></ul>\n'
 '        <div style="font-size: 13px">[Variant for a new item the mecha may only read, or a new parameter: Nothing is measured again until a hypothesis uses it.] [Variant for narrower limits: Hypotheses that changed files now outside the limits are dropped at the next DROP.]</div>\n'
 '      </div>\n\n'+block)
ss=ss[:a]+head+ss[b:]
a=ss.index('      <section id="n" aria-labelledby="nw"'); b=ss.index('    </main>')
ss=ss[:a]+ss[b:]
ss=ss.replace('"$preview":{"width":1360,"height":1400}','"$preview":{"width":1360,"height":1500}')
wr('SettingsSurface.dc.html',ss)
# Environment: secrets and executors only
en=rd('Environment.dc.html')
a=en.index('    <section aria-labelledby="rp"'); b=en.index('    <section aria-labelledby="sc"')
en=en[:a]+('    <div style="font-size: 15px; line-height: 1.5; padding: 12px 16px; border: 1px solid {{c.line}}; border-radius: 8px; background: {{c.surf}}">Repositories, files, models, data and parameters are in <a href="SettingsSurface.dc.html" style="color: {{c.acc}}">What the mecha may change and read</a>. Each experiment receives them as <code>dk0 run-function</code> arguments.</div>\n\n')+en[b:]
en=sub(en,'What every experiment starts with, wherever it runs: this computer, GitHub Actions or Diskuv SaaS. A person running an experiment does not get these.',
          'The secrets every executor can hold, wherever experiments run: this computer, GitHub Actions or Diskuv SaaS. A person running an experiment never gets them.')
en=sub(en,'Out of bounds in each project says which steps may use each secret.','"Secrets each step may use", under Scope, says which steps receive each one.')
a=en.index('    <section aria-labelledby="ev"'); b=en.index('  </main>')
en=en[:a]+en[b:]
en=en.replace('<title>Executor environment</title>','<title>Experiment environment</title>',1)
wr('Environment.dc.html',en)
# GitHub executor: the repository that runs the experiments
gh=rd('GitHubRemote.dc.html')
gh=sub(gh,'<h2 id="s2" style="margin: 0; font-size: 18px">3. Choose where experiments run</h2>',
          '<h2 id="s2" style="margin: 0; font-size: 18px">3. Repository that runs the experiments</h2>\n      <div style="font-size: 14px; line-height: 1.5">Its GitHub Actions runners run each experiment, and the secrets you allow are copied to it as Actions secrets. The mecha never changes it, and experiments never receive it. Choose a repository of its own for this.</div>')
gh=sub(gh,'in the repository you choose.','in the repository that runs the experiments.')
wr('GitHubRemote.dc.html',gh)
d=json.load(open(os.path.join(P,'canvas.json')))
d['boards']['SettingsSurface.dc.html']={'x':7670,'y':9520,'w':1360,'h':1500,'expand':'fill','title':'Web: settings, what the mecha may change and read'}
d['boards']['Environment.dc.html']['title']='Web: experiment environment (secrets)'
if 'SettingsSurface.dc.html' not in d['order']: d['order'].insert(d['order'].index('Environment.dc.html')+1,'SettingsSurface.dc.html')
d['notes']['t6']['maxW']=9030
json.dump(d,open(os.path.join(P,'canvas.json'),'w'),indent=2)
