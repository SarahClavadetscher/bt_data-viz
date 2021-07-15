# -*- coding: utf-8 -*-
"""
Created on Tue May 25 15:10:59 2021

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

df = pd.read_csv("https://covid.ourworldindata.org/data/owid-covid-data.csv")

dff = df.copy()

    
#leere Zellen ersetzen
dff.replace('', 0, inplace=True)
dff.replace(np.NaN, 0, inplace=True) 

dff= dff[dff["date"] > "2021-06-01"]

#Attribut Neue Fälle für Deutschland 
newCasesGER = dff[dff["location"] == "Germany"]
newCasesGER = newCasesGER.filter(['date', 'new_cases', 'location'])


#Attribut Neue Fälle für die Schweiz
newCasesSUI = dff[dff["location"] == "Switzerland"] 
newCasesSUI = newCasesSUI.filter(['date', 'new_cases', 'location'])
    
#Left Outer Join zum kombinieren der beiden Länder Attribute mit den gemeinsamen Tagen
combi = newCasesGER.merge(newCasesSUI, left_on="date", right_on="date", how="outer", suffixes=("_GER", "_SUI"))


combibi = combi.filter(['new_cases_GER', 'new_cases_SUI'])




#Farbskala erstellen
img = io.imread('C:\\Users\\Sarah\\Documents\\Studium\\_BT\\farbskala\\farbskala1.png')

img_arr = np.array(img)


newarr= img_arr.reshape(-1, 3)


def bivariate_colors(newarr):
    
    n_colors = len(newarr)
    index = set(range(n_colors))

    biv_colors = []
    for c in newarr:
        biv_colors.append(f'rgb{tuple(c)}')
        
    return biv_colors

biv_colors = bivariate_colors(newarr)

#print(biv_colors)

matrixarray = combibi.to_numpy(dtype=int)



#Farbkoordinaten zu den Attriut-Werten bestimmen
attMax = matrixarray.max()
        
intervalstep = attMax/200
    
def set_color_coordinates():
    n = intervalstep
    m = 1
    collist = []

    for x in np.nditer(matrixarray):
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

#colarr für Color-Array. Die Farbkoordinaten aus der zuvor definierten Funktion 
#set_interval_value() als einzelne Werte.
colarr = np.array(set_color_coordinates())

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


app = dash.Dash(__name__)

app.layout = html.Div(children=[
    
    html.Div(children = [
    html.H1('COVID-19 Datenset'),
    html.P ('BT-Visualisierung'), ],
    className="header"),
    
    html.Div(children = [
        html.Div(children = [
            html.H2("Untertitel"),
            
            dcc.Dropdown(id='continent',
                options = [
                    {"label": "Nordamerika", "value": 'North America'},
                    {"label": "Südamerika", "value": 'South America'},
                    {"label": "Ozeanien", "value": 'Oceania'},
                    {"label": "Afrika", "value": 'Africa'},
                    {"label": "Europa", "value": 'Europe'},
                    {"label": "nicht zugeordnet", "value": 0},
                    {"label": "Asien", "value": 'Asia'}],
                multi = False,
                value = 'Europe',
                className="dropdown dropdown-list"),
                
                        
            dcc.Graph(id='crossfilter-scatter', figure = {})
            
        ], className="wrapper-list"),
        
    html.Div(children = [
        html.Div(children = [
                html.Div(id='output_container'),
                html.Br() ],
             className="dropdown-titles"),

        html.Div(children = [
                html.Div(children = [
                    dcc.Graph(id='colormatrix', figure = {}, style = {'display': 'inline-block'}),
                    dcc.Graph(id='marginalhist', figure = {}, style = {'display': 'inline-block'}),
                    ], className="graphs"), 

                    dcc.Graph(id='marginalhist2', figure = {}, style = {'display': 'inline-block'}),
                    dcc.Graph(id='adjacency', figure = {}, style = {'display': 'inline-block'}),
                    
                           
        ], className="wrapper-graphs"),
    ], className="graph-container"),
], className="container")
])
    
@app.callback(
    [Output(component_id='crossfilter-scatter', component_property='figure'),
     Output(component_id='marginalhist', component_property='figure'),
     Output(component_id='colormatrix', component_property='figure'),
     Output(component_id='marginalhist2', component_property='figure'),
     Output(component_id='adjacency', component_property='figure')],
     [Input(component_id='continent', component_property='value')]
)

def update_graph(option_slctd):
    print(option_slctd)
    print(type(option_slctd))
    


    fig1 = px.scatter_matrix(dff,
        dimensions=["total_cases", "hosp_patients", "new_cases", "new_vaccinations"],
        color='location')
    
    
    fig2 = px.histogram(combi, x="date", y="new_cases_SUI", 
                        #color_discrete_map={"date" : 'rgb(48, 38, 131)'},
                        width=700, height=300)
    fig2.update_xaxes(type='category')
    fig2.update_yaxes(visible=False, showticklabels=False)
    fig2.update_layout(
        xaxis={"mirror" : "all", 'side': 'top'}, 
        yaxis={"mirror" : "all", 'side': 'right'},
        margin=dict(l=20, r=20, t=20, b=20)
        )
    


    img = io.imread('C:\\Users\\Sarah\\Documents\\Studium\\_BT\\farbskala\\farbskala1.png')
    fig3 = px.imshow(img, width=300, height=300)


    fig4 = px.histogram(combi, x="new_cases_GER", y="date", 
                        orientation='h',
                        color_discrete_map={"new_cases_GER":'rgb(232, 78, 27)'},
                        width=300, height=700)
    fig4.update_yaxes(autorange="reversed", type='category')
    #fig4.update_xaxes(mirror=True, side='top')
    fig4.update_xaxes(autorange="reversed", visible=False, showticklabels=False)
    fig4.update_layout(
            #funktionieren nur bei der Beschriftung, keinen Einfluss auf die Balken
            xaxis={"mirror" : "all", 'side': 'bottom'}, 
            yaxis={"mirror" : True, 'side': 'left'},
            margin=dict(l=20, r=20, t=20, b=20)
        )
    
    

    fig5 = px.imshow(valcolors, width=700, height=700)
    fig5.update_xaxes(showticklabels=False)
    fig5.update_yaxes(showticklabels=False)
    fig5.update_layout(
        margin=dict(l=20, r=20, t=20, b=20))


    
    return fig1, fig2, fig3, fig4, fig5



if __name__ == '__main__':
    app.run_server(debug=False)