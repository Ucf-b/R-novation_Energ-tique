# Projet Efficacity - Optimisation Rénovation Énergétique

Optimisation multi-objectifs pour la planification de rénovations énergétiques d'un parc de bâtiments tertiaires (2026-2050).

---

## 📁 Structure du projet

```
Code_Projet/
│
├── Jalons 1 & 2/                          # Approches initiales (Jalons 1 et 2)
│   ├── Jalon 1.ipynb                      # Optimisation linéaire de base
│   ├── Jalon 2.ipynb                      # Ajout du graphe de transitions
│   ├── efficacity_data_v1.xlsx            # Dataset initial (sans durées de travaux)
│   └── plan_renovation_solution.xlsx      # Résultats Jalon 2
│
├── Analyse_gain_maximal/                  # Étude du potentiel maximal théorique
│   ├── analyse_gain_maximal.py            # Script Python autonome
│   └── resultats_gain_maximal.xlsx        # Résultats de l'analyse
│
├── Archive Jalon 3 approche alternative/  # Versions obsolètes (archivées)
│   └── Jalon_3_deprecated.ipynb           # Ancienne approche abandonnée
│
├── Jalon_3_Graphe_Temporel.ipynb          # Solution finale (graphe temporel)
├── dataset_efficacity_avec_duree.xlsx     # Dataset complet avec durées de travaux
├── plan_renovation_graphe_temporel.xlsx   # Plan de rénovation optimal (sortie finale)
└── README.md                              # Ce fichier
```

---

## 📄 Description des fichiers

### Notebooks d'optimisation

#### `Jalons 1 & 2/Jalon 1.ipynb`
**Approche** : Optimisation linéaire classique (MILP)

**Principe** :
- Variables binaires `X[b,r,t]` = 1 si rénovation `r` sur bâtiment `b` à l'année `t`
- Contraintes : budget annuel, disponibilité par catégorie, une rénovation max par bâtiment
- Objectif : minimiser les écarts aux objectifs 2030/2040/2050

**Entrées** :
- `efficacity_data_v1.xlsx` : données calibrées + simulations de rénovations

**Sorties** :
- `plan_renovation_solution.xlsx` : planning de rénovations par bâtiment et année

**Limites** :
- Une seule rénovation possible par bâtiment sur toute la période
- Pas de gestion des durées de travaux

---

#### `Jalons 1 & 2/Jalon 2.ipynb`
**Approche** : Graphe de transitions entre rénovations

**Innovation** :
- Construction d'un graphe de compatibilité entre rénovations
- Transitions possibles : `r → r'` si `Travaux(r) ⊆ Travaux(r')`
- Coût de transition : `Coût(r→r') = Coût(r') - Coût(r)`
- Permet plusieurs rénovations successives sur un même bâtiment

**Entrées** :
- `efficacity_data_v1.xlsx`
- Colonnes de travaux (G à N) pour calculer les compatibilités

**Sorties** :
- Planning de rénovations avec transitions progressives

**Limites** :
- Toujours pas de gestion temporelle des travaux

---

#### `Jalon_3_Graphe_Temporel.ipynb` **SOLUTION FINALE**
**Approche** : Graphe temporel spatio-temporel

**Principe** :
- Nœuds : `(r, t)` = état de rénovation `r` au mois `t`
- Arêtes d'attente : `(r, t) → (r, t+1)` (coût = 0)
- Arêtes de transition : `(r, t) → (r', t+d)` où `d` = durée des travaux
- Contraintes budgétaires mensuelles avec acompte initial (20% par défaut)
- Contraintes de disponibilité par catégorie par mois

**Hyperparamètres configurables** (cellule 2) :
```python
acompte = 0.2              # Part d'acompte initial
duree_optimiste = 0        # 0 = durée totale, 1 = durée incrémentale
budget_annuel = 2e6        # Budget max par an
poids_2030/2040/2050       # Pondération des objectifs
sobriete = 0.2             # Taux de sobriété comportementale
```

**Entrées** :
- `dataset_efficacity_avec_duree.xlsx` : inclut les durées de travaux (colonne `temps_de_travaux`)

**Sorties** :
- `plan_renovation_graphe_temporel.xlsx` :
  - Onglet **Plan_Renovation** : calendrier mensuel par bâtiment
  - Onglet **Détail_Transitions** : liste de toutes les transitions
  - Onglet **Résumé_Bâtiment** : consommation avant/après
  - Onglet **Budget_Mensuel** : utilisation du budget mois par mois
  - Onglet **Objectifs** : suivi 2030/2040/2050

---

### Scripts Python

#### `Analyse_gain_maximal/analyse_gain_maximal.py`
**Objectif** : Déterminer le gain maximal théorique atteignable

**Méthode** :
- Pour chaque bâtiment, sélectionne la rénovation avec le gain énergétique maximal
- Calcule la réduction totale maximale possible
- Compare avec les objectifs 2030/2040/2050

**Utilisation** :
```bash
cd Analyse_gain_maximal
python analyse_gain_maximal.py
```

**Entrées** :
- `../dataset_efficacity_avec_duree.xlsx`

**Sorties** :
- Console : résumé de l'analyse avec métriques clés
- `resultats_gain_maximal.xlsx` :
  - Onglet **Résumé** : métriques principales
  - Onglet **Meilleures rénovations** : détail par bâtiment
  - Onglet **Calculateur Sobriété** : tableau Excel interactif
---

### Datasets

#### `efficacity_data_v1.xlsx` (Jalons 1 & 2)
**Contenu** :
- 76 bâtiments (71 rénovables + 5 sans simulations)
- ~2087 scénarios de rénovation simulés

---

#### `dataset_efficacity_avec_duree.xlsx` (Jalon 3)
**Contenu** :
- Identique à `efficacity_data_v1.xlsx` avec ajout :
  - `temps_de_travaux` : durée des travaux en mois (1-24 mois)

**Utilisation** : Dataset complet pour le Jalon 3 et l'analyse gain maximal

---

### Résultats

#### `plan_renovation_solution.xlsx` (sortie Jalon 2)
Planning de rénovations généré par l'optimisation linéaire.

#### `resultats_gain_maximal.xlsx` (sortie Analyse gain maximal)
Analyse théorique du potentiel maximal avec calculateur de sobriété interactif.

#### `plan_renovation_graphe_temporel.xlsx` (sortie Jalon 3)
Plan de rénovation optimal final avec calendrier mensuel détaillé.

---

### Archive

#### `Archive Jalon 3 approche alternative/Jalon_3_deprecated.ipynb`
Version obsolète du Jalon 3. Conservée pour référence historique.

**Raison de l'abandon** : Approche remplacée par le graphe temporel (meilleure gestion de mémoire).

---

## 🔧 Prérequis

### Logiciels
- Python 3.8+
- Jupyter Notebook / JupyterLab
- Gurobi Optimizer 11.0+ avec licence valide

### Packages Python
```
numpy>=1.21.0
pandas>=1.3.0
openpyxl>=3.0.9
gurobipy>=11.0.0
jupyter>=1.0.0
```

### Installation
```bash
pip install numpy pandas openpyxl gurobipy jupyter
```

---

## 🚀 Exécution

### 1. Analyse du gain maximal
```bash
cd Analyse_gain_maximal
python analyse_gain_maximal.py
```

### 2. Optimisation finale (Jalon 3)
```bash
jupyter notebook Jalon_3_Graphe_Temporel.ipynb
# Exécuter toutes les cellules : Cell > Run All
```

### 3. Jalons précédents (référence)
```bash
cd "Jalons 1 & 2"
jupyter notebook "Jalon 1.ipynb"
jupyter notebook "Jalon 2.ipynb"
```

---

## 📝 Notes techniques

### Gestion du code commenté
Le code commenté dans les notebooks (ex: génération Excel) est **intentionnel** :
- Protège les fichiers Excel modifiés manuellement (ajout de graphiques, mise en forme)
- Évite de les réécrire par erreur lors de nouvelles exécutions

### Preprocessing répété
Le préprocessing est volontairement **répété dans chaque notebook** :
- Facilite la compréhension pédagogique
- Permet d'exécuter chaque jalon indépendamment
- Aucun impact sur les performances (exécution unique)

---

## 🔗 Références

- Gurobi Documentation : https://www.gurobi.com/documentation/
- Décret tertiaire : https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000038812251

---

**Dernière mise à jour** : Avril 2026  
**Version** : 3.0 (Graphe Temporel)
