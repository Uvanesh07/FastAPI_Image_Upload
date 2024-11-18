from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = "mysql+pymysql://root:Uvan%4012%2334%2Ar@localhost:3306/test-img"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declare a base class for the database models
Base = declarative_base()

# Define the Image model
class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)
    path = Column(String(255))  # Specify the length of the VARCHAR here

# Create the images table
Base.metadata.create_all(bind=engine)

# Initialize the FastAPI application
app = FastAPI()

# API endpoint to upload an image
@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Create a local directory to save images
        os.makedirs("uploads", exist_ok=True)

        # Create a file path and save the uploaded image
        file_location = f"uploads/{file.filename}"
        with open(file_location, "wb") as image_file:
            image_file.write(await file.read())

        # Save the image path to the database
        db = SessionLocal()
        db_image = Image(path=file_location)
        db.add(db_image)
        db.commit()
        db.refresh(db_image)

        logger.info(f"Uploaded image saved at: {file_location}")
        return {"info": f"Image uploaded successfully, stored at: {file_location}"}
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload image.")

# API endpoint to retrieve an image by ID
@app.get("/images/{image_id}")
async def get_image(image_id: int):
    db = SessionLocal()
    image = db.query(Image).filter(Image.id == image_id).first()

    if image is None:
        logger.warning(f"Image with ID {image_id} not found.")
        raise HTTPException(status_code=404, detail="Image not found.")

    # Return the image using the path stored in the database
    return FileResponse(path=str(image.path))

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
