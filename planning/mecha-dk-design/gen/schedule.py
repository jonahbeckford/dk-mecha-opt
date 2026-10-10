import os, sys, json
OUT=sys.argv[1]
src=open(os.path.join(os.path.dirname(__file__),'stages.py')).read()
ns={}
exec(src.split("DONE = lambda")[0].replace("OUT = sys.argv[1]","OUT = None"), ns)
HEAD, TAIL, btn, a, section, p, tag, table, ul = (ns[k] for k in ['HEAD','TAIL','btn','a','section','p','tag','table','ul'])
FS='min-height: 44px; box-sizing: border-box; padding: 0 10px; font-size: 15px; border: 1px solid {{c.line}}; border-radius: 6px; background: {{c.bg}}; color: {{c.ink}}'
LB='display: flex; flex-direction: column; gap: 4px; flex: 1 1 160px; font-size: 14px; font-weight: 600'
def inp(label, typ, val='', extra=''): return f'<label style="{LB}">{label}<input type="{typ}" value="{val}" {extra} style="{FS}"></label>'
def sel(label, opts): return f'<label style="{LB}">{label}<select style="{FS}">' + ''.join(f'<option{" selected" if i==0 else ""}>{o}</option>' for i,o in enumerate(opts)) + '</select></label>'
def chk(label, on=False, flex='1 1 100%'): return f'<label style="display: flex; align-items: center; gap: 8px; flex: {flex}; min-height: 44px; font-size: 14px"><input type="checkbox"{" checked" if on else ""} style="width: 20px; height: 20px; margin: 0"> {label}</label>'
def row(*x): return '        <div style="display: flex; flex-wrap: wrap; gap: 10px; align-items: flex-end">' + ''.join(x) + '</div>'
days=''.join(f'<label style="display: inline-flex; align-items: center; justify-content: center; gap: 6px; min-width: 64px; min-height: 44px; padding: 0 10px; border: 1px solid {{{{c.line}}}}; border-radius: 6px; font-size: 14px"><input type="checkbox"{" checked" if d not in ("Sat","Sun") else ""} style="width: 18px; height: 18px; margin: 0"> {d}</label>' for d in ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'])
PAUSE='min-height: 44px; padding: 0 18px; font-size: 15px; font-weight: 700; border: 2px solid {{c.bad}}; border-radius: 6px; background: transparent; color: {{c.bad}}'
H=1500
html = (HEAD.format(title='Windows and pausing') + f'''<div style="min-height: {H}px; box-sizing: border-box; display: flex; flex-direction: column; background: {{{{c.bg}}}}; color: {{{{c.ink}}}}">
  <header style="display: flex; flex-wrap: wrap; align-items: center; gap: 8px 12px; padding: 6px 24px; min-height: 56px; background: {{{{c.surf}}}}; border-bottom: 1px solid {{{{c.line}}}}">
    <a href="Projects.dc.html" style="font-size: 18px; font-weight: 700; text-decoration: none; min-height: 44px; display: inline-flex; align-items: center">Mecha DK</a>
    <div style="font-size: 15px; color: {{{{c.mut}}}}; flex: 1 1 auto">/ [Project name] / <a href="Cycle.dc.html">Cycle [n]</a> / Windows</div>
    <span style="font-size: 14px; font-weight: 600">Attended until 18:00</span>
    <button type="button" style="{PAUSE}">Pause now</button>
  </header>
  <main style="width: 100%; max-width: 1080px; box-sizing: border-box; margin: 0 auto; padding: 24px; display: flex; flex-direction: column; gap: 18px">
    <div style="display: flex; flex-direction: column; gap: 6px">
      <h1 style="margin: 0; font-size: 26px">Attended and unattended windows</h1>
      <div style="font-size: 15px; color: {{{{c.mut}}}}; line-height: 1.5; max-width: 820px">In an attended window, cycles stop at AUTHORIZE, REVIEW and CALIBRATE to ask you. In an unattended window they run back to back, skip those stages, and leave anything that needs you parked. An unattended window lets the mecha run; paid runs wait for you unless you approve an amount for them below. Experiments for a person are sent only if you allow it below. Runs that use a secret you approve each use always wait.</div>
    </div>
''' + section('Now', '''        <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 12px 20px">
          <div style="flex: 1 1 300px; display: flex; flex-direction: column; gap: 2px"><span style="font-size: 18px; font-weight: 700">Attended</span><span style="font-size: 14px; color: {{c.mut}}">Working hours, until 18:00 today. Then unattended until 09:00 tomorrow.</span></div>
          <button type="button" style="''' + PAUSE + '''">Pause now</button>
        </div>
        <fieldset style="min-width: 0; margin: 0; padding: 10px 14px 14px; border: 1px solid {{c.line}}; border-radius: 6px; display: flex; flex-direction: column; gap: 10px"><legend style="font-size: 15px; font-weight: 600; padding: 0 4px">Switch to unattended now</legend>
''' + row(sel('Until', ['Start of working hours (09:00 tomorrow)', 'Monday 09:00', 'A date and time']), inp('Date and time', 'datetime-local'), btn('Switch now', True)) + '''
        ''' + p('Every unattended window has an end; the mecha never guesses one. It uses the limits under Every unattended window.', True) + '''
        </fieldset>''', 'h-now') + section('Working hours', '''        <div role="group" aria-label="Working days" style="display: flex; flex-wrap: wrap; gap: 8px">''' + days + '''</div>
''' + row(inp('From', 'time', '09:00'), inp('To', 'time', '18:00'), sel('Time zone', ['[America/Toronto], this computer', 'Choose']))
 + row(sel('Outside working hours', ['Run unattended', 'Pause until working hours', 'Keep waiting for me (attended)']))
 + p('With "Run unattended", each evening and weekend becomes its own window that ends when working hours start. Holidays: add a window below or pause.', True), 'h-hours')
 + section('Upcoming windows', table(['When', 'Why', 'Limits', ''], [
   ['Fri 18:00 to Mon 09:00', 'Weekend (working hours)', 'Up to 6 cycles', ''],
   ['[Mon 12 Oct] 09:00 to [Wed 14 Oct] 09:00', '[Away at a conference]', 'Up to [10] cycles; paid runs up to [amount] in total', btn('Edit') + ' ' + btn('Cancel')]], 700)
   + '        <div>' + btn('Add an unattended window') + '</div>', 'h-up')
 + section('Before the next window opens', p('These need you, and stay parked while you are away. Clear them in an attended cycle first, or leave them.')
   + ul(['<span style="flex: 1 1 300px">[n] hypotheses parked for your approval</span>' + a('AUTHORIZE','StageAuthorize.dc.html'),
         '<span style="flex: 1 1 300px">[n] merged changes waiting for REVIEW</span>' + a('REVIEW','ReviewCalibrate.dc.html'),
         '<span style="flex: 1 1 300px">[n] hypotheses waiting for a revelation from you</span>' + a('Tree','Tree.dc.html')])
   + row(sel('Attended cycles to run first', ['None', '1', '2'])), 'h-prep')
 + section('Every unattended window', row(inp('Stop after this many cycles', 'number', '6'), inp('Stop after this many cycles in a row that learn nothing', 'number', '2'))
   + chk('Approve paid runs up to [amount] in total during this window') 
   + chk('Allow experiments that a person runs to be sent (they wait for the person)')
   + p('Anything not allowed here stays parked. Measurement changes and revelations are never made inside a window.', True), 'h-lim')
 + section('Pausing', p('Pause now stops the mecha after the step it is doing, and starts nothing new: no new experiment, no new paid run. Experiments already running finish and their results are kept. Nothing already done is undone. The project stays paused until you resume it, even when a window would open.')
   + p('Pause works from any device signed in to this project, including your phone. If the desktop running the project cannot be reached, the pause waits and is applied the moment it can.', True)
   + '        <div style="display: flex; flex-wrap: wrap; gap: 10px; align-items: center; padding: 10px 12px; border: 2px solid {{c.bad}}; border-radius: 6px"><span style="flex: 1 1 260px; font-size: 15px"><strong>When paused:</strong> Paused by [you] at [time] from [phone]. [n] experiments still finishing.</span>' + btn('Resume', True) + '</div>', 'h-pause')
 + section('Past windows', table(['When', 'Cycles', 'Ended because', ''], [
   ['[Sat] 18:00 to [Mon] 09:00', '6, 4 learned something', 'Reached 6 cycles', a('Window report','#report')],
   ['[Thu] 18:00 to [Thu] 23:10', '2', 'Paused by [you]', a('Window report','#report')]], 640), 'h-past') + f'''  </main>
</div>
''' + (TAIL % H))
open(os.path.join(OUT,'Windows.dc.html'),'w').write(html)
d=json.load(open(os.path.join(OUT,'canvas.json')))
d['boards']['Windows.dc.html']={'x':12960,'y':11420,'w':1360,'h':1500,'expand':'fill','title':'Web: attended and unattended windows, pause'}
if 'Windows.dc.html' not in d['order']: d['order'].append('Windows.dc.html')
json.dump(d,open(os.path.join(OUT,'canvas.json'),'w'),indent=2)
