# Prompt para usar no Codex

Use a skill `padrao-do-plano-de-negocios-pdf-cimol` deste repositório para criar um PDF de plano de negócios no mesmo padrão visual do modelo CIMOL.

Tarefa:
1. Leia o `SKILL.md`.
2. Use `examples/cimol.sample.json` como formato base.
3. Antes de montar o JSON, peça nome, segmento/público, problema/solução, cores da marca e estilo de capa (`minimal`, `geometric` ou `bold`).
4. Atualize o conteúdo e `branding` conforme o projeto atual; só use o tema CIMOL se a pessoa confirmar que não tem identidade visual própria.
5. Gere o PDF com `scripts/business_plan_pdf.py`.
6. O PDF final deve ter exatamente 5 páginas, com tabelas centralizadas e afastadas das bordas.
7. Se houver QR codes, coloque-os na página 5, em anexos, lado a lado.
8. Entregue o PDF final e avise se alguma projeção financeira foi estimada.

Comando sugerido:

```bash
pip install -r requirements.txt
python scripts/business_plan_pdf.py --input examples/cimol.sample.json --output plano_negocios.pdf --qr1 ./qr_1.png --qr2 ./qr_2.png
```
