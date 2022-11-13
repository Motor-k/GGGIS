"""
This program is kind of a middleware responsible for handling web requests and providing sort of an API
It can serve template web pages
It can draw charts and refresh the local element without having to redraw or reload the entire page
It can recieve requests for filters and draw only those elements
"""
import io
import base64
from logging import exception
# import flask

import socket
from attr import define
import geopandas as gpd
import matplotlib.pyplot as plt, mpld3
from mpld3 import fig_to_html, plugins

import functions
import os
import json
from numpy import empty
from shapely import geometry
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes, mark_inset

from flask import Flask, render_template, Response, request, redirect, url_for, jsonify
import random

app = Flask(__name__)


# rendering the HTML page which has the button
@app.route('/home')
def home():
    # hostname = socket.gethostname()
    # local_ip = socket.gethostbyname(hostname)

    return render_template('home.html', local_ip="127.0.0.1")


# background process happening without any refreshing
@app.route('/background_process_test', methods=['GET', 'POST'])
def background_process_test():
    if request.method == "POST":

        directory = "./archives"
        ext = ".geojson"
        lista = []
        listadirs = []
        fp = {}
        dic = {}
        filtro = request.form['filter']
        mode = bool(request.form['mode'])
        print(mode)
        condition = filtro.split(",")
        filtro = json.loads(filtro) if condition[0] != "99" else "99"
        filtrolist = []
        # sizex = request.form['width']
        # sizey = 700
        # because python is a garbage language
        try:
            importance = request.form['importance']
        except:
            importance = {}
        try:
            zone = request.form['zone']
        except:
            zone = ""
        curr = 0
        limit = 1
        while curr < limit:
            i = 0
            listafiles = []
            for root, dirs, files in os.walk(directory):

                if len(dirs) > 0:
                    listadirs = dirs

                if len(files) > 0:
                    for value in files:
                        listafiles.append(root.replace("/", "\\") + "\\" + value.replace("/", "\\"))

                    dic[listadirs[i]] = listafiles
                    listafiles = []
                    i += 1

                for file in files:
                    if file.endswith(ext):
                        if filtro[curr] is not None:

                            if filtro[curr].find(file.replace(".geojson", "")) != -1 and len(filtro[curr]) == len(
                                    file.replace(".geojson", "")):
                                ficheiro = os.path.join(root, file)
                                filtrolist.append(filtro[curr])
                                lista.append(gpd.read_file(ficheiro))

            curr += 1

        if filtro != '99':
            lista = []
            filtrolist = []
            lista, filtrolist = functions.readdirectory("./archives", ".geojson", *[a for a in filtro])
            ListMapsRead = functions.readdirectory("./maps", ".geojson")

            '''Choropleth with Points of Filter'''

            geopoints = []
            geopointsfiltered = []
            geopointsforexplore = {}
            count = []
            total = []
            importance2 = {}
            
            for a in range(0,len(filtrolist)):
    
                importance2[str(filtrolist[a]).replace('.geojson','')] = int(importance[importance.find(str(filtrolist[a]).replace('.geojson', '')+'"') + len(str(filtrolist[a]).replace('.geojson', ''))+3])

            # organizing the names

            for b in range(0, len(lista)):

                # append da geometry de filtro por filtro
                for idx, row in lista[b].iterrows():
                    geopoints.append(row.geometry)

                for ele in geopoints:
                    if ele is not None:
                        geopointsfiltered.append(ele)

                # FOR para analisar a intesecção dos pontos com as regiões
                for a in geopointsfiltered:
                    for idx1, row1 in ListMapsRead[0].iterrows():
                        if a.intersects(row1.geometry):
                            count.append(row1.NOME)
                            # append em count da repetição das localidades

                # for para analisar a contagem dos pontos de cada regiao realizando um append a "total"
                for a in ListMapsRead[0].NOME:
                    numb = count.count(a)
                    total.append(numb)
                    print(total)

                # transformação para int
                for a in range(len(total)):
                    total[a] = float(total[a])

               
                fp[filtrolist[b]] = total

                geopointsforexplore[filtrolist[b]] = geopointsfiltered
                geopoints = []
                geopointsfiltered = []
                count = []
                total = []

                # df_places.GlobalID=number

                sum = 0
            # organizing the names of Lisboa
            ListMapsRead[0].NOME = sorted(ListMapsRead[0].NOME)

            # soma todos os pontos e dps divide pela quantidade total
            for a in range(len(filtrolist)):
                for b in range(0, len(fp[filtrolist[a]])):
                    sum += fp[filtrolist[a]][b]

                for b in range(0, len(fp[filtrolist[a]])):
                    
                    if str(filtrolist[a]).replace('.geojson','') in importance2.keys(): 
                        fp[filtrolist[a]][b] = (fp[filtrolist[a]][b] / sum) * float(importance2[str(filtrolist[a]).replace('.geojson', '')])
                    else:
                        fp[filtrolist[a]][b] = (fp[filtrolist[a]][b] / sum) 
                sum = 0

            choropleth = []
            # soma dos pontos das mesmas regioes
            for a in range(len(fp[filtrolist[0]])):
                for b in range(0, len(filtrolist)):
                    sum += fp[filtrolist[b]][a]

                # print(sum)
                choropleth.append(sum)
                sum = 0

            ListMapsRead[0]["Censos 2021 População Lisboa_field_4"] = choropleth

            if mode == True:

                color = []

                for i in range(len(lista)):
                    color.append('#%06X' % random.randint(0, 0xFFFFFF))

                plot2 = ListMapsRead[0].explore(column="Censos 2021 População Lisboa_field_4",
                                          cmap='YlOrRd', style_kwds=dict(color="black"))

                for a in range(len(lista)):
                    axa = random.randint(0, len(color) - 1)
                    lista[a] = lista[a][lista[a].geometry != None]
                    d = {'name': filtrolist[a].replace('.geojson', ''), 'geometry': lista[a].geometry}
                    gdf = gpd.GeoDataFrame(d, crs="EPSG:4326")
                    gdf.explore(m=plot2,
                                color=color.pop(axa),
                                style_kwds=dict(weight=9),
                                popup=True)
                for a in range(1, len(ListMapsRead)):
                    ListMapsRead[a].explore(m=plot2)
                plot2.save("./static/graph.html")



            elif mode == False:

                c = 2
                fig, ax = plt.subplots()
                for a in lista:
                    c += 1
                    a.plot(ax=ax, zorder=c)

                axis = ListMapsRead[0].plot(ax=ax, edgecolor="black", column="Censos 2021 População Lisboa_field_4",
                                      cmap="YlOrRd", zorder=1)

                for idx, row in ListMapsRead[0].iterrows():
                    coord = row['geometry'].centroid
                    coordinates = coord.coords.xy

                    x, y = coordinates[0][0], coordinates[1][0]
                    axis.annotate(row['NOME'], xy=(x, y), xytext=(x, y), font="Tahoma")

                html_str = mpld3.fig_to_html(fig, no_extras=True, figid="Jiro")
                Html_file = open("./static/graph.html", "w")
                Html_file.write(html_str)
                Html_file.close()

            # wtf = df_places.explore(column="Censos 2021 População Lisboa_POPULACAO RESIDENTE", cmap='YlOrRd')
            # a = "./static/graph.html"
            # wtf.save(a)

        json_object = dic

        return jsonify(data=json_object, status=200)
    #only works on Lisboa for now
    elif request.method == "GET":
        df_places = gpd.read_file('maps/Lisboa.geojson')
        df_places.NOME = sorted(df_places.NOME)
        listname = df_places.NOME.tolist()
        listname = ",".join(listname)
        return listname

@app.route('/save_file_geojson', methods=['POST'])
def save_file_geojson():
    try:
        mapdata = request.form['mapdata']
        zone = request.form['name']
        with open("./maps/"+zone+".geojson", "w") as fo:
                fo.write(mapdata)
    except:
        return 'File could not be saved due to missing or incorrect data'

    return 'File saved successfully'