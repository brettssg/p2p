# -*- coding: utf-8 -*-
import dash
import dash_table
from dash_table import DataTable
import dash_core_components as dcc
import dash_html_components as html
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Format, Scheme, Sign, Symbol
from collections import OrderedDict
from dash.dependencies import Input, Output
import plotly.subplots as tls
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import urllib
import base64

#import choropleth_geojson as cg
#import plotly.offline as offline

#from io import StringIO

external_stylesheets = ['SSG-base.css']


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#0f2347',
    'background2': '#444',
    'watermelon': '#FF3B3F', 
    'turquoise': '#22b1dc', 
    'charcoal': '#444444',
    'sky1': '#CAEBF2',
    'sky2': '#3399FF',
    'sky': '#1063AD',
    'carbon': '#A9A9A9',
    'neutral1': '#EFEFEF',
    'neutral': '#22B1DC',
    'blackboard': '#565656',
    'text': '#7FDBFF',
    'white':'#FFFFFF'
}

ssg_image_filename = 'ssg_logo.png' # replace with your own image
ssg_encoded_image = base64.b64encode(open(ssg_image_filename, 'rb').read())

cdp_image_filename = 'cdp_logo.png' # replace with your own image
cdp_encoded_image = base64.b64encode(open(cdp_image_filename, 'rb').read())

cerc_image_filename = 'climate-equity-reference2.jpg' # replace with your own image
cerc_encoded_image = base64.b64encode(open(cerc_image_filename, 'rb').read())

P2P_image_filename = 'Pathwaytoparis-Blue-01-01.png' # replace with your own image
p2p_encoded_image = base64.b64encode(open(P2P_image_filename, 'rb').read())

thousand_image_filename = '1000+CITIES+logo+blue.png' # replace with your own image
thousand_encoded_image = base64.b64encode(open(thousand_image_filename, 'rb').read())


# download latest CDP reported emissions data (from https://data.cdp.net/browse?category=Emissions) and save a csv file with subset of rows that contain values for 'Total BASIC Emissions (GPC)'
# download latest CERC projections (from https://calculator.climateequityreference.org/) and save a csv file with the following selections:
# Select a mitigation pathway: 1.5°C Standard ("Greater than or equal to 50% chance of staying below 1.5°C in 2100.
# Historical Responsibility, calculated based on emissions cumulative since: 1990
# Capability to Act, calculated in increasingly economically progressive ways: $7,500 development threshold
# Relative Weight for Historical Responsibility vs Economic Capability to Act: 50% Responsibility and 50% Capability

#CDP csv file
df_city = pd.read_csv('2018_-_2019_City-wide_emissions.csv')
df_city_v2 = pd.read_csv('2018_-_2019_City-wide_emissions_v2.csv')
df_country_v2 = pd.read_csv('2020_cerc_all_output_1579470200_lat_long.csv')


#CERC csv file
df_country = pd.read_csv('cerc_all_output_1579470200.csv')


Metrics = ['Projected emissions', 'Equal share emissions', 'Fair-share emissions', 'City emissions', 'Remaining GHG emissions', 'Remaining GHG emissions per person', 'Years left at current rate'] 
Values = ['Based on continuation of 2016 rate of GHG emissions (from CERC) as population grows',
         'If each country adopted different responsibilities as moderated by their capability to reduce GHG emissions (CERC). Based on responsibility related to emissions since 1990 and the capability to contribute after a $7,500 development threshold for each person',
         'A percentage of the country fair share emissions (from CERC) based on the latest city reported emissions (from CDP)',
         'Remaining emissions to meet the global target with fair-share allocations. After this point some countries will need to produce negative emissions to reach global targets',
         'Remaining emissions per person for the city to meet the global target with fair-share allocations'
         'The number of years left with allowable emissions based on the emssion rate for the last reported year']
  
metrics_series = pd.Series(Metrics) 
values_series = pd.Series(Values) 
  
frame = { 'Category': metrics_series, 'Assumption': values_series } 
  
df_Assumptions = pd.DataFrame(frame) 

available_assumptions = df_Assumptions['Category'].unique()

dict_assumptions = {'Projected emissions':'Projected GHG emissions based on continuation of 2016 rate of GHG emissions (from CERC) as population grows.',
                    'Fair-share emissions':'Projected GHG emissions if each country adopted different responsibilities as moderated by their capability to reduce GHG emissions (from CERC). Based on responsibility related to emissions since 1990 and the capability to contribute after a $7,500 development threshold for each person.',
                    'City emissions':'A percentage of the country fair share emissions (from CERC) based on the latest reported emissions for the city (from CDP).',
                    'Remaining GHG emissions':'Remaining emissions to meet the global target with fair-share allocations. After this point some countries will need to produce negative emissions to reach global targets.',
                    'Remaining GHG emissions per person':'Remaining emissions per person for the city to meet the global target with fair-share allocations.',
                    'Years left at current rate':'The number of years left with allowable emissions based on the emssion rate for the last reported year.'
                    }

# guide the calculations based on a selected city and target year. The start year is assigned as 2020.

df_city.sort_values(by=['Country'], inplace=True)
available_countries = df_city['Country'].unique()

df_FilterCity = df_city[df_city['Country'] == 'Canada']
available_cities = df_FilterCity['City'].unique()

# = df_CountryCity[df_CountryCity['Country'] == selectedCountry]
#available_cities = df_CountryCityFilter['City'].unique()

#available_cities = df_city['City'].unique()
available_end_years = ['2030', '2035', '2040', '2045', '2050']

# get proportion of allocated reduction for the world as a guide to the domestic (or 'fair share') contributions of other countries
dff_world = df_country[df_country['country'] == 'World']

dff_world['total_emission'] = (dff_world.fossil_CO2_MtCO2+dff_world.NonCO2_MtCO2e)
dff_world['percent_domestic'] = (dff_world.allocation_MtCO2/dff_world.total_emission)

WorldTotalEmissionList = dff_world['total_emission'].tolist()
WorldPercentAllocateList = dff_world['percent_domestic'].tolist()

# get the years as a common series for the x-axis
# get the total contribution of the selected country to guide the percentage of domestic (or 'fair share') contribution based on the World allocation
# get the allocated contribution of the country to guide the city's share
dff_selectedCountry = df_country[df_country['country'] == 'Canada']
dff_selectedCountry['total_emission'] = (dff_selectedCountry.fossil_CO2_MtCO2+dff_selectedCountry.NonCO2_MtCO2e)

CountryYearList = dff_selectedCountry['year'].tolist()
CountryTotalEmissionList = dff_selectedCountry['total_emission'].tolist()
CountryTotalAllocationList = dff_selectedCountry['allocation_MtCO2'].tolist()

# create a dataframe that includes the percentage allocation of the world to calculate the domestic (or 'fair share') contribution for the selected country
# include the allocated amount for the country to guide the city's share
df_CountryWorldAllocation = pd.DataFrame(list(zip(CountryYearList, CountryTotalEmissionList, WorldPercentAllocateList, CountryTotalAllocationList)),
              columns=['year', 'total_emission','percent_domestic', 'allocation_MtCO2'])
df_CountryWorldAllocation['country_domestic'] = (df_CountryWorldAllocation.total_emission*df_CountryWorldAllocation.percent_domestic)

# get the latest reported year
dff_city = df_city[df_city['City'] == 'Edmonton']
yearToSelect = dff_city['Year Reported to CDP'].max()

# report this value to the dataframe
df_CountryWorldAllocation['ReportedYear'] = (yearToSelect)

# get the total country allocation for the latest reported year
dff_country2 = dff_selectedCountry[dff_selectedCountry['year'] == yearToSelect]
CountryAllocatedValue = dff_country2['allocation_MtCO2'].max()
CountryTotalEmissionValue = dff_country2['total_emission'].max()


# filter the CDP table for the latest reported year
# get the reported value, population, population year and calculate the rate of carbon use for that combination
dff_city2 = dff_city[dff_city['Year Reported to CDP'] == yearToSelect]
ReportedValue = dff_city2['Total BASIC Emissions (GPC)'].max()
ReportedPopulation = dff_city2['Population'].max()
ReportedPopulationYear = dff_city2['Population Year'].max()
ReportedRate = ReportedValue/ReportedPopulation

# report these values to the dataframe
df_CountryWorldAllocation['ReportedValue'] = (ReportedValue)
df_CountryWorldAllocation['ReportedPopulation'] = (ReportedPopulation)
df_CountryWorldAllocation['ReportedPopulationYear'] = (ReportedPopulationYear)
df_CountryWorldAllocation['ReportedRate'] = (ReportedRate)

# !! remember to state the population year as different to the reported year

# use the city reported value and the country's allocated value to calculate the city percentage of total country emissions
# calculate (and report these values to the dataframe) the City percentage of projected total, allocated and domestic (fair-share) emissions
df_CountryWorldAllocation['CityPercentage'] = (ReportedValue/(CountryTotalEmissionValue*1000000))
df_CountryWorldAllocation['CityAllocatedPortion'] = ((df_CountryWorldAllocation.CityPercentage*df_CountryWorldAllocation.allocation_MtCO2*1000000))
df_CountryWorldAllocation['CityProjectedPortion'] = ((df_CountryWorldAllocation.CityPercentage*df_CountryWorldAllocation.total_emission*1000000))
df_CountryWorldAllocation['CityDomesticPortion'] = ((df_CountryWorldAllocation.CityPercentage*df_CountryWorldAllocation.country_domestic*1000000))

# filter the dataframe on 2020 to guide carbon budget calculations
df_CountryWorldAllocation2 = df_CountryWorldAllocation[df_CountryWorldAllocation['year'] >=2020]

# filter the dataframe on the end year to guide total carbon budget calculations
df_CountryWorldAllocation3 = df_CountryWorldAllocation2[df_CountryWorldAllocation2['year'] <=2050]
CityTotalBudget = df_CountryWorldAllocation3['CityAllocatedPortion'].sum()

# calculate allowable emissions per year based on total budget
AmountPerYearToMeetTarget = CityTotalBudget/(2050-2020)/ReportedPopulation

# filter the dataframe on positive values to guide positive carbon budget calculations
df_CountryWorldAllocation4 = df_CountryWorldAllocation3[df_CountryWorldAllocation2['CityAllocatedPortion'] >0]
CityPositiveBudget = df_CountryWorldAllocation4['CityAllocatedPortion'].sum()

# calculate years left for allowable emissions
YearsLeftofPositiveAtReportedRate = CityPositiveBudget/ReportedValue

#calculate years left for total emissions based on reported rate
YearsLeftTotalAtReportedRate = CityTotalBudget/ReportedValue

# filter the dataframe on negative values to guide negative carbon budget calculations
df_CountryWorldAllocation5 = df_CountryWorldAllocation3[df_CountryWorldAllocation2['CityAllocatedPortion'] <0]
CityNegativeBudget = df_CountryWorldAllocation5['CityAllocatedPortion'].sum()

# report these budget calculations to the dataframe
df_CountryWorldAllocation['CityTotalBudget'] = (CityTotalBudget)
df_CountryWorldAllocation['CityPositiveBudget'] = (CityPositiveBudget)
df_CountryWorldAllocation['CityNegativeBudget'] = (CityNegativeBudget)
df_CountryWorldAllocation['YearsLeftofPositiveAtReportedRate'] = (YearsLeftofPositiveAtReportedRate)
df_CountryWorldAllocation['AmountPerYearToMeetTarget'] = (AmountPerYearToMeetTarget)
df_CountryWorldAllocation['YearsLeftTotalAtReportedRate'] = (YearsLeftTotalAtReportedRate)

Metrics = ['City emissions', 'Remaining positive GHG budget', 'Remaining negative GHG budget', 'Remaining total GHG budget', 'Amount per person per year'] 
Values = [ ReportedValue,  CityPositiveBudget, CityNegativeBudget, CityTotalBudget, AmountPerYearToMeetTarget]
  
metrics_series = pd.Series(Metrics) 
values_series = pd.Series(Values) 
  
frame = { 'GHG Budget till 0 emissions': metrics_series, 'tCO2e': values_series } 
  
df_summary = pd.DataFrame(frame) 
df_summary['tCO2e']=df_summary['tCO2e'].map("{:,.0f}".format)

#Metrics = ['City Population', 'Years left of positive GHG at current rate', 'Years left of total GHG budget at current rate', 'Amount per person per year'] 
Metrics = ['Years left at current rate'] 
Values = [YearsLeftofPositiveAtReportedRate]
  
metrics_series = pd.Series(Metrics) 
values_series = pd.Series(Values) 
  
frame = { 'Time till 0 emissions': metrics_series, 'Years': values_series } 
  
df_summary2 = pd.DataFrame(frame) 
df_summary2['Years']=df_summary2['Years'].map("{:,.0f}".format)


app.layout = html.Div([
    html.Div([
        html.Div(id='Introduction')
    ],style={'height': 24, 'backgroundColor': colors['sky'], 'fontFamily':'Fendrix', 'fontSize': 22, 'padding':12,'color': colors['white'],},
    ),
    html.Div([  
        html.Div([
            dcc.Dropdown(
                id='selectedCountry',
                options=[{'label': i, 'value': i} for i in available_countries],
                value='Canada', 
            )
            ],style={'width': '31%', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='selectedCity',
                options=[{'label': i, 'value': i} for i in available_cities],
                value='Vancouver',
            )
            ],style={'width': '31%', 'float': 'middle', 'display': 'inline-block'}),
         #html.Div([
         #   dcc.Dropdown(
         #       id='endYear',
         #       options=[{'label': i, 'value': i} for i in available_end_years],
         #       value='2050'
         #   )
         #   ],style={'width': '31%', 'float': 'middle', 'display': 'inline-block'})
    ],style={'height': 28, 'backgroundColor': colors['sky'], 'fontFamily':'Fendrix', 'fontSize': 18, 'paddingBottom':8},
    ),
    html.Div([
        html.Div(id='year-summary')
    ],style={'height': 24, 'backgroundColor': colors['sky'], 'fontFamily':'Fendrix', 'fontSize': 18, 'padding':12,'color': colors['white'],},
    ),
    html.Div([
        html.Div([
            html.Div([
                dash_table.DataTable(
                id='summary-table',
                data=df_summary.to_dict('rows'),
                columns=[{'name': i, 'id': i} for i in df_summary.columns],
                style_cell_conditional=[
                {
                    'if': {
                        'column_id': 'GHG Budget till 0 emissions'
                     },
                    'textAlign': 'left'
                },
                {
                    'if': {
                        'column_id': 'tCO2e'
                     },
                    'type': 'numeric',
                    'minWidth': '90px', 'width': '90px', 'maxWidth': '90px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                },
                ],
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ],
                style_header={
                    'backgroundColor': colors['sky'],
                    'fontWeight': 'bold',
                    'color': colors['white']
                },
                )],style={'backgroundColor': colors['neutral']},  
            ),
            html.Div([
                dash_table.DataTable(
                id='summary-table2',
                data=df_summary2.to_dict('rows'),
                columns=[{'name': i, 'id': i} for i in df_summary2.columns],
                style_cell_conditional=[
                {
                    'if': {
                        'column_id': 'Time till 0 emissions'
                     },
                    'textAlign': 'left'
                },
                {
                    'if': {
                        'column_id': 'Years'
                     },
                    'type': 'numeric',
                    'minWidth': '90px', 'width': '90px','maxWidth': '90px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                },
                ],
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ],
                style_header={
                    'backgroundColor': colors['sky'],
                    'fontWeight': 'bold',
                    'color': colors['white']
                }
                )],style={'backgroundColor': colors['neutral'],'paddingTop':0,'paddingBottom':0}, 
            ),
            html.H1(
                children='Assumptions:',
                style={
                    'textAlign': 'left',
                    'color': colors['white'], 
                    'fontSize': 14,
                    'fontFamily':'Courier New',
                    'fontWeight': 'bold',
                    'backgroundColor': colors['sky'],
                    'paddingTop':0,
                    'paddingBottom':0
                }
            ),
            html.Div([
                dcc.Dropdown(
                id='selectedCategory',
                options=[{'label': i, 'value': i} for i in dict_assumptions.keys()],
                value='City emissions'
                )
            ],style={'backgroundColor': colors['sky']}
            ),
             html.Div([
                html.Div(id='Assumptions')
            ],
            style={
                'textAlign': 'left',
                'color': colors['charcoal'], 
                'fontSize': 14,
                'fontFamily':'Courier New',
                'fontWeight': 'normal',
                'backgroundColor': colors['neutral'],
                'paddingTop':5, 
                'paddingBottom':5
            }
            ),
        ], style={'width': '25%', 'float': 'left', 'display': 'inline-block', 'backgroundColor': colors['sky'], 'paddingTop':0, 'paddingBottom':0}
        ),
        html.Div([
            dcc.Graph(id='emissions')
        ], style={'width': '75%', 'float': 'right', 'display': 'inline-block', 'backgroundColor': colors['sky'], 'paddingTop':0, 'paddingBottom':0}
        ),
    ],
    ),
    html.Div([
        html.H1(
            children='Created by:',
            style={
                'textAlign': 'left',
                'color': colors['charcoal'], 
                'fontSize': 15,
                'fontFamily':'Courier New',
                'fontWeight': 'bold',
                'backgroundColor': colors['white'],
                'paddingTop':8, 
                'paddingBottom':5,
                'width': '25%', 
                'float': 'left', 
                'display': 'inline-block', 
                
            }
        ),
    ], 
    ),
    html.Div([
        html.Div(id='P2P-linka'),
        html.A(
            html.Img(src='data:image/png;base64,{}'.format(p2p_encoded_image.decode()),style={'width': '120px'}),
            id='P2P-link',
            #download="rawdata.csv",
            href="https://pathwaytoparis.com/",
            target="_blank",
            )
    ],
    style={
                'textAlign': 'left',
                'color': colors['white'], 
                'fontSize': 14,
                'fontFamily':'Courier New',
                'fontWeight': 'normal',
                'backgroundColor': colors['white'],
                #'paddingTop':10, 
                #'paddingBottom':10,
                'width': '10%', 
                'float': 'left', 
                'display': 'inline-block', 
            }, 
    ),
    html.Div([
        html.Div(id='SSG-linka'),
        html.A(
            html.Img(src='data:image/png;base64,{}'.format(ssg_encoded_image.decode()),style={'width': '210px'}),
            id='SSG-link',
            #download="rawdata.csv",
            href="http://www.ssg.coop/",
            target="_blank",
            )
    ],
    style={
                'textAlign': 'left',
                'color': colors['white'], 
                'fontSize': 14,
                'fontFamily':'Courier New',
                'fontWeight': 'bold',
                'backgroundColor': colors['white'],
                #'paddingTop':10, 
                #'paddingBottom':10,
                'width': '15%', 
                'float': 'left', 
                'display': 'inline-block', 
            }, 
    ),
    html.Div([
        html.Div(id='thousand-linka'),
        html.A(
            html.Img(src='data:image/png;base64,{}'.format(thousand_encoded_image.decode()),style={'width': '170px'}),
            id='thousand-link',
            #download="rawdata.csv",
            href="https://pathwaytoparis.com/1000-cities/",
            target="_blank",
            )
    ],
    style={
                'textAlign': 'left',
                'color': colors['white'], 
                'fontSize': 14,
                'fontFamily':'Courier New',
                'fontWeight': 'bold',
                'backgroundColor': colors['white'],
                #'paddingTop':10, 
                #'paddingBottom':10,
                'width': '15%', 
                'float': 'left', 
                'display': 'inline-block', 
            }, 
    ),
    html.Div([
    html.Div(id='table-a'),
        html.A(
            ' ',
            id='download-link-a',
            #download="rawdata.csv",
            #href="",
            target="_blank",
            style={
                    'textAlign': 'center',
                    'color': colors['white'], 
                    'fontSize': 1,
                    'fontFamily':'Fendrix',
                    'fontWeight': 'bold',
                    'backgroundColor': colors['sky'],
                    'paddingTop':0, 
                    'paddingBottom':0,
                    'width': '100%', 
                    'float': 'middle', 
                    'display': 'inline-block', 
                    'text-decoration':'none',
                },
        )
    ]),
    html.Div([
        html.Div(children='''
            Select a map:
        '''),
    ],style={'width': '100%','height': 24, 'float': 'middle', 'backgroundColor': colors['sky'], 'fontFamily':'Fendrix', 'fontSize': 22, 'padding':6,'color': colors['white'],},
    ),
   
    html.Div([
        dcc.RadioItems(
            id='mapType',
            options=[
                {'label': 'Year to Reach Net Zero', 'value': 'Net Zero'},
                {'label': 'Total Emissions', 'value': 'Country Total'},
                {'label': 'Per Capita Emissions', 'value': 'Country PCC'}
            ],
            value='Country Total',
            labelStyle={'display': 'inline-block', 'float': 'middle'}, 
            style={'width': '100%', 'height': 24, 'backgroundColor': colors['sky'], 'fontFamily':'Fendrix', 'fontSize': 22, 'padding':12,'color': colors['white'],},
        )  
    ]),
    html.Div([
        html.Div(id='MapIntroduction')
    ],style={'width': '100%', 'height': 24, 'backgroundColor': colors['sky'], 'display': 'inline-block', 'float': 'middle', 'textAlign': 'center', 'fontFamily':'Fendrix', 'fontSize': 22, 'padding':12,'color': colors['white'],},
    ),
    #html.Div([
    #    dash_table.DataTable(
    #        id='reporting-table',
    #        columns=[{'name': i, 'id': i} for i in df_CountryWorldAllocation.columns],
    #    )
    #]),
    html.Div([
        dcc.Graph(id='map')
        ], style={'width': '95%', 'float': 'left', 'display': 'inline-block', 'backgroundColor': colors['white'], 'paddingTop':0, 'paddingBottom':0}
        ),
        html.Div([
            dcc.Graph(id='legend')
        ], style={'width': '5%', 'float': 'right', 'display': 'inline-block', 'backgroundColor': colors['white'], 'paddingTop':0, 'paddingBottom':0}
    ),
    html.Div([
    html.Div(id='table'),
        html.A(
            'Download Data',
            id='download-link',
            download="rawdata.csv",
            href="",
            target="_blank",
            style={
                    'textAlign': 'center',
                    'color': colors['white'], 
                    'fontSize': 18,
                    'fontFamily':'Fendrix',
                    'fontWeight': 'bold',
                    'backgroundColor': colors['sky'],
                    'paddingTop':20, 
                    'paddingBottom':20,
                    'width': '100%', 
                    'float': 'middle', 
                    'display': 'inline-block', 
                    'text-decoration':'none',
                },
        )
    ]),
    html.Div([
    html.Div(id='cerc-linka'),
        html.A(
            'GHG emission projections from Climate Equity Reference Calculator',
            id='cerc-link',
            download="rawdata.csv",
            href="https://calculator.climateequityreference.org/",
            target="_blank",
            style={
                    'textAlign': 'center',
                    'text-decoration': 'none',
                    'color': colors['charcoal'], 
                    'fontSize': 18,
                    'fontFamily':'Fendrix',
                    'fontWeight': 'bold',
                    'backgroundColor': colors['white'],
                    'paddingTop':10, 
                    'paddingBottom':10,
                    'width': '100%', 
                    'float': 'middle', 
                    'display': 'inline-block', 
                    'text-decoration':'none',
                },
        )
    ]),
    html.Div([
    html.Div(id='cdp-linka'),
        html.A(
            'City self-reporting from CDP',
            id='cdp-link',
            download="rawdata.csv",
            href="https://www.cdp.net/en",
            target="_blank",
            style={
                    'textAlign': 'center',
                    'color': colors['charcoal'], 
                    'fontSize': 18,
                    'fontFamily':'Fendrix',
                    'fontWeight': 'bold',
                    'backgroundColor': colors['white'],
                    'paddingTop':10, 
                    'paddingBottom':10,
                    'width': '100%', 
                    'float': 'middle', 
                    'display': 'inline-block', 
                    'text-decoration':'none',
                },
        )
    ]),
],style={'backgroundColor': colors['white']})

def create_time_series(dff, title):
    return {
        'data': [dict(
            x=dff['year'],
            y=dff['CityProjectedPortion'],
            type='line',
            name='Projected emissions',
            mode='lines+markers'
        ),
        dict(
            x=dff['year'],
            y=dff['CityDomesticPortion'],
            type='line',
            name='Equal share emissions',
            mode='lines+markers'
        ),
        dict(
            x=dff['year'],
            y=dff['CityAllocatedPortion'],
            type='line',
            name='Fair share emissions',
            mode='lines+markers'
        )],
        'layout': {
            'height': 400,
            'margin': {'l': 10, 'b': 30, 'r': 10, 't': 40},
            'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': title
            }],
            'yaxis': {'type': 'linear'},
            'xaxis': {'showgrid': False}
        }
    }


@app.callback(
    Output('selectedCity', 'options'),
    [Input('selectedCountry', 'value')])
def set_cities_options(selectedCountry):
    df_FilterCity = df_city[df_city['Country'] == selectedCountry]
    df_FilterCity.sort_values(by=['City'], inplace=True)
    available_cities = df_FilterCity['City'].unique()
    return [{'label': i, 'value': i} for i in available_cities]


@app.callback(Output('Introduction', 'children'),
              [Input('selectedCountry', 'value')])

def update_text(selectedCountry):

    return u'''
        Select a country and city to calculate the future GHG emission budget:
    '''.format(yearToSelect, ReportedPopulation, ReportedPopulationYear)

@app.callback(Output('Assumptions', 'children'),
              [Input('selectedCategory', 'value')])

def update_text(selectedCategory):
    dff_Assumptions = df_Assumptions[df_Assumptions['Category'] == selectedCategory]
    dff_Assumptions['Assumption'] = dff_Assumptions['Assumption'].astype(str)
    theText = dff_Assumptions['Assumption']
    theTextAsString = str(theText)
    mystring = repr(theText)
    
    mystring = dict_assumptions[selectedCategory]
    
    return u'''
        {}
    '''.format(mystring)
    
@app.callback(Output('year-summary', 'children'),
              [Input('selectedCountry', 'value'), Input ('selectedCity', 'value')])

def update_text(selectedCountry, selectedCity):
    endYearFloat = float(2050)

    # get proportion of allocated reduction for the world as a guide to the domestic (or 'fair share') contributions of other countries
    dff_world = df_country[df_country['country'] == 'World']

    dff_world['total_emission'] = (dff_world.fossil_CO2_MtCO2+dff_world.NonCO2_MtCO2e)
    dff_world['percent_domestic'] = (dff_world.allocation_MtCO2/dff_world.total_emission)

    WorldTotalEmissionList = dff_world['total_emission'].tolist()
    WorldPercentAllocateList = dff_world['percent_domestic'].tolist()

    # get the years as a common series for the x-axis
    # get the total contribution of the selected country to guide the percentage of domestic (or 'fair share') contribution based on the World allocation
    # get the allocated contribution of the country to guide the city's share
    dff_selectedCountry = df_country[df_country['country'] == selectedCountry]
    dff_selectedCountry['total_emission'] = (dff_selectedCountry.fossil_CO2_MtCO2+dff_selectedCountry.NonCO2_MtCO2e)

    CountryYearList = dff_selectedCountry['year'].tolist()
    CountryTotalEmissionList = dff_selectedCountry['total_emission'].tolist()
    CountryTotalAllocationList = dff_selectedCountry['allocation_MtCO2'].tolist()

    # create a dataframe that includes the percentage allocation of the world to calculate the domestic (or 'fair share') contribution for the selected country
    # include the allocated amount for the country to guide the city's share
    df_CountryWorldAllocation = pd.DataFrame(list(zip(CountryYearList, CountryTotalEmissionList, WorldPercentAllocateList, CountryTotalAllocationList)),
                  columns=['year', 'total_emission','percent_domestic', 'allocation_MtCO2'])
    df_CountryWorldAllocation['country_domestic'] = (df_CountryWorldAllocation.total_emission*df_CountryWorldAllocation.percent_domestic)

    # get the latest reported year
    dff_city = df_city[df_city['City'] == selectedCity]
    yearToSelect = dff_city['Year Reported to CDP'].max()

    # report this value to the dataframe
    df_CountryWorldAllocation['ReportedYear'] = (yearToSelect)

    # get the total country allocation for the latest reported year
    dff_country2 = dff_selectedCountry[dff_selectedCountry['year'] == yearToSelect]
    CountryAllocatedValue = dff_country2['allocation_MtCO2'].max()
    CountryTotalEmissionValue = dff_country2['total_emission'].max()


    # filter the CDP table for the latest reported year
    # get the reported value, population, population year and calculate the rate of carbon use for that combination
    dff_city2 = dff_city[dff_city['Year Reported to CDP'] == yearToSelect]
    ReportedValue = dff_city2['Total BASIC Emissions (GPC)'].max()
    IntReportedValue = int(ReportedValue)
    ReportedPopulation = dff_city2['Population'].max()
    IntReportedPopulation = int(ReportedPopulation)
    ReportedPopulationYear = dff_city2['Population Year'].max()
    ReportedRate = ReportedValue/ReportedPopulation
    
    ProperReportedValue = '{:,}'.format(IntReportedValue)
    ProperReportedPopulation = '{:,}'.format(IntReportedPopulation)
    
        # report these values to the dataframe
    df_CountryWorldAllocation['ReportedValue'] = (ReportedValue)
    df_CountryWorldAllocation['ReportedPopulation'] = (ReportedPopulation)
    df_CountryWorldAllocation['ReportedPopulationYear'] = (ReportedPopulationYear)
    df_CountryWorldAllocation['ReportedRate'] = (ReportedRate)

    # !! remember to state the population year as different to the reported Time
    

    # use the city reported value and the country's allocated value to calculate the city percentage of total country emissions
    # calculate (and report these values to the dataframe) the City percentage of projected total, allocated and domestic (fair-share) emissions
    df_CountryWorldAllocation['CityPercentage'] = (ReportedValue/(CountryTotalEmissionValue*1000000))
    df_CountryWorldAllocation['CityAllocatedPortion'] = ((df_CountryWorldAllocation.CityPercentage*df_CountryWorldAllocation.allocation_MtCO2*1000000))
    df_CountryWorldAllocation['CityProjectedPortion'] = ((df_CountryWorldAllocation.CityPercentage*df_CountryWorldAllocation.total_emission*1000000))
    df_CountryWorldAllocation['CityDomesticPortion'] = ((df_CountryWorldAllocation.CityPercentage*df_CountryWorldAllocation.country_domestic*1000000))
    
    # filter the dataframe on 2020 to guide carbon budget calculations
    df_CountryWorldAllocation2 = df_CountryWorldAllocation[df_CountryWorldAllocation['year'] >=2020]

    # filter the dataframe on the end year to guide total carbon budget calculations
    df_CountryWorldAllocation3 = df_CountryWorldAllocation2[df_CountryWorldAllocation2['year'] <= endYearFloat]
    CityTotalBudget = df_CountryWorldAllocation3['CityAllocatedPortion'].sum()


    
    # calculate allowable emissions per year based on total budget
    AmountPerYearToMeetTarget = CityTotalBudget/(endYearFloat -2020)/ReportedPopulation

    # filter the dataframe on positive values to guide positive carbon budget calculations
    df_CountryWorldAllocation4 = df_CountryWorldAllocation3[df_CountryWorldAllocation2['CityAllocatedPortion'] >0]
    CityPositiveBudget = df_CountryWorldAllocation4['CityAllocatedPortion'].sum()
    
    IntCityPositiveBudget = int(CityPositiveBudget)
    ProperCityPositiveBudget = '{:,}'.format(IntCityPositiveBudget)

    # calculate allowable emissions per person based on total budget
    AmountPerPerson = CityPositiveBudget/ReportedPopulation
    IntAmountPerPerson = int(AmountPerPerson)
    ProperAmountPerPerson = '{:,}'.format(IntAmountPerPerson)

    # calculate years left for allowable emissions
    YearsLeftofPositiveAtReportedRate = CityPositiveBudget/ReportedValue
    IntYearsLeftofPositiveAtReportedRate = int(YearsLeftofPositiveAtReportedRate)
    ProperYearsLeftofPositiveAtReportedRate = '{:,}'.format(IntYearsLeftofPositiveAtReportedRate)

    #calculate years left for total emissions based on reported rate
    YearsLeftTotalAtReportedRate = CityTotalBudget/ReportedValue

    # filter the dataframe on negative values to guide negative carbon budget calculations
    df_CountryWorldAllocation5 = df_CountryWorldAllocation3[df_CountryWorldAllocation2['CityAllocatedPortion'] <0]
    CityNegativeBudget = df_CountryWorldAllocation5['CityAllocatedPortion'].sum()

    return u'''
        The reported GHG emissions for {} are {} tCO2e. 
        The reported population for {} is {}.
    '''.format(yearToSelect,ProperReportedValue, ReportedPopulationYear, ProperReportedPopulation)

@app.callback(
    Output(component_id='emissions', component_property='figure'),
    [Input('selectedCountry', 'value'), Input('selectedCity', 'value')])
 
def update_graph(selectedCountry, selectedCity):
    
    endYearFloat= float(2050)
    
    # get proportion of allocated reduction for the world as a guide to the domestic (or 'fair share') contributions of other countries
    dff_world = df_country[df_country['country'] == 'World']

    dff_world['total_emission'] = (dff_world.fossil_CO2_MtCO2+dff_world.NonCO2_MtCO2e)
    dff_world['percent_domestic'] = (dff_world.allocation_MtCO2/dff_world.total_emission)

    WorldTotalEmissionList = dff_world['total_emission'].tolist()
    WorldPercentAllocateList = dff_world['percent_domestic'].tolist()

    # get the years as a common series for the x-axis
    # get the total contribution of the selected country to guide the percentage of domestic (or 'fair share') contribution based on the World allocation
    # get the allocated contribution of the country to guide the city's share
    dff_selectedCountry = df_country[df_country['country'] == selectedCountry]
    dff_selectedCountry['total_emission'] = (dff_selectedCountry.fossil_CO2_MtCO2+dff_selectedCountry.NonCO2_MtCO2e)

    CountryYearList = dff_selectedCountry['year'].tolist()
    CountryTotalEmissionList = dff_selectedCountry['total_emission'].tolist()
    CountryTotalAllocationList = dff_selectedCountry['allocation_MtCO2'].tolist()

    # create a dataframe that includes the percentage allocation of the world to calculate the domestic (or 'fair share') contribution for the selected country
    # include the allocated amount for the country to guide the city's share
    df_CountryWorldAllocation = pd.DataFrame(list(zip(CountryYearList, CountryTotalEmissionList, WorldPercentAllocateList, CountryTotalAllocationList)),
                  columns=['year', 'total_emission','percent_domestic', 'allocation_MtCO2'])
    df_CountryWorldAllocation['country_domestic'] = (df_CountryWorldAllocation.total_emission*df_CountryWorldAllocation.percent_domestic)

    # get the latest reported year
    dff_city = df_city[df_city['City'] == selectedCity]
    yearToSelect = dff_city['Year Reported to CDP'].max()

    # report this value to the dataframe
    df_CountryWorldAllocation['ReportedYear'] = (yearToSelect)

    # get the total country allocation for the latest reported year
    dff_country2 = dff_selectedCountry[dff_selectedCountry['year'] == yearToSelect]
    CountryAllocatedValue = dff_country2['allocation_MtCO2'].max()
    CountryTotalEmissionValue = dff_country2['total_emission'].max()


    # filter the CDP table for the latest reported year
    # get the reported value, population, population year and calculate the rate of carbon use for that combination
    dff_city2 = dff_city[dff_city['Year Reported to CDP'] == yearToSelect]
    ReportedValue = dff_city2['Total BASIC Emissions (GPC)'].max()
    ReportedPopulation = dff_city2['Population'].max()
    ReportedPopulationYear = dff_city2['Population Year'].max()
    ReportedRate = ReportedValue/ReportedPopulation

    # report these values to the dataframe
    df_CountryWorldAllocation['ReportedValue'] = (ReportedValue)
    df_CountryWorldAllocation['ReportedPopulation'] = (ReportedPopulation)
    df_CountryWorldAllocation['ReportedPopulationYear'] = (ReportedPopulationYear)
    df_CountryWorldAllocation['ReportedRate'] = (ReportedRate)

    # !! remember to state the population year as different to the reported year

    # use the city reported value and the country's allocated value to calculate the city percentage of total country emissions
    # calculate (and report these values to the dataframe) the City percentage of projected total, allocated and domestic (fair-share) emissions
    df_CountryWorldAllocation['CityPercentage'] = (ReportedValue/(CountryTotalEmissionValue*1000000))
    df_CountryWorldAllocation['CityAllocatedPortion'] = ((df_CountryWorldAllocation.CityPercentage*df_CountryWorldAllocation.allocation_MtCO2*1000000))
    df_CountryWorldAllocation['CityProjectedPortion'] = ((df_CountryWorldAllocation.CityPercentage*df_CountryWorldAllocation.total_emission*1000000))
    df_CountryWorldAllocation['CityDomesticPortion'] = ((df_CountryWorldAllocation.CityPercentage*df_CountryWorldAllocation.country_domestic*1000000))

    
    #return fig
    title = 'Two emission pathways for ' + selectedCity +', ' + selectedCountry
    #selected = all_options[df_CountryWorldAllocation]

    return {
        'data': [dict(
            x=df_CountryWorldAllocation['year'],
            y=df_CountryWorldAllocation['CityProjectedPortion'],
            type='line',
            name='Projected emissions',
            mode='lines'
        ),
        #dict(
        #    x=df_CountryWorldAllocation['year'],
        #    y=df_CountryWorldAllocation['CityDomesticPortion'],
        #    type='line',
        #    name='Equal share emissions',
        #    mode='lines'
        #),
        dict(
            x=df_CountryWorldAllocation['year'],
            y=df_CountryWorldAllocation['CityAllocatedPortion'],
            type='line',
            name='Fair share emissions',
            mode='lines',
            color='royalblue', width=4, dash='dash',
        )],
        'layout': {
            'height': 500,
            'margin': {'l': 20, 'b': 30, 'r': 10, 't': 40},
            'annotations': [{
                'x': 0, 'y': 0, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': title
            }],
            'yaxis': {'type': 'linear'},
            'xaxis': {'showgrid': False}
        }
    }

@app.callback(
    Output(component_id='map', component_property='figure'),
    [Input('selectedCountry', 'value'), Input('selectedCity', 'value'), Input('mapType', 'value')])
 
def update_graph(selectedCountry, selectedCity, mapType):
    
    if mapType =='Net Zero':
        fig = px.scatter_mapbox(df_city_v2, lat="lat", lon="lon", hover_name="City", hover_data=["Year to reach net zero", "City total emissions (t)", "City per capita emissions (t)"],
                            color_discrete_sequence=["grey"], zoom=3, height=300)
        #fig = px.scatter_mapbox(df_country_v2, lat="lat", lon="lon", hover_name="Country", hover_data=["Country Total Emissions 2020 (tonnes)", "Country PCC Emissions 2020 (tonnes)"],
        #                    color_discrete_sequence=["turquoise"], zoom=3, height=300)
        fig.update_layout(mapbox_style="mapbox://styles/bletch42/ck9d5u0r50ydj1ip74so6v75e", mapbox_accesstoken='pk.eyJ1IjoiYmxldGNoNDIiLCJhIjoiY2s3Ymo3bWY4MDM1ZjNscnlkb2MxcG1nZCJ9.LnjSNVWMM-v3x9juFVoZgg')
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height = 600)       
        fig.update_layout(mapbox=dict(center=dict(lat=38.92, lon=-77.07), zoom=3), hoverlabel=dict(bgcolor="white", font_size=18, font_family="Futura",namelength = -1))
    elif mapType =='Country Total':
        fig = px.scatter_mapbox(df_city_v2, lat="lat", lon="lon", hover_name="City", hover_data=["Year to reach net zero", "City total emissions (t)", "Country total emissions 2020 (t)"],
                            color_discrete_sequence=["grey"], zoom=3, height=300)
        #fig = px.scatter_mapbox(df_country_v2, lat="lat", lon="lon", hover_name="Country", hover_data=["Country Total Emissions 2020 (tonnes)", "Country PCC Emissions 2020 (tonnes)"],
        #                    color_discrete_sequence=["turquoise"], zoom=3, height=300)
        fig.update_layout(mapbox_style="mapbox://styles/bletch42/ck98x6x2y066g1itc0m6j8n2p", mapbox_accesstoken='pk.eyJ1IjoiYmxldGNoNDIiLCJhIjoiY2s3Ymo3bWY4MDM1ZjNscnlkb2MxcG1nZCJ9.LnjSNVWMM-v3x9juFVoZgg')
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height = 600)       
        fig.update_layout(mapbox=dict(center=dict(lat=38.92, lon=-77.07), zoom=3), hoverlabel=dict(bgcolor="white", font_size=18, font_family="Futura",namelength = -1))
    else:
        fig = px.scatter_mapbox(df_city_v2, lat="lat", lon="lon", hover_name="City", hover_data=["Year to reach net zero", "City per capita emissions (t)", "Country per capita emissions 2020 (t)"],
                            color_discrete_sequence=["grey"], zoom=3, height=300)
        #fig = px.scatter_mapbox(df_country_v2, lat="lat", lon="lon", hover_name="Country", hover_data=["Country Total Emissions 2020 (tonnes)", "Country PCC Emissions 2020 (tonnes)"],
        #                  color_discrete_sequence=["turquoise"], zoom=3, height=300)
        fig.update_layout(mapbox_style="mapbox://styles/bletch42/ck9aequak027o1iqqp2at7eb3", mapbox_accesstoken='pk.eyJ1IjoiYmxldGNoNDIiLCJhIjoiY2s3Ymo3bWY4MDM1ZjNscnlkb2MxcG1nZCJ9.LnjSNVWMM-v3x9juFVoZgg')
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height = 600)
        fig.update_layout(mapbox=dict(center=dict(lat=38.92, lon=-77.07), zoom=3), hoverlabel=dict(bgcolor="white", font_size=18, font_family="Futura",namelength = -1))

    #fig.update_layout(mapbox_tyle="carto-positron",
    #              mapbox_zoom=3, mapbox_center = {"lat": 37.0902, "lon": -95.7129})
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    
    #fig.show()
    return fig


@app.callback(Output('MapIntroduction', 'children'),
              [Input('mapType', 'value')])

def update_text(mapType):
    if mapType =='Net Zero':
        return u'''
           COUNTRY AND CITY TIMELINE TO REACH NET ZERO EMISSIONS IN ORDER TO MEET THE PARIS AGREEMENT (limiting global temperature rise to 1.5).
        '''.format(yearToSelect, ReportedPopulation, ReportedPopulationYear)
    elif mapType =='Country Total':
        return u'''
            COUNTRY AND CITY CURRENT TOTAL EMISSIONS (in megatonnes).
        '''.format(yearToSelect, ReportedPopulation, ReportedPopulationYear)
    else: 
        return u'''
            COUNTRY AND CITY CURRENT PER CAPITA EMISSIONS (in tonnes).
        '''.format(yearToSelect, ReportedPopulation, ReportedPopulationYear)
@app.callback(
    Output(component_id='legend', component_property='figure'),
    [Input('selectedCountry', 'value'), Input('selectedCity', 'value'), Input('mapType', 'value')])
 
def update_graph(selectedCountry, selectedCity, mapType):
    
    if mapType =='Net Zero':
        fig = go.Figure()

        fig.add_trace(go.Heatmap(
            z=[[2020],
               [2025],
               [2030], 
               [2035],
               [2040], 
               [2045],
               [2050]],
            
            x=['Target Year'],
            y=["2020", "2025", "2030", "2035", "2040","2045","2050"],
            hoverinfo='none',
            
            colorscale=[
                # Let first 10% (0.1) of the values have color rgb(0, 0, 0)
                [0, "rgb(18, 43, 165)"],
                [0.2, "rgb(38, 161, 232)"],
                [0.4, "rgb(146, 218, 222)"],
                [0.5, "rgb(226, 152, 24)"],
                [0.6, "rgb(191, 59, 114)"],
                [0.8, "rgb(122, 6, 116)"],

                # Let values between 10-20% of the min and max of z
                # have color rgb(20, 20, 20)
                [1, "rgb(174, 9, 9)"]
                ],
                colorbar=dict(
                    title="Target Year",
                    titleside="top",
                    tickmode="array",
                    tickvals=[0, 0.2, 0.4, 0.5, 0.6, 0.8, 1],
                    ticktext=["2020", "2025", "2030", "2035", "2040","2045","2050"],
                    ticks="outside"
                )
            ))
        fig.update_layout(margin={"r":0,"t":4,"l":0,"b":4}, width = 90, height = 600)
    elif mapType =='Country Total':
        fig = go.Figure()

        fig.add_trace(go.Heatmap(
            z=[[0],
               [8.8],
               [38.0],
               [119.4], 
               [416.6],
               [734.9], 
               [3569.7],
               [14998.7]],
            
            x=['MTonnes'],
            y=["0", "9", "38", "119", "417", "735", "3570", "10000", "14998"],
            hoverinfo='none',
            
            colorscale=[
                # Let first 10% (0.1) of the values have color rgb(0, 0, 0)
                [0, "rgb(221, 182, 226)"],

                # Let values between 10-20% of the min and max of z
                # have color rgb(20, 20, 20)
                [1, "rgb(82, 4, 113)"]
                ],
                colorbar=dict(
                    title="MTonnes",
                    titleside="top",
                    tickmode="array",
                    tickvals=[0, 9, 38, 119, 417, 735, 2000, 3000, 3570, 14998],
                    ticktext=["0", "9", "38", "119", "417", "735", "3570", "14998"],
                    ticks="outside"
                )
            ))
        fig.update_layout(margin={"r":0,"t":4,"l":0,"b":4}, width = 90, height = 600)
    else:
        fig = go.Figure()

        fig.add_trace(go.Heatmap(
             z=[[0],
               [2.1],
               [4.5],
               [8.4], 
               [14.2],
               [19.6], 
               [37.0],
               [71.0]],
            
            x=['tonnes'],
            y=["0", "2.1", "4.5", "8.4", "14.2", "19.6", "37", "50", "71"],
            hoverinfo='none',
            
            colorscale=[
                # Let first 10% (0.1) of the values have color rgb(0, 0, 0)
                [0, "rgb(181,226,253)"],

                # Let values between 10-20% of the min and max of z
                # have color rgb(20, 20, 20)
                [1, "rgb(8,18,166)"]
                ],
                colorbar=dict(
                    title="Tonnes",
                    titleside="top",
                    tickmode="array",
                    tickvals=[4.5, 8.4, 14.2, 19.6, 37.0, 71.0],
                    ticktext=["50th", "75th", "90th", "95th", "99th","100th"],
                    ticks="outside"
                )
            ))
        fig.update_layout(margin={"r":0,"t":4,"l":0,"b":4}, width = 90, height = 600)

    #fig.update_layout(mapbox_tyle="carto-positron",
    #              mapbox_zoom=3, mapbox_center = {"lat": 37.0902, "lon": -95.7129})
    fig.update_layout(margin={"r":10,"t":10,"l":0,"b":10})
    
    
    #fig.show()
    return fig
    
def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

#@app.callback(dash.dependencies.Output('table', 'children'),[Input ('selectedCountry', 'value')])
#def update_table(filter_value):

#return generate_table(df_CityPlot)
@app.callback(dash.dependencies.Output('download-link', 'href'))

def update_download_link():
    csv_string = df_CityPlot.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.quote(csv_string)
    return csv_string

@app.callback(
    Output('summary-table', 'data'),
    [Input ('selectedCountry', 'value'), Input ('selectedCity', 'value')])
def update_table(selectedCountry, selectedCity):
    endYearFloat= float(2050)
    
    # get proportion of allocated reduction for the world as a guide to the domestic (or 'fair share') contributions of other countries
    dff_world = df_country[df_country['country'] == 'World']

    dff_world['total_emission'] = (dff_world.fossil_CO2_MtCO2+dff_world.NonCO2_MtCO2e)
    dff_world['percent_domestic'] = (dff_world.allocation_MtCO2/dff_world.total_emission)

    WorldTotalEmissionList = dff_world['total_emission'].tolist()
    WorldPercentAllocateList = dff_world['percent_domestic'].tolist()

    # get the years as a common series for the x-axis
    # get the total contribution of the selected country to guide the percentage of domestic (or 'fair share') contribution based on the World allocation
    # get the allocated contribution of the country to guide the city's share
    dff_selectedCountry = df_country[df_country['country'] == selectedCountry]
    dff_selectedCountry['total_emission'] = (dff_selectedCountry.fossil_CO2_MtCO2+dff_selectedCountry.NonCO2_MtCO2e)

    CountryYearList = dff_selectedCountry['year'].tolist()
    CountryTotalEmissionList = dff_selectedCountry['total_emission'].tolist()
    CountryTotalAllocationList = dff_selectedCountry['allocation_MtCO2'].tolist()

    # create a dataframe that includes the percentage allocation of the world to calculate the domestic (or 'fair share') contribution for the selected country
    # include the allocated amount for the country to guide the city's share
    df_CountryWorldAllocation = pd.DataFrame(list(zip(CountryYearList, CountryTotalEmissionList, WorldPercentAllocateList, CountryTotalAllocationList)),
                  columns=['year', 'total_emission','percent_domestic', 'allocation_MtCO2'])
    df_CountryWorldAllocation['country_domestic'] = (df_CountryWorldAllocation.total_emission*df_CountryWorldAllocation.percent_domestic)

    # get the latest reported year
    dff_city = df_city[df_city['City'] == selectedCity]
    yearToSelect = dff_city['Year Reported to CDP'].max()

    # report this value to the dataframe
    df_CountryWorldAllocation['ReportedYear'] = (yearToSelect)

    # get the total country allocation for the latest reported year
    dff_country2 = dff_selectedCountry[dff_selectedCountry['year'] == yearToSelect]
    CountryAllocatedValue = dff_country2['allocation_MtCO2'].max()
    CountryTotalEmissionValue = dff_country2['total_emission'].max()


    # filter the CDP table for the latest reported year
    # get the reported value, population, population year and calculate the rate of carbon use for that combination
    dff_city2 = dff_city[dff_city['Year Reported to CDP'] == yearToSelect]
    ReportedValue = dff_city2['Total BASIC Emissions (GPC)'].max()
    ReportedPopulation = dff_city2['Population'].max()
    ReportedPopulationYear = dff_city2['Population Year'].max()
    ReportedRate = ReportedValue/ReportedPopulation

    # report these values to the dataframe
    df_CountryWorldAllocation['ReportedValue'] = (ReportedValue)
    df_CountryWorldAllocation['ReportedPopulation'] = (ReportedPopulation)
    df_CountryWorldAllocation['ReportedPopulationYear'] = (ReportedPopulationYear)
    df_CountryWorldAllocation['ReportedRate'] = (ReportedRate)

    # !! remember to state the population year as different to the reported Time
    

    # use the city reported value and the country's allocated value to calculate the city percentage of total country emissions
    # calculate (and report these values to the dataframe) the City percentage of projected total, allocated and domestic (fair-share) emissions
    df_CountryWorldAllocation['CityPercentage'] = (ReportedValue/(CountryTotalEmissionValue*1000000))
    df_CountryWorldAllocation['CityAllocatedPortion'] = ((df_CountryWorldAllocation.CityPercentage*df_CountryWorldAllocation.allocation_MtCO2*1000000))
    df_CountryWorldAllocation['CityProjectedPortion'] = ((df_CountryWorldAllocation.CityPercentage*df_CountryWorldAllocation.total_emission*1000000))
    df_CountryWorldAllocation['CityDomesticPortion'] = ((df_CountryWorldAllocation.CityPercentage*df_CountryWorldAllocation.country_domestic*1000000))
    
    # filter the dataframe on 2020 to guide carbon budget calculations
    df_CountryWorldAllocation2 = df_CountryWorldAllocation[df_CountryWorldAllocation['year'] >=2020]

    # filter the dataframe on the end year to guide total carbon budget calculations
    df_CountryWorldAllocation3 = df_CountryWorldAllocation2[df_CountryWorldAllocation2['year'] <= endYearFloat]
    CityTotalBudget = df_CountryWorldAllocation3['CityAllocatedPortion'].sum()


    
    # calculate allowable emissions per year based on total budget
    AmountPerYearToMeetTarget = CityTotalBudget/(endYearFloat -2020)/ReportedPopulation

    # filter the dataframe on positive values to guide positive carbon budget calculations
    df_CountryWorldAllocation4 = df_CountryWorldAllocation3[df_CountryWorldAllocation2['CityAllocatedPortion'] >0]
    CityPositiveBudget = df_CountryWorldAllocation4['CityAllocatedPortion'].sum()

    # calculate allowable emissions per person based on total budget
    AmountPerPerson = CityPositiveBudget/ReportedPopulation

    # calculate years left for allowable emissions
    YearsLeftofPositiveAtReportedRate = CityPositiveBudget/ReportedValue

    #calculate years left for total emissions based on reported rate
    YearsLeftTotalAtReportedRate = CityTotalBudget/ReportedValue

    # filter the dataframe on negative values to guide negative carbon budget calculations
    df_CountryWorldAllocation5 = df_CountryWorldAllocation3[df_CountryWorldAllocation2['CityAllocatedPortion'] <0]
    CityNegativeBudget = df_CountryWorldAllocation5['CityAllocatedPortion'].sum()

    # report these budget calculations to the dataframe
    df_CountryWorldAllocation['CityTotalBudget'] = (CityTotalBudget)
    df_CountryWorldAllocation['CityPositiveBudget'] = (CityPositiveBudget)
    df_CountryWorldAllocation['CityNegativeBudget'] = (CityNegativeBudget)
    df_CountryWorldAllocation['YearsLeftofPositiveAtReportedRate'] = (YearsLeftofPositiveAtReportedRate)
    df_CountryWorldAllocation['AmountPerPeson'] = (AmountPerPerson)
    df_CountryWorldAllocation['AmountPerYearToMeetTarget'] = (AmountPerYearToMeetTarget)
    df_CountryWorldAllocation['YearsLeftTotalAtReportedRate'] = (YearsLeftTotalAtReportedRate)
   
   
    Metrics = ['Remaining GHG emissions', 'Remaining GHG emissions per person'] 
    Values = [CityPositiveBudget, AmountPerPerson]
      
    metrics_series = pd.Series(Metrics) 
    values_series = pd.Series(Values) 
      
    frame = { 'GHG Budget till 0 emissions': metrics_series, 'tCO2e': values_series } 
      
    df_summary = pd.DataFrame(frame) 
    df_summary['tCO2e']=df_summary['tCO2e'].map("{:,.0f}".format)
    return df_summary.to_dict(orient='records')

@app.callback(
    Output('summary-table2', 'data'),
    [Input ('selectedCountry', 'value'), Input ('selectedCity', 'value')])
def update_table(selectedCountry, selectedCity):
   
    endYearFloat= float(2050)
    
    # get proportion of allocated reduction for the world as a guide to the domestic (or 'fair share') contributions of other countries
    dff_world = df_country[df_country['country'] == 'World']

    dff_world['total_emission'] = (dff_world.fossil_CO2_MtCO2+dff_world.NonCO2_MtCO2e)
    dff_world['percent_domestic'] = (dff_world.allocation_MtCO2/dff_world.total_emission)

    WorldTotalEmissionList = dff_world['total_emission'].tolist()
    WorldPercentAllocateList = dff_world['percent_domestic'].tolist()

    # get the years as a common series for the x-axis
    # get the total contribution of the selected country to guide the percentage of domestic (or 'fair share') contribution based on the World allocation
    # get the allocated contribution of the country to guide the city's share
    dff_selectedCountry = df_country[df_country['country'] == selectedCountry]
    dff_selectedCountry['total_emission'] = (dff_selectedCountry.fossil_CO2_MtCO2+dff_selectedCountry.NonCO2_MtCO2e)

    CountryYearList = dff_selectedCountry['year'].tolist()
    CountryTotalEmissionList = dff_selectedCountry['total_emission'].tolist()
    CountryTotalAllocationList = dff_selectedCountry['allocation_MtCO2'].tolist()

    # create a dataframe that includes the percentage allocation of the world to calculate the domestic (or 'fair share') contribution for the selected country
    # include the allocated amount for the country to guide the city's share
    df_CountryWorldAllocation = pd.DataFrame(list(zip(CountryYearList, CountryTotalEmissionList, WorldPercentAllocateList, CountryTotalAllocationList)),
                  columns=['year', 'total_emission','percent_domestic', 'allocation_MtCO2'])
    df_CountryWorldAllocation['country_domestic'] = (df_CountryWorldAllocation.total_emission*df_CountryWorldAllocation.percent_domestic)

    # get the latest reported year
    dff_city = df_city[df_city['City'] == selectedCity]
    yearToSelect = dff_city['Year Reported to CDP'].max()

    # report this value to the dataframe
    df_CountryWorldAllocation['ReportedYear'] = (yearToSelect)

    # get the total country allocation for the latest reported year
    dff_country2 = dff_selectedCountry[dff_selectedCountry['year'] == yearToSelect]
    CountryAllocatedValue = dff_country2['allocation_MtCO2'].max()
    CountryTotalEmissionValue = dff_country2['total_emission'].max()


    # filter the CDP table for the latest reported year
    # get the reported value, population, population year and calculate the rate of carbon use for that combination
    dff_city2 = dff_city[dff_city['Year Reported to CDP'] == yearToSelect]
    ReportedValue = dff_city2['Total BASIC Emissions (GPC)'].max()
    ReportedPopulation = dff_city2['Population'].max()
    ReportedPopulationYear = dff_city2['Population Year'].max()
    ReportedRate = ReportedValue/ReportedPopulation

    # report these values to the dataframe
    df_CountryWorldAllocation['ReportedValue'] = (ReportedValue)
    df_CountryWorldAllocation['ReportedPopulation'] = (ReportedPopulation)
    df_CountryWorldAllocation['ReportedPopulationYear'] = (ReportedPopulationYear)
    df_CountryWorldAllocation['ReportedRate'] = (ReportedRate)

    # !! remember to state the population year as different to the reported year

    # use the city reported value and the country's allocated value to calculate the city percentage of total country emissions
    # calculate (and report these values to the dataframe) the City percentage of projected total, allocated and domestic (fair-share) emissions
    df_CountryWorldAllocation['CityPercentage'] = (ReportedValue/(CountryTotalEmissionValue*1000000))
    df_CountryWorldAllocation['CityAllocatedPortion'] = ((df_CountryWorldAllocation.CityPercentage*df_CountryWorldAllocation.allocation_MtCO2*1000000))
    df_CountryWorldAllocation['CityProjectedPortion'] = ((df_CountryWorldAllocation.CityPercentage*df_CountryWorldAllocation.total_emission*1000000))
    df_CountryWorldAllocation['CityDomesticPortion'] = ((df_CountryWorldAllocation.CityPercentage*df_CountryWorldAllocation.country_domestic*1000000))
    
    # filter the dataframe on 2020 to guide carbon budget calculations
    df_CountryWorldAllocation2 = df_CountryWorldAllocation[df_CountryWorldAllocation['year'] >=2020]

    # filter the dataframe on the end year to guide total carbon budget calculations
    df_CountryWorldAllocation3 = df_CountryWorldAllocation2[df_CountryWorldAllocation2['year'] <= endYearFloat]
    CityTotalBudget = df_CountryWorldAllocation3['CityAllocatedPortion'].sum()

    # calculate allowable emissions per year based on total budget
    AmountPerYearToMeetTarget = CityTotalBudget/(endYearFloat -2020)/ReportedPopulation

    # filter the dataframe on positive values to guide positive carbon budget calculations
    df_CountryWorldAllocation4 = df_CountryWorldAllocation3[df_CountryWorldAllocation2['CityAllocatedPortion'] >0]
    CityPositiveBudget = df_CountryWorldAllocation4['CityAllocatedPortion'].sum()

    # calculate years left for allowable emissions
    YearsLeftofPositiveAtReportedRate = CityPositiveBudget/ReportedValue


    #calculate years left for total emissions based on reported rate
    YearsLeftTotalAtReportedRate = CityTotalBudget/ReportedValue

    # filter the dataframe on negative values to guide negative carbon budget calculations
    df_CountryWorldAllocation5 = df_CountryWorldAllocation3[df_CountryWorldAllocation2['CityAllocatedPortion'] <0]
    CityNegativeBudget = df_CountryWorldAllocation5['CityAllocatedPortion'].sum()

    # report these budget calculations to the dataframe
    df_CountryWorldAllocation['CityTotalBudget'] = (CityTotalBudget)
    df_CountryWorldAllocation['CityPositiveBudget'] = (CityPositiveBudget)
    df_CountryWorldAllocation['CityNegativeBudget'] = (CityNegativeBudget)
    df_CountryWorldAllocation['YearsLeftofPositiveAtReportedRate'] = (YearsLeftofPositiveAtReportedRate)
    df_CountryWorldAllocation['AmountPerYearToMeetTarget'] = (AmountPerYearToMeetTarget)
    df_CountryWorldAllocation['YearsLeftTotalAtReportedRate'] = (YearsLeftTotalAtReportedRate)
   
   
    #Metrics = ['City Population', 'Years left of positive GHG at current rate', 'Years left of total GHG budget at current rate', 'Amount per person per year']
    Metrics = ['Years left at current rate']    
    Values = [YearsLeftofPositiveAtReportedRate]
      
    metrics_series = pd.Series(Metrics) 
    values_series = pd.Series(Values) 
      
    frame = { 'Time till 0 emissions': metrics_series, 'Years': values_series } 
      
    df_summary2 = pd.DataFrame(frame) 
    df_summary2['Years']=df_summary2['Years'].map("{:,.0f}".format)
    return df_summary2.to_dict(orient='records')

#@app.callback (Output('reporting-table', 'data'),[Input('selectedCountry', 'value'), Input('selectedCity', 'value')])    

def update_table(selectedCountry, selectedCity):

    endYearFloat= float(2050)
    
    # get proportion of allocated reduction for the world as a guide to the domestic (or 'fair share') contributions of other countries
    dff_world = df_country[df_country['country'] == 'World']

    dff_world['total_emission'] = (dff_world.fossil_CO2_MtCO2+dff_world.NonCO2_MtCO2e)
    dff_world['percent_domestic'] = (dff_world.allocation_MtCO2/dff_world.total_emission)

    WorldTotalEmissionList = dff_world['total_emission'].tolist()
    WorldPercentAllocateList = dff_world['percent_domestic'].tolist()

    # get the years as a common series for the x-axis
    # get the total contribution of the selected country to guide the percentage of domestic (or 'fair share') contribution based on the World allocation
    # get the allocated contribution of the country to guide the city's share
    dff_selectedCountry = df_country[df_country['country'] == selectedCountry]
    dff_selectedCountry['total_emission'] = (dff_selectedCountry.fossil_CO2_MtCO2+dff_selectedCountry.NonCO2_MtCO2e)

    CountryYearList = dff_selectedCountry['year'].tolist()
    CountryTotalEmissionList = dff_selectedCountry['total_emission'].tolist()
    CountryTotalAllocationList = dff_selectedCountry['allocation_MtCO2'].tolist()

    # create a dataframe that includes the percentage allocation of the world to calculate the domestic (or 'fair share') contribution for the selected country
    # include the allocated amount for the country to guide the city's share
    df_CountryWorldAllocation = pd.DataFrame(list(zip(CountryYearList, CountryTotalEmissionList, WorldPercentAllocateList, CountryTotalAllocationList)),
                  columns=['year', 'total_emission','percent_domestic', 'allocation_MtCO2'])
    df_CountryWorldAllocation['country_domestic'] = (df_CountryWorldAllocation.total_emission*df_CountryWorldAllocation.percent_domestic)

    # get the latest reported year
    dff_city = df_city[df_city['City'] == selectedCity]
    yearToSelect = dff_city['Year Reported to CDP'].max()

    # report this value to the dataframe
    df_CountryWorldAllocation['ReportedYear'] = (yearToSelect)

    # get the total country allocation for the latest reported year
    dff_country2 = dff_selectedCountry[dff_selectedCountry['year'] == yearToSelect]
    CountryAllocatedValue = dff_country2['allocation_MtCO2'].max()
    CountryTotalEmissionValue = dff_country2['total_emission'].max()


    # filter the CDP table for the latest reported year
    # get the reported value, population, population year and calculate the rate of carbon use for that combination
    dff_city2 = dff_city[dff_city['Year Reported to CDP'] == yearToSelect]
    ReportedValue = dff_city2['Total BASIC Emissions (GPC)'].max()
    ReportedPopulation = dff_city2['Population'].max()
    ReportedPopulationYear = dff_city2['Population Year'].max()
    ReportedRate = ReportedValue/ReportedPopulation

    # report these values to the dataframe
    df_CountryWorldAllocation['ReportedValue'] = (ReportedValue)
    df_CountryWorldAllocation['ReportedPopulation'] = (ReportedPopulation)
    df_CountryWorldAllocation['ReportedPopulationYear'] = (ReportedPopulationYear)
    df_CountryWorldAllocation['ReportedRate'] = (ReportedRate)

    # !! remember to state the population year as different to the reported year

    # use the city reported value and the country's allocated value to calculate the city percentage of total country emissions
    # calculate (and report these values to the dataframe) the City percentage of projected total, allocated and domestic (fair-share) emissions
    df_CountryWorldAllocation['CityPercentage'] = (ReportedValue/(CountryTotalEmissionValue*1000000))
    df_CountryWorldAllocation['CityAllocatedPortion'] = ((df_CountryWorldAllocation.CityPercentage*df_CountryWorldAllocation.allocation_MtCO2*1000000))
    df_CountryWorldAllocation['CityProjectedPortion'] = ((df_CountryWorldAllocation.CityPercentage*df_CountryWorldAllocation.total_emission*1000000))
    df_CountryWorldAllocation['CityDomesticPortion'] = ((df_CountryWorldAllocation.CityPercentage*df_CountryWorldAllocation.country_domestic*1000000))

    # filter the dataframe on 2020 to guide carbon budget calculations
    df_CountryWorldAllocation2 = df_CountryWorldAllocation[df_CountryWorldAllocation['year'] >=2020]

    # filter the dataframe on the end year to guide total carbon budget calculations
    df_CountryWorldAllocation3 = df_CountryWorldAllocation2[df_CountryWorldAllocation2['year'] <=endYearFloat]
    CityTotalBudget = df_CountryWorldAllocation3['CityAllocatedPortion'].sum()

    # calculate allowable emissions per year based on total budget
    AmountPerYearToMeetTarget = CityTotalBudget/(endYearFloat-2020)

    # filter the dataframe on positive values to guide positive carbon budget calculations
    df_CountryWorldAllocation4 = df_CountryWorldAllocation3[df_CountryWorldAllocation2['CityAllocatedPortion'] >0]
    CityPositiveBudget = df_CountryWorldAllocation4['CityAllocatedPortion'].sum()

    # calculate years left for allowable emissions
    YearsLeftofPositiveAtReportedRate = CityPositiveBudget/ReportedValue

    #calculate years left for total emissions based on reported rate
    YearsLeftTotalAtReportedRate = CityTotalBudget/ReportedValue

    # filter the dataframe on negative values to guide negative carbon budget calculations
    df_CountryWorldAllocation5 = df_CountryWorldAllocation3[df_CountryWorldAllocation2['CityAllocatedPortion'] <0]
    CityNegativeBudget = df_CountryWorldAllocation5['CityAllocatedPortion'].sum()

    # report these budget calculations to the dataframe
    df_CountryWorldAllocation['CityTotalBudget'] = (CityTotalBudget)
    df_CountryWorldAllocation['CityPositiveBudget'] = (CityPositiveBudget)
    df_CountryWorldAllocation['CityNegativeBudget'] = (CityNegativeBudget)
    df_CountryWorldAllocation['YearsLeftofPositiveAtReportedRate'] = (YearsLeftofPositiveAtReportedRate)
    df_CountryWorldAllocation['AmountPerYearToMeetTarget'] = (AmountPerYearToMeetTarget)
    df_CountryWorldAllocation['YearsLeftTotalAtReportedRate'] = (YearsLeftTotalAtReportedRate)

    return df_CountryWorldAllocation.to_dict(orient='records')
      

  
if __name__ == '__main__':
    app.run_server(debug=True)