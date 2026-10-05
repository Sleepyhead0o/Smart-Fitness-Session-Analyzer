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

The program reads data from CSV files to get the fitness-session observations and participant profiles. The data is validated and invalid records are rejected. Observations are grouped into sessions, and the measurements with each participants references values are compared. Also each session that are valid is analyzed and classified. The program continues processing when individual rows contain invalid data instead of stopping the entire application. After the analysis, three output files are created and it prints out a short completion summary. Showing the accepted rows, rejected rows and created report files.

The possible classifications are:

- resting
- moderate activity
- high activity
- recovering
- insufficient data

The program calculates for each session the average, minimum and maximum values
for heart rate, skin response, temperature, activity level and signal quality. Also the amount of usable or rejected observations and an explanation of the classification is reported.


## Class design and responsiblity 

Instead of having only a long main.py file like in assigment 1. The program is now separated into several modules. 

### models.py
This module contains the main data classes used to represent participants, reference values, observations and sessions.

- `Ref` – stores baseline heart rate, skin response and temperature. It also validates these values using properties and setters. 
- `Person` – represents a participant, and stores the participants ID, name and a `Ref` object with their baseline values.
- `Obs` – represents one valid fitness observation. It stores timestamp, heart rate, skin response, temperature, activity level, and signal quality.
- `Session` – represents one complete fitness session. It connects a participant with the valid observations belonging to the session and stores the total number of observations.

### analysis.py

This module contains the logic used to analyze valid fitness sessions and determine their classification.


- `ActivityAnalysis` – It can classify a session with high activity, moderate activity or resting by comparing baseline with average values (hr and act). 

- `RecoveryAnalysis` – It can determine if a session has a recovery fase. Which is indicated by a decrease in both heart rate and activity from the active part of the session toward the end.

- `FitnessAnalyzer` – combines the activity and recovery analysis. It decides the final classification and creates a structured result containing summary statistics, usable and rejected observations and an explanation.

### datahandling_io.py

This module is reading CSV files and validating records. Also it is handling invalid data and creating the output files.

- `InvalidIdentifierError` – Is a custom exception that is used when a participants ID or session ID are in an invalid format.

- `InvalidRecordError` – custom exception used when a CSV record are not accepted.

- `read_people()` – It reads the participants.csv data file and validates records. Then two objects `Ref` and `Person` are created and it also stores rejected rows.

- `read_sessions()` – It reads the session CSV data files, validates each row and connects observations to existing participants. Then it groups observations by session ID and creates the objects`Obs` and `Session`.

- `save_reports()` – It creates the output directory/folder. Then it writes the output report files in that folder.

### main.py

The main file are connecting the different modules and controll the flow. It reads command-line arguments, loads data and collect collects the rejected records. Then it runs `FitnessAnalyzer`, saves the reports in output directory and prints out a short completion summary.


### __init__.py

It marks the `fitness` folder as a Python package, which allows the program to easily to import its modules. 


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
- **High activity:** The activity level should be at least 0.67 and a heart rate of at least 45 bpm above the baseline value.
- **Moderate activity:** A minimum of 0.30 activity level or a heart rate at least 15 bpm above baseline.
- **Recovering:** A decreasing heart rate of at least 20 bpm, and the activity level decreases by at least 0.20.
- **Insufficient data:** - If the amount of usable observations are fewer than 3 or less than 50%.  

Also, If the signal quality is below 0.60 the observation is disregarded . 

## Assumptions

- The supplied CSV files use the required column names and order.
- A participants ID must follow the format `P***`.
- A fitness session ID must follow the format `FIT-YYYY-NNN`.
- A session belongs to only one participant.
- Heart rate values between 35 and 205 bpm are considered valid.
- Temperature values between 25 and 42 °C are considered valid.
- Skin response cannot be negative.
- Activity level must be between 0 and 1.
- Signal quality must be between 0 and 1.
- Observations with signal quality below 0.60 are rejected.
- A minimum of three usable observations is required for a normal activity classification.
- At least 50% of the observations in a session must be usable.
- At least six usable observations are required to detect recovery.

## Known limitations

- I use a rule-based classification with fixed threshold values.
- Recovery detection must have at least six usable observations.
- Recovery is only determined based on changes in heart rate and activity level.
- The program is not intended for medical use.
- The program expects the CSV files to follow the required format and column structure.

## Example output
```text
Analysis complete.
Accepted rows: 25
Rejected rows: 15
Processed sessions: 7
Created files:
- output/analysis_summary.csv
- output/analysis_report.txt
- output/rejected_records.txt
```
