from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

@app.get("/upload")
def api():
    data = {
        "message": "Hello, FastAPI",
        "status": 200
    }
    return JSONResponse(content=data)

# staticディレクトリにあるindex.htmlを使う (Svelte用)
#app.mount("/", StaticFiles(directory="../../client/static", html=True), name="static")
#数百キロバイトなら問題ない（～１０MB）ならOK