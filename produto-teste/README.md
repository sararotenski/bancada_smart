# Produto de teste — Smart 4.0 x Senior ERP X

Primeiro produto de teste da integração: **Bloco Simples** (1 caixa), base preta e as 3 lâminas pretas.

Código do produto: **`SMART40-SIMPLE-BLACK`**

## Como gerar

```bash
python3 produto-teste/produto_teste.py
```

Os dados do produto e da loja ficam no bloco `CONFIGURAÇÃO EDITÁVEL`, no início do `produto_teste.py`.

## Arquivos gerados em `saida/`

- `produto_SMART40-SIMPLE-BLACK.json` e `.csv`: ficha do produto para a Senior cadastrar o item no ERP.
- `produto_loja.json`: o produto no formato `Product` da loja (`lib/types.ts`).
- `mensagem_senior.txt`: texto para enviar à Senior junto com a ficha.

## Pendências na loja

- A loja ainda não oferece lâmina preta (`SIDE_COLORS` em `lib/constants.ts`).
- A loja envia hoje o código `SMART40-SIMPLE` (`lib/senior-api.ts`), sem a configuração.
