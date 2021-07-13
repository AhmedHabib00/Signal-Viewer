# IMPORTS
import matplotlib.pyplot as plt
import pandas as pd
from scipy import signal
from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
from fpdf import FPDF
import functools


# ~ IMPORTS

# ------------------------------------------------------------------------------------------------

window = Tk()

# LOADING THE DATA
EMG = pd.read_csv('EMG.csv')

voice = pd.read_csv('samples (8).csv')

ECG = pd.read_csv('ECG.csv')


signals = [ECG,EMG,voice]
# ~ LOADING
# -----------------------------------------------------------
# PDF
pdf = FPDF()
pdf.add_page()
pdf.set_font('Arial', 'B', 16)
pdf.cell(40, 10, 'DSP REPORT')

WIDTH = 210
HEIGHT = 297
pad = 10

#---------------------------------------------------------------------------------------
# PDF

def PDF(i):
        figtest = plt.figure(figsize=(10.0, 5.0), linewidth=30.0)
        ax = figtest.add_subplot(111)
        ax.plot(signals[i]['Elapsed time'], signals[i]['vals'], color='b')
        ax.figure.savefig(f"{i}.png")
        if i==0:
            pdf.image(f"{i}.png", 0, 30, WIDTH / 2 - 5)
        elif i==1:
            pdf.image(f"{i}.png", 0, 100, WIDTH / 2 - 5)
        else:
            pdf.image(f"{i}.png", 0, 160, WIDTH / 2 - 5)


        freqs, times, spectrogram = signal.spectrogram(signals[0]['vals'])
        ecgspec = plt.imshow(spectrogram, aspect='auto', cmap='hot_r', origin='lower')
        ecgspec.figure.savefig(f'{i}spec.png')
        if i==0:
            pdf.image(f"{i}spec.png", WIDTH / 2, 30, WIDTH / 2 - 5)
        elif i==1:
            pdf.image(f"{i}spec.png", WIDTH / 2, 100, WIDTH / 2 - 5)
        else:
            pdf.image(f"{i}spec.png", WIDTH / 2, 160, WIDTH / 2 - 5)


PDF(0)
PDF(1)
PDF(2)
pdf.output('Report.pdf', 'F')

# Set UP

window.title('signal viewer')
fig = plt.figure(figsize=(10.0, 5.0), linewidth=30.0)
ax = fig.add_subplot(111)


is_zoomed = False
x_min, x_max = ax.get_xlim()
y_min, y_max = ax.get_ylim()
def zoomin():
    global is_zoomed
    is_zoomed = True
    if is_zoomed:
        ax.set_xlim(x_min*2,x_max/2)
        ax.set_ylim(y_min,y_max/2)
def zoomout():
    global is_zoomed
    is_zoomed = False
    ax.set_xlim(x_min/2, x_max)
    ax.set_ylim(y_min, y_max*2)


spectro = plt.figure(figsize=(10, 2))
ax.set_facecolor('#efefef')
ax2 = spectro.add_subplot(111)
ax2.set_facecolor('#efefef')

is_paused = False
i = 0
j =0
#@cache
def start(i):
    global is_paused
    global j
    if j>len(signals[i]['Elapsed time']):
        return
    is_paused = False
    window.after(1,plot(i,count=j))

def spec(i):
    plt.clf()
    freqs, times, spectrogram = signal.spectrogram(signals[i]['vals'])
    plt.imshow(spectrogram, aspect='auto', cmap='hot_r', origin='lower')
    plt.tight_layout()
    fig.canvas.draw()
    plt.ylim(0, 0.03)
    plt.draw()

is_not_scrolled = True
x, y = [], []
c =0
def plot(i,count=0):
    global c
    if c != i:
        return
    playit = Button(master=window, text='Play', command=functools.partial(start,i))
    playit.place(x=0, y=500)
    global x
    global y
    global j
    j = count
    global is_zoomed
    if count > len(signals[i]['Elapsed time']):
        x,y=[],[]
        return
    if is_paused:
        return
    #ax.cla()
    x.append(signals[i]['Elapsed time'][count])
    y.append(signals[i]['vals'][count])

    ax.set_xlim(signals[i]['Elapsed time'][count] - 0.5*signals[i]['Elapsed time'][count], signals[i]['Elapsed time'][count] + 0.5*signals[i]['Elapsed time'][count])

    ax.plot(x, y, color='g', linewidth=3.0)

    fig.canvas.draw()
    window.after(1, lambda: plot(i,count =count + 100))


# ecg plot

def stop():
    #ax.figure.clf()
    global is_paused
    is_paused = True

def reset():
    global c
    ax.set_xlim(0,signals[c]['Elapsed time'].max())
    ax.set_ylim(signals[c]['vals'].min(),signals[c]['vals'].max())
    fig.canvas.draw()

def ECGBUTT():
    global x
    global y
    global j
    global c
    c =0
    j=0
    x,y=[],[]
    ax.cla()
    spec(0)
    plot(0)

def EMGBUTT():
    global x
    global y
    global j
    global c
    c=1
    j=0
    x,y=[],[]
    ax.cla()
    spec(1)
    plot(1)


def voiceBUTT():
    global x
    global y
    global j
    global c
    c=2
    j=0
    x,y=[],[]
    ax.cla()
    spec(2)
    plot(2)
#---------------------------------------------------------------

# GUI

canvas = FigureCanvasTkAgg(fig, master=window)
canvas.get_tk_widget().grid(column=1,row=0)
def on_key_press(event):
    global is_not_scrolled
    global x
    global y
    global c
    x_min, x_max = ax.get_xlim()
    y_min,y_max = ax.get_ylim()
    if event.key == "left":
        if x_min>signals[c]['Elapsed time'].min():
            ax.set_xlim(x_max-0.002,x_max-0.001)
        fig.canvas.draw()
    if event.key == "right":
        if x_max<signals[c]['Elapsed time'].max():
            ax.set_xlim(x_min+0.001,x_min+0.002)
        fig.canvas.draw()
    if event.key == "up":
        if y_min>signals[c]['vals'].min():
            ax.set_ylim(y_min+0.1,y_max+0.2)
        fig.canvas.draw()
    if event.key == "down":
        if y_min<signals[c]['vals'].max():
            ax.set_ylim(y_min-0.1,y_max-0.1)
        fig.canvas.draw()
    if event.key == "c":
        ECGBUTT()
    if event.key == "m":
        EMGBUTT()
    if event.key =="v":
        voiceBUTT()
    if event.key == "z":
        zoomin()
    if event.key == "x":
        zoomout()
    if event.key == "p":
        start(c)
    if event.key =="s":
        stop()
    if event.key =="r":
        reset()
canvas.mpl_connect(
    "key_press_event", on_key_press)
canvas = FigureCanvasTkAgg(spectro,master = window)
canvas.get_tk_widget().grid(column=1,row=1)
ecgplot = Button(master=window, height=5, width=10, text='ECG', command=ECGBUTT)
ecgplot.grid(column=0,row=0)
emgplot = Button(master=window, height=5, width=10, text='EMG', command=EMGBUTT)
emgplot.place(x=0,y=100)
voiceplot = Button(master=window, height=5, width=10, text='Voice', command=voiceBUTT)
voiceplot.place(x=0,y=320)
pauseit = Button(master = window, text='Pause',command = stop)
pauseit.place(x=0,y=450)
resetit = Button(master = window,text='reset',command=reset)
resetit.place(x=0,y=550)
zoomit = Button(master = window, command = zoomin, text = '+')
zoomit.place(x =1000, y=100)
zooooom = Button(master=window,command=zoomout,text = '-')
zooooom.place(x=1000,y=150)
window.mainloop()