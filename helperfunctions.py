from math import sqrt


def dist(A, B):
    return sqrt((A[0]-B[0])**2+(A[1]-B[1])**2)


def disks_intersect(diskA, diskB):
    d = dist(diskA[0:2], diskB[0:2])
    return diskA[2]/2 + diskB[2]/2 > d


def box_intersects_disk(disk, box):
    centerbox_x = (box[1]+box[0])/2
    centerbox_y = (box[3] + box[2]) / 2
    boxheight = box[3]-box[2]
    boxwidth = box[1]-box[0]
    circle_distx = abs(disk[0] - centerbox_x)
    circle_disty = abs(disk[1] - centerbox_y)

    if disk[0] - disk[2]/2 == box[1]:
        return False
    if disk[1] - disk[2]/2 == box[3]:
        return False
    if disk[0] + disk[2]/2 == box[0]:
        return False
    if disk[1] + disk[2]/2 == box[2]:
        return False

    if circle_distx > (boxwidth / 2 + disk[2]/2):
        return False
    if circle_disty > (boxheight / 2 + disk[2]/2):
        return False
    if circle_distx <= boxwidth / 2:
        return True
    if circle_disty <= boxheight / 2:
        return True

    corner_dist = (circle_distx - boxwidth / 2)**2 + (circle_disty -
                                                       boxheight / 2)**2

    return corner_dist <= disk[0] ** 2


def box_contains_disk(disk, box):
    xmin, xmax = disk[0] - disk[2] / 2, disk[0] + disk[2] / 2
    ymin, ymax = disk[1] - disk[2] / 2, disk[1] + disk[2] / 2
    xcontained = box[0] < xmin and xmax <= box[1]
    ycontained = box[2] < ymin and ymax <= box[3]
    return xcontained and ycontained

def compute_active(vh,k,rs):
    if vh % k > rs:
        vh -= (vh % k - rs)
    if vh % k < rs:
        vh -= (vh % k + 1)
        vh -= (k - 1 - rs)
    return vh

def weight_disks(names, alldisks):
    return sum([alldisks[name][2] for name in names])