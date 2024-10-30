from data.fromjira import get_jira_data
from process.pivot import assign_team, parse_datetime,add_adj_done_time,calc_backlog_time, calc_lead_time
import pandas as pd
from datetime import datetime
import argparse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import set_with_dataframe


def main(args):
    current_date = datetime.now() 
    current_month = args.month
    jira_jql = 'reporter in (6405dab7c6e77744a1de682b,712020:a2a6a113-c613-4e55-aa7c-e88184817789,557058:869e99fd-4380-4a2a-84f4-b364fa0d911d,712020:368eafd5-0553-4b70-bd42-579db4d15b9f,712020:1178947c-fafa-4286-8cc9-641256f66d35,712020:1b2fc4da-a966-4eaa-b2fe-35a0c106dbd1,557058:0c3219cb-ee37-49a8-819a-7c4903fdb1e2) and type in (bug,Systemdrift) and project in (DI,Commerce,"Foundations team","DI Analytics Platform","Last mile optimize") and (status in ("In Progress", "Awaiting input", "Code review","Needs Code Review","Ready for testing","Quality control","Ready for release", Done, Released, Closed) and "ImplStart[Time stamp]" is not EMPTY or (status not in ("In Progress", "Awaiting input", "Code review","Needs Code Review","Ready for testing","Quality control","Ready for release", Done, Released, Closed) and "ImplStart[Time stamp]" is EMPTY)) order BY status ASC'

    jira_data = get_jira_data(jira_jql)
    processed_issues = []  # need to process the data from Jira as it is nested
    
    for issue in jira_data['issues']:
        # Process components
        components = issue['fields'].get('components', [])
        flattened_components = [component['name'] for component in components]
        components_str = ', '.join(flattened_components)  # Join names with comma

        # Process issuetype
        issuetype = issue['fields'].get('issuetype', None)
        issuetype_name = issuetype['name'] if issuetype and 'name' in issuetype else 'Unknown'

        # Process reporter
        reporter = issue['fields'].get('reporter', None)
        reporter_name = reporter['displayName'] if reporter and 'displayName' in reporter else 'Unknown'

        # Extract others fields
        ImplStart = issue['fields'].get('customfield_12149', 'N/A')
        ImplDone = issue['fields'].get('customfield_12157', 'N/A')
        ImplMerge = issue['fields'].get('customfield_12150', 'N/A')
        ResolutionDate = issue['fields'].get('resolutiondate', 'N/A')
        CreatedDate = issue['fields'].get('created', 'N/A')
        Prio = issue['fields'].get('priority', 'N/A')
        Status = issue['fields'].get('status', 'N/A')


        # Add processed data to the list
        processed_issues.append({
            'Key': issue['key'],  
            'Issue Type': issuetype_name,
            'Status': Status['name'],
            'Reporter': reporter_name,
            'Components': components_str,
            'ImplStart': ImplStart,
            'ImplDone': ImplDone,
            'ImplMerge': ImplMerge,
            'ResolutionDate': ResolutionDate,
            'CreatedDate': CreatedDate,
            'Priority': Prio['name'],
        })

    
    df = pd.DataFrame(processed_issues)
    
    df['Team'] = df.apply(assign_team, axis=1)

    df['Adj_Done_Time'] = df.apply(add_adj_done_time, axis=1, year=int(current_date.year), month=int(current_month))

    #calculate backlog time for all rows 
    df['backlog_time_' + str(current_month)] = df.apply(calc_backlog_time, axis=1, year=int(current_date.year), month=int(current_month))
    df['backlog_time_' + str(current_month)] = df['backlog_time_' + str(current_month)].dt.total_seconds() / 86400


    #calculate lead time for all rows 
    df['lead_time_' + str(current_month)] = df.apply(calc_lead_time, axis=1, year=int(current_date.year), month=int(current_month))
    df['lead_time_' + str(current_month)] = df['lead_time_' + str(current_month)].dt.total_seconds() / 86400

    #creating new dataframes for backlog and impl time where other entries are dropped for each
    df_backlog = df.dropna(subset=['backlog_time_' + str(current_month)])
    df_impl = df.dropna(subset=['lead_time_' + str(current_month)])
    
    #create pivot tables for backlog time
    backlog_pivot_table_mean = pd.pivot_table(df_backlog, values='backlog_time_' + str(current_month), index='Team', columns='Issue Type', aggfunc='mean')
    backlog_pivot_table_count = pd.pivot_table(df_backlog, values='backlog_time_' + str(current_month), index='Team', columns='Issue Type', aggfunc='count')
    
    #create pivot tables for impl time
    impl_pivot_table_mean = pd.pivot_table(df_impl, values='lead_time_' + str(current_month), index='Team', columns='Issue Type', aggfunc='mean')
    impl_pivot_table_count = pd.pivot_table(df_impl, values='lead_time_' + str(current_month), index='Team', columns='Issue Type', aggfunc='count')
    
    

    # Google Sheets authentication
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('data/python-int-428111-3d29442d357d.json', scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet (by name or URL)
    spreadsheet = client.open("DI-KPI")
    # Select the first sheet

    # Create a new worksheet
    worksheet_name = 'Support_Month' + str(current_month)

    
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
    set_with_dataframe(worksheet, backlog_pivot_table_mean.reset_index(), row=1, col=1)
    set_with_dataframe(worksheet, backlog_pivot_table_count.reset_index(), row=10, col=1)

    set_with_dataframe(worksheet, impl_pivot_table_mean.reset_index(), row=20, col=1)
    set_with_dataframe(worksheet, impl_pivot_table_count.reset_index(), row=30, col=1)

    set_with_dataframe(worksheet, df.reset_index(), row=40, col=1)

    print("Data successfully written to Google Sheet")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--month', help='For which month you want to calculate the KPI')
    args = parser.parse_args()
    main(args)