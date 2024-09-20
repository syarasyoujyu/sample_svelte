from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

@app.get("/api")
def api():
    data = {
        "message": "Hello, FastAPI",
        "status": 200
    }
    return JSONResponse(content=data)

# staticディレクトリにあるindex.htmlを使う (Svelte用)
#app.mount("/", StaticFiles(directory="../../client/static", html=True), name="static")
