FROM ubuntu:latest

MAINTAINER Artem Minin - @softandiron
LABEL version="1.0"

RUN apt-get update && \
    apt-get install -y python3-pip

ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"
RUN apt-get update

RUN apt-get install -y wget && rm -rf /var/lib/apt/lists/*

RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh
RUN conda --version

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN conda install psycopg2
RUN pip install python-multipart

COPY . .

# CMD ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"]


# RUN pip install -r requirements.txt
#RUN pip install wheel
#RUN pip install pipwin
#
#RUN pip install numpy
#RUN pip install pandas
#RUN pip install pygeos
#RUN pip install geopandas
#RUN pip install shapely
#    RUN pip install gdal
#RUN pip install fiona
#RUN pip install pyproj
#RUN pip install six
#RUN pip install rtree
#
#RUN pip install aiofiles
#RUN pip install fastapi
#RUN pip install pydantic
#RUN pip install rasterio
#RUN pip install sentinelsat
#RUN pip install SQLAlchemy
#RUN pip install uvicorn

