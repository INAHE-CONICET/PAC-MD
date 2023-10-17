## PAC-MD ![Badge en Desarollo](https://img.shields.io/badge/VERSION-1.0%20-yellow) ![Badge en Desarollo](https://img.shields.io/badge/ESTADO-beta_estable%20-green) ![Badge en Desarollo](https://img.shields.io/badge/LICENCIA-mpl2.0%20-red) 


_PAC-MD es una herramienta de post-procesamiento de archivos de salida de simulaciones dinámicas obtenidas en motores de cálculos avanzados de luz natural (Radiance). Las métricas dinámicas incorporadas a esta herramienta son: DA, sDA, UDI, sUDI, CDI y sCDI._

### Requisitos

```
Windows or Mac OS or Linux operating system:
Python 3.9-3.11
Numpy 1.22.4
Pandas 1.5.0
Matplotlib 3.6.0
Visual Studio Code
```
Las versiones indicadas son las mínimas requeridas, pero se pueden utilizar las versiones más recientes tanto de Python como de las librerías.

### Instalación

Crear la carpeta donde se intalará la herramienta 'pac_md'

Ingresar a la carpeta

```
cd pac_md
```
 
Crear entorno virtual

```
python3 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install matplotlib numpy pandas
```

Clonar carpeta de 'pac_md' desde Github

```
git clone https://github.com/INAHE-CONICET/PAC-MD.git
```

o descomprimir el archivo ZIP descargado en la carpeta donde se instaló 'pac_md' y salir.

---

Para instalar Visual Studio Code, dirijase al siguiente link (https://code.visualstudio.com/Download)

---

### Flujo de trabajo

Ingresar a la capeta donde se instaló 'pac_md'

```
cd pac_md
```

Activar el entorno virtual

```
source env/bin/activate
```

Ingresar a la capeta descargada 'PAC-MD'

```
cd ./PAC-MD/
```

En el caso de usuario Windows defina las siguientes carpetas y comente 'OS Mac o Linux' (linea 38-41)
```
31 # SO Windows
32 filesPathData = ".\example\Results\\"
33 filesPathCoordenadas = ".\example\Workplanes\\"
34 filesPathProcesados = ".\example\Results\pac_md\\"
35 filePathsImagen = ".\example\Results\pac_md\\"
36
37 # SO Mac or Linux
38 #filesPathData = "./example/Results/"
39 #filesPathCoordenadas = "./example/Workplanes/"
40 #filesPathProcesados = "./example/Results/pac_md/"
41 #filePathsImagen = "./example/Results/pac_md/"
42
43 nombreCarpetaImagen = "./images/"		
```

En el caso de usuarios OS Mac o Linux, comente 'OS Windows' (32-35)

Ejecutar el post-procesamiento

```
python3 pac-md.py
```

A los resultados se puede acceder desde:

```
./example/Results/pac_md/
```

### Autores

**Ing. Emanuel R. Schumacher**. Personal de Apoyo. Instituto de Ambiente, Hábitat y Energía (INAHE), CONICET, Mendoza, Argentina. Enlaces de interés: [CONICET](https://www.conicet.gov.ar/new_scp/detalle.php?id=57001&keywords=Emanuel%2BSchumacher&datos_academicos=yes)

**Dr. Juan Manuel Monteoliva**. Investigador Asistente. Instituto de Ambiente, Hábitat y Energía (INAHE), CONICET, Mendoza, Argentina. Enlaces de interés: [CONICET](https://www.conicet.gov.ar/new_scp/detalle.php?id=33083&datos_academicos=yes) - [ResearchGate](https://www.researchgate.net/profile/Juan-Manuel-Monteoliva).

### Financiamiento

Esta investigación fue apoyada por el Consejo Nacional de Investigaciones Científicas y Técnicas (CONICET, Argentina) - **PIBAA 2872021010-0031CO** y la Agencia Nacional de Investigaciones Científicas y Tecnológicas Promoción (ANPCyT, Argentina) - **PICT 2019-04356**. La fuente de financiación no participó en el diseño de este estudio; en la recopilación, análisis e interpretación de datos; en la redacción del informe; o en la decisión de someter 

### Citación

Monteoliva, J.M, Schumacher, E.R. (2023, 7 de septiembre)_. Herramienta de código abierto para el pos-procesamiento de métricas dinámicas y visualización de resultados a partir de datos originales de simulaciones anuales_ [Congreso]. LUZ 2023 - XVI Jornadas Argentinas de Luminotecnia, Santiago del Estero, Argentina.

### Licencia

Mozilla 2.0  	https://www.mozilla.org/en-US/MPL/2.0/
