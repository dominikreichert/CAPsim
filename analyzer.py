####
#
# CAPsim
# Sensitivity Analysis Module
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

from calculator import *



def run_sa(start_year, end_year, n_years, n_vehicles, vehicles_data, cagr, n_init_years, registrations, loss, dismantling, recycling, production, tmp, set_years, set_vehicles, shape, scale, sensitivity):

    sa_data_plus = []
    sa_data_minus = []
    sa_titles = []
    sa_tmp_plus = {}
    sa_tmp_minus = {}
    sa_tmp_elements = ['vehicles_data', 'cagr', 'registrations', 'fleet_detail', 'fleet', 'eol', 'loss', 'dismantling', 'recycling', 'production']
    

    # (SA.1) INPUT DATA

    # (SA.1.1) VEHICLES_DATA

    # (SA.1.1.1) VEHICLES_DATA: TOTAL_MASS

    for i in range(1, n_vehicles + 1):
        _vehicles_data = vehicles_data.copy()

        for j in range(start_year, end_year + 1):
            value = vehicles_data.loc[(i, j), 'total_mass'] 
            _vehicles_data.loc[(i, j), 'total_mass'] = value * (1 + sensitivity)
            
        _registrations, _fleet_detail, _fleet, _eol, _closedloop = calc_all(start_year, end_year, _vehicles_data, cagr, n_init_years, registrations, loss, dismantling, recycling, production, set_years, set_vehicles, shape, scale)

        sa_data_plus.append(_closedloop)

        name = f'total_mass_vehicle_{i}'
        sa_tmp_plus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol, loss, dismantling, recycling, production]

        print(f'   (SA:) calculating +{sensitivity * 100}% for total_mass, vehicle {i} done.')


        _vehicles_data = vehicles_data.copy()

        for j in range(start_year, end_year + 1):
            value = vehicles_data.loc[(i, j), 'total_mass'] 
            _vehicles_data.loc[(i, j), 'total_mass'] = value * (1 - sensitivity)
            
        _registrations, _fleet_detail, _fleet, _eol, _closedloop = calc_all(start_year, end_year, _vehicles_data, cagr, n_init_years, registrations, loss, dismantling, recycling, production, set_years, set_vehicles, shape, scale)

        sa_data_minus.append(_closedloop)
        
        sa_tmp_minus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol, loss, dismantling, recycling, production]

        print(f'   (SA:) calculating -{sensitivity * 100}% for total_mass, vehicle {i} done.')

        sa_titles.append(f'total mass of vehicle {i}')


    # (SA.1.1.2) VEHICLES_DATA: PLASTIC CONTENTS

    parameter = ['plastic_content', 'pp_content', 'pa_content', 'pc_content', 'abs_content']

    parameter_titels = ['plastic content', 'PP content', 'PA content', 'PC content', 'ABS content']
    parameter_count = 0

    for p in parameter:

        for i in range(1, n_vehicles + 1):
            _vehicles_data = vehicles_data.copy()

            for j in range(start_year, end_year + 1):
                value = vehicles_data.loc[(i, j), p] 
                _vehicles_data.loc[(i, j), p] = min(value * (1 + sensitivity), 100) # max 100%
                
            _registrations, _fleet_detail, _fleet, _eol, _closedloop = calc_all(start_year, end_year, _vehicles_data, cagr, n_init_years, registrations, loss, dismantling, recycling, production, set_years, set_vehicles, shape, scale)

            sa_data_plus.append(_closedloop)

            name = f'{p}_vehicle_{i}'
            sa_tmp_plus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol, loss, dismantling, recycling, production]

            print(f'   (SA:) calculating +{sensitivity * 100}% for {p}, vehicle {i} done.')


            _vehicles_data = vehicles_data.copy()

            for j in range(start_year, end_year + 1):
                value = vehicles_data.loc[(i, j), p] 
                _vehicles_data.loc[(i, j), p] = value * (1 - sensitivity)
                
            _registrations, _fleet_detail, _fleet, _eol, _closedloop = calc_all(start_year, end_year, _vehicles_data, cagr, n_init_years, registrations, loss, dismantling, recycling, production, set_years, set_vehicles, shape, scale)

            sa_data_minus.append(_closedloop)

            sa_tmp_minus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol, loss, dismantling, recycling, production]

            print(f'   (SA:) calculating -{sensitivity * 100}% for {p}, vehicle {i} done.')

            sa_titles.append(f'{parameter_titels[parameter_count]} of vehicle {i}')
        
        parameter_count += 1

          
    ### (SA.1.2) CAGR

    _cagr = cagr * (1 + sensitivity)

    _registrations, _fleet_detail, _fleet, _eol, _closedloop = calc_all(start_year, end_year, vehicles_data, _cagr, n_init_years, registrations, loss, dismantling, recycling, production, set_years, set_vehicles, shape, scale)

    sa_data_plus.append(_closedloop)

    name = f'cagr'
    sa_tmp_plus[name] = [vehicles_data, _cagr, _registrations, _fleet_detail, _fleet, _eol, loss, dismantling, recycling, production]

    print(f'   (SA:) calculating +{sensitivity * 100}% for CAGR done.')


    _cagr = cagr * (1 - sensitivity)

    _registrations, _fleet_detail, _fleet, _eol, _closedloop = calc_all(start_year, end_year, vehicles_data, _cagr, n_init_years, registrations, loss, dismantling, recycling, production, set_years, set_vehicles, shape, scale)

    sa_data_minus.append(_closedloop)

    sa_tmp_minus[name] = [vehicles_data, _cagr, _registrations, _fleet_detail, _fleet, _eol, loss, dismantling, recycling, production]

    print(f'   (SA:) calculating -{sensitivity * 100}% for CAGR done.')

    sa_titles.append(f'CAGR')


    ### (SA.1.3) LOSS

    parameter = ['exports', 'unknown_whereabouts']

    for p in parameter:

        _loss = loss.copy()

        for j in range(start_year, end_year + 1):
            value = loss.loc[j, p] 
            _loss.loc[j, p] = min(value * (1 + sensitivity), 100)

        _registrations, _fleet_detail, _fleet, _eol, _closedloop = calc_all(start_year, end_year, vehicles_data, cagr, n_init_years, registrations, _loss, dismantling, recycling, production, set_years, set_vehicles, shape, scale)

        sa_data_plus.append(_closedloop)

        name = f'{p}'
        sa_tmp_plus[name] = [vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol, _loss, dismantling, recycling, production]

        print(f'   (SA:) calculating +{sensitivity * 100}% for {p} done.')


        _loss = loss.copy()

        for j in range(start_year, end_year + 1):
            value = loss.loc[j, p] 
            _loss.loc[j, p] = value * (1 - sensitivity)

        _registrations, _fleet_detail, _fleet, _eol, _closedloop = calc_all(start_year, end_year, vehicles_data, cagr, n_init_years, registrations, _loss, dismantling, recycling, production, set_years, set_vehicles, shape, scale)

        sa_data_minus.append(_closedloop)

        sa_tmp_minus[name] = [vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol, _loss, dismantling, recycling, production]

        print(f'   (SA:) calculating -{sensitivity * 100}% for {p} done.')

        sa_titles.append(f'{p.replace("_", " ")}')


    ### (SA.1.4) DISMANTLING CONTENT

    parameter = ['pp_mass', 'pa_mass', 'pc_mass', 'abs_mass']

    for p in parameter:
        for i in range(1, n_vehicles + 1):

            _dismantling = dismantling.copy()
        
            for j in range(start_year, end_year + 1):
                value = dismantling.loc[(i,j), p] 
                _dismantling.loc[(i,j), p] = value * (1 + sensitivity)

            _registrations, _fleet_detail, _fleet, _eol, _closedloop = calc_all(start_year, end_year, vehicles_data, cagr, n_init_years, registrations, loss, _dismantling, recycling, production, set_years, set_vehicles, shape, scale)

            sa_data_plus.append(_closedloop)

            name = f'dismantling_{p}_vehicle_{i}'
            sa_tmp_plus[name] = [vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol, loss, _dismantling, recycling, production]

            print(f'   (SA:) calculating +{sensitivity * 100}% for dismantling {p}, vehicle {i} done.')


            _dismantling = dismantling.copy()
        
            for j in range(start_year, end_year + 1):
                value = dismantling.loc[(i,j), p] 
                _dismantling.loc[(i,j), p] = value * (1 - sensitivity)

            _registrations, _fleet_detail, _fleet, _eol, _closedloop = calc_all(start_year, end_year, vehicles_data, cagr, n_init_years, registrations, loss, _dismantling, recycling, production, set_years, set_vehicles, shape, scale)

            sa_data_minus.append(_closedloop)

            sa_tmp_minus[name] = [vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol, loss, _dismantling, recycling, production]

            print(f'   (SA:) calculating -{sensitivity * 100}% for dismantling {p}, vehicle {i} done.')

            title = f'{p.replace("_", " ")}'
            sa_titles.append(f'dismantled {title[:3].upper() + title[3:]} of vehicle {i}')


    ### (SA.1.5) RECYCLING EFFICIENCY

    parameter = ['pp_efficiency', 'pa_efficiency', 'pc_efficiency', 'abs_efficiency']

    for p in parameter:

        _recycling = recycling.copy()

        for j in range(start_year, end_year + 1):
            value = recycling.loc[j, p] 
            _recycling.loc[j, p] = min(value * (1 + sensitivity), 100)

        _registrations, _fleet_detail, _fleet, _eol, _closedloop = calc_all(start_year, end_year, vehicles_data, cagr, n_init_years, registrations, loss, dismantling, _recycling, production, set_years, set_vehicles, shape, scale)

        sa_data_plus.append(_closedloop)

        name = f'recycling_{p}'
        sa_tmp_plus[name] = [vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol, loss, dismantling, _recycling, production]

        print(f'   (SA:) calculating +{sensitivity * 100}% for recycling {p} done.')


        _recycling = recycling.copy()

        for j in range(start_year, end_year + 1):
            value = recycling.loc[j, p] 
            _recycling.loc[j, p] = value * (1 - sensitivity)

        _registrations, _fleet_detail, _fleet, _eol, _closedloop = calc_all(start_year, end_year, vehicles_data, cagr, n_init_years, registrations, loss, dismantling, _recycling, production, set_years, set_vehicles, shape, scale)

        sa_data_minus.append(_closedloop)

        sa_tmp_minus[name] = [vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol, loss, dismantling, _recycling, production]

        print(f'   (SA:) calculating -{sensitivity * 100}% for recycling {p} done.')

        title = f'{p.replace("_", " ")}'
        sa_titles.append(f'recycling {title[:3].upper() + title[3:]}')


    ### (SA.1.6) PRODUCTION EFFICIENCY

    parameter = ['pp_efficiency', 'pa_efficiency', 'pc_efficiency', 'abs_efficiency']

    for p in parameter:

        _production = production.copy()

        for j in range(start_year, end_year + 1):
            value = production.loc[j, p] 
            _production.loc[j, p] = min(value * (1 + sensitivity), 100)

        _registrations, _fleet_detail, _fleet, _eol, _closedloop = calc_all(start_year, end_year, vehicles_data, cagr, n_init_years, registrations, loss, dismantling, recycling, _production, set_years, set_vehicles, shape, scale)

        sa_data_plus.append(_closedloop)

        name = f'production_{p}'
        sa_tmp_plus[name] = [vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol, loss, dismantling, recycling, _production]

        print(f'   (SA:) calculating +{sensitivity * 100}% for production {p} done.')


        _production = production.copy()

        for j in range(start_year, end_year + 1):
            value = production.loc[j, p] 
            _production.loc[j, p] = value * (1 - sensitivity)

        _registrations, _fleet_detail, _fleet, _eol, _closedloop = calc_all(start_year, end_year, vehicles_data, cagr, n_init_years, registrations, loss, dismantling, recycling, _production, set_years, set_vehicles, shape, scale)

        sa_data_minus.append(_closedloop)

        sa_tmp_minus[name] = [vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol, loss, dismantling, recycling, _production] 

        print(f'   (SA:) calculating -{sensitivity * 100}% for production {p} done.')

        title = f'{p.replace("_", " ")}'
        sa_titles.append(f'production {title[:3].upper() + title[3:]}')


    ### (SA.1.7) MAXIMUM RECYCLED INPUT

    parameter = ['max_pp', 'max_pa', 'max_pc', 'max_abs']

    for p in parameter:

        _production = production.copy()

        for j in range(start_year, end_year + 1):
            value = production.loc[j, p] 
            _production.loc[j, p] = min(value * (1 + sensitivity), 100)

        _registrations, _fleet_detail, _fleet, _eol, _closedloop = calc_all(start_year, end_year, vehicles_data, cagr, n_init_years, registrations, loss, dismantling, recycling, _production, set_years, set_vehicles, shape, scale)

        sa_data_plus.append(_closedloop)

        name = f'production_{p}'
        sa_tmp_plus[name] = [vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol, loss, dismantling, recycling, _production]

        print(f'   (SA:) calculating +{sensitivity * 100}% for production {p} done.')


        _production = production.copy()

        for j in range(start_year, end_year + 1):
            value = production.loc[j, p] 
            _production.loc[j, p] = value * (1 - sensitivity)

        _registrations, _fleet_detail, _fleet, _eol, _closedloop = calc_all(start_year, end_year, vehicles_data, cagr, n_init_years, registrations, loss, dismantling, recycling, _production, set_years, set_vehicles, shape, scale)

        sa_data_minus.append(_closedloop)

        sa_tmp_minus[name] = [vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol, loss, dismantling, recycling, _production]

        print(f'   (SA:) calculating -{sensitivity * 100}% for production {p} done.')

        title = p[4:].upper()
        sa_titles.append(f'max recycled {title} input')


    # (SA.2) MODEL DATA

    # (SA.2.1) WEIBULL PARAMETERS

    # (SA.2.1.1) WEIBULL SHAPE PARAMETER

    # _shape = shape * (1 + sensitivity)

    # _registrations, _fleet_detail, _fleet, _eol, _closedloop = calc_all(start_year, end_year, vehicles_data, cagr, n_init_years, registrations, loss, dismantling, recycling, production, set_years, set_vehicles, _shape, scale)

    # sa_data_plus.append(_closedloop)

    # name = 'weibull_shape'
    # sa_tmp_plus[name] = [vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol, loss, dismantling, recycling, production]

    # print(f'   (SA:) calculating +{sensitivity * 100}% for Weibull shape parameter done.')


    # _shape = shape * (1 - sensitivity)

    # _registrations, _fleet_detail, _fleet, _eol, _closedloop = calc_all(start_year, end_year, vehicles_data, cagr, n_init_years, registrations, loss, dismantling, recycling, production, set_years, set_vehicles, _shape, scale)

    # sa_data_minus.append(_closedloop)

    # sa_tmp_minus[name] = [vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol, loss, dismantling, recycling, production]

    # print(f'   (SA:) calculating -{sensitivity * 100}% for Weibull shape parameter done.')

    # sa_titles.append('Weibull shape parameter')


    # # (SA.2.1.2) WEIBULL SCALE PARAMETER

    # _scale = scale * (1 + sensitivity)

    # _registrations, _fleet_detail, _fleet, _eol, _closedloop = calc_all(start_year, end_year, vehicles_data, cagr, n_init_years, registrations, loss, dismantling, recycling, production, set_years, set_vehicles, shape, _scale)

    # sa_data_plus.append(_closedloop)

    # name = 'weibull_scale'
    # sa_tmp_plus[name] = [vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol, loss, dismantling, recycling, production]

    # print(f'   (SA:) calculating +{sensitivity * 100}% for Weibull scale parameter done.')


    # _scale = scale * (1 - sensitivity)

    # _registrations, _fleet_detail, _fleet, _eol, _closedloop = calc_all(start_year, end_year, vehicles_data, cagr, n_init_years, registrations, loss, dismantling, recycling, production, set_years, set_vehicles, shape, _scale)

    # sa_data_minus.append([_closedloop, vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol, loss, dismantling, recycling, production])

    # sa_tmp_minus[name] = [vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol, loss, dismantling, recycling, production]

    # print(f'   (SA:) calculating -{sensitivity * 100}% for Weibull scale parameter done.')

    # sa_titles.append('Weibull scale parameter')


    return sa_data_plus, sa_data_minus, sa_titles, sa_tmp_plus, sa_tmp_minus, sa_tmp_elements