"""Rigenera API.md: elenco delle funzioni degli script riusabili, con i parametri. Uso: python templates/genera_api.py"""
import ast, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MODS = ['scripts/common.py', 'scripts/render_setup.py', 'scripts/set004.py', 'scripts/pippo.py', 'scripts/tumbo.py', 'scripts/props004.py', 'scripts/props007.py', 'scripts/props009.py', 'scripts/giulia.py', 'scripts/pippo2.py',
        'scripts/props010.py', 'scripts/props011.py', 'scripts/props012.py', 'scripts/eleonora.py', 'scripts/props013.py', 'scripts/props014.py', 'scripts/props015.py', 'scripts/props016.py', 'scripts/props016b.py', 'scripts/animali.py', 'scripts/paesaggi.py', 'scripts/posti.py',
        'scripts/lookdev.py', 'scripts/kitlook.py', 'scripts/render_t004.py', 'scripts/trascrivi.py', 'scripts/kit_options.py', 'scripts/sheet_opts.py', 'scripts/sheet_opts3.py', 'scripts/foto_pippo.py',
        'assets/pt_assets.py']
out = ['# Indice delle funzioni (generato dagli script)', '']
for m in MODS:
    p = os.path.join(ROOT, m)
    if not os.path.exists(p): continue
    try: tree = ast.parse(open(p, encoding='utf-8').read())
    except SyntaxError: continue
    out += ['', '## ' + m, '']
    doc = ast.get_docstring(tree)
    if doc: out += [doc.strip(), '']
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and not (m.startswith('assets/') and n.name.startswith('_')):
            d = ast.get_docstring(n); first = d.strip().splitlines()[0] if d else ''
            out.append('- `%s(%s)`' % (n.name, ast.unparse(n.args)) + (' — ' + first if first else ''))
open(os.path.join(ROOT, 'API.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n'); print('API.md', len(out), 'righe')
