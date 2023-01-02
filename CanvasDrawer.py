from collections import defaultdict
from pprint import pprint

from SolveOpt import bisector, intersect_bisectors, dist


class CanvasDrawer:

    def __init__(self, canvas):
        self.canvas = canvas

    def reset(self, points):
        self.canvas.delete("all")
        points = defaultdict(list)

    def draw_point(self, x, y, points, color):
        self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, outline="black", fill=color, width=1)
        points[color].append([x, y])

    def draw_xaxis(self): self.canvas.create_line(0, 0, 1200, 0, width=2)

    def draw_yaxis(self): self.canvas.create_line(0, 0, 0, 800, width=2)

    def draw_convex_hull(self, hull, pointset):
        poly = [pointset[p][i] for p in hull for i in [0, 1]]
        self.canvas.create_polygon(poly, outline='gray', fill="", width=2)

    def draw_bounding_boxes(self, intervals):
        for color in intervals:
            width = intervals[color][1]-intervals[color][0]
            height = intervals[color][3] - intervals[color][2]
            x = intervals[color][0]
            y = intervals[color][1]
            self.canvas.create_rectangle(x, y, x+width, y+height, fill="", outline="black")

    def draw_line_segment(self, s, t): self.canvas.create_line(s[0], s[1], t[0], t[1], width=2)

    def create_circle(self, x, y, r, **kwargs): return self.canvas.create_oval(x - r, y - r, x + r, y + r, **kwargs)

    def create_circle_points(self, u,  v,  w, **kwargs):
        bi1 = bisector(u,v)
        bi2 = bisector(v,w)
        center = intersect_bisectors(u,v,w)
        r = dist(center, u)
        return self.create_circle(center[0],center[1],r)