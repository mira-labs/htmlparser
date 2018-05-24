from bs4 import BeautifulSoup
from pathlib import Path
import re

# Read all html files
file_list = [f for f in Path(".").glob("**/*.html") if f.is_file()]

# Create CSV headers
csv_string = "insurance_group,make,model,variant,engine_size,door_no,year_from,year_to" + "\n"
csv_string_info_not_split = "insurance_group,make,model,variant,info" + "\n"

# Loop through files
for f in file_list:
    with open(f) as fp:
        soup = BeautifulSoup(fp, "html.parser")
        path = fp.name.split('/')
        group = path[1].split('-')[1]

        # Find the lowest level children
        vehicle_containers = soup.find_all("div", class_="vehicle")

        # For each find text values and parent elementes
        for vehicle_container in vehicle_containers:
            text = vehicle_container.contents
            variant = text[0]
            engine_size = ""
            door_no = ""
            year_from = ""
            year_to = ""
            info_full_text = ""
            try:
                # Split text into components
                info_full_text = text[1].contents[0]
                info_full_text_components = info_full_text.split('-')

                # Check if components can be identified as engine size or  door number
                for i in range(len(info_full_text_components)):
                    if info_full_text_components[i].find('litre') > -1:
                        engine_size = info_full_text_components[i]
                        engine_size = engine_size[0:engine_size.find(' ')].strip()
                    if info_full_text_components[i].find('door') > -1:
                        door_no = info_full_text_components[i]
                        door_no = door_no[0:door_no.find('door')].strip()

                # Find years component as text in brackets
                year_components = re.findall('\(.*?\)', info_full_text)[0]
                year_components = re.sub("\(|\)", "", year_components).split('-')
                year_from = year_components[0]

                # Check if year_from exists
                if len(year_from) < 4 or year_from.isdigit() is False:
                    year_from = ""
                if len(year_components) == 2:
                    year_to = year_components[1]
            except IndexError:
                engine_size = ""
                door_no = ""
                year_from = ""
                year_to = ""

            # Find model and make
            model_container = vehicle_container.parent.parent
            model_label = model_container.select(".label")
            model_contents = model_label[0]
            model = model_contents.contents[0].strip()
            make_container = model_container.parent.parent.select("h3")
            make = make_container[0].contents[0].strip()
            pattern = re.compile(make + " " + model, re.IGNORECASE)
            variant = pattern.sub("", variant).strip()

            # Add to CSV string
            csv_string = csv_string + group + "," + make + "," + model + "," + variant + "," \
                         + engine_size + "," + door_no + "," + year_from + "," + year_to + "\n"
            csv_string_info_not_split = csv_string_info_not_split + group + "," + make + "," + model + "," \
                                        + variant + "," + info_full_text + "\n"

# Save files
file = open("insurance_groups.csv", "w")
file.write(csv_string)

file = open("insurance_groups_info_not_split.csv", "w")
file.write(csv_string_info_not_split)
file.close()
