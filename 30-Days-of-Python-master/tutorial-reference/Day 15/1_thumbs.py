from conf import SAMPLE_INPUTS, SAMPLE_OUTPUTS
from moviepy.editor import *
from PIL import Image

source_path = os.path.join(SAMPLE_INPUTS, 'sample.mp4')
thumbnail_dir = os.path.join(SAMPLE_OUTPUTS, "thumbnails")
thumbnail_per_frame_dir = os.path.join(SAMPLE_OUTPUTS, "thumbnails-per-frame")
thumbnail_per_half_second_dir = os.path.join(SAMPLE_OUTPUTS, "thumbnails-per-half-second")

os.makedirs(thumbnail_dir, exist_ok=True)
os.makedirs(thumbnail_per_frame_dir, exist_ok=True)
os.makedirs(thumbnail_per_half_second_dir, exist_ok=True)


clip = VideoFileClip(source_path)
print(clip.reader.fps) # frames per second
print(clip.reader.nframes)
print(clip.duration) # seconds
duration = clip.duration # clip.reader.duration
max_duration = int(duration) + 1
for i in range(0, max_duration):
    frame = clip.get_frame(i)
    # print(frame) # np.array numpy array # inference
    new_img_filepath = os.path.join(thumbnail_dir, f"{i}.jpg")
    # print(f"frame at {i} seconds saved at {new_img_filepath}")
    new_img = Image.fromarray(frame)
    new_img.save(new_img_filepath)



print(clip.reader.fps) # frames per second
print(clip.reader.nframes)

fps = clip.reader.fps
nframes = clip.reader.nframes
seconds = nframes / (fps * 1.0)

for i, frame in enumerate(clip.iter_frames()):
    # print(frame) # np.array numpy array # inference
    if i % fps == 0:
        current_ms = int((i / fps) * 1000)
        new_img_filepath = os.path.join(thumbnail_per_frame_dir, f"{current_ms}.jpg")
        # print(f"frame at {i} seconds saved at {new_img_filepath}")
        new_img = Image.fromarray(frame)
        new_img.save(new_img_filepath)



for i, frame in enumerate(clip.iter_frames()):
    # print(frame) # np.array numpy array # inference
    fphs = int(fps/2.0)
    if i % fphs == 0:
        current_ms = int((i / fps) * 1000)
        new_img_filepath = os.path.join(thumbnail_per_half_second_dir, f"{current_ms}.jpg")
        # print(f"frame at {i} seconds saved at {new_img_filepath}")
        new_img = Image.fromarray(frame)
        new_img.save(new_img_filepath)