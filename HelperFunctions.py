from collections import defaultdict

import numpy
import numpy as np
from scipy.spatial import ConvexHull
from math import sqrt


def flatten_list_dict(dict):
    l = []
    for e in dict:
        for le in dict[e]:
            l.append(le)
    return l

def intersect_bisectors(u,v,l):
    a, b, c = bisector(u, v)
    d, e, f = bisector(u, l)
    return intersect_lines(a, b, c, d, e, f)

def bisector(u, v):
    c = (u[0] ** 2 - v[0] ** 2 + u[1] ** 2 - v[1] ** 2) / 2.0
    return u[0] - v[0], u[1] - v[1], c

# return intersection point of two lines ax+by=c and dx+ey=f
def intersect_lines(a, b, c, d, e, f):
    return (c * e - b * f) / (a * e - b * d), (a * f - c * d) / (a * e - b * d)

def compute_convex_hulls(pointsets):
    convexhulls = defaultdict(list)
    for color in pointsets:
        if len(pointsets[color]) > 2:
            convexhulls[color] = ConvexHull(pointsets[color]).vertices
        if len(pointsets[color]) == 2:
            convexhulls[color] = [0, 1]
        if len(pointsets[color]) == 1:
            convexhulls[color] = [0]
    return convexhulls

def display_convex_hulls(hulls, pointsets, drawer):
    for color in pointsets:
        drawer.draw_convex_hull(hulls[color], pointsets[color])

def orientation_point_line(x,y, ax, ay, bx, by):
    return numpy.sign((x-ax)*(by-ay)-(y-ay)*(bx-ax))

def dist(pa, pb):
    return sqrt((pb[0] - pa[0]) ** 2 + (pb[1] - pa[1]) ** 2)

def get_coords(point, pointsets, color):
    return pointsets[color][point][0], pointsets[color][point][1]

def midpoint(p1,p2):
    return (p1[0]+p2[0])/2, (p1[1]+p2[1])/2

def betweenpoint(p1,p2,factor):
    print((p1[0]+p2[0])/factor, (p1[1]+p2[1])/factor)
    return (p1[0]+p2[0])/factor, (p1[1]+p2[1])/factor

#computes center of circle through three points
def comp_circle(x1, y1, x2, y2, x3, y3):
    a = (x2 - x3) ** 2 + (y2 - y3) ** 2
    b = (x3 - x1) ** 2 + (y3 - y1) ** 2
    c = (x1 - x2) ** 2 + (y1 - y2) ** 2
    s = 2 * (a * b + b * c + c * a) - (a * a + b * b + c * c)
    x = (a * (b + c - a) * x1 + b * (c + a - b) * x2 + c * (a + b - c) * x3) / s
    y = (a * (b + c - a) * y1 + b * (c + a - b) * y2 + c * (a + b - c) * y3) / s
    return x, y, dist([x, y], [x1, y1])


