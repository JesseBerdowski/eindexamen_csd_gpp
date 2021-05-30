# local imports
from util import import_numpy
from model_training.model_training import Model

if __name__ == '__main__':
    train = import_numpy()
    model_training = Model(train, False)
    model_training.run_model()