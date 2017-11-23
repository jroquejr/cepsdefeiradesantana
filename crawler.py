import requests
from bs4 import BeautifulSoup
import json
from time import sleep


CEPURL = "http://www.buscacep.correios.com.br/sistemas/buscacep/resultadoBuscaCepEndereco.cfm?t"


def cep_retrieve(cep):
    response = requests.post(CEPURL, data={
        "relaxation": cep,
        "Metodo": "listaLogradouro",
        "TipoConsulta": "relaxation",
        "StartRow": 1,
        "EndRow": 10,
    }, timeout=10)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as ex:
        raise ex

    return response.text


def cep_extract(html):

    soup = BeautifulSoup(html, 'html.parser')
    linhas = soup.select('.tmptabela tr')

    if len(linhas) <= 1:
        return None

    linhas = linhas[1:]

    retorno = []

    for linha in linhas:

        colunas = linha.select('td')

        cidade = ""
        estado = ""

        cidade_uf = colunas[2].text
        if cidade_uf:
            cidade, estado = cidade_uf.split('/', 1)

        item = {
            'logradouro': colunas[0].text.strip(),
            'bairro': colunas[1].text.strip(),
            'cidade': cidade.strip(),
            'estado': estado.strip(),
            'cep': colunas[3].text.replace('-', '').strip()
        }

        retorno.append(item)

    return retorno

def get_bairro_ceps(cep):
    html_doc = cep_retrieve(cep)
    return cep_extract(html_doc)

if __name__ == "__main__":

    range_ceps = range(44000001,  44149999)
    grande_data = []
    counter = 0

    for cep in range_ceps:
        ceps_data = get_bairro_ceps(cep)

        if counter == 15:
            counter = 0
            sleep(1)
        else:
            counter += 1

        if ceps_data == None:
            print('Nada para {}'.format(cep))
            continue;
        
        print('achei para {}'.format(cep))

        for cep_found in ceps_data:
            grande_data.append(cep_found)
    
    
    with open('data.json', 'w') as outfile:
        json.dump(grande_data, outfile, indent=2)
