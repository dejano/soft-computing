# coding=utf-8
# Plot ad hoc mnist instances

import os
from keras.datasets import mnist
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers.normalization import BatchNormalization
from keras.models import Sequential, load_model
from keras.optimizers import SGD, Adam
from keras.preprocessing.image import ImageDataGenerator
from keras.utils import np_utils


def create_model_2():
    # Three steps to Convolution
    # 1. Convolution
    # 2. Activation
    # 3. Polling
    # Repeat Steps 1,2,3 for adding more hidden layers

    # 4. After that make a fully connected network
    # This fully connected network gives ability to the CNN
    # to classify the samples

    model = Sequential()

    model.add(Conv2D(32, (3, 3), input_shape=(28, 28, 1)))
    model.add(Activation('relu'))
    BatchNormalization(axis=-1)
    model.add(Conv2D(32, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    BatchNormalization(axis=-1)
    model.add(Conv2D(64, (3, 3)))
    model.add(Activation('relu'))
    BatchNormalization(axis=-1)
    model.add(Conv2D(64, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Flatten())
    # Fully connected layer

    BatchNormalization()
    model.add(Dense(512))
    model.add(Activation('relu'))
    BatchNormalization()
    model.add(Dropout(0.2))
    model.add(Dense(10))

    # model.add(Convolution2D(10,3,3, border_mode='same'))
    # model.add(GlobalAveragePooling2D())
    model.add(Activation('softmax'))

    model.summary()

    model.compile(loss='categorical_crossentropy', optimizer=Adam(), metrics=['accuracy'])

    return model


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
    x_train = x_train.reshape(x_train.shape[0], 28, 28, 1).astype('float32')
    x_test = x_test.reshape(x_test.shape[0], 28, 28, 1).astype('float32')

    # normalize inputs 0-255 -> 0-1
    x_train = x_train / 255
    x_test = x_test / 255

    # one hot encode outputs
    number_of_classes = 10
    y_train = np_utils.to_categorical(y_train, number_of_classes)
    y_test = np_utils.to_categorical(y_test, number_of_classes)

    # model = create_model(number_of_pixels, number_of_classes)
    model = create_model_2()

    batch_size = 64
    epochs = 5

    gen = ImageDataGenerator(rotation_range=20, width_shift_range=0.3, shear_range=0.3,
                             height_shift_range=0.3, zoom_range=0.3)

    test_gen = ImageDataGenerator()

    train_generator = gen.flow(x_train, y_train, batch_size=64)
    test_generator = test_gen.flow(x_test, y_test, batch_size=64)

    model.fit_generator(train_generator, steps_per_epoch=60000 // 64, epochs=5,
                        validation_data=test_generator, validation_steps=10000 // 64)

    # model.fit(x_train, y_train, epochs=20, batch_size=8, verbose=2, shuffle=False)
    persist(model, 'conv-45-e.1')

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
