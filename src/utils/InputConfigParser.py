import json
from pathlib import Path

# TODO loop under all subkey to automatically add new key

class InputConfigParser:

    def __init__(self, input_config_file_path: str):
        
        self.input_config = self.load_input_config_file(input_config_file_path)

    
    def load_input_config_file(self, input_config_file_path: str) -> None:
        path = Path(input_config_file_path)
        
        if not path.exists():
            raise NameError(f"Input config file not found at path {path}")
        
        json_content = {}
        with open(path, "r") as file:
            json_content = json.load(file)

        return json_content


    def parse_head_key(self, big_key_name: str) -> str:
        """ From config file parse subkey """
        content = ""
        for key in self.input_config[big_key_name]:
            if self.input_config[big_key_name][key] == "": continue
            content += f"{key}:'{self.input_config[big_key_name][key]}'_\n"
        return content.strip("_\n")


    def get_description(self) -> str:
        description = self.parse_head_key("description")
        if description == "":
            raise NameError("Description is mandatory please fill at least abstract in config file.")
        return description


    def get_relation(self) -> str:
        return self.input_config['relation']


    def get_type(self) -> str:
        return self.input_config['type']
    

    def get_subject(self) -> str:
        return self.input_config['subject']


    def get_creator(self) -> str:
        return self.parse_head_key("creator")


    def get_rights(self) -> str:
        return self.parse_head_key("rights")