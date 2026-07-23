from fastapi import FastAPI
app = FastAPI()
@app.get("/")
def hello():
    return {"message": "Hello, Im Gonzaga!"}


@app.get("/hello")
def hello_name():
    return {"message": "Hello from FastAPI!"}
