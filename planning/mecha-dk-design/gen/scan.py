import re, glob, html, sys
pat=re.compile(r'—|--|, not |, never |, so | rather than |The @[0-9]| revision |Since @|As of |does not mandate|is not required|out of the | not | never | no longer |instead of ')
for f in sorted(glob.glob('canvas/project/*.dc.html')):
    s=open(f).read()
    s=s[s.find('<x-dc>'):s.find('</x-dc>')]
    s=re.sub(r'<style.*?</style>','',s,flags=re.S)
    txt=re.sub(r'<[^>]+>','\n',s)
    for line in txt.split('\n'):
        line=html.unescape(line).strip()
        if line and pat.search(line):
            print(f.split('/')[-1][:-8],'|',line[:230])
