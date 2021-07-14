# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 10:48:38 2021

@author: Sarah
"""

import pandas as pd
import plotly.express as px
import numpy as np
from skimage import io, data

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date

### Daten-Basis schaffen ###

#OWID-Daten laden und einlesen mit Pandas 
df = pd.read_csv("https://covid.ourworldindata.org/data/owid-covid-data.csv")



#leere Zellen im Datensatz ersetzen
df.replace('', np.NaN, inplace=True)
#df.replace(np.NaN, 0, inplace=True) 

#neustes Datum als Variable definieren für den Datepicker
newestDate = df["date"].max()
   
df.new_cases_per_million = df.new_cases_per_million.astype(float)


###Farbskala erstellen###

#Vorbereitete Farbskala einlesen (200x200Px PNG mit Adobe Illustrator erstellt)
img = io.imread('C:\\Users\\Sarah\\Documents\\Studium\\_BT\\farbskala\\farbskala3.png')

#Farbwerte der einzelnen Pixel in einem Array speichern
img_arr = np.array(img)

#Array umformen
newarr= img_arr.reshape(-1, 3)

#Farbbibliothek erstellen für generelle Nutzung in Visualisierungen 
#(für Matrix nicht verwendet)
def bivariate_colors(newarr):
    
    n_colors = len(newarr)
    index = set(range(n_colors))

    biv_colors = []
    for c in newarr:
        biv_colors.append(f'rgb{tuple(c)}')
        
    return biv_colors

biv_colors = bivariate_colors(newarr)


def set_color_coordinatesA(matrixarrayA, intervalstepA):
    n = intervalstepA
    m = 1
    collist = []

    for x in np.nditer(matrixarrayA):
        while m <= 200:
        
            if x < n*m:
                collist.append(m-1)
                break

            elif n*m == x:
                if m == 200:
                    collist.append(m-1)
                else: 
                    collist.append(m)
                break
            m = m+1
        m=1
              
    return collist

def set_color_coordinatesB(matrixarrayB, intervalstepB):
    n = intervalstepB
    m = 1
    collist = []

    for x in np.nditer(matrixarrayB):
        while m <= 200:
        
            if x < n*m:
                collist.append(m-1)
                break

            elif n*m == x:
                if m == 200:
                    collist.append(m-1)
                else: 
                    collist.append(m)
                break
            m = m+1
        m=1
              
    return collist



app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div(children = [
    html.H1('COVID-19 Visualization of dynamic correlations'),
    ], className="header"),
    dcc.Tabs(id='tabs-example', value='tab-1', 
             parent_className='custom-tabs', 
             className='custom-tabs-container',
             children=[
        dcc.Tab(label='Compare Countries', value='tab-1',
                className='custom-tab',
                selected_className='custom-tab--selected'),
        dcc.Tab(label='Compare Attributes', value='tab-2',
                className='custom-tab',
                selected_className='custom-tab--selected'),
    ]),
    html.Div(id='tabs-example-content')
])

@app.callback(Output('tabs-example-content', 'children'),
              Input('tabs-example', 'value'))

def render_content(tab):
    if tab == 'tab-1':
        return html.Div(children = [
                html.Div(children = [
                html.H2("Selection"),
            
                html.Div(children=[
                    dcc.Dropdown(id='country',
                                 options = [{'label': i, 'value': i} for i in df["location"].unique()],
                                 multi = True,
                                 value = ["Switzerland", "Germany"],
                                 className="dropdown"),
            
                    dcc.Dropdown(id='attributes',
                                 options = [{'label': "New cases", 'value': "new_cases"},
                                            {'label': "New cases per Million", 'value': "new_cases_per_million"},
                                            {'label': "New deaths", 'value': "new_deaths"},
                                            {'label': "People fully Vaccinated", 'value': "people_fully_vaccinated"}],
                                 multi = False,
                                 value = "new_cases",
                                 className="dropdown")
                ], className="selectionrow"),
            
                html.Br(),
            
                html.Div(children=[
                    dcc.DatePickerRange(
                        id='datepicker',
                        min_date_allowed=date(2020, 1, 22),
                        start_date=date(2020, 1, 22),
                        max_date_allowed=newestDate,
                        end_date=newestDate,
                        ),
                ], className="selectionrow2"),
            
                html.Div(children=[
                    dcc.Graph(id='crossfilter-scatter', figure = {}, responsive=True,
                              config={'displayModeBar': False}
                          )
                ], className="scatter-row"),
                
                html.Div(children=[
                    dcc.Graph(id='total-population-hist', figure = {}, responsive=True,
                              config={'displayModeBar': False}
                              ),
                    dcc.Graph(id='total-cases-hist', figure = {}, responsive=True,
                              config={'displayModeBar': False}
                              ),
                    dcc.Graph(id='total-deaths-hist', figure = {}, responsive=True,
                              config={'displayModeBar': False}
                          )
                ], className="overview-hists")
            
            ], className="wrapper-list"),
        
            html.Div(children = [
                    html.Div(children = [
                        dcc.Graph(id='colormatrix', figure = {}, style = {'display': 'inline-block'}, responsive=True,
                                  config={'displayModeBar': False}),
                        dcc.Graph(id='marginalhistA', figure = {}, style = {'display': 'inline-block'}, responsive=True,
                                  config={'displayModeBar': False}),
                    ], className="graphs"), 
                    html.Div(children = [
                        dcc.Graph(id='marginalhistB', figure = {}, style = {'display': 'inline-block'}, responsive=True,
                                  config={'displayModeBar': False}),
                        dcc.Graph(id='adjacency', figure = {}, style = {'display': 'inline-block'}, responsive=True,),
                    ], className="graphs"),
                ], className="graph-container"),
        ], className="container")
    
    
    
    elif tab == 'tab-2':
        return html.Div(children = [
                html.Div(children = [
                html.H2("Selection"),
            
                html.Div(children=[
                    dcc.Dropdown(id='country2',
                                 options = [{'label': i, 'value': i} for i in df["location"].unique()],
                                 multi = False,
                                 value = "Switzerland",
                                 className="dropdown"),
            
                    dcc.Dropdown(id='attributes2',
                                 options = [{'label': "New cases", 'value': "new_cases"},
                                            {'label': "Stringency Index", 'value': "stringency_index"},
                                            {'label': "New deaths", 'value': "new_deaths"},
                                            {'label': "New Vaccinations", 'value': "new_vaccinations"}],
                                 multi = True,
                                 value = ["new_cases", "new_deaths"] ,
                                 className="dropdown")
                ], className="selectionrow"),
            
                html.Br(),
            
                html.Div(children=[
                    dcc.DatePickerRange(
                        id='datepicker',
                        min_date_allowed=date(2020, 1, 22),
                        start_date=date(2020, 1, 22),
                        max_date_allowed=newestDate,
                        end_date=newestDate,
                        ),
                ], className="selectionrow2"),
            
                html.Div(children=[
                    dcc.Graph(id='crossfilter-scatter2', figure = {}, responsive=True,
                              config={'displayModeBar': False}
                          )
                ], className="scatter-row"),
                
                html.Div(children=[
                    dcc.Graph(id='total-population-hist2', figure = {},responsive=True, 
                              config={'displayModeBar': False}
                              ),
                    dcc.Graph(id='total-cases-hist2', figure = {}, responsive=True,
                              config={'displayModeBar': False}
                              ),
                    dcc.Graph(id='total-deaths-hist2', figure = {}, responsive=True,
                              config={'displayModeBar': False}
                          )
                ], className="overview-hists")
            
            ], className="wrapper-list"),
        
            html.Div(children = [
                    html.Div(children = [
                        dcc.Graph(id='colormatrix2', figure = {}, style = {'display': 'inline-block'}, responsive=True,
                                  config={'displayModeBar': False}),
                        dcc.Graph(id='marginalhistA2', figure = {}, style = {'display': 'inline-block'}, responsive=True, 
                                  config={'displayModeBar': False}),
                    ], className="graphs"), 
                    html.Div(children = [
                        dcc.Graph(id='marginalhistB2', figure = {}, style = {'display': 'inline-block'},responsive=True,
                                  config={'displayModeBar': False}),
                        dcc.Graph(id='adjacency2', figure = {}, style = {'display': 'inline-block'}, responsive=True),
                    ], className="graphs"),
                ], className="graph-container"),
        ], className="container")
    
    
@app.callback(
    [Output(component_id='crossfilter-scatter', component_property='figure'),
     Output(component_id='total-population-hist', component_property='figure'),
     Output(component_id='total-cases-hist', component_property='figure'),
     Output(component_id='total-deaths-hist', component_property='figure'),
     Output(component_id='marginalhistA', component_property='figure'),
     Output(component_id='colormatrix', component_property='figure'),
     Output(component_id='marginalhistB', component_property='figure'),
     Output(component_id='adjacency', component_property='figure')
     ],
     [Input(component_id='country', component_property='value'),
      Input(component_id='datepicker', component_property='start_date'),
      Input(component_id='datepicker', component_property='end_date'),
      Input(component_id='attributes', component_property='value')],
     
     #[dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
     #dash.dependencies.Input('crossfilter-yaxis-column', 'value'),]
)

def update_countries(country_slctd, date_slctd1, date_slctd2, attr_slctd):
    
    #Arbeitskopie der geladenen Daten erstellen
    dff = df.copy()
    
    #Eingrenzung des Scatterplots auf einen Kontinent
    #Später dann Mehrfachauswahl möglich machen
    dff = dff[dff["location"].isin(country_slctd)]
    
    #Eingrenzen der Zeitserie
    dff = dff[dff["date"] >= date_slctd1]
    dff = dff[dff["date"] <= date_slctd2]
    

    fig1 = px.scatter_matrix(dff,
        dimensions=["new_cases", "new_deaths", "people_fully_vaccinated"],
        #== xaxis_column_name]['Value']
        #== yaxis_column_name]['Value'],
        color='location', template='plotly_white')
                          
    fig1.update_layout(clickmode='event+select', margin=dict(l=2, r=5, t=10, b=0))
    #fig1.update_traces(customdata=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'])
    
    
    newestDateP = dff["date"].max() 
    dffP = dff[dff["date"] == newestDateP]
    dffP = dffP.filter(["location", "population", "population_density", "total_cases", "total_deaths"])
    
    fig2 = px.histogram(dffP, x="location", y="population", 
                        color="location", title="Population", template='plotly_white')
    fig2.update_layout(showlegend=False, 
        margin=dict(l=2, r=5, t=35, b=0))
    fig2.update_xaxes(title='', visible=True, showticklabels=True)
    fig2.update_yaxes(title='', visible=True, showticklabels=True)
    
    fig3 = px.histogram(dffP, x="location", y="total_cases", 
                        color="location", title="Total Cases", template='plotly_white')
    fig3.update_layout(showlegend=False,
        margin=dict(l=2, r=5, t=35, b=0))
    fig3.update_xaxes(title='', visible=True, showticklabels=True)
    fig3.update_yaxes(title='', visible=True, showticklabels=True)
    
    fig4 = px.histogram(dffP, x="location", y="total_deaths", 
                        color="location", title="Total Deaths", template='plotly_white')
    fig4.update_layout(showlegend=False,
        margin=dict(l=2, r=5, t=35, b=0))
    fig4.update_xaxes(title='', visible=True, showticklabels=True)
    fig4.update_yaxes(title='', visible=True, showticklabels=True)
    

    
    if  attr_slctd == "new_cases":
        dff2 = dff.filter(["date", "new_cases", "location"])
        
        dffA = dff2[dff2['location'] == country_slctd[0]]
        #dffA = dffA.filter(["date", "new_cases", "location"])
    
        dffB = dff2[dff2['location'] == country_slctd[1]]
        #dffB = dffB.filter(["date", "new_cases", "location"])
        #Farbkoordinaten zu den Attriut-Werten bestimmen
        
        combi = dffA.merge(dffB, left_on="date", right_on="date", how="outer", suffixes=("_A", "_B"))

        
        combibi = combi.filter(['new_cases_A', 'new_cases_B'])
        matrixarrayA = combibi.to_numpy(dtype=int)
        matrixarrayA = np.where(matrixarrayA<0, 0, matrixarrayA)


    elif attr_slctd == "new_cases_per_million":
        dff2 = dff.filter(["date", "new_cases_per_million", "location"])
        
        dffA = dff2[dff2['location'] == country_slctd[0]]
        #dffA = dffA.filter(["date", "new_cases", "location"])
    
        dffB = dff2[dff2['location'] == country_slctd[1]]
        #dffB = dffB.filter(["date", "new_cases", "location"])
        #Farbkoordinaten zu den Attriut-Werten bestimmen
        
        combi = dffA.merge(dffB, left_on="date", right_on="date", how="outer", suffixes=("_A", "_B"))

        
        combibi = combi.filter(['new_cases_per_million_A', 'new_cases_per_million_B'])
        matrixarrayA = combibi.to_numpy(dtype=int)
        matrixarrayA = np.where(matrixarrayA<0, 0, matrixarrayA)

        
    elif attr_slctd == "new_deaths":
        dff2 = dff.filter(["date", "new_deaths", "location"])
        
        dffA = dff2[dff2['location'] == country_slctd[0]]
        #dffA = dffA.filter(["date", "new_cases", "location"])
    
        dffB = dff2[dff2['location'] == country_slctd[1]]
        #dffB = dffB.filter(["date", "new_cases", "location"])
        #Farbkoordinaten zu den Attriut-Werten bestimmen
        
        combi = dffA.merge(dffB, left_on="date", right_on="date", how="outer", suffixes=("_A", "_B"))

        
        combibi = combi.filter(['new_deaths_A', 'new_deaths_B'])
        matrixarrayA = combibi.to_numpy(dtype=int)
        matrixarrayA = np.where(matrixarrayA<0, 0, matrixarrayA)
        

        
    elif attr_slctd == "people_fully_vaccinated":
        dff2 = dff.filter(["date", "people_fully_vaccinated", "location"])
        
        dffA = dff2[dff2['location'] == country_slctd[0]]
        #dffA = dffA.filter(["date", "new_cases", "location"])
    
        dffB = dff2[dff2['location'] == country_slctd[1]]
        #dffB = dffB.filter(["date", "new_cases", "location"])
        #Farbkoordinaten zu den Attriut-Werten bestimmen
        
        combi = dffA.merge(dffB, left_on="date", right_on="date", how="outer", suffixes=("_A", "_B"))

        
        combibi = combi.filter(['people_fully_vaccinated_A', 'people_fully_vaccinated_B'])
        matrixarrayA = combibi.to_numpy(dtype=int)
        matrixarrayA = np.where(matrixarrayA<0, 0, matrixarrayA)
    
    else: 
        combibi = dff.filter(["date", "new_cases", "new_deaths", "location"])
        matrixarrayA = combibi.to_numpy(dtype=int)
        #matrixarray = np.where(matrixarray<0, 0, matrixarray)
        
        


    
    
    attMax = matrixarrayA.max()
        
    intervalstepA = attMax/200
    

    #colarr für Color-Array. Die Farbkoordinaten aus der zuvor definierten Funktion 
    #set_interval_value() als einzelne Werte.
    colarr = np.array(set_color_coordinatesA(matrixarrayA, intervalstepA))
    

    # Halbe Länge des Arrays entspricht nachher der Länge einer Achse lA
    #lA muss zusätzlich als Integer definiert werden

    lA = len(colarr)/2
    lA = int(lA)


    #Halbieren des colarr Arrays und anschliessendes Kombinieren der Werte zu den
    #X- und Y-Koordinaten des gewünschten Vergleichspaares in der Liste colcoor
    #(colcoor -> Color-Coordinates)
    halfcolarr = np.array_split(colarr, 2)

    colcoor = [[a, b] for a in halfcolarr[0] 
                      for b in halfcolarr[1]] 
                         
    #Umformen der Liste zu einem Array und der Anordnung für X- und Y-Achse
    colcoor = np.array(colcoor)
    colcoor = colcoor.reshape(lA,lA,2)



    #Umformen des Farbarrays aus der Farbmatrix zu einem 3D-Array
    bivarray = newarr.reshape(200, 200, 3)

    #Erstellen einer Liste mit den Farben, die für die Visualisierung benötigt werden
    #valcollist -> value-color-list
    valcollist = []

    for x in colcoor:
        for y in x:
            a = y[0]
            b = y[1]
            valcollist.append(bivarray[a][b])


    #Bereinigen der erstellten Liste
    valcollist2 = [list(i) for i in valcollist]

    #Umformen der Liste in ein 3D-Array
    valcolors = np.array(valcollist2).reshape(lA,lA,3)
    
    
    # def update_matrix(dff, contin_slctd, date_slctd1, date_slctd2):    
    fig5 = px.histogram(dffB, x="date", y=dffB.columns[1], template='plotly_white',
                        height=100, width=550,
                        labels={
                            "date": "Series of " + dffB["location"].iloc[0] + " for " + attr_slctd}
                        #color_discrete_map={"new_cases_SUI" : 'rgb(48, 38, 131)'},
                        )
    fig5.update_xaxes(type='category')
    fig5.update_yaxes(visible=False, showticklabels=False)
    fig5.update_layout(
        xaxis={"mirror" : "all", 'side': 'top'}, 
        yaxis={"mirror" : "all", 'side': 'right'},
        margin=dict(l=20, r=20, t=2, b=2)
        )
    


    img = io.imread('C:\\Users\\Sarah\\Documents\\Studium\\_BT\\farbskala\\farbskala3.png')
    fig6 = px.imshow(img, height=100, width=100)
    fig6.update_xaxes(visible=False, showticklabels=False, automargin=True)
    fig6.update_yaxes(visible=False, showticklabels=False, automargin=True)
    fig6.update_layout(margin=dict(l=5, r=5, t=10, b=5))


    fig7 = px.histogram(dffA, x=dffA.columns[1], y="date", template='plotly_white',
                        orientation='h', height=550, width=100,
                        color_discrete_map={"new_cases":'rgb(232, 78, 27)'},
                        labels={
                            "date": "Series of " + dffA["location"].iloc[0] + " for " + attr_slctd})
    fig7.update_yaxes(autorange="reversed", type='category')
    #fig4.update_xaxes(mirror=True, side='top')
    fig7.update_xaxes(autorange="reversed", visible=False, showticklabels=False)
    fig7.update_layout(
            #funktionieren nur bei der Beschriftung, keinen Einfluss auf die Balken
            xaxis={"mirror" : "all", 'side': 'bottom'}, 
            yaxis={"mirror" : True, 'side': 'left'},
            margin=dict(l=2, r=5, t=2, b=5)
        )
    
    

    fig8 = px.imshow(valcolors, width=550, height=550, template='plotly_white')
    fig8.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
    fig8.update_yaxes(showticklabels=False, showgrid=False, zeroline=False)
    fig8.update_layout(
        margin=dict(l=2, r=2, t=10, b=5))


    
    return fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8

@app.callback(
    [Output(component_id='crossfilter-scatter2', component_property='figure'),
      Output(component_id='total-population-hist2', component_property='figure'),
      Output(component_id='total-cases-hist2', component_property='figure'),
      Output(component_id='total-deaths-hist2', component_property='figure'),
      Output(component_id='marginalhistA2', component_property='figure'),
      Output(component_id='colormatrix2', component_property='figure'),
      Output(component_id='marginalhistB2', component_property='figure'),
      Output(component_id='adjacency2', component_property='figure')
      ],
      [Input(component_id='country2', component_property='value'),
      Input(component_id='datepicker', component_property='start_date'),
      Input(component_id='datepicker', component_property='end_date'),
      Input(component_id='attributes2', component_property='value')],
)

def update_attributes(country_slctd, date_slctd1, date_slctd2, attr_slctd):
    
    #Arbeitskopie der geladenen Daten erstellen
    dff = df.copy()
    
    #Eingrenzung des Scatterplots auf einen Kontinent
    #Später dann Mehrfachauswahl möglich machen
    dff = dff[dff["location"] == country_slctd]
    
    #Eingrenzen der Zeitserie
    dff = dff[dff["date"] >= date_slctd1]
    dff = dff[dff["date"] <= date_slctd2]
    

    fig1 = px.scatter_matrix(dff,
        dimensions=["new_cases", "new_deaths", "people_fully_vaccinated"],
        #== xaxis_column_name]['Value']
        #== yaxis_column_name]['Value'],
        template='plotly_white',
        color='location')
                          
    fig1.update_layout(clickmode='event+select', margin=dict(l=2, r=5, t=10, b=0))
    #fig1.update_traces(customdata=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'])
    
    
    newestDateP = dff["date"].max() 
    dffP = dff[dff["date"] == newestDateP]
    dffP = dffP.filter(["location", "population", "population_density", "total_cases", "total_deaths"])
    
    fig2 = px.histogram(dffP, x="location", y="population", template='plotly_white',
                        color="location", title="Population")
    fig2.update_layout(showlegend=False, 
        margin=dict(l=2, r=5, t=35, b=0))
    fig2.update_xaxes(title='', visible=True, showticklabels=True)
    fig2.update_yaxes(title='', visible=True, showticklabels=True)
    
    fig3 = px.histogram(dffP, x="location", y="total_cases",template='plotly_white',
                        color="location", title="Total Cases")
    fig3.update_layout(showlegend=False,
        margin=dict(l=2, r=5, t=35, b=0))
    fig3.update_xaxes(title='', visible=True, showticklabels=True)
    fig3.update_yaxes(title='', visible=True, showticklabels=True)
    
    fig4 = px.histogram(dffP, x="location", y="total_deaths", template='plotly_white',
                        color="location", title="Total Deaths")
    fig4.update_layout(showlegend=False,
        margin=dict(l=2, r=5, t=35, b=0))
    fig4.update_xaxes(title='', visible=True, showticklabels=True)
    fig4.update_yaxes(title='', visible=True, showticklabels=True)
   
    
    if  "new_cases" in attr_slctd:
        if "new_deaths" in attr_slctd:
            combi = dff.filter(["date", "new_cases","new_deaths", "location"])
            attrNames = ["new_cases", "new_deaths"]
            
            #combibi = combi.filter(['new_cases', 'new_deaths'])
            
            attMaxA = combi["new_cases"].max()
            attMaxB = combi["new_deaths"].max()
        
            intervalstepA = attMaxA/200
            intervalstepB = attMaxB/200
            
            matrixarrayA = combi["new_cases"].to_numpy(dtype=int)
            matrixarrayB = combi["new_deaths"].to_numpy(dtype=int)

        elif "new_vaccinations" in attr_slctd:
            combi = dff.filter(["date", "new_cases", "new_vaccinations", "location"])
            attrNames = ["new_cases", "new_vaccinations"]
            
            #combibi = combi.filter(['new_cases', 'new_deaths'])
            
            attMaxA = combi["new_cases"].max()
            attMaxB = combi["new_vaccinations"].max()
        
            intervalstepA = attMaxA/200
            intervalstepB = attMaxB/200
            
            matrixarrayA = combi["new_cases"].to_numpy(dtype=int)
            matrixarrayB = combi["new_vaccinations"].to_numpy(dtype=int)


        elif "stringency_index" in attr_slctd:
            combi = dff.filter(["date", "new_cases", "stringency_index", "location"])
            attrNames = ["new_cases", "stringency_index"]
            
            #combibi = combi.filter(['new_cases', 'new_deaths'])
            
            attMaxA = combi["new_cases"].max()
            attMaxB = combi["stringency_index"].max()
        
            intervalstepA = attMaxA/200
            intervalstepB = attMaxB/200
            
            matrixarrayA = combi["new_cases"].to_numpy(dtype=int)
            matrixarrayB = combi["stringency_index"].to_numpy(dtype=int)
 
    
    elif "stringency_index" in attr_slctd:
        if "new_deaths" in attr_slctd:
            combi = dff.filter(["date", "stringency_index", "new_deaths", "location"])
            attrNames = ["stringency_index", "new_deaths"]
            
            #combibi = combi.filter(['new_cases', 'new_deaths'])
            
            attMaxA = combi["stringency_index"].max()
            attMaxB = combi["new_deaths"].max()
        
            intervalstepA = attMaxA/200
            intervalstepB = attMaxB/200
            
            matrixarrayA = combi["stringency_index"].to_numpy(dtype=int)
            matrixarrayB = combi["new_deaths"].to_numpy(dtype=int)

        elif "new_vaccinations" in attr_slctd:
            combi = dff.filter(["date", "stringency_index", "new_vaccinations", "location"])
            attrNames = ["stringency_index", "new_vaccinations"]
            
            #combibi = combi.filter(['new_cases', 'new_deaths'])
            
            attMaxA = combi["stringency_index"].max()
            attMaxB = combi["new_vaccinations"].max()
        
            intervalstepA = attMaxA/200
            intervalstepB = attMaxB/200
            
            matrixarrayA = combi["stringency_index"].to_numpy(dtype=int)
            matrixarrayB = combi["new_vaccinations"].to_numpy(dtype=int)

        
    elif "new_deaths" in attr_slctd:
        if "new_vaccinations" in attr_slctd:
            combi = dff.filter(["date", "new_deaths", "new_vaccinations", "location"])
            attrNames = ["new_deaths", "new_vaccinations"]
            
            #combibi = combi.filter(['new_cases', 'new_deaths'])
            
            attMaxA = combi["new_deaths"].max()
            attMaxB = combi["new_vaccinations"].max()
        
            intervalstepA = attMaxA/200
            intervalstepB = attMaxB/200
            
            matrixarrayA = combi["new_deaths"].to_numpy(dtype=int)
            matrixarrayB = combi["new_vaccinations"].to_numpy(dtype=int)    
    
    else: 
        combibi = dff.filter(["date", "new_cases", "new_deaths", "location"])
        matrixarray = combibi.to_numpy(dtype=int)
        #matrixarray = np.where(matrixarray<0, 0, matrixarray)
        
        
    

    #colarr für Color-Array. Die Farbkoordinaten aus der zuvor definierten Funktion 
    #set_interval_value() als einzelne Werte.
    colarrA = np.array(set_color_coordinatesA(matrixarrayA, intervalstepA))
    colarrB = np.array(set_color_coordinatesB(matrixarrayB, intervalstepB))

    # Halbe Länge des Arrays entspricht nachher der Länge einer Achse lA
    #lA muss zusätzlich als Integer definiert werden
    lA = len(colarrA)
    lA = int(lA)


    colcoor = [[a, b] for a in colarrA 
                      for b in colarrB] 
                         
    #Umformen der Liste zu einem Array und der Anordnung für X- und Y-Achse
    colcoor = np.array(colcoor)
    colcoor = colcoor.reshape(lA,lA,2)



    #Umformen des Farbarrays aus der Farbmatrix zu einem 3D-Array
    bivarray = newarr.reshape(200, 200, 3)

    #Erstellen einer Liste mit den Farben, die für die Visualisierung benötigt werden
    #valcollist -> value-color-list
    valcollist = []

    for x in colcoor:
        for y in x:
            a = y[0]
            b = y[1]
            valcollist.append(bivarray[a][b])


    #Bereinigen der erstellten Liste
    valcollist2 = [list(i) for i in valcollist]

    #Umformen der Liste in ein 3D-Array
    valcolors = np.array(valcollist2).reshape(lA,lA,3)
    
    
    # def update_matrix(dff, contin_slctd, date_slctd1, date_slctd2):    
    fig5 = px.histogram(combi, x="date", y=combi.columns[2], template='plotly_white',
                        height=100, width=550,
                        labels={
                            "date": "Series of " + combi["location"].iloc[0] + " for " + attrNames[1]}
                        #color_discrete_map={"new_cases_SUI" : 'rgb(48, 38, 131)'},
                        )
    fig5.update_xaxes(type='category')
    fig5.update_yaxes(visible=False, showticklabels=False)
    fig5.update_layout(
        xaxis={"mirror" : "all", 'side': 'top'}, 
        yaxis={"mirror" : "all", 'side': 'right'},
        margin=dict(l=20, r=20, t=2, b=2)
        )
    


    img = io.imread('C:\\Users\\Sarah\\Documents\\Studium\\_BT\\farbskala\\farbskala3.png')
    fig6 = px.imshow(img, height=100, width=100)
    fig6.update_xaxes(visible=False, showticklabels=False, automargin=True)
    fig6.update_yaxes(visible=False, showticklabels=False, automargin=True)
    fig6.update_layout(margin=dict(l=5, r=5, t=10, b=5))


    fig7 = px.histogram(combi, x=combi.columns[1], y="date", template='plotly_white',
                        orientation='h', height=550, width=100, 
                        color_discrete_map={"new_cases":'rgb(232, 78, 27)'},
                        labels={
                            "date": "Series of " + combi["location"].iloc[0] + " for " + attrNames[0]})
    fig7.update_yaxes(autorange="reversed", type='category')
    #fig4.update_xaxes(mirror=True, side='top')
    fig7.update_xaxes(autorange="reversed", visible=False, showticklabels=False)
    fig7.update_layout(
            #funktionieren nur bei der Beschriftung, keinen Einfluss auf die Balken
            xaxis={"mirror" : "all", 'side': 'bottom'}, 
            yaxis={"mirror" : True, 'side': 'left'},
            margin=dict(l=2, r=5, t=2, b=5)
        )
    
    

    fig8 = px.imshow(valcolors, width=550, height=550, template='plotly_white')
    fig8.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
    fig8.update_yaxes(showticklabels=False, showgrid=False, zeroline=False)
    fig8.update_layout(
         margin=dict(l=0, r=0, t=10, b=5))


    
    return fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8



if __name__ == '__main__':
    app.run_server(debug=False)