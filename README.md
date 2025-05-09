# rto_analysis
A project intended to pull RTO data and analyse them


actions.py
This script automates interactions with the Vahan Parivahan dashboard website using Selenium WebDriver. It opens the specified website and provides functions for selecting and clicking specific elements on the page based on their XPath.

open_website()
Description: Opens the Vahan Parivahan dashboard website and applies an implicit wait.

select_something(XPATH_dropdown_list, XPATH_list_item)
Description: Selects the dropdown list (XPATH_dropdown_list) from a dropdown and then selects list-item (XPATH_list_item)

click_something(XPATH)
Description: Clicks an element specified by its XPath.

E2W(two_wheeler_nt_path, two_wheeler_t_path)
Description: Applies E2W setting on side menu and stdout log

E3W(three_wheeler_nt_path, three_wheeler_t_path)
Description: Applies E3W setting on side menu and stdout log

en_date(list_of_dates, meta_year)
Description: Takes in a list of MMM and YYYY str and returns a list of DD-MM-YYYY. Dependancy for return_header

return_header(rows, trim, year)
Description: Takes in a list of lists (list of rows, row is a list of cells), returns a modified row 4 with formatted dates and added headings. Trims the last month if trim is set to True

return_row(list_of_rows, serial_number, trim, var_ph, rto_ph, state_ph)
Description: Takes in a list of lists (list of rows, row is a list of cells), returns a modifid row (serial_number) with added meta-data as per headings. Trims the last month if trim is set to True


worker.py
Imports arguments via cmd line in the following format: State RTO Year Product Trim_Str_Bool

Downloads file
Creates csv in temp_path
Reads temp_path csv and creates a formatted csv in output (meta-data from args, PLEASE ADD A CHECKER/VALIDATION FROM BROWSER)
Deletes temp_path csv
Deletes downloaded file

orchestrator.py
loan state json on line 25
modify line 31 loop as needed











checker.py


merge_vertical.py
Merges all files in a folder, vertically
New Rows


merge_horizontal.py
Merges all files in a folder, horizontally
New Columns
Can improve this

Create separate program to run the 2nd sweep
Need to implement checks on entered data vs portal data (State, RTO, ETC)



===============================================
How TO

Edit the orchestrator file to select the state, year, product type and trim boolean
Run the orchestrator file

Run checker file and look for missing RTOs

Re run orch until all missing ones have been solved for

Put all files into merger>input and merge them vertically
