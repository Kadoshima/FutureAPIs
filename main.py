from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pymongo import MongoClient
from passlib.context import CryptContext
import uvicorn
from pydantic import BaseModel
from fastapi.responses import FileResponse
import pandas as pd
import csv

class User(BaseModel):
    username: str
    password: str

app = FastAPI()
client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
users_collection = db["users"]
items_collection = db["test001"]


security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    user = users_collection.find_one({"username": credentials.username})
    if not user or not pwd_context.verify(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.post("/register/")
async def register(user: User):
    hashed_password = pwd_context.hash(user.password)
    users_collection.insert_one({"username": user.username, "hashed_password": hashed_password})
    return {"message": "User created successfully"}

@app.post("/test001/")
async def create_item(item: dict, username: str = Depends(verify_credentials)):
    items_collection.insert_one(item)
    return {"message": "https://www.server-world.info/query?os=Ubuntu_22.04&p=influxdb&f=1"}

@app.get("/test001/")
async def get_items(username: str = Depends(verify_credentials)):
    items = list(items_collection.find().sort("_id", -1).limit(5))
    for item in items:
        item["_id"] = str(item["_id"])
    return {"items": items}


@app.get("/csv_test/")
async def get_csv(username: str = Depends(verify_credentials)):
    items = list(items_collection.find().sort("_id", -1))
    for item in items:
        item["_id"] = str(item["_id"])
    
    # Convert the list of dictionaries to a pandas DataFrame
    df = pd.DataFrame(items)
    
    # Write the DataFrame to a CSV file
    df.to_csv('items.csv', index=False, quoting=csv.QUOTE_NONNUMERIC)
    
    return FileResponse('items.csv', media_type='text/csv', filename='items.csv')

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")