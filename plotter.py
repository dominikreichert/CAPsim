####
#
# CAPsim
# Plot Module for Scenario-Specific Results
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
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import operator



### COLOR SCHEME

color = pd.DataFrame({
    'pp': (0/255, 139/255, 139/255),
    'pa': (250/255, 128/255, 114/255),
    'pc': (128/255, 128/255, 0/255),
    'abs': (218/255, 165/255, 32/255),
    'total': (139/255, 0/255, 0/255),
    'ICEV': (48/255, 66/255, 141/255),
    'BEV': (64/255, 139/255, 102/255)
})



def plot_data(export_path, scenario_id, scenario_name, n_scenarios, set_years, set_vehicles, vehicles_names, registrations, cagr, fleet, closedloop, target_year):


    ### (1) REGISTRATIONS

    if n_scenarios == 1:
        name = 'registrations.pdf'
    else:
        name = f'{scenario_id}_registrations.pdf'

    reg_total = [0 for j in set_years]

    for veh in set_vehicles:

        reg = [registrations.loc[(veh, j), 'registrations'] / 1e6 for j in set_years]
        veh_name = vehicles_names.loc[veh, 'name']

        reg_total = list(map(operator.add, reg_total, reg))

        plt.plot(set_years, reg, color=tuple(color[veh_name]), label=veh_name)

    plt.plot(set_years, reg_total, color=tuple(color['total']), linestyle='--', label='total')

    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))

    plt.title(f'Vehicle registrations [M] with CAGR = {cagr:.2f}%')
    plt.legend()

    plt.savefig(f'{export_path}{name}', bbox_inches='tight')
    plt.clf()

    print(f'   {name} exported.')


    ### (2) FLEET

    if n_scenarios == 1:
        name = 'fleet.pdf'
    else:
        name = f'{scenario_id}_fleet.pdf'

    stock_total = [0 for j in set_years]

    for veh in set_vehicles:

        stock = [fleet.loc[(veh, j), 'stock'] / 1e6 for j in set_years]
        veh_name = vehicles_names.loc[veh, 'name']

        stock_total = list(map(operator.add, stock_total, stock))

        plt.plot(set_years, stock, color=tuple(color[veh_name]), label=veh_name)

    plt.plot(set_years, stock_total, color=tuple(color['total']), linestyle='--', label='total')

    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))

    plt.title('Vehicle fleet [M]')
    plt.legend()

    plt.savefig(f'{export_path}{name}', bbox_inches='tight')
    plt.clf()

    print(f'   {name} exported.')


    ### (3) END-OF-LIFE

    for veh in set_vehicles:
        veh_name = vehicles_names.loc[veh, 'name']
        
        if n_scenarios == 1:
            name = f'eol_veh_{veh_name}.pdf'
        else:
            name = f'{scenario_id}_eol_veh_{veh_name}.pdf'

        exit = [fleet.loc[(veh, j), 'elvs_exit'] / 1e6 for j in set_years]
        export = [fleet.loc[(veh, j), 'elvs_export'] / 1e6 for j in set_years]
        unknown = [fleet.loc[(veh, j), 'elvs_unknown'] / 1e6 for j in set_years]
        recycling = [fleet.loc[(veh, j), 'elvs_recycling'] / 1e6 for j in set_years]

        plt.plot(set_years, exit, label='exiting fleet')
        plt.plot(set_years, export, label='exports')
        plt.plot(set_years, unknown, label='unknown whereabouts')
        plt.plot(set_years, recycling, label='entering ELV recycling')

        plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))

        plt.title(f'End-of-life vehicle {veh}: {veh_name} [M]')
        plt.legend()

        plt.savefig(f'{export_path}{name}', bbox_inches='tight')
        plt.clf()

        print(f'   {name} exported.')


    ### (4) CLOSED-LOOP CONTENT

        if n_scenarios == 1:
            name = 'closed-loop-content.pdf'
        else:
            name = f'{scenario_id}_closed-loop-content.pdf'

        demand_pp = [closedloop.loc[j, 'demand_pp'] / 1e9 for j in set_years]
        demand_pa = [closedloop.loc[j, 'demand_pa'] / 1e9 for j in set_years]
        demand_pc = [closedloop.loc[j, 'demand_pc'] / 1e9 for j in set_years]
        demand_abs = [closedloop.loc[j, 'demand_abs'] / 1e9 for j in set_years]
        demand_total = [closedloop.loc[j, 'demand_plastic'] / 1e9 for j in set_years]

        supply_pp = [closedloop.loc[j, 'supply_pp'] / 1e9 for j in set_years]
        supply_pa = [closedloop.loc[j, 'supply_pa'] / 1e9 for j in set_years]
        supply_pc = [closedloop.loc[j, 'supply_pc'] / 1e9 for j in set_years]
        supply_abs = [closedloop.loc[j, 'supply_abs'] / 1e9 for j in set_years]
        supply_total = [closedloop.loc[j, 'supply_total'] / 1e9 for j in set_years]

        plt.plot(set_years, demand_pp, color=tuple(color['pp']), linestyle='--', label='PP demand')
        plt.plot(set_years, supply_pp, color=tuple(color['pp']), label='recycled PP supply')

        plt.plot(set_years, demand_pa, color=tuple(color['pa']), linestyle='--', label='PA demand')
        plt.plot(set_years, supply_pa, color=tuple(color['pa']), label='recycled PA supply')

        plt.plot(set_years, demand_pc, color=tuple(color['pc']), linestyle='--', label='PC demand')
        plt.plot(set_years, supply_pc, color=tuple(color['pc']), label='recycled PC supply')

        plt.plot(set_years, demand_abs, color=tuple(color['abs']), linestyle='--', label='ABS demand')
        plt.plot(set_years, supply_abs, color=tuple(color['abs']), label='recycled ABS supply')
        
        plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.1f}"))

        plt.title('Plastic material demand and supply in Mtons')
        plt.legend()

        plt.savefig(f'{export_path}{name}', bbox_inches='tight')
        plt.clf()

        print(f'   {name} exported.')


    ### (5) CLOSED-LOOP RATES

    if n_scenarios == 1:
        name = 'closed-loop-rates.pdf'
    else:
        name = f'{scenario_id}_closed-loop-rates.pdf'

    pp = [closedloop.loc[j, 'pp'] for j in set_years]
    pa = [closedloop.loc[j, 'pa'] for j in set_years]
    pc = [closedloop.loc[j, 'pc'] for j in set_years]
    abs = [closedloop.loc[j, 'abs'] for j in set_years]
    total = [closedloop.loc[j, 'total'] for j in set_years]

    idx = target_year - set_years[0] # target value index

    maximum = max(max(pp), max(pa), max(pc), max(abs), max(total))

    plt.plot(set_years, pp, color=tuple(color['pp']), label='PP')
    target_value = pp[idx]
    plt.plot(target_year, target_value, 'o', color=tuple(color['pp']), markersize=6)
    plt.text(target_year + 0.5, target_value + 0.5, f'{target_value:.2f}', color=tuple(color['pp']), fontsize=10)

    plt.plot(set_years, pa, color=tuple(color['pa']), label='PA')
    target_value = pa[idx]
    plt.plot(target_year, target_value, 'o', color=tuple(color['pa']), markersize=6)
    plt.text(target_year + 0.5, target_value + 0.5, f'{target_value:.2f}', color=tuple(color['pa']), fontsize=10)

    plt.plot(set_years, pc, color=tuple(color['pc']), label='PC')
    target_value = pc[idx]
    plt.plot(target_year, target_value, 'o', color=tuple(color['pc']), markersize=6)
    plt.text(target_year + 0.5, target_value + 0.5, f'{target_value:.2f}', color=tuple(color['pc']), fontsize=10)

    plt.plot(set_years, abs, color=tuple(color['abs']), label='ABS')
    target_value = abs[idx]
    plt.plot(target_year, target_value, 'o', color=tuple(color['abs']), markersize=6)
    plt.text(target_year + 0.5, target_value + 0.5, f'{target_value:.2f}', color=tuple(color['abs']), fontsize=10)

    plt.plot(set_years, total, color=tuple(color['total']), linestyle='--', label='Total')
    target_value = total[idx]
    plt.plot(target_year, target_value, 'o', color=tuple(color['total']), markersize=6)
    plt.text(target_year + 0.5, target_value + 0.5, f'{target_value:.2f}', color=tuple(color['total']), fontsize=10)

    plt.title('Closed-loop rates [%]')
    plt.gca().set_ylim(0, maximum + 2)
    plt.gca().set_xlim(set_years[0], set_years[-1])
    plt.legend()

    plt.savefig(f'{export_path}{name}', bbox_inches='tight')

    if n_scenarios == 1:
        plt.show()

    plot = (scenario_id, scenario_name, set_years, pp, pa, pc, abs, total, target_year)

    plt.clf()
    plt.close()

    print(f'   {name} exported.')

    return plot