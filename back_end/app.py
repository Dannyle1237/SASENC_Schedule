from flask import Flask, render_template, jsonify
import pandas as pd
import csv
from datetime import datetime
import pytz

def custom_time_sort(time_str):
    time_str = time_str.split()
    begin_time_str = time_str[0]
    hours, minutes = begin_time_str.split(':')
    minutes = minutes[:-2]
    if hours == "12":
        hours = "0"
    if 'AM' in begin_time_str:
        return int(hours) * 60 + int(minutes)
    else:
        return (int(hours) + 12) * 60 + int(minutes)

app = Flask(__name__)
def is_time_in_range(target_time, start_time, end_time):
    target_datetime = datetime.strptime(target_time, '%I:%M%p')
    start_datetime = datetime.strptime(start_time, '%I:%M%p')
    end_datetime = datetime.strptime(end_time, '%I:%M%p')
    return start_datetime <= target_datetime <= end_datetime

data = ""
schedule_data = {}

with open('NC.csv', mode='r') as file:
    csv_reader = csv.reader(file)
    header = next(csv_reader)  # Read the header row
    dates = header[1::2]  # Extract dates from the header

    for date in dates:
        schedule_data[date] = {}

    for row in csv_reader:
        time_slots = row[::2]  # Extract time slots from the row
        descriptions = row[1::2]  # Extract event descriptions from the row
        
        for date, time, description in zip(dates, time_slots, descriptions):
            if (time and description):
                tokens = time.split()
                formatted_time = time
                if(len(tokens) > 2):
                    time_tokens = tokens[0].split(":")
                    if len(time_tokens[0]) == 1:
                        time_tokens[0] = "0" + time_tokens[0]
                    begin_formatted_time = f"{time_tokens[0]}:{time_tokens[1]}"

                    time_tokens = tokens[3].split(":")
                    if len(time_tokens[0]) == 1:
                        time_tokens[0] = "0" + time_tokens[0]
                    end_formatted_time = f"{time_tokens[0]}:{time_tokens[1]}"

                    formatted_time = f"{begin_formatted_time}{tokens[1]} - {end_formatted_time}{tokens[4]}"

                schedule_data[date][formatted_time] = description


# Define the timezone for Atlanta
atlanta_tz = pytz.timezone('America/New_York')

# Get the current date and time in Atlanta timezone
current_time_in_atlanta = datetime.now(atlanta_tz)
# Extract the day
current_day = current_time_in_atlanta.strftime("%A")
# momth and day of the month
current_month = current_time_in_atlanta.strftime("%m")
current_day_of_month = current_time_in_atlanta.strftime("%d")
current_hr = current_time_in_atlanta.strftime("%H")
current_min = current_time_in_atlanta.strftime("%m")
am_pm = current_time_in_atlanta.strftime("%p")

current_day = f"{current_day} - {current_month}/{current_day_of_month}"
current_time = f"{current_hr}:{current_min}{am_pm}"

current_day_data = {
    "current_day": current_day,
    "current_day_data": schedule_data[current_day]
}

current_data = {
    "time_range" : f"Current Time: {current_time}",
    "description": "Nothing is going on right now, enjoy your day!"
}

if current_day in schedule_data:
    for time in schedule_data[current_day]:
        tokens = time.split()
        if(is_time_in_range(current_time, tokens[0], tokens[2])):
            current_data = {
                "time_range" :time,
                "description": schedule_data[current_day][time]}

json_schedule_data = {
    "schedule": {},
    "sorted_dates": []
}

for day in schedule_data:
    schedule_list = [(time, description) for time, description in schedule_data[day].items()]

    schedule_list = sorted(schedule_list, key=lambda x:custom_time_sort(x[0]))
    json_schedule_data["schedule"][day] = schedule_list

for day in json_schedule_data["schedule"]:
    json_schedule_data["sorted_dates"].append(day)
json_schedule_data["sorted_dates"] = sorted(json_schedule_data["sorted_dates"], key=lambda x: (x[-5:], x[-2:]))

# for item in json_schedule_data:
#     print(f"{item}:\n{json_schedule_data[item]}")

@app.route('/get_schedule_data', methods=['GET'])
def get_schedule_data():
    print(f"returning {jsonify(json_schedule_data)}")
    return jsonify(json_schedule_data)

@app.route('/get_current_day_data', methods=['GET'])
def get_current_day_data():
    return jsonify(current_day_data)

@app.route('/get_current_data', methods=['GET'])
def get_current_data():
    return jsonify(current_data)

if __name__ == '__main__':
    app.run(debug=True)
