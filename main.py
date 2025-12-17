####
#
# CAPsim
# Circular Automotive Plastics simulation model for assessing
# the closed-loop recycled content of plastic in new passenger cars
# 
# AUTHOR: Dominik Reichert
#         Technical University of Munich
#         (dominik.reichert@tum.de)
#  
# VERSION: 1.0.0
# 
# PUBLISHED: 12/17/2025
#
# LICENSE: Copyright 2025 Dominik Reichert
#     Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0.
#     Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
####



import pandas as pd
from scipy.stats import weibull_min
import matplotlib.pyplot as plt
from datetime import datetime
import os
import re
import shutil
import math

from reader import import_data
from calculator import *
from analyzer import run_sa
from plotter import plot_data
from plotter_multi import plot_multi_data
from plotter_sa import plot_sa_data
from plotter_sa_multi import plot_sa_multi_data
from writer import export_data
from writer_sa import export_sa_data



#########################################################################

###
###  SETTINGS
###

# Set Weibull parameters:
shape = 3.2  # k
scale = 16.75  # lambda

# Set time span for plotting multi-scenario results:
# (!) years must be consistant with the input data
plotter_start_year = 2025
plotter_end_year = 2050

#  Set highlighted target year in plotted results:
# (!) year must be consistant with the input data
target_year = 2035

# Perform sensitivity analysis?
# (!) This function can lead to a significant increase in computing time.
#     The model calculations can take over 15 minutes per scenario.
perform_sa = True  # [True/False]
sensitivity = 0.2

#########################################################################



print('\n##### CAPsim - Circular Automotive Plastics simulation model #####')
print('Copyright 2025 Dominik Reichert')

plots = []
sa_plots = []
sa_results = []



###
###  IMPORT DATA
###

print('\n>  Looking for input files...')

files = sorted([
    file for file in os.listdir('data/') if file.lower().startswith('data') and file.lower().endswith(('.xls', '.xlsx'))
    ])

if not files:
    raise FileNotFoundError(f"(!) The expected input file 'data.xlsx' was not found in 'data/'.")
    
n_scenarios = len(files)

print(f'   number of input files (scenarios) found: {n_scenarios}')


### IMPORT DATA FROM EXCEL FILE FOR EACH SCENARIO

for s in range(n_scenarios):

    if n_scenarios > 1:
        scenario_id = re.search(r'data_(\d+)\.xlsx$', files[s]).group(1)

        print(f'\n>  Importing data of scenario {scenario_id}...')

    else:
        print('\n>  Importing data...')

    import_file = f"data/{files[s]}"

    scenario_name, start_year, end_year, n_years, n_vehicles, vehicles_names, vehicles_data, cagr, n_init_years, registrations, loss, dismantling, recycling, production, tmp = import_data(import_file)



    ###
    ###  MODELING
    ###

    if n_scenarios > 1:
        print(f'\n>  Start modeling of scenario {scenario_id}...')

    set_years = range(start_year, end_year + 1)
    set_vehicles = range(1, n_vehicles + 1)


    # (1) MODEL VEHICLE REGISTRATIONS

    print('\n>  Modeling vehicle registrations...')

    registrations_origin = registrations.copy()

    registrations = calc_registrations(start_year, end_year, set_vehicles, cagr, n_init_years, registrations)

    tmp['registrations'] = registrations

    print('   modeling future vehicle registrations done.')


    # (2) MODEL VEHICLE FLEET

    print('\n>  Modeling vehicle fleet...')

    fleet_detail, fleet = calc_fleet(start_year, end_year, set_years, set_vehicles, registrations, shape, scale)

    tmp['fleet_detail'] = fleet_detail
    tmp['fleet'] = fleet

    print('   modeling vehicle fleet done.')


    # (3) MODEL END-OF-LIFE VEHICLES
    #
    # (3.1) MODEL FLEET EXITS
    # (3.2) MODEL EXPORTS AND UNKNOWN WHEREABOUTS
    # (3.3) MODEL VEHICLES ENTERING RECYCLING
    
    print('\n>  Modeling ELVs...')

    fleet_detail, fleet = calc_eol(start_year, end_year, set_years, set_vehicles, fleet_detail, fleet, loss)

    tmp['fleet_detail'] = fleet_detail
    tmp['fleet'] = fleet

    print('   modeling ELVs done.')


    # (4) MODEL RECYCLING

    print('\n>  Modeling recycling...')

    eol = calc_recycling(start_year, end_year, set_years, set_vehicles, vehicles_data, fleet_detail, dismantling, recycling)

    tmp['eol'] = eol

    print('   modeling recycling done.')


    ### (5) CALCULATE CLOSED-LOOP RATES

    print('\n>  Modeling closed-loop rates...')

    closedloop = calc_closedloop(set_years, set_vehicles, vehicles_data, registrations, eol, production)

    tmp['closedloop'] = closedloop

    print('   modeling closed-loop rates done.')



    ###
    ###  SENSITIVITY ANALYSIS
    ###

    if perform_sa:

        print('\n>  Performing sensitivity analysis...')

        sa_data_plus, sa_data_minus, sa_titles, sa_tmp_plus, sa_tmp_minus, sa_tmp_elements = run_sa(start_year, end_year, n_years, n_vehicles, vehicles_data, cagr, n_init_years, registrations_origin, loss, dismantling, recycling, production, tmp, set_years, set_vehicles, shape, scale, sensitivity)

        sa_results.append([sa_data_plus, sa_data_minus, sa_titles, sa_tmp_plus, sa_tmp_minus, sa_tmp_elements])

        print('   sensitivity analysis done.')



    ###
    ###  EXPORT RESULTS
    ###

    print('\n>  Export results...')


    # (a) EXPORT SINGLE-SCENARIO RESULTS

    if n_scenarios == 1:

        scenario_id = 1


        # CREATE RESULTS FOLDER AND TMP-FILES

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        export_path_ = 'results/' + timestamp
        os.makedirs(export_path_, exist_ok=True)

        export_path = export_path_ + '/'

        # Copy input file:

        dst = export_path + files[s]
        shutil.copy(import_file, dst)

        # Create SA results folder:

        if perform_sa:
            _path = export_path + 'sensitivity_analysis'
            os.makedirs(_path, exist_ok=True)
            export_sa_path = _path + '/'

        print('   results folder created.')

        # Save tmp files:

        with pd.ExcelWriter(f'{export_path}tmp.xlsx', engine='openpyxl') as writer:
            for sheet_name, df in tmp.items():
                df.to_excel(writer, sheet_name=str(sheet_name))

        print('   tmp files saved.')


        # PLOT RESULTS

        plot_data(export_path, scenario_id, scenario_name, n_scenarios, set_years, set_vehicles, vehicles_names, registrations, cagr, fleet, closedloop, target_year)

        print('   plots created.')


        # PLOT SENSITIVITY ANALYSIS RESULTS

        if perform_sa:

            sa_plot, tmp_tornado_1, tmp_tornado_2, results_range = plot_sa_data(export_sa_path, scenario_id, scenario_name, n_scenarios, start_year, end_year, set_years, plotter_start_year, plotter_end_year, set_vehicles, vehicles_names, registrations, cagr, fleet, closedloop, target_year, sa_results[s-1], sensitivity)

            print('   sensitivity analysis plots created.')


        # EXPORT RESULTS

        export_data(export_path, scenario_id, n_scenarios, set_years, set_vehicles, vehicles_names, registrations, fleet, eol, closedloop)

        print('   results exported.')

    else:

        # (b) EXPORT MULTI-SCENARIO RESULTS

        # CREATE RESULTS FOLDER AND TMP-FILES

        if s == 0:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            export_path_ = 'results/' + timestamp

        export_path_origin = f'{export_path_}/'
        export_path = f'{export_path_}/scenario_{scenario_id}/'
        os.makedirs(export_path, exist_ok=True)

        # Copy input file:

        dst = export_path + files[s]
        shutil.copy(import_file, dst)

        # Create SA results folder:

        if perform_sa:
            _path = export_path + 'sensitivity_analysis'
            os.makedirs(_path, exist_ok=True)
            export_sa_path = _path + '/'

        print('   results folder created.')

        # Save tmp files:

        with pd.ExcelWriter(f'{export_path}{scenario_id}_tmp.xlsx', engine='openpyxl') as writer:
            for sheet_name, df in tmp.items():
                df.to_excel(writer, sheet_name=str(sheet_name))

        print('   tmp files saved.')


        # PLOT SINGLE RESULTS

        plot = plot_data(export_path, scenario_id, scenario_name, n_scenarios, set_years, set_vehicles, vehicles_names, registrations, cagr, fleet, closedloop, target_year)

        plots.append(plot)

        print('   plots created.')


        # PLOT SENSITIVITY ANALYSIS RESULTS

        if perform_sa:

            sa_plot, tmp_tornado_1, tmp_tornado_2, results_range = plot_sa_data(export_sa_path, scenario_id, scenario_name, n_scenarios, start_year, end_year, set_years, plotter_start_year, plotter_end_year, set_vehicles, vehicles_names, registrations, cagr, fleet, closedloop, target_year, sa_results[s], sensitivity)

            sa_plots.append(sa_plot)

            print('   sensitivity analysis plot created.')


        # EXPORT RESULTS

        export_data(export_path, scenario_id, n_scenarios, set_years, set_vehicles, vehicles_names, registrations, fleet, eol, closedloop)

        print('   results exported.')


        # PLOT SCENARIO-COMPARISON RESULTS

        if s + 1 == n_scenarios:
            plot_multi_data(export_path_origin, n_scenarios, plots, plotter_start_year, plotter_end_year)

            if perform_sa:
                plot_sa_multi_data(export_path_origin, n_scenarios, sa_plots, plotter_start_year, plotter_end_year)

        print('   plot for scenario comparison created.')


    # (c) EXPORT SENSITIVITY ANALYSIS RESULTS

    if perform_sa:

        # Create tmp folder and define export paths:

        _path = export_sa_path + 'tmp'
        os.makedirs(_path, exist_ok=True)
        export_sa_tmp_path = _path + '/'

        if n_scenarios == 1:
            _export_sa_path = f'{export_sa_path}'
            _export_sa_tmp_path = f'{export_sa_tmp_path}'
        else:
            _export_sa_path = f'{export_sa_path}{scenario_id}_'
            _export_sa_tmp_path = f'{export_sa_tmp_path}{scenario_id}_'

        # Export SA data and results:

        export_sa_data(_export_sa_path, _export_sa_tmp_path, s, sa_results, tmp_tornado_1, tmp_tornado_2, results_range, start_year, end_year, set_years, target_year, plotter_end_year)

        print('   sensitivity analysis data and results exported.')


    print(f'\n>  Scenario {scenario_id} completed.')


print('\n>  End')