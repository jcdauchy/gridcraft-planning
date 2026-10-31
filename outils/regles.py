# -*- coding: utf-8 -*-
"""Règles du planning, transcrites depuis CLAUDE.md.

A METTRE A JOUR quand CLAUDE.md change (équipe, temps partiels, consultations...).
Convention : jour 0=lundi ... 4=vendredi ; parité 'P' (paire) / 'I' (impaire) / None (toutes les semaines) ;
demi-journée 'M' (matin) / 'A' (après-midi) / 'J' (journée entière).
"""

# --- Equipe -----------------------------------------------------------------
SPECIALITE = {
    'FOR': 'interniste', 'VIN': 'interniste', 'VAL': 'interniste', 'MEI': 'interniste', 'CAR': 'interniste',
    'LEC': 'polyvalent', 'MON': 'polyvalent', 'CHE': 'polyvalent',
    'CON': 'néphrologue', 'GIE': 'néphrologue',
    'ELZ': 'infectiologue', 'GAR': 'infectiologue', 'BEC': 'infectiologue',
    'CLA': 'rhumatologue', 'COS': 'rhumatologue', 'LAM': 'rhumatologue',
    'VER': 'endocrinologue', 'MAL': 'endocrinologue',
}
SPECIALITES_A_COUVRIR = ['interniste', 'néphrologue', 'infectiologue', 'rhumatologue']  # règle 8
ENDOCRINO = {i for i, s in SPECIALITE.items() if s == 'endocrinologue'}
POLYVALENTS = {i for i, s in SPECIALITE.items() if s == 'polyvalent'}

# Facteur de charge en hospitalisation (1 = normal). Règle 4 (équité) : exceptions.
CHARGE_HOSPIT = {'ELZ': 0.5, 'GAR': 0.5, 'BEC': 0.5, 'CHE': 0.5, 'CON': 0.25, 'VER': 0, 'MAL': 0}

# --- Temps partiel (jours off) ---------------------------------------------
TEMPS_PARTIEL = {
    'FOR': [(2, 'P', 'J'), (3, 'I', 'J')],
    'VIN': [(2, 'I', 'J'), (4, 'P', 'J')],
    'VAL': [(2, 'I', 'J'), (3, 'P', 'J')],
    'MEI': [(3, 'P', 'J'), (4, 'I', 'J')],
    'CAR': [(3, 'I', 'J'), (4, 'P', 'J')],
    'ELZ': [(2, 'I', 'J'), (4, 'P', 'J'), (1, None, 'A')],
    'GAR': [(2, 'P', 'J'), (4, 'I', 'J')],
    'BEC': [(3, None, 'J')],
    'LAM': [(3, None, 'J')],
    'CLA': [(2, None, 'J')],
    'COS': [(4, None, 'J')],
    'CON': [(3, None, 'J'), (4, 'I', 'J')],
    'GIE': [(2, None, 'J')],
    'LEC': [(4, None, 'J')],
    'CHE': [(2, None, 'J')],
}

# --- Consultations ----------------------------------------------------------
CONSULTATIONS = {
    'FOR': [(3, 'P', 'A'), (2, 'I', 'A'), (4, None, 'M')],
    'VIN': [(0, 'P', 'A'), (3, None, 'M'), (2, 'I', 'M')],
    'VAL': [(0, None, 'A'), (2, 'I', 'A'), (3, 'P', 'A'), (4, None, 'A')],
    'MEI': [(2, None, 'J'), (0, None, 'A')],
    'ELZ': [(3, None, 'M'), (2, 'P', 'M'), (4, 'I', 'M')],
    'GAR': [(3, None, 'A'), (2, 'I', 'M'), (4, 'P', 'M')],
    'BEC': [(1, None, 'A'), (2, None, 'M')],
    'LAM': [(0, None, 'A'), (2, None, 'A'), (4, None, 'A'), (2, None, 'M')],
    'CLA': [(1, None, 'A'), (4, None, 'M'), (3, None, 'A')],
    'COS': [(2, None, 'M'), (3, None, 'A'), (1, None, 'A')],
    'CON': [(0, None, 'J'), (1, None, 'J'), (3, None, 'J'), (4, 'P', 'M')],
    'GIE': [(1, None, 'A'), (3, None, 'A')],
}
RHUMATOS = ['CLA', 'COS', 'LAM']   # toujours un rhumato dispo le mardi matin (ostéoporose)

# --- Préférences vacances (règle 9) ----------------------------------------
PAS_HOSPIT_SEMAINE_AVANT_VACANCES = {'FOR', 'GIE', 'VAL'}
PAS_HOSPIT_SEMAINE_APRES_VACANCES = {'CHE', 'LAM', 'CLA'}

# --- Astreintes -------------------------------------------------------------
MAX_JOURS_CONSECUTIFS = 6
NUITS_INTERDITES_AVANT_WE_W = (2, 3)      # nuits mer + jeu avant le WE (grande astreinte)
NUITS_INTERDITES_AVANT_WE_X = (3,)        # nuit jeu avant le WE (petite astreinte ; le ven. est la nuit de la grande astreinte)
NUITS_INTERDITES_APRES_WE = (0, 1)        # nuits lun + mar après le WE
ENDOCRINO_WE_EN_MOINS_PAR_AN = 1

# --- Colonnes de la feuille Calendrier -------------------------------------
COL_DATE, COL_SEMAINE = 'C', 'B'
COLS_3EME = ['D', 'E', 'F']                 # 3 postes séniors au 3ème (journée entière, >=2 présents)
COLS_4EME = {'4ème 1': ('L', 'M'), '4ème 2': ('N', 'O'), '4ème 3': ('P', 'Q')}   # (matin, après-midi)
COL_NUIT, COL_WE_1, COL_WE_2, COL_URG = 'V', 'W', 'X', 'Z'    # W = grande astreinte, X = petite (doublure)
COLS_INTERNES = ('AD', 'AM')
COLS_CONGES = ('BA', 'BG')                  # congés
COLS_JOUR_OFF_CLASSEUR = ('BH', 'BN')       # jours off / temps partiel saisis dans le classeur
COLS_FORMATION = ('BO', 'BR')
COLS_DESIDERATA = ('BW', 'CD')
FERIES_FEUILLE, FERIES_COLONNE, FERIES_LIGNES = 'Paramètres', 'R', range(2, 15)
