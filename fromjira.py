import requests
from requests.auth import HTTPBasicAuth
import data.config


def get_jira_data(jql):
    api_key = data.config.api_key
    api_user = data.config.api_user    
    url = 'https://jira-di.atlassian.net/rest/api/3/search'
    
    all_items = []  # List to collect all items
    start_at = 0  # Initial startAt value
    max_results = 50  #maxResults (can be adjusted based on API limits)
    total = None  # To keep track of total items to fetch
    
    while total is None or start_at < total:
        params = {
            'jql': jql,
            'startAt': start_at,
            'maxResults': max_results,
            'fields': 'key, customfield_12149, customfield_12157, customfield_12150, resolutiondate, components, issuetype, status, priority, created, reporter'
        }

        response = requests.get(url, params=params, auth=(api_user, api_key))
        response_json = response.json()

        if 'issues' in response_json:
            all_items.extend(response_json['issues'])  # Collect items from current page
            
        # Update total, if it's the first response
        if total is None:
            total = response_json.get('total', 0)
            
        # Prepare for the next iteration/page
        start_at += max_results
        
    # Combine all items into one response before returning
    full_response = {'issues': all_items, 'total': total}
   
    return full_response