####
#
# CAPsim
# Import Module
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



def import_data(file_path):

    tmp = {}


    ### (1) IMPORT 'Vehicles' DATA
    
    # Import vehicle model data from sheet 'Vehicles' and basic scenario information (scenario name, start year, end year, number of vehicle models, vehicle model names)
    
    # vehicles_names[id] = {name}
    # vehicles_data[id, year] = {total_mass, plastic_content, pp_content, pa_content, pc_content, abs_content}
    
    try:
        df = pd.read_excel(file_path, sheet_name='Vehicles')

        scenario_name = str(df.iat[3, 2])
        start_year = int(df.iat[5, 2])
        end_year = int(df.iat[6, 2])
        n_years = int(end_year - start_year + 1)
        n_vehicles = int(df.iat[8, 2])

        print(f'   start year: {start_year}')
        print(f'   end year: {end_year}')
        print(f'   number of vehicles: {n_vehicles}')

        vehicles_names = pd.DataFrame({
            'id': range(1, n_vehicles + 1)})
        vehicles_names.set_index('id', inplace=True)


        vehicles_data = pd.DataFrame({
            'id': [i for i in range(1, n_vehicles + 1) for j in range(start_year, end_year + 1)],
            'year': [j for i in range(1, n_vehicles + 1) for j in range(start_year, end_year + 1)]})
        vehicles_data.set_index(['id', 'year'], inplace=True)

        row = 15

        for i in range(1, n_vehicles + 1):
            for j in range(start_year, end_year + 1):
                vehicles_names.loc[i, 'name'] = df.iat[11, 1+i]

                vehicles_data.loc[(i, j), 'total_mass'] = df.iat[row, j-start_year+2]  # [kg]
                vehicles_data.loc[(i, j), 'plastic_content'] = df.iat[row+1, j-start_year+2]  # [%]
                vehicles_data.loc[(i, j), 'pp_content'] = df.iat[row+2, j-start_year+2]  # [%]
                vehicles_data.loc[(i, j), 'pa_content'] = df.iat[row+3, j-start_year+2]  # [%]
                vehicles_data.loc[(i, j), 'pc_content'] = df.iat[row+4, j-start_year+2]  # [%]
                vehicles_data.loc[(i, j), 'abs_content'] = df.iat[row+5, j-start_year+2]  # [%]

            row += 8

    except FileNotFoundError:
        raise Exception(f"ERROR: The input file '{file_path}' was not found.")
    
    except Exception as e:
        print(f"(!) An error occurred while importing data from sheet 'Vehicles': {e}")
        return None
    

    ### (2) IMPORT 'Registrations' DATA
    
    # Import vehicle registration data from sheet 'Registrations' and the CAGR for forcasting future registrations
    
    # registrations[id, year] = {registrations}

    try:
        df = pd.read_excel(file_path, sheet_name='Registrations')

        cagr = float(df.iat[3, 2])
        n_init_years = df.loc[5].count()
        
        print(f'   CAGR [%]: {cagr}')
        print(f'   number of model initialization years: {n_init_years}')

        registrations = pd.DataFrame({
            'id': [i for i in range(1, n_vehicles + 1) for j in range(start_year, start_year + n_init_years)],
            'year': [j for i in range(1, n_vehicles + 1) for j in range(start_year, start_year + n_init_years)]})
        registrations.set_index(['id', 'year'], inplace=True)

        for i in range(1, n_vehicles + 1):
            for j in range(start_year, start_year + n_init_years):
                registrations.loc[(i, j), 'registrations'] = df.iat[6+i, j-start_year+2]

    except FileNotFoundError:
        raise Exception(f"ERROR: The input file '{file_path}' was not found.")
    
    except Exception as e:
        print(f"(!) An error occurred while importing data from sheet 'Registrations': {e}")
        return None
    

    ### (3) IMPORT 'EoL' DATA
    
    # Import end-of-life vehicle data from sheet 'EoL' including systemic material loss rates (exports, unknown whereabouts) and dismantling contents for plastic fractions
    
    # loss[year] = {exports, unknown_whereabouts}
    # dismantling[id, year] = {pp_mass, pa_mass, pc_mass, abs_mass}

    try:
        df = pd.read_excel(file_path, sheet_name='EoL')

        loss = pd.DataFrame({
            'year': range(start_year, end_year + 1),
            'exports': df.iloc[7, 2:2+n_years].values,  # [%]
            'unknown_whereabouts': df.iloc[8, 2:2+n_years].values})  # [%]
        loss.set_index('year', inplace=True)

        dismantling = pd.DataFrame({
            'id': [i for i in range(1, n_vehicles + 1) for j in range(start_year, end_year + 1)],
            'year': [j for i in range(1, n_vehicles + 1) for j in range(start_year, end_year + 1)]})
        dismantling.set_index(['id', 'year'], inplace=True)

        row = 13

        for i in range(1, n_vehicles + 1):
            for j in range(start_year, end_year + 1):
                dismantling.loc[(i, j), 'pp_mass'] = df.iat[row, j-start_year+2]  # [kg]
                dismantling.loc[(i, j), 'pa_mass'] = df.iat[row+1, j-start_year+2]  # [kg]
                dismantling.loc[(i, j), 'pc_mass'] = df.iat[row+2, j-start_year+2]  # [kg]
                dismantling.loc[(i, j), 'abs_mass'] = df.iat[row+3, j-start_year+2]  # [kg]

            row += 6

    except FileNotFoundError:
        raise Exception(f"ERROR: The input file '{file_path}' was not found.")
    
    except Exception as e:
        print(f"(!) An error occurred while importing data from sheet 'EoL': {e}")
        return None
    

    ### (4) IMPORT 'Recycling' DATA
    
    # Import recycling data from sheet 'Recycling' including recycling (sorting) efficiencies for PP, PA, PC and ABS in ELV recycling, the production efficiency for producing new PP, PA, PC, ABS components, and the maximum recycling capacities for plastic fractions
    
    # recycling[year] = {pp_efficiency, pa_efficiency, pc_efficiency, abs_efficiency}
    # production[year] = {pp_efficiency, pa_efficiency, pc_efficiency, abs_efficiency, max_pp, max_pa, max_pc, max_abs}

    try:
        df = pd.read_excel(file_path, sheet_name='Recycling')

        recycling = pd.DataFrame({
            'year': range(start_year, end_year + 1),
            'pp_efficiency': df.iloc[7, 2:2+n_years].values,
            'pa_efficiency': df.iloc[8, 2:2+n_years].values,
            'pc_efficiency': df.iloc[9, 2:2+n_years].values,
            'abs_efficiency': df.iloc[10, 2:2+n_years].values})
        recycling.set_index('year', inplace=True)

        production = pd.DataFrame({
            'year': range(start_year, end_year + 1),
            'pp_efficiency': df.iloc[14, 2:2+n_years].values,
            'pa_efficiency': df.iloc[15, 2:2+n_years].values,
            'pc_efficiency': df.iloc[16, 2:2+n_years].values,
            'abs_efficiency': df.iloc[17, 2:2+n_years].values,

            'max_pp': df.iloc[21, 2:2+n_years].values,
            'max_pa': df.iloc[22, 2:2+n_years].values,
            'max_pc': df.iloc[23, 2:2+n_years].values,
            'max_abs': df.iloc[24, 2:2+n_years].values})
        production.set_index('year', inplace=True)

    except FileNotFoundError:
        raise Exception(f"ERROR: The input file '{file_path}' was not found.")
    
    except Exception as e:
        print(f"(!) An error occurred while importing data from sheet 'Production': {e}")
        return None
    

    ### (5) SAVE TMP FILES
    
    # Save all imported data in a temporary dictionary tmp for quick checks of the imported data
    
    tmp['vehicles_names'] = vehicles_names
    tmp['vehicles_data'] = vehicles_data
    tmp['loss'] = loss
    tmp['dismantling'] = dismantling
    tmp['recycling'] = recycling
    tmp['production'] = production


    print('   import done.')

    return scenario_name, start_year, end_year, n_years, n_vehicles, vehicles_names, vehicles_data, cagr, n_init_years, registrations, loss, dismantling, recycling, production, tmp