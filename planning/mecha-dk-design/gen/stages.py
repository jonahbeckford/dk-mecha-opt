import json, os, sys
OUT = sys.argv[1]
STAGES = [
 ('OBSERVE','StageObserve','done'),('AUTHORIZE','StageAuthorize','now'),('IDEATE','StageIdeate','next'),
 ('DROP','StageDrop','next'),('SELECT','StageSelect','next'),('DISPATCH','StageDispatch','next'),
 ('UPDATE','StageUpdate','next'),('DECIDE','StageDecide','next'),('REVIEW','ReviewCalibrate','att'),
 ('CALIBRATE','ReviewCalibrate','llm'),('PERSIST','StagePersist','next')]
HEAD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&amp;family=Lato:wght@400;700&amp;family=Ubuntu+Mono:wght@400;700&amp;display=swap">
<style>
body{{margin:0;font-family:Inter,Helvetica,Arial,sans-serif}}
h1,h2,h3,legend{{font-family:Lato,Inter,sans-serif;font-weight:700}}
code{{font-family:"Ubuntu Mono",monospace}}
button,input,textarea,select{{font-family:inherit}}
a{{color:inherit}}
th{{font-weight:600}}
</style>
</helmet>
'''
TAIL = '''</x-dc>
<script type="text/x-dc" data-dc-script data-props='{"dark":{"editor":"boolean","default":false,"section":"Theme"},"$preview":{"width":1360,"height":%d}}'>
class Component extends DCLogic {
  renderVals() {
    const d = !!this.props.dark;
    const c = d
      ? { bg: '#000000', surf: '#1A1A1A', surf2: '#0F1D24', sel: '#2A174F', done: '#142F0E', att: '#2F2A0E', track: '#404040', wide: '#4D357D', ink: '#FFFFFF', mut: '#A6A6A6', line: '#404040', acc: '#9A82CA', accInk: '#000000', warn: '#D0BE62', ok: '#A9E19D', bad: '#D67686' }
      : { bg: '#E6E6E6', surf: '#FFFFFF', surf2: '#DBE9F0', sel: '#E2DBF0', done: '#DDF3D8', att: '#F6F2E0', track: '#E6E6E6', wide: '#9A82CA', ink: '#000000', mut: '#595959', line: '#B3B3B3', acc: '#542F9D', accInk: '#FFFFFF', warn: '#766923', ok: '#2A621E', bad: '#B0354A' };
    return { c };
  }
}
</script>
</body>
</html>
'''
BTN = 'min-height: 44px; padding: 0 16px; font-size: 15px; border: 1px solid {{c.line}}; border-radius: 6px; background: transparent; color: {{c.ink}}'
PRI = 'min-height: 44px; padding: 0 18px; font-size: 15px; font-weight: 600; border: 0; border-radius: 6px; background: {{c.acc}}; color: {{c.accInk}}'
LINK = 'min-height: 44px; display: inline-flex; align-items: center; color: {{c.acc}}'
def btn(t, primary=False): return f'<button type="button" style="{PRI if primary else BTN}">{t}</button>'
def a(t, href): return f'<a href="{href}" style="{LINK}">{t}</a>'
def section(title, body, sid, border='1px solid {{c.line}}'):
    return f'''      <section aria-labelledby="{sid}" style="background: {{{{c.surf}}}}; border: {border}; border-radius: 8px; padding: 18px; display: flex; flex-direction: column; gap: 10px">
        <h2 id="{sid}" style="margin: 0; font-size: 17px">{title}</h2>
{body}
      </section>
'''
def p(t, small=False): return f'        <div style="font-size: {13 if small else 14}px; color: {{{{c.mut}}}}; line-height: 1.5">{t}</div>'
def tag(t, col): return f'<span style="font-weight: 600; color: {{{{c.{col}}}}}">{t}</span>'
def table(cols, rows, minw=640):
    th = ''.join(f'<th scope="col" style="padding: 8px 12px; text-align: left; color: {{{{c.mut}}}}">{c}</th>' for c in cols)
    tr = ''.join('<tr style="border-top: 1px solid {{c.line}}">' + ''.join(f'<td style="padding: 8px 12px; vertical-align: top">{x}</td>' for x in r) + '</tr>' for r in rows)
    return f'        <div style="overflow-x: auto"><table style="width: 100%; min-width: {minw}px; border-collapse: collapse; font-size: 14px"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'
def ul(items):
    li = ''.join(f'<li style="padding: 10px 0; border-top: 1px solid {{{{c.line}}}}; display: flex; flex-wrap: wrap; gap: 4px 12px; align-items: baseline">{x}</li>' for x in items)
    return f'        <ul style="list-style: none; margin: 0; padding: 0; font-size: 15px">{li}</ul>'

def rail(cur):
    out = []
    for name, f, st in STAGES:
        here = name == cur
        if st == 'now':
            sty = 'border: 2px solid {{c.warn}}; background: {{c.att}}'; sub = tag('needs you', 'warn')
        elif st == 'done':
            sty = 'background: {{c.done}}'; sub = 'done'
        elif st == 'att':
            sty = 'border: 1px dashed {{c.warn}}'; sub = 'attended'
        elif st == 'next':
            sty = 'border: 1px solid {{c.line}}'; sub = 'next'
        else:
            sty = 'border: 1px dashed {{c.warn}}'; sub = 'with an LLM only'
        if here: sty += '; outline: 3px solid {{c.acc}}; outline-offset: 1px'
        cur_attr = ' aria-current="page"' if here else ''
        out.append(f'<li style="flex: 1 0 84px; display: flex"><a href="{f}.dc.html"{cur_attr} style="flex: 1 1 auto; min-height: 44px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: center; padding: 6px 8px; border-radius: 6px; {sty}; font-size: 12px; font-weight: 600; text-decoration: none"><span>{name}</span><span style="font-weight: 400; color: {{{{c.mut}}}}">{sub}</span></a></li>')
    return '<ol aria-label="Stages of cycle [n]" style="margin: 0; padding: 0; list-style: none; display: flex; flex-wrap: wrap; gap: 6px">' + ''.join(out) + '</ol>'

def page(stage, fname, h1, what, facts, body, reads, writes, height=1300):
    fact_html = ''.join(f'<div style="flex: 1 1 200px; display: flex; flex-direction: column; gap: 2px"><span style="font-size: 13px; color: {{{{c.mut}}}}">{k}</span><span style="font-size: 15px; font-weight: 600">{v}</span></div>' for k, v in facts)
    html = HEAD.format(title=f'{stage} stage') + f'''<div style="min-height: {height}px; box-sizing: border-box; display: flex; flex-direction: column; background: {{{{c.bg}}}}; color: {{{{c.ink}}}}">
  <header style="display: flex; flex-wrap: wrap; align-items: center; gap: 8px 12px; padding: 6px 24px; min-height: 56px; background: {{{{c.surf}}}}; border-bottom: 1px solid {{{{c.line}}}}">
    <a href="Projects.dc.html" style="font-size: 18px; font-weight: 700; text-decoration: none; min-height: 44px; display: inline-flex; align-items: center">Mecha DK</a>
    <div style="font-size: 15px; color: {{{{c.mut}}}}; flex: 1 1 auto">/ [Project name] / <a href="Cycle.dc.html">Cycle [n]</a> / {stage}</div>
    <a href="Windows.dc.html" style="display: inline-flex; align-items: center; min-height: 44px; padding: 0 12px; font-size: 14px; font-weight: 600; border: 1px solid {{{{c.line}}}}; border-radius: 6px; text-decoration: none">Attended until 18:00</a><button type="button" style="min-height: 44px; padding: 0 16px; font-size: 15px; font-weight: 700; border: 2px solid {{{{c.bad}}}}; border-radius: 6px; background: transparent; color: {{{{c.bad}}}}">Pause now</button>
    <nav aria-label="Cycles" style="display: inline-flex; gap: 6px"><a href="#prev" style="display: inline-flex; align-items: center; min-height: 44px; padding: 0 14px; font-size: 14px; border: 1px solid {{{{c.line}}}}; border-radius: 6px; text-decoration: none">Cycle [n-1]</a><a href="#next" aria-disabled="true" style="display: inline-flex; align-items: center; min-height: 44px; padding: 0 14px; font-size: 14px; border: 1px solid {{{{c.line}}}}; border-radius: 6px; text-decoration: none; color: {{{{c.mut}}}}">Cycle [n+1]</a></nav>
  </header>
  <main style="width: 100%; max-width: 1180px; box-sizing: border-box; margin: 0 auto; padding: 22px 24px; display: flex; flex-direction: column; gap: 18px">
    {rail(stage)}
    <div style="display: flex; flex-direction: column; gap: 6px">
      <h1 style="margin: 0; font-size: 26px">{stage}: {h1}</h1>
      <div style="font-size: 15px; color: {{{{c.mut}}}}; line-height: 1.5; max-width: 820px">{what}</div>
    </div>
    <div style="display: flex; flex-wrap: wrap; gap: 12px 20px; padding: 14px 18px; background: {{{{c.surf}}}}; border: 1px solid {{{{c.line}}}}; border-radius: 8px">{fact_html}</div>
{body}
    <div style="display: flex; flex-wrap: wrap; gap: 12px 24px; font-size: 13px; color: {{{{c.mut}}}}; line-height: 1.5; padding-top: 4px; border-top: 1px solid {{{{c.line}}}}">
      <div style="flex: 1 1 300px"><strong style="color: {{{{c.ink}}}}">Reads</strong> {reads}</div>
      <div style="flex: 1 1 300px"><strong style="color: {{{{c.ink}}}}">Writes</strong> {writes}</div>
    </div>
  </main>
</div>
''' + (TAIL % height)
    open(os.path.join(OUT, fname + '.dc.html'), 'w').write(html)

DONE = lambda t: ('Status', tag('Done', 'ok') + f' <span style="font-weight: 400; color: {{{{c.mut}}}}">{t}</span>')
LAST = ('Status', 'Not reached yet in cycle [n] <span style="display: block; font-weight: 400; font-size: 13px; color: {{c.mut}}">Showing cycle [n-1], done [time], took [duration]</span>')
MECHA = ('Done by', 'The mecha, on [device]')
ALWAYS = ('Runs', 'Every cycle, attended or not')

page('OBSERVE','StageObserve','read where things stand',
 'The mecha reads the project as it was left: what it believes about each hypothesis, what was posed since the last cycle, and what went wrong last time.',
 [DONE('[time], took [duration]'), MECHA, ALWAYS],
 section('Posed since cycle [n-1]', ul([
   tag('Question','acc') + '<span style="flex: 1 1 300px">[Research question]</span><span style="color: {{c.mut}}">by [person], [date]. Goes to IDEATE</span>',
   tag('Hypothesis','acc') + '<span style="flex: 1 1 300px">[Hypothesis]</span><span style="color: {{c.mut}}">by [person], [date]. Placed under [parent]</span>']), 'h-posed')
 + section('Problems from last cycle', p('Each failure is matched to the hypothesis it belongs to. The tree keeps it as evidence.') + table(['What happened','Matched to','Next'], [
   [tag('Failed','bad') + ' [experiment]: [first line of the error]', '[Hypothesis]', a('Open log','#log')],
   [tag('Timed out','warn') + ' [experiment] after [duration]', '[Hypothesis]', 'Counts as no result; may be chosen again']]), 'h-prob')
 + section('Where beliefs stand', p('No change since the end of cycle [n-1]. [n] hypotheses open, [n] parked, [n] settled.') + '        <div style="display: flex; flex-wrap: wrap; gap: 10px">' + a('Open the hypothesis tree','Tree.dc.html') + '</div>', 'h-bel'),
 'the hypothesis tree and its stored results, everything posed, last cycle\'s logs.',
 'nothing new to the tree; it hands the matched problems to IDEATE and SELECT.', 1250)

page('AUTHORIZE','StageAuthorize','release what is waiting on you',
 'Some hypotheses wait for you before the mecha may choose them: a run that does something you asked to approve, a revelation only you can make, or an experiment a person must run. Release them here, or leave them parked. In an unattended window this stage is skipped and they stay parked.',
 [('Status', tag('Needs you','warn') + ' <span style="font-weight: 400; color: {{c.mut}}">since [time]</span>'), ('Done by', 'You'), ('Runs', 'Attended windows only')],
 section('Parked for what the run does ([n])', table(['Hypothesis','What needs you','Cost, worked out now','Value of what it would tell us',''], [
   ['[Hypothesis]', 'Runs on a paid executor: [Diskuv SaaS]', 'Up to [$3.20]: time limit [2 h] at [$1.60] an hour. ' + a('Show the calculation','#calc'), '[VoI], expected loss [L]', '<span style="display: flex; flex-wrap: wrap; gap: 6px">' + btn('Authorize, up to [$3.20]', True) + btn('Run on this computer') + btn('Keep parked') + '</span>'],
   ['[Hypothesis]', 'Its run step uses <code>[RELEASE_TOKEN]</code>, which you marked Approve each use', '[What the secret lets it do, in your words]', '[VoI], expected loss [L]', '<span style="display: flex; flex-wrap: wrap; gap: 6px">' + btn('Authorize this run', True) + btn('Keep parked') + '</span>']], 900)
   + p('The mecha parks a run for what it does, as set in ' + a('Experiment environment','Environment.dc.html') + ': a paid executor, or a secret marked Approve each use. Each approval releases one run of one hypothesis, and is recorded with who gave it and when. Run on this computer appears when this computer meets the hardware.', True), 'h-sp', '2px solid {{c.warn}}')
 + section('Waiting for a revelation from you ([n])', p('The mecha asks: [the question only you can answer]. Your revelation is checked against the project\'s other revelations before it is added.')
   + '        <div style="display: flex; flex-wrap: wrap; gap: 10px"><input aria-label="Your revelation" type="text" placeholder="[State what is true]" style="flex: 1 1 300px; min-height: 44px; box-sizing: border-box; padding: 0 12px; font-size: 16px; border: 1px solid {{c.line}}; border-radius: 6px; background: {{c.bg}}; color: {{c.ink}}">' + btn('Check and add', True) + '</div>', 'h-st')
 + section('Experiments for a person ([n])', ul([
   '<span style="flex: 1 1 300px">[Experiment: the protocol, in one line]</span><select aria-label="Who runs it" style="min-height: 44px; padding: 0 10px; font-size: 15px; border: 1px solid {{c.line}}; border-radius: 6px; background: {{c.bg}}; color: {{c.ink}}"><option>You</option><option>[Collaborator]</option></select>' + btn('Authorize and send', True) + a('Read the protocol','HumanTask.dc.html')]), 'h-hu')
 + '      <div style="display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 10px">' + btn('Done, continue to IDEATE', True) + '</div>\n',
 'what SELECT parked last cycle and why.', 'your releases, each with who released it and when; released hypotheses become choosable at SELECT.', 1250)

page('IDEATE','StageIdeate','propose new hypotheses',
 'New hypotheses come from the people on the project and, if the project has one, from an LLM. The LLM always reads this project\'s hypotheses and results, plus the sources the project allows. Each new hypothesis starts with a prior: how likely the mecha thinks it is before any experiment.',
 [LAST, ('Done by', '[People on the project] and [LLM: connection / model]'), ('Sources used', '[Zotero, Semantic Scholar]')],
 section('New hypotheses ([n])', table(['Hypothesis','For','From','Starting belief'], [
   ['[Hypothesis]', '[Research question]', '[LLM], citing ' + a('[Zotero item]','#src') + ', ' + a('[paper]','#src'), '<code>Beta(1, 3)</code> about 25%'],
   ['[Hypothesis]', '[Research question]', '[Collaborator], posed [date]', '<code>Beta(1, 1)</code> no view yet'],
   ['[Hypothesis]', 'Follows from a revelation', '[LLM], from ' + a('[revelation]','Cycle.dc.html#rev'), '<code>Beta(2, 2)</code> about 50%']], 760)
   + p('Two kinds: some follow from a revelation, others from the results so far. The mecha keeps a mix, and leans toward the second when the first keep failing.', True), 'h-new')
 + section('What the LLM looked at', ul([
   tag('Zotero','acc') + '<span style="flex: 1 1 300px"><code>[query]</code> in [library]</span><span style="color: {{c.mut}}">[n] items read</span>',
   tag('Semantic Scholar','acc') + '<span style="flex: 1 1 300px"><code>[query]</code>, fields of study [field]</span><span style="color: {{c.mut}}">[n] papers</span>',
   tag("The LLM's own search",'acc') + '<span style="flex: 1 1 300px"><code>[query]</code></span><span style="color: {{c.mut}}">[n] pages cited</span>'])
   + '        <div style="font-size: 13px; line-height: 1.45; padding: 10px 12px; border-radius: 6px; border: 2px solid {{c.bad}}">Papers, notes and web pages can carry a prompt injection. Check a hypothesis from an unfamiliar source before you authorize a run of it. ' + a('More','Collaborators.dc.html') + '</div>'
   + '        <div>' + a('Open the full LLM transcript','#transcript') + '</div>', 'h-src'),
 'the tree, open research questions, the revelations, last cycle\'s results, the allowed sources.',
 'new hypotheses into the tree, each with its starting belief and the sources it came from.', 1350)

page('DROP','StageDrop','check new hypotheses against the revelations',
 'Before the mecha spends on a new hypothesis, it checks it against the project\'s revelations. A clear contradiction is dropped. A weaker one is kept, flagged, and believed less.',
 [LAST, MECHA, ALWAYS],
 section('Results for the [n] new hypotheses', table(['Hypothesis','Result','Because'], [
   ['[Hypothesis]', tag('Dropped','bad'), 'Contradicts "' + a('[revelation]','Cycle.dc.html#rev') + '" with high confidence ([0.97])'],
   ['[Hypothesis]', tag('Flagged','warn') + ', belief lowered from 50% to [30%]', 'May contradict "' + a('[revelation]','Cycle.dc.html#rev') + '" ([0.62])'],
   ['[Hypothesis]', tag('Passed','ok'), 'No contradiction found']], 760)
   + p('A dropped hypothesis stays in the tree, marked dropped. You can see it was considered.', True), 'h-drop'),
 'the hypotheses IDEATE just added, the revelations.', 'dropped and flagged marks, and lowered starting beliefs.', 1000)

page('SELECT','StageSelect','choose what to test',
 'The mecha weighs every open hypothesis, new or old, by how much testing it would tell us against what it costs, and picks the best within the cycle\'s budget. A test that only tells us something can still be worth running.',
 [LAST, MECHA, ('Budget this cycle', '[budget], [spent] chosen')],
 section('The choice', table(['Hypothesis','Belief now','Value of testing','Cost','Choice'], [
   ['[Hypothesis]', '<code>Beta(3, 2)</code> 60%', '[high]', '[cost]', tag('Chosen','ok')],
   ['[Hypothesis]', '<code>Beta(1, 1)</code> no view yet', '[high]', '[cost]', tag('Parked','warn') + ': runs on a paid executor, ' + a('AUTHORIZE','StageAuthorize.dc.html')],
   ['[Hypothesis]', '<code>Beta(1, 4)</code> 20%', '[low]', '[cost]', 'Not this cycle'],
   ['[Hypothesis]', '<code>Beta(2, 2)</code> 50%', '[medium]', '[cost]', tag('Parked','warn') + ': needs a person, ' + a('AUTHORIZE','StageAuthorize.dc.html')]], 760)
   + p('Value of testing is how much the result is expected to improve the next decision. The numbers behind each row are in ' + a('the SELECT report','#report') + '.', True), 'h-sel'),
 'every open hypothesis and its belief, costs per executor, what parks for your approval, the budget.',
 'the chosen list for DISPATCH, and parked hypotheses with the reason.', 1050)

page('DISPATCH','StageDispatch','run the experiments',
 'Each chosen hypothesis becomes an experiment, written by you or an LLM, and runs where the project says: on this computer, on GitHub Actions, on Diskuv SaaS, or with a person.',
 [LAST, ('Done by', '[Executor]; experiments written by [you / LLM]'), ('Results', '[n] observed, [n] failed, [n] with a person')],
 section('Experiments ([n])', table(['Hypothesis','Where','Status','Result'], [
   ['[Hypothesis]', 'This computer, in an MXC sandbox', tag('Observed','ok') + ' [duration]', '[outcome y] ' + a('Log','#log') + ' ' + a('Version S3','SuoBrowser.dc.html')],
   ['[Hypothesis]', a('GitHub Actions','GitHubRemote.dc.html') + ' [repo]', tag('Observed','ok') + ' [duration]', '[outcome y] ' + a('Run','#run')],
   ['[Hypothesis]', a('Diskuv SaaS','SaaSRemote.dc.html'), tag('Failed','bad') + ' [duration]', a('Log','#log')],
   ['[Hypothesis]', '[Person]', tag('With [person]','warn') + ' sent [date]', a('Protocol','HumanTask.dc.html')]], 760)
   + p('Results that arrive after this stage, such as a person\'s, are used in the next cycle\'s UPDATE.', True), 'h-dis'),
 'the chosen list, the experiment environment, each executor\'s sign-in.', 'one result or failure per experiment, with its log.', 1050)

page('UPDATE','StageUpdate','fold results into beliefs',
 'Each result changes the belief in its hypothesis, and that change carries up the tree to the hypotheses above it. What moves is the full belief. Every measurement is kept.',
 [LAST, MECHA, ALWAYS],
 section('Beliefs that changed ([n])', table(['Hypothesis','Before','After','Why'], [
   ['[Hypothesis]', '<code>Beta(3, 2)</code> 60%', '<code>Beta(4, 2)</code> 67%', 'Passed on [case]'],
   ['&nbsp;&nbsp;above it: [parent]', '<code>Beta(5, 5)</code> 50%', '<code>Beta(6, 5)</code> 55%', 'From [hypothesis]'],
   ['[Hypothesis]', '<code>t(0.40, 0.12, 6)</code>', '<code>t(0.31, 0.08, 7)</code>', 'Measured [0.29] on [case]']], 760)
   + '        <div style="display: flex; flex-wrap: wrap; gap: 10px">' + btn('Show curves') + a('What these formulas mean','#formulas') + '</div>'
   + p('Each hypothesis also gets a short note in words. The note is for reading; the belief is what the mecha decides with.', True), 'h-up'),
 'DISPATCH results, the tree.', 'new beliefs for each tested hypothesis and those above it.', 1050)

page('DECIDE','StageDecide','merge, prune or keep testing',
 'With the new beliefs, the mecha decides for each tested hypothesis whether it is settled. A change better than the current best is merged. A hypothesis whose next test would cost more than it could tell us is pruned. The rest stay open.',
 [LAST, MECHA, ALWAYS],
 section('Decisions ([n])', table(['Hypothesis','Decision','Because'], [
   ['[Hypothesis]', tag('Merged','ok') + ' into the current best', 'Better than the current best with [96%] probability; expected loss of merging [L]'],
   ['[Hypothesis]', tag('Pruned','bad'), 'Expected gain [g] is below the cost of another test'],
   ['[Hypothesis]', 'Keep testing', 'Not yet clear: [55%]; worth [VoI] more']], 760)
   + p('A merged change goes to REVIEW, where you read it against the protocol of record. Pruned hypotheses stay in the tree and can be reopened by new evidence.', True)
   + '        <div>' + a('Go to REVIEW','ReviewCalibrate.dc.html') + '</div>', 'h-dec'),
 'beliefs after UPDATE, the current best, costs.', 'merge and prune decisions; merged changes go to REVIEW.', 1000)

page('PERSIST','StagePersist','save the cycle',
 'The mecha saves the updated tree and any measurement changes researched at CALIBRATE. Another device can then pick up the project where this one stopped.',
 [LAST, MECHA, ALWAYS],
 section('Saved', ul([
   '<span style="flex: 1 1 260px">Hypothesis tree, version [v]</span><span style="color: {{c.mut}}">[n] hypotheses, [n] results</span>',
   '<span style="flex: 1 1 260px">Measurement changes researched</span><span style="color: {{c.mut}}">[n], waiting for the next break between cycles</span>',
   '<span style="flex: 1 1 260px">Where</span><span style="color: {{c.mut}}">The project folder, <code>[~/Mecha DK/project-title]</code> on [this computer]</span>'])
   + p('Secrets and keys are never saved with the project.', True)
   + p('The next cycle starts from this saved version, on this device or another.', True), 'h-per'),
 'the tree after DECIDE, CALIBRATE\'s approved changes.', 'a new saved version of the project.', 950)

d = json.load(open(os.path.join(OUT, 'canvas.json')))
y = 11420
d['notes']['t7'] = {'x': 0, 'y': 11120, 'text': 'One page per stage of a cycle (REVIEW and CALIBRATE are above)', 'kind': 'title1', 'maxW': 12880}
names = [s for s in STAGES if s[1].startswith('Stage')]
for i, (name, f, _) in enumerate(names):
    key = f + '.dc.html'
    d['boards'][key] = {'x': i * 1440, 'y': y, 'w': 1360, 'h': 1350, 'expand': 'fill', 'title': f'Web: {name} stage'}
    if key not in d['order']: d['order'].append(key)
json.dump(d, open(os.path.join(OUT, 'canvas.json'), 'w'), indent=2)
