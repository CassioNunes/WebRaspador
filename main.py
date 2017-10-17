#!/root/scrapingEnv/bin/python3

from urllib.request import urlopen, Request
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re
import sqlite3
import time
import sys

JORNAIS  = {

    "http://www.viomundo.com.br/" : {

            'sessoes' :
                            ['politica','denuncias','voce-escreve','entrevistas','falatorio'],

            'tags_sessao' : 'h2',
                            
            'tags_artigo' : {
                            'delimitador' : {"div":{"class":"post"}},
                            'data': {'span':{'class':'date'}},
                            'titulo': {"h1":{'void':'void'}},
                            'corpo': {"div":{"class":"text"}},
                            'comando': {'[eliminate_end]' : {'strong':2}},
                            },
                                    },
    
    #"http://www.diariodocentrodomundo.com.br/" : {

            #'sessoes' :
                    #["politica","brasil","mundo","comportamento","cultura","economia","esporte","especiais-dcm"],

            #'tags_sessao' : {

                            #},
            #'tags_artigo' : {

                            #},
                                                #},
    #"http://jornalggn.com.br/" : {
        
            #'sessoes':
                    #["politica","desenvolvimento","economia","cultura","consumidor","cidadania","analise","opiniao","artigos","europa","geopolitica","tecnologia"],
            #'tags_artigo' : {

                    #},
                                 #},
                                 
    #"http://apublica.org/" : {
    
            #'sessoes':
                    #["reportagens"],
            #'tags_sessao' : {

                            #},
            #'tags_artigo' : {

                            #},
                             #},
                            
    #"http://www.metropoles.com/" : {
            #'sessoes' : 
                    #["distrito-federal","concursos-e-empregos","entretenimento","gastronomia","vida-e-estilo","brasil","mundo"],
            #'tags_sessao' : {

                            #},
            #'tags_artigo' : {

                            #},
                                    #},
                                    
    #"https://www.cartacapital.com.br/" : {
            #'sessoes' :
                    #["politica","internacional","sociedade","cultura","economia"],
            #'tags_sessao' : {

                            #},
            #'tags_artigo' : {

                            #},
                                         #},
                                         
    #"https://www.brasildefato.com.br/" : {
            #'sessoes':
                    #["opiniao","politica","direitos_humanos","cultura","geral","internacional","especiais"],
            #'tags_sessao' : {

                            #},
            #'tags_artigo' : {

                            #},
                                         #},
                                         
    #"http://veja.abril.com.br/" : {
            #'sessoes':
                    #["politica","mundo","brasil","entretenimento","economia","ciencia",],
            #'tags_sessao' : {

                            #},
            #'tags_artigo' : {

                            #},
                                   #},
                                   
    #"http://www.bbc.com/portuguese" : {
            #'sessoes' :
                    #["brasil","internacional"],
            #'tags_artigo' : {
                            #},
                                        #},
} #/JORNAIS

TAGS = {
    #"endereco do site" : "["link para noticia contida na pagina da sessao","area da noticia na pagina","sessao","titulo",
    #"data","autor","texto da noticia","[comando para tratar texto]"]",
    "http://www.viomundo.com.br/" : ["h2" , {"div":{"class":"post"}} , {"div":{"class":"category"}},"h1", {"span":{"class":"date"}} , {"[last_seq]":"strong"} , {"div":{"class":"text"}} , {"[eliminate_end]" : {"strong":2}}],
    "http://www.diariodocentrodomundo.com.br/" : ["h3"],
    "http://jornalggn.com.br/" : [{"div" : {"class":"field-capa-dp-titulo-value"}}],
    "http://apublica.org/" : ["h2"],
    "http://www.metropoles.com/" : ["h1"],
    "https://www.cartacapital.com.br/" : ["h4"],
    "https://www.brasildefato.com.br/" : [{"div" : {"class":"news-item-link divisor"}}],
    "http://www.bbc.com/portuguese/" : [{"div" : {"class":"eagle-item__body"}}],
}

######Funcoes

def eprint(*args, **kwargs):
    ''' Funcao imprime argumentos via stderr
    
    source: https://stackoverflow.com/questions/5574702/how-to-print-to-stderr-in-python
    '''
    print(*args, file=sys.stderr, **kwargs)


def openLink(articleUrl):
    '''
        Funcao tenta abrir um link HTML e tenta administrar possiveis erros
    '''

    try:
        html = urlopen(Request(articleUrl, headers={'User-Agent':'Mozilla'}))
    except HTTPError as e:
        print(e)
        return None #insert plan B here
    else:
        if html is None:
            print("URL not found.")
            return None
        else:
            bsObj = BeautifulSoup(html,'html.parser')
            return bsObj

###main

#<inicia banco de dados>
try:
    db = sqlite3.connect('mydb_scrap.sqlite')
    cursor = db.cursor()
    cursor.execute('''
                       CREATE TABLE IF NOT EXISTS
                       origem(id INTEGER PRIMARY KEY, origem TEXT)''')

    cursor.execute('''
                       CREATE TABLE IF NOT EXISTS
                       sessoes(id INTEGER PRIMARY KEY, sessao TEXT)''')


    cursor.execute('''
                       CREATE TABLE IF NOT EXISTS
                       autores(id INTEGER PRIMARY KEY, nome TEXT)''')


    cursor.execute('''
                       CREATE TABLE IF NOT EXISTS
                       tipoTexto(id INTEGER PRIMARY KEY, nome TEXT)''')
    
    cursor.execute('''
                       CREATE TABLE IF NOT EXISTS
                       textos(id INTEGER PRIMARY KEY, titulo TEXT, autor INTEGER, data TEXT, origem INTEGER, sessao INTEGER, tipoTexto INTEGER, link TEXT, texto TEXT)''')

except Exception as e:
    db.rollback()
    raise e
finally:
    db.close()

#</inicia banco de dados>


for jornal in JORNAIS:
    eprint(jornal)
    sessoes = JORNAIS[jornal]['sessoes']
    eprint(sessoes)
    links_noticias = set()
    for sessao in sessoes:
        eprint(jornal+sessao)
        tempLink = jornal+sessao
        bsObj = openLink(tempLink)

        tag = JORNAIS[jornal]['tags_sessao'] #tags da sessao
        
        if type(tag) == type({}):
            for key, value in tag.items():
                tag_Type = key
                tag_Att = value #value é um dicionário, daí a necessidade do for abaixo 
                break #mais de uma chave no dicionario, so a primeira eh verificada
            for key, value in tag_Att.items():
                tag_Type_Att = key
                tag_Type_Att_Value = value 
                break #mais de uma chave no dicionario, so a primeira eh verificada
            listaItens = bsObj.findAll(tag_Type, {tag_Type_Att : tag_Type_Att_Value})
        elif type(tag) == type('string'):
            eprint("elemento contendo link para noticia: "+tag)
            listaItens = bsObj.findAll(tag)
        Base_Url = jornal

        for item in listaItens: #em cada item um link para uma noticia
            try:
                leaf_part=str(item.find('a').attrs["href"])
            except AttributeError as e:
                #eprint("Elemento "+str(item)+"da página nao é link html.\n"+str(e))
                break
            else:
                link = urljoin(Base_Url, str(item.find('a').attrs["href"]))
                links_noticias.add(link)
                #eprint(link)
        time.sleep(60)
        #exit() #aborta apos a primeira sessao de um jornal
        
    print(links_noticias)
    #eprint(links_noticias)
    time.sleep(60)
    #exit() #aborta apos selecionados os links de todas as sessoes registradas de um jornal

    

