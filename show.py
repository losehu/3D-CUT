import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, LineString, MultiLineString

def generate_polygons(points_list):
    """
    根据给定的多组点集生成多个多边形
    points_list: 列表，包含多组坐标点，每组坐标点代表一个多边形的顶点。
    返回: 多边形对象列表，每个多边形由shapely.geometry.Polygon表示。
    """
    return [Polygon(points) for points in points_list]

def create_grid_lines(polygons, fill_rate):
    """
    生成网格线填充多边形列表
    polygons: 多边形对象列表。
    fill_rate: 填充率，表示多边形内网格线的密集程度。
    返回: 网格线列表，包含多个shapely.geometry.LineString对象。
    """
    if fill_rate == 1:
        # 如果填充率为1，则不生成网格线，直接返回空列表
        return []
    lines = []
    for polygon in polygons:
        minx, miny, maxx, maxy = polygon.bounds  # 获取多边形的边界
        dx = dy = np.sqrt(1 - fill_rate) * 0.1  # 根据填充率计算网格线间距
        # 生成水平网格线
        for y in np.arange(miny, maxy, dy):
            line = LineString([(minx, y), (maxx, y)])
            intersection = polygon.intersection(line)
            if not intersection.is_empty:
                if isinstance(intersection, LineString):
                    lines.append(intersection)
                elif isinstance(intersection, MultiLineString):
                    lines.extend(intersection.geoms)  # 添加所有交集线段

        # 生成垂直网格线
        for x in np.arange(minx, maxx, dx):
            line = LineString([(x, miny), (x, maxy)])
            intersection = polygon.intersection(line)
            if not intersection.is_empty:
                if isinstance(intersection, LineString):
                    lines.append(intersection)
                elif isinstance(intersection, MultiLineString):
                    lines.extend(intersection.geoms)  # 添加所有交集线段

    return lines

def plot_filled_polygons(polygons, grid_lines, fill_rate):
    """
    绘制多个多边形和网格线
    polygons: 多边形对象列表。
    grid_lines: 网格线列表，每个元素为shapely.geometry.LineString。
    fill_rate: 填充率，用于调整显示效果，虽然在这个函数中未直接使用。
    """
    fig, ax = plt.subplots()
    for polygon in polygons:
        x, y = polygon.exterior.xy  # 获取多边形的外边界坐标
        ax.fill(x, y, alpha=0.5, fc='gray', ec='none')  # 绘制并填充多边形
    for line in grid_lines:
        x, y = line.xy
        ax.plot(x, y, 'blue')  # 绘制网格线
    plt.show()

# 示例数据
def input_point(points_list, fill_rate):
    """
    主函数，用于生成多边形，创建网格线，并绘制结果
    points_list: 多组坐标点列表，用于生成多边形。
    fill_rate: 填充率，控制网格线的密度。
    """
    polygons = generate_polygons(points_list)  # 生成多边形
    grid_lines = create_grid_lines(polygons, fill_rate)  # 生成网格线
    plot_filled_polygons(polygons, grid_lines, fill_rate)  # 绘制多边形和网格线
