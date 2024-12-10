from ubuntu/python:3.12-24.04_stable

RUN apt-get update && \
    apt-get install -y --no-install-recommends r-base r-base-dev libsodium-dev libsodium-dev libsecret-1-dev wkhtmltopdf && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir \
    beautifulsoup4==4.12.3 \
    exifread==3.0.0 \
    exifread==0.18.0 \
    folium==3.0.0 \
    geopandas=1.0.1 \
    matplotlib==3.9.3 \
    pdfkit== 1.0.0 \
    pillow== 11.0.0 \
    pycountry== 24.6.1 \
    rasterio== 1.4.3 \
    requests== 2.32.3 \
    rpy2== 3.5.12 \
    xmltodict== 0.14.2 \
    webdriver-manager== 4.0.2 \ 
    wkhtmltopdf== 0.2 \

R -e "require('remotes') | install_github('eblondel/geoflow', dependencies = c('Depends', 'Imports'), force=TRUE)"