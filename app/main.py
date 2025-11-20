from fastapi import FastAPI


from . import core, shared,models
app = FastAPI()

@app.get('/')
def user_login():
    return{ "name": "hi"}