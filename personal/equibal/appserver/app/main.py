from fastapi import FastAPI
app = FastAPI()
@app.get("/")
def hello():
    return {"message": "Hello, Im Equibal"}

@app.get("/hello")
def hello_name():
    return {"message":"Hello from fastAPI!"}
