# AUTHORIZE parks a run for what it does: a paid executor, a secret marked Approve each use, a person.
import sys, os
P=sys.argv[1]
def edit(fn, pairs):
    f=os.path.join(P,fn); s=open(f).read()
    for o,n in pairs:
        assert s.count(o)==1,(fn,o[:70],s.count(o)); s=s.replace(o,n)
    open(f,'w').write(s)
CHK=lambda label,on=False,locked=False: ('<label style="display: inline-flex; align-items: center; gap: 8px; min-height: 44px; font-size: 13px"><input type="checkbox"'+(' checked' if on else '')+(' disabled' if locked else '')+' style="width: 20px; height: 20px; margin: 0"> '+label+'</label>')
edit('Environment.dc.html',[
 ('<span style="font-size: 13px">This computer, GitHub, SaaS</span></li>',
  '<span style="font-size: 13px">This computer, GitHub, SaaS</span>'+CHK('Approve each use')+'</li>'),
 ('<span style="font-size: 13px">[This computer, GitHub]</span><button',
  '<span style="font-size: 13px">[This computer, GitHub]</span>'+CHK('Approve each use',True)+'<button'),
 ('"Secrets each step may use", under Scope, says which steps receive each one.</div>',
  '"Secrets each step may use", under Scope, says which steps receive each one. Tick Approve each use for a secret that can publish, release or pay for something: every run whose steps receive it waits for you at AUTHORIZE.</div>'),
 ('  </main>',
  '    <section aria-labelledby="ap" style="background: {{c.surf}}; border: 1px solid {{c.line}}; border-radius: 8px; padding: 14px 20px; display: flex; flex-direction: column; gap: 8px">\n'
  '      <h2 id="ap" style="margin: 0; font-size: 18px">Runs that wait for your approval</h2>\n'
  '      <ul style="margin: 0; padding-left: 20px; font-size: 14px; line-height: 1.6">'
  '<li>A run on a paid executor: Diskuv SaaS, or a cloud virtual machine. The mecha works out the most it can cost, from the executor\'s hourly price and the step\'s time limit, and shows you the calculation.</li>'
  '<li>A run whose steps receive a secret marked Approve each use.</li>'
  '<li>An experiment for a person.</li></ul>\n'
  '      <div style="font-size: 13px; color: {{c.mut}}; line-height: 1.45">These wait at <a href="StageAuthorize.dc.html" style="color: {{c.acc}}">AUTHORIZE</a>. Each approval releases one run of one hypothesis. In an unattended window they stay parked, and the mecha keeps proposing hypotheses like them.</div>\n'
  '    </section>\n  </main>')])
edit('PIProject.dc.html',[("When that run costs money or a person\\'s time, it waits for your approval at AUTHORIZE.".replace("\\'","'"),
  "When that run does something you approve each time, such as running on a paid executor, it waits for you at AUTHORIZE.")])
