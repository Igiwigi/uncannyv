import pandas as pd
import numpy as np
import random
import glob
import os
from psychopy import core, visual, event, gui, monitors, event
from random import sample
from triggers import setParallelData

frame_rate=60 #Hz

fixation_duration = int(0.5*frame_rate) # in seconds
stimulus_duration=int(0.7*frame_rate)
iti_min = int(0.3*frame_rate)  # minimum inter-trial interval in seconds (divisible by 60 hz?)
iti_max = int(0.6*frame_rate)  # maximum inter-trial interval in seconds
rating_duration = int(2*frame_rate)  # time to rate animacy in seconds
break_duration = int(10*frame_rate) #a 10s break
rgb_values = (153 / 255, 153 / 255, 153 / 255)  # the shade of gray they seem to have used

#specs of the monitor used for the experiment?
MON_DISTANCE = 60  # Distance between subject's eyes and monitor
MON_WIDTH = 20  # Width of your monitor in cm
MON_SIZE = [1200, 1000]  # Pixel-dimensions of your monitor
#MON_SIZE = [2560, 1600]  # Pixel-dimensions of your monitor


#setting up monitor
clock = core.Clock()

my_monitor = monitors.Monitor('testMonitor', width=MON_WIDTH, distance=MON_DISTANCE)  # Create monitor object from the variables above. This is needed to control size of stimuli in degrees.
my_monitor.setSizePix(MON_SIZE)

experiment_data = None
folder_name = "logfiles"
stimuli = glob.glob("chosen_images/*.png")
stimuli = random.sample(stimuli * 3, len(stimuli) * 3)
randomized_stimuli = []
Escape_pressed, Break_taken = False, False
real_unreal = None
i_trials = None

#make the folder if it doesnt exist
if not os.path.exists(folder_name):
    os.makedirs(folder_name)


#just to make sure the same ones don't repeat in a row
for i in range(len(stimuli)-1):
    randomized_stimuli.append(stimuli[i])
    if i < len(stimuli) - 1 and stimuli[i] == stimuli[i + 1] and i != 0 and i != 1:
        randomized_stimuli[-1], randomized_stimuli[-2] = randomized_stimuli[-2], randomized_stimuli[-1]
print(randomized_stimuli)

#define logfile
#unideal columns but should contain the information necessary?
columns = ["i", "EXP_start","ID", "Gender", "Age", "Stimulus", "Animacy_Rating", "Fixation_Start", "SOA_Start", "Face_Start", "Rating_Start", "Loop_End", "Keypress_time", "RT", "rating_dur_var", "fixation_dur_var", "stimuli_dur_var", "soa", "real_unreal", "break_taken_justb4" ]
experiment_data = pd.DataFrame(columns=columns)

# show dialogue box when starting
dialogue = gui.Dlg(title="Face Experiment")
dialogue.addField("Participant ID:")
dialogue.addField("Participant Gender:", choices=["F", "M", "Other"])
dialogue.addField("Participant Age:")
dialogue.show()

if dialogue.OK:
    ID = dialogue.data[0]
    Gender = dialogue.data[1]
    Age = dialogue.data[2]
else:
    core.quit()

#writer = ppc.csv_writer(ID, folder="saved_data")


# define window
win = visual.Window(monitor=my_monitor, units='deg', fullscr=True, allowGUI=False, color=rgb_values)

#stimdot only for testing the timings
#stimDot = visual.GratingStim(win, size=1, tex=None, pos=(10, -4), color=1, mask='circle', autoLog=False)
#stimDot_dark = visual.GratingStim(win, size=1, tex=None, pos=(10, -4), color=-1, mask='circle', autoLog=False)

# fixation cross
fixation_cross = visual.TextStim(win, '+', color = "black")

# instruction text
instruction_text = """
You will be presented with faces.
Please focus on each face and rate its ANIMACY during the rating phase.
Rate the ANIMACY from 1 (low, unreal) to 2 (high, real), using the number buttons of the keyboard (1, 2). 
You have two seconds max to do this between stimuli. 
Please rest your left hand on the number buttons 1-2 as you do the experiment.

There are 80 trials, with 10 second breaks between every 20 trials.

Press 'SPACE' when you are ready to continue.
"""

height_limit = 0.7  # Adjust based on your window size

# Create a TextStim with specified parameters
instruction_message = visual.TextStim(win, text=instruction_text, color="black",
                                      height=height_limit)

# Draw the instruction message
instruction_message.draw()
win.flip()

# Wait for these keys to continue


exp_start=core.monotonicClock.getTime()

keys = event.waitKeys(keyList=['space', 'escape'])

if 'space' in keys:
    #maybe add an animacity explainer
    animacity_text = """
    ANIMACY = how SENTIENT or ALIVE a being appears.
    
    Press 'SPACE' to start the experiment proper.
    """
    animacity_message = visual.TextStim(win, text=animacity_text, color="black", height=height_limit)
    # Draw the instruction message
    animacity_message.draw()
    win.flip()
if 'escape' in keys:
    # Close the experiment if 'escape' is pressed
    core.quit()

#wait for them to read
keys = event.waitKeys(keyList=['space', 'escape'])

key, time_key = None, None

#1 sec of wait before we start
for frame in range(1*frame_rate):
    fixation_cross.draw()
    #stimDot_dark.draw()
    win.flip()

#define the experimental loop
def begin_experiment():
    global experiment_data
    global Escape_pressed, Break_taken
    global real_unreal, i_trials
    global key, time_key
    rating_text = visual.TextStim(win, text="Rate animacy: 1 (low) - 2 (high)", color = "black" , height=height_limit)
    thanks_text = visual.TextStim(win, text="Thanks so much for participating in our experiment, it is done now!   ((quitting in 3s))", color = "black" , height=height_limit)
    i_trials = 1


    for stimulus in randomized_stimuli:
        if 'escape' in event.getKeys() or Escape_pressed == True: #quit if requested (though always late on the next loop)
            file_path = os.path.join(folder_name, f"logfile_{ID}.csv")
            experiment_data.to_csv(file_path, index=False)
            core.quit()
            
        if i_trials % 20 == 0 and i_trials != 0: #every 20 trials a 10s break
            remaining_time = 10
            for frame in range(break_duration):
                resting_text = visual.TextStim(win, text=f"Please rest for {remaining_time} seconds :)", color = "black" , height=height_limit) 
                resting_text.draw()
                win.flip()
                if frame % frame_rate == 0 and frame != 0:
                    remaining_time -= 1
                if frame == break_duration -1: #give them an extra 1s before the experiment starts back up
                    for frame in range(1*frame_rate):
                        Break_taken = True
                        fixation_cross.draw()
                        win.flip()
                time_flip_cross=core.monotonicClock.getTime()
        
        #clears keyboard events from earlier loops & the animacy_rating from earlier loops & trigger & keys
        event.clearEvents(eventType='keyboard')
        animacy_rating = None
        key, time_key = None, None
        pullTriggerDown = False #these are worthless but im just keeping them in since im used to the visual
        break_taken_var = Break_taken #just so i can test this in the csv and it doesnt get instawiped ahead
        
        #1 doing the fixations now
        if not Break_taken:
            time_flip_cross=core.monotonicClock.getTime() #onset of cross but only when no break taken since the break contains a cross
            #print("break not taken this round so we take the normal time flip!!"))
        Break_taken = False
        for frame in range(fixation_duration):
            fixation_cross.draw()
            #stimDot_dark.draw()
            if frame==0:
                win.callOnFlip(setParallelData, 1)  # pull trigger up, what does it send?
                pullTriggerDown = True
                
            win.flip()
            if frame == fixation_duration-1:
                win.callOnFlip(setParallelData, 0)
                pullTriggerDown = False
                
        #part 2, soa
        soa = np.random.randint(iti_min, iti_max+1) #this will be in frames
        offset_soa_start_cross_end = core.monotonicClock.getTime()  # offset of stimulus
        
        for frame in range(soa):
            #draw nothing so flip to empty
            if frame == 0: 
                win.callOnFlip(setParallelData, 2)  # pull trigger up
                pullTriggerDown = True
            if frame == soa-1:
                win.callOnFlip(setParallelData, 0)
                pullTriggerDown = False
        soa_end = core.monotonicClock.getTime()
        
        #part 3 drawing stimulus
        stimulus_to_draw = visual.ImageStim(win, image=stimulus)  # Define stimulus
        for frame in range(stimulus_duration):
                stimulus_to_draw.draw()
                #stimDot.draw()
                if frame==0 and any(char.isdigit() for char in stimulus):
                    real_unreal = "unreal"
                    win.callOnFlip(setParallelData, 3)  # pull trigger up
                    pullTriggerDown = True
                win.flip()
                if frame==0 and not any(char.isdigit() for char in stimulus):
                    win.callOnFlip(setParallelData, 4)  # pull trigger up
                    real_unreal = "real"
                    pullTriggerDown = True
                if frame == stimulus_duration-1:
                    win.callOnFlip(setParallelData, 0)
                    pullTriggerDown = False
        stimuli_end = core.monotonicClock.getTime()
        #part 4 drawing rating
        for frame in range(rating_duration):
                rating_text.draw()
                #stimDot_dark.draw()
                if frame==0:
                    win.callOnFlip(setParallelData, 5)  # pull trigger up
                    pullTriggerDown = True
            
            #move on if a key is pressed early
                if key is not None and frame != 0:
                    win.callOnFlip(setParallelData, 0)  # take the rating off if a key is pressed earlier than 2s
                    pullTriggerDown = False
                    break
                    
                win.flip()

                if frame == rating_duration-1:
                    win.callOnFlip(setParallelData, 0)  # take the rating off if a time out happens
                    pullTriggerDown = False
                    
        #since this is done at the end of each frame we can break out of the loop earlier on the next frame
                try:
                    key, time_key= event.getKeys(keyList=('1','2','escape'), timeStamped=True)[0]

                    if key == 'escape':
                        Escape_pressed = True
                    else:
                        animacy_rating = key
                        keypress_time = time_key - exp_start
                        stimuli_end = stimuli_end - exp_start
                        rt = time_key - stimuli_end 
                            
                except IndexError:  #if no responses were given, the getKeys function produces an IndexError
                    animacy_rating = None
                    key = None
                    keypress_time = None
                    rt = None
                    time_key = None
                        
        rating_end = core.monotonicClock.getTime()
        new_row = {
            "i": i_trials,
            "EXP_start": exp_start,
            "ID": ID,
            "Gender": Gender,
            "Age": Age,
            "Stimulus": stimulus,
            "Animacy_Rating": animacy_rating,
            "Fixation_Start": time_flip_cross-exp_start,
            "SOA_Start": offset_soa_start_cross_end-exp_start, #clumsily taken out the exp_start from each entry
            "Face_Start": soa_end-exp_start,
            "Rating_Start": stimuli_end,
            "Loop_End": rating_end - exp_start,
            "Keypress_time": keypress_time, 
            "RT": rt,
            "rating_dur_var": rating_duration,
            "fixation_dur_var": fixation_duration,
            "stimuli_dur_var": stimulus_duration,
            "soa": soa,
            "real_unreal": real_unreal,
            "break_taken_justb4": break_taken_var #this was just for testing, not particularly useful
            }
        experiment_data = pd.concat([experiment_data, pd.DataFrame([new_row])], ignore_index=True)
        i_trials+= 1
    #thank them before the experiment shuts off for all of 3 seconds
    for frame in range(3*frame_rate):
        thanks_text.draw()
        win.flip()
    
    

# Close the instruction window if 'space' is pressed
if 'space' in keys:
    begin_experiment()
    file_path = os.path.join(folder_name, f"logfile_{ID}.csv")
    experiment_data.to_csv(file_path, index=False)
else:
    core.quit()

