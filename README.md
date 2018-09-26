# Modelo de clasificación de texto



Este modelo consta de tres módulos. 
1.  Filtración de mensajes por reglas (script_reglas.py)
2. El módulo de entrenamiento de modelo (entrena_modelo.py)
3. El módulo de predicción del modelo (predice_modelo.py)

## Filtración de mensajes por reglas

Requirements:
+ emoji 0.5.0
+ unicodedata
+ re

Este módulo contiene tres funciones. 
+ **is_emoji:** cuenta el número de emojis presentes en el texto. Esta función recibe el texto de mensaje y regresa un entero.
+ **give_emoji_free_text:** Elimina los emojis del texto. Esta función recibe el texto y regresa texto.
+ procesa_reglas: realiza procesamiento básico del texto y hace pruebas pruebas para asignar una categoría a cada mensaje. 
    + **Entrada:** texto
    + **Salida:** diccionario {'result':categoría, 'texto':texto original,'texto_procesado':texto, 'wc':número de palabas, 'cc':número de caracteres}
+ Procesamiento: 
    + Pasa el texto a minúsculas
    + Quita espacios al inicio y al final del mensaje
    + Realiza un conteo de palabras y caracteres
    + Quita signos de puntuación del mensaje
    + Quita acentos y los cambia por su equivalente caracter ascii
+ Reglas: 

    | Regla  |Categoría que regresa el script |
    |---|---|
    | Si el mensaje contiene la palabra "aborto"  |  "aborto" |
    |  Si el mensaje contiene las palabas "hasta luego" | "hasta luego"  |
    | Si el mensaje contiene "https://scontent"  | "like-fb"  |
    | Si el mensaje contiene "t.co"| "twitter image"|
    | Si el mensaje tiene igual número de "?" y caracteres | "pregunta"|
    | Si el mensaje contiene igual número de emojis y caracteres | "emoji"|
    | Si el mensaje contiene sólo un caracter entre la a y la z | "otra"|
    | Si el mensaje contiene "http" y sólo una palabra | "spam"|
    | Si el mensaje contiene "si" y sólo dos caracteres | "si"|
    | Si el mensaje contiene "no" y sólo dos caracteres | "no"|
    | Si el mensaje contiene "salu" y no "mi" o "secret"| "hola"|
    |Si el mensaje contiene "gracia" o "graicas" y hasta 5 palabras | "gracias" |
    | Si el mensaje contiene "ok" y hasta tres palabras | "ok" |
    | Si el mensaje contiene "hola" u "hoola" u "holi" o "bonjour" u "ola" y hasta dos palabras | "hola"|
    | Si el mensaje contiene "ola" o "bien dia" o "que tal" o "bn dia" o "hola" o "buenad tardes" o "buena tarde" o "buen dia" o "buena noche" o "buenas tardea" o "buenas tardes" o "buenas noches"o "buenos dias" y hasta 4 palabras | "hola" |
    |Si el mensaje contiene "horario" y "atención"|"pregunta"|
    |Si el mensaje contiene "número" y "teléfono" y hasta 9 palabras |"pregunta"|
    |Si el mensaje contiene "what" y "number"  |"pregunta"|
    |Si el mensaje contiene "added"  |"like-fb"|
    |Si el mensaje no cae en ninguna de las categorías anteriores|"modelo"|
    
## entrenamiento de modelo

Requirements: 
+ pandas 0.20.3
+ script_reglas
+ re 
+ unicodedata
+ nltk 3.2.4
+ nltk.stem.snowball 3.2.4
+ numpy 1.13.3
+ sklearn 0.19.2
+ xgboost 0.7

Este módulo debe ejecutarse cuando se quiera expandir el programa para hacer otro modelo. 
Es necesario tener la tabla que sale del webhook de autoetiquetado, con por lo menos, la hora del último mensaje, el texto del mensaje original y la categoría asignada.

**Entrada:** *para_entrenamiento.csv*

| hora_ultimo  |  texto | categ_opi  |
|---|---|---|
| 18  | La solicitud de enviar el SMS por Cobrar a 552...  | otra  |
| 18  | Te llame y no pude localizarte. Tramita en lin...  |  otra |
| 18  |  Mi bebe |  nacimiento |
|...|...|...|
|int|str|str|


 **Salida:** 
    + Método que transforma mensajes a un vector numérico de conteo de palabras: **mat_tfidf.pkl**
    + Método que reduce a 33 dimensiones el vector de conteo de palabras: **pca.pkl**
    + Modelo entrenado: **modelo.pkl**

**Nota: Cada paso del entrenamiento está explicado en *entrena_modelo.ipynb***

## Predicciones del modelo
Este módulo debe ejecutarse una vez que el modelo está entrenado. Sirve para que, a partir del texto de un nuevo mensaje, se obtenga una predicción que se pueda conectar a un flujo.


**Entrada:**
+ Método que transforma mensajes a un vector numérico de conteo de palabras: **mat_tfidf.pkl**
+ Método que reduce a 33 dimensiones el vector de conteo de palabras: **pca.pkl**
+ Modelo entrenado: **modelo.pkl**
+ Mapeo de números a etiquetas de predicción **label_map**
    + diccionario {"númerodepredicción": "etiqueta"}
    + El modelo entrenado transformará etiquetas a números enteros. Estos números deben coincidir con el nombre del flujo al que se conectarán. Por ejemplo, para mi salud:  ` label_map={0:'emergencia',
           1:'informacion',
           2:'nacimiento',
           3:'otra',
           4:'pregunta',
           5:'respuesta'} `
    + El modelo asigna el orden de las etiquetas en orden alfabético
    + Esta variable debe cambiarse dentro del código

**Salida:** ` {'pred':etiqueta de predicción (str),
        'probabilidad_maxima':probabilidad máxima (float),
        'indice_seguridad': índice de concentraciónd de probabilidad (float), 
        'proba': probabilidades para cada clase de predicción (array)}`


Para el caso de Mi Salud, cada parte del script está explicada en funcion_modelo.ipynb. Las especificidades importates de este modelo son las siguientes: 
+ Se agregaron categorías para ayudar a la clasificación de mensajes. Se agrega:
    + Pregunta:
        + Búsqueda de trabajo
        + Preguntas médicas
        + Otras Preguntas
    + Otra:
        + Quejas
        + Otras
Esto significa que, para poder ajustar a un nuevo modelo que no tenga estas categorías adicionales, hay que modificar el código de tal forma que no se sumen las probabilidades para producir la predicción. esto se modifica en esta parte del código: 

`proba=array([proba[0][0], #'emergencia'
    proba[0][1], #Informacion
    proba[0][2], #Nacimiento
    proba[0][3]+proba[0][4], #otra
    proba[0][5]+proba[0][6]+proba[0][7], #Pregunta
    proba[0][8]]) #Respuesta`

+ la categoría "cancelar" se colapsó con la de respuestas. Esta categoría tenía sólo 7 mensajes muy dinstintos entre sí, por lo que era imposible hacer una predicción efectiva
+ El modelo calcula una predicción para todos los mensajes. Sin embargo, habrá veces que dos o más clases tienen alta probabilidad. Para controlar ese caso, se calcula un índice de concentración. Entre más alto, más concentrada está la probabilidad en una sola clase. Si el índice está por debajo de 4767.621 el modelo no asignará una clase. El modelo asignará una clase a aproximadamente el 80% de los mensajes enviados. Esto resulta en una precisión fuera de muestra de 80%.
+ Los mensajes que sean emergencias y el modelo no prediga correctamente, son los errores más costosos. Por ello, si la probabilidad de emergencia es mayor a 3%, se le asignará la clase cuya probabildad sea la máxima. Sin embargo, se agregará un flag que indicará que el mensaje tiene una probabilidad alta de ser emergencia. Este flag se le asigna al ~8% de los mensajes y logra captar ~60% de las emergencias. Es decir, de 10 emergencias reales que lleguen al modelo, sólo 3 no verán el mensaje precautorio.
