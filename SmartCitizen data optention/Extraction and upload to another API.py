## Downloading data from the Smartcitizen API to the SCORE project one

### Mandatoy Librairies

get_ipython().system('pip install scdata --user')

### Data Downloading thanks to the ID into a csv

import requests
import csv
from scdata.io.device_api import ScApiDevice

def extract_and_save_data(sensor_id, csv_file_path):
    # Connect to Smartcitizen API and retrieve device data
    device = ScApiDevice(sensor_id)
    device_data = device.get_device_data(min_date='2021-01-01', max_date=None, frequency='1Min', clean_na=None)
    
    # Extract available data properties dynamically
    extracted_data = {}
    for property_name in device_data.columns:
        extracted_data[property_name] = device_data[property_name]
    
    # Save the extracted data to the CSV file
    with open(csv_file_path, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=extracted_data.keys())
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow(extracted_data)
    
    print('Data saved successfully!')

# Example usage
sensor_id = 'your_sensor_id'
csv_file_path = 'data.csv'
extract_and_save_data(sensor_id, csv_file_path)


## Multicriterias into csv

import csv
import requests
from scdata.io.device_api import ScApiDevice
from difflib import get_close_matches

def download_and_create_csv():
    # Prompt the user to input the criteria
    city = input("Enter the city name (optional): ")
    min_date = input("Enter the minimum date (optional, format: YYYY-MM-DD): ")
    max_date = input("Enter the maximum date (optional, format: YYYY-MM-DD): ")
    within_radius = input("Enter the within radius (optional): ")
    lat = input("Enter the latitude (optional): ")
    lon = input("Enter the longitude (optional): ")
    tags = input("Enter the tags (optional, comma-separated): ")
    tag_method = input("Enter the tag method (optional, 'all' or 'any'): ")
    
    # Fetch the device IDs based on the selected criteria
    device_ids = ScApiDevice.get_world_map(
        city=city,
        min_date=min_date,
        max_date=max_date,
        within=(float(lat), float(lon), float(within_radius)) if lat and lon and within_radius else None,
        tags=tags.split(",") if tags else None,
        tag_method=tag_method
    )
    
    # Validate the device selection
    if len(device_ids) == 0:
        print("No devices found with the specified criteria. Aborting.")
        return
    elif len(device_ids) == 1:
        selected_device_id = device_ids[0]
    else:
        print("Multiple devices found with the specified criteria. Select the desired device:")
        for i, device_id in enumerate(device_ids):
            print(f"{i+1}. {device_id}")
        selection = input("Enter the device number to download data from: ")
        while not selection.isdigit() or int(selection) < 1 or int(selection) > len(device_ids):
            print("Invalid selection. Please enter a valid device number.")
            selection = input("Enter the device number to download data from: ")
        selected_device_id = device_ids[int(selection)-1]
    
    # Confirm the selection
    print(f"Selected device: {selected_device_id}")
    confirm = input("Do you want to proceed with data download? (y/n): ")
    if confirm.lower() != 'y':
        print("Aborted by user.")
        return
    
    # Download data for the selected device
    device = ScApiDevice(selected_device_id)
    device_data = device.get_device_data(min_date=min_date, max_date=max_date)
    
    # Extract desired data from device_data
    extracted_data = []
    for data in device_data:
        extracted_data.append(data)
    
    # Get the unique keys from the extracted data to determine the column names
    column_names = set()
    for data in extracted_data:
        column_names.update(data.keys())
    
    # Write the extracted data to a CSV file
    csv_file = "device_data.csv"  # Specify the CSV file name
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=column_names)
        writer.writeheader()
        writer.writerows(extracted_data)
    
    print(f"CSV file '{csv_file}' created successfully!")


### Upload to API from a csv file

import csv
import requests

# Define the base URL of the SensorThings API endpoint
api_endpoint = input("Enter the API endpoint URL: ")

# Read data from the CSV file
csv_file = input("Enter the path to the CSV file: ")
with open(csv_file, "r") as file:
    reader = csv.DictReader(file)
    csv_data = list(reader)

# Create a list to store the observations
observations = []

# Iterate over the CSV data rows and create observations
for row in csv_data:
    observation = {
        "phenomenonTime": f"{row['Date']}T{row['Time']}Z",
        "result": {}
    }
    for field_name, value in row.items():
        if field_name not in ['Date', 'Time']:
            observation["result"][field_name] = value
    observations.append(observation)

# Prepare the SensorThings API data
sensor_data = {
    "observations": observations
}

# POST request to the SensorThings API endpoint
response = requests.post(api_endpoint, json=sensor_data)

# Check the response status
if response.status_code == 201:
    print("Data successfully sent to the API!")
else:
    print("Failed to send data to the API. Response:", response.status_code)
