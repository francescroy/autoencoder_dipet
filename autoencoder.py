


# NECESSARY IMPORTS

from sklearn.preprocessing import StandardScaler, LabelEncoder
import numpy as np
import os
import pandas as pd
import time
from tensorflow.keras.optimizers import Adam
from tensorflow import keras
import tensorflow as tf
import math
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from tensorflow.keras import layers, losses
from tensorflow.keras.models import Model
from kafka import KafkaConsumer



# NEURAL NETWORK DEFINITION

number_input_features = 45

class AnomalyDetector(Model):
    def __init__(self):
        super(AnomalyDetector, self).__init__()

        self.encoder = tf.keras.Sequential([
            layers.Dense(32, activation="relu", input_shape=(number_input_features,)),
            layers.Dense(16, activation="relu"),
            layers.Dense(8, activation="relu")])

        self.decoder = tf.keras.Sequential([
            layers.Dense(16, activation="relu", input_shape=(8,)),
            layers.Dense(32, activation="relu"),
            layers.Dense(number_input_features, activation="sigmoid")])  # NUMBER OF INPUT FEATURES

    def call(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

# CONVERTS MESSAGE FROM KAFKA TOPIC TO RECORD
def convert_to_trace(message_value):
    return message_value



if __name__ == "__main__":

    # READING THE DATASET

    df1 = pd.read_csv("/home/francesc/Escritorio/dataset_kaggle/MachineLearningCSV/MachineLearningCVE/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv")

    # PREPROCESSING

    # todo





    # SPLITING BETWEEN TRAIN AND TEST SET
    raw_data = [] # anomal and normal records, with a 1 o 0 label (last column)
    labels = raw_data[:, -1]
    data = raw_data[:, 0:-1]
    train_data, test_data, train_labels, test_labels = train_test_split(data, labels, test_size=0.2, random_state=21)




    # STANDARIZE THE DATA
    scaler = StandardScaler()
    train_data = scaler.fit_transform(train_data)
    test_data = scaler.transform(test_data)



    # SPLIT INTO NORMAL AND ANOMAL DATA (FOR TRAIN SET AND FOR TEST SET)
    train_labels = train_labels.astype(bool)
    test_labels = test_labels.astype(bool)
    normal_train_data = train_data[train_labels]
    normal_test_data = test_data[test_labels]
    anomalous_train_data = train_data[~train_labels]
    anomalous_test_data = test_data[~test_labels]



    # INITIALIZING AUTOENCODER
    autoencoder = AnomalyDetector()
    optimizer = Adam(learning_rate=0.001)
    autoencoder.compile(optimizer=optimizer, loss='mae') #or mse?

    # TRAINING
    history = autoencoder.fit(normal_train_data, normal_train_data,
          epochs=20,
          batch_size=512,
          validation_data=(test_data, test_data),
          shuffle=True)


    reconstructions = autoencoder.predict(normal_train_data)
    train_loss = tf.keras.losses.mae(reconstructions, normal_train_data) #or mse if we want to try...
    threshold = np.mean(train_loss) + np.std(train_loss)







    # INFERENCE

    #Each time a new record is consumed from kafka we predict (but before preprocess the trace, standarize it, etc...!!!)

    bootstrap_servers = ['localhost:9092']
    topic_name='network_traces'

    consumer = KafkaConsumer (topic_name,bootstrap_servers = bootstrap_servers)

    # START READING TOPIC
    for msg in consumer:

        new_trace = convert_to_trace(msg.value)

        reconstructions = autoencoder.predict(new_trace)
        test_loss = tf.keras.losses.mae(reconstructions, new_trace)
        if test_loss > threshold:
            print("ANOMALY! SO TALK TO PROMETHEUS!")



