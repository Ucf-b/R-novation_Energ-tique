"""
Analyse du gain maximal théorique atteignable sur le parc de bâtiments.

Ce script calcule la réduction maximale de consommation énergétique en sélectionnant
pour chaque bâtiment la meilleure rénovation possible (celle avec le gain maximal).
"""

import pandas as pd
import numpy as np


def charger_donnees(filepath):
    """Charge et prépare les données du dataset."""
    df = pd.read_excel(filepath)
    
    # Séparer les données calibrated (état initial) et les simulations (rénovations)
    df_calibrated = df[df['id_simulation'].astype(str).str.contains('calibrated', case=False)]
    df_simulations = df[~df['id_simulation'].astype(str).str.contains('calibrated', case=False)]
    
    return df, df_calibrated, df_simulations


def calculer_gain_maximal_par_batiment(df_calibrated, df_simulations):
    """
    Pour chaque bâtiment, trouve la rénovation avec le gain maximal.
    
    Returns:
        DataFrame avec les meilleures rénovations par bâtiment
    """
    building_names = df_calibrated[df_calibrated['building_name'].isin(df_simulations['building_name'].unique())]['building_name'].unique()
    
    resultats = []
    
    for building in building_names:
        # Toutes les simulations pour ce bâtiment
        sims = df_simulations[df_simulations['building_name'] == building]
        
        if len(sims) > 0:
            # Trouver la simulation avec le gain maximal
            max_idx = sims['gains_totaux_mwh_an'].idxmax()
            max_sim = sims.loc[max_idx]
            
            resultats.append({
                'building': building,
                'best_simulation': max_sim['id_simulation'],
                'max_gain_mwh_an': max_sim['gains_totaux_mwh_an'],
                'conso_apres_mwh_an': max_sim['conso_total_mwh_an'],
                'cost_euros': max_sim['cout_investissement_euros'],
                'duration_months': max_sim['temps_de_travaux'],
                'co2_reduction_tonnes': max_sim['gains_emm_co2_total_tonnes']
            })
    
    return pd.DataFrame(resultats)


def analyser_gain_maximal(filepath, sobriete=0.10):
    """
    Analyse complète du gain maximal théorique.
    
    Args:
        filepath: Chemin vers le fichier Excel
        sobriete: Taux de sobriété comportementale (default: 10%)
    
    Returns:
        dict: Résultats de l'analyse
    """
    print("="*80)
    print("ANALYSE DU GAIN MAXIMAL THÉORIQUE")
    print("="*80)
    
    # Charger les données
    print("\n1. Chargement des données...")
    df, df_calibrated, df_simulations = charger_donnees(filepath)
    
    # Calcul de la consommation initiale
    building_names_with_sims = df_simulations['building_name'].unique()
    df_calibrated_filtered = df_calibrated[df_calibrated['building_name'].isin(building_names_with_sims)]
    conso_initiale = df_calibrated_filtered['conso_total_mwh_an'].sum()
    
    print(f"   Bâtiments: {len(df_calibrated)}")
    print(f"   Consommation initiale: {conso_initiale:,.2f} MWh/an")
    
    # Trouver les meilleures rénovations
    print("\n2. Calcul des meilleures rénovations par bâtiment...")
    df_max = calculer_gain_maximal_par_batiment(df_calibrated, df_simulations)
    
    # Statistiques globales
    total_max_gain = df_max['max_gain_mwh_an'].sum()
    total_cost = df_max['cost_euros'].sum()
    conso_finale = df_max['conso_apres_mwh_an'].sum()
    
    # Réductions
    reduction_absolue = total_max_gain
    reduction_pct_brut = (reduction_absolue / conso_initiale) * 100
    reduction_pct_avec_sobriete = sobriete * 100 + (1 - sobriete) * reduction_pct_brut
    
    print("\n" + "="*80)
    print("RÉSULTATS PRINCIPAUX")
    print("="*80)
    
    print(f"\nGain maximal total: {total_max_gain:,.2f} MWh/an")
    print(f"Coût total nécessaire: {total_cost:,.2f} € ({total_cost/1e6:.2f} M€)")
    print(f"Coût par MWh/an économisé: {total_cost/total_max_gain:,.2f} €/(MWh/an)")
    
    print(f"\nConsommation finale minimale: {conso_finale:,.2f} MWh/an")
    print(f"\nRéduction maximale (sans sobriété): {reduction_pct_brut:.2f}%")
    print(f"Réduction maximale (avec sobriété {sobriete*100:.0f}%): {reduction_pct_avec_sobriete:.2f}%")
    
    # Comparaison avec les objectifs
    print("\n" + "="*80)
    print("COMPARAISON AVEC LES OBJECTIFS DÉCENNAUX")
    print("="*80)
    
    objectifs = [
        (2030, 40.0),
        (2040, 50.0),
        (2050, 60.0)
    ]
    
    print(f"\n{'Année':<10} {'Objectif':<12} {'Max Possible':<15} {'Écart':<12} {'Atteignable?'}")
    print("-" * 80)
    
    for annee, objectif_pct in objectifs:
        ecart = reduction_pct_avec_sobriete - objectif_pct
        atteignable = "✓ OUI" if ecart >= 0 else "✗ NON"
        
        print(f"{annee:<10} {objectif_pct:>6.1f}%       {reduction_pct_avec_sobriete:>6.2f}%          "
              f"{ecart:>+6.2f}%       {atteignable}")
    
    # Statistiques par bâtiment
    print("\n" + "="*80)
    print("STATISTIQUES PAR BÂTIMENT")
    print("="*80)
    
    print(f"\nGain moyen: {df_max['max_gain_mwh_an'].mean():,.2f} MWh/an")
    print(f"Gain médian: {df_max['max_gain_mwh_an'].median():,.2f} MWh/an")
    print(f"Gain min/max: {df_max['max_gain_mwh_an'].min():,.2f} / "
          f"{df_max['max_gain_mwh_an'].max():,.2f} MWh/an")
    
    print(f"\nCoût moyen: {df_max['cost_euros'].mean():,.2f} €")
    print(f"Durée moyenne: {df_max['duration_months'].mean():.1f} mois")
    print(f"Durée maximale: {df_max['duration_months'].max():.0f} mois")
    
    # Top 10 bâtiments
    print("\n" + "="*80)
    print("TOP 10 BÂTIMENTS - PLUS GROS POTENTIEL DE GAIN")
    print("="*80)
    
    top10 = df_max.nlargest(10, 'max_gain_mwh_an')
    
    print(f"\n{'Rang':<6} {'Bâtiment':<40} {'Gain (MWh/an)':<15} {'Coût (k€)':<12} {'Durée (mois)'}")
    print("-" * 80)
    
    for idx, (_, row) in enumerate(top10.iterrows(), 1):
        print(f"{idx:<6} {row['building'][:38]:<40} {row['max_gain_mwh_an']:>10.2f}     "
              f"{row['cost_euros']/1000:>8.0f}       {row['duration_months']:>4.0f}")
    
    # Analyse détaillée de l'écart avec 2050
    print("\n" + "="*80)
    print("ANALYSE DÉTAILLÉE - OBJECTIF 2050")
    print("="*80)
    
    objectif_2050 = 60.0
    reduction_necessaire_reno = (objectif_2050 - sobriete * 100) / (1 - sobriete)
    ecart_2050 = reduction_pct_brut - reduction_necessaire_reno
    
    print(f"\nPour atteindre {objectif_2050:.0f}% en 2050:")
    print(f"  Sobriété acquise: {sobriete*100:.0f}%")
    print(f"  Rénovations nécessaires: {reduction_necessaire_reno:.2f}% de la conso (après sobriété)")
    print(f"  Rénovations max possibles: {reduction_pct_brut:.2f}%")
    print(f"  Écart: {ecart_2050:.2f} points de %")
    
    if ecart_2050 < 0:
        print(f"\n⚠️  CONCLUSION: L'objectif 2050 est IMPOSSIBLE à atteindre.")
        print(f"     Il manque {-ecart_2050:.2f} points de % même en réalisant")
        print(f"     TOUTES les meilleures rénovations possibles.")
    else:
        print(f"\n✓  CONCLUSION: L'objectif 2050 est atteignable.")
    
    # Retourner les résultats
    return {
        'df_max': df_max,
        'conso_initiale': conso_initiale,
        'total_max_gain': total_max_gain,
        'total_cost': total_cost,
        'conso_finale': conso_finale,
        'reduction_pct_brut': reduction_pct_brut,
        'reduction_pct_avec_sobriete': reduction_pct_avec_sobriete,
        'sobriete': sobriete
    }


def exporter_resultats(resultats, output_path='Analyse_gain_maximal/resultats_gain_maximal.xlsx'):
    """
    Exporte les résultats dans un fichier Excel.
    """
    df_max = resultats['df_max']
    
    # Ajouter des colonnes calculées
    df_export = df_max.copy()
    df_export['roi_euros_per_mwh_an'] = df_export['cost_euros'] / df_export['max_gain_mwh_an']
    
    # Trier par gain décroissant
    df_export = df_export.sort_values('max_gain_mwh_an', ascending=False)
    
    # Créer un résumé
    resume = pd.DataFrame([{
        'Métrique': 'Consommation initiale (MWh/an)',
        'Valeur': resultats['conso_initiale']
    }, {
        'Métrique': 'Gain maximal total (MWh/an)',
        'Valeur': resultats['total_max_gain']
    }, {
        'Métrique': 'Consommation finale minimale (MWh/an)',
        'Valeur': resultats['conso_finale']
    }, {
        'Métrique': 'Coût total nécessaire (€)',
        'Valeur': resultats['total_cost']
    }, {
        'Métrique': 'Réduction maximale sans sobriété (%)',
        'Valeur': resultats['reduction_pct_brut']
    }, {
        'Métrique': 'Réduction maximale avec sobriété (%)',
        'Valeur': resultats['reduction_pct_avec_sobriete']
    }])
    
    # AJOUTER CETTE PARTIE - Feuille de calcul paramétrable
    calcul_sobriete = pd.DataFrame([
    ['PARAMÈTRE MODIFIABLE', ''],
    ['Sobriété (%)', resultats['sobriete'] * 100],
    ['', ''],
    ['CONSTANTES', ''],
    ['Consommation initiale (MWh/an)', resultats['conso_initiale']],
    ['Gain maximal rénovations (MWh/an)', resultats['total_max_gain']],
    ['', ''],
    ['FORMULES (NE PAS MODIFIER)', ''],
    ['Consommation après rénovations (MWh/an)', f'=B5-B6'],
    ['Consommation après rénovations + sobriété (MWh/an)', f'=B9*(1-B2/100)'],
    ['Réduction totale (MWh/an)', f'=B5-B10'],
    ['Réduction totale (%)', f'=B11/B5*100'],
    ['', ''],
    ['OBJECTIFS 2030/2040/2050', 'Atteint?'],
    ['Objectif 2030: 40%', f'=IF(B12>=40,"✓ OUI","✗ NON")'],
    ['Objectif 2040: 50%', f'=IF(B12>=50,"✓ OUI","✗ NON")'],
    ['Objectif 2050: 60%', f'=IF(B12>=60,"✓ OUI","✗ NON")']
    ], columns=['Description', 'Valeur'])
    
    # Export Excel
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        resume.to_excel(writer, sheet_name='Résumé', index=False)
        df_export.to_excel(writer, sheet_name='Meilleures rénovations', index=False)
        calcul_sobriete.to_excel(writer, sheet_name='Calculateur Sobriété', index=False, header=False)
        
        # Formater la feuille Calculateur
        worksheet = writer.sheets['Calculateur Sobriété']
        worksheet.column_dimensions['A'].width = 45
        worksheet.column_dimensions['B'].width = 20
        
        # Mettre en évidence la cellule modifiable
        from openpyxl.styles import PatternFill, Font
        yellow_fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
        bold_font = Font(bold=True)
        
        worksheet['B2'].fill = yellow_fill
        worksheet['B2'].font = bold_font
        worksheet['A2'].font = bold_font
    
    print(f"\n✓ Résultats exportés dans: {output_path}")
    print(f"  → Modifiez la cellule B2 dans l'onglet 'Calculateur Sobriété' pour tester différents taux")


def main():
    """Fonction principale."""
    # Chemin vers le fichier de données
    filepath = './dataset_efficacity_avec_duree.xlsx'
    
    # Analyse
    resultats = analyser_gain_maximal(filepath, sobriete=0.10)
    
    # Export
    exporter_resultats(resultats)
    
    print("\n" + "="*80)
    print("ANALYSE TERMINÉE")
    print("="*80)


if __name__ == '__main__':
    main()
