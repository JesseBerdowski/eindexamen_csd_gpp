# native imports
import os
import time
import yaml
import csv
import queue

# local imports
from util import runtime_print, remove_spacebar_from_file


def batch_extractor_essentia(is_test=False):
    """
    batch extract features from audio files using the streaming_extractor_music command line executable,
    iterates over audio files in a folder. source:  https://essentia.upf.edu/streaming_extractor_music.html
    """

    # directory containing audio files
    dir_path = '{}/essentia_extraction'.format(os.path.dirname(os.path.realpath(__file__)))

    # change directory for running command line executable
    os.chdir(dir_path)

    lst_files = queue.Queue()

    if not is_test:
        maps = ['metal', 'lounge']
    else:
        maps = ['validate']

    for folder in maps:
        for x, file in enumerate(os.listdir('{}/songs/{}'.format(dir_path, folder))):
            # check if file is audio file
            if file.endswith('.wav') or file.endswith('.mp3'):

                # check if file contains spacebars
                if ' ' in file:
                    remove_spacebar_from_file(file, folder)

                # for developer messages
                start_time = time.time()

                # runs the streaming_extractor_music command line executable
                os.replace('{}/songs/{}/{}'.format(dir_path, folder, file), '{}/{}'.format(dir_path, file))
                os.system('streaming_extractor_music {} {}_features essentia_hparams.yaml'.format(file, file[:-4]))

                os.replace('{}/{}_features'.format(dir_path, file[:-4]),
                           '{}/songs/{}/{}_features'.format(dir_path, folder, file[:-4]))

                os.replace('{}/{}'.format(dir_path, file),
                           '{}/songs/{}/{}'.format(dir_path, folder, file))

                # prints runtime
                runtime_print(start_time)

    return lst_files


def features_to_csv(is_test=False):
    """
    dissect the feature extraction output file (in yaml format) to csv file. The file is contains several 'dictionaries
    within dictionaries', which explains the nested 'for' loops

    """
    rows = []
    column_names = []
    values = []

    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # bool that specifies writing the first row
    first_row = True

    # internal method for writing a list to .csv file
    def write_csv(lst):
        with open('extraction_outputs/batch_extracted_features_{}.csv'.format(folder), mode='w', newline='') as batch_extracted_features:
            csv_writer = csv.writer(batch_extracted_features, delimiter=',')
            for row in lst:
                csv_writer.writerow(row)

    if not is_test:
        maps = ['metal', 'lounge']
    else:
        maps = ['validate']

    _dir = 'essentia_extraction/songs/'
    for folder in maps:

        # iterate over files in directory
        for file in os.listdir('{}/{}'.format(_dir, folder)):

            # the yaml files containing the features end with '_features'
            if file.endswith('_features'):
                with open('{}/{}/{}'.format(_dir, folder, file)) as f:
                    documents = yaml.full_load(f)

                    # first dictionary iteration, only contains description of features, no values
                    for item, doc in documents.items():

                        # the 'metadata' dictionary doesn't contain relevant data except for the title, so isn't used
                        if item == 'metadata':
                            for i, d in doc.items():
                                if i == 'tags':
                                    for ii, dd in d.items():
                                        if ii == 'file_name':
                                            title = dd[:-4]

                        elif item == 'lowlevel':

                            for i, d in doc.items():

                                if i == 'barkbands_flatness_db' \
                                        or i == 'dissonance'\
                                        or i == 'hfc'\
                                        or i == 'spectral_centroid':
                                    [mean, var] = [dd for ii, dd in d.items()]
                                    values.append((round(mean, 3), round(var, 3)))
                                    column_names.append(i)

                                elif i == 'dynamic_complexity':
                                    values.append(d)
                                    column_names.append(i)

                        elif item == 'rhythm':

                            for i, d in doc.items():

                                if i == 'danceability' or i == 'bpm':
                                    values.append(round(d, 3))
                                    column_names.append(i)

                        elif item == 'tonal':

                            for i, d in doc.items():

                                if i == 'key_scale':

                                    values.append(d)
                                    column_names.append(i)

                # if first_row == True, add the 'items' row (the names of the columns) aka the extracted features
                if first_row:
                    column_names.insert(0, 'title')
                    rows.append(column_names)
                    first_row = False
                    column_names = []

                # add the 'values' row (the values of the features for the particular audio file)
                values.insert(0, title)
                rows.append(values)

                # reset the row. the row is now ready for the next iteration
                values = []
        # write the list of rows to a .csv file
        write_csv(rows)
        rows = []
        column_names = []
        first_row = True
