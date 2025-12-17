####
#
# CAPsim
# Plot Module for Scenario-Specific Sensitivity Analysis Results
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



def plot_sa_data(export_path, scenario_id, scenario_name, n_scenarios, start_year, end_year, set_years, plotter_start_year, plotter_end_year, set_vehicles, vehicles_names, registrations, cagr, fleet, closedloop, target_year, sa_results, sensitivity):


    ### (1) CLOSED LOOP RATES PLOT FOR TOTAL TIME SPAN

    if n_scenarios == 1:
        name = 'sa_closed-loop-rates.pdf'
    else:
        name = f'{scenario_id}_sa_closed-loop-rates.pdf'


    # PLOT CLOSED-LOOP RATES BASED ON INPUT DATA

    pp = [closedloop.loc[j, 'pp'] for j in set_years]
    pa = [closedloop.loc[j, 'pa'] for j in set_years]
    pc = [closedloop.loc[j, 'pc'] for j in set_years]
    abs_ = [closedloop.loc[j, 'abs'] for j in set_years]
    total = [closedloop.loc[j, 'total'] for j in set_years]

    idx = target_year - set_years[0] # target value index

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

    plt.plot(set_years, abs_, color=tuple(color['abs']), label='ABS')
    target_value = abs_[idx]
    plt.plot(target_year, target_value, 'o', color=tuple(color['abs']), markersize=6)
    plt.text(target_year + 0.5, target_value + 0.5, f'{target_value:.2f}', color=tuple(color['abs']), fontsize=10)

    plt.plot(set_years, total, color=tuple(color['total']), linestyle='--', label='Total')
    target_value = total[idx]
    plt.plot(target_year, target_value, 'o', color=tuple(color['total']), markersize=6)
    plt.text(target_year + 0.5, target_value + 0.5, f'{target_value:.2f}', color=tuple(color['total']), fontsize=10)


    # PLOT CLOSED-LOOP RATE AREAS BASED ON SENSITIVITY ANALYSIS RESULTS

    results_range = {}

    # PP:

    _max = [closedloop.loc[j, 'pp'] for j in set_years]
    _min = [closedloop.loc[j, 'pp'] for j in set_years]

    for j in range(start_year, end_year + 1):
        idx = j - start_year

        for a in range(len(sa_results[0])):

            _max[idx] = max(_max[idx], sa_results[0][a].loc[j, 'pp'], sa_results[1][a].loc[j, 'pp'])

            _min[idx] = min(_min[idx], sa_results[0][a].loc[j, 'pp'], sa_results[1][a].loc[j, 'pp'])

    pp_plus = _max
    pp_minus = _min

    results_range['PP'] = {'min': pp_minus,
                           'baseline': pp,
                           'max':pp_plus}

    plt.fill_between(set_years, pp_plus, pp_minus, alpha=0.2, color=color['pp'])

    # PA:

    _max = [closedloop.loc[j, 'pa'] for j in set_years]
    _min = [closedloop.loc[j, 'pa'] for j in set_years]

    for j in range(start_year, end_year + 1):
        idx = j - start_year
        
        for a in range(len(sa_results[0])):

            _max[idx] = max(_max[idx], sa_results[0][a].loc[j, 'pa'], sa_results[1][a].loc[j, 'pa'])

            _min[idx] = min(_min[idx], sa_results[0][a].loc[j, 'pa'], sa_results[1][a].loc[j, 'pa'])

    pa_plus = _max
    pa_minus = _min

    results_range['PA'] = {'min': pa_minus,
                           'baseline': pa,
                           'max':pa_plus}

    plt.fill_between(set_years, pa_plus, pa_minus, alpha=0.2, color=color['pa'])

    # PC:

    _max = [closedloop.loc[j, 'pc'] for j in set_years]
    _min = [closedloop.loc[j, 'pc'] for j in set_years]

    for j in range(start_year, end_year + 1):
        idx = j - start_year
        
        for a in range(len(sa_results[0])):

            _max[idx] = max(_max[idx], sa_results[0][a].loc[j, 'pc'], sa_results[1][a].loc[j, 'pc'])

            _min[idx] = min(_min[idx], sa_results[0][a].loc[j, 'pc'], sa_results[1][a].loc[j, 'pc'])

    pc_plus = _max
    pc_minus = _min

    results_range['PC'] = {'min': pc_minus,
                           'baseline': pc,
                           'max':pc_plus}

    plt.fill_between(set_years, pc_plus, pc_minus, alpha=0.2, color=color['pc'])

    # ABS:

    _max = [closedloop.loc[j, 'abs'] for j in set_years]
    _min = [closedloop.loc[j, 'abs'] for j in set_years]

    for j in range(start_year, end_year + 1):
        idx = j - start_year
        
        for a in range(len(sa_results[0])):

            _max[idx] = max(_max[idx], sa_results[0][a].loc[j, 'abs'], sa_results[1][a].loc[j, 'abs'])

            _min[idx] = min(_min[idx], sa_results[0][a].loc[j, 'abs'], sa_results[1][a].loc[j, 'abs'])

    abs_plus = _max
    abs_minus = _min

    results_range['ABS'] = {'min': abs_minus,
                           'baseline': abs_,
                           'max':abs_plus}

    plt.fill_between(set_years, abs_plus, abs_minus, alpha=0.2, color=color['abs'])

    # TOTAL:

    _max = [closedloop.loc[j, 'total'] for j in set_years]
    _min = [closedloop.loc[j, 'total'] for j in set_years]

    for j in range(start_year, end_year + 1):
        idx = j - start_year
        
        for a in range(len(sa_results[0])):

            _max[idx] = max(_max[idx], sa_results[0][a].loc[j, 'total'], sa_results[1][a].loc[j, 'total'])

            _min[idx] = min(_min[idx], sa_results[0][a].loc[j, 'total'], sa_results[1][a].loc[j, 'total'])

    total_plus = _max
    total_minus = _min

    results_range['total'] = {'min': total_minus,
                           'baseline': total,
                           'max':total_plus}

    plt.fill_between(set_years, total_plus, total_minus, alpha=0.2, color=color['total'])


    # PLOT SETTINGS

    maximum = max(max(pp), max(pp_plus), max(pa), max(pa_plus), max(pc), max(pc_plus), max(abs_), max(abs_plus), max(total), max(total_plus))

    plt.title('Closed-loop rates [%]')
    plt.gca().set_ylim(0, maximum + 2)
    plt.gca().set_xlim(set_years[0], set_years[-1])
    plt.legend()

    plt.savefig(f'{export_path}{name}', bbox_inches='tight')

    if n_scenarios == 1:
        plt.show()

    plot = (scenario_id, scenario_name, set_years, pp, pa, pc, abs_, total, pp_plus, pa_plus, pc_plus, abs_plus, total_plus, pp_minus, pa_minus, pc_minus, abs_minus, total_minus, target_year)

    plt.clf()

    print(f'   {name} exported.')


    ### (2) CLOSED LOOP RATES PLOT FOR TARGET TIME SPAN

    if n_scenarios == 1:
        name = 'sa_closed-loop-rates_2.pdf'
    else:
        name = f'{scenario_id}_sa_closed-loop-rates_2.pdf'

    set_years = range(plotter_start_year, plotter_end_year + 1)


    # PLOT CLOSED-LOOP RATES BASED ON INPUT DATA

    pp = [closedloop.loc[j, 'pp'] for j in set_years]
    pa = [closedloop.loc[j, 'pa'] for j in set_years]
    pc = [closedloop.loc[j, 'pc'] for j in set_years]
    abs_ = [closedloop.loc[j, 'abs'] for j in set_years]
    total = [closedloop.loc[j, 'total'] for j in set_years]

    idx = target_year - set_years[0] # target value index

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

    plt.plot(set_years, abs_, color=tuple(color['abs']), label='ABS')
    target_value = abs_[idx]
    plt.plot(target_year, target_value, 'o', color=tuple(color['abs']), markersize=6)
    plt.text(target_year + 0.5, target_value + 0.5, f'{target_value:.2f}', color=tuple(color['abs']), fontsize=10)

    plt.plot(set_years, total, color=tuple(color['total']), linestyle='--', label='Total')
    target_value = total[idx]
    plt.plot(target_year, target_value, 'o', color=tuple(color['total']), markersize=6)
    plt.text(target_year + 0.5, target_value + 0.5, f'{target_value:.2f}', color=tuple(color['total']), fontsize=10)


    # PLOT CLOSED-LOOP RATE AREAS BASED ON SENSITIVITY ANALYSIS RESULTS

    # PP:

    _max = [closedloop.loc[j, 'pp'] for j in set_years]
    _min = [closedloop.loc[j, 'pp'] for j in set_years]

    for j in set_years:
        idx = j - plotter_start_year

        for a in range(len(sa_results[0])):

            _max[idx] = max(_max[idx], sa_results[0][a].loc[j, 'pp'], sa_results[1][a].loc[j, 'pp'])

            _min[idx] = min(_min[idx], sa_results[0][a].loc[j, 'pp'], sa_results[1][a].loc[j, 'pp'])

    pp_plus = _max
    pp_minus = _min

    plt.fill_between(set_years, pp_plus, pp_minus, alpha=0.2, color=color['pp'])

    # PA:

    _max = [closedloop.loc[j, 'pa'] for j in set_years]
    _min = [closedloop.loc[j, 'pa'] for j in set_years]

    for j in set_years:
        idx = j - plotter_start_year
        
        for a in range(len(sa_results[0])):

            _max[idx] = max(_max[idx], sa_results[0][a].loc[j, 'pa'], sa_results[1][a].loc[j, 'pa'])

            _min[idx] = min(_min[idx], sa_results[0][a].loc[j, 'pa'], sa_results[1][a].loc[j, 'pa'])

    pa_plus = _max
    pa_minus = _min

    plt.fill_between(set_years, pa_plus, pa_minus, alpha=0.2, color=color['pa'])

    # PC:

    _max = [closedloop.loc[j, 'pc'] for j in set_years]
    _min = [closedloop.loc[j, 'pc'] for j in set_years]

    for j in set_years:
        idx = j - plotter_start_year
        
        for a in range(len(sa_results[0])):

            _max[idx] = max(_max[idx], sa_results[0][a].loc[j, 'pc'], sa_results[1][a].loc[j, 'pc'])

            _min[idx] = min(_min[idx], sa_results[0][a].loc[j, 'pc'], sa_results[1][a].loc[j, 'pc'])

    pc_plus = _max
    pc_minus = _min

    plt.fill_between(set_years, pc_plus, pc_minus, alpha=0.2, color=color['pc'])

    # ABS:

    _max = [closedloop.loc[j, 'abs'] for j in set_years]
    _min = [closedloop.loc[j, 'abs'] for j in set_years]

    for j in set_years:
        idx = j - plotter_start_year
        
        for a in range(len(sa_results[0])):

            _max[idx] = max(_max[idx], sa_results[0][a].loc[j, 'abs'], sa_results[1][a].loc[j, 'abs'])

            _min[idx] = min(_min[idx], sa_results[0][a].loc[j, 'abs'], sa_results[1][a].loc[j, 'abs'])

    abs_plus = _max
    abs_minus = _min

    plt.fill_between(set_years, abs_plus, abs_minus, alpha=0.2, color=color['abs'])

    # TOTAL:

    _max = [closedloop.loc[j, 'total'] for j in set_years]
    _min = [closedloop.loc[j, 'total'] for j in set_years]

    for j in set_years:
        idx = j - plotter_start_year
        
        for a in range(len(sa_results[0])):

            _max[idx] = max(_max[idx], sa_results[0][a].loc[j, 'total'], sa_results[1][a].loc[j, 'total'])

            _min[idx] = min(_min[idx], sa_results[0][a].loc[j, 'total'], sa_results[1][a].loc[j, 'total'])

    total_plus = _max
    total_minus = _min

    plt.fill_between(set_years, total_plus, total_minus, alpha=0.2, color=color['total'])


    # PLOT SETTINGS

    maximum = max(max(pp), max(pp_plus), max(pa), max(pa_plus), max(pc), max(pc_plus), max(abs_), max(abs_plus), max(total), max(total_plus))

    plt.title('Closed-loop rates [%]')
    plt.gca().set_ylim(0, maximum + 2)
    plt.gca().set_xlim(set_years[0], set_years[-1])
    plt.legend()

    plt.savefig(f'{export_path}{name}', bbox_inches='tight')

    if n_scenarios == 1:
        plt.show()

    plt.clf()

    print(f'   {name} exported.')


    ### (3) TORNADO PLOT FOR THE TARGET YEAR

    tmp_tornado_1 = pd.DataFrame()

    labels = sa_results[2]
    n_labels = len(labels)

    for p in ['pp', 'pa', 'pc', 'abs', 'total']:

        if n_scenarios == 1:
            name = f'sa_tornado_{target_year}_{p}.pdf'
        else:
            name = f'{scenario_id}_sa_tornado_{target_year}_{p}.pdf'

        # Get total values:

        base_value = closedloop.loc[target_year, p]
        plus_values = [sa_results[0][l].loc[target_year, p] for l in range(n_labels)]
        minus_values = [sa_results[1][l].loc[target_year, p] for l in range(n_labels)]

        # Calculate relative differences to base values:

        plus_differences = [(plus_values[l] - base_value) / base_value * 100 for l in range(n_labels)]
        minus_differences = [(minus_values[l] - base_value) / base_value * 100 for l in range(n_labels)]

        spectrum = [abs(dl) + abs(dh) for dl, dh in zip(minus_differences, plus_differences)]

        # Filter out entries where spectrum is zero (no sensitivity effect):

        filtered_values = [(label, minus_diff, plus_diff, spec) for label, minus_diff, plus_diff, spec in zip(labels, minus_differences, plus_differences, spectrum) if spec > 0]

        # Sort by spectrum (impact):

        sorted_values = sorted(filtered_values, key=lambda x: x[3], reverse=False)

        labels_sorted = [x[0] for x in sorted_values]
        minus_differences_sorted = [x[1] for x in sorted_values]
        plus_differences_sorted = [x[2] for x in sorted_values]

        # Save tmp data:

        _df = pd.DataFrame({
            'polymer': [p, p],
            'sensitivity': ['plus', 'minus']
        })
        for i, label in enumerate(labels):
            _df[label] = [plus_differences[i], minus_differences[i]]

        tmp_tornado_1 = pd.concat([tmp_tornado_1, _df], ignore_index=True)

        # Plot:

        fig, ax = plt.subplots(figsize=(10, 6))
        y_pos = range(len(labels_sorted))

        ax.barh(y_pos, minus_differences_sorted, color="#AA2B2B", label=f'parameter values -{sensitivity * 100:.0f}%')

        ax.barh(y_pos, plus_differences_sorted, color="#4F6640", label=f'parameter values +{sensitivity * 100:.0f}%')

        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels_sorted)

        if p == 'total':
            ax.set_xlabel('Deviation of the total closed-loop rate [%]')
        else:
            ax.set_xlabel(f'Deviation of the polymer-specific closed-loop rate for {p.upper()} [%]')

        ax.set_title(f'Sensitivity analysis for {target_year:.0f}')
        ax.axvline(0, color='black', linewidth=1)
        ax.legend(loc='lower left')
        ax.grid(axis='x', alpha=0.2)
        
        plt.savefig(f'{export_path}{name}', bbox_inches='tight')

        plt.clf()
        plt.close()

        print(f'   {name} exported.')


    ### (4) TORNADO PLOT FOR THE LAST YEAR (PLOTTER_END_YEAR)

    target_year = plotter_end_year

    tmp_tornado_2 = pd.DataFrame()

    labels = sa_results[2]
    n_labels = len(labels)

    for p in ['pp', 'pa', 'pc', 'abs', 'total']:

        if n_scenarios == 1:
            name = f'sa_tornado_{target_year}_{p}.pdf'
        else:
            name = f'{scenario_id}_sa_tornado_{target_year}_{p}.pdf'

        # Get total values:

        base_value = closedloop.loc[target_year, p]
        plus_values = [sa_results[0][l].loc[target_year, p] for l in range(n_labels)]
        minus_values = [sa_results[1][l].loc[target_year, p] for l in range(n_labels)]

        # Calculate relative differences to base values:

        plus_differences = [(plus_values[l] - base_value) / base_value * 100 for l in range(n_labels)]
        minus_differences = [(minus_values[l] - base_value) / base_value * 100 for l in range(n_labels)]

        spectrum = [abs(dl) + abs(dh) for dl, dh in zip(minus_differences, plus_differences)]

        # Filter out entries where spectrum is zero (no sensitivity effect):

        filtered_values = [(label, minus_diff, plus_diff, spec) for label, minus_diff, plus_diff, spec in zip(labels, minus_differences, plus_differences, spectrum) if spec > 0]

        # Sort by spectrum (impact):

        sorted_values = sorted(filtered_values, key=lambda x: x[3], reverse=False)

        labels_sorted = [x[0] for x in sorted_values]
        minus_differences_sorted = [x[1] for x in sorted_values]
        plus_differences_sorted = [x[2] for x in sorted_values]

        # Save tmp data:

        _df = pd.DataFrame({
            'polymer': [p, p],
            'sensitivity': ['plus', 'minus']
        })
        for i, label in enumerate(labels):
            _df[label] = [plus_differences[i], minus_differences[i]]

        tmp_tornado_2 = pd.concat([tmp_tornado_2, _df], ignore_index=True)

        # Plot:

        fig, ax = plt.subplots(figsize=(10, 6))
        y_pos = range(len(labels_sorted))

        ax.barh(y_pos, minus_differences_sorted, color="#AA2B2B", label=f'parameter values -{sensitivity * 100:.0f}%')

        ax.barh(y_pos, plus_differences_sorted, color="#4F6640", label=f'parameter values +{sensitivity * 100:.0f}%')

        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels_sorted)

        if p == 'total':
            ax.set_xlabel('Deviation of the total closed-loop rate [%]')
        else:
            ax.set_xlabel(f'Deviation of the polymer-specific closed-loop rate for {p.upper()} [%]')

        ax.set_title(f'Sensitivity analysis for {target_year:.0f}')
        ax.axvline(0, color='black', linewidth=1)
        ax.legend(loc='lower left')
        ax.grid(axis='x', alpha=0.2)
        
        plt.savefig(f'{export_path}{name}', bbox_inches='tight')

        plt.clf()
        plt.close()

        print(f'   {name} exported.')


    return plot, tmp_tornado_1, tmp_tornado_2, results_range