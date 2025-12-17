####
#
# CAPsim
# Export Module
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



def export_data(export_path, scenario_id, n_scenarios, set_years, set_vehicles, vehicles_names, registrations, fleet, eol, closedloop):

    if n_scenarios == 1:
        file_name = 'results'
    else:
        file_name = f'{scenario_id}_results'

    columns = ['vehicle'] + [str(year) for year in set_years]


    ### (1) REGISTRATIONS

    sheet_registrations = pd.DataFrame({}, columns=columns)

    sheet_registrations.loc[0, 'vehicle'] = 'Total'

    total = [0 for year in set_years]

    for veh in set_vehicles:
        sheet_registrations.loc[veh, 'vehicle'] = vehicles_names.loc[veh, 'name']

        data = [registrations.loc[(veh, year), 'registrations'] for year in set_years]

        idx = 0

        for year in set_years:
            sheet_registrations.loc[veh, str(year)] = data[idx]

            total[idx] += data[idx]
            idx += 1

    idx = 0

    for year in set_years:
        sheet_registrations.loc[0, str(year)] = total[idx]
        idx += 1


    ### (2) FLEET

    sheet_fleet = pd.DataFrame({}, columns=columns)

    sheet_fleet.loc[0, 'vehicle'] = 'Total'

    total = [0 for year in set_years]

    for veh in set_vehicles:
        sheet_fleet.loc[veh, 'vehicle'] = vehicles_names.loc[veh, 'name']

        data = [fleet.loc[(veh, year), 'stock'] for year in set_years]

        idx = 0

        for year in set_years:
            sheet_fleet.loc[veh, str(year)] = data[idx]

            total[idx] += data[idx]
            idx += 1

    idx = 0

    for year in set_years:
        sheet_fleet.loc[0, str(year)] = total[idx]
        idx += 1


    ### (3) ELVS_EXIT

    sheet_exit = pd.DataFrame({}, columns=columns)

    sheet_exit.loc[0, 'vehicle'] = 'Total'

    total = [0 for year in set_years]

    for veh in set_vehicles:
        sheet_exit.loc[veh, 'vehicle'] = vehicles_names.loc[veh, 'name']

        data = [fleet.loc[(veh, year), 'elvs_exit'] for year in set_years]

        idx = 0

        for year in set_years:
            sheet_exit.loc[veh, str(year)] = data[idx]

            total[idx] += data[idx]
            idx += 1

    idx = 0

    for year in set_years:
        sheet_exit.loc[0, str(year)] = total[idx]
        idx += 1


    ### (4) ELVS_EXPORT

    sheet_export = pd.DataFrame({}, columns=columns)

    sheet_export.loc[0, 'vehicle'] = 'Total'

    total = [0 for year in set_years]

    for veh in set_vehicles:
        sheet_export.loc[veh, 'vehicle'] = vehicles_names.loc[veh, 'name']

        data = [fleet.loc[(veh, year), 'elvs_export'] for year in set_years]

        idx = 0

        for year in set_years:
            sheet_export.loc[veh, str(year)] = data[idx]

            total[idx] += data[idx]
            idx += 1

    idx = 0

    for year in set_years:
        sheet_export.loc[0, str(year)] = total[idx]
        idx += 1


    ### (5) ELVS_UNKNOWN

    sheet_unknown = pd.DataFrame({}, columns=columns)

    sheet_unknown.loc[0, 'vehicle'] = 'Total'

    total = [0 for year in set_years]

    for veh in set_vehicles:
        sheet_unknown.loc[veh, 'vehicle'] = vehicles_names.loc[veh, 'name']

        data = [fleet.loc[(veh, year), 'elvs_unknown'] for year in set_years]

        idx = 0

        for year in set_years:
            sheet_unknown.loc[veh, str(year)] = data[idx]

            total[idx] += data[idx]
            idx += 1

    idx = 0

    for year in set_years:
        sheet_unknown.loc[0, str(year)] = total[idx]
        idx += 1


    ### (6) ELVS_RECYCLING

    sheet_recycling = pd.DataFrame({}, columns=columns)

    sheet_recycling.loc[0, 'vehicle'] = 'Total'

    total = [0 for year in set_years]

    for veh in set_vehicles:
        sheet_recycling.loc[veh, 'vehicle'] = vehicles_names.loc[veh, 'name']

        data = [fleet.loc[(veh, year), 'elvs_recycling'] for year in set_years]

        idx = 0

        for year in set_years:
            sheet_recycling.loc[veh, str(year)] = data[idx]

            total[idx] += data[idx]
            idx += 1

    idx = 0

    for year in set_years:
        sheet_recycling.loc[0, str(year)] = total[idx]
        idx += 1


    ### (7) EOL_INPUT

    columns = ['vehicle', 'plastic'] + [str(year) for year in set_years]

    sheet_rec_input = pd.DataFrame({}, columns=columns)

    row = 0

    for veh in set_vehicles:
        sheet_rec_input.loc[row, 'vehicle'] = vehicles_names.loc[veh, 'name']

        # PP:

        sheet_rec_input.loc[row, 'plastic'] = 'PP'
        data = [eol.loc[(veh, year), 'input_pp'] for year in set_years]

        idx = 0
        for year in set_years:
            sheet_rec_input.loc[row, str(year)] = data[idx]
            idx += 1

        row += 1

        # PA:

        sheet_rec_input.loc[row, 'plastic'] = 'PA'
        data = [eol.loc[(veh, year), 'input_pa'] for year in set_years]

        idx = 0
        for year in set_years:
            sheet_rec_input.loc[row, str(year)] = data[idx]
            idx += 1

        row += 1

        # PC:

        sheet_rec_input.loc[row, 'plastic'] = 'PC'
        data = [eol.loc[(veh, year), 'input_pc'] for year in set_years]

        idx = 0
        for year in set_years:
            sheet_rec_input.loc[row, str(year)] = data[idx]
            idx += 1

        row += 1

        # ABS:

        sheet_rec_input.loc[row, 'plastic'] = 'ABS'
        data = [eol.loc[(veh, year), 'input_abs'] for year in set_years]

        idx = 0
        for year in set_years:
            sheet_rec_input.loc[row, str(year)] = data[idx]
            idx += 1

        row += 1


    ### (8) EOL_DISMANTLING

    sheet_rec_dismantling = pd.DataFrame({}, columns=columns)

    row = 0

    for veh in set_vehicles:
        sheet_rec_dismantling.loc[row, 'vehicle'] = vehicles_names.loc[veh, 'name']

        # PP:
        
        sheet_rec_dismantling.loc[row, 'plastic'] = 'PP'
        data = [eol.loc[(veh, year), 'dismantling_output_pp'] for year in set_years]

        idx = 0
        for year in set_years:
            sheet_rec_dismantling.loc[row, str(year)] = data[idx]
            idx += 1

        row += 1

        # PA:

        sheet_rec_dismantling.loc[row, 'plastic'] = 'PA'
        data = [eol.loc[(veh, year), 'dismantling_output_pa'] for year in set_years]

        idx = 0
        for year in set_years:
            sheet_rec_dismantling.loc[row, str(year)] = data[idx]
            idx += 1

        row += 1

        # PC:

        sheet_rec_dismantling.loc[row, 'plastic'] = 'PC'
        data = [eol.loc[(veh, year), 'dismantling_output_pc'] for year in set_years]

        idx = 0
        for year in set_years:
            sheet_rec_dismantling.loc[row, str(year)] = data[idx]
            idx += 1

        row += 1

        # ABS:

        sheet_rec_dismantling.loc[row, 'plastic'] = 'ABS'
        data = [eol.loc[(veh, year), 'dismantling_output_abs'] for year in set_years]

        idx = 0
        for year in set_years:
            sheet_rec_dismantling.loc[row, str(year)] = data[idx]
            idx += 1
        
        row += 1


    ### (9) EOL_OUTPUT

    sheet_rec_output = pd.DataFrame({}, columns=columns)

    row = 0

    for veh in set_vehicles:
        sheet_rec_output.loc[row, 'vehicle'] = vehicles_names.loc[veh, 'name']

        # PP:

        sheet_rec_output.loc[row, 'plastic'] = 'PP'
        data = [eol.loc[(veh, year), 'recycling_output_pp'] for year in set_years]

        idx = 0
        for year in set_years:
            sheet_rec_output.loc[row, str(year)] = data[idx]
            idx += 1
        
        row += 1

        # PA:

        sheet_rec_output.loc[row, 'plastic'] = 'PA'
        data = [eol.loc[(veh, year), 'recycling_output_pa'] for year in set_years]

        idx = 0
        for year in set_years:
            sheet_rec_output.loc[row, str(year)] = data[idx]
            idx += 1

        row += 1

        # PC:

        sheet_rec_output.loc[row, 'plastic'] = 'PC'
        data = [eol.loc[(veh, year), 'recycling_output_pc'] for year in set_years]

        idx = 0
        for year in set_years:
            sheet_rec_output.loc[row, str(year)] = data[idx]
            idx += 1

        row += 1

        # ABS:

        sheet_rec_output.loc[row, 'plastic'] = 'ABS'
        data = [eol.loc[(veh, year), 'recycling_output_abs'] for year in set_years]

        idx = 0
        for year in set_years:
            sheet_rec_output.loc[row, str(year)] = data[idx]
            idx += 1

        row += 1


    ### (10) CLOSED-LOOP RATES

    columns = [''] + [str(year) for year in set_years]

    sheet_closedloop = pd.DataFrame({}, columns=columns)

    # Total:

    row = 0
    sheet_closedloop.loc[row, ''] = 'Total'
    data = [closedloop.loc[year, 'total'] for year in set_years]

    idx = 0
    for year in set_years:
        sheet_closedloop.loc[row, str(year)] = data[idx]
        idx += 1

    # PP:

    row += 1
    sheet_closedloop.loc[row, ''] = 'PP'
    data = [closedloop.loc[year, 'pp'] for year in set_years]

    idx = 0
    for year in set_years:
        sheet_closedloop.loc[row, str(year)] = data[idx]
        idx += 1

    # PA:

    row += 1
    sheet_closedloop.loc[row, ''] = 'PA'
    data = [closedloop.loc[year, 'pa'] for year in set_years]

    idx = 0
    for year in set_years:
        sheet_closedloop.loc[row, str(year)] = data[idx]
        idx += 1

    # PC:

    row += 1
    sheet_closedloop.loc[row, ''] = 'PC'
    data = [closedloop.loc[year, 'pc'] for year in set_years]

    idx = 0
    for year in set_years:
        sheet_closedloop.loc[row, str(year)] = data[idx]
        idx += 1

    # ABS:

    row += 1
    sheet_closedloop.loc[row, ''] = 'ABS'
    data = [closedloop.loc[year, 'abs'] for year in set_years]

    idx = 0
    for year in set_years:
        sheet_closedloop.loc[row, str(year)] = data[idx]
        idx += 1


    ### (11) EXPORT

    file_name = f'{export_path}{file_name}.xlsx'

    with pd.ExcelWriter(file_name) as writer:
        sheet_closedloop.to_excel(writer, sheet_name='closed-loop-rates', index=False)

        sheet_registrations.to_excel(writer, sheet_name='registrations', index=False)

        sheet_fleet.to_excel(writer, sheet_name='fleet', index=False)

        sheet_exit.to_excel(writer, sheet_name='exits', index=False)

        sheet_export.to_excel(writer, sheet_name='exports', index=False)

        sheet_unknown.to_excel(writer, sheet_name='unknown-whereabouts', index=False)

        sheet_recycling.to_excel(writer, sheet_name='to-recycling', index=False)

        sheet_rec_input.to_excel(writer, sheet_name='recycling-input', index=False)

        sheet_rec_dismantling.to_excel(writer, sheet_name='dismantling', index=False)

        sheet_rec_output.to_excel(writer, sheet_name='recycling-output', index=False)