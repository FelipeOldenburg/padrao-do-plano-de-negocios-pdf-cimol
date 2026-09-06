# Padrão-do-plano-de-negocios-pdf-CIMOL

Gera um PDF A4 de plano de negócios no padrão visual CIMOL: capa, resumo executivo, análise de mercado, modelo de negócio, projeção financeira e anexo de QR codes. O layout completo usa cinco páginas e nunca excede esse limite.

O identificador técnico da skill é `padrao-do-plano-de-negocios-pdf-cimol`. Ele e o slug do GitHub usam ASCII para atender às regras de instalação; o nome exibido permanece **Padrão-do-plano-de-negocios-pdf-CIMOL**.

## O que a skill entrega

- Capa executiva e quatro cards de resumo.
- Análise de oportunidade, problema, solução e diferenciais.
- Modelo de negócio, preços, operação e roadmap.
- Estratégia comercial e projeção financeira estimada de 12 meses.
- Anexo com dois QR codes, ou placeholders claros quando eles não forem fornecidos.
- Identidade visual adaptável: cores, estilo de capa e identificação do projeto.

## Pré-requisitos

- Python 3.10 ou superior para gerar o PDF.
- Node.js e npm somente para instalar via `npx`.
- Git somente para clonar o repositório manualmente.
- QR codes em arquivos de imagem, como PNG ou JPG, quando forem usados.

## Instalação pelo terminal

Após publicar o repositório, instale a skill com:

```bash
npx skills@latest add https://github.com/FelipeOldenburg/padrao-do-plano-de-negocios-pdf-cimol
```

Para usar o gerador diretamente, clone o repositório e execute o instalador adequado:

```bash
git clone https://github.com/FelipeOldenburg/padrao-do-plano-de-negocios-pdf-cimol.git
cd padrao-do-plano-de-negocios-pdf-cimol
./install.sh
```

```powershell
git clone https://github.com/FelipeOldenburg/padrao-do-plano-de-negocios-pdf-cimol.git
Set-Location padrao-do-plano-de-negocios-pdf-cimol
.\install.ps1
```

Os instaladores exigem Python 3.10 ou superior e criam `.venv` com as dependências do projeto.

## Uso no Codex e ChatGPT

Depois de instalar, mencione `$padrao-do-plano-de-negocios-pdf-cimol` no Codex ou selecione a skill com `@` no aplicativo desktop do ChatGPT. Forneça os dados do negócio ou adapte `examples/cimol.sample.json`.

Skills independentes funcionam no Codex e no aplicativo desktop do ChatGPT. Para disponibilizá-la no ChatGPT pela web, ela precisa ser empacotada como um plug-in.

Exemplo de pedido:

```text
$padrao-do-plano-de-negocios-pdf-cimol
Crie um plano de negócios para uma plataforma de gestão escolar. Use os dados a seguir,
marque valores não comprovados como estimativas e gere o PDF com QR codes em anexo.
```

Antes de gerar, a skill pede um briefing curto: nome do projeto, segmento/público, problema e solução, cores da marca e estilo de capa (`minimal`, `geometric` ou `bold`). Ela só usa o visual CIMOL como padrão quando a pessoa confirmar que não possui identidade visual própria.

## Personalização visual

Inclua `branding` no JSON para adaptar o material ao projeto. Todos os campos de cor usam hexadecimal; os campos ausentes mantêm o padrão CIMOL.

```json
"branding": {
  "primary_color": "#173B5C",
  "secondary_color": "#0E7490",
  "accent_color": "#E0F2FE",
  "cover_style": "geometric",
  "cover_label": "NOME DA MARCA | PLANO 2026"
}
```

- `cover_style`: `minimal`, `geometric` (padrão) ou `bold`.
- `text_color`, `muted_color`, `border_color` e `highlight_color` refinam texto, bordas e destaques quando necessário.
- Tabelas são centralizadas dentro da área útil, preservando espaço lateral e evitando o efeito de conteúdo encostado na página.

## Formato do JSON

Copie `examples/cimol.sample.json` e edite-o; ele é a referência completa do formato. As chaves principais são:

| Campo | Conteúdo |
| --- | --- |
| `title`, `project_name`, `subtitle` | Identificação do plano e do projeto |
| `branding` | Cores, estilo e rótulo da capa do projeto |
| `summary_cards` | Problema, solução, público-alvo e estágio |
| `page2` | Oportunidade, mercado e diferenciais |
| `page3` | Modelo de negócio, preços, consolidados e roadmap |
| `page4` | Estratégia comercial, projeção e investimento |
| `page5` | Textos do anexo e rótulos dos QR codes |

Escreva de forma objetiva. O gerador limita listas e tabelas para preservar o layout, mas conteúdos excessivamente longos devem ser resumidos antes da geração.

## Gerar o PDF

Sem QR codes, a página de anexos mostra espaços identificados como “QR não informado”:

```powershell
.\.venv\Scripts\python.exe scripts\business_plan_pdf.py --input examples\cimol.sample.json --output plano_sem_qr.pdf
```

```bash
.venv/bin/python scripts/business_plan_pdf.py --input examples/cimol.sample.json --output plano_sem_qr.pdf
```

Com dois QR codes:

```powershell
.\.venv\Scripts\python.exe scripts\business_plan_pdf.py --input examples\cimol.sample.json --output plano_com_qr.pdf --qr1 .\qr_github.png --qr2 .\qr_aplicacao.png
```

```bash
.venv/bin/python scripts/business_plan_pdf.py --input examples/cimol.sample.json --output plano_com_qr.pdf --qr1 ./qr_github.png --qr2 ./qr_aplicacao.png
```

O próprio gerador falha se o resultado não tiver cinco páginas.

## QR codes

- `--qr1` e `--qr2` recebem os arquivos que aparecem lado a lado na página 5.
- Esses argumentos têm prioridade sobre caminhos opcionais informados em `page5.qr_cards`.
- Sem QR codes, a página de anexos continua presente com o aviso “QR não informado”.
- Se um caminho de QR for informado e não existir, o comando falha em vez de gerar um PDF incompleto.

## Verificação

Em caso de sucesso, o gerador imprime `PDF criado: ...` e valida o resultado com `pypdf`. O template atual sempre gera exatamente cinco páginas, atendendo ao limite máximo definido pela skill.

## Solução de problemas

- **Python não encontrado ou versão baixa:** instale Python 3.10+ e execute novamente `install.sh` ou `install.ps1`.
- **`ModuleNotFoundError`:** rode o instalador e use o Python dentro de `.venv` nos comandos de geração.
- **PowerShell bloqueia o script:** execute `powershell -ExecutionPolicy Bypass -File .\install.ps1` apenas para essa sessão.
- **QR code não encontrado:** confirme o caminho passado em `--qr1` e `--qr2`.
- **A skill não aparece no Codex:** reinicie o aplicativo após a instalação.

## Privacidade

O gerador processa localmente o JSON e as imagens informadas. Ele não envia o conteúdo do plano para serviços externos.

## Estrutura

```text
Padrão-do-plano-de-negocios-pdf-CIMOL/
├── SKILL.md
├── README.md
├── requirements.txt
├── install.sh
├── install.ps1
├── scripts/business_plan_pdf.py
├── examples/cimol.sample.json
└── docs/instalacao_terminal.md
```

As projeções do exemplo são estimativas. Substitua-as por dados reais antes de usar o plano em uma apresentação oficial.
