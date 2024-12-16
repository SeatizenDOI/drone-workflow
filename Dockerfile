FROM ghcr.io/osgeo/gdal:ubuntu-small-latest

# Add local directory and change permission.
ADD --chown=seatizen . /home/seatizen/app/

# Setup workdir in directory.
WORKDIR /home/seatizen/app

RUN apt-get update && \
    apt-get install -y --no-install-recommends sqlite3 python3 python3-pip python3-dev build-essential r-base r-base-core r-base-dev \
    libsodium-dev libsecret-1-dev wkhtmltopdf libssl-dev libcurl4-openssl-dev libxml2-dev libudunits2-dev libproj-dev \
    libsqlite3-dev libsqlite3-0 libgdal-dev libgeos-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --break-system-package \
    beautifulsoup4==4.12.3 \
    exifread==3.0.0 \
    folium==0.18.0 \
    geopandas==1.0.1 \
    matplotlib==3.9.3 \
    pdfkit==1.0.0 \
    pillow==11.0.0 \
    pycountry==24.6.1 \
    rasterio==1.4.3 \
    requests==2.32.3 \
    rpy2==3.5.12 \
    xmltodict==0.14.2 \
    webdriver-manager==4.0.2 \ 
    wkhtmltopdf==0.2

RUN R -e "install.packages('remotes')"
RUN R -e "remotes::install_github('eblondel/geoflow', dependencies = c('Depends', 'Imports'), force=TRUE)"

# Change with our user.
USER seatizen

# Define the entrypoint script to be executed.
ENTRYPOINT ["python", "workflow.py"]