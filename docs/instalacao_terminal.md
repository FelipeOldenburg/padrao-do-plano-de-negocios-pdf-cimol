# Instalação pelo terminal

É necessário ter Python 3.10 ou superior.

## Linux, macOS ou Git Bash

```bash
./install.sh
.venv/bin/python scripts/business_plan_pdf.py --input examples/cimol.sample.json --output plano_negocios.pdf
```

## Windows PowerShell

```powershell
.\install.ps1
.\.venv\Scripts\python.exe scripts\business_plan_pdf.py --input examples\cimol.sample.json --output plano_negocios.pdf
```

## Instalação da skill

Depois que o repositório estiver publicado, use:

```bash
npx skills@latest add https://github.com/FelipeOldenburg/padrao-do-plano-de-negocios-pdf-cimol
```

Para gerar com QR codes, acrescente `--qr1 caminho/qr1.png --qr2 caminho/qr2.png` ao comando do gerador.
