from utils import ProxyRapidpro

#Constante para ejemplo
contact_uuid = "a78fe386-b115-410b-911c-5a957e0da2d9"

def main():

    #Area de mensajes a consola:
    print("*"*20)
    print("* Ejemplo de uso del api para seguimiento de msg *")
    print("*"*20)
    print()
    print()
    print("Mostramos el historico de las conversaciones")
    print("de %s"%(contact_uuid) )


    #Construccion del proxy al API de rapidpro 
    rapidpro_c = ProxyRapidpro()
    runs = rapidpro_c.get_contact_history(contact_uuid)

    #Imprimimos las ultimas 10 conversaciones:
    last_conversation = [r.flow.name for r in runs][:10]
    print ("Las ultimas 10 conversaciones son: \n %s"%(
            ", ".join(last_conversation)))



if __name__ == '__main__':
    main()
