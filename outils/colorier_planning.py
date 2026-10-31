# -*- coding: utf-8 -*-
"""Crée une COPIE du classeur où la couleur de chaque médecin est écrite en dur dans les cellules du Calendrier.

Les couleurs sont lues dans les règles de mise en forme conditionnelle du classeur (formules du type IF(D9="VIN",...)),
donc elles suivent automatiquement les changements de couleur faits dans Excel. Le fichier d'origine n'est jamais modifié ;
macros, protections et mises en forme conditionnelles de la copie sont conservées.

Usage :
    python outils/colorier_planning.py "Planning seniors.xlsm" ["Planning seniors - couleurs.xlsm"] [--feuille Calendrier]
"""
import argparse, os, re, shutil, sys, zipfile
import xml.etree.ElementTree as ET

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}


def col2n(c):
    n = 0
    for ch in c:
        n = n * 26 + ord(ch) - 64
    return n


def chemin_feuille(z, nom):
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    rels = {r.get('Id'): r.get('Target') for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
    for s in wb.find('m:sheets', NS):
        if s.get('name') == nom:
            t = rels[s.get('{%s}id' % NS['r'])].lstrip('/')
            return t if t.startswith('xl/') else 'xl/' + t
    raise SystemExit(f'Feuille introuvable : {nom}')


def couleurs_medecins(sheet_xml, styles_xml):
    """{initiales: (couleur_fond, couleur_police)} d'après les règles IF(X9="ABC", ...) et leur dxf."""
    dxfs = re.findall(r'<dxf>.*?</dxf>|<dxf/>', re.search(r'<dxfs.*?</dxfs>', styles_xml, re.S).group(0), re.S)
    out = {}
    for m in re.finditer(r'<cfRule [^>]*dxfId="(\d+)"[^>]*>\s*<formula>([^<]*)</formula>', sheet_xml):
        f = re.match(r'IF\(\$?[A-Z]+\$?\d+="([^"]+)"', m.group(2).replace('&quot;', '"'))
        if not f:
            continue
        dx = dxfs[int(m.group(1))]
        fond = re.search(r'<fill>.*?<bgColor rgb="(\w{8})"', dx, re.S) or re.search(r'<fill>.*?<fgColor rgb="(\w{8})"', dx, re.S)
        pol = re.search(r'<font>.*?<color rgb="(\w{8})"', dx, re.S)
        if fond:
            out.setdefault(f.group(1).upper(), (fond.group(1), pol.group(1) if pol else 'FF000000'))
    return out


def colorier(src, dst, feuille='Calendrier', premiere=9, derniere=373, col_a='D', col_b='CD'):
    zin = zipfile.ZipFile(src)
    chemin = chemin_feuille(zin, feuille)
    sheet = zin.read(chemin).decode('utf-8')
    styles = zin.read('xl/styles.xml').decode('utf-8')
    ss = []
    for si in ET.fromstring(zin.read('xl/sharedStrings.xml')).findall('m:si', NS):
        ss.append(''.join(t.text or '' for t in si.iter('{%s}t' % NS['m'])))
    palette = couleurs_medecins(sheet, styles)

    # --- styles : nouveaux remplissages et nouveaux xf
    fills_blk = re.search(r'<fills count="(\d+)">(.*?)</fills>', styles, re.S)
    nb_fills = int(fills_blk.group(1))
    xfs_blk = re.search(r'<cellXfs count="(\d+)">(.*?)</cellXfs>', styles, re.S)
    xfs = re.findall(r'<xf\b[^>]*?/>|<xf\b[^>]*?>.*?</xf>', xfs_blk.group(2), re.S)
    assert len(xfs) == int(xfs_blk.group(1)), 'cellXfs non analysable'
    fills_new, fill_id = [], {}
    for ini, (fond, _) in palette.items():
        if fond not in fill_id:
            fill_id[fond] = nb_fills + len(fills_new)
            fills_new.append(f'<fill><patternFill patternType="solid"><fgColor rgb="{fond}"/><bgColor indexed="64"/></patternFill></fill>')
    xf_new, xf_cache = [], {}

    def xf_pour(s, fond):
        cle = (s, fond)
        if cle not in xf_cache:
            xf = xfs[s]
            tete = re.match(r'<xf\b[^>]*?(/?)>', xf).group(0)
            nt = re.sub(r'\sfillId="\d+"', '', tete)
            nt = re.sub(r'\sapplyFill="\d+"', '', nt)
            nt = nt.replace('<xf', f'<xf fillId="{fill_id[fond]}" applyFill="1"', 1)
            xf_cache[cle] = len(xfs) + len(xf_new)
            xf_new.append(xf.replace(tete, nt, 1))
        return xf_cache[cle]

    # --- cellules
    n1, n2 = col2n(col_a), col2n(col_b)
    compte, inconnus = {}, {}

    def cellule(m):
        ref, attrs, corps = m.group(1), m.group(2), m.group(3)
        mm = re.match(r'([A-Z]+)(\d+)$', ref)
        if not (n1 <= col2n(mm.group(1)) <= n2 and premiere <= int(mm.group(2)) <= derniere):
            return m.group(0)
        v = re.search(r'<v>([^<]*)</v>', corps)
        if not v:
            return m.group(0)
        t = re.search(r'\bt="(\w+)"', attrs)
        if t and t.group(1) == 's':
            txt = ss[int(v.group(1))]
        elif t and t.group(1) == 'str':
            txt = v.group(1)
        else:
            return m.group(0)
        ini = txt.strip().upper()
        if ini not in palette:
            if 2 <= len(ini) <= 4 and ini.isalpha():
                inconnus[ini] = inconnus.get(ini, 0) + 1
            return m.group(0)
        s = re.search(r'\bs="(\d+)"', attrs)
        s = int(s.group(1)) if s else 0
        ns = xf_pour(s, palette[ini][0])
        attrs2 = re.sub(r'\bs="\d+"', f's="{ns}"', attrs) if re.search(r'\bs="\d+"', attrs) else attrs + f' s="{ns}"'
        compte[ini] = compte.get(ini, 0) + 1
        return f'<c r="{ref}"{attrs2}>{corps}</c>'

    sheet2 = re.sub(r'<c r="([A-Z]+\d+)"([^>]*?)>(.*?)</c>', cellule, sheet, flags=re.S)

    styles2 = styles.replace(fills_blk.group(0),
                             f'<fills count="{nb_fills + len(fills_new)}">{fills_blk.group(2)}{"".join(fills_new)}</fills>')
    styles2 = styles2.replace(xfs_blk.group(0),
                              f'<cellXfs count="{len(xfs) + len(xf_new)}">{xfs_blk.group(2)}{"".join(xf_new)}</cellXfs>')

    with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
        for it in zin.infolist():
            data = zin.read(it.filename)
            if it.filename == chemin:
                data = sheet2.encode('utf-8')
            elif it.filename == 'xl/styles.xml':
                data = styles2.encode('utf-8')
            zout.writestr(it, data)
    return palette, compte, inconnus


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('source')
    ap.add_argument('copie', nargs='?')
    ap.add_argument('--feuille', default='Calendrier')
    a = ap.parse_args()
    dst = a.copie or os.path.splitext(a.source)[0] + ' - couleurs' + os.path.splitext(a.source)[1]
    if os.path.abspath(dst) == os.path.abspath(a.source):
        raise SystemExit('La copie doit avoir un nom différent du fichier source.')
    palette, compte, inconnus = colorier(a.source, dst, a.feuille)
    sys.stdout.reconfigure(encoding='utf-8')
    print(f'Copie écrite : {dst}')
    print(f'{sum(compte.values())} cellules colorées ({len(compte)} médecins) : ' +
          ', '.join(f'{k} {v}' for k, v in sorted(compte.items())))
    if inconnus:
        print('Initiales sans couleur dans les règles du classeur : ' + ', '.join(f'{k} ({v})' for k, v in inconnus.items()))


if __name__ == '__main__':
    main()
