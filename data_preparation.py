# native imports
import csv
# third party imports
import pandas as pd
import numpy as np


def import_csv(file_directory):
    """

    :param file_directory: string, directory to the file
    :return: a list with the .csv data
    """
    with open(file_directory, 'r') as file:
        reader = csv.reader(file)
        return list(reader)


def create_test_csv():
    """12 weeks, 12*7 = 84 days. 8 restaurants, 4 categories"""
    rest_exp = 8
    res_contr = 8

    weeks = 12
    no_days = weeks * 7

    no_obs_cat = no_days//4
    obs_per_cat = no_obs_cat * 8
    total_obs = obs_per_cat * 4

    mean_revenue = 106.83

    brand_fit_A = list(np.random.randint(low=mean_revenue-10, high=mean_revenue+10, size=obs_per_cat))
    brand_fit_B = list(np.random.randint(low=mean_revenue - 180, high=mean_revenue + 300, size=obs_per_cat))
    no_brand_fit = list(np.random.randint(low=mean_revenue - 90, high=mean_revenue - 30, size=obs_per_cat))
    no_music = list(np.random.randint(low=mean_revenue - 100, high=mean_revenue - 50, size=obs_per_cat))

    # brand_fit_A = [1, 20, 10000, 2, 1, 1, 30, 30000000, 1, -200, -1000000] * 21
    # brand_fit_B = [1, 2000000, 10000, 2, 1, 1, 1, 2] * 21
    # no_brand_fit = [1, 2000000, 1, 2, 10000000, 2, -100000, 1] * 21
    # no_music = [1, 2, 1, 2, -100000, 10000, -2000000, 1] * 21

    column_names = ['venue', 'values', 'treatment']
    values = brand_fit_A + brand_fit_B + no_brand_fit + no_music
    rest_rows = no_days * [rest for rest in range(8)]
    cat_lst = []
    for x in range(4):
        cat_lst += [x] * obs_per_cat

    if len(values) == len(rest_rows) and len(rest_rows) == len(cat_lst):
        print('test')

    with open('../static/client_data/dummy_data.csv', mode='w', newline='') as employee_file:
        employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        employee_writer.writerow(column_names)

        for row in range(total_obs):
            employee_writer.writerow([rest_rows[row], values[row], cat_lst[row]])


def csv_to_dataframe(file_directory, datalog):
    s = 'succesfully imported file with filename `{}`'.format(file_directory)
    datalog.write_line(s)
    return pd.read_csv(file_directory)


if __name__ == '__main__':
    create_test_csv()