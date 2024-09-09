# Telerehabilitation Gloves
This document contains information related to important files and folders of the project.
## 1. CloudModel Results
### 1.1. ConfusionMatrix
It includes accuracy results and confusion matrices.
### 1.2. Index
Predictions and actual labels of the test set for models trained in the Cloud for the index finger.
### 1.3. Middle
Predictions and actual labels of the test set for models trained in the Cloud for the middle finger.
### 1.4. Pinkie
Predictions and actual labels of the test set for models trained in the Cloud for the pinkie finger.
### 1.5. Ring
Predictions and actual labels of the test set for models trained in the Cloud for the ring finger.
### 1.6. Thumb
Predictions and actual labels of the test set for models trained in the Cloud for the thumb finger.
### 1.7. RecreateConfusionMatrices.py
A script that generates results based on the predicted and actual labels.
 
## 2. DataAnalysis
This project visualizes traffic generator results.
### 2.1. ProcessedResults
Article chart results
### 2.2. Results
Raw results
### 2.3. Main.py
It processes the raw results and saves them in the ProcessedResults folder.

## 3. DatasetEditor
This project has the GUI for editing the test subject data.
### 3.1. DataPlotter
Plot each data in "./Data/" folder.
### 3.2. DatasetEditor.py
GUI script for data editor. It edits the data under './Data/' folder.
### 3.3. run.command
Start script for MacOS.

## 4. GloveCloudApplication
Cloud applications for prediction and communication systems.

### 4.1. FingerPhasePredictor
Prediction program of the project.
#### 4.1.1. Data
The data was collected from test subjects. It is used for train and test. The GloveTrafficGenerator also uses these files to test the cloud.
#### 4.1.2. Model 
The model was trained in the cloud and used for performance tests.
#### 4.1.2. main.py
The main file of the prediction file. 

### 4.2. Resource Manager
The resource monitor of the system. It is used to monitor CPU, Memory, and Network Bandwidth usage of the system.

### 4.3. Server.js
The main file of the communication module of the cloud system.

### 4.4. Run.sh
The script for starting the communication, prediction, and resource monitoring programs.

## 5. GloveLabellingSystem
The program for the data acquisition system.
### 5.1. main.py
The GUI for Windows OS.
### 5.2. main_mac.py
The GUI for MacOS.

## 6. GloveRealTimeApplication
This project collects data from the sensing IoT gloves and transmits it to the cloud. It also contains a patient connection script.
### 6.1 main.py
The GUI for getting data from the sensing IoT glove. It also communicates with the cloud server for therapy.
### 6.2 Patient.py
This script is an interface with the control system of an actuating IoT glove and the cloud.

## 7.GloveTrafficGenerator
This project reads the stored data and sends them to the cloud to extract time analysis of the cloud.
### 7.1. Main.py
This script sends data to the cloud at a frequency of 50 Hz using the given model as an argument and records data related to time and resource usage metrics. Each time the script is run, it tests the system with a file that has not been used before. Once all files have been used, the script does not initiate a new test for the corresponding model.
### 7.2. Run_Models.bat Files
This script runs the traffic generator for all test subject data.

## 8. SoftSensorsLiveChart
This project illustrates the sensing IoT Glove sensor data via GloveLabellingSystem in real time.

## Contact Information
Please do not hesitate to contact Kadir Ozlem ([kadir.ozlem@itu.edu.tr](mailto:kadir.ozlem@itu.edu.tr)) for further questions.

