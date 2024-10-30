import pytest
import datetime
from process.pivot import assign_team, parse_datetime, calc_lead_time

#Test that Publisher is assigned to Media
def test_assign_team_Media_team():
    test_row  = {
        'Issue Type' : 'Story',
        'Issue key': 'DI-12345',
        'Summary' : 'Summary text' ,
        'Components': 'Publisher',
        'Assignee' : 'dummy text',
        'Reporter' : 'dummy text',
        'Priority' : 'dummy text',
        'Status' : 'dummy text',
        'Resolution' : 'dummy text',
        'Updated' : 'dummy text',
        'Custom' :  'dummy text',
        'field (ImplStart)': 'dummy text',
        'Custom field (ImplMerged)': 'dummy text',
        'Custom field (ImplDone)' : 'dummy text',
        'Resolved' :'dummy text',
        'Custom field (Story Points)' : 'dummy text',
        'Project key' : 'dummy text',
        'Custom field (Product Category)' :'dummy text' ,
        'Created' : 'dummy text',
        'Parent' : 'dummy text',
         'summary' : 'dummy text'
    } 
    expected_output = 'Media'
    assert assign_team(test_row) == expected_output

    #Test that Buddy is assigned to Last Mile
def test_assign_team_Buddy_team():
    test_row  = {
        'Issue Type' : 'Story',
        'Issue key': 'DI-12345',
        'Summary' : 'Summary text' ,
        'Components': 'Buddy',
        'Assignee' : 'dummy text',
        'Reporter' : 'dummy text',
        'Priority' : 'dummy text',
        'Status' : 'dummy text',
        'Resolution' : 'dummy text',
        'Updated' : 'dummy text',
        'Custom' :  'dummy text',
        'field (ImplStart)': 'dummy text',
        'Custom field (ImplMerged)': 'dummy text',
        'Custom field (ImplDone)' : 'dummy text',
        'Resolved' :'dummy text',
        'Custom field (Story Points)' : 'dummy text',
        'Project key' : 'dummy text',
        'Custom field (Product Category)' :'dummy text' ,
        'Created' : 'dummy text',
        'Parent' : 'dummy text',
         'summary' : 'dummy text'
    } 
    expected_output = 'Last Mile'
    assert assign_team(test_row) == expected_output

        #Test that DIAP key is assigned to Analytics
def test_assign_team_Analytics_team():
    test_row  = {
        'Issue Type' : 'Story',
        'Issue key': 'DIAP-12345',
        'Summary' : 'Summary text' ,
        'Components': 'Buddy',
        'Assignee' : 'dummy text',
        'Reporter' : 'dummy text',
        'Priority' : 'dummy text',
        'Status' : 'dummy text',
        'Resolution' : 'dummy text',
        'Updated' : 'dummy text',
        'Custom' :  'dummy text',
        'field (ImplStart)': 'dummy text',
        'Custom field (ImplMerged)': 'dummy text',
        'Custom field (ImplDone)' : 'dummy text',
        'Resolved' :'dummy text',
        'Custom field (Story Points)' : 'dummy text',
        'Project key' : 'dummy text',
        'Custom field (Product Category)' :'dummy text' ,
        'Created' : 'dummy text',
        'Parent' : 'dummy text',
         'summary' : 'dummy text'
    } 
    expected_output = 'Analytics'
    assert assign_team(test_row) == expected_output

      #Test that DIAP key is assigned to Commerce
def test_assign_team_Commerce_team():
    test_row  = {
        'Issue Type' : 'Story',
        'Issue key': 'COM-12345',
        'Summary' : 'Summary text' ,
        'Components': 'Buddy',
        'Assignee' : 'dummy text',
        'Reporter' : 'dummy text',
        'Priority' : 'dummy text',
        'Status' : 'dummy text',
        'Resolution' : 'dummy text',
        'Updated' : 'dummy text',
        'Custom' :  'dummy text',
        'field (ImplStart)': 'dummy text',
        'Custom field (ImplMerged)': 'dummy text',
        'Custom field (ImplDone)' : 'dummy text',
        'Resolved' :'dummy text',
        'Custom field (Story Points)' : 'dummy text',
        'Project key' : 'dummy text',
        'Custom field (Product Category)' :'dummy text' ,
        'Created' : 'dummy text',
        'Parent' : 'dummy text',
         'summary' : 'dummy text'
    } 
    expected_output = 'Commerce'
    assert assign_team(test_row) == expected_output

      #Test that DIAP key is assigned to Foundations
def test_assign_team_Foundations_team():
    test_row  = {
        'Issue Type' : 'Story',
        'Issue key': 'FOUN-12345',
        'Summary' : 'Summary text' ,
        'Components': 'Buddy',
        'Assignee' : 'dummy text',
        'Reporter' : 'dummy text',
        'Priority' : 'dummy text',
        'Status' : 'dummy text',
        'Resolution' : 'dummy text',
        'Updated' : 'dummy text',
        'Custom' :  'dummy text',
        'field (ImplStart)': 'dummy text',
        'Custom field (ImplMerged)': 'dummy text',
        'Custom field (ImplDone)' : 'dummy text',
        'Resolved' :'dummy text',
        'Custom field (Story Points)' : 'dummy text',
        'Project key' : 'dummy text',
        'Custom field (Product Category)' :'dummy text' ,
        'Created' : 'dummy text',
        'Parent' : 'dummy text',
         'summary' : 'dummy text'
    } 
    expected_output = 'Foundations'
    assert assign_team(test_row) == expected_output


    #Test of parse_daytime function
def test_parse_daytime_seconds_valid():
    dt_str = "21/12/2021 12:00:00"
    expected_output = datetime.datetime(2021, 12, 21, 12, 0, 0)
    assert parse_datetime(dt_str) == expected_output

def test_parse_daytime_no_seconds_valid():
    dt_str = "21/12/2021 12:00"
    expected_output = datetime.datetime(2021, 12, 21, 12, 0, 0)
    assert parse_datetime(dt_str) == expected_output

def test_calc_lead_time_within_related_month():
    test_row  = {
        'Issue Type' : 'Story',
        'Issue key': 'FOUN-12345',
        'Summary' : 'Summary text' ,
        'Components': 'Buddy',
        'Assignee' : 'dummy text',
        'Reporter' : 'dummy text',
        'Priority' : 'dummy text',
        'Status' : 'dummy text',
        'Resolution' : 'dummy text',
        'Updated' : 'dummy text',
        'Custom field (ImplStart)': '13/05/2024 12:00:00',
        'Custom field (ImplMerged)': 'dummy text',
        'Adj_Done_Time' : '14/05/2024 12:00:00',
        'Resolved' :'dummy text',
        'Custom field (Story Points)' : 'dummy text',
        'Project key' : 'dummy text',
        'Custom field (Product Category)' :'dummy text' ,
        'Created' : 'dummy text',
        'Parent' : 'dummy text',
         'summary' : 'dummy text'
    } 
    year = 2024
    month = 5
    expected_output = datetime.timedelta(days=1)
    assert calc_lead_time(test_row, year, month) == expected_output

def test_calc_lead_time_within_start_before_current_month():
    test_row  = {
        'Issue Type' : 'Story',
        'Issue key': 'FOUN-12345',
        'Summary' : 'Summary text' ,
        'Components': 'Buddy',
        'Assignee' : 'dummy text',
        'Reporter' : 'dummy text',
        'Priority' : 'dummy text',
        'Status' : 'dummy text',
        'Resolution' : 'dummy text',
        'Updated' : 'dummy text',
        'Custom field (ImplStart)': '13/04/2024 12:00:00',
        'Custom field (ImplMerged)': 'dummy text',
        'Adj_Done_Time' : '14/05/2024 12:00:00',
        'Resolved' :'dummy text',
        'Custom field (Story Points)' : 'dummy text',
        'Project key' : 'dummy text',
        'Custom field (Product Category)' :'dummy text' ,
        'Created' : 'dummy text',
        'Parent' : 'dummy text',
         'summary' : 'dummy text'
    } 
    year = 2024
    month = 5
    expected_output = datetime.timedelta(days=1)
    assert calc_lead_time(test_row, year, month) == expected_output
