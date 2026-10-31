"""
Produto de teste da integração Smart 4.0 x Senior ERP X.

Entrega 1: cadastrar o primeiro produto de teste, o mais simples possível
(Bloco Simples, com todas as lâminas pretas), gerar o código do produto e
preparar os arquivos para enviar à Senior, que vai criar o item no ERP.

O modelo de dados segue a loja do repositório bancada-smart
(lib/types.ts e lib/constants.ts):
    - blockType: "simple" (1 caixa), "double" (2 caixas), "triple" (3 caixas)
    - cada caixa tem uma cor de base (boxColor) e 3 lâminas laterais
      (side1Color = frente, side2Color = direita, side3Color = topo)
    - os pedidos são enviados à Senior com o código em items[].product.code

Uso:
    python3 produto_teste.py

Arquivos gerados na pasta "saida/":
    produto_<codigo>.json   ficha do produto para a Senior
    produto_<codigo>.csv    a mesma ficha em formato de planilha
    produto_loja.json       o produto no formato "Product" da loja (lib/types.ts)
    mensagem_senior.txt     texto pronto para enviar à Senior
"""

import csv
import json
from pathlib import Path
from typing import Dict, List

# ---------------------------------------------------------------------------
# CONFIGURAÇÃO EDITÁVEL
# ---------------------------------------------------------------------------

# Dados da loja. Ajuste se a loja usada mudar.
LOJA = {
    "nome": "Bancada Smart 4.0 - E-commerce",
    "url": "https://bancadasmart.vercel.app",
    "repositorio": "https://github.com/emanoelsp/bancada-smart",
}

# Produto de teste: Bloco Simples, base preta, todas as lâminas pretas.
TIPO_BLOCO = "simple"     # "simple", "double" ou "triple"
COR_BASE = "black"        # cor da caixa base
COR_LAMINAS = "black"     # cor de todas as lâminas
UNIDADE_MEDIDA = "UN"

# Prefixo usado pela loja nos códigos de produto (lib/senior-api.ts).
PREFIXO_CODIGO = "SMART40"

# True:  o código identifica a configuração (ex.: SMART40-SIMPLE-BLACK).
# False: o código é só o tipo de bloco (SMART40-SIMPLE), que é o que a loja
#        envia hoje em items[].product.code.
INCLUIR_CONFIGURACAO_NO_CODIGO = True

# ---------------------------------------------------------------------------
# DADOS DA SMART 4.0
# ---------------------------------------------------------------------------

# Tipos de bloco, como em BLOCK_TYPES (lib/constants.ts).
BLOCK_TYPES = {
    "simple": {"label": "Bloco Simples", "caixas": 1, "preco": 150.0},
    "double": {"label": "Bloco Duplo", "caixas": 2, "preco": 280.0},
    "triple": {"label": "Bloco Triplo", "caixas": 3, "preco": 400.0},
}

# Manual Smart 4.0: "três locais para lâminas em cada base".
LAMINAS_POR_CAIXA = 3

# Cores de base, como em BOX_COLORS (lib/constants.ts).
CORES_BASE = {
    "black": "Preta",
    "blue": "Azul",
    "red": "Vermelha",
}

# As seis cores de lâmina da planta (manual Smart 4.0, Figura 06).
# A letra é usada no código quando a configuração tem cores diferentes.
CORES_LAMINA = {
    "red": {"label": "Vermelha", "letra": "R"},
    "blue": {"label": "Azul", "letra": "B"},
    "yellow": {"label": "Amarela", "letra": "Y"},
    "green": {"label": "Verde", "letra": "G"},
    "white": {"label": "Branca", "letra": "W"},
    "black": {"label": "Preta", "letra": "K"},
}

# Cores de lâmina que a loja oferece hoje (SIDE_COLORS em lib/constants.ts).
CORES_LAMINA_NA_LOJA = {"yellow", "blue", "green", "red"}

# ---------------------------------------------------------------------------

PASTA_SAIDA = Path(__file__).parent / "saida"


def montar_produto() -> Dict:
    """Monta o produto no formato "Product" da loja (lib/types.ts)."""
    if TIPO_BLOCO not in BLOCK_TYPES:
        raise SystemExit(f"TIPO_BLOCO inválido: {TIPO_BLOCO}. Use: {', '.join(BLOCK_TYPES)}")
    if COR_BASE not in CORES_BASE:
        raise SystemExit(f"COR_BASE inválida: {COR_BASE}. Use: {', '.join(CORES_BASE)}")
    if COR_LAMINAS not in CORES_LAMINA:
        raise SystemExit(f"COR_LAMINAS inválida: {COR_LAMINAS}. Use: {', '.join(CORES_LAMINA)}")

    caixas = [
        {
            "boxColor": COR_BASE,
            "side1Color": COR_LAMINAS,
            "side2Color": COR_LAMINAS,
            "side3Color": COR_LAMINAS,
        }
        for _ in range(BLOCK_TYPES[TIPO_BLOCO]["caixas"])
    ]
    return {"blockType": TIPO_BLOCO, "boxes": caixas, "quantity": 1}


def laminas(caixa: Dict) -> List[str]:
    return [caixa["side1Color"], caixa["side2Color"], caixa["side3Color"]]


def gerar_codigo(produto: Dict) -> str:
    """
    Regra do código:
      - só o tipo de bloco:                       SMART40-SIMPLE
      - base e lâminas todas da mesma cor:        SMART40-SIMPLE-BLACK
      - cores diferentes: uma parte por caixa, com a cor da base
        e a letra de cada lâmina (frente, direita, topo):
                                                  SMART40-DOUBLE-BLACK-RBY-RED-GGW
    """
    base = f"{PREFIXO_CODIGO}-{produto['blockType'].upper()}"
    if not INCLUIR_CONFIGURACAO_NO_CODIGO:
        return base

    cores = {c["boxColor"] for c in produto["boxes"]}
    for caixa in produto["boxes"]:
        cores.update(laminas(caixa))
    if len(cores) == 1:
        return f"{base}-{cores.pop().upper()}"

    partes = []
    for caixa in produto["boxes"]:
        letras = "".join(CORES_LAMINA[c]["letra"] for c in laminas(caixa))
        partes.append(f"{caixa['boxColor'].upper()}-{letras}")
    return base + "-" + "-".join(partes)


def gerar_descricao(produto: Dict) -> str:
    tipo = BLOCK_TYPES[produto["blockType"]]["label"]
    descricoes = []
    for i, caixa in enumerate(produto["boxes"], start=1):
        base = CORES_BASE[caixa["boxColor"]]
        lams = [CORES_LAMINA[c]["label"] for c in laminas(caixa)]
        if len(set(lams)) == 1:
            descricoes.append(f"Caixa {i}: base {base.lower()}, 3 laminas {lams[0].lower()}s")
        else:
            descricoes.append(f"Caixa {i}: base {base.lower()}, laminas {'/'.join(lams).lower()}")
    return f"{tipo} - " + " | ".join(descricoes)


def montar_ficha(produto: Dict) -> Dict:
    tipo = BLOCK_TYPES[produto["blockType"]]
    return {
        "codigo": gerar_codigo(produto),
        "descricao": gerar_descricao(produto),
        "tipo_bloco": tipo["label"],
        "quantidade_caixas": tipo["caixas"],
        "quantidade_laminas": tipo["caixas"] * LAMINAS_POR_CAIXA,
        "cor_base": CORES_BASE[COR_BASE],
        "cor_laminas": CORES_LAMINA[COR_LAMINAS]["label"],
        "preco_loja": tipo["preco"],
        "unidade_medida": UNIDADE_MEDIDA,
        "loja": LOJA["url"],
        "observacao": "Produto de teste da integracao Smart 4.0 x Senior ERP X",
    }


def avisos(produto: Dict) -> List[str]:
    resultado = []
    for caixa in produto["boxes"]:
        for cor in laminas(caixa):
            if cor not in CORES_LAMINA_NA_LOJA:
                resultado.append(
                    f"A loja ainda não oferece lâmina {CORES_LAMINA[cor]['label'].lower()} "
                    f"(SIDE_COLORS em lib/constants.ts só tem amarela, azul, verde e vermelha)."
                )
                break
        else:
            continue
        break
    if INCLUIR_CONFIGURACAO_NO_CODIGO:
        resultado.append(
            f"A loja envia hoje o código {PREFIXO_CODIGO}-{produto['blockType'].upper()} "
            f"(lib/senior-api.ts), sem a configuração. Para um pedido usar este item, "
            f"a loja vai precisar enviar o código gerado aqui."
        )
    return resultado


def gravar_arquivos(produto: Dict, ficha: Dict) -> List[Path]:
    PASTA_SAIDA.mkdir(exist_ok=True)
    codigo = ficha["codigo"]

    caminho_loja = PASTA_SAIDA / "produto_loja.json"
    produto_loja = {"id": codigo, **produto}
    caminho_loja.write_text(json.dumps(produto_loja, ensure_ascii=False, indent=2), encoding="utf-8")

    caminho_json = PASTA_SAIDA / f"produto_{codigo}.json"
    ficha_completa = {**ficha, "configuracao": produto["boxes"]}
    caminho_json.write_text(json.dumps(ficha_completa, ensure_ascii=False, indent=2), encoding="utf-8")

    caminho_csv = PASTA_SAIDA / f"produto_{codigo}.csv"
    with caminho_csv.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(ficha.keys()))
        writer.writeheader()
        writer.writerow(ficha)

    caminho_msg = PASTA_SAIDA / "mensagem_senior.txt"
    caminho_msg.write_text(
        "Olá,\n\n"
        "Segue o primeiro produto de teste da integração Smart 4.0 x Senior ERP X.\n"
        "Pedimos, por favor, o cadastro do item no ERP (empresa 1, filial 2 - SENAI Blumenau)\n"
        "com exatamente este código, pois ele será enviado em items[].product.code\n"
        f"nos pedidos de venda feitos pela loja ({LOJA['url']}):\n\n"
        f"  Código:              {ficha['codigo']}\n"
        f"  Descrição:           {ficha['descricao']}\n"
        f"  Tipo de bloco:       {ficha['tipo_bloco']} ({ficha['quantidade_caixas']} caixa)\n"
        f"  Cor da base:         {ficha['cor_base']}\n"
        f"  Lâminas:             {ficha['quantidade_laminas']}, todas {ficha['cor_laminas'].lower()}s\n"
        f"  Unidade de medida:   {ficha['unidade_medida']}\n"
        f"  Preço na loja:       R$ {ficha['preco_loja']:.2f}\n\n"
        "Os dados também estão nos arquivos JSON e CSV em anexo.\n"
        "Se o ERP exigir outros campos (NCM, família, origem, etc.), nos avisem.\n\n"
        "Obrigado!\n",
        encoding="utf-8",
    )

    return [caminho_json, caminho_csv, caminho_loja, caminho_msg]


def main() -> None:
    produto = montar_produto()
    ficha = montar_ficha(produto)
    arquivos = gravar_arquivos(produto, ficha)

    print(f"Loja:               {LOJA['nome']} ({LOJA['url']})")
    print(f"Produto cadastrado: {ficha['descricao']}")
    print(f"Código do produto:  {ficha['codigo']}")
    print("Arquivos gerados:")
    for caminho in arquivos:
        print(f"  {caminho}")
    for aviso in avisos(produto):
        print(f"Atenção: {aviso}")


if __name__ == "__main__":
    main()
