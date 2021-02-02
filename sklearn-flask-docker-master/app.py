"""
This file runs the Flask application we are using as an API endpoint.
"""

import pickle
from math import log10
from flask import Flask
from flask import request
from flask import jsonify
from sklearn import linear_model
from sklearn.externals import joblib

# Create a flask
app = Flask(__name__)

# Load pickled model file
model = joblib.load('model.pkl')

# Create an API end point
@app.route('/api/v1.0/predict', methods=['GET'])
def get_prediction(trained_model=model):

    # sepal length
    sepal_length = float(request.args.get('sl'))
    # sepal width
    sepal_width = float(request.args.get('sw'))
    # petal length
    petal_length = float(request.args.get('pl'))
    # petal width
    petal_width = float(request.args.get('pw'))

    # The features of the observation to predict
    features = [sepal_length,
                sepal_width,
                petal_length,
                petal_width]

    # Predict the class using the model
    predicted_class = int(trained_model.predict([features]))

    # Return a json object containing the features and prediction
    return jsonify(features=features, predicted_class=predicted_class)

if __name__ == '__main__':
    # Run the app at 0.0.0.0:3333
    app.run(port=3333,host='0.0.0.0')