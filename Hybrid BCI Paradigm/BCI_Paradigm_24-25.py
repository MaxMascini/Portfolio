import gc
from psychopy import visual, logging, core, event, monitors, data, gui
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER, priority)
from psychopy.tools import environmenttools
from numpy import sin, cos, pi
import psychopy
import matplotlib
matplotlib.use('Qt5Agg')  # change this to control the plotting 'back end'
import os.path as op
import os
import numpy as np
from numpy.random import random, randint
import random
# for markers
import socket
from subprocess import Popen, PIPE
from pylsl import StreamInfo, StreamOutlet
import json

import time

#######################################
# Define functions for this experiment
#######################################
def showExpInfoDlg(expInfo, gui):
    """
    Show participant info dialog.
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    
    Returns
    ==========
    dict
        Information about this experiment.
    """
    # temporarily remove keys which the dialog doesn't need to show
    poppedKeys = {
        'date': expInfo.pop('date'),
        'expName': expInfo.pop('expName'),
        'psychopyVersion': expInfo.pop('psychopyVersion'),
    }
    # show participant info dialog
    dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName)
    if dlg.OK == False:
        core.quit()  # user pressed cancel
    # restore hidden keys
    expInfo.update(poppedKeys)
    # return expInfo
    return expInfo

def setupData(expInfo, data_dir):
    """
    Make an ExperimentHandler to handle trials and saving.
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    data_dir : Path, str or None
        Folder to save the data to, leave as None to create a folder in the current directory.    
    Returns
    ==========
    psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    """
    # BIDS-compliant data directory
    
    # data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
    filename = u'%s_task-%s' % (expInfo['participant'], expInfo['condition'])
    
    data_dir = op.join(data_dir, expInfo['participant'], expInfo['session'])
    
    eeg_dir = op.join(data_dir, 'eeg')
    os.makedirs(eeg_dir, exist_ok=True)
    
    data_dir = op.join(data_dir, 'beh')
    os.makedirs(data_dir, exist_ok=True)

    # an ExperimentHandler isn't essential but helps with data saving
    thisExp = data.ExperimentHandler(
        name=expName, version='',
        extraInfo=expInfo, runtimeInfo=None,
        savePickle=True, saveWideText=True,
        dataFileName= data_dir + os.sep + filename, sortColumns='time'
    )
    thisExp.setPriority('thisRow.t', priority.CRITICAL)
    thisExp.setPriority('expName', priority.LOW)
    # return experiment handler
    return thisExp, data_dir

def setupLogging(filename):
    """
    Setup a log file and tell it what level to log at.
    
    Parameters
    ==========
    filename : str or pathlib.Path
        Filename to save log file and data files as, doesn't need an extension.
    
    Returns
    ==========
    psychopy.logging.LogFile
        Text stream to receive inputs from the logging system.
    """
    # this outputs to the screen, not a file
    # logging.console.setLevel(logging.EXP)
    # save a log file for detail verbose info
    logFile = logging.LogFile(filename + '.log', level=logging.EXP)
    
    return logFile

def saveData(thisExp):
    """
    Save data from this experiment
    
    Parameters
    ==========
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    """
    filename = thisExp.dataFileName
    # these shouldn't be strictly necessary (should auto-save)
    thisExp.saveAsWideText(filename + '.csv', delim='auto')
    thisExp.saveAsPickle(filename)

def endExperiment(thisExp, win=None):
    """
    End this experiment, performing final shut down operations.
    
    This function does NOT close the window or end the Python process - use `quit` for this.
    
    Parameters
    ==========
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    inputs : dict
        Dictionary of input devices by name.
    win : psychopy.visual.Window
        Window for this experiment.
    """
    
    print('\n *-- Ending experiment, please wait... --* \n')
    
    if win is not None:
        # remove autodraw from all current components
        win.clearAutoDraw()
        win.flip()
        
        # Draw message for participant
        visual.TextStim(win, text='Saving data and exiting please wait...', pos=(0, 0), color='white').setAutoDraw(True)
        win.flip()
    # mark experiment handler as finished
    thisExp.status = FINISHED
    
    # Cleanup and Exit
    labrecorder.sendall(b"stop\n")
    core.wait(15.) # Wait for LabRecorder to finish saving data
    pid.terminate() 
    pid.wait()
    logging.flush()
    
    win.close()
    core.quit()
    
def generate_randomized_list(image_stims, repeats=10):
    """
    Generate a list where each stimulus is repeated exactly `repeats` times.
    The list is randomized such that no stimulus repeats consecutively.
    
    Parameters:
    - image_stims: List of stimuli to choose from.
    - repeats: Number of times each stimulus should appear in the list.
    
    Returns:
    - stim_list: A randomized list of stimuli with no consecutive repetitions.
    """
    # Create a list with each stimulus repeated `repeats` times
    stim_list = image_stims * repeats
    random.shuffle(stim_list)  # Initial shuffle
    
    # Ensure no consecutive duplicates
    for i in range(1, len(stim_list)):
        if stim_list[i] == stim_list[i - 1]:
            # Find an index to swap that doesn't create consecutive duplicates
            swap_idx = i
            while swap_idx < len(stim_list) and (stim_list[swap_idx] == stim_list[i] or stim_list[swap_idx] == stim_list[i - 1]):
                swap_idx += 1
            if swap_idx < len(stim_list):
                # Swap elements to avoid consecutive duplicates
                stim_list[i], stim_list[swap_idx] = stim_list[swap_idx], stim_list[i]
    
    return stim_list

def generate_randomized_list_with_flicker(image_stims, flicker_frames_per_cycle, repeats=10):
    """
    Generate a list of randomized stimuli where each stimulus appears `repeats` times, 
    with no consecutive repetitions, and ensure the flicker period for each stimulus is attached.

    Parameters:
    - image_stims: List of PsychoPy stimuli (ImageStim objects).
    - flicker_frames_per_cycle: List of corresponding flicker periods for each stimulus.
    - repeats: Number of times each stimulus should appear.
    
    Returns:
    - stim_flicker_list: A randomized list of tuples (stimulus, flicker_period) with no consecutive repetitions.
    """
    # Create a list of tuples [(stim1, flicker1), (stim2, flicker2), ...] repeated `repeats` times
    stim_flicker_list = [(stim, flicker) for stim, flicker in zip(image_stims, flicker_frames_per_cycle)] * repeats
    
    # Shuffle the list while ensuring no consecutive duplicates
    random.shuffle(stim_flicker_list)
    
    for i in range(1, len(stim_flicker_list)):
        if stim_flicker_list[i][0] == stim_flicker_list[i - 1][0]:
            swap_idx = i
            while swap_idx < len(stim_flicker_list) and (stim_flicker_list[swap_idx][0] == stim_flicker_list[i][0] or stim_flicker_list[swap_idx][0] == stim_flicker_list[i - 1][0]):
                swap_idx += 1
            if swap_idx < len(stim_flicker_list):
                # Swap to avoid consecutive duplicates
                stim_flicker_list[i], stim_flicker_list[swap_idx] = stim_flicker_list[swap_idx], stim_flicker_list[i]
    
    return stim_flicker_list

def create_form(name, items):
    return visual.Form(win=win, name=name,
        items=items,
        textHeight=0.04,
        font='Open Sans',
        randomize=False,
        style='custom...',
        fillColor=[-1.0000, -1.0000, -1.0000], borderColor=None, itemColor='white', 
        responseColor='white', markerColor='red', colorSpace='rgb', 
        units='height', size=(1, 0.7), pos=(0, 0), itemPadding=0.05, depth=0
    )
    
def create_button_stim(name, image):
    return visual.ImageStim(win=win,
                            name=name, 
                            image=image, 
                            anchor='bottom-right',
                            units='height',
                            pos=(0.75, -0.35), size=(0.15,0.2),
                            interpolate=True, depth=-2.0
                            )

def load_stimuli(win, path, locations, size=5):
    files = os.listdir(path)
    images = [os.path.join(path, f) for f in files if os.path.isfile(os.path.join(path, f))]
    return [visual.ImageStim(win, image=images[n], pos=locations[n], size=size, autoLog=False) for n in range(len(locations))]

############################################
# Setup LabRecorder & LSL Basics
############################################
expName = 'BCI_Paradigm_24-25'
psychopyVersion = psychopy.__version__
expt_root = op.dirname(op.abspath(__file__))

print(f"Experiment Root: {expt_root}")

markers = StreamInfo('BCIMarkerStream', 'Markers', 1, 0, 'string', 'BCIPsychoPy')
lsl_outlet = StreamOutlet(markers)
logging.console.setLevel(logging.WARNING)
# BIDS-compliant data directory
data_root = op.join(expt_root, 'data')

############################################
# GUI for user input
############################################
expInfo = {'participant': 'sub-' + f'{randint(200, 999):03.0f}', # Empty participant ID field
            'condition': ['Flicker', 'Oddball', 'FlickerOddball', 'DannyFlicker', 'DannyFlickerOddball'], 
            'monitor_name': ['Alienware', 'testMonitor', 'testMonitor144Hz'],
            'session' : ['ses-001'],
            'date': data.getDateStr(),  # Timestamp of run
            'expName': expName, # Name of experiment - defined above
            'psychopyVersion': psychopyVersion, # Psychopy version - defined above
            }

screens = {'Alienware': {'width': 58.8, 'resolution': [2560, 1440], 'monitor_num': 1, 'useRetina': False, 'flicker_freqs': [12.63, 10, 12, 10.43, 11.43, 10.91], 'refresh_rate': 240}, # Monitor num 2 = Alienware in recording room
            'testMonitor': {'width': 30, 'resolution': [1920, 1080], 'monitor_num': 0, 'useRetina': False, 'flicker_freqs': [6, 12, 6.67, 10, 7.5, 8.57], 'refresh_rate': 60}, # Default psychopy monitor - assumes 60Hz screen
            'testMonitor144Hz': {'width': 30, 'resolution': [1920, 1080], 'monitor_num': 0, 'useRetina': False, 'flicker_freqs': [7.2, 12, 8.47, 11.08, 9.6, 10.29], 'refresh_rate': 144},
            }

################################
# Get Info From GUI
################################
expInfo = showExpInfoDlg(expInfo=expInfo, gui=gui)
thisExp, data_dir = setupData(expInfo=expInfo, data_dir=data_root)
logFile = setupLogging(filename=thisExp.dataFileName)

monitor_name = expInfo['monitor_name']
monitor_num = screens[monitor_name]['monitor_num']
monitor_width = screens[monitor_name]['width']
view_dist = 60.
monitor_res = screens[monitor_name]['resolution']

################################
# launch LabRecorder
################################
pid = Popen(['./LabRecorder/LabRecorder.exe'], stdin=PIPE)
# open connection to LabRecorder
try:
    labrecorder = socket.create_connection(("localhost", 22347))
except:
    print('Please launch Lab Recorder application and then restart the experiment')
    exit()  
    
expt_mode = expInfo['condition']
subj_id = expInfo['participant'][-3:]
ses = expInfo['session'][-3:]
labrecorder.sendall(b"filename {task:%s} {participant:%s} {session:%s} \n" % (expt_mode.encode(), subj_id.encode(), ses.encode()))

############################################  
# Parameters user might want to change
############################################
# "target" is the location the user is instructed to attend to
# "trial" is the highlighting of a single location (Oddball) or flickering of all locations (Flicker)
# "block" is the set of trials after a single target location has been highlighted
flicker_freqs = screens[monitor_name]['flicker_freqs']  # The provided alpha-band frequencies for the chosen monitor -> see `screens`
bg_color = 'black'
num_locations = 6 # Number of locations at which possible targets can appear
dist_from_ctr = 8 # degrees
img_size = 5 # degrees
target_marker_size = img_size * 1.5 # degrees
target_id_color = 'magenta' # color that indicates the target identity
num_blocks = num_locations * 1 # num blocks should be multiple of num_locations
num_trials = 10 # 10 trials per block

#######
# General Condition Vars
#######
flicker_trial_time = 30. # Number of seconds the Flicker block should last
flickeroddball_flicker_time = 0.500 # Number of seconds the stim flickers in FlickerOddball
highlight_duration = 0.500 # seconds the target location is highlighted in Oddball
between_trial_duration = 0.250 # seconds 
target_id_duration = 2. # seconds - how long target location is shown before start of trials
inter_block_interval = 2. # Wait 2 seconds between blocks

#######
# Danny Condition Vars
#######
danny_flicker_trial_time = 5. # Number of seconds the DannyFlicker block should last
danny_flicker_inter_trial_time = 1. # Number of seconds the non-flickering sihouettes show in DannyFlicker 
danny_flicker_repeats = 10 # Number of start/stop flicker cycles before the next target is selected (i.e., block ends)
danny_flickeroddball_flicker_time = 0.500 # Number of seconds the stim flickers in DannyFlickerOddball

################################################
# Parameters that could improve performance
################################################
visual.useFBO = True  # if available (try without for comparison)
disable_gc = False  # disable python garbage collection (try without for comparison)
process_priority = 'realtime'  # 'high' or 'realtime'

if process_priority == 'normal':
    pass
elif process_priority == 'high':
    core.rush(True)
elif process_priority == 'realtime':
    # Only makes a diff compared to 'high' on Windows.
    core.rush(True, realtime=True)
else:
    print('Invalid process priority:', process_priority, "Process running at normal.")
    process_priority = 'normal'

if disable_gc:
    gc.disable()

#######################
# Set up the window
#######################
mon = monitors.Monitor(monitor_name) #, width=monitor_width, distance=view_dist)
    
win = visual.Window(monitor = mon,
                    screen = monitor_num,
                    size = monitor_res, 
                    units = 'deg',
                    winType = 'pyglet', 
                    fullscr = True, 
                    allowGUI = False, 
                    waitBlanking = True,
                    checkTiming = True,
                    color = bg_color,
                    useRetina = screens[monitor_name]['useRetina'],
                    allowStencil = True
                    )

############################################
# Setup Flash Counter Form
############################################
item_width = 1
response_width = 1
options = '0, 50, 100'
layout = 'horiz'
granularity = 0
flash_questions = ['How many times did the target location appear?']

flash_q_items = [{'itemText': flash_questions[0], 
                'itemWidth': item_width, 'type': 'rating', 'responseWidth': response_width,
                'options': '0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12', 'layout': layout, 'granularity': granularity
                }]
    
continue_button = create_button_stim('continue', 'images/buttons/button_next.png')
end_button = create_button_stim('end', 'images/buttons/button_finish.png')

clickable_buttons = [continue_button, end_button]

############################################
# define the locations of the stimuli
############################################
# define cartesian coordinates for num_locations locations arranged in a circle around 0, 0 - at a distance of dist_from_ctr
locations = [(round(dist_from_ctr * sin(2 * pi * n / num_locations), 4),
              round(dist_from_ctr * cos(2 * pi * n / num_locations), 4)) for n in range(num_locations)]


###############################################################################
# Presentation Start
###############################################################################
win.mouseVisible = False

refresh_rate = screens[monitor_name]['refresh_rate']

# If refresh_rate isn't supplied, measure it.
refresh_rate = refresh_rate if refresh_rate else round(win.getActualFrameRate(nIdentical=10, nWarmUpFrames=50), 1)

# print('Monitor refresh rate: %10.3f Hz' % refresh_rate)

############################################
# Parameters for flickering stimuli
############################################
# print('Flicker frequencies = ', flicker_freqs)

# Calculate the cycle durations for each frequency (1/frequency)
durations = [1.0 / freq for freq in flicker_freqs]
flicker_frames_per_cycle = [round(refresh_rate / freq, 0) for freq in flicker_freqs]

# print('Flicker periods = ', flicker_frames_per_cycle)

######
## Useful for debugging purposes
######
# for freq, duration in zip(flicker_freqs, durations):
#     flicker_period = round(refresh_rate / freq, 0)
#     print(f"Frequency: {freq} Hz, Duration: {duration} s, Flicker period: {flicker_period} frames")
#     flicker_period2 = refresh_rate / (1.0 / duration) 
#     print(f"Flicker period: {flicker_period2} frames")
    
    
############################################
# Set up Images
############################################ 

# Load Target Highlight Screen Gray Sihouettes
grey_path = os.path.join('images', 'sil_grey')
grey_sil = load_stimuli(win, grey_path, locations)

# Load White Faces or Gray Silhouettes depending on the experiment mode
stim_path = os.path.join('images', 'white_faces') if expt_mode in ['Oddball', 'FlickerOddball', 'DannyFlicker', 'DannyFlickerOddball'] else os.path.join('images', 'sil_grey')
image_stims = load_stimuli(win, stim_path, locations)

# Load Gray Silhouettes
sil_path = os.path.join('images', 'sil_grey')
silhouettes = load_stimuli(win, sil_path, locations)

# Mapping the number (0-6), with the coordinates, frequency, and frames on/off of that stimulus.
    # Results in a dictionary with structure of "0: {'coordinates': (x1, y1), 'frequency': freq1, 'frames' : frames1},"
stimuli_map = {i: {'coordinates': locations[i], 'frequency': flicker_freqs[i], 'frames': flicker_frames_per_cycle[i]} for i in range(num_locations)}

# print(json.dumps(stimuli_map, indent=1)) # Makes the output more legible for debugging

#######################
# Create Purple Highlight Box
#######################
target_markers = [visual.Rect(win,
                                width=target_marker_size, height=target_marker_size, 
                                lineColor=target_id_color,
                                lineWidth=5,
                                fillColor=None,
                                pos=locations[n]
                                )
                    for n in range(len(locations))
                    ]

#######################
# Create a fixation cross
#######################
fixation = visual.TextStim(win=win, name='fixation',
    text='+',
    font='Open Sans',
    pos=(0, 0), height=1.5, wrapWidth=None, ori=0.0, 
    color='magenta', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=0.0)

#######################
# Set Instructions by Condition
#######################
if expt_mode == 'Oddball':
    image='images/instructions/oddball_instruct.png'
elif expt_mode == 'FlickerOddball':
    image='images/instructions/flicker_oddball_instruct.png'
elif expt_mode == 'Flicker':
    image='images/instructions/flicker_instruct.png'
elif expt_mode == 'DannyFlicker':
    image='images/instructions/danny_flicker_instruct.png'
elif expt_mode == 'DannyFlickerOddball':
    image='images/instructions/danny_flicker_oddball_instruct.png'
else:
    image='images/instructions/instruct_0.png'

instruct = visual.ImageStim(win = win,
                            image = image,
                            size = win.size,
                            units = 'pix',
                            pos = (0, 0)
                            ) 

# Show instructions
instruct.setAutoDraw(True)
while not event.getKeys(keyList=["space"]):
        win.flip()
instruct.setAutoDraw(False)
win.flip() 

print(f"\nStarting Condition: {expt_mode}")

# start the clock
routine_timer = core.Clock() 

# Determine order of targets
target_order = np.random.permutation(num_locations)

#############################
# Main Loop 
##############################

# Send the frequencies at the beginning, and only once
if expt_mode in ['Flicker', 'FlickerOddball', 'DannyFlicker', 'DannyFlickerOddball']:
    
    # Iterate over the stimuli_mapping to push the frequency for each stimulus
    for loc_index, details in stimuli_map.items():
        frequency = details['frequency']  # Get the frequency for this stimulus
        marker = f'loc_{loc_index}/freq_{frequency}'
        
        # Push the marker to the LSL outlet
        # print(f"Pushing Marker: {marker}")
        lsl_outlet.push_sample([marker])

# Outer Block loop
for block in range(num_blocks): # 6 blocks
    
    win.mouseVisible = False # Make mouse invisible after showing flash_q_form
    
    print(f"Starting Block: {block}")
    
    marker_prefix = expt_mode + '/block_' + str(block) + '/'
    t = routine_timer.getTime()
    cue_started = False    
    target_loc = target_order[block]
    
    # Draw the target highlight for 2 seconds
    for n in range(num_locations):
        grey_sil[n].setAutoDraw(True)  # Set the silhouette to auto draw
        
        if n == target_loc:
            target_markers[n].setAutoDraw(True)  # Set the target marker to auto draw
            marker = marker_prefix + 'target_marker/' + 'loc_' + str(n) 
            # print(f"Pushing Marker: {marker}")
            lsl_outlet.push_sample([marker])

    while routine_timer.getTime() - t <= target_id_duration:
        win.flip()  # Flip the window to show the silhouettes and target markers

    # After the duration, set the silhouettes and target markers to not auto draw
    for n in range(num_locations):
        grey_sil[n].setAutoDraw(False)
        target_markers[n].setAutoDraw(False)

    marker = marker_prefix + 'block_start'
    # print(f"Pushing Marker: {marker}")
    lsl_outlet.push_sample([marker])    
        
###########
# Flicker
###########

    if expt_mode == 'Flicker':
        
        frame_count = 0
        
        # This loop executes each frame for the duration of the flicker cycle -> Speed of code here is key
        for _ in range(int(refresh_rate * flicker_trial_time)): 
            
            # Check for key presses to exit early
            if 'escape' in event.getKeys():
                thisExp.status = FINISHED
                if thisExp.status == FINISHED:
                    endExperiment(thisExp, win=win)                    
                    
            # Increment frame count
            frame_count += 1
            
            # Loop through the flickering stimuli 
            for image_stim, flicker_period in zip(image_stims, flicker_frames_per_cycle):
                                
                # Determine whether to show or hide the stimulus based on frame count
                if (frame_count % flicker_period) < (flicker_period / 2):
                    image_stim.setAutoDraw(True)  # Show the stimulus
                else:
                    image_stim.setAutoDraw(False)  # Hide the stimulus

            # Flip the window to update the display
            win.flip()

        marker =  marker_prefix + 'block_end'
        # print(f"Pushing Marker: {marker}")
        lsl_outlet.push_sample([marker])
        
###########
# Oddball
###########

    elif expt_mode == 'Oddball':    
        
        randomized_stim_list = generate_randomized_list(image_stims, repeats=num_trials)
    
        for image_stim in randomized_stim_list:
        
            if 'escape' in event.getKeys():
                thisExp.status = FINISHED
                if thisExp.status == FINISHED:
                    endExperiment(thisExp, win=win)  
            
            # Determine the location of the current stimulus and push target/non-target marker
            for loc_n, location in enumerate(locations):
                
                if np.array_equal(location, image_stim.pos):  # Check the position of the stimulus
                    
                    if loc_n == target_loc:
                        marker = marker_prefix  + 'target/' + 'loc_' + str(loc_n)
                    else:
                        marker = marker_prefix + 'nontarget/' + 'loc_' + str(loc_n)
                        
                    # print(f"Pushing Marker: {marker}")
                    lsl_outlet.push_sample([marker])

                silhouettes[loc_n].draw()
            
            # Draw the image
            image_stim.draw()

            # Flip the window to show the image
            win.flip()

            # Show the white stim for 500ms
            core.wait(highlight_duration)
            
            # Draw all the silhouettes and wait for 250ms before showing next stim
            for sil in silhouettes:
                sil.draw()
            win.flip()
            core.wait(between_trial_duration)

        marker = marker_prefix + 'block_end'
        # print(f"Pushing Marker: {marker}")
        lsl_outlet.push_sample([marker])

###########
# FlickerOddball
###########

    elif expt_mode == 'FlickerOddball':
        
        # Generate a randomized list of stimuli, with each stimulus repeated 10 times
        randomized_stim_list = generate_randomized_list(image_stims, repeats=num_trials)
        
        for image_stim in randomized_stim_list:
            
            frame_count = 0
            
            # Determine the target or non-target marker based on stimulus position
            loc_index = locations.index(tuple(image_stim.pos))  # Find the index of the stimulus location
            
            if loc_index == target_loc:
                marker = marker_prefix + f'target/loc_{loc_index}'
            else:
                marker = marker_prefix + f'nontarget/loc_{loc_index}'
                
            # Check for key presses to exit early
            if 'escape' in event.getKeys():
                thisExp.status = FINISHED
                if thisExp.status == FINISHED:
                    endExperiment(thisExp, win=win)  
            
            # print(f"Pushing Marker: {marker}")
            lsl_outlet.push_sample([marker])

            # Execute the flicker loop for the duration of the flicker time
            for _ in range(int(refresh_rate * flickeroddball_flicker_time)):
                # Increment frame count for flickering
                frame_count += 1

                # Loop through all the locations and flicker both silhouettes and image stimuli
                for loc_n, flicker_period in enumerate(flicker_frames_per_cycle):

                    # If the current location is where the red face should appear, flicker it
                    if loc_n == loc_index:
                        if (frame_count % flicker_period) < (flicker_period / 2):
                            image_stim.setAutoDraw(True)  # Show the red face
                        else:
                            image_stim.setAutoDraw(False)  # Hide the red face
                    else:
                        # Flicker the silhouette (white face) at other locations
                        if (frame_count % flicker_period) < (flicker_period / 2):
                            silhouettes[loc_n].setAutoDraw(True)  # Show the silhouette
                        else:
                            silhouettes[loc_n].setAutoDraw(False)  # Hide the silhouette

                # Flip the window to update the display
                win.flip()
            
            # After the flicker loop, clear the autoDraw for both current_red_face and silhouettes

            #### NEW 250ms PERIOD WHERE ONLY SILHOUETTES FLICKER ####
            frame_count = 0

            # Clear the autoDraw for both current image_stim and silhouettes
            image_stim.setAutoDraw(False)
            for sil in silhouettes:
                sil.setAutoDraw(False)
            win.flip(clearBuffer=True) 
            
            # Flicker only the silhouettes for 250ms before the next trial                
            for _ in range(int(refresh_rate * between_trial_duration)):
                # Increment frame count
                frame_count += 1

                # Flicker the silhouettes only (red face is turned off during this period)
                for loc_n, flicker_period in enumerate(flicker_frames_per_cycle):
                    
                    # Flicker the silhouette (white face) at other locations
                    if (frame_count % flicker_period) < (flicker_period / 2):
                        silhouettes[loc_n].setAutoDraw(True)  # Show the silhouette
                    else:
                        silhouettes[loc_n].setAutoDraw(False)  # Hide the silhouette

                # Flip the window to update the display
                win.flip()            
            
            # After the flicker loop, clear the autoDraw for both current image_stim and silhouettes
            image_stim.setAutoDraw(False)
            for sil in silhouettes:
                sil.setAutoDraw(False)
                
        # Record the end of the block and push marker to LSL
        marker = marker_prefix + 'block_end'
        # print(f"Pushing Marker: {marker}")
        lsl_outlet.push_sample([marker])

        win.clearBuffer()

######################
# Danny Conditions 
######################

###########
# DannyFlicker
###########

    if expt_mode == 'DannyFlicker':
        
        frame_count = 0

        # This loop repeats the start/stop flickering X times before a new target is selected
        for repeat_n in range(danny_flicker_repeats):
            
            # Draws all the images during the 1s wait
            for image_stim in image_stims:
                image_stim.draw()
            win.flip()

            core.wait(danny_flicker_inter_trial_time) # 1s wait time before all flickering again

            ## Temporary code for if LSL markers are wanted on each repeat
            marker = marker_prefix + f'repeat_{repeat_n + 1}' # Add one to the repeat_n so that we don't get 0
            # print(f"Pushing Marker: {marker}")
            lsl_outlet.push_sample([marker])
            
            # Check for key presses to exit early
            if 'escape' in event.getKeys():
                thisExp.status = FINISHED
                if thisExp.status == FINISHED:
                    endExperiment(thisExp, win=win)  
        
            # This loop executes each frame for the duration of the flicker cycle -> Speed of code here is key
            for _ in range(int(refresh_rate * danny_flicker_trial_time)): # 5 seconds

                # Increment frame count
                frame_count += 1
                
                # Loop through the flickering stimuli
                for image_stim, flicker_period in zip(image_stims, flicker_frames_per_cycle):
                    
                    # Determine whether to show or hide the stimulus based on frame count
                    if (frame_count % flicker_period) < (flicker_period / 2):
                        image_stim.setAutoDraw(True)  # Show the stimulus
                    else:
                        image_stim.setAutoDraw(False)  # Hide the stimulus

                # Flip the window to update the display
                win.flip()
            
            win.clearBuffer()

        marker =  marker_prefix + 'block_end'
        # print(f"Pushing Marker: {marker}")
        lsl_outlet.push_sample([marker])

###########
# DannyFlickerOddball
###########

    elif expt_mode == 'DannyFlickerOddball':

        stim_flicker_list = generate_randomized_list_with_flicker(image_stims, flicker_frames_per_cycle, repeats=num_trials)

        frame_count = 0

        for stim, flicker_period in stim_flicker_list:
            start_time = time.time()  # Record the start time

            # Compare current image_stim position with the target location directly
            if np.array_equal(stim.pos, locations[target_loc]):
                marker = marker_prefix + f'target/loc_{target_loc}'
            else:
                loc_index = locations.index(tuple(stim.pos))  # Find the index of the current stim location
                marker = marker_prefix + f'nontarget/loc_{loc_index}'
            
            # print(f"Pushing Marker: {marker}")
            lsl_outlet.push_sample([marker])
            
            # This loop draws the silhouettes at non-target locations
            for loc_n in range(len(locations)):
                
                # Reset autoDraw for all the silhouettes
                silhouettes[loc_n].autoDraw = False

                # Set autoDraw for the silhouettes at non-target locations
                if not np.array_equal(locations[loc_n], stim.pos):
                    
                    silhouettes[loc_n].autoDraw = True
            
            if 'escape' in event.getKeys():
                thisExp.status = FINISHED
                if thisExp.status == FINISHED:
                    endExperiment(thisExp, win=win)
                
            # This loop executes each frame for the duration of the flicker cycle -> Speed of code here is key            
            for _ in range(int(refresh_rate * danny_flickeroddball_flicker_time)):
                
                # Increment the frame count
                frame_count += 1
                
                if (frame_count % flicker_period) < (flicker_period / 2):
                    stim.setAutoDraw(True)
                else:
                    stim.setAutoDraw(False)  

                win.flip()
                
            # After flickering, draw all the silhouettes and wait for 250ms before showing next stim
            for sil in silhouettes:
                sil.draw()
            win.flip()
            core.wait(between_trial_duration)
                
        marker = marker_prefix + 'block_end'
        # print(f"Pushing Marker: {marker}")
        lsl_outlet.push_sample([marker])
        win.clearBuffer()

###########################################
# Show Flash Count Form
###########################################
    if expt_mode in ['Oddball', 'FlickerOddball', 'DannyFlickerOddball']:
        
        marker = marker_prefix + 'flash_count_start'
        # print(f"Pushing Marker: {marker}")
        lsl_outlet.push_sample([marker])
        
        exec = environmenttools.setExecEnvironment(globals())
        win.mouseVisible = True
        mouse = event.Mouse(win=win)
        x, y = [None, None]
        mouse.mouseClock = core.Clock()

        globalClock = core.Clock() 
        routineTimer = core.Clock()  # to track time remaining of each (possibly non-slip) routine
        frameTolerance = 0.001  # how close to onset before 'same' frame

        # Creates the form
        flash_form = create_form('flash', flash_q_items[:2])
        flash_forms = [flash_form]

        for f_idx, form in enumerate(flash_forms):
            continueRoutine = True
            # update component parameters for each repeat
            thisExp.addData(form.name + '.started', globalClock.getTime())
            # setup some python lists for storing info about the mouse
            mouse.x = []
            mouse.y = []
            mouse.leftButton = []
            mouse.midButton = []
            mouse.rightButton = []
            mouse.time = []
            mouse.clicked_name = []
            gotValidClick = False  # until a click is received
            # keep track of which components have finished
            clickable_img = clickable_buttons[f_idx]
            questions_Components = [form, mouse, clickable_img]
            for thisComponent in questions_Components:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            # reset timers
            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            frameN = -1
            
            # --- Run Routine "questions" ---
            routineForceEnded = not continueRoutine
            while continueRoutine:
                # get current time
                t = routineTimer.getTime()
                tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                
                # *form* updates
                
                # if form is starting this frame...
                if form.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                    # keep track of start time/frame for later
                    form.frameNStart = frameN  # exact frame index
                    form.tStart = t  # local t and not account for scr refresh
                    form.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(form, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'form.started')
                    # update status
                    form.status = STARTED
                    form.setAutoDraw(True)
                
                # if form is active this frame...
                if form.status == STARTED:
                    # update params
                    pass
                # *mouse* updates
                
                # if mouse is starting this frame...
                if mouse.status == NOT_STARTED and t >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    mouse.frameNStart = frameN  # exact frame index
                    mouse.tStart = t  # local t and not account for scr refresh
                    mouse.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(mouse, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.addData('mouse.started', t)
                    # update status
                    mouse.status = STARTED
                    mouse.mouseClock.reset()
                    prevButtonState = mouse.getPressed()  # if button is down already this ISN'T a new click
                if mouse.status == STARTED:  # only update if started and not finished!
                    buttons = mouse.getPressed()
                    if buttons != prevButtonState:  # button state changed?
                        prevButtonState = buttons
                        if sum(buttons) > 0:  # state changed to a new click
                            # check if the mouse was inside our 'clickable' objects
                            gotValidClick = False
                            clickableList = environmenttools.getFromNames(clickable_img, namespace=locals())
                            for obj in clickableList:
                                # is this object clicked on?
                                if obj.contains(mouse):
                                    gotValidClick = True
                                    mouse.clicked_name.append(obj.name)
                            x, y = mouse.getPos()
                            mouse.x.append(x)
                            mouse.y.append(y)
                            buttons = mouse.getPressed()
                            mouse.leftButton.append(buttons[0])
                            mouse.midButton.append(buttons[1])
                            mouse.rightButton.append(buttons[2])
                            mouse.time.append(mouse.mouseClock.getTime())
                            if gotValidClick:
                                continueRoutine = False  # end routine on response
                
                # *clickable_img* updates
                
                # if clickable_img is starting this frame...
                if clickable_img.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance and form.complete == True:
                    # keep track of start time/frame for later
                    clickable_img.frameNStart = frameN  # exact frame index
                    clickable_img.tStart = t  # local t and not account for scr refresh
                    clickable_img.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(clickable_img, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'clickable_img.started')
                    # update status
                    clickable_img.status = STARTED
                    clickable_img.setAutoDraw(True)
                
                # if clickable_img is active this frame...
                if clickable_img.status == STARTED:
                    # update params
                    pass
                
                # check for quit (typically the Esc key)
                if event.getKeys(keyList=["escape"]):
                    thisExp.status = FINISHED
                if thisExp.status == FINISHED:
                    endExperiment(thisExp, win=win)
                    # return
                
                # check if all components have finished
                if not continueRoutine:  # a component has requested a forced-end of Routine
                    routineForceEnded = True
                    break
                continueRoutine = False  # will revert to True if at least one component still running
                for thisComponent in questions_Components:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
            
            for thisComponent in questions_Components:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            thisExp.addData(form.name + '.stopped', globalClock.getTime())
            form.addDataToExp(thisExp, 'rows')
            form.autodraw = False
            # store data for thisExp (ExperimentHandler)
            thisExp.addData('mouse.x', mouse.x)
            thisExp.addData('mouse.y', mouse.y)
            thisExp.addData('mouse.leftButton', mouse.leftButton)
            thisExp.addData('mouse.midButton', mouse.midButton)
            thisExp.addData('mouse.rightButton', mouse.rightButton)
            thisExp.addData('mouse.time', mouse.time)
            thisExp.addData('mouse.clicked_name', mouse.clicked_name)
            thisExp.nextEntry()
            # the Routine "flash_count_forms" was not non-slip safe, so reset the non-slip timer
            routineTimer.reset()
    else: # Only wait when form isn't shown ('Flicker' condition)
        core.wait(inter_block_interval)

# --- Tidy up, save, and exit ---
endExperiment(thisExp, win=win)
