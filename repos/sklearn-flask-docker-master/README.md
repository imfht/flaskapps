# sklearn-flask-docker
An example of deploying a sklearn model using Flask using a Docker container.

This tutorial requires basic Docker knowledge.

## Steps:

## 1. Train The Model

For this example we are training a toy model using Iris training dataset. To train a new model, run this:

`python train.py`

This outputs a pickle model in a file named `model.pkl`.

## 2. Build A Docker Image Containing Flask And The Model

Construct an image (`docker build`) called chrisalbon/sklearn-flask-docker (`--tag chrisalbon/sklearn-flask-docker`) from the Dockerfile (`.`).

The construction of this image is defined by `Dockerfile`.

`docker build --tag chrisalbon/sklearn-flask-docker .`

## 3. Build A Container From The Docker Image

Create and start (`docker run`) a detached (`-d`) Docker container called sklearn-flask-docker (`--name sklearn-flask-docker`) from the image `chrisalbon/sklearn-flask-docker:latest` where port of the host machine is connected to port 3333 of the Docker container (`-p 3000:3333`).

`docker run -p 3000:3333 -d --name sklearn-flask-docker chrisalbon/sklearn-flask-docker:latest`

## 4. Query The Prediction API With An Example Observation

Since our model is trained on the Iris toy dataset, we can test the API by queries it for the predicted class for this example observation:

- sepal length = 4.5
- sepal width = 2.3
- petal length = 1.3
- petal width = 0.3

### In Your Browser

Paste this URL into your browser bar:

`http://0.0.0.0:3000/api/v1.0/predict?sl=4.5&sw=2.3&pl=1.3&pw=0.3`

In your browser you should see something like this:
```
{"features":[4.5,2.3,1.3,0.3],"predicted_class":0}
```

`"predicted_class":0` means that the predicted class is "Iris setosa"

### Using Curl

Paste this URL into your terminal:

`curl -i "0.0.0.0:3000/api/v1.0/predict?sl=4.5&sw=2.3&pl=1.3&pw=0.3"`

You should see something like this:
```
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 51
Server: Werkzeug/1.0.1 Python/3.6.12
Date: Tue, 25 Aug 2020 20:29:41 GMT

{"features":[4.5,2.3,1.3,0.3],"predicted_class":0}
```

## Basic Docker Operations

You will need to use `sudo` for these commands, however best practice is to add your user to the `docker` group when in production.

### Start The Container

`docker start sklearn-flask-docker`

### Stop The Container

`docker stop sklearn-flask-docker`

### Delete The Container

`docker rm sklearn-flask-docker`