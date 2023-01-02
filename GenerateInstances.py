import math
from collections import defaultdict
from random import uniform, choice, randrange
import sys
from numpy import cos, sin

from InputOutput import save


def random_color():
    return "#" + ''.join([choice('0123456789ABCDEF') for j in range(6)])

def random_circle(sizex, sizey):
    cx = uniform(10.0,sizex-10.0)
    cy = uniform(10.0, sizey-10.0)
    spacex = min(cx,sizex-cx)
    spacey = min(cy,sizey-cy)
    r = uniform(sys.float_info.min, min(spacex, spacey))
    return cx, cy, r

#check if circles intersect, touching in a point is allowed
def c_intersect(ax, ay, ar, bx, by, br):
    distance = ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5
    return distance < ar + br

def generate_circles(sizex,sizey, nsets, drawer, clist, colors):
    while len(clist) < nsets:
        cx, cy, r = random_circle(sizex, sizey)
        #generate array containing truth values of possible intersections
        check = [c_intersect(cx, cy, r, lc[0], lc[1], lc[2]) for lc in clist]
        if any(check):
            continue
        clist.append([cx, cy, r])
        print("picking color")
        color = random_color()
        while color in colors: #check if color was allready used
            color = random_color()
        colors.append(color)
        print("creating circle")
        if drawer is not None:
            drawer.create_circle(cx, cy, r, outline=color)

#returns random point lying in circle
def random_point(circle,leftright):
    # create random polar coord. relative to center of circle
    r = uniform(sys.float_info.min, circle[2])
    if leftright == 0:
        theta = uniform(0, math.pi)
    else:
        theta = uniform(math.pi,2*math.pi)
    cart = [r * cos(theta), r * sin(theta)] #convert to cartesian
    return [circle[0] + cart[0], circle[1] + cart[1]] #use as offset

#generate upto maxpoints points lying within circle
def generate_points(circle, maxpoints):
    leftright = randrange(2)
    return [random_point(circle,leftright) for i in range(randrange(
        maxpoints)+1)]

def oneinstance(sizex, sizey, nsets, maxpoints, drawer=None):
    clist = []
    colors = []
    generate_circles(sizex/2, sizey/2, nsets, drawer, clist, colors)
    points = defaultdict(list)
    for i in range(len(clist)):
        points[colors[i]] = generate_points(clist[i], maxpoints)
    if drawer is not None:
        for color in points:
            for pt in points[color]:
                drawer.draw_point(pt[0], pt[1], defaultdict(list), color)
    return points

def ninstances(n, sizex, sizey, nsets, maxpoints, drawer=None):
    for i in range(n):
        name = "instance" + str(i)
        save(name, oneinstance(sizex, sizey, nsets, maxpoints, drawer))

