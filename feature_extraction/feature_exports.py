# native imports
import os
from collections import OrderedDict

# local imports
from util import to_tuple

# third-party imports
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

_dir = os.path.dirname(os.path.realpath(__file__))


def export_csv_data(is_test=False):
    """
    extracts data per column of a .csv file. Then, exports data in numpy array for tensorflow training,
    and exports a visualization of the data

    :param is_test: bool, whether the data is from the validate file or not
    """

    # TODO: maps is a hparam
    if not is_test:
        maps = ['metal', 'lounge']
    else:
        maps = ['validate']

    # all relevant column titles
    cols = ['title', 'barkbands_flatness_db', 'dissonance', 'dynamic_complexity', 'hfc', 'spectral_centroid',
            'bpm', 'danceability', 'key_scale']

    lst = []
    plot_lst = []

    os.chdir(_dir)

    # iterate over the maps
    for folder in maps:

        od = OrderedDict()

        # iterate over files in map
        for file in os.listdir('extraction_outputs'.format(folder)):

            # only take into account csv file
            if file.endswith(".csv") and folder in file:
                # create Dataframe object
                data = pd.read_csv('{}/extraction_outputs/{}'.format(_dir, file))
                arr = np.zeros(data.shape)

                # iterate over the columns in the Dataframe
                for i, col in enumerate(cols):

                    if not i:

                        # dummy method, not functional
                        _ = _series_to_array(data[col][:])

                    else:

                        # plot data per column
                        arr[:, i - 1], name = _series_to_array(data[col][:])

                        print()

                        od[name] = arr[:, i - 1]

        # append the data and the genre type (name of the folder) to a lst, for later plotting
        plot_lst.append((folder, od))

        # add classification in the final column
        if folder == 'lounge':
            arr[:, -1] = int(1)

        # append array to list for later concatenation to other songs
        lst.append(arr)

    # append arrays to export data
    for _, a in enumerate(lst):
        if not _:
            _a = a
        else:
            _a = np.concatenate((a, _a), 0)

    os.chdir('../')

    # export array data
    if not is_test:
        with open('feature_extraction/extraction_outputs/data_array.npy', 'wb') as f:
            np.save(f, _a)
    else:
        with open('feature_extraction/extraction_outputs/test_array.npy', 'wb') as f:
            np.save(f, _a)

    # plot the data only if the data is not from the validation
    if not is_test:
        plot_data(plot_lst, is_test)


def _series_to_array(series):
    """
    plot the column data
    :param series: panda Series object, containing all data per column
    :param folder: the folder containing the data
    :param is_test: bool, whether or not the data is for testing
    :return:
    """
    lst = []

    # iterate over datapoints in Series
    for item in series:

        # convert to float
        if series.name == 'dynamic_complexity' or series.name == 'bpm' or series.name == 'danceability':
            lst.append(float(item))

        # don't convert
        elif series.name == 'key_scale':
            lst.append(item)

        # title is not included
        elif series.name == 'title':
            continue

        else:
            lst.append(to_tuple(item))

    if not series.name == 'title':

        # create a list of datapoints
        if isinstance(lst[0], tuple):
            dots = [average for (average, variance) in lst]

        elif isinstance(lst[0], float):
            dots = lst

        # create dummy variable for major and minor modes
        elif isinstance(lst[0], str):
            name = 'mode'
            dots = []
            for song in lst:
                if song == 'major':
                    dots.append(1)
                if song == 'minor':
                    dots.append(0)

            dots = dots

        return dots, series.name


def plot_data(plot_lst, is_test=False):
    """
    plot and export the column data
    :param plot_lst: panda Series object, containing all data per column
    :param is_test: bool, whether or not the data is for testing
    """

    cols = ['barkbands_flatness_db', 'dissonance', 'dynamic_complexity', 'hfc', 'spectral_centroid',
            'bpm', 'danceability', 'key_scale']

    for col in cols:

        # column of the dataframe, and the genre (folder) of that dataframe data
        series_0 = plot_lst[0][1][col]
        folder_0 = plot_lst[0][0]

        series_1 = plot_lst[1][1][col]
        folder_1 = plot_lst[1][0]

        fig, ax = plt.subplots(1, 2)
        fig.set_size_inches(15, 9)

        # iterate over datapoints in Series and plot data for both of the series
        for row, (serie, folder) in enumerate([(series_0, folder_0), (series_1, folder_1)]):

            ax[row].plot(serie, 'x', color='black', label=col)

            # average
            average = np.average(serie)

            ax[row].hlines(y=average, xmin=0, xmax=len(serie) - 1, ls='-.', color='ghostwhite',
                            label='average {}'.format(col))

            ax[row].set_facecolor('cornflowerblue')
            ax[row].grid(linestyle=':', color='mintcream')
            ax[row].set_xlabel('song no.')

            ax[row].set_xlim(0, len(serie) - 1)

            ax[row].set_title(
                '{} from \'{}\' directory \n average ratio = {}'.format(col, folder, np.round(average, 2)))

            xticks = range(len(serie))
            xticks = xticks[::5]

            ax[row].set_xticks(ticks=xticks)
            # labels to string:
            labels = [str(index + 1) for index in xticks]
            ax[row].set_xticklabels(labels)

            # change y axis depending on the column
            if col == 'barkbands_flatness_db':
                ax[row].set_ylabel('Barkband flatness (ratio)')
                ax[row].set_ylim(0, 1)
            elif col == 'dissonance':
                ax[row].set_ylabel('Dissonance (ratio)')
                ax[row].set_ylim(0, 1)
            elif col == 'hfc':
                ax[row].set_ylabel('High-Frequency Coefficient')
            elif col == 'spectral_centroid':
                ax[row].set_ylabel('Spectral Centriod (Hz)')
                ax[row].set_ylim(0, 10000)
            elif col == 'dynamic_complexity':
                ax[row].set_ylabel('Dynamic Complexity (dB)')
                ax[row].set_ylim(0, 30)
            elif col == 'bpm':
                ax[row].set_ylabel('Beats per Minute (bpm)')
                ax[row].set_ylim(0, 300)
            elif col == 'danceability':
                ax[row].set_ylabel('Danceability')
                ax[row].set_ylim(0, 3)
            elif col == 'key_scale':
                ax[row].set_ylabel('Mode')
                ax[row].set_ylim(0, 1)
                ax[row].set_yticks([0, 0.25, 0.5, 0.75, 1])
                ax[row].set_yticklabels(['Minor', '', '', '', 'Major'])

            ax[row].legend()

        # export plot
        if not is_test:
            plt.tight_layout()
            plt.savefig('{}/extraction_outputs/prediction_plots/{}'.format(_dir, col))

        plt.close()
