# -*- coding: utf-8 -*-
"""SVD-MatrixFactorization-Furnichanter.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1FKpLSOfRhXy-rOTVieNOMTif4rtDlHDh

## Python Imports
"""

import numpy as np
from math import sqrt
import torch
import pandas as pd
import torch.nn.functional as F
import random
from collections import OrderedDict
import matplotlib.pyplot as plt
import matplotlib
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import svds
matplotlib.rc('font', **{'family': 'DejaVu Sans', 'size'   : 16})
matplotlib.rc('figure', figsize=(15, 7.5))

"""## Initial Setup and Rating Matrix Data"""

# Visualize the data
# 200 user data-points
# 12 initial furniture features
ratingMatrix = np.array(np.random.randint(6, size=(200, 12)), dtype=np.float32)
plt.figure(figsize=(200, 12))
plt.imshow(ratingMatrix, cmap='binary')
plt.xlabel('Items')
plt.ylabel('Users')
plt.title('Furniture Matrix Data (Material)')
plt.show()

"""## SVD Initial Approach"""

num_users, num_items = ratingMatrix.shape
print(ratingMatrix)

"""## Factor Rating Matrix into SVD

Important Realization:
When we factor the matrix into 3 distinct categories (U, Sigma, V Transpose), the U represents the user-embedding (or n x k user matrix) and the V represents the item-embedding matrix (or k x n item matrix). We can break the rating matrix into its factors n x k user matrix and k x n item matrix. Where k is the given latent factors of the rating matrix. This would be characteristics or features of the items you have in the rating matrix (color, width, material, shape, stlye, height, weight of couch). U would essentially represent the weight of how much each user prefers different features, V would simply represent whether the feature is represented in the given object (whether couch actually does have the weight, style prefrences, normally binary-scale (0,1))
"""

# Num. latent features for user and item matrices
# create sparse matrix using SciKit-Learn
# 5 latent features - width, height, length, color, material

latent_features = 5
A = csc_matrix(ratingMatrix)

u, s, vt = svds(A, latent_features)

print ('A:\n', A.toarray())
print ('=')
print ('\nU:\n', u)
print ('\nΣ:\n', s)
print ('\nV.T:\n', vt)

"""### Dot Product Between User and Item Matrix (U and V.T) Give Correlation of Features"""

print('Approximation of Ratings Matrix')
u.dot(np.diag(s).dot(vt))

print('Rounded Approximation of Ratings Matrix')
np.round(u.dot(np.diag(s).dot(vt)))

"""## Train until convergence using GD"""

def train_until_convergence(u, s, vt, ratingMatrix, learning_rate=0.001, convergence_threshold=1e-6, max_iterations=100, gradient_clip=5.0):
    """
    Trains the SVD decomposition until convergence using gradient descent.
    """

    # Normalize the rating matrix to the range 0-1
    min_rating = np.min(ratingMatrix)
    max_rating = np.max(ratingMatrix)
    normalized_matrix = (ratingMatrix - min_rating) / (max_rating - min_rating)

    u_trained = u.copy()
    vt_trained = vt.copy()
    s_trained = np.diag(s)

    for iteration in range(max_iterations):
        # Compute the current reconstruction error
        reconstructed_matrix = u_trained.dot(s_trained).dot(vt_trained)
        error_matrix = normalized_matrix - reconstructed_matrix
        current_error = np.sum(error_matrix**2)

        print(f"Iteration {iteration + 1}: Error = {current_error}")

        if iteration > 0 and abs(previous_error - current_error) < convergence_threshold:
            print("Converged!")
            break

        previous_error = current_error

        # Update U and V.T using gradient descent
        for i in range(u_trained.shape[0]):
            for k in range(u_trained.shape[1]):
                gradient_u = -2 * np.sum(error_matrix[i, :] * s_trained[k, k] * vt_trained[k, :])
                gradient_u = np.clip(gradient_u, -gradient_clip, gradient_clip)  # Clip gradients
                u_trained[i, k] -= learning_rate * gradient_u

        for k in range(vt_trained.shape[0]):
            for j in range(vt_trained.shape[1]):
                gradient_vt = -2 * np.sum(error_matrix[:, j] * s_trained[k, k] * u_trained[:, k])
                gradient_vt = np.clip(gradient_vt, -gradient_clip, gradient_clip)  # Clip gradients
                vt_trained[k, j] -= learning_rate * gradient_vt

    # Scale the reconstructed matrix back to the original range (0-5)
    final_matrix = u_trained.dot(s_trained).dot(vt_trained)
    final_matrix = final_matrix * (max_rating - min_rating) + min_rating

    return u_trained, s_trained, vt_trained, final_matrix


# Example usage
np.random.seed(42)
ratingMatrix = np.random.rand(5, 5) * 5  # Generate a random rating matrix with values from 0-5
u, s, vt = np.linalg.svd(ratingMatrix)
u_trained, s_trained, vt_trained, final_matrix = train_until_convergence(u, s, vt, ratingMatrix)

# Print the final approximated matrix
print("Final approximated matrix:")
print(final_matrix)

def rmse(prediction, ground_truth):
    """
    Calculates the Root Mean Squared Error (RMSE) between the prediction and ground truth.

    Args:
        prediction (numpy.ndarray): The predicted ratings.
        ground_truth (numpy.ndarray): The actual ratings.

    Returns:
        float: The RMSE value.
    """
    # Ignore NaN values in the ground truth
    mask = ~np.isnan(ground_truth)
    prediction = prediction[mask]
    ground_truth = ground_truth[mask]

    return sqrt(np.mean((prediction - ground_truth)**2))

predicted_ratings = u.dot(np.diag(s).dot(vt))
rmse_value = rmse(predicted_ratings, ratingMatrix)
print(f"RMSE: {rmse_value}")

"""## Results and Evaluation"""

matplotlib.rc('font', **{'family': 'DejaVu Sans', 'size': 16})
matplotlib.rc('figure', figsize=(15, 7.5))


# Plotting the error
plt.figure(figsize=(10, 6))
plt.plot(errors)
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.title('Loss Function across Epochs')
plt.grid(True)
plt.show()