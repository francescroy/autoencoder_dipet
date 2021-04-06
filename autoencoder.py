


# NECESSARY IMPORTS

from sklearn.preprocessing import StandardScaler, LabelEncoder
import numpy as np
import os
import pandas as pd
from tensorflow.keras.optimizers import Adam
from tensorflow import keras
import tensorflow as tf
import math
import time
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from tensorflow.keras import layers, losses
from tensorflow.keras.models import Model
from kafka import KafkaConsumer
from preprocessing import *


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


def preprocessing(df):
    df.insert(4, "TCP", 0)
    df.insert(5, "UDP", 0)
    df.insert(6, "ICMP", 0)
    df.insert(7, "GRE", 0)
    df.insert(8, "OTHER", 0)

    df["TCP"] = df["ip_proto"].apply(setTCP)
    df["UDP"] = df["ip_proto"].apply(setUDP)
    df["ICMP"] = df["ip_proto"].apply(setICMP)
    df["GRE"] = df["ip_proto"].apply(setGRE)
    df["OTHER"] = df["ip_proto"].apply(setOTHER)

    del df['ip_proto']

    df["port_src"] = df["port_src"].apply(setWellKnownPort)
    df["port_dst"] = df["port_dst"].apply(setWellKnownPort)

    df.insert(16, "avarage_packet_size", 0)
    df["avarage_packet_size"] = df["bytes"] / df["packets"]

    df.insert(3, "NS", 0)
    df.insert(4, "CWR", 0)
    df.insert(5, "ECE", 0)
    df.insert(6, "URG", 0)
    df.insert(7, "ACK", 0)
    df.insert(8, "PSH", 0)
    df.insert(9, "RST", 0)
    df.insert(10, "SYN", 0)
    df.insert(11, "FIN", 0)

    df["NS"] = df["tcp_flags"].apply(setNS)
    df["CWR"] = df["tcp_flags"].apply(setCWR)
    df["ECE"] = df["tcp_flags"].apply(setECE)
    df["URG"] = df["tcp_flags"].apply(setURG)
    df["ACK"] = df["tcp_flags"].apply(setACK)
    df["PSH"] = df["tcp_flags"].apply(setPSH)
    df["RST"] = df["tcp_flags"].apply(setRST)
    df["SYN"] = df["tcp_flags"].apply(setSYN)
    df["FIN"] = df["tcp_flags"].apply(setFIN)

    del df['tcp_flags']



    return df




if __name__ == "__main__":

    # READING THE DATASET

    df = pd.read_csv(os.path.dirname(os.path.realpath(__file__))+"/nftraces.csv")
    df = preprocessing(df)



    # SPLITING BETWEEN TRAIN AND TEST SET
    data = [] # normal records

    train_data, test_data = train_test_split(data, test_size=0.2, random_state=21)




    # STANDARIZE THE DATA
    scaler = StandardScaler()
    train_data = scaler.fit_transform(train_data)
    test_data = scaler.transform(test_data)
    ##zero mean and unit variance
    # df["bytes"] = (df["bytes"] - df["bytes"].mean()) / df["bytes"].std()
    # df["packets"] = (df["packets"] - df["packets"].mean()) / df["packets"].std()
    # df["avarage_packet_size"] = (df["avarage_packet_size"] - df["avarage_packet_size"].mean()) / df["avarage_packet_size"].std()




    # INITIALIZING AUTOENCODER
    autoencoder = AnomalyDetector()
    optimizer = Adam(learning_rate=0.001)
    autoencoder.compile(optimizer=optimizer, loss='mae') #or mse?

    # TRAINING
    history = autoencoder.fit(train_data, train_data,
          epochs=20,
          batch_size=512,
          validation_data=(test_data, test_data),
          shuffle=True)


    reconstructions = autoencoder.predict(train_data)
    train_loss = tf.keras.losses.mae(reconstructions, train_data) #or mse if we want to try...
    threshold = np.mean(train_loss) + np.std(train_loss)







    # INFERENCE

    #Each time a new record is consumed from kafka we predict (but before preprocess the trace, standarize it, etc...!!!)

    bootstrap_servers = ['localhost:9092']
    topic_name='network_traces'

    consumer = KafkaConsumer (topic_name,bootstrap_servers = bootstrap_servers)

    # START READING TOPIC
    for msg in consumer:

        new_trace = convert_to_trace(msg.value)

        new_trace = preprocessing(new_trace)
        new_trace = scaler.transform(new_trace)

        reconstructions = autoencoder.predict(new_trace)
        test_loss = tf.keras.losses.mae(reconstructions, new_trace)
        if test_loss > threshold:
            print("ANOMALY! SO TALK TO PROMETHEUS!")





## PROVAR CON DIFERENTES AUTOENCODERS....!!!! CON MAS O CON MENOS PARAMETROS... TRANSPRECISEEEE!