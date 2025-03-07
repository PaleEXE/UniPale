import math
from functools import partial

import numpy as np
import pandas as pd
from sklearn.naive_bayes import GaussianNB
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, confusion_matrix, recall_score, f1_score, precision_score

class GaussianNaiveBayesPale:
    SMALL = float('1e-15')

    @staticmethod
    def likelihood(x, mean, standard_deviation):
        return np.exp(-(x - mean) ** 2 / (2 * standard_deviation ** 2)) / (standard_deviation * np.sqrt(2 * np.pi))

    @staticmethod
    def log_likelihood(x, mean, standard_deviation):
        likelihood_value = GaussianNaiveBayesPale.likelihood(x, mean, standard_deviation) + GaussianNaiveBayesPale.SMALL
        return math.log(likelihood_value, math.e)

    @staticmethod
    def array_log_likelihood(array, mean=None, standard_deviation=None):
        if mean is None:
            mean = array.mean()
        if standard_deviation is None:
            standard_deviation = array.std()
        compute_log_likelihood = partial(GaussianNaiveBayesPale.log_likelihood, mean=mean, standard_deviation=standard_deviation)
        return np.array(list(map(compute_log_likelihood, array))), mean, standard_deviation

    def fit(self, features, labels):
        features_class_0 = features[labels == 0]
        features_class_1 = features[labels != 0]

        # Compute means and standard deviations for each class
        self.mean_class_0 = np.mean(features_class_0, axis=0)
        self.mean_class_1 = np.mean(features_class_1, axis=0)
        self.std_class_0 = np.std(features_class_0, axis=0)
        self.std_class_1 = np.std(features_class_1, axis=0)

        # Compute log of class prior probabilities
        probability_class_0 = len(features_class_0) / len(labels)
        self.log_prior_class_0 = math.log(probability_class_0, np.e)
        self.log_prior_class_1 = math.log(1 - probability_class_0, np.e)

        # Compute correlation of each feature with the labels
        self.feature_correlations = np.array([
            np.corrcoef(features[:, i], labels)[0, 1] for i in range(features.shape[1])
        ])

    def predict(self, data):
        likelihoods_class_0 = np.zeros_like(data)
        likelihoods_class_1 = np.zeros_like(data)

        for feature_index, feature_column in enumerate(data.T):
            likelihoods_class_0[:, feature_index] = GaussianNaiveBayesPale.array_log_likelihood(
                feature_column, self.mean_class_0[feature_index], self.std_class_0[feature_index])[0]
            likelihoods_class_1[:, feature_index] = GaussianNaiveBayesPale.array_log_likelihood(
                feature_column, self.mean_class_1[feature_index], self.std_class_1[feature_index])[0]

        total_likelihood_class_0 = likelihoods_class_0 @ self.feature_correlations ** 2 + self.log_prior_class_0
        total_likelihood_class_1 = likelihoods_class_1 @ self.feature_correlations ** 2 + self.log_prior_class_1

        return (total_likelihood_class_1 > total_likelihood_class_0).astype(int)


# Load data
data = load_breast_cancer()
features = data.data
labels = data.target

stratified_k_fold = StratifiedKFold(n_splits=10)
results = []

# Run cross-validation
for train_index, test_index in stratified_k_fold.split(features, labels):
    train_features = features[train_index]
    train_labels = labels[train_index]
    test_features = features[test_index]
    test_labels = labels[test_index]

    pale_model = GaussianNaiveBayesPale()
    pale_model.fit(train_features, train_labels)
    pale_predictions = pale_model.predict(test_features)

    pale_accuracy = accuracy_score(test_labels, pale_predictions)
    pale_precision = precision_score(test_labels, pale_predictions)
    pale_recall = recall_score(test_labels, pale_predictions)
    pale_f1 = f1_score(test_labels, pale_predictions)
    pale_confusion = confusion_matrix(test_labels, pale_predictions)

    sklearn_model = GaussianNB()
    sklearn_model.fit(train_features, train_labels)
    sklearn_predictions = sklearn_model.predict(test_features)

    sklearn_accuracy = accuracy_score(test_labels, sklearn_predictions)
    sklearn_precision = precision_score(test_labels, sklearn_predictions)
    sklearn_recall = recall_score(test_labels, sklearn_predictions)
    sklearn_f1 = f1_score(test_labels, sklearn_predictions)
    sklearn_confusion = confusion_matrix(test_labels, sklearn_predictions)

    results.append({
        "Pale_Accuracy": pale_accuracy,
        "Pale_Precision": pale_precision,
        "Pale_Recall": pale_recall,
        "Pale_F1": pale_f1,
        "Pale_Confusion": pale_confusion.tolist(),
        "SKLearn_Accuracy": sklearn_accuracy,
        "SKLearn_Precision": sklearn_precision,
        "SKLearn_Recall": sklearn_recall,
        "SKLearn_F1": sklearn_f1,
        "SKLearn_Confusion": sklearn_confusion.tolist()
    })

results_df = pd.DataFrame(results)
with open("classification_report.txt", "w") as file:
    file.write("Detailed Classification Report\n\n")
    file.write(results_df.to_markdown())
    file.write("\n\nSummary Statistics\n")
    file.write(results_df.describe().to_markdown())
