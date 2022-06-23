# https://scihub.copernicus.eu/dhus/#/home

from sentinelsat import SentinelAPI, geojson_to_wkt, read_geojson
import logging
from datetime import datetime, timedelta
import os
import zipfile

import config

logger = logging.getLogger("scenes_loader")

sentinel_api = SentinelAPI(config.sentinel_user, config.sentinel_password, config.sentinel_url)


def download_sentinel_scene(file_path: str):
    logger.debug("reading geoJson file ....")
    wkt = geojson_to_wkt(read_geojson(file_path))
    logger.debug("searching for products ....")
    products = sentinel_api.query(
        wkt,
        date=(datetime.today() - timedelta(30), datetime.today()),
        limit=50,
        platformname='Sentinel-2',
        cloudcoverpercentage=(0, 50)  # всё равно потом выберем наименьший
    )

    products_df = sentinel_api.to_geodataframe(products)

    logger.debug("searching for product with lowest cloud coverage % ....")
    cloudless_product_df = products_df[products_df.cloudcoverpercentage == products_df.cloudcoverpercentage.min()]

    cloudless_scene_uuid = cloudless_product_df['uuid'][0]
    cloudless_scene_title = cloudless_product_df['title'][0]
    cloudless_scene_size = cloudless_product_df['size'][0]

    if os.path.exists(config.archives_folder):
        # проверка, чтобы не качать несколько раз один и тот же тяжёлый файл
        if not os.path.exists(config.archives_folder + cloudless_scene_title + '.SAFE'):
            logger.debug(f"Archive size: {cloudless_scene_size}. Downloading the product ....")
            scene = sentinel_api.download(cloudless_scene_uuid, config.archives_folder)

        else:
            logger.debug('file already exists')
    else:
        logger.error('path not found')

    logger.debug('unzipping the scene tile....')
    with zipfile.ZipFile(config.archives_folder + cloudless_scene_title + ".zip", 'r') as zip_ref:
        zip_ref.extractall(config.scenes_folder)
        scene_name = zip_ref.namelist()[0]
        logger.debug('scene tile is ready')

    return scene_name

