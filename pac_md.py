#-*- coding: utf-8 -*-
'''
PROGRAMA PARA AUTOMATIZACIÓN DE CÁLCULOS - MÉTRICAS DINÁMICAS (PAC-MD) v0.7
PROGRAM FOR CALCULATION AUTOMATION, DYNAMIC METRICS v0.7

Es una herramienta de post-procesamiento de archivos de salida de simulaciones dinámicas obtenidas en motores cálculos avanzados de luz natural (Radiance). 
Las métricas dinámicas incorporadas a esta herramienta son: DA, sDA, UDI, sUDI, CDI y sCDI.
    
Autores: 
    PhD. Juan Manuel Monteoliva  
    Eng. Emanuel R. Schumacher
    
Fecha inicio: 20/09/2022

'''
###### LIBRARIES ######
from datetime import datetime
import pandas as pd
import numpy as np
import os
import glob
from sys import exit
from io import StringIO
import matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt

######  CONFIG PARAMETERS OF DYNAMIC METRICS   ######

# FILES PATHS
# SO Windows
filesPathData = ".\example\Results\\" 
filesPathCoordenadas = ".\example\Workplanes\\"
filesPathProcesados = ".\example\Results\pac_md\\"
filePathsImagen = ".\example\Results\pac_md\\"

 
# SO Mac or Linux
#filesPathData = "./example/Results/"
#filesPathCoordenadas = "./example/Workplanes/"
#filesPathProcesados = "./example/Results/pac_md/"
#filePathsImagen = "./example/Results/pac_md/"

nombreCarpetaImagen = "images\\"

# HEADERS && EXTENSIONS

resultsFileReference = "results_"
scheduleFileReference = "schedule_"
procesadosFileReference = "procesados-"
wpFileHeader = "results_"
extensionCSV = ".csv"
extensionPTS = ".pts"

######  CONFIG PARAMETERS FOR GRAPHICS ######

valorAlpha = 0.25
markerSize = 15


# DA - DAYLIGHT AUTONOMY
'''
Porcentaje anual de los intervalos de tiempo ocupados cuando la iluminancia excede
un umbral predefinido (por defecto 200 lux)
'''
daIlumValue = 200 # DA threshold value 

# sDA - SPATIAL DAYLIGHT AUTONOMY
'''
Porcentaje de un espacio que recibe una iluminancia objetivo mínima predefinida 
(por defecto 200 lux) durante al menos el 50% de las horas anuales ocupadas
'''
sdaIlumValue = daIlumValue # sDA threshold value
sdaPorcentajeSensores = 0.5 # fraction of sensors to consider for analysis
sdaPorcentajeHoras = 0.5 # fraction of hours to consider for analysis

# UDI - USEFUL DAYLIGHT INDEX
'''
UDI - porcentaje anual de los intervalos de tiempo
ocupados cuando la iluminancia es útil -dentro de los límites inferior y superior 
(por defecto 100-2500 lux)
'''
udiIlumMin = 100 # UDI minimum threshold value
udiIlumMax = 2500 # UDI maximum threshold value
udiPorcentajeSensores = 0.5 # fraction of sensor to consider for analysis

# sUDI - SPATIAL USEFUL DAYLIGHT INDEX
'''
Porcentaje de un espacio que recibe iluminancias útiles -dentro de los límites
inferior y superior- durante al menos el 50% de las horas anuales ocupadas
'''

sudiIlumMin = udiIlumMin # sUDI minimum threshold value
sudiIlumMax = udiIlumMax # sUDI maximum threshold value
sudiPorcentajeHoras = 0.5 # fraction of hours to consider for analysis

# CDI  - Characteristic Daylight Illuminance and sCDI
'''
Esta métrica proporciona una interpretación inversa al DA. Ésta
no representa un porcentaje de tiempo correspondiente a una iluminancia objetivo (por ejemplo,
200 lux), sino una iluminancia de tarea (0lx, 50lx, 100lx, 200lx, 300lx, 500lx, 750lx, 1000lx,
2000lx) correspondiente al porcentaje de tiempo ocupado
'''
cdiPorcentajeSensores = 0.5 # fraction of sensor to consider for analysis


######  FUNCTIONS DECLARATION   ######

def listar_archivos(ruta, fileNameReference, extension):
    ''' 
    - EXTACCIÓN DE NOMBRE DE ARCHIVOS DE UNA CARPETA -

    Dada un a RUTA de carpeta o directorio, se identifican los elementos con el TEXTO ("results_", "schedule_", etc), y con la EXTENSION indicada (.csv por ejemplo)

    Parametros input
        ruta - Elemento tipo string con la ruta de directorio donde se realiza la búsqueda
        texto - Elemento tipo string con el texto, indica el nombre de archivo que se busca
        extension - Elemento tipo string, indica la extension de los archivos (.csv, .pts)

    Parametros output
        listaCompleta - Elemento tipo lista con los nombres de los archivos encontrados en la RUTA indicada

    '''
    listaCompleta = []
    listaRutas = []

    rutaDeBusqueda = ruta+fileNameReference+"*"+extension
    print(f"Ruta de archivos {rutaDeBusqueda} \n")
    listaArchivos = glob.glob(rutaDeBusqueda)
    listaArchivos.sort()  
    txtAux = ruta + fileNameReference

    for r in listaArchivos:
        routePos = r.find(txtAux) + len(txtAux)
        listaRutas.append(r[routePos:-(len(extension))])       

    listaCompleta = listaRutas
    print(f"Lista de {fileNameReference} de archivos encontrados es: \n {listaCompleta}")
    
    return listaCompleta

def split_filenames(lista):
    '''
    - EXTRACCIÓN DE IDENTIFICADOR DE LOS ARCHIVOS results Y schedule -

    Se genera una lista de los ID de los archivos listados

    Parámetos input
        lista - Estructura tipo diccionario {"resultados":[], "schedules":[]} la cual contiene los nombres de los archivos results y schedule a analizar, esta lista se genera
        con la función listar_archivos(ruta, referencia, extension)
        La lista correspondiente a cada key debe tener la forma:
        [referencia_parentID_childID]


    Parámetros output
        listaCompleta - Elemento tipo lista, la cual contiene los identificadores de los archivos a analizar.
        rDict - Elemento tipo Diccionario, { "parentID": [id1, id2, ...], "childID" :[resultID1, resultID2, ...]}, contiene los índices de los archivos results
        sDict - Elemento tipo Diccionario, { "parentID": [id1, id2, ...], "childID" :[scheduleID1, scheduleID2, ...]}, contiene los índices de los archivos schedule
        sIndex - Elemento tipo Diccionario, { "parentID1": [lista de schedulesID asociados al parentID1], "parentID2": [lista de schedulesID asociados al parentID2], ...} 
        
    '''
    resultados = lista["resultados"]
    schedules = lista["schedules"]
    underScore = "_"
    exten = ".csv"

    rLista = []
    sLista = []

    # Separamos los "APELLIDOS" y los NOMBRES  de la lista de archivos a procesar y los guardamos en una lista
    for r in resultados:
        rLista.append(r.split(underScore))         
    
    for s in schedules:
        sLista.append(s.split(underScore))       
    
    # Creamos una lista con elementos tipo diccionario con los pares apellido y nombre obtenidos en la lista anterior
    rDict = []
    sDict = []

    for elemento in rLista:
        rDict.append({"parentID": elemento[0], "childID": elemento[1]})

    for elemento in sLista:
        sDict.append({"parentID": elemento[0], "childID": elemento[1]})

    sIndex = {}
    
    #Se crean los key con los nombres de los "parentID en función de la lista de parentID de rDict"
    for row in rDict:
        if row["parentID"] not in sIndex:
            sIndex[str(row["parentID"])] = []


    for row in sIndex:
        for elemento in sDict:
            if elemento["parentID"] == row:
                #sIndex[row].append(str(elemento["parentID"]+"_"+elemento["childID"]))
                sIndex[row].append(str(elemento["childID"]))

    print("Schedules Index")
    print(sIndex)    
        
    return rDict, sDict, sIndex

def count_ocurrencies(lista, indice):
    '''
    - CALCULO DE OCURRENCIA DE APELLIDOS

    Recorre una lista cuyos elementos son un diccionario con el formato {"parentID": AAA, "childID": NNN}, 
    luego con el parametro indice = "parentID" se extrae el valor del mismo, se guarda como key en un nuevo diccionario y se contabiliza la cantidad
    de veces que aparece ese key en la lista, el formato de ese nuevo diccionario es {"AAA": X}

    Parametros input:
        - lista: Estructura tipo lista de diccionarios con el formato {"parentID": AAA, "childID": NNN}
        - indice: elemento tipo string, representa el key a buscar en el parametro de entrada "lista"

    Parametros output
        - counts: Estructura tipo lista de diccionarios, con el formato {"AAA": X}, donde AAA representa el parentID, y X la cantidad de veces que aparece en el parametro lista 

    '''
    counts = {}
    for row in lista:
        if row[indice] not in counts:
            counts[str(row[indice])] = 1
        else:
            counts[str(row[indice])] += 1
    return counts

def daylight_autonomy(daIlumValue, dmcNsensors, dmcCondicion, dmcRows, dmcRealHours, dfResultados):    
    '''
    - DAYLIGHT AUTONOMY -

    daylight_autonomy(daIlumValue,dmcNsensors,dmcRows, ocupacion, periodoAnalisis)

    CALCULO DE CANTIDAD DE HORAS QUE TIENEN UN VALOR SUPERIOR A daIlumValue = 300 Y CUMPLEN CON LA CONDICIÓN DE ocupacion Y periodoAnalisis

    SE REALIZA EL CALCULO POR SENSOR

    Parámetos input
        daIlumValue - Elemento tipo entero, indica el mínimo valor de medición de sensor 

    Parámetros output
        daIlumHoursCount - Elemento tipo lista, cada elemento indica la cantidad de horas anuales en las que el sensor analizado supera el valor mínimo indicado en la variable daIlumValue y 
        cumple con las condiciones de ocupación y período de análisis
        daOcurranceRate - Elemento tipo lista, cada valor indica el porcentaje entre daIlumHoursCount y las horas reales de análisis por cada sensor
        daAverageOcurranceRate - Elemento tipo float con el valor promedio (%) entre daOcurranceRate y la cantidad de sensores

    '''

    daIlumHoursCount = np.zeros(dmcNsensors)
    daOcurranceRate = np.zeros(dmcNsensors)
    daAux = 0

    dfIlumHoursCount = dfResultados.copy()
    dfIlumHoursCount[:] = 0

    for sensor in range(dfIlumHoursCount.shape[1]):
        dfIlumHoursCount.loc[((dfResultados[sensor] >= daIlumValue) & (dmcCondicion['condicion'] == 1)), sensor] = 1
        daIlumHoursCount[sensor]= dfIlumHoursCount[sensor].sum()
        daOcurranceRate[sensor] = (daIlumHoursCount[sensor] * 100) / dmcRealHours
        daAux = daAux + daOcurranceRate[sensor]

    daAverageOcurranceRate = daAux/dmcNsensors
    print(f"La cantidad de sensores son: {dmcNsensors}")

    return daIlumHoursCount, daOcurranceRate, daAverageOcurranceRate

def useful_daylight_index(udiIlumMin, udiIlumMax, dmcNsensors, dmcRealHours, dmcRows, dfResultados):
    ''' 
    - USEFUL DAYLIGHT INDEX AND sUDI-

    CALCULO DE CANTIDAD DE HORAS QUE TIENEN UN VALOR COMPRENDIDO ENTRE UN MÍNIMO Y UN MÁXIMO Y CUMPLEN CON LA CONDICIÓN DE ocupacion Y periodoAnalisis
    SE REALIZA EL CALCULO POR SENSOR

    Parámetros input
        udiIlumMin - Elemento tipo entero, india el mínimo valor de medición de sensor
        udiIlumMax - Elemento tipo entero, india el máximo valor de medición de sensor
        dmcNsensors - Elemento tipo entero, indica cantidad de sensores
        dmcRealHours - Elemento tipo entero, cantidad de horas a considerar
        dfResultados - Elemento tipo lista con los valores de medición de todos los sensores 

    Parámetros output
        udiIlumHoursCount - Cantidad de horas anuales en las que el sensor analizado se encuentra comprendido entre los valores 
        establecidoes entre un mínimo udiIlumMin y un valor maximo udiIlumMax y cumple con las condiciones de ocupación y período de análisis
        udiOcurranceRate - Elemento tipo float con el valor promedio (%) entre udiIlumHoursCount y las horas reales de análisis

    '''
    udiIlumHoursCount = np.zeros(dmcNsensors)
    udiOcurranceRate = np.zeros(dmcNsensors)
    sudiIlumSensorCount = np.zeros(dmcNsensors)
    sudiOccurrancePercentSensor = np.zeros(dmcNsensors)
    udiAux = 0
    udiHours = 0
    udiQttySensor = 0
    sudiQttyHoras = 0
    sUDIhoras = 0
    sUDI = 0

    # DETERMIANR LA CANTIDAD DE SENSORES CORRESPONDIENTE AL PORCETAJE SELECCIONADO
    udiSensors = dmcNsensors*udiPorcentajeSensores
    condicionSensores = udiSensors - int(udiSensors)
        
    if (condicionSensores) > 0:
        udiQttySensor = int(udiSensors) + 1 
    else:
        udiQttySensor = int(udiSensors)

    dfudiIlumHoursCount = dfResultados.copy()
    dfudiIlumHoursCount[:] = 0

    for sensor in range(dfudiIlumHoursCount.shape[1]):
        dfudiIlumHoursCount.loc[((dfResultados[sensor] >= udiIlumMin) & (dfResultados[sensor] <= udiIlumMax) & (dmcCondicion["condicion"] == 1)), sensor ] = 1
        udiIlumHoursCount[sensor] = dfudiIlumHoursCount[sensor].sum()    
        udiOcurranceRate[sensor] = (udiIlumHoursCount[sensor] * 100) / dmcRealHours
        udiAux = udiAux + udiOcurranceRate[sensor]
        udiHours= udiHours + udiIlumHoursCount[sensor] # calculo de horas totales que cumplen con el rango seleccionado
    
    #       CALCULO DE sUDI          #
    # DETERMIANR LA CANTIDAD DE HORAS CORRESPONDIENTE AL PORCETAJE SELECCIONADO
    sudiHoursReference = dmcRealHours*sudiPorcentajeHoras
    condicionHoras = sudiHoursReference - int(sudiHoursReference)
        
    if (condicionHoras) > 0:
        sudiQttyHoras = int(sudiHoursReference) + 1 
    else:
        sudiQttyHoras = int(sudiHoursReference)

    dfsudiIlumSensorCount = dfResultados.copy()
    dfsudiIlumSensorCount[:] = 0

    for sensor in range(dfsudiIlumSensorCount.shape[1]):    
        dfsudiIlumSensorCount.loc[((dfResultados[sensor] >= sudiIlumMin) & (dfResultados[sensor] <= sudiIlumMax) & (dmcCondicion['condicion'] == 1)), sensor] = 1
        sudiIlumSensorCount[sensor] = dfsudiIlumSensorCount[sensor].sum()

        if sudiIlumSensorCount[sensor] >= sudiQttyHoras: # considera solo los casos en donde la cantidad de sensores es igual o mayor a la deseada
            sudiOccurrancePercentSensor[sensor] = 1
        else:
            sudiOccurrancePercentSensor[sensor] = 0

        sUDIhoras = sUDIhoras + sudiOccurrancePercentSensor[sensor]
    sUDI = sUDIhoras * 100 / dmcNsensors
    #       FIN CALCULO DE sUDI          #

    udiAverageOcurranceRate = udiAux/dmcNsensors

    print(f"sUDI - Limite inferior [lx]: {sudiIlumMin}, Limite superior [lx]: {sudiIlumMax}")
    print(f"sUDI - Horas simuladas: {dmcRealHours}, Horas considedradas: {sudiQttyHoras}")
    print(f"sUDI - Horas que cumplen la condicion del {(udiPorcentajeSensores*100)}: {sUDIhoras}")

    return udiIlumHoursCount, udiOcurranceRate, udiAverageOcurranceRate, udiHours, sUDI, sUDIhoras, sudiIlumSensorCount, sudiOccurrancePercentSensor

def spatial_daylight_autonomy(sdaIlumValue, dmcNsensors, dmcRealHours, dmcCondicion, dfResultados):
    ''' 
    - SPATIAL DAYLIGHT AUTONOMY -
    CALCULO POR HORA DE LA CANTIDAD DE HORAS QUE EL SENSOR ANALIZADO TIENE UN VALOR MEDIDO SUPERIOR O IGUAL A UN MINIMO Y CUMPLEN CON LA CONDICIÓN DE ocupacion Y periodoAnalisis

    SE REALIZA EL ANÁLISIS PARA LAS HORAS ANUALES Y PARA TODOS LOS SENSORES DEL ARCHIVO ANALIZADO

    Parámetros Input
        sdaIlumValue - Elemento tipo entero, indica el mínimo valor de medición de sensor
        dmcCondicion - Elemento tipo lista, indica si la hora analizada debe tenerse en cuenta o no, surge de analizar las condiciones de hora de uso y periodo del año analizado, 
            tiene la misma longitud de dfResultados
        dmcRealHours - Elemento tipo entero, cantidad de horas de análisis, será afectado por el porcentaje de horas a considerar
        dmcNsensors - Elemento tipo entero, cantidad de horas a considerar
        dfResultados - Elemento tipo lista con los valores de medición de todos los sensores (matriz Horas x Sensores)

    Parámetros Output
        sdaIlumSensorCount - Elemento tipo lista con la cantidad de sensores que superan el valor mínimo establecido y cumplen con las condiciones de ocupación y período de análisis por hora analizada
        sdaOccurrancePercentSensor - Elemento tipo lista, se indica si en la Hora analizada la cantidad de sensores contabilizados es igual o mayor a la totalidad de los mismos
        sdaAnualOccurranceRate - Elemento tipo float con el valor promedio (%) de "sdaOccurrancePercentSensor" con respecto a la cantidad total de horas analizadas
        sdaOcurranceAllSensors - type int. How many sensor comply with hours condition  
    '''
    sdaIlumHoursCount = np.zeros(dmcNsensors)
    sdaOccurrancePercentSensor = np.zeros(dmcNsensors)
    sdaQttyHoras = 0
    sdaOcurranceAllSensors = 0

    # DETERMINAR LA CANTIDAD DE HORAS A CONSIDERAR
    sdaHoras = dmcRealHours * sdaPorcentajeHoras
    condicionHoras = sdaHoras - int(sdaHoras)
    
    if (condicionHoras) > 0:
        sdaQttyHoras = int(sdaHoras) + 1 
    else:
        sdaQttyHoras = int(sdaHoras)

    print (f"sDA - Horas de análisis: {dmcRealHours}, Horas consideradas: {sdaQttyHoras}")

    dfsdaIlumHoursCount = dfResultados.copy()
    dfsdaIlumHoursCount[:] = 0

    for sensor in range(dfsdaIlumHoursCount.shape[1]):    
        dfsdaIlumHoursCount.loc[(dfResultados[sensor] >= sdaIlumValue) & (dmcCondicion["condicion"] == 1), sensor] = 1
        sdaIlumHoursCount[sensor] = dfsdaIlumHoursCount[sensor].sum()

        if sdaIlumHoursCount[sensor] >= sdaQttyHoras: # considera solo los casos en donde la cantidad de sensores es igual o mayor a la deseada
            sdaOccurrancePercentSensor[sensor] = 1
        else:
            sdaOccurrancePercentSensor[sensor] = 0

        sdaOcurranceAllSensors = sdaOcurranceAllSensors + sdaOccurrancePercentSensor[sensor] # how many sensor comply with hours condition        

    print(f"sDA - Sensores con cumplimiento del {(sdaPorcentajeHoras*100)}%: {sdaOcurranceAllSensors}\n")
    sdaAnualOccurranceRate = sdaOcurranceAllSensors*100/dmcNsensors

    return sdaIlumHoursCount, sdaOccurrancePercentSensor, sdaAnualOccurranceRate, sdaOcurranceAllSensors

def dmc_condicion_and_realHours(dfCondiciones, dmcRows):
    '''
    - CALCULO DE LAS CONDICIONES Y LAS CANTIDADES DE HORAS REALES - 

    Parámetros Input
        ocupacion - Elemento tipo lista con la condición de ocupación a tener en cuenta para el analisis de los sensores por cada hora
        periodoAnalisis - Elemento tipo lista con la condición de periodo de analisis a tener en cuenta para el analisis de los sensores por cada hora
        dmcRows - Elemento tipo entero, indica la cantidad de filas (cada fila representa una hora a analizar) que tienen las listas ocupación y periodoAnalisis
    Parámetros Output
        dmcCondicion - Elemento tipo Pandas DataFrame, pero funciona como binario, valores que puede adopotar son 0 ó 1
        dmcRealHours - Elemento tipo entero, indica la cantidad de horas reales a considerar de acuerdo a la ocupacion y periodoAnalisis
    '''
    
    dfRows = {'condicion': np.zeros(len(dfCondiciones.index))} 
    dmcCondicion = pd.DataFrame(dfRows)
    dmcRealHours = 0

    dmcCondicion.loc[((dfCondiciones['ocupacion'] == 1) & (dfCondiciones['periodoAnalisis'] == 1)), 'condicion'] = 1
    dmcRealHours = dmcCondicion["condicion"].sum()

    return dmcCondicion, dmcRealHours

def get_cdi_index(dmcNsensors, dmcRows, dmcRealHours, dmcCondicion, dfResultados):
    '''
    - CALCULO DE PARÁMETRO CDI
    Escala de valores de iluminancia: 0lx, 50lx, 100lx, 200lx, 300lx, 500lx, 750lx, 1000lx, 2000lx

    Parámetros Input
        dmcNsensors -  cantida de sensores 
        dmcRealHours - cantidad de horas a considerar 
        dmcCondicion - condición de ocupación, y horas a considerar
        dfResultados - dataFrame con los valores de iluminancia de todos los sensores a analizar

    Parámetros Output
        cdiValues - dataframe, valor de máxima iluminancia por sensor, segun escala
        sCDIvalues - porcentaje de sensores para cada rango de la escala indicada

    '''
    cdiMenor50 = np.zeros(dmcNsensors, dtype=float)
    cdiMayor50 = np.zeros(dmcNsensors, dtype=float)
    cdiMayor100 = np.zeros(dmcNsensors, dtype=float)
    cdiMayor200 = np.zeros(dmcNsensors, dtype=float)
    cdiMayor300 = np.zeros(dmcNsensors, dtype=float)
    cdiMayor500 = np.zeros(dmcNsensors, dtype=float)
    cdiMayor750 = np.zeros(dmcNsensors, dtype=float)
    cdiMayor1000 = np.zeros(dmcNsensors, dtype=float)
    cdiMayor2000 = np.zeros(dmcNsensors, dtype=float)

    cdiMenor50Aux = np.zeros(dmcNsensors, dtype=float)
    cdiMayor50Aux = np.zeros(dmcNsensors, dtype=float)
    cdiMayor100Aux = np.zeros(dmcNsensors, dtype=float)
    cdiMayor200Aux = np.zeros(dmcNsensors, dtype=float)
    cdiMayor300Aux = np.zeros(dmcNsensors, dtype=float)
    cdiMayor500Aux = np.zeros(dmcNsensors, dtype=float)
    cdiMayor750Aux = np.zeros(dmcNsensors, dtype=float)
    cdiMayor1000Aux = np.zeros(dmcNsensors, dtype=float)
    cdiMayor2000Aux = np.zeros(dmcNsensors, dtype=float)

    cdiValues = np.zeros(dmcNsensors,dtype=float)
    sCDIvalues = { "0lx": 0, "50lx": 0, "100lx": 0, "200lx": 0, "300lx": 0, "500lx": 0, "750lx": 0, "1000lx": 0, "2000lx": 0 }

    # DETERMIANR LA CANTIDAD DE SENSORES CORRESPONDIENTE AL PORCETAJE SELECCIONADO
    cdiSensorsPercent = 100 * cdiPorcentajeSensores
    print(f"\nCDI - Porcentaje de sensores considerados: {cdiSensorsPercent:.2f} %\n")
    
    dfCDIVector = dfResultados[[dfResultados.columns[0]]].copy() # permite generar un array con la misma cantida de filas que el dataFrame que recibimos
    dfCDIVector[:] = 0    
    
    for sensor in range(dfResultados.shape[1]):
        dfCDIVector.loc[((dfResultados[sensor] < 50) & (dmcCondicion['condicion'] == 1)), dfCDIVector.columns[0]] = 1
        cdiMenor50[sensor] = dfCDIVector[dfCDIVector.columns[0]].sum()
        dfCDIVector[:] = 0        

        dfCDIVector.loc[(dfResultados[sensor] >= 50) & (dmcCondicion['condicion'] == 1), dfCDIVector.columns[0]] = 1
        cdiMayor50[sensor] = dfCDIVector[dfCDIVector.columns[0]].sum()
        dfCDIVector[:] = 0

        dfCDIVector.loc[(dfResultados[sensor] >= 100) & (dmcCondicion['condicion'] == 1), dfCDIVector.columns[0]] = 1
        cdiMayor100[sensor] = dfCDIVector[dfCDIVector.columns[0]].sum()
        dfCDIVector[:] = 0

        dfCDIVector.loc[(dfResultados[sensor] >= 200) & (dmcCondicion['condicion'] == 1), dfCDIVector.columns[0]] = 1
        cdiMayor200[sensor] = dfCDIVector[dfCDIVector.columns[0]].sum()
        dfCDIVector[:] = 0

        dfCDIVector.loc[(dfResultados[sensor] >= 300) & (dmcCondicion['condicion'] == 1), dfCDIVector.columns[0]] = 1
        cdiMayor300[sensor] = dfCDIVector[dfCDIVector.columns[0]].sum()
        dfCDIVector[:] = 0

        dfCDIVector.loc[(dfResultados[sensor] >= 500) & (dmcCondicion['condicion'] == 1), dfCDIVector.columns[0]] = 1
        cdiMayor500[sensor] = dfCDIVector[dfCDIVector.columns[0]].sum()
        dfCDIVector[:] = 0

        dfCDIVector.loc[(dfResultados[sensor] >= 750) & (dmcCondicion['condicion'] == 1), dfCDIVector.columns[0]] = 1
        cdiMayor750[sensor] = dfCDIVector[dfCDIVector.columns[0]].sum()
        dfCDIVector[:] = 0

        dfCDIVector.loc[(dfResultados[sensor] >= 1000) & (dmcCondicion['condicion'] == 1), dfCDIVector.columns[0]] = 1
        cdiMayor1000[sensor] = dfCDIVector[dfCDIVector.columns[0]].sum()
        dfCDIVector[:] = 0

        dfCDIVector.loc[(dfResultados[sensor] >= 2000) & (dmcCondicion['condicion'] == 1), dfCDIVector.columns[0]] = 1
        cdiMayor2000[sensor] = dfCDIVector[dfCDIVector.columns[0]].sum()     
        dfCDIVector[:] = 0         

        cdiMenor50Aux[sensor] = cdiMenor50[sensor] * 100 / dmcRealHours
        cdiMayor50Aux[sensor] = cdiMayor50[sensor] * 100 / dmcRealHours
        cdiMayor100Aux[sensor] = cdiMayor100[sensor] * 100 / dmcRealHours
        cdiMayor200Aux[sensor] = cdiMayor200[sensor] * 100 / dmcRealHours
        cdiMayor300Aux[sensor] = cdiMayor300[sensor] * 100 / dmcRealHours
        cdiMayor500Aux[sensor] = cdiMayor500[sensor] * 100 / dmcRealHours
        cdiMayor750Aux[sensor] = cdiMayor750[sensor] * 100 / dmcRealHours
        cdiMayor1000Aux[sensor] = cdiMayor1000[sensor] * 100 / dmcRealHours
        cdiMayor2000Aux[sensor] = cdiMayor2000[sensor] * 100 / dmcRealHours

        if cdiMenor50Aux[sensor] >= cdiSensorsPercent:
            cdiValues[sensor] = 0
        if cdiMayor50Aux[sensor] >= cdiSensorsPercent:
            cdiValues[sensor] = 50
        if cdiMayor100Aux[sensor] >= cdiSensorsPercent:
            cdiValues[sensor] = 100
        if cdiMayor200Aux[sensor] >= cdiSensorsPercent:
            cdiValues[sensor] = 200
        if cdiMayor300Aux[sensor] >= cdiSensorsPercent:
            cdiValues[sensor] = 300
        if cdiMayor500Aux[sensor] >= cdiSensorsPercent:
            cdiValues[sensor] = 500
        if cdiMayor750Aux[sensor] >= cdiSensorsPercent:
            cdiValues[sensor] = 750
        if cdiMayor1000Aux[sensor] >= cdiSensorsPercent:
            cdiValues[sensor] = 1000
        if cdiMayor2000Aux[sensor] >= cdiSensorsPercent:
            cdiValues[sensor] = 2000
        
        if int(cdiValues[sensor]) == 0:
            sCDIvalues["0lx"] = sCDIvalues["0lx"] + 1
        if int(cdiValues[sensor]) == 50:
            sCDIvalues["50lx"] = sCDIvalues["50lx"] + 1
        if int(cdiValues[sensor]) == 100:
            sCDIvalues["100lx"] = sCDIvalues["100lx"] + 1
        if int(cdiValues[sensor]) == 200:
            sCDIvalues["200lx"] = sCDIvalues["200lx"] + 1
        if int(cdiValues[sensor]) == 300:
            sCDIvalues["300lx"] = sCDIvalues["300lx"] + 1
        if int(cdiValues[sensor]) == 500:
            sCDIvalues["500lx"] = sCDIvalues["500lx"] + 1
        if int(cdiValues[sensor]) == 750:
            sCDIvalues["750lx"] = sCDIvalues["750lx"] + 1
        if int(cdiValues[sensor] )== 1000:
            sCDIvalues["1000lx"] = sCDIvalues["1000lx"] + 1
        if int(cdiValues[sensor]) == 2000:
            sCDIvalues["2000lx"] = sCDIvalues["2000lx"] + 1
    
    
    print(f"valores de sCDI: {sCDIvalues}")
    for k in sCDIvalues:
        sCDIvalues[k] = sCDIvalues[k]*100/dmcNsensors 
    
    cdiMaxValue = cdiValues.max()

    print(f"Valores de sCDI normalizados: < 50lx: {sCDIvalues['0lx']:.2f} >= 50lx: {sCDIvalues['50lx']:.2f}, >= 100lx: {sCDIvalues['100lx']:.2f}, >= 200lx: {sCDIvalues['200lx']:.2f}, >= 300lx: {sCDIvalues['300lx']:.2f}, >= 500lx: {sCDIvalues['500lx']:.2f}, >= 750lx: {sCDIvalues['750lx']:.2f}, >= 1000lx: {sCDIvalues['1000lx']:.2f}, >= 2000lx: {sCDIvalues['2000lx']:.2f}\n")
    
    return cdiValues, sCDIvalues, cdiMaxValue

def creacion_archivos(filePath, nombre, pathResultados, pathSchedule ,daIlumHoursCount, daOcurranceRate, daAverageOcurranceRate, udiIlumHoursCount, udiOcurranceRate, udiAverageOcurranceRate, udiHours, sUDIpercentual,  sUDIsensorCount, sUDIsensorOccurrance, sdaSensorCount, sdaOccurrancePercentSensor, sdaAnualOccurranceRate, sdaHoras, cdi, sCDI, cdiValue, dmcRows, dmcNsensors):
    '''
    - GENERACIÓN DE ARCHIVOS CON LOS DATOS PROCESADOS
        Se generan los archivos "procesados-..." con los datos calculados, en el directorio indicado.
        
    '''
    dfArchivo = pd.DataFrame()
   
    dfArchivo['DA Horas Contabilizadas'] = daIlumHoursCount
    dfArchivo['DA Frecuencia de Ocurrencia'] = daOcurranceRate
    dfArchivo['UDI Horas Contabilizadas'] = udiIlumHoursCount
    dfArchivo['UDI Frecuencia de Ocurrencia'] = udiOcurranceRate
    dfArchivo['CDI'] = cdi
    dfArchivo['SDA Contabilizacion de sensores'] = sdaSensorCount
    dfArchivo[f'SDA Frecuencia de Ocurrencia mayor al {(sdaPorcentajeHoras*100)} %'] = sdaOccurrancePercentSensor
    dfArchivo['sUDI Sensores Contabilizados'] = sUDIsensorCount
    dfArchivo[f'sUDI Frecuencia de ocurrencia mayor al {(sudiPorcentajeHoras*100)} %'] = sUDIsensorOccurrance
    
    fileName = procesadosFileReference+nombre+'.csv'
    #fileNameTodo = 'otroResumen-'+nombre+'.csv'

    if os.path.isdir(filePath):
        #print("La carpeta existe")
        path = filePath
    else:
        os.mkdir(filePath)
        path = filePath
        #print(f"Se creo la carpeta results la ruta es {path}")

    with open(path+fileName, 'a') as f:
        f.write("ARCHIVOS FUENTE:\n")
        f.write(pathResultados)
        f.write("\n")
        f.write(pathSchedule)
        f.write("\n")    
        f.write("\n")
        f.write(f"DA iluminancia limite [lx]: {daIlumValue}\n")
        f.write(f"sDA [%]: {sdaPorcentajeHoras}\n")
        f.write(f"UDI iluminancia maxima [lx]: {udiIlumMax}\n")
        f.write(f"UDI iluminancia minima [lx]: {udiIlumMin}\n")
        f.write(f"sUDI [%]: {sudiPorcentajeHoras}\n")
        f.write("\n")
        f.write("METRICAS DINÁMICAS\n")
        f.write("\n")
        f.write(f"DA - Horas de cumplimiento de [{daIlumValue} lx]: {daAverageOcurranceRate:.2f}\n")
        f.write(f"sDA: {sdaAnualOccurranceRate:.2f}\n") 
        f.write(f"sDA - Horas con cumplimiento del {(sdaPorcentajeHoras*100)} %: {int(sdaHoras)}\n") #falta incluir las horas de sDA
        f.write("\n")
        f.write(f"UDI: {udiAverageOcurranceRate:.2f}\n")
        f.write(f"UDI - Horas de cumplimiento de [{udiIlumMin} - {udiIlumMax} lx]: {udiHours}\n")
        f.write(f"sUDI: {sUDIpercentual:.2f}\n")  
        f.write(f"sUDI - Horas con cumplimiento del {(sudiPorcentajeHoras*100)} %: {int(sUDIhs)}\n")
        f.write(f"CDI: {cdiValue}\n")
        for k in sCDI:
            f.write(f"sCDI - {k}: {sCDI[k]:.2f} \n")     
        f.write("\n")
        
    dfArchivo.to_csv(path+fileName, mode='a')
    
    return 1

def crear_archivo_unificado(filesPath, indice, dfUnificado):
    '''
    - GENERACIÓN DE ARCHIVOS CON LOS DATOS UNIFICADOS
        Se genera el archivo "unificado" con los datos calculados, en el directorio indicado.
    
    Parámetros Input
        filesPath - Elemento tipo String, indica la ruta a la carpeto donde se guardará el archivo
        indice - Elemento tipo diccionario, contiene las rutas de los archivos procesados
        dfUnificado - Elemento tipo Panda dataframe, contiene la información a guardar en el archivo
        
    Parámetros Output
        archivo unificado generado en el filePath indicado

    '''

    if os.path.isdir(filesPath):
        #print("La carpeta existe")
        path = filesPath
    else:
        os.mkdir(filesPath)
        path = filesPath
        #print(f"Se creo la carpeta results la ruta es {path}")

    for elemento in indice:
        dfAux = dfUnificado.query('parentID == @elemento')  
        print(dfAux)     
        fileNameUnificado = 'unificado_results_'+elemento+'.csv'
        dfAux.drop(columns = 'parentID')
        dfAux.to_csv(path+fileNameUnificado, index = False ,mode='a')
    return 1

def get_parentID_childID(listaNombreArchivosProcesados, listaNombreArchivosCoordenadas):
    '''
    - EXTRACCIÓN DE IDENTIFICADOR DE LOS ARCHIVOS results Y schedule -

    Se genera una lista de los ID de los archivos procesados y de coordenadas de las escenas

    Input
        listaNombreArchivosProcesados - Elemento tipo diccionario {"resultados":[], "schedules":[]} 
        la cual contiene los nombres de los archivos results y schedule a analizar

        listaNombreArchivosCoordenadas - Elemento tipo 

    Output
        listaCompleta - Elemento tipo lista, la cual contiene los identificadores de los archivos a analizar.

    '''
    listaA = listaNombreArchivosProcesados
    listaB = listaNombreArchivosCoordenadas
    underScore = "_"
    hypen = "-"    

    rLista = []
    sLista = []
    
    # Separamos los APELLIDOS y los NOMBRES  de la lista de archivos a procesar y los guardamos en una nueva lista
    for r in listaA:
        rLista.append(r.split(underScore)) 

    for s in listaB:
        sLista.append(s.split(underScore))
    
    # Creamos una lista con elementos tipo diccionario con los pares apellido y nombre obtenidos en la lista anterior
    rDict = []
    sDict = []

    #print(f"contenido de rLista: {rLista}")

    for elemento in rLista:
        rDict.append({"parentID": elemento[0], "childID": elemento[1], "scheduleID": elemento[2]})

    for elemento in sLista:
        sDict.append({"parentID": elemento[0], "childID": elemento[1]})

    sIndex = {}
    
    for row in rDict:
        if row["parentID"] not in sIndex:
            sIndex[str(row["parentID"])] = []

    for row in sIndex:
        for elemento in rDict:
            if elemento["parentID"] == row:
                sIndex[row].append(str(elemento["parentID"]+"_"+elemento["childID"] +"_"+elemento["scheduleID"]))

    return rDict, sDict, sIndex

def get_dataframe_fileNames(fileList):
    '''
    EXTRACCIÓN DE LOS IDENTIFICADORES DE LA LISTA DE ARCHIVOS PROCESADOS

    Parámetros Input
        fileList - Elemento tipo lista. El contenido son los nombres de los archivos procesados
    Parámetros Output
        df - Elemento tipo oandas dataframe. El contenido de este dataframe se divide en 3 columnas, "parentID", "resultID", "shceduleID"        
    '''

    underScore = '_'
    parametersList = []
    
    # Separamos las partes según el simbolo, obteniendo los diferentes descriptores de la lista de archivos a procesar
    for r in fileList:
        parametersList.append(r.split(underScore)) 

    df = pd.DataFrame(parametersList, columns=['parentID', 'resultID', 'scheduleID'])

    return df

def convertir_a_dataframes(filesPath, procesadosFileReference, listaArchivosProcesados, extensionCSV):
    '''
    - EXTRACCIÓN DE LOS DATOS DE LAS MÉTRICAS DINÁMICAS

    Parámetros Input
        filesPath - Elemento tipo String. Indica la ruta de acceso a la carpeta donde se encutran los archivos a leer
        procesadosFileReference - Elemento tipo String. Nombre de la carpeta donde se encuentran los archivos leer.
        listaArchivosProcesados - Elemento tipo String. Nombre de archivo procesados que se desea leer.
        extensionCSV - Elemento tipo String. Indica la extensión de los archivos a leer.

    Parámetros Output
        df - Elemento tipo Pandas dataframe. Contiene los datos procesados del archivo indicado.
        
    '''

    with open(filesPath+procesadosFileReference+listaArchivosProcesados+extensionCSV, 'r') as f:
        read_data = f.read()
        offsetComa = read_data.find(',')
        datos = read_data[offsetComa:-1]
        df = pd.read_csv(StringIO(datos),sep=',', index_col = 0)
          
    return df

def generar_carpeta_imagenes(filePath,nombreCarpetaImagen):
    '''
    - GENERACIÓN DE CARPETA PARA ALMACENAR LAS IMÁGNES

    Parámetros Input
        filePath - Elemento tipo String. Indica la ruta de acceso en donde se quiere almacenar las imágenes
        nombreCarpetaImagen - Elemento tipo String. Indica el nombre de la carpeta donde se desean almacenar las imágenes      

    '''

    if os.path.isdir(filePath+nombreCarpetaImagen):
        #print("La carpeta existe")
        path = filePath+nombreCarpetaImagen
    else:
        os.mkdir(filePath+nombreCarpetaImagen)
        path = filePath+nombreCarpetaImagen
        #print(f"Se creo la carpeta results la ruta es {path}")

    return 1


''' - INICIO PROGRAMA PRINCIPAL - '''
print("#########   CALCULATION OF DYNAMIC METRICS    ######### \n")
startTime = datetime.now()
extensionCSV = ".csv"
listarArchivos = {"resultados":[], "schedules":[]}

listarArchivos["resultados"] = listar_archivos(filesPathData, "results_", extensionCSV)
listarArchivos["schedules"] = listar_archivos(filesPathData, "schedule_", extensionCSV)

resultsDict, schedulesDict, schedulesIndex = split_filenames(listarArchivos)

print(f"El resultsDict contiene \n {resultsDict} \n")

resultsRecount = count_ocurrencies(resultsDict, "parentID")
schedulesRecount = count_ocurrencies(schedulesDict, "parentID")

longitudRecuentoR = len(resultsRecount)
longitudRecuentoS = len(schedulesRecount)

# REVISAMOS INTEGRIDAD DE LAS CANTIDADES Y TIPOS DE APELLIDOS DE LOS ARCHIVOS results Y schedule
if longitudRecuentoR != longitudRecuentoS:
    flagIntegrityCheck = 1
else:
    flagIntegrityCheck = 0
    keysR = list(resultsRecount.keys())
    keysS = list(schedulesRecount.keys())

    for i in range(0,longitudRecuentoR):
        if keysR[i] != keysS[i]:
            flagIntegrityCheck = 2
            break
        else:
            flagIntegrityCheck = 0
#   ###########################################################################

#   Generamos mensajes de error si hubieran
if flagIntegrityCheck != 0:
    print("HA OCURRIDO UN ERROR")
    if flagIntegrityCheck == 1:
        print("ATENCIÓN: NO SE CUMPLE LA CONDICIÓN DE IGUALDAD EN LOS IDENTIFICADORES USADOS PARA RESULTADOS Y SCHEDULES")
        print("Favor de revisar los identidicadores usados para los rchivos de resultados y los schedules sean no sean diferentes.")
        exit()
    elif flagIntegrityCheck == 2:
        print("ATENCION: REVISE LOS NOMBRES ASIGANDOS PARA LOS PARES RESULTADOS Y SCHEDULES")
        print("Los nombres para identificar los results con los schedules no coinciden, favor revisar.")
        exit()
    elif flagIntegrityCheck > 2 or flagIntegrityCheck < 0:
        print("ERROR INDETERMINADO !!!")
        print("Revise integridad de los datos")
        exit()
    else:
        print("")
else:
    print("")
#   ###########################################################################

print(f"Listado general de archivos a procesar: {listarArchivos}\n")

#   UNA VEZ IDENTIFICADO QUE ESTÁ TODO BIEN, SE PROCEDE A DETERMINAR SI TENEMOS MUCHOS results CON 1 schedule, VICEVERSA Ó 1 VS 1

parentID = []
scheduleID = []
archivoFuente = []
horasSimuladas = [] 
horasDeUso = []

da_ilum_limite = []            
sDA_ilum_limite = []
sDA_porcentaje_horas = []
UDI_ilum_min = []
UDI_ilum_max = []
sUDI_ilum_min = []
sUDI_ilum_max = []
sUDI_porcentaje_horas = []
sCDI_porcentaje_sensores = []

da_value = []
udi_value = []
sUDI_value = []
sDA_value = []
cdi_value = []
sCDI_0lx = []
sCDI_50lx = []
sCDI_100lx = []
sCDI_200lx = []
sCDI_300lx = []
sCDI_500lx = []
sCDI_750lx = []
sCDI_1000lx = []
sCDI_2000lx = []

for element in resultsDict:
    dfResultados = pd.read_csv(filesPathData+"results_"+element["parentID"]+"_"+element["childID"]+extensionCSV, sep=',', header=None)   

    dmcNsensors = len(dfResultados.axes[1])
    dmcCantFilasResultados = len(dfResultados.axes[0])

    for elemento in range(0, len(schedulesIndex[element["parentID"]])):
        print("\n\nArchivo procesado: ")
        print(filesPathData+"results_"+element["parentID"]+"_"+element["childID"]+extensionCSV)
        print(filesPathData+"schedule_"+element["parentID"]+"_"+schedulesIndex[element["parentID"]][elemento]+extensionCSV)
        print("ID: ", element["parentID"])
        print("")
        dfSchedule = pd.read_csv(filesPathData+"schedule_"+element["parentID"]+"_"+schedulesIndex[element["parentID"]][elemento]+extensionCSV, sep=',', header=None)
        dmcCantFilasSchedule = len(dfSchedule.axes[0])

        if dmcCantFilasResultados == dmcCantFilasSchedule:
            dmcRows = dmcCantFilasResultados
        elif dmcCantFilasResultados >= dmcCantFilasSchedule:
            dmcRows = dmcCantFilasSchedule
        else:
            dmcRows = dmcCantFilasResultados
        
        print(f"Horas simuladas: {dmcRows}")

        # Extraemos los valores de ocupacion y periodo de analisis
        dfCondiciones = dfSchedule.loc[:,[3,4]] # columna 3 representa la condicion de ocupacion, columna 4 representa la condicion de periodo de analisis
        dfCondiciones.columns = ['ocupacion', 'periodoAnalisis']
                
        ###     DEBEMOS LLAMAR A LAS 3 FUNCIONES Y TRAERNOS LOS VALORES QUE NECESITAMOS GUARDAR EN EL ARCHIVO POR CADA UNA DE LOS ARCHIVOS PROCESADOS
        
        dmcCondicion, dmcRealHours = dmc_condicion_and_realHours(dfCondiciones, dmcRows)
        print(f"Horas de Uso: {dmcRealHours} \n")
        print(f"DA - Iluminancia límite [lx]: {daIlumValue}")
        print(f"sDA - Iluminancia límite [lx]: {sdaIlumValue}, Porcentaje de tiempo considerado: {(sdaPorcentajeSensores*100)} % [default 50 %]")

        daIlumHoursCount, daOcurranceRate, daAverageRate = daylight_autonomy(daIlumValue, dmcNsensors, dmcCondicion, dmcRows, dmcRealHours, dfResultados)
        sdaIlumSensorCount, sdaOccurrancePercentSensor, sdaAnualRate, sdaHoras = spatial_daylight_autonomy(sdaIlumValue, dmcNsensors, dmcRealHours, dmcCondicion, dfResultados)

        print(f"UDI - Limite inferior [lx]: {udiIlumMin}, Limite superior [lx]: {udiIlumMax}")
        udiIlumHoursCount, udiOcurranceRate, udiAverageRate, udiHours, sUDIpercentual, sUDIhs, sUDIsensorCount, sUDIsensorOccurrance = useful_daylight_index(udiIlumMin, udiIlumMax, dmcNsensors, dmcRealHours, dmcRows, dfResultados)
        
        cdi, sCDI, cdiValue = get_cdi_index(dmcNsensors, dmcRows, dmcRealHours, dmcCondicion, dfResultados)

        print("\nMETRICAS DINÁMICAS DE ILUMINACIÓN NATURAL\n")
        print(f"DA: {daAverageRate:.2f}")
        print(f"sDA: {sdaAnualRate:.2f}\n")
        print(f"UDI: {udiAverageRate:.2f}")        
        print(f"sUDI: {sUDIpercentual:.2f}\n")
        print(f"CDI: {cdiValue}\n")
        for k in sCDI:
            print(f"sCDI-{k}: {sCDI[k]:.2f}")

        a = creacion_archivos(filesPathProcesados, element["parentID"]+"_"+element["childID"]+"_"+schedulesIndex[element["parentID"]][elemento], filesPathData+"results_"+element["parentID"]+"_"+element["childID"], filesPathData+"schedules_"+schedulesIndex[element["parentID"]][elemento],daIlumHoursCount, daOcurranceRate, daAverageRate, udiIlumHoursCount, udiOcurranceRate, udiAverageRate, udiHours, sUDIpercentual, sUDIsensorCount, sUDIsensorOccurrance, sdaIlumSensorCount, sdaOccurrancePercentSensor, sdaAnualRate, sdaHoras, cdi, sCDI, cdiValue, dmcRows, dmcNsensors)
        
        parentID.append(element["parentID"])
        scheduleID.append(schedulesIndex[element["parentID"]][elemento])
        archivoFuente.append(str(filesPathData+"results_"+element["parentID"]+"_"+element["childID"]+" - "+filesPathData+"schedules_"+schedulesIndex[element["parentID"]][elemento]))
        horasSimuladas.append(dmcRows)
        horasDeUso.append(int(dmcRealHours))

        da_ilum_limite.append(daIlumValue)             
        sDA_ilum_limite.append(sdaIlumValue)
        sDA_porcentaje_horas.append(sdaPorcentajeHoras)
        UDI_ilum_min.append(udiIlumMin)
        UDI_ilum_max.append(udiIlumMax)
        sUDI_ilum_min.append(sudiIlumMin)
        sUDI_ilum_max.append(sudiIlumMax)
        sUDI_porcentaje_horas.append(sudiPorcentajeHoras)
        sCDI_porcentaje_sensores.append(cdiPorcentajeSensores)

        da_value.append(daAverageRate)
        udi_value.append(udiAverageRate)
        sUDI_value.append(sUDIpercentual)
        sDA_value.append(sdaAnualRate)
        cdi_value.append(cdiValue)
        sCDI_0lx.append(sCDI['0lx'])
        sCDI_50lx.append(sCDI['50lx'])
        sCDI_100lx.append(sCDI['100lx'])
        sCDI_200lx.append(sCDI['200lx'])
        sCDI_300lx.append(sCDI['300lx'])
        sCDI_500lx.append(sCDI['500lx'])
        sCDI_750lx.append(sCDI['750lx'])
        sCDI_1000lx.append(sCDI['1000lx'])
        sCDI_2000lx.append(sCDI['2000lx'])

resultados = {
                "parentID" : parentID, 
                "schedule" : scheduleID,
                "ARCHIVOS FUENTES": archivoFuente, 
                "Horas simuladas": horasSimuladas, 
                "Horas de uso": horasDeUso, 
                "DA ilum limite": da_ilum_limite,                
                "sDA ilum limite": sDA_ilum_limite,
                "sDA porcentaje horas": sDA_porcentaje_horas,
                "UDI ilum min": UDI_ilum_min,
                "UDI ilum max": UDI_ilum_max,
                "sUDI ilum min": sUDI_ilum_min,
                "sUDI ilum max": sUDI_ilum_max,
                "sUDI porcentaje horas": sUDI_porcentaje_horas,
                "sCDI porcentaje sensores": sCDI_porcentaje_sensores,
                "DA": da_value,
                "sDA": sDA_value,
                "UDI": udi_value,
                "sUDI": sUDI_value,
                "CDI": cdi_value,
                "sCDI-0lx": sCDI_0lx,
                "sCDI-50lx": sCDI_50lx,
                "sCDI-100lx": sCDI_100lx,
                "sCDI-200lx": sCDI_200lx,
                "sCDI-300lx": sCDI_300lx,
                "sCDI-500lx": sCDI_500lx,
                "sCDI-750lx": sCDI_750lx,
                "sCDI-1000lx": sCDI_1000lx,
                "sCDI-2000lx": sCDI_2000lx                
            }

dfUnificados = pd.DataFrame(resultados)

indiceParent = schedulesIndex.keys()
crear_archivo_unificado(filesPathProcesados, indiceParent, dfUnificados)

#   GENERACION DE GRÁFICOS
print("#########   IMAGES GENERATION    ######### \n")

listaArchivosProcesados = listar_archivos(filesPathProcesados, procesadosFileReference, extensionCSV)
listaArchivosCoordenadas = listar_archivos(filesPathCoordenadas, wpFileHeader, extensionPTS)

dfFileNames = get_dataframe_fileNames(listaArchivosProcesados)

parentList = dfFileNames['parentID'].unique().tolist()
scheduleList = dfFileNames['scheduleID'].unique().tolist()
rList = dfFileNames['resultID'].unique().tolist()

coordenadasEstructura = {"x": 0, "y": 0, "z": 0}
generar_carpeta_imagenes(filePathsImagen, nombreCarpetaImagen)
dfGraficos = pd.DataFrame()

for schElement in scheduleList:
    scheduleMask = dfFileNames["scheduleID"] == schElement
    dfScheduleFilter = dfFileNames[scheduleMask]    

    for pElement in parentList:
        parentMask = dfFileNames["parentID"] == pElement
        dfParentFilter = dfFileNames[parentMask]

        for rElement in range(len(dfParentFilter)):
            fileNameCoord = str(dfParentFilter.iloc[rElement]['parentID'] + '_' + dfParentFilter.iloc[rElement]['resultID'])
            fileNameProcesado = str(dfParentFilter.iloc[rElement]['parentID'] + '_' + dfParentFilter.iloc[rElement]['resultID']+ '_' + dfParentFilter.iloc[rElement]['scheduleID'])

            dfArchivoCoordenadas = pd.read_csv(filesPathCoordenadas + wpFileHeader + fileNameCoord + extensionPTS, sep='\t', header=None) 
            dfCoordenadas = dfArchivoCoordenadas.iloc[:, [0,1,2]].copy()
            
            dfProcesadoAux = convertir_a_dataframes(filesPathProcesados, procesadosFileReference, fileNameProcesado, extensionCSV)
            dfProcesado = dfProcesadoAux[[dfProcesadoAux.columns[1], dfProcesadoAux.columns[3], dfProcesadoAux.columns[4], dfProcesadoAux.columns[6], dfProcesadoAux.columns[8]]].copy()
            dfGrafAux = pd.concat([dfCoordenadas, dfProcesado], axis=1)
        
            dfGraficos = pd.concat([dfGraficos, dfGrafAux], axis=0)       

        ####    GRAFICA DE RESULTADOS    ####

        dfGraficos.sort_values(dfGraficos.columns[0])
        fileNameImage = str(dfParentFilter.iloc[rElement]['parentID'] + '_' + dfParentFilter.iloc[rElement]['scheduleID'])

        xValues = np.array(dfGraficos[dfGraficos.columns[0]])
        yValues = np.array(dfGraficos[dfGraficos.columns[1]])

        daValues = np.array(dfGraficos[dfGraficos.columns[3]])
        udiValues = np.array(dfGraficos[dfGraficos.columns[4]])
        cdiValues = np.array(dfGraficos[dfGraficos.columns[5]])
        sDAvalues = np.array(dfGraficos[dfGraficos.columns[6]])
        sUDIvalues = np.array(dfGraficos[dfGraficos.columns[7]])

        figDA, graficoDA = plt.subplots()
        figUDI, graficoUDI = plt.subplots()
        figCDI, graficoCDI = plt.subplots()
        figSDA, graficoSDA = plt.subplots()
        figSUDI, graficoSUDI = plt.subplots()

        # DA
        graficoDA.set_facecolor('silver')
        graficoDA.set_alpha(valorAlpha)
        graficoDA.set_title(dfGraficos.columns[3])
        graficoDA.title.set_size(10)
        imagenDA = graficoDA.scatter(x = xValues, 
                                    y = yValues, 
                                    c = daValues, 
                                    cmap = 'CMRmap',
                                    vmin = 0,
                                    vmax = 100,
                                    s = markerSize, 
                                    alpha = 0.75, 
                                    edgecolors = 'black', 
                                    linewidths = 0.5, 
                                    marker = 'o')       
        cbarDA = figDA.colorbar(imagenDA, ticks=[0, 25, 50, 75, 100])
        cbarDA.set_ticklabels(['0%', '25%', '50%', '75%', '100%'])
        figDA.suptitle(f"Grafica de {fileNameImage}")   
        graficoDA.axis('equal')   
        figDA.tight_layout()

        # UDI
        graficoUDI.set_facecolor('silver')
        graficoUDI.set_alpha(valorAlpha)
        graficoUDI.set_title(dfGraficos.columns[4])
        graficoUDI.title.set_size(10)
        imagenUDI = graficoUDI.scatter(x = xValues, 
                                    y = yValues, 
                                    c = udiValues, 
                                    cmap = 'CMRmap',
                                    vmin = 0,
                                    vmax = 100,
                                    s = markerSize, 
                                    alpha = 0.75, 
                                    edgecolors = 'black', 
                                    linewidths = 0.75, 
                                    marker = 'o')       

        cbarUDI = figUDI.colorbar(imagenUDI, ticks=[0, 25, 50, 75, 100])
        cbarUDI.set_ticklabels(['0%', '25%', '50%', '75%', '100%'])
        figUDI.suptitle(f"Grafica de {fileNameImage}")      
        figUDI.tight_layout()

        # CDI
        graficoCDI.set_facecolor('silver')
        graficoCDI.set_alpha(valorAlpha)
        graficoCDI.set_title(dfGraficos.columns[5])
        graficoCDI.title.set_size(10)
        imagenCDI = graficoCDI.scatter(x = xValues, 
                                    y = yValues, 
                                    c = cdiValues, 
                                    cmap = 'CMRmap',
                                    vmin = 0,
                                    vmax = 2000,
                                    s = markerSize, 
                                    alpha = 0.75, 
                                    edgecolors = 'black', 
                                    linewidths = 0.75, 
                                    marker = 'o')       

        cbarCDI = figCDI.colorbar(imagenCDI, ticks=[0, 50, 100, 200, 300, 500, 750, 1000, 2000])
        cbarCDI.set_ticklabels(['0lx', '50lx', '100lx', '200lx', '300lx', '500lx', '750lx', '1000lx', '2000lx'])
        figCDI.suptitle(f"Grafica de {fileNameImage}")      
        figCDI.tight_layout()

        # sDA frecuencia de ocurrencia > al porcentaje de horas indicadas
        graficoSDA.set_facecolor('silver')
        graficoSDA.set_alpha(valorAlpha)
        graficoSDA.set_title(dfGraficos.columns[6])
        graficoSDA.title.set_size(10)
        imagenSDA = graficoSDA.scatter(x = xValues, 
                                    y = yValues, 
                                    c = sDAvalues, 
                                    cmap = matplotlib.colors.ListedColormap(['white', 'lightblue']),
                                    s = markerSize, 
                                    alpha = 0.75, 
                                    edgecolors = 'black', 
                                    linewidths = 0.75, 
                                    marker = 'o')       
        cbarSDA = figSDA.colorbar(imagenSDA, ticks = [0, 1])
        cbarSDA.set_ticklabels(['0', '1'])
        figSDA.suptitle(f"Grafica de {fileNameImage}")      
        figSDA.tight_layout()

        # sUDI frecuencia de ocurrencia > al porcentaje de horas indicadas
        graficoSUDI.set_facecolor('silver')
        graficoSUDI.set_alpha(valorAlpha)
        graficoSUDI.set_title(dfGraficos.columns[7])
        graficoSUDI.title.set_size(10)
        imagenSUDI = graficoSUDI.scatter(x = xValues, 
                                        y = yValues, 
                                        c = sUDIvalues, 
                                        cmap = matplotlib.colors.ListedColormap(['white', 'lightblue']),
                                        s = markerSize, 
                                        alpha = 0.75, 
                                        edgecolors = 'black', 
                                        linewidths = 0.75, 
                                        marker = 'o')       
        cbarSUDI = figSUDI.colorbar(imagenSUDI, ticks = [0, 1])
        cbarSUDI.set_ticklabels(['0', '1'])
        figSUDI.suptitle(f"Grafica de {fileNameImage}")      
        figSUDI.tight_layout()

        # CORRECCIÓN DE ESCALA - VISTA EN PLANTA 
        graficoDA.axis('equal')
        graficoUDI.axis('equal')
        graficoCDI.axis('equal')
        graficoSDA.axis('equal')
        graficoSUDI.axis('equal')
        #####

        #plt.show() 

        # GRABAR IMAGENES GENERADAS EN DIRECTORIO INDICADO
        print(f"################################################\n")
        print(f"Generamos las imagenes del schedule: {schElement}\n")

        figFileName = filePathsImagen+nombreCarpetaImagen+fileNameImage

        figDA.savefig(figFileName + "_DA", bbox_inches='tight', dpi= 800)
        figUDI.savefig(figFileName + "_UDI", bbox_inches='tight', dpi= 800)
        figCDI.savefig(figFileName + "_CDI", bbox_inches='tight', dpi= 800)
        figSDA.savefig(figFileName + "_sDA", bbox_inches='tight', dpi= 800)
        figSUDI.savefig(figFileName + "_sUDI", bbox_inches='tight', dpi= 800)

endTime = datetime.now() - startTime
print("Tiempo de ejecución: "+ str(endTime))
