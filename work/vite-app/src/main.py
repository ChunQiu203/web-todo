from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import time

app=FastAPI()

@app.get("/data/")
async def get_data():
    def event_stream():
        for i in range(5):
            yield f"data chunk {i+1}\n"
            time.sleep(1)
    return StreamingResponse(event_stream(), media_type="text/plain")

from starlette.middleware.cors import CORSMiddleware

app.add_middleware(     
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods = ["*"],
    allow_headers=["*"]
)
