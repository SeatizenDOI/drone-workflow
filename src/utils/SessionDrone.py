import shutil
import pandas as pd
import geopandas as gpd
from pathlib import Path
from shapely import Polygon
from argparse import Namespace

from ..DroneMD.meteo_helper import meteo
from ..DroneMD.raster_helper import series_to_img
from ..DroneMD.report import define_map, map_html, convert_map_pdf
from ..DroneMD.exif_helper import images_coords, bbox, center_bbox, datebe, altimg, common_tags

class SessionDrone:
    def __init__(self, session: Path):
    
        self.session = session
        self.place, self.platform, self.date = "", "", ""
        self.alpha3code, self.title = "", ""

        self.DCIM_FOLDER = Path(session, "DCIM")
        self.GPS_FOLDER = Path(session, "GPS")
        self.GPS_DEVICE_FOLDER = Path(self.GPS_FOLDER, "DEVICE")
        self.METADATA_FOLDER = Path(session, "METADATA")

        self.metadata_df = pd.DataFrame()
        self.metadata_gdf, self.gdfutm = gpd.GeoDataFrame(), gpd.GeoDataFrame()
        self.img_list = []
        self.survey_area = 0

        self.compute_basics()
    

    def compute_basics(self) -> None:
        """ Retrieve basics information. """

        # Transform 20231202_REU-HERMITAGE_UAV_01 into 20231202, REU-HERMITAGE, UAV, 01 
        self.date, place, self.platform, session_number = self.session.name.split('_')[0:4]

        # Transform UAV-1 into UAV.
        if '-' in self.platform:
            self.platform = self.platform.split('-')

        if '-' in place:
            self.alpha3code = place.split('-')[0]
            self.place = '-'.join(place.split('-')[1:])
        else:
            self.alpha3code = place

        self.title = f"Aerial images collected by {self.platform}, {self.place}, {self.alpha3code} - {self.date} - {session_number}"

    def generate_metadata(self, opt: Namespace) -> None:
        """ Main function to generate metadata. """

        # Prepare folder.
        self.setup_session(opt.clean)

        # Generate gps gpkg.
        self.create_survey_gpkg()

        # Generate HTML and PDF report
        self.generate_pdf_and_html_report()


    def setup_session(self, need_clean: bool = True) -> None:
        """ Clean and create folder."""
        print("\n-- func: Create and clean folder.")
        
        if self.GPS_FOLDER.exists() and need_clean:
            shutil.rmtree(self.GPS_FOLDER)
        self.GPS_FOLDER.mkdir(exist_ok=True, parents=True)


        self.GPS_DEVICE_FOLDER.mkdir(exist_ok=True, parents=True)

        if self.METADATA_FOLDER.exists() and need_clean:
            shutil.rmtree(self.METADATA_FOLDER)
        self.METADATA_FOLDER.mkdir(exist_ok=True, parents=True)
    

    def get_img_list(self) -> list[Path]:

        if len(self.img_list) != 0: return self.img_list 

        self.img_list = sorted([img for img in list(self.DCIM_FOLDER.iterdir()) if img.suffix.lower() in [".png", ".jpg", ".jpeg"]])

        return self.img_list
    

    def create_survey_gpkg(self) -> None:
        print("\n-- func: Create and save Survey Gpkg and metadata.")

        self.metadata_df = images_coords(self.get_img_list())
        self.metadata_df["relative_file_path"] = self.metadata_df.apply(lambda row: f"{self.session.name}/DCIM/{row['FileName']}", axis=1)

        self.metadata_gdf = gpd.GeoDataFrame(self.metadata_df, geometry = gpd.points_from_xy(self.metadata_df['GPSLongitude'], self.metadata_df['GPSLatitude']), crs = 'EPSG:4326')
        self.gdfutm = self.metadata_gdf.to_crs(self.metadata_gdf.estimate_utm_crs())
        geom_mdt = "SurveyMetadata.gpkg"

        print("func: Compute convex hull")
        survey_polygon = Polygon(self.gdfutm.geometry.to_list()).convex_hull
        self.survey_area = round(survey_polygon.area/10000, 2)
        survey_polygon_gdf = gpd.GeoDataFrame(pd.DataFrame({'Identifier':[self.session.name], 'polygon':[survey_polygon]}), geometry='polygon', crs = self.gdfutm.crs.srs)
        
        print("func: Export BBOX to GPKG")
        survey_polygon_gdf.to_file(Path(self.GPS_DEVICE_FOLDER, geom_mdt), layer="emprise", driver="GPKG")
        
        print("func: Exporting geolocation files including thumbnails: it could take some time !")
        self.gdfutm.to_file(Path(self.GPS_DEVICE_FOLDER, geom_mdt), layer="images", driver='GPKG')

        print("func: Exporting metadata.csv !")
        self.metadata_gdf.to_csv(Path(self.METADATA_FOLDER, "metadata.csv"), quoting=1, quotechar='"', index=False)

        print("func: Create thumbails pdf")
        series_to_img(self.get_img_list(), self.session)


    def generate_pdf_and_html_report(self) -> None:
        print("\n-- func: Generate PDF and HTML report.")

        # Minimal information to export in pdf
        nb_images = len(self.img_list)
        bb = bbox(self.metadata_df)
        lon = str(center_bbox(bb)[0])
        lat = str(center_bbox(bb)[1])
        begin = datebe(self.metadata_df)[0].replace(":", "-")
        end = datebe(self.metadata_df)[1].replace(":", "-")
        exif = str(common_tags(self.img_list)).replace(",", "\n").replace("{","").replace("}","").replace("'","")
        condition = meteo(lat, lon, begin, end, "best_match")
        alt = altimg(self.metadata_df)
        start = self.metadata_df['DateTime'].min()
        end = self.metadata_df['DateTime'].max()

        survey_info_minimal = "- Camera model and parameters:\n" + " " + str(exif) + \
            "\n\n- Survey informations:\n" + \
            " No Images: {}".format(str(nb_images) + "\n") + \
            " Median height: {}".format(str(round(alt)))+" meters\n" + \
            " Survey area: {}".format(str(self.survey_area))+" hectares\n" + \
            " Survey from: " + start + " to: " + end
        
        survey_info = (survey_info_minimal + "\n\nUTM Coordinate system:\n" +
                                                        " " + self.gdfutm.crs.name + "\n" +
                                                        " " + self.gdfutm.crs.srs + "\n Description:\n" +
                                                        str(self.gdfutm.crs.area_of_use).replace("- ", "  ") +
                                                        "\n\n- Meteo:\n" + str(condition)
                                                        )

        print("func: Generate map")
        map = define_map(self.metadata_gdf, self.session, self.title, nb_images, str(round(alt)), self.survey_area, start, end)
        
        print("func: Generate html")
        map_to_html = map_html(map, survey_info, self.metadata_gdf)
        
        print("func: Save html to disk")
        html_file= Path(self.METADATA_FOLDER,"Report_" + start.replace(":","-").replace(" ", "_") + "_" + str(nb_images) + "-JPEGs.html")
        with open(html_file, "w") as html_fn:
            html_fn.write(map_to_html)

        print("func: Convert html to pdf")
        convert_map_pdf(html_file)
    

    def get_spatial_coverage(self) -> str:
        """ Return spatial coverage in geoflow format."""
        pol = Polygon(self.metadata_gdf.geometry.to_list()).convex_hull
        srid = int(str(self.metadata_gdf.crs.srs).split(":")[1])
        # return f"srid:{srid}"
        return f"SRID={srid};{pol}"
    

    def get_temporal_coverage(self) -> str:
        """ Return temporal coverga in geoflow format."""
        begin, end = datebe(self.metadata_df)
        begin_d, begin_h = begin.split(' ')
        end_d, end_h = end.split(' ')
        begin_d = begin_d.replace(':', '-')
        end_d = end_d.replace(':', '-')

        return f"{begin_d}T{begin_h}Z/{end_d}T{end_h}Z"