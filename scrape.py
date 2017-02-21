import re
import pandas as pd
import numpy as np
import copy
from bs4 import BeautifulSoup

def clean_mode(mode_element):
    return mode_element.text.split(", ")[0].strip().lower()

modes_default = {
    "Regular modes of transportation: Walk": 0,
    "Regular modes of transportation: Bike": 0,
    "Regular modes of transportation: Taxi/Uber": 0,
    "Regular modes of transportation: Subway/Light Rail": 0,
    "Regular modes of transportation: Car": 0,
    "Regular modes of transportation: Bus": 0
}

def assign_modes(modes_default, modes_list):
    new_modes = copy.copy(modes_default)
    base_mode = "Regular modes of transportation: "
    for mode in modes_list:
        mode = mode.strip().lower()
        if mode == "walk":
            new_modes[base_mode + "Walk"] = 1
        if mode == "bike" or mode == "bicycle":
            new_modes[base_mode+ "Bike"] = 1
        if mode == "taxi" or mode == "uber":
            new_modes[base_mode + "Taxi/Uber"] = 1
        if mode == "subway/light rail":
            new_modes[base_mode + "Subway/Light Rail"] = 1
        if mode == "car":
            new_modes[base_mode + "Car"] =  1
        if mode == "bus":
            new_modes[base_mode + "Bus"] = 1
    return new_modes

def clean_zip_code(zipcode):
    try:
        int(zipcode)
    except:
        return np.NaN
    else:
        if len(zipcode) < 5:
            return np.NaN
        else:
            return int(zipcode[:5])

data = []
for n in range(1, 28):
    print(n)
    f = open('Responses/Response #' + str(n) + '.html', 'r')
    soup = BeautifulSoup(f, 'html.parser')
    sections = soup.find_all(class_="response-question-list-container")
    for section in sections:
        container = section.find(class_="response-question-list")
        answers = {}
        for i, question in enumerate(container.find_all(class_="response-question-container")):
            if i == 4:
                answer_key = question.find(class_="response-question-title-text").text.strip().replace("\xa0", " ")
                modes = [clean_mode(x) for x in question.find_all(class_=re.compile("response-text$"))]
                new_modes = assign_modes(modes_default, modes)
                answers.update(new_modes)
            elif i == 7:
                for j, item in enumerate(question.find_all(class_="response-list-item")):
                    inner_answer = {}
                    inner_answer_key = item.find("span", class_="response-text-label").text.strip().replace("\xa0", " ")
                    inner_answer_value = item.find(class_="response-text").text.strip()
                    answers["Factors discouraging bike trip: " + inner_answer_key] = inner_answer_value
            elif i == 8:
                for j, item in enumerate(question.find_all(class_="response-list-item")):
                    inner_answer = {}
                    inner_answer_key = item.find("span", class_="response-text-label").text.strip().replace("\xa0", " ")
                    inner_answer_value = item.find(class_="response-text").text.strip()
                    answers["Factors encouraging bike trip: " + inner_answer_key] = inner_answer_value
            elif i == 9:
                answer_key = question.find(class_="response-question-title-text").text.strip().replace("\xa0", " ")
                answer_value = question.find(class_=re.compile("response-text$")).text.strip()
                match = re.match('[0-9]+', answer_value)
                if match:
                    answers[answer_key] = match
                else:
                    answers[answer_key] = np.NaN
            else:
                answer_key = question.find(class_="response-question-title-text").text.strip().replace("\xa0", " ")
                answer_value = question.find(class_=re.compile("response-text")).text.strip()
                answers[answer_key] = answer_value
            
        if answers not in data:
            data.append(answers)

def replace_skipped(data):
    to_skip = ["N/A", "Respondent skipped this question", "(no label)"]
    if data in to_skip:
        return np.NaN
    else: 
        return data

def replace_encourage_discourage(data):
    if data == "Discourage me very little":
        return 0
    elif data == "Discourage me greatly":
        return 1
    elif data == "Encourage me very little":
        return 0
    elif data == "Encourage me greatly":
        return 1
    else:
        return data

df = pd.DataFrame(data)
df = df.applymap(replace_skipped)
df = df.applymap(replace_encourage_discourage)

columns_to_drop = [
    'Factors encouraging bike trip: Other (please specify)',
    'Factors discouraging bike trip: Other (please specify)',
    'What is the most common short trip that you make (5 miles or less)?',
    'What mode of transportation do you typically use for that trip?',
    'Why did you choose that answer?',
    'Have you ever used a bike share system, such as CitiBike? If so, what was your experience?',
    'If you have time for a 10 minute video interview, please enter your name and contact info:'

]
df.drop(columns_to_drop, axis=1, inplace=True)
df["What is your ZIP code/postal code?"] = df["What is your ZIP code/postal code?"].apply(clean_zip_code)
print(df.columns.values)
for value in df.columns.values:
    print(df[value])

