import os
from moviepy.editor import *
path = r"C:\Users\a.paris\Videos\Captures"
mp4path = [
            r"Netflix - Mozilla Firefox 2021-12-13 12-03-06.mp4",
            r"Netflix - Mozilla Firefox 2021-12-13 12-03-58.mp4",
          ]
for mp in mp4path:
    mp3path = mp.replace(".mp4", ".mp3")
    video = VideoFileClip(os.path.join(path, mp))
    video.audio.write_audiofile(os.path.join("./", mp3path))