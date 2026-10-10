# Apply the maintainer's answers to the eight open questions (2026-10-10) to the boards.
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from starting import *
P=sys.argv[1]
def edit(fn, pairs):
    f=os.path.join(P,fn); s=open(f).read()
    for o,n in pairs:
        assert s.count(o)==1,(fn,o[:70],s.count(o)); s=s.replace(o,n)
    open(f,'w').write(s)
# 6: keep history in git, ticked
edit('PIProject.dc.html',[('To continue the project on another computer, copy or sync the folder, or keep it in a git repository.</span>\n    </div>',
 'To continue the project on another computer, copy or sync the folder, or keep it in a git repository.</span>\n'
 '      <label style="display: flex; align-items: flex-start; gap: 8px; min-height: 44px; font-size: 15px"><input type="checkbox" checked style="width: 20px; height: 20px; margin: 2px 0 0; flex: none"><span style="display: flex; flex-direction: column; gap: 2px"><span>Keep the history in git</span><span style="font-size: 13px; color: {{c.mut}}; line-height: 1.45">Makes the folder a git repository, and each cycle commits what it saved at PERSIST. You choose whether to push it anywhere, in project settings.</span></span></label>\n    </div>')])
# 2: moving to a newer template version
sec=('      <section id="tv" aria-labelledby="tvh" style="margin-top: 8px; background: {{c.surf}}; border: 1px solid {{c.line}}; border-radius: 8px; padding: 20px; display: flex; flex-direction: column; gap: 8px">\n'
 '        <h2 id="tvh" style="margin: 0; font-size: 18px">Template</h2>\n'
 '        <div style="font-size: 15px">Started from <b>[Fix a program until its tests pass]</b>, version [3]. '+badge('Version [4] is available')+'</div>\n'
 '        <div style="font-size: 14px; line-height: 1.5">[What changed, in the author\'s words.] Moving waits for the next break between cycles. If the new version changes how results are measured, the mecha measures the starting version again for a fresh baseline. Your own additions to sections 1 to 4 stay.</div>\n'
 '        <div style="display: flex; flex-wrap: wrap; gap: 10px">'+btn('Show the changes')+btn('Move to version [4]')+'</div>\n'
 '      </section>\n\n')
edit('ProjectSettings.dc.html',[('      <section id="n" aria-labelledby="nw"', sec+'      <section id="n" aria-labelledby="nw"')])
