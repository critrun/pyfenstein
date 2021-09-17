#AFR POWERED GAME
#Anton's Fast Render

#Update pip and install pgzero
import os
os.system("python -m pip install --upgrade pip --user")
os.system("python -m pip install pgzero --user")
os.system("python -m pip install numpy --user")
os.system("python -m pip install opencv-python --user")

#Do necessary imports
import pgzrun
import _pickle as p
import math as m
import timeit
import cv2
import numpy as np
import mouse as mouselib
from random import randint

#Define read write commands
def read(path):
    "Reads and returns object from given file path."
    with open(path, "rb") as input:
        return p.load(input)

def write(path, Object):
    "Writes object to given path."
    with open(path, "wb") as output:
        p.dump(Object, output, -1)

#Define Fundamental commands
def importMap(path):
    global map
    map = read(path)

def writeMap(path):
    global map
    write(path, map)

def abs(n):
    if n < 0:
        return -n
    return n

def onlyDecimal(n):
    return n - int(n)

def isEven(n):
    return n%2 == 0

#Define global variables
importMap("testing.afr")
renderDistance = 5
renderResolutionClose = 4
renderResolutionFar = 8
playerRot = 0.0
playerPos = [2,2]

playerPos[0] = len(map)-playerPos[0]

#Render stuff
def renderLine(v):
    global playerPos
    global map
    global renderDistance

    #Variables can't be 0, fix it by making them very small.
    if playerPos[0] == int(playerPos[0]):
        playerPos[0]+= 0.0000000000001
    if playerPos[1] == int(playerPos[1]):
        playerPos[1]+= 0.0000000000001
    if v == int(v):
        v+= 0.0000000000001

    #Get line from rotation and position
    lk = m.tan(m.pi/2 - v)
    lm = playerPos[1] - lk * playerPos[0]

    #Set start position of the casted ray.
    currentPos = [playerPos[0], playerPos[1]]

    for _ in range(renderDistance*2):
        #Find distances to either new X line or Y line
        if (v >= 0 or v < -m.pi) and v < m.pi:
            newx = m.floor(currentPos[0]+1)
        else:
            newx = m.ceil(currentPos[0]-1)
        distx = (newx - currentPos[0])**2 + (lk * newx + lm - currentPos[1])**2

        if -m.pi/2 <= v <= m.pi/2:
            newy = m.floor(currentPos[1]+1)
        else:
            newy = m.ceil(currentPos[1]-1)
        disty = (newy - currentPos[1])**2 + ((newy - lm)/lk - currentPos[0])**2

        #If X line is closer, move to X line and vice versa.
        if distx < disty:
            #change to new position
            currentPos[0] = newx
            currentPos[1] = lk * currentPos[0] + lm
        else:
            currentPos[1] = newy
            currentPos[0] = (currentPos[1] - lm)/lk
        
        #get coordinates of colliding blocks
        if type(currentPos[0]) is int:
            b0 = (currentPos[0], m.floor(currentPos[1]))
            b1 = (currentPos[0]-1, m.floor(currentPos[1]))
        else:
            b0 = (m.floor(currentPos[0]), currentPos[1])
            b1 = (m.floor(currentPos[0]), currentPos[1]-1)

        #See if there is a collision
        try:
            if map[b0[0]][b0[1]] != 0 :
                return ((playerPos[0] - currentPos[0])**2 + (playerPos[1] - currentPos[1])**2)**0.5, onlyDecimal(int(type(currentPos[0]) is float)*currentPos[0] + int(type(currentPos[1]) is float)*currentPos[1]), map[b0[0]][b0[1]]
            elif map[b1[0]][b1[1]] != 0:
                return ((playerPos[0] - currentPos[0])**2 + (playerPos[1] - currentPos[1])**2)**0.5, onlyDecimal(int(type(currentPos[0]) is float)*currentPos[0] + int(type(currentPos[1]) is float)*currentPos[1]), map[b1[0]][b1[1]]
        except:
            return -1, 0, 0
    return -1, 0, 0

#PyGame stuff
WIDTH = 1280
HEIGHT = 720
wallHeight = 1
playerHeight = 0.65
fov = 90
maxVelocity = 2.5
acceleration = 10
breaking = 5
fogColor = (29,53,50)
groundColor = (129,122,145)
roofColor = (68,64,76)
bulletColor = (107,158,255)
noiseFidelity = 32
noiseIntensity = 10
mouseSensitivity = 0.5
gunModelSize = 2.5
bobbingLength = 0.08
bobbingSpeed = 0.15
bulletSize = 0.02
bulletSpeed = 10
bulletGravity = 0.04
bulletSpawnToSideAmount = 0.1 #Can't be 0
reloadTime = 0.4
firingTime = 0.1
magazineSize = 100
autoReload = True
fullyAutomatic = True

noiseList = [randint(0, noiseIntensity) for _ in range(noiseFidelity)]
fov*= m.pi/180
focalDistance = WIDTH/(2*m.tan(fov/2))
maxDistance = m.tan(fov/2)
stepSize = (maxDistance*2) / WIDTH
bullets = []

#Generate skybox to make fog more convincing
skybox = np.zeros((HEIGHT,WIDTH,3), np.uint8)
skybox = cv2.rectangle(skybox,(0,0),(WIDTH,HEIGHT),groundColor,3)
for rrow in range(int(HEIGHT/2)):
    row = int(HEIGHT/2 - rrow)
    dist = (focalDistance * wallHeight) / max(abs(row*2 - HEIGHT), 0.000001)

    perspectiveHeight = (focalDistance * (playerHeight + bobbingLength/2 - wallHeight/2)) / dist

    fogRatio = min(dist/renderDistance, 1)
    color = (fogRatio * fogColor[2] + (1 - fogRatio) * roofColor[2], fogRatio * fogColor[1] + (1 - fogRatio) * roofColor[1], fogRatio * fogColor[0] + (1 - fogRatio) * roofColor[0])
    skybox = cv2.line(skybox,(0,row+int(perspectiveHeight)),(WIDTH,row+int(perspectiveHeight)),color,1)
    skybox = cv2.rectangle(skybox, (0,row+int(perspectiveHeight)), (WIDTH, 0), color, thickness=-1)
for row in range(int(HEIGHT/2)):
    dist = (focalDistance * wallHeight) / max(abs((int(HEIGHT/2)-row)*2 - HEIGHT), 0.000001)

    perspectiveHeight = (focalDistance * (playerHeight + bobbingLength/2 - wallHeight/2)) / dist

    fogRatio = min(dist/renderDistance, 1)
    color = (fogRatio * fogColor[2] + (1 - fogRatio) * groundColor[2], fogRatio * fogColor[1] + (1 - fogRatio) * groundColor[1], fogRatio * fogColor[0] + (1 - fogRatio) * groundColor[0])
    skybox = cv2.rectangle(skybox, (0,row+int(HEIGHT/2)+int(perspectiveHeight)), (WIDTH, HEIGHT), color, thickness=-1)
cv2.imwrite("images/skybox.png", skybox)

#Create gun texture
gun = cv2.imread("gun.png", cv2.IMREAD_UNCHANGED)
gun = cv2.resize(gun, (int(WIDTH/gunModelSize), int((50/89)*(WIDTH/gunModelSize))), interpolation=cv2.INTER_NEAREST)
cv2.imwrite("images/gun.png", gun)

leftIsDown=False
focused = False
def on_mouse_up(button, pos):
    global focused
    global leftIsDown
    if not focused and mouse.RIGHT is button:
        focused = True
        mouselib.move(int(WIDTH/2)-pos[0], int(HEIGHT/2)-pos[1], absolute=False)
    elif focused and mouse.RIGHT is button:
        focused = False
    if mouse.LEFT is button:
        leftIsDown = False
        

fireTimer = 0
reloadTimer = 0
magazine = magazineSize
def on_mouse_down(button):
    global fireTimer
    global magazine
    global reloadTimer
    global leftIsDown
    if mouse.LEFT is button:
        leftIsDown = True
    if mouse.LEFT is button:
        if magazine > 0:
            if not fullyAutomatic:
                if reloadTimer < timeit.default_timer() - reloadTime:
                    if fireTimer < timeit.default_timer() - firingTime:
                        fireTimer = timeit.default_timer()
                        sounds.fire.play()
                        magazine-= 1
                        vector = [m.sin(playerRot), m.cos(playerRot), 0]
                        right = [m.sin(playerRot+m.pi/2), m.cos(playerRot+m.pi/2)]
                        bullets.append((playerPos[0]+right[0]*bulletSpawnToSideAmount, playerPos[1]+right[1]*bulletSpawnToSideAmount, playerHeight, vector, False))
        elif not autoReload:
            reloadTimer = timeit.default_timer()
            sounds.reload.play()
            magazine = magazineSize

def on_key_down(key):
    global magazine
    global reloadTimer
    if key == keys.R and fireTimer < timeit.default_timer() - firingTime and magazine != magazineSize:
        reloadTimer = timeit.default_timer()
        sounds.reload.play()
        magazine = magazineSize

def on_mouse_move(pos):
    global playerRot
    global focused
    if focused:
        playerRot+= ((pos[0]-int(WIDTH/2))/ 100)*mouseSensitivity
        mouselib.move(int(WIDTH/2)-pos[0], int(HEIGHT/2)-pos[1], absolute=False)

def draw():
    #Draw 3D graphics
    screen.fill(groundColor)
    screen.blit("skybox", (0,0))
    i=0
    while True:
        v = m.atan(maxDistance - stepSize*i)
        dist, textureRow, wallColor = renderLine(playerRot - v)
        width = 1
        if dist != -1:
            dist*= m.cos(abs(v))
            height = (focalDistance * wallHeight) / dist
            width = int(min(dist / renderDistance, 1)*(renderResolutionFar-renderResolutionClose))+renderResolutionClose

            #Add player height here and fix skybox to account for the fog changes.
            perspectiveHeight = (focalDistance * (playerHeight + bobbing[0] - wallHeight/2)) / dist

            fogRatio = min(dist/renderDistance, 1)

            noise = noiseList[m.floor(textureRow*(noiseFidelity-1))]
            wallColor = max(wallColor[0] - noise, 0), max(wallColor[1] - noise, 0), max(wallColor[2] - noise, 0)

            color = (fogRatio * fogColor[0] + (1 - fogRatio) * wallColor[0], fogRatio * fogColor[1] + (1 - fogRatio) * wallColor[1], fogRatio * fogColor[2] + (1 - fogRatio) * wallColor[2])
            
            rect = Rect((i, int(HEIGHT / 2 - height / 2 + perspectiveHeight)), (width, int(height)))
            screen.draw.filled_rect(rect, color)
        i+=width
        if i >= WIDTH:
            break
    #Draw bullets
    #bullet = (2.5,2.5,0.5)
    for bullet in bullets:
        v = abs(m.atan((bullet[1] - playerPos[1]) / (bullet[0] - playerPos[0]))-m.pi/2) - m.pi * int(bullet[0] - playerPos[0] < 0)
        i = (maxDistance - m.tan(playerRot - v))/stepSize
        if 0 <= i < WIDTH:
            v = m.atan(maxDistance - stepSize*i)
            dist, _, _ = renderLine(playerRot - v)
            bulletDist = ((playerPos[0] - bullet[0])**2 + (playerPos[1] - bullet[1])**2)**0.5
            if dist > bulletDist or dist == -1:
                height = (focalDistance * bullet[2]) / bulletDist
                size = (focalDistance * bulletSize) / bulletDist
                perspectiveHeight = (focalDistance * (playerHeight + bobbing[0] - bullet[2]/2)) / bulletDist
                fogRatio = min(bulletDist/renderDistance, 1)
                color = (fogRatio * fogColor[0] + (1 - fogRatio) * bulletColor[0], fogRatio * fogColor[1] + (1 - fogRatio) * bulletColor[1], fogRatio * fogColor[2] + (1 - fogRatio) * bulletColor[2])
                screen.draw.filled_circle((i, int(HEIGHT / 2 - height / 2 + perspectiveHeight)), size, color)
    #Draw HUD
    screen.blit("gun", (bobbing[0]*150 + WIDTH - int(WIDTH/gunModelSize), (((m.sin(bobbing[0]*((m.pi*2)/bobbingLength)-m.pi/2)+1)/2)*10 + HEIGHT - int((50/89)*(WIDTH/gunModelSize)))))
    screen.draw.text(str(round(10/passedTime)/10), topleft = (10,10), fontsize=60, color=(0,0,0))

last = 0.000001
passedTime = 0
lastPos = 0
lastCor = 0
bobbing = [0, 0]
velocity = [0, 0]
def update():
    global last
    global playerRot
    global passedTime
    global lastPos
    global lastCor
    global bobbing
    global velocity
    global bullets
    global reloadTimer
    global magazine
    global fireTimer

    #Last positions
    lastPos = (m.floor(playerPos[0]), m.floor(playerPos[1]))
    lastCor = (playerPos[0], playerPos[1])

    #Calculating rotation matrix
    passedTime = timeit.default_timer() - last
    forward = [m.sin(playerRot), m.cos(playerRot)]
    right = [m.sin(playerRot+m.pi/2), m.cos(playerRot+m.pi/2)]

    #Apply player motion

    if keyboard.a:
        velocity[0]+= -right[0] * passedTime * acceleration
        velocity[1]+= -right[1] * passedTime * acceleration
    if keyboard.d:
        velocity[0]+= right[0] * passedTime * acceleration
        velocity[1]+= right[1] * passedTime * acceleration
    if keyboard.w:
        velocity[0]+= forward[0] * passedTime * acceleration
        velocity[1]+= forward[1] * passedTime * acceleration
    if keyboard.s:
        velocity[0]+= -forward[0] * passedTime * acceleration
        velocity[1]+= -forward[1] * passedTime * acceleration

    if not keyboard.w and not keyboard.a and not keyboard.s and not keyboard.d:
        for i in range(2):
            old_vel = velocity[i]
            if velocity[i] < 0:
                velocity[i]+= breaking * passedTime
            else:
                velocity[i]-= breaking * passedTime
            if old_vel * velocity[i] <= 0:
                velocity[i] = 0
    
    l = (velocity[0]**2 + velocity[1]**2)**0.5
    if velocity[0]**2 + velocity[1]**2 > maxVelocity**2:
        velocity[0]*= maxVelocity / l
        velocity[1]*= maxVelocity / l
    
    playerPos[0]+= velocity[0] * passedTime
    playerPos[1]+= velocity[1] * passedTime
    
    if keyboard.left:
        playerRot-= 3 * passedTime
    if keyboard.right:
        playerRot+= 3 * passedTime
    playerRot = ((playerRot + m.pi) % (m.pi*2)) - m.pi
    
    #add bobbing
    if bobbing[1] == 0:
        bobbing[0]+= bobbingSpeed * passedTime * l
        if bobbing[0] > bobbingLength:
            bobbing[1] = 1
    else:
        bobbing[0]-= bobbingSpeed * passedTime * l
        if bobbing[0] < 0:
            bobbing[1] = 0

    #Make sure player doesn't leave the map
    if playerPos[0] < 0:
        playerPos[0] = 0
    elif playerPos[0] >= len(map):
        playerPos[0] = len(map)-0.0000001
    if playerPos[1] < 0:
        playerPos[1] = 0
    elif playerPos[1] >= len(map[0]):
        playerPos[1] = len(map[0])-0.0000001
    
    #Apply hitbox
    if map[m.floor(playerPos[0])][m.floor(playerPos[1])] != 0:
        if lastPos[0] - m.floor(playerPos[0]) != 0:
            playerPos[0] = lastCor[0]
            velocity[0] = 0
        if lastPos[1] - m.floor(playerPos[1]) != 0:
            playerPos[1] = lastCor[1]
            velocity[1] = 0
    
    #Move bullets
    tempBullets = []
    for bullet in bullets:
        pos = [0,0,0]
        pos[0], pos[1], pos[2], vector, state = bullet
        pos[0]+= vector[0] * bulletSpeed * passedTime
        pos[1]+= vector[1] * bulletSpeed * passedTime
        vector[2]-= bulletGravity
        pos[2]+= vector[2] * passedTime
        if pos[2] > 0:
            try:
                if map[m.floor(pos[0])][m.floor(pos[1])] == 0:
                    tempBullets.append((pos[0], pos[1], pos[2], vector, state))
            except:
                pass
    bullets = tempBullets

    #Autoreload magazine
    if magazine <= 0 and autoReload and fireTimer < timeit.default_timer() - firingTime:
        reloadTimer = timeit.default_timer()
        sounds.reload.play()
        magazine = magazineSize
    
    #Fire weapon if it's fully automatic
    if leftIsDown and magazine > 0 and fireTimer < timeit.default_timer() - firingTime and fullyAutomatic and reloadTimer < timeit.default_timer() - reloadTime:
        fireTimer = timeit.default_timer()
        sounds.fire.play()
        magazine-= 1
        vector = [m.sin(playerRot), m.cos(playerRot), 0]
        right = [m.sin(playerRot+m.pi/2), m.cos(playerRot+m.pi/2)]
        bullets.append((playerPos[0]+right[0]*bulletSpawnToSideAmount, playerPos[1]+right[1]*bulletSpawnToSideAmount, playerHeight, vector, False))

    last = timeit.default_timer()

pgzrun.go()