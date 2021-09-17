import cv2
import _pickle as p

def write(path, Object):
    "Writes object to given path."
    with open(path, "wb") as output:
        p.dump(Object, output, -1)

path = input("path to image: ")
outpath = input("output path: ")

img = cv2.imread(path)

ys,xs,_ = img.shape

map = []
for x in range(xs):
    print(str(round((x/(xs-1))*100))+"%", end="\r")
    row = []
    for y in range(ys):
        color = (int(img[y,x,2]), int(img[y,x,1]), int(img[y,x,0]))
        if color != (0,0,0):
            row.append((int(img[y,x,2]), int(img[y,x,1]), int(img[y,x,0])))
        else:
            row.append(0)
    map.append(row)
map.reverse()
write(outpath, map)
print("\nDone")


    