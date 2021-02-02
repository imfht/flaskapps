# Build Python Wheel
FROM python:3.7.4-stretch as builder

WORKDIR /
COPY . bento/

WORKDIR /bento
RUN pip install poetry==1.0.0
RUN poetry install
RUN make package

#######################################

FROM circleci/python:3.6.9-stretch-node

USER root

RUN pip install pytest~=5.3.1

COPY --from=builder /bento/dist/*.whl ./
RUN pip install ./*.whl

# Verify Installation
RUN node --version
RUN git --version
RUN bento --version

COPY ./tests /tests