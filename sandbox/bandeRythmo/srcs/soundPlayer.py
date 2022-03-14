# -*- coding: utf-8 -*-

from xmlrpc.client import DateTime
import pygame
from pygame import mixer
import cv2
import datetime

import readDetx
import sys

TXT_WIDTH = 500
TXT_HEIGHT = 50

class LineImg():
    def __init__(self, line, font):
        self.line = line
        self.font = font
        self.loaded = False
        self.role = self.line.role
        c = self.role.color.replace("#", '')
        self.color = [int(c[i:i+2],16) for i in range(0,len(c),2)]
        self.width = int((self.line.timecodeEnd - self.line.timecodeStart).total_seconds() * TXT_WIDTH)
        self.timeStart = self.line.timecodeStart
        self.timeEnd = self.line.timecodeEnd
        # print(self.line.timecodeEnd, self.line.timecodeStart)
        # print((self.line.timecodeEnd - self.line.timecodeStart).total_seconds())
        self.frame = pygame.Surface((self.width, TXT_HEIGHT + 8), pygame.SRCALPHA, 32)
        # self.frame = pygame.Surface((self.width, TXT_HEIGHT + 8), 32)
        # self.frame.set_alpha(256)
        self.frame = self.frame.convert_alpha()

    def load(self):
        if self.loaded:
            return
        for ti in self.line.text:
            txt = ti[2]
            size = int((ti[1] - ti[0]).total_seconds()  * TXT_WIDTH)
            pos = int((ti[0] - self.timeStart).total_seconds() * TXT_WIDTH)
            # print(txt, (ti[1] - ti[0]).total_seconds(), (ti[0] - self.timeStart).total_seconds())
            img_txt = self.font.render(txt, True, self.color)
            img_txt = pygame.transform.scale(img_txt, (size, TXT_HEIGHT))
            # pygame.draw.rect(self.frame, (0,255,0), pygame.Rect(pos, 0, 1, TXT_HEIGHT + 8))
            # pygame.draw.rect(self.frame, (0,0,255), pygame.Rect(pos + size - 1, 0, 1, TXT_HEIGHT + 8))

            self.frame.blit(img_txt, (pos,4))
        self.loaded = True

    def unload(self):
        self.loaded = False


    def getPos(self, currentTime):
        return int((currentTime - self.line.timecodeStart).total_seconds() * TXT_WIDTH)

class SeparatorShotImg():
    def __init__(self, timecode):
        self.loaded = False
        self.timecode = timecode
        self.frame = pygame.Surface((5, 320), pygame.SRCALPHA, 32)  # the TXT_WIDTH of your rect
        pygame.draw.rect(self.frame, (50,50,50), pygame.Rect(0, 0, 5, 320))


    def getPos(self, currentTime):
        return int((currentTime - self.timecode).total_seconds()  * TXT_WIDTH)

originalSndFlPth = r"C:\Users\paris_a\Documents\Creative Seeds\Random\doublage\montage\robot\un ticket pour robot ville\robots.un_ticket_pour_robotville.original.mp3"
noVoicesSndFlPth = r"C:\Users\paris_a\Documents\Creative Seeds\Random\doublage\montage\robot\un ticket pour robot ville\robots.un_ticket_pour_robotville.novoices.mp3"
video_path = r"C:\Users\paris_a\Documents\Creative Seeds\Random\doublage\capture\robots\hitfilm_mp4\robots.un_ticket_pour_robotville.mp4"
transcript_path = r"C:\Users\paris_a\Documents\Creative Seeds\Random\doublage\banderythmo\Robots.Un_ticket_pour_robotville.detx"

# originalSndFlPth = r"C:\Users\paris_a\Documents\Creative Seeds\Random\doublage\montage\robot\meet the rusties\robots.meet_the_rusties.original.mp3"
# noVoicesSndFlPth = r"C:\Users\paris_a\Documents\Creative Seeds\Random\doublage\montage\robot\meet the rusties\robots.meet_the_rusties.novoices.mp3"
# video_path = r"C:\Users\paris_a\Documents\Creative Seeds\Random\doublage\capture\robots\hitfilm_mp4\robots.meet_the_rusties.mp4"
# transcript_path = r"C:\Users\paris_a\Documents\Creative Seeds\Random\doublage\banderythmo\Robots.meet_the_rusties.detx"

# originalSndFlPth = r"C:\Users\paris_a\Documents\Creative Seeds\Random\doublage\capture\eldorado\Untitled_1_.mp3"
# noVoicesSndFlPth = r"C:\Users\paris_a\Documents\Creative Seeds\Random\doublage\capture\eldorado\el-dorado.mp3"
# video_path = r"C:\Users\paris_a\Documents\Creative Seeds\Random\doublage\capture\eldorado\netflix-mozilla-firefox-2021-12-12-22-43-04_cZiEHbbh.mp4"
# transcript_path = r"C:\Users\paris_a\Documents\Creative Seeds\Random\doublage\banderythmo\el-dorado.duel.detx"

originalSndFlPth = r"S:\a.paris\Download\robots.meet_the_rusties.lowdef.mp3"
noVoicesSndFlPth = r"S:\a.paris\Download\robots.meet_the_rusties.lowdef.mp3_music.mp3"
video_path = r"D:\a.paris\Random\doublage\bandeRythmo\01_extrait\robots\hitfilm_mp4\robots.meet_the_rusties.mp4"
transcript_path = r"D:\a.paris\Random\doublage\bandeRythmo\02_cappella_files\Robots.meet_the_rusties.detx"

balises = readDetx.Balise.read(transcript_path)
roles = readDetx.Role.getRoles(balises[0][1])
shotCut = readDetx.getShots(balises)
readDetx.Line.getLines(balises[0][2], roles)


# exit()
# mixer.init()                    # Starting the mixer
# mixer.music.load(originalSndFlPth) # Loading the song
# mixer.music.set_volume(0.7)     # Setting the volume
# mixer.music.play()              # Start playing the song

pygame.mixer.init()
mus_org = pygame.mixer.Sound(originalSndFlPth)
mus_nVc = pygame.mixer.Sound(noVoicesSndFlPth)






FPS = 60
REDLINEPOS = 200
pygame.init()
clock = pygame.time.Clock()

video = cv2.VideoCapture(video_path)
success, video_image = video.read()
video_fps = video.get(cv2.CAP_PROP_FPS)
print("fps: ", video_fps)
print((FPS / video_fps))
fpsCorrection = (FPS / video_fps)


imageTXT_WIDTH = video_image.shape[1::-1]
imageTXT_WIDTH = (1920, 1040)
window = pygame.display.set_mode(imageTXT_WIDTH)

mus_org.play(0)
mus_nVc.play(0)

fonFolder = r".\ToolBox\sandbox\bandeRythmo\fonts/" 
fonFolder = r".\sandbox\bandeRythmo\fonts/"

fontPath = fonFolder + r"Chateau des Oliviers.ttf"
fontPath = fonFolder + r"Cornelia.ttf"
fontPath = fonFolder + r"Homeday.otf"
fontPath = fonFolder + r"Gendis Script Test.ttf"
fontPath = fonFolder + r"KGRedHands.ttf"
fontPath = fonFolder + r"SleeptightDisplayRegular.ttf"

font = pygame.font.Font(fontPath, 128, italic=True)
font_fps = pygame.font.SysFont("comic", 32)
# font.italic()
GAP = datetime.timedelta(seconds=5)

# success = True
# imagesFrames = []
# while success:
#     success, video_image = video.read()
#     imagesFrames.append(video_image)


playing = True
switchVoice = False
loopTime = datetime.datetime.now()
gapTime = datetime.timedelta(seconds=0)
currentTime = datetime.timedelta(seconds=0)
lines = []
for k, v in roles.items():
    lines += v.lines
imgLines = [LineImg(x, font) for x in lines]
imgShot = [SeparatorShotImg(x) for x in shotCut]


i = 0
paused = False
while playing:
    gapTime = datetime.datetime.now() - loopTime
    loopTime = datetime.datetime.now()
    if not paused:
        currentTime += gapTime
    clock.tick(FPS)
    fps = clock.get_fps()

    # switching instrumental/originale
    speaking = False
    # for char in ['controleur', 'pere']:
    for char in ['fender', "miguael"]:
    # for char in []:
        if char in roles:
            speaking = max(roles[char].isSpeaking(currentTime, 0.01), speaking)

    if speaking:
        mus_org.set_volume(0)
        mus_nVc.set_volume(1)
    else:
        mus_org.set_volume(1)
        mus_nVc.set_volume(0)



    # events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            playing = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                playing = False
            if event.key == pygame.K_SPACE:
                paused = not paused
                if paused:
                    pygame.mixer.pause()
                else:
                    pygame.mixer.unpause()


    # Playing Video
    fpsCorrection = max((fps / max(video_fps, 1)), 1)
    if int(i % fpsCorrection) == 0 and not paused:
        success, video_image = video.read()
    i += 1

    if success:
        video_surf = pygame.image.frombuffer(
            video_image.tobytes(), video_image.shape[1::-1], "BGR")
        # video_surf = pygame.transform.scale(video_surf, imageTXT_WIDTH)
        video_surf = pygame.transform.scale(video_surf, (960, 520))
        
    else:
        playing = False

    # Loading Lines
    window.blit(pygame.Surface(imageTXT_WIDTH, 32), (0, 0))

    for il in imgLines:
        if il.timeStart - GAP <= currentTime and currentTime <= il.timeStart:
            il.load()
        if il.timeEnd + GAP <= currentTime and currentTime <= il.timeEnd + 2 * GAP:
            il.unload()

    window.blit(video_surf, (0, 0))
    for imgS in imgShot:
        window.blit(imgS.frame, (REDLINEPOS - imgS.getPos(currentTime), imageTXT_WIDTH[1] - 400))

    for il in imgLines:
        if il.loaded:
            window.blit(il.frame, (REDLINEPOS - il.getPos(currentTime), imageTXT_WIDTH[1] - 400 + (TXT_HEIGHT + 8) * il.line.track))
            # window.blit(il.frame, (REDLINEPOS, imageTXT_WIDTH[1] - 150 + 20 * il.line.track))

    pygame.draw.rect(window, (255,0,0), pygame.Rect(REDLINEPOS, imageTXT_WIDTH[1] - 400, 3, 350))

    fps_txt = font_fps.render(str(fps), True, (255,255,255))
    window.blit(fps_txt, (0,0))

    pygame.display.flip()

pygame.quit()
