from data.fromjira import get_jira_data
from process.pivot import assign_team, parse_datetime,add_adj_done_time,calc_lead_time
import pandas as pd
from datetime import datetime
import argparse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import set_with_dataframe    

def main(args):
    current_date = datetime.now() 
    current_month = args.month
    jira_jql = 'project in (di, com, "Foundations team","DI Analytics Platform", "Last mile optimize") and type not in (epic, subTaskIssueTypes()) and updatedDate > 2024-01-01'

    jira_data = get_jira_data(jira_jql)
    processed_issues = []  # need to process the data from Jira as it is nested
    
    #processed_issues = []  # Initialize an empty list to hold processed issue data
    for issue in jira_data['issues']:
        # Process components
        components = issue['fields'].get('components', [])
        flattened_components = [component['name'] for component in components]
        components_str = ', '.join(flattened_components)  # Join names with comma

        # Process issuetype
        issuetype = issue['fields'].get('issuetype', None)
        issuetype_name = issuetype['name'] if issuetype and 'name' in issuetype else 'Unknown'

        # Extract custom fields
        ImplStart = issue['fields'].get('customfield_12149', 'N/A')
        ImplDone = issue['fields'].get('customfield_12157', 'N/A')
        ImplMerge = issue['fields'].get('customfield_12150', 'N/A')
        ResolutionDate = issue['fields'].get('resolutiondate', 'N/A')
        Status = issue['fields'].get('status', 'N/A')

        # Add processed data to the list
        processed_issues.append({
            'Key': issue['key'],  
            'Issue Type': issuetype_name,
            'Status': Status['name'],
            'ImplStart': ImplStart,
            'ImplDone': ImplDone,
            'ImplMerge': ImplMerge,
            'Components': components_str,
            'ResolutionDate': ResolutionDate,
        })

 
    # Create a DataFrame from the processed issues
    df = pd.DataFrame(processed_issues)
   
    #ignore rows with missing 'ImplStart' values
    df = df.dropna(subset=['ImplStart'])
   
    # Filter out rows with 'Status' for items not yet started
    df = df[~df['Status'].isin(['New', 'Refinement', 'Open', 'Backlog', 'To Do'])]

    # Assign team based on components/project in Jira
    df['Team'] = df.apply(assign_team, axis=1)
    
    #making use of both implDone and resolution date to have a consolidated done time
    df['Adj_Done_Time'] = df.apply(add_adj_done_time, axis=1, year=int(current_date.year), month=int(current_month))

    #calculate the lead time for each entry and getting it to days
    df['lead_time_' + str(current_month)] = df.apply(calc_lead_time, axis=1, year=int(current_date.year), month=int(current_month))
    df['lead_time_' + str(current_month)] = df['lead_time_' + str(current_month)].dt.total_seconds() / 86400
    
    # Create a copy of the DataFrame to get metrics to items completed
    df_done = df.copy()

    # Drop rows where 'Adj_Done_Time' is missing or invalid
    df_done = df_done.dropna(subset=['ImplDone'])

    # Convert 'Adj_Done_Time' using the custom parse_datetime function
    df_done['ImplDone'] = df_done['ImplDone'].apply(parse_datetime)

    # Enforce conversion to datetime
    df_done['ImplDone'] = pd.to_datetime(df_done['ImplDone'], errors='coerce')

    # Filter the DataFrame to include only entries with 'Adj_Done_Time' in the specified month
    df_done = df_done[df_done['ImplDone'].dt.month == current_month]

    pivot_done_count = pd.pivot_table(df_done, values='lead_time_' + str(current_month), index='Team', columns='Issue Type', aggfunc='count')

    #creating the actual pivot tables
    pivot_table_mean = pd.pivot_table(df, values='lead_time_' + str(current_month), index='Team', columns='Issue Type', aggfunc='mean')
    pivot_table_count = pd.pivot_table(df, values='lead_time_' + str(current_month), index='Team', columns='Issue Type', aggfunc='count')
    pivot_table_status_count = pd.pivot_table(df, values='lead_time_' + str(current_month), index='Team', columns='Status', aggfunc='count')
    pivot_table_median = pd.pivot_table(df, values='lead_time_' + str(current_month), index='Team', columns='Issue Type', aggfunc='median')
    pivot_table_mean = pivot_table_mean.drop('Unknown', axis=0)
    pivot_table_median = pivot_table_median.drop('Unknown', axis=0)
    pivot_table_count = pivot_table_count.drop('Unknown', axis=0)
   

    # Google Sheets authentication
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('data/python-int-428111-3d29442d357d.json', scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet (by name or URL)
    spreadsheet = client.open("DI-KPI")
    # Select the first sheet

    # Create a new worksheet
    worksheet_name = 'Month' + str(current_month)

    
    # Function to clear or create worksheet
    def clear_or_create_worksheet(spreadsheet, worksheet_name):
        try:
            # Try to open the worksheet
            worksheet = spreadsheet.worksheet(worksheet_name)
            # Clear the worksheet if it exists
            worksheet.clear()
            print(f'Worksheet "{worksheet_name}" exists. Clearing data...')
        except gspread.exceptions.WorksheetNotFound:
            # Create the worksheet if it does not exist
            worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows="100", cols="20")
            print(f'Worksheet "{worksheet_name}" does not exist. Creating new worksheet...')
        


    # Clear or create the worksheet and add new data
    clear_or_create_worksheet(spreadsheet, worksheet_name)

    worksheet = spreadsheet.worksheet(worksheet_name)

    # Write the pivot table to the Google Sheet
    set_with_dataframe(worksheet, pivot_table_mean.reset_index(), row=1, col=1)

    set_with_dataframe(worksheet, pivot_table_median.reset_index(), row=10, col=1)

    set_with_dataframe(worksheet, pivot_table_count.reset_index(), row=20, col=1)

    set_with_dataframe(worksheet, pivot_done_count.reset_index(), row=30, col=1)
    
    set_with_dataframe(worksheet, pivot_table_status_count.reset_index(), row=40, col=1)

    print("Data successfully written to Google Sheet")

   


    #list items with longest leadtime for each team
    #df_without_done_cancelled = df.loc[~df['Status'].isin(['Done', 'Cancelled'])]
    average_lead_time_per_team = df.groupby('Team')['lead_time_' + str(current_month)].mean()
    print(average_lead_time_per_team)
    
    threshold_lead_time_per_team = average_lead_time_per_team * 1.1

    items_above_threshold = {}
    for team, threshold in threshold_lead_time_per_team.items():
        filtered_items = df[(df['Team'] == team) & (df['lead_time_' + str(current_month)] > threshold)]
        items_above_threshold[team] = filtered_items

    for team, items in items_above_threshold.items():
        print(f"Items for team {team} with lead time > 10% above average:")
        print(items, "\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--month', help='For which month you want to calculate the KPI')
    args = parser.parse_args()
    main(args)