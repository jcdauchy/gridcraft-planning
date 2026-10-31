# Outils de vérification du planning

`verifier_planning.py` contrôle la feuille **Calendrier** de `Planning seniors.xlsm` par rapport aux règles de `CLAUDE.md`.

```
python outils/verifier_planning.py "Planning seniors.xlsm" --md outils/rapport_dernier.md
```

Options : `--debut` / `--fin` (AAAA-MM-JJ), `--parite auto|iso|weeknum`, `--max N` (lignes affichées par règle).

- Aucune dépendance : lit directement le fichier (valeurs en cache → enregistrer le classeur avant de lancer).
- Période par défaut : du 1er janvier au dernier jour renseigné (dernière semaine écartée si elle est à moins de 50 % remplie).
- **Règles** : `outils/regles.py` (équipe, jours off, consultations, colonnes). À mettre à jour quand `CLAUDE.md` change.
- Gravité : `VIOLATION` = règle obligatoire non respectée ; `ALERTE` = préférence / à examiner / non vérifiable.

## Hypothèses d'interprétation (à confirmer)
- Colonnes : 3ème = 3 postes séniors D/E/F (journée entière, ≥2 présents) ; 4ème = 3 secteurs matin/après-midi (L:M, N:O, P:Q) ; V nuit, W grande astreinte, X petite astreinte, Z urgences.
- Colonnes internes (AD:AM) vides → organisation « 4 internes » supposée.
- Parité des semaines : le classeur applique pair/impair selon `WEEKNUM(date;2)` (1er janvier = semaine 1), pas selon la semaine ISO affichée en colonne B ; la convention est détectée automatiquement.
- Nuits interdites avant le WE : mer+jeu (grande astreinte), jeu (petite) ; après : lun+mar.
