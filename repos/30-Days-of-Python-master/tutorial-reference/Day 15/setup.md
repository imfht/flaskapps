# Overview & Setup

We're going to be using Moviepy to do the following:
1. Create thumbnails from videos
2. Image Collection to Video
3. Generate a GIF animation
4. Combine Audio Samples in a Video
5. Overlay Text, Image, or Video


##### Requirements:
- Python 3.6+
- Pipenv (or another virtual environment)
- moviepy==1.0.2 (or greater)
- ffmpeg & imagemagick installed (see below)



### Installations 

#### [FFmpeg](https://www.ffmpeg.org/download.html) ([Link](https://www.ffmpeg.org/download.html))
Moviepy and ffmpeg work well together. ffmpeg can do most/all of this on it's own but, as far as this writing, lacks Python bindings. Thus, moviepy is used!

##### macOS:

Use [homebrew](http://brew.sh)

```
brew update && brew install ffmpeg
```

#### Windows/Linux:
Use the [executable](https://www.ffmpeg.org/download.html)



#### [ImageMagick](https://imagemagick.org/script/download.php) ([Link](https://imagemagick.org/script/download.php))
To add text, you must install ImageMagic.

##### macOS:

Use [homebrew](http://brew.sh)

```
brew update && brew install imagemagick
```
#### Linux:
Download [here](https://imagemagick.org/script/download.php)

#### Windows:
Use the [binary or exe](https://imagemagick.org/script/download.php#windows)



### Base Project


#### 1. Start project
We're using pipenv and [Moviepy](https://zulko.github.io/moviepy/) ([Link](https://zulko.github.io/moviepy/))

```
cd path/to/your/project/folder/
```

```
pipenv install --python 3.8 moviepy
pipenv shell
mkdir data
mkdir data/samples
mkdir data/samples/inputs
mkdir data/samples/outputs
```


#### 2. Create `conf.py`

```python
import os

ABS_PATH = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(ABS_PATH)
DATA_DIR = os.path.join(BASE_DIR, "data")
SAMPLE_DIR = os.path.join(DATA_DIR, "samples")
SAMPLE_INPUTS = os.path.join(SAMPLE_DIR, "inputs")
SAMPLE_OUTPUTS = os.path.join(SAMPLE_DIR, 'outputs')
```


#### 3. Download sample audio and video

- [audio.mp3](https://github.com/codingforentrepreneurs/30-Days-of-Python/raw/master/tutorial-reference/Day%2015/data/samples/inputs/audio.mp3)
- [sample.mp4](https://github.com/codingforentrepreneurs/30-Days-of-Python/raw/master/tutorial-reference/Day%2015/data/samples/inputs/sample.mp4)

Once downloaded, move these files to your project's `data/samples/inputs` directory.
