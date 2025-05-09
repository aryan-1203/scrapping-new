import subprocess, json, time, os, pandas as pd

start_time = time.time()

# Output folder path
output_folder_path = 'output/'

# STATES to scrape
states = ["maharashtra", "madhya_pradesh", "rajasthan", "chhattisgarh"]

# YEARS to scrape
years = ["2023", "2024", "2025"]

# PRODUCTS to scrape (added E2W)
products = ["E2W", "L3P", "L3G", "L5P", "L5G"]

# Other settings
trim = "True"
worker_script = "worker.py"

# Master output file path (final Excel file)
master_output_filename = 'output/master_combined.xlsx'

# Track existing files
list_of_existing_files = os.listdir(output_folder_path)

# If master file exists, load it, else create an empty DataFrame
if os.path.exists(master_output_filename):
    master_df = pd.read_excel(master_output_filename)
else:
    master_df = pd.DataFrame()

for state in states:
    print(f"\n==============================")
    print(f"🚀 Starting State: {state.upper()}")
    print(f"==============================")

    # Load RTOs for the state
    with open(f'jsons/{state}_rtos.json', 'r') as file:
        rtos = json.load(file)

    # Scrape each RTO for each year and each product
    for year in years:
        for product in products:
            for rto in rtos:
                check_filename = f"{state}.{rto}.{year}.{product}.csv"
                if check_filename in list_of_existing_files:
                    print(f"✅ Already downloaded: {state} - {rto} - {year} - {product}")
                    continue

                print(f"🚀 Running worker for State: {state}, RTO: {rto}, Year: {year}, Product: {product}")

                try:
                    result = subprocess.run(
                        ["python", worker_script, state, rto, year, product, trim],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )

                    print(result.stdout)
                    if result.stderr:
                        print("⚠️ Error Output:")
                        print(result.stderr)

                except subprocess.CalledProcessError as e:
                    print(f"❌ Failed for {state} - {rto} - {year} - {product}")
                    print(e.output)
                    print(e.stderr)
                    with open("output/error_log.txt", "a") as log_file:
                        log_file.write(f"{state},{rto},{year},{product}\n")
                    continue 

    # After scraping fully done for this state
    print(f"✅ Scraping completed for {state.upper()}!")

    # Append data to master Excel for this state
    for year in years:
        for product in products:
            for file in os.listdir(output_folder_path):
                if file.endswith(".csv") and file.startswith(f"{state}.") and f".{year}.{product}" in file:
                    df = pd.read_csv(os.path.join(output_folder_path, file))
                    master_df = pd.concat([master_df, df], ignore_index=True)

# Save the final master Excel file
if not master_df.empty:
    master_df.to_excel(master_output_filename, index=False)
    print(f"📄 Final Master Excel created: {master_output_filename}")

# Final time report
end_time = time.time()
execution_time = end_time - start_time
minutes = int(execution_time // 60)
seconds = execution_time % 60
print(f"\n⏱️ Total Execution time: {minutes} minutes and {seconds:.2f} seconds")

if os.path.exists("output/error_log.txt"):
    print("\n🔁 Retrying failed jobs...\n")
    with open("output/error_log.txt") as log_file:
        failed_jobs = log_file.readlines()

    os.remove("output/error_log.txt")

    for line in failed_jobs:
        state, rto, year, product = line.strip().split(",")
        try:
            result = subprocess.run(
                ["python", worker_script, state, rto, year, product, trim],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print(result.stdout)
        except Exception as e:
            print(f"❌ Retried and failed again: {state}-{rto}-{year}-{product}")
