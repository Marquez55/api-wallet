

def renameKey(listado, keyUpdate):

    lista = []
    for el in listado:
        lista.append(obtenerValores(el, 'user__'))

    return lista


def obtenerValores(data,  keys_transform):
    valores = {}
    for key in data.keys():
        valores[key.replace(keys_transform, '')] = data[key]
    return valores
