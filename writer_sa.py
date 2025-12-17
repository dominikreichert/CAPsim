####
#
# CAPsim
# Export Module for Scenario-Specific Sensitivity Analysis Results
# 
# AUTHOR: Dominik Reichert
#         Technical University of Munich
#         (dominik.reichert@tum.de)
#  
# VERSION: 1.0.0
#
# LICENSE: Copyright 2025 Dominik Reichert
#  
####



import pandas as pd
from openpyxl import load_workbook
import os



def export_sa_data(export_sa_path, export_sa_tmp_path, s, sa_results, tmp_tornado_1, tmp_tornado_2, results_range, start_year, end_year, set_years, target_year, plotter_end_year):

    # Export SA results:

    with pd.ExcelWriter(f'{export_sa_path}sa_results_plus.xlsx', engine='xlsxwriter', engine_kwargs={'options': {'strings_to_numbers': False}}) as writer:
        for i, data in enumerate(sa_results[s][0]):
            df = data.reset_index(drop=True)
            df.insert(0, 'year', list(set_years))
            df.to_excel(writer, sheet_name=sa_results[s][2][i][:31], index=False)

    with pd.ExcelWriter(f'{export_sa_path}sa_results_minus.xlsx', engine='xlsxwriter', engine_kwargs={'options': {'strings_to_numbers': False}}) as writer:
        for i, data in enumerate(sa_results[s][1]):
            df = data.reset_index(drop=True)
            df.insert(0, 'year', list(set_years))
            df.to_excel(writer, sheet_name=sa_results[s][2][i][:31], index=False)

    # Export SA tmp data (only DataFrames, skip scalars for speed):

    for param_name, values_list in sa_results[s][3].items():
        fname = f'{export_sa_tmp_path}sa_tmp_plus_{param_name}.xlsx'
        with pd.ExcelWriter(fname, engine='xlsxwriter') as writer:
            for element_name, data in zip(sa_results[s][5], values_list):
                if isinstance(data, pd.DataFrame):
                    data.to_excel(writer, sheet_name=element_name[:30], index=True)

    for param_name, values_list in sa_results[s][4].items():
        fname = f'{export_sa_tmp_path}sa_tmp_minus_{param_name}.xlsx'
        with pd.ExcelWriter(fname, engine='xlsxwriter') as writer:
            for element_name, data in zip(sa_results[s][5], values_list):
                if isinstance(data, pd.DataFrame):
                    data.to_excel(writer, sheet_name=element_name[:30], index=True)

    # Export SA tornado data:

    fname = f'{export_sa_path}sa_tornado_{target_year}_data.xlsx'
    with pd.ExcelWriter(fname, engine='xlsxwriter') as writer:
        for polymer in ['pp', 'pa', 'pc', 'abs', 'total']:
            df_polymer = tmp_tornado_1[tmp_tornado_1['polymer'] == polymer].copy()

            df_polymer = df_polymer.drop('polymer', axis=1)
            df_polymer = df_polymer.set_index('sensitivity')

            df_transposed = df_polymer.T

            df_transposed.to_excel(writer, sheet_name=polymer.upper(), index=True)

    fname = f'{export_sa_path}sa_tornado_{plotter_end_year}_data.xlsx'
    with pd.ExcelWriter(fname, engine='xlsxwriter') as writer:
        for polymer in ['pp', 'pa', 'pc', 'abs', 'total']:
            df_polymer = tmp_tornado_2[tmp_tornado_2['polymer'] == polymer].copy()

            df_polymer = df_polymer.drop('polymer', axis=1)
            df_polymer = df_polymer.set_index('sensitivity')

            df_transposed = df_polymer.T

            df_transposed.to_excel(writer, sheet_name=polymer.upper(), index=True)
    
    # Export SA results range data:

    fname = f'{export_sa_path}sa_results_range.xlsx'
    with pd.ExcelWriter(fname, engine='xlsxwriter') as writer:
        for key, value_dict in results_range.items():
            df = pd.DataFrame(
                {year: [value_dict['min'][i], 
                    value_dict['baseline'][i], 
                    value_dict['max'][i]] 
                for i, year in enumerate(range(start_year, end_year + 1))}
            )
            df.insert(0, '', ['min', 'baseline', 'max'])
            df.to_excel(writer, sheet_name=key, index=False)


    return