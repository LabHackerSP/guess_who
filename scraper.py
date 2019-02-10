from urllib.request import urlopen, urlretrieve
from urllib.parse import urlparse, urljoin, quote
from bs4 import BeautifulSoup
import json, os, re

url_vereadores = "http://www.saopaulo.sp.leg.br/vereadores/?filtro=ordem-alfabetica"
url_mesa = "http://www.saopaulo.sp.leg.br/vereadores/?filtro=mesa-diretora"
url_comissoes = "http://www.saopaulo.sp.leg.br/atividade-legislativa/comissoes/?p="
# TODO: deduzir IDs pela página ao invés de hardcoded
p_comissoes = [
  "41810",
  "41824",
  "41815",
  "41603",
  "41817",
  "41823",
  "41816",
  "86804",
  "41802",
  "41609",
  "41826",
  "41809",
  "41806"
]

# variaveis a preencher
vereadores = []
partidos = []
comissoes = []

# baixa uma foto para uma pasta e retorna seu diretório
def getfoto(url, base_path):
  a = urlparse(url)
  encoded_link = urljoin(url, quote(a.path.encode("utf-8")))
  path = os.path.join(base_path, os.path.basename(a.path))
  if not os.path.exists(path):
    urlretrieve(encoded_link, path)
  return path
  
# exporta json do mesmo modo para cada lista
def savejson(data, path):
  with open(path, 'w', encoding='utf-8') as out:
    json.dump(data, out, ensure_ascii=False, indent=2, sort_keys=True)

# cria lista de vereadores
page_vereadores = urlopen(url_vereadores)
soup_vereadores = BeautifulSoup(page_vereadores, 'html.parser')
vereadores_list = soup_vereadores.select("article.vereador-profile-thumb")

for elem in vereadores_list:
    vereador = {}
    img_partido = elem.find(attrs={"class":"vereador-party"}).find("img")
    img_vereador = elem.find(attrs={"class":"vereador-picture"}).find("img")
    vereador["foto"] = getfoto(img_vereador.get("src"), "fotos/")
    vereador["nome"] = elem.find(attrs={"class":"vereador-name"}).find("a").string.strip()
    vereador["partido"] = img_partido.get("title")
    vereadores.append(vereador)

    # busca se partido já foi gravado, se não cria entrada
    if not any(p["sigla"] == vereador["partido"] for p in partidos):
      partido = {}
      partido["sigla"] = vereador["partido"]
      partido["img"] = getfoto(img_partido.get("src"), "partidos/")
      partidos.append(partido)

# adiciona mesa diretora a vereadores
page_mesa = urlopen(url_mesa)
soup_mesa = BeautifulSoup(page_mesa, 'html.parser')
mesa_list = soup_mesa.select("article.vereador-profile-thumb")

for elem in mesa_list:
  nome = elem.find(attrs={"class":"vereador-name"}).find("a").string.strip()
  vereador = next((x for x in vereadores if x["nome"] == nome), None)
  if vereador != None:
    vereador["mesa_diretora"] = elem.find(attrs={"class":"vereador-position"}).string.strip()

# cria comissões e adiciona comissões à lista de vereadores
for comissao in p_comissoes:
  url_comissao = url_comissoes + comissao
  page_comissao = urlopen(url_comissao)
  soup_comissao = BeautifulSoup(page_comissao, 'html.parser')

  comissao = {}
  comissao["nome"] = soup_comissao.find("header", attrs={"class":"article-header"}).find(attrs={"class":"page-title"}).string.strip()
  img_comissao = soup_comissao.find("img", attrs={"class":"wp-post-image"})
  comissao["logo"] = getfoto(img_comissao.get("src"), "comissoes/")

  # busca membros da comissão
  comissao_list = soup_comissao.select("article.vereador-profile-thumb")
  comissao["membros"] = {}

  for elem in comissao_list:
    nome = elem.find(attrs={"class":"vereador-name"}).find("a").string.strip()
    cargo = elem.find("h4").string.strip()
    comissao["membros"][nome] = cargo
    vereador = next((x for x in vereadores if x["nome"] == nome), None)
    if vereador != None:
      try:
        vereador["comissoes"][comissao["nome"]] = cargo
      except KeyError:
        vereador["comissoes"] = {comissao["nome"] : cargo}

  comissoes.append(comissao)

savejson(vereadores, "dados/vereadores.json")
savejson(partidos, "dados/partidos.json")
savejson(comissoes, "dados/comissoes.json")
