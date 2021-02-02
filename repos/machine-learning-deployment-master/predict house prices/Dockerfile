FROM ubuntu:16.04

MAINTAINER Abhinav Sagar "abhinavsagar4@gmail.com"


RUN apt -y update &&\
    apt -y install python3 python3-pip

RUN python3 -m pip install --upgrade pip

 
ADD ./python_requirements.txt /
RUN python3 -m pip install -r python_requirements.txt

ADD ./prediction.py /
ADD ./server.py /
ADD ./kc_house_data.csv /

CMD [ "python3", "-u", "./server.py" ]
