# coding: utf-8
import re
from emoji import UNICODE_EMOJI
from unicodedata import normalize


def is_emoji(text):
    """
    Funcion que cuenta si un texto contiene emojis
    """
    count = 0

    for emoji in range(1, len(UNICODE_EMOJI)):
        count += text.count(list(UNICODE_EMOJI.keys())[emoji])

    return count


def give_emoji_free_text(text):
    """
    Funcion que limpia texto de emojis
    """
    allchars = [str for str in text]
    emoji_list = [c for c in allchars if c in UNICODE_EMOJI]
    clean_text = ' '.join([str for str in text.split() if not any(i in str for i in emoji_list)])

    return clean_text


def procesa_reglas(texto):
    """
    Reglas basicas de procesamiento
    de texto. 

    Salida:
     {
        'result':out,
        'texto':texto_orig,
        'texto_proc':texto,
        'wc':wc,
        'cc':cc
    }

    """
    result = []
    out = []
    texto_orig = texto

    # Todo minusculas
    texto = texto.lower()

    #print('pasando a minusculas')
    #print(texto)

    # Quitando trailing leading
    texto = re.sub('^[ \t]+|[ \t]+$', '', texto) 

    #print('quitar trailing leading')
    #print(texto)

    # Palabra aborto
    if (bool(re.search('aborto', texto))) & (len(out) == 0):
       # print('es hasta luego')
        out = 'aborto'

    # Despedidas
    if (bool(re.search('hasta luego', texto))) & (len(out) == 0):
       # print('es hasta luego')
        out = 'hasta luego'

    # Facebook link o Facebook like
    if (bool(re.search('https://scontent', texto))) & (len(out) == 0):
      #  print('es like')
        out = 'like-fb'

    # Conteo de caracteres
    wc = len(str(texto).split(" "))
    cc_1 = cc = len(str(texto))

    # Es link de twitter
    if bool(re.search('t.co', texto)) & (wc == 1):
       # print('es twitter')
        out = 'twitter-image'

    #print('nchar:'+ str(cc))
    #print('wc:'+ str(wc))

    # Es pregunta
    if (len(re.findall("\?", texto)) == cc) & (len(out)==0):
       # print('puros ?')
        out = 'pregunta'

    # Retirar signos de puntuacion
    texto=re.sub('[^\w\s]','', texto)
    #print('quitar punct '+texto)

    # Quitando trailing leading
    texto=re.sub('^[ \t]+|[ \t]+$', '', texto)
    #print('quitar leading y trailing '+texto)

    #Contar palabras y caracteres otra vez
    wc=len(str(texto).split(" "))
    cc=len(str(texto))

    #print('nchar: '+ str(cc))
    #print('wc: '+ str(wc))

    # Conteo de emojis en el mensaje
    emojis=is_emoji(texto)
    #print('conteo de emojis: '+ str(emojis))

    # Solo emojis
    if (emojis == cc) & (cc_1 > 0) & (len(out) == 0):
        #print('puros emojis')
        out = 'emoji'

    if (cc_1 == 1) & (len(out) == 0) & bool(re.search('[a-z]|[A-Z]', texto)):
       # print('es twitter')
        out='otra'

    # Limpiar texto de emojis
    texto=give_emoji_free_text(texto)
    #print('quitar emojis:'+ texto)

    # Es solo spam (links a otra cosa)
    if (wc == 1) & (bool(re.search('https|http', texto))) & (len(out) == 0):
        #print('es spam')
        out='spam'

    # Solo ASCII sin acentos
    texto = normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')
    #print('quitar acentos '+texto)

    # Afirmacion (Si)
    if (cc == 2) & (bool(re.search('si|sii|ssi', texto))) & (len(out) == 0):
        #print('es: sí')
        out = 'si'

    # Negacion (No)
    if (cc == 2) & (bool(re.search('no|noo|nno', texto))) & (len(out) == 0):
        #print('es: no')
        out = 'no'

    # Saludos
    if (wc == 1) & (bool(re.search('salu', texto))) & (len(out) == 0) & ~(bool(re.search('mi', texto))) & ~(bool(re.search('secret', texto))):
       # print('es: gracias')
        out = 'hola'

    # Gracias
    if (wc == 1) & (bool(re.search('gracias|graicas|gracia|graciad|graciaa', texto))) & (len(out) == 0):
       # print('es: gracias')
        out = 'gracias'

    # Ok
    if (wc <= 3) & (bool(re.search('ok|ook|okk', texto))) & (len(out) == 0):
        #print('es: ok')
        out = 'ok'

    # Saludos
    if (wc <= 2) & (bool(re.search('hola|holaa|hhola|hoola|holi|bonjour|ola', texto))) & (len(out) == 0):
        #print('es: hola')
        out = 'hola'

    # Saludos
    if (wc <= 4) & (bool(re.search('ola|bien dia|que tal|bn dia|hola|buenad tardes|buena tarde|buen dia|buena noche|buenas tardea|buenas tardes|buenas noches|buenos dias', texto))) & (len(out) == 0):
        #print('es: hola')
        out = 'hola'

    # Gracias
    if (wc <= 5) & (bool(re.search('gracias|graicas|gracia|graciad|graciaa|gracaias', texto))) & (len(out) == 0):
        #print('es: gracias')
        out = 'gracias'

    # Pregunta
    if (bool(re.search('horario', texto))) & (bool(re.search('atencion', texto))) & (len(out) == 0):
        #print('es: informacion (horario atencion)')
        out = 'pregunta'

    if (bool(re.search('telefono', texto))) & (bool(re.search('numero', texto))) & (wc < 10) & (len(out) == 0):
        #print('es: informacion (telefono)')
        out = 'pregunta'

    if (bool(re.search('what ', texto))) & (bool(re.search('number', texto))) & (len(out) == 0):
        #print('es: informacion (telefono)')
        out = 'pregunta'

    if (bool(re.search('added', texto))) & (len(out) == 0):
       # print('es: like (added)')
        out = 'like-fb'

    # Se debe clasificar por modelo
    if len(out) == 0:
        out = 'modelo'
    else:
        out = out

    out = {
        'result':out,
        'texto':texto_orig,
        'texto_proc':texto,
        'wc':wc,
        'cc':cc
    }

    return(out)


if __name__ == "__main__":
    texto = 'a'
    salida = procesa_reglas(texto)
    print(salida)
