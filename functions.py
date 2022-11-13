import geopandas as gpd
import os


def readdirectory(directory, ext, *filtro):
    dic = {}
    lista = []
    filtrolist = []
    ListMapsReads = []
    i = 0
    listafiles = []
    for root, dirs, files in os.walk(directory):
        if directory == "./archives":
            if len(dirs) > 0:
                listadirs = dirs
            if len(files) > 0:
                for value in files:
                    listafiles.append(root.replace("/", "\\") + "\\" + value.replace("/", "\\"))

                dic[listadirs[i]] = listafiles
                listafiles = []
                i += 1
            for file in files:
                for filter in filtro:
                    if file.endswith(ext):
                        if filter is not None:

                            if filter.find(file.replace(".geojson", "")) != -1 and len(filter) == len(
                                    file.replace(".geojson", "")):
                                ficheiro = os.path.join(root, file)
                                filtrolist.append(filter)
                                lista.append(gpd.read_file(ficheiro))

        elif directory == "./maps":
            listadirs = ["maps"]
            if len(files) > 0:
                for value in files:
                    listafiles.append(root.replace("/", "\\") + "\\" + value.replace("/", "\\"))
                i += 1
            for file in files:
                if file.endswith(ext):
                    if len(listafiles) > 0:
                        ficheiro = os.path.join(root, file)
                        ListMapsReads.append(gpd.read_file(ficheiro))

    if len(lista) > 0 and len(filtrolist) > 0:
        return lista, filtrolist
    elif len(ListMapsReads) > 0:
        return ListMapsReads