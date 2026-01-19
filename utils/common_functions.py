import os
from src.logger import get_logger
from src.custom_exception import CustomException
import yaml
import pandas as pd

logger = get_logger(__name__)

def read_yaml(file_path):
    """
    This function reads a YAML file and returns its contents as a dictionary.
    file_path : str : path to the YAML file
    Returns a dictionary containing the YAML file contents.
    """
    
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File is not in the given path")
        
        with open(file_path,"r") as yaml_file:
            config = yaml.safe_load(yaml_file)
            logger.info("Succesfully read the YAML file")
            return config
    
    except Exception as e:
        logger.error("Error while reading YAML file")
        raise CustomException("Failed to read YAMl file" , e)
    