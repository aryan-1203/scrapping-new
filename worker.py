import sys, time, json, os, csv, pandas as pd
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from worker_actions.actions import driver

from worker_actions import select_something, open_website, click_something, E2W, E3W, return_header, return_row

short_wait = 3
long_wait = 5

# Parse command-line args
arg_holder = sys.argv[1:]
print(arg_holder)
sys.stdout.flush()

# Load JSON configs
with open('jsons/paths.json', 'r') as file:
    paths_json = json.load(file)

with open('jsons/states.json', 'r') as file:
    state_paths_json = json.load(file)

with open(f'jsons/{arg_holder[0]}_rtos.json') as file:
    rtos_json = json.load(file)

# Paths from JSONs
year_field_path = paths_json['year_field_path']
year_path = paths_json[f"data_year_{arg_holder[2]}_path"]

state_field_path = paths_json['state_field_path']
state_path = state_paths_json[arg_holder[0]]

rto_field_path = paths_json['rto_field_path']
rto_path = str(paths_json['rto_path']).replace('PLACEHOLDER', str(rtos_json[arg_holder[1]]))

x_axis_field_path = paths_json['x_axis_field_path']
x_axis_month_path = paths_json['x_axis_month_path']

y_axis_field_path = paths_json['y_axis_field_path']
y_axis_make_path = paths_json['y_axis_make_path']

button_refresh_main = paths_json['button_refresh_main']
button_expand = paths_json['button_expand']
button_refresh_side = paths_json['button_refresh_side']
button_download = paths_json['button_download']

# Fuel and product category paths
fuel = paths_json['fuel']
pure = paths_json['pure']
vehicle_class = paths_json.get(arg_holder[3], "NULL")  # Default to NULL if not found

two_wheeler_nt = paths_json['two_wheeler_nt']
two_wheeler_t = paths_json['two_wheeler_t']
three_wheeler_nt = paths_json['three_wheeler_nt']
three_wheeler_t = paths_json['three_wheeler_t']

# Print basic info
print(f"Product starting letter: {arg_holder[3][0]}")
sys.stdout.flush()

# Set up project output path
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

default_xlsx_path = output_dir / "reportTable.xlsx"
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
xlsx_renamed_path = output_dir / f"{arg_holder[1]}_{timestamp}.xlsx"

# Output and temp paths
temp_path = output_dir / "reportTable.csv"
output_file_path = output_dir / f"{arg_holder[0]}.{arg_holder[1]}.{arg_holder[2]}.{arg_holder[3]}.csv"

# Product-specific UI handling
def product_settings():
    click_something(fuel)
    print("Log: Fuel selected")
    sys.stdout.flush()

    click_something(pure)
    print("Log: Pure EV selected")
    sys.stdout.flush()

    if vehicle_class != "NULL":
        click_something(vehicle_class)
        print(f"Log: Vehicle Class {vehicle_class} clicked")
    else:
        print("Warning: Vehicle Class is NULL, skipped")
    sys.stdout.flush()

    match arg_holder[3][0]:
        case "E":  # E2W
            E2W(two_wheeler_nt, two_wheeler_t)
        case "L":  # L3 or L5
            E3W(three_wheeler_nt, three_wheeler_t)
        case _:
            print("⚠️ Unknown product category. Skipping E2W/E3W specific selection.")
            sys.stdout.flush()

# Main automation flow
open_website()
print("Log: URL opened")
sys.stdout.flush()

select_something(year_field_path, year_path)
time.sleep(short_wait)
print(f"Log: Year {arg_holder[2]} selected")
sys.stdout.flush()

select_something(x_axis_field_path, x_axis_month_path)
time.sleep(short_wait)
print("Log: X-axis Month selected")
sys.stdout.flush()

select_something(y_axis_field_path, y_axis_make_path)
time.sleep(short_wait)
print("Log: Y-axis Make selected")
sys.stdout.flush()

select_something(state_field_path, state_path)
time.sleep(short_wait)
print(f"Log: State {arg_holder[0]} selected")
sys.stdout.flush()

click_something(button_refresh_main)
time.sleep(long_wait)
print("Log: Main refresh (1st) done")
sys.stdout.flush()

select_something(rto_field_path, rto_path)
time.sleep(short_wait)
print(f"Log: RTO {arg_holder[1]} selected")
sys.stdout.flush()

click_something(button_refresh_main)
time.sleep(long_wait)
print("Log: Main refresh (2nd) done")
sys.stdout.flush()

click_something(button_expand)
time.sleep(short_wait)
print("Log: Sidebar expanded")
sys.stdout.flush()

product_settings()
time.sleep(short_wait)

click_something(button_refresh_side)
time.sleep(long_wait)
print("Log: Side refresh done")
sys.stdout.flush()

click_something(button_download)
time.sleep(5)  # Extra wait for file download
print("Log: Download button clicked")
sys.stdout.flush()

# Rename downloaded file
if os.path.exists(default_xlsx_path):
    os.rename(default_xlsx_path, xlsx_renamed_path)
    print(f"Log: File renamed to {xlsx_renamed_path}")
    sys.stdout.flush()
else:
    print("❌ Download failed: reportTable.xlsx not found")
    driver.quit()
    sys.exit(1)

# Process downloaded file
pd_worker = pd.read_excel(xlsx_renamed_path)
pd_worker.to_csv(temp_path, index=False)

# Format and write output
trim = True if arg_holder[4] == "True" else False
year = arg_holder[2]

with open(temp_path, 'r') as data_file:
    rows = list(csv.reader(data_file))
    holder = []

    holder.append(return_header(rows, trim, year))
    number_of_data_rows = len(rows) - 4

    for row in range(1, number_of_data_rows + 1):
        holder.append(return_row(rows, row, trim, arg_holder[3], arg_holder[1], arg_holder[0]))

    with open(output_file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(holder)

    # Also create corresponding Excel file
    pd.DataFrame(holder[1:], columns=holder[0]).to_excel(output_file_path.with_suffix('.xlsx'), index=False)


print(f"✅ Saved processed CSV and Excel at: {output_file_path}")

# Cleanup
os.remove(temp_path)
os.remove(xlsx_renamed_path)

driver.quit()
print("Log: Browser closed and cleanup done")
