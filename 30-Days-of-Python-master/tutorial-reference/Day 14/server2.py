import os
import datetime
from fastapi import FastAPI
from logger import trigger_log_save
from scrape import run as scrape_runner
app = FastAPI()

@app.get("/")
def hello_world():
    return {"hello": "world"}

@app.get("/abc")
def abc_view():
    return {"data": [1,2,3]}


@app.post("/box-office-mojo-scraper")
def scrape_runner_view():
    trigger_log_save()
    scrape_runner()
    return {"data": [1,2,3]}