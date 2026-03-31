from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
def say_hello():
    return {"message": "Hello World!"}

# Запуск: uvicorn server_test:app --reload
# Открыть в браузере: http://localhost:8000/hello