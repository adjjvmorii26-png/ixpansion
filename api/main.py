from fastapi import FastAPI

app = FastAPI(title="IXPANSION API", version="1.2.0-rc3")


@app.get("/")
def read_root() -> dict:
    return {"service": "ixpansion", "status": "ok"}


@app.get("/health")
def health() -> dict:
    return {"status": "healthy"}
