from fastapi import FastAPI
from pydantic import BaseModel

# Create the FastAPI app instance
app = FastAPI()

# Define what our AI query request should look like
class Query(BaseModel):
    prompt: str
    max_tokens: int = 100  # default value of 100
    
@app.get("/")
def read_root():
    return {"message": "Welcome to the NBA AI Prop Bet Analyzer API"}

# Create our first endpoint
@app.post("/ai/query")
async def process_query(query: Query):
    return {"response": f"You asked: {query.prompt}"}

## https://www.youtube.com/watch?v=iWS9ogMPOI0 WATCH REST OF THIS VIDEO BEFORE CONTINUTINGZVINGIGNING