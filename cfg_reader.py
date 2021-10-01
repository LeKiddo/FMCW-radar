#Reads a .cfg file and outputs an Excel file with a recap 
#code based on TI GUI_main.py code for their people counting demo application


import xlsxwriter
import tkinter as tk
from tkinter import *
import tkinter.filedialog


def cfg_file_load():
    root = Tk()
    root.title("GUI ")
    root.iconbitmap('icon.ico')
    # root.overrideredirect(1)
    root.withdraw()
    print("Please provide the adequate config file (.cfg)")
    cfgfile_path = tk.filedialog.askopenfilename(title="Please provide the adequate config file (.cfg)")
    print("Selected config file = ", cfgfile_path)
    config_file = r"{}".format(cfgfile_path)
    print("config file=", config_file)
    root.destroy()
    return config_file

def config_profile(config_file):
    counter = 0
    chirpCount = 0
    cfg_file = open(config_file, 'r')
    cfg = cfg_file.readlines()
    print(cfg)
    profile = {}
    C = 300000000 #speed of light

    for line in cfg:
        args = line.split()
        if (len(args) > 0):
            if (args[0] == 'channelCfg'):
                antenna_setup = {'Rx1': bin(int(args[1]))[2], 'Rx2': bin(int(args[1]))[3],
                                      'Rx3': bin(int(args[1]))[4],
                                      'Rx4': bin(int(args[1]))[5], 'Tx1': bin(int(args[2]))[2],
                                      'Tx2': bin(int(args[2]))[3],
                                      'Tx3': bin(int(args[2]))[4]}
                print("\n Enabled antennas = ", antenna_setup, "\n")
            elif (args[0] == 'SceneryParam' or args[0] == 'boundaryBox'):
                boundaryLine = counter
                profile['leftX'] = float(args[1])
                profile['rightX'] = float(args[2])
                profile['nearY'] = float(args[3])
                profile['farY'] = float(args[4])
                #no z for sense and direct
                #profile['bottomZ'] = float(args[5])
                #profile['topZ'] = float(args[6])
                #profile['bottomZ'] = float(-3)
                #profile['topZ'] = float(3)
            elif (args[0] == 'staticBoundaryBox'):
                staticLine = counter
            elif (args[0] == 'profileCfg'):
                profile['startFreq'] = float(args[2])
                profile['idle'] = float(args[3])
                profile['adcStart'] = float(args[4])
                profile['rampEnd'] = float(args[5])
                profile['slope'] = float(args[8])
                profile['samples'] = float(args[10])
                profile['sampleRate'] = float(args[11])
            elif (args[0] == 'frameCfg'):
                profile['numLoops'] = float(args[3])
                profile['numTx'] = float(args[2]) + 1
            elif (args[0] == 'chirpCfg'):
                chirpCount += 1
            elif (args[0] == 'sensorPosition'):
                profile['sensorHeight'] = float(args[1])
                profile['az_tilt'] = float(args[2])
                profile['elev_tilt'] = float(args[3])
                profile['groudLevelZ'] = 3 - profile['sensorHeight']

        counter += 1

    # FURTHER COMPUTATION
    profile['maxRange'] = profile['sampleRate'] * 1e3 * 0.9 * 3e8 / (2 * profile['slope'] * 1e12)

    bw = profile['samples'] / (profile['sampleRate'] * 1e3) * profile['slope'] * 1e12
    profile['Range Resolution'] = 3e8 / (2 * bw)

    Tc = (profile['idle'] * 1e-6 + profile['rampEnd'] * 1e-6) * chirpCount
    lda = 3e8 / (profile['startFreq'] * 1e9)

    profile['maxVelocity'] = lda / (4 * Tc)

    profile['velocityRes'] = lda / (2 * Tc * profile['numLoops'] * profile['numTx'])
    #user defined
    profile['Bandwidth_Light'] = C / (2*profile['Range Resolution'])
    profile['Bandwidth_slope_Ghz']= profile['slope']* (profile['samples']/profile['sampleRate'])
    profile['Bandwidth'] = bw
    profile["TotalchirpTIme_Tc"] = Tc
    #user defined

    path=r"C:\ti\mmwave_industrial_toolbox_4_7_0\labs\people_counting\visualizer\out_of_box\Cfg_files"
    xlsx_name = path + '\profile_'+config_file[len(config_file)-9:len(config_file)-4]+'.xlsx'
    print("xls name = ",xlsx_name )
    # writing of the  Configuration Profile in a .csv
    #workbook = xlsxwriter.Workbook("profile_resume2.xlsx")
    workbook = xlsxwriter.Workbook( xlsx_name)
    worksheet = workbook.add_worksheet()
    row = 0
    col = 0
    for key, value in profile.items():
        worksheet.write(row, col, key)
        worksheet.write(row, col + 1, value)
        row += 1
    workbook.close()



if __name__ == '__main__':

    config_file=cfg_file_load()
    config_profile(config_file)
#config_profile("sense_and_direct_68xx_Test0.cfg")
#config_profile("ISK_6m_default.cfg")