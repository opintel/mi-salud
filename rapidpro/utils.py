import requests
import configparser
from rapidpro.rapidpro_python.temba_client.v2 import TembaClient

#Read tokens
config = configparser.ConfigParser()
config.read('rapidpro/keys.ini', encoding="utf-8")
TOKEN_MATERNO = config["MATERNO"]["TOKEN"]
ENDPOINT_URL = "http://10.20.55.67"

class ProxyRapidpro():

    def __init__(self,  token = None):
        self.token = token if token else TOKEN_MATERNO
        self.rapidpro_client = TembaClient(ENDPOINT_URL,self.token)

   
    def get_contact_history(self, contact_uuid):
        runs = self.rapidpro_client.get_runs(contact=contact_uuid)
        runs = sorted([r for r in runs], key = lambda x: x.created_on)
        return runs


    def make_request(self, endpoint_url):
       token = 'token %s' % self.token
       headers = {'content-type': 'application/json', 'Authorization': token}
       r = requests.get(endpoint_url, headers = headers)
       return r.json() 


    def get_last_messages(self, contact_uuid):
       url = 'http://'+ENDPOINT_URL+'/api/v2/messages.json?contact=%s&top=True'%(
             contact_uuid)
       result_json = self.make_request(url)
       return result_json
        
