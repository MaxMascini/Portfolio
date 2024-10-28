import gc
from psychopy import visual, logging, core, event, monitors, data, gui
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER, priority)
import psychopy
import os.path as op
import os
import numpy as np
from numpy.random import random, randint
import random
import u3



############################################
# Necessary Functions:
############################################
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
    core.wait(2.)
    logging.flush()
    
    win.close()
    core.quit()

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
    filename = u'%s_task-%s' % (expInfo['participant'], expInfo['task'])
    
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

## This function creates a list with no back-to-back repeats
def create_randomized_stim_sequence(win, image_paths, characters, position, num_stim=51):
    # Generate an initial random sequence with choices
    random_sequence = random.choices(characters, k=num_stim)
    
    # Adjust to ensure no consecutive duplicates
    for i in range(1, len(random_sequence)):
        if random_sequence[i] == random_sequence[i - 1]:
            # Pick a new character that is not the same as the previous one
            available_characters = [char for char in characters if char != random_sequence[i - 1]]
            random_sequence[i] = random.choice(available_characters)
            
    # Create the stimulus sequence with ImageStim objects
    # stim_sequence = [visual.ImageStim(win, image=image_paths[char], pos=position, name=char) for char in random_sequence]
    stim_sequence = [visual.ImageStim(win, image=image_paths[char], pos=position, name=char, units='deg', mask=None, anchor='center',
        ori=0.0, size=letter_size,
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-2.0) for char in random_sequence] # change texRes to 256.0 from 128.0
    return stim_sequence

def clear_window():
    win.clearAutoDraw()
    win.clearBuffer()
    win.flip()

# Define a mock class for LabJack
class MockLabJack:
    def getCalibrationData(self):
        print("Mock: Calibration data retrieved.")
    
    def voltageToDACBits(self, voltage, dacNumber=1, is16Bits=False):
        voltage = voltage
        dacNumber = dacNumber
        is16Bits = is16Bits
        # print(f"Mock: Voltage {voltage} set on DAC {dacNumber}.")
        return 0  # return a dummy bit value

    def getFeedback(self, feedback):
        # print(f"Mock: Feedback with value {feedback}.")
        feedback = feedback
        # print('Mock: Feedback with value {}.'.format(feedback))
        pass

############################################
# Basic Study Information & Setup
############################################
expName = 'OPM_Paradigm_24-25'
psychopyVersion = psychopy.__version__
expt_root = op.dirname(op.abspath(__file__))

print(f"Experiment Root: {expt_root}")

data_root = op.join(expt_root, 'data')

###############################
# LabJack Initialization
###############################
# Try to initialize LabJack; if it fails, use MockLabJack
try:
    import u3
    d = u3.U3()
    d.getCalibrationData()
    labjack_available = True
except Exception:  # Catch any exception if LabJack device is not connected
    labjack_available = False

# Initialize LabJack or MockLabJack based on availability
if labjack_available:
    print("\nLabJack connected.")
else:
    print("\nLabJack not connected, using MockLabJack. \n")
    d = MockLabJack()

# Start block marker
BLOCK_START_VAL = d.voltageToDACBits(2.5, dacNumber=1, is16Bits=False)

# Within trial markers:
OFF_VAL = d.voltageToDACBits(0.0, dacNumber=1, is16Bits=False) # Flicker off 0.0 V
FIXATION_ON_VAL = d.voltageToDACBits(0.5, dacNumber=1, is16Bits=False) # Fixation cross on 0.5 V
ARROW_ONSET_VAL = d.voltageToDACBits(1.0, dacNumber=1, is16Bits=False) # Arrow onset 1.0 V
FIXATION_2_ON_VAL = d.voltageToDACBits(1.5, dacNumber=1, is16Bits=False) # Fixation cross 2 on 1.5 V
FLICKER_ON_VAL = d.voltageToDACBits(2.0, dacNumber=1, is16Bits=False) # Flicker on 2.0 V

# Condition markers:
LEFT_ATT_10HZ_LEFT_12HZ_RIGHT = d.voltageToDACBits(3.0, dacNumber=1, is16Bits=False)
LEFT_ATT_12HZ_LEFT_10HZ_RIGHT = d.voltageToDACBits(3.5, dacNumber=1, is16Bits=False)
RIGHT_ATT_10HZ_LEFT_12HZ_RIGHT = d.voltageToDACBits(4.0, dacNumber=1, is16Bits=False)
RIGHT_ATT_12HZ_LEFT_10HZ_RIGHT = d.voltageToDACBits(4.5, dacNumber=1, is16Bits=False)

# Set to 0 before starting
d.getFeedback(u3.DAC0_8(OFF_VAL))

############################################
# GUI for user input
############################################
expInfo = {'participant': 'sub-' + f'{randint(200, 999):03.0f}', # Empty participant ID field
            'monitor_name': ['Epson', 'Alienware', 'testMonitor'],
            'task' : ['OPM_SSVEP'],
            'session' : ['ses-001'],
            'date': data.getDateStr(),  # Timestamp of run
            'expName': expName, # Name of experiment - defined above
            'psychopyVersion': psychopyVersion, # Psychopy version - defined above
            }

screens = {'Alienware': {'width': 58.8, 'resolution': [2560, 1440], 'monitor_num': 1, 'view_dist': 60.0, 'useRetina': False, 'refresh_rate': 240}, # Monitor num 2 = Alienware in recording room
            'Epson': {'width': 30, 'resolution': [1920, 1200], 'monitor_num': 1, 'view_dist': 13.0, 'useRetina': False, 'refresh_rate': 60}, # Monitor num 1 = Epson in recording room
            'testMonitor': {'width': 30, 'resolution': [1920, 1080], 'monitor_num': 0, 'view_dist': 60, 'useRetina': False, 'refresh_rate': 60}, # Default psychopy monitor - assumes 60Hz screen
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
monitor_res = screens[monitor_name]['resolution']

############################################  
# Parameters user might want to change
############################################
refresh_rate = screens[monitor_name]['refresh_rate']  # Monitor refresh rate
letter_duration = 0.2  # 200ms
frames_per_letter = int(refresh_rate * letter_duration) # 200 ms = 12 frames @ 60 frames per second
trial_duration = 10 # Seconds
num_trials = 8 # Number of trials per block
num_blocks = 15 # Number of blocks per participant
arrow_duration = 1.5 # Seconds
fixation_cross_duration = 3 # Seconds
vertical_offset = 0

view_dist = screens[monitor_name]['view_dist'] #60.0 #13.0  # viewing distance in cm
letter_size = (2.0, 2.0) # letter size
character_height_deg = 1.0  # character height in degrees
square_size_deg = 2.0  # square size in degrees
fixation_distance_deg = 5.7  # distance from fixation to stimulus center in degrees


def calculate_visual_params(view_dist, angle):
    # Calculate size or distance based on the visual angle
    return 2 * view_dist * np.tan(np.radians(angle / 2))

# Calculate sizes and positions in cm
character_height = calculate_visual_params(view_dist, character_height_deg)
square_size = calculate_visual_params(view_dist, square_size_deg)
fixation_distance = calculate_visual_params(view_dist, fixation_distance_deg)

# Define conditions with integrated voltage values and descriptive marker names
conditions = [
    {"attention": "left", "flicker": {"left": 12, "right": 10}, "voltage": LEFT_ATT_12HZ_LEFT_10HZ_RIGHT},
    {"attention": "right", "flicker": {"left": 12, "right": 10}, "voltage": RIGHT_ATT_12HZ_LEFT_10HZ_RIGHT},
    {"attention": "left", "flicker": {"left": 10, "right": 12}, "voltage": LEFT_ATT_10HZ_LEFT_12HZ_RIGHT},
    {"attention": "right", "flicker": {"left": 10, "right": 12}, "voltage": RIGHT_ATT_10HZ_LEFT_12HZ_RIGHT},
]

# Generate counterbalanced blocks
all_blocks = []
for block_num in range(num_blocks):
    # Create two repetitions of each condition within a block
    block_conditions = conditions * 2
    # Shuffle to randomize order within the block
    random.shuffle(block_conditions)
    all_blocks.append(block_conditions)


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
                    units = 'deg', # 'cm', 
                    winType = 'pyglet', 
                    fullscr = True, 
                    allowGUI = False, 
                    waitBlanking = True,
                    checkTiming = True,
                    color = 'black',
                    useRetina = False,
                    allowStencil = True
                    )

#######################
# Create the stimuli
#######################
# Update window with calculated sizes and positions
fixation_cross = visual.ShapeStim(win, name='fixation', vertices='cross', units='deg', 
                                  size=(character_height, character_height), pos=(0, vertical_offset), 
                                  color='white', fillColor='white')
ready = visual.TextStim(win=win, name='ready', text='Ready', font='Arial', units='deg', pos=(0, (3-vertical_offset)), height=1.0, wrapWidth=None, ori=0.0, color='white', colorSpace='rgb', languageStyle='LTR', depth=-1.0)
left_arrow = visual.ImageStim(win, image='images/left.png', mask=None, anchor='center',
                                ori=0.0, pos=(0, vertical_offset), size=(4, 4),
                                color=[1,1,1], colorSpace='rgb', opacity=None,
                                flipHoriz=False, flipVert=False,
                                texRes=128.0, interpolate=True, depth=-3.0)
right_arrow = visual.ImageStim(win, image='images/right.png', mask=None, anchor='center',
                                ori=0.0, pos=(0, vertical_offset), size=(4, 4),
                                color=[1,1,1], colorSpace='rgb', opacity=None,
                                flipHoriz=False, flipVert=False,
                                texRes=128.0, interpolate=True, depth=-3.0)

left_box = visual.Rect(
    win=win, name='left_box', units='deg', 
    width=square_size, height=square_size,
    pos=(-fixation_distance, vertical_offset), anchor='center',
    lineWidth=1.0, colorSpace='rgb',  lineColor='white', fillColor='white',
    opacity=1.0, depth=1.0, interpolate=True)

right_box = visual.Rect(
    win=win, name='right_box', units='deg', 
    width=square_size, height=square_size,
    pos=(fixation_distance, vertical_offset), anchor='center',
    lineWidth=1.0, colorSpace='rgb',  lineColor='white', fillColor='white',
    opacity=1.0, depth=1.0, interpolate=True)

# Define character stimuli with calculated size
characters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', '5']
image_paths = {char: f'images/stimuli/{char}.png' for char in characters}
left_character_sequence = create_randomized_stim_sequence(win, image_paths, characters, position=(-fixation_distance, 0))
right_character_sequence = create_randomized_stim_sequence(win, image_paths, characters, position=(fixation_distance, 0))

flicker_boxes = [left_box, right_box]


###############################
# Start Experiment
###############################
print(f"\nWaiting for spacebar to start experiment")


while not event.getKeys(keyList=["space"]):
    visual.TextStim(win, text='Press the spacebar to start the experiment', pos=(0, 0), color='white').setAutoDraw(True)
    win.flip()

print(f"Starting Experiment\n")

win.mouseVisible = False

# start the clock
routine_timer = core.Clock() 

for block_num, block in enumerate(all_blocks):
    
    clear_window()
    
    # Participants are allowed to take a break between blocks
    if block_num != 0:
        while not event.getKeys(keyList=["space"]):
            visual.TextStim(win, text='You may take a break. \nPress the spacebar to start the next block', pos=(0, 0), color='white').setAutoDraw(True)
            win.flip()
    
    print(f"*-- Starting Block {block_num + 1} --*")
    
    d.getFeedback(u3.DAC0_8(BLOCK_START_VAL))
    
    for trial_num, trial in enumerate(block):
        
        # Add break/exit option for participant control
        if 'escape' in event.getKeys():
            win.close()
            core.quit()
        
        # Clear the screen
        clear_window()
        
        # Get attention direction and flicker configuration for this trial
        attention = trial["attention"] # Left or right
        flicker_left = trial["flicker"]["left"] # 10 or 12
        flicker_right = trial["flicker"]["right"] # 10 or 12
        trial_voltage = trial["voltage"] # Retrieves the voltage for the current condition
        
        flicker_freqs = [flicker_left, flicker_right]
        flicker_frames_per_cycle = [int(refresh_rate / freq) for freq in flicker_freqs]

        # Set arrow direction based on trial
        arrow_image = left_arrow if attention == "left" else right_arrow
        
        # Set up the visual elements accordingly
        print(f"\nTrial {trial_num + 1}: Attention {attention}; Left: {flicker_left}Hz, Right: {flicker_right}Hz")
        
        if trial != 0:
            core.wait(2.0) # Wait for 2 seconds between trials
                
        clear_window()
        
        # Showing 'ready' and fixation cross for 2 seconds       
        t = routine_timer.getTime()
        while routine_timer.getTime() - t <= 2:
            fixation_cross.setAutoDraw(True)
            ready.setAutoDraw(True)
            win.flip()
            
            d.getFeedback(u3.DAC0_8(trial_voltage))

        # Showing just the fixation cross for 3 seconds
        t = routine_timer.getTime()
        while routine_timer.getTime() - t <= fixation_cross_duration:
            ready.setAutoDraw(False)
            win.flip()
            
            d.getFeedback(u3.DAC0_8(FIXATION_ON_VAL))
        
        # Clear window
        clear_window()
        
        # Show the arrow for 1.5 seconds
        t = routine_timer.getTime()
        while routine_timer.getTime() - t <= arrow_duration:

            arrow_image.setAutoDraw(True)
            win.flip()
            
            d.getFeedback(u3.DAC0_8(ARROW_ONSET_VAL)) # Marker for arrow onset

        # Clear window
        clear_window()
        
        # Set the fixation cross to be drawn for the duration of the trial
        fixation_cross.setAutoDraw(True)
        
        d.getFeedback(u3.DAC0_8(FIXATION_2_ON_VAL)) # Marker for fixation 2 onset
        
        core.wait(0.500) # Wait for 500 ms

        frame_count = 0
        letter_frame_count = 0
        letter_index = 0  # Track the current letter index

        d.getFeedback(u3.DAC0_8(FLICKER_ON_VAL)) # Marker for flicker on
        
        # This loop needs to execute each frame for the duration of the flicker cycle
        for frame in range(int(refresh_rate * trial_duration)): # Produces exactly 600 cycles (60 Hz/fps x 10 seconds)
            # Increment frame count
            letter_frame_count += 1
            frame_count += 1
            
            # Determine if the current letter has been shown for 12 frames
            if letter_frame_count >= frames_per_letter:
                # Reset the frame count and increment the letter index to show the next letter
                letter_frame_count = 0
                letter_index += 1
            
            # Loop through the flickering stimuli 
            for box, flicker_period in zip(flicker_boxes, flicker_frames_per_cycle):
                # Determine whether to show or hide the stimulus based on frame count
                if (frame_count % flicker_period) < (flicker_period / 2):
                    box.draw()
                else:
                    pass
                    
            # Get the current letters to draw based on the letter index
            left_letter = left_character_sequence[letter_index]
            right_letter = right_character_sequence[letter_index]
            
            # Draw the current letters
            left_letter.draw()
            right_letter.draw()

            # if right_letter.name or left_letter.name == '5' and frame_count % 12 == 0:
            #     print("5 Detected")
            
            # Flip the window to update the display
            win.flip()
            
            
            # core.wait(1)
            # # Add break/exit option for participant control
            # if 'escape' in event.getKeys():
            #     win.close()
            #     core.quit()
    
            
        d.getFeedback(u3.DAC0_8(OFF_VAL))
        
        
print("\nExperiment complete. Exiting...")

endExperiment(thisExp, win=win)