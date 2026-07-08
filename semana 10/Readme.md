# Projeto Final PDAD

## Proposta - Recorte E — Trabalho e ocupação
Pergunta central: como se distribui a população ocupada no DF? Quais setores de atividade predominam?

Variáveis principais: bloco I (trabalho e renda) dos moradores, localidade, escolaridade, id_genero, idade_calculada

O sistema deve permitir filtrar por setor de atividade, visualizar a distribuição de ocupação por RA e gênero, e identificar a relação entre escolaridade e renda.

## Descrição do sistema
Este sistema analisa dados do censo de moradores por RA e gera gráficos de ocupação e relatórios. A interface é feita com Tkinter e apresenta comparações entre duas RAs selecionadas. O foco é visualizar ocupação por código e gerar relatórios em texto para cada RA. O sistema também mostra um relatório global de ocupação por RA.

## Como executar
1. Abra um terminal na pasta do projeto.
2. Ative seu ambiente virtual, se usar um.
3. Execute:

```bash
python "sistema.py"
```


## Dependências
Instale as dependências com pip:

```bash
pip install pandas matplotlib seaborn openpyxl
```

## Arquivos de dados necessários
- `moradores.csv`
- `domicilios.xlsx`
Encontrados no site https://pdad.ipe.df.gov.br

## Integrante
- Jamil Araujo Machado

## Componente Curricular
APC 2026/1 — Licenciatura em Computação — UnB/CIC Prof. Jorge Henrique Cabral Fernandes | jhcf@unb.br
