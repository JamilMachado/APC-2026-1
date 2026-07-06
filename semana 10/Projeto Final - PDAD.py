import tkinter as tk
from tkinter import messagebox
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import sys


def carregar_dados():
    moradores = pd.read_csv("moradores.csv", sep=";", decimal=",", encoding="utf-8-sig")
    domicilio = pd.read_excel("domicilios.xlsx")
    return moradores, domicilio


RA_NOMES = {
    5301: "Brasília", 5302: "Gama", 5303: "Taguatinga", 5304: "Brazlândia",
    5305: "Sobradinho", 5306: "Planaltina", 5307: "Paranoá", 5308: "Núcleo Bandeirante",
    5309: "Ceilândia", 5310: "Guará", 5311: "Cruzeiro", 5312: "Samambaia",
    5313: "Santa Maria", 5314: "São Sebastião", 5315: "Recanto Das Emas", 5316: "Lago Sul",
    5317: "Riacho Fundo", 5318: "Lago Norte", 5319: "Candangolândia", 5320: "Águas Claras",
    5321: "Riacho Fundo II", 5322: "Sudoeste e Octogonal", 5323: "Varjão", 5324: "Park Way",
    5325: "SCIA", 5326: "Sobradinho II", 5327: "Jardim Botânico", 5328: "Itapoã",
    5329: "SIA", 5330: "Vicente Pires", 5331: "Fercal", 5332: "Sol Nascente / Pôr do Sol",
    5333: "Arniqueira", 5334: "Arapoanga", 5335: "Água Quente", 5336: "Área Rural",
    5241: "Águas Lindas de Goiás", 5242: "Alexânia", 5243: "Cidade Ocidental", 5244: "Cristalina",
    5245: "Cocalzinho de Goiás", 5246: "Formosa", 5247: "Luziânia", 5248: "Novo Gama",
    5249: "Padre Bernardo", 5250: "Planaltina de Goiás", 5251: "Santo Antônio do Descoberto", 5252: "Valparaíso de Goiás"
}

OCUPACAO = {
    1: "Empregado no setor público",
    2: "Militar do exército, da marinha, da aeronáutica, da polícia militar ou do corpo de bombeiros militar",
    3: "Empregado no setor privado (Exceto Empregado Doméstico)",
    4: "Empregado Doméstico",
    5: "Estágio Remunerado",
    6: "Aprendiz",
    7: "Conta Própria ou Autônomo",
    8: "Empregador",
    9: "Presta Serviço Militar Obrigatório",
    10: "Trabalhador não remunerado em ajuda a membro do domicílio ou parente",
}

ESCOLARIDADE = {
    1: "Sem instrução", 2: "Fund. incompleto", 3: "Fund. completo",
    4: "Médio incompleto", 5: "Médio completo", 6: "Superior incompleto",
    7: "Superior completo", 8: "Pós-graduação"
}


def bubble_sort_por_idade(lista):
    n = len(lista)
    for i in range(n):
        for j in range(n - i - 1):
            if lista[j]["idade"] > lista[j + 1]["idade"]:
                lista[j], lista[j + 1] = lista[j + 1], lista[j]
    return lista


def gerar_relatorio(ra_codigo):
    moradores = pd.read_csv("moradores.csv", sep=";", decimal=",", encoding="utf-8-sig", low_memory=False)
    filtro = moradores[moradores["localidade"] == ra_codigo]

    if filtro.empty:
        print(f"Nenhum dado encontrado para a RA {ra_codigo}.")
        sys.exit(1)

    ra_nome = RA_NOMES.get(ra_codigo, f"RA-{ra_codigo}")
    validos = filtro[filtro["idade_calculada"] != 99999]
    idades = validos["idade_calculada"].tolist()

    lista_moradores = []
    for _, linha in validos.iterrows():
        ocupacao_valor = pd.to_numeric(linha["I13"], errors="coerce")
        if pd.isna(ocupacao_valor) or not 1 <= int(ocupacao_valor) <= 10:
            continue
        ocupacao = OCUPACAO.get(int(ocupacao_valor), "?")
        lista_moradores.append({
            "id": linha["morador_id"],
            "idade": linha["idade_calculada"],
            "ocupacao": ocupacao,
            "escolaridade": ESCOLARIDADE.get(linha["escolaridade"], "?"),
            "renda": linha["renda_ind"] if linha["renda_ind"] != 99999 else None,
        })
    lista_moradores = bubble_sort_por_idade(lista_moradores)

    linhas = []
    linhas.append("=" * 55)
    linhas.append(f"  PDAD 2024 — Análise da RA: {ra_nome} (cód. {ra_codigo})")
    linhas.append("=" * 55)
    linhas.append(f"  Total de moradores na amostra : {len(filtro)}")
    linhas.append(f"  Com idade declarada           : {len(validos)}")
    if idades:
        linhas.append(f"  Média de idade                : {sum(idades)/len(idades):.1f} anos")
        linhas.append(f"  Faixa etária                  : {min(idades)} a {max(idades)} anos")
    linhas.append("")
    linhas.append("  Moradores (ordenados por idade):")
    linhas.append("  " + "-" * 50)
    for m in lista_moradores:
        renda_str = f"R$ {m['renda']:,.0f}" if m["renda"] else "não declarada"
        linhas.append(f"  {m['id']:12s} | {m['idade']:3d} anos | {m['escolaridade']:25s} | {renda_str}")
    linhas.append("")
    return linhas, ra_nome


def gerar_relatorio_global():
    moradores = pd.read_csv("moradores.csv", sep=";", decimal=",", encoding="utf-8-sig", low_memory=False)
    dados = moradores[["localidade", "I13"]].copy()
    dados.columns = ["localidade", "ocupacao"]
    dados = dados.dropna(subset=["ocupacao"])
    dados["ocupacao"] = pd.to_numeric(dados["ocupacao"], errors="coerce")
    dados = dados[dados["ocupacao"].between(1, 10)]
    dados["ra_nome"] = dados["localidade"].map(RA_NOMES).fillna("RA desconhecida")
    dados["ocupacao_desc"] = dados["ocupacao"].map(OCUPACAO).fillna("Sem classificação")

    resumo = (
        dados.groupby(["ra_nome", "ocupacao_desc"], dropna=False)
        .size()
        .reset_index(name="quantidade")
    )

    if resumo.empty:
        messagebox.showinfo("Sem dados", "Nenhum dado disponível para gerar o relatório global.")
        return

    janela_grafico = tk.Toplevel(janela)
    janela_grafico.title("Relatório Global de Ocupação")
    janela_grafico.geometry("1200x700")

    sns.set_theme(style="whitegrid")
    fig = Figure(figsize=(11.5, 6.5), dpi=100)
    ax = fig.add_subplot(111)
    pivot = resumo.pivot(index="ra_nome", columns="ocupacao_desc", values="quantidade").fillna(0)
    pivot.plot(kind="bar", stacked=True, ax=ax, width=0.8, colormap="Set2")
    ax.set_title("Ocupação por RA — Relatório Global")
    ax.set_ylabel("Quantidade de moradores")
    ax.set_xlabel("Nome da RA")
    ax.set_xticks(range(len(pivot.index)))
    ax.set_xticklabels(pivot.index, rotation=60, ha="right")
    ax.legend(title="Ocupação", bbox_to_anchor=(1.01, 1), loc="upper left")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=janela_grafico)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def carregar_resumo_dados():
    moradores = pd.read_csv("moradores.csv", sep=";", decimal=",", encoding="utf-8-sig", low_memory=False)
    dados = moradores[["localidade", "I13"]].copy()
    dados.columns = ["localidade", "ocupacao"]
    dados = dados.dropna(subset=["ocupacao"])
    dados["ocupacao"] = pd.to_numeric(dados["ocupacao"], errors="coerce")
    validas = dados[dados["ocupacao"].between(1, 10)]
    invalidas = len(dados) - len(validas)

    return {
        "total_registros": len(moradores),
        "total_ras": len(RA_NOMES),
        "ocupacoes_validas": len(validas),
        "ocupacoes_invalidas": invalidas,
    }


def gerar_grafico_ocupacao_por_ra(ra_codigo=None):
    moradores = pd.read_csv("moradores.csv", sep=";", decimal=",", encoding="utf-8-sig", low_memory=False)
    dados = moradores[["localidade", "I13"]].copy()
    dados.columns = ["localidade", "ocupacao"]
    dados = dados.dropna(subset=["ocupacao"])
    dados["ocupacao"] = pd.to_numeric(dados["ocupacao"], errors="coerce")
    dados = dados[dados["ocupacao"].between(1, 10)]
    dados["ra_nome"] = dados["localidade"].map(RA_NOMES).fillna("RA desconhecida")
    dados["ocupacao_desc"] = dados["ocupacao"].map(OCUPACAO).fillna("Sem classificação")

    if ra_codigo is not None:
        dados = dados[dados["localidade"] == ra_codigo]

    if dados.empty:
        messagebox.showinfo("Sem dados", "Nenhum dado disponível para gerar o gráfico.")
        return

    resumo = (
        dados.groupby(["ra_nome", "ocupacao_desc"], dropna=False)
        .size()
        .reset_index(name="quantidade")
    )

    janela_grafico = tk.Toplevel(janela)
    janela_grafico.title("Análise de ocupação por RA")
    janela_grafico.geometry("1100x650")

    sns.set_theme(style="whitegrid")
    fig = Figure(figsize=(10.5, 6.2), dpi=100)
    ax = fig.add_subplot(111)

    if ra_codigo is not None:
        ra_nome = RA_NOMES.get(ra_codigo, f"RA-{ra_codigo}")
        resumo = resumo.sort_values("quantidade", ascending=False)
        sns.barplot(data=resumo, x="ocupacao_desc", y="quantidade", hue="ocupacao_desc", ax=ax, palette="Set2", legend=False)
        ax.set_title(f"Ocupações para {ra_nome}")
        ax.set_ylabel("Quantidade de moradores")
        ax.set_xlabel("Descrição da ocupação")
        for label in ax.get_xticklabels():
            label.set_rotation(45)
            label.set_ha("right")
    else:
        pivot = resumo.pivot(index="ra_nome", columns="ocupacao_desc", values="quantidade").fillna(0)
        pivot.plot(kind="bar", stacked=True, ax=ax, width=0.8, colormap="Set2")
        ax.set_title("Ocupação por nome de RA")
        ax.set_ylabel("Quantidade de moradores")
        ax.set_xlabel("Nome da RA")
        for label in ax.get_xticklabels():
            label.set_rotation(45)
            label.set_ha("right")
        ax.legend(title="Ocupação", bbox_to_anchor=(1.01, 1), loc="upper left")

    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=janela_grafico)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


janela = tk.Tk()
janela.title("Análise PDAD")
janela.geometry("800x650")

label_instrucao = tk.Label(
    janela,
    text="Selecione uma RA para abrir a análise de ocupação ou gere o relatório global.",
    font=("Arial", 11),
)
label_instrucao.pack(pady=10)

resumo = carregar_resumo_dados()
texto_resumo = (
    f"Dados coletados:\n"
    f"- Total de registros: {resumo['total_registros']}\n"
    f"- Total de RAs disponíveis: {resumo['total_ras']}\n"
    f"- Registros com ocupação válida: {resumo['ocupacoes_validas']}\n"
    f"- Registros filtrados (inválidos): {resumo['ocupacoes_invalidas']}\n"
    f"\nDados filtrados para análise:\n"
    f"- Foram consideradas apenas os 10 tipos de ocupações.\n"
    f"- Valores como 99999 e 88888 foram ignorados."
)

caixa_resumo = tk.Text(janela, height=8, width=80, font=("Arial", 10))
caixa_resumo.insert("1.0", texto_resumo)
caixa_resumo.config(state="disabled")
caixa_resumo.pack(padx=10, pady=(0, 10))

botao_global = tk.Button(
    janela,
    text="Gerar relatório global",
    command=gerar_relatorio_global,
    width=24,
    height=2,
)
botao_global.pack(pady=(0, 10))

canvas = tk.Canvas(janela)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)

scrollbar = tk.Scrollbar(janela, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

canvas.configure(yscrollcommand=scrollbar.set)

frame_botoes = tk.Frame(canvas)
canvas.create_window((0, 0), window=frame_botoes, anchor="nw")

frame_botoes.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))

for index, (ra_codigo, ra_nome) in enumerate(sorted(RA_NOMES.items())):
    botao_ra = tk.Button(
        frame_botoes,
        text=f"{ra_codigo} - {ra_nome}",
        command=lambda codigo=ra_codigo: gerar_grafico_ocupacao_por_ra(codigo),
        width=24,
        anchor="w",
    )
    botao_ra.grid(row=index // 4, column=index % 4, padx=6, pady=3, sticky="ew")

for coluna in range(4):
    frame_botoes.columnconfigure(coluna, weight=1)

janela.mainloop()