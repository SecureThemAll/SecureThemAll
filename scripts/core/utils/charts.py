from typing import List, AnyStr
from pathlib import Path
from venn import pseudovenn

import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import FuncFormatter
from matplotlib.path import Path as MatPath
from matplotlib.spines import Spine
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
# from matplotlib_venn import venn3, venn3_circles
from matplotlib.transforms import Affine2D
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.ticker import StrMethodFormatter
from matplotlib import rc
from scipy import stats
import matplotlib.font_manager as font_manager
from mpl_toolkits.axes_grid1 import ImageGrid

plt.style.use('seaborn-dark')

small_font = {'family': 'serif',
              'name': 'Helvetica',
              'weight': 'bold',
              'size': 18}

legend_font = font_manager.FontProperties(family=small_font["name"],
                                          weight=small_font["weight"],
                                          style="normal", size=20)

medium_font = small_font.copy()
medium_font["size"] = 22
large_font = medium_font.copy()
large_font["size"] = 24
big_font = large_font.copy()
big_font["size"] = 26
rc_font = medium_font.copy()
del rc_font["name"]
rc('font', **rc_font)

global_colors = ['coral', 'seagreen', 'steelblue', 'plum', 'teal', 'slategray', 'gold', 'tomato', 'pink', 'salmon',
                 'purple', 'red']


def bins_labels(bins, **kwargs):
    bin_w = (max(bins) - min(bins)) / (len(bins) - 1)
    plt.xticks(np.arange(min(bins) + bin_w / 2, max(bins), bin_w), bins, **kwargs)
    plt.xlim(bins[0], bins[-1])


def nearest_square(limit):
    answer = 0
    while (answer + 1) ** 2 <= limit:
        answer += 1
    return answer


def color_map(num: int, cmp: str):
    cm = plt.get_cmap(cmp)
    return [cm(1. * i / num) for i in range(num)]


def unit_poly_verts(theta):
    """Return vertices of polygon for subplot axes.

    This polygon is circumscribed by a unit circle centered at (0.5, 0.5)
    """
    x0, y0, r = [0.5] * 3
    verts = [(r * np.cos(t) + x0, r * np.sin(t) + y0) for t in theta]
    return verts


# source https://matplotlib.org/gallery/api/radar_chart.html
def radar_factory(num_vars, frame='circle'):
    """Create a radar chart with `num_vars` axes.

    This function creates a RadarAxes projection and registers it.

    Parameters
    ----------
    num_vars : int
        Number of variables for radar chart.
    frame : {'circle' | 'polygon'}
        Shape of frame surrounding axes.

    """
    # calculate evenly-spaced axis angles
    theta = np.linspace(0, 2 * np.pi, num_vars, endpoint=False)

    class RadarAxes(PolarAxes):

        name = 'radar'
        # use 1 line segment to connect specified points
        RESOLUTION = 1

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # rotate plot such that the first axis is at the top
            self.set_theta_zero_location('N')

        def fill(self, *args, closed=True, **kwargs):
            """Override fill so that line is closed by default"""
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            # FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.concatenate((x, [x[0]]))
                y = np.concatenate((y, [y[0]]))
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            # The Axes patch must be centered at (0.5, 0.5) and of radius 0.5
            # in axes coordinates.
            if frame == 'circle':
                return Circle((0.5, 0.5), 0.5)
            elif frame == 'polygon':
                return RegularPolygon((0.5, 0.5), num_vars,
                                      radius=.5, edgecolor="k")
            else:
                raise ValueError("unknown value for 'frame': %s" % frame)

        def _gen_axes_spines(self):
            if frame == 'circle':
                return super()._gen_axes_spines()
            elif frame == 'polygon':
                # spine_type must be 'left'/'right'/'top'/'bottom'/'circle'.
                spine = Spine(axes=self,
                              spine_type='circle',
                              path=MatPath.unit_regular_polygon(num_vars))
                # unit_regular_polygon gives a polygon of radius 1 centered at
                # (0, 0) but we want a polygon of radius 0.5 centered at (0.5,
                # 0.5) in axes coordinates.
                spine.set_transform(Affine2D().scale(.5).translate(.5, .5)
                                    + self.transAxes)
                return {'polar': spine}
            else:
                raise ValueError("unknown value for 'frame': %s" % frame)

    register_projection(RadarAxes)
    return theta


def radar_chart(data: List[List[int]], spoke_labels: List[str], colors, labels: List[str],
                title: str, ax_title: str = "", frame: str = 'polygon'):
    num_vars = len(spoke_labels)
    theta = radar_factory(num_vars, frame=frame)

    fig, ax = plt.subplots(figsize=(20, 10), subplot_kw=dict(projection='radar'))
    fig.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)

    ax.set_rgrids([0.2, 0.4, 0.6, 0.8])
    ax.set_title(ax_title, position=(0.5, 1.1), horizontalalignment='center', verticalalignment='center', **large_font)

    for d, color in zip(data, colors):
        ax.plot(theta, d, color=color)
        ax.fill(theta, d, facecolor=color, alpha=0.25)

    ax.set_varlabels(spoke_labels)
    legend = ax.legend(labels, loc=(0.9, .95), labelspacing=0.1, fontsize='small', prop=legend_font)
    # fig.text(0.5, 0.965, title, horizontalalignment='center', color='black', **large_font)


def venn_plot(data: List[set], labels: List[AnyStr], colors):
    if len(data) > 6:
        data = data[:-1]
        labels = labels[:-1]
    pseudovenn({name: vals for name, vals in zip(labels, data)}, fmt="{size}", cmap="plasma", fontsize=12,
               legend_loc="upper left")
    # if len(data) != len(labels) != len(colors) != 3:
    #    raise ValueError('Subsets and labels must be of size 3')
    # Custom text labels: change the label of group A
    # v = venn3(subsets=data, set_labels=tuple(labels), set_colors=global_colors[:3])
    # c = venn3_circles(subsets=data, linestyle='dashed', linewidth=1, color="grey")


# source https://stackoverflow.com/a/50205834
def stacked_bars_plot(data, series_labels, x_labels=None, show_values=False, value_format="{}", y_labels=None,
                      colors=None, grid=True, reverse=False):
    """Plots a stacked bar chart with the data and labels provided.

    Keyword arguments:
    data            -- 2-dimensional numpy array or nested list
                       containing data for each series in rows
    series_labels   -- list of series labels (these appear in
                       the legend)
    x_labels        -- list of category labels (these appear
                       on the x-axis)
    show_values     -- If True then numeric value labels will
                       be shown on each bar
    value_format    -- Format string for numeric value labels
                       (default is "{}")
    y_labels        -- Labels for y-axis (str)
    colors          -- List of color labels
    grid            -- If True display grid
    reverse         -- If True reverse the order that the
                       series are displayed (left-to-right
                       or right-to-left)
    """

    ny = len(data[0])
    ind = list(range(ny))

    axes = []
    cum_size = np.zeros(ny)

    data = np.array(data)

    if reverse:
        data = np.flip(data, axis=1)
        x_labels = reversed(x_labels)

    for i, row_data in enumerate(data):
        color = colors[i] if colors is not None else None
        axes.append(plt.bar(ind, row_data, bottom=cum_size,
                            label=series_labels[i], color=color))
        cum_size += row_data

    if x_labels:
        plt.xticks(ind, x_labels, **large_font)

    if y_labels:
        plt.ylabel("Score (0-8)", **large_font)

    plt.legend(prop=legend_font)

    if grid:
        plt.grid()

    if show_values:
        for axis in axes:
            for bar in axis:
                w, h = bar.get_width(), bar.get_height()
                plt.text(bar.get_x() + w / 2, bar.get_y() + h / 2,
                         value_format.format(h), ha="center",
                         va="bottom", **medium_font)


# source https://matplotlib.org/3.3.1/gallery/images_contours_and_fields/image_annotated_heatmap.html
def heatmap(data, row_labels, col_labels, ax=None, cbar_kw: dict = None, cbarlabel="", **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels.

    Parameters
    ----------
    data
        A 2D numpy array of shape (N, M).
    row_labels
        A list or array of length N with the labels for the rows.
    col_labels
        A list or array of length M with the labels for the columns.
    ax
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted.  If
        not provided, use current axes or create a new one.  Optional.
    cbar_kw
        A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
    cbarlabel
        The label for the colorbar.  Optional.
    **kwargs
        All other arguments are forwarded to `imshow`.
    """

    if not ax:
        ax = plt.gca()

    # Plot the heatmap

    im = ax.imshow(data, **kwargs)
    cbar = None
    # Create colorbar
    if cbar_kw:
        cbar = ax.figure.colorbar(im, orientation='horizontal', fraction=0.10, aspect=20, ax=ax, pad=0.10, **cbar_kw)
        cbar.ax.set_title(cbarlabel, **big_font)

    # We want to show all ticks...
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    # ... and label them with the respective list entries.
    ax.set_xticklabels(col_labels, **big_font)
    ax.set_yticklabels(row_labels, **big_font)

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=True, bottom=False,
                   labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=-75, ha="right", va="center",
             rotation_mode="anchor")

    # Turn spines off and create white grid.
    for edge, spine in ax.spines.items():
        spine.set_visible(False)

    ax.set_xticks(np.arange(data.shape[1] + 1) - .5, minor=True)
    ax.set_yticks(np.arange(data.shape[0] + 1) - .5, minor=True)
    ax.grid(which="minor", color="black", linestyle='-', linewidth=1)
    ax.tick_params(which="minor", bottom=False, left=False)

    return im, cbar


def annotate_heatmap(im, data=None, valfmt="{x:.2f}", textcolors=None, threshold=None, **textkw):
    """
    A function to annotate a heatmap.

    Parameters
    ----------
    im
        The AxesImage to be labeled.
    data
        Data used to annotate.  If None, the image's data is used.  Optional.
    valfmt
        The format of the annotations inside the heatmap.  This should either
        use the string format method, e.g. "$ {x:.2f}", or be a
        `matplotlib.ticker.Formatter`.  Optional.
    textcolors
        A list or array of two color specifications.  The first is used for
        values below a threshold, the second for those above.  Optional.
    threshold
        Value in data units according to which the colors from textcolors are
        applied.  If None (the default) uses the middle of the colormap as
        separation.  Optional.
    **kwargs
        All other arguments are forwarded to each call to `text` used to create
        the text labels.
    """

    if textcolors is None:
        textcolors = ["red", "white"]
    if not isinstance(data, (list, np.ndarray)):
        data = im.get_array()

    # Normalize the threshold to the images color range.
    if threshold is not None:
        threshold = im.norm(threshold)
    else:
        threshold = im.norm(data.max()) / 2.

    # Set default alignment to center, but allow it to be
    # overwritten by textkw.
    kw = dict(horizontalalignment="center", verticalalignment="center")
    kw.update(textkw)

    # Get the formatter in case a string is supplied
    if isinstance(valfmt, str):
        valfmt = StrMethodFormatter(valfmt)

    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []

    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            kw.update(color=textcolors[int(im.norm(data[i, j]) > threshold)])
            text = im.axes.text(j, i, valfmt(data[i, j], None), **kw, **small_font)
            texts.append(text)

    return texts


def cbar_repair_status():
    cell_labels_ac = np.array(['FR', 'FSC', 'FFL', 'NCP', 'CP', 'R'])
    cell_labels = np.array(
        ['Fails\nRepair', 'Fails\nSanity\nCheck', 'Fails\nFault\nLocalization', 'No\nCandidate\nPatches',
         'Candidate\nPatches', 'Repair'])
    boundaries = np.array([0, 0.20, 0.40, 0.60, 0.80, 1])
    ticks_step = 1 / cell_labels.size
    cbar_ticks = np.linspace(0, 1, len(boundaries), endpoint=False)
    cbar_ticks = cbar_ticks + (ticks_step / 2)
    mapped = {x: cell_labels_ac[i] for i, x in enumerate(boundaries)}
    cba_mapped = {x: cell_labels[i] for i, x in enumerate(cbar_ticks)}
    # cba_mapped.update(mapped)
    fmt = FuncFormatter(lambda x, pos: mapped[x])
    cbar_fmt = FuncFormatter(lambda x, pos: cba_mapped[x])

    return cbar_fmt, cbar_ticks,


def heatmap2(data, col_labels, row_labels, titles, **kwargs):
    fig = plt.figure(figsize=(30, 15))
    # np_data = np.array(data)
    # transpose = np_data.transpose()
    size = len(data)
    # print(transpose, len(transpose))
    grid = ImageGrid(fig, 111, nrows_ncols=(1, size), axes_pad=0.4)
    images = []

    for ax, im_data, labels, title in zip(grid, data, col_labels, titles):
        np_data = np.array(im_data)
        im = ax.imshow(np_data, vmin=0, vmax=1, cmap=plt.get_cmap("RdYlGn", 6))
        images.append(im)
        # We want to show all ticks...
        ax.set_xticks(np.arange(np_data.shape[1]))
        # ... and label them with the respective list entries.
        ax.set_xticklabels(labels, **big_font)

        # Let the horizontal axes labeling appear on top.
        ax.tick_params(top=True, bottom=False,
                       labeltop=True, labelbottom=False)
        # Rotate the tick labels and set their alignment.
        plt.setp(ax.get_xticklabels(), rotation=-75, ha="right", va="center",
                 rotation_mode="anchor")

        # Turn spines off and create white grid.
        for edge, spine in ax.spines.items():
            spine.set_visible(False)
        ax.set_xticks(np.arange(np_data.shape[1] + 1) - .5, minor=True)
        ax.set_yticks(np.arange(len(row_labels) + 1) - .5, minor=True)
        ax.grid(which="minor", color="black", linestyle='-', linewidth=1)
        ax.tick_params(which="minor", bottom=False, left=False)
        ax.set_title(title, y=-0.1, fontdict={'verticalalignment': 'top'})

    grid.axes_column[0][0].set_yticks(np.arange(len(row_labels)))
    # ... and label them with the respective list entries.
    grid.axes_column[0][0].set_yticklabels(row_labels, **big_font)

    # Set Colorbar
    cbar_fmt, cbar_ticks = cbar_repair_status()
    cbar_kw = dict(ticks=cbar_ticks, format=cbar_fmt)
    cbar = fig.colorbar(images[0], orientation='horizontal', fraction=0.10, aspect=20,
                        ax=grid.axes_all, pad=0.05, **cbar_kw)
    cbar.ax.set_title("Repair Status", **big_font)
    fig.tight_layout()


def multi_heatmap(data, col_labels, row_labels, **kwargs):
    width, height = len(data[0]), len(data)
    figsize = (25, 15)

    if width < 7:
        figsize = (20, 10)

    fig, axn = plt.subplots(nrows=1, ncols=1, figsize=figsize)
    cbar_fmt, cbar_ticks = cbar_repair_status()
    im, _ = heatmap(np.array(data), col_labels=col_labels, row_labels=row_labels, ax=axn, cbarlabel="Repair Status",
                    cmap=plt.get_cmap("RdYlGn", 6), cbar_kw=dict(ticks=cbar_ticks, format=cbar_fmt),
                    **kwargs)
    # ims.append(im)
    # annotate_heatmap(im, valfmt=fmt, threshold=-1, textcolors=("white", "black"))
    # texts = annotate_heatmap(im, valfmt="{x:.2f}")
    # axn.set_title(titles, **big_font)

    # cbar = fig.colorbar(im, ax=axn)
    # cbar.ax.set_ylabel("Fix score", rotation=-90, va="bottom")


def histogram(data: List[List[int]], title: str, labels: List[str], x_label: str, y_label: str, **kwargs):
    xticks = np.arange(0.05, 1, 0.05)
    shifts = [-0.005, -0.0025, -0.001, 0, 0.001, 0.0025, 0.005]

    for i, (lst, label, shift) in enumerate(zip(data, labels, shifts)):
        if not lst:
            continue
        # bins = np.histogram_bin_edges(lst, 20, (0, 1))
        np_lst = np.array(lst)

        print(f"Total: {len(lst)}\t{label} >= 5%:", len(np.where(np_lst >= 0.05)[0]), "\t>= 50%:",
              len(np.where(np_lst >= 0.5)[0]), "\t= 100%:", len(np.where(np_lst == 1)[0]))
        unique_values, inv = np.unique(lst, return_inverse=True)
        counts = np.bincount(inv)
        bars = plt.bar(unique_values + shift, counts, width=0.02, align="center", edgecolor="black",
                       color=global_colors[i],
                       alpha=0.75, label=label)
        sns.kdeplot(np_lst, linewidth=2, color=global_colors[-(i + 1)], label=f"{label}_kde")
        # n, bins, bars = plt.hist(lst, bins=xticks, edgecolor="black", color=global_colors[i], rwidth=1,
        #                         linewidth=1, density=True, alpha=0.7, align="mid", label=label)

        # ax = sns.histplot(lst, kde=True, bins=bins, color=global_colors[i], label=label, stat="density",
        #                  line_kws={'linewidth': 2, "color": global_colors[-(i + 1)], "label": f"{label}_kde"})
        # density = stats.norm(lst)
        # histo, bin_edges = np.histogram(lst, bins=21, range=[0, 1.05])
        # plt.plot([bar.get_x() for bar in bars], density([bar.get_y() for bar in bars]), color=global_colors[-(i+1)], label=f"{label}_kde")
        # colors = color_map(len(lst), cmap)
        # Good old loop. Choose colormap of your taste

        # print(bars)
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                plt.annotate(f'{round(height, 2)}', xy=(bar.get_x() + bar.get_width() / 2, height),
                             xytext=(0, 1), textcoords='offset points', ha='center', va='bottom', **medium_font)

        # Add title and labels with custom font sizes
    plt.legend(loc='best', prop=legend_font)
    plt.yticks(**medium_font)
    # rotation=25, ha="left",
    plt.xticks(xticks, **medium_font, rotation=35)
    plt.xlim(-0.05, 1.05)
    # plt.xlabel(x_label, **big_font)
    # plt.ylabel(y_label, **big_font)
    plt.ylabel("", **medium_font)
    # plt.title(title, **big_font)


class Plotter:
    def __init__(self, out_path: str, fig_width: int = 20, fig_height: int = 10):
        self.out_path = Path(out_path)
        self.fig_size = (fig_width, fig_height)
        self.plots = {'heatmap': multi_heatmap, 'bars': stacked_bars_plot, 'venn': venn_plot, 'radar': radar_chart,
                      'hist': histogram, "heatmap2": heatmap2}

        if self.out_path and not self.out_path.exists():
            self.out_path.mkdir()

    def __call__(self, plot: str, file_name: str, data, cmap: str, **kwargs):
        colors = color_map(len(data), cmap)

        if plot in self.plots:
            plt.figure(figsize=self.fig_size, constrained_layout=(plot == 'heatmap'))
            self.plots[plot](data=data, colors=colors, **kwargs)
            plt.savefig(f"{self.out_path / Path(file_name)}", bbox_inches='tight')
            plt.clf()
