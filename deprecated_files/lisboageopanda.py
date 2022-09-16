import geopandas as gpd
import matplotlib.pyplot as plt, mpld3
import os
from shapely import geometry
fig, ax = plt.subplots(1,1)

plt.rcParams['figure.figsize'] = (20, 10)
df_places = gpd.read_file('./Lisboa.geojson')

axis = df_places.plot(ax=ax,color="lightblue",edgecolor = "black",figsize = (40,20))

for idx, row in df_places.iterrows():
    #print(row['geometry'].exterior.coords[1])
    coord = row['geometry'].centroid
    coordinates = coord.coords.xy

    #print(row['geometry'].centroid.wkt.replace('POINT ',''))
    x, y = coordinates[0][0], coordinates[1][0]
    #axis.scatter(x, y, s=10, color='red')
    axis.annotate(row['NOME'], xy=(x, y), xytext=(x, y))  
                       
directory = "./archives"
ext = ".geojson"
lista=[]
listadirs=[]
dic={}

def leitura(filtro):
    i=0
    global lista, listadirs, dic
    listafiles=[]
    for root, dirs, files in os.walk(directory):
        
        if len(dirs) > 0:
            listadirs = dirs

        if len(files) > 0:
            for value in files:
                listafiles.append(root.replace("/", "\\")+"\\"+value.replace("/","\\"))

            dic[listadirs[i]] = listafiles
            listafiles = []
            i+=1    
        
        for file in files:
            if file.endswith(ext):
                if filtro is not None:
                    if filtro.find(file.replace(".geojson","")) != -1:
                        ficheiro = os.path.join(root, file)
                        lista.append(gpd.read_file(ficheiro))

def pprint():
    for k,v in dic.items():
        print(k+":")
        for value in v:
            print("       "+ value)

leitura(None)
pprint()

a = "Amb_EcopontosSubterraneos.geojson"
leitura(a)


    
fig, ax = plt.subplots(1,1)
ax.set_aspect('equal')
axis = df_places.plot(ax=ax, color="lightblue",edgecolor = "black")
for idx, row in df_places.iterrows():
    #print(row['geometry'].exterior.coords[1])
    coord = row['geometry'].centroid
    coordinates = coord.coords.xy

    #print(row['geometry'].centroid.wkt.replace('POINT ',''))
    x, y = coordinates[0][0], coordinates[1][0]
    #axis.scatter(x, y, s=10, color='red')
    axis.annotate(row['NOME'], xy=(x, y), xytext=(x, y))  
for a in lista:
    a.plot(ax=ax, color='white', edgecolor='black', legend=True)
        
plt.show()
