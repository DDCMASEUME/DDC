class SquareTreeNode:
    def __init__(self, level, xmin=None, xmax=None, ymin=None, ymax=None):
        self.xmin, self.xmax, self.ymin, self.ymax = xmin, xmax, ymin, ymax
        self.level = level
        self.disks = []
        self.children = []
        self.table = dict()


    def get_empty_table(self):
        return self.table[tuple([])]


    def intersect(self, node):
        def inval_intersect(inval1, inval2):
            if inval1[0] <= inval2[0] and inval1[1] <= inval2[0]:
                return False
            if inval1[0] >= inval2[1] and inval1[1] >= inval2[1]:
                return False
            return True

        xinval1, xinval2 = [self.xmin, self.xmax], [node.xmin, node.xmax]
        yinval1, yinval2 = [self.ymin, self.ymax], [node.ymin, node.ymax]
        xintersects = inval_intersect(xinval1, xinval2)
        yintersects = inval_intersect(yinval1, yinval2)
        return xintersects and yintersects

    def addchild(self, child):
        self.children.append(child)

    def __str__(self):
        return "\n-----------------------------------------------\n" + \
            "[" + str(self.xmin) + "," + str(self.xmax) + "]"    + \
            "[" + str(self.ymin) + "," + str(self.ymax) + "]" + \
            "  "   +   str(len(self.children)) + " children" + \
            "\n-----------------------------------------------\n"



class SquareTree:

    def __init__(self, square):
        self.root = square
        self.leaves = []

    def __str__(self):
        st_string = ""

        bfsqueue = [self.root]
        while bfsqueue:
            current = bfsqueue.pop(0)
            st_string += current.__str__()
            for c in current.children:
                bfsqueue.append(c)

        return st_string
