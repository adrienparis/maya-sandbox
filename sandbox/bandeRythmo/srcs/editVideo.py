from moviepy.editor import VideoFileClip
from skimage.filters import gaussian_filter
def blur(image):
    """ Returns a blurred (radius=2 pixels) version of the image """
    return gaussian_filter(image.astype(float), sigma=2)



mp4path = r"S:\a.paris\Downloads\Kaamelott - drakkars.mp4"

clip = VideoFileClip(mp4path)

clip_blurred = clip.fl_image( blur )
clip_blurred.write_videofile("blurred_video.mp4")