import data_preparation


class HyperParameters:
    def __init__(self, data_log, h_file):
        csv = data_preparation.import_csv(h_file)
        hps_dict = dict()

        for i in range(len(csv[0])):
            hps_dict[csv[0][i]] = csv[1][i]
        i = []
        for item, value in hps_dict.items():
            if item == 'no_venues':
                i.append(item)
                self.no_rests = int(hps_dict[item])
            if item == 'bootstrap_n':
                i.append(item)
                self.bootstrap_n = int(hps_dict[item])
            if item == 'placebo_n':
                i.append(item)
                self.placebo_n = int(hps_dict[item])
            if item == 'no_treatments':
                i.append(item)
                self.treatments = list(range(int(hps_dict[item])))
            if item == 'filename':
                i.append(item)
                self.filename = hps_dict[item]

        for item in i:
            if item not in ['no_venues', 'bootstrap_n', 'placebo_n', 'no_treatments', 'filename']:
                print('Error importing Hyperparameters')
                exit()

        data_log.write_line('Succesfully imported Hyperparameters from file `static/hparams/hparams` ')