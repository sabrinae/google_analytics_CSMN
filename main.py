from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta, date
from calendar import monthrange
from decimal import Decimal
import pandas as pd

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = 'daily-csmn-credentials.json'
VIEW_ID = '460....'


def initialize_analyticsreporting():
  """Initializes an Analytics Reporting API V4 service object.

  Returns:
    An authorized Analytics Reporting API V4 service object.
  """
  credentials = ServiceAccountCredentials.from_json_keyfile_name(
      KEY_FILE_LOCATION, SCOPES)

  # Build the service object.
  analytics = build('analyticsreporting', 'v4', credentials=credentials)

  return analytics

def get_report(analytics):
  """Queries the Analytics Reporting API V4.

  Args:
    analytics: An authorized Analytics Reporting API V4 service object.
  Returns:
    The Analytics Reporting API V4 response.
  """

  yesterday = date.strftime(date.today() - timedelta(1),"%Y-%m-%d")
  print('yesterday: ' + yesterday)
  yesterday_obj = datetime.strptime(yesterday, '%Y-%m-%d')
  start_of_month = yesterday_obj.replace(day=1).strftime('%Y-%m-%d')
  start_of_month = str(start_of_month)
  print('start of month: ' + start_of_month)

  return analytics.reports().batchGet(
      body={
        'reportRequests': [
        {
          'viewId': VIEW_ID,
          # this api takes multiple date ranges when submitting get request
          'dateRanges': [{'startDate': yesterday, 'endDate': yesterday},
                         {'startDate': start_of_month, 'endDate': yesterday}],
          'metrics': [{'expression': 'ga:adClicks'},
                      {'expression':'ga:CPC'},
                      {'expression':'ga:metric9'},
                      {'expression':'ga:adCost'}],
          'dimensions': [{'name': 'ga:adwordsCustomerID'}]
        }
        ]
      }
  ).execute()

def print_response(response):
  """
  Args:
    response: An Analytics Reporting API V4 response.
  """
  yesterday = date.strftime(date.today() - timedelta(1),"%Y-%m-%d")
  print('yesterday: ' + yesterday)

  # total number of days in current month
  t = yesterday.split('-')
  numbs = [ int(x) for x in t]
  year = numbs[0]
  month = numbs[1]

  numb_days_in_month = monthrange(year,month)[1]
  print('number of days in month: ' + str(numb_days_in_month))

  # days remaining in month (from "yesterday" variable, not pull date)
  days_left_over = numb_days_in_month - numbs[2]
  print('days left in month: ' + str(days_left_over))

  columns = ['Date','Account Id','Account','Gross Spend','CPC','Clicks','VDPs','VDP Per Click','Cost Per VDP',
             '% of Month','MTD Clicks','MTD Gross Spend','Pacing','MTD VDPs','MTD Cost Per VDP','Monthly Budget','Daily Spend','VDP Goal %','Daily VDP','VDP Goal',
             'Cost Per VDP Goal','Gross Budget','Net Budget']
  csmn_fields = []

  for report in response.get('reports', []):
    print(report)
    for row in report.get('data', {}).get('rows', []):
      ads_id = row.get('dimensions', [])
      ids = ads_id[0]

      # enter location name AND gross / net budgets below
      if '111.......' in ids:
        loc = 'LaCrosse'
        gr_budget = 5500
        cost_per_vdp_goal = .90
      elif '291.......' in ids:
        loc = 'Twin Cities'
        gr_budget = 55000
        cost_per_vdp_goal = .30
      elif '389.......' in ids:
        loc = 'Milwaukee'
        gr_budget = 6000
        cost_per_vdp_goal = .54
      elif '540.......' in ids:
        loc = 'Green Bay'
        gr_budget = 0
        cost_per_vdp_goal = 0.0
      elif '562.......' in ids:
        loc = 'Rochester'
        gr_budget = 6000
        cost_per_vdp_goal = .70
      elif '676.......' in ids:
        loc = 'Duluth'
        gr_budget = 6000
        cost_per_vdp_goal = .85
      elif '737.......' in ids:
        loc = 'Mankato'
        gr_budget = 3000
        cost_per_vdp_goal = 1.0
      elif '982.......' in ids:
        loc = 'Madison'
        gr_budget = 5500
        cost_per_vdp_goal = .50
      elif '552.......' in ids:
        loc = 'Fargo'
        gr_budget = 7000
        cost_per_vdp_goal = .90
      elif '474.......' in ids:
        loc = 'Oklahoma City'
        gr_budget = 8000
        cost_per_vdp_goal = .30
      else:
        loc = 'not set'
        gr_budget = 0.0
        cost_per_vdp_goal = 0.0

      metrics = row.get('metrics',[])
      daily_data = metrics[0]['values']
      monthly_data = metrics[1]['values']
      #print(daily_data)
      #print(monthly_data)

      cost = daily_data[3]
      clicks = daily_data[0]
      cpc = daily_data[1]
      vdp = daily_data[2]

      mtd_vdps = monthly_data[2]
      mtd_clicks = monthly_data[0]
      mtd_cost = monthly_data[3]

      try:
        vdp_per_click = int(vdp)/int(clicks)
        gross_spend = Decimal(str(cost)) / Decimal('0.9')
        mtd_gross_spend = Decimal(str(mtd_cost)) / Decimal('0.9')
        money_per_vdp = Decimal(str(cost))/int(vdp)
        net_budget = Decimal(str(gr_budget)) * Decimal('0.9')
        pacing = Decimal(str(gross_spend)) / Decimal(str(gr_budget)) * 100

        ## ESTIMATE CALCS - NOT VISUALIZED ##
        est_remaining_spend = int(days_left_over) * Decimal(str(gross_spend))
        est_total_spend_at_daily_spend = Decimal(str(gross_spend)) + Decimal(str(est_remaining_spend))
        est_remaining_vdp = int(days_left_over) * int(vdp)
        est_total_vdp_at_current_vdp = int(mtd_vdps) + int(est_remaining_vdp)
        daily_budget = Decimal(str(gr_budget)) / int(numb_days_in_month)
        monthly_progress = (int(numb_days_in_month) - int(days_left_over)) / int(numb_days_in_month) * 100

        ## MTD CALCULATIONS ##
        mtd_cost_per_vdp = (Decimal('1.1111') * Decimal(str(mtd_gross_spend))) / int(mtd_vdps)

        ## PACING CALCULATIONS ##
        monthly_budget = Decimal(str(est_total_spend_at_daily_spend)) / Decimal(str(gr_budget)) * 100
        daily_spend = Decimal(str(gross_spend)) / Decimal(str(daily_budget)) * 100
        vdp_goal = Decimal(str(gr_budget)) / Decimal(str(cost_per_vdp_goal))
        vdp_goal_percent = Decimal(str(est_total_vdp_at_current_vdp)) / Decimal(str(vdp_goal)) * 100
        daily_vdp_goal = Decimal(str(vdp_goal)) / int(numb_days_in_month)
        daily_vdp = int(vdp) / Decimal(str(daily_vdp_goal))

      except ZeroDivisionError:
        print('no divide by zero')
        vdp_per_click = 0 
        gross_spend = 0
        mtd_gross_spend = 0
        money_per_vdp = 0
        net_budget = 0
        pacing = 0

        est_remaining_spend = 0
        est_total_spend_at_daily_spend = 0
        est_remaining_vdp = 0
        est_total_vdp_at_current_vdp = 0
        daily_budget = 0
        monthly_progress = 0

        mtd_cost_per_vdp = 0

        monthly_budget = 0
        daily_spend = 0
        vdp_goal = 0
        vdp_goal_percent = 0
        daily_vdp_goal = 0
        daily_vdp = 0

      csmn_fields.append([yesterday,ids,loc,gross_spend,cpc,clicks,vdp,vdp_per_click,money_per_vdp,
                          monthly_progress,mtd_clicks,mtd_gross_spend,pacing,mtd_vdps,mtd_cost_per_vdp,monthly_budget,daily_spend,vdp_goal_percent,daily_vdp,vdp_goal,
                          cost_per_vdp_goal,gr_budget,net_budget])
      
      csmn_df = pd.DataFrame(csmn_fields,columns=columns)

      #remove rows that are 'not set'
      delete_rows = csmn_df[csmn_df['Account'] == 'not set'].index
      csmn_df.drop(delete_rows, inplace=True)

      csmn_daily_file = csmn_df.to_csv('CSMNDailySpend_' + yesterday + '.csv', index=False)

# create stored procedure to insert record and call it here when connecting with SQL Server

def main():
  analytics = initialize_analyticsreporting()
  response = get_report(analytics)
  print_response(response)

if __name__ == '__main__':
  main()
