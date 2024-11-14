from bson.objectid import ObjectId
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


# MongoDB connection settings
MONGO_DETAILS = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.socialMediaDB
collection = database.social_media_data

# Pydantic model for the document structure
class SocialMediaData(BaseModel):
    month: str
    service: str
    social_events: int
    facebook_shares: int
    twitter_retweets: int
    social_interactions: int
    
    class Config:
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin; change to specific domain if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/data", response_model=List[SocialMediaData])
async def get_social_media_data():
    # Fetch all documents from MongoDB
    data = await collection.find().to_list(length=100)
    # Transform data into list of dictionaries without '_id' field
    response_data = [
        {
            "month": item["month"],
            "service": item["service"],
            "social_events": item["social_events"],
            "facebook_shares": item["facebook_shares"],
            "twitter_retweets": item["twitter_retweets"],
            "social_interactions": item["social_interactions"],
        }
        for item in data
    ]
    return response_data

@app.get("/data/{id}", response_model=SocialMediaData)
async def get_social_media_data_by_id(id: str):
    try:
        obj_id = ObjectId(id)
        #print(obj_id)
        document = await collection.find_one({"_id": obj_id})
        if document:
            return document
        raise HTTPException(status_code=404, detail="Data not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid ID format: {str(e)}")

# Run the server with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)