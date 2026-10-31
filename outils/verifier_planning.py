# -*- coding: utf-8 -*-
"""Vérifie la feuille « Calendrier » de « Planning seniors.xlsm » par rapport aux règles de CLAUDE.md.

Usage :
    python outils/verifier_planning.py "Planning seniors.xlsm" [--debut AAAA-MM-JJ] [--fin AAAA-MM-JJ]
                                       [--parite auto|iso|weeknum] [--md rapport.md] [--max 12]

- Lecture directe du fichier (valeurs en cache), aucune dépendance externe. Enregistrer le classeur dans
  Excel/GridCraft avant de lancer l'outil pour que les valeurs calculées soient à jour.
- Par défaut la période vérifiée va du 1er jour au dernier jour renseigné dans les secteurs.
- Les règles sont dans outils/regles.py (à tenir à jour avec CLAUDE.md).
"""
import argparse, collections, datetime as dt, json, os, re, sys, zipfile
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import regles as R

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
JOURS = ['lun', 'mar', 'mer', 'jeu', 'ven', 'sam', 'dim']
EPOCH = dt.date(1899, 12, 30)


# ----------------------------------------------------------------- lecture du classeur
def col2n(c):
    n = 0
    for ch in c:
        n = n * 26 + ord(ch) - 64
    return n


def n2col(n):
    s = ''
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def cols(a, b=None):
    if isinstance(a, tuple):
        a, b = a
    return [n2col(i) for i in range(col2n(a), col2n(b) + 1)]


def lire_classeur(chemin):
    z = zipfile.ZipFile(chemin)
    ss = []
    if 'xl/sharedStrings.xml' in z.namelist():
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', NS):
            ss.append(''.join(t.text or '' for t in si.iter('{%s}t' % NS['m'])))
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    rels = {r.get('Id'): r.get('Target') for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
    feuilles = {}
    for s in wb.find('m:sheets', NS):
        t = rels[s.get('{%s}id' % NS['r'])].lstrip('/')
        if not t.startswith('xl/'):
            t = 'xl/' + t
        d = {}
        for c in ET.fromstring(z.read(t)).iter('{%s}c' % NS['m']):
            v = c.find('m:v', NS)
            if v is None or v.text is None:
                continue
            ty = c.get('t')
            if ty == 's':
                val = ss[int(v.text)]
            elif ty in ('str', 'b', 'e', 'inlineStr'):
                val = v.text
            else:
                try:
                    val = float(v.text)
                except ValueError:
                    val = v.text
            d[c.get('r')] = val
        feuilles[s.get('name')] = d
    return feuilles


# ----------------------------------------------------------------- modèle
class Planning:
    def __init__(self, chemin, debut=None, fin=None, parite='auto'):
        self.f = lire_classeur(chemin)
        self.cal = self.f['Calendrier']
        self.lignes = {}
        for r in range(9, 400):
            v = self.cal.get(f'{R.COL_DATE}{r}')
            if isinstance(v, float):
                self.lignes[r] = EPOCH + dt.timedelta(days=int(v))
        self.ligne_de = {d: r for r, d in self.lignes.items()}
        self.annee = max(self.lignes.values()).year
        self.feries = self._feries()
        cols_secteur = R.COLS_3EME + [c for p in R.COLS_4EME.values() for c in p]
        remplies = [d for r, d in self.lignes.items() if any(self.v(c, r) for c in cols_secteur)]
        self.debut = debut or min(self.lignes.values())
        self.fin = fin or self._fin_par_defaut(remplies, cols_secteur)
        self.jours = [d for d in sorted(self.ligne_de) if self.debut <= d <= self.fin]
        self.parite_mode = parite
        self.parite_info = ''
        self.meds_connus = set(R.SPECIALITE)

    def _fin_par_defaut(self, remplies, cols_secteur):
        """Dernier jour renseigné ; la dernière semaine est écartée si elle est remplie à moins de 50 %."""
        if not remplies:
            return max(self.lignes.values())
        fin = max(remplies)
        lundi = fin - dt.timedelta(days=fin.weekday())
        cols4 = [c for pr in R.COLS_4EME.values() for c in pr]
        jours = [lundi + dt.timedelta(days=i) for i in range(5)]
        jours = [d for d in jours if d in self.ligne_de and d not in self.feries]
        total = len(jours) * len(cols4)
        remplis = sum(1 for d in jours for c in cols4 if self.v(c, self.ligne_de[d]))
        if total and remplis / total < 0.5:
            fin = lundi - dt.timedelta(days=1)
        return fin

    # -- accès cellules
    def v(self, col, r):
        x = self.cal.get(f'{col}{r}')
        if isinstance(x, str):
            x = x.strip().upper() or None
        return x

    def vs(self, plage, r):
        return {x for x in (self.v(c, r) for c in cols(plage)) if isinstance(x, str)}

    def _feries(self):
        P = self.f.get(R.FERIES_FEUILLE, {})
        out = set()
        for r in R.FERIES_LIGNES:
            x = P.get(f'{R.FERIES_COLONNE}{r}')
            if isinstance(x, float):
                out.add(EPOCH + dt.timedelta(days=int(x)))
        return out

    # -- calendrier
    def ouvre(self, d):          # jour d'hospitalisation (lun-ven non férié)
        return d.weekday() < 5 and d not in self.feries

    def parite(self, d):
        mode = self.parite_mode
        if mode == 'iso':
            w = d.isocalendar()[1]
        else:                    # WEEKNUM(date;2)
            j1 = dt.date(d.year, 1, 1)
            w = ((d - j1).days + j1.weekday()) // 7 + 1
        return 'P' if w % 2 == 0 else 'I'

    def blocs_we(self):
        """Blocs de jours non ouvrés consécutifs (WE + fériés) : liste de listes de dates."""
        blocs, cur = [], []
        d0 = min(self.lignes.values())
        for d in sorted(self.ligne_de):
            if not self.ouvre(d):
                cur.append(d)
            elif cur:
                blocs.append(cur); cur = []
        if cur:
            blocs.append(cur)
        return blocs

    # -- absences
    def regle_jour_off(self, med, d, demi):
        for (jr, par, h) in R.TEMPS_PARTIEL.get(med, []):
            if jr == d.weekday() and (par is None or par == self.parite(d)) and h in ('J', demi):
                return True
        return False

    def repos_post_we(self):
        """{(date, demi_ou_'J'): {med}} d'après W (lundi suivant) et X (mardi après-midi)."""
        rep = collections.defaultdict(set)
        for b in self.blocs_we():
            w = {self.v(R.COL_WE_1, self.ligne_de[d]) for d in b if d in self.ligne_de}
            x = {self.v(R.COL_WE_2, self.ligne_de[d]) for d in b if d in self.ligne_de}
            fin = b[-1]
            j1 = fin + dt.timedelta(days=1)
            while not self.ouvre(j1) and j1 in self.ligne_de:
                j1 += dt.timedelta(days=1)
            for m in w:
                if isinstance(m, str):
                    rep[(j1, 'J')].add(m)
            mardi = fin + dt.timedelta(days=(1 - fin.weekday()) % 7 or 7)
            for m in x:
                if isinstance(m, str):
                    rep[(mardi, 'A')].add(m)
        return rep

    def absences(self, med, d):
        """Raisons d'absence d'un médecin à une date -> {demi: [raisons]} (demi = 'M','A')."""
        r = self.ligne_de.get(d)
        out = {'M': [], 'A': []}
        if r is None:
            return out
        if med in self.vs(R.COLS_CONGES, r):
            for h in out: out[h].append('congé (colonnes Congés)')
        if med in self.vs(R.COLS_JOUR_OFF_CLASSEUR, r):
            for h in out: out[h].append('jour off saisi dans le classeur')
        if med in self.vs(R.COLS_FORMATION, r):
            for h in out: out[h].append('formation')
        for h in out:
            if self.regle_jour_off(med, d, h):
                out[h].append('jour off (CLAUDE.md)')
        for (dd, h), meds in self._repos.items():
            if dd == d and med in meds:
                for hh in (('M', 'A') if h == 'J' else (h,)):
                    out[hh].append('repos après WE (' + ('1ère ligne' if h == 'J' else '2ème ligne') + ')')
        return out

    def preparer(self):
        self._repos = self.repos_post_we()


# ----------------------------------------------------------------- détection de la convention de parité
def choisir_parite(p):
    """Compare les jours off de CLAUDE.md (selon la parité) aux colonnes BH:BN du classeur."""
    meilleur = None
    for mode in ('iso', 'weeknum'):
        p.parite_mode = mode
        ok = ko = 0
        for d in p.jours:
            if d.weekday() >= 5:
                continue
            r = p.ligne_de[d]
            saisis = p.vs(R.COLS_JOUR_OFF_CLASSEUR, r)
            for med, regles in R.TEMPS_PARTIEL.items():
                if not any(par for (_, par, _) in regles):
                    continue
                attendu = p.regle_jour_off(med, d, 'M') and p.regle_jour_off(med, d, 'A')
                if any(j == d.weekday() and par for (j, par, _) in regles):
                    if attendu == (med in saisis):
                        ok += 1
                    else:
                        ko += 1
        if meilleur is None or ok > meilleur[1]:
            meilleur = (mode, ok, ko)
    return meilleur


# ----------------------------------------------------------------- rapport
class Rapport:
    def __init__(self):
        self.regles = collections.OrderedDict()   # titre -> {'niveau':, 'infos':[], 'details':[]}

    def regle(self, titre):
        return self.regles.setdefault(titre, {'details': [], 'infos': []})

    def ajout(self, titre, niveau, date, texte):
        self.regle(titre)['details'].append((niveau, date, texte))

    def info(self, titre, texte):
        self.regle(titre)['infos'].append(texte)


def f(d):
    return f'{JOURS[d.weekday()]} {d.strftime("%d/%m/%Y")}'


# ----------------------------------------------------------------- vérifications
def poste_demi(p, d):
    """{demi: {médecin: [lieux]}} pour secteurs 3ème/4ème et urgences."""
    r = p.ligne_de[d]
    out = {'M': collections.defaultdict(list), 'A': collections.defaultdict(list)}
    for i, c in enumerate(R.COLS_3EME):
        m = p.v(c, r)
        if isinstance(m, str):
            for h in out: out[h][m].append(f'3ème (poste {i + 1})')
    for nom, (cm, ca) in R.COLS_4EME.items():
        for h, c in (('M', cm), ('A', ca)):
            m = p.v(c, r)
            if isinstance(m, str):
                out[h][m].append(nom)
    return out


def verifier(p, rap):
    p.preparer()
    jours_ouvres = [d for d in p.jours if p.ouvre(d)]
    postes = {d: poste_demi(p, d) for d in jours_ouvres}
    urg = {d: p.v(R.COL_URG, p.ligne_de[d]) for d in jours_ouvres}

    # médecins hors liste
    T0 = '0. Équipe : écarts avec la liste de CLAUDE.md'
    vus = collections.Counter()
    for d in p.jours:
        r = p.ligne_de[d]
        for c in (R.COLS_3EME + [x for pr in R.COLS_4EME.values() for x in pr] +
                  [R.COL_NUIT, R.COL_WE_1, R.COL_WE_2, R.COL_URG]):
            m = p.v(c, r)
            if isinstance(m, str) and m not in R.SPECIALITE:
                vus[m] += 1
    rap.regle(T0)
    presents = set(vus) | {m for d in p.jours for c in (R.COLS_3EME + [x for pr in R.COLS_4EME.values() for x in pr] +
                                                      [R.COL_NUIT, R.COL_WE_1, R.COL_WE_2, R.COL_URG])
                           for m in [p.v(c, p.ligne_de[d])] if isinstance(m, str)}
    for m in sorted(set(R.SPECIALITE) - presents):
        rap.ajout(T0, 'ALERTE', None, f"{m} ({R.SPECIALITE[m]}) n'apparaît nulle part (secteurs, urgences, nuits, WE) sur la période")
    for m, n in vus.most_common():
        rap.ajout(T0, 'ALERTE', None, f'{m} apparaît {n} fois mais n\'est pas dans l\'équipe de CLAUDE.md '
                                     f'(spécialité inconnue : exclu des contrôles de spécialité)')

    # 1. remplissage
    T1 = '1. Remplissage des secteurs (matin et après-midi)'
    rap.regle(T1)
    n_internes = {d: len(p.vs(R.COLS_INTERNES, p.ligne_de[d])) for d in jours_ouvres}
    if not any(n_internes.values()):
        rap.info(T1, 'Colonnes internes (AD:AM) vides : règles liées aux internes non vérifiables ; '
                     'organisation « 4 internes » supposée (3 postes séniors au 3ème avec ≥2 présents, 3 secteurs au 4ème).')
    for d in jours_ouvres:
        r = p.ligne_de[d]
        pres3 = [p.v(c, r) for c in R.COLS_3EME if isinstance(p.v(c, r), str)]
        if len(pres3) < 2:
            rap.ajout(T1, 'VIOLATION', d, f'3ème étage : {len(pres3)} sénior(s) présent(s) (<2) {pres3}')
        for nom, (cm, ca) in R.COLS_4EME.items():
            for h, c in (('matin', cm), ('après-midi', ca)):
                if not isinstance(p.v(c, r), str):
                    rap.ajout(T1, 'VIOLATION', d, f'secteur {nom} {h} sans médecin')

    # 2. unicité
    T2 = '2. Unicité (un médecin = un secteur à la fois)'
    rap.regle(T2)
    for d in jours_ouvres:
        for h, nom in (('M', 'matin'), ('A', 'après-midi')):
            for m, lieux in postes[d][h].items():
                if len(lieux) > 1:
                    # le 3ème est un poste "journée" : un même médecin sur 2 postes 3ème / 3ème+4ème = double
                    rap.ajout(T2, 'VIOLATION', d, f'{m} sur {" + ".join(lieux)} le {nom} '
                                                  f'(exception possible si les 2 secteurs ont un interne : non vérifiable)')

    # 3. absences
    T3 = '3. Médecin posté alors qu\'il est absent (congé / formation / jour off / repos après WE)'
    rap.regle(T3)
    for d in jours_ouvres:
        for h, nom in (('M', 'matin'), ('A', 'après-midi')):
            for m, lieux in postes[d][h].items():
                raisons = p.absences(m, d)[h]
                if raisons:
                    rap.ajout(T3, 'VIOLATION', d, f'{m} posté {nom} ({", ".join(lieux)}) mais absent : {", ".join(sorted(set(raisons)))}')
        m = urg[d]
        if isinstance(m, str):
            raisons = p.absences(m, d)['M']
            if raisons:
                rap.ajout(T3, 'VIOLATION', d, f'{m} aux urgences le matin mais absent : {", ".join(sorted(set(raisons)))}')
    for d in p.jours:           # nuits / WE
        r = p.ligne_de[d]
        for lib, c in (('nuit', R.COL_NUIT), ('WE 1ère ligne', R.COL_WE_1), ('WE 2ème ligne', R.COL_WE_2)):
            m = p.v(c, r)
            if isinstance(m, str):
                a = p.absences(m, d)
                raisons = {x for x in a['M'] + a['A'] if x.startswith(('congé', 'formation'))}
                if raisons:
                    rap.ajout(T3, 'VIOLATION', d, f'{m} de garde ({lib}) mais absent : {", ".join(sorted(raisons))}')

    # 3b. cohérence jours off CLAUDE.md vs classeur
    T3b = '3b. Cohérence des jours off : CLAUDE.md vs colonnes du classeur (BH:BN)'
    rap.regle(T3b)
    ecarts = collections.Counter()
    for d in jours_ouvres:
        saisis = p.vs(R.COLS_JOUR_OFF_CLASSEUR, p.ligne_de[d])
        for med in R.TEMPS_PARTIEL:
            attendu = p.regle_jour_off(med, d, 'M') and p.regle_jour_off(med, d, 'A')
            if attendu and med not in saisis:
                ecarts[(med, 'attendu CLAUDE.md, absent du classeur', JOURS[d.weekday()], p.parite(d))] += 1
            if not attendu and med in saisis and not p.regle_jour_off(med, d, 'M'):
                ecarts[(med, 'saisi dans le classeur, absent de CLAUDE.md', JOURS[d.weekday()], p.parite(d))] += 1
    for (med, sens, jr, par), n in sorted(ecarts.items()):
        rap.ajout(T3b, 'ALERTE', None, f'{med} : {sens} — {jr} semaines {"paires" if par == "P" else "impaires"} ({n} fois)')
    rap.info(T3b, p.parite_info)

    # 4. endocrinologues
    T4 = '4. Endocrinologues jamais en secteur ni aux urgences'
    rap.regle(T4)
    for d in jours_ouvres:
        for h in 'MA':
            for m, lieux in postes[d][h].items():
                if m in R.ENDOCRINO:
                    rap.ajout(T4, 'VIOLATION', d, f'{m} en secteur ({", ".join(lieux)})')
        if urg[d] in R.ENDOCRINO:
            rap.ajout(T4, 'VIOLATION', d, f'{urg[d]} aux urgences')

    # 5. urgences
    T5 = '5. Urgences (matin, 1 médecin, hors endocrino, hors secteur/consultation si possible)'
    rap.regle(T5)
    for d in jours_ouvres:
        m = urg[d]
        if not isinstance(m, str):
            rap.ajout(T5, 'VIOLATION', d, 'aucun médecin aux urgences')
            continue
        if m in postes[d]['M']:
            rap.ajout(T5, 'ALERTE', d, f'{m} aux urgences ET en secteur le matin ({", ".join(postes[d]["M"][m])})')
        for (jr, par, h) in R.CONSULTATIONS.get(m, []):
            if jr == d.weekday() and (par is None or par == p.parite(d)) and h in ('J', 'M'):
                rap.ajout(T5, 'ALERTE', d, f'{m} aux urgences mais en consultation le matin')
                break

    # 6. présence de chaque spécialité hors hospitalisation (règle 8)
    T6 = '6. Au moins un médecin de chaque spécialité hors hospitalisation et non absent'
    rap.regle(T6)
    for d in jours_ouvres:
        for h, nom in (('M', 'matin'), ('A', 'après-midi')):
            en_secteur = set(postes[d][h])
            for sp in R.SPECIALITES_A_COUVRIR:
                membres = [m for m, s in R.SPECIALITE.items() if s == sp]
                libres = [m for m in membres if m not in en_secteur and not p.absences(m, d)[h]]
                if not libres:
                    niveau = 'ALERTE' if sp != 'infectiologue' else 'VIOLATION'
                    detail = ', '.join(m + ('(sect.)' if m in en_secteur else '(abs.)') for m in membres)
                    rap.ajout(T6, niveau, d, f'{nom} : aucun {sp} hors hospitalisation ({detail})')

    # 6b. un rhumato dispo le mardi matin
    T6b = '6b. Un rhumatologue disponible le mardi matin (ostéoporose)'
    rap.regle(T6b)
    for d in jours_ouvres:
        if d.weekday() != 1:
            continue
        libres = [m for m in R.RHUMATOS if m not in postes[d]['M'] and urg[d] != m and not p.absences(m, d)['M']]
        if not libres:
            rap.ajout(T6b, 'VIOLATION', d, 'aucun rhumatologue libre le mardi matin')

    # 7. nuits
    T7 = '7. Astreintes de nuit (lun-jeu)'
    rap.regle(T7)
    nuits = {d: p.v(R.COL_NUIT, p.ligne_de[d]) for d in p.jours}
    manquantes = [d for d in p.jours if d.weekday() < 4 and p.ouvre(d) and not isinstance(nuits[d], str)]
    if manquantes:
        par_mois = collections.Counter(d.strftime('%m/%Y') for d in manquantes)
        rap.ajout(T7, 'VIOLATION', manquantes[0],
                  f'{len(manquantes)} nuit(s) lun-jeu sans astreinte, du {f(manquantes[0])} au {f(manquantes[-1])} '
                  f'(par mois : {dict(par_mois)}) — liste complète : ' + ', '.join(d.strftime('%d/%m') for d in manquantes))
    par_semaine = collections.defaultdict(list)
    for d in p.jours:
        if d.weekday() < 4 and p.ouvre(d) and isinstance(nuits[d], str):
            par_semaine[(d.isocalendar()[:2], nuits[d])].append(d)
    for (sem, m), ds in par_semaine.items():
        if len(ds) > 1:
            rap.ajout(T7, 'VIOLATION', ds[0], f'{m} : {len(ds)} nuits la même semaine ({", ".join(f(x) for x in ds)})')
    for b in p.blocs_we():
        ls = [p.ligne_de[d] for d in b if d in p.ligne_de]
        W = {p.v(R.COL_WE_1, r) for r in ls} - {None}
        X = {p.v(R.COL_WE_2, r) for r in ls} - {None}
        j0, jn = b[0], b[-1]
        for med, avant in [(m, R.NUITS_INTERDITES_AVANT_WE_W) for m in W] + [(m, R.NUITS_INTERDITES_AVANT_WE_X) for m in X]:
            for k in avant:                       # jours (lun=0) avant le WE : nuits mer(2)/jeu(3) de la semaine du bloc
                dd = j0 - dt.timedelta(days=(j0.weekday() - k) % 7 or 7) if j0.weekday() > k else None
                if dd and nuits.get(dd) == med:
                    rap.ajout(T7, 'VIOLATION', dd, f'{med} de nuit {f(dd)} avant son WE d\'astreinte ({f(j0)})')
            for k in R.NUITS_INTERDITES_APRES_WE:
                dd = jn + dt.timedelta(days=1 + k)
                if nuits.get(dd) == med:
                    rap.ajout(T7, 'VIOLATION', dd, f'{med} de nuit {f(dd)} juste après son WE d\'astreinte ({f(jn)})')
        # cohérence WE / nuits : nuit du samedi = 2ème ligne, autres nuits du bloc et nuit précédente = 1ère ligne
        for d in b:
            if d not in nuits:
                continue
            attendu = X if d.weekday() == 5 else W
            n = nuits[d]
            if isinstance(n, str) and attendu and n not in attendu:
                rap.ajout(T7, 'ALERTE', d, f'nuit {f(d)} : {n} (attendu {"/".join(sorted(attendu))} selon colonnes WE/Doub)')
        veille = j0 - dt.timedelta(days=1)
        if veille in nuits and W and nuits[veille] not in W and veille >= p.debut:
            rap.ajout(T7, 'ALERTE', veille, f'nuit du vendredi {f(veille)} : {nuits[veille]} (attendu {"/".join(sorted(W))}, grande astreinte)')

    # 8. WE & fériés
    T8 = '8. Astreintes de WE / jours fériés (2 médecins)'
    rap.regle(T8)
    for b in p.blocs_we():
        if b[0] < p.debut or b[-1] > p.fin and b[-1].weekday() != 6:
            pass
        ls = [p.ligne_de[d] for d in b if d in p.ligne_de and p.debut <= d <= p.fin]
        if not ls:
            continue
        W = [p.v(R.COL_WE_1, r) for r in ls]
        X = [p.v(R.COL_WE_2, r) for r in ls]
        if any(not isinstance(m, str) for m in W):
            rap.ajout(T8, 'VIOLATION', b[0], f'grande astreinte (1ère ligne) manquante sur {f(b[0])} → {f(b[-1])}')
        if any(not isinstance(m, str) for m in X):
            rap.ajout(T8, 'VIOLATION', b[0], f'petite astreinte (2ème ligne) manquante sur {f(b[0])} → {f(b[-1])}')
        if len({m for m in W if m}) > 1:
            rap.ajout(T8, 'ALERTE', b[0], f'1ère ligne change au sein du bloc {f(b[0])} → {f(b[-1])} : {sorted({m for m in W if m})}')
        if len({m for m in X if m}) > 1:
            rap.ajout(T8, 'ALERTE', b[0], f'2ème ligne change au sein du bloc {f(b[0])} → {f(b[-1])} : {sorted({m for m in X if m})}')
        if {m for m in W if m} & {m for m in X if m}:
            rap.ajout(T8, 'VIOLATION', b[0], f'même médecin en 1ère et 2ème ligne : {sorted(({m for m in W if m} & {m for m in X if m}))}')

    # 9. 6 jours consécutifs max
    T9 = '9. Maximum 6 jours consécutifs travaillés puis 1 jour de repos'
    rap.regle(T9)
    rap.info(T9, 'Jour travaillé = jour ouvré non absent (congé, formation, jour off, repos après WE) ou jour de WE/férié en astreinte (jour). '
                 'Les nuits ne comptent pas.')
    we_jour = collections.defaultdict(set)
    for d in p.jours:
        if not p.ouvre(d):
            r = p.ligne_de[d]
            for m in (p.v(R.COL_WE_1, r), p.v(R.COL_WE_2, r)):
                if isinstance(m, str):
                    we_jour[d].add(m)
    meds = sorted({m for m in R.SPECIALITE})
    for m in meds:
        run, deb = 0, None
        for d in p.jours:
            if p.ouvre(d):
                a = p.absences(m, d)
                travaille = not (a['M'] and a['A'])
            else:
                travaille = m in we_jour.get(d, set())
            if travaille:
                run += 1
                deb = deb or d
                if run == R.MAX_JOURS_CONSECUTIFS + 1:
                    rap.ajout(T9, 'VIOLATION', d, f'{m} : 7 jours consécutifs travaillés depuis {f(deb)} (sans jour de repos)')
            else:
                run, deb = 0, None

    # 10. continuité des soins
    T10 = '10. Continuité de soins (référent ≥ 6 demi-journées/semaine, 3 semaines idéalement)'
    rap.regle(T10)
    semaines = collections.OrderedDict()
    for d in jours_ouvres:
        semaines.setdefault(d.isocalendar()[:2], []).append(d)
    referents = {}
    sect = [(c,) for c in R.COLS_3EME] + [(nom, cm, ca) for nom, (cm, ca) in R.COLS_4EME.items()]
    for sem, ds in semaines.items():
        complete = len(ds) == 5
        for sc in sect:
            cnt = collections.Counter()
            for d in ds:
                r = p.ligne_de[d]
                if len(sc) == 1:                       # poste du 3ème = journée entière = 2 demi-journées
                    m = p.v(sc[0], r)
                    if isinstance(m, str): cnt[m] += 2
                else:
                    for c in sc[1:]:
                        m = p.v(c, r)
                        if isinstance(m, str): cnt[m] += 1
            nom = sc[0] if len(sc) > 1 else f'3ème poste {sc[0]}'
            if cnt:
                ref, n = cnt.most_common(1)[0]
                referents[(sem, nom)] = ref
                if complete and n < 6:
                    rap.ajout(T10, 'ALERTE', ds[0], f'semaine {sem[1]} {nom} : référent {ref} seulement {n}/10 demi-journées ({dict(cnt)})')
    # durée des séquences par secteur
    for nom in sorted({k[1] for k in referents}):
        seq, prev, n = [], None, 0
        for sem in semaines:
            ref = referents.get((sem, nom))
            if ref == prev and ref:
                n += 1
            else:
                if prev: seq.append((prev, n))
                prev, n = ref, 1
        if prev: seq.append((prev, n))
        courtes = [f'{m} {n} sem.' for m, n in seq[:-1] if n == 1] if len(seq) > 1 else []
        rap.info(T10, f'{nom} : ' + ', '.join(f'{m} {n}s' for m, n in seq))
        if courtes:
            rap.ajout(T10, 'ALERTE', None, f'{nom} : séquences d\'1 seule semaine ({len(courtes)}) — idéal 3, à défaut 2 ou 4')

    # 11. équité / décomptes
    T11 = '11. Équité et décomptes par médecin (période vérifiée)'
    rap.regle(T11)
    demi = collections.Counter(); urgc = collections.Counter(); nuitc = collections.Counter()
    w1 = collections.Counter(); w2 = collections.Counter(); feries_trav = collections.Counter()
    for d in jours_ouvres:
        for h in 'MA':
            for m in postes[d][h]:
                demi[m] += 1
        if isinstance(urg[d], str): urgc[urg[d]] += 1
    for d in p.jours:
        r = p.ligne_de[d]
        if isinstance(nuits[d], str) and d.weekday() < 4 and p.ouvre(d): nuitc[nuits[d]] += 1
    for b in p.blocs_we():
        ls = [p.ligne_de[d] for d in b if d in p.ligne_de and p.debut <= d <= p.fin]
        if not ls: continue
        for m in {p.v(R.COL_WE_1, r) for r in ls} - {None}: w1[m] += 1
        for m in {p.v(R.COL_WE_2, r) for r in ls} - {None}: w2[m] += 1
        nf = sum(1 for d in b if d in p.feries and d.weekday() < 5)
        for m in ({p.v(R.COL_WE_1, r) for r in ls} | {p.v(R.COL_WE_2, r) for r in ls}) - {None}:
            feries_trav[m] += nf
    tous = sorted(set(R.SPECIALITE) | set(demi) | set(w1) | set(w2) | set(nuitc) | set(urgc))
    lignes = [f'{"Méd.":5} {"Spé.":14} {"Jours sect.":>11} {"Sem. hosp.":>10} {"Urgences":>8} {"Nuits":>5} {"WE 1ère":>7} {"WE 2ème":>7} {"Repos WE":>8}']
    for m in tous:
        lignes.append(f'{m:5} {R.SPECIALITE.get(m, "?"):14} {demi[m] / 2:11.1f} {demi[m] / 10:10.1f} {urgc[m]:8d} {nuitc[m]:5d} '
                      f'{w1[m]:7d} {w2[m]:7d} {w1[m] + w2[m] + feries_trav[m]:8d}')
    rap.info(T11, 'Décomptes (« Repos WE » = 1 jour par WE d\'astreinte + 1 par férié travaillé) :\n    ' + '\n    '.join(lignes))
    # écarts
    def spread(cnt, titre, exclure=()):
        vals = {m: cnt[m] for m in tous if m not in exclure}
        if vals and max(vals.values()) - min(vals.values()) > 1:
            bas = [m for m, v in vals.items() if v == min(vals.values())]
            haut = [m for m, v in vals.items() if v == max(vals.values())]
            rap.ajout(T11, 'ALERTE', None, f'{titre} : écart {min(vals.values())}→{max(vals.values())} '
                                           f'(min : {",".join(bas)} ; max : {",".join(haut)})')
    actifs = [m for m in R.SPECIALITE]
    spread(nuitc, 'Nuits d\'astreinte (tous les médecins, même nombre)', exclure=[m for m in tous if m not in actifs])
    we_tot = collections.Counter({m: w1[m] + w2[m] for m in tous})
    spread(we_tot, 'WE d\'astreinte (hors endocrinologues : 1 de moins par an)',
           exclure=[m for m in tous if m not in actifs or m in R.ENDOCRINO])
    norm = {m: demi[m] / 10 for m in actifs if R.CHARGE_HOSPIT.get(m, 1) == 1 and m not in R.ENDOCRINO}
    if norm:
        moy = sum(norm.values()) / len(norm)
        for m, v in sorted(norm.items()):
            if moy and abs(v - moy) > max(1.5, 0.35 * moy):
                rap.ajout(T11, 'ALERTE', None, f'{m} : {v:.1f} semaines de secteur vs moyenne {moy:.1f} (médecins à charge normale)')
    for m in actifs:
        ch = R.CHARGE_HOSPIT.get(m, 1)
        if ch < 1 and norm:
            moy = sum(norm.values()) / len(norm)
            if ch and demi[m] / 10 > ch * moy * 1.5 + 0.5:
                rap.ajout(T11, 'ALERTE', None, f'{m} : {demi[m] / 10:.1f} sem. de secteur, charge attendue ≈ {ch * moy:.1f} (facteur {ch})')
    # CON : périodes de 2 semaines max
    runs, cur = [], 0
    for sem, ds in semaines.items():
        s = sum(1 for d in ds for h in 'MA' if 'CON' in postes[d][h])
        if s >= 4: cur += 1
        else:
            if cur: runs.append(cur)
            cur = 0
    if cur: runs.append(cur)
    if any(x > 2 for x in runs):
        rap.ajout(T11, 'ALERTE', None, f'CON en hospitalisation sur plus de 2 semaines consécutives ({runs})')
    rap.info(T11, 'Équité secteurs avec/sans internes : non vérifiable (colonnes internes vides).' if not any(n_internes.values()) else '')

    # 12. consultations en conflit avec une pose en secteur
    T12 = '12. Médecin en secteur pendant sa demi-journée de consultation (information)'
    rap.regle(T12)
    conflits = collections.Counter(); detail = collections.defaultdict(list)
    for d in jours_ouvres:
        for h in 'MA':
            for m, lieux in postes[d][h].items():
                for (jr, par, hh) in R.CONSULTATIONS.get(m, []):
                    if jr == d.weekday() and (par is None or par == p.parite(d)) and hh in ('J', h):
                        conflits[m] += 1; detail[m].append(f(d) + (' matin' if h == 'M' else ' AM'))
                        break
    for m, n in conflits.most_common():
        rap.ajout(T12, 'ALERTE', None, f'{m} : {n} demi-journées en secteur sur un créneau de consultation (ex. {", ".join(detail[m][:3])})')

    # 13. préférences vacances
    T13 = '13. Préférence : pas d\'hospitalisation la semaine avant / après les vacances'
    rap.regle(T13)
    for m in sorted(R.PAS_HOSPIT_SEMAINE_AVANT_VACANCES | R.PAS_HOSPIT_SEMAINE_APRES_VACANCES):
        jours_conge = [d for d in jours_ouvres if m in p.vs(R.COLS_CONGES, p.ligne_de[d])
                       and (m, 'J') not in [(x, 'J') for x in p._repos.get((d, 'J'), set())]]
        # bloc de congés = ≥3 jours ouvrés consécutifs (les jours isolés sont des repos après WE)
        blocs, cur = [], []
        for d in jours_ouvres:
            if d in jours_conge: cur.append(d)
            elif cur:
                if len(cur) >= 3: blocs.append(cur)
                cur = []
        if len(cur) >= 3: blocs.append(cur)
        for bl in blocs:
            if m in R.PAS_HOSPIT_SEMAINE_AVANT_VACANCES:
                sem = bl[0].isocalendar()[:2]
                prec = [s for s in semaines if s < sem][-1:]
                for s in prec:
                    if sum(1 for d in semaines[s] for h in 'MA' if m in postes[d][h]):
                        rap.ajout(T13, 'ALERTE', semaines[s][0], f'{m} en hospitalisation la semaine avant ses vacances ({f(bl[0])})')
            if m in R.PAS_HOSPIT_SEMAINE_APRES_VACANCES:
                sem = bl[-1].isocalendar()[:2]
                suiv = [s for s in semaines if s > sem][:1]
                for s in suiv:
                    if sum(1 for d in semaines[s] for h in 'MA' if m in postes[d][h]):
                        rap.ajout(T13, 'ALERTE', semaines[s][0], f'{m} en hospitalisation la semaine après ses vacances ({f(bl[-1])})')
    rap.info(T13, 'Vérifié uniquement sur les blocs de ≥3 jours ouvrés consécutifs dans les colonnes Congés (peu de congés saisis à ce jour).')

    # 14. cohérence repos post-WE saisi dans le classeur
    T14 = '14. Repos après WE : colonne Congés du classeur vs 1ère ligne de WE'
    rap.regle(T14)
    for (dd, h), meds in sorted(p._repos.items()):
        if h != 'J' or dd not in p.ligne_de or not (p.debut <= dd <= p.fin):
            continue
        saisis = p.vs(R.COLS_CONGES, p.ligne_de[dd])
        for m in meds:
            if m not in saisis:
                rap.ajout(T14, 'ALERTE', dd, f'{m} (1ère ligne le WE précédent) non saisi en repos {f(dd)} dans les colonnes Congés')


def afficher(p, rap, maxi, md=None):
    ordre = {'VIOLATION': 0, 'ALERTE': 1}
    lignes = []
    lignes.append(f'# Vérification du planning {p.annee}')
    lignes.append(f'Période vérifiée : {f(p.debut)} → {f(p.fin)} ({len(p.jours)} jours). Convention de parité des semaines : {p.parite_mode}.')
    lignes.append('')
    lignes.append('## Synthèse')
    for t, d in rap.regles.items():
        nv = sum(1 for x in d['details'] if x[0] == 'VIOLATION')
        na = sum(1 for x in d['details'] if x[0] == 'ALERTE')
        etat = 'OK' if nv == na == 0 else f'{nv} violation(s), {na} alerte(s)'
        lignes.append(f'- {t} : **{etat}**')
    for t, d in rap.regles.items():
        lignes.append('')
        lignes.append(f'## {t}')
        for i in d['infos']:
            if i:
                lignes.append(f'_{i}_' if '\n' not in i else i)
        det = sorted(d['details'], key=lambda x: (ordre[x[0]], x[1] or dt.date(1900, 1, 1)))
        for k, (niv, date, txt) in enumerate(det):
            if md is None and k >= maxi:
                lignes.append(f'  … {len(det) - maxi} autre(s) (voir --md pour la liste complète)')
                break
            lignes.append(f'- [{niv}] {f(date) + " : " if date else ""}{txt}')
    return '\n'.join(lignes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('fichier')
    ap.add_argument('--debut'); ap.add_argument('--fin')
    ap.add_argument('--parite', default='auto', choices=['auto', 'iso', 'weeknum'])
    ap.add_argument('--md', help='écrit le rapport complet (Markdown) dans ce fichier')
    ap.add_argument('--max', type=int, default=12, help='lignes de détail par règle à l\'écran')
    a = ap.parse_args()
    D = lambda s: dt.date.fromisoformat(s) if s else None
    p = Planning(a.fichier, D(a.debut), D(a.fin), a.parite)
    if a.parite == 'auto':
        mode, ok, ko = choisir_parite(p)
        p.parite_mode = mode
        p.parite_info = (f'Parité auto : la convention « {mode} » rapproche le mieux CLAUDE.md des jours off saisis dans le classeur '
                         f'({ok} concordances / {ko} écarts sur les médecins à alternance paire/impaire).')
    else:
        p.parite_info = f'Parité imposée : {a.parite}.'
    rap = Rapport()
    verifier(p, rap)
    sys.stdout.reconfigure(encoding='utf-8')
    print(afficher(p, rap, a.max))
    if a.md:
        open(a.md, 'w', encoding='utf-8').write(afficher(p, rap, a.max, md=True))
        print(f'\nRapport complet écrit dans {a.md}')


if __name__ == '__main__':
    main()
