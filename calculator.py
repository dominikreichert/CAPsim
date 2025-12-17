####
#
# CAPsim
# Calculation Module
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
import numpy as np
from scipy.stats import weibull_min
import math



###
###  (1) CALCULATE FUTURE VEHICLE REGISTRATIONS
###

# Model future vehicle registrations from the last year with defined registration data in the input file based on the defined CAGR, and update the registrations matrix

# registrations[id, year] = {registrations}

def calc_registrations(start_year, end_year, set_vehicles, cagr, n_init_years, registrations):

    init_year = start_year + n_init_years - 1  # last year for which registration data is defined in the input file

    if n_init_years == 0:
        raise ValueError('(!) Registrations cannot be predicted because no registration data is defined in the input file. Please add registration data for at least one year.')

    if init_year >= end_year:
        print('(!) Vehicle registrations already defined.')

    elif init_year < end_year:

        for veh in set_vehicles:
            
            init_reg = registrations.loc[(veh, init_year), 'registrations']

            # CAGR = (end value / start value)^(1 / number of years) - 1
            # => end value = start value * (1 + CAGR)^(number of years)

            for year in range(init_year + 1, end_year + 1):
                new_row = pd.DataFrame(
                    init_reg * (1 + cagr / 100) ** (year - init_year),
                    columns = registrations.columns, index = [(veh, year)])
                registrations = pd.concat([registrations, new_row])

    return registrations



###
###  (2) CALCULATE VEHILCE FLEET
###

# Create detailed and cumulated vehicle fleet matrix per vehicle model (id), and calculate vehicle stocks (vehicle fleet). The matrices will be added by data on vehicles exiting the vehicle fleet (elvs_exit), thereof, veheicles being exported (elvs_export), vehicles with unknown whereabouts (elvs_unknown), vehicles entering recycling (elvs_recycling), and the resulting vehicle stock (stock) for each year of registration (year_reg) and each current year (year_now)

# fleet_detail[id, year_reg, year_now] = {stock, elvs_exit, elvs_export, elvs_unknown, elvs_recycling}
# fleet[id, year] = {stock, elvs_exit, elvs_export, elvs_unknown, elvs_recycling}

def calc_fleet(start_year, end_year, set_years, set_vehicles, registrations, shape, scale):


    # DETAILED VEHICLE FLEET

    fleet_detail = pd.DataFrame({
        'id': [i for i in set_vehicles for j_reg in set_years for j_now in set_years],
        'year_reg': [j_reg for i in set_vehicles for j_reg in set_years for j_now in set_years],
        'year_now': [j_now for i in set_vehicles for j_reg in set_years for j_now in set_years],
        'stock': [0 for i in set_vehicles for j_reg in set_years for j_now in set_years],
        'elvs_exit': [0 for i in set_vehicles for j_reg in set_years for j_now in set_years],
        'elvs_export': [0 for i in set_vehicles for j_reg in set_years for j_now in set_years],
        'elvs_unknown': [0 for i in set_vehicles for j_reg in set_years for j_now in set_years],
        'elvs_recycling': [0 for i in set_vehicles for j_reg in set_years for j_now in set_years]})
    fleet_detail.set_index(['id', 'year_reg', 'year_now'], inplace=True)

    for veh in set_vehicles:
        for year_reg in set_years:

            veh_reg = registrations.loc[(veh, year_reg), 'registrations']

            exit_sum = 0

            for year_now in range(year_reg, end_year + 1):

                # Calculate number of vehicles exiting the fleet according to Weibull distribution including Weibull parameters shape and scale defined in lines 39-40 above:

                elvs_exit = math.floor(veh_reg * weibull_min.pdf(year_now - year_reg, shape, scale=scale))

                exit_sum += elvs_exit

                # No negative stock permitted: check if more vehicles exit the fleet than were originally registered:

                if exit_sum > veh_reg:
                    if year_now == year_reg:
                        elvs_exit = veh_reg

                    elif year_now > year_reg:
                        elvs_exit = min(fleet_detail.loc[(veh, year_reg, year_now-1), 'stock'], elvs_exit)

                fleet_detail.loc[(veh, year_reg, year_now), 'elvs_exit'] = elvs_exit

                # Calculate vehicle stock:

                if year_now == year_reg:
                    fleet_detail.loc[(veh, year_reg, year_now), 'stock'] = veh_reg - elvs_exit

                else:
                    fleet_detail.loc[(veh, year_reg, year_now), 'stock'] = fleet_detail.loc[(veh, year_reg, year_now-1), 'stock'] - elvs_exit


    # CUMULATED VEHICLE FLEET

    fleet = pd.DataFrame({
        'id': [i for i in set_vehicles for j in set_years],
        'year': [j for i in set_vehicles for j in set_years],
        'stock': [0 for i in set_vehicles for j in set_years],
        'elvs_exit': [0 for i in set_vehicles for j in set_years],
        'elvs_export': [0 for i in set_vehicles for j in set_years],
        'elvs_unknown': [0 for i in set_vehicles for j in set_years],
        'elvs_recycling': [0 for i in set_vehicles for j in set_years]})
    fleet.set_index(['id', 'year'], inplace=True)

    for veh in set_vehicles:
        for year_now in set_years:
            stock_j = 0

            for year_reg in range(start_year, year_now + 1):
                stock_j += fleet_detail.loc[(veh, year_reg, year_now), 'stock']

            fleet.loc[(veh, year_now), 'stock'] = stock_j

    return fleet_detail, fleet



###
###  (3) CALCULATE END-OF-LIFE (ELVS)
###

def calc_eol(start_year, end_year, set_years, set_vehicles, fleet_detail, fleet, loss):


    # (3.1) FLEET EXITS

    # Calculate vehicles exiting the fleet (elvs_exit) in the detailed vehicle fleet matrix fleet_detail per vehicle model (id) for each current year (year_now) based on the change in stock, and update the cumulated vehicle fleet matrix fleet

    # adding fleet_detail[id, year_reg, year_now] = {elvs_exit}
    # adding fleet[id, year] = {elvs_exit}

    for veh in set_vehicles:
        for year_now in set_years:

            # First year:

            fleet_detail.loc[(veh, year_now, year_now), 'elvs_exit'] = 0

            # From second year on:

            exits = 0

            for year_reg in range(start_year, year_now):
                exits_ = fleet_detail.loc[(veh, year_reg, year_now-1), 'stock'] - fleet_detail.loc[(veh, year_reg, year_now), 'stock']

                fleet_detail.loc[(veh, year_reg, year_now), 'elvs_exit'] = exits_
                exits += exits_
                
            fleet.loc[(veh, year_now), 'elvs_exit'] = exits


    # (3.2) EXPORTS, UNKNOWN WHEREABOUTS

    # Calculate vehicles being exported (elvs_export) and vehicles with unknown whereabouts (elvs_unknown) in the detailed vehicle fleet matrix fleet_detail per vehicle model (id) for each current year (year_now) based on the vehicles exiting the fleet (elvs_exit), and update the cumulated vehicle fleet matrix fleet

    # adding fleet_detail[id, year_reg, year_now] = {elvs_export, elvs_unknown}
    # adding fleet[id, year] = {elvs_export, elvs_unknown}

    for veh in set_vehicles:
        for year_now in set_years:

            exports = loss.loc[year_now, 'exports']
            unknown_whereabouts = loss.loc[year_now, 'unknown_whereabouts']

            exp = 0
            unk = 0

            for year_reg in range(start_year, year_now):
                exp_ = fleet_detail.loc[(veh, year_reg, year_now), 'elvs_exit'] * exports / 100
                fleet_detail.loc[(veh, year_reg, year_now), 'elvs_export'] = exp_
                exp += exp_

                unk_ = fleet_detail.loc[(veh, year_reg, year_now), 'elvs_exit'] * unknown_whereabouts / 100
                fleet_detail.loc[(veh, year_reg, year_now), 'elvs_unknown'] = unk_
                unk += unk_
                
            fleet.loc[(veh, year_now), 'elvs_export'] = exp
            fleet.loc[(veh, year_now), 'elvs_unknown'] = unk


    # (3.3) ELVS / VEHICLES ENTERING RECYCLING

    # Calculate vehicles entering recycling (elvs_recycling) in the detailed vehicle fleet matrix fleet_detail per vehicle model (id) for each current year (year_now) based on the vehicles exiting the fleet (elvs_exit) minus vehicles being exported (elvs_export) and vehicles with unknown whereabouts (elvs_unknown), and update the cumulated vehicle fleet matrix fleet

    # adding fleet_detail[id, year_reg, year_now] = {elvs_recycling}
    # adding fleet[id, year] = {elvs_recycling}

    for veh in set_vehicles:
        for year_now in set_years:

            rec = 0

            for year_reg in range(start_year, year_now):
                rec_ = fleet_detail.loc[(veh, year_reg, year_now), 'elvs_exit'] - fleet_detail.loc[(veh, year_reg, year_now), 'elvs_export'] - fleet_detail.loc[(veh, year_reg, year_now), 'elvs_unknown']
                fleet_detail.loc[(veh, year_reg, year_now), 'elvs_recycling'] = rec_
                rec += rec_
                
            fleet.loc[(veh, year_now), 'elvs_recycling'] = rec

    
    return fleet_detail, fleet



###
###  (4) CALCULATE RECYCLING OUTPUTS
###

# Model recycling outputs or recyclate supplies from ELVs based on the vehicles entering recycling (elvs_recycling) in the detailed vehicle fleet matrix fleet_detail per vehicle model (id) for each current year (year_now), the vehicle model data (total mass, plastic content, polymer contents) in vehicles_data, the dismantling rates in dismantling, and the recycling efficiencies in recycling

# eol[id, year] = {input_pp, input_pa, input_pc, input_abs, input_elvs, dismantling_output_pp, dismantling_output_pa, dismantling_output_pc, dismantling_output_abs, recycling_output_pp, recycling_output_pa, recycling_output_pc, recycling_output_abs}

def calc_recycling(start_year, end_year, set_years, set_vehicles, vehicles_data, fleet_detail, dismantling, recycling):

    eol = pd.DataFrame({
        'id': [i for i in set_vehicles for j in set_years],
        'year': [j for i in set_vehicles for j in set_years],
        'input_pp': [0 for i in set_vehicles for j in set_years],
        'input_pa': [0 for i in set_vehicles for j in set_years],
        'input_pc': [0 for i in set_vehicles for j in set_years],
        'input_abs': [0 for i in set_vehicles for j in set_years],
        'input_elvs': [0 for i in set_vehicles for j in set_years],

        'dismantling_output_pp': [0 for i in set_vehicles for j in set_years],
        'dismantling_output_pa': [0 for i in set_vehicles for j in set_years],
        'dismantling_output_pc': [0 for i in set_vehicles for j in set_years],
        'dismantling_output_abs': [0 for i in set_vehicles for j in set_years],

        'recycling_output_pp': [0 for i in set_vehicles for j in set_years],
        'recycling_output_pa': [0 for i in set_vehicles for j in set_years],
        'recycling_output_pc': [0 for i in set_vehicles for j in set_years],
        'recycling_output_abs': [0 for i in set_vehicles for j in set_years]
        })
    eol.set_index(['id', 'year'], inplace=True)


    for veh in set_vehicles:


        # POLYMER-SPECIFIC RECYCLING INPUTS
        
        # Calculate polymer-specific recycling inputs (input_pp, input_pa, input_pc, input_abs) and number of ELVs entering recycling (input_elvs) per vehicle model (id) for each current year (year_now) based on the vehicles entering recycling (elvs_recycling) in the detailed vehicle fleet matrix fleet_detail and the vehicle model data (total mass, plastic content, polymer contents) in vehicles_data
        
        # adding eol[id, year] = {input_pp, input_pa, input_pc, input_abs, input_elvs}

        for year_now in set_years:

            pp = 0
            pa = 0
            pc = 0
            abs = 0
            n_veh_ = 0

            for year_reg in range(start_year, year_now + 1):
                n_veh = fleet_detail.loc[(veh, year_reg, year_now), 'elvs_recycling']
                v_mass = vehicles_data.loc[(veh, year_reg), 'total_mass']
                v_plast_cont = vehicles_data.loc[(veh, year_reg), 'plastic_content']
                v_pp_cont = vehicles_data.loc[(veh, year_reg), 'pp_content']
                v_pa_cont = vehicles_data.loc[(veh, year_reg), 'pa_content']
                v_pc_cont = vehicles_data.loc[(veh, year_reg), 'pc_content']
                v_abs_cont = vehicles_data.loc[(veh, year_reg), 'abs_content']

                pp_ = n_veh * v_mass * v_plast_cont / 100 * v_pp_cont / 100
                pa_ = n_veh * v_mass * v_plast_cont / 100 * v_pa_cont / 100
                pc_ = n_veh * v_mass * v_plast_cont / 100 * v_pc_cont / 100
                abs_ = n_veh * v_mass * v_plast_cont / 100 * v_abs_cont / 100

                pp += pp_
                pa += pa_
                pc += pc_
                abs += abs_
                n_veh_ += n_veh

            eol.loc[(veh, year_now), 'input_pp'] = pp
            eol.loc[(veh, year_now), 'input_pa'] = pa
            eol.loc[(veh, year_now), 'input_pc'] = pc
            eol.loc[(veh, year_now), 'input_abs'] = abs
            eol.loc[(veh, year_now), 'input_elvs'] = n_veh_


        for year_now in set_years:


            # DISMANTLING OUTPUTS
            
            # Calculate polymer-specific dismantling outputs (dismantling_output_pp, dismantling_output_pa, dismantling_output_pc, dismantling_output_abs) per vehicle model (id) for each current year (year_now) based on the number of ELVs entering recycling (input_elvs) in eol and the dismantling rates in dismantling
            
            # adding eol[id, year] = {dismantling_output_pp, dismantling_output_pa, dismantling_output_pc, dismantling_output_abs}

            n_veh = eol.loc[(veh, year_now), 'input_elvs']

            veh_dism_pp = dismantling.loc[(veh, year_now), 'pp_mass']
            veh_dism_pa = dismantling.loc[(veh, year_now), 'pa_mass']
            veh_dism_pc = dismantling.loc[(veh, year_now), 'pc_mass']
            veh_dism_abs = dismantling.loc[(veh, year_now), 'abs_mass']

            eol.loc[(veh, year_now), 'dismantling_output_pp'] = n_veh * veh_dism_pp
            eol.loc[(veh, year_now), 'dismantling_output_pa'] = n_veh * veh_dism_pa
            eol.loc[(veh, year_now), 'dismantling_output_pc'] = n_veh * veh_dism_pc
            eol.loc[(veh, year_now), 'dismantling_output_abs'] = n_veh * veh_dism_abs

            bodies_pp = eol.loc[(veh, year_now), 'input_pp'] - eol.loc[(veh, year_now), 'dismantling_output_pp']
            bodies_pa = eol.loc[(veh, year_now), 'input_pa'] - eol.loc[(veh, year_now), 'dismantling_output_pa']
            bodies_pc = eol.loc[(veh, year_now), 'input_pc'] - eol.loc[(veh, year_now), 'dismantling_output_pc']
            bodies_abs = eol.loc[(veh, year_now), 'input_abs'] - eol.loc[(veh, year_now), 'dismantling_output_abs']


            # RECYCLING OUTPUTS
            
            # Calculate polymer-specific recycling outputs (recycling_output_pp, recycling_output_pa, recycling_output_pc, recycling_output_abs) and the total recycling output (recycling_output_total) per vehicle model (id) for each current year (year_now) based on the bodies entering recycling (input_pp, input_pa, input_pc, input_abs) and the recycling efficiencies in recycling
            
            # adding eol[id, year] = {recycling_output_pp, recycling_output_pa, recycling_output_pc, recycling_output_abs, recycling_output_total}

            output_pp = bodies_pp * recycling.loc[year_now, 'pp_efficiency'] / 100
            output_pa = bodies_pa * recycling.loc[year_now, 'pa_efficiency'] / 100
            output_pc = bodies_pc * recycling.loc[year_now, 'pc_efficiency'] / 100
            output_abs = bodies_abs * recycling.loc[year_now, 'abs_efficiency'] / 100

            eol.loc[(veh, year_now), 'recycling_output_pp'] = output_pp
            eol.loc[(veh, year_now), 'recycling_output_pa'] = output_pa
            eol.loc[(veh, year_now), 'recycling_output_pc'] = output_pc
            eol.loc[(veh, year_now), 'recycling_output_abs'] = output_abs
            eol.loc[(veh, year_now), 'recycling_output_total'] = output_pp + output_pa + output_pc + output_abs

    return eol



###
###  (5) CALCULATE CLOSED-LOOP RATES
###

# Calculate closed-loop rates based on the polymer-specific recycling outputs (recycling_output_pp, recycling_output_pa, recycling_output_pc, recycling_output_abs) in eol, the vehicles registrations (registrations), the vehicle model data (total mass, plastic content, polymer contents) in vehicles_data, and the production efficiencies and maximum recycled contents in production

# closedloop[year] = {demand_pp, demand_pa, demand_pc, demand_abs, demand_plastic, supply_pp, supply_pa, supply_pc, supply_abs, supply_total, pp, pa, pc, abs, total}

def calc_closedloop(set_years, set_vehicles, vehicles_data, registrations, eol, production):

    closedloop = pd.DataFrame({
        'year': [j for j in set_years],

        'demand_pp': [0 for j in set_years],
        'demand_pa': [0 for j in set_years],
        'demand_pc': [0 for j in set_years],
        'demand_abs': [0 for j in set_years],
        'demand_plastic': [0 for j in set_years],

        'supply_pp': [0 for j in set_years],
        'supply_pa': [0 for j in set_years],
        'supply_pc': [0 for j in set_years],
        'supply_abs': [0 for j in set_years],
        'supply_total': [0 for j in set_years],

        'pp': [0 for j in set_years],
        'pa': [0 for j in set_years],
        'pc': [0 for j in set_years],
        'abs': [0 for j in set_years],
        'total': [0 for j in set_years]
        })
    closedloop.set_index('year', inplace=True)

    for year_now in set_years:
        demand_pp = 0
        demand_pa = 0
        demand_pc = 0
        demand_abs = 0
        demand_plastic = 0

        supply_pp = 0
        supply_pa = 0
        supply_pc = 0
        supply_abs = 0

        pp_eff = production.loc[year_now, 'pp_efficiency'] / 100
        pa_eff = production.loc[year_now, 'pa_efficiency'] / 100
        pc_eff = production.loc[year_now, 'pc_efficiency'] / 100
        abs_eff = production.loc[year_now, 'abs_efficiency'] / 100

        for veh in set_vehicles:
            n_veh = registrations.loc[(veh, year_now), 'registrations']
            veh_mass = vehicles_data.loc[(veh, year_now), 'total_mass']
            veh_plastic = vehicles_data.loc[(veh, year_now), 'plastic_content']
            veh_pp = vehicles_data.loc[(veh, year_now), 'pp_content']
            veh_pa = vehicles_data.loc[(veh, year_now), 'pa_content']
            veh_pc = vehicles_data.loc[(veh, year_now), 'pc_content']
            veh_abs = vehicles_data.loc[(veh, year_now), 'abs_content']

            demand_pp += n_veh * veh_mass * veh_plastic / 100 * veh_pp / 100
            demand_pa += n_veh * veh_mass * veh_plastic / 100 * veh_pa / 100
            demand_pc += n_veh * veh_mass * veh_plastic / 100 * veh_pc / 100
            demand_abs += n_veh * veh_mass * veh_plastic / 100 * veh_abs / 100
            demand_plastic += n_veh * veh_mass * veh_plastic / 100

            supply_pp += eol.loc[(veh, year_now), 'recycling_output_pp']
            supply_pa += eol.loc[(veh, year_now), 'recycling_output_pa']
            supply_pc += eol.loc[(veh, year_now), 'recycling_output_pc']
            supply_abs += eol.loc[(veh, year_now), 'recycling_output_abs']

        closedloop.loc[year_now, 'demand_pp'] = demand_pp
        closedloop.loc[year_now, 'demand_pa'] = demand_pa
        closedloop.loc[year_now, 'demand_pc'] = demand_pc
        closedloop.loc[year_now, 'demand_abs'] = demand_abs
        closedloop.loc[year_now, 'demand_plastic'] = demand_plastic

        # Check for maximum recycled input:

        if (supply_pp * pp_eff) > (demand_pp * production.loc[year_now, 'max_pp'] / 100):
            supply_pp = demand_pp * production.loc[year_now, 'max_pp'] / 100 / pp_eff
        if (supply_pa * pa_eff) > (demand_pa * production.loc[year_now, 'max_pa'] / 100):
            supply_pa = demand_pa * production.loc[year_now, 'max_pa'] / 100 / pa_eff
        if (supply_pc * pc_eff) > (demand_pc * production.loc[year_now, 'max_pc'] / 100):
            supply_pc = demand_pc * production.loc[year_now, 'max_pc'] / 100 / pc_eff
        if (supply_abs * abs_eff) > (demand_abs * production.loc[year_now, 'max_abs'] / 100):
            supply_abs = demand_abs * production.loc[year_now, 'max_abs'] / 100 / abs_eff

        closedloop.loc[year_now, 'supply_pp'] = supply_pp
        closedloop.loc[year_now, 'supply_pa'] = supply_pa
        closedloop.loc[year_now, 'supply_pc'] = supply_pc
        closedloop.loc[year_now, 'supply_abs'] = supply_abs
        closedloop.loc[year_now, 'supply_total'] = supply_pp + supply_pa + supply_pc + supply_abs

        supply_total_ = supply_pp * pp_eff + supply_pa * pa_eff + supply_pc * pc_eff + supply_abs * abs_eff

        closedloop.loc[year_now, 'pp'] = supply_pp * pp_eff / demand_pp * 100
        closedloop.loc[year_now, 'pa'] = supply_pa * pa_eff / demand_pa * 100
        closedloop.loc[year_now, 'pc'] = supply_pc * pc_eff / demand_pc * 100
        closedloop.loc[year_now, 'abs'] = supply_abs * abs_eff / demand_abs * 100
        closedloop.loc[year_now, 'total'] = supply_total_ / demand_plastic * 100

    return closedloop



###
###  CALCULATE ALL
###

def calc_all(start_year, end_year, vehicles_data, cagr, n_init_years, registrations, loss, dismantling, recycling, production, set_years, set_vehicles, shape, scale):


    # (1) REGISTRATIONS

    _registrations = calc_registrations(start_year, end_year, set_vehicles, cagr, n_init_years, registrations)


    # (2) VEHICLE FLEET

    _fleet_detail, _fleet = calc_fleet(start_year, end_year, set_years, set_vehicles, _registrations, shape, scale)


    # (3) END-OF-LIFE (ELVS)

    _fleet_detail, _fleet = calc_eol(start_year, end_year, set_years, set_vehicles, _fleet_detail, _fleet, loss)


    # (4) RECYCLING OUTPUTS

    _eol = calc_recycling(start_year, end_year, set_years, set_vehicles, vehicles_data, _fleet_detail, dismantling, recycling)


    # (5) CLOSED-LOOP RATES

    _closedloop = calc_closedloop(set_years, set_vehicles, vehicles_data, _registrations, _eol, production)


    return _registrations, _fleet_detail, _fleet, _eol, _closedloop