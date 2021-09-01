#!/usr/bin/env python
# coding: utf-8

# # Creación de Dataset de Municipios de Colombia

# #### Tarea #1: Obtener la información para un municipio

# In[1]:


# Importar librerías principales

import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
import pickle


# In[3]:


# Cargar el contenido de la pagina web (Recurso: Wikipedia)
w = requests.get("https://es.wikipedia.org/wiki/Bogot%C3%A1")

# Convertir a un objeto "BeautifulSoup"
bsobj = bs(w.content)

# Imprimir (Revisar estructura del código html)
print(bsobj.prettify())


# In[4]:


# Revisar la información de la "tabla de datos" usando una clase específica

info_caja = bsobj.find(class_="infobox geography vcard")
info_filas = info_caja.find_all("tr")
for fila in info_filas:
    print(fila.prettify())


# In[5]:


# Función para obtener los valores dados diferentes casos, además, se reemplazan caracteres extraños (unicode).
def obtener_valores(fila_data):
    if fila_data.find("div") and fila_data.find("br"):
        return [texto for texto in fila_data.stripped_strings]
    else:
        return fila_data.get_text(" ").replace("\xa0", " ").replace("\u200b", "").strip()

# Crear función para eliminar etiquetas [1] (span) solo en el caso de que no tengan información relevante
def limpiar_etiquetas(bs_objeto):
    if bs_objeto.find_all("sup", {'class': 'reference separada'}):
        for etiqueta in bs_objeto.find_all("sup"):
            etiqueta.decompose()
    pass

limpiar_etiquetas(bsobj)
         
municipios_info = {}

# Crear una lista de títulos para tomar el indice desde el cuál empezar a obtener los datos
titulos = [fila.get('title') for fila in info_caja.find_all("a") if fila.get('title') is not None]
contador = 0
for indice, fila in enumerate(info_filas):
    if indice == 0 and fila.find("th"):
        municipios_info['municipio'] = fila.find("th").get_text(" ", strip=True)
    # En caso de que el tag "th" no contenga información o no exista, tomar el nombre del municipio del encabezado (tag "h1")
    elif indice == 0 and not fila.find("th"):
        municipios_info['municipio'] = bsobj.find("h1").get_text(" ", strip=True)
    elif indice < titulos.index('Coordenadas geográficas'): # Imágenes y otros datos irrelevantes no serán tenidos en cuenta
        continue
    else: # Las filas de tabla (tr) que no contengan elementos "th" & "td" serán evitadas
        try:
            # Se obtiene las llaves y se reemplazan caracteres extraños. 
            # Se anexa un número a aquellas llaves que posean el mismo nombre "* Total" para evitar errores en los datos
            if fila.find("th").get_text(" ", strip=True) == "• Total":
                llaves = fila.find("th").get_text(" ", strip=True).replace("•", "").strip() + f"_{contador}"
                valores = obtener_valores(fila.find("td"))
                municipios_info[llaves] = valores
                contador += 1
            else:
                llaves = fila.find("th").get_text(" ", strip=True).replace("•", "").replace("\u200b", "").strip()
                valores = obtener_valores(fila.find("td"))
                municipios_info[llaves] = valores
        except AttributeError as e:
            pass

municipios_info


# #### Tarea #2: Obtener la información para todos los municipios de Colombia

# In[24]:


# Cargar el contenido de la página (Lista de municipios de Colombia por población)
url = requests.get("https://es.wikipedia.org/wiki/Anexo:Municipios_de_Colombia_por_poblaci%C3%B3n")

# Convertir a un objeto BS
bso = bs(url.content)

# Imprimir HTML
print(bso.prettify())


# In[25]:


# Extraer las etiquetas "href" para la clase especificada
municipios = bso.select(".wikitable.sortable td")
rutas = [m.a['href'] for m in municipios if m.a and m.get('align') is None]
print(rutas)


# In[26]:


# Extraer las rutas de cada municipio y formar junto al dominio, los enlaces completos.

dominio = "https://es.wikipedia.org"
enlaces = []
for ruta in rutas:
    enlaces.append(dominio + ruta)


# In[27]:


# En algunos casos, las rutas estaban conectadas a municipalidades de otros paises. Se cambian por los enlaces correctos
for n, i in enumerate(enlaces):
    if i == 'https://es.wikipedia.org/wiki/Aquitania':
        enlaces[n] = 'https://es.wikipedia.org/wiki/Aquitania_(Boyac%C3%A1)'
    elif i == 'https://es.wikipedia.org/wiki/Saman%C3%A1':
        enlaces[n] = 'https://es.wikipedia.org/wiki/Saman%C3%A1_(Caldas)'
    elif i == 'https://es.wikipedia.org/wiki/Roncesvalles':
        enlaces[n] = 'https://es.wikipedia.org/wiki/Roncesvalles_(Tolima)'
              


# In[28]:


# Crear función para obtener los valores dependiendo de la etiqueta, además, se eliminan caracteres extraños.
def obtener_valores(fila_data):
    if fila_data.find("div") and fila_data.find("br"):
        return [texto for texto in fila_data.stripped_strings]
    else:
        return fila_data.get_text(" ").replace("\xa0", " ").replace("\u200b", "").strip()

# Crear función para eliminar etiquetas [1] (span) solo en el caso de que no tengan información relevante
def limpiar_etiquetas(bs_objeto):
    if bs_objeto.find_all("sup", {'class': 'reference separada'}):
        for etiqueta in bs_objeto.find_all("sup"):
            etiqueta.decompose()
    pass

# Crear función para obtener la información de un municipio dada su dirección url.
def obtener_info(url):
    
    w = requests.get(url)
    
    bsobj = bs(w.content)
    info_caja = bsobj.find(class_="infobox geography vcard")
    info_filas = info_caja.find_all("tr")
    
    limpiar_etiquetas(bsobj)
    
    municipios_info = {}

    # Crear una lista de títulos para tomar el indice desde el cuál empezar a obtener los datos
    titulos = [fila.get('title') for fila in info_caja.find_all("a") if fila.get('title') is not None]
    contador = 0
    for indice, fila in enumerate(info_filas):
        if indice == 0 and fila.find("th"):
            municipios_info['municipio'] = fila.find("th").get_text(" ", strip=True)
        # En el caso de que no exista la etiqueta "th", será necesario tomar el nombre de la cabecera "h1" del código HTML.
        elif indice == 0 and not fila.find("th"):
            municipios_info['municipio'] = bsobj.find("h1").get_text(" ", strip=True)
        elif indice < titulos.index('Coordenadas geográficas'): # Imágenes y otros datos irrelevantes no serán tenidos en cuenta
            continue
        # Manejo de excepciones y reemplazo de strings en la obtención de los datos
        else:
            try:# Caso especial: En el caso de que una dos etiquetas "th" contengan el mismo texto, se le agrega un caracter 
                # adicional al texto para diferenciarlos, y así evitar errores en la conexión con los "td" relacionados.
                if fila.find("th").get_text(" ", strip=True) == "• Total":
                    llaves = fila.find("th").get_text(" ", strip=True).replace("•", "").strip() + f"_{contador}"
                    valores = obtener_valores(fila.find("td"))
                    municipios_info[llaves] = valores
                    contador += 1
                # Evitar tomar los datos de IDH y Población Metropolitana, debido a que solo se encuentran contabilizados en pocos municipios (Ciudades Capitales)
                elif 'IDH' in fila.find("th").get_text(" ", strip=True).upper() or 'METROPOLITANA' in fila.find("th").get_text(" ", strip=True).upper():
                    continue
                else:
                    llaves = fila.find("th").get_text(" ", strip=True).replace("•", "").replace("\u200b", "").strip()
                    valores = obtener_valores(fila.find("td"))
                    municipios_info[llaves] = valores
            except AttributeError as e:
                pass

    return municipios_info


# In[11]:


# Probar la función "obtener_info()" para solo un municipio. Verificar que funcione correctamente.
obtener_info("https://es.wikipedia.org/wiki/Medell%C3%ADn")


# In[29]:


# Se inicia el proceso de extracción de datos para todos los municipios (Guardar todos los diccionarios en una lista)

municipios = []
for enlace in enlaces:
    try:
        municipios.append(obtener_info(enlace))
    except Exception as e:
        print(enlace)
        print(e)    


# In[30]:


len(municipios)
# Se logra obtener los datos de 1118 municipios de 1122 existentes. 
# Para el caso de los municipios de "Isla de San Andrés" e "Isla de Providencia" las tablas no soportan el método "find_all"
# En los otros dos casos, no existe una tabla para la obtención de los datos.


# In[31]:


# Definir una función para guardar el archivo .json y otra para cargar el archivo .json

import json

def guardar_datos(titulo, datos):
    with open(titulo, 'w', encoding='utf-8') as a:
        json.dump(datos, a, ensure_ascii=False, indent=2)
        
def cargar_datos(titulo):
    with open(titulo, encoding="utf-8") as a:
        return json.load(a)


# In[32]:


# Guardar resultados obtenidos hasta el momento.

guardar_datos("municipios_col.json", municipios)


# #### Tarea #3: Limpieza de Datos

# In[16]:


# Cargar datos

municipios_col = cargar_datos("municipios_col.json")


# In[17]:


# Imprimir todas las distintas llaves de la lista de dictionarios

all_keys = set().union(*(d.keys() for d in municipios_col))
all_keys

# Se identifican diversas llaves que no contienen información relevante, otras que contienen valores faltantes excesivos,
# algunas difieren en el nombre pero guardan valores similares.


# In[144]:


# Para este ejercicio, se trabaja con la información bajo un DataFrame (para facilitar algunas operaciones de limpieza)

municipios_df = pd.DataFrame(municipios_col)


# In[73]:


# Aquitania Boyacá (Cambiar link) https://es.wikipedia.org/wiki/Aquitania_(Boyac%C3%A1)
# Samaná Caldas (Cambiar link) https://es.wikipedia.org/wiki/Saman%C3%A1_(Caldas)
# Roncesvalles Tolima (Cambiar link) https://es.wikipedia.org/wiki/Roncesvalles_(Tolima)
# Eliminar key "Aeropuerto"
# Eliminar key "Autoridad tradicional Ne'jwesx 2019 - 2021"
# Eliminar "Flor", "Arbol", "Ave", "Cabecera", "Cabecera municipal", "Capital", "Barrios", "Veredas", "Caseríos"
# Eliminar "Centros Poblados", "Hermanada con", "Idioma oficial", "Moneda", "Máxima", "Mínima", "Matrícula"
# Unir Alcalde/Corregidor
# Unir localidades, comunas, barrios
# Eliminar "Otras S(s)uperficies" 'PIB (nominal)','PIB per cápita','Partidos gobernantes'
# Eliminar 'Presidente regional','Presupuesto anual', 'Temperatura', 'Temperatura promedio', 'Total_2'
# Ajustar verdadero nombre '[[Departamentos de \nColombia|Departamento]]','[xau[Subregiones de Antioquia'


# In[145]:


municipios_df.head()


# ##### ** Eliminar columnas con información irrelevante, incompleta o nula **

# In[146]:



columnas_erradas = ["Aeropuerto", "Flor", "Arbol", "Árbol", "Ave", "Cabecera", "Cabecera municipal",
        "Capital", "Barrios", "Veredas", "Caseríos", "Centros Poblados", "Nombre", "Fiestas mayores",
        "Hermanada con","Idioma oficial","Moneda","Máxima","Mínima","Matrícula","Patrono(a)","Localidades",
        "Otras Superficies:","PIB (nominal)","PIB per cápita","Partidos gobernantes","Corregimientos",
        "Otras superficies:", "Presidente regional","Presupuesto anual", "Temperatura", "Creación",
        "Temperatura promedio", "Total_2", "Eventos históricos","Superficie","Altitud", "Comunas",
        "Curso de agua","Código Dane (Divipola)","Código Dian","Correspondencia actual","Subdivisiones",
        "Autoridad tradicional Ne'jwesx 2019 - 2021", "Otros idiomas", "", "Prefijo telefónico",
        "Región", "Provincia", "Zona"]

for col in columnas_erradas:
    if col in municipios_df.columns:
        municipios_df = municipios_df.drop(col, 1)
    continue

#municipio['Superficie'] = municipio.pop('Total_0')
#municipio['Altitud Media'] = municipio.pop('Media')
# Unir Región, Subregión y Zona


# In[147]:


# Las columnas 'Total_0', Total_1', 'Urbana' y 'Media' contiene la información correspondiente 
# a 'Superficie', 'Población', 'Pobl. Urbana' y 'Altitud Media' respectivamente, por lo tanto,
# cambiamos el nombre de las columnas.

municipios_df = municipios_df.rename(columns={'Total_0': 'Superficie', 'Total_1': 'Población Total',
                                              'Media': 'Altitud Media', 'Urbana': 'Pobl. Urbana'})


# ##### ** Unir columnas con igual información pero diferente nombre **

# In[149]:


# Reducir a una sola columna aquellas que contienen la misma información pero difieren en su encabezado

from re import search

columnas = {'lcald': 'Alcalde', 'epartamento': 'Departamento', 'unicipio': 'Municipio',
           'oblación': 'Población Total', 'Subregi': 'Subregión', 'Código': 'Código postal'}

for col in municipios_df.columns:
    for key, value in columnas.items():
        if search(key, col) and col != value:
            municipios_df[value].fillna(municipios_df[col], inplace=True)
            municipios_df = municipios_df.drop(col, 1)
        continue

municipios_df = municipios_df.drop("Subregión", 1)


# In[151]:


# Unir las columnas Alcalde/Corregidor

municipios_df['Alcalde'].fillna(municipios_df['Corregidor'], inplace=True)
municipios_df = municipios_df.drop('Corregidor', 1)


# ##### Extraer y añadir la información de códigos postales para todos los municipios

# In[153]:


# Extraer el contenido de la página y crear el objeto BS (Departamentos)

url = requests.get("https://codigo-postal.co/colombia/")
soup = bs(url.content)
print(soup.prettify())


# In[170]:


# Identificar todas las etiquetas "li" dentro de contenido de la clase especificada

info_box = soup.find(class_="column-list")
info_rows = info_box.find_all("li")
for row in info_rows:
    print(row.prettify())


# In[155]:


# Extraer y guardar los enlaces de cada departamento

dptos = []

for row in info_rows:
    dptos.append(row.a['href'])

dptos


# In[194]:


# Se define la función "get_urls" la cual accede al enlace del departamento, extrae y guarda los enlaces de todos sus municipios

def get_urls(dpto, mpios):
    url = requests.get(dpto)
    soup = bs(url.content)

    info_box = soup.find(class_="col-md-8")
    info_rows = info_box.find_all("ul")

    info_lists = []
    for row in info_rows:
        info_lists.append(row.find_all("li"))
    
    for info_list in info_lists:
        for renglon in info_list:
            mpios.append(renglon.a['href'])


    return mpios

# Extraer los enlaces de todos los municipios de cada departamento. Guardar en una misma lista todos los enlaces.
mpios = []
for dpto in dptos:
    get_urls(dpto, mpios)


# In[197]:


# En este caso, se procede a crear una nueva columna que contenga los nombres de cada municipio pero sin tildes (´) en caso...
# ... de que existan. Esto para facilitar el proceso de asignación del código postal para su correspondiente. Mas adelante...

import re
from unicodedata import normalize

municipios_df['New_municipios'] = ""

series = municipios_df['Municipio']
for index, value in series.items():
    municipios_df['New_municipios'][index] = normalize('NFC', re.sub(
        r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1", 
        normalize( "NFD", value), 0, re.I))


# In[198]:


# Se asigna la nueva columna como indice del DataFrame
municipios_df = municipios_df.set_index('New_municipios')


# In[199]:


municipios_df.head()


# In[204]:


# La función "get_codes" accede al enlace del municipio, extrae y guarda el nombre del municipio y su código postal.

def get_codes(mpio, postales):
    try:
        url = requests.get(mpio)
        soup = bs(url.content)

        info_box_head = soup.find(class_="breadcrumb")
        info_rows_head = info_box_head.find_all("li")
    
        llave = info_rows_head[3].find("span").get_text(" ", strip=True)
    
        info_box_body = soup.find(class_="table-responsive")
        info_rows_body = info_box_body.find_all("tr")
    
        valor = info_rows_body[1].find("a").get_text(" ", strip=True)
    
        postales[llave] = valor

        return postales
    
    except AttributeError as e:
        print(f"¡{llave} no tiene código postal asignado!")
        pass

# Extraer el código postal para todos los municipio. Guardar la información en un diccionario.
postales = {}
for mpio in mpios:
    get_codes(mpio, postales)


# In[206]:


# La razón por la que se creó una nueva columna con los nombres de cada municipio sin tilde es porque es necesario asignarlos...
# ... usando el nombre de la llave, cuyos nombres no poseen tildes en los casos en los que debería tenerla. Por lo tanto, ...
# ... se utilizan los nuevos indices para 

municipios_df = municipios_df.drop("Código postal", 1)

municipios_df['Código Postal'] = 0
for key, value in postales.items():
    for index, val in municipios_df['Clima'].items():
        if search(key, index):
            municipios_df['Código Postal'][index] = value
            


# In[210]:


# Se elimina la columna indice que fue tomada solo como referencia
municipios_df.reset_index(drop=True, inplace=True)


# In[217]:


municipios_df.head()


# ##### ** Convertir fechas en string a datetime **

# In[370]:


# Extraer la fecha de cada string de la columna "Fundación" ("5 de junio de 1935" --> "5/junio/1935")

for idx in municipios_df.index:
    try:
        if len(municipios_df['Fundación'][idx].split()) > 4:
            municipios_df['Fundación'][idx] = ' '.join(municipios_df['Fundación'][idx].split()[:5]).replace(' de', '').replace(' ', '/')
        continue
    except Exception as e:
        print(f"{idx}: {e}")


# In[371]:


# Extraer la fecha de cada string de la columna "Erección" ("5 de junio de 1935" --> "5/junio/1935")

for idx in municipios_df.index:
    try:
        if len(municipios_df['Erección'][idx].split()) > 4:
            municipios_df['Erección'][idx] = ' '.join(municipios_df['Erección'][idx].split()[:5]).replace(' de', '').replace(' ', '/')
        continue
    except Exception as e:
        print(f"{idx}: {e}")


# In[372]:


# Convertir las fechas de las columnas "Fundación" y "Erección" de formato string a datetime

from datetime import datetime
import locale # Usar locale para configurar la lectura de las fechas en idioma español.

locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

columnas = ['Fundación', 'Erección']

for col in columnas:
    for idx in municipios_df.index:
        try:
            municipios_df[col][idx] = datetime.strptime(municipios_df[col][idx], '%d/%B/%Y')
        except Exception as e:
            print(f"{idx}: {e}")


# In[373]:


# Para aquellas fechas incompletas extraer, por lo menos, el año.

from re import search

columnas = ['Fundación', 'Erección']

for col in columnas:
    for idx in municipios_df.index:
        try:
            if not isinstance(municipios_df[col][idx], datetime):
                municipios_df[col][idx] = search('\d{4}', municipios_df[col][idx]).group(0)
        except Exception as e:
            print(f"{idx}: {e}")


# ##### ** Conversión de datos númericos, modificación de strings y  manejo de valores faltantes (NaN) **

# In[375]:


# Convertir valores de la columna superficie a flotantes, creando una nueva columna que muestre la unidad de medida en (km²)

municipios_df['Superficie (km²)'] = np.NaN

for idx in municipios_df.index:
    try:
        municipios_df['Superficie (km²)'][idx] = float(municipios_df['Superficie'][idx].split()[0])
    except ValueError:
        try:
            municipios_df['Superficie (km²)'][idx] = float(municipios_df['Superficie'][idx].split()[0].replace(',', '.'))
        except Exception as e:
            print(f"{idx}: {e}")

# Eliminar columna 'Superficie'
municipios_df = municipios_df.drop("Superficie", 1)


# In[376]:


# Convertir valores de la columna 'Altitud Media' a enteros, creando una nueva columna que muestre la unidad de medida en (msnm)

municipios_df['Altitud Media (m.s.n.m)'] = np.NaN

for idx in municipios_df.index:
    try:
        municipios_df['Altitud Media (m.s.n.m)'][idx] = float(municipios_df['Altitud Media'][idx].split()[0].replace(',', '.'))
    except Exception as e:
        print(f"{idx}: {e}")

# Eliminar columna 'Altitud Media'
municipios_df = municipios_df.drop("Altitud Media", 1)


# In[377]:


# Convertir valores de columna 'Densidad' a flotantes, creando una nueva columna que muestre la unidad de medida en (hab/km²)

municipios_df['Densidad (hab/km²)'] = np.NaN

for idx in municipios_df.index:
    try:
        municipios_df['Densidad (hab/km²)'][idx] = float(municipios_df['Densidad'][idx].split()[0])
    except (ValueError, AttributeError):
        try:
            municipios_df['Densidad (hab/km²)'][idx] = float(municipios_df['Densidad'][idx].split()[0].replace(',', '.'))
        except Exception as e:
            print(f"{idx}: {e}")


# Eliminar columna 'Densidad'
municipios_df = municipios_df.drop("Densidad", 1)


# In[397]:


# Convertir los valores de las columnas 'Población Total' y 'Pobl. Urbana' de string a enteros

columnas = {'Población Total': 'Población Total (hab)', 'Pobl. Urbana': 'Pobl. Urbana (hab)'}

municipios_df['Pobl. Urbana (hab)'] = np.NaN
municipios_df['Población Total (hab)'] = np.NaN

for key, value in columnas.items():
    for idx in municipios_df.index:
        try:
            municipios_df[value][idx] = int(municipios_df[key][idx].split(' hab.')[0].replace(' ', '').replace(',', ''))
        except Exception as e:   
            print(f"{idx}: {e}")
    
    # Eliminar la columna correspondiente (anterior)
    municipios_df = municipios_df.drop(key, 1)


# In[432]:


# Acortar el tamaño de las coordenadas, mostrando solo la latitud y la longitud.

for idx in municipios_df.index:
    try:
        municipios_df['Coordenadas'][idx] = municipios_df['Coordenadas'][idx].split('/')[0].replace('\ufeff', '').strip()
    except Exception as e:
        print(f"{idx}: {e}")


# In[431]:


# Extraer solo el nombre del alcalde de cada municipio (originalmente aparece el año de posesión y el partido político)

for idx in municipios_df.index:
    try:
        municipios_df['Alcalde'][idx] = municipios_df['Alcalde'][idx].split('(')[0].strip()
    except Exception as e:
        print(f"{idx}: {e}")


# In[418]:


# En el caso de las columnas de huso horario, país y entidad los valores son iguales para todos los indices, es decir,
# Uso horario: UTC -5, Entidad: Municipio y País: Colombia. Se usa esta información para rellenar los valores nulos.

municipios_df['Huso horario'].fillna("UTC -5", inplace=True)
municipios_df['Entidad'].fillna("Municipio", inplace=True)
municipios_df['País'].fillna("Colombia", inplace=True)


# In[433]:


# Cambiar el orden de las columnas dependiendo de la relevancia de la información contenida.

municipios_df = municipios_df[['Municipio', 'Departamento', 'Entidad', 'País', 'Fundación', 'Erección', 'Superficie (km²)',
                              'Altitud Media (m.s.n.m)', 'Población Total (hab)', 'Pobl. Urbana (hab)', 'Densidad (hab/km²)',
                              'Coordenadas', 'Clima', 'Gentilicio', 'Alcalde', 'Código Postal', 'Huso horario']]


# ##### ** ¡Trabajo finalizado! Ahora, guardar los datos en formato CSV **

# In[21]:


# Guardar datos en formato CSV

municipios_df.to_csv("municipios_colombia_df.csv")

