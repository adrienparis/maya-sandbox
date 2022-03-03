import os
from moviepy.editor import *
import librosa
import numpy as np

mp4path = r"S:\a.paris\Downloads\Kaamelott - drakkars.mp4"
mp3path = r"S:\a.paris\Downloads\Kaamelott - drakkars.mp3"
video = VideoFileClip(mp4path)
video.audio.write_audiofile(mp3path)


y, sr = librosa.load(mp3path, duration=120)

# And compute the spectrogram magnitude and phase
S_full, phase = librosa.magphase(librosa.stft(y))

S_filter = librosa.decompose.nn_filter(S_full,
                                       aggregate=np.median,
                                       metric='cosine',
                                       width=int(librosa.time_to_frames(2, sr=sr)))

# The output of the filter shouldn't be greater than the input
# if we assume signals are additive.  Taking the pointwise minimium
# with the input spectrum forces this.
S_filter = np.minimum(S_full, S_filter)