import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from util import export_history

class Model:
    def __init__(self, data, lst_files=None, is_test=False):
        """
        class that trains and exports model

        :param train: numpy array, input data
        :param test: numpy array, output data (value of the tag)
        :returns bool, whether training was successful
        """
        self.is_test = is_test

        self.lst_file = lst_files

        self.x, self.y = self._prepare_data(data)

        self.model = tf.keras.models.Sequential([
                                                  tf.keras.layers.Dense(512, activation='relu'),
                                                  tf.keras.layers.Dropout(0.28),
                                                  tf.keras.layers.Dense(2)
                                                ])

        self.loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)

    @staticmethod
    def _prepare_data(data):
        """
        prepares data for training or testing, creates a array of classifications and an array of data

        :return: x and y are data and classifications per song for training, X and Y for validation
        """
        np.random.shuffle(data)

        x = data[:, :-1]
        y = data[:, -1]

        return x, y

    def run_model(self):
        """
        run the model based on class parameters

        """

        if not self.is_test:
            _ = self.model(self.x)
            self.model.compile(optimizer='adam', loss=self.loss, metrics=['accuracy'])

            checkpoint_path = "static/checkpoint_data/pretrained_model.ckpt"

            # Create a callback that saves the model's weights
            cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
                                                             save_weights_only=True,
                                                             save_best_only=True,
                                                             monitor='accuracy',
                                                             verbose=2)

            history = self.model.fit(x=self.x, y=self.y, epochs=1000, callbacks=[cp_callback])
            export_history(history.history)

        else:
            # load checkpoint weights
            self.model.load_weights("static/checkpoint_data/pretrained_model.ckpt").expect_partial()
            self.model.compile(optimizer='adam', loss=self.loss, metrics=['accuracy'])

            # run probability validation
            probability_model = tf.keras.Sequential([self.model, tf.keras.layers.Softmax()])
            predictions = probability_model.predict(self.x)

            # visualize predictions
            self.visualise_predictions(predictions)

    def visualise_predictions(self, preds):
        """
        visualizes and exports a prediction

        :param preds: classification prediction per song
        :return:
        """

        for i, prediction in enumerate(preds):
            x = range(len(prediction))
            plt.bar(x, height=prediction)
            class_names = ['metal', 'lounge']
            plt.xticks([0, 1], class_names, rotation=45)
            plt.title('Prediction')
            plt.ylabel('probability')
            plt.xlabel('genre')

            plt.savefig('model_training/prediction_plots/prediction_{}'.format(i))
            plt.close()
