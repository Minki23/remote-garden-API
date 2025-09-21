from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


# @TODO check why not working
def add(app: FastAPI):
    app.mount("/static", StaticFiles(directory="static"), name="static")
