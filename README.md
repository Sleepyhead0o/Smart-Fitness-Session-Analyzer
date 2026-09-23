# Smart-Fitness-Session-Analyzer
Selected option A, the Smart Fitness Session Analyzer. 

Name: Celina Jåsund  
Student number: s374172

## How to start the project:
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
I have not used inheritance and method overriding because the classes do not have a natural "is-a" relationship. For example, a `Session` is not a type of `Person`, and an `Obs` is not a type of `Session`. A session has multiple Obs objects. A session is not an obseravtion. 

For example if we had a class animal and another class dog. Then we can use inheritance, since dog is a subclass that inherits from another class animal. 

I used composition instead because each class has its own task, and the classes work together to analyze a fitness session. 
