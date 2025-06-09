import numpy as np
from copy import copy

class Theta:
    def __init__(self,theta,id):
        self.theta = theta
        self.id = id

class Intersection:
    def __init__(self,intersection,id):
        self.intersection = intersection
        self.id = id

class Point:
    def __init__(self,x,y,infinite=0):
        self.x = x
        self.y = y
        self.infinite = infinite

class Edge:
    def __init__(self,start,end,right,left):
        self.start = start
        self.end = end
        self.right= right
        self.left = left
        

class VoronoiDiagram():

    def __init__(self):
        self.point_set = []
        self.state_map = {"didn't have point":0,
                          'only one point':1,
                          'two points':2,
                          'three points on same line':3,
                          'acute angle':4,
                          'obtuse angle':5}
        self.fram_size = 600
        self.running_record = []
        self.save_record_path = './running_record.txt'


    def clean_point_set(self):
        self.point_set = []
    
    def input_data(self,data):
        for i in range(len(data)):
            x = data[i][0]
            y = data[i][1]
            p = Point(x,y)
            self.point_set.append(p)

    def record_to_file(self):
        self.running_record.append('-stop-')
        f = open(self.save_record_path, 'w')
        f.writelines(self.running_record)
        self.running_record = []
        f.close()

    def run_algo(self):
        edge_set = []
        edge_set = self.divide_and_conquer(self.point_set)
        self.record_to_file()
        return self.destructure_edge(edge_set)

    def divide_and_conquer(self,point_set):
        Sl = [] #point set
        Sr = [] #point set
        Vl = [] #edge set
        Vr = [] #edge set
        edge_set = []
        if len(point_set) > 3:
            Sl, Sr = self.separate_right_left_set(point_set)
            Vl = self.divide_and_conquer(Sl)
            Vr = self.divide_and_conquer(Sr)
            self.write_record_points(Sl,Sr)
            edge_set = self.marge(Vl,Vr,Sl,Sr,point_set)
            edge_set = self.normalize_edge(edge_set)
        else:
            edge_set = self.termination_point(point_set)
        return edge_set

    def marge(self,Vl,Vr,Sl,Sr,point_set):
        edge_set = []
        HP = []
        hull_L = self.get_convex_hull(Sl)
        hull_R = self.get_convex_hull(Sr)
        self.write_record_sub_hull(hull_L,hull_R)
        hull = self.get_convex_hull(point_set)
        self.write_record_combine_hull(hull)
        upper,lower = self.find_diff_hull(hull_L,hull_R,hull)
        HP = self.get_hyper_plane(upper,lower,Vl,Vr)
        self.write_record_merge(Vl,Vr,HP)
        Vl,Vr = self.cut_over(Vl,Vr,HP)
        self.write_record_merge(Vl,Vr,HP)
        edge_set = Vl + Vr + HP
        return edge_set

    def normalize_edge(self,edge_set):
        pop_list = []
        for i in range(len(edge_set)):
            edge = copy(edge_set[i])
            #左方
            if edge.start.x < 0 and edge.end.x < 0:
                pop_list.append(edge)
            elif edge.start.x < 0:
                edge_m = self.find_slope(edge.start.x,edge.start.y,edge.end.x,edge.end.y)
                edge_p = edge.start
                intersection = self.find_intersection(Point(0,0),None,edge_p,edge_m)
                intersection.infinite = 1
                edge.start = intersection
            elif edge.end.x < 0:
                edge_m = self.find_slope(edge.start.x,edge.start.y,edge.end.x,edge.end.y)
                edge_p = edge.end
                intersection = self.find_intersection(Point(0,0),None,edge_p,edge_m)
                intersection.infinite = 1
                edge.end = intersection
            #右方
            if edge.start.x > self.fram_size and edge.end.x > self.fram_size:
                pop_list.append(edge)
            elif edge.start.x > self.fram_size:
                edge_m = self.find_slope(edge.start.x,edge.start.y,edge.end.x,edge.end.y)
                edge_p = edge.start
                intersection = self.find_intersection(Point(600,0),None,edge_p,edge_m)
                intersection.infinite = 1
                edge.start = intersection
            elif edge.end.x > self.fram_size:
                edge_m = self.find_slope(edge.start.x,edge.start.y,edge.end.x,edge.end.y)
                edge_p = edge.end
                intersection = self.find_intersection(Point(600,0),None,edge_p,edge_m)
                intersection.infinite = 1
                edge.end = intersection
            #上方
            if edge.start.y > self.fram_size and edge.end.y > self.fram_size:
                pop_list.append(edge)
            elif edge.start.y > self.fram_size:
                edge_m = self.find_slope(edge.start.x,edge.start.y,edge.end.x,edge.end.y)
                edge_p = edge.start
                intersection = self.find_intersection(Point(0,600),0,edge_p,edge_m)
                intersection.infinite = 1
                edge.start = intersection
            elif edge.end.y > self.fram_size:
                edge_m = self.find_slope(edge.start.x,edge.start.y,edge.end.x,edge.end.y)
                edge_p = edge.end
                intersection = self.find_intersection(Point(0,600),0,edge_p,edge_m)
                intersection.infinite = 1
                edge.end = intersection
            #下方
            if edge.start.y < 0 and edge.end.y < 0 :
                pop_list.append(edge)
            elif edge.start.y < 0 :
                edge_m = self.find_slope(edge.start.x,edge.start.y,edge.end.x,edge.end.y)
                edge_p = edge.start
                intersection = self.find_intersection(Point(0,0),0,edge_p,edge_m)
                intersection.infinite = 1
                edge.start = intersection
            elif edge.end.y < 0 :
                edge_m = self.find_slope(edge.start.x,edge.start.y,edge.end.x,edge.end.y)
                edge_p = edge.end
                intersection = self.find_intersection(Point(0,0),0,edge_p,edge_m)
                intersection.infinite = 1
                edge.end = intersection
            edge_set[i] = edge

            if np.float32(edge.start.x) == np.float32(edge.end.x) and np.float32(edge.start.y) == np.float32(edge.end.y):
                pop_list.append(edge)
                
        for i in range(len(pop_list)):
            for j in range(len(edge_set)):
                if edge_set[j].start.x == pop_list[i].start.x and edge_set[j].start.y == pop_list[i].start.y and edge_set[j].end.x == pop_list[i].end.x and edge_set[j].end.y == pop_list[i].end.y:
                    edge_set.pop(j)
                    break

        for i in range(len(edge_set)):
            edge = copy(edge_set[i])
            if edge.start.infinite == 1 and edge.end.infinite == 0:
                tmp = edge.start
                edge.start = edge.end
                edge.end = tmp
            edge_set[i] = edge


        return edge_set



    def cut_over(self,Vl,Vr,HP):
        #刪除Vl在HP右邊的線
        pop_list = []
        for i in range(len(Vl)):
            tmp_edge = copy(Vl[i])
            start_index = self.find_hp_block(tmp_edge.start,HP)
            end_index = self.find_hp_block(tmp_edge.end,HP)
            if self.is_on_hp(tmp_edge.start,HP[start_index]) == 1 and self.is_on_hp(tmp_edge.end,HP[end_index]) == 1:
                pop_list.append(tmp_edge)
            elif self.is_on_hp(tmp_edge.start,HP[start_index]) == 1:
                index = 0
                while index < len(HP):
                    intersection = self.intersection_on_hp(tmp_edge,HP[index])
                    if intersection != None:
                        intersection_index = self.find_hp_block(intersection,HP)  
                        if index == intersection_index and intersection.x <= 600 and intersection.x >= 0 and intersection.y <= 600 and intersection.y >= 0:
                            break
                    index = index + 1
                tmp_edge.start = intersection
                Vl[i] = tmp_edge
            elif self.is_on_hp(tmp_edge.end,HP[end_index]) == 1:
                index = 0
                while index < len(HP):
                    intersection = self.intersection_on_hp(tmp_edge,HP[index])
                    if intersection != None:
                        intersection_index = self.find_hp_block(intersection,HP)  
                        if index == intersection_index and intersection.x <= 600 and intersection.x >= 0 and intersection.y <= 600 and intersection.y >= 0:
                            break
                    index = index + 1
                tmp_edge.end = intersection
                Vl[i] = tmp_edge
        for i in range(len(pop_list)):
            for j in range(len(Vl)):
                if Vl[j].start.x == pop_list[i].start.x and Vl[j].start.y == pop_list[i].start.y and Vl[j].end.x == pop_list[i].end.x and Vl[j].end.y == pop_list[i].end.y:
                    Vl.pop(j)
                    break
            

        #刪除Vr在HP左邊的線
        pop_list = []
        for i in range(len(Vr)):
            tmp_edge = copy(Vr[i])
            start_index = self.find_hp_block(tmp_edge.start,HP)
            end_index = self.find_hp_block(tmp_edge.end,HP)
            if self.is_on_hp(tmp_edge.start,HP[start_index]) == 2 and self.is_on_hp(tmp_edge.end,HP[end_index]) == 2:
                pop_list.append(tmp_edge)
            elif self.is_on_hp(tmp_edge.start,HP[start_index]) == 2:
                index = 0
                while index < len(HP):
                    intersection = self.intersection_on_hp(tmp_edge,HP[index])
                    if intersection != None:
                        intersection_index = self.find_hp_block(intersection,HP)  
                        if index == intersection_index and intersection.x <= 600 and intersection.x >= 0 and intersection.y <= 600 and intersection.y >= 0:
                            break
                    index = index + 1
                tmp_edge.start = intersection
                Vr[i] = tmp_edge
            elif self.is_on_hp(tmp_edge.end,HP[end_index]) == 2:
                index = 0
                while index < len(HP):
                    intersection = self.intersection_on_hp(tmp_edge,HP[index])
                    if intersection != None:
                        intersection_index = self.find_hp_block(intersection,HP)  
                        if index == intersection_index and intersection.x <= 600 and intersection.x >= 0 and intersection.y <= 600 and intersection.y >= 0:
                            break
                    index = index + 1
                tmp_edge.end = intersection
                Vr[i] = tmp_edge
        for i in range(len(pop_list)):
            for j in range(len(Vr)):
                if Vr[j].start.x == pop_list[i].start.x and Vr[j].start.y == pop_list[i].start.y and Vr[j].end.x == pop_list[i].end.x and Vr[j].end.y == pop_list[i].end.y:
                    Vr.pop(j)
                    break

        return Vl,Vr

    def intersection_on_hp(self,edge,hp):
        hp_m = self.find_slope(hp.start.x,hp.start.y,hp.end.x,hp.end.y)
        hp_p = hp.start
        edge_m = self.find_slope(edge.start.x,edge.start.y,edge.end.x,edge.end.y)
        edge_p = edge.start
        intersection = self.find_intersection(hp_p,hp_m,edge_p,edge_m)
        return intersection

    def is_on_hp(self,p,hp):
        m = self.find_slope(hp.start.x,hp.start.y,hp.end.x,hp.end.y)
        intersection = self.find_intersection(hp.start,m,p,0)
        if intersection.x < p.x:
            return 1 #點在hp的右邊
        elif intersection.x > p.x:
            return 2 #點在hp的左邊
        else:
            return 0 #點在hp上

    def find_hp_block(self,p,HP):
        for i in range(len(HP)):
            hp = HP[i]
            if hp.start.y >= hp.end.y:
                upper = hp.start.y
                lower = hp.end.y
            else:
                upper = hp.end.y
                lower = hp.start.y
            if int(p.y) <= upper and int(p.y) > lower:
                return i
        y_max,y_min = self.find_hp_block_min_max(HP)
        if p.y >= y_max:
            return 0
        if p.y <= y_min:
            return -1
        return None

    def find_hp_block_min_max(self,HP):
        y_max = max(HP[0].start.y,HP[0].end.y)
        y_min = min(HP[0].start.y,HP[0].end.y)
        for i in range(1,len(HP)):
            if y_max < max(HP[i].start.y,HP[i].end.y):
                y_max = max(HP[i].start.y,HP[i].end.y)
            if y_min > min(HP[i].start.y,HP[i].end.y):
                y_min = min(HP[i].start.y,HP[i].end.y)
        return y_max, y_min

    def get_hyper_plane(self,upper,lower,Vl,Vr):
        union = Vl + Vr
        HP = []
        SG = upper
        p, right, left, m = self.find_middle_vertical_line(SG.start,SG.end)
        start, end = self.two_point_edge_bound(p,m)
        BS = Edge(start,end,right,left)
        HP.append(BS)
        i = 0
        old_intersection = Point(0,99999999,0)
        while self.is_same_edge(SG,lower) == False and i<50:
            #算交點
            intersection = self.find_first_intersection(p,m,union,old_intersection)
            if intersection != None:
                id = intersection.id
                #找下一個SG
                SG = self.find_next_SG(SG,union[id].right,union[id].left)
                if SG.end == None or SG.start == None:
                    break
                union.pop(id)
                p, right, left, m = self.find_middle_vertical_line(SG.start,SG.end)
                start, end = self.two_point_edge_bound(p,m)
                #剪掉新BS的頭
                if start.y >= end.y:
                    start = copy(intersection.intersection)
                else:
                    end = start
                    start = copy(intersection.intersection)
                BS = Edge(start,end,right,left)
                HP.append(BS)
                #剪掉舊BS的尾
                old_BS = HP[-2]
                if old_BS.start.y <= old_BS.end.y:
                    old_BS.start = old_BS.end
                    old_BS.end = copy(intersection.intersection)
                else:
                    old_BS.end = copy(intersection.intersection)
                HP[-2] = old_BS
                old_intersection = intersection.intersection
            i = i + 1
        return HP


    def find_next_SG(self,SG,p1,p2):
        px = SG.start
        py = SG.end
        new_px = None
        new_py = None
        if p1.x == px.x and p1.y == px.y:
            new_px = copy(py)
        elif p1.x == py.x and p1.y == py.y:
            new_px = copy(px)
        else:
            new_py = copy(p1)
        if p2.x == px.x and p2.y == px.y:
            new_px = copy(py)
        elif p2.x == py.x and p2.y == py.y:
            new_px = copy(px)
        else:
            new_py = copy(p2)
        return Edge(new_px,new_py,None,None)

    def find_first_intersection(self,BS_p,BS_m,union,old_intersection):
        candidate_set = []
        for i in range(len(union)):
            tmp_edge = union[i]
            tmp_p = tmp_edge.start
            tmp_m = self.find_slope(tmp_edge.start.x,tmp_edge.start.y,tmp_edge.end.x,tmp_edge.end.y)
            intersection = self.find_intersection(BS_p,BS_m,tmp_p,tmp_m)
            if self.legal_intersection(intersection,tmp_edge) == True and old_intersection.y >= intersection.y and self.in_edge_range(tmp_edge,intersection) == True:
                candidate_set.append(Intersection(intersection,i))
        candidate_set = sorted(candidate_set, key = lambda c: c.intersection.y,reverse=True)
        if candidate_set != []:
            return candidate_set[0]
        else:
            return None

    def in_edge_range(self,edge,intersection):
        if edge.start.infinite == 0 and edge.end.infinite == 0:
            x1 = edge.start.x
            x2 = edge.end.x
            y1 = edge.start.y
            y2 = edge.end.y
            if x1 < x2:
                tmp = x2
                x2 = x1
                x1 = tmp
            if y1 < y2:
                tmp = y2
                y2 = y1
                y1 = tmp
            if x1 >= intersection.x and x2 <= intersection.x and y2 <= intersection.y and y1 >= intersection.y:
                return True
            else:
                return False
        else:
            return True
        


    
    def legal_intersection(self,p,edge):
        if p == None:
            return False
        if edge.start.infinite == 1 and edge.end.infinite == 1:
            return True
        start = edge.start
        end = edge.end
        v1 = [end.x - start.x, end.y - start.y] #原射線
        v2 = [p.x - start.x, p.y - start.y] #對交點射線
        #算兩射線角度
        inner = v1[0]*v2[0] + v1[1]*v2[1]
        dist_v1 = (v1[0]**2+v1[1]**2)**(1/2)
        dist_v2 = (v2[0]**2+v2[1]**2)**(1/2)
        if inner == 0:
            theta = 0
        else:
            theta = inner / (dist_v1*dist_v2)
        #算相似度
        if theta <= 1.5 and theta > 0.5:
            return True
        else:
            return False

    def find_intersection(self,p1,m1,p2,m2):
        if m1 != m2:
            if m1 == None:
                c2 = p2.y - m2*p2.x
                x = p1.x
                y = m2*x + c2
            elif m2 == None:
                c1 = p1.y - m1*p1.x
                x = p2.x
                y = m1*x + c1
            else:
                c1 = p1.y - m1*p1.x
                c2 = p2.y - m2*p2.x 
                x = (c2 - c1) / (m1 - m2)
                y = m1*x + c1
            return Point(x,y)
        else:
            return None

    def is_same_edge(self,e1,e2):
        if (e1.start.x == e2.start.x and e1.start.y == e2.start.y) and (e1.end.x == e2.end.x and e1.end.y == e2.end.y):
            return True
        elif (e1.start.x == e2.end.x and e1.start.y == e2.end.y) and (e1.end.x == e2.start.x and e1.end.y == e2.start.y):
            return True
        else:
            return False

    def find_diff_hull(self,hull_L,hull_R,hull):
        union = hull_L + hull_R
        bound = []
        upper = None
        lower = None
        #找合併後有但合併前沒有的hull邊
        for i in range(len(hull)):
            target_edge = hull[i]
            if self.in_union(target_edge,union) == False:
                bound.append(copy(target_edge))
        #分出哪條邊是上邊，哪條邊是下邊
        if len(bound) != 2:
            print("error : find_diff_hull")
        else:
            if (bound[0].start.y + bound[0].end.y) >= (bound[1].start.y + bound[1].end.y):
                upper = bound[0]
                lower = bound[1]
            else:
                upper = bound[1]
                lower = bound[0]
        return upper, lower

    def in_union(self,edge,union):
        for i in range(len(union)):
            if (edge.start.x == union[i].start.x and edge.start.y == union[i].start.y) and (edge.end.x == union[i].end.x and edge.end.y == union[i].end.y):
                return True
            elif (edge.start.x == union[i].end.x and edge.start.y == union[i].end.y) and (edge.end.x == union[i].start.x and edge.end.y == union[i].start.y):
                return True
        return False

    def restructure_hull(self,hull):
        new_hull = []
        n = len(hull)
        for i in range(n):
            start = Point(hull[i].x,hull[i].y)
            end = Point(hull[(i+1)%n].x,hull[(i+1)%n].y)
            e = Edge(start,end,None,None)
            new_hull.append(e)
        return new_hull

    def get_convex_hull(self,point_set):
        if len(point_set) < 2:
            return []
        #find minimun point
        mini_ptr = self.get_mini(point_set)
        #find all point theta and sort
        theta_set = self.get_sorted_theta_sequence(point_set,mini_ptr)
        #create stack to save convex hull
        fp = copy(point_set[mini_ptr])
        sp = copy(point_set[theta_set[0].id])
        hull = [fp,sp]
        for i in range(1,len(theta_set)):
            tp = copy(point_set[theta_set[i].id])
            while self.is_turn_left(hull[-2],hull[-1],tp) != True:
                if len(hull)>2:
                    hull.pop()
                else:
                    break
            hull.append(tp)
        return self.restructure_hull(hull)
                
    def is_turn_left(self,p1,p2,p3):
        x1 = p1.x
        y1 = p1.y
        x2 = p2.x
        y2 = p2.y
        x3 = p3.x
        y3 = p3.y
        if (x2-x1)*(y3-y1)-(y2-y1)*(x3-x1) >= 0:
            return True
        else:
            return False

    def get_sorted_theta_sequence(self,point_set,mini_ptr):
        theta_set = []
        mini = point_set[mini_ptr]
        for i in range(len(point_set)):
            if i != mini_ptr:
                x = point_set[i].x
                y = point_set[i].y
                theta = self.get_theta([x-mini.x,y-mini.y])
                theta_set.append(Theta(theta,i))
        return sorted(theta_set, key = lambda t: t.theta)

    def get_mini(self,point_set):
        mini_x = point_set[0].x
        mini_y = point_set[0].y
        mini_ptr = 0
        for i in range(1,len(point_set)):
            if point_set[i].y < mini_y:
                mini_x = point_set[i].x
                mini_y = point_set[i].y
                mini_ptr = i
            elif point_set[i].y == mini_y:
                if point_set[i].x < mini_x:
                    mini_x = point_set[i].x
                    mini_y = point_set[i].y
                    mini_ptr = i
        return mini_ptr
        
    def get_theta(self,vector):
        #和x軸單位向量求theta
        inner = vector[0]*1
        dist_v = (vector[0]**2+vector[1]**2)**(1/2)
        dist_x = 1
        if inner == 0:
            return 3.14/2
        else:
            return np.arccos(inner / (dist_v*dist_x))


    def write_record_points(self,Sl,Sr):
        self.running_record.append('divide_points\n')
        self.running_record.append(str(len(Sl)) + ' ' + str(len(Sr)) + '\n')
        for i in range(len(Sl)):
            self.running_record.append(str(Sl[i].x) + ' ' + str(Sl[i].y) + '\n')
        for i in range(len(Sr)):
            self.running_record.append(str(Sr[i].x) + ' ' + str(Sr[i].y) + '\n')

    def write_record_sub_hull(self,hull_L,hull_R):
        hull_L_edge_set = self.destructure_edge(hull_L)
        hull_R_edge_set = self.destructure_edge(hull_R)
        self.running_record.append('sub_hull\n')
        self.running_record.append(str(len(hull_L_edge_set)) + ' ' + str(len(hull_R_edge_set)) + '\n')
        for i in range(len(hull_L_edge_set)):
            self.running_record.append(str(hull_L_edge_set[i][0]) + ' ' + str(hull_L_edge_set[i][1]) + ' ' + str(hull_L_edge_set[i][2]) + ' ' + str(hull_L_edge_set[i][3])+ '\n')
        for i in range(len(hull_R_edge_set)):
            self.running_record.append(str(hull_R_edge_set[i][0]) + ' ' + str(hull_R_edge_set[i][1]) + ' ' + str(hull_R_edge_set[i][2]) + ' ' + str(hull_R_edge_set[i][3])+ '\n')

    def write_record_combine_hull(self,hull):
        hull_edge_set = self.destructure_edge(hull)
        self.running_record.append('combine_hull\n')
        self.running_record.append(str(len(hull_edge_set)) + '\n')
        for i in range(len(hull_edge_set)):
            self.running_record.append(str(hull_edge_set[i][0]) + ' ' + str(hull_edge_set[i][1]) + ' ' + str(hull_edge_set[i][2]) + ' ' + str(hull_edge_set[i][3])+ '\n')

    def write_record_merge(self,Vl,Vr,HP):
        Vl_edge_set = self.destructure_edge(Vl)
        Vr_edge_set = self.destructure_edge(Vr)
        HP_edge_set = self.destructure_edge(HP)
        self.running_record.append('merge\n')
        self.running_record.append(str(len(Vl_edge_set)) + ' ' + str(len(Vr_edge_set)) + ' ' + str(len(HP_edge_set)) + '\n')
        for i in range(len(Vl_edge_set)):
            self.running_record.append(str(Vl_edge_set[i][0]) + ' ' + str(Vl_edge_set[i][1]) + ' ' + str(Vl_edge_set[i][2]) + ' ' + str(Vl_edge_set[i][3])+ '\n')
        for i in range(len(Vr_edge_set)):
            self.running_record.append(str(Vr_edge_set[i][0]) + ' ' + str(Vr_edge_set[i][1]) + ' ' + str(Vr_edge_set[i][2]) + ' ' + str(Vr_edge_set[i][3])+ '\n')
        for i in range(len(HP_edge_set)):
            self.running_record.append(str(HP_edge_set[i][0]) + ' ' + str(HP_edge_set[i][1]) + ' ' + str(HP_edge_set[i][2]) + ' ' + str(HP_edge_set[i][3])+ '\n')

    def separate_right_left_set(self,point_set):
        Sl = []
        Sr = []
        mean = 0
        for i in range(len(point_set)):
            mean = mean + point_set[i].x
        mean = mean / len(point_set)
        for i in range(len(point_set)):
            if point_set[i].x <= mean:
                Sl.append(point_set[i])
            else:
                Sr.append(point_set[i])
        return Sl, Sr

    def termination_point(self,point_set):
        edge_set = []
        state = self.check_point_case(point_set)
        if state == -1:
            edge_set = []

        if state == self.state_map["didn't have point"]:
            edge_set = []

        elif state == self.state_map['only one point']:
            edge_set = []

        elif state == self.state_map['two points']:
            p, right, left, m = self.find_middle_vertical_line(point_set[0],point_set[1])
            start, end = self.two_point_edge_bound(p,m)
            edge_set.append(Edge(start,end,right,left))

        elif state == self.state_map['three points on same line']:
            p1 = point_set[0]
            p2 = point_set[1]
            p3 = point_set[2]
            out1 = None
            out2 = None
            in1 = None
            if self.check_inside_point(p1,p2,p3):
                out1 = p2
                out2 = p3
                in1 = p1
            elif self.check_inside_point(p2,p1,p3):
                out1 = p1
                out2 = p3
                in1 = p2
            elif self.check_inside_point(p3,p1,p2):
                out1 = p1
                out2 = p2
                in1 = p3
            p, right, left, m = self.find_middle_vertical_line(out1,in1)
            start, end = self.two_point_edge_bound(p,m)
            edge_set.append(Edge(start,end,right,left))
            p, right, left, m = self.find_middle_vertical_line(out2,in1)
            start, end = self.two_point_edge_bound(p,m)
            edge_set.append(Edge(start,end,right,left))

        elif state == self.state_map['acute angle']:
            p1 = point_set[0]
            p2 = point_set[1]
            p3 = point_set[2]
            cx,cy = self.Circum(p1,p2,p3)
            mean = Point((p1.x+p2.x+p3.x)/3,(p1.y+p2.y+p3.y)/3)
            #p1 and p2 edge
            edge_set.append(self.acute_edge(p1,p2,cx,cy,mean))
            #p2 and p3 edge
            edge_set.append(self.acute_edge(p2,p3,cx,cy,mean))
            #p1 and p3 edge
            edge_set.append(self.acute_edge(p1,p3,cx,cy,mean))

        elif state == self.state_map['obtuse angle']:
            p1 = point_set[0]
            p2 = point_set[1]
            p3 = point_set[2]
            cx,cy = self.Circum(p1,p2,p3)
            mean = Point((p1.x+p2.x+p3.x)/3,(p1.y+p2.y+p3.y)/3)
            longest = self.longest_length(p1,p2,p3)
            #p1 and p2 edge
            edge_set.append(self.obtuse_edge(p1,p2,cx,cy,longest==1))
            #p2 and p3 edge
            edge_set.append(self.obtuse_edge(p2,p3,cx,cy,longest==2))
            #p1 and p3 edge
            edge_set.append(self.obtuse_edge(p1,p3,cx,cy,longest==3))

        return edge_set

    def destructure_edge(self,edge_set):
        new_edge_set = []
        if edge_set == []:
            return new_edge_set
        for i in range(len(edge_set)):
            vertex1 = [edge_set[i].start.x,edge_set[i].start.y]
            vertex2 = [edge_set[i].end.x,edge_set[i].end.y]
            if vertex1[0] > vertex2[0]:
                tmp = vertex1
                vertex1 = vertex2
                vertex2 = tmp
            elif vertex1[0] == vertex2[0]:
                if vertex1[1] > vertex2[1]:
                    tmp = vertex1
                    vertex1 = vertex2
                    vertex2 = tmp
            new_edge_set.append([int(vertex1[0]),int(vertex1[1]),int(vertex2[0]),int(vertex2[1])])
        return new_edge_set

    def obtuse_edge(self,p1,p2,cx,cy,longest):
        mid, right, left, m = self.find_middle_vertical_line(p1,p2)
        if longest == True:
            vx = mid.x - cx
            vy = mid.y - cy
            bound = self.triangle_bound(Point(cx-vx,cy-vy),m,cx,cy)
        else:
            bound = self.triangle_bound(mid,m,cx,cy)
        return Edge(Point(cx,cy),bound,right,left)

    def longest_length(self,p1,p2,p3):
        l1 = ((p2.x-p1.x)**2+(p2.y-p1.y)**2)**0.5
        l2 = ((p3.x-p2.x)**2+(p3.y-p2.y)**2)**0.5
        l3 = ((p3.x-p1.x)**2+(p3.y-p1.y)**2)**0.5
        if l1 >= l2 and l1 >= l3:
            return 1
        elif l2 >= l1 and l2 >= l3:
            return 2
        elif l3 >= l1 and l3 >= l2:
            return 3

    def acute_edge(self,p1,p2,cx,cy,mean):
        mid, right, left, m = self.find_middle_vertical_line(p1,p2)
        if mid.x == cx and mid.y == cy:
            vx = mean.x - cx
            vy = mean.y - cy
            bound = self.triangle_bound(Point(cx-vx,cy-vy),m,cx,cy)
        else:
            bound = self.triangle_bound(mid,m,cx,cy)
        return Edge(Point(cx,cy),bound,right,left)

    def triangle_bound(self,mid,m,cx,cy):
        if (mid.x <= 600 and mid.x >= 0 and mid.y <= 600 and mid.y >= 0) == False:
            bound = Point(mid.x,mid.y,1)
        else:
            if cx < mid.x:
                bound = self.right_bound(mid,m)
            elif cx > mid.x:
                bound = self.left_bound(mid,m)
            else:
                if cy < mid.y:
                    bound = Point(cx,600,1)
                elif cy > mid.y:
                    bound = Point(cx,0,1)
        return bound


    def Circum(self,p1,p2,p3):
        ax = p1.x
        ay = p1.y
        bx = p2.x
        by = p2.y
        cx = p3.x
        cy = p3.y
        
        d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
        ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
        uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
        return ux,uy

    def check_inside_point(self,p1,p2,p3):
        if p1.x <= p3.x and p1.x > p2.x:
            return True
        elif p1.y <= p3.y and p1.y > p2.y:
            return True
        else:
            return False
    


    def two_point_edge_bound(self,p,m):
        
        x_max = self.fram_size
        y_max = self.fram_size
        
        if m == None:
            start = Point(p.x,0,1)
            end = Point(p.x,y_max,1)
        elif m == 0:
            start = Point(0,p.y,1)
            end = Point(x_max,p.y,1)
        else:
            #left bound
            start = self.left_bound(p,m)
        
            #right bound
            end = self.right_bound(p,m)

        return start, end

    def left_bound(self,p,m):
        y_max = self.fram_size
        c = p.y - m * p.x
        if 0 <= c and c <= y_max:
            bound = Point(0,c)
        elif c < 0:
            bound = Point(-c/m,0)
        elif c > y_max:
            bound = Point((600-c)/m, 600)
        bound.infinite = 1
        return bound

    def right_bound(self,p,m):
        y_max = self.fram_size
        c = p.y - m * p.x
        if 0 <= m*600 + c and m*600 + c <= y_max:
            bound = Point(600,m*600 + c)
        elif m*600 + c < 0:
            bound = Point(-c/m,0)
        elif m*600 + c > y_max:
            bound = Point((600-c)/m, 600)
        bound.infinite = 1
        return bound
        

    def find_middle_vertical_line(self,p1,p2):
        x1 = p1.x
        y1 = p1.y
        x2 = p2.x
        y2 = p2.y
        middle_x = (x2 + x1) / 2
        middle_y = (y2 + y1) / 2
        right,left = self.get_middle_right_left(p1,p2)
        m = self.find_slope(x1,y1,x2,y2)
        if m == None:
            m = 0
        elif m == 0:
            m = None
        else:
            m = -(1/m)
        return Point(middle_x,middle_y), right, left, m

    def find_slope(self,x1,y1,x2,y2):
        if (y2 - y1) != 0 and (x2 - x1) != 0:
            m =  (y2 - y1) / (x2 - x1)
        elif (y2 - y1) == 0:
            m = 0
        elif (x2 - x1) == 0:
            m = None
        return m

    def get_middle_right_left(self,p1,p2):
        x1 = p1.x
        y1 = p1.y
        x2 = p2.x
        y2 = p2.y
        if x1 < x2:
            right = Point(x2,y2)
            left = Point(x1,y1)
        elif x1 > x2:
            right = Point(x1,y1)
            left = Point(x2,y2)
        else:
            if y1 < y2:
                right = Point(x2,y2)
                left = Point(x1,y1)
            else:
                right = Point(x1,y1)
                left = Point(x2,y2)
        return right,left

    def check_point_case(self,point_set):
        '''
        return:
            0, didn't have point
            1, only one point
            2, two points
            there three case be happened by three points
            3, three points on same line
            4, acute angle
            5, obtuse angle
            
        '''
        acute_angle = 4
        obtuse_angle = 5
        num_point = len(point_set)

        tmpx = 0
        tmpy = 0
        for i in range(num_point):
            tmpx = tmpx + point_set[i].x
            tmpy = tmpy + point_set[i].y
        if int(tmpx/num_point) == point_set[0].x and int(tmpy/num_point) == point_set[0].y:
            return -1

        if num_point == 0:
            return self.state_map["didn't have point"]
        elif num_point == 1:
            return self.state_map['only one point']
        elif num_point == 2:
            return self.state_map['two points']
        elif num_point == 3:
            p1 = point_set[0]
            p2 = point_set[1]
            p3 = point_set[2]
            if self.cosine_similarity(p1,p2,p3) == 1:
                return self.state_map['three points on same line']
            elif self.check_angle(p1,p2,p3) == acute_angle:
                return self.state_map['acute angle']
            elif self.check_angle(p1,p2,p3) == obtuse_angle:
                return self.state_map['obtuse angle']



    def check_angle(self,p1,p2,p3):
        l1 = self.get_length(p1,p2)
        l2 = self.get_length(p1,p3)
        l3 = self.get_length(p2,p3)
        tmp = [l1,l2,l3]
        tmp.sort()
        if tmp[2]**2 > tmp[0]**2 + tmp[1]**2:
            return 5 #obtuse angle
        else:
            return 4 #acute angle

    def get_length(self,p1,p2):
        return ((p2.x - p1.x)**2 + (p2.y - p1.y)**2)**0.5

    def cosine_similarity(self,p1,p2,p3):
        v1 = np.array([p2.x - p1.x, p2.y - p1.y])
        v2 = np.array([p3.x - p1.x, p3.y - p1.y])
        cos_theta = np.inner(v1,v2) / (np.sqrt(np.inner(v1,v1))*np.sqrt(np.inner(v2,v2)))
        return cos_theta
