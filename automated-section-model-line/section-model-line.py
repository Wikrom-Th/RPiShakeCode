from obspy.clients.fdsn import Client
from obspy import UTCDateTime, Stream, read
from obspy.taup import TauPyModel
from obspy.geodetics.base import locations2degrees
from matplotlib.transforms import blended_transform_factory
from os import path
from matplotlib import cm
from numpy import linspace
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import numpy as np

client = Client('http://fdsnws.raspberryshakedata.com')

# Change this to your station
STATION = {
    "network": "AM",
    "id": "R21C3",
    "lat": 13.7207,
    "lon": 100.7701,
    "channel": "EHZ"
}

# configuration of the section plot
DURATION = 1400  # Length in seconds of data to plot after origin time
MIN_DIST = 0 # minimum distance for a seismometer in degrees
MAX_DIST = 180 # maximum distance in degrees
STEP = 2.25 # step in degrees between seismometers
ANGLE_DX = 10 # angle between tick marks on x-axis of section
PHASES = ["P", "pP", "PP", "S", "Pdiff", "PKP", "PKIKP", "PcP", "ScP", "ScS", "PKiKP", "SKiKP",
            "SKP", "SKS"] # list of phases for which to compute theoretical times
PHASE_PLOT = "spots" # choose lines or spots for phases
DPI = 80 # dpi for plot
FIG_SIZE = (1920/DPI, 1080/DPI) # size of figure in inches. Slightly bigger than PLOT_SIZE
PLOT_SIZE = (FIG_SIZE[0]*DPI*0.75,FIG_SIZE[1]*DPI*0.75) # plot size in pixels with borders for labels
F1 = 0.1  # High-pass filter corner for seismometers up to 90 degrees
F2 = 3.0  # Low-pass filter corner 
F3 = 0.4  # High-pass filter corner for seismometers from 90 degrees
F4 = 1.2  # Low-pass filter corner 
MODEL = 'iasp91'  # Velocity model to predict travel-times through
EXCLUDE = ['R6F29', 'R4355', 'R6324', 'RE063', 'RAE6A', 'REB59', 'R7143', 'R6F15', 'R49B6', 'RFF8B', 'R026F',
           'RBD93', 'R8D5C', 'R4FF5', 'RA211', 'RDD01', 'R2DB4', 'R16F7', 'RE8ED', 'REFF7', 'R9DAA', 'R6924',
           'RA482', 'REFFB', 'RCC45', 'R9627', 'R433E', 'R3EE8', 'R5DFC', 'R9F18', 'RA419', 'RA60A'] # noisy or mis-located seismometers
NETWORK_DATA = "../ShakeNetwork2020.csv" # data file containing seismometer names and locations, different format to 2019 data
GLOBE_PHASES = [
    # Phase, distance
    ('P', 26), 
    ('PP', 60),
    ('p', 6),
    ('pP', 45),
    ('PcP', 80),
    ('PKIKP', 150),
    ('PKiKP', 100),
    ('S', 65),
    ('ScS', -60),
    ('SKS', -82),
    ('ScP', -40),
    ('PKIKP', -150),
    ('Pdiff', -120)
]
# Calculated constants
COLORS = [ cm.plasma(x) for x in linspace(0, 0.8, len(PHASES)) ] # colours from 0.8-1.0 are not very visible

# End of parameters to define

# utility subroutines for data handling and plotting
def plottext(xtxt, ytxt, phase, vertical, horizontal, color, textlist):
    clash = True
    while clash:
        clash = False
        for i in range(len(textlist)):
            while textlist[i][0] > (xtxt - 3) and textlist[i][0] < (xtxt + 3) and textlist[i][1] > (ytxt - 24) and textlist[i][1] < (ytxt + 24):
                clash = True
                ytxt -= 2
    plt.text(xtxt, ytxt, phase, verticalalignment=vertical, horizontalalignment=horizontal, color=color, fontsize=10)
    textlist.append((xtxt, ytxt))


#TODO Find earthquakes live, only query the ones within the specified mag (>=7.0 in this case), and graph

# variables used to calculate stuffs

# sta_dist = locations2degrees(eq["lat"], eq["lon"], STATION["lat"], STATION["lon"]) # distance to local station
# eq_latlon = (eq["lat"], eq["lon"])
# start_time = UTCDateTime(eq["time"])
# end_time = start_time+DURATION