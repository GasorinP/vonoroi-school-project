from operator import itemgetter
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import  QPainter, QColor, QPen
from PyQt5.QtWidgets import QFileDialog
from UI import Ui_MainWindow
import copy
from algo import VoronoiDiagram,Point

'''
pointset, Sl, Sr, hull_L, hull_R, VD_L, VD_R setting
'''


class MainWindow_controller(QMainWindow):
    def __init__(self):
        super().__init__() # in python3, super(Class, self).xxx = super().xxx
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_control()
        self.point_set = []
        self.edge_set = []
        self.edge_set_tmp = []
        self.filelines = []
        self.algo = VoronoiDiagram()
        self.fpt = 0
        self.save_path = '../../SaveResult/'
        #self.save_path = './SaveResult/'
        '''
        frame setting
        '''
        self.X_offset = 300
        self.Y_offset = 30
        self.frame = QRectF(self.X_offset,self.Y_offset,600,600)
        
        '''
        control setting
        '''
        self.algorun = 0
        self.complete = 0

        '''
        running record
        '''
        self.save_record_path = './running_record.txt'
        self.record_lines = []
        self.record_read_ptr = 0
        self.step_by_step_used = False
        self.record_step = 0 #0,1,2
        '''
        draw graph
        '''
        self.Sl = []
        self.Sr = []
        self.hull = []
        self.hull_L = []
        self.hull_R = []
        self.Vl = []
        self.Vr = []
        self.HP = []


    def setup_control(self):
        self.ui.OpenFile.clicked.connect(self.openfile)
        self.ui.NextGraph.clicked.connect(self.nextgraph)
        self.ui.StepByStep.clicked.connect(self.new_step_by_step)
        self.ui.Run.clicked.connect(self.algo_run)
        self.ui.Clean.clicked.connect(self.cleangraph)
        self.ui.SaveResult.clicked.connect(self.save_result)
        self.ui.LoadResult.clicked.connect(self.load_result)
        self.mousePressEvent = self.mouse_press
    
    def save_result(self):
        f = open(self.save_path + 'result.txt','w')
        tmp = copy.deepcopy(self.point_set)
        tmp = sorted(tmp, key=itemgetter(0,1))
        for i in range(len(tmp)):
            f.write('P ')
            for j in range(len(tmp[i])):
                f.write(str(tmp[i][j]) + ' ')
            f.write('\n')

        tmp = copy.deepcopy(self.edge_set)
        tmp = sorted(tmp, key=itemgetter(0,1,2,3))
        for i in range(len(tmp)):
            f.write('E ')
            for j in range(len(tmp[i])):
                f.write(str(tmp[i][j]) + ' ')
            f.write('\n')
        f.close()
    
    def load_result(self):
        self.cleangraph()
        filename, filetype = QFileDialog.getOpenFileName(self,
                  "Open file",
                  "./")
        #print(filename)
        file = open(filename, 'r',encoding="utf-8")
        lines = file.readlines()
        for i in range(len(lines)):
            line = lines[i].split()
            if line[0] == 'P':
                self.point_set.append([int(line[1]),int(line[2])])
            elif line[0] == 'E':
                self.edge_set.append([int(line[1]),int(line[2]),int(line[3]),int(line[4])])
        self.update()

    def mouse_press(self, event):
        x = event.x()
        y = event.y()
        if x<=self.X_offset or y<=self.Y_offset or x>self.X_offset+600 or y>self.Y_offset+600:
            return
        else:
            self.point_set.append([x-self.X_offset,y-self.Y_offset])
            self.show_pointset()
            self.update()
        

    def algo_run(self):

        if self.step_by_step_used == True:
            self.step_by_step_used = False
            self.cleangraph_without_points()
            self.algo_run_last()
        else:
            self.algo.clean_point_set()
            self.algo.input_data(self.point_set)
            self.edge_set = self.algo.run_algo()
        self.update()

    def algo_run_last(self):
        if self.edge_set_tmp != []:
            self.edge_set = self.edge_set_tmp
            self.edge_set_tmp = []
    
    def step_finish(self):
        self.cleangraph_without_points()
        self.algo_run()
        
    def new_step_by_step(self):
        if self.step_by_step_used == False:
            self.cleangraph_without_points()
            self.algo.clean_point_set()
            self.algo.input_data(self.point_set)
            self.edge_set_tmp = self.algo.run_algo()
            f = open(self.save_record_path, 'r')
            self.record_lines = f.readlines()
            f.close()
            self.step_by_step_used = True
            self.record_read_ptr = 0

        self.decode_record()
        self.update()


    def decode_record(self):
        key = self.record_lines[self.record_read_ptr]
        self.record_read_ptr = self.record_read_ptr + 1
        if key.split()[0] == 'divide_points':
            self.decoder_divide_points()
        elif key.split()[0] == 'sub_hull':
            self.decoder_sub_hull()
        elif key.split()[0] == 'combine_hull':
            self.decoder_combine_hull()
        elif key.split()[0] == 'merge':
            self.decoder_merge()
        elif key.split()[0] == '-stop-':
            print('step by step end')
            self.step_finish()

    def decoder_merge(self):
        self.Vl = []
        self.Vr = []
        self.hull = []
        self.HP = []
        number = self.record_lines[self.record_read_ptr]
        number = number.split()
        len_Vl = int(number[0])
        len_Vr = int(number[1])
        len_HP = int(number[2])
        for i in range(len_Vl):
            self.record_read_ptr = self.record_read_ptr + 1
            point_tmp = self.record_lines[self.record_read_ptr]
            point_tmp = point_tmp.split()
            self.Vl.append([int(point_tmp[0]), int(point_tmp[1]), int(point_tmp[2]), int(point_tmp[3])])
        for i in range(len_Vr):
            self.record_read_ptr = self.record_read_ptr + 1
            point_tmp = self.record_lines[self.record_read_ptr]
            point_tmp = point_tmp.split()
            self.Vr.append([int(point_tmp[0]), int(point_tmp[1]), int(point_tmp[2]), int(point_tmp[3])])
        for i in range(len_HP):
            self.record_read_ptr = self.record_read_ptr + 1
            point_tmp = self.record_lines[self.record_read_ptr]
            point_tmp = point_tmp.split()
            self.HP.append([int(point_tmp[0]), int(point_tmp[1]), int(point_tmp[2]), int(point_tmp[3])])
        self.record_read_ptr = self.record_read_ptr + 1

    def decoder_combine_hull(self):
        self.hull_L = []
        self.hull_R = []
        self.hull = []
        number = self.record_lines[self.record_read_ptr]
        number = number.split()
        len_hull = int(number[0])
        for i in range(len_hull):
            self.record_read_ptr = self.record_read_ptr + 1
            point_tmp = self.record_lines[self.record_read_ptr]
            point_tmp = point_tmp.split()
            self.hull.append([int(point_tmp[0]), int(point_tmp[1]), int(point_tmp[2]), int(point_tmp[3])])
        self.record_read_ptr = self.record_read_ptr + 1

    def decoder_sub_hull(self):
        self.hull_L = []
        self.hull_R = []
        number = self.record_lines[self.record_read_ptr]
        number = number.split()
        len_hull_L = int(number[0])
        len_hull_R = int(number[1])
        for i in range(len_hull_L):
            self.record_read_ptr = self.record_read_ptr + 1
            point_tmp = self.record_lines[self.record_read_ptr]
            point_tmp = point_tmp.split()
            self.hull_L.append([int(point_tmp[0]), int(point_tmp[1]), int(point_tmp[2]), int(point_tmp[3])])
        for i in range(len_hull_R):
            self.record_read_ptr = self.record_read_ptr + 1
            point_tmp = self.record_lines[self.record_read_ptr]
            point_tmp = point_tmp.split()
            self.hull_R.append([int(point_tmp[0]), int(point_tmp[1]), int(point_tmp[2]), int(point_tmp[3])])
        self.record_read_ptr = self.record_read_ptr + 1

    def decoder_divide_points(self):
        self.Sl = []
        self.Sr = []
        self.hull_L = []
        self.hull_R = []
        self.hull = []
        self.Vl = []
        self.Vr = []
        self.HP = []
        number = self.record_lines[self.record_read_ptr]
        number = number.split()
        len_sl = int(number[0])
        len_sr = int(number[1])
        for i in range(len_sl):
            self.record_read_ptr = self.record_read_ptr + 1
            point_tmp = self.record_lines[self.record_read_ptr]
            point_tmp = point_tmp.split()
            self.Sl.append([int(point_tmp[0]), int(point_tmp[1])])
        for i in range(len_sr):
            self.record_read_ptr = self.record_read_ptr + 1
            point_tmp = self.record_lines[self.record_read_ptr]
            point_tmp = point_tmp.split()
            self.Sr.append([int(point_tmp[0]), int(point_tmp[1])])
        self.record_read_ptr = self.record_read_ptr + 1
        
    def cleangraph_without_points(self):
        self.edge_set = []
        self.Sl = []
        self.Sr = []
        self.hull_L = []
        self.hull_R = []
        self.hull = []
        self.Vl = []
        self.Vr = []
        self.HP = []
        self.step_by_step_used = False
        self.update()

    def cleangraph(self):
        self.point_set = []
        self.edge_set = []
        self.Sl = []
        self.Sr = []
        self.hull_L = []
        self.hull_R = []
        self.hull = []
        self.Vl = []
        self.Vr = []
        self.HP = []
        self.ui.pointset.setText('')
        self.step_by_step_used = False
        self.update()

    def drawframe(self, painter):
        painter.fillRect(self.frame,QColor(255,255,255))
        painter.setPen(QColor(0,0,0))
        painter.drawRect(self.frame)

    def drawpointset(self, painter):
        pen = QPen()
        pen.setColor(QColor(0,0,0))
        pen.setWidth(4)
        painter.setPen(pen)
        point_set = self.point_set
        for i in range(len(point_set)):
            painter.drawPoint(point_set[i][0] + self.X_offset, point_set[i][1] + self.Y_offset)

    def draw_edge_set(self, painter):
        edge_set = self.edge_set
        for i in range(len(edge_set)):
            x1 = edge_set[i][0] + self.X_offset
            y1 = edge_set[i][1] + self.Y_offset
            x2 = edge_set[i][2]+ self.X_offset
            y2 = edge_set[i][3] + self.Y_offset
            painter.drawLine(x1,y1,x2,y2)
    
    def drawSlSr(self, painter):
        pen = QPen()
        pen.setWidth(6)
        pen.setColor(QColor(255,0,0))
        painter.setPen(pen)
        ps = self.Sl
        for i in range(len(ps)):
            painter.drawPoint(ps[i][0] + self.X_offset, ps[i][1] + self.Y_offset)

        pen.setColor(QColor(0,0,255))
        painter.setPen(pen)
        ps = self.Sr
        for i in range(len(ps)):
            painter.drawPoint(ps[i][0] + self.X_offset, ps[i][1] + self.Y_offset)

    def drawhull(self, painter):
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(QColor(0,0,0))
        painter.setPen(pen)
        hull = self.hull_L
        for i in range(len(hull)):
            x1 = hull[i][0] + self.X_offset
            y1 = hull[i][1] + self.Y_offset
            x2 = hull[i][2] + self.X_offset
            y2 = hull[i][3] + self.Y_offset
            painter.drawLine(x1, y1, x2, y2)
        hull = self.hull_R
        for i in range(len(hull)):
            x1 = hull[i][0] + self.X_offset
            y1 = hull[i][1] + self.Y_offset
            x2 = hull[i][2] + self.X_offset
            y2 = hull[i][3] + self.Y_offset
            painter.drawLine(x1, y1, x2, y2)
        
        hull = self.hull
        for i in range(len(hull)):
            x1 = hull[i][0] + self.X_offset
            y1 = hull[i][1] + self.Y_offset
            x2 = hull[i][2] + self.X_offset
            y2 = hull[i][3] + self.Y_offset
            painter.drawLine(x1, y1, x2, y2)
        
    def draw_merge(self, painter):
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(QColor(255,0,0))
        painter.setPen(pen)
        vd = self.Vl
        for i in range(len(vd)):
            x1 = vd[i][0] + self.X_offset
            y1 = vd[i][1] + self.Y_offset
            x2 = vd[i][2] + self.X_offset
            y2 = vd[i][3] + self.Y_offset
            painter.drawLine(x1, y1, x2, y2)
        
        pen.setColor(QColor(0,0,255))
        painter.setPen(pen)
        vd = self.Vr
        for i in range(len(vd)):
            x1 = vd[i][0] + self.X_offset
            y1 = vd[i][1] + self.Y_offset
            x2 = vd[i][2] + self.X_offset
            y2 = vd[i][3] + self.Y_offset
            painter.drawLine(x1, y1, x2, y2)
        
        pen.setColor(QColor(0,255,0))
        painter.setPen(pen)
        hp = self.HP
        for i in range(len(hp)):
            x1 = hp[i][0] + self.X_offset
            y1 = hp[i][1] + self.Y_offset
            x2 = hp[i][2] + self.X_offset
            y2 = hp[i][3] + self.Y_offset
            painter.drawLine(x1, y1, x2, y2)
        

    def inframe(self,edge):
        bp0 = Point(0,0)
        bp1 = Point(600,0)
        bp2 = Point(600,600)
        bp3 = Point(0,600)
    
        #假設有一點是無限射線的情況
        if edge.start.infinite == 0 and edge.end.infinite == 1:
            if edge.start.x <= 600 and edge.start.x >= 0 and edge.start.y <= 600 and edge.start.y >= 0:
                x1 = int(edge.start.x)
                y1 = int(edge.start.y)
                #求與邊界的交點
                #右邊界
                p1 = self.getIntersection(edge.start, edge.end, bp1, bp2)
                if p1[0] != None:
                    if (p1[0] - x1) * (edge.end.x - x1) >= 0 and (p1[1] - y1) * (edge.end.y - y1) >= 0 and p1[1] <= 600 and p1[1] >=0:
                        x2 = int(p1[0])
                        y2 = int(p1[1])
                #左邊界
                p2 = self.getIntersection(edge.start, edge.end, bp0, bp3)
                if p2[0] != None:
                    if (p2[0] - x1) * (edge.end.x - x1) >= 0 and (p2[1] - y1) * (edge.end.y - y1) >= 0 and p2[1] <= 600 and p2[1] >=0:
                        x2 = int(p2[0])
                        y2 = int(p2[1])
                #上邊界
                p3 = self.getIntersection(edge.start, edge.end, bp2, bp3)
                if p3[0] != None:
                    if (p3[0] - x1) * (edge.end.x - x1) >= 0 and (p3[1] - y1) * (edge.end.y - y1) >= 0 and p3[0] <= 600 and p3[0] >=0:
                        x2 = int(p3[0])
                        y2 = int(p3[1])
                #下邊界
                p4 = self.getIntersection(edge.start, edge.end, bp0, bp1)
                if p4[0] != None:
                    if (p4[0] - x1) * (edge.end.x - x1) >= 0 and (p4[1] - y1) * (edge.end.y - y1) >= 0 and p4[0] <= 600 and p4[0] >=0:
                        x2 = int(p4[0])
                        y2 = int(p4[1])
            else:
                x1 = None
                x2 = None
                y1 = None
                y2 = None
        else:
            x1 = int(edge.start.x)
            y1 = int(edge.start.y)
            x2 = int(edge.end.x)
            y2 = int(edge.end.y)
        
        return x1,y1,x2,y2
                
    def paintEvent(self, paintEvent):
        painter = QPainter(self)
        painter.begin(self)
        self.drawframe(painter)
        self.drawpointset(painter)
        self.draw_edge_set(painter)
        self.drawSlSr(painter)
        self.drawhull(painter)
        self.draw_merge(painter)
        painter.end()
    
    def openfile(self):
        self.cleangraph()
        filename, filetype = QFileDialog.getOpenFileName(self,
                  "Open file",
                  "./")
        #print(filename)
        file = open(filename, 'r',encoding="utf-8")
        self.filelines = file.readlines()
        self.fpt = 0

        self.process_fileline()
        self.show_pointset()
        file.close()

    def process_fileline(self):
        '''
        return:
            0, end
        '''
        self.point_set = []
        line = self.filelines[self.fpt]
        self.fpt = self.fpt + 1
        while(line[0]=='#' or line[0]=='\n'):
            line = self.filelines[self.fpt]
            self.fpt = self.fpt + 1
        num_point = int(line.split()[0])
        if num_point == 0:
            return 0
        for i in range(num_point):
            line = self.filelines[self.fpt]
            self.fpt = self.fpt + 1
            point = line.split(' ')
            self.point_set.append([int(point[0]),int(point[1])])
        return 1
    
    def show_pointset(self):
        text = ''
        for i in range(len(self.point_set)):
            x = self.point_set[i][0]
            y = self.point_set[i][1]
            text = text + 'x: ' + str(x) + ' y: ' + str(y) + '\n'
        self.ui.pointset.setText(text)

    def nextgraph(self):
        self.cleangraph()
        if self.filelines == []:
            self.ui.pointset.setText("didn't open file")
            return 
        recall = self.process_fileline()
        if recall == 0:
            self.ui.pointset.setText("end")
            self.filelines = []
        else:
            self.show_pointset()

    