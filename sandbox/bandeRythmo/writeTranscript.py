# Import everything needed to edit video clips 
from moviepy.editor import *
    
# loading video dsa gfg intro video 
clip = VideoFileClip(r"C:\Users\paris_a\Documents\Creative Seeds\Random\doublage\capture\robots\hitfilm_mp4\robots.Les_mensonges_invente.mp4") 
    
# clipping of the video  
# getting video for only starting 10 seconds 
clip = clip.subclip(0, 10) 
    
# Reduce the audio volume (volume x 0.8) 
clip = clip.volumex(0.8) 
    
# Generate a text clip 
txt_clip = TextClip("GeeksforGeeks", fontsize = 75, color = 'black') 
    
# setting position of text in the center and duration will be 10 seconds 
txt_clip = txt_clip.set_pos('center').set_duration(10) 
    
# Overlay the text clip on the first video clip 
video = CompositeVideoClip([clip, txt_clip]) 
    
# showing video 
video.ipython_display(width = 280) 