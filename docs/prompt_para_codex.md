# Prompt para usar no Codex

Use a skill `padrao-do-plano-de-negocios-pdf-cimol` deste repositório para criar um PDF de plano de negócios no mesmo padrão visual do modelo CIMOL.

Tarefa:
1. Leia o `SKILL.md`.
2. Use `examples/cimol.sample.json` como formato base.
3. Atualize o conteúdo conforme o projeto atual.
4. Gere o PDF com `scripts/business_plan_pdf.py`.
5. O PDF final deve ter exatamente 5 páginas.
6. Se houver QR codes, coloque-os na página 5, em anexos, lado a lado.
7. Entregue o PDF final e avise se alguma projeção financeira foi estimada.

Comando sugerido:

```bash
pip install -r requirements.txt
python scripts/business_plan_pdf.py --input examples/cimol.sample.json --output plano_negocios.pdf --qr1 ./qr_1.png --qr2 ./qr_2.png
```
