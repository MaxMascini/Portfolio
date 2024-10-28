# OPM-Flicker-Paradigm_24-25

This repository contains the codebase for an experimental recreation based on the EEG study ["Selective attention to stimulus location modulates the steady-state visual evoked potential" by Morgan et al. (1996)](https://doi.org/10.1073/pnas.93.10.4770). The experiment aims to investigate attentional modulation of the Steady-State Visual Evoked Potential (SSVEP) by presenting flickering visual stimuli at different frequencies in each visual field, requiring selective attention from participants. 

We aim to recreate this experiment and their findings using Optically Pumped Magnetometer - Magnetoencephalography (OPM-MEG) in place of electroencephalography (EEG) used in the original paper.
*Note*: The frequencies of the stimuli in the original experiment were 8.6 Hz and 12 Hz, however we used 10 Hz and 12 Hz in our recreation.

## Experiment Overview

In this experiment, participants view two flickering boxes displaying alphanumeric characters that change every 200 ms. The task requires participants to focus on one visual field and respond to the appearance of a target character ('5') only in the attended field, while ignoring it in the unattended field.

### Key Features
- **Selective Attention**: Flickering boxes displayed in left and right fields; participants focus on either side based on cues.
- **Flickering Frequencies**: Boxes flicker at either 10 Hz or 12 Hz, varying by trial condition.
- **Target Detection Task**: Participants respond to an infrequent target character ('5') in the attended field.

---

## Experiment Details

### Trial Structure
Each trial includes the following phases:
1. **"Ready" Screen**: Fixation cross and the word "Ready" for 2 seconds.
2. **Fixation**: Fixation cross displayed alone for 3 seconds.
3. **Attention Cue**: A left or right arrow appears for 1.5 seconds to indicate which field to attend to.
4. **Flicker/Character Sequence**: Boxes flicker and display randomized characters for 10 seconds at either 10 Hz or 12 Hz.
5. **Fixation**: A fixation cross displayed for 2 seconds.
   - Note: The fixation cross remains visible throughout the entire trial.

### Conditions
Four experimental conditions, each defined by the attended visual field and flickering frequencies:
1. **Attend Left at 10 Hz**
2. **Attend Right at 12 Hz**
3. **Attend Right at 10 Hz**
4. **Attend Left at 12 Hz**

### Block Structure
- Each block consists of 8 trials:
   - 2 trials for each of the 4 conditions, counterbalanced.
- The experiment includes 15 blocks in total.
- Participants can take a break between blocks.

### Task Requirements
- Alphanumeric characters from A-K are displayed on each flickering square, changing every 200 ms.
- **Target Detection**: Participants press a button when the number '5' appears in the attended field but not in the unattended field.

### Data Collection
Time-domain averages of the SSVEP are calculated off-line over an 11-second epoch beginning 1 second before the flickering stimuli onset.

---

## Prerequisites
- **Python 3.8+** (3.8.20)
- **Dependencies**: Listed in `requirements.txt`

## Code Structure
- `OPM_Flicker_Paradigm.py`: Main script for setting up and running the experiment.
- `images/`: Folder and subfolders containing image files used for stimuli.
- `data/`: Directory where experiment data is saved.

---

## References
Morgan, S. T., Hansen, J. C., & Hillyard, S. A. (1996). *Selective attention to stimulus location modulates the steady-state visual evoked potential*. Proceedings of the National Academy of Sciences, 93(10), 4770–4774. [doi:10.1073/pnas.93.10.4770](https://doi.org/10.1073/pnas.93.10.4770)
