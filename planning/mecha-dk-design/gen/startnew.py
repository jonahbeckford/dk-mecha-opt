# Add section 4 (starting problems and hypotheses) and the "Describe it" start to PIProject; renumber 4,5 -> 5,6.
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from starting import *
f=os.path.join(sys.argv[1],'PIProject.dc.html'); s=open(f).read()
def sub(o,n,c=1):
    global s; assert s.count(o)==c,(o[:70],s.count(o)); s=s.replace(o,n)
sub('6. Who helps','6. Who helps',0)
sub('5. Who helps the mecha','6. Who helps the mecha')
sub('4. Who runs the experiments</legend>','5. Who runs the experiments</legend>')
sub('A template fills sections 1 to 3. You can change anything it fills.','A template fills sections 1 to 4. You can change anything it fills.')
sub('"Save sections 1 to 3 as a template" saves these with the template','"Save sections 1 to 4 as a template" saves these with the template')
sub('Save sections 1 to 3 as a template</button><span style="font-size: 13px; color: {{c.mut}}">Saves the scope, outcomes, revelations and standing instructions for the next project like this one.',
    'Save sections 1 to 4 as a template</button><span style="font-size: 13px; color: {{c.mut}}">Saves the scope, outcomes, revelations, standing instructions, and the problems and hypotheses to start with, for the next project like this one.')
# Describe it, after Blank
k=s.index('Fill in every section yourself.</span></span></label>')+len('Fill in every section yourself.</span></span></label>')
opt=('<label style="flex: 1 1 220px; display: flex; gap: 10px; align-items: flex-start; padding: 12px; border: 1px solid {{c.line}}; border-radius: 8px; background: {{c.surf}}; cursor: pointer"><input type="radio" name="tpl" style="width: 20px; height: 20px; margin: 2px 0 0; flex: none"><span style="display: flex; flex-direction: column; gap: 2px"><span style="font-size: 15px; font-weight: 600">Describe it</span><span style="font-size: 13px; color: {{c.mut}}; line-height: 1.4">Say what you want in your own words. The LLM fills in the form for you to check. Needs an LLM.</span></span></label>')
s=s[:k]+opt+s[k:]
items=[(1,'Problem','[A question to explore, such as: why does the model overfit?]','',True),
       (2,'Hypothesis','[A change to try, and what it should do]','',True)]
sec=section(items,'Saved with the template when you save sections 1 to 4. A project started from that template begins with them.')
k=s.index('    <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 10px; margin-top: -8px"><button type="button"')
s=s[:k]+sec+s[k:]
open(f,'w').write(s)
