from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def user_login():
    return{ "name": "hi"}