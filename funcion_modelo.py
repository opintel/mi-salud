
# coding: utf-8

# In[14]:


import requests
import json
from sklearn.externals import joblib
import re
import script_reglas
import unicodedata
from numpy import reshape, concatenate, unique, vectorize, array
from nltk.stem.snowball import SnowballStemmer
import nltk


# In[15]:


features_stem_tfidf=joblib.load('./modelo/mat_tfidf.pkl') #1
pca=joblib.load('./modelo/pca.pkl')  #2
clasificador=joblib.load('./modelo/modelo.pkl') # 3


# Cargamos los pkls que se generaron en entrenamiento modelo y les aplicamos las mismas funciones al texto nuevo para que entre igual que el texto con el que se entrenó. 
# 
# En la función de producción de modelo construimos la tabla de features en el mismo orden en el que entró al entrenamiento: 33 factores, word count y hora. La hora del nuevo mensaje saldrá de una petición GET al api de rapidpro. Se busca el último mensaje y extra su hora (en entero del 0 al 24). 
# 
# Se saca la probabilidad predicha de cada clase y se suman las probabilidades que van juntas. (Se agregaron categorías para ayudar a la clasificación de mensajes. Pregunta médica y pregunta busca trabajo son ambas preguntas, pero contienen mensajes muy diferentes). 
# 
# #### Se agrega: 
# * Pregunta:
#  + Búsqueda de trabajo
#  + Preguntas médicas
#  + Otras Preguntas  
# * Otra:
#  + Quejas
#  + Otras
#  
# #### Índice de concentración
# 
# El modelo calcula una predicción para todos los mensajes. Sin embargo, habrá veces que dos o más clases tienen alta probabilidad. Para controlar ese caso, se calcula un índice de concentración. Entre más alto, más concentrada está la probabilidad en una sola clase. Si el índice está por debajo de 4,000 el modelo no asignará una clase. El modelo asignará una clase a aproximadamente el 80% de los mensajes enviados.
# 
# #### Flag de emergencias
# 
# Los mensajes que sean emergencias y el modelo no prediga correctamente, son los errores más costosos. Por ello, si la probabilidad de emergencia es mayor a 1%, se le asignará la clase cuya probabildad sea la máxima. Sin embargo, se 

# In[63]:


def procesa_texto(texto):
    texto=texto.lower()
    
    
    part=texto.partition('http')
    part=part[0]+part[1]+' '+ ' '.join(part[2].split(' ')[1:])
    texto=part
    
    part=texto.partition('bit.ly')
    part=part[0]+part[1]+' '+ ' '.join(part[2].split(' ')[1:])
    texto=part
    
    texto=re.sub('^[ \t]+|[ \t]+$', '', texto) 

    texto=re.sub('[^\w\s]','', texto)

    texto=re.sub('^[ \t]+|[ \t]+$', '', texto)

    texto=script_reglas.give_emoji_free_text(texto)

    texto=unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')
    wc=len(str(texto).split(" "))
    texto=re.sub('ola|buena noche|buenos dias|buenos dia|buen dia|buenas noches|buenas tardes|buenas tarde|buen dia|bien dia|buena tardes|buena tarde|saludos|hola','', texto)
    texto=re.sub('\n',' ', texto)
    texto=re.sub('^[ \t]+|[ \t]+$', '', texto)
    return texto , wc

stemmer = SnowballStemmer("spanish")


def tokenize_and_stem(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    stems = [stemmer.stem(t) for t in filtered_tokens]
    return stems



def predice_modelo(contact_uuid, texto, token):
    response = requests.get("http://rapidpro.datos.gob.mx/api/v2/runs.json",
                            headers={"Authorization": token},
                            params={"contact": contact_uuid})
    response=json.loads(response.text)
    hora=response['results'][0]['created_on']
    hora=int(hora[11:13])

    texto, wc =procesa_texto(texto)
    
    texto=tokenize_and_stem(texto)
    texto=' '.join(texto)
    
    wc=reshape(wc, (-1, 1))
    hora=reshape(hora, (-1, 1))


    tfidf=features_stem_tfidf.transform([texto])
    features=pca.transform(tfidf)

    features=concatenate((features, wc), axis=1)
    features=concatenate((features, hora), axis=1)



    proba=clasificador.predict_proba(features)

    proba_orig=proba
    
    proba=array([proba[0][0], #'emergencia'
    proba[0][1], #Informacion
    proba[0][2], #Nacimiento
    proba[0][3]+proba[0][4], #otra
    proba[0][5]+proba[0][6]+proba[0][7], #Pregunta
    proba[0][8]]) #Respuesta
    
    pred=proba.argmax()
    
    conc=proba*100
    conc=conc*conc
    conc=conc.sum()


    pred=proba.argmax()
    max_proba=proba.max()
    

    
    pred=str(vectorize(label_map.get)(pred))
    
    
    if conc<minimo_conc:
        pred='No_se_puede_asignar_etiqueta'
    if proba[0]>0.01:
        pred=pred+'-FLAG'
    
    out={'pred':pred,
        'probabilidad_maxima':max_proba,
        'indice_seguridad':conc, 
        'proba':proba}
    return out


# In[64]:



##THRESHOLD DE CONCENTRACIÓN. ABAJO DE ESTO NO SE PUEDE PREDECIR

minimo_conc=4000

##ETIQUETAS DE PREDICCIONES (NO CAMBIAR)
label_map={0:'emergencia', 1:'informacion',
           2:'nacimiento', 3:'otra',
           4:'pregunta', 5:'respuesta'}


# In[93]:


#ID CONTACTO
contact_uuid='fb82e199-ac49-41cd-a269-1654f29e180b'
#TEXTO DEL MENSAJE
texto= "22.11.1997"
# TOKEN DEL API
token="Token [inserta aqui]"

predice_modelo(contact_uuid, texto, token)






# In[94]:


get_ipython().system('jupyter nbconvert --to script funcion_modelo.ipynb')

