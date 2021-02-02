# Load libraries
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn import datasets
from sklearn.externals import joblib

# Load the iris data
iris = datasets.load_iris()

# Create a matrix, X, of features and a vector, y.
X, y = iris.data, iris.target

# Train a naive logistic regression model
clf = LogisticRegression(random_state=0, solver='liblinear', multi_class='auto')
clf.fit(X, y)

# Save the trained model as a pickle string.
saved_model = pickle.dumps(clf)

# Save the model as a pickle in a file
joblib.dump(clf, 'model.pkl')