# Replace the "Check by measuring the starting version" button with a setup check that Start the project runs.
import sys, os
P=sys.argv[1]; f=os.path.join(P,'PIProject.dc.html'); s=open(f).read()
a=s.index('        <div style="display: flex; flex-wrap: wrap; gap: 10px; align-items: center"><button type="button" style="min-height: 44px; padding: 0 18px; font-size: 15px; font-weight: 600; border: 0; border-radius: 6px; background: {{c.acc}}; color: {{c.accInk}}">Check by measuring the starting version</button>')
b=s.index('</div>\n',a)+len('</div>\n'); s=s[:a]+s[b:]
o='    <div style="display: flex; flex-wrap: wrap; gap: 12px; justify-content: flex-end">\n      <a href="Projects.dc.html"'
assert s.count(o)==1
note=('    <div style="font-size: 14px; line-height: 1.5; padding: 12px 14px; border: 1px solid {{c.line}}; border-radius: 6px; background: {{c.surf}}"><b>Start the project</b> first checks the setup. The mecha runs Set up, then one experiment on the starting version, on the executor you chose. '
      'When that run costs money or a person\'s time, it waits for your approval at AUTHORIZE. If the check fails, the project page shows what failed and no cycle starts. If it passes, its results are the starting version\'s first measurement, and the first cycle begins.</div>\n')
s=s.replace(o,note+o)
open(f,'w').write(s)
