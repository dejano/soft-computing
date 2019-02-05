# coding=utf-8
# Plot ad hoc mnist instances
import os

from keras.datasets import mnist
from keras.engine.saving import load_model
from keras.layers.core import Dense
from keras.models import Sequential
from keras.optimizers import SGD
from keras.utils import np_utils


def create_model(input_dim, number_of_classes):
    model = Sequential()
    model.add(Dense(800, input_dim=input_dim, activation='sigmoid'))
    model.add(Dense(number_of_classes, activation='sigmoid'))
    sgd = SGD(lr=2)
    model.compile(loss='mean_squared_error', optimizer=sgd, metrics=['accuracy'])
    return model


def train_and_persist():
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    # reshape to be [samples][pixels][width][height]
    number_of_pixels = x_train.shape[1] * x_train.shape[2]
    x_train = x_train.reshape(x_train.shape[0], number_of_pixels).astype('float32')
    x_test = x_test.reshape(x_test.shape[0], number_of_pixels).astype('float32')

    # normalize inputs 0-255 -> 0-1
    x_train = x_train / 255
    x_test = x_test / 255

    # one hot encode outputs
    number_of_classes = 10
    y_train = np_utils.to_categorical(y_train, number_of_classes)
    y_test = np_utils.to_categorical(y_test, number_of_classes)

    model = create_model(number_of_pixels, number_of_classes)
    model.fit(x_train, y_train, epochs=20, batch_size=8, verbose=2, shuffle=False)
    persist(model)

    scores = model.evaluate(x_test, y_test, verbose=0)
    print scores
    print("CNN Error: %.2f%%" % (100 - scores[1] * 100))


def persist(model, name='keras_mnist'):
    save_dir = "./models/"
    model_name = '%s.h5' % name
    model_path = os.path.join(save_dir, model_name)
    model.save(model_path)
    print('Saved trained model at %s ' % model_path)


def load(name='keras_mnist'):
    save_dir = "./models/"
    model_name = '%s.h5' % name
    model_path = os.path.join(save_dir, model_name)
    return load_model(model_path)
