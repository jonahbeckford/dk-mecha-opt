import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
from common import *
f=sys.argv[1]; s=open(f).read()
MONO="font-family: 'Ubuntu Mono', monospace"
# 1 Set up -> run-function
k=s.index('Set up (optional)</div>')
a=s.index('<div style="display: flex; flex-wrap: wrap; gap: 10px; align-items: flex-end">',k)
b=s.index('</div></div>',a)+len('</div>')
fn=f'<label style="{LB.replace("1 1 200px","2 1 320px")}">Function rule<span style="display: flex; gap: 8px; align-items: center"><code style="flex: none; font-size: 14px; font-weight: 400">dk0 run-function</code><input type="text" value="[Setup_MODULE@VERSION]" style="{FS}; flex: 1 1 auto; {MONO}"></span></label>'
s=s[:a]+row(fn, sel('Time limit',['[30 minutes]','[2 hours]','[8 hours]'],'0 1 180px'))+s[b:]
s=s.replace('Runs once per executor before the first experiment, to download or prepare inputs. The only step that may use the internet and the setup secrets.','A function rule run once per executor before the first experiment, to download or prepare inputs. Given the same items as the experiment. The only step that may use the internet and the setup secrets.',1)
# 2 standing instructions -> textarea editor
m=re.search(r'<label style="display: flex; flex-direction: column; gap: 4px; flex: 2 1 320px; font-size: 14px; font-weight: 600">Standing instructions<input[^>]*></label>',s)
assert m
tb=lambda t,aria: f'<button type="button" aria-label="{aria}" style="min-height: 36px; min-width: 36px; padding: 0 8px; font-size: 13px; border: 1px solid {{{{c.line}}}}; border-radius: 4px; background: transparent; color: {{{{c.ink}}}}">{t}</button>'
ed=(f'<div style="flex: 1 1 100%; display: flex; flex-direction: column; gap: 4px"><label for="si" style="font-size: 14px; font-weight: 600">Standing instructions</label>'
    f'<div style="border: 1px solid {{{{c.line}}}}; border-radius: 6px; overflow: hidden"><div role="toolbar" aria-label="Formatting" style="display: flex; flex-wrap: wrap; gap: 4px; padding: 4px; border-bottom: 1px solid {{{{c.line}}}}; background: {{{{c.surf}}}}">{tb("<b>B</b>","Bold")}{tb("<i>I</i>","Italic")}{tb("•","Bulleted list")}{tb("1.","Numbered list")}{tb("&lt;/&gt;","Code")}{tb("Preview","Preview")}</div>'
    f'<textarea id="si" rows="8" style="display: block; box-sizing: border-box; width: 100%; padding: 10px 12px; font-size: 15px; line-height: 1.5; border: 0; background: {{{{c.bg}}}}; color: {{{{c.ink}}}}; resize: vertical; {MONO}">[Build a statistically sound validation before you trust any score.\n\nApply the same feature set, preprocessing and encoding to validation and test inputs.]</textarea></div>'
    f'<span style="font-size: 12px; color: {{{{c.mut}}}}">Markdown. Read by the LLM before it proposes hypotheses and writes each experiment. Saved with the project and in templates.</span></div>')
s=s[:m.start()]+ed+s[m.end():]
# 3 Protocol of record -> list of specification files
k=s.index('<h3 style="font-size: 15px; font-weight: 700; margin: 0">Protocol of record</h3>')
a=s.rindex('      <div style="display: flex; flex-direction: column; gap: 8px; padding-top: 12px; border-top: 1px solid {{c.line}}">',0,k)
b=s.index('      <div style="display: flex; flex-direction: column; gap: 8px; padding-top: 12px; border-top: 1px solid {{c.line}}">',k)
TD='padding: 6px 10px; vertical-align: middle'
def S(opts,aria,first=0):
    return f'<select aria-label="{aria}" style="{FS}">'+''.join(f'<option{" selected" if i==first else ""}>{o}</option>' for i,o in enumerate(opts))+'</select>'
kinds=['Specification','Reference','Checked assumptions','Protocol or pre-registration','Other']
def r(path, where, kind, checked):
    return f'<tr style="border-top: 1px solid {{{{c.line}}}}"><td style="{TD}"><code>{path}</code></td><td style="{TD}; color: {{{{c.mut}}}}">{where}</td><td style="{TD}">{S(kinds,"Kind",kinds.index(kind))}</td><td style="{TD}; color: {{{{c.mut}}}}">{checked}</td><td style="{TD}"><button type="button" style="{BTN}">Delete</button></td></tr>'
th=''.join(f'<th scope="col" style="{TD}; font-weight: 600">{h}</th>' for h in ['File','In','Kind','Checked how'])
tbl=(f'<div style="overflow-x: auto; border: 1px solid {{{{c.line}}}}; border-radius: 6px"><table style="width: 100%; min-width: 760px; border-collapse: collapse; font-size: 14px"><thead><tr style="text-align: left; color: {{{{c.mut}}}}">{th}<th scope="col" style="{TD}"><span style="position: absolute; left: -9999px">Actions</span></th></tr></thead><tbody>'
     + r('SPECIFICATION.md','[github.com/owner/app]','Specification','Read at REVIEW')
     + r('DK0-REFERENCE.md','[github.com/owner/app]','Reference','Read at REVIEW')
     + r('Assumptions.ml','[github.com/owner/app]','Checked assumptions','Compiled: fails when a named symbol changes')
     + '</tbody></table></div>')
new=f'''      <div style="display: flex; flex-direction: column; gap: 8px; padding-top: 12px; border-top: 1px solid {{{{c.line}}}}">
        <h3 style="font-size: 15px; font-weight: 700; margin: 0">Protocol of record</h3>
        <div style="font-size: 14px; color: {{{{c.mut}}}}; line-height: 1.45">The specification, references, checked assumptions, protocol or pre-registration, in as many files as you keep. When a change is adopted, you review it against all of them.</div>
        {tbl}
        {row(btn('Add a file from a repository'), btn('Upload a document'), btn('None yet: the mecha drafts a specification at the start'), align='center')}
        <div style="font-size: 13px; color: {{{{c.mut}}}}; line-height: 1.45">A checked-assumptions file stops a stale assumption silently surviving: in a typed language it fails to compile when a symbol it names changes; in a dynamic language it is an assertion that fails when run. These files are read-only to the mecha unless you list them under "may change".</div>
      </div>
'''
s=s[:a]+new+s[b:]
open(f,'w').write(s)
