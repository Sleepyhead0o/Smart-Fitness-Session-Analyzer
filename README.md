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
│
├── main.py
├── data_generator.py
├── tests.py
├── README.md
├── requirements.txt
└── env.yml

## Project description

This project is a small and simple object-oriented Python application. That analyzes simulated fitness-session data.

The program receives a participant profile and a list of observations from the `data_generator.py`. The generator returns raw dictionaries and lists, while the program converts the data into objects, validates the measurements, analyzes the session, classifies the activity level, and prints a readable report.

The possible classifications are:

- resting
- moderate activity
- high activity
- recovering
- insufficient data
