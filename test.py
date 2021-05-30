# local imports
from util import import_numpy
from model_training.model_training import Model
from feature_extraction.feature_extraction import features_to_csv, batch_extractor_essentia
from feature_extraction.feature_exports import export_csv_data

if __name__ == '__main__':
    batch_extractor_essentia(is_test=True)
    features_to_csv(is_test=True)
    export_csv_data(is_test=True)
    test = import_numpy(is_test=True)
    model_training = Model(test, is_test=True)
    model_training.run_model()
