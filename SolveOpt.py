import os
import subprocess
import re
from itertools import combinations, product
from subprocess import PIPE
from pprint import pprint
from HelperFunctions import *

SOLVER = "BARON"

XML_TAGS = defaultdict(list)

XML_TAGS["BARON"] = ["<model>", "</model>", "<data>", "</data>", "<commands>",
                     "</commands>"]
XML_TAGS["scip"] = ["<mod>", "</mod>", "<dat>", "</dat>", "<com>", "</com>"]

INDIVIDUAL = False

def get_diameter(pointsets):
    all_points = flatten_list_dict(pointsets)
    diam = 0
    for (u, v) in combinations(all_points, 2):
        diam = max(dist(u, v), diam)
    return diam

#returns bounding of the minimal size around all points in pointsets plus
#additional size diameter of the area of all points
def get_bounds_s(pointsets,diam):
    xvalues = [p[0] for color in pointsets for p in pointsets[color]]
    yvalues = [p[1] for color in pointsets for p in pointsets[color]]

    xmin, xmax = min(xvalues) - diam, max(xvalues) + diam
    ymin, ymax = min(yvalues) - diam, max(yvalues) + diam
    return xmin, xmax, ymin, ymax, diam

#returns collection of bounding boxes, one for each set in pointsets
def get_bounds_each_s(pointsets):
    bounds = defaultdict(list)
    for color in pointsets:
        #repackage current pointset as dictionary so get_diameter and
        # get_bounds_s can be reused
        pset = defaultdict(list)
        pset[color] = pointsets[color]

        xmin, xmax, ymin, ymax, r = get_bounds_s(pset, get_diameter(pset))
        bounds[color] = [xmin, xmax, ymin, ymax, r]
    return bounds


def write_xml(pointsets,  **kwargs):

    sets = defaultdict(list)
    for k, v in pointsets.items():
        sets["'" + k[:] + "'"] = v
    os.remove("job.xml")
    f = open('job.xml', 'w')
    f.truncate(0)

    f.write("""<document>
                   <category>go</category> 

                   """)
    f.write("<solver>" + SOLVER + "</solver>")
    f.write("""
                   <inputMethod>AMPL</inputMethod> 
                   <email> insert valid email address </email>
                   <client><![CDATA[Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36@31.4.243.121]]></client>
                   <priority><![CDATA[long]]></priority>
                   <email><![CDATA[okpat@tutanota.com]]></email>
               """)
    f.write(XML_TAGS[SOLVER][0])
    f.write("""
                   <![CDATA[
                   set PSETS;        	#indices for point sets
                   set POINTS{PSETS};	#indices for points in each set
                   set XYTUPLE;		#indices for x/y-coord. of points
                   set WITHOUT{PSETS};

                   param pcoord {i in PSETS, POINTS[i], XYTUPLE} ;

                   #start solution
                   param cx_start {s in PSETS} := sum{p in POINTS[s]} pcoord[s,p,'X']/card(POINTS[s]) ;
                   param cy_start {s in PSETS} := sum{p in POINTS[s]} pcoord[s,p,'Y']/card(POINTS[s]) ;
                   param rstart {s in PSETS} :=  
                       max{p in POINTS[s]} (abs(pcoord[s,p,'X'] - cx_start[s]) + abs(pcoord[s,p,'Y'] - cy_start[s])) ;

                   #parameters for bounds on variables    
                   param cx_max {s in PSETS} ;
                   param cx_min {s in PSETS} ;
                   param cy_max {s in PSETS} ;
                   param cy_min {s in PSETS} ;
                   """)
    if INDIVIDUAL is True:
        bounds = kwargs.get('bounds', None)
        for color in sets:
            f.write(""" 
                            #variables for each circle
                            var cx {s in PSETS} := cx_start[s]"""
                    + ">=" + "" + ", <=" + "" + "; \n"
                    + "var cy {s in PSETS} := cy_start[s]"
                    + ">=" + "" + ", <=" + "" + "; \n"
                    + "var r  {s in PSETS} := rstart[s] >= 0, <=" + "" +
                    "; \n")
    else:
        cxmin, cxmax = kwargs.get('cxmin', None), kwargs.get('cxmax', None)
        cymin, cymax = kwargs.get('cymin', None), kwargs.get('cymax', None)
        rmax         = kwargs.get('rmax', None)
        f.write(""" 
                #variables for each circle
                var cx {s in PSETS} := cx_start[s]"""
                + ">=" + str(cxmin) + ", <=" + str(cxmax) + "; \n"
                + "var cy {s in PSETS} := cy_start[s]"
                + ">=" + str(cymin) + ", <=" + str(cymax) + "; \n"
                + "var r  {s in PSETS} := rstart[s] >= 0, <=" + str(rmax) +
                "; \n")
    f.write("""
                #variable measuring overlap
                var z {i in PSETS, j in WITHOUT[i]} :=
                    max( (rstart[i]+rstart[j])^2-((cx_start[i]-cx_start[j])^2+(cy_start[i]-cy_start[j])^2),0) ;
                     minimize Overlap:  (sum {i in PSETS,j in WITHOUT[i]} z[i,j])/2 ;

                subject to Overlap_Metric {i in PSETS,j in WITHOUT[i]}:
                     z[i,j] >= (r[i]+r[j])^2-((cx[i]-cx[j])^2+(cy[i]-cy[j])^2) ;
                subject to OnlyPositiveOverlap {i in PSETS,j in WITHOUT[i]}:
                     z[i,j] >= 0;
                subject to Contains_Points {s in PSETS,p in POINTS[s]}:
                    (pcoord[s,p,'X']-cx[s])^2+(pcoord[s,p,'Y']-cy[s])^2 <= r[s]^2 ; ]]>
                  """)
    f.write(XML_TAGS[SOLVER][1])

    f.write(XML_TAGS[SOLVER][2])
    f.write("""
                <![CDATA[ 
                set PSETS :=
                """)
    for color in sets:
        f.write(color + " ")
    f.write("; \n")
    for color in sets:
        f.write("set WITHOUT[" + color + "] := ")
        for other_color in sets:
            if other_color == color:
                continue
            f.write(other_color + " ")
        f.write(";\n")

    for color in sets:
        f.write("set POINTS[" + color + "] := ")
        for i in range(len(sets[color])):
            f.write(str(i + 1) + " ")
        f.write("; \n")
    f.write("set XYTUPLE := X Y; \n")
    f.write("param pcoord :=			 #def. coordinates of points \n")
    for color in sets:
        f.write("[" + color + ",*,*]:     X  Y := \n")
        for i in range(len(sets[color])):
            f.write(
                str(i + 1) + "  " + str(sets[color][i][0]) + "  " + str(
                    sets[color][i][1]) + "\n")
    f.write(";	\n]]>"+XML_TAGS[SOLVER][3])
    f.write(XML_TAGS[SOLVER][4])
    f.write("""<![CDATA[
                printf "DDCstartvalues";
                display _varname, _var;
                printf "DDCend_startvalues";
                solve;
                printf "DDCsolution";
                display _varname, _var;
                printf "DDCend_solution" ;
                ]]>
                """)
    f.write(XML_TAGS[SOLVER][5])
    f.write("""
                <par><![CDATA[]]></par>
                <comment><![CDATA[]]></comment>
                </document>""")
    f.close()

def extract_string_between(s, start, end):
    res = ''
    for idx in range(s.index(start) + len(start) + 1, s.index(end)):
        res = res + s[idx]

    return res


def get_solution(pointsets, refined, **kwargs):
    print("generating xml")
    if INDIVIDUAL is False:

        diam = get_diameter(pointsets)
        cxmin, cxmax, cymin, cymax, rmax = get_bounds_s(pointsets, diam)


        write_xml(pointsets, cxmin=cxmin, cxmax=cxmax, cymin=cymin,
                  cymax=cymax, rmax=rmax)
    else:
        bounds = get_bounds_each_s(pointsets)
        write_xml(pointsets, bounds=bounds)

    drw = kwargs.get('drawer', None)
    print("calling neos server")
    process = subprocess.Popen(["python", "NeosClient.py", "job.xml"], stdout=PIPE, stderr=PIPE)

    s, stderr = process.communicate()
    s = s.decode()
    print(s)

    start, end = 'DDCstartvalues\n', 'DDCend_startvalues'
    print("STARTVALUES: \n")

    sv = extract_string_between(s, start, end)
    print(sv)

    start, end = 'DDCsolution', 'DDCend_solution'
    sol_values = extract_string_between(s, start, end)
    sol_values = re.split('\s+', sol_values)
    print("split sol")
    print(sol_values)

    process.stdout.close()
    process.stderr.close()
    process.terminate()
    print_solution(sol_values, pointsets, drawer=drw)
    print("process terminated")

def print_solution(sol_values, pointsets, **kwargs):
    drw = kwargs.get('drawer', None)

    ncolors = len(pointsets)

    # extract solution values from NEOS output
    x_centers, y_centers, radii = [], [], []
    for i in range(6, 6 + 3 * ncolors, 3):
        print(re.findall(r"[-+]?(?:\d*\.\d+|\d+)", sol_values[i]))
        f = float(re.findall(r"[-+]?(?:\d*\.\d+|\d+)", sol_values[i])[0])
        x_centers.append(f)
    for i in range(6 + 3 * ncolors, 6 + 6 * ncolors, 3):
        f = float(re.findall(r"[-+]?(?:\d*\.\d+|\d+)", sol_values[i])[0])
        y_centers.append(f)
    for i in range(6 + 6 * ncolors, 6 + 9 * ncolors, 3):
        f = float(re.findall(r"[-+]?(?:\d*\.\d+|\d+)", sol_values[i])[0])
        radii.append(f)

    sol = list(zip(x_centers, y_centers, radii))

    pprint("SOLUTIONS: x y r \n")
    for i in range(len(x_centers)):
        pprint(" ".join([str(sol[i][0]), str(sol[i][1]), str(sol[i][2]), "\n"]))
        if drw is not None:
            drw.create_circle(sol[i][0], sol[i][1], sol[i][2])
            drw.canvas.update()
