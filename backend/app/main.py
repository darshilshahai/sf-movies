from fastapi import FastAPI

app = FastAPI(
    title="SF Movies Explorer API",
    description="Backend API for exploring San Francisco film locations using DataSF data.",
    version="1.0.0",
)


@app.get("/")
def read_root():
    return {"message": "Welcome to SF Movies Explorer API"}
