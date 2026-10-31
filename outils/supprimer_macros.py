# -*- coding: utf-8 -*-
"""Crée une copie .xlsx sans macro VBA ni bouton (ActiveX / contrôles de formulaire), pour supprimer les avertissements
de sécurité à l'ouverture. Le fichier source n'est pas modifié.

Supprimé : vbaProject.bin, contrôles ActiveX, boutons de formulaire (et leur dessin VML / image), codeName.
Conservé : données, formules, tableaux, mises en forme (dont conditionnelles), protections, formes et images de dessin.

Usage : python outils/supprimer_macros.py "Planning seniors - couleurs.xlsm" ["Planning seniors - couleurs.xlsx"]
"""
import argparse, os, posixpath, re, sys, zipfile
import xml.dom.minidom

CT_SANS_MACRO = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml'
TYPES_A_ELAGUER = ('/control', '/ctrlProp', '/vmlDrawing', '/image', '/oleObject')


def rels_de(partie):
    d, f = posixpath.split(partie)
    return posixpath.join(d, '_rels', f + '.rels')


def cible(partie, target):
    return posixpath.normpath(posixpath.join(posixpath.dirname(partie), target))


def convertir(src, dst):
    zin = zipfile.ZipFile(src)
    noms = zin.namelist()
    contenu = {n: zin.read(n) for n in noms}
    supprimes = {n for n in noms if n == 'xl/vbaProject.bin' or n.startswith(('xl/activeX/', 'xl/ctrlProps/'))
                 or re.match(r'xl/drawings/(_rels/)?vmlDrawing\d+\.vml(\.rels)?$', n)}

    # 1. feuilles : on retire <controls> et <legacyDrawing>, puis les relations devenues inutiles
    for n in [n for n in noms if re.match(r'xl/worksheets/sheet\d+\.xml$', n)]:
        s = contenu[n].decode('utf-8')
        s = re.sub(r'<controls>.*?</controls>', '', s, flags=re.S)
        s = re.sub(r'<legacyDrawing\b[^>]*/>', '', s)
        s = re.sub(r'(<sheetPr\b[^>]*?)\scodeName="[^"]*"', r'\1', s)
        contenu[n] = s.encode('utf-8')
        rn = rels_de(n)
        if rn in contenu:
            r = contenu[rn].decode('utf-8')
            def garder(m):
                typ = re.search(r'Type="([^"]*)"', m.group(0)).group(1)
                rid = re.search(r'Id="([^"]*)"', m.group(0)).group(1)
                if typ.endswith(TYPES_A_ELAGUER) and f'"{rid}"' not in s:
                    return ''
                return m.group(0)
            contenu[rn] = re.sub(r'<Relationship\b[^>]*/>', garder, r).encode('utf-8')

    # 2. classeur : plus de VBA ni de codeName
    r = contenu['xl/_rels/workbook.xml.rels'].decode('utf-8')
    contenu['xl/_rels/workbook.xml.rels'] = re.sub(r'<Relationship\b[^>]*vbaProject[^>]*/>', '', r).encode('utf-8')
    w = contenu['xl/workbook.xml'].decode('utf-8')
    w = re.sub(r'\scodeName="[^"]*"', '', w)
    contenu['xl/workbook.xml'] = w.encode('utf-8')

    # 3. médias devenus orphelins
    cibles = set()
    for n, b in contenu.items():
        if n.endswith('.rels') and n not in supprimes:
            base = posixpath.dirname(posixpath.dirname(n))
            for t, mode in re.findall(r'Target="([^"]*)"(?:\s+TargetMode="(\w+)")?', b.decode('utf-8')):
                if mode != 'External' and not t.startswith(('mailto:', 'http')):
                    cibles.add(posixpath.normpath(posixpath.join(base, t)) if not t.startswith('/') else t.lstrip('/'))
    for n in noms:
        if n.startswith('xl/media/') and n not in cibles:
            supprimes.add(n)

    # 4. [Content_Types].xml
    ct = contenu['[Content_Types].xml'].decode('utf-8')
    ct = ct.replace('application/vnd.ms-excel.sheet.macroEnabled.main+xml', CT_SANS_MACRO)
    def ct_garder(m):
        part = re.search(r'PartName="/([^"]*)"', m.group(0))
        return '' if part and part.group(1) in supprimes else m.group(0)
    ct = re.sub(r'<Override\b[^>]*/>', ct_garder, ct)
    contenu['[Content_Types].xml'] = ct.encode('utf-8')

    # 5. écriture + contrôles d'intégrité
    with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
        for it in zin.infolist():
            if it.filename not in supprimes:
                zout.writestr(it, contenu[it.filename])
    z = zipfile.ZipFile(dst)
    restant = set(z.namelist())
    problemes = []
    for n in restant:
        if n.endswith(('.xml', '.rels', '.vml')):
            try:
                xml.dom.minidom.parseString(z.read(n))
            except Exception as e:
                problemes.append(f'{n} : XML invalide ({e})')
        if n.endswith('.rels'):
            base = posixpath.dirname(posixpath.dirname(n))
            for t, mode in re.findall(r'Target="([^"]*)"(?:\s+TargetMode="(\w+)")?', z.read(n).decode('utf-8')):
                if mode == 'External' or t.startswith(('mailto:', 'http')):
                    continue
                c = t.lstrip('/') if t.startswith('/') else posixpath.normpath(posixpath.join(base, t))
                if c not in restant:
                    problemes.append(f'{n} : cible manquante {c}')
    for n in restant:
        if re.match(r'xl/worksheets/sheet\d+\.xml$', n):
            s = z.read(n).decode('utf-8')
            rels = z.read(rels_de(n)).decode('utf-8') if rels_de(n) in restant else ''
            for rid in set(re.findall(r'r:id="([^"]*)"', s)):
                if f'Id="{rid}"' not in rels:
                    problemes.append(f'{n} : r:id {rid} sans relation')
    return sorted(supprimes), problemes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('source')
    ap.add_argument('copie', nargs='?')
    a = ap.parse_args()
    dst = a.copie or os.path.splitext(a.source)[0] + '.xlsx'
    if os.path.abspath(dst) == os.path.abspath(a.source):
        raise SystemExit('La copie doit avoir un autre nom que la source.')
    supprimes, problemes = convertir(a.source, dst)
    sys.stdout.reconfigure(encoding='utf-8')
    print(f'Copie écrite : {dst}')
    print(f'{len(supprimes)} fichier(s) internes supprimés (VBA, ActiveX, boutons, images de boutons).')
    print('Contrôle d\'intégrité : ' + ('OK' if not problemes else '\n  ' + '\n  '.join(problemes)))


if __name__ == '__main__':
    main()
