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
# import pepega.lib
import socket
from attr import define
import geopandas as gpd
import matplotlib.pyplot as plt, mpld3
from mpld3 import fig_to_html, plugins

import os
import json
from numpy import empty
from shapely import geometry
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes, mark_inset

from flask import Flask, render_template, Response, request, redirect, url_for, jsonify

app = Flask(__name__)


# rendering the HTML page which has the button
@app.route('/')
def home():
    # hostname = socket.gethostname()
    # local_ip = socket.gethostbyname(hostname)

    return render_template('home_legacy.html', local_ip="127.0.0.1")


# background process happening without any refreshing
@app.route('/background_process', methods=['GET', 'POST'])
def background_process_test():
    if request.method == "POST":

        df_places = gpd.read_file('maps/Lisboa.geojson')
        directory = "./archives"
        ext = ".geojson"
        lista = []
        plt.rcParams['figure.figsize'] = (7, 7)  # setting parameters
        listadirs = []
        dic = {}
        filtro = request.form['filter']
        condition = filtro.split(",")
        filtro = json.loads(filtro) if condition[0] != "99" else "99"
        filtrolist = []
        # sizex = request.form['width']
        # sizey = 700
        # because python is a garbage language
        try:
            zone = request.form['zone']

        except:
            zone = ""
        curr = 0
        limit = len(filtro) if filtro != '99' else 1
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
                            # needs to be fixed tomorrow
                            if filtro[curr].find(file.replace(".geojson", "")) != -1:
                                ficheiro = os.path.join(root, file)
                                lista.append(gpd.read_file(ficheiro))

            for k, v in dic.items():
                for value in v:
                    if value.find(filtro[curr]) != -1:
                        filtrolist.append(k)
            curr += 1

        if filtro != '99':
            '''Choropleth with Points of Filter'''

            listafilter = []
            listafilted = []
            count = []
            number = []

            df_places.NOME = sorted(df_places.NOME)

            for b in range(0, len(lista)):
                for idx, row in lista[b].iterrows():
                    listafilter.append(row.geometry)

                for ele in listafilter:
                    if ele != None:
                        listafilted.append(ele)

                for a in listafilted:
                    for idx1, row1 in df_places.iterrows():
                        if a.intersects(row1.geometry) == True:
                            count.append(row1.NOME)

                for a in df_places.NOME:
                    numb = count.count(a)
                    number.append(numb)

                for a in range(0, len(number)):
                    number[a] = int(number[a])

                filtrolist[b] = number
                print(type(number))

                listafilter = []
                listafilted = []
                count = []
                number = []

            # df_places.GlobalID=number

            fig, ax = plt.subplots()
            lista[0].plot(ax=ax, edgecolor="black", color="yellow", zorder=2)
            axis = df_places.plot(ax=ax, edgecolor="black", column=df_places.GlobalID, cmap="YlOrRd", zorder=1)

            for idx, row in df_places.iterrows():
                coord = row['geometry'].centroid
                coordinates = coord.coords.xy

                x, y = coordinates[0][0], coordinates[1][0]
                axis.annotate(row['NOME'], xy=(x, y), xytext=(x, y), font="Tahoma")
            sum = 0
            df_places.NOME = sorted(df_places.NOME)
            for a in range(0, len(filtrolist)):
                print(a)
                for b in range(0, len(filtrolist[a])):
                    sum += filtrolist[a][b]
                for b in range(0, len(filtrolist[a])):
                    filtrolist[a][b] = filtrolist[a][b] / sum

                sum = 0

            choropleth = []
            for a in range(0, len(filtrolist[0])):
                for b in range(0, len(filtrolist)):
                    sum += filtrolist[b][a]

                # print(sum)
                choropleth.append(sum)
                sum = 0

            print(choropleth)

            df_places["Censos 2021 População Lisboa_field_4"] = choropleth
            c = 2
            fig, ax = plt.subplots()
            for a in lista:
                c += 1
                a.plot(ax=ax, zorder=c)

            axis = df_places.plot(ax=ax, edgecolor="black", column="Censos 2021 População Lisboa_field_4",
                                  cmap="YlOrRd", zorder=1)

            for idx, row in df_places.iterrows():
                coord = row['geometry'].centroid
                coordinates = coord.coords.xy

                x, y = coordinates[0][0], coordinates[1][0]
                axis.annotate(row['NOME'], xy=(x, y), xytext=(x, y), font="Tahoma")

            plt.margins(x=0)
            ax.margins(x=0)
            # Set whitespace to 0
            plt.subplots_adjust(left=0,right=1,bottom=0,top=1)
            ax.axis('tight')

            html_str = mpld3.fig_to_html(fig, figid="Jiro")
            Html_file = open("./static/graph.html", "w")
            Html_file.write(html_str)
            Html_file.close()

            # wtf = df_places.explore(column="Censos 2021 População Lisboa_POPULACAO RESIDENTE", cmap='YlOrRd')
            # a = "./static/graph.html"
            # wtf.save(a)

        json_object = dic

        return jsonify(data=json_object, status=200)

    elif request.method == "GET":
        df_places = gpd.read_file('maps/Lisboa.geojson')
        df_places.NOME = sorted(df_places.NOME)
        listname = df_places.NOME.tolist()
        listname = ",".join(listname)
        return listname
