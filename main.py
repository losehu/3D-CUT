import numpy as np
from stl import mesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import sys
from matplotlib.patches import Rectangle
import os
import glob
from point import circle_dict_make
j=3
def load_mesh(file_path):
    # 从STL文件加载网格模型
    return mesh.Mesh.from_file(file_path)


def delete_png_files(directory):
    # 构建一个匹配所有PNG文件的路径
    png_files = glob.glob(os.path.join(directory, '*.png'))
    # 遍历所有匹配的文件并删除它们
    for file in png_files:
        os.remove(file)


def rotation_matrix_x(theta):
    # 生成绕X轴旋转的旋转矩阵
    c, s = np.cos(theta), np.sin(theta)
    rot = np.array([[1, 0, 0],
                    [0, c, -s],
                    [0, s, c]])
    return rot


def rotate_mesh(mesh, theta):
    # 使用X轴的旋转矩阵旋转网格
    rot = rotation_matrix_x(theta)
    mesh.vectors = np.dot(mesh.vectors.reshape(-1, 3), rot.T).reshape(mesh.vectors.shape)


def get_bounds(mesh):
    # 获取网格在X轴和Z轴的边界
    x_min = np.min(mesh.vectors[:, :, 0])
    x_max = np.max(mesh.vectors[:, :, 0])
    y_min = np.min(mesh.vectors[:, :, 1])
    y_max = np.max(mesh.vectors[:, :, 1])
    z_min = np.min(mesh.vectors[:, :, 2])
    z_max = np.max(mesh.vectors[:, :, 2])
    return x_min, x_max,y_min, y_max, z_min, z_max


def interpolate(p1, p2, z):
    # 在给定的z值处，对点p1和p2进行线性插值
    return p1 + (p2 - p1) * (z - p1[2]) / (p2[2] - p1[2])


def intersect_facet(z, facet):  # 获取与水平面z高度相交的点

    points = []
    for i in range(3):
        for j in range(i + 1, 3):
            if (facet[i, 2] - z) * (facet[j, 2] - z) < 0:
                points.append(interpolate(facet[i], facet[j], z))
    return points

def check_dict(my_dict):
    for key, value in my_dict.items():
        if value[2]==0:
            return key,value
    return None,None


def plot_slices(mesh, x_min, x_max, y_min,y_max,z_min, z_max, num_slices,fill_rate):
    # 在3D和2D视图上绘制网格的切片
    fig = plt.figure()
    delete_png_files('./cut')
    ax = fig.add_subplot(111, projection='3d')
    fig2, ax2 = plt.subplots()

    plt.xlim(x_min, x_max)
    plt.ylim(z_min, z_max)
    colors = plt.cm.nipy_spectral(np.linspace(0, 1, num_slices))
    for idx, z in enumerate(np.linspace(z_min, z_max, num_slices)):  # 遍历每个z轴
        if idx == 0 or idx == num_slices - 1:
            continue
        intersections = []
        for facet in mesh.vectors:
            if np.min(facet[:, 2]) <= z <= np.max(facet[:, 2]):  # z与三角形交
                points = intersect_facet(z, facet)  # 获取交点
                if len(points) == 2:
                    intersections.append(points)

        left_x = sys.maxsize
        right_x = -sys.maxsize
        fig1, ax1 = plt.subplots()
        my_dict = []
        dict_excel=[]
        total_gcode = []

        for segment in intersections:
            point1=round(segment[1][0],j),round( segment[1][1],j)
            point2=round(segment[0][0],j),round( segment[0][1],j)
            my_dict.append([point1[0],point1[1],point2[0],point2[1]])
            my_dict.append([point2[0],point2[1],point1[0],point1[1]])


            # if(my_dict[(round(segment[0][0],j),round( segment[0][1],j))] )
            # my_dict[(round(segment[1][0],j),round( segment[1][1],j))] = [round(segment[0][0],j),round( segment[0][1],j),0]

            ax1.plot([segment[0][0], segment[1][0]], [segment[0][1], segment[1][1]], 'k-')
            ax.plot([segment[0][0], segment[1][0]], [segment[0][1], segment[1][1]], [z, z], color=colors[idx])
            if segment[0][0] < left_x:
                left_x = segment[0][0]
            if segment[1][0] > right_x:
                right_x = segment[1][0]


        # print(my_dict)
        circle_dict_make(my_dict,fill_rate,z,num_slices,x_min, x_max,y_min,y_max)
        rect = Rectangle((left_x, z), right_x - left_x, slice_thickness, color=colors[idx], linewidth=0, fill=True)
        ax2.add_patch(rect)
        ax1.set_title(f'z={z:.2f}')
        ax1.set_aspect('equal')
        output_directory = "./cut"  # 定义保存图片的文件夹
        save_path = os.path.join(output_directory, f"{z:.2f}.png")
        fig1.savefig(save_path)
        plt.close(fig1)  # 关闭图像以节省内存
        # fill_cut(my_dict,0.5)

    # ax.set_title('3D View of Slices')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    # ax2.set_title('2D View on X-Z Plane')
    ax2.set_xlabel('X')
    ax2.set_ylabel('Z')

    save_path = os.path.join(output_directory, f"3D.png")
    fig.savefig(save_path,dpi=960)
    save_path = os.path.join(output_directory, f"2D.png")
    fig2.savefig(save_path,dpi=960)

    plt.show()


# 如果直接运行这个脚本文件，则执行main函数
if __name__ == "__main__":
    with open("output.txt", "w") as file:  # Clear the file at the beginning
        file.write("")  # This will clear the content of the file
    file_path = './零件2.STL'  # STL文件路径
    my_mesh = load_mesh(file_path)
    rotate_mesh(my_mesh, np.pi / 2)
    x_min, x_max,y_min,y_max, z_min, z_max = get_bounds(my_mesh)
    print(x_min- x_max,y_min-y_max, z_min- z_max)
    slice_thickness = 0.25
    fill_rate=0.5
    num_slices = int((z_max - z_min) / slice_thickness) + 1
    print(num_slices)
    plot_slices(my_mesh, x_min, x_max,y_min,y_max, z_min, z_max, num_slices,fill_rate)
