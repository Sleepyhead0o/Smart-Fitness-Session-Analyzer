# Smart-Fitness-Session-Analyzer
Selected option A, the Smart Fitness Session Analyzer. 

Name: Celina Jåsund  
Student number: s374172

## How to start the project:
git clone git@github.com:Sleepyhead0o/Smart-Fitness-Session-Analyzer.git
cd Smart-Fitness-Session-Analyzer 
conda env create -f env.yml </br>
conda activate fitness-analyzer </br>
python main.py </br>
python -m unittest tests.py </br>

## Project structure
Smart-Fitness-Session-Analyzer/
│</br>
├── main.py</br>
├── data_generator.py</br>
├── tests.py</br>
├── README.md</br>
├── requirements.txt</br>
└── env.yml</br>

## Project description

This project is a small and simple object-oriented Python application. That analyzes simulated fitness-session data.

The program receives a participant profile and a list of observations from the `data_generator.py`. The generator returns raw dictionaries and lists. While the program converts the data into objects, validates the measurements, analyzes the session, classifies the activity level and prints out a report.

The possible classifications are:

- resting
- moderate activity
- high activity
- recovering
- insufficient data

The program calculates for each session the average, minimum and maximum values
for heart rate, skin response, temperature, activity level and signal quality. Also the amount of usable or rejected observations and an explanation of the classification is reported.

## Class design and responsiblity 

- `Ref` – stores baseline heart rate, skin response and temperature.
- `Person` – represents a participant and contains a `Ref`.
- `Obs` – represents and validates one observation.
- `Session` – contains a participant and multiple observations.
- `ActivityAnalysis` – classifies resting, moderate and high activity.
- `RecoveryAnalysis` – checks whether heart rate and activity decrease.
- `FitnessAnalyzer` – combines the analysis and creates the final result.

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

- The provided `data_generator.py` is not modified.
- Signal quality below `0.60` is considered unreliable.
- Classification is rule-based.
- Heart rate and activity level are the main values used for classification.
- Skin response and temperature are compared with baseline values.

## Example output
```text
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
```
