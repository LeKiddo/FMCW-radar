# This file intends to plot data returned by the function readAndParseUart() of oob_parser_py
#written by A.N.SOW, for Halmstad University
# oob_parser is distributed by Texas instrument along with their mmwave indistrual toolbox.
# oob_parser.py can be found in \ti\mmwave_industrial_toolbox_4_7_0\labs\people_counting\visualizer

# readAndParseUart() read the UART ports, then call a function to parse the specific demo output
# This will return 1 frame of data. This must be called for each frame of data that is expected. It will return a dict containing:
#   1. Point Cloud (x,y,z,doppler,snr)
#   2. Target List
#   3. Target Indexes
#   4. number of detected points in point cloud
#   5. number of detected targets
#   6. frame number
#   7. Fail - if one, data is bad
#   8. classifier output
#   9. polar info (range, azimuth, elev (if 3D people counting) , doppler,snr)


import math
import platform
from oob_parser_ori import uartParserSDK
import serial
import time
import tkinter as tk
from tkinter import *
import tkinter.filedialog
import tkinter.ttk as ttk  # combobox
from tkinter.ttk import *
from tkinter import messagebox
import serial.tools.list_ports
import numpy as np
import sys
import xlsxwriter
#from multiprocessing import Value, Array, Process, Queue
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure

import matplotlib;matplotlib.use("TkAgg") #for plotting under IDE along with plt.show()
#import multiprocessing
#from matplotlib.artist import Artist as artplot

class setup():
    def __init__(self):
        self.platform=platform.system()
       # / dev / ttyACM0
        #/ dev / ttyACM1
        self.userPort = "COM -1"
        self.dataPort = "COM -1"
        self.profile = {}
        self.default=-1
        self.root=Tk()
        self.demo_name=""
        self.config_file=""
        self.profile_filename = 'Profile_.xlsx'
        self.plotcountdown=1


    def main_program(self):

        #self.mainProgram_start_time = time.time()
        while (1):

             # ------------------ READING AND PARSE OF DATA  {use of readandParseUART() from oob_parser_ori.py } -------------------------

            self.parsedData=self.parser.readAndParseUart()

            print("\n length of data is ", len(self.parsedData))
            print("Parsed data = ",self.parsedData)
            for i in range(len(self.parsedData)):
                print(f"parsedData[{i}] = ", self.parsedData[i])

            # if ((time.time() - self.mainProgram_start_time) > 60): #TODO plot evolution plot

            #("pcbufping (x,y,z,doppler,snr) ", self.parsedData[0])
            print("length de parsed data [1] aka Targets = ", len(self.parsedData[1]))
            print("length de parsed data [0] aka pcbufping = ", len (self.parsedData[0]))
            for i in range(len(self.parsedData[0])):
                print(f"parsedData[0][{i}] = ", self.parsedData[0][i])

            print("\nx PC= ",self.parsedData[0][0])
            print("\ny PC = ", self.parsedData[0][1])
            print("\nz PC = ", self.parsedData[0][2])
            print("\ndoppler = ",self.parsedData[0][3])
            print("\nsnr = ",self.parsedData[0][4])

            #print("polar_returned ( range,azimuth,elevation,doppler,snr) ", self.parsedData[8])
            print("\nrange = ", self.parsedData[8][0])
            print("\nazimuth = ", self.parsedData[8][1])
            print("\nelevation = ", self.parsedData[8][2])
            #print("\ndoppler = ", self.parsedData[8][3])
            #print("\nsnr = ", self.parsedData[8][4])

            #print("Target List", self.parsedData[1])
            print("Target Indexes", self.parsedData[2])
            print("number of detected points in point cloud", self.parsedData[3])
            print("number of detected targets or people count", self.parsedData[4])
            self.numTargets=self.parsedData[4]
            print("frame number", self.parsedData[5])
            self.framenum=self.parsedData[5]
            print("If 1, data is bad", self.parsedData[6])
            self.dataisBad = self.parsedData[6]
            print("classifier output", self.parsedData[7])

            if (self.demo_name == "3D People Counting" or self.demo_name == "Sense and Detect HVAC Control" ) and self.dataisBad!=1:
                i = 0
                for key, value in self.Targets.items(): #keys may  not ordered?  > for key in ["targetId, "posX"], "posY", "posZ", "velX", "velY", "velZ","accX", "accY", "accZ"]
                #for key in sorted(self.Targets.keys()): #alphabetic sort, not wanted

                    self.Targets[key] = self.parsedData[1][i]
                    i += 1


                print("Position X tab for targets", self.Targets["posX"][0])
                print("Position Y tab for targets", self.Targets["posY"][0])
                print("Position Z tab for targets", self.Targets["posZ"][0])
                print("Velocity X tab for targets", self.Targets["velX"][0])
                print("Velocity Y tab for targets", self.Targets["velY"][0])
                print("Velocity Z tab for targets", self.Targets["velZ"][0])
                print("Acceleration X tab for targets", self.Targets["accX"][0])
                print("Acceleration Y tab for targets", self.Targets["accY"][0])
                print("Acceleration Z tab for targets", self.Targets["accZ"][0])
                print("Targets =", self.Targets)

            if self.dataisBad != 1:

                i = 0
                #for key in self.Point_cloud.keys() - self.ignore_keys_1:
                for key in ["x","y","z","doppler","snr"]:
                    self.Point_cloud[key] = self.parsedData[0][i]
                    i += 1


                i = 0
                for key in self.ranAziElev:
                    self.Point_cloud[key] = self.parsedData[8][i]
                    i += 1

                print("Point cloud= ",self.Point_cloud)

                self.plotcountdown -= 1
                if self.plotcountdown == 0:
                    self.plot_update()
                    self.plotcountdown = 1





    def program(self):
        self.greetings_demo()
        self.parser=uartParserSDK(type=self.demo_name)
        # self.parser.frametime=50 # 50 ms
        self.init_data_structure()
        self.greetings_ComPorts()
        self.Config_profile()
        self.plot_init()
        self.main_program()





    def init_data_structure(self):

        if self.demo_name == "SDK Out of Box Demo":

            # No Gtrack = No target

            self.Point_cloud = {"x": [], "y": [], "z": [], "doppler": [], "snr": [], "range": [], "azimuth": [],
                                "elev": []}

            self.ranAziElev= ["range","azimuth","elev"]

        elif self.demo_name == "3D People Counting":

            self.Targets = {"targetId": [], "posX": [], "posY": [], "posZ": [],
                            "velX": [], "velY": [], "velZ": [],
                            "accX": [], "accY": [], "accZ": []}
            # ec[16] Target Error covarience matrix ; g ; confidenceLevel( Tracker confidence metric) also available

            self.Point_cloud = {"x": [], "y": [], "z": [], "doppler": [], "snr": [], "range": [], "azimuth": [],
                                "elev": []}
            self.ranAziElev = ["range", "azimuth", "elev"]
            #self.ignore_keys_1 =["range","azimuth","elev"]


        elif self.demo_name == "Sense and Detect HVAC Control":
            # Z= posZ = velZ = accZ = 0  for "Sense and Detect HVAC Control"

            self.Targets = {"targetId": [], "posX": [], "posY": [], "posZ": [],
                            "velX": [], "velY": [], "velZ": [],
                            "accX": [], "accY": [], "accZ": []}

            self.Point_cloud = {"x": [], "y": [],"z": [],"doppler": [], "snr": [], "range": [], "azimuth": []}
            self.ranAziElev = ["range", "azimuth"]


    def retrieve(self):
        if (self.Combo.get() == "Pick a Demo"):
            indication = tk.Label(text="Please choose a Demo")
            indication.pack()
            self.root.update_idletasks()
            self.root.update()
        else:
            self.demo_name = str(self.Combo.get())
            print("Choosen demo:", self.demo_name)
            self.root.destroy()

    def onWindow_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
            sys.exit("Program stopped")

    def greetings_demo(self):
        self.root.title("GUI ")
       # self.root.iconbitmap('icon.ico')
        self.root.geometry("200x150")
        frame = Frame(self.root)
        frame.pack()
        list = ["SDK Out of Box Demo", "3D People Counting","Sense and Detect HVAC Control"]

        self.Combo = ttk.Combobox(frame, values=list)
        self.Combo.set("Pick a Demo")
        self.Combo.pack(padx=4, pady=4)
        Button = tk.Button(frame, text="Submit", command=lambda: [f() for f in [self.retrieve]])
        Button.pack(padx=4, pady=4)


        self.root.protocol("WM_DELETE_WINDOW", self.onWindow_closing)
        self.root.mainloop()

    def greetings_ComPorts(self):
        if self.demo_name == "":
            self.root = Tk()
            self.greetings_demo()

        self.root = Tk()
        self.root.title("GUI ")
        #self.root.iconbitmap('icon.ico')
        frame = tk.Frame(self.root)
        frame.pack()
        self.ComPorts_autodetection()

        label = tk.Label(frame,text=f"Com ports are automatically detected for AWR6843. \n User port = {self.userPort} \n Data port = {self.dataPort}\n if default setup is exact, press submit, else change manually \n" )
        label.pack()

        default_com = tk.Button(frame,
                                text="submit",
                                fg="blue",
                                command=lambda: self.Com_Ports_connection(1))
        default_com.pack()

        change = tk.Button(frame,
                           text="change setup",
                           fg='#ff1944',
                           command=lambda: [f() for f in [lambda: self.Com_Ports_connection(0)]])
        change.pack()
        self.root.protocol("WM_DELETE_WINDOW", self.onWindow_closing)
        self.root.mainloop()

    def com_connection(self,userPort, dataPort):
        try:
            self.parser.connectComPorts(userPort, dataPort)
        except Exception as e:
            print(e)
            print('Com port connection failed')

    def ComPorts_autodetection(self):
        ports = serial.tools.list_ports.comports(include_links=False)
        for p in ports:
            if 'Silicon Labs Dual CP2105 USB to UART Bridge: Enhanced COM Port' in p.description:
                self.userPort= p.device
                print("user com port number", self.userPort)
            if 'Silicon Labs Dual CP2105 USB to UART Bridge: Standard COM Port' in p.description:
                self.dataPort = p.device
                print("data com port number", self.dataPort)


    def UserDefined_comPorts(self,user_entry,data_entry):
        self.userPort = 'COM' + user_entry.get()

        self.dataPort = 'COM' + data_entry.get()
        if (user_entry.get() == "" or data_entry.get() == ""):
            label = tk.Label(text="Please provide both com ports")
            label.pack()
            # self.root.mainloop()
            self.root.update_idletasks()
            self.root.update()
        print("user com=", self.userPort, "data com = ", self.dataPort)
        self.root.destroy()
        self.com_connection(self.userPort, self.dataPort)
        self.cfg_file_load()


    def Com_Ports_connection(self,default):

        if (default) :
           self.com_connection(self.userPort,self.dataPort)
           self.root.destroy()
           self.cfg_file_load()
        else:
            self.root.destroy()
            self.root = Tk()
            self.root.title("GUI ")
            #self.root.iconbitmap('icon.ico')
            frame = tk.Frame(self.root)
            frame.pack()
            tk.Label(frame,text="Press ok button when done").pack()
            tk.Label(frame,text="Please provide user com port #").pack()
            user_entry=tk.Entry(frame)
            user_entry.pack()
            tk.Label(frame,text="Please provide user com port # ").pack()
            data_entry=tk.Entry(frame)
            data_entry.pack()

            ok = tk.Button(frame,
                           text="ok",
                           fg="blue",
                           command=lambda: self.UserDefined_comPorts(user_entry,data_entry))

            ok.pack(side=tk.LEFT)
            self.root.mainloop()

    def cfg_file_load(self):
        self.root = Tk()
        self.root.title("GUI ")
        #self.root.iconbitmap('icon.ico')
        # root.overrideredirect(1)
        self.root.withdraw()
        print("Please provide the adequate config file (.cfg)")
        cfgfile_path = tk.filedialog.askopenfilename(title="Please provide the adequate config file (.cfg)")
        print("Selected config file = ", cfgfile_path)
        self.config_file = r"{}".format(cfgfile_path)
        print("config file=",self.config_file)
        self.root.destroy()


    def Config_profile(self):
        counter = 0
        chirpCount = 0
        cfg_file = open(self.config_file, 'r')
        cfg = cfg_file.readlines()
        print(cfg)

        for line in cfg:
            args = line.split()
            if (len(args) > 0):
                if (args[0] == 'channelCfg'):
                    self.antenna_setup = {'Rx1': bin(int(args[1]))[2], 'Rx2': bin(int(args[1]))[3], 'Rx3': bin(int(args[1]))[4],
                                'Rx4': bin(int(args[1]))[5], 'Tx1': bin(int(args[2]))[2], 'Tx2': bin(int(args[2]))[3],
                                'Tx3': bin(int(args[2]))[4]}
                    print("\n Enabled antennas = ", self.antenna_setup, "\n")
                elif (args[0] == 'SceneryParam' or args[0] == 'boundaryBox'):
                    boundaryLine = counter
                    self.profile['leftX'] = float(args[1])
                    self.profile['rightX'] = float(args[2])
                    self.profile['nearY'] = float(args[3])
                    self.profile['farY'] = float(args[4])
                    if self.demo_name == "3D People Counting":
                        self.profile['bottomZ'] = float(args[5])
                        self.profile['topZ'] = float(args[6])
                        self.profile['bottomZ'] = float(-3)
                        self.profile['topZ'] = float(3)
                elif (args[0] == 'staticBoundaryBox'):
                    staticLine = counter
                elif (args[0] == 'profileCfg'):
                    self.profile['startFreq'] = float(args[2])
                    self.profile['idle'] = float(args[3])
                    self.profile['adcStart'] = float(args[4])
                    self.profile['rampEnd'] = float(args[5])
                    self.profile['slope'] = float(args[8])
                    self.profile['samples'] = float(args[10])
                    self.profile['sampleRate'] = float(args[11])
                elif (args[0] == 'frameCfg'):
                    self.profile['numLoops'] = float(args[3])
                    self.profile['numTx'] = float(args[2]) + 1
                elif (args[0] == 'chirpCfg'):
                    chirpCount += 1
                elif (args[0] == 'sensorPosition'):
                    self.profile['sensorHeight'] = float(args[1])
                    self.profile['az_tilt'] = float(args[2])
                    self.profile['elev_tilt'] = float(args[3])
                    self.profile['groudLevelZ'] = 3 - self.profile['sensorHeight']

            counter += 1

        # FURTHER COMPUTATION
        self.profile['maxRange'] = self.profile['sampleRate'] * 1e3 * 0.9 * 3e8 / (2 * self.profile['slope'] * 1e12)


        bw = self.profile['samples'] / (self.profile['sampleRate'] * 1e3) * self.profile['slope'] * 1e12
        self.profile['Range Resolution'] = 3e8 / (2 * bw)

        Tc = (self.profile['idle'] * 1e-6 + self.profile['rampEnd'] * 1e-6) * chirpCount
        lda = 3e8 / (self.profile['startFreq'] * 1e9)

        self.profile['maxVelocity'] = lda / (4 * Tc)

        self.profile['velocityRes'] = lda / (2 * Tc * self.profile['numLoops'] * self.profile['numTx'])
        #writing of the  Configuration Profile in a .csv
        workbook = xlsxwriter.Workbook(self.profile_filename)
        worksheet = workbook.add_worksheet()
        row = 0
        col = 0
        for key, value in self.profile.items():
            worksheet.write(row, col, key)
            worksheet.write(row, col + 1, value)
            row += 1
        workbook.close()

        self.parser.sendCfg(cfg)

    def plot_init(self):
        plt.ion()
        self.min_y = 0
        self.max_y = 10
        self.xlim = 7
        self.zlim = 7


        #Set up plot
        self.figure1= plt.figure(1)
        self.figure2 = plt.figure(2)
        #self.ax1 = self.figure1.add_subplot(111, projection='3d')
        #self.ax1.set_title('3D position')
        #self.ax1.set_xlabel('X Label')
        #self.ax1.set_ylabel('Y Label')
        #self.ax1.set_zlabel('Z Label')

        #self.lines1, = self.ax1.plot([],[],[], 'o')



        if (self.demo_name == "3D People Counting" or self.demo_name == "Sense and Detect HVAC Control"):
            self.ax1 = self.figure1.add_subplot(121, projection='3d')
            self.ax4 = self.figure1.add_subplot(122, projection='3d')
            self.lines1, = self.ax1.plot([], [], [], 'o')
            self.ax4.set_title('3D position for targets')
            self.ax4.set_xlabel('X Label')
            self.ax4.set_ylabel('Y Label')
            self.ax4.set_zlabel('Z Label')

            self.lines4, = self.ax4.plot([], [], [], 'o', c='r')
            self.ax4.set_autoscaley_on(True)
            self.ax4.set_xlim(-(self.xlim/2), (self.xlim/2))
            self.ax4.set_zlim(-self.zlim, self.zlim)
            self.ax4.set_ylim(self.min_y, self.max_y)
            self.ax4.grid()

        else:
            self.ax1 = self.figure1.add_subplot(111, projection='3d')

        self.ax1.set_title('3D position')
        self.ax1.set_xlabel('X Label')
        self.ax1.set_ylabel('Y Label')
        self.ax1.set_zlabel('Z Label')

        self.lines1, = self.ax1.plot([], [], [], 'o')
        # Autoscale on unknown axis and known lims on the other
        self.ax1.set_autoscaley_on(True)
        self.ax1.set_xlim(-self.xlim, self.xlim)
        self.ax1.set_zlim(-self.zlim, self.zlim)
        self.ax1.set_ylim(self.min_y, self.max_y)
        self.ax1.grid()

        # Other stuff

        #self.ax2 = self.figure1.add_subplot(211, projection='polar')
        # self.ax2.set_thetamin(0)
        # self.ax2.set_thetamax(180)
        self.ax2 = self.figure2.add_subplot(121)
        title2 = self.ax2.set_title('FOV')
        self.ax2.set_xlabel('x (m) ')
        self.ax2.set_ylabel('y (l)')
        self.lines2,=self.ax2.plot([], [], 'o')
        self.ax2.grid()
        #self.ax2.set_autoscaley_on(True)
        self.ax2.set_xlim(-self.xlim, self.xlim)
        self.ax2.set_ylim(-self.min_y, self.max_y)

        self.ax3 = self.figure2.add_subplot(122)

        self.ax3.set_title('doppler ')
        self.ax3.set_xlabel('Range (m) )')
        self.ax3.set_ylabel('doppler (m/s)')

        self.lines3,=self.ax3.plot([], [], 'o')
        self.ax3.grid()
        #self.ax3.set_autoscaley_on(True)
        self.ax3.set_xlim(-self.min_y, self.max_y)
        self.ax3.set_ylim(-25, 60)
        plt.tight_layout()


    def plot_update(self):


        self.lines1.set_xdata(self.Point_cloud["x"])
        self.lines1.set_ydata(self.Point_cloud["y"])
        self.lines1.set_3d_properties(self.Point_cloud["z"])
        # Need both of these in order to rescale
        self.ax1.relim()
        self.ax1.autoscale_view()

        if (self.demo_name == "3D People Counting" or self.demo_name == "Sense and Detect HVAC Control"):
            if self.numTargets >= 1 :
                self.lines4.set_xdata(self.Targets["posX"])
                self.lines4.set_ydata(self.Targets["posY"])
                self.lines4.set_3d_properties(self.Targets["posZ"])
                targetnum=0
                for xTarget, yTarget, zTarget in zip(self.Targets["posX"], self.Targets["posY"],self.Targets["posZ"]):
                    text = str(np.round(xTarget,2)) + ', ' + str(np.round(yTarget,2)) + ', ' + str(np.round(zTarget,2))

                    print("ax texts before del= ",self.ax4.texts)
                    if len(self.ax4.texts)>=1 :
                        del self.ax4.texts[0]
                    print("ax texts after del ", self.ax4.texts)

                    txt = self.ax4.text(xTarget, yTarget, zTarget, text, zdir=(0, 0, 0))
                #self.lines4.set_label('x %d, y %d z= %d'%(round(self.Targets["posX"],1),round(self.Targets["posY"],1),round(self.Targets["posZ"],1)))
                # Need both of these in order to rescale
                self.ax4.relim()
                self.ax4.autoscale_view()



        # We need to draw *and* flush

        self.lines2.set_xdata(self.Point_cloud["x"])
        self.lines2.set_ydata(self.Point_cloud["y"])
        #self.ax2.relim()
        #self.ax2.autoscale_view()

        self.lines3.set_xdata(self.Point_cloud["y"])
        self.lines3.set_ydata(self.Point_cloud["doppler"])
        #self.ax3.relim()
        #self.ax3.autoscale_view()
        plt.show()
        #plt.pause(0.001)

        self.figure1.canvas.draw()
        self.figure1.canvas.flush_events()
        #self.figure2.canvas.draw()
        #self.figure2.canvas.flush_events()





# Program--------
if __name__ == '__main__':
    setup=setup()
    setup.program()
