# Vérification du planning 2027
Période vérifiée : ven 01/01/2027 → dim 04/04/2027 (94 jours). Convention de parité des semaines : weeknum.

## Synthèse
- 0. Équipe : écarts avec la liste de CLAUDE.md : **0 violation(s), 4 alerte(s)**
- 1. Remplissage des secteurs (matin et après-midi) : **7 violation(s), 0 alerte(s)**
- 2. Unicité (un médecin = un secteur à la fois) : **2 violation(s), 0 alerte(s)**
- 3. Médecin posté alors qu'il est absent (congé / formation / jour off / repos après WE) : **9 violation(s), 0 alerte(s)**
- 3b. Cohérence des jours off : CLAUDE.md vs colonnes du classeur (BH:BN) : **0 violation(s), 5 alerte(s)**
- 4. Endocrinologues jamais en secteur ni aux urgences : **OK**
- 5. Urgences (matin, 1 médecin, hors endocrino, hors secteur/consultation si possible) : **0 violation(s), 19 alerte(s)**
- 6. Au moins un médecin de chaque spécialité hors hospitalisation et non absent : **6 violation(s), 68 alerte(s)**
- 6b. Un rhumatologue disponible le mardi matin (ostéoporose) : **OK**
- 7. Astreintes de nuit (lun-jeu) : **2 violation(s), 0 alerte(s)**
- 8. Astreintes de WE / jours fériés (2 médecins) : **3 violation(s), 0 alerte(s)**
- 9. Maximum 6 jours consécutifs travaillés puis 1 jour de repos : **4 violation(s), 0 alerte(s)**
- 10. Continuité de soins (référent ≥ 6 demi-journées/semaine, 3 semaines idéalement) : **0 violation(s), 3 alerte(s)**
- 11. Équité et décomptes par médecin (période vérifiée) : **0 violation(s), 8 alerte(s)**
- 12. Médecin en secteur pendant sa demi-journée de consultation (information) : **0 violation(s), 12 alerte(s)**
- 13. Préférence : pas d'hospitalisation la semaine avant / après les vacances : **OK**
- 14. Repos après WE : colonne Congés du classeur vs 1ère ligne de WE : **OK**

## 0. Équipe : écarts avec la liste de CLAUDE.md
- [ALERTE] LEC (polyvalent) n'apparaît nulle part (secteurs, urgences, nuits, WE) sur la période
- [ALERTE] MON (polyvalent) n'apparaît nulle part (secteurs, urgences, nuits, WE) sur la période
- [ALERTE] DEC apparaît 78 fois mais n'est pas dans l'équipe de CLAUDE.md (spécialité inconnue : exclu des contrôles de spécialité)
- [ALERTE] SHA apparaît 7 fois mais n'est pas dans l'équipe de CLAUDE.md (spécialité inconnue : exclu des contrôles de spécialité)

## 1. Remplissage des secteurs (matin et après-midi)
_Colonnes internes (AD:AM) vides : règles liées aux internes non vérifiables ; organisation « 4 internes » supposée (3 postes séniors au 3ème avec ≥2 présents, 3 secteurs au 4ème)._
- [VIOLATION] mer 13/01/2027 : 3ème étage : 0 sénior(s) présent(s) (<2) []
- [VIOLATION] mer 20/01/2027 : 3ème étage : 1 sénior(s) présent(s) (<2) ['CAR']
- [VIOLATION] jeu 28/01/2027 : 3ème étage : 1 sénior(s) présent(s) (<2) ['GIE']
- [VIOLATION] jeu 18/02/2027 : 3ème étage : 1 sénior(s) présent(s) (<2) ['CAR']
- [VIOLATION] mer 10/03/2027 : 3ème étage : 1 sénior(s) présent(s) (<2) ['BEC']
- [VIOLATION] ven 26/03/2027 : 3ème étage : 1 sénior(s) présent(s) (<2) ['VIN']
- [VIOLATION] ven 02/04/2027 : 3ème étage : 1 sénior(s) présent(s) (<2) ['GAR']

## 2. Unicité (un médecin = un secteur à la fois)
- [VIOLATION] jeu 25/02/2027 : VIN sur 4ème 1 + 4ème 2 le matin (exception possible si les 2 secteurs ont un interne : non vérifiable)
- [VIOLATION] jeu 25/02/2027 : VIN sur 4ème 1 + 4ème 2 le après-midi (exception possible si les 2 secteurs ont un interne : non vérifiable)

## 3. Médecin posté alors qu'il est absent (congé / formation / jour off / repos après WE)
- [VIOLATION] mar 05/01/2027 : ELZ posté après-midi (3ème (poste 3)) mais absent : jour off (CLAUDE.md)
- [VIOLATION] mer 06/01/2027 : MEI posté matin (4ème 2) mais absent : jour off saisi dans le classeur
- [VIOLATION] jeu 07/01/2027 : MEI posté matin (4ème 2) mais absent : jour off (CLAUDE.md)
- [VIOLATION] ven 08/01/2027 : ELZ posté matin (3ème (poste 3)) mais absent : jour off (CLAUDE.md)
- [VIOLATION] ven 08/01/2027 : ELZ posté après-midi (3ème (poste 3)) mais absent : jour off (CLAUDE.md)
- [VIOLATION] mar 12/01/2027 : ELZ posté après-midi (3ème (poste 3)) mais absent : jour off (CLAUDE.md)
- [VIOLATION] mar 02/03/2027 : ELZ posté après-midi (3ème (poste 2)) mais absent : jour off (CLAUDE.md)
- [VIOLATION] mar 09/03/2027 : ELZ posté après-midi (3ème (poste 2)) mais absent : jour off (CLAUDE.md)
- [VIOLATION] mer 31/03/2027 : FOR aux urgences le matin mais absent : jour off (CLAUDE.md), jour off saisi dans le classeur

## 3b. Cohérence des jours off : CLAUDE.md vs colonnes du classeur (BH:BN)
_Parité auto : la convention « weeknum » rapproche le mieux CLAUDE.md des jours off saisis dans le classeur (196 concordances / 5 écarts sur les médecins à alternance paire/impaire)._
- [ALERTE] ELZ : attendu CLAUDE.md, absent du classeur — ven semaines paires (1 fois)
- [ALERTE] LAM : attendu CLAUDE.md, absent du classeur — jeu semaines impaires (6 fois)
- [ALERTE] LAM : attendu CLAUDE.md, absent du classeur — jeu semaines paires (7 fois)
- [ALERTE] MEI : attendu CLAUDE.md, absent du classeur — jeu semaines paires (1 fois)
- [ALERTE] MEI : saisi dans le classeur, absent de CLAUDE.md — mer semaines paires (1 fois)

## 4. Endocrinologues jamais en secteur ni aux urgences

## 5. Urgences (matin, 1 médecin, hors endocrino, hors secteur/consultation si possible)
- [ALERTE] mar 05/01/2027 : MEI aux urgences ET en secteur le matin (4ème 2)
- [ALERTE] mer 06/01/2027 : COS aux urgences mais en consultation le matin
- [ALERTE] jeu 07/01/2027 : CHE aux urgences ET en secteur le matin (4ème 1)
- [ALERTE] mer 20/01/2027 : BEC aux urgences mais en consultation le matin
- [ALERTE] mer 03/02/2027 : VIN aux urgences ET en secteur le matin (4ème 1)
- [ALERTE] ven 05/02/2027 : MEI aux urgences ET en secteur le matin (4ème 1)
- [ALERTE] mer 10/02/2027 : CON aux urgences ET en secteur le matin (4ème 1)
- [ALERTE] jeu 11/02/2027 : CLA aux urgences ET en secteur le matin (4ème 3)
- [ALERTE] mer 17/02/2027 : ELZ aux urgences mais en consultation le matin
- [ALERTE] ven 19/02/2027 : BEC aux urgences ET en secteur le matin (4ème 2)
- [ALERTE] mer 24/02/2027 : BEC aux urgences mais en consultation le matin
- [ALERTE] jeu 25/02/2027 : DEC aux urgences ET en secteur le matin (4ème 3)
- [ALERTE] mer 10/03/2027 : MEI aux urgences mais en consultation le matin
- [ALERTE] mer 17/03/2027 : MEI aux urgences ET en secteur le matin (4ème 1)
- [ALERTE] mer 17/03/2027 : MEI aux urgences mais en consultation le matin
- [ALERTE] jeu 18/03/2027 : ELZ aux urgences mais en consultation le matin
- [ALERTE] mer 24/03/2027 : BEC aux urgences mais en consultation le matin
- [ALERTE] ven 26/03/2027 : GIE aux urgences ET en secteur le matin (4ème 1)
- [ALERTE] jeu 01/04/2027 : DEC aux urgences ET en secteur le matin (4ème 3)

## 6. Au moins un médecin de chaque spécialité hors hospitalisation et non absent
- [VIOLATION] mer 06/01/2027 : matin : aucun infectiologue hors hospitalisation (ELZ(sect.), GAR(abs.), BEC(sect.))
- [VIOLATION] mer 06/01/2027 : après-midi : aucun infectiologue hors hospitalisation (ELZ(sect.), GAR(abs.), BEC(sect.))
- [VIOLATION] ven 12/03/2027 : matin : aucun infectiologue hors hospitalisation (ELZ(sect.), GAR(abs.), BEC(sect.))
- [VIOLATION] ven 12/03/2027 : après-midi : aucun infectiologue hors hospitalisation (ELZ(sect.), GAR(abs.), BEC(sect.))
- [VIOLATION] jeu 25/03/2027 : matin : aucun infectiologue hors hospitalisation (ELZ(sect.), GAR(sect.), BEC(abs.))
- [VIOLATION] jeu 25/03/2027 : après-midi : aucun infectiologue hors hospitalisation (ELZ(sect.), GAR(sect.), BEC(abs.))
- [ALERTE] ven 08/01/2027 : matin : aucun interniste hors hospitalisation (FOR(sect.), VIN(abs.), VAL(sect.), MEI(sect.), CAR(abs.))
- [ALERTE] mer 20/01/2027 : matin : aucun néphrologue hors hospitalisation (CON(abs.), GIE(abs.))
- [ALERTE] mer 20/01/2027 : après-midi : aucun néphrologue hors hospitalisation (CON(abs.), GIE(abs.))
- [ALERTE] jeu 21/01/2027 : matin : aucun néphrologue hors hospitalisation (CON(abs.), GIE(sect.))
- [ALERTE] jeu 21/01/2027 : après-midi : aucun néphrologue hors hospitalisation (CON(abs.), GIE(sect.))
- [ALERTE] ven 22/01/2027 : matin : aucun néphrologue hors hospitalisation (CON(abs.), GIE(sect.))
- [ALERTE] ven 22/01/2027 : après-midi : aucun néphrologue hors hospitalisation (CON(abs.), GIE(sect.))
- [ALERTE] jeu 28/01/2027 : matin : aucun néphrologue hors hospitalisation (CON(abs.), GIE(sect.))
- [ALERTE] jeu 28/01/2027 : après-midi : aucun néphrologue hors hospitalisation (CON(abs.), GIE(sect.))
- [ALERTE] ven 29/01/2027 : matin : aucun néphrologue hors hospitalisation (CON(abs.), GIE(sect.))
- [ALERTE] ven 29/01/2027 : après-midi : aucun néphrologue hors hospitalisation (CON(abs.), GIE(sect.))
- [ALERTE] mer 03/02/2027 : matin : aucun rhumatologue hors hospitalisation (CLA(abs.), COS(sect.), LAM(sect.))
- [ALERTE] mer 03/02/2027 : après-midi : aucun rhumatologue hors hospitalisation (CLA(abs.), COS(sect.), LAM(sect.))
- [ALERTE] jeu 04/02/2027 : matin : aucun néphrologue hors hospitalisation (CON(abs.), GIE(sect.))
- [ALERTE] jeu 04/02/2027 : matin : aucun rhumatologue hors hospitalisation (CLA(sect.), COS(sect.), LAM(abs.))
- [ALERTE] jeu 04/02/2027 : après-midi : aucun néphrologue hors hospitalisation (CON(abs.), GIE(sect.))
- [ALERTE] jeu 04/02/2027 : après-midi : aucun rhumatologue hors hospitalisation (CLA(sect.), COS(sect.), LAM(abs.))
- [ALERTE] mer 10/02/2027 : matin : aucun néphrologue hors hospitalisation (CON(sect.), GIE(abs.))
- [ALERTE] mer 10/02/2027 : matin : aucun rhumatologue hors hospitalisation (CLA(abs.), COS(sect.), LAM(sect.))
- [ALERTE] mer 10/02/2027 : après-midi : aucun néphrologue hors hospitalisation (CON(sect.), GIE(abs.))
- [ALERTE] mer 10/02/2027 : après-midi : aucun rhumatologue hors hospitalisation (CLA(abs.), COS(sect.), LAM(sect.))
- [ALERTE] jeu 11/02/2027 : matin : aucun interniste hors hospitalisation (FOR(abs.), VIN(sect.), VAL(sect.), MEI(sect.), CAR(abs.))
- [ALERTE] jeu 11/02/2027 : matin : aucun rhumatologue hors hospitalisation (CLA(sect.), COS(sect.), LAM(abs.))
- [ALERTE] jeu 11/02/2027 : après-midi : aucun interniste hors hospitalisation (FOR(abs.), VIN(sect.), VAL(sect.), MEI(sect.), CAR(abs.))
- [ALERTE] jeu 11/02/2027 : après-midi : aucun rhumatologue hors hospitalisation (CLA(sect.), COS(sect.), LAM(abs.))
- [ALERTE] ven 12/02/2027 : matin : aucun interniste hors hospitalisation (FOR(sect.), VIN(sect.), VAL(sect.), MEI(abs.), CAR(sect.))
- [ALERTE] ven 12/02/2027 : après-midi : aucun interniste hors hospitalisation (FOR(sect.), VIN(sect.), VAL(sect.), MEI(abs.), CAR(sect.))
- [ALERTE] mar 16/02/2027 : après-midi : aucun néphrologue hors hospitalisation (CON(sect.), GIE(abs.))
- [ALERTE] mer 17/02/2027 : matin : aucun néphrologue hors hospitalisation (CON(sect.), GIE(abs.))
- [ALERTE] mer 17/02/2027 : après-midi : aucun néphrologue hors hospitalisation (CON(sect.), GIE(abs.))
- [ALERTE] jeu 18/02/2027 : matin : aucun néphrologue hors hospitalisation (CON(abs.), GIE(sect.))
- [ALERTE] jeu 18/02/2027 : après-midi : aucun néphrologue hors hospitalisation (CON(abs.), GIE(sect.))
- [ALERTE] mer 24/02/2027 : matin : aucun néphrologue hors hospitalisation (CON(sect.), GIE(abs.))
- [ALERTE] mer 24/02/2027 : après-midi : aucun néphrologue hors hospitalisation (CON(sect.), GIE(abs.))
- [ALERTE] jeu 25/02/2027 : matin : aucun interniste hors hospitalisation (FOR(abs.), VIN(sect.), VAL(sect.), MEI(sect.), CAR(abs.))
- [ALERTE] jeu 25/02/2027 : après-midi : aucun interniste hors hospitalisation (FOR(abs.), VIN(sect.), VAL(sect.), MEI(sect.), CAR(abs.))
- [ALERTE] mar 02/03/2027 : matin : aucun néphrologue hors hospitalisation (CON(sect.), GIE(abs.))
- [ALERTE] mar 02/03/2027 : après-midi : aucun néphrologue hors hospitalisation (CON(sect.), GIE(abs.))
- [ALERTE] mer 03/03/2027 : matin : aucun néphrologue hors hospitalisation (CON(sect.), GIE(abs.))
- [ALERTE] mer 03/03/2027 : après-midi : aucun néphrologue hors hospitalisation (CON(sect.), GIE(abs.))
- [ALERTE] jeu 04/03/2027 : matin : aucun néphrologue hors hospitalisation (CON(abs.), GIE(sect.))
- [ALERTE] jeu 04/03/2027 : après-midi : aucun néphrologue hors hospitalisation (CON(abs.), GIE(sect.))
- [ALERTE] ven 05/03/2027 : matin : aucun rhumatologue hors hospitalisation (CLA(sect.), COS(abs.), LAM(sect.))
- [ALERTE] ven 05/03/2027 : après-midi : aucun rhumatologue hors hospitalisation (CLA(sect.), COS(abs.), LAM(sect.))
- [ALERTE] lun 08/03/2027 : matin : aucun rhumatologue hors hospitalisation (CLA(sect.), COS(abs.), LAM(sect.))
- [ALERTE] lun 08/03/2027 : après-midi : aucun rhumatologue hors hospitalisation (CLA(sect.), COS(abs.), LAM(sect.))
- [ALERTE] mer 10/03/2027 : matin : aucun rhumatologue hors hospitalisation (CLA(abs.), COS(sect.), LAM(sect.))
- [ALERTE] mer 10/03/2027 : après-midi : aucun rhumatologue hors hospitalisation (CLA(abs.), COS(sect.), LAM(sect.))
- [ALERTE] jeu 11/03/2027 : matin : aucun néphrologue hors hospitalisation (CON(abs.), GIE(sect.))
- [ALERTE] jeu 11/03/2027 : après-midi : aucun néphrologue hors hospitalisation (CON(abs.), GIE(sect.))
- [ALERTE] ven 12/03/2027 : matin : aucun néphrologue hors hospitalisation (CON(abs.), GIE(sect.))
- [ALERTE] ven 12/03/2027 : matin : aucun rhumatologue hors hospitalisation (CLA(sect.), COS(abs.), LAM(sect.))
- [ALERTE] ven 12/03/2027 : après-midi : aucun néphrologue hors hospitalisation (CON(abs.), GIE(sect.))
- [ALERTE] ven 12/03/2027 : après-midi : aucun rhumatologue hors hospitalisation (CLA(sect.), COS(abs.), LAM(sect.))
- [ALERTE] jeu 18/03/2027 : matin : aucun néphrologue hors hospitalisation (CON(abs.), GIE(sect.))
- [ALERTE] jeu 18/03/2027 : matin : aucun rhumatologue hors hospitalisation (CLA(sect.), COS(sect.), LAM(abs.))
- [ALERTE] jeu 18/03/2027 : après-midi : aucun néphrologue hors hospitalisation (CON(abs.), GIE(sect.))
- [ALERTE] jeu 18/03/2027 : après-midi : aucun rhumatologue hors hospitalisation (CLA(sect.), COS(sect.), LAM(abs.))
- [ALERTE] ven 19/03/2027 : matin : aucun rhumatologue hors hospitalisation (CLA(sect.), COS(abs.), LAM(sect.))
- [ALERTE] ven 19/03/2027 : après-midi : aucun rhumatologue hors hospitalisation (CLA(sect.), COS(abs.), LAM(sect.))
- [ALERTE] mer 24/03/2027 : matin : aucun interniste hors hospitalisation (FOR(sect.), VIN(abs.), VAL(abs.), MEI(sect.), CAR(sect.))
- [ALERTE] mer 24/03/2027 : après-midi : aucun interniste hors hospitalisation (FOR(sect.), VIN(abs.), VAL(abs.), MEI(sect.), CAR(sect.))
- [ALERTE] ven 26/03/2027 : matin : aucun néphrologue hors hospitalisation (CON(abs.), GIE(sect.))
- [ALERTE] ven 26/03/2027 : après-midi : aucun néphrologue hors hospitalisation (CON(abs.), GIE(sect.))
- [ALERTE] mer 31/03/2027 : matin : aucun interniste hors hospitalisation (FOR(abs.), VIN(sect.), VAL(sect.), MEI(sect.), CAR(sect.))
- [ALERTE] mer 31/03/2027 : après-midi : aucun interniste hors hospitalisation (FOR(abs.), VIN(sect.), VAL(sect.), MEI(sect.), CAR(sect.))
- [ALERTE] jeu 01/04/2027 : matin : aucun néphrologue hors hospitalisation (CON(abs.), GIE(sect.))
- [ALERTE] jeu 01/04/2027 : après-midi : aucun néphrologue hors hospitalisation (CON(abs.), GIE(sect.))

## 6b. Un rhumatologue disponible le mardi matin (ostéoporose)

## 7. Astreintes de nuit (lun-jeu)
- [VIOLATION] mar 19/01/2027 : VIN de nuit mar 19/01/2027 juste après son WE d'astreinte (dim 17/01/2027)
- [VIOLATION] lun 01/02/2027 : 35 nuit(s) lun-jeu sans astreinte, du lun 01/02/2027 au jeu 01/04/2027 (par mois : {'02/2027': 16, '03/2027': 18, '04/2027': 1}) — liste complète : 01/02, 02/02, 03/02, 04/02, 08/02, 09/02, 10/02, 11/02, 15/02, 16/02, 17/02, 18/02, 22/02, 23/02, 24/02, 25/02, 01/03, 02/03, 03/03, 04/03, 08/03, 09/03, 10/03, 11/03, 15/03, 16/03, 17/03, 18/03, 22/03, 23/03, 24/03, 25/03, 30/03, 31/03, 01/04

## 8. Astreintes de WE / jours fériés (2 médecins)
- [VIOLATION] sam 27/03/2027 : grande astreinte (1ère ligne) manquante sur sam 27/03/2027 → lun 29/03/2027
- [VIOLATION] sam 27/03/2027 : petite astreinte (2ème ligne) manquante sur sam 27/03/2027 → lun 29/03/2027
- [VIOLATION] sam 03/04/2027 : petite astreinte (2ème ligne) manquante sur sam 03/04/2027 → dim 04/04/2027

## 9. Maximum 6 jours consécutifs travaillés puis 1 jour de repos
_Jour travaillé = jour ouvré non absent (congé, formation, jour off, repos après WE) ou jour de WE/férié en astreinte (jour). Les nuits ne comptent pas._
- [VIOLATION] mer 20/01/2027 : VIN : 7 jours consécutifs travaillés depuis jeu 14/01/2027 (sans jour de repos)
- [VIOLATION] dim 31/01/2027 : MAL : 7 jours consécutifs travaillés depuis lun 25/01/2027 (sans jour de repos)
- [VIOLATION] dim 07/02/2027 : VER : 7 jours consécutifs travaillés depuis lun 01/02/2027 (sans jour de repos)
- [VIOLATION] dim 14/03/2027 : MAL : 7 jours consécutifs travaillés depuis lun 08/03/2027 (sans jour de repos)

## 10. Continuité de soins (référent ≥ 6 demi-journées/semaine, 3 semaines idéalement)
_3ème poste D : VIN 2s, CAR 6s, CLA 3s, VIN 2s_
_3ème poste E : LAM 1s, CLA 2s, BEC 2s, VAL 3s, ELZ 2s, COS 3s_
_3ème poste F : ELZ 2s, GIE 3s, MEI 4s, BEC 2s, GAR 2s_
_4ème 1 : VAL 3s, VIN 3s, CON 2s, GIE 3s, MEI 2s_
_4ème 2 : MEI 1s, DEC 3s, COS 3s, LAM 3s, CAR 3s_
_4ème 3 : FOR 3s, LAM 3s, DEC 3s, FOR 3s, VAL 1s_
- [ALERTE] 3ème poste E : séquences d'1 seule semaine (1) — idéal 3, à défaut 2 ou 4
- [ALERTE] 4ème 2 : séquences d'1 seule semaine (1) — idéal 3, à défaut 2 ou 4
- [ALERTE] lun 04/01/2027 : semaine 1 4ème 2 : référent MEI seulement 5/10 demi-journées ({'MEI': 5, 'DEC': 5})

## 11. Équité et décomptes par médecin (période vérifiée)
Décomptes (« Repos WE » = 1 jour par WE d'astreinte + 1 par férié travaillé) :
    Méd.  Spé.           Jours sect. Sem. hosp. Urgences Nuits WE 1ère WE 2ème Repos WE
    BEC   infectiologue         18.0        3.6        7     1       0       1        1
    CAR   interniste            34.0        6.8        4     0       1       0        1
    CHE   polyvalent             3.5        0.7        3     0       1       0        1
    CLA   rhumatologue          23.0        4.6        5     1       1       1        2
    CON   néphrologue           11.0        2.2        3     0       0       0        0
    COS   rhumatologue          25.0        5.0        5     1       2       0        2
    DEC   ?                     36.5        7.3        2     0       0       1        1
    ELZ   infectiologue         17.0        3.4        7     1       1       1        3
    FOR   interniste            23.5        4.7        5     0       0       0        0
    GAR   infectiologue          7.0        1.4        1     0       1       0        1
    GIE   néphrologue           26.0        5.2        5     2       1       1        2
    LAM   rhumatologue          29.5        5.9        4     1       1       0        1
    LEC   polyvalent             0.0        0.0        0     0       0       0        0
    MAL   endocrinologue         0.0        0.0        0     2       0       2        2
    MEI   interniste            26.5        5.3        5     2       1       1        3
    MON   polyvalent             0.0        0.0        0     0       0       0        0
    SHA   ?                      0.0        0.0        0     1       0       2        2
    VAL   interniste            30.5        6.1        4     2       1       1        2
    VER   endocrinologue         0.0        0.0        0     1       1       0        1
    VIN   interniste            31.0        6.2        4     1       1       1        2
_Équité secteurs avec/sans internes : non vérifiable (colonnes internes vides)._
- [ALERTE] Nuits d'astreinte (tous les médecins, même nombre) : écart 0→2 (min : CAR,CHE,CON,FOR,GAR,LEC,MON ; max : GIE,MAL,MEI,VAL)
- [ALERTE] WE d'astreinte (hors endocrinologues : 1 de moins par an) : écart 0→2 (min : CON,FOR,LEC,MON ; max : CLA,COS,ELZ,GIE,MEI,VAL,VIN)
- [ALERTE] CAR : 6.8 semaines de secteur vs moyenne 4.5 (médecins à charge normale)
- [ALERTE] LEC : 0.0 semaines de secteur vs moyenne 4.5 (médecins à charge normale)
- [ALERTE] MON : 0.0 semaines de secteur vs moyenne 4.5 (médecins à charge normale)
- [ALERTE] VIN : 6.2 semaines de secteur vs moyenne 4.5 (médecins à charge normale)
- [ALERTE] CON : 2.2 sem. de secteur, charge attendue ≈ 1.1 (facteur 0.25)
- [ALERTE] CON en hospitalisation sur plus de 2 semaines consécutives ([3])

## 12. Médecin en secteur pendant sa demi-journée de consultation (information)
- [ALERTE] LAM : 31 demi-journées en secteur sur un créneau de consultation (ex. lun 04/01/2027 AM, mer 06/01/2027 matin, mer 06/01/2027 AM)
- [ALERTE] COS : 20 demi-journées en secteur sur un créneau de consultation (ex. mer 13/01/2027 matin, mar 02/02/2027 AM, mer 03/02/2027 matin)
- [ALERTE] MEI : 19 demi-journées en secteur sur un créneau de consultation (ex. mer 06/01/2027 matin, lun 08/02/2027 AM, mer 10/02/2027 matin)
- [ALERTE] CLA : 18 demi-journées en secteur sur un créneau de consultation (ex. mar 12/01/2027 AM, jeu 14/01/2027 AM, ven 15/01/2027 matin)
- [ALERTE] VAL : 14 demi-journées en secteur sur un créneau de consultation (ex. lun 04/01/2027 AM, ven 08/01/2027 AM, lun 11/01/2027 AM)
- [ALERTE] FOR : 14 demi-journées en secteur sur un créneau de consultation (ex. jeu 07/01/2027 AM, ven 08/01/2027 matin, mer 13/01/2027 AM)
- [ALERTE] CON : 13 demi-journées en secteur sur un créneau de consultation (ex. lun 04/01/2027 matin, lun 04/01/2027 AM, lun 15/02/2027 matin)
- [ALERTE] GIE : 13 demi-journées en secteur sur un créneau de consultation (ex. mar 19/01/2027 AM, jeu 21/01/2027 AM, mar 26/01/2027 AM)
- [ALERTE] VIN : 12 demi-journées en secteur sur un créneau de consultation (ex. lun 04/01/2027 AM, jeu 07/01/2027 matin, jeu 14/01/2027 matin)
- [ALERTE] ELZ : 9 demi-journées en secteur sur un créneau de consultation (ex. mer 06/01/2027 matin, jeu 07/01/2027 matin, jeu 14/01/2027 matin)
- [ALERTE] BEC : 9 demi-journées en secteur sur un créneau de consultation (ex. mer 06/01/2027 matin, mar 26/01/2027 AM, mer 27/01/2027 matin)
- [ALERTE] GAR : 4 demi-journées en secteur sur un créneau de consultation (ex. mer 24/03/2027 matin, jeu 25/03/2027 AM, jeu 01/04/2027 AM)

## 13. Préférence : pas d'hospitalisation la semaine avant / après les vacances
_Vérifié uniquement sur les blocs de ≥3 jours ouvrés consécutifs dans les colonnes Congés (peu de congés saisis à ce jour)._

## 14. Repos après WE : colonne Congés du classeur vs 1ère ligne de WE