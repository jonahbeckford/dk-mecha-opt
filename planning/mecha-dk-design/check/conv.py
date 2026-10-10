import re,sys
C={'bg': '#E6E6E6', 'surf': '#FFFFFF', 'surf2': '#DBE9F0', 'sel': '#E2DBF0', 'done': '#DDF3D8', 'att': '#F6F2E0', 'track': '#E6E6E6', 'wide': '#9A82CA', 'ink': '#000000', 'mut': '#595959', 'line': '#B3B3B3', 'acc': '#542F9D', 'accInk': '#FFFFFF', 'warn': '#766923', 'ok': '#2A621E', 'bad': '#B0354A'}
for src,dst in zip(sys.argv[1::2],sys.argv[2::2]):
    t=open(src).read(); t=re.sub(r'\{\{c\.(\w+)\}\}',lambda m:C[m.group(1)],t); t=re.sub(r'<script.*?</script>','',t,flags=re.S)
    open(dst,'w').write(t)
