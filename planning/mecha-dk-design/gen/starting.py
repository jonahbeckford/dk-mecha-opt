# Shared pieces: the "Problems and hypotheses to start with" section and badges.
BTNS='min-height: 44px; padding: 0 16px; font-size: 15px; border: 1px solid {{c.line}}; border-radius: 6px; background: transparent; color: {{c.ink}}'
FLD='min-height: 44px; box-sizing: border-box; padding: 0 10px; font-size: 15px; border: 1px solid {{c.line}}; border-radius: 6px; background: {{c.bg}}; color: {{c.ink}}'
def badge(t, need=False):
    bg='{{c.att}}' if need else '{{c.sel}}'
    col='; color: {{c.warn}}' if need else ''
    return '<span style="font-size: 12px; font-weight: 600; padding: 2px 8px; border-radius: 10px; background: '+bg+col+'; white-space: nowrap">'+t+'</span>'
def btn(t): return '<button type="button" style="'+BTNS+'">'+t+'</button>'
def item(n, kind, text, source, ph=False):
    opts=''.join('<option%s>%s</option>'%(' selected' if k==kind else '',k) for k in ('Problem','Hypothesis'))
    body=('' if ph else text)
    phattr=(' placeholder="'+text+'"') if ph else ''
    return ('<li style="display: flex; flex-wrap: wrap; align-items: flex-start; gap: 8px 10px; padding: 10px 0; border-top: 1px solid {{c.line}}">'
      '<label style="display: flex; flex-direction: column; gap: 4px; flex: 0 1 150px; min-width: 0; font-size: 14px; font-weight: 600">Kind<select style="'+FLD+'; max-width: 100%">'+opts+'</select></label>'
      '<label style="display: flex; flex-direction: column; gap: 4px; flex: 1 1 300px; min-width: 0; font-size: 14px; font-weight: 600"><span style="display: flex; flex-wrap: wrap; gap: 6px 10px; align-items: center">'+('Question or problem' if kind=='Problem' else 'Change to try, and what it should do')+(' '+badge(source) if source else '')+'</span>'
      '<textarea rows="2"'+phattr+' style="box-sizing: border-box; width: 100%; padding: 8px 10px; font: inherit; font-size: 15px; font-weight: 400; border: 1px solid {{c.line}}; border-radius: 6px; background: {{c.bg}}; color: {{c.ink}}; resize: vertical">'+body+'</textarea></label>'
      '<span style="flex: 0 0 auto; padding-top: 22px">'+btn('Delete')+'</span></li>')
def section(items, note):
    lis=''.join(item(*x) for x in items).replace('border-top: 1px solid {{c.line}}','',1)
    return ('    <fieldset style="min-width: 0; margin: 0; background: {{c.surf}}; border: 1px solid {{c.line}}; border-radius: 8px; padding: 18px; display: flex; flex-direction: column; gap: 10px">\n'
      '      <legend style="font-size: 17px; font-weight: 600; padding: 0 6px">4. Problems and hypotheses to start with</legend>\n'
      '      <div style="font-size: 14px; line-height: 1.5">The first cycle starts from these. At IDEATE the mecha turns each problem into hypotheses. At DROP it checks each hypothesis against the revelations, and SELECT weighs it with the rest. You and your collaborators can pose more at any time.</div>\n'
      '      <ul style="list-style: none; margin: 0; padding: 0">'+lis+'</ul>\n'
      '      <div style="display: flex; flex-wrap: wrap; gap: 10px">'+btn('Add a problem')+btn('Add a hypothesis')+'</div>\n'
      '      <div style="font-size: 13px; color: {{c.mut}}; line-height: 1.45">'+note+'</div>\n'
      '    </fieldset>\n')
