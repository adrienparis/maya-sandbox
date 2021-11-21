import subprocess

def play_mp3(path):
    subprocess.Popen(['mpg123', '-q', path]).wait()

path = r"S:\a.paris\Downloads\minecraft-glass-break-sound-effect-hd.mp3"

play_mp3(path)