from xml.dom import minidom
import xpath
import os
import json
import base64
import mimetypes

with open("templates/cartela_template_1.svg", 'r', encoding='utf-8') as f:
  _cartela1 = minidom.parse(f)

with open("templates/cartela_template_2.svg", 'r', encoding='utf-8') as f:
  _cartela2 = minidom.parse(f)

with open("dados/vereadores.json", 'r', encoding='utf-8') as f:
  vereadores = json.load(f)

with open("dados/comissoes.json", 'r', encoding='utf-8') as f:
  _comissoes = json.load(f)
  comissoes = dict(map(lambda c: (c["nome"], c["logo"]), _comissoes))

with open("dados/partidos.json", 'r', encoding='utf-8') as f:
  _partidos = json.load(f)
  partidos = dict(map(lambda p: (p["sigla"], p["img"]), _partidos))

# abre imagem como base64
def openBase64(filename):
  with open(filename, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    mime, encoding = mimetypes.guess_type(filename)
    return f"data:{mime};base64,{encoded_string}"

def gera_vereadores(start, end, num):
  for i in range(start, end):
    vereador = vereadores[i]
    elem_vereador = elem_vereadores[i - start]

    # troca foto
    elem_foto = xpath.find("./*[@inkscape:label='foto']", elem_vereador)[0]
    elem_foto.setAttribute("xlink:href", openBase64(vereador["foto"]))

    # troca nome
    elem_nome = xpath.find("./*[@inkscape:label='nome']/tspan/text()",elem_vereador)[0]
    elem_nome.nodeValue = vereador["nome"]

    # troca partido
    elem_partido = xpath.find("./*[@inkscape:label='partido']", elem_vereador)[0]
    elem_partido.setAttribute("xlink:href", openBase64(partidos[vereador["partido"]]))

    # troca comissões
    comissao = 1
    elem_comissao = xpath.find(f"./*[@inkscape:label='comiss{comissao}']", elem_vereador)[0]
    
    # tenta primeira comissão mesa diretora
    try:
      if vereador["mesa_diretora"]:
        elem_comissao.setAttribute("xlink:href", openBase64("comissoes/mesa_diretora.png"))
        comissao += 1
        elem_comissao = xpath.find(f"./*[@inkscape:label='comiss{comissao}']", elem_vereador)[0]
    except KeyError:
      pass

    # tenta comissões
    try:
      for c in vereador["comissoes"]:
        elem_comissao.setAttribute("xlink:href", openBase64(comissoes[c]))
        comissao += 1
        elem_comissao = xpath.find(f"./*[@inkscape:label='comiss{comissao}']", elem_vereador)[0]
    except (KeyError, IndexError):
      pass

    # remove icones extra
    while comissao <= 5:
      elem_comissao = xpath.find(f"./*[@inkscape:label='comiss{comissao}']", elem_vereador)[0]
      elem_comissao.parentNode.removeChild(elem_comissao)
      comissao += 1

  with open(f'output/cartela_{num}.svg', 'w', encoding='utf-8') as f:
    cartela.writexml(f)

cartela = _cartela1.cloneNode(True)
elem_vereadores = xpath.find("//*[@inkscape:label='vereador']",cartela)
gera_vereadores(0, 21, 1)

cartela = _cartela2.cloneNode(True)
elem_vereadores = xpath.find("//*[@inkscape:label='vereador']",cartela)
gera_vereadores(21, 55, 2)
