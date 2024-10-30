import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
import calendar

 #Define a dictionary that maps component names to team names
component_mapping = {
    'Publisher':                'Media',
    'Buddy':                    'Last Mile A1',
    'Retailer':	                'Media',
    'Distribution Network':	    'Last Mile A2',
    'Plan & Go App':            'Last Mile A1',
    'Last Mile Support':	    'Last Mile A2',
    'Control':	                'Last Mile A2',
    'Plan & Go Dashboard':	    'Last Mile A1',
    'Distribution Insight':	    'Last Mile A2',
    'Payroll':	                'Last Mile A2',
    'Route Optimization':	    'Last Mile A2'
}

team_mapping = {
    'DIAP': 'Analytics',
    'COM-': 'Commerce',
    'FOUN': 'Foundations',
    'LMO-': 'Optimize'
}

def read_csv(file_path):
    return pd.read_csv(file_path)

def assign_team(row):
    components = row['Components'].split(',')
    if row['Key'].startswith('DI-'):
        for comp in components:
            comp = comp.strip()  # Remove any leading/trailing whitespace
            if comp in component_mapping:
                result = component_mapping[comp]
                return result
    
    key_prefix = row['Key'][:4]
    if key_prefix in team_mapping:

        result = team_mapping[key_prefix]
        return result
    else:
        return 'Unknown'

def add_adj_done_time(row, year, month):
    if row['ImplDone']:
        return row['ImplDone']
    else:
        if row['ResolutionDate']:
            return row['ResolutionDate']
        else:
            _, last_day = calendar.monthrange(year, month)
            return datetime(year, month, last_day, tzinfo=ZoneInfo('Europe/Paris')).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        
def parse_datetime(dt_str):
    return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S.%f%z")
   

def calc_lead_time(row, year, month):
    start_date = datetime(year, month, 1, tzinfo=ZoneInfo('Europe/Paris'))
    _, last_day = calendar.monthrange(year, month)
    end_date = datetime(year, month, last_day, tzinfo=ZoneInfo('Europe/Paris'))
    if end_date > datetime.now(tz=ZoneInfo("Europe/Paris")):
        end_date = datetime.now(tz=ZoneInfo("Europe/Paris"))
  
    if row['ImplStart'] and isinstance(row['ImplStart'], str):
        start_event = parse_datetime(row['ImplStart'])
    else:
        return None
    
    if row['Adj_Done_Time'] and isinstance(row['Adj_Done_Time'], str):
        end_event = parse_datetime(row['Adj_Done_Time'])
    else:
        end_event = end_date  # Fallback to the end of the month if not a valid string
     
    
    #actual calculation of lead time for applicable entries within the related month
    if start_event < end_date and end_event > start_date:
        if end_event > end_date:
            
            return end_date - start_event
        else:
            
            return end_event - start_event 
    return None

#used by the support metric script for calculating the backlog time(time from jira item created until moved to in progress)
def calc_backlog_time(row, year, month):
    start_date = datetime(year, month, 1, tzinfo=ZoneInfo('Europe/Paris'))
    _, last_day = calendar.monthrange(year, month)
    end_date = datetime(year, month, last_day, tzinfo=ZoneInfo('Europe/Paris'))
    if end_date > datetime.now(tz=ZoneInfo("Europe/Paris")):
        end_date = datetime.now(tz=ZoneInfo("Europe/Paris"))

    if row['CreatedDate'] and isinstance(row['CreatedDate'], str):
        create_event = parse_datetime(row['CreatedDate'])
 
    else:
        create_event = start_date  # Fallback to the start of the month if not a valid string
        print('!!!!!!!!!!!!!fallback for create_event as CreateDate not present!!!!!!!!!')
        
    
    if row['ImplStart'] and isinstance(row['ImplStart'], str):
        backlog_end_event = parse_datetime(row['ImplStart'])
    
    else:
        if row['ResolutionDate'] and isinstance(row['ResolutionDate'], str):
            backlog_end_event = parse_datetime(row['ResolutionDate'])
            
        else:
            backlog_end_event = end_date
            print('!!!!!! no ImplStart or ResolutionDate, using end_date !!!!!!!')
    

    if create_event < end_date and backlog_end_event > start_date:
        if backlog_end_event > end_date:
            
            return end_date - create_event
        else:
            
            return backlog_end_event - create_event 
    return None  






