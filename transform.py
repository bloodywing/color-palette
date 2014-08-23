#!/usr/bin/python

# -*- coding: utf-8 -*-

# -y11+a13*x13+a12*x12+a11*x11+b1
# -y12+a23*x13+a22*x12+a21*x11+b2
# -y13+a33*x13+a32*x12+a31*x11+b3
# -y21+a13*x23+a12*x22+a11*x21+b1
# -y22+a23*x23+a22*x22+a21*x21+b2
# -y23+a33*x23+a32*x22+a31*x21+b3
# -y31+a13*x33+a12*x32+a11*x31+b1
# -y32+a23*x33+a22*x32+a21*x31+b2
# -y33+a33*x33+a32*x32+a31*x31+b3
# -y41+a13*x43+a12*x42+a11*x41+b1
# -y42+a23*x43+a22*x42+a21*x41+b2
# -y43+a33*x43+a32*x42+a31*x41+b3

from math import sqrt
import itertools
import numpy as np
from numpy.linalg import solve, det

from colors import *
from spaces import *

def get_A(x):
    return np.array([[x[0][0], x[0][1], x[0][2], 0, 0, 0, 0, 0, 0, 1, 0, 0],
                     [0, 0, 0, x[0][0], x[0][1], x[0][2], 0, 0, 0, 0, 1, 0],
                     [0, 0, 0, 0, 0, 0, x[0][0], x[0][1], x[0][2], 0, 0, 1],
                     [x[1][0], x[1][1], x[1][2], 0, 0, 0, 0, 0, 0, 1, 0, 0],
                     [0, 0, 0, x[1][0], x[1][1], x[1][2], 0, 0, 0, 0, 1, 0],
                     [0, 0, 0, 0, 0, 0, x[1][0], x[1][1], x[1][2], 0, 0, 1],
                     [x[2][0], x[2][1], x[2][2], 0, 0, 0, 0, 0, 0, 1, 0, 0],
                     [0, 0, 0, x[2][0], x[2][1], x[2][2], 0, 0, 0, 0, 1, 0],
                     [0, 0, 0, 0, 0, 0, x[2][0], x[2][1], x[2][2], 0, 0, 1],
                     [x[3][0], x[3][1], x[3][2], 0, 0, 0, 0, 0, 0, 1, 0, 0],
                     [0, 0, 0, x[3][0], x[3][1], x[3][2], 0, 0, 0, 0, 1, 0],
                     [0, 0, 0, 0, 0, 0, x[3][0], x[3][1], x[3][2], 0, 0, 1] ])

def get_B(y):
    return np.array([[y[0][0]], [y[0][1]], [y[0][2]],
                     [y[1][0]], [y[1][1]], [y[1][2]],
                     [y[2][0]], [y[2][1]], [y[2][2]],
                     [y[3][0]], [y[3][1]], [y[3][2]] ])

def color_row(space, color):
    x1,x2,x3 = space.getCoords(color)
    return np.array([x1,x2,x3])

def color_column(space, color):
    x1,x2,x3 = space.getCoords(color)
    return np.array([[x1],[x2],[x3]])

def colors_array(space, *colors):
    return np.array([color_row(space, c) for c in colors])

def find_transform_colors(space, cx1, cx2, cx3, cx4, cy1, cy2, cy3, cy4):
    x = colors_array(space, cx1, cx2, cx3, cx4)
    y = colors_array(space, cy1, cy2, cy3, cy4)
    return find_transform(x,y)

def find_transform(x, y):
    m = solve(get_A(x), get_B(y))
    a = np.array([[m[0][0], m[1][0], m[2][0]],
                  [m[3][0], m[4][0], m[5][0]],
                  [m[6][0], m[7][0], m[8][0]]])
    b = np.array([[m[9][0]], [m[10][0]], [m[11][0]]])
    return (a, b)

def transform_colors(space, a, b, cx):
    x = color_column(space, cx)
    y = a.dot(x) + b
    #print("X: " + str(x))
    #print("Y: " + str(y))
    return space.fromCoords(y[0][0], y[1][0], y[2][0])

def transform(a, b, x):
    #print(type(x))
    return a.dot(x[:,None]) + b

def rhoC(space, color1, color2):
    x1,y1,z1 = space.getCoords(color1)
    x2,y2,z2 = space.getCoords(color2)
    return sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)

def rho(c1, c2):
    x1,y1,z1 = c1[0], c1[1], c1[2]
    x2,y2,z2 = c2[0], c2[1], c2[2]
    return sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)

def get_center(points):
    zero = np.array([0,0,0])
    return sum(points, zero) / float(len(points))

def get_center_color(space, colors):
    zero = np.array([0,0,0])
    points = [space.getCoords(c) for c in colors]
    center = sum(points, zero) / float(len(points))
    c1,c2,c3 = center[0], center[1], center[2]
    return space.fromCoords((c1,c2,c3))

def get_nearest(x, points):
    #print x
    return min(points, key = lambda p: rho(x, p))

def get_nearest_color(space, cx, colors):
    points = [space.getCoords(c) for c in colors]
    cy = get_nearest(space.getCoords(cx), points)
    return space.fromCoords((cy[0], cy[1], cy[2]))

def get_farest(points):
    center = get_center(points)
    #print(str(center))
    srt = sorted(points, key = lambda c: -rho(center, c))
    return srt[:4]

def get_farest_colors(space, colors):
    points = [space.getCoords(c) for c in colors]
    farest = get_farest(points)
    return [space.fromCoords(c) for c in farest]

def match_colors(space, colors1, colors2):
    points1 = [color_row(space, c) for c in colors1]
    points2 = [color_row(space, c) for c in colors2]
    farest1 = get_farest(points1)
    farest2 = get_farest(points2)
    best_d = None
    best_a = None
    best_b = None
    for pts in itertools.permutations(farest1):
        a, b = find_transform(pts, farest2)
        #print("D:\n" + str(det(a)))
        d = abs( det(a) - 1.0 )
        if best_d is None or d < best_d:
            best_d = d
            best_a = a
            best_b = b
    #print("A:\n" + str(best_a))
    #print("B:\n" + str(best_b))
    #print("D:\n" + str(best_d))
    transformed = [transform(best_a, best_b, x) for x in points1]
    matched = [get_nearest(x, points2) for x in transformed]
    return [space.fromCoords(x) for x in matched]

if __name__ == "__main__":

    x1 = Color(0,0,0)
    x2 = Color(0,10,0)
    x3 = Color(0,0,20)
    x4 = Color(20,0,10)
    x5 = Color(10,10,10)
    x6 = Color(0,20,0)
    x7 = Color(0,0,40)
    x8 = Color(40,0,20)

    y1 = Color(0,0,0)
    y2 = Color(0,10,0)
    y3 = Color(0,0,20)
    y4 = Color(20,0,10)
    y5 = Color(10,10,10)
    y6 = Color(0,20,0)
    y7 = Color(0,0,40)
    y8 = Color(40,0,20)

    res = match_colors(RGB, [x1,x2,x3,x4,x5,x6,x7,x8], [y1,y2,y3,y4,y5,y6,y7,y8])
    print([c.getRGB() for c in res])

