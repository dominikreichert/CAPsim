####
#
# CAPsim
# Plot Module for Multi-Scenario Sensitivity Analysis Results
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
from matplotlib.gridspec import GridSpec
import math
import numpy as np



### COLOR SCHEME

color = pd.DataFrame({
    'pp': (0/255, 139/255, 139/255),
    'pa': (250/255, 128/255, 114/255),
    'pc': (128/255, 128/255, 0/255),
    'abs': (218/255, 165/255, 32/255),
    'total': (139/255, 0/255, 0/255)
})



def plot_sa_multi_data(export_path, n_scenarios, sa_plots, plotter_start_year, plotter_end_year):

    name = 'sa_closed-loop-rates.pdf'

    set_years = range(plotter_start_year, plotter_end_year + 1)

    # Find max. y-lim:

    maximum = 0
    for plot, (scenario_id, scenario_name, set_years, pp, pa, pc, abs, total, pp_plus, pa_plus, pc_plus, abs_plus, total_plus, pp_minus, pa_minus, pc_minus, abs_minus, total_minus, target_year) in enumerate(sa_plots):
        maximum = max(maximum, max(pp), max(pp_plus), max(pp_minus), max(pa), max(pa_plus), max(pa_minus), max(pc), max(pc_plus), max(pc_minus), max(abs), max(abs_plus), max(abs_minus), max(total), max(total_plus), max(total_minus))


    n_cols = min(math.ceil(math.sqrt(n_scenarios)), 3)
    n_rows = (n_scenarios + n_cols - 1) // n_cols

    subplot_width = 4
    subplot_height = 4
    wspace_inch = 1.2
    hspace_inch = 1.2

    fig_width = n_cols * subplot_width + (n_cols - 1) * wspace_inch
    fig_height = n_rows * subplot_height + (n_rows - 1) * hspace_inch

    fig = plt.figure(figsize=(fig_width, fig_height))
    grid = GridSpec(n_rows, n_cols, figure=fig)
    grid.update(
        wspace=wspace_inch / subplot_width,
        hspace=hspace_inch / subplot_height
    )

    flag = True

    for plot, (scenario_id, scenario_name, set_years, pp, pa, pc, abs, total, pp_plus, pa_plus, pc_plus, abs_plus, total_plus, pp_minus, pa_minus, pc_minus, abs_minus, total_minus, target_year) in enumerate(sa_plots):
        row = plot // n_cols
        col = plot % n_cols

        sub_plt = fig.add_subplot(grid[row, col])

        idx = target_year - set_years[0]  # target value index

        sub_plt.plot(set_years, pp, color=tuple(color['pp']), label='PP')
        target_value = pp[idx]
        sub_plt.plot(target_year, target_value, 'o', color=tuple(color['pp']), markersize=4)
        sub_plt.text(target_year - 0.6, target_value + 0.6, f'{target_value:.2f}', color=tuple(color['pp']), fontsize=8, ha='right')

        sub_plt.plot(set_years, pa, color=tuple(color['pa']), label='PA')
        target_value = pa[idx]
        sub_plt.plot(target_year, target_value, 'o', color=tuple(color['pa']), markersize=4)
        sub_plt.text(target_year + 0.6, target_value + 0.6, f'{target_value:.2f}', color=tuple(color['pa']), fontsize=8, ha='left')

        sub_plt.plot(set_years, pc, color=tuple(color['pc']), label='PC')
        target_value = pc[idx]
        sub_plt.plot(target_year, target_value, 'o', color=tuple(color['pc']), markersize=4)
        sub_plt.text(target_year - 0.6, target_value + 0.6, f'{target_value:.2f}', color=tuple(color['pc']), fontsize=8, ha='right')

        sub_plt.plot(set_years, abs, color=tuple(color['abs']), label='ABS')
        target_value = abs[idx]
        sub_plt.plot(target_year, target_value, 'o', color=tuple(color['abs']), markersize=4)
        sub_plt.text(target_year - 0.6, target_value + 0.6, f'{target_value:.2f}', color=tuple(color['abs']), fontsize=8, ha='right')

        sub_plt.plot(set_years, total, color=tuple(color['total']), linestyle='--', label='Total')
        target_value = total[idx]
        sub_plt.plot(target_year, target_value, 'o', color=tuple(color['total']), markersize=4)
        sub_plt.text(target_year + 0.6, target_value + 0.6, f'{target_value:.2f}', color=tuple(color['total']), fontsize=8, ha='left')

        # Sensitivity analysis areas:

        sub_plt.fill_between(set_years, pp_plus, pp_minus, alpha=0.2, color=color['pp'])
        sub_plt.fill_between(set_years, pa_plus, pa_minus, alpha=0.2, color=color['pa'])
        sub_plt.fill_between(set_years, pc_plus, pc_minus, alpha=0.2, color=color['pc'])
        sub_plt.fill_between(set_years, abs_plus, abs_minus, alpha=0.2, color=color['abs'])
        sub_plt.fill_between(set_years, total_plus, total_minus, alpha=0.2, color=color['total'])


        sub_plt.set_title(f'{scenario_name} scenario')
        sub_plt.set_xlim(plotter_start_year, plotter_end_year)
        sub_plt.set_ylim(0, maximum + 2)
        sub_plt.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}%"))
        sub_plt.set_box_aspect(1)
        
        if flag:
            sub_plt.legend()
            flag = False

    plt.show()

    fig.savefig(f'{export_path}{name}', bbox_inches = 'tight')

    print(f'   {name} exported.')