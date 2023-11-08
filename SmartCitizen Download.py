####Mandatory Librairies
!pip install scdata --user

####Data Downloading thanks to the ID
import requests
from scdata.io.device_api import ScApiDevice

def extract_and_upload_data_id(sensor_id, upload_url):
    # Connect to Smartcitizen API and retrieve device data
    device = ScApiDevice(sensor_id)
    device_data = device.get_device_data(min_date='2021-01-01', max_date=None, frequency='1Min', clean_na=None)
    
    # Extract available data properties dynamically
    extracted_data = {}
    for property_name in device_data.columns:
        extracted_data[property_name] = device_data[property_name]
    
    # Upload the extracted data to the specified API endpoint
    response = requests.post(upload_url, json=extracted_data)
    
    # Check the response status
    if response.status_code == 200:
        print('Data uploaded successfully!')
    else:
        print('Failed to upload data. Error:', response.status_code)
#####Example
sensor_id = '10712'
upload_url = 'https://your-upload-api-endpoint.com/data'
extract_and_upload_data_id(sensor_id, upload_url)

####Data Downloading thanks to criterias
import requests
from scdata.io.device_api import ScApiDevice
from difflib import get_close_matches

def extract_and_upload_data_crit():
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
    confirm = input("Do you want to proceed with data download and upload? (y/n): ")
    if confirm.lower() != 'y':
        print("Aborted by user.")
        return
    
    # Download and upload data for the selected device
    device = ScApiDevice(selected_device_id)
    device_data = device.get_device_data(min_date=min_date, max_date=max_date)
    
    # Extract desired data from device_data and prepare for upload
    
    # Upload the data to the specified API endpoint
    upload_url = "https://example.com/upload" #to be modified
    response = requests.post(upload_url, json=extracted_data)
    
    # Check the response status
    if response.status_code == 200:
        print(f"Data for device {selected_device_id} uploaded successfully!")
    else:
        print(f"Failed to upload data for device {selected_device_id}. Error:", response.status_code)
#####Example
extract_and_upload_data_crit()
