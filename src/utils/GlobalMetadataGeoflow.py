import json
import shutil
import pandas as pd
from pathlib import Path
from rpy2.robjects.packages import importr

from .SessionDrone import SessionDrone
from .InputConfigParser import InputConfigParser

# https://github.com/r-geoflow/geoflow/blob/master/doc/metadata.md
class GlobalMetadataGeoflow:
    """ Wrapper to setup geoflow and called geoflow pipeline. """
    def __init__(self, folder_to_save: str, input_config_file_path: str, session_parent_folder: str, need_clean: bool):

        self.input_config_manager = InputConfigParser(input_config_file_path)
        self.session_parent_folder = session_parent_folder
        self.folder_to_save = Path(folder_to_save, session_parent_folder.replace("/", "_").replace("\\", "_").strip("_"))
        if self.folder_to_save.exists() and need_clean:
            shutil.rmtree(self.folder_to_save)
        self.folder_to_save.mkdir(parents=True, exist_ok=True) 

        self.iso19115_config_json_path = Path(self.folder_to_save, 'iso19115-config.json')
        self.iso19115_metadata_csv_path = Path(self.folder_to_save, 'iso19115-metadata.csv')


        self.sessions = []


    def generate_config_json(self):
        print("\n-- func: Create geoflow config file.")

        iso19115config = {
            'profile': {
                'id': 'iso19115', 
                'name': 'iso19115', 
                'project': 'Generate iso19115 with Geoflow', 
                'organization': 'Ifremer', 
                'logos': ['https://raw.githubusercontent.com/SeatizenDOI/.github/refs/heads/main/images/logo_partenaire_2.png'], 
                'mode': 'entity'
            }, 
            'metadata': {
                'entities': [{
                    'handler': 'csv', 
                    'source': str(self.iso19115_metadata_csv_path)
                }], 
                'contacts': [{
                    'handler': 'csv', 
                    'source': './configs/geoflow_ifremer_contacts.csv'
                }]
            }, 
            'software': [], 
            'actions': [{'id': 'geometa-create-iso-19115', "run": True}]
        }

        # Export json to file
        with open(self.iso19115_config_json_path, 'w') as f:
            json.dump(iso19115config, f, indent=4)


    def add_session(self, session: SessionDrone):
        print("\n-- func: Add session to be processed by geoflow.")

        self.sessions.append({
            "Identifier": f"id:{session.session.name}",
            "Title": f"title:{session.title}",
            "Description": self.input_config_manager.get_description(),
            "Subject": "discipline:'aled'",
            "Date": "publication:2021-03-22",
            "Creator": self.input_config_manager.get_creator(),
            "Type": self.input_config_manager.get_type(),
            "Language": "eng",
            "SpatialCoverage": session.get_spatial_coverage(),
            "TemporalCoverage": session.get_temporal_coverage(),
            "Format": "resource:text/csv",
            "Relation": self.input_config_manager.get_relation(),
            "Rights": self.input_config_manager.get_rights(),
            "Provenance": "statement:My data management workflow", 
            "Data": "source:README.md@https://raw.githubusercontent.com/eblondel/zen4R/master/README.md"
        })


    def generate_metadata_geoflow(self):
        print("\n-- func: Create geoflow metadata file.")
        header = [ 
            "Identifier", "Title", "Description", "Subject", "Date", "Creator", \
            "Type", "Language", "SpatialCoverage", "TemporalCoverage", "Format", \
            "Relation", "Rights", "Provenance", "Data"
        ]

        df = pd.DataFrame(self.sessions, columns=header)

        df.to_csv(Path(self.folder_to_save, "iso19115-metadata.csv"), index=False)


    def launch_geoflow(self, R_LIB_DIRECTORY):
        print("\n-- func: Launch geoflow pipeline.")

        try:
            geoflow = importr('geoflow', lib_loc=R_LIB_DIRECTORY)
        except Exception as e:
            print(f"Error when trying to import geoflow lib: {e}")
            return

        if not self.iso19115_config_json_path.exists():
            print(f"Cannot find iso19115 config file, cannot execute geoflow workflow")
            return
        
        print("func: geoflow package found")
        gf = geoflow.executeWorkflow(str(self.iso19115_config_json_path), str(self.folder_to_save))
        return gf


    def move_xml_files(self):

        # Get last jobs folder.
        jobs_folder = sorted(list(Path(self.folder_to_save, "jobs").iterdir()), reverse=True)[0]
        entities_folder = Path(jobs_folder, "entities")

        for session_name in entities_folder.iterdir():
            src = Path(session_name, "metadata", f"{session_name.name}_ISO-19115.xml")
            dest = Path(self.session_parent_folder, session_name.name, "METADATA", f"{session_name.name}_ISO-19115.xml")
            
            print(f"-- func: Copy {src} to {dest}")
            shutil.copy(src, dest)
