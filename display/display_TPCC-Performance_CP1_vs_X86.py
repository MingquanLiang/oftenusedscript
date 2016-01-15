"""
This is a program to show the different TPCC Value from CP1 and X86.

Please add the following two sentence when error happens
during import matplotlib module
import matplotlib
matplotlib.use('Agg')
"""

import os
import sys
import time
from shutil import copyfile

import wx
from matplotlib.figure import Figure
import matplotlib.font_manager as font_manager
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigureCanvas


__author__ = 'mingquan.liang@powercore.com.cn'
__version__ = "2015/11/15"

#clean the screen after N Dot
EMPTY_NUMBER = 60
#EMPTY_NUMBER = 200

#CYCLE = 500
CYCLE = 1000
#CYCLE = 200
# wxWidgets object ID for the timer
TIMER_ID = wx.NewId()

Y_MIN_VALUE = 0
#Y_MAX_VALUE = 3375000
#Y_STEP_VALUE = 375000
#Y_MAX_VALUE = 400000
#Y_GAP_STEP = 5
Y_MAX_VALUE = 350000
Y_GAP_STEP = 7
Y_STEP_VALUE = Y_MAX_VALUE/ Y_GAP_STEP
X_MIN_VALUE = 0
X_MAX_VALUE = EMPTY_NUMBER
X_STEP_VALUE = 20

# Some global variable for data
current_dir = os.path.dirname(os.path.abspath(__file__))

power8_source_dir = '/mnt/power8'
x86_source_dir = '/mnt/x86'
power8_source_filename = os.path.join(power8_source_dir, 'power8.log')
x86_source_filename = os.path.join(x86_source_dir, 'x86.log')

power8_input_dir = os.path.join(current_dir, 'input_file/power8')
x86_input_dir = os.path.join(current_dir, 'input_file/x86')
power8_input_filename = os.path.join(power8_input_dir, 'power8.log.bak')
x86_input_filename = os.path.join(x86_input_dir, 'x86.log.bak')

for needed_dir in (power8_source_dir, x86_source_dir,
        power8_input_dir, x86_input_dir):
    if not os.path.isdir(needed_dir):
        try:
            print("Create Directory {0} ... ".format(needed_dir))
            os.makedirs(needed_dir)
        except Exception as ex:
            print("Failed To Create Directory {0}".format(needed_dir))
            sys.exit(1)

#(1920, 1080) ==> (1900, 1000)

class PlotFigure(wx.Frame):
    def __init__(self):
        self.screen_size = wx.DisplaySize()
        #print("the screen size is {0}".format(self.screen_size))
        self.screen_dpi = 100
        self.frame_length = int(self.screen_size[0])
        self.frame_width = int(self.screen_size[1])
        self.fig_length = self.frame_length //  self.screen_dpi
        self.fig_width = self.frame_width // self.screen_dpi
        self.frame_length = self.fig_length * self.screen_dpi
        self.frame_width = self.fig_width * self.screen_dpi
        wx.Frame.__init__(self, None, wx.ID_ANY,
                          title='CP1/X86 TPCC Performance Comparison',
                          size=(self.frame_length, self.frame_width)
                          #size=(1900, 1000)
                        )
        # Matplotlib Figure, x/y-size should size_in_Frame/dpi
        #eg: 1800 = 15 * 120, 600 = 5 * 120
        #self.fig = Figure((19, 10), 100)
        self.fig = Figure((self.fig_length, self.fig_width), self.screen_dpi)

        #print(self.frame_length, self.frame_width)
        #print(self.fig_length, self.fig_width)

        self.canvas = FigureCanvas(self, wx.ID_ANY, self.fig)

        self.ax = self.fig.add_subplot(211)
        self.ax.set_ylim([Y_MIN_VALUE, Y_MAX_VALUE])
        self.ax.set_xlim([X_MIN_VALUE, X_MAX_VALUE])

        self.ax.set_autoscale_on(False)

        #self.ax.set_xticks([])
        self.ax.set_xticks(range(0, 61, 10))
        #self.ax.set_xticks(range(X_MIN_VALUE, X_MAX_VALUE + 1, X_STEP_VALUE))
        self.ax.set_yticks(range(Y_MIN_VALUE, Y_MAX_VALUE + 1, Y_STEP_VALUE))

        self.ax.set_xlabel("Time(second)")
        self.ax.set_ylabel("Transactions Per Minute(tpmC)")
        self.ax.grid(True)

        self.power8_current_all_values = [None] * EMPTY_NUMBER
        self.x86_current_all_values = [None] * EMPTY_NUMBER
        self.power8_plot, = self.ax.plot(range(EMPTY_NUMBER),
                #self.power8_current_all_values, label='CP1 Value',
                self.power8_current_all_values, label='CP1 TPC-C',
                #color='red', linestyle = ':', linewidth = 2, marker = 'o'
                color='red', marker = '.'
                )
        self.x86_plot, = self.ax.plot(range(EMPTY_NUMBER),
                #self.x86_current_all_values, label='X86 Value',
                self.x86_current_all_values, label='X86 TPC-C',
                color='green', marker = '.'
                )

        self.ax.legend(loc='upper center', ncol=4,
                prop=font_manager.FontProperties(size=16)
                #prop=font_manager.FontProperties(size=10)
                )

        # for 2nd subplot
        self.average = self.fig.add_subplot(212)
        self.average.set_ylim(0, 6)
        #self.average.set_xlim(Y_MIN_VALUE, Y_MAX_VALUE)
        self.average.set_xlim(Y_MIN_VALUE, 300000)

        #self.average.set_ylabel("yHello world")
        self.average.set_xlabel("Transactions Per Minute(tpmC)")

        self.power8_accumulate_value = 0
        self.x86_accumulate_value = 0
        self.power8_previous_value = 0
        self.x86_previous_value = 0

        self.power8_ave_index = [3]
        self.x86_ave_index = [1]
        self.power8_ave_value = [0]
        self.x86_ave_value = [0]
        self.power8_barh, = self.average.barh(bottom=self.power8_ave_index,
                width=self.power8_ave_value, height=1.0,
                color='red', label='CP1 TPC-C (Average)')
        self.x86_barh, = self.average.barh(bottom=self.x86_ave_index,
                width=self.x86_ave_value, height=1.0,
                color='green', label="X86 TPC-C (Average)")

        self.average.grid(True)
        self.average.legend(loc='upper center', ncol=4,
                prop=font_manager.FontProperties(size=16)
                #prop=font_manager.FontProperties(size=10)
                )
        self.average.set_yticks([])

        self.fig.subplots_adjust(left=0.08, right=0.95, bottom=0.05, top=0.95)

        ##########################################################################################

        # TODO: resize the subplot in figure
        self.ax.set_position([0.08, 0.40, 0.85, 0.55])
        self.average.set_position([0.08, 0.05, 0.85, 0.28])

        self.canvas.draw()
        # save the clean background
        self.background_1st = self.canvas.copy_from_bbox(self.ax.bbox)
        self.background_2nd = self.canvas.copy_from_bbox(self.average.bbox)

        self.global_timer_index = 0
        self.local_timer_index = 0
        self.power8_current_all_values = []
        self.x86_current_all_values = []

        wx.EVT_TIMER(self, TIMER_ID, self.on_timer)

    def on_timer(self, event):
        # restore the clean background, saved at the beginning
        self.canvas.restore_region(self.background_1st)
        self.canvas.restore_region(self.background_2nd)

        #copyfile(power8_source_filename, power8_input_filename)
        #copyfile(x86_source_filename, x86_input_filename)
        #print(time.strftime("%s"))

        self.global_timer_index += 1
        self.local_timer_index += 1

        line_index = self.global_timer_index - 1
        less_number = EMPTY_NUMBER - self.local_timer_index
        needed_number = self.local_timer_index - 1

        # get the value of current index from file
        power8_current_value = self.read_from_file_by_index(
                power8_input_filename, line_index)
        x86_current_value = self.read_from_file_by_index(
                x86_input_filename, line_index)

        # normal return: accumulate the return value directly.
        # abnormal return: accumulate the previous one.
        if power8_current_value:
            self.power8_accumulate_value += power8_current_value
            self.power8_previous_value = power8_current_value
        else:
            # TODO: new add for error character
            power8_current_value = self.power8_previous_value
            self.power8_accumulate_value += self.power8_previous_value
        if x86_current_value:
            self.x86_accumulate_value += x86_current_value
            self.x86_previous_value = x86_current_value
        else:
            # TODO: new add for error character
            x86_current_value = self.x86_previous_value
            self.x86_accumulate_value += self.x86_previous_value
        #print("==> accumulate = {0} and previous = {1} and current ="
        #        "{2}".format(self.power8_accumulate_value,
        #            self.power8_previous_value,
        #            power8_current_value))

        # update the new data into 1st subplot
        self.power8_current_all_values = \
            self.power8_current_all_values[:needed_number] + \
            [power8_current_value] + [None] * less_number
        self.x86_current_all_values = \
            self.x86_current_all_values[:needed_number] + \
            [x86_current_value] + [None] * less_number
        self.power8_plot.set_ydata(self.power8_current_all_values)
        self.x86_plot.set_ydata(self.x86_current_all_values)

        # update the new data into 2nd subplot
        self.power8_ave_value = self.power8_accumulate_value / \
            self.global_timer_index
        self.x86_ave_value = self.x86_accumulate_value / \
            self.global_timer_index
        self.power8_barh.set_width(self.power8_ave_value)
        self.x86_barh.set_width(self.x86_ave_value)

        self.ax.draw_artist(self.power8_plot)
        self.ax.draw_artist(self.x86_plot)
        self.average.draw_artist(self.power8_barh)
        self.average.draw_artist(self.x86_barh)

        # clean the data on screen
        if self.local_timer_index == EMPTY_NUMBER:
            #print("local_timer_index is full")
            self.power8_current_all_values = []
            self.x86_current_all_values = []
            self.local_timer_index = 0

        self.canvas.blit(self.ax.bbox)
        self.canvas.blit(self.average.bbox)

    def read_from_file_by_index(self, filename, line_number):
        try:
            with open(filename, 'r') as file_object:
                all_content = file_object.read().split('\n')[:-1]
                file_length = len(all_content)
        except IOError, e:
            print("Error->[read_from_file_by_index]: CAN NOT find the"
                  "filename:[{0}]".format(filename))
        except Exception as ex:
            print("Error->[read_from_file_by_index]: {0}".format(str(ex)))
        if file_length == 0:
            print("Warning->[read_from_file_by_index]: {0} still no data.".format(filename))
            time.sleep(2)
            return None
        elif file_length <= line_number:
            print("Warning->[read_from_file_by_index]: {0} "\
                  "is not enoughdata.".format(filename))
            time.sleep(2)
            return None
        else:
            try:
                ret = int(all_content[line_number])
            except:
                print("Warning->[read_from_file_by_index]: No.{0} line " \
                      "in {1} is not a digital number".format(
                          line_number, filename))
                return None
            else:
                #print("OK->[read_from_file_by_index]: filename={0}, value={1}".format(os.path.basename(filename), ret))
                return ret

if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = PlotFigure()
    #frame.Maximize()
    frame.Center()
    t = wx.Timer(frame, TIMER_ID)
    t.Start(CYCLE)
    frame.Show()
    app.MainLoop()
