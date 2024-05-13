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
    # max_spacing = 1-0.38*2  # Maximum spacing between lines at fill_rate = 0
    # min_spacing = 0.38  # Minimum spacing between lines at fill_rate = 1

    # Calculate dynamic spacing based on fill rate
    # spacing = max_spacing * (1 - fill_rate) + min_spacing * fill_rate
    spacing=0.51*(1/fill_rate)
    for polygon in polygons:
        minx, miny, maxx, maxy = polygon.bounds
        # Generate horizontal grid lines
        for y in np.arange(miny, maxy, spacing):
            line = LineString([(minx, y), (maxx, y)])
            intersection = polygon.intersection(line)
            if not intersection.is_empty:
                if isinstance(intersection, LineString):
                    lines.append(intersection)
                elif isinstance(intersection, MultiLineString):
                    lines.extend(intersection.geoms)

        # Generate vertical grid lines
        for x in np.arange(minx, maxx, spacing):
            line = LineString([(x, miny), (x, maxy)])
            intersection = polygon.intersection(line)
            if not intersection.is_empty:
                if isinstance(intersection, LineString):
                    lines.append(intersection)
                elif isinstance(intersection, MultiLineString):
                    lines.extend(intersection.geoms)

    return lines

def plot_filled_polygons(polygons, grid_lines, fill_rate,x_min, x_max,y_min,y_max):
    """
    绘制多个多边形和网格线
    polygons: 多边形对象列表。
    grid_lines: 网格线列表，每个元素为shapely.geometry.LineString。
    fill_rate: 填充率，用于调整显示效果，虽然在这个函数中未直接使用。
    """
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    # x_limit=x_max-x_min
    # y_limit=y_max-y_min
    # max_limit=max(x_limit,y_limit)
    # plt.xlim(x_min, x_min+max_limit)
    # plt.ylim(y_min, y_min+max_limit)
    for polygon in polygons:
        x, y = polygon.exterior.xy  # 获取多边形的外边界坐标
        if fill_rate!=1:
            ax.fill(x, y, alpha=0.5, fc='white', ec='black', lw=2)  # 绘制并填充多边形
        else :
            ax.fill(x, y, alpha=0.5, fc='blue', ec='black', lw=1)  # 绘制并填充多边形

    for line in grid_lines:
        x, y = line.xy
        ax.plot(x, y, 'blue',lw=1)  # 绘制网格线
    # plt.show()
    # plt.close(fig)
# 示例数据
def input_point(points_list, fill_rate,current_z,layer_thickness,x_min, x_max,y_min,y_max):
    """
    主函数，用于生成多边形，创建网格线，并绘制结果
    points_list: 多组坐标点列表，用于生成多边形。
    fill_rate: 填充率，控制网格线的密度。
    """
    polygons = generate_polygons(points_list)  # 生成多边形
    grid_lines = create_grid_lines(polygons, fill_rate)  # 生成网格线
    plot_filled_polygons(polygons, grid_lines, fill_rate,x_min, x_max,y_min,y_max)  # 绘制多边形和网格线

    layer_gcode = generate_layer_gcode(polygons, grid_lines, layer_thickness, current_z)
    # for line in layer_gcode:
    #     print(line)
    with open("output.txt", "a") as file:  # Open file in append mode
        for line in layer_gcode:
            file.write(line + "\n")  # Write each line to the file
    # print(layer_gcode)


def generate_layer_gcode(polygons, grid_lines, layer_height, z_height):
    """
    Generate G-code for a single layer.
    polygons: List of shapely.geometry.Polygon objects for the layer.
    grid_lines: List of shapely.geometry.LineString objects for infill.
    layer_height: The thickness of the layer in mm.
    z_height: Current height of the Z-axis in mm.
    Returns: List of G-code strings.
    """
    gcode = []
    gcode.append(f"G0 Z{z_height:.3f} ; Move to layer height")  # Move Z-axis to the start of this layer

    # Convert points to G-code commands
    def points_to_gcode(points, movement_type="G1", feedrate=1500):
        return [f"{movement_type} X{point[0]:.3f} Y{point[1]:.3f} F{feedrate}" for point in points]

    # Perimeters
    for polygon in polygons:
        exterior_points = list(polygon.exterior.coords)
        gcode.append("G0 " + points_to_gcode([exterior_points[0]], "G0")[0])  # Move to start point of perimeter
        gcode.extend(points_to_gcode(exterior_points))  # Draw perimeter

    # Infill
    for line in grid_lines:
        line_points = list(line.coords)
        gcode.append("G0 " + points_to_gcode([line_points[0]], "G0")[0])  # Move to start point of infill line
        gcode.extend(points_to_gcode(line_points))  # Draw infill line

    return gcode

# Main function to handle multiple layers
def print_3d_object(layers, points_list, base_layer_height, layer_thickness):
    """
    Generate G-code for multiple layers of a 3D object.
    layers: Number of layers to print.
    points_list: List of point sets for generating polygons (one per layer or shared).
    base_layer_height: Initial height of the first layer in mm.
    layer_thickness: Thickness of each layer in mm.
    """
    total_gcode = []
    current_z = base_layer_height

    for i in range(layers):
        fill_rate = 0.5 + i * 0.05  # Example: increment fill rate for each layer
        polygons = generate_polygons(points_list)
        grid_lines = create_grid_lines(polygons, fill_rate)
        layer_gcode = generate_layer_gcode(polygons, grid_lines, layer_thickness, current_z)
        total_gcode.extend(layer_gcode)
        current_z += layer_thickness  # Increase Z-height for the next layer

    return total_gcode