import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from common import *
OUT=sys.argv[1]
H=1300
def tree_item(t, depth=0, cur=False, kind='', changed=False):
    mark=f'<span style="font-size: 12px; font-weight: 700; color: {{{{c.warn}}}}">changed</span>' if changed else ''
    sty='background: {{c.sel}}; font-weight: 600' if cur else ''
    return f'<li><a href="#f" {"aria-current=\"page\" " if cur else ""}style="display: flex; align-items: center; gap: 8px; min-height: 40px; padding: 0 10px 0 {10+depth*16}px; border-radius: 6px; font-size: 14px; text-decoration: none; {sty}"><span style="flex: 1 1 auto; font-family: \'Ubuntu Mono\', monospace">{t}</span>{kind}{mark}</a></li>'
def grp(title, items): return f'<li style="padding: 10px 10px 2px; font-size: 12px; font-weight: 700; color: {{{{c.mut}}}}; letter-spacing: 0.02em">{title}</li>' + ''.join(items)
files='<ul role="tree" aria-label="Files and parameters" style="list-style: none; margin: 0; padding: 0">' + grp('MAY CHANGE',[
  tree_item('[github.com/owner/app]'), tree_item('src/',1), tree_item('Parser.java',2,cur=True,changed=True), tree_item('Lexer.java',2), tree_item('build.gradle',1)]) + grp('MAY READ',[
  tree_item('[github.com/owner/spec] @ v1.2'), tree_item('description.md'), tree_item('data/train.csv'), tree_item('figures/yield.png')]) + grp('PARAMETERS',[
  tree_item('[Incubation temperature]',changed=True)]) + '</ul>'
code_lines=[(' ','41','  Token next() {'),(' ','42','    skipWhitespace();'),('-','43','    if (pos > input.length()) return Token.EOF;'),('+','43','    if (pos >= input.length()) return Token.EOF;'),(' ','44','    char ch = input.charAt(pos);'),(' ','45','    ...')]
def cl(sign,n,t):
    bg={'+':'background: {{c.done}}','-':'background: {{c.att}}',' ':''}[sign]
    col={'+':'color: {{c.ok}}','-':'color: {{c.bad}}',' ':'color: {{c.mut}}'}[sign]
    lab={'+':'added','-':'removed',' ':''}[sign]
    return f'<div style="display: flex; {bg}"><span style="width: 44px; flex: none; text-align: right; padding-right: 8px; color: {{{{c.mut}}}}">{n}</span><span aria-label="{lab}" style="width: 18px; flex: none; {col}; font-weight: 700">{sign.strip()}</span><span style="white-space: pre">{t}</span></div>'
code='<div role="region" aria-label="Changes in Parser.java" style="overflow-x: auto; border: 1px solid {{c.line}}; border-radius: 6px; padding: 8px 0; font-family: \'Ubuntu Mono\', monospace; font-size: 14px; line-height: 1.6; background: {{c.surf}}">'+''.join(cl(*x) for x in code_lines)+'</div>'
img=f'''<div style="display: flex; flex-wrap: wrap; gap: 12px">
            <figure style="flex: 1 1 240px; margin: 0; display: flex; flex-direction: column; gap: 6px"><div role="img" aria-label="[figures/yield.png at S2]" style="height: 150px; border: 1px solid {{{{c.line}}}}; border-radius: 6px; background: {{{{c.track}}}}"></div><figcaption style="font-size: 13px; color: {{{{c.mut}}}}">S2, before</figcaption></figure>
            <figure style="flex: 1 1 240px; margin: 0; display: flex; flex-direction: column; gap: 6px"><div role="img" aria-label="[figures/yield.png at S3]" style="height: 150px; border: 1px solid {{{{c.line}}}}; border-radius: 6px; background: {{{{c.track}}}}"></div><figcaption style="font-size: 13px; color: {{{{c.mut}}}}">S3, this version</figcaption></figure>
          </div>'''
params=table(['Parameter','At S2','At S3','Allowed'],[['[Incubation temperature]','[35] °C','<strong>[37] °C</strong>','[30] to [40] °C']],480)
cases=ul([tag('Passed','ok')+'<span style="flex: 1 1 200px"><code>[ParserTest.testEof]</code></span>'+a('Log','#log'),
          tag('Failed','bad')+'<span style="flex: 1 1 200px"><code>relevant-suite-regressions</code></span><span style="color: {{c.mut}}">[LexerTest.testEmpty] regressed</span>'])
versions=sel('Version',['S3: from [Hypothesis: fix the end-of-input check], fix attempt, [time]','S2: from [Hypothesis], fix attempt','S1: from [Hypothesis], fix attempt','S0: the starting version'],'2 1 360px')
cmp=sel('Compare with',['S2, the version it started from','S0, the starting version','Nothing: show whole files'],'1 1 240px')
html=HEAD.format(title='Browse a version')+f'''<div style="min-height: {H}px; box-sizing: border-box; display: flex; flex-direction: column; background: {{{{c.bg}}}}; color: {{{{c.ink}}}}">
  <header style="display: flex; flex-wrap: wrap; align-items: center; gap: 8px 12px; padding: 6px 24px; min-height: 56px; background: {{{{c.surf}}}}; border-bottom: 1px solid {{{{c.line}}}}">
    <a href="Projects.dc.html" style="font-size: 18px; font-weight: 700; text-decoration: none; min-height: 44px; display: inline-flex; align-items: center">Mecha DK</a>
    <div style="font-size: 15px; color: {{{{c.mut}}}}; flex: 1 1 auto">/ [Project name] / <a href="Tree.dc.html">Hypothesis tree</a> / [Hypothesis] / Version S3</div>
  </header>
  <div style="padding: 14px 24px; background: {{{{c.surf}}}}; border-bottom: 1px solid {{{{c.line}}}}; display: flex; flex-direction: column; gap: 8px">
    {row(versions, cmp, btn('Copy commit <code>[abc1234]</code>'), btn('Open a copy on this computer'))}
    <div style="font-size: 13px; color: {{{{c.mut}}}}; line-height: 1.45">Every fix attempt makes a new version of what the mecha works on. This hypothesis made S3; its results were measured at S2 and S3. Read-only, like a commit: nothing here changes the project.</div>
  </div>
  <div style="display: flex; flex-wrap: wrap; flex: 1 1 auto; align-items: stretch">
    <nav aria-label="Files" style="flex: 1 1 260px; max-width: 320px; box-sizing: border-box; padding: 12px 10px; border-right: 1px solid {{{{c.line}}}}; background: {{{{c.surf}}}}">{files}
      <div style="padding: 10px; font-size: 12px; color: {{{{c.mut}}}}; line-height: 1.4">The same lists as Scope: what the mecha may change, what it may only read, and its parameters.</div>
    </nav>
    <main style="flex: 999 1 560px; min-width: 0; box-sizing: border-box; padding: 20px 24px; display: flex; flex-direction: column; gap: 16px">
      <section aria-labelledby="fv" style="display: flex; flex-direction: column; gap: 8px">
        <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 10px"><h1 id="fv" style="margin: 0; font-size: 20px; flex: 1 1 auto; font-family: 'Ubuntu Mono', monospace">src/Parser.java</h1>{btn('Changes')}{btn('Whole file')}</div>
        {code}
      </section>
      <section aria-labelledby="iv" style="display: flex; flex-direction: column; gap: 8px">
        <h2 id="iv" style="margin: 0; font-size: 16px">An image: <code>figures/yield.png</code></h2>
        {img}
        <div style="font-size: 13px; color: {{{{c.mut}}}}">Images, PDFs and data files open in a preview; a table shows its first rows and columns.</div>
      </section>
      <section aria-labelledby="pv" style="display: flex; flex-direction: column; gap: 8px">
        <h2 id="pv" style="margin: 0; font-size: 16px">Parameters at this version</h2>
        {params}
      </section>
      <section aria-labelledby="cv" style="display: flex; flex-direction: column; gap: 8px">
        <h2 id="cv" style="margin: 0; font-size: 16px">Cases measured at S3</h2>
        {cases}
      </section>
    </main>
  </div>
</div>
'''+(TAIL % H)
html=html.replace('a{color:inherit}','a{color:inherit}\nlabel{min-width:0}\nselect{max-width:100%;min-width:0}',1)
open(os.path.join(OUT,'SuoBrowser.dc.html'),'w').write(html)
d=json.load(open(os.path.join(OUT,'canvas.json')))
d['boards']['SuoBrowser.dc.html']={'x':4320,'y':1640,'w':1360,'h':1300,'expand':'fill','title':'Web: browse a version of what the mecha works on'}
if 'SuoBrowser.dc.html' not in d['order']: d['order'].insert(d['order'].index('Tree.dc.html')+1,'SuoBrowser.dc.html')
json.dump(d,open(os.path.join(OUT,'canvas.json'),'w'),indent=2)
