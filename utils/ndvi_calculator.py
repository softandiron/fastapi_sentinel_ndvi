import rasterio
import logging
import os

import config

logger = logging.getLogger("NDVI_calculator")


def get_bands_from_safe(scene_name):
    file_path = config.scenes_folder + scene_name
    logger.debug(f"getting bands from {file_path}")
    path = [x[0] for x in os.walk(file_path + "GRANULE/")]
    subdirectory = path[1]
    img_data_path = subdirectory + "/IMG_DATA/"
    bands = next(os.walk(img_data_path), (None, None, []))[2]
    bands.sort()
    b2_blue = rasterio.open(img_data_path + bands[2])
    b3_green = rasterio.open(img_data_path + bands[3])
    b4_red = rasterio.open(img_data_path + bands[4])
    logger.debug(f"b2_blue: {b2_blue}")
    logger.debug(f"b3_green: {b3_green}")
    logger.debug(f" b4_blue: {b4_red}")
    return b2_blue, b3_green, b4_red


def create_tiff(random_id, b2_blue, b3_green, b4_red):
    # Create an RGB image
    file_name = f"{random_id}.tiff"
    logger.debug(f" creating file {file_name} .....")
    with rasterio.open(config.tiff_images + file_name, 'w', driver='Gtiff',
                       width=b2_blue.width, height=b2_blue.height,
                       count=3,
                       crs=b2_blue.crs,
                       transform=b2_blue.transform,
                       dtype=b2_blue.dtypes[0]) as rgb:
        rgb.write(b2_blue.read(1), 1)
        rgb.write(b3_green.read(1), 2)
        rgb.write(b4_red.read(1), 3)
        rgb.close()

    logger.debug(f" file {file_name} composed")
    return file_name
