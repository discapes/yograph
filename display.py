
from typing import NamedTuple
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict, namedtuple
from itertools import groupby

def survey(results, category_names, points):
    """
    Parameters
    ----------
    results : dict
        A mapping from question labels to a list of answers per category.
        It is assumed all lists contain the same number of entries and that
        it matches the length of *category_names*.
    category_names : list of str
        The category labels.
    """
    labels = list(results.keys())
    data = np.array(list(results.values()))
    data_cum = data.cumsum(axis=1)
    category_colors = pslt.colormaps['RdYlGn'](
        np.linspace(0.15, 0.85, data.shape[1]))[::-1]

    fig, ax = plt.subplots(figsize=(9.2, 5))
    fig.suptitle(title)
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    #ax.set_xlim(0, np.sum(data, axis=1).max())
    ax.set_xlim(0, 1)
    ax.format_coord = lambda x, y: f"x: {round((1 - x) * max_points)}"

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        rects = ax.barh(labels, widths, left=starts, height=0.5,
                        label=colname, color=color)

        r, g, b, _ = color
        text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
        ax.bar_label(rects, labels=[f"{v:.0%}" for v in widths], label_type='center', color=text_color)
        
        if i < len(letters):
            for j, rect in enumerate(rects):
                label = labels[j]
                if label in points:
                    score = points[label][i]
                    ax.text(1 - score / max_points, rect.get_y() - 0.15, letters[i],
                            ha='center', va='center', color='black', fontsize=10, fontweight='bold')
                    ax.plot(1 - score / max_points, rect.get_y(), '.', color="black")
            
    ax.legend(ncols=len(category_names), bbox_to_anchor=(0, 1),
              loc='lower left', fontsize='small')

    return fig, ax

async def line_graph(data1, data2):
    fig, ax1 = plt.subplots()

    color = 'tab:blue'
    ax1.set_xlabel('Koekerta')
    ax1.set_ylabel('Koe oli helppo', color=color)
    ax1.plot(list(data1.keys())[::-1], list(data1.values())[::-1], color=color, marker='o', linestyle='-')
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  
    color = 'tab:red'
    ax2.set_ylabel('Pisteraja', color=color)  
    ax2.plot(list(data2.keys())[::-1], list(data2.values())[::-1], color=color, marker='o', linestyle='-')
    ax2.tick_params(axis='y', labelcolor=color)

    ax1.xaxis.grid(True)  # Adding vertical grid lines only

    plt.title("YLE-kyselyn ja pisterajan korrelaatio")
    plt.show()
    
class DataSource(NamedTuple):
    data: list[NamedTuple]
    yaxis: str
    category: str | None
    percent_cats: bool
    
# magic line chart tool that works for everything 
#
def draw_line_chart(ds1: DataSource, ds2: DataSource, xaxis: str, suptitle=None):
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()  
    
    def draw_datasource(ds: DataSource, ax: Axes, two=False):
        data, yaxis, category, percent_cats = ds
        x_is_string = isinstance(getattr(data[0], xaxis), str)
        unique_x_values = set([getattr(item, xaxis) for item in data])
        if x_is_string:
            unique_x_values = sorted(unique_x_values)
        
        if percent_cats:
            unique_sums = { x: None for x in unique_x_values}
            x_arr = [getattr(item, xaxis) for item in data]
            y_arr = [getattr(item, yaxis) for item in data]
            for x, y in zip(x_arr, y_arr):
                unique_sums[x] = (unique_sums[x] or 0) + y
        
        
        def make_unique(x_arr, y_arr, label):
            unique_data = { x: None for x in unique_x_values}
            for x, y in zip(x_arr, y_arr):
                unique_data[x] = (unique_data[x] or 0) + ((y / unique_sums[x]) if percent_cats else y)
            print(label, unique_data)
            
            return list(unique_data.keys()), list(unique_data.values())   
        
        def plot_x_y(data, label=None):
            x = [getattr(item, xaxis) for item in data]
            y = [getattr(item, yaxis) for item in data]
            x, y = make_unique(x, y, label)
            ax.plot(x, y, "--k" if two else "", label=label)
        
        if category:
            categories = set(getattr(item, category) for item in data)
            for cat in categories:
                filtered_data = [item for item in data if getattr(item, category) == cat]
                plot_x_y(filtered_data, cat)
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
                    fancybox=True, shadow=True, ncol=5)
            plt.subplots_adjust(bottom=0.15)
        else:
            plot_x_y(data)
        ax.set_xlabel(xaxis)
        ax.set_ylabel(yaxis)
            
    draw_datasource(ds1, ax1)
    draw_datasource(ds2, ax2, True)
    if suptitle:
        fig.suptitle(suptitle)
   # ax.set_title(f'{yaxis} per {xaxis}' + f" grouped by {category}" if category else "")
    plt.show()

