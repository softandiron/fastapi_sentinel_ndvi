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
from utils import ndvi_calculator

logging.basicConfig(level=logging.DEBUG)
main_log = logging.getLogger("main.py")

app = FastAPI()


class Footprint(BaseModel):  # serializer
    id: Optional[str]  # формируется длинный рандомный уникальный id
    timestamp: str     # формируется из datetime.utcnow()
    geoJson: str       # здесь будет не сам файл, даже не адрес, а его статус. Можно потом поменять.

    class Config:
        orm_mode = True


db = SessionLocal()


@app.get("/footprints", response_model=List[Footprint], status_code=status.HTTP_200_OK)
def get_all_footprints():
    """
    Возвращает список всех записей из базы
    """
    footprints = db.query(models.Footprint).all()
    return footprints


@app.get("/footprint/{fp_id}", response_model=Footprint, status_code=status.HTTP_200_OK)
def get_footprint_by_id(fp_id: str):
    """
    Возвращает нужную запись по id
    """
    footprint = db.query(models.Footprint).filter(models.Footprint.id == fp_id).first()
    return footprint


@app.post("/footprints", response_model=Footprint, status_code=status.HTTP_201_CREATED)
async def add_footprint(geojson_file: UploadFile):
    """
    Самая большая функция, которая запрашивает только json, и по нему ищет подходящие продукты sentinel,
    скачивает их, распаковывает, идёт в папку с каналами (bands) и извлекает их.
    Потом, по-идее, формирует tiff, вырезает из него нужное поле в соответствии с геометрией geojson,
    считает NDVI и выдаёт красивую картинку.
    :param geojson_file: прикрепить файлик geoJson
    :return: пока ничего интересного, кроме спутниковых снимков в хранилище и косячного tiff-файла :(
    """
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
        # скачиваем и разархивируем sentinel продукт с подходящим тайлом:
        scene_name = scenes_loader.download_sentinel_scene(file_path)

        # Получаем разные цветовые каналы (я для начала взял RGB)
        b2_blue, b3_green, b4_red = ndvi_calculator.get_bands_from_safe(scene_name)

        # Вот на этапе формирования tiff изображения я застрял:
        tiff_file = ndvi_calculator.create_tiff(random_id, b2_blue, b3_green, b4_red)
        # файл tiff формируется, но не корректный.

    return geojson


@app.put("/footprint/{fp_id}", response_model=Footprint, status_code=status.HTTP_200_OK)
def update_footprint_by_id(fp_id: str, geojson: str):
    """
    Обновляет данные в записи по id
    """
    footprint_to_update = db.query(models.Footprint).filter(models.Footprint.id == fp_id).first()
    footprint_to_update.timestamp = str(datetime.utcnow())
    footprint_to_update.geoJson = geojson

    db.commit()

    return footprint_to_update


@app.delete("/footprint/{fp_id}")
def delete_footprint_by_id(fp_id: str):
    """
    Удаляет записи по id
    """
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
