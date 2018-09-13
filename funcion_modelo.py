
# coding: utf-8

# In[53]:


import requests
import json
from sklearn.externals import joblib
import re
import script_reglas
import unicodedata
from numpy import reshape, concatenate, unique, vectorize, array


# In[2]:


features_stem_tfidf=joblib.load('./modelo/mat_tfidf.pkl') #1
pca=joblib.load('./modelo/pca.pkl')  #2
clasificador=joblib.load('./modelo/modelo.pkl') # 3


# In[3]:


def procesa_texto(texto):
    texto=texto.lower()
    texto=re.sub('^[ \t]+|[ \t]+$', '', texto) 

    texto=re.sub('[^\w\s]','', texto)

    texto=script_reglas.give_emoji_free_text(texto)

    texto=unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')
    wc=len(str(texto).split(" "))
    texto=re.sub('ola|\n|buena noche|buenos dias|buenos dia|buen dia|buenas noches|buenas tardes|buenas tarde|buen dia|bien dia|buena tardes|buena tarde|saludos|hola','', texto)
    texto=re.sub('^[ \t]+|[ \t]+$', '', texto)
    return texto , wc


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

    wc=reshape(wc, (-1, 1))
    hora=reshape(hora, (-1, 1))


    tfidf=features_stem_tfidf.transform([texto])
    features=pca.transform(tfidf)

    features=concatenate((features, wc), axis=1)
    features=concatenate((features, hora), axis=1)



    proba=clasificador.predict_proba(features)


    conc=proba*100
    conc=conc*conc
    conc=conc.sum()



    proba_orig=proba
    proba=proba/counts


    pred=proba.argmax()
    max_proba=proba_orig.max()
    

    
    pred=str(vectorize(label_map.get)(pred))
    
    
    if conc<minimo_conc:
        pred='No_se_puede_asignar_etiqueta'
        
    out={'pred':pred,
        'probabilidad_maxima':max_proba,
        'indice_seguridad':conc}
    return out


# In[44]:


##Proporción por etiqueta (NO CAMBIAR)
counts=[0.00616016,  0.04928131,
        0.00718686,  0.28644764,
        0.14887064,0.34599589,
        0.05954825,  0.01848049,
        0.07802875]

##THRESHOLD DE CONCENTRACIÓN. ABAJO DE ESTO NO SE PUEDE PREDECIR

minimo_conc=4106.366777

##ETIQUETAS DE PREDICCIONES (NO CAMBIAR)
label_map={0:'otra',
          1:'informacion',
          2: 'nacimiento',
          3: 'respuesta',
          4: 'emergencia',
          5: 'pregunta',
          6: 'pregunta',
          7: 'otra',
          8: 'pregunta'}


# In[59]:


#ID CONTACTO
contact_uuid='fb82e199-ac49-41cd-a269-1654f29e180b'
#TEXTO DEL MENSAJE
texto='mi bebe ya nacio'
# TOKEN DEL API
token="Token [llenar aqui]"

predice_modelo(contact_uuid, texto, token)






