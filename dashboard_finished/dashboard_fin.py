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
#Quick and Dirty Workaround weil Plotly Express 0-Werte am Anfang und Ende 
#im Histogramm nicht anzeigt. Solange Zeilen nicht summiert werden geht das...
df.replace('', 0.01, inplace=True)
df.replace(np.NaN, 0.01, inplace=True) 
df.replace(0, 0.01, inplace=True)

#neustes Datum als Variable definieren für den Datepicker
newestDate = df["date"].max()

#Definition von new_cases_per_million als Float. 
#Sonst wird eine Fehlermeldung ausgegeben sobald die Variable angewendet wird   
df.new_cases_per_million = df.new_cases_per_million.astype(float)


###Farbskala erstellen###

#Vorbereitete Farbskala einlesen (200x200Px PNG mit Adobe Illustrator erstellt)
img = io.imread('farbskala3.png')

#Farbwerte der einzelnen Pixel in einem Array speichern
img_arr = np.array(img)

#Array umformen
newarr= img_arr.reshape(-1, 3)

#Farbbibliothek erstellen für generelle Nutzung in Visualisierungen 
#(für Matrix nicht verwendet)
# def bivariate_colors(newarr):
    
#     n_colors = len(newarr)
#     index = set(range(n_colors))

#     biv_colors = []
#     for c in newarr:
#         biv_colors.append(f'rgb{tuple(c)}')
        
#     return biv_colors

# biv_colors = bivariate_colors(newarr)


#Funktion die die Attributswerte in einzelne Koordinaten umwandelt. 
#Passiert über die Zuordnung zu einzelnen Intervallschritte
#Funktion wird für den Attributvergleich zweimal benötigt (A & B)
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


###Layout###

#Iniziieren der Dash App 
app = dash.Dash(__name__)

app.layout = html.Div([
    #Titelzeile
    html.Div(children = [
    html.H1('COVID-19 Visualization of dynamic correlations'),
    ], className="header"),
    
    #Tabs, erste Selektionsfunktion für die App. 
    #Sollen zwei Länder oder zwei Attribute verglichen werden?
    dcc.Tabs(id='selection-tabs', value='tab-1', 
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
    html.Div(id='selection-tabs-content')
])

@app.callback(Output('selection-tabs-content', 'children'),
              Input('selection-tabs', 'value'))


#Der Inhalt der Tabs wird durch eine Funktion generiert. 
#Der Output der Funktion bildet den gesamten Tab-Content ab. 
#Je nachdem welcher Tab angewählt ist, wird entweder der Content für 
#die "Compare Countries" oder die "Compare Attributs" Variante ausgegeben.
def render_content(tab):
    
    #Content Tab1
    if tab == 'tab-1':
        return html.Div(children = [
                html.Div(children = [
                    
                #Linke Spalte
                html.H2("Selection"),
            
                #Selektionstools auf der ersten Zeile (nebeneinander abbgebildet)
                html.Div(children=[
                    dcc.Dropdown(id='country',
                                 options = [{'label': i, 'value': i} for i in df["location"].unique()],
                                 multi = True,
                                 value = ["Switzerland", "Germany"],
                                 className="dropdown"),
            
                    dcc.Dropdown(id='attributes',
                                 options = [{'label': "New cases per Million", 'value': "new_cases_per_million"},
                                            {'label': "New deaths per Million", 'value': "new_deaths_per_million"},
                                            {'label': "New Vaccinations per Million", 'value': "new_vaccinations_smoothed_per_million"}],
                                 multi = False,
                                 value = "new_cases_per_million",
                                 className="dropdown")
                ], className="selectionrow"),
            
                html.Br(),
            
                #Selektionstools auf der zweiten Zeile (nur Datepicker)
                html.Div(children=[
                    dcc.DatePickerRange(
                        id='datepicker',
                        min_date_allowed=date(2020, 1, 22),
                        start_date=date(2020, 1, 22),
                        max_date_allowed=newestDate,
                        end_date=newestDate,
                        ),
                ], className="selectionrow2"),
            
                #Zeile der Scattermatrix
                html.Div(children=[
                    dcc.Graph(id='scatter-matrix', figure = {}, responsive=True,
                              config={'displayModeBar': False}
                          )
                ], className="scatter-row"),
                
                #Zeile der Übersichts-Histogramme 
                #(Bevölkerungszahl, totale Fallzahl, totale Todesfälle)
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

            #rechte Spalte        
            html.Div(children = [
                    
                    #Erste Zeile mit Farbmatrix und horizontalem Histogramm
                    html.Div(children = [
                        dcc.Graph(id='colormatrix', figure = {}, style = {'display': 'inline-block'}, responsive=True,
                                  config={'displayModeBar': False}),
                        dcc.Graph(id='marginalhistA', figure = {}, style = {'display': 'inline-block'}, responsive=True,
                                  config={'displayModeBar': False}),
                    ], className="graphs"), 
                    
                    #Zweite Zeile mit vertikalem Histogramm und Adjazenzmatrix
                    html.Div(children = [
                        dcc.Graph(id='marginalhistB', figure = {}, style = {'display': 'inline-block'}, responsive=True,
                                  config={'displayModeBar': False}),
                        dcc.Graph(id='adjacency', figure = {}, style = {'display': 'inline-block'}, responsive=True,),
                    ], className="graphs"),
                ], className="graph-container"),
        ], className="container")
    
    
    #Content Tab2
    elif tab == 'tab-2':
        return html.Div(children = [
            
                #Linke Spalte
                html.Div(children = [
                html.H2("Selection"),
            
                #Selektionstools auf der ersten Zeile (nebeneinander abbgebildet)
                html.Div(children=[
                    dcc.Dropdown(id='country2',
                                 options = [{'label': i, 'value': i} for i in df["location"].unique()],
                                 multi = False,
                                 value = "Switzerland",
                                 className="dropdown"),
            
                    dcc.Dropdown(id='attributes2',
                                 options = [{'label': "New cases", 'value': "new_cases"},
                                            {'label': "New deaths", 'value': "new_deaths"},
                                            {'label': "Stringency Index", 'value': "stringency_index"}],
                                 multi = True,
                                 value = ["new_cases", "new_deaths"],
                                 className="dropdown")
                ], className="selectionrow"),
            
                html.Br(),
            
                #Selektionstools auf der zweiten Zeile (nur Datepicker)
                html.Div(children=[
                    dcc.DatePickerRange(
                        id='datepicker',
                        min_date_allowed=date(2020, 1, 22),
                        start_date=date(2020, 1, 22),
                        max_date_allowed=newestDate,
                        end_date=newestDate,
                        ),
                ], className="selectionrow2"),
            
                #Zeile der Scattermatrix
                html.Div(children=[
                    dcc.Graph(id='scatter-matrix2', figure = {}, responsive=True,
                              config={'displayModeBar': False}
                          )
                ], className="scatter-row"),
                
                #Zeile der Übersichts-Histogramme 
                #(Bevölkerungszahl, totale Fallzahl, totale Todesfälle)
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
        
            #rechte Spalte 
            html.Div(children = [
                
                    #Erste Zeile mit Farbmatrix und horizontalem Histogramm
                    html.Div(children = [
                        dcc.Graph(id='colormatrix2', figure = {}, style = {'display': 'inline-block'}, responsive=True,
                                  config={'displayModeBar': False}),
                        dcc.Graph(id='marginalhistA2', figure = {}, style = {'display': 'inline-block'}, responsive=True, 
                                  config={'displayModeBar': False}),
                    ], className="graphs"), 
                    
                    #Zweite Zeile mit vertikalem Histogramm und Adjazenzmatrix
                    html.Div(children = [
                        dcc.Graph(id='marginalhistB2', figure = {}, style = {'display': 'inline-block'},responsive=True,
                                  config={'displayModeBar': False}),
                        dcc.Graph(id='adjacency2', figure = {}, style = {'display': 'inline-block'}, responsive=True),
                    ], className="graphs"),
                ], className="graph-container"),
        ], className="container")
    
###Befüllen des Dash Gerüsts mit den Visualisierungen###

#Callback und nachfolgende Funktion für
#Tab1    
@app.callback(
    [Output(component_id='scatter-matrix', component_property='figure'),
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
)


def update_countries(country_slctd, date_slctd1, date_slctd2, attr_slctd):
    
    #Arbeitskopie der des Dataframe erstellen
    dff = df.copy()
    
    #Eingrenzung desDataframes auf die ausgewählten Länder
    dff = dff[dff["location"].isin(country_slctd)]
    
    #Eingrenzen der Zeitserie anhand der beiden Werte aus dem Datepicker
    dff = dff[dff["date"] >= date_slctd1]
    dff = dff[dff["date"] <= date_slctd2]
    
    
    #Scattermatrix die drei dargestellten Attribute werden als Dimensionen übergeben
    fig1 = px.scatter_matrix(dff,
        dimensions=["new_cases", "new_deaths", "new_vaccinations"],
        color='location', template='plotly_white')
     
    #Mit Clickmode können einzelne Punkte vervorgehoben werden                     
    fig1.update_layout(clickmode='event+select', margin=dict(l=2, r=5, t=10, b=0))
   
    
    #Für die drei Übersichtshistogramme muss das Datum auf das aktuellste eingegrenzt werden.
    #Dies verhindert, das die bereits summierten Werte in den einzelnen Zeilen im Dataframe  
    #erneut zusammengezählt werden
    newestDateP = dff["date"].max() 
    dffP = dff[dff["date"] == newestDateP]
    dffP = dffP.filter(["location", "population", "population_density", "total_cases", "total_deaths"])
    
    #Die drei Histogramme
    #Jeweils anschliessend die Anpassungen am Layout. Randbreite, Verstecken der Achsentitel.
    
    #Erstes Histogramm "Population"
    fig2 = px.histogram(dffP, x="location", y="population", 
                        color="location", title="Population", template='plotly_white')
    #Anpassungen
    fig2.update_layout(showlegend=False, 
        margin=dict(l=2, r=5, t=35, b=0))
    fig2.update_xaxes(title='', visible=True, showticklabels=True)
    fig2.update_yaxes(title='', visible=True, showticklabels=True)
    
    #Zweites Histogramm "Total Cases"
    fig3 = px.histogram(dffP, x="location", y="total_cases", 
                        color="location", title="Total Cases", template='plotly_white')
    #Anpassungen
    fig3.update_layout(showlegend=False,
        margin=dict(l=2, r=5, t=35, b=0))
    fig3.update_xaxes(title='', visible=True, showticklabels=True)
    fig3.update_yaxes(title='', visible=True, showticklabels=True)
    
    #Drittes Histogramm "Total Deaths"
    fig4 = px.histogram(dffP, x="location", y="total_deaths", 
                        color="location", title="Total Deaths", template='plotly_white')
    #Anpassungen
    fig4.update_layout(showlegend=False,
        margin=dict(l=2, r=5, t=35, b=0))
    fig4.update_xaxes(title='', visible=True, showticklabels=True)
    fig4.update_yaxes(title='', visible=True, showticklabels=True)
    

    ### Datenverarbeitung für Adjazenzmatrix ###
   
    #Je nach ausgewähltem Attribut wird der Dataframe zu einem Farbwert-Array umgebaut.
    
    if  attr_slctd == "new_cases_per_million":
        #Dataframe wird auf die drei benötigten Spalten reduziert
        dff2 = dff.filter(["date", "new_cases_per_million", "location"])
        
        #Als nächstes wird der Dataframe so halbiert, 
        #dass dffA alle Werte des einen Landes enthält
        #und dffB alle Werte des anderen Landes.
        dffA = dff2[dff2['location'] == country_slctd[0]]
    
        dffB = dff2[dff2['location'] == country_slctd[1]]

        #Die beiden Teile werden so zusammengesetzt, dass die Attributwerte der beiden Länder
        #schliesslich in zwei unterschiedlichen Spalten (_A & _B) aufgeführt sind
        combi = dffA.merge(dffB, left_on="date", right_on="date", how="outer", suffixes=("_A", "_B"))

        #Nun wird auch die Datumsspalte nicht mehr benötigt. Nur noch die Attributswerte sind wichtig.
        combibi = combi.filter(['new_cases_per_million_A', 'new_cases_per_million_B'])
        
        #Der Dataframe wird in ein Array umgewandelt
        matrixarrayA = combibi.to_numpy(dtype=int)
        
        #Versuch negative Werte zu neutralisieren (fehlgeschlagen)
        matrixarrayA = np.where(matrixarrayA < 0, 0, matrixarrayA)

        
    #Gleiches Vorgehen auch für die anderen auswählbaren Attribute...       
    elif attr_slctd == "new_deaths_per_million":
        dff2 = dff.filter(["date", "new_deaths_per_million", "location"])
        
        dffA = dff2[dff2['location'] == country_slctd[0]]
    
        dffB = dff2[dff2['location'] == country_slctd[1]]
        
        combi = dffA.merge(dffB, left_on="date", right_on="date", how="outer", suffixes=("_A", "_B"))

        
        combibi = combi.filter(['new_deaths_per_million_A', 'new_deaths_per_million_B'])
        matrixarrayA = combibi.to_numpy(dtype=int)
        matrixarrayA = np.where(matrixarrayA<0, 0, matrixarrayA)
        

        
    elif attr_slctd == "new_vaccinations_smoothed_per_million":
        dff2 = dff.filter(["date", "new_vaccinations_smoothed_per_million", "location"])
        
        dffA = dff2[dff2['location'] == country_slctd[0]]
    
        dffB = dff2[dff2['location'] == country_slctd[1]]

        
        combi = dffA.merge(dffB, left_on="date", right_on="date", how="outer", suffixes=("_A", "_B"))

        
        combibi = combi.filter(['new_vaccinations_smoothed_per_million_A', 'new_vaccinations_smoothed_per_million_B'])
        matrixarrayA = combibi.to_numpy(dtype=int)
        matrixarrayA = np.where(matrixarrayA<0, 0, matrixarrayA)
    
    
    #Default-Einstellung, falls irgendetwas schief läuft,
    #werden wieder die Voreinstellungen aus der Attributselektion ausgegeben.
    else: 
        combibi = dff.filter(["date", "new_cases_per_million", "new_deaths_per_million", "location"])
        matrixarrayA = combibi.to_numpy(dtype=int)
        #matrixarray = np.where(matrixarray<0, 0, matrixarray)
        
        
    #Ermittlung des höchsten Werts im Array für die Einteilung in die Farbskala     
    attMax = matrixarrayA.max()
        
    #Aufgrund des höchsten Attributwerts werden die Intervalllängen bestimmt
    #Ein Intervall entspricht einer Feldnummer in der Farbskala
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
    #Die Schleifen schreiben den jeweiligen RGB-Farbwert, welcher sich an der Stelle im bivarray befindet 
    #die den Koordinaten aus colcoor entspricht, in eine Liste
    #valcollist -> value-color-list
    valcollist = []

    for x in colcoor:
        for y in x:
            a = y[0]
            b = y[1]
            valcollist.append(bivarray[a][b])


    #Bereinigen der erstellten Liste, so dass nur noch die Farbwerte im Array stehen
    valcollist2 = [list(i) for i in valcollist]

    #Umformen der Liste in ein 3D-Array
    valcolors = np.array(valcollist2).reshape(lA,lA,3)
    
    #Erstellen des ersten marginalen Histogramms unter Verwendung des Dataframes dffB
    #der noch Datum und die Attributwerte des einzelnen Landes enthält
    fig5 = px.histogram(dffB, x="date", y=dffB.columns[1], template='plotly_white',
                        height=100, width=550,
                        #Definition eines automatisch generierten Diagramm-Titels
                        #"Series of <Land> for <Attribut>"
                        labels={    
                            "date": "Series of " + dffB["location"].iloc[0] + " for " + attr_slctd}
                        )
    #Verschiedene Anpassungen bezüglich Anzeige und Layout
    fig5.update_xaxes(type='category', tickangle=90)
    fig5.update_yaxes(visible=False, showticklabels=False)
    fig5.update_layout(
        xaxis={"mirror" : "all", 'side': 'top'}, 
        yaxis={"mirror" : "all", 'side': 'right'},
        margin=dict(l=20, r=20, t=2, b=2)
        )
    

    #Implementieren der Farbskala in das Dashboard
    img = io.imread('farbskala3.png')
    
    fig6 = px.imshow(img, height=100, width=100)
    fig6.update_xaxes(visible=False, showticklabels=False, automargin=True)
    fig6.update_yaxes(visible=False, showticklabels=False, automargin=True)
    fig6.update_layout(margin=dict(l=5, r=5, t=10, b=5))

    #Erstellen des zweiten marginalen Histogramms unter Verwendung des Dataframes dffA
    #x und y sind vertauscht um die Ausrichtung zu ändern
    fig7 = px.histogram(dffA, x=dffA.columns[1], y="date", template='plotly_white',
                        orientation='h', height=550, width=100,
                        color_discrete_map={"new_cases":'rgb(232, 78, 27)'},
                        labels={
                            "date": "Series of " + dffA["location"].iloc[0] + " for " + attr_slctd})
    
    #Anpassungen um den Nullpunkt oben rechts zu setzen. 
    #So laufen die Balken von rechts nach links und das älteste Datum ist oben
    fig7.update_yaxes(autorange="reversed", type='category')
    fig7.update_xaxes(autorange="reversed", visible=False, showticklabels=False)
    fig7.update_layout(
            #Anpassungen für die Beschriftung, keinen Einfluss auf die Balken
            xaxis={"mirror" : "all", 'side': 'bottom'}, 
            yaxis={"mirror" : True, 'side': 'left'},
            margin=dict(l=2, r=5, t=2, b=5)
        )
    
    
    #Das Herzstück, die Adjazenzmatrix. 
    #Das dreidimensionale Array valcolors wird als Bild ausgegeben
    fig8 = px.imshow(valcolors, width=550, height=550, template='plotly_white')
    fig8.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
    fig8.update_yaxes(showticklabels=False, showgrid=False, zeroline=False)
    fig8.update_layout(
        margin=dict(l=2, r=2, t=10, b=5))


    
    return fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8


#Callback und nachfolgende Funktion für
#Tab2
@app.callback(
    [Output(component_id='scatter-matrix2', component_property='figure'),
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
    
    #Eingrenzung desDataframes auf die ausgewählten Länder
    dff = dff[dff["location"] == country_slctd]
    
    #Eingrenzen der Zeitserie
    dff = dff[dff["date"] >= date_slctd1]
    dff = dff[dff["date"] <= date_slctd2]
    
    
    #Scattermatrix, die drei dargestellten Attribute werden als Dimensionen übergeben
    fig1 = px.scatter_matrix(dff,
        dimensions=["new_cases", "new_deaths", "new_vaccinations"],
        template='plotly_white',
        color='location')
    
    #Mit Clickmode können einzelne Punkte vervorgehoben werden                       
    fig1.update_layout(clickmode='event+select', margin=dict(l=2, r=5, t=10, b=0))
   
    
    #Für die drei Übersichtshistogramme muss das Datum auf das aktuellste eingegrenzt werden.
    #Dies verhindert, das die bereits summierten Werte in den einzelnen Zeilen im Dataframe  
    #erneut zusammengezählt werden
    newestDateP = dff["date"].max() 
    dffP = dff[dff["date"] == newestDateP]
    dffP = dffP.filter(["location", "population", "population_density", "total_cases", "total_deaths"])
    
    #Die drei Histogramme
    #Jeweils anschliessend die Anpassungen am Layout. Randbreite, Verstecken der Achsentitel.
    
    #Erstes Histogramm "Population"
    fig2 = px.histogram(dffP, x="location", y="population", template='plotly_white',
                        color="location", title="Population")
    #Anpassungen
    fig2.update_layout(showlegend=False, 
        margin=dict(l=2, r=5, t=35, b=0))
    fig2.update_xaxes(title='', visible=True, showticklabels=True)
    fig2.update_yaxes(title='', visible=True, showticklabels=True)
    
    #Zweites Histogramm "Total Cases"
    fig3 = px.histogram(dffP, x="location", y="total_cases",template='plotly_white',
                        color="location", title="Total Cases")
    #Anpassungen
    fig3.update_layout(showlegend=False,
        margin=dict(l=2, r=5, t=35, b=0))
    fig3.update_xaxes(title='', visible=True, showticklabels=True)
    fig3.update_yaxes(title='', visible=True, showticklabels=True)
    
    #Drittes Histogramm "Total Deaths"
    fig4 = px.histogram(dffP, x="location", y="total_deaths", template='plotly_white',
                        color="location", title="Total Deaths")
    #Anpassungen
    fig4.update_layout(showlegend=False,
        margin=dict(l=2, r=5, t=35, b=0))
    fig4.update_xaxes(title='', visible=True, showticklabels=True)
    fig4.update_yaxes(title='', visible=True, showticklabels=True)
   
    
    ### Datenverarbeitung für Adjazenzmatrix ###
   
    #Je nach ausgewählten Attributen in attr_slctd wird der Dataframe zu einem Farbwert-Array umgebaut.
    if  "new_cases" in attr_slctd:
        if "new_deaths" in attr_slctd:
            #Dataframe wird auf die vier benötigten Spalten reduziert
            combi = dff.filter(["date", "new_cases","new_deaths", "location"])
            
            #Die Liste attrNames wird später für die Achsenbeschriftung der
            #Visualisierungen verwendet
            attrNames = ["new_cases", "new_deaths"]
            
            #Bestimmung der höchsten Attributwerte je Spalte
            attMaxA = combi["new_cases"].max()
            attMaxB = combi["new_deaths"].max()
            
            #Aufgrund den höchsten Attributwerten werden die Intervalllängen bestimmt
            #Ein Intervall entspricht einer Feldnummer in der Farbskala
            intervalstepA = attMaxA/200
            intervalstepB = attMaxB/200
            
            #Erstellen zweier einzelner Matrixarrays, werden später zusammengeführt
            matrixarrayA = combi["new_cases"].to_numpy(dtype=int)
            matrixarrayB = combi["new_deaths"].to_numpy(dtype=int)


        #Gleiches Vorgehen auch für die anderen auswählbaren Attributkombinationen...



        elif "stringency_index" in attr_slctd:
            combi = dff.filter(["date", "new_cases", "stringency_index", "location"])
            
            attrNames = ["new_cases", "stringency_index"]
            
            attMaxA = combi["new_cases"].max()
            #attMaxB = combi["stringency_index"].max()
        
            intervalstepA = attMaxA/200
            #intervalstepB = attMaxB/200
            
            #Beim Stringency Index wird der allgemein höchstmögliche Wert verwendet
            intervalstepB = 100/200
            
            matrixarrayA = combi["new_cases"].to_numpy(dtype=int)
            matrixarrayB = combi["stringency_index"].to_numpy(dtype=int)
 
    
    elif "stringency_index" in attr_slctd:
        if "new_deaths" in attr_slctd:
            combi = dff.filter(["date", "new_deaths", "stringency_index", "location"])
            
            attrNames = [ "new_deaths", "stringency_index"]
            
            attMaxA = combi["new_deaths"].max()
            attMaxB = combi["stringency_index"].max()
        
            intervalstepA = attMaxA/200
            intervalstepB = attMaxB/200
            
            matrixarrayA = combi["new_deaths"].to_numpy(dtype=int)
            matrixarrayB = combi["stringency_index"].to_numpy(dtype=int)
  
    
    
    #Default-Einstellung, falls irgendetwas schief läuft,
    #werden wieder die Voreinstellungen aus der Attributselektion ausgegeben.
    else: 
            combi = dff.filter(["date", "new_cases","new_deaths", "location"])
            
            attrNames = ["new_cases", "new_deaths"]
            
            attMaxA = combi["new_cases"].max()
            attMaxB = combi["new_deaths"].max()
        
            intervalstepA = attMaxA/200
            intervalstepB = attMaxB/200
            
            matrixarrayA = combi["new_cases"].to_numpy(dtype=int)
            matrixarrayB = combi["new_deaths"].to_numpy(dtype=int)
        
        
    

    #colarr für Color-Array. Die Farbkoordinaten aus der zuvor definierten Funktion 
    #set_interval_value() als einzelne Werte.
    colarrA = np.array(set_color_coordinatesA(matrixarrayA, intervalstepA))
    colarrB = np.array(set_color_coordinatesB(matrixarrayB, intervalstepB))

    # Halbe Länge des Arrays entspricht nachher der Länge einer Achse lA
    #lA muss zusätzlich als Integer definiert werden
    lA = len(colarrA)
    lA = int(lA)

    #Erstellt eine Liste mit den Koordinatenpaaren. 
    #Alle Einzelkoordinaten von AttributA mit allen Einzelkoordinaten von AttributB
    colcoor = [[a, b] for a in colarrA 
                      for b in colarrB] 
                         
    #Umformen der Liste zu einem Array und der Anordnung für X- und Y-Achse
    colcoor = np.array(colcoor)
    colcoor = colcoor.reshape(lA,lA,2)

    #Umformen des Farbarrays aus der Farbmatrix zu einem 3D-Array
    bivarray = newarr.reshape(200, 200, 3)

    #Erstellen einer Liste mit den Farben, die für die Visualisierung benötigt werden
    #Die Schleifen schreiben den jeweiligen RGB-Farbwert, welcher sich an der Stelle im bivarray befindet 
    #die den Koordinaten aus colcoor entspricht, in eine Liste
    #valcollist -> value-color-list
    valcollist = []

    for x in colcoor:
        for y in x:
            a = y[0]
            b = y[1]
            valcollist.append(bivarray[a][b])


    #Bereinigen der erstellten Liste, so dass nur noch die Farbwerte im Array stehen
    valcollist2 = [list(i) for i in valcollist]

    #Umformen der Liste in ein 3D-Array
    valcolors = np.array(valcollist2).reshape(lA,lA,3)
    
    #Erstellen des ersten marginalen Histogramms unter Verwendung des Dataframes Combi   
    fig5 = px.histogram(combi, x="date", y=combi.columns[2], template='plotly_white',
                        height=100, width=550,
                        #Definition eines automatisch generierten Diagramm-Titels
                        #"Series of <Land> for <Attribut>"
                        labels={
                            "date": "Series of " + combi["location"].iloc[0] + " for " + attrNames[1]}
                        )
    #Verschiedene Anpassungen bezüglich Anzeige und Layout
    fig5.update_xaxes(type='category', tickangle=90)
    fig5.update_yaxes(visible=False, showticklabels=False)
    fig5.update_layout(
        xaxis={"mirror" : "all", 'side': 'top'}, 
        yaxis={"mirror" : "all", 'side': 'right'},
        margin=dict(l=20, r=20, t=2, b=2)
        )
    
    #Implementieren der Farbskala in das Dashboard
    img = io.imread('farbskala3.png')
    fig6 = px.imshow(img, height=100, width=100)
    fig6.update_xaxes(visible=False, showticklabels=False, automargin=True)
    fig6.update_yaxes(visible=False, showticklabels=False, automargin=True)
    fig6.update_layout(margin=dict(l=5, r=5, t=10, b=5))

    #Erstellen des zweiten marginalen Histogramms unter Verwendung des Dataframes Combi
    #x und y sind vertauscht um die Ausrichtung zu ändern
    fig7 = px.histogram(combi, x=combi.columns[1], y="date", template='plotly_white',
                        orientation='h', height=550, width=100, 
                        color_discrete_map={"new_cases":'rgb(232, 78, 27)'},
                        labels={
                            "date": "Series of " + combi["location"].iloc[0] + " for " + attrNames[0]})
    #Anpassungen um den Nullpunkt oben rechts zu setzen. 
    #So laufen die Balken von rechts nach links und das älteste Datum ist oben
    fig7.update_yaxes(autorange="reversed", type='category')
    fig7.update_xaxes(autorange="reversed", visible=False, showticklabels=False)
    fig7.update_layout(
            #Anpassungen für die Beschriftung, keinen Einfluss auf die Balken
            xaxis={"mirror" : "all", 'side': 'bottom'}, 
            yaxis={"mirror" : True, 'side': 'left'},
            margin=dict(l=2, r=5, t=2, b=5)
        )
    
    #Das Herzstück, die Adjazenzmatrix. 
    #Das dreidimensionale Array valcolors wird als Bild ausgegeben
    fig8 = px.imshow(valcolors, width=550, height=550, template='plotly_white')
    fig8.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
    fig8.update_yaxes(showticklabels=False, showgrid=False, zeroline=False)
    fig8.update_layout(
         margin=dict(l=0, r=0, t=10, b=5))


    
    return fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8



if __name__ == '__main__':
    app.run_server(debug=False)
