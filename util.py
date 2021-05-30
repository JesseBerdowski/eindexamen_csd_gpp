# local imports
import time
import yaml
import json
import numpy as np
import os


def yaml_import(file_directory):
    with open(file_directory) as f:
        return yaml.full_load(f)


def write_json(json_data, file_name):
    with open('../static/{}.json'.format(file_name), 'w') as f:
        json.dump(json_data, f)


def load_json(file_name):
    with open('../static/{}.json'.format(file_name)) as json_file:
        return json.load(json_file)


def runtime_print(start_time):
    end_time = time.time()
    print('total run time: {} sec'.format(round(end_time - start_time, 2)))


def to_tuple(item):
    item = item.replace(',', '')
    item = item.replace('(', '')
    item = item.replace(')', '')

    item = item.split(' ')

    # create tuple from the two separate strings
    return float(item[0]), float(item[1])


def import_numpy(is_test=False):
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    if not is_test:
        with open('feature_extraction/extraction_outputs/data_array.npy', 'rb') as f:
            data = np.load(f)
            return data
    else:
        with open('feature_extraction/extraction_outputs/test_array.npy', 'rb') as g:
            data = np.load(g)
            return data


def remove_spacebar_from_file(file, folder):
    dir_path = '{}/feature_extraction/essentia_extraction/{}'.format(os.path.dirname(os.path.realpath(__file__)), folder)
    os.chdir(dir_path)
    file_nospace = file.replace(" ", "")
    os.rename(file, file_nospace)


def export_history(history):
    lowest_losses = []
    lowest_loss = 0
    highest_accs = []
    highest_acc = 0

    for _, loss in enumerate(history['loss']):
        if _:
            if loss < lowest_loss:
                lowest_loss = loss
                lowest_losses.append('epoch: {}, lowest loss: {}'.format(_, round(lowest_loss, 3)))

        else:
            lowest_loss = loss
            lowest_losses.append('epoch: {}, lowest loss: {}'.format(_, round(lowest_loss, 3)))

    for _, acc in enumerate(history['accuracy']):
        if _:
            if acc > highest_acc:
                highest_acc = acc
                highest_accs.append('epoch: {}, highest accuracy: {}'.format(_, round(highest_acc, 7)))

        else:
            highest_acc = acc
            highest_accs.append('epoch: {}, highest accuracy: {}'.format(_, round(highest_acc, 7)))

    f = open("static/training_results.txt", "w+")

    for i, acc in enumerate(highest_accs):
        if not i:
            f.write('Highest accuracy history: \n')
        else:
            f.write('{}\n'.format(acc))

    for i, loss in enumerate(lowest_losses):
        if not i:
            f.write('\nHighest loss history: \n')
        else:
            f.write('{}\n'.format(loss))

    f.close()


