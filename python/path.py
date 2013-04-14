#!/usr/bin/python
#-*-coding:utf-8-*-
__author__ = 'venkman'


import pprint

'''
A*寻路测试

'''


def main():
    map_list = [[{'x':x,'y':y,'deco':0} for x in range(10)] for y in range(10)]
    decoration = [(4,1),(4,2),(4,3),(4,4),(4,5),(4,6)]
    for point in decoration:
        map_list[point[1]][point[0]]['deco'] = 1

    start_point = (1,3)
    end_point   = (8,5)
    point_list  = []
    closed_list = [start_point]

    tmp_point = start_point

    def calculate_distance(tmp_point):
        #F=G+H
        G = abs(start_point[0]-tmp_point[0]) + abs(start_point[1]-tmp_point[1])
        H = abs(tmp_point[0]-end_point[0]) + abs(tmp_point[1]-end_point[1])
        F = G + H
        #(x,y,F,G,H)
        return (tmp_point[0], tmp_point[1], F, G, H)

    def find_next_points(tmp_point):
        #上下左右
        tmp_point_list = []
        #上
        if tmp_point[1]-1 >= 0:
            tmp = (tmp_point[0], tmp_point[1]-1)
            if tmp not in closed_list and 0 == map_list[tmp[1]][tmp[0]]['deco']:
                tmp_point_list.append(calculate_distance(tmp))
        #下
        if tmp_point[1]+1 <= 9:
            tmp = (tmp_point[0], tmp_point[1]+1)
            if tmp not in closed_list and 0 == map_list[tmp[1]][tmp[0]]['deco']:
                tmp_point_list.append(calculate_distance(tmp))
        #左
        if tmp_point[0]-1 >= 0:
            tmp = (tmp_point[0]-1, tmp_point[1])
            if tmp not in closed_list and 0 == map_list[tmp[1]][tmp[0]]['deco']:
                tmp_point_list.append(calculate_distance(tmp))
        #右
        if tmp_point[0]+1 <= 9:
            tmp = (tmp_point[0]+1, tmp_point[1])
            if tmp not in closed_list and 0 == map_list[tmp[1]][tmp[0]]['deco']:
                tmp_point_list.append(calculate_distance(tmp))

        return tmp_point_list

    end_point_around = find_next_points(end_point)
    found = False
    while not found:
        next_points = find_next_points(tmp_point)
        print "可能：",next_points

        if 0 == len(next_points):
            break;

        min_point = None
        for point in next_points:
            if end_point[0] == point[0] and end_point[1] == point[1]:
                found = True
                break;
            else:
                if min_point is not None:
                    if point[2] <= min_point[2]:
                        if point[3] >= min_point[3]:
                            if (min_point[0], min_point[1]) not in closed_list:
                                closed_list.append((min_point[0], min_point[1]))
                            min_point = point
                        else:
                            closed_list.append((point[0], point[1]))
                    else:
                        closed_list.append((point[0], point[1]))
                else:
                    min_point = point

        print "最小:", min_point

        if min_point:
            point_list.append(min_point)
            tmp_point = min_point
            if (min_point[0], min_point[1]) not in closed_list:
                closed_list.append((min_point[0], min_point[1]))

        #判断是否已经目标周围坐标
        if min_point in end_point_around:
            found = True

        print "途径:", point_list
        print "关闭:", closed_list

        print "==================================="

    pprint.pprint(point_list if found else "Not Found")

if __name__ == '__main__':
    try:
        main()
    except:
        pass