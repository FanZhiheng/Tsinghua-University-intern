# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 10:48:17 2019

@author: fanzh
"""

import numpy as np  # 数组相关的库
import matplotlib.pyplot as plt  # 绘图库
x = []
y = []
fly = {'fly':1, 'fly1': 2, 'fly3' : 3, 'fly4' : 4}
land = {'fly': 1, 'fly1': 2}
for key in fly:
    if key in land:
        x.append(land[key])
        y.append(fly[key])

plt.scatter(x, y, alpha=0.6)  # 绘制散点图，透明度为0.6（这样颜色浅一点，比较好看）
plt.legend()
plt.show()
