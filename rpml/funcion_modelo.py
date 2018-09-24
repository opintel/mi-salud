# coding: utf-8
import re
import json
import requests
import nltk
import unicodedata
from sklearn.externals import joblib
from numpy import reshape, concatenate, unique, vectorize, array
from nltk.stem.snowball import SnowballStemmer
from rpml.script_reglas import procesa_reglas,give_emoji_free_text


# ETIQUETAS DE PREDICCIONES (NO CAMBIAR)
label_map = {
    0:'emergencia',
    1:'informacion',
    2:'nacimiento',
    3:'otra',
    4:'pregunta',
    5:'respuesta'
}


def load_pkl():
    """
    Funcion que carga los pkls
    generados en el entrenamiento del modelo
    """
    try:
        from django.contrib.staticfiles import finders

        features_stem_path = finders.find('modelo/mat_tfidf.pkl')
        pca_path = finders.find('modelo/pca.pkl')
        clasificador_path = finders.find('modelo/modelo.pkl')

        features_stem_tfidf = joblib.load(features_stem_path) #1
        pca = joblib.load(pca_path) #2
        clasificador = joblib.load(clasificador_path) # 3
    except:
        features_stem_tfidf = joblib.load('/static/modelo/mat_tfidf.pkl') #1
        pca = joblib.load('/static/modelo/pca.pkl') #2
        clasificador = joblib.load('/static/modelo/modelo.pkl') # 3


    return features_stem_tfidf, pca, clasificador


def procesa_texto(texto):
    """
    Funcion para limpieza de texto de un mensaje
    """
    texto=texto.lower()

    part = texto.partition('http')
    part = part[0] + part[1] + ' ' + ' '.join(part[2].split(' ')[1:])
    texto = part

    part = texto.partition('bit.ly')
    part = part[0] + part[1] + ' ' + ' '.join(part[2].split(' ')[1:])
    texto = part

    texto = re.sub('^[ \t]+|[ \t]+$', '', texto) 

    texto = re.sub('[^\w\s]','', texto)

    texto = re.sub('^[ \t]+|[ \t]+$', '', texto)

    texto = give_emoji_free_text(texto)

    texto = unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')
    wc = len(str(texto).split(" "))
    texto = re.sub('ola|buena noche|buenos dias|buenos dia|buen dia|buenas noches|buenas tardes|buenas tarde|buen dia|bien dia|buena tardes|buena tarde|saludos|hola','', texto)
    texto = re.sub('\n',' ', texto)
    texto = re.sub('^[ \t]+|[ \t]+$', '', texto)

    return texto , wc



def tokenize_and_stem(text):
    stemmer = SnowballStemmer("spanish")
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []

    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    stems = [stemmer.stem(t) for t in filtered_tokens]

    return stems


def predice_modelo(contact_uuid, texto, token, minimo_conc, pre_categoria, hora_mensaje):
    """
    Función de producción de modelo. Se construye la tabla de features
    en el mismo orden en el que entró al entrenamiento: 33 factores, word count y hora.

    Notas:
    - Se agregaron categorías para ayudar a la clasificación de mensajes.
    - Pregunta médica y pregunta busca trabajo son ambas preguntas, pero contienen mensajes muy diferentes.

    - Los mensajes que sean emergencias y el modelo no prediga correctamente, son los errores más costosos.
      Por ello, si la probabilidad de emergencia es mayor a 1%, se le asignará la clase cuya probabildad sea la máxima.
    - El modelo calcula una predicción para todos los mensajes. Sin embargo, habrá veces 
      que dos o más clases tengan alta probabilidad. Para controlar ese caso, se calcula un índice de concentración.
    """

    # Cargamos pkls
    features_stem_tfidf, pca, clasificador = load_pkl()

    # La hora del nuevo mensaje se obtiene de una petición GET al api de rapidpro
    # response = requests.get(
    #     "http://rapidpro.datos.gob.mx/api/v2/runs.json",
    #     headers={"Authorization": token},
    #     params={"contact": contact_uuid}
    # )

    # response = json.loads(response.text)
    # hora = response['results'][0]['created_on']
    # Se busca el último mensaje y extra su hora (en entero del 0 al 24).
    # hora = int(hora[11:13])

    hora = hora_mensaje

    # Aplicamos las mismas funciones al texto nuevo
    texto, wc  = procesa_texto(texto)
    texto = tokenize_and_stem(texto)
    texto = ' '.join(texto)

    wc = reshape(wc, (-1, 1))
    hora = reshape(hora, (-1, 1))

    tfidf = features_stem_tfidf.transform([texto])
    features = pca.transform(tfidf)

    features = concatenate((features, wc), axis=1)
    features = concatenate((features, hora), axis=1)

    if pre_categoria == 'pregunta':
        pred = pre_categoria
        proba = array([
            0, # Emergencia
            0, # Informacion
            0, # Nacimiento
            0, # Otra
            0, # Pregunta
            0
        ])
        max_proba = 0
        conc = 0
    else:
        proba = clasificador.predict_proba(features)
        proba_orig = proba

        # Se saca la probabilidad predicha de cada clase y se suman las probabilidades que van juntas.
        proba = array([
            proba[0][0], # Emergencia
            proba[0][1], # Informacion
            proba[0][2], # Nacimiento
            proba[0][3] + proba[0][4], # Otra
            proba[0][5] + proba[0][6] + proba[0][7], # Pregunta
            proba[0][8]
        ])

        pred = proba.argmax()

        # Se calcula un índice de concentración para desempate de categorias
        conc = proba * 100
        conc = conc * conc
        conc = conc.sum()

        # Entre más alto, más concentrada está la probabilidad en una sola clase.
        pred = proba.argmax()
        max_proba = proba.max()

        pred = str(vectorize(label_map.get)(pred))

        # Si el índice está por debajo de 4,000 el modelo no asignará una clase.
        if conc < minimo_conc:
            pred = 'No_se_puede_asignar_etiqueta'

    # Si la probabilidad de emergencia es mayor a 1%, se le asignará la clase cuya probabildad sea la máxima. 
    if proba[0] > 0.01:
        pred = pred + '-FLAG'

    out = {
        'pred':pred,
        'probabilidad_maxima': max_proba,
        'indice_seguridad': conc,
        'proba': proba
    }

    return out


if __name__ == "__main__":
    import os
    from datetime import datetime

    #ID CONTACTO
    contact_uuid='fb82e199-ac49-41cd-a269-1654f29e180b'
    #TEXTO DEL MENSAJE
    texto= "22.11.1997"
    # TOKEN DEL API
    token="Token {}".format(os.environ.get('RP_TOKEN'))
    minimo_conc = 4000

    resultado = predice_modelo(contact_uuid, texto, token, minimo_conc, 'pregunta', datetime.now().hour)
    print(resultado)
