# Docker README

## Build image.

`docker build --progress=plain -f Dockerfile -t drone-workflow:latest . 2>&1 | tee build.log`

## Launch image


```bash
docker run --user 1000 --rm \
  -v ./configs/:/home/seatizen/app/configs \
  -v ./output/:/home/seatizen/app/output \
  -v /media/bioeos/E/drone_serge_test:/home/seatizen/sessions  \
 --name drone-workflow drone-workflow:latest -c -efol -pfol /home/seatizen/sessions -pgl /usr/local/lib/R/site-library
```