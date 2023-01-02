import sys
from math import ceil, floor, log
from operator import attrgetter
from pprint import pprint
import numpy as np
from itertools import product

import ST
from helperfunctions import disks_intersect, box_intersects_disk, weight_disks, \
    compute_active, box_contains_disk


class Approx:
    def __init__(self, disks):
        self.disks = disks
        self.scale_factor = 1
        self.squaretrees = []

    def scale_disks(self, factor):
        scaled = {}
        for name, disk in self.disks.items():
            scaled[name] = (disk[0], disk[1], disk[2]/factor)
        self.disks = scaled
        self.scale_factor = factor

    # overall best approx solution
    def get_solution(self, eps):
        maxdiam = max([d[2] for d in self.disks.values()])
        self.scale_disks(maxdiam)
        mindiam = min([d[2] for d in self.disks.values()])
        self.k = ceil(3 / eps) + 1
        self.l = floor(log(1 / mindiam, self.k + 1))
        print("k:" + str(self.k))
        print("l:" + str(self.l))

        self.set_disk_hierarchy(self.k, self.l)
        pprint("diskhier: " + str(self.diskhier))
        maxval, maxsol = 0, None
        for r, s in product(range(self.k), range(self.k)):
            print("r:" + str(r))
            print("s:" + str(s))
            partsol, partval = self.get_rssol(r, s)
            print("partsol: ")
            print(partsol)

            if partval > maxval:
                maxval = partval
                maxsol = partsol

        return maxsol, maxval

    # solution for active lines with (r,s)
    def get_rssol(self, r, s):
        self.build_square_trees(r, s)

        sol, val = [], 0
        print("len ST" + str(len(self.squaretrees)))
        for st in self.squaretrees:
            print("st is:")
            print([st.root.xmin, st.root.xmax, st.root.ymin, st.root.ymax])
            self.compute_tables(st.root, r, s)
            roottable = st.root.get_empty_table()
            print("roottable is: " )
            print(roottable)
            rootval = sum([self.disks[name][2] for name in roottable])
            sol += roottable
            val += rootval
        return sol, val

    def check_disjoint(self, diskset):
        for d1, d2 in product(range(len(diskset)), range(len(diskset))):
            if d1 != d2 and disks_intersect(diskset[d1], diskset[d2]):
                return False
        return True

    def compute_tables(self, node, r, s):

        for child in node.children:
            self.compute_tables(child, r, s)

        disks_above = self.get_disks_above(node, node.level)
        print("computing table for: ")
        box = [node.xmin, node.xmax, node.ymin, node.ymax]
        print("on level: " + str(node.level))
        print(box)
        print("disks_above: " + str(disks_above))

        def powerset(set):
            ps = []
            for i in range(1 << len(set)):
                ps.append([set[j] for j in range(len(set)) if (i & (1 << j))])
            return ps

        for I in powerset(disks_above):
            if not self.check_disjoint([self.disks[i] for i in I]):
                continue
            print("selected as I")
            print(I)
            disks_on = self.get_disks_on(node, node.level, I)

            pprint(disks_on)

            tableI = []
            if not disks_on:
                for s in node.children:
                    tableI += s.table[tuple(I)]

                node.table[tuple(I)] = tableI
                print("created table entry1:")
                print(node.table[tuple(I)])
                continue

            table_max = []
            for Iprime in powerset(disks_on):
                if not self.check_disjoint([self.disks[i] for i in Iprime]):
                    continue
                u = I + Iprime  # union of disks in I and Iprime
                table_cand = Iprime
                if(len(node.children) > 0):
                    print("has " + str(len(node.children)) + " children")
                counter = 0
                for s in node.children:
                    print("child " + str(counter))
                    counter += 1
                    box = [s.xmin, s.xmax, s.ymin, s.ymax]
                    u_in_s = []
                    print("box " + str(box))
                    for d in u:
                        if box_intersects_disk(self.disks[d], box):
                            print("intersects box " + str(self.disks[d]))
                            u_in_s.append(d)

                    print("u_in_s")
                    print(u_in_s)
                    print("s.table")
                    print(s.table[tuple(u_in_s)])
                    table_cand += s.table[tuple(u_in_s)]
                    print("table_cand")
                    print(table_cand)

                wcand = weight_disks(table_cand, self.disks)
                wmax = weight_disks(table_max, self.disks)
                if wcand > wmax:
                    table_max = table_cand

            node.table[tuple(I)] = table_max
            print("created table entry2:")
            print(node.table[tuple(I)])

    def set_disk_hierarchy(self, k, l):
        # if there is just one level diskhier. is just one 3D list containing
        # all disks form self.disks in entry 0
        if l == 0:
            self.diskhier = [self.disks]
            return

        keys = list(self.disks.keys())
        diams = [d[2] for d in self.disks.values()]
        bins = [(1 / (k + 1)) ** (i + 1) for i in range(l + 1)]
        binned = np.digitize(diams, bins, right=True)
        self.diskhier = [[] for i in range(l + 1)]
        for i in range(len(binned)):
            idx = binned[i]
            self.diskhier[idx].append(keys[i])


    # returns the distance between gridlines on level j
    def leveldist(self, j, k):
        return (k + 1) ** (-j)

    # returns the distance between active lines on level j
    def agriddist(self, j, k):
        return self.leveldist(j, k) * k

    # returns the relevant square for disk on level j when it is in D(r,s)
    def get_rel_square(self, disk, j, r, s):
        diskleft, diskbottom = disk[0] - disk[2] / 2, disk[1] - disk[2] / 2

        ldist = self.leveldist(j, self.k)  # distance of gridlines on lvl j
        v = floor(diskleft / ldist)  # rightmost gridl. left of disk
        v = compute_active(v, self.k, r)  # rightmost act. gridl. left of v
        h = floor(diskbottom / ldist)  # highest gridl. below disk
        h = compute_active(h, self.k, s)  # highest act. gridl. below h

        xleft, xright = v * ldist, (v + self.k) * ldist
        ybottom, ytop = h * ldist, (h + self.k) * ldist

        # check if found square intersects disk but does not contain it.
        # that means disk is in D\(D(r,s) and found square is not relevant
        if xleft == diskleft or xright < disk[0] + disk[2] / 2:
            return None, None
        if ybottom == diskbottom or ytop < disk[1] + disk[2] / 2:
            return None, None
        return [xleft, xright, ybottom, ytop]

    def build_square_trees(self, r, s):
        # saves relevant squares found so far as 4-tuples from get_rel_square
        # together with the respective SquareTreeNode
        nodes = []

        self.squaretrees = []
        for j in range(len(self.diskhier)):
            for name in self.diskhier[j]:

                rsq = self.get_rel_square(self.disks[name], j, r, s)
                #print("found square " + str(rsq) + " for disk " + str(disk))
                if rsq in [nd[0] for nd in nodes]:  # allready found
                    continue
                if all(e is None for e in rsq):  # not relevant
                    continue

                square = ST.SquareTreeNode(j, rsq[0], rsq[1], rsq[2], rsq[3])

                if all((not nd[1].intersect(square)) for nd in nodes):
                    # no relevant parent, square is new root of a ST
                    #print("making new squaretree")
                    self.squaretrees.append(ST.SquareTree(square))
                else:
                    # find parent on deepest level and add as child
                    #print("adding as child to existing ST")
                    parents = [nd[1] for nd in nodes if nd[1].intersect(square)]
                    deepest = max(parents, key=attrgetter('level'))
                    deepest.addchild(square)
                nodes.append((rsq, square))

    def get_disks_above(self, square, j):
        I = []
        for j in range(j):
            for name in self.diskhier[j]:
                box = [square.xmin, square.xmax, square.ymin, square.ymax]
                if box_intersects_disk(self.disks[name], box):
                    I.append(name)
        return I

    def get_disks_on(self, square, j, I):
        I_ = []

        for name in self.diskhier[j]:
            disk = self.disks[name]
            box = [square.xmin, square.xmax, square.ymin, square.ymax]
            if name in I:
                continue
            if any([disks_intersect(disk, self.disks[i]) for i in I]):
                continue
            if box_contains_disk(disk, box):
                I_.append(name)
        return I_


if __name__ == '__main__':
    # in format (cx,cy,diam)
    disks = {"E": [3.125, 3.125, 0.25],
             "G": [3.375, 3.125, 0.25],
             "H": [3.625, 3.125, 0.25],
             "F": [3.875, 3.125, 0.25],
             "I": [3.125, 3.375, 0.25],
             "L": [3.375, 3.375, 0.25],
             "O": [3.625, 3.375, 0.25],
             "R": [3.875, 3.375, 0.25],
             "J": [3.125, 3.625, 0.25],
             "M": [3.375, 3.625, 0.25],
             "Q": [3.625, 3.625, 0.25],
             "S": [3.875, 3.625, 0.25],
             "K": [3.125, 3.875, 0.25],
             "N": [3.375, 3.875, 0.25],
             "P": [3.625, 3.875, 0.25],
             "T": [3.875, 3.875, 0.25],
             "B": [3.25, 3.25, 0.5],
             "U": [3.75, 3.25, 0.5],
             "C": [3.25, 3.75, 0.5],
             "D": [3.75, 3.75, 0.5],
             "A": [3.5, 3.5, 1.0]
    }
    """
    the more simple instance
    disks = [[3.5, 3.5, 1.0],
             [3.5, 3.25, 0.5],
             [3.25, 3.75, 0.5],
             [3.75, 3.75, 0.5],
             [3.125, 3.125, 0.25],
             [3.875, 3.125, 0.25]]
    """

    approx = Approx(disks)

    sol, val = approx.get_solution(1.5)
    print("solution")
    pprint(sol)
    pprint(val)

    """
    for st in approx.squaretrees:
        sq = st.root
        print("disks smaller j")
        I = approx.get_disj_smallerj(sq,1)
        pprint(I)
        print("disks on j")
        pprint(approx.get_disj_onj(sq, 1, I))
    """