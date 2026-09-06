---
name: padrao-do-plano-de-negocios-pdf-cimol
description: Gere PDFs de plano de negócios no padrão visual CIMOL, com capa, resumo executivo, análise de mercado, modelo de negócio, projeção financeira e anexos de QR codes em até cinco páginas.
---

# Skill: Padrão-do-plano-de-negocios-pdf-CIMOL

Use esta skill quando o usuário pedir um **plano de negócios em PDF**, especialmente no padrão visual CIMOL: documento curto, bonito, objetivo, com linguagem escolar/profissional e limite máximo de 5 páginas. Adapte a identidade visual ao projeto da pessoa; CIMOL é o padrão de partida, não uma paleta obrigatória.

## Resultado esperado

Produzir um PDF em A4 com **até 5 páginas**. O gerador entrega cinco páginas para preservar o padrão completo:

1. **Capa executiva**
   - Faixa superior azul-marinho escura.
   - Título grande em branco.
   - Subtítulo objetivo.
   - Quatro cards de resumo: Problema, Solução, Público-alvo e Estágio atual.
   - Frase de proposta de valor no final.

2. **Oportunidade, problema e solução**
   - Duas colunas.
   - Coluna esquerda: dor do cliente e solução proposta.
   - Coluna direita: evidências de mercado e público-alvo.
   - Tabela de diferenciais competitivos.

3. **Modelo de negócio, produto e operação**
   - Tabela de fontes de receita.
   - Tabela de pacotes/preços.
   - Lista do que já foi consolidado.
   - Roadmap em três fases.

4. **Estratégia comercial e projeção financeira**
   - Aquisição de clientes, indicadores-chave, riscos e mitigação.
   - Tabela financeira de 12 meses.
   - Investimento inicial sugerido.
   - Conclusão executiva.

5. **Anexos**
   - Dois QR codes lado a lado, quando fornecidos.
   - Sem QR codes, manter o anexo com os espaços identificados como não informados.
   - Texto curto de explicação e linha de fontes de atualização.

## Regras de escrita

- Escrever em português brasileiro.
- Ser direto, profissional e fácil de apresentar.
- Evitar texto demais: o objetivo é caber em 5 páginas sem parecer poluído.
- Quando o usuário enviar muito conteúdo, resumir e priorizar o que tem valor de plano de negócios.
- Não inventar validações externas. Se algo for estimativa, escrever como estimativa.
- Usar valores financeiros plausíveis e marcados como estimados quando não houver dados reais.
- Manter o documento pronto para escola, banca, professor ou apresentação institucional.

## Briefing obrigatório

Antes de gerar o PDF, peça estas informações básicas em uma única mensagem curta:

- Nome do projeto, segmento e público-alvo.
- Problema, solução e estágio atual.
- Cores da marca (códigos hex, se houver) e estilo desejado para a capa: `minimal`, `geometric` ou `bold`.
- Nome/ano ou frase curta para a capa, se desejado.

Pergunte também por diferenciais, modelo de receita, projeção e QR codes quando eles não estiverem no contexto. Não invente identidade visual: se a pessoa não tiver cores, ofereça o tema CIMOL como padrão e peça confirmação antes de usá-lo.

## Fluxo de trabalho

1. Com o briefing respondido, reunir os dados do negócio e a identidade visual.

2. Criar ou preencher um arquivo JSON no formato de `examples/cimol.sample.json`.

3. Rodar o gerador:

```bash
python scripts/business_plan_pdf.py \
  --input examples/cimol.sample.json \
  --output plano_negocios.pdf \
  --qr1 caminho/qr_1.png \
  --qr2 caminho/qr_2.png
```

4. Confirmar que o PDF final possui no máximo 5 páginas.

## Padrão visual

- Página A4, com margens e respiro visual.
- A paleta vem de `branding` no JSON: `primary_color`, `secondary_color`, `accent_color`, `text_color`, `muted_color`, `border_color` e `highlight_color` aceitam hexadecimal.
- A capa usa `branding.cover_style`: `minimal`, `geometric` (padrão) ou `bold`; `cover_label` adiciona uma identificação curta no topo.
- Sem `branding`, usar a paleta CIMOL: principal `#0F172A`, secundária `#0B2447`, destaque `#E0EAFF` e bordas `#CBD5E1`.
- Centralizar tabelas dentro da área útil, mantendo folga lateral; nunca encostá-las visualmente nas bordas da página.
- Rodapé com data/descrição à esquerda e número da página à direita.
- Cabeçalho nas páginas internas com o nome do plano.

## Quando faltar informação

Se faltar conteúdo do plano, marque projeções como estimativas. Se faltar o briefing visual, faça as perguntas do briefing obrigatório antes de gerar. QR codes são opcionais.
