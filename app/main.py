from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"name": "Loukaniko",
            "description": "Travel value data API",
            "version": "v1", 
            }