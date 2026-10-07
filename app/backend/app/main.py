from fastapi import FastAPI

app = FastAPI()

@app.get("/api/sante")
def sante():
    return {"status":"ok"}