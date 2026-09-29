# Smart-Fitness-Session-Analyzer
Selected option A, the Smart Fitness Session Analyzer. 

Name: Celina Jåsund  
Student number: s374172

## How to start the project:
git clone git@github.com:Sleepyhead0o/Smart-Fitness-Session-Analyzer.git </br>
cd Smart-Fitness-Session-Analyzer </br>
conda env create -f env.yml </br>
conda activate fitness-analyzer </br>
python main.py </br>
python main.py --profiles data/participants.csv --sessions data/fitness_sessions.csv data/fitness_sessions_invalid.csv --output output </br>
python -m unittest tests.py </br>

## Project structure
Smart-Fitness-Session-Analyzer/
│</br>
├── data/</br>
│   ├── participants.csv</br>
│   ├── fitness_sessions.csv</br>
│   └── fitness_sessions_invalid.csv</br>
│</br>
├── fitness/</br>
│   ├── __init__.py</br>
│   ├── models.py</br>
│   ├── analysis.py</br>
│   └── datahandling_io.py</br>
│</br>
├── main.py</br>
├── data_generator.py</br>
├── tests.py</br>
├── README.md</br>
├── requirements.txt</br>
└── env.yml</br>

## Project description

This project is a small file-based object oriented Python program. That analyzes simulated fitness-session data.

The program reads participant profiles and fitness-session observations from CSV files. It validates the data, rejects invalid records, groups observations into sessions and compares measurements with each participant's reference values. Each valid session is analyzed and classified. The program continues processing when individual rows contain invalid data instead of stopping the entire application.
After the analysis, three output files are created and it prints out a short completion summary. Showing the accepted rows, rejected rows and created report files.

The possible classifications are:

- resting
- moderate activity
- high activity
- recovering
- insufficient data

The program calculates for each session the average, minimum and maximum values
for heart rate, skin response, temperature, activity level and signal quality. Also the amount of usable or rejected observations and an explanation of the classification is reported.


## Class design and responsiblity 

### models.py
This module contains the main data classes used to represent participants, reference values, observations and sessions.

- `Ref` – stores baseline heart rate, skin response and temperature. It also validates these values using properties and setters. 
- `Person` – represents a participant, and stores the participant ID, name and a `Ref` object with baseline values.
- `Obs` – represents one valid fitness observation. It stores timestamp, heart rate, skin response, temperature, activity level, and signal quality.
- `Session` – represents one complete fitness session. It connects a participant with the valid observations belonging to the session and stores the total number of observations.

### analysis.py

This module contains the logic used to analyze valid fitness sessions and determine their classification.


- `ActivityAnalysis` – A session is classified as high activity, moderate activity or resting by comparing baseline with average values (hr and act). 

- `RecoveryAnalysis` – Determines if a session has a recovery fase. Which is indicated by a decrease in both heart rate and activity from the active part of the session toward the end.

- `FitnessAnalyzer` – combines the activity and recovery analysis. It decides the final classification and creates a structured result containing summary statistics, usable and rejected observations and an explanation.

### datahandling_io.py

This module is responsible for reading CSV files, validating records, handling invalid data and creating the output files.

- `InvalidIdentifierError` – custom exception used when a participant ID or session ID has an invalid format.

- `InvalidRecordError` – custom exception used when a CSV record are not accepted.

- `read_people()` – It reads the participants.csv data file and validates records. Then two objects `Ref` and `Person` are created and it also stores rejected rows.

- `read_sessions()` – It reads the session CSV data files, validates each row and connects observations to existing participants. Then it groups observations by session ID and creates the objects`Obs` and `Session`.

- `save_reports()` – It creates the output directory and writes the report files in that folder.

### main.py

This file is the entry point of the program. It connects the different modules and controls the overall program flow. It reads command-line arguments, loads participant data, the valid and invalid session files. Then it collects the rejected records, runs `FitnessAnalyzer`, saves the reports in output directory and prints out a short completion summary.

### __init__.py

This file makes the `fitness` folder a Python package. It basically provides a simple way for `main.py` and `tests.py` to import the main classes and functions from that package.


## Object oriented programming concepts used

### Encapsulation
`Ref` uses private attributes such as `__hr`, `__sk` and `__tp`. Properties and setters control access and validate the values.

### Composition
Composition is used because the objects have "has-a" relationships:

- `Person` has a `Ref`
- `Session` has a `Person` and multiple `Obs`
- `FitnessAnalyzer` has `ActivityAnalysis` and `RecoveryAnalysis`

### Inheritance and overriding
I have not used inheritance or method overriding. The classes do not have a natural "is-a" relationship. A Session is not an Obs but contains multiple Obs objects. It is more suitable to use inheritance, when one class is a specific type of another class (subclass). For instance, if we had a class animal and another class dog. Dog can inherit from Animal class because a dog is an animal. I used composition instead because the classes have different tasks and work together to analyze a fitness session.

## Classification rules
- **Resting:** low activity level and heart rate close to the participant's baseline.
- **Moderate activity:** A minimum of 0.30 activity level or a heart rate at least 15 bpm above baseline.
- **High activity:** At least 0.67 activity level a heart rate of at least 45 bpm above baseline.
- **Recovering:** A decreasing heart rate of at least 20 bpm, and the activity level decreases by at least 0.20.
- **Insufficient data:** usable observations fewer than 3 or less than 50% of the observations are usable.

Observations with a below 0.60 signal quality are rejected.

## Assumptions

- Data_generator.py is not modified.
- Signal quality below `0.60` is considered unreliable.
- Classification is rule-based.
- Heart rate and activity level are the main values used for classification.
- Skin response and temperature are compared with baseline values.

## Known limitations

- The program only use simulated data.
- The classification thresholds are manually defined.
- Signal quality uses a fixed threshold of `0.60`.
- Skin response and temperature do not directly determine the activity   classification.
- The program is not intended for medical use.

## Example output
```text
Scenario: resting
Participant: P001
Usable observations: 12/12
Rejected observations: 0
Classification: resting

Measurement            Average   Minimum   Maximum
--------------------------------------------------
Heart rate               62.17     57.00     66.00
Skin response             1.55      1.43      1.64
Temperature              33.09     32.96     33.21
Activity level            0.12      0.03      0.19
Signal quality            0.90      0.83      0.98

Explanation:
The activity level is low. Average heart rate is 62.2 bpm compared with the baseline of 60 bpm.

==========================================================
Scenario: moderate_activity
Participant: P001
Usable observations: 12/12
Rejected observations: 0
Classification: moderate activity

Measurement            Average   Minimum   Maximum
--------------------------------------------------
Heart rate               88.50     79.00     96.00
Skin response             1.86      1.69      2.01
Temperature              33.34     33.17     33.49
Activity level            0.52      0.39      0.64
Signal quality            0.90      0.83      0.98

Explanation:
The activity level is moderate and heart rate is 28.5 bpm above baseline. Skin response differs from baseline by 0.34 and temperature differs by 0.25 °C.

==========================================================
Scenario: high_activity
Participant: P001
Usable observations: 12/12
Rejected observations: 0
Classification: high activity

Measurement            Average   Minimum   Maximum
--------------------------------------------------
Heart rate              118.58    104.00    130.00
Skin response             2.16      1.90      2.38
Temperature              33.64     33.39     33.87
Activity level            0.82      0.69      0.93
Signal quality            0.90      0.83      0.98

Explanation:
The activity level is high and heart rate is 58.6 bpm above baseline. Skin response differs from baseline by 0.64 and temperature differs by 0.55 °C.

==========================================================
Scenario: recovery
Participant: P001
Usable observations: 12/12
Rejected observations: 0
Classification: recovering

Measurement            Average   Minimum   Maximum
--------------------------------------------------
Heart rate               96.42     61.00    121.00
Skin response             1.94      1.56      2.22
Temperature              33.36     33.17     33.57
Activity level            0.47      0.09      0.91
Signal quality            0.90      0.82      0.96

Explanation:
Heart rate and activity decrease near the end of the session. Average heart rate is 36.4 bpm above the participant's baseline.

==========================================================
Scenario: poor_quality
Participant: P001
Usable observations: 0/12
Rejected observations: 12
Classification: insufficient data

Explanation:
There are too few usable observations to classify the session.
```
