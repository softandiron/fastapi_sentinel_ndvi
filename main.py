"""
Developed by Artem Minin
"""

import uvicorn
from fastapi import FastAPI, status, UploadFile
from pydantic import BaseModel
from typing import Optional, List
import aiofiles
import uuid
from datetime import datetime
import logging

import config
from database import models, db_init
from db import SessionLocal
from utils import scenes_loader

logging.basicConfig(level=logging.DEBUG)
main_log = logging.getLogger("main.py")

app = FastAPI()


class Footprint(BaseModel):  # serializer
    id: Optional[str]
    timestamp: str
    geoJson: str

    class Config:
        orm_mode = True


db = SessionLocal()


@app.get("/footprints", response_model=List[Footprint], status_code=status.HTTP_200_OK)
def get_all_footprints():
    footprints = db.query(models.Footprint).all()
    return footprints


@app.get("/footprint/{fp_id}", response_model=Footprint, status_code=status.HTTP_200_OK)
def get_footprint_by_id(fp_id: str):
    footprint = db.query(models.Footprint).filter(models.Footprint.id == fp_id).first()
    return footprint


@app.post("/footprints", response_model=Footprint, status_code=status.HTTP_201_CREATED)
async def add_footprint(geojson_file: UploadFile):
    main_log.debug("add_footprint() function triggered")
    random_id = str(uuid.uuid1())
    geojson = "waiting for upload"
    file_path = f"{config.geojson_folder}{random_id}.geojson"

    try:
        async with aiofiles.open(file_path, 'wb') as src:
            content = await geojson_file.read()
            await src.write(content)
            geojson = "file uploaded"
            main_log.debug("file uploaded")
    except Exception as err:
        geojson = f"error: {err}"
        main_log.error("file uploading error")

    new_footprint = models.Footprint(
        id=random_id,
        timestamp=str(datetime.utcnow()),
        geoJson=geojson
    )
    db.add(new_footprint)
    db.commit()

    if geojson == "file uploaded":
        main_log.debug("going to scenes loader ....")
        scenes_loader.download_sentinel_scene(file_path)
    # return content


@app.put("/footprint/{fp_id}", response_model=Footprint, status_code=status.HTTP_200_OK)
def update_footprint_by_id(fp_id: str, geojson: str):
    footprint_to_update = db.query(models.Footprint).filter(models.Footprint.id == fp_id).first()
    footprint_to_update.timestamp = str(datetime.utcnow())
    footprint_to_update.geoJson = geojson

    db.commit()

    return footprint_to_update


@app.delete("/footprint/{fp_id}")
def delete_footprint_by_id(fp_id: str):
    footprint_to_delete = db.query(models.Footprint).filter(models.Footprint.id == fp_id).first()

    if footprint_to_delete is None:
        raise status.HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                   detail="Footprint with this ID not found")
    else:
        db.delete(footprint_to_delete)
        db.commit()

    return footprint_to_delete


if __name__ == "__main__":
    main_log.debug("STARTING MAIN")
    db_init.create_table_if_ne()
    uvicorn.run("main:app")
