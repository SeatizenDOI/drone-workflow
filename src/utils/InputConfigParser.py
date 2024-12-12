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
        
        jsd = {}
        with open(path, "r") as file:
            jsd = json.load(file)

        return jsd


    def get_description(self) -> str:
        a = self.input_config['description']['abstract']
        p = self.input_config['description']['purpose']
        c = self.input_config['description']['credit']
        i = self.input_config['description']['info']
        e = self.input_config['description']['edition']
        s = self.input_config['description']['status']

        return f"abstract:'{a}'_\npurpose:'{p}'_\ncredit:'{c}'_\ninfo:'{i}'_\nedition:'{e}'_\nstatus:'{s}'"

    def get_relation(self) -> str:
        return self.input_config['relation']

    def get_type(self) -> str:
        return self.input_config['type']
    
    def get_subject(self) -> str:
        return self.input_config['subject']
    
    def get_creator(self) -> str:
        return f"owner:'{self.input_config['creator']['owner']}'"

    def get_rights(self) -> str:

        l = self.input_config['rights']['license']
        u = self.input_config['rights']['useLimitation']
        o = self.input_config['rights']['otherConstraint']

        return f"license:'{l}'_\nuseLimitation:'{u}'_\notherConstraint:'{o}'"