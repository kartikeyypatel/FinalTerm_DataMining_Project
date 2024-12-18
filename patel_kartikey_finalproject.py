# -*- coding: utf-8 -*-
"""Patel_Kartikey_FinalProject.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1oA0nIp8wse3qC_xnoAOuZzjf3FVOlVRV

# Importing The Libraries
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score, brier_score_loss
from keras.models import Sequential
from keras.layers import Conv1D, MaxPooling1D, Flatten, Dense
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from keras.layers import LSTM
from sklearn.metrics import roc_curve, auc
import tensorflow as tf

"""# Load The Data set"""

# Load dataset
data = pd.read_csv('raisin_varieties.csv')

data.head()

data.info()

data.Class.value_counts()

label_enc = LabelEncoder()
data['Class'] = label_enc.fit_transform(data['Class'])

data.head()

"""# Checking missing values"""

print(data.isnull().sum())

"""# Spliting the features and labels"""

# Split features and labels
features = data.drop(columns=['Class'])
labels = data['Class']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42, stratify=labels)

# Standardize the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

"""# Data Visualisation"""

df = pd.DataFrame(data)

# Value counts of the target variable
class_counts = df['Class'].value_counts()

# Bar plot
plt.figure(figsize=(8, 5))
sns.barplot(x=class_counts.index, y=class_counts.values)
plt.xlabel('Class', fontsize=15)
plt.ylabel('Count', fontsize=15)
plt.title('Distribution of Classes', fontsize=15)
plt.show()

# Plot histograms for each feature (excluding the target variable)
features = df.columns[:-1]  # Exclude the last column ('Class')

plt.figure(figsize=(15, 10))
for i, feature in enumerate(features, 1):
    plt.subplot(3, 3, i)  # Adjust rows and columns based on the number of features
    plt.hist(df[feature], bins=10, color='skyblue', edgecolor='black')
    plt.title(feature, fontsize=12)
    plt.xlabel('Value', fontsize=10)
    plt.ylabel('Frequency', fontsize=10)

plt.tight_layout()
plt.show()

# Generate pairplot
sns.pairplot(data, hue='Class')  # Exclude the target variable 'Class' for pairwise comparison
plt.show()

# Set up figure
plt.figure(figsize=(10, 8))

# Draw correlation matrix
sns.heatmap(data.corr(), annot=True, cmap='Spectral', fmt=".2f", linewidths=.5)

# Show the figure
plt.title('Correlation Matrix')
plt.show()

# describing dataset
data.describe()

"""# Evaluation of Confusion matrix"""

def calc_metrics(confusion_matrix):
    TP, FN = confusion_matrix[0][0], confusion_matrix[0][1]
    FP, TN = confusion_matrix[1][0], confusion_matrix[1][1]
    TPR = TP / (TP + FN)
    TNR = TN / (TN + FP)
    FPR = FP / (TN + FP)
    FNR = FN / (TP + FN)
    Precision = TP / (TP + FP)
    F1_measure = 2 * TP / (2 * TP + FP + FN)
    Accuracy = (TP + TN) / (TP + FP + FN + TN)
    Error_rate = (FP + FN) / (TP + FP + FN + TN)
    BACC = (TPR + TNR) / 2
    TSS = TPR - FPR
    HSS = 2 * (TP * TN - FP * FN) / ((TP + FN) * (FN + TN) + (TP + FP) * (FP + TN))
    metrics = [TP, TN, FP, FN, TPR, TNR, FPR, FNR, Precision, F1_measure, Accuracy, Error_rate, BACC, TSS, HSS]
    return metrics

from sklearn.metrics import confusion_matrix, roc_auc_score, brier_score_loss

def get_metrics(model, X_train, X_test, y_train, y_test, LSTM_flag):
    metrics = []

    if LSTM_flag == 1:
        # Convert data to numpy array
        Xtrain, Xtest, ytrain, ytest = map(np.array, [X_train, X_test, y_train, y_test])
        # Reshape data
        shape = Xtrain.shape
        Xtrain_reshaped = Xtrain.reshape(len(Xtrain), shape[1], 1)
        Xtest_reshaped = Xtest.reshape(len(Xtest), shape[1], 1)
        model.fit(Xtrain_reshaped, ytrain, epochs=50, validation_data=(Xtest_reshaped, ytest), verbose=0)
        lstm_scores = model.evaluate(Xtest_reshaped, ytest, verbose=0)
        predict_prob = model.predict(Xtest_reshaped)
        pred_labels = predict_prob > 0.5
        pred_labels_1 = pred_labels.astype(int)
        matrix = confusion_matrix(ytest, pred_labels_1, labels=[1, 0])
        lstm_brier_score = brier_score_loss(ytest, predict_prob)
        lstm_roc_auc = roc_auc_score(ytest, predict_prob)
        metrics.extend(calc_metrics(matrix))
        metrics.extend([lstm_brier_score, lstm_roc_auc, lstm_scores[1]])

    elif LSTM_flag == 0:
        model.fit(X_train, y_train)
        predicted = model.predict(X_test)
        matrix = confusion_matrix(y_test, predicted, labels=[1, 0])
        model_brier_score = brier_score_loss(y_test, model.predict_proba(X_test)[:, 1])
        model_roc_auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
        metrics.extend(calc_metrics(matrix))
        metrics.extend([model_brier_score, model_roc_auc, model.score(X_test, y_test)])

    return metrics

"""# Random Forest Classifier Model Training"""

# build the model
rfModel = RandomForestClassifier(random_state=42)

# Fit the model
rfModel.fit(X_train, y_train)

# Make predictions
rf_pred = rfModel.predict(X_test)

# accuracy
rf_accuracy = accuracy_score(y_test, rf_pred)*100
print(f"Accuracy without CV: {rf_accuracy:.2f}")

param_grid = {
    "n_estimators": [10, 20, 30, 40, 50, 60, 100],
    "min_samples_split": [2, 4, 6, 8, 10]
}

# Create grid search
rf_gridsearch = GridSearchCV(estimator=rfModel,param_grid=param_grid, cv=10, scoring='accuracy',n_jobs=-1)

# Fit grid search
rf_gridsearch.fit(X_train, y_train)

rf_best_params = rf_gridsearch.best_params_
best_estimator = rf_gridsearch.best_estimator_

print(f"Best Parameters : {rf_best_params}")
print(f"Best Estimator  : {best_estimator}")

min_samples_split = rf_gridsearch.best_params_['min_samples_split']
n_estimators = rf_gridsearch.best_params_['n_estimators']
rf_pred_CV = best_estimator.predict(X_test)
rf_accuracy_cv = accuracy_score(y_test, rf_pred_CV)*100
print(f"Best Accuracy: {rf_accuracy_cv:.2f}")
print(f"Random Forest accuracy without CV : {rf_accuracy:.2f}")
print(f"Random Forest accuracy with CV    : {rf_accuracy_cv:.2f}")

"""# KNN Classifier Algorithm Implementation"""

#Define KNN parameters for grid search
knn_parameters = {"n_neighbors": [2, 3, 4, 6, 8, 10, 12, 15]}
# Create KNN model
knn_model = KNeighborsClassifier()
# Perform grid search with cross-validation
knn_cv = GridSearchCV(knn_model, knn_parameters, cv=10, n_jobs=-1)
knn_cv.fit(X_train_scaled, y_train)
# Print the best parameters found by GridSearchCV
print("\nBest Parameters for KNN based on GridSearchCV: ", knn_cv.best_params_)
best_n_neighbors = knn_cv.best_params_['n_neighbors']

"""# LSTM Model Implementation & Using 10 fold Cross Validation"""

from sklearn.model_selection import StratifiedKFold

features = df.drop(columns=['Class'])  # Drop the target column to keep only the features
labels = df['Class']  # Target variable should be the 'Class' column


# Define Stratified K-Fold cross-validator
cv_stratified = StratifiedKFold(n_splits=10, shuffle=True, random_state=21)

# Initialize metric columns
metric_columns = ['TP', 'TN', 'FP', 'FN', 'TPR', 'TNR', 'FPR', 'FNR',
                  'Precision', 'F1_measure', 'Accuracy', 'Error_rate',
                  'BACC', 'TSS', 'HSS', 'Brier_score', 'AUC', 'Acc_by_package_fn']

# Initialize metrics lists for each algorithm
knn_metrics_list, rf_metrics_list, lstm_metrics_list = [], [], []

# 10 Iterations of 10-fold cross-validation
for iter_num, (train_index, test_index) in enumerate(cv_stratified.split(features, labels), start=1):
    # KNN Model
    knn_model = KNeighborsClassifier(n_neighbors=best_n_neighbors)
    # Random Forest Model
    rf_model = RandomForestClassifier(min_samples_split=min_samples_split, n_estimators=n_estimators)
    # LSTM model
    lstm_model = Sequential()
    lstm_model.add(LSTM(64, activation='relu', return_sequences=False))
    lstm_model.add(Dense(1, activation='sigmoid'))
    # Compile model
    lstm_model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])


    # Get metrics for each algorithm
    knn_metrics = get_metrics(knn_model, X_train, X_test, y_train, y_test, 0)
    rf_metrics = get_metrics(rf_model, X_train, X_test, y_train, y_test, 0)
    lstm_metrics = get_metrics(lstm_model, X_train, X_test, y_train, y_test, 1)

    # Append metrics to respective lists
    knn_metrics_list.append(knn_metrics)
    rf_metrics_list.append(rf_metrics)
    lstm_metrics_list.append(lstm_metrics)

    # Create a DataFrame for all metrics
    metrics_all_df = pd.DataFrame([knn_metrics, rf_metrics, lstm_metrics],
                                  columns=metric_columns,
                                  index=['KNN', 'RF', 'LSTM'])

    # Display metrics for all algorithms in each iteration
    print('\nIteration {}: \n'.format(iter_num))
    print('\n----- Metrics for all Algorithms in Iteration {} -----\n'.format(iter_num))
    print(metrics_all_df.round(decimals=2).T)
    print('\n')

# Initialize metric index for each iteration
metric_index_df = ['iter1', 'iter2', 'iter3', 'iter4', 'iter5', 'iter6', 'iter7', 'iter8', 'iter9', 'iter10']

# Create DataFrames for each algorithm's metrics
knn_metrics_df = pd.DataFrame(knn_metrics_list, columns=metric_columns, index=metric_index_df)
rf_metrics_df = pd.DataFrame(rf_metrics_list, columns=metric_columns, index=metric_index_df)
lstm_metrics_df = pd.DataFrame(lstm_metrics_list, columns=metric_columns, index=metric_index_df)
# Display metrics for each algorithm in each iteration
algorithm_names  = ['KNN', 'RF', 'LSTM']
for i, metrics_df in enumerate([knn_metrics_df, rf_metrics_df, lstm_metrics_df], start=1):
    print('\nMetrics for Algorithm {}:\n'.format(algorithm_names[i-1]))
    print(metrics_df.round(decimals=2).T)
    print('\n')

#Calculate the average metrics for each algorithm
knn_avg_df = knn_metrics_df.mean()
rf_avg_df = rf_metrics_df.mean()
lstm_avg_df = lstm_metrics_df.mean()
# Create a DataFrame with the average performance for each algorithm
avg_performance_df = pd.DataFrame({'KNN': knn_avg_df, 'RF': rf_avg_df, 'LSTM': lstm_avg_df}, index=metric_columns)
# Display the average performance for each algorithm
print(avg_performance_df.round(decimals=2))
print('\n')

"""# Performance Comparision between all models"""

# Analyze the results to determine which algorithm performs better
discussion = ""

# Summarize performance for each algorithm
knn_summary = f"KNN has a high True Positive Rate (TPR: {avg_performance_df.loc['TPR', 'KNN']:.2f}) and balanced metrics, but its True Negative Rate (TNR: {avg_performance_df.loc['TNR', 'KNN']:.2f}) is lower compared to RF."
rf_summary = f"RF demonstrates the best overall performance, with the highest Accuracy ({avg_performance_df.loc['Accuracy', 'RF']:.2f}), TPR ({avg_performance_df.loc['TPR', 'RF']:.2f}), and AUC ({avg_performance_df.loc['AUC', 'RF']:.2f}), indicating it effectively handles both positive and negative classes."
lstm_summary = f"LSTM has lower metrics overall, with a TPR of {avg_performance_df.loc['TPR', 'LSTM']:.2f} and Accuracy of {avg_performance_df.loc['Accuracy', 'LSTM']:.2f}. Its higher Error Rate ({avg_performance_df.loc['Error_rate', 'LSTM']:.2f}) and lower HSS ({avg_performance_df.loc['HSS', 'LSTM']:.2f}) suggest potential overfitting or suboptimal training."

# Compare algorithms
comparison = f"""
1. KNN is simple and achieves reliable results with an Accuracy of {avg_performance_df.loc['Accuracy', 'KNN']:.2f} and F1 Score of {avg_performance_df.loc['F1_measure', 'KNN']:.2f}, but it struggles with False Positives (FPR: {avg_performance_df.loc['FPR', 'KNN']:.2f}).
2. RF is the best performer with the highest overall metrics, including AUC ({avg_performance_df.loc['AUC', 'RF']:.2f}) and Brier Score ({avg_performance_df.loc['Brier_score', 'RF']:.2f}), indicating a robust balance between precision and recall.
3. LSTM, while promising, performs poorly here, with significantly lower Accuracy ({avg_performance_df.loc['Accuracy', 'LSTM']:.2f}) and higher Error Rate ({avg_performance_df.loc['Error_rate', 'LSTM']:.2f}). This could be due to challenges in tuning hyperparameters or insufficient training data.
"""

# Justification for RF's performance
justification = f"""
RF's superior performance can be attributed to its ability to combine the outputs of multiple decision trees, effectively capturing complex patterns in the data while avoiding overfitting. Its higher TNR ({avg_performance_df.loc['TNR', 'RF']:.2f}) and lower Error Rate ({avg_performance_df.loc['Error_rate', 'RF']:.2f}) indicate strong generalization to unseen data.
"""

# Compile discussion
discussion += f"{knn_summary}\n\n"
discussion += f"{rf_summary}\n\n"
discussion += f"{lstm_summary}\n\n"
discussion += "Comparison of Algorithms:"
discussion += comparison
discussion += "\nJustification for RF's Performance:"
discussion += justification

# Print discussion
print(discussion)

"""# Visualization of KNN ROC Curve"""

knn_model = KNeighborsClassifier(n_neighbors=best_n_neighbors)
knn_model.fit(X_train_scaled, y_train)

# Obtain predicted probabilities
y_score = knn_model.predict_proba(X_test_scaled)[:, 1]

# Compute ROC curve and ROC area
fpr, tpr, _ = roc_curve(y_test, y_score)
roc_auc = auc(fpr, tpr)

# Plot ROC curve
plt.figure(figsize=(8, 8))
plt.plot(fpr, tpr, color='red', lw=2, label='ROC curve (area = {:.2f})'.format(roc_auc))
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('KNN ROC Curve')
plt.legend(loc='lower right')
plt.show()

"""# Visualization of The Random Forest ROC Curve"""

# Random Forest Model
rf_model = RandomForestClassifier(min_samples_split=min_samples_split, n_estimators=n_estimators)
rf_model.fit(X_train_scaled, y_train)

# Obtain predicted probabilities
y_score_rf = rf_model.predict_proba(X_test_scaled)[:, 1]

# Compute ROC curve and ROC area
fpr_rf, tpr_rf, _ = roc_curve(y_test, y_score_rf)
roc_auc_rf = auc(fpr_rf, tpr_rf)

# Plot Random Forest ROC curve
plt.figure()
plt.plot(fpr_rf, tpr_rf, color="green", label="Random Forest ROC curve (area = {:.2f})".format(roc_auc_rf))
plt.plot([0, 1], [0, 1], color="navy", linestyle="--")
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("Random Forest ROC Curve")
plt.legend(loc="lower right")
plt.show()

#lstm model
lstm_model = Sequential()
lstm_model.add(LSTM(64, activation='relu', return_sequences=False))
lstm_model.add(Dense(1, activation='sigmoid'))
lstm_model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# Convert data to numpy array
X_train_array = X_train.to_numpy()
X_test_array = X_test.to_numpy()
y_train_array = y_train.to_numpy()
y_test_array = y_test.to_numpy()

# Reshape data for LSTM model compatibility
input_shape = X_train_array.shape
input_train = X_train_array.reshape(len(X_train_array), input_shape[1], 1)
input_test = X_test_array.reshape(len(X_test_array), input_shape[1], 1)
output_train = y_train_array
output_test = y_test_array

# Train the LSTM model
history = lstm_model.fit(input_train, output_train, epochs=50, validation_data=(input_test, output_test), verbose=0)


# Predict probabilities for test set
lstm_probs = lstm_model.predict(X_test).ravel()  # Assuming lstm_model is already trained

lstm_fpr, lstm_tpr, _ = roc_curve(y_test, lstm_probs)
lstm_roc_auc = auc(lstm_fpr, lstm_tpr)

# Plot ROC AUC curves
plt.figure(figsize=(8, 8))
plt.plot(lstm_fpr, lstm_tpr, color='blue', lw=2, label='LSTM ROC curve (AUC = %0.2f)' % lstm_roc_auc)
plt.plot([0, 1], [0, 1], color='navy', linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('LSTM ROC AUC Curve')
plt.legend(loc="lower right")

plt.tight_layout()
plt.show()