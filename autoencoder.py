


# NECESSARY IMPORTS

from sklearn.preprocessing import StandardScaler, LabelEncoder
import numpy as np # linear algebra
import os # accessing directory structure
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import time
from tensorflow.keras.optimizers import Adam
from tensorflow import keras
import tensorflow as tf
import math
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from tensorflow.keras import layers, losses
from tensorflow.keras.models import Model


# NEURAL NETWORK DEFINITION

class AnomalyDetector(Model):
    def __init__(self):
        super(AnomalyDetector, self).__init__()

        self.encoder = tf.keras.Sequential([
            layers.Dense(32, activation="relu", input_shape=(45,)),
            layers.Dense(16, activation="relu"),
            layers.Dense(8, activation="relu")])

        self.decoder = tf.keras.Sequential([
            layers.Dense(16, activation="relu", input_shape=(8,)),
            layers.Dense(32, activation="relu"),
            layers.Dense(45, activation="sigmoid")])  # NUMBER OF INPUT FEATURES

    def call(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded




# READING THE DATASET

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

df1 = pd.read_csv("/home/francesc/Escritorio/dataset_kaggle/MachineLearningCSV/MachineLearningCVE/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv")
df2=pd.read_csv("/home/francesc/Escritorio/dataset_kaggle/MachineLearningCSV/MachineLearningCVE/Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv")
df3=pd.read_csv("/home/francesc/Escritorio/dataset_kaggle/MachineLearningCSV/MachineLearningCVE/Friday-WorkingHours-Morning.pcap_ISCX.csv")
df4=pd.read_csv("/home/francesc/Escritorio/dataset_kaggle/MachineLearningCSV/MachineLearningCVE/Monday-WorkingHours.pcap_ISCX.csv")
df5=pd.read_csv("/home/francesc/Escritorio/dataset_kaggle/MachineLearningCSV/MachineLearningCVE/Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv")
#df6=pd.read_csv("/home/francesc/Escritorio/dataset_kaggle/MachineLearningCSV/MachineLearningCVE/Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv")
#df7=pd.read_csv("/home/francesc/Escritorio/dataset_kaggle/MachineLearningCSV/MachineLearningCVE/Tuesday-WorkingHours.pcap_ISCX.csv")
#df8=pd.read_csv("/home/francesc/Escritorio/dataset_kaggle/MachineLearningCSV/MachineLearningCVE/Wednesday-workingHours.pcap_ISCX.csv")

# CONCATENING ALL THE DATASETS FROM EVERY DAY

df = pd.concat([df1,df2])
del df1,df2
df = pd.concat([df,df3])
del df3
df = pd.concat([df,df4])
del df4
df = pd.concat([df,df5])
del df5
#df = pd.concat([df,df6]) # its not necessary to use them all...
#del df6
#df = pd.concat([df,df7])
#del df7
#df = pd.concat([df,df8])
#del df8
nRow, nCol = df.shape




## PREPROCESSING

# todo

## END PREPROCESSING

raw_data = [] # anomal and normal records, with a 1 o 0 label (last column)

labels = raw_data[:, -1]

data = raw_data[:, 0:-1]

train_data, test_data, train_labels, test_labels = train_test_split(data, labels, test_size=0.2, random_state=21)


#Correct? Normalize the data
scaler = StandardScaler()
train_data = scaler.fit_transform(train_data)
test_data = scaler.transform(test_data)
#Correct?



train_labels = train_labels.astype(bool)
test_labels = test_labels.astype(bool)
normal_train_data = train_data[train_labels]
normal_test_data = test_data[test_labels]
anomalous_train_data = train_data[~train_labels]
anomalous_test_data = test_data[~test_labels]









autoencoder = AnomalyDetector()
optimizer = Adam(learning_rate=0.001)
autoencoder.compile(optimizer=optimizer, loss='mae') #or mse?

history = autoencoder.fit(normal_train_data, normal_train_data,
          epochs=20,
          batch_size=512,
          validation_data=(test_data, test_data),
          shuffle=True)


reconstructions = autoencoder.predict(normal_train_data)
train_loss = tf.keras.losses.mae(reconstructions, normal_train_data) #or mse?
threshold = np.mean(train_loss) + np.std(train_loss)






###############################################
###############################################
########### KAFKA CONNECTION ##################
###############################################
###############################################

# todo

#Each time a new record is consumed from kafka we predict (but before preprocess the trace!!!)
#reconstructions = autoencoder.predict(new_trace)
#test_loss = tf.keras.losses.mae(reconstructions, new_trace)
#if test_loss < threshold:
#   ANOMALY! TALK TO PROMETHEUS!


#from kafka import KafkaConsumer

#consumer = KafkaConsumer('streams-plaintext-input')

#for msg in consumer:
#    print (msg.value)
#    if msg.value == 'ja':
#        break
