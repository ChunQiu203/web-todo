from fastapi import FastAPI

app=FastAPI()

@app.get("/data/")
async def get_data():
    return {"name":'test','age':20}

from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(     
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods = ["*"],
    allow_headers=["*"]
)
