# Planning des séniors (médecine interne et polyvalente)

Objectif : m'aider à **vérifier** que le planning respecte les règles, et à le **mettre à jour** (désiderata, congés, remplacements)
sans jamais casser les règles.

## Règles
Toutes les règles du service sont dans @REGLES-PLANNING.md (seul fichier que l'utilisateur modifie pour changer une règle).
Leur version lisible par les scripts est `outils/regles.py` : **la mettre à jour dès que REGLES-PLANNING.md change**
(et ajouter le contrôle correspondant dans `outils/verifier_planning.py` si la règle est nouvelle).

## Fichier de travail
- `Planning seniors - couleurs.xlsx` : version de travail (sans macro, couleurs des médecins, colonne « 3ème 3 » démasquée).
- `Planning seniors.xlsm` : fichier d'origine avec macros. Ne jamais le modifier.
- Les feuilles sont protégées : modifier le planning par les outils GridCraft (MCP `gridcraft` / `gridcraft-live`) ou par script ;
  la feuille à modifier est **Calendrier** (une ligne par jour à partir de la ligne 9).

## Disposition de la feuille Calendrier (à confirmer avec l'utilisateur si doute)
- Colonnes : C = date ; D:G = 3ème étage ; L:Q = 4ème 1 (L:M), 4ème 2 (N:O), 4ème 3 (P:Q) en matin/après-midi ;
  V = nuit, W = grande astreinte WE, X = petite astreinte (doublure), Z = urgences (matin) ;
  AD:AM = internes ; BA:BG = congés ; BH:BN = jours off ; BO:BR = formation ; BW:CD = desiderata de congés.
- Le 3ème étage est en cours de réorganisation (colonnes H:I « 3ème 3 » ajoutées) : demander la disposition exacte avant de modifier.

## Outils (dossier `outils/`, les réutiliser, ne pas refaire de scripts jetables)
- Vérifier : `python outils/verifier_planning.py "Planning seniors - couleurs.xlsx" --md outils/rapport_dernier.md`
- Recolorier une copie : `python outils/colorier_planning.py <source> <copie>`
- Retirer les macros : `python outils/supprimer_macros.py <source.xlsm> <copie.xlsx>`
- Détails et hypothèses d'interprétation : `outils/README.md`

## Méthode de travail
1. **Avant toute modification** : lancer la vérification pour connaître l'état de départ.
2. **Modification** : appliquer uniquement ce que l'utilisateur a demandé ; pour une absence ou un désiderata, proposer d'abord
   le remplaçant et les conséquences (règles touchées, équité, continuité) et attendre son accord.
3. **Après modification** : relancer la vérification et comparer avec l'état de départ (aucune nouvelle violation).
   Ne jamais livrer un planning avec une violation nouvelle sans la signaler.
4. Toujours distinguer `VIOLATION` (règle obligatoire) et `ALERTE` (préférence / non vérifiable) dans les comptes rendus.
5. Travailler sur une copie datée avant un gros remaniement ; ne rien enregistrer sur le fichier de travail sans accord.
6. Les valeurs lues par `verifier_planning.py` sont celles en cache : le classeur doit être enregistré avant la vérification.

## Points ouverts connus
- DEC (Deceuninck) et SHA apparaissent dans le planning mais pas dans l'équipe des règles.
- LEC et MON n'apparaissent pas dans le planning.
- Parité des semaines : le classeur utilise WEEKNUM(date;2) (1er janvier = semaine 1), pas la semaine ISO de la colonne B.
- Colonnes internes vides : les règles liées aux internes ne sont pas vérifiables.
