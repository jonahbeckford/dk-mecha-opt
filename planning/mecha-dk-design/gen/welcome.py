import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from common import *
OUT=sys.argv[1]
def opt(name, desc, action, primary=False, badge=''):
    b=f'<span style="font-size: 12px; font-weight: 600; color: {{{{c.ok}}}}">{badge}</span>' if badge else ''
    return f'<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px 14px; padding: 10px 12px; border: 1px solid {{{{c.line}}}}; border-radius: 8px"><span style="flex: 1 1 260px; display: flex; flex-direction: column; gap: 2px"><span style="font-size: 16px; font-weight: 600">{name} {b}</span><span style="font-size: 13px; color: {{{{c.mut}}}}; line-height: 1.4">{desc}</span></span>{btn(action, primary)}</div>'
def grp(title, items): return f'<div style="display: flex; flex-direction: column; gap: 8px"><h3 style="margin: 4px 0 0; font-size: 15px">{title}</h3>' + ''.join(items) + '</div>'
steps=['Welcome','Connect an LLM','This computer','Your first project']
rail='<ol aria-label="Steps" style="margin: 0; padding: 0; list-style: none; display: flex; flex-wrap: wrap; gap: 6px">'+''.join(
 f'<li{" aria-current=\"step\"" if i==1 else ""} style="flex: 1 1 120px; padding: 8px 10px; border-radius: 6px; font-size: 13px; font-weight: 600; {"background: {{c.done}}" if i==0 else ("outline: 2px solid {{c.acc}}; background: {{c.sel}}" if i==1 else "border: 1px solid {{c.line}}")}"><span style="display: block; font-weight: 400; color: {{{{c.mut}}}}">Step {i+1} of 4</span>{t}</li>' for i,t in enumerate(steps))+'</ol>'
body=grp('Use a coding agent you already have',[
  opt('Claude Code','Uses your Claude Pro or Max subscription. Opens your browser to sign in to Claude; the token stays in this computer\'s key store.','Sign in with Claude'),
  opt('Codex CLI','Signs in with its own login, or an API key.','Set up'),
  opt('Gemini CLI','Signs in with its own login, or an API key.','Set up'),
  opt('Grok Build','Signs in with its own login, or an API key.','Set up')])+grp('Or connect a model',[f'<div style="font-size: 13px; color: {{{{c.mut}}}}; line-height: 1.45">Writing and running experiments needs a coding agent. When you connect a model, Mecha DK downloads goose, an open-source coding agent, and sets it up to use that model. Nothing else to install.</div>',
  opt('Through Diskuv SaaS','No key to manage; uses your Diskuv credits. Works in a browser and on a phone too. Includes Diskuv\'s build of goose, which you can also use on its own.','Sign in'),
  opt('Anthropic (Claude)','With your Anthropic API key.','Add key'),
  opt('OpenAI (ChatGPT)','With your OpenAI API key.','Add key'),
  opt('Your own server or an OpenAI-compatible service','Ollama, llama.cpp, LM Studio, vLLM and hosted services that speak the same API.','Add server')])
H=1450
html=HEAD.format(title='Welcome to Mecha DK')+f'''<div style="min-height: {H}px; box-sizing: border-box; display: flex; flex-direction: column; align-items: center; padding: 32px 16px; background: {{{{c.bg}}}}; color: {{{{c.ink}}}}">
  <div role="dialog" aria-labelledby="wt" style="width: 100%; max-width: 760px; box-sizing: border-box; background: {{{{c.surf}}}}; border: 1px solid {{{{c.line}}}}; border-radius: 12px; padding: 24px; display: flex; flex-direction: column; gap: 16px">
    {rail}
    <div style="display: flex; flex-direction: column; gap: 6px">
      <h1 id="wt" style="margin: 0; font-size: 26px">Connect an LLM</h1>
      <div style="font-size: 15px; color: {{{{c.mut}}}}; line-height: 1.5">An LLM, also called a coding agent or a model, proposes hypotheses, writes experiments and judges results, while you decide what goes ahead. Most projects use one.</div>
    </div>
    {body}
    <div style="font-size: 13px; line-height: 1.45; padding: 10px 12px; border-radius: 6px; border: 2px solid {{{{c.bad}}}}">An LLM acts with your access. Text it reads, from collaborators, papers or web pages, can steer it (a prompt injection). <a href="Collaborators.dc.html" style="color: {{{{c.acc}}}}">More</a></div>
    <div style="display: flex; flex-wrap: wrap; gap: 10px; align-items: center; justify-content: space-between; padding-top: 6px; border-top: 1px solid {{{{c.line}}}}">
      {btn('Back')}
      <span style="display: inline-flex; flex-wrap: wrap; gap: 10px">{btn('Skip: people only for now')}{btn('Continue', True)}</span>
    </div>
  </div>
  <section aria-labelledby="os" style="width: 100%; max-width: 760px; box-sizing: border-box; margin-top: 24px; display: flex; flex-direction: column; gap: 10px; font-size: 14px; line-height: 1.5">
    <h2 id="os" style="margin: 0; font-size: 16px">The other steps</h2>
    <div><strong>1. Welcome.</strong> What Mecha DK does, the two public demos to open first, and signing in to Diskuv SaaS or continuing without an account (drawn on its own board).</div>
    <div><strong>3. This computer.</strong> Where projects are kept by default (<code>[~/Mecha DK]</code>), and whether this computer keeps running projects in the background so a phone or browser can reach them.</div>
    <div><strong>4. Your first project.</strong> New project (from a template or blank), Open project folder, or open one of the two demos read-only.</div>
    <div style="color: {{{{c.mut}}}}">The wizard opens on first launch and can be reopened from Settings. Any step can be skipped. On the web and on phones, the agents are not offered here (they run on a desktop or an executor), so step 2 starts with Diskuv SaaS. Choosing a model on a desktop also downloads and sets up goose with it. Each choice opens the same setup as <a href="LLMs.dc.html" style="color: {{{{c.acc}}}}">Settings, LLMs</a> and returns here.</div>
  </section>
</div>
'''+(TAIL % H)
open(os.path.join(OUT,'Welcome.dc.html'),'w').write(html)
d=json.load(open(os.path.join(OUT,'canvas.json')))
d['boards']['Welcome.dc.html']={'x':4400,'y':300,'w':1200,'h':1450,'expand':'fill','title':'First launch: welcome wizard, step 2 (connect an LLM)'}
if 'Welcome.dc.html' not in d['order']: d['order'].insert(2,'Welcome.dc.html')
json.dump(d,open(os.path.join(OUT,'canvas.json'),'w'),indent=2)

# ---- Step 1 board, with the two public demos
def demo(title, desc, meta):
    return f'<div style="flex: 1 1 300px; display: flex; flex-direction: column; gap: 8px; padding: 14px; border: 1px solid {{{{c.line}}}}; border-radius: 8px; background: {{{{c.bg}}}}"><span style="font-size: 12px; font-weight: 600; color: {{{{c.mut}}}}">PUBLIC DEMO, READ-ONLY</span><span style="font-size: 17px; font-weight: 700">{title}</span><span style="font-size: 14px; line-height: 1.45">{desc}</span><span style="font-size: 13px; color: {{{{c.mut}}}}">{meta}</span><span>{btn("Open the demo")}</span></div>'
rail1=rail.replace('aria-current="step" ','').replace('outline: 2px solid {{c.acc}}; background: {{c.sel}}','border: 1px solid {{c.line}}').replace('background: {{c.done}}','outline: 2px solid {{c.acc}}; background: {{c.sel}}',1)
H1=720
html1=HEAD.format(title='Welcome to Mecha DK')+f'''<div style="min-height: {H1}px; box-sizing: border-box; display: flex; flex-direction: column; align-items: center; padding: 32px 16px; background: {{{{c.bg}}}}; color: {{{{c.ink}}}}">
  <div role="dialog" aria-labelledby="w1" style="width: 100%; max-width: 760px; box-sizing: border-box; background: {{{{c.surf}}}}; border: 1px solid {{{{c.line}}}}; border-radius: 12px; padding: 24px; display: flex; flex-direction: column; gap: 16px">
    {rail1}
    <div style="display: flex; flex-direction: column; gap: 8px">
      <h1 id="w1" style="margin: 0; font-size: 28px">Welcome to Mecha DK</h1>
      <div style="font-size: 15px; line-height: 1.55">You pose research questions and hypotheses. The mecha turns them into experiments, runs them in cycles, and keeps track of what each result means. It stops to ask you before it spends, when a change is ready for review, and when how results are measured should change. It works for software and for studies in the lab or the field.</div>
    </div>
    <section aria-labelledby="dm" style="display: flex; flex-direction: column; gap: 10px">
      <h2 id="dm" style="margin: 0; font-size: 17px">See it working first</h2>
      <div style="display: flex; flex-wrap: wrap; gap: 12px">
        {demo("Improving the dk build system","The hypothesis tree behind Paper I: changes proposed, tested and decided for MlFront, the dk build and learning system.","[n] hypotheses, [n] cycles")}
        {demo("Fixing bugs in Java programs","A tree grown from program repairs on RunBugRun, then used to seed repairs of real Java bugs from Defects4J.","[n] hypotheses, [n] repairs")}
      </div>
      <div style="font-size: 13px; color: {{{{c.mut}}}}">Demos open read-only and need no account. They are also under Demos on the Projects page.</div>
    </section>
    <div style="display: flex; flex-wrap: wrap; gap: 10px; align-items: center; justify-content: space-between; padding-top: 6px; border-top: 1px solid {{{{c.line}}}}">
      {btn('Sign in to Diskuv SaaS')}
      <span style="display: inline-flex; flex-wrap: wrap; gap: 10px">{btn('Continue without an account', True)}</span>
    </div>
  </div>
</div>
'''+(TAIL % H1)
open(os.path.join(OUT,'WelcomeStart.dc.html'),'w').write(html1)
d=json.load(open(os.path.join(OUT,'canvas.json')))
d['boards']['WelcomeStart.dc.html']={'x':5680,'y':300,'w':1200,'h':720,'expand':'fill','title':'First launch: welcome wizard, step 1 (with the demos)'}
if 'WelcomeStart.dc.html' not in d['order']: d['order'].insert(d['order'].index('Welcome.dc.html'),'WelcomeStart.dc.html')
json.dump(d,open(os.path.join(OUT,'canvas.json'),'w'),indent=2)
