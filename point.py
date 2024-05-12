from show import input_point


def check_dict(my_dict):
    for key, value in my_dict.items():
        if value[2] == 0:
            return key, value
    return None, None


def divide_point(my_dict): #分离不同图形
    all_num = []  # 新的列表，用于存储每次执行check_dict后的num

    key, value = check_dict(my_dict)
    while key is not None:
        my_dict[key][2] = 1
        next_key = tuple(value[0:2])
        num = []
        num.append(list(key))

        # 确保下一个键存在于字典中
        while next_key in my_dict and my_dict[next_key][2] == 0:
            my_dict[next_key][2] = 1
            num.append(list(next_key))
            next_key = tuple(my_dict[next_key][0:2])
        all_num.append(num)
        key, value = check_dict(my_dict)
    return all_num


def fill_cut(my_dict, fill_rate):
    my_dict1 = {}
    # print(my_dict)
    for key in my_dict:
        value = list(my_dict[key])
        # print(value)
        my_dict1[key] = value + [0]
    # print(divide_point(my_dict1))
    input_point(divide_point(my_dict1), fill_rate)


def find_endpoint(edges, x, y):
    for index, edge in enumerate(edges):
        if edge[0] == x and edge[1] == y:
            return edge[2], edge[3], index

    return None, None, None  # 如果没有找到匹配的边，返回None


def circle_dict_make(edges, fill_rate): #将重复列表变有序字典
    my_dict1 = {}
    while len(edges) > 0:
        first_key1, first_key2, first_value1, first_value2, idx = edges[0][0], edges[0][1], edges[0][2], edges[0][3], 0
        my_dict1[(first_key1, first_key2)] = [first_value1, first_value2]
        if edges[idx + 1][0] == first_value1 and edges[idx + 1][1] == first_value2:
            # print('del ', edges[idx])
            del edges[idx]
            # print('del ', edges[idx])
            del edges[idx]

        else:
            # print('del ', edges[idx])
            del edges[idx]
            # print('del ', edges[idx - 1])
            del edges[idx - 1]
        now_value1, now_value2 = 0.59856, 0.5896
        now_key1, now_key2 = first_value1, first_value2
        while now_value1 != first_key1 or now_value2 != first_key2:

            now_value1, now_value2, idx = find_endpoint(edges, now_key1, now_key2)
            if now_value1 is None:
                break
            my_dict1[(now_key1, now_key2)] = [now_value1, now_value2]

            if idx + 1 < len(edges) and edges[idx + 1][0] == now_value1 and edges[idx + 1][1] == now_value2:
                # print('del ', edges[idx])
                del edges[idx]
                # print('del ', edges[idx])
                del edges[idx]
            else:
                # print('del ', edges[idx])
                del edges[idx]
                # print('del ', edges[idx - 1])
                del edges[idx - 1]
            now_key1, now_key2 = now_value1, now_value2

    fill_cut(my_dict1, fill_rate)


# edge = [[0.0, -0.5, 0.0, -1.0], [0.0, -1.0, 0.0, -0.5], [0.0, 0.0, 0.0, -0.5], [0.0, -0.5, 0.0, 0.0],
#         [1.0, -0.5, 1.0, -1.0], [1.0, -1.0, 1.0, -0.5], [1.0, 0.0, 1.0, -0.5], [1.0, -0.5, 1.0, 0.0],
#         [0.5, -1.0, 1.0, -1.0], [1.0, -1.0, 0.5, -1.0], [0.0, -1.0, 0.5, -1.0], [0.5, -1.0, 0.0, -1.0],
#         [0.5, 0.0, 1.0, 0.0], [1.0, 0.0, 0.5, 0.0], [0.0, 0.0, 0.5, 0.0], [0.5, 0.0, 0.0, 0.0],
#         [2, 2, 2, 3], [2,3, 2, 2],
# [3, 2, 2, 2],[2, 2, 3, 2],
# [3, 2, 2, 3],[2, 3, 3, 2]
#         ]
# circle_dict_make(edge,0.5)