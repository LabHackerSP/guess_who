from xml.dom import minidom
import xpath
import os
import json
import copy

with open("templates/page_template.svg", 'r', encoding='utf-8') as f:
  _page = minidom.parse(f)

with open("dados/vereadores.json", 'r', encoding='utf-8') as f:
  vereadores = json.load(f)

def gera_page(start, end, num):
  page = _page.cloneNode(True)

  for i in range(start, end):
    id_carta = f"carta{i - start + 1}"
    elem_template = xpath.find(f"//*[@inkscape:label='{id_carta}']", page)[0]

    try:
      vereador = vereadores[i]
    except IndexError:
      elem_template.parentNode.removeChild(elem_template)
      continue

    # debug
    #print(f"{id_carta} - {vereador['nome']}")

    # cria grupo de carta
    with open(f"cartas/{vereador['nome']}.svg", 'r', encoding='utf-8') as f:
      carta = minidom.parse(f)

    elem_carta = page.createElement("g")
    elem_carta.setAttribute("id", id_carta)
    elem_layer = xpath.find(f"//g[@id='layer1']", carta)[0]
    for child in elem_layer.childNodes:
      elem_carta.appendChild(child.cloneNode(True))

    # magic numbers
    x = float(elem_template.getAttribute("x")) + 4
    y = float(elem_template.getAttribute("y")) - 204
    elem_carta.setAttribute("transform", f"translate({x},{y})")

    elem_template.parentNode.insertBefore(elem_carta, elem_template)
    elem_template.parentNode.removeChild(elem_template)

  with open(f'output/page_{int(num)+1}.svg', 'w', encoding='utf-8') as out:
    page.writexml(out)

for i in range(0, 56, 8):
  gera_page(i, i+8, i/8)