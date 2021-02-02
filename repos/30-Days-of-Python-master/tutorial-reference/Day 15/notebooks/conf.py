import os
from moviepy.editor import *
from moviepy.video import fx

ABS_PATH = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(ABS_PATH))
DATA_DIR = os.path.join(BASE_DIR, "data")
SAMPLE_DIR = os.path.join(DATA_DIR, "samples")
SAMPLE_INPUTS = os.path.join(SAMPLE_DIR, "inputs")
SAMPLE_OUTPUTS = os.path.join(SAMPLE_DIR, 'outputs')


os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SAMPLE_INPUTS, exist_ok=True)
os.makedirs(SAMPLE_OUTPUTS, exist_ok=True)

