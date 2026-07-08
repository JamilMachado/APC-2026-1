import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.colors import to_hex
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Patch
import seaborn as sns
import sys


def carregar_dados():
    moradores = pd.read_csv("moradores.csv", sep=";", decimal=",", encoding="utf-8-sig")
    domicilio = pd.read_excel("domicilios.xlsx")
    return moradores, domicilio


RA_NOMES = {
    5301: "Plano Piloto", 5302: "Gama", 5303: "Taguatinga", 5304: "Brazlândia",
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


def gerar_relatorio_txt(ra_codigo):
    barra_progresso["value"] = 0
    texto_progresso.set("Iniciando geração do relatório...")
    janela.update_idletasks()

    moradores = pd.read_csv("moradores.csv", sep=";", decimal=",", encoding="utf-8-sig", low_memory=False)
    barra_progresso["value"] = 20
    texto_progresso.set("Carregando dados da RA...")
    janela.update_idletasks()

    filtro = moradores[moradores["localidade"] == ra_codigo].copy()

    if filtro.empty:
        barra_progresso["value"] = 0
        texto_progresso.set("Nenhum dado encontrado")
        janela.update_idletasks()
        messagebox.showinfo("Sem dados", f"Nenhum dado encontrado para a RA {ra_codigo}.")
        return

    domicilios = pd.read_excel("domicilios.xlsx")
    total_domicilios = int((domicilios["localidade"] == ra_codigo).sum())
    total_moradores = int(len(filtro))

    barra_progresso["value"] = 40
    texto_progresso.set("Processando dados...")
    janela.update_idletasks()

    filtro = filtro[["morador_id", "escolaridade", "E03", "idade_calculada", "I13"]].copy()
    filtro.columns = ["morador_id", "escolaridade", "sexo", "idade_calculada", "ocupacao"]

    filtro["escolaridade"] = filtro["escolaridade"].map(ESCOLARIDADE).fillna("?")
    filtro["ocupacao"] = pd.to_numeric(filtro["ocupacao"], errors="coerce")
    filtro["ocupacao"] = filtro["ocupacao"].map(OCUPACAO).fillna("?")
    filtro["idade_calculada"] = pd.to_numeric(filtro["idade_calculada"], errors="coerce")
    filtro["idade_calculada"] = filtro["idade_calculada"].replace(99999, None)

    resumo_escolaridade = filtro["escolaridade"].value_counts().sort_index()
    resumo_ocupacao = filtro["ocupacao"].value_counts().sort_index()
    resumo_sexo = filtro["sexo"].value_counts().sort_index()
    media_idades = filtro["idade_calculada"].mean()

    barra_progresso["value"] = 80
    texto_progresso.set("Escrevendo arquivo .txt...")
    janela.update_idletasks()

    ra_nome = RA_NOMES.get(ra_codigo, f"RA-{ra_codigo}")
    nome_arquivo = f"relatorio_ra_{ra_codigo}.txt"
    with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
        arquivo.write(f"Relatório PDAD - RA {ra_codigo} - {ra_nome}\n")
        arquivo.write("=" * 60 + "\n")
        arquivo.write("Resumo:\n")
        arquivo.write(f"- Total de domicílios: {total_domicilios}\n")
        arquivo.write(f"- Total de moradores: {total_moradores}\n")
        arquivo.write(f"- Quantidade por escolaridade:\n")
        for item, quantidade in resumo_escolaridade.items():
            arquivo.write(f"  - {item}: {quantidade}\n")
        arquivo.write(f"- Quantidade por ocupação:\n")
        for item, quantidade in resumo_ocupacao.items():
            arquivo.write(f"  - {item}: {quantidade}\n")
        arquivo.write(f"- Quantidade por sexo:\n")
        for item, quantidade in resumo_sexo.items():
            arquivo.write(f"  - {item}: {quantidade}\n")
        arquivo.write(f"- Média de idade: {media_idades:.1f} anos\n")
        arquivo.write("\n")
        arquivo.write("Dados detalhados:\n")
        arquivo.write(filtro.to_string(index=False))

    barra_progresso["value"] = 100
    texto_progresso.set("Relatório concluído")
    janela.update_idletasks()
    messagebox.showinfo("Relatório gerado", f"Arquivo salvo em: {nome_arquivo}")


def limpar_frame_conteudo(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def mostrar_legenda_em_janela(titulo, itens):
    legenda_janela = tk.Toplevel(janela)
    legenda_janela.title(titulo)
    legenda_janela.geometry("320x420")
    legenda_janela.resizable(width=False, height=True)

    frame_legenda = tk.Frame(legenda_janela)
    frame_legenda.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    canvas_legenda = tk.Canvas(frame_legenda, borderwidth=0)
    scrollbar_legenda = ttk.Scrollbar(frame_legenda, orient="vertical", command=canvas_legenda.yview)
    inner_legenda = tk.Frame(canvas_legenda)
    inner_legenda.bind(
        "<Configure>",
        lambda event: canvas_legenda.configure(scrollregion=canvas_legenda.bbox("all"))
    )
    canvas_legenda.create_window((0, 0), window=inner_legenda, anchor="nw")
    canvas_legenda.configure(yscrollcommand=scrollbar_legenda.set)

    canvas_legenda.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar_legenda.pack(side=tk.RIGHT, fill=tk.Y)

    for cor, texto in itens:
        linha = tk.Frame(inner_legenda)
        linha.pack(fill=tk.X, pady=2)

        if cor:
            swatch = tk.Label(linha, width=2, bg=cor, relief="solid", bd=1)
            swatch.pack(side=tk.LEFT, padx=(0, 8))
        else:
            tk.Label(linha, width=2).pack(side=tk.LEFT, padx=(0, 8))

        tk.Label(linha, text=texto, anchor="w", justify="left", wraplength=240).pack(side=tk.LEFT, fill=tk.X, expand=True)


def mostrar_grafico_no_frame(resumo, titulo, tipo="ra"):
    limpar_frame_conteudo(frame_grafico)
    texto_progresso.set("Carregando gráfico...")
    barra_progresso["value"] = 20
    janela.update_idletasks()

    sns.set_theme(style="whitegrid")
    fig = Figure(figsize=(10.8, 5.8), dpi=100)
    ax = fig.add_subplot(111)

    if tipo == "ra":
        resumo = resumo.sort_values("quantidade", ascending=False).copy()
        resumo["codigo_ocupacao"] = resumo["ocupacao_desc"].map(lambda texto: next((str(chave) for chave, valor in OCUPACAO.items() if valor == texto), "?"))
        resumo["codigo_numero"] = pd.to_numeric(resumo["codigo_ocupacao"], errors="coerce")
        resumo["percentual"] = resumo["quantidade"] / resumo["quantidade"].sum() * 100

        palette = sns.color_palette("Set2", n_colors=len(resumo))
        bars = ax.bar(
            resumo["codigo_ocupacao"],
            resumo["quantidade"],
            color=palette,
            edgecolor="black",
        )
        ax.set_title(titulo)
        ax.set_ylabel("Quantidade de moradores")
        ax.set_xlabel("Código da ocupação")
        ax.set_ylim(0, max(resumo["quantidade"]) * 1.18)

        for bar, pct in zip(bars, resumo["percentual"]):
            altura = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                altura + max(resumo["quantidade"]) * 0.01,
                f"{pct:.1f}%",
                ha="center",
                va="bottom",
                fontsize=8,
            )

        color_map = {codigo: to_hex(color) for codigo, color in zip(resumo["codigo_ocupacao"], palette)}
        legenda_ordenada = resumo.sort_values("codigo_numero", ascending=True)
        legenda_itens = [
            (color_map[row["codigo_ocupacao"]], f"{row['codigo_ocupacao']} - {row['ocupacao_desc']}")
            for _, row in legenda_ordenada.iterrows()
        ]
        mostrar_legenda_em_janela("Legenda - Código da ocupação", legenda_itens)
        for label in ax.get_xticklabels():
            label.set_rotation(45)
            label.set_ha("right")
    else:
        pivot = resumo.pivot(index="ra_nome", columns="ocupacao_desc", values="quantidade").fillna(0)
        palette = sns.color_palette("Set2", n_colors=len(pivot.columns))
        pivot.plot(kind="bar", stacked=True, ax=ax, width=0.8, color=palette, legend=False)
        ax.set_title(titulo)
        ax.set_ylabel("Quantidade de moradores")
        ax.set_xlabel("Nome da RA")
        ax.set_xticks(range(len(pivot.index)))
        ax.set_xticklabels(pivot.index, rotation=60, ha="right")
        legenda_itens = [(to_hex(color), ocupacao) for color, ocupacao in zip(palette, pivot.columns)]
        mostrar_legenda_em_janela("Legenda - Ocupação", legenda_itens)

    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()

    barra_progresso["value"] = 80
    janela.update_idletasks()

    canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    barra_progresso["value"] = 100
    texto_progresso.set("Gráfico carregado")
    janela.update_idletasks()


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

    mostrar_grafico_no_frame(resumo, "Ocupação por RA — Relatório Global", tipo="global")


def carregar_resumo_dados():
    moradores = pd.read_csv("moradores.csv", sep=";", decimal=",", encoding="utf-8-sig", low_memory=False)
    domicilios = pd.read_excel("domicilios.xlsx")

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
        "total_moradores": len(moradores),
        "total_domicilios": len(domicilios),
    }


def gerar_grafico_comparativo(ra_codigo_1, ra_codigo_2):
    moradores = pd.read_csv("moradores.csv", sep=";", decimal=",", encoding="utf-8-sig", low_memory=False)
    dados = moradores[["localidade", "I13"]].copy()
    dados.columns = ["localidade", "ocupacao"]
    dados = dados.dropna(subset=["ocupacao"])
    dados["ocupacao"] = pd.to_numeric(dados["ocupacao"], errors="coerce")
    dados = dados[dados["ocupacao"].between(1, 10)]
    dados["ra_nome"] = dados["localidade"].map(RA_NOMES).fillna("RA desconhecida")
    dados["ocupacao_desc"] = dados["ocupacao"].map(OCUPACAO).fillna("Sem classificação")

    dados_1 = dados[dados["localidade"] == ra_codigo_1]
    dados_2 = dados[dados["localidade"] == ra_codigo_2]

    if dados_1.empty or dados_2.empty:
        messagebox.showinfo("Sem dados", "Uma das RAs selecionadas não possui dados para comparação.")
        return

    resumo_1 = (
        dados_1.groupby(["ra_nome", "ocupacao_desc"], dropna=False)
        .size()
        .reset_index(name="quantidade")
    )
    resumo_2 = (
        dados_2.groupby(["ra_nome", "ocupacao_desc"], dropna=False)
        .size()
        .reset_index(name="quantidade")
    )

    resumo_1["grupo"] = f"{RA_NOMES.get(ra_codigo_1, ra_codigo_1)}"
    resumo_2["grupo"] = f"{RA_NOMES.get(ra_codigo_2, ra_codigo_2)}"
    resumo = pd.concat([resumo_1, resumo_2], ignore_index=True)
    resumo["codigo_ocupacao"] = resumo["ocupacao_desc"].map(lambda texto: next((str(chave) for chave, valor in OCUPACAO.items() if valor == texto), "?"))
    resumo["codigo_numero"] = pd.to_numeric(resumo["codigo_ocupacao"], errors="coerce")

    limpar_frame_conteudo(frame_grafico)
    texto_progresso.set("Carregando comparação...")
    barra_progresso["value"] = 20
    janela.update_idletasks()

    sns.set_theme(style="whitegrid")
    fig = Figure(figsize=(10.8, 5.8), dpi=100)
    ax = fig.add_subplot(111)

    resumo_ordenado = resumo.sort_values(["quantidade", "codigo_numero"], ascending=[False, True]).copy()
    categorias = []
    for _, row in resumo_ordenado.iterrows():
        if row["ocupacao_desc"] not in categorias:
            categorias.append(row["ocupacao_desc"])

    pivot = resumo_ordenado.pivot(index="ocupacao_desc", columns="grupo", values="quantidade").fillna(0)
    pivot = pivot.reindex(categorias)

    bars = ax.bar(
        range(len(pivot.index)),
        pivot.iloc[:, 0].tolist(),
        width=0.35,
        color="#4C78A8",
        label=list(pivot.columns)[0],
    )
    bars2 = ax.bar(
        [x + 0.35 for x in range(len(pivot.index))],
        pivot.iloc[:, 1].tolist() if len(pivot.columns) > 1 else [0] * len(pivot.index),
        width=0.35,
        color="#F58518",
        label=list(pivot.columns)[1] if len(pivot.columns) > 1 else "",
    )

    ax.set_title(f"Comparação entre {RA_NOMES.get(ra_codigo_1, ra_codigo_1)} e {RA_NOMES.get(ra_codigo_2, ra_codigo_2)}")
    ax.set_ylabel("Quantidade de moradores")
    ax.set_xlabel("Código da ocupação")
    ax.set_xticks([x + 0.175 for x in range(len(pivot.index))])
    codigos_eixo = [resumo_ordenado.loc[resumo_ordenado["ocupacao_desc"] == ocup, "codigo_ocupacao"].iloc[0] for ocup in pivot.index]
    ax.set_xticklabels(codigos_eixo, rotation=45, ha="right")

    dados_hover = {}
    for ocup in pivot.index:
        codigo = resumo_ordenado.loc[resumo_ordenado["ocupacao_desc"] == ocup, "codigo_ocupacao"].iloc[0]
        dados_hover[codigo] = {
            "descricao": ocup,
            "valor_1": int(pivot.loc[ocup, list(pivot.columns)[0]]),
            "valor_2": int(pivot.loc[ocup, list(pivot.columns)[1]]) if len(pivot.columns) > 1 else 0,
        }

    annotation = ax.annotate(
        "",
        xy=(0, 0),
        xytext=(12, 12),
        textcoords="offset points",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="gray"),
        fontsize=9,
        arrowprops=dict(arrowstyle="->"),
    )
    annotation.set_visible(False)

    def mostrar_info_hover(event):
        if event.inaxes != ax:
            annotation.set_visible(False)
            fig.canvas.draw_idle()
            return

        for txt in ax.get_xticklabels():
            if txt.contains(event)[0]:
                codigo = txt.get_text()
                if codigo in dados_hover:
                    dados = dados_hover[codigo]
                    texto = (
                        f"Código: {codigo}\n"
                        f"Ocupação: {dados['descricao']}\n"
                        f"{list(pivot.columns)[0]}: {dados['valor_1']}\n"
                        f"{list(pivot.columns)[1]}: {dados['valor_2']}"
                    )
                    annotation.set_text(texto)
                    annotation.xy = (event.xdata, event.ydata)
                    annotation.set_visible(True)
                    fig.canvas.draw_idle()
                else:
                    annotation.set_visible(False)
                return

        annotation.set_visible(False)
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", mostrar_info_hover)

    for bar_container in [bars, bars2]:
        for bar in bar_container:
            altura = bar.get_height()
            if altura > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    altura + max(pivot.max().max() * 0.01, 0.2),
                    f"{altura:.0f}",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                )

    legenda_ra_itens = [
        ("#4C78A8", list(pivot.columns)[0]),
        ("#F58518", list(pivot.columns)[1] if len(pivot.columns) > 1 else "")
    ]
    mostrar_legenda_em_janela("Legenda - RAs", legenda_ra_itens)

    unique_codigos = resumo_ordenado.sort_values("codigo_numero")["codigo_ocupacao"].drop_duplicates()
    palette_codigos = sns.color_palette("Set2", n_colors=max(3, len(unique_codigos)))
    legenda_ocupacao_itens = [
        (to_hex(color), f"{codigo} - {resumo_ordenado.loc[resumo_ordenado['codigo_ocupacao'] == codigo, 'ocupacao_desc'].iloc[0]}")
        for codigo, color in zip(unique_codigos, palette_codigos)
    ]
    mostrar_legenda_em_janela("Legenda - Código da ocupação", legenda_ocupacao_itens)

    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()

    barra_progresso["value"] = 100
    texto_progresso.set("Comparação carregada")
    janela.update_idletasks()

    canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def comparar_ras_selecionadas():
    if not var_ra1.get() or not var_ra2.get():
        messagebox.showinfo("Seleção incompleta", "Selecione duas RAs para comparar.")
        return

    ra_codigo_1 = int(var_ra1.get().split(" - ")[0])
    ra_codigo_2 = int(var_ra2.get().split(" - ")[0])

    if ra_codigo_1 == ra_codigo_2:
        messagebox.showinfo("Seleção inválida", "Escolha duas RAs diferentes para comparar.")
        return

    gerar_grafico_comparativo(ra_codigo_1, ra_codigo_2)


def gerar_grafico_ocupacao_por_ra(ra_codigo=None):
    if ra_codigo is not None:
        resposta = messagebox.askyesno(
            "Gerar relatório em TXT",
            f"Gostaria de gerar um relatório em .txt para a RA {ra_codigo}?"
        )
        if resposta:
            gerar_relatorio_txt(ra_codigo)

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

    if ra_codigo is not None:
        ra_nome = RA_NOMES.get(ra_codigo, f"RA-{ra_codigo}")
        mostrar_grafico_no_frame(resumo, f"Ocupações para {ra_nome}", tipo="ra")
    else:
        mostrar_grafico_no_frame(resumo, "Ocupação por nome de RA", tipo="global")


janela = tk.Tk()
janela.title("Recorte E — Trabalho e ocupação - Jamil Machado")
janela.geometry("1000x750")

label_instrucao = tk.Label(
    janela,
    text="""Este sistema analisa dados do censo de moradores por RA e gera gráficos de ocupação e relatórios,
    com base em dados extraídos do site https://pdad.ipe.df.gov.br, a analise dos dados será capaz de responder as perguntas. 
    Como se distribui a população ocupada no DF? Quais setores de atividade predominam?""",
    font=("Arial", 11),
)
label_instrucao.pack(pady=10)

resumo = carregar_resumo_dados()
texto_resumo = (
    f"Dados coletados:\n"
    f"- Total de moradores: {resumo['total_moradores']}\n"
    f"- Total de domicílios: {resumo['total_domicilios']}\n"
    f"- Total de RAs disponíveis: {resumo['total_ras']}\n"
    f"- Registros com ocupação declarada: {resumo['ocupacoes_validas']}\n"
    f"- Registros filtrados (ocupação não declarada): {resumo['ocupacoes_invalidas']}\n"
    f"\nDados filtrados para análise:\n"
    f"- Foram consideradas apenas os 10 tipos de ocupações.\n"
    f"- Valores como 99999 e 88888 foram ignorados."
)

caixa_resumo = tk.Text(janela, height=8, width=80, font=("Arial", 10))
caixa_resumo.insert("1.0", texto_resumo)
caixa_resumo.config(state="disabled")
caixa_resumo.pack(padx=10, pady=(0, 10))

frame_controles = tk.Frame(janela)
frame_controles.pack(fill=tk.X, padx=10, pady=(0, 10))

label_ra = tk.Label(frame_controles, text="RA para análise:")
label_ra.pack(side=tk.LEFT, padx=(0, 8))

opcoes_ra = [f"{ra_codigo} - {ra_nome}" for ra_codigo, ra_nome in sorted(RA_NOMES.items())]
var_ra = tk.StringVar()
combo_ra = ttk.Combobox(frame_controles, textvariable=var_ra, values=opcoes_ra, width=25, state="readonly")
combo_ra.pack(side=tk.LEFT)
combo_ra.bind("<<ComboboxSelected>>", lambda event: gerar_grafico_ocupacao_por_ra(int(var_ra.get().split(" - ")[0])) if var_ra.get() else None)

label_ra1 = tk.Label(frame_controles, text="RA 1:")
label_ra1.pack(side=tk.LEFT, padx=(10, 6))
var_ra1 = tk.StringVar()
combo_ra1 = ttk.Combobox(frame_controles, textvariable=var_ra1, values=opcoes_ra, width=25, state="readonly")
combo_ra1.pack(side=tk.LEFT)

label_ra2 = tk.Label(frame_controles, text="RA 2:")
label_ra2.pack(side=tk.LEFT, padx=(10, 6))
var_ra2 = tk.StringVar()
combo_ra2 = ttk.Combobox(frame_controles, textvariable=var_ra2, values=opcoes_ra, width=25, state="readonly")
combo_ra2.pack(side=tk.LEFT)

botao_comparar = tk.Button(
    frame_controles,
    text="Comparar RAs",
    command=comparar_ras_selecionadas,
    width=16,
    height=1,
)
botao_comparar.pack(side=tk.LEFT, padx=(10, 0))

botao_global = tk.Button(
    frame_controles,
    text="Relatório global",
    command=gerar_relatorio_global,
    width=18,
    height=1,
)
botao_global.pack(side=tk.LEFT, padx=(10, 0))

frame_progresso = tk.Frame(janela)
frame_progresso.pack(fill=tk.X, padx=10, pady=(0, 10))

texto_progresso = tk.StringVar(value="Aguardando")
label_progresso = tk.Label(frame_progresso, textvariable=texto_progresso, font=("Arial", 9))
label_progresso.pack(anchor=tk.W)

barra_progresso = ttk.Progressbar(frame_progresso, orient=tk.HORIZONTAL, length=300, mode="determinate")
barra_progresso.pack(fill=tk.X, pady=(4, 0))
barra_progresso["value"] = 0

frame_grafico = tk.Frame(janela, bg="white", bd=1, relief=tk.SOLID)
frame_grafico.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

janela.mainloop()