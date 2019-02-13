from xml.dom import minidom
import xpath
import os
import json
import base64
import mimetypes

with open("templates/card_template.svg", 'r') as f:
  _carta = minidom.parse(f)

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

for vereador in vereadores:
  # começa com carta mestre
  carta = _carta.cloneNode(True)

  # troca nome
  elem_nome = xpath.find("//*[@id='texto_nome']/tspan/text()",carta)[0]
  elem_nome.nodeValue = vereador["nome"]

  # troca partido
  elem_partido = xpath.find("//*[@id='image_partido']", carta)[0]
  elem_partido.removeAttribute("sodipodi:absref")
  elem_partido.setAttribute("xlink:href", openBase64(partidos[vereador["partido"]]))

  # troca foto
  elem_foto = xpath.find("//*[@id='image_foto']", carta)[0]
  elem_foto.removeAttribute("sodipodi:absref")
  elem_foto.setAttribute("xlink:href", openBase64(vereador["foto"]))

  # troca sala
  elem_sala = xpath.find("//*[@id='texto_sala']/tspan/text()", carta)[0]
  try:
    if vereador["sala"]:
      elem_sala.nodeValue = str(vereador["sala"])
  except KeyError:
    elem_sala.parentNode.parentNode.parentNode.removeChild(elem_sala.parentNode.parentNode)
    elem_sala_caption = xpath.find("//*[@id='texto_sala_caption']", carta)[0]
    elem_sala_caption.parentNode.removeChild(elem_sala_caption)

  # troca comissões
  comissao = 1
  elem_comissao = xpath.find(f"//*[@id='image_comiss{comissao}']", carta)[0]
  elem_comissao.removeAttribute("sodipodi:absref")

  # tenta primeira comissão mesa diretora
  try:
    if vereador["mesa_diretora"]:
      elem_comissao.setAttribute("xlink:href", openBase64("comissoes/mesa_diretora.png"))
      comissao += 1
      elem_comissao = xpath.find(f"//*[@id='image_comiss{comissao}']", carta)[0]
      elem_comissao.removeAttribute("sodipodi:absref")
  except KeyError:
    pass

  # tenta comissões
  try:
    for c in vereador["comissoes"]:
      elem_comissao.setAttribute("xlink:href", openBase64(comissoes[c]))
      comissao += 1
      elem_comissao = xpath.find(f"//*[@id='image_comiss{comissao}']", carta)[0]
      elem_comissao.removeAttribute("sodipodi:absref")
  except KeyError:
    pass

  # remove icones extra
  while comissao <= 6:
    elem_comissao = xpath.find(f"//*[@id='image_comiss{comissao}']", carta)[0]
    elem_comissao.parentNode.removeChild(elem_comissao)
    comissao += 1

  with open(f'cartas/{vereador["nome"]}.svg', 'w', encoding='utf-8') as f:
    carta.writexml(f)