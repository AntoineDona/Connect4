import logging
import os
from os import path

SCRIPT_PATH = path.dirname(path.abspath(__file__))

LOGS_PATH = path.join(SCRIPT_PATH, "logs")
if not path.exists(LOGS_PATH):
    os.makedirs(LOGS_PATH, exist_ok=True)

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
file_handler = logging.FileHandler(path.join(LOGS_PATH, "fv.log"))
formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
file_handler.setFormatter(formatter)
LOGGER.addHandler(file_handler)