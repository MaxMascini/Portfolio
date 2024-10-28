# BCI-PsychoPy - Information

PsychoPy code for the [NeuroCognitive Imaging Lab](https://www.ncilab.ca/) BCI experiment for 2024-25 academic year. 

Part of the PhD project of Danny Godfrey and honours project for Liam Pickles.

### Explanation & Language
This experiment runs in trials and blocks. There are 6 target locations for all of the 5 experimental conditions: `Oddball`, `Flicker`, `FlickerOddball`, `DannyFlicker`, and `DannyFlickerOddball`.
- **Trial**: 
  - For `Oddball`, `FlickerOddball`, and `DannyFlickerOddball`, only one stimulus is presented at a time, and a trial is defined as the presentation of a single stimulus.
    - In all oddball and hybrid conditions, each location is stimulated 10 times per block, resulting in 60 trials per block. Of these, 10 are target trials and 50 are non-target trials. Consecutive stimulation of the same location is avoided.
  - For `Flicker` and `DannyFlicker`: a trial is defined as the entire period of stimulation (since all locations are being stimulated simultaneously)
- **Block**: The trials for one target location - resulting in 6 blocks for each condition.

### Experimental Conditions
1. `Flicker`: All 6 locations show gray silhouettes flickering at distinct frequencies in the alpha band for 30 seconds per block.
2. `Oddball`: Oddball paradigm where 5 locations show static gray silhouettes and the remaining location is highlighted with a white face for 500 ms, then all locations return to static gray silhouettes for 250 ms before the white face is shown.
3. `FlickerOddball`: 5 gray silhouettes flicker at distinct frequencies, and the remaining location is highlighted with a white face for 500 ms. After the 500 ms period, the white face disappears for 250 ms while all 6 of the locations flicker with gray silhouettes until next white face is highlighted.
4. `DannyFlicker`: All 6 locations flicker white faces at distinct frequencies for 5 seconds, then become static for 1 second. This repeats 10 times per block.
5. `DannyFlickerOddball`: 5 locations show static gray silhouettes while the remaining location is highlighted with a flickering white face for 500 ms. After the 500 ms stimulation period, all 6 locations show static gray silhouettes for 250 ms before the next white face is shown.

## Stimuli Presentation Details:
- Stimuli are presented in a circle around the center of the screen. 
- Each stimulus is mapped with an index [0-5] starting from the top and continuing clock-wise.
- Details on flicker frequency and number of on/off frames can be found in `stimuli_map.json`

## Monitors
1. `Alienware`: The butterfly room 240Hz monitor - Flicker freqs: 12.63, 10, 12, 10.43, 11.43, 10.91
   - This is the only monitor that should be used for the experiment, and is the only one with optimized distances between stimuli frequencies.
2. `testMonitor`: Default Psychopy monitor, assumes 60Hz refresh rate - Flicker freqs: 12, 10, 8.57, 7.5, 6.67, 6
3. `testMonitor144Hz`: A test monitor used for testing with a 144Hz monitor - Flicker freqs: 12, 11.08, 10.29, 9.6, 8.47, 7.2
