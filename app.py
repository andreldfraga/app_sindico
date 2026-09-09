import os
import base64
import hashlib

import streamlit as st
import streamlit.components.v1 as components
from datetime import date


from db import get_connection

st.set_page_config(page_title="Gestão de Condomínios", page_icon="🏢", layout="wide")
LOGO = "logo.png"

# ===== CSS =====
st.markdown("""
<style>
    .stApp { background-color: #eef2f7; }
    h1, h2, h3 { color: #1f3a5f; }
    .stButton > button {
        background-color: #1f3a5f; color: white; border-radius: 10px; border: none;
        padding: 0.5rem 1.2rem; font-weight: 600; box-shadow: 0 2px 6px rgba(31,58,95,0.25); transition: all 0.2s;
    }
    .stButton > button:hover { background-color: #2e5a8a; color: white; transform: translateY(-1px); }
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div,
    .stNumberInput input, .stDateInput input { border-radius: 8px; border: 1px solid #c9d4e3; background-color: #ffffff; }
    .stAlert { border-radius: 10px; }
    .card {
        background: #ffffff; border-radius: 14px; padding: 1.2rem 1.4rem;
        box-shadow: 0 3px 10px rgba(31,58,95,0.08); border-left: 6px solid #1f3a5f; margin-bottom: 0.8rem;
    }
    .card-receita { border-left-color: #2e9e5b; }
    .card-despesa { border-left-color: #d64545; }
    .card-saldo   { border-left-color: #1f3a5f; }
    .card-conta   { border-left-color: #d9a514; }
    .card-azul    { border-left-color: #2e5a8a; }
    .card-roxo    { border-left-color: #7b4fd0; }
    .card-laranja { border-left-color: #e07b39; }
    .card-amarelo { border-left-color: #d9a514; }
    .card-cinza   { border-left-color: #6b7280; }
    .card h4 { margin: 0 0 0.2rem 0; color: #6b7280; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; }
    .card .valor { font-size: 1.7rem; font-weight: 700; color: #1f3a5f; }
    .caixa {
        background: #ffffff; border-radius: 14px; padding: 1.1rem 1.3rem;
        box-shadow: 0 3px 10px rgba(31,58,95,0.08); border: 1px solid #e2e8f0; margin-bottom: 1rem;
    }
    .banner {
        border-radius: 12px; padding: 10px 16px; margin-bottom: 12px; color: #ffffff;
        font-weight: 700; font-size: 1.05rem; box-shadow: 0 3px 8px rgba(0,0,0,0.12);
    }
    .banner-azul    { background: linear-gradient(90deg, #1f3a5f, #2e5a8a); }
    .banner-verde   { background: linear-gradient(90deg, #1e7a46, #2e9e5b); }
    .banner-vermelho{ background: linear-gradient(90deg, #b53434, #d64545); }
    .banner-amarelo { background: linear-gradient(90deg, #b8860b, #d9a514); }
    .banner-roxo    { background: linear-gradient(90deg, #5b2d8a, #7b4fd0); }
    .banner-laranja { background: linear-gradient(90deg, #c05621, #e07b39); }
    .badge {
        display: inline-block; padding: 3px 10px; border-radius: 20px; color: #fff;
        font-size: 0.75rem; font-weight: 700;
    }
    .badge-verde   { background: #2e9e5b; }
    .badge-vermelho{ background: #d64545; }
    .badge-amarelo { background: #d9a514; }
    .badge-azul    { background: #2e5a8a; }
    .badge-roxo    { background: #7b4fd0; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #f8fbff 0%, #e8eef7 100%); border-right: 2px solid #1f3a5f; }
    [data-testid="stSidebar"] .stRadio > div { gap: 6px; }
    [data-testid="stSidebar"] .stRadio label {
        background: #ffffff; border: 2px solid #dbe3ee; border-left: 6px solid #1f3a5f;
        border-radius: 12px; padding: 10px 14px; margin: 0;
        box-shadow: 0 2px 6px rgba(31,58,95,0.08); font-weight: 600; color: #1f3a5f;
        transition: all 0.2s ease; cursor: pointer;
    }
    [data-testid="stSidebar"] .stRadio label:hover { border-color: #1f3a5f; background: #f0f6ff; transform: translateX(3px); }
    [data-testid="stSidebar"] .stRadio label:has(input:checked) {
        background: linear-gradient(90deg, #dbeafe 0%, #bfdbfe 100%);
        color: #1f3a5f !important; border-left-color: #f0b429; box-shadow: 0 4px 12px rgba(31,58,95,0.25);
    }
    [data-testid="stSidebar"] .stRadio label:has(input:checked) p,
    [data-testid="stSidebar"] .stRadio label:has(input:checked) div,
    [data-testid="stSidebar"] .stRadio label:has(input:checked) span { color: #1f3a5f !important; font-weight: 700; }
    [data-testid="stSidebar"] div[data-testid="stElementContainer"]:has(div[data-testid="stRadio"]) ~ div[data-testid="stElementContainer"]:has(div[data-testid="stRadio"]) div[data-testid="stRadio"] label {
        margin-left: 20px; padding: 8px 12px; border-left-color: #f0b429; background: #fafbfd;
    }
    [data-testid="stSidebar"] div[data-testid="stElementContainer"]:has(div[data-testid="stRadio"]) ~ div[data-testid="stElementContainer"]:has(div[data-testid="stRadio"]) div[data-testid="stRadio"] label:hover {
        background: #eef2f7; border-color: #f0b429;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] > div { border-radius: 10px; border: 2px solid #1f3a5f; background: #ffffff; font-weight: 600; }
    [data-testid="stSidebar"] .stButton > button { background-color: #d64545; width: 100%; box-shadow: none; }
    [data-testid="stSidebar"] .stButton > button:hover { background-color: #b53434; }
    .streamlit-expanderHeader { font-weight: 600; color: #1f3a5f; }
    .streamlit-expander { border: 1px solid #e2e8f0; border-radius: 10px; }
    [data-testid="stMetric"] { background: #ffffff; border-radius: 14px; padding: 1rem 1.2rem; box-shadow: 0 3px 10px rgba(31,58,95,0.08); border-left: 6px solid #1f3a5f; }
    [data-testid="stMetricLabel"] { color: #6b7280; }
    [data-testid="stMetricValue"] { color: #1f3a5f; }

    /* ===== CONTRASTE DOS WIDGETS DE SELEÇÃO ===== */
    .stSelectbox label, .stMultiselect label, .stRadio label,
    .stCheckbox label, .stTextInput label, .stNumberInput label,
    .stDateInput label, .stTextArea label {
        color: #0f1e3a !important;
        font-weight: 700 !important;
    }
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div {
        background-color: #ffffff !important;
        border: 2px solid #1f3a5f !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 6px rgba(15, 30, 58, 0.15) !important;
    }
    div[data-baseweb="select"] * {
        color: #0f1e3a !important;
    }
    div[data-baseweb="select"] [role="listbox"],
    div[data-baseweb="select"] ul {
        background-color: #ffffff !important;
    }
    div[data-baseweb="popover"] {
        background-color: #ffffff !important;
        border: 1px solid #1f3a5f !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="checkbox"], div[role="radiogroup"] {
        background-color: #ffffff !important;
        border: 1px solid #c5d1e2 !important;
        border-radius: 8px !important;
        padding: 6px 10px !important;
    }
    .stDownloadButton>button, .stButton>button {
        border: 2px solid #1f3a5f !important;
        box-shadow: 0 2px 6px rgba(15, 30, 58, 0.2) !important;
    }

</style>
""", unsafe_allow_html=True)

# ===== FUNÇÕES AUXILIARES =====
def fmt_br(v):
    return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def card(titulo, valor, tipo="saldo"):
    cor = {"receita": "card-receita", "despesa": "card-despesa", "saldo": "card-saldo",
           "conta": "card-conta", "azul": "card-azul", "roxo": "card-roxo",
           "laranja": "card-laranja", "amarelo": "card-amarelo", "cinza": "card-cinza"}.get(tipo, "card-saldo")
    st.markdown(f'<div class="card {cor}"><h4>{titulo}</h4><div class="valor">{valor}</div></div>',
                unsafe_allow_html=True)

def banner(titulo, cor="azul"):
    cores = {"azul": "banner-azul", "verde": "banner-verde", "vermelho": "banner-vermelho",
             "amarelo": "banner-amarelo", "roxo": "banner-roxo", "laranja": "banner-laranja"}
    st.markdown(f'<div class="banner {cores.get(cor, "banner-azul")}">{titulo}</div>',
                unsafe_allow_html=True)

def badge(texto, cor="azul"):
    cores = {"verde": "badge-verde", "vermelho": "badge-vermelho", "amarelo": "badge-amarelo",
             "azul": "badge-azul", "roxo": "badge-roxo"}
    return f'<span class="badge {cores.get(cor, "badge-azul")}">{texto}</span>'

def html_logo(max_height=80):
    if not os.path.exists(LOGO):
        return ""
    try:
        with open(LOGO, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        mime = "image/jpeg" if LOGO.lower().endswith((".jpg", ".jpeg")) else "image/png"
        return f'<div style="text-align:center; margin-bottom:10px;"><img src="data:{mime};base64,{b64}" style="max-height:{max_height}px;"></div>'
    except Exception:
        return ""

def ficha_cadastral_html(cur, apto_id, numero, bloco, proprietario, telefone, email, nome_condominio):
    """Monta o HTML da ficha cadastral: dados, moradores, veículos/pets e funcionárias."""
    cur.execute(
        "SELECT nome, parentesco, telefone, email, is_principal FROM moradores "
        "WHERE apartamento_id = %s ORDER BY is_principal DESC, nome", (apto_id,),
    )
    moradores = cur.fetchall()
    itens_moradores = ""
    for m in moradores:
        principal = " (morador principal)" if m["is_principal"] else ""
        parentesco_txt = f" ({m['parentesco']})" if m["parentesco"] else ""
        itens_moradores += f"<li>{m['nome']}{parentesco_txt}{principal} — {m['telefone'] or ''} {m['email'] or ''}</li>"
    if not itens_moradores:
        itens_moradores = "<li>Nenhum morador cadastrado.</li>"

    linhas_vep = ""
    try:
        cur.execute("SELECT tipo, marca, modelo, placa, cor, ano FROM veiculos "
                    "WHERE apartamento_id = %s ORDER BY id", (apto_id,))
        for v in cur.fetchall():
            desc = f"{v['tipo']} {v['marca'] or ''} {v['modelo'] or ''}".strip()
            detalhes = f"Placa {v['placa'] or '—'} | Cor {v['cor'] or '—'} | Ano {v['ano'] or '—'}"
            linhas_vep += f"<tr><td>🚗</td><td>{desc}</td><td>{detalhes}</td></tr>"
    except Exception:
        pass
    try:
        cur.execute("SELECT tipo, raca, porte, observacao FROM pets "
                    "WHERE apartamento_id = %s ORDER BY id", (apto_id,))
        for p in cur.fetchall():
            desc = p["tipo"] or ""
            if p["raca"]:
                desc += f" {p['raca']}"
            detalhes = ""
            if p["porte"]:
                detalhes += f"Porte {p['porte']}"
            if p["observacao"]:
                detalhes += (f" | {p['observacao']}" if detalhes else p["observacao"])
            linhas_vep += f"<tr><td>🐾</td><td>{desc}</td><td>{detalhes}</td></tr>"
    except Exception:
        pass
    if not linhas_vep:
        linhas_vep = "<tr><td colspan='3'>Nenhum veículo ou pet cadastrado.</td></tr>"

    linhas_func = ""
    try:
        cur.execute("SELECT nome, cpf, telefone FROM empregadas "
                    "WHERE apartamento_id = %s ORDER BY nome", (apto_id,))
        for f in cur.fetchall():
            cpf_txt = f["cpf"] or ""
            if len(cpf_txt) == 11:
                cpf_txt = f"{cpf_txt[:3]}.{cpf_txt[3:6]}.{cpf_txt[6:9]}-{cpf_txt[9:]}"
            linhas_func += f"<tr><td>{f['nome']}</td><td>{cpf_txt or '—'}</td><td>{f['telefone'] or '—'}</td></tr>"
    except Exception:
        linhas_func = ""
    if not linhas_func:
        linhas_func = "<tr><td colspan='3'>Nenhuma funcionária vinculada a este apartamento.</td></tr>"

    bloco_txt = f" - Bloco {bloco}" if bloco else ""
    return f"""
    <h2 style="text-align:center;">FICHA CADASTRAL</h2>
    <p style="text-align:center; font-weight:bold;">{nome_condominio}</p>
    <p style="text-align:center;">Apartamento {numero}{bloco_txt}</p>
    <hr>
    <p><b>Proprietário:</b> {proprietario or '—'}</p>
    <p><b>Telefone:</b> {telefone or '—'} &nbsp;|&nbsp; <b>E-mail:</b> {email or '—'}</p>
    <h3>Moradores</h3>
    <ul>{itens_moradores}</ul>
    <h3>🚗 Veículos e 🐾 Pets</h3>
    <table style="width:100%; border-collapse:collapse; font-size:0.85em;">
        <tr style="background:#1f3a5f; color:#fff;">
            <th style="padding:4px; border:1px solid #ccc; text-align:left; width:5%;"></th>
            <th style="padding:4px; border:1px solid #ccc; text-align:left;">Descrição</th>
            <th style="padding:4px; border:1px solid #ccc; text-align:left;">Detalhes</th>
        </tr>{linhas_vep}
    </table>
    <h3>👩‍💼 Funcionárias do apartamento</h3>
    <table style="width:100%; border-collapse:collapse; font-size:0.85em;">
        <tr style="background:#1f3a5f; color:#fff;">
            <th style="padding:4px; border:1px solid #ccc; text-align:left;">Nome</th>
            <th style="padding:4px; border:1px solid #ccc; text-align:left;">CPF</th>
            <th style="padding:4px; border:1px solid #ccc; text-align:left;">Telefone</th>
        </tr>{linhas_func}
    </table>
    """

def saldo_acumulado_ate(condominio_id, cur, mes, ano):
    """Saldo acumulado até o FIM do mês/ano informado (usa saldo inicial + lançamentos)."""
    try:
        cur.execute(
            "SELECT mes, ano, valor FROM saldos_iniciais "
            "WHERE condominio_id = %s AND (ano < %s OR (ano = %s AND mes <= %s)) "
            "ORDER BY ano DESC, mes DESC LIMIT 1",
            (condominio_id, ano, ano, mes),
        )
        reg = cur.fetchone()
    except Exception:
        reg = None
    data_fim = date(ano + 1, 1, 1) if mes == 12 else date(ano, mes + 1, 1)
    if reg:
        saldo = float(reg["valor"])
        data_inicio = date(reg["ano"], reg["mes"], 1)
        cur.execute(
            "SELECT COALESCE(SUM(CASE WHEN tipo = 'receita' THEN valor ELSE -valor END), 0) AS saldo "
            "FROM lancamentos WHERE condominio_id = %s AND data_lancamento >= %s AND data_lancamento < %s",
            (condominio_id, data_inicio, data_fim),
        )
        saldo += float(cur.fetchone()["saldo"])
        return saldo
    cur.execute(
        "SELECT COALESCE(SUM(CASE WHEN tipo = 'receita' THEN valor ELSE -valor END), 0) AS saldo "
        "FROM lancamentos WHERE condominio_id = %s AND data_lancamento < %s",
        (condominio_id, data_fim),
    )
    return float(cur.fetchone()["saldo"])

def registrar_auditoria(cur, tabela, registro_id, acao, detalhes=""):
    """Registra uma ação no log de auditoria (tolerante a falhas)."""
    try:
        cur.execute(
            "INSERT INTO auditoria (usuario_id, usuario_nome, tabela, registro_id, acao, detalhes) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (st.session_state.get("usuario_id"),
             st.session_state.get("usuario", "—"),
             tabela, registro_id, acao, detalhes[:500]),
        )
    except Exception:
        pass

MESES_NOMES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
               "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]


def garantir_coluna_logo(conn):
    """Adiciona a coluna logo (BYTEA) à tabela condominios, se ainda não existir."""
    try:
        cur = conn.cursor()
        cur.execute("ALTER TABLE condominios ADD COLUMN IF NOT EXISTS logo BYTEA")
        conn.commit()
        cur.close()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass

def obter_logo(cur, condominio_id):
    """Retorna os bytes da logomarca do condomínio, ou None."""
    try:
        cur.execute("SELECT logo FROM condominios WHERE id = %s", (condominio_id,))
        r = cur.fetchone()
        if r and r.get("logo"):
            return bytes(r["logo"])
    except Exception:
        pass
    return None

def gerar_excel_prestacao(cur, conn, condominio_id, filtro_data, params_data,
                          saldo_anterior, total_receitas, total_despesas,
                          saldo_periodo, saldo_atual, titulo_doc, nome_sel,
                          titulo_periodo):
    """Gera o Excel da prestação de contas seguindo o modelo (mensal ou anual)."""
    import re
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
             "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    eh_anual = "ano" in str(titulo_periodo).lower()

    def chave_apto(numero, bloco):
        try:
            num_key = (0, int(numero))
        except (TypeError, ValueError):
            num_key = (1, str(numero or ""))
        return (num_key, str(bloco or ""))

    wb = Workbook()
    wb.remove(wb.active)
    thin = Side(style="thin", color="BBBBBB")
    borda = Border(top=thin, bottom=thin, left=thin, right=thin)
    titulo_aba = f"{nome_sel} — {titulo_periodo}"

    def add_sheet(nome_aba, colunas, linhas, negrito_ultima_linha=True):
        ws = wb.create_sheet(nome_aba)
        ncols = max(len(colunas), 1)
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncols)
        c = ws.cell(row=1, column=1, value=titulo_aba)
        c.font = Font(bold=True, size=13, color="1F3A5F")
        c.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 24
        ws.append(colunas)
        for j in range(1, len(colunas) + 1):
            cell = ws.cell(row=2, column=j)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="1F3A5F")
            cell.alignment = Alignment(horizontal="center", vertical="center")
        for i, linha in enumerate(linhas):
            ws.append([linha.get(col) for col in colunas])
            if negrito_ultima_linha and i == len(linhas) - 1:
                for j in range(1, len(colunas) + 1):
                    ws.cell(row=ws.max_row, column=j).font = Font(bold=True)
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row,
                                min_col=1, max_col=len(colunas)):
            for cell in row:
                cell.border = borda
        ws.freeze_panes = "A3"
        for j in range(1, len(colunas) + 1):
            letra = get_column_letter(j)
            maxlen = 10
            for row in ws.iter_rows(min_row=3, max_row=ws.max_row,
                                    min_col=j, max_col=j):
                for cell in row:
                    v = cell.value
                    if v is not None and len(str(v)) > maxlen:
                        maxlen = len(str(v))
            ws.column_dimensions[letra].width = min(maxlen + 2, 40)
        return ws

    if eh_anual:
        # Meses com dados
        cur.execute(f"SELECT DISTINCT EXTRACT(MONTH FROM l.data_lancamento) AS mes "
                    f"FROM lancamentos l WHERE l.condominio_id = %s AND {filtro_data} "
                    f"ORDER BY mes", (condominio_id, *params_data))
        meses_dados = sorted(int(r["mes"]) for r in cur.fetchall())
        meses_uso = list(range(1, 13)) if meses_dados else []
        cab_meses = [MESES[m - 1] for m in meses_uso]

        # 1) Receitas por apartamento
        cur.execute(f"SELECT a.numero, a.bloco, "
                    f"EXTRACT(MONTH FROM l.data_lancamento) AS mes, SUM(l.valor) AS total "
                    f"FROM lancamentos l "
                    f"LEFT JOIN apartamentos a ON a.id = l.apartamento_id "
                    f"WHERE l.condominio_id = %s AND l.tipo = 'receita' "
                    f"AND l.apartamento_id IS NOT NULL AND {filtro_data} "
                    f"GROUP BY a.numero, a.bloco, EXTRACT(MONTH FROM l.data_lancamento)",
                    (condominio_id, *params_data))
        por_apto = {}
        tot_mes1 = {m: 0.0 for m in meses_uso}
        for r in cur.fetchall():
            chave = chave_apto(r["numero"], r["bloco"])
            if chave not in por_apto:
                por_apto[chave] = {m: 0.0 for m in meses_uso}
                por_apto[chave]["_rotulo"] = (f"{r['numero']}"
                                              + (f" - Bloco {r['bloco']}" if r["bloco"] else ""))
            por_apto[chave][int(r["mes"])] += float(r["total"])
            tot_mes1[int(r["mes"])] += float(r["total"])

        linhas1 = []
        for chave in sorted(por_apto.keys()):
            vals = por_apto[chave]
            linha = {"Apartamento": vals["_rotulo"]}
            for m in meses_uso:
                linha[MESES[m - 1]] = vals[m] if vals[m] else None
            linha["Total"] = sum(vals[m] for m in meses_uso)
            linhas1.append(linha)
        if linhas1:
            linha_tot = {"Apartamento": "Total"}
            for m in meses_uso:
                linha_tot[MESES[m - 1]] = tot_mes1[m] if tot_mes1[m] else None
            linha_tot["Total"] = sum(tot_mes1.values())
            linhas1.append(linha_tot)
            add_sheet("Receitas por Apartamento",
                      ["Apartamento"] + cab_meses + ["Total"], linhas1)

        # 2) Outras receitas
        cur.execute(f"SELECT COALESCE(NULLIF(l.descricao, ''), l.categoria) AS nome, "
                    f"EXTRACT(MONTH FROM l.data_lancamento) AS mes, SUM(l.valor) AS total "
                    f"FROM lancamentos l "
                    f"WHERE l.condominio_id = %s AND l.tipo = 'receita' "
                    f"AND l.apartamento_id IS NULL AND {filtro_data} "
                    f"GROUP BY nome, EXTRACT(MONTH FROM l.data_lancamento)",
                    (condominio_id, *params_data))
        por_outras = {}
        tot_mes2 = {m: 0.0 for m in meses_uso}
        for r in cur.fetchall():
            nome = r["nome"] or "—"
            if nome not in por_outras:
                por_outras[nome] = {m: 0.0 for m in meses_uso}
            por_outras[nome][int(r["mes"])] += float(r["total"])
            tot_mes2[int(r["mes"])] += float(r["total"])

        linhas2 = []
        for nome in sorted(por_outras.keys()):
            vals = por_outras[nome]
            linha = {"Descrição": nome}
            for m in meses_uso:
                linha[MESES[m - 1]] = vals[m] if vals[m] else None
            linha["Total"] = sum(vals[m] for m in meses_uso)
            linhas2.append(linha)
        if linhas2:
            linha_tot = {"Descrição": "Total"}
            for m in meses_uso:
                linha_tot[MESES[m - 1]] = tot_mes2[m] if tot_mes2[m] else None
            linha_tot["Total"] = sum(tot_mes2.values())
            linhas2.append(linha_tot)
            add_sheet("Outras Receitas", ["Descrição"] + cab_meses + ["Total"], linhas2)

        # 3) Despesas
        cur.execute(f"SELECT l.categoria AS nome, "
                    f"EXTRACT(MONTH FROM l.data_lancamento) AS mes, SUM(l.valor) AS total "
                    f"FROM lancamentos l "
                    f"WHERE l.condominio_id = %s AND l.tipo = 'despesa' "
                    f"AND {filtro_data} "
                    f"GROUP BY l.categoria, EXTRACT(MONTH FROM l.data_lancamento)",
                    (condominio_id, *params_data))
        por_dep = {}
        tot_mes3 = {m: 0.0 for m in meses_uso}
        for r in cur.fetchall():
            nome = r["nome"] or "—"
            if nome not in por_dep:
                por_dep[nome] = {m: 0.0 for m in meses_uso}
            por_dep[nome][int(r["mes"])] += float(r["total"])
            tot_mes3[int(r["mes"])] += float(r["total"])

        linhas3 = []
        for nome in sorted(por_dep.keys()):
            vals = por_dep[nome]
            linha = {"Categoria": nome}
            for m in meses_uso:
                linha[MESES[m - 1]] = vals[m] if vals[m] else None
            linha["Total"] = sum(vals[m] for m in meses_uso)
            linhas3.append(linha)
        if linhas3:
            linha_tot = {"Categoria": "Total"}
            for m in meses_uso:
                linha_tot[MESES[m - 1]] = tot_mes3[m] if tot_mes3[m] else None
            linha_tot["Total"] = sum(tot_mes3.values())
            linhas3.append(linha_tot)
            add_sheet("Despesas", ["Categoria"] + cab_meses + ["Total"], linhas3)

        # 4) Consolidação
        receitas_mes = {m: tot_mes1.get(m, 0.0) + tot_mes2.get(m, 0.0) for m in meses_uso}
        despesas_mes = tot_mes3
        saldo_inicial = None
        m_ano = re.search(r"(\d{4})", str(titulo_periodo))
        if m_ano and meses_uso:
            ano_periodo = int(m_ano.group(1))
            cur.execute("SELECT valor FROM saldos_iniciais "
                        "WHERE condominio_id = %s AND mes = %s AND ano = %s",
                        (condominio_id, meses_uso[0], ano_periodo))
            r = cur.fetchone()
            if r:
                saldo_inicial = float(r["valor"])
        if saldo_inicial is None:
            saldo_inicial = float(saldo_anterior)

        saldo_ant = {}
        saldo_acum = {}
        acum = saldo_inicial
        for m in meses_uso:
            saldo_ant[m] = acum
            acum = acum + receitas_mes[m] - despesas_mes[m]
            saldo_acum[m] = acum

        valores4 = {
            "Saldo anterior": saldo_ant,
            "(+) Receitas": receitas_mes,
            "(\u2212) Despesas": despesas_mes,
            "(=) Saldo do mês": {m: receitas_mes[m] - despesas_mes[m] for m in meses_uso},
            "Saldo acumulado": saldo_acum,
        }
        linhas4 = []
        for nome, vals in valores4.items():
            linha = {"Rubrica": nome}
            for m in meses_uso:
                linha[MESES[m - 1]] = vals[m]
            linha["Total"] = sum(vals[m] for m in meses_uso)
            linhas4.append(linha)
        add_sheet("Consolidação", ["Rubrica"] + cab_meses + ["Total"], linhas4)

    else:
        # ===== MENSAL =====
        cur.execute(f"SELECT a.numero, a.bloco, l.categoria, l.valor "
                    f"FROM lancamentos l "
                    f"LEFT JOIN apartamentos a ON a.id = l.apartamento_id "
                    f"WHERE l.condominio_id = %s AND l.tipo = 'receita' "
                    f"AND l.apartamento_id IS NOT NULL AND {filtro_data} "
                    f"ORDER BY a.numero", (condominio_id, *params_data))
        linhas1 = []
        tot1 = 0.0
        for r in cur.fetchall():
            apto_txt = (f"{r['numero']}" + (f" - Bloco {r['bloco']}" if r["bloco"] else ""))
            linhas1.append({"Apartamento": apto_txt, "Categoria": r["categoria"],
                            "Valor": float(r["valor"])})
            tot1 += float(r["valor"])
        if linhas1:
            linhas1.append({"Apartamento": "Total", "Categoria": "", "Valor": tot1})
            add_sheet("Receitas", ["Apartamento", "Categoria", "Valor"], linhas1)

        cur.execute(f"SELECT l.categoria, l.descricao, l.valor "
                    f"FROM lancamentos l "
                    f"WHERE l.condominio_id = %s AND l.tipo = 'receita' "
                    f"AND l.apartamento_id IS NULL AND {filtro_data} "
                    f"ORDER BY l.categoria", (condominio_id, *params_data))
        linhas2 = []
        tot2 = 0.0
        for r in cur.fetchall():
            linhas2.append({"Categoria": r["categoria"], "Descrição": r["descricao"] or "",
                            "Valor": float(r["valor"])})
            tot2 += float(r["valor"])
        if linhas2:
            linhas2.append({"Categoria": "Total", "Descrição": "", "Valor": tot2})
            add_sheet("Outras Receitas", ["Categoria", "Descrição", "Valor"], linhas2)

        linhas3 = [
            {"Rubrica": "Receita Taxa de Condomínio/Garagem", "Valor": tot1},
            {"Rubrica": "Outras Receitas", "Valor": tot2},
            {"Rubrica": "Total das Receitas", "Valor": tot1 + tot2},
        ]
        add_sheet("Resumo das Receitas", ["Rubrica", "Valor"], linhas3)

        cur.execute(f"SELECT l.categoria, l.descricao, l.valor "
                    f"FROM lancamentos l "
                    f"WHERE l.condominio_id = %s AND l.tipo = 'despesa' "
                    f"AND {filtro_data} ORDER BY l.categoria", (condominio_id, *params_data))
        linhas4 = []
        tot4 = 0.0
        for r in cur.fetchall():
            linhas4.append({"Categoria": r["categoria"], "Descrição": r["descricao"] or "",
                            "Valor": float(r["valor"])})
            tot4 += float(r["valor"])
        if linhas4:
            linhas4.append({"Categoria": "Total", "Descrição": "", "Valor": tot4})
            add_sheet("Despesas", ["Categoria", "Descrição", "Valor"], linhas4)

    linhas5 = [
        {"Rubrica": "Saldo do mês anterior", "Valor": saldo_anterior},
        {"Rubrica": "(+) Receitas", "Valor": total_receitas},
        {"Rubrica": "(\u2212) Despesas", "Valor": total_despesas},
        {"Rubrica": "(=) Saldo do mês", "Valor": saldo_periodo},
        {"Rubrica": "Saldo atual", "Valor": saldo_atual},
    ]
    add_sheet("Resumo do período", ["Rubrica", "Valor"], linhas5)

    cur.execute("SELECT banco, tipo, agencia, numero_conta, saldo "
                "FROM contas_bancarias WHERE condominio_id = %s ORDER BY banco",
                (condominio_id,))
    contas = cur.fetchall()
    linhas6 = []
    tot_contas = 0.0
    for c in contas:
        ag_cc = (f"{c['agencia'] or ''} / {c['numero_conta'] or ''}"
                 if (c["agencia"] or c["numero_conta"]) else "—")
        linhas6.append({"Banco": c["banco"], "Tipo": c["tipo"],
                        "Agência / Conta": ag_cc, "Saldo": float(c["saldo"] or 0)})
        tot_contas += float(c["saldo"] or 0)
    if linhas6:
        linhas6.append({"Banco": "Total distribuído em contas", "Tipo": "",
                        "Agência / Conta": "", "Saldo": tot_contas})
        add_sheet("Distribuição por Conta", ["Banco", "Tipo", "Agência / Conta", "Saldo"],
                  linhas6)

    caminho = "prestacao_contas.xlsx"
    wb.save(caminho)
    with open(caminho, "rb") as f:
        st.download_button(
            "💾 Baixar prestacao_contas.xlsx", f.read(),
            file_name="prestacao_contas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    registrar_auditoria(cur, "prestacao_contas", None, "INSERT",
                        f"Exportação Excel do relatório {titulo_periodo}")
    conn.commit()


def gerar_pdf_prestacao(cur, conn, condominio_id, filtro_data, params_data,
                        saldo_anterior, total_receitas, total_despesas,
                        saldo_periodo, saldo_atual, titulo_doc, nome_sel,
                        titulo_periodo):
    """Gera o PDF da prestação de contas seguindo o modelo (mensal ou anual)."""
    import re
    from io import BytesIO
    from datetime import datetime
    from xml.sax.saxutils import escape

    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                    Paragraph, Spacer)
    from reportlab.platypus import Image as RLImage

    MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
             "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    eh_anual = "ano" in str(titulo_periodo).lower()

    def fmt_num(v):
        s = f"{float(v or 0):,.2f}"
        return s.replace(",", "X").replace(".", ",").replace("X", ".")

    def cel(texto, negrito=False):
        if isinstance(texto, dict):
            texto = "; ".join(f"{k}: {v}" for k, v in texto.items())
        estilo = estilo_cel_bold if negrito else estilo_cel
        return Paragraph(escape(str(texto)), estilo)
    
    def chave_apto(numero, bloco):
        try:
            num_key = (0, int(numero))
        except (TypeError, ValueError):
            num_key = (1, str(numero or ""))
        return (num_key, str(bloco or ""))

    def montar_tabela(cabecalho, linhas, linha_total=None, largs=None):
        dados = [cabecalho] + linhas
        if linha_total:
            dados.append(linha_total)
        if largs is None:
            largs = [150] + [48] * (len(cabecalho) - 2) + [64]
        t = Table(dados, repeatRows=1, colWidths=largs)
        t.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3a5f")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 7),
            ("FONTSIZE", (0, 1), (-1, -1), 6.5),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e0e0e0")),
        ]))
        return t

    estilos = getSampleStyleSheet()
    estilo_cel = ParagraphStyle("cel", parent=estilos["Normal"], fontSize=6.5, leading=8)
    estilo_cel_bold = ParagraphStyle("celb", parent=estilos["Normal"], fontSize=6.5,
                                     leading=8, fontName="Helvetica-Bold")
    estilo_titulo = ParagraphStyle("titulo", parent=estilos["Title"],
                                   alignment=1, fontSize=16, spaceAfter=4)
    estilo_nome = ParagraphStyle("nome", parent=estilos["Heading1"],
                                 alignment=1, fontSize=13, spaceAfter=2)
    estilo_periodo = ParagraphStyle("per", parent=estilos["Normal"], alignment=1,
                                    fontSize=9, textColor=colors.HexColor("#555555"))

    pdf_path = "prestacao_contas.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=landscape(A4),
                            leftMargin=16, rightMargin=16,
                            topMargin=22, bottomMargin=22)
    elementos = []

        # ===== Cabeçalho: logo + título + nome + período (centralizados) =====
    _logo_arq = None
    try:
        if os.path.exists(LOGO):
            _logo_arq = LOGO
    except Exception:
        pass
    if _logo_arq is None:
        _logo_arq = next((n for n in ("logo.png", "logo.jpg", "logo.jpeg")
                          if os.path.exists(n)), None)
    if _logo_arq:
        try:
            from reportlab.platypus import Image as RLImage
            _img = RLImage(_logo_arq, width=56, height=56)
            _img.hAlign = "CENTER"
            elementos.append(_img)
        except Exception:
            pass
    elementos.append(Paragraph(f"<b>{escape(titulo_doc)}</b>", estilo_titulo))
    elementos.append(Paragraph(f"<b>{escape(nome_sel)}</b>", estilo_nome))
    elementos.append(Paragraph(f"Período: {escape(titulo_periodo)}", estilo_periodo))
    elementos.append(Spacer(1, 12))

    if eh_anual:
        # ===== ANUAL — matriz Jan a Dez + Total =====
        cur.execute(f"SELECT DISTINCT EXTRACT(MONTH FROM l.data_lancamento) AS mes "
                    f"FROM lancamentos l WHERE l.condominio_id = %s AND {filtro_data} "
                    f"ORDER BY mes", (condominio_id, *params_data))
        meses_dados = sorted(int(r["mes"]) for r in cur.fetchall())
        meses_uso = list(range(1, 13)) if meses_dados else []
        cab_meses = [MESES[m - 1] for m in meses_uso]

        # 1) Receitas — Contribuição por apartamento
        cur.execute(f"SELECT a.numero, a.bloco, "
                    f"EXTRACT(MONTH FROM l.data_lancamento) AS mes, SUM(l.valor) AS total "
                    f"FROM lancamentos l "
                    f"LEFT JOIN apartamentos a ON a.id = l.apartamento_id "
                    f"WHERE l.condominio_id = %s AND l.tipo = 'receita' "
                    f"AND l.apartamento_id IS NOT NULL AND {filtro_data} "
                    f"GROUP BY a.numero, a.bloco, EXTRACT(MONTH FROM l.data_lancamento)",
                    (condominio_id, *params_data))
        por_apto = {}
        tot_mes1 = {m: 0.0 for m in meses_uso}
        for r in cur.fetchall():
            chave = chave_apto(r["numero"], r["bloco"])
            if chave not in por_apto:
                por_apto[chave] = {m: 0.0 for m in meses_uso}
                por_apto[chave]["_rotulo"] = (f"{r['numero']}"
                                              + (f" - Bloco {r['bloco']}" if r["bloco"] else ""))
            mes = int(r["mes"])
            val = float(r["total"])
            por_apto[chave][mes] += val
            tot_mes1[mes] += val

        if por_apto:
            linhas1 = []
            for chave in sorted(por_apto.keys()):
                vals = por_apto[chave]
                linhas1.append([cel(vals["_rotulo"])]
                               + [fmt_num(vals[m]) if vals[m] else "—" for m in meses_uso]
                               + [fmt_num(sum(vals[m] for m in meses_uso))])
            total1 = (["Total"]
                      + [fmt_num(tot_mes1[m]) if tot_mes1[m] else "—" for m in meses_uso]
                      + [fmt_num(sum(tot_mes1.values()))])
            elementos.append(Paragraph("<b>1) Receitas — Contribuição por apartamento</b>",
                                       estilos["Heading2"]))
            elementos.append(montar_tabela(["Apartamento"] + cab_meses + ["Total"],
                                           linhas1, total1))
            elementos.append(Spacer(1, 8))

        # 2) Receitas — Outras
        cur.execute(f"SELECT COALESCE(NULLIF(l.descricao, ''), l.categoria) AS nome, "
                    f"EXTRACT(MONTH FROM l.data_lancamento) AS mes, SUM(l.valor) AS total "
                    f"FROM lancamentos l "
                    f"WHERE l.condominio_id = %s AND l.tipo = 'receita' "
                    f"AND l.apartamento_id IS NULL AND {filtro_data} "
                    f"GROUP BY nome, EXTRACT(MONTH FROM l.data_lancamento)",
                    (condominio_id, *params_data))
        por_outras = {}
        tot_mes2 = {m: 0.0 for m in meses_uso}
        for r in cur.fetchall():
            nome = r["nome"] or "—"
            if nome not in por_outras:
                por_outras[nome] = {m: 0.0 for m in meses_uso}
            mes = int(r["mes"])
            val = float(r["total"])
            por_outras[nome][mes] += val
            tot_mes2[mes] += val

        if por_outras:
            linhas2 = []
            for nome in sorted(por_outras.keys()):
                vals = por_outras[nome]
                linhas2.append([cel(nome)]
                               + [fmt_num(vals[m]) if vals[m] else "—" for m in meses_uso]
                               + [fmt_num(sum(vals[m] for m in meses_uso))])
            total2 = (["Total"]
                      + [fmt_num(tot_mes2[m]) if tot_mes2[m] else "—" for m in meses_uso]
                      + [fmt_num(sum(tot_mes2.values()))])
            elementos.append(Paragraph("<b>2) Receitas — Outras</b>", estilos["Heading2"]))
            elementos.append(montar_tabela(["Descrição"] + cab_meses + ["Total"],
                                           linhas2, total2))
            elementos.append(Spacer(1, 8))

        # 3) Despesas
        cur.execute(f"SELECT l.categoria AS nome, "
                    f"EXTRACT(MONTH FROM l.data_lancamento) AS mes, SUM(l.valor) AS total "
                    f"FROM lancamentos l "
                    f"WHERE l.condominio_id = %s AND l.tipo = 'despesa' "
                    f"AND {filtro_data} "
                    f"GROUP BY l.categoria, EXTRACT(MONTH FROM l.data_lancamento)",
                    (condominio_id, *params_data))
        por_dep = {}
        tot_mes3 = {m: 0.0 for m in meses_uso}
        for r in cur.fetchall():
            nome = r["nome"] or "—"
            if nome not in por_dep:
                por_dep[nome] = {m: 0.0 for m in meses_uso}
            mes = int(r["mes"])
            val = float(r["total"])
            por_dep[nome][mes] += val
            tot_mes3[mes] += val

        if por_dep:
            linhas3 = []
            for nome in sorted(por_dep.keys()):
                vals = por_dep[nome]
                linhas3.append([cel(nome)]
                               + [fmt_num(vals[m]) if vals[m] else "—" for m in meses_uso]
                               + [fmt_num(sum(vals[m] for m in meses_uso))])
            total3 = (["Total"]
                      + [fmt_num(tot_mes3[m]) if tot_mes3[m] else "—" for m in meses_uso]
                      + [fmt_num(sum(tot_mes3.values()))])
            elementos.append(Paragraph("<b>3) Despesas</b>", estilos["Heading2"]))
            elementos.append(montar_tabela(["Categoria"] + cab_meses + ["Total"],
                                           linhas3, total3))
            elementos.append(Spacer(1, 8))

        # 4) Consolidação
        receitas_mes = {m: tot_mes1.get(m, 0.0) + tot_mes2.get(m, 0.0) for m in meses_uso}
        despesas_mes = tot_mes3

        saldo_inicial = None
        m_ano = re.search(r"(\d{4})", str(titulo_periodo))
        if m_ano and meses_uso:
            ano_periodo = int(m_ano.group(1))
            cur.execute("SELECT valor FROM saldos_iniciais "
                        "WHERE condominio_id = %s AND mes = %s AND ano = %s",
                        (condominio_id, meses_uso[0], ano_periodo))
            r = cur.fetchone()
            if r:
                saldo_inicial = float(r["valor"])
        if saldo_inicial is None:
            saldo_inicial = float(saldo_anterior)

        saldo_ant = {}
        saldo_acum = {}
        acum = saldo_inicial
        for m in meses_uso:
            saldo_ant[m] = acum
            acum = acum + receitas_mes[m] - despesas_mes[m]
            saldo_acum[m] = acum

        linhas4 = []
        valores4 = {
            "Saldo anterior": saldo_ant,
            "(+) Receitas": receitas_mes,
            "(\u2212) Despesas": despesas_mes,
            "(=) Saldo do mês": {m: receitas_mes[m] - despesas_mes[m] for m in meses_uso},
            "Saldo acumulado": saldo_acum,
        }
        for nome, vals in valores4.items():
            linhas4.append([cel(nome)]
                           + [fmt_num(vals[m]) for m in meses_uso]
                           + [fmt_num(sum(vals[m] for m in meses_uso))])
        elementos.append(Paragraph("<b>4) Consolidação</b>", estilos["Heading2"]))
        elementos.append(montar_tabela(["Rubrica"] + cab_meses + ["Total"], linhas4))
        elementos.append(Spacer(1, 8))

    else:
        # ===== MENSAL — modelo estruturado =====
        # 1) Receitas — Taxa de Condomínio/Garagem
        cur.execute(f"SELECT a.numero, a.bloco, l.categoria, l.valor "
                    f"FROM lancamentos l "
                    f"LEFT JOIN apartamentos a ON a.id = l.apartamento_id "
                    f"WHERE l.condominio_id = %s AND l.tipo = 'receita' "
                    f"AND l.apartamento_id IS NOT NULL AND {filtro_data} "
                    f"ORDER BY a.numero", (condominio_id, *params_data))
        rows1 = cur.fetchall()
        linhas1 = []
        tot1 = 0.0
        for r in rows1:
            apto_txt = (f"{r['numero']}" + (f" - Bloco {r['bloco']}" if r["bloco"] else ""))
            linhas1.append([cel(apto_txt), cel(r["categoria"]), fmt_num(r["valor"])])
            tot1 += float(r["valor"])
        if linhas1:
            elementos.append(Paragraph("<b>1) Receitas — Taxa de Condomínio/Garagem</b>",
                                       estilos["Heading2"]))
            elementos.append(montar_tabela(["Apartamento", "Categoria", "Valor"],
                                           linhas1, ["Total", "", fmt_num(tot1)],
                                           largs=[150, 220, 90]))
            elementos.append(Spacer(1, 8))

        # 2) Outras Receitas
        cur.execute(f"SELECT l.categoria, l.descricao, l.valor "
                    f"FROM lancamentos l "
                    f"WHERE l.condominio_id = %s AND l.tipo = 'receita' "
                    f"AND l.apartamento_id IS NULL AND {filtro_data} "
                    f"ORDER BY l.categoria", (condominio_id, *params_data))
        rows2 = cur.fetchall()
        linhas2 = []
        tot2 = 0.0
        for r in rows2:
            linhas2.append([cel(r["categoria"]), cel(r["descricao"] or "—"), fmt_num(r["valor"])])
            tot2 += float(r["valor"])
        if linhas2:
            elementos.append(Paragraph("<b>2) Outras Receitas</b>", estilos["Heading2"]))
            elementos.append(montar_tabela(["Categoria", "Descrição", "Valor"],
                                           linhas2, ["Total", "", fmt_num(tot2)],
                                           largs=[150, 220, 90]))
            elementos.append(Spacer(1, 8))

        # 3) Resumo das Receitas
        elementos.append(Paragraph("<b>3) Resumo das Receitas</b>", estilos["Heading2"]))
        linhas3 = [
            [cel("Receita Taxa de Condomínio/Garagem"), fmt_num(tot1)],
            [cel("Outras Receitas"), fmt_num(tot2)],
            [cel("Total das Receitas", True), fmt_num(tot1 + tot2)],
        ]
        t3 = Table(linhas3, colWidths=[260, 120])
        t3.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#e8f5e9")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ]))
        elementos.append(t3)
        elementos.append(Spacer(1, 8))

        # 4) Despesas
        cur.execute(f"SELECT l.categoria, l.descricao, l.valor "
                    f"FROM lancamentos l "
                    f"WHERE l.condominio_id = %s AND l.tipo = 'despesa' "
                    f"AND {filtro_data} ORDER BY l.categoria", (condominio_id, *params_data))
        rows4 = cur.fetchall()
        linhas4 = []
        tot4 = 0.0
        for r in rows4:
            linhas4.append([cel(r["categoria"]), cel(r["descricao"] or "—"), fmt_num(r["valor"])])
            tot4 += float(r["valor"])
        if linhas4:
            elementos.append(Paragraph("<b>4) Despesas</b>", estilos["Heading2"]))
            elementos.append(montar_tabela(["Categoria", "Descrição", "Valor"],
                                           linhas4, ["Total", "", fmt_num(tot4)],
                                           largs=[150, 220, 90]))
            elementos.append(Spacer(1, 8))

    # ===== 5) Resumo do período (comum) =====
    elementos.append(Paragraph("<b>5) Resumo do período</b>", estilos["Heading2"]))
    dados_res = [
        [cel("Rubrica", True), cel("Valor", True)],
        [cel("Saldo do mês anterior"), f"R$ {fmt_br(saldo_anterior)}"],
        [cel("(+) Receitas"), f"R$ {fmt_br(total_receitas)}"],
        [cel("(\u2212) Despesas"), f"R$ {fmt_br(total_despesas)}"],
        [cel("(=) Saldo do mês"), f"R$ {fmt_br(saldo_periodo)}"],
        [cel("Saldo atual"), f"R$ {fmt_br(saldo_atual)}"],
    ]
    t_res = Table(dados_res, colWidths=[260, 160])
    t_res.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3a5f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#eef4fb")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))
    elementos.append(t_res)
    elementos.append(Spacer(1, 8))

    # ===== 6) Distribuição do saldo por conta (comum) =====
    elementos.append(Paragraph("<b>6) Distribuição do saldo por conta</b>", estilos["Heading2"]))
    cur.execute("SELECT banco, tipo, agencia, numero_conta, saldo "
                "FROM contas_bancarias WHERE condominio_id = %s ORDER BY banco",
                (condominio_id,))
    contas = cur.fetchall()
    if contas:
        dados_contas = [[cel("Banco", True), cel("Tipo", True),
                         cel("Agência / Conta", True), cel("Saldo", True)]]
        tot_contas = 0.0
        for c in contas:
            ag_cc = (f"{c['agencia'] or ''} / {c['numero_conta'] or ''}"
                     if (c["agencia"] or c["numero_conta"]) else "—")
            dados_contas.append([cel(c["banco"]), cel(c["tipo"]), cel(ag_cc),
                                 f"R$ {fmt_br(c['saldo'])}"])
            tot_contas += float(c["saldo"] or 0)
        dados_contas.append([cel("Total distribuído em contas", True),
                             cel("", True), cel("", True),
                             f"R$ {fmt_br(tot_contas)}"])
        t_contas = Table(dados_contas, colWidths=[160, 90, 170, 120])
        t_contas.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3a5f")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#eef4fb")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("ALIGN", (3, 1), (3, -1), "RIGHT"),
        ]))
        elementos.append(t_contas)
    else:
        elementos.append(Paragraph("Nenhuma conta bancária cadastrada.", estilos["Normal"]))
    elementos.append(Spacer(1, 10))

    # ===== Rodapé =====
    elementos.append(Paragraph(f"Emitido em {datetime.now().strftime('%d/%m/%Y')}",
                               estilos["Normal"]))

    doc.build(elementos)
    with open(pdf_path, "rb") as f:
        st.download_button("💾 Baixar prestacao_contas.pdf", f.read(),
                           file_name="prestacao_contas.pdf", mime="application/pdf")
    registrar_auditoria(cur, "prestacao_contas", None, "INSERT",
                        f"Exportação PDF do relatório {titulo_periodo}")
    conn.commit()

    
def gerar_excel_prestacao(cur, conn, condominio_id, filtro_data, params_data,
                          saldo_anterior, total_receitas, total_despesas,
                          saldo_periodo, saldo_atual, titulo_doc, nome_sel,
                          titulo_periodo):
    """Gera o Excel da prestação de contas seguindo o modelo (mensal ou anual)."""
    import re
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
             "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    eh_anual = "ano" in str(titulo_periodo).lower()

    def chave_apto(numero, bloco):
        try:
            num_key = (0, int(numero))
        except (TypeError, ValueError):
            num_key = (1, str(numero or ""))
        return (num_key, str(bloco or ""))

    wb = Workbook()
    wb.remove(wb.active)
    thin = Side(style="thin", color="BBBBBB")
    borda = Border(top=thin, bottom=thin, left=thin, right=thin)
    titulo_aba = f"{nome_sel} — {titulo_periodo}"

    def add_sheet(nome_aba, colunas, linhas, negrito_ultima_linha=True):
        ws = wb.create_sheet(nome_aba)
        ncols = max(len(colunas), 1)
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncols)
        c = ws.cell(row=1, column=1, value=titulo_aba)
        c.font = Font(bold=True, size=13, color="1F3A5F")
        c.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 24
        ws.append(colunas)
        for j in range(1, len(colunas) + 1):
            cell = ws.cell(row=2, column=j)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="1F3A5F")
            cell.alignment = Alignment(horizontal="center", vertical="center")
        for i, linha in enumerate(linhas):
            ws.append([linha.get(col) for col in colunas])
            if negrito_ultima_linha and i == len(linhas) - 1:
                for j in range(1, len(colunas) + 1):
                    ws.cell(row=ws.max_row, column=j).font = Font(bold=True)
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row,
                                min_col=1, max_col=len(colunas)):
            for cell in row:
                cell.border = borda
        ws.freeze_panes = "A3"
        for j in range(1, len(colunas) + 1):
            letra = get_column_letter(j)
            maxlen = 10
            for row in ws.iter_rows(min_row=3, max_row=ws.max_row,
                                    min_col=j, max_col=j):
                for cell in row:
                    v = cell.value
                    if v is not None and len(str(v)) > maxlen:
                        maxlen = len(str(v))
            ws.column_dimensions[letra].width = min(maxlen + 2, 40)
        return ws

    if eh_anual:
        cur.execute(f"SELECT DISTINCT EXTRACT(MONTH FROM l.data_lancamento) AS mes "
                    f"FROM lancamentos l WHERE l.condominio_id = %s AND {filtro_data} "
                    f"ORDER BY mes", (condominio_id, *params_data))
        meses_dados = sorted(int(r["mes"]) for r in cur.fetchall())
        meses_uso = list(range(1, 13)) if meses_dados else []
        cab_meses = [MESES[m - 1] for m in meses_uso]

        cur.execute(f"SELECT a.numero, a.bloco, "
                    f"EXTRACT(MONTH FROM l.data_lancamento) AS mes, SUM(l.valor) AS total "
                    f"FROM lancamentos l "
                    f"LEFT JOIN apartamentos a ON a.id = l.apartamento_id "
                    f"WHERE l.condominio_id = %s AND l.tipo = 'receita' "
                    f"AND l.apartamento_id IS NOT NULL AND {filtro_data} "
                    f"GROUP BY a.numero, a.bloco, EXTRACT(MONTH FROM l.data_lancamento)",
                    (condominio_id, *params_data))
        por_apto = {}
        tot_mes1 = {m: 0.0 for m in meses_uso}
        for r in cur.fetchall():
            chave = chave_apto(r["numero"], r["bloco"])
            if chave not in por_apto:
                por_apto[chave] = {m: 0.0 for m in meses_uso}
                por_apto[chave]["_rotulo"] = (f"{r['numero']}"
                                              + (f" - Bloco {r['bloco']}" if r["bloco"] else ""))
            por_apto[chave][int(r["mes"])] += float(r["total"])
            tot_mes1[int(r["mes"])] += float(r["total"])

        linhas1 = []
        for chave in sorted(por_apto.keys()):
            vals = por_apto[chave]
            linha = {"Apartamento": vals["_rotulo"]}
            for m in meses_uso:
                linha[MESES[m - 1]] = vals[m] if vals[m] else None
            linha["Total"] = sum(vals[m] for m in meses_uso)
            linhas1.append(linha)
        if linhas1:
            linha_tot = {"Apartamento": "Total"}
            for m in meses_uso:
                linha_tot[MESES[m - 1]] = tot_mes1[m] if tot_mes1[m] else None
            linha_tot["Total"] = sum(tot_mes1.values())
            linhas1.append(linha_tot)
            add_sheet("Receitas por Apartamento",
                      ["Apartamento"] + cab_meses + ["Total"], linhas1)

        cur.execute(f"SELECT COALESCE(NULLIF(l.descricao, ''), l.categoria) AS nome, "
                    f"EXTRACT(MONTH FROM l.data_lancamento) AS mes, SUM(l.valor) AS total "
                    f"FROM lancamentos l "
                    f"WHERE l.condominio_id = %s AND l.tipo = 'receita' "
                    f"AND l.apartamento_id IS NULL AND {filtro_data} "
                    f"GROUP BY nome, EXTRACT(MONTH FROM l.data_lancamento)",
                    (condominio_id, *params_data))
        por_outras = {}
        tot_mes2 = {m: 0.0 for m in meses_uso}
        for r in cur.fetchall():
            nome = r["nome"] or "—"
            if nome not in por_outras:
                por_outras[nome] = {m: 0.0 for m in meses_uso}
            por_outras[nome][int(r["mes"])] += float(r["total"])
            tot_mes2[int(r["mes"])] += float(r["total"])

        linhas2 = []
        for nome in sorted(por_outras.keys()):
            vals = por_outras[nome]
            linha = {"Descrição": nome}
            for m in meses_uso:
                linha[MESES[m - 1]] = vals[m] if vals[m] else None
            linha["Total"] = sum(vals[m] for m in meses_uso)
            linhas2.append(linha)
        if linhas2:
            linha_tot = {"Descrição": "Total"}
            for m in meses_uso:
                linha_tot[MESES[m - 1]] = tot_mes2[m] if tot_mes2[m] else None
            linha_tot["Total"] = sum(tot_mes2.values())
            linhas2.append(linha_tot)
            add_sheet("Outras Receitas", ["Descrição"] + cab_meses + ["Total"], linhas2)

        cur.execute(f"SELECT l.categoria AS nome, "
                    f"EXTRACT(MONTH FROM l.data_lancamento) AS mes, SUM(l.valor) AS total "
                    f"FROM lancamentos l "
                    f"WHERE l.condominio_id = %s AND l.tipo = 'despesa' "
                    f"AND {filtro_data} "
                    f"GROUP BY l.categoria, EXTRACT(MONTH FROM l.data_lancamento)",
                    (condominio_id, *params_data))
        por_dep = {}
        tot_mes3 = {m: 0.0 for m in meses_uso}
        for r in cur.fetchall():
            nome = r["nome"] or "—"
            if nome not in por_dep:
                por_dep[nome] = {m: 0.0 for m in meses_uso}
            por_dep[nome][int(r["mes"])] += float(r["total"])
            tot_mes3[int(r["mes"])] += float(r["total"])

        linhas3 = []
        for nome in sorted(por_dep.keys()):
            vals = por_dep[nome]
            linha = {"Categoria": nome}
            for m in meses_uso:
                linha[MESES[m - 1]] = vals[m] if vals[m] else None
            linha["Total"] = sum(vals[m] for m in meses_uso)
            linhas3.append(linha)
        if linhas3:
            linha_tot = {"Categoria": "Total"}
            for m in meses_uso:
                linha_tot[MESES[m - 1]] = tot_mes3[m] if tot_mes3[m] else None
            linha_tot["Total"] = sum(tot_mes3.values())
            linhas3.append(linha_tot)
            add_sheet("Despesas", ["Categoria"] + cab_meses + ["Total"], linhas3)

        receitas_mes = {m: tot_mes1.get(m, 0.0) + tot_mes2.get(m, 0.0) for m in meses_uso}
        despesas_mes = tot_mes3
        saldo_inicial = None
        m_ano = re.search(r"(\d{4})", str(titulo_periodo))
        if m_ano and meses_uso:
            ano_periodo = int(m_ano.group(1))
            cur.execute("SELECT valor FROM saldos_iniciais "
                        "WHERE condominio_id = %s AND mes = %s AND ano = %s",
                        (condominio_id, meses_uso[0], ano_periodo))
            r = cur.fetchone()
            if r:
                saldo_inicial = float(r["valor"])
        if saldo_inicial is None:
            saldo_inicial = float(saldo_anterior)

        saldo_ant = {}
        saldo_acum = {}
        acum = saldo_inicial
        for m in meses_uso:
            saldo_ant[m] = acum
            acum = acum + receitas_mes[m] - despesas_mes[m]
            saldo_acum[m] = acum

        valores4 = {
            "Saldo anterior": saldo_ant,
            "(+) Receitas": receitas_mes,
            "(\u2212) Despesas": despesas_mes,
            "(=) Saldo do mês": {m: receitas_mes[m] - despesas_mes[m] for m in meses_uso},
            "Saldo acumulado": saldo_acum,
        }
        linhas4 = []
        for nome, vals in valores4.items():
            linha = {"Rubrica": nome}
            for m in meses_uso:
                linha[MESES[m - 1]] = vals[m]
            linha["Total"] = sum(vals[m] for m in meses_uso)
            linhas4.append(linha)
        add_sheet("Consolidação", ["Rubrica"] + cab_meses + ["Total"], linhas4)

    else:
        cur.execute(f"SELECT a.numero, a.bloco, l.categoria, l.valor "
                    f"FROM lancamentos l "
                    f"LEFT JOIN apartamentos a ON a.id = l.apartamento_id "
                    f"WHERE l.condominio_id = %s AND l.tipo = 'receita' "
                    f"AND l.apartamento_id IS NOT NULL AND {filtro_data} "
                    f"ORDER BY a.numero", (condominio_id, *params_data))
        linhas1 = []
        tot1 = 0.0
        for r in cur.fetchall():
            apto_txt = (f"{r['numero']}" + (f" - Bloco {r['bloco']}" if r["bloco"] else ""))
            linhas1.append({"Apartamento": apto_txt, "Categoria": r["categoria"],
                            "Valor": float(r["valor"])})
            tot1 += float(r["valor"])
        if linhas1:
            linhas1.append({"Apartamento": "Total", "Categoria": "", "Valor": tot1})
            add_sheet("Receitas", ["Apartamento", "Categoria", "Valor"], linhas1)

        cur.execute(f"SELECT l.categoria, l.descricao, l.valor "
                    f"FROM lancamentos l "
                    f"WHERE l.condominio_id = %s AND l.tipo = 'receita' "
                    f"AND l.apartamento_id IS NULL AND {filtro_data} "
                    f"ORDER BY l.categoria", (condominio_id, *params_data))
        linhas2 = []
        tot2 = 0.0
        for r in cur.fetchall():
            linhas2.append({"Categoria": r["categoria"], "Descrição": r["descricao"] or "",
                            "Valor": float(r["valor"])})
            tot2 += float(r["valor"])
        if linhas2:
            linhas2.append({"Categoria": "Total", "Descrição": "", "Valor": tot2})
            add_sheet("Outras Receitas", ["Categoria", "Descrição", "Valor"], linhas2)

        linhas3 = [
            {"Rubrica": "Receita Taxa de Condomínio/Garagem", "Valor": tot1},
            {"Rubrica": "Outras Receitas", "Valor": tot2},
            {"Rubrica": "Total das Receitas", "Valor": tot1 + tot2},
        ]
        add_sheet("Resumo das Receitas", ["Rubrica", "Valor"], linhas3)

        cur.execute(f"SELECT l.categoria, l.descricao, l.valor "
                    f"FROM lancamentos l "
                    f"WHERE l.condominio_id = %s AND l.tipo = 'despesa' "
                    f"AND {filtro_data} ORDER BY l.categoria", (condominio_id, *params_data))
        linhas4 = []
        tot4 = 0.0
        for r in cur.fetchall():
            linhas4.append({"Categoria": r["categoria"], "Descrição": r["descricao"] or "",
                            "Valor": float(r["valor"])})
            tot4 += float(r["valor"])
        if linhas4:
            linhas4.append({"Categoria": "Total", "Descrição": "", "Valor": tot4})
            add_sheet("Despesas", ["Categoria", "Descrição", "Valor"], linhas4)

    linhas5 = [
        {"Rubrica": "Saldo do mês anterior", "Valor": saldo_anterior},
        {"Rubrica": "(+) Receitas", "Valor": total_receitas},
        {"Rubrica": "(\u2212) Despesas", "Valor": total_despesas},
        {"Rubrica": "(=) Saldo do mês", "Valor": saldo_periodo},
        {"Rubrica": "Saldo atual", "Valor": saldo_atual},
    ]
    add_sheet("Resumo do período", ["Rubrica", "Valor"], linhas5)

    cur.execute("SELECT banco, tipo, agencia, numero_conta, saldo "
                "FROM contas_bancarias WHERE condominio_id = %s ORDER BY banco",
                (condominio_id,))
    contas = cur.fetchall()
    linhas6 = []
    tot_contas = 0.0
    for c in contas:
        ag_cc = (f"{c['agencia'] or ''} / {c['numero_conta'] or ''}"
                 if (c["agencia"] or c["numero_conta"]) else "—")
        linhas6.append({"Banco": c["banco"], "Tipo": c["tipo"],
                        "Agência / Conta": ag_cc, "Saldo": float(c["saldo"] or 0)})
        tot_contas += float(c["saldo"] or 0)
    if linhas6:
        linhas6.append({"Banco": "Total distribuído em contas", "Tipo": "",
                        "Agência / Conta": "", "Saldo": tot_contas})
        add_sheet("Distribuição por Conta", ["Banco", "Tipo", "Agência / Conta", "Saldo"],
                  linhas6)

    caminho = "prestacao_contas.xlsx"
    wb.save(caminho)
    with open(caminho, "rb") as f:
        st.download_button(
            "💾 Baixar prestacao_contas.xlsx", f.read(),
            file_name="prestacao_contas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    registrar_auditoria(cur, "prestacao_contas", None, "INSERT",
                        f"Exportação Excel do relatório {titulo_periodo}")
    conn.commit()    


# ===== ESTADO DA SESSÃO =====
if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = None

def hash_senha(senha):
    """Gera o hash SHA-256 da senha (padrão único do sistema)."""
    return hashlib.sha256(senha.encode()).hexdigest()

def verificar_login(usuario_input, senha_input):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, usuario, senha, nome, perfil, condominio_id, ativo "
        "FROM usuarios WHERE usuario = %s",
        (usuario_input,),
    )
    row = cur.fetchone()
    cur.close(); conn.close()

    if row is None or not row["ativo"]:
        return None

    senha_armazenada = row["senha"] or ""
    perfil = row["perfil"] or "master"
    condominio_id = row["condominio_id"]

    # 1) bcrypt — hash antigo de 60 caracteres ($2b$...)
    if senha_armazenada.startswith("$2") and len(senha_armazenada) == 60:
        try:
            import bcrypt
            if bcrypt.checkpw(senha_input.encode(), senha_armazenada.encode()):
                return {"id": row["id"], "nome": row["nome"], "perfil": perfil, "condominio_id": condominio_id}
        except Exception:
            pass
        return None

    # 2) SHA-256 — padrão atual do app (64 caracteres hexadecimais)
    if len(senha_armazenada) == 64:
        if hashlib.sha256(senha_input.encode()).hexdigest() == senha_armazenada:
            return {"id": row["id"], "nome": row["nome"], "perfil": perfil, "condominio_id": condominio_id}
        return None

    # 3) Texto puro — ajuste manual feito no pgAdmin
    if senha_input == senha_armazenada:
        return {"id": row["id"], "nome": row["nome"], "perfil": perfil, "condominio_id": condominio_id}
    return None

# ===== Migração: coluna logo =====
try:
    _conn_mig = get_connection()
    garantir_coluna_logo(_conn_mig)
    _conn_mig.close()
except Exception:
    pass

# ===== LOGIN =====
if not st.session_state.logado:
    if os.path.exists(LOGO):
        try:
            with open(LOGO, "rb") as f:
                logo_b64 = base64.b64encode(f.read()).decode()
            mime = "image/jpeg" if LOGO.lower().endswith((".jpg", ".jpeg")) else "image/png"
            st.markdown(f'<div style="text-align:center; padding-top:20px;"><img src="data:{mime};base64,{logo_b64}" width="180"></div>',
                        unsafe_allow_html=True)
        except Exception:
            pass
    st.markdown('<h1 style="text-align:center; color:#1f3a5f;">🏢 Gestão de Condomínios</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#6b7280;">Versão 3.0 Set26</p>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        with st.form("login_form"):
            usuario_input = st.text_input("Usuário")
            senha_input = st.text_input("Senha", type="password")
            entrar = st.form_submit_button("Entrar")
        if entrar:
            if not usuario_input.strip() or not senha_input:
                st.error("Informe usuário e senha.")
            else:
                user = verificar_login(usuario_input.strip(), senha_input)
                if user:
                    st.session_state.logado = True
                    st.session_state.usuario = user["nome"]
                    st.session_state.usuario_id = user["id"]
                    st.session_state.perfil = user["perfil"]
                    st.session_state.condominio_id = user["condominio_id"]
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos.")
    st.stop()

usuario = st.session_state.usuario
perfil_atual = st.session_state.get("perfil", "master")
condominio_fixo = st.session_state.get("condominio_id")

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown(
        '<div style="background:linear-gradient(90deg,#1f3a5f,#2e5a8a); color:#fff; padding:14px 12px; '
        'border-radius:12px; text-align:center; margin-bottom:8px; box-shadow:0 3px 8px rgba(31,58,95,.3);">'
        '<span style="font-size:1.05rem; font-weight:700;">🏢 Gestão de Condomínios</span></div>',
        unsafe_allow_html=True,
    )
    if os.path.exists(LOGO):
        try:
            st.image(LOGO, width=140)
        except Exception:
            pass
    st.markdown(
        f'<div style="background:#ffffff; border:2px solid #c9d4e3; border-left:6px solid #f0b429; '
        f'border-radius:10px; padding:8px 12px; color:#1f3a5f; font-weight:700; margin-bottom:6px;">👤 {usuario}</div>',
        unsafe_allow_html=True,
    )

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nome FROM condominios ORDER BY nome")
    condominios = cur.fetchall()
    cur.close(); conn.close()
    opcoes = {c["nome"]: c["id"] for c in condominios}
    nome_sel = ""

    if perfil_atual == "master":
        if opcoes:
            nome_sel = st.selectbox("🏢 Condomínio", list(opcoes.keys()), key="cond_sel")
            condominio_id = opcoes[nome_sel]
        else:
            condominio_id = None
            st.info("Nenhum condomínio cadastrado.")
    else:
        if condominio_fixo and condominio_fixo in opcoes.values():
            nome_sel = next(n for n, i in opcoes.items() if i == condominio_fixo)
            st.selectbox("🏢 Condomínio", [nome_sel], disabled=True, key="cond_fixo")
            condominio_id = condominio_fixo
        else:
            condominio_id = None
            st.warning("Seu usuário não está vinculado a um condomínio. Fale com o Master.")

    ICONES_SECOES = {
        "Dashboard": "📊 Dashboard",
        "Gestão Pessoal": "👥 Gestão Pessoal",
        "Gestão Financeira": "💰 Gestão Financeira",
        "Comunicação": "📧 Comunicação",
        "Usuários": "👥 Usuários",
        "Auditoria": "🔍 Auditoria",
    }
    ICONES_MODULOS = {
        "Condomínio": "🏢 Condomínio",
        "Apartamentos": "🔑 Apartamentos",
        "Empregadas": "👩‍💼 Funcionárias",
        "Lançamentos": "💰 Lançamentos",
        "Inadimplência": "📋 Inadimplência",
        "Bancos": "🏦 Bancos",
        "Prestação de Contas": "📑 Prestação de Contas",
    }

    secoes = ["Dashboard", "Gestão Pessoal", "Gestão Financeira", "Comunicação"]
    if perfil_atual == "master":
        secoes.append("Usuários")
        secoes.append("Auditoria")

    st.markdown("**Navegação**")
    secao = st.radio("Seção", secoes,
                     format_func=lambda x: ICONES_SECOES.get(x, x),
                     label_visibility="collapsed", key="menu_secao")

    if secao == "Gestão Pessoal":
        st.markdown('<div style="font-size:0.75rem; color:#6b7280; margin:6px 0 2px 20px; font-weight:600;">MÓDULOS</div>',
                    unsafe_allow_html=True)
        modulos_pessoal = ["Condomínio", "Apartamentos", "Empregadas"]
        if perfil_atual != "master":
            modulos_pessoal = ["Apartamentos", "Empregadas"]
        pagina = st.radio("Módulos", modulos_pessoal,
                          format_func=lambda x: ICONES_MODULOS.get(x, x),
                          label_visibility="collapsed", key="mod_pessoal")
    elif secao == "Gestão Financeira":
        st.markdown('<div style="font-size:0.75rem; color:#6b7280; margin:6px 0 2px 20px; font-weight:600;">MÓDULOS</div>',
                    unsafe_allow_html=True)
        pagina = st.radio("Módulos", ["Lançamentos", "Inadimplência", "Bancos", "Prestação de Contas"],
                          format_func=lambda x: ICONES_MODULOS.get(x, x),
                          label_visibility="collapsed", key="mod_financeiro")
    else:
        pagina = secao

    st.markdown("---")
    if st.button("🚪 Sair"):
        st.session_state.logado = False
        st.session_state.usuario = None
        for chave in ("perfil", "condominio_id", "usuario_id"):
            st.session_state.pop(chave, None)
        st.rerun()

# ===== DASHBOARD =====
if pagina == "Dashboard":
    banner(f"📊 Dashboard — {nome_sel or '—'}", "azul")
    if condominio_id is None:
        st.warning("Nenhum condomínio cadastrado ainda. Cadastre um em 'Condomínio' para começar.")
    else:
        hoje = date.today()
        c_m, c_a = st.columns(2)
        with c_m:
            mes_sel = st.selectbox("Selecione o mês", list(range(1, 13)),
                                   format_func=lambda m: MESES_NOMES[m - 1],
                                   index=hoje.month - 1, key="dash_mes")
        with c_a:
            anos = list(range(2028, 2024, -1))
            idx_ano = anos.index(hoje.year) if hoje.year in anos else 0
            ano_sel = st.selectbox("Selecione o ano", anos, index=idx_ano, key="dash_ano")

        conn = get_connection(); cur = conn.cursor()
        cur.execute("SELECT COALESCE(SUM(valor) FILTER (WHERE tipo='receita'),0) AS receitas, "
                    "COALESCE(SUM(valor) FILTER (WHERE tipo='despesa'),0) AS despesas "
                    "FROM lancamentos WHERE condominio_id=%s "
                    "AND EXTRACT(MONTH FROM data_lancamento)=%s AND EXTRACT(YEAR FROM data_lancamento)=%s",
                    (condominio_id, mes_sel, ano_sel))
        t = cur.fetchone()
        receitas_mes, despesas_mes = float(t["receitas"]), float(t["despesas"])
        cur.execute("SELECT COALESCE(SUM(valor) FILTER (WHERE tipo='receita'),0) AS receitas, "
                    "COALESCE(SUM(valor) FILTER (WHERE tipo='despesa'),0) AS despesas "
                    "FROM lancamentos WHERE condominio_id=%s AND EXTRACT(YEAR FROM data_lancamento)=%s",
                    (condominio_id, ano_sel))
        ta = cur.fetchone()
        receitas_ano, despesas_ano = float(ta["receitas"]), float(ta["despesas"])
        cur.execute("SELECT COALESCE(SUM(saldo),0) AS total FROM contas_bancarias WHERE condominio_id=%s", (condominio_id,))
        total_contas = float(cur.fetchone()["total"])
        cur.execute("SELECT COUNT(*) AS total FROM apartamentos WHERE condominio_id=%s", (condominio_id,))
        n_aptos = cur.fetchone()["total"]
        cur.close(); conn.close()

        st.markdown(f'<div class="caixa"><b>📅 Painel do mês — {MESES_NOMES[mes_sel - 1]}/{ano_sel}</b></div>',
                    unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: card("Receitas do mês", f"R$ {fmt_br(receitas_mes)}", "receita")
        with c2: card("Despesas do mês", f"R$ {fmt_br(despesas_mes)}", "despesa")
        with c3: card("Saldo do mês", f"R$ {fmt_br(receitas_mes - despesas_mes)}", "saldo")

        st.markdown(f'<div class="caixa"><b>📆 Acumulado do ano — {ano_sel}</b></div>', unsafe_allow_html=True)
        c4, c5, c6 = st.columns(3)
        with c4: card("Receitas acumuladas", f"R$ {fmt_br(receitas_ano)}", "receita")
        with c5: card("Despesas acumuladas", f"R$ {fmt_br(despesas_ano)}", "despesa")
        with c6: card("Saldo acumulado", f"R$ {fmt_br(receitas_ano - despesas_ano)}", "saldo")

        st.markdown(f'<div class="caixa">🏦 Total em contas: <b>R$ {fmt_br(total_contas)}</b> &nbsp;|&nbsp; '
                    f'🏠 Apartamentos cadastrados: <b>{n_aptos}</b></div>', unsafe_allow_html=True)

        # ===== CONDOMÍNIO =====

        if perfil_atual != "master":
            st.warning("🔒 Acesso restrito ao usuário Master.")
        st.stop()

elif pagina == "Condomínio":
    if perfil_atual != "master":
        st.warning("🔒 Acesso restrito ao usuário Master.")
        st.stop()
    banner("🏢 Condomínio", "verde")
    conn = get_connection(); cur = conn.cursor()
    with st.form("novo_condominio"):
        st.subheader("Cadastrar novo condomínio")
        nome = st.text_input("Nome do condomínio *")
        cnpj = st.text_input("CNPJ")
        endereco = st.text_input("Endereço")
        cidade = st.text_input("Cidade")
        uf = st.text_input("UF", max_chars=2)
        st.markdown("---")
        st.subheader("📧 E-mail de comunicação")
        email_com = st.text_input("E-mail de comunicação *",
                                  placeholder="ex.: comunicados@seucondominio.com.br",
                                  help="Este e-mail será o remetente dos comunicados no módulo Comunicação.")
        senha_com = st.text_input("Senha do e-mail *", type="password",
                                  help="Senha ou senha de aplicativo (app password) do e-mail acima.")
        salvar = st.form_submit_button("Salvar condomínio")
    if salvar:
        if not nome.strip():
            st.error("O nome do condomínio é obrigatório.")
        elif not email_com.strip() or not senha_com:
            st.error("Informe o e-mail de comunicação e a senha.")
        else:
            try:
                cur.execute("INSERT INTO condominios (nome, cnpj, endereco, cidade, uf, email, senha_email) "
                            "VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
                            (nome.strip(), cnpj.strip() or None, endereco.strip() or None,
                             cidade.strip() or None, uf.strip().upper() or None,
                             email_com.strip(), senha_com))
                novo_id = cur.fetchone()["id"]
                registrar_auditoria(cur, "condominios", novo_id, "INSERT", f"Condomínio '{nome.strip()}' criado")
                conn.commit()
                st.success(f"Condomínio '{nome.strip()}' cadastrado com sucesso!")
            except Exception as e:
                conn.rollback()
                st.error(f"Erro ao cadastrar: {e}")
    st.subheader("Condomínios cadastrados")
    cur.execute("SELECT id, nome, cnpj, cidade, uf, email FROM condominios ORDER BY nome")
    conds = cur.fetchall()
    if conds:
        for c in conds:
            email_txt = c["email"] if "email" in c and c["email"] else "sem e-mail de comunicação"
            st.write(f"**{c['nome']}** — CNPJ: {c['cnpj'] or '—'} | {c['cidade'] or ''} {c['uf'] or ''} | 📧 {email_txt}")
    else:
        st.info("Nenhum condomínio cadastrado ainda.")
    cur.close(); conn.close()

# ===== APARTAMENTOS =====
elif pagina == "Apartamentos":
    banner("🔑 Apartamentos", "laranja")
    if condominio_id is None:
        st.warning("Selecione um condomínio na barra lateral antes de cadastrar apartamentos.")
    else:
        conn = get_connection(); cur = conn.cursor()
        parentescos = ["Esposa", "Esposo", "Filho", "Filha", "Sobrinho", "Sobrinha",
                       "Enteado", "Enteada", "Pai", "Mãe", "Avô", "Avó", "Genro", "Nora", "Outro"]

        with st.form("novo_apartamento"):
            st.subheader("1️⃣ Cadastrar apartamento")
            numero = st.text_input("Número *")
            bloco = st.text_input("Bloco")
            proprietario = st.text_input("Proprietário")
            telefone = st.text_input("Telefone")
            email = st.text_input("E-mail")
            st.markdown("---")
            st.subheader("Morador principal")
            proprietario_e_morador = st.checkbox("O proprietário é também o morador?", value=True)
            if proprietario_e_morador:
                st.caption("O morador será preenchido com os dados do proprietário.")
                morador_nome, morador_telefone, morador_email = proprietario, telefone, email
            else:
                st.caption("Preencha os dados do morador (diferente do proprietário).")
                morador_nome = st.text_input("Nome do morador *")
                morador_telefone = st.text_input("Telefone do morador")
                morador_email = st.text_input("E-mail do morador")
            salvar = st.form_submit_button("Salvar apartamento")
        if salvar:
            if not numero.strip():
                st.error("O número do apartamento é obrigatório.")
            elif not morador_nome.strip():
                st.error("O nome do morador é obrigatório.")
            else:
                try:
                    cur.execute("INSERT INTO apartamentos (condominio_id, numero, bloco, proprietario, telefone, email) "
                                "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                                (condominio_id, numero.strip(), bloco.strip() or None,
                                 proprietario.strip() or None, telefone.strip() or None, email.strip() or None))
                    apto_id = cur.fetchone()["id"]
                    cur.execute("INSERT INTO moradores (apartamento_id, nome, parentesco, telefone, email, is_principal) "
                                "VALUES (%s, %s, %s, %s, %s, %s)",
                                (apto_id, morador_nome.strip(),
                                 "Proprietário" if proprietario_e_morador else "Morador",
                                 morador_telefone.strip() or None, morador_email.strip() or None, True))
                    registrar_auditoria(cur, "apartamentos", apto_id, "INSERT",
                                        f"Apartamento {numero.strip()} criado")
                    conn.commit()
                    st.success(f"Apartamento {numero.strip()} cadastrado com sucesso!")
                except Exception as e:
                    conn.rollback(); st.error(f"Erro ao cadastrar: {e}")

        st.markdown("---")
        st.subheader("2️⃣ Cadastrar morador em apartamento existente")
        cur.execute("SELECT id, numero, bloco FROM apartamentos WHERE condominio_id = %s ORDER BY numero", (condominio_id,))
        aptos = cur.fetchall()
        opcoes_apto = {}
        for a in aptos:
            rotulo = f"{a['numero']}" + (f" - Bloco {a['bloco']}" if a["bloco"] else "")
            opcoes_apto[rotulo] = a["id"]
        if opcoes_apto:
            with st.form("novo_morador"):
                apto_rotulo = st.selectbox("Apartamento *", list(opcoes_apto.keys()))
                m_nome = st.text_input("Nome do morador *")
                m_parentesco = st.selectbox("Parentesco", parentescos)
                m_telefone = st.text_input("Telefone")
                m_email = st.text_input("E-mail")
                adicionar = st.form_submit_button("Salvar morador")
            if adicionar:
                if not m_nome.strip():
                    st.error("O nome do morador é obrigatório.")
                else:
                    try:
                        cur.execute("INSERT INTO moradores (apartamento_id, nome, parentesco, telefone, email, is_principal) "
                                    "VALUES (%s, %s, %s, %s, %s, %s)",
                                    (opcoes_apto[apto_rotulo], m_nome.strip(), m_parentesco,
                                     m_telefone.strip() or None, m_email.strip() or None, False))
                        registrar_auditoria(cur, "moradores", None, "INSERT",
                                            f"Morador {m_nome.strip()} no apto {apto_rotulo}")
                        conn.commit()
                        st.success(f"{m_nome.strip()} cadastrado no apartamento {apto_rotulo}!")
                    except Exception as e:
                        conn.rollback(); st.error(f"Erro ao cadastrar: {e}")
        else:
            st.info("Cadastre um apartamento primeiro para poder vincular moradores.")

        st.markdown("---")
        st.subheader("3️⃣ Ficha cadastral do apartamento")
        if opcoes_apto:
            apto_ficha = st.selectbox("Selecione o apartamento para ver a ficha", list(opcoes_apto.keys()), key="apto_ficha_sel")
            apto_id_ficha = opcoes_apto[apto_ficha]
            cur.execute("SELECT id, numero, bloco, proprietario, telefone, email FROM apartamentos WHERE id = %s", (apto_id_ficha,))
            a = cur.fetchone()
            cur.execute("SELECT nome, parentesco, telefone, email, is_principal FROM moradores "
                        "WHERE apartamento_id = %s ORDER BY is_principal DESC, nome", (apto_id_ficha,))
            moradores = cur.fetchall()
            st.markdown('<h3 style="text-align:center;">🏠 Ficha Cadastral</h3>', unsafe_allow_html=True)
            st.markdown(f'<p style="text-align:center; font-weight:bold; color:#1f3a5f;">{nome_sel}</p>', unsafe_allow_html=True)
            bloco_txt_ficha = f" - Bloco {a['bloco']}" if a["bloco"] else ""
            st.markdown(f'<p style="text-align:center;">Apartamento {a["numero"]}{bloco_txt_ficha}</p>', unsafe_allow_html=True)
            st.markdown(f"**Proprietário:** {a['proprietario'] or '—'}")
            st.markdown(f"**Telefone:** {a['telefone'] or '—'} | **E-mail:** {a['email'] or '—'}")
            st.markdown("**Moradores:**")
            if moradores:
                for m in moradores:
                    principal = " 👑 (morador principal)" if m["is_principal"] else ""
                    parentesco_txt = f" ({m['parentesco']})" if m["parentesco"] else ""
                    st.markdown(f"- {m['nome']}{parentesco_txt}{principal} — {m['telefone'] or ''} {m['email'] or ''}")
            else:
                st.markdown("- Nenhum morador cadastrado.")

            cur.execute("SELECT tipo, marca, modelo, placa, cor, ano FROM veiculos "
                        "WHERE apartamento_id = %s ORDER BY id", (apto_id_ficha,))
            veiculos_ficha = cur.fetchall()
            st.markdown("**🚗 Veículos / Motos:**")
            if veiculos_ficha:
                for v in veiculos_ficha:
                    linha_v = f"{v['tipo']} — {v['marca'] or ''} {v['modelo'] or ''}".strip(" —")
                    linha_v += f" | Placa: {v['placa'] or '—'} | Cor: {v['cor'] or '—'} | Ano: {v['ano'] or '—'}"
                    st.markdown(f"- {linha_v}")
            else:
                st.markdown("- Nenhum veículo cadastrado.")

            cur.execute("SELECT tipo, raca, porte, observacao FROM pets "
                        "WHERE apartamento_id = %s ORDER BY id", (apto_id_ficha,))
            pets_ficha = cur.fetchall()
            st.markdown("**🐾 Pets:**")
            if pets_ficha:
                for p in pets_ficha:
                    linha_p = p["tipo"] or ""
                    if p["raca"]:
                        linha_p += f" — {p['raca']}"
                    if p["porte"]:
                        linha_p += f" — porte {p['porte']}"
                    if p["observacao"]:
                        linha_p += f" — {p['observacao']}"
                    st.markdown(f"- {linha_p}")
            else:
                st.markdown("- Nenhum pet cadastrado.")

            cur.execute("SELECT nome, telefone FROM empregadas WHERE apartamento_id = %s ORDER BY nome",
                        (apto_id_ficha,))
            funcs_ficha = cur.fetchall()
            st.markdown("**👩‍💼 Funcionárias do apartamento:**")
            if funcs_ficha:
                for f in funcs_ficha:
                    st.markdown(f"- {f['nome']} — {f['telefone'] or ''}")
            else:
                st.markdown("- Nenhuma funcionária vinculada a este apartamento.")

            if st.button("🖨️ Imprimir ficha cadastral", key="btn_ficha_unica"):
                corpo_ficha = ficha_cadastral_html(
                    cur, apto_id_ficha, a["numero"], a["bloco"],
                    a["proprietario"], a["telefone"], a["email"], nome_sel,
                )
                st.iframe(f"""
                <html><head><meta charset="utf-8"><title>Ficha Cadastral</title></head>
                <body style="font-family:Arial,sans-serif; padding:20px;">
                    {html_logo()}{corpo_ficha}
                    <hr>
                    <p style="text-align:center; font-size:12px;">Emitido em {date.today().strftime('%d/%m/%Y')}</p>
                    <script>window.print();</script>
                </body></html>""", height=700)

            if st.button("🖨️ Imprimir fichas de todos os apartamentos", key="btn_fichas_todas"):
                fichas_html = ""
                for a_item in aptos:
                    cur.execute("SELECT id, numero, bloco, proprietario, telefone, email "
                                "FROM apartamentos WHERE id = %s", (a_item["id"],))
                    a_full = cur.fetchone()
                    corpo_ficha = ficha_cadastral_html(
                        cur, a_full["id"], a_full["numero"], a_full["bloco"],
                        a_full["proprietario"], a_full["telefone"], a_full["email"], nome_sel,
                    )
                    fichas_html += f'<div style="page-break-after: always;">{corpo_ficha}</div>'
                st.iframe(f"""
                <html><head><meta charset="utf-8"><title>Fichas Cadastrais — {nome_sel}</title></head>
                <body style="font-family:Arial,sans-serif; padding:20px;">
                    {html_logo()}
                    <h1 style="text-align:center;">FICHAS CADASTRAIS</h1>
                    <p style="text-align:center; font-weight:bold;">{nome_sel}</p>
                    <p style="text-align:center;">Total de apartamentos: {len(aptos)}</p>
                    <hr>{fichas_html}
                    <p style="text-align:center; font-size:12px;">Emitido em {date.today().strftime('%d/%m/%Y')}</p>
                    <script>window.print();</script>
                </body></html>""", height=700)

        st.markdown("---")
        st.subheader("4️⃣ Editar cadastro do apartamento")
        if opcoes_apto:
            apto_edit = st.selectbox("Selecione o apartamento", list(opcoes_apto.keys()), key="apto_edit_sel")
            apto_id_edit = opcoes_apto[apto_edit]
            cur.execute("SELECT id, numero, bloco, proprietario, telefone, email FROM apartamentos WHERE id = %s", (apto_id_edit,))
            a_edit = cur.fetchone()
            with st.form("editar_apartamento"):
                e_numero = st.text_input("Número", value=a_edit["numero"] or "")
                e_bloco = st.text_input("Bloco", value=a_edit["bloco"] or "")
                e_proprietario = st.text_input("Proprietário", value=a_edit["proprietario"] or "")
                e_telefone = st.text_input("Telefone", value=a_edit["telefone"] or "")
                e_email = st.text_input("E-mail", value=a_edit["email"] or "")
                salvar_a = st.form_submit_button("Salvar dados do apartamento")
            if salvar_a:
                if e_numero.strip():
                    cur.execute("UPDATE apartamentos SET numero=%s, bloco=%s, proprietario=%s, telefone=%s, email=%s WHERE id=%s",
                                (e_numero.strip(), e_bloco.strip() or None, e_proprietario.strip() or None,
                                 e_telefone.strip() or None, e_email.strip() or None, apto_id_edit))
                    registrar_auditoria(cur, "apartamentos", apto_id_edit, "UPDATE",
                                        f"Dados do apto {e_numero.strip()} atualizados")
                    conn.commit(); st.success("Dados do apartamento atualizados!"); st.rerun()
                else:
                    st.error("O número do apartamento é obrigatório.")
            st.subheader("Editar moradores")
            cur.execute("SELECT id, nome, parentesco, telefone, email, is_principal "
                        "FROM moradores WHERE apartamento_id = %s ORDER BY is_principal DESC, nome", (apto_id_edit,))
            moradores_edit = cur.fetchall()
            if moradores_edit:
                for m in moradores_edit:
                    with st.expander(f"{m['nome']} ({m['parentesco'] or 'Morador'})"):
                        with st.form(f"editar_morador_{m['id']}"):
                            e_nome = st.text_input("Nome", value=m["nome"] or "")
                            idx_parentesco = parentescos.index(m["parentesco"]) if m["parentesco"] in parentescos else 0
                            e_parentesco = st.selectbox("Parentesco", parentescos, index=idx_parentesco)
                            e_telefone = st.text_input("Telefone", value=m["telefone"] or "")
                            e_email = st.text_input("E-mail", value=m["email"] or "")
                            salvar_m = st.form_submit_button("Salvar alterações")
                        if salvar_m:
                            if e_nome.strip():
                                cur.execute("UPDATE moradores SET nome=%s, parentesco=%s, telefone=%s, email=%s WHERE id=%s",
                                            (e_nome.strip(), e_parentesco, e_telefone.strip() or None,
                                             e_email.strip() or None, m["id"]))
                                registrar_auditoria(cur, "moradores", m["id"], "UPDATE",
                                                    f"Morador {e_nome.strip()} atualizado")
                                conn.commit(); st.success("Morador atualizado!"); st.rerun()
                            else:
                                st.error("O nome do morador é obrigatório.")
            else:
                st.info("Este apartamento não tem moradores cadastrados.")
        else:
            st.info("Cadastre um apartamento para poder editar.")


                # ===== 5️⃣ VEÍCULOS, PETS E FUNCIONÁRIAS DO APARTAMENTO =====
        st.markdown("---")
        st.subheader("5️⃣ Veículos, pets e funcionárias do apartamento")
        if opcoes_apto:
            apto_vep = st.selectbox("Selecione o apartamento", list(opcoes_apto.keys()), key="vep_apto")
            apto_id_vep = opcoes_apto[apto_vep]

            cur.execute("SELECT id, tipo, marca, modelo, placa, cor, ano FROM veiculos "
                        "WHERE apartamento_id = %s ORDER BY id", (apto_id_vep,))
            veiculos = cur.fetchall()
            st.markdown(f"**🚗 Veículos / motos — {len(veiculos)}/3**")
            if veiculos:
                for v in veiculos:
                    linha_v = f"{v['tipo']} — {v['marca'] or ''} {v['modelo'] or ''}".strip(" —")
                    linha_v += f" | Placa: {v['placa'] or '—'} | Cor: {v['cor'] or '—'} | Ano: {v['ano'] or '—'}"
                    c_v, c_d = st.columns([5, 1])
                    c_v.write(linha_v)
                    if c_d.button("🗑️", key=f"del_vec_{v['id']}"):
                        cur.execute("DELETE FROM veiculos WHERE id = %s", (v["id"],))
                        registrar_auditoria(cur, "veiculos", v["id"], "DELETE", f"Veículo do apto {apto_vep} excluído")
                        conn.commit(); st.success("Veículo excluído."); st.rerun()
            if len(veiculos) < 3:
                with st.form("add_veiculo"):
                    v_tipo = st.selectbox("Tipo", ["Carro", "Moto"])
                    v_marca = st.text_input("Marca *")
                    v_modelo = st.text_input("Modelo *")
                    v_placa = st.text_input("Placa")
                    v_cor = st.text_input("Cor")
                    v_ano = st.number_input("Ano", min_value=1950, max_value=date.today().year + 1,
                                            step=1, value=date.today().year)
                    salvar_v = st.form_submit_button("➕ Adicionar veículo")
                if salvar_v:
                    if not v_marca.strip() or not v_modelo.strip():
                        st.error("Informe marca e modelo do veículo.")
                    else:
                        cur.execute("INSERT INTO veiculos (apartamento_id, tipo, marca, modelo, placa, cor, ano) "
                                    "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                    (apto_id_vep, v_tipo, v_marca.strip(), v_modelo.strip(),
                                     v_placa.strip().upper() or None, v_cor.strip() or None,
                                     int(v_ano) if v_ano else None))
                        registrar_auditoria(cur, "veiculos", None, "INSERT",
                                            f"{v_tipo} {v_marca.strip()} {v_modelo.strip()} no apto {apto_vep}")
                        conn.commit(); st.success("Veículo adicionado!"); st.rerun()
            else:
                st.info("Limite de 3 veículos atingido para este apartamento.")

            st.markdown("---")
            cur.execute("SELECT id, tipo, raca, porte, observacao FROM pets "
                        "WHERE apartamento_id = %s ORDER BY id", (apto_id_vep,))
            pets = cur.fetchall()
            st.markdown(f"**🐾 Pets — {len(pets)}**")
            if pets:
                for p in pets:
                    linha_p = p["tipo"] or ""
                    if p["raca"]:
                        linha_p += f" — {p['raca']}"
                    if p["porte"]:
                        linha_p += f" — porte {p['porte']}"
                    if p["observacao"]:
                        linha_p += f" — {p['observacao']}"
                    c_p, c_d2 = st.columns([5, 1])
                    c_p.write(linha_p)
                    if c_d2.button("🗑️", key=f"del_pet_{p['id']}"):
                        cur.execute("DELETE FROM pets WHERE id = %s", (p["id"],))
                        registrar_auditoria(cur, "pets", p["id"], "DELETE", f"Pet do apto {apto_vep} excluído")
                        conn.commit(); st.success("Pet excluído."); st.rerun()
            with st.form("add_pet"):
                p_tipo = st.selectbox("Tipo de pet *", ["Cão", "Gato", "Outro"])
                p_raca = st.text_input("Raça")
                p_porte = st.selectbox("Porte", ["Pequeno", "Médio", "Grande"])
                p_obs = st.text_input("Observações (se 'Outro', informe qual pet)")
                salvar_p = st.form_submit_button("➕ Adicionar pet")
            if salvar_p:
                if p_tipo == "Outro" and not p_obs.strip():
                    st.error("Para 'Outro', informe qual é o pet no campo Observações.")
                else:
                    cur.execute("INSERT INTO pets (apartamento_id, tipo, raca, porte, observacao) "
                                "VALUES (%s, %s, %s, %s, %s)",
                                (apto_id_vep, p_tipo, p_raca.strip() or None, p_porte, p_obs.strip() or None))
                    registrar_auditoria(cur, "pets", None, "INSERT",
                                        f"Pet {p_tipo} no apto {apto_vep}")
                    conn.commit(); st.success("Pet adicionado!"); st.rerun()

            st.markdown("---")
            cur.execute("SELECT id, nome, cpf, telefone, endereco FROM empregadas "
                        "WHERE apartamento_id = %s ORDER BY nome", (apto_id_vep,))
            funcs_vep = cur.fetchall()
            st.markdown(f"**👩‍💼 Funcionárias do apartamento — {len(funcs_vep)}**")
            if funcs_vep:
                for f in funcs_vep:
                    cpf_txt = f["cpf"] or ""
                    if len(cpf_txt) == 11:
                        cpf_txt = f"{cpf_txt[:3]}.{cpf_txt[3:6]}.{cpf_txt[6:9]}-{cpf_txt[9:]}"
                    with st.expander(f"{f['nome']} — CPF: {cpf_txt} — {f['telefone'] or ''}"):
                        with st.form(f"editar_func_vep_{f['id']}"):
                            e_nome = st.text_input("Nome", value=f["nome"] or "")
                            e_cpf = st.text_input("CPF", value=f["cpf"] or "")
                            e_telefone = st.text_input("Telefone", value=f["telefone"] or "")
                            e_endereco = st.text_input("Endereço", value=f["endereco"] or "")
                            c1, c2 = st.columns(2)
                            salvar_f = c1.form_submit_button("💾 Salvar")
                            excluir_f = c2.form_submit_button("🗑️ Excluir")
                        if salvar_f:
                            cpf_limpo = "".join(filter(str.isdigit, e_cpf))
                            if not e_nome.strip():
                                st.error("O nome é obrigatório.")
                            elif len(cpf_limpo) != 11:
                                st.error("CPF inválido — informe os 11 dígitos.")
                            else:
                                cur.execute("UPDATE empregadas SET nome=%s, cpf=%s, telefone=%s, endereco=%s WHERE id=%s",
                                            (e_nome.strip(), cpf_limpo, e_telefone.strip() or None,
                                             e_endereco.strip() or None, f["id"]))
                                registrar_auditoria(cur, "empregadas", f["id"], "UPDATE",
                                                    f"Funcionária {e_nome.strip()} atualizada")
                                conn.commit(); st.success("Funcionária atualizada!"); st.rerun()
                        if excluir_f:
                            cur.execute("DELETE FROM empregadas WHERE id = %s", (f["id"],))
                            registrar_auditoria(cur, "empregadas", f["id"], "DELETE",
                                                f"Funcionária do apto {apto_vep} excluída")
                            conn.commit(); st.success("Funcionária excluída!"); st.rerun()
            else:
                st.info("Nenhuma funcionária vinculada a este apartamento.")
        else:
            st.info("Cadastre um apartamento antes de registrar veículos, pets e funcionárias.")

        # ===== 6️⃣ IMPORTAR APARTAMENTOS E MORADORES =====
        st.markdown("---")
        st.subheader("6️⃣ Importar apartamentos e moradores de planilha")
        st.caption("Use a planilha modelo (aba 'Apartamentos'). O apartamento é localizado por número + bloco; "
                   "se já existir, os dados do proprietário são atualizados e o morador principal é adicionado.")
        arquivo_imp = st.file_uploader("Planilha de importação (.xlsx)", type=["xlsx", "xls"], key="imp_aptos")
        if arquivo_imp is not None:
            try:
                import pandas as pd
                df = pd.read_excel(arquivo_imp, sheet_name="Apartamentos").fillna("")
                st.write(f"Linhas encontradas na planilha: {len(df)}")
                if st.button("📥 Importar apartamentos e moradores", key="btn_imp_aptos"):
                    importados, erros = 0, []
                    for idx, row in df.iterrows():
                        numero = str(row.get("Número", "")).strip()
                        bloco = str(row.get("Bloco", "")).strip()
                        proprietario = str(row.get("Proprietário", "")).strip()
                        telefone = str(row.get("Telefone", "")).strip()
                        email = str(row.get("E-mail", "")).strip()
                        morador = str(row.get("Morador principal", "")).strip()
                        parentesco = str(row.get("Parentesco", "")).strip() or "Morador"
                        tel_morador = str(row.get("Tel. morador", "")).strip()
                        email_morador = str(row.get("E-mail morador", "")).strip()
                        if not numero:
                            erros.append(f"Linha {idx + 2}: número do apartamento vazio.")
                            continue
                        cur.execute("SELECT id FROM apartamentos WHERE condominio_id = %s "
                                    "AND numero = %s AND COALESCE(bloco,'') = %s", (condominio_id, numero, bloco))
                        reg = cur.fetchone()
                        if reg:
                            apto_id = reg["id"]
                            cur.execute("UPDATE apartamentos SET proprietario=%s, telefone=%s, email=%s WHERE id=%s",
                                        (proprietario or None, telefone or None, email or None, apto_id))
                        else:
                            cur.execute("INSERT INTO apartamentos (condominio_id, numero, bloco, proprietario, telefone, email) "
                                        "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                                        (condominio_id, numero, bloco or None, proprietario or None,
                                         telefone or None, email or None))
                            apto_id = cur.fetchone()["id"]
                        if morador:
                            cur.execute("INSERT INTO moradores (apartamento_id, nome, parentesco, telefone, email, is_principal) "
                                        "VALUES (%s, %s, %s, %s, %s, TRUE)",
                                        (apto_id, morador, parentesco, tel_morador or None, email_morador or None))
                        importados += 1
                    registrar_auditoria(cur, "apartamentos", None, "INSERT",
                                        f"Importação de planilha: {importados} apartamento(s)")
                    conn.commit()
                    st.success(f"✅ {importados} apartamento(s) importado(s) com sucesso!")
                    if erros:
                        st.warning("Linhas com problemas:\n" + "\n".join(erros))
                    st.rerun()
            except Exception as e:
                st.error(f"Erro ao ler a planilha: {e}")

        # ===== 7️⃣ IMPORTAR VEÍCULOS E PETS DE PLANILHA =====
        st.markdown("---")
        st.subheader("7️⃣ Importar veículos e pets de planilha")
        st.caption("Use a planilha modelo (abas 'Veículos' e 'Pets'). O apartamento é localizado por número + bloco "
                   "e o limite é de 3 veículos por apartamento.")
        arquivo_vep = st.file_uploader("Planilha de veículos e pets (.xlsx)", type=["xlsx", "xls"], key="imp_vep")
        if arquivo_vep is not None:
            try:
                import pandas as pd
                if st.button("📥 Importar veículos e pets", key="btn_imp_vep"):
                    xl = pd.ExcelFile(arquivo_vep)
                    importados_v = 0
                    importados_p = 0
                    erros = []
                    if "Veículos" in xl.sheet_names:
                        df_v = pd.read_excel(xl, sheet_name="Veículos").fillna("")
                        for idx, row in df_v.iterrows():
                            numero = str(row.get("Apartamento", "")).strip()
                            bloco = str(row.get("Bloco", "")).strip()
                            tipo = str(row.get("Tipo", "")).strip() or "Carro"
                            marca = str(row.get("Marca", "")).strip()
                            modelo = str(row.get("Modelo", "")).strip()
                            placa = str(row.get("Placa", "")).strip()
                            cor = str(row.get("Cor", "")).strip()
                            ano_raw = str(row.get("Ano", "")).strip()
                            if not numero:
                                erros.append(f"Veículos, linha {idx + 2}: apartamento vazio.")
                                continue
                            if not marca or not modelo:
                                erros.append(f"Veículos, linha {idx + 2}: marca e modelo obrigatórios.")
                                continue
                            cur.execute("SELECT id FROM apartamentos WHERE condominio_id = %s "
                                        "AND numero = %s AND COALESCE(bloco,'') = %s",
                                        (condominio_id, numero, bloco))
                            reg = cur.fetchone()
                            if not reg:
                                erros.append(f"Veículos, linha {idx + 2}: apartamento {numero} não encontrado.")
                                continue
                            cur.execute("SELECT COUNT(*) AS total FROM veiculos WHERE apartamento_id = %s", (reg["id"],))
                            if cur.fetchone()["total"] >= 3:
                                erros.append(f"Veículos, linha {idx + 2}: apto {numero} já tem 3 veículos.")
                                continue
                            try:
                                ano_int = int(ano_raw) if ano_raw else None
                            except Exception:
                                ano_int = None
                            cur.execute("INSERT INTO veiculos (apartamento_id, tipo, marca, modelo, placa, cor, ano) "
                                        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                        (reg["id"], tipo, marca, modelo,
                                         placa.upper() or None, cor or None, ano_int))
                            importados_v += 1
                    if "Pets" in xl.sheet_names:
                        df_p = pd.read_excel(xl, sheet_name="Pets").fillna("")
                        for idx, row in df_p.iterrows():
                            numero = str(row.get("Apartamento", "")).strip()
                            bloco = str(row.get("Bloco", "")).strip()
                            tipo = str(row.get("Tipo", "")).strip()
                            raca = str(row.get("Raça", "")).strip()
                            porte = str(row.get("Porte", "")).strip()
                            obs = str(row.get("Observação", "")).strip()
                            if not numero:
                                erros.append(f"Pets, linha {idx + 2}: apartamento vazio.")
                                continue
                            if not tipo:
                                erros.append(f"Pets, linha {idx + 2}: tipo do pet obrigatório.")
                                continue
                            if tipo.lower() == "outro" and not obs:
                                erros.append(f"Pets, linha {idx + 2}: para 'Outro', informe o pet em Observação.")
                                continue
                            cur.execute("SELECT id FROM apartamentos WHERE condominio_id = %s "
                                        "AND numero = %s AND COALESCE(bloco,'') = %s",
                                        (condominio_id, numero, bloco))
                            reg = cur.fetchone()
                            if not reg:
                                erros.append(f"Pets, linha {idx + 2}: apartamento {numero} não encontrado.")
                                continue
                            cur.execute("INSERT INTO pets (apartamento_id, tipo, raca, porte, observacao) "
                                        "VALUES (%s, %s, %s, %s, %s)",
                                        (reg["id"], tipo, raca or None, porte or None, obs or None))
                            importados_p += 1
                    registrar_auditoria(cur, "veiculos", None, "INSERT",
                                        f"Importação: {importados_v} veículo(s) e {importados_p} pet(s)")
                    conn.commit()
                    st.success(f"✅ {importados_v} veículo(s) e {importados_p} pet(s) importados!")
                    if erros:
                        st.warning("Linhas com problemas:\n" + "\n".join(erros))
                    st.rerun()
            except Exception as e:
                st.error(f"Erro ao ler a planilha: {e}")
        cur.close(); conn.close()

# ===== FUNCIONÁRIAS =====
elif pagina == "Empregadas":
    banner("👩‍💼 Funcionárias", "roxo")
    if condominio_id is None:
        st.warning("Selecione um condomínio na barra lateral antes de cadastrar funcionárias.")
    else:
        conn = get_connection(); cur = conn.cursor()
        cur.execute("SELECT id, numero, bloco FROM apartamentos WHERE condominio_id = %s ORDER BY numero", (condominio_id,))
        aptos = cur.fetchall()
        opcoes_apto = {}
        for a in aptos:
            rotulo = f"{a['numero']}" + (f" - Bloco {a['bloco']}" if a["bloco"] else "")
            opcoes_apto[rotulo] = a["id"]

        with st.form("nova_empregada"):
            st.subheader("Cadastrar funcionária")
            nome = st.text_input("Nome *")
            cpf = st.text_input("CPF *", placeholder="Somente números, ex.: 12345678900")
            telefone = st.text_input("Telefone")
            endereco = st.text_input("Endereço residencial")
            if opcoes_apto:
                apto_rotulo = st.selectbox("Apartamento onde trabalha", list(opcoes_apto.keys()))
                apartamento_id = opcoes_apto[apto_rotulo]
            else:
                apartamento_id = None
                st.caption("Cadastre um apartamento antes para vincular a funcionária.")
            salvar = st.form_submit_button("Salvar funcionária")
        if salvar:
            cpf_limpo = "".join(filter(str.isdigit, cpf))
            if not nome.strip():
                st.error("O nome da funcionária é obrigatório.")
            elif len(cpf_limpo) != 11:
                st.error("CPF inválido — informe os 11 dígitos (somente números).")
            else:
                try:
                    cur.execute("INSERT INTO empregadas (condominio_id, apartamento_id, nome, cpf, telefone, endereco) "
                                "VALUES (%s, %s, %s, %s, %s, %s)",
                                (condominio_id, apartamento_id, nome.strip(), cpf_limpo,
                                 telefone.strip() or None, endereco.strip() or None))
                    registrar_auditoria(cur, "empregadas", None, "INSERT",
                                        f"Funcionária {nome.strip()} cadastrada")
                    conn.commit()
                    st.success(f"Funcionária {nome.strip()} cadastrada com sucesso!")
                except Exception as e:
                    conn.rollback(); st.error(f"Erro ao cadastrar: {e}")

        st.subheader("Funcionárias cadastradas")
        cur.execute("SELECT e.id, e.nome, e.cpf, e.telefone, e.endereco, e.apartamento_id, a.numero, a.bloco "
                    "FROM empregadas e LEFT JOIN apartamentos a ON a.id = e.apartamento_id "
                    "WHERE e.condominio_id = %s ORDER BY e.nome", (condominio_id,))
        empregadas = cur.fetchall()
        if empregadas:
            for e in empregadas:
                cpf_txt = e["cpf"] or ""
                if cpf_txt:
                    cpf_txt = f"{cpf_txt[:3]}.{cpf_txt[3:6]}.{cpf_txt[6:9]}-{cpf_txt[9:]}"
                apto_txt = ""
                if e["apartamento_id"]:
                    apto_txt = f" - Apto {e['numero']}" + (f" Bloco {e['bloco']}" if e["bloco"] else "")
                st.write(f"**{e['nome']}** — CPF: {cpf_txt} | {e['telefone'] or ''} | {e['endereco'] or ''}{apto_txt}")
        else:
            st.info("Nenhuma funcionária cadastrada ainda.")

        st.markdown("---")
        if st.button("🖨️ Imprimir Relatório de Funcionárias"):
            linhas = ""
            for e in empregadas:
                unidade = f"Apto {e['numero']}" + (f" - Bloco {e['bloco']}" if e["bloco"] else "") if e["apartamento_id"] else "—"
                linhas += f"<tr><td>{e['nome']}</td><td>{e['telefone'] or '—'}</td><td>{unidade}</td></tr>"
            if not linhas:
                linhas = "<tr><td colspan='3'>Nenhuma funcionária cadastrada.</td></tr>"
            st.iframe(f"""
            <html><head><meta charset="utf-8"><title>Relatório de Funcionárias</title></head>
            <body style="font-family:Arial,sans-serif; padding:20px;">
                {html_logo()}
                <h2 style="text-align:center;">RELATÓRIO DE FUNCIONÁRIAS</h2>
                <p style="text-align:center; font-weight:bold;">{nome_sel}</p>
                <p style="text-align:center;">Total de funcionárias: {len(empregadas)}</p>
                <hr>
                <table style="width:100%; border-collapse:collapse;">
                    <tr style="background:#1f3a5f; color:#fff;">
                        <th style="text-align:left; padding:8px; border:1px solid #ccc;">Funcionária</th>
                        <th style="text-align:left; padding:8px; border:1px solid #ccc;">Telefone</th>
                        <th style="text-align:left; padding:8px; border:1px solid #ccc;">Apartamento</th>
                    </tr>{linhas}
                </table>
                <hr>
                <p style="text-align:center; font-size:12px;">Emitido em {date.today().strftime('%d/%m/%Y')}</p>
                <script>window.print();</script>
            </body></html>""", height=600)

        st.markdown("---")
        st.subheader("📥 Importar funcionárias de planilha")
        st.caption("Use a planilha modelo (aba 'Funcionárias'). O CPF deve ter 11 dígitos e o apartamento precisa já estar cadastrado.")
        arquivo_func = st.file_uploader("Planilha de funcionárias (.xlsx)", type=["xlsx", "xls"], key="imp_func")
        if arquivo_func is not None:
            try:
                import pandas as pd
                df_func = pd.read_excel(arquivo_func, sheet_name="Funcionárias").fillna("")
                st.write(f"Linhas encontradas na planilha: {len(df_func)}")
                if st.button("📥 Importar funcionárias", key="btn_imp_func"):
                    importadas, erros = 0, []
                    for idx, row in df_func.iterrows():
                        nome = str(row.get("Nome", "")).strip()
                        cpf = "".join(filter(str.isdigit, str(row.get("CPF", ""))))
                        telefone = str(row.get("Telefone", "")).strip()
                        endereco = str(row.get("Endereço", "")).strip()
                        numero_apto = str(row.get("Apartamento", "")).strip()
                        bloco = str(row.get("Bloco", "")).strip()
                        if not nome:
                            erros.append(f"Linha {idx + 2}: nome vazio.")
                            continue
                        if len(cpf) != 11:
                            erros.append(f"Linha {idx + 2}: CPF inválido para {nome or '(sem nome)'}.")
                            continue
                        apartamento_id = None
                        if numero_apto:
                            cur.execute("SELECT id FROM apartamentos WHERE condominio_id = %s "
                                        "AND numero = %s AND COALESCE(bloco,'') = %s", (condominio_id, numero_apto, bloco))
                            reg = cur.fetchone()
                            if reg:
                                apartamento_id = reg["id"]
                            else:
                                erros.append(f"Linha {idx + 2}: apartamento {numero_apto} não encontrado para {nome}.")
                                continue
                        cur.execute("INSERT INTO empregadas (condominio_id, apartamento_id, nome, cpf, telefone, endereco) "
                                    "VALUES (%s, %s, %s, %s, %s, %s)",
                                    (condominio_id, apartamento_id, nome, cpf, telefone or None, endereco or None))
                        importadas += 1
                    registrar_auditoria(cur, "empregadas", None, "INSERT",
                                        f"Importação: {importadas} funcionária(s)")
                    conn.commit()
                    st.success(f"✅ {importadas} funcionária(s) importada(s) com sucesso!")
                    if erros:
                        st.warning("Linhas com problemas:\n" + "\n".join(erros))
                    st.rerun()
            except Exception as e:
                st.error(f"Erro ao ler a planilha: {e}")
        cur.close(); conn.close()

        # ===== LANÇAMENTOS =====
elif pagina == "Lançamentos":
    banner("💰 Lançamentos", "azul")
    if condominio_id is None:
        st.warning("Selecione um condomínio na barra lateral antes de lançar receitas e despesas.")
    else:
        conn = get_connection(); cur = conn.cursor()

        st.subheader("1️⃣ Categorias do condomínio")
        with st.form("nova_categoria"):
            c_tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
            c_nome = st.text_input("Nome da categoria *")
            salvar_c = st.form_submit_button("Adicionar categoria")
        if salvar_c:
            if not c_nome.strip():
                st.error("Informe o nome da categoria.")
            else:
                try:
                    cur.execute("INSERT INTO categorias (condominio_id, tipo, nome) VALUES (%s, %s, %s) RETURNING id",
                                (condominio_id, c_tipo.lower(), c_nome.strip()))
                    cat_id = cur.fetchone()["id"]
                    registrar_auditoria(cur, "categorias", cat_id, "INSERT",
                                        f"Categoria {c_tipo} '{c_nome.strip()}'")
                    conn.commit()
                    st.success(f"Categoria '{c_nome.strip()}' adicionada!")
                except Exception as e:
                    conn.rollback(); st.error(f"Erro ao adicionar: {e}")
        cur.execute("SELECT id, tipo, nome FROM categorias WHERE condominio_id = %s ORDER BY tipo, nome", (condominio_id,))
        categorias = cur.fetchall()
        cat_receitas = [c["nome"] for c in categorias if c["tipo"] == "receita"]
        cat_despesas = [c["nome"] for c in categorias if c["tipo"] == "despesa"]
        if categorias:
            st.selectbox("Categorias cadastradas", [f"{c['nome']} ({c['tipo']})" for c in categorias], key="cat_lista")
        else:
            st.info("Nenhuma categoria cadastrada. Adicione acima ou use 'Outras receitas'/'Outras despesas'.")

        st.markdown("---")
        st.subheader("2️⃣ Novo lançamento")
        l_tipo = st.radio("Tipo", ["Receita", "Despesa"], horizontal=True, key="lanc_tipo")
        if l_tipo == "Receita":
            opcoes_cat = cat_receitas + ["Outras receitas"]
        else:
            opcoes_cat = cat_despesas + ["Outras despesas"]
        if not opcoes_cat:
            opcoes_cat = ["Outras receitas"] if l_tipo == "Receita" else ["Outras despesas"]
        with st.form("novo_lancamento"):
            l_categoria = st.selectbox("Categoria", opcoes_cat, key="lanc_categoria")
            l_apartamento_id = None
            if l_tipo == "Receita":
                cur.execute("SELECT id, numero, bloco FROM apartamentos WHERE condominio_id = %s ORDER BY numero", (condominio_id,))
                aptos_lanc = cur.fetchall()
                opcoes_apto_lanc = {"— Não informar —": None}
                for a in aptos_lanc:
                    rotulo = f"{a['numero']}" + (f" - Bloco {a['bloco']}" if a["bloco"] else "")
                    opcoes_apto_lanc[rotulo] = a["id"]
                apto_rotulo = st.selectbox("Apartamento responsável pelo pagamento", list(opcoes_apto_lanc.keys()), key="lanc_apto")
                l_apartamento_id = opcoes_apto_lanc[apto_rotulo]
            l_descricao = st.text_input("Descrição", placeholder="Ex.: instalação de antena / registros cartorários", key="lanc_descricao")
            l_valor = st.number_input("Valor (R$) *", min_value=0.01, step=10.0, format="%.2f", key="lanc_valor")
            l_data = st.date_input("Data do lançamento", value=date.today(), key="lanc_data")
            salvar_l = st.form_submit_button("Salvar lançamento")
        if salvar_l:
            if l_categoria.startswith("Outras") and not l_descricao.strip():
                st.error("Para 'Outras receitas'/'Outras despesas', informe a descrição.")
            elif l_valor <= 0:
                st.error("Informe um valor maior que zero.")
            else:
                try:
                    cur.execute("INSERT INTO lancamentos (condominio_id, apartamento_id, tipo, categoria, descricao, valor, data_lancamento) "
                                "VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
                                (condominio_id, l_apartamento_id, l_tipo.lower(), l_categoria,
                                 l_descricao.strip(), l_valor, l_data))
                    novo_lanc_id = cur.fetchone()["id"]
                    registrar_auditoria(cur, "lancamentos", novo_lanc_id, "INSERT",
                                        f"{l_tipo} '{l_categoria}' R$ {fmt_br(l_valor)} em {l_data}")
                    conn.commit()
                    st.success(f"Lançamento de {l_tipo} '{l_categoria}' salvo com sucesso!")
                except Exception as e:
                    conn.rollback(); st.error(f"Erro ao salvar: {e}")

        st.markdown("---")
        st.subheader("3️⃣ Lançamentos do mês")
        hoje = date.today()
        c_m, c_a = st.columns(2)
        with c_m:
            mes_sel = st.selectbox("Mês", list(range(1, 13)), format_func=lambda m: MESES_NOMES[m - 1],
                                   index=hoje.month - 1, key="lanc_mes")
        with c_a:
            anos = list(range(2028, 2024, -1))
            idx_ano = anos.index(hoje.year) if hoje.year in anos else 0
            ano_sel = st.selectbox("Ano", anos, index=idx_ano, key="lanc_ano")
        exibir_lanc = st.checkbox("📋 Exibir Lançamentos", value=False, key="exibir_lanc")
        if not exibir_lanc:
            st.caption("Marque 'Exibir Lançamentos' para ver a lista do mês selecionado.")
        else:
            cur.execute("SELECT l.id, l.tipo, l.categoria, l.descricao, l.valor, l.data_lancamento, "
                        "l.apartamento_id, a.numero, a.bloco "
                        "FROM lancamentos l LEFT JOIN apartamentos a ON a.id = l.apartamento_id "
                        "WHERE l.condominio_id = %s "
                        "AND EXTRACT(MONTH FROM l.data_lancamento) = %s AND EXTRACT(YEAR FROM l.data_lancamento) = %s "
                        "ORDER BY l.data_lancamento DESC, l.id DESC", (condominio_id, mes_sel, ano_sel))
            lancamentos = cur.fetchall()
            if lancamentos:
                receitas = [l for l in lancamentos if l["tipo"] == "receita"]
                despesas = [l for l in lancamentos if l["tipo"] == "despesa"]
                total_receitas = sum(float(l["valor"]) for l in receitas)
                total_despesas = sum(float(l["valor"]) for l in despesas)

                def linha_lanc(l):
                    apto_pag = ""
                    if l.get("apartamento_id"):
                        apto_pag = f"Apto {l['numero']}" + (f" Bloco {l['bloco']}" if l["bloco"] else "")
                    return (
                        f"<tr>"
                        f"<td style='border:1px solid #ccc; padding:5px;'>{l['data_lancamento'].strftime('%d/%m/%Y')}</td>"
                        f"<td style='border:1px solid #ccc; padding:5px;'>{l['categoria']}</td>"
                        f"<td style='border:1px solid #ccc; padding:5px;'>{l['descricao'] or ''}</td>"
                        f"<td style='border:1px solid #ccc; padding:5px;'>{apto_pag}</td>"
                        f"<td style='border:1px solid #ccc; padding:5px; text-align:right; white-space:nowrap;'>R$ {fmt_br(l['valor'])}</td>"
                        f"</tr>"
                    )

                cabecalho = (
                    "<tr style='background:#1f3a5f; color:#fff;'>"
                    "<th style='border:1px solid #ccc; padding:6px;'>Data</th>"
                    "<th style='border:1px solid #ccc; padding:6px;'>Categoria</th>"
                    "<th style='border:1px solid #ccc; padding:6px;'>Descrição</th>"
                    "<th style='border:1px solid #ccc; padding:6px;'>Apartamento</th>"
                    "<th style='border:1px solid #ccc; padding:6px; text-align:right;'>Valor</th>"
                    "</tr>"
                )

                corpo = ""
                corpo += (
                    "<tr style='background:#e8f5e9;'>"
                    "<td colspan='5' style='border:1px solid #ccc; padding:6px; font-weight:700; color:#1e7a46;'>Receitas</td>"
                    "</tr>"
                )
                for l in receitas:
                    corpo += linha_lanc(l)
                corpo += (
                    "<tr style='background:#e8f5e9; font-weight:700;'>"
                    "<td colspan='4' style='border:1px solid #ccc; padding:6px;'>Total Receitas</td>"
                    f"<td style='border:1px solid #ccc; padding:6px; text-align:right; white-space:nowrap;'>R$ {fmt_br(total_receitas)}</td>"
                    "</tr>"
                )
                corpo += "<tr><td colspan='5' style='border:1px solid #ccc; padding:2px;'>&nbsp;</td></tr>"
                corpo += (
                    "<tr style='background:#fdecea;'>"
                    "<td colspan='5' style='border:1px solid #ccc; padding:6px; font-weight:700; color:#b53434;'>Despesas</td>"
                    "</tr>"
                )
                for l in despesas:
                    corpo += linha_lanc(l)
                corpo += (
                    "<tr style='background:#fdecea; font-weight:700;'>"
                    "<td colspan='4' style='border:1px solid #ccc; padding:6px;'>Total Despesas</td>"
                    f"<td style='border:1px solid #ccc; padding:6px; text-align:right; white-space:nowrap;'>R$ {fmt_br(total_despesas)}</td>"
                    "</tr>"
                )
                corpo += (
                    "<tr style='background:#eef4fb; font-weight:700;'>"
                    "<td colspan='4' style='border:1px solid #ccc; padding:6px;'>Saldo do mês</td>"
                    f"<td style='border:1px solid #ccc; padding:6px; text-align:right; white-space:nowrap;'>R$ {fmt_br(total_receitas - total_despesas)}</td>"
                    "</tr>"
                )

                st.markdown(
                    f"<table style='width:100%; border-collapse:collapse;'>"
                    f"<thead>{cabecalho}</thead><tbody>{corpo}</tbody></table>",
                    unsafe_allow_html=True,
                )

                st.markdown("---")
                st.subheader("✏️ Alterar / excluir lançamento")
                opcoes_lanc = {}
                for l in lancamentos:
                    opcoes_lanc[f"#{l['id']} — {l['data_lancamento'].strftime('%d/%m/%Y')} — {l['categoria']} — "
                                f"{l['descricao'] or ''} — R$ {fmt_br(l['valor'])}"] = l["id"]
                lanc_sel = st.selectbox("Selecione o lançamento", list(opcoes_lanc.keys()), key="lanc_edit_sel")
                lanc_id = opcoes_lanc[lanc_sel]
                l_edit = next(x for x in lancamentos if x["id"] == lanc_id)
                if l_edit["tipo"] == "receita":
                    opcoes_edit = cat_receitas + ["Outras receitas"]
                else:
                    opcoes_edit = cat_despesas + ["Outras despesas"]
                idx_edit = opcoes_edit.index(l_edit["categoria"]) if l_edit["categoria"] in opcoes_edit else 0
                with st.form("editar_lancamento"):
                    e_categoria = st.selectbox("Categoria", opcoes_edit, index=idx_edit)
                    e_descricao = st.text_input("Descrição", value=l_edit["descricao"] or "")
                    e_valor = st.number_input("Valor (R$)", min_value=0.01, step=10.0, format="%.2f",
                                              value=float(l_edit["valor"]))
                    e_data = st.date_input("Data", value=l_edit["data_lancamento"])
                    ce1, ce2 = st.columns(2)
                    salvar_e = ce1.form_submit_button("💾 Salvar alterações")
                    excluir_e = ce2.form_submit_button("🗑️ Excluir lançamento")
                if salvar_e:
                    cur.execute("UPDATE lancamentos SET categoria=%s, descricao=%s, valor=%s, data_lancamento=%s WHERE id=%s",
                                (e_categoria.strip(), e_descricao.strip(), e_valor, e_data, lanc_id))
                    registrar_auditoria(cur, "lancamentos", lanc_id, "UPDATE",
                                        f"Lançamento #{lanc_id} alterado para '{e_categoria}' R$ {fmt_br(e_valor)}")
                    conn.commit(); st.success("Lançamento atualizado!"); st.rerun()
                if excluir_e:
                    cur.execute("DELETE FROM lancamentos WHERE id = %s", (lanc_id,))
                    registrar_auditoria(cur, "lancamentos", lanc_id, "DELETE",
                                        f"Lançamento #{lanc_id} excluído")
                    conn.commit(); st.success("Lançamento excluído!"); st.rerun()
            else:
                st.info("Nenhum lançamento neste mês.")

        st.markdown("---")
        st.subheader("4️⃣ Saldo inicial do mês (saldo do mês anterior)")
        saldo_inicial_atual = 0.0
        try:
            cur.execute("SELECT valor FROM saldos_iniciais WHERE condominio_id = %s AND mes = %s AND ano = %s",
                        (condominio_id, mes_sel, ano_sel))
            si_reg = cur.fetchone()
            saldo_inicial_atual = float(si_reg["valor"]) if si_reg else 0.0
        except Exception:
            st.warning("Acesso à tabela 'saldos_iniciais' negado. Rode no pgAdmin (como superusuário): "
                       "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO <seu_usuario>;")
        cur.execute("SELECT COALESCE(SUM(saldo), 0) AS total FROM contas_bancarias WHERE condominio_id = %s", (condominio_id,))
        total_contas_sugestao = float(cur.fetchone()["total"])
        origem = st.radio("Origem do saldo inicial", ["Informar manualmente", "Usar saldo das contas (sugestão)"],
                          horizontal=True, key="si_origem")
        valor_sugerido = total_contas_sugestao if origem == "Usar saldo das contas (sugestão)" else saldo_inicial_atual
        st.caption(f"Total atual em contas bancárias: R$ {fmt_br(total_contas_sugestao)}")
        with st.form("saldo_inicial_form"):
            si_valor = st.number_input("Saldo inicial do mês (R$)", min_value=0.0, step=100.0, format="%.2f",
                                       value=float(valor_sugerido))
            salvar_si = st.form_submit_button("💾 Salvar saldo inicial")
        if salvar_si:
            try:
                cur.execute("INSERT INTO saldos_iniciais (condominio_id, mes, ano, valor) VALUES (%s, %s, %s, %s) "
                            "ON CONFLICT (condominio_id, mes, ano) DO UPDATE SET valor = EXCLUDED.valor, atualizado_em = CURRENT_TIMESTAMP",
                            (condominio_id, mes_sel, ano_sel, si_valor))
                registrar_auditoria(cur, "saldos_iniciais", None, "UPDATE",
                                    f"Saldo inicial de {MESES_NOMES[mes_sel - 1]}/{ano_sel} = R$ {fmt_br(si_valor)}")
                conn.commit()
                st.success(f"Saldo inicial de {MESES_NOMES[mes_sel - 1]}/{ano_sel} salvo: R$ {fmt_br(si_valor)}")
                st.rerun()
            except Exception:
                conn.rollback()
                st.error("Não foi possível salvar o saldo inicial — verifique a permissão da tabela "
                         "'saldos_iniciais' (GRANT ALL PRIVILEGES ... ) ou se o usuário do banco é o dono da tabela.")
        cur.close(); conn.close()


        # ===== PRESTAÇÃO DE CONTAS =====
elif pagina == "Prestação de Contas":
    banner("📑 Prestação de Contas", "azul")
    if condominio_id is None:
        st.warning("Selecione um condomínio na barra lateral antes de gerar a prestação de contas.")
    else:
        conn = get_connection(); cur = conn.cursor()
        hoje = date.today()

        periodo = st.radio("Período do relatório", ["Mensal", "Anual"], horizontal=True, key="pc_periodo")
        if periodo == "Mensal":
            c_m, c_a = st.columns(2)
            with c_m:
                mes_sel = st.selectbox("Mês", list(range(1, 13)), format_func=lambda m: MESES_NOMES[m - 1],
                                       index=hoje.month - 1, key="pc_mes")
            with c_a:
                anos = list(range(2028, 2024, -1))
                idx_ano = anos.index(hoje.year) if hoje.year in anos else 0
                ano_sel = st.selectbox("Ano", anos, index=idx_ano, key="pc_ano")
        else:
            anos = list(range(2028, 2024, -1))
            idx_ano = anos.index(hoje.year) if hoje.year in anos else 0
            ano_sel = st.selectbox("Ano do balancete", anos, index=idx_ano, key="pc_ano_anual")

        incluir_apto = st.checkbox("Incluir receitas por apartamento", value=True, key="pc_apto")
        incluir_sem_vinculo = st.checkbox("Incluir receitas sem vínculo", value=True, key="pc_sem_vinculo")

        if periodo == "Mensal":
            filtro_data = "EXTRACT(MONTH FROM data_lancamento) = %s AND EXTRACT(YEAR FROM data_lancamento) = %s"
            params_data = (mes_sel, ano_sel)
            titulo_periodo = f"{MESES_NOMES[mes_sel - 1]} de {ano_sel}"
            titulo_doc = "PRESTAÇÃO DE CONTAS"
        else:
            filtro_data = "EXTRACT(YEAR FROM data_lancamento) = %s"
            params_data = (ano_sel,)
            titulo_periodo = f"Ano {ano_sel}"
            titulo_doc = "BALANCETE ANUAL"

        cur.execute(f"SELECT COALESCE(SUM(valor) FILTER (WHERE tipo = 'receita'), 0) AS total_receitas, "
                    f"COALESCE(SUM(valor) FILTER (WHERE tipo = 'despesa'), 0) AS total_despesas "
                    f"FROM lancamentos WHERE condominio_id = %s AND {filtro_data}", (condominio_id, *params_data))
        totais_pc = cur.fetchone()
        total_receitas = float(totais_pc["total_receitas"])
        total_despesas = float(totais_pc["total_despesas"])
        saldo_periodo = total_receitas - total_despesas

        saldo_anterior = None
        if periodo == "Mensal":
            try:
                cur.execute("SELECT valor FROM saldos_iniciais WHERE condominio_id = %s AND mes = %s AND ano = %s",
                            (condominio_id, mes_sel, ano_sel))
                si_pc = cur.fetchone()
                if si_pc:
                    saldo_anterior = float(si_pc["valor"])
            except Exception:
                saldo_anterior = None
            if saldo_anterior is None:
                mes_ant = 12 if mes_sel == 1 else mes_sel - 1
                ano_ant = ano_sel - 1 if mes_sel == 1 else ano_sel
                saldo_anterior = saldo_acumulado_ate(condominio_id, cur, mes_ant, ano_ant)
        else:
            try:
                cur.execute("SELECT valor FROM saldos_iniciais WHERE condominio_id = %s AND mes = 1 AND ano = %s",
                            (condominio_id, ano_sel))
                si_pc = cur.fetchone()
                if si_pc:
                    saldo_anterior = float(si_pc["valor"])
            except Exception:
                saldo_anterior = None
            if saldo_anterior is None:
                saldo_anterior = saldo_acumulado_ate(condominio_id, cur, 12, ano_sel - 1)
        saldo_atual = saldo_anterior + saldo_periodo

        st.markdown("---")
        st.subheader("📊 Resumo do período")
        c1, c2, c3 = st.columns(3)
        with c1: card("Saldo anterior", f"R$ {fmt_br(saldo_anterior)}", "cinza")
        with c2: card("Saldo do período", f"R$ {fmt_br(saldo_periodo)}", "saldo")
        with c3: card("Saldo acumulado", f"R$ {fmt_br(saldo_atual)}", "conta")

        valores_dist = {}
        contas_dist = []
        if periodo == "Mensal":
            st.markdown("---")
            st.subheader("💳 Distribuição do saldo por conta")
            st.caption(f"Informe como o saldo acumulado (R$ {fmt_br(saldo_atual)}) está distribuído "
                       "entre as contas correntes e a poupança. A soma deve conferir com o saldo acumulado.")
            cur.execute("SELECT id, tipo, banco, agencia, numero_conta FROM contas_bancarias "
                        "WHERE condominio_id = %s ORDER BY tipo, banco", (condominio_id,))
            contas_dist = cur.fetchall()
            if contas_dist:
                dist_salva = {}
                try:
                    cur.execute("SELECT conta_id, valor FROM distribuicao_contas "
                                "WHERE condominio_id = %s AND mes = %s AND ano = %s",
                                (condominio_id, mes_sel, ano_sel))
                    for d in cur.fetchall():
                        dist_salva[d["conta_id"]] = float(d["valor"])
                except Exception:
                    dist_salva = {}
                cols = st.columns(2)
                for i, c in enumerate(contas_dist):
                    rotulo = f"{c['banco']} ({'Corrente' if c['tipo'] == 'corrente' else 'Poupança'})"
                    with cols[i % 2]:
                        valores_dist[c["id"]] = st.number_input(
                            f"💵 R$ — {rotulo}",
                            min_value=0.0, step=100.0, format="%.2f",
                            value=float(dist_salva.get(c["id"], 0.0)),
                            key=f"dist_{c['id']}_{mes_sel}_{ano_sel}",
                        )
                total_dist = round(sum(valores_dist.values()), 2)
                saldo_ref = round(saldo_atual, 2)
                diferenca = round(total_dist - saldo_ref, 2)
                if diferenca != 0:
                    st.warning(f"A soma da distribuição (R$ {fmt_br(total_dist)}) difere do saldo acumulado "
                               f"(R$ {fmt_br(saldo_ref)}) em R$ {fmt_br(abs(diferenca))}. "
                               "Ajuste os valores antes de imprimir.")
                else:
                    st.success(f"✅ Distribuição confere: R$ {fmt_br(total_dist)}")
                if st.button("💾 Salvar distribuição", key="btn_salvar_dist"):
                    try:
                        for conta_id, valor in valores_dist.items():
                            cur.execute(
                                "INSERT INTO distribuicao_contas (condominio_id, mes, ano, conta_id, valor) "
                                "VALUES (%s, %s, %s, %s, %s) "
                                "ON CONFLICT (condominio_id, mes, ano, conta_id) DO UPDATE SET valor = EXCLUDED.valor",
                                (condominio_id, mes_sel, ano_sel, conta_id, round(valor, 2)),
                            )
                        registrar_auditoria(cur, "distribuicao_contas", None, "UPDATE",
                                        f"Distribuição de {MESES_NOMES[mes_sel - 1]}/{ano_sel} salva")
                        conn.commit()
                        st.success("Distribuição salva com sucesso!")
                    except Exception as e:
                        conn.rollback()
                        st.error(f"Erro ao salvar distribuição: {e}")
            else:
                st.info("Nenhuma conta bancária cadastrada. Cadastre contas no módulo Bancos.")

        if st.button("🖨️ Imprimir Prestação de Contas"):
            # ===== DISTRIBUIÇÃO POR CONTA (para o relatório) =====
            if periodo == "Mensal":
                total_contas = 0.0
                linhas_contas = ""
                for c in contas_dist:
                    valor = round(valores_dist.get(c["id"], 0.0), 2)
                    total_contas += valor
                    linhas_contas += (
                        f"<tr><td style='border:1px solid #ccc; padding:5px;'>{c['banco']}</td>"
                        f"<td style='border:1px solid #ccc; padding:5px;'>{'Corrente' if c['tipo'] == 'corrente' else 'Poupança'}</td>"
                        f"<td style='border:1px solid #ccc; padding:5px;'>Ag {c['agencia'] or '—'} / Conta {c['numero_conta'] or '—'}</td>"
                        f"<td style='border:1px solid #ccc; padding:5px; text-align:right; white-space:nowrap;'>R$ {fmt_br(valor)}</td></tr>"
                    )
                if not linhas_contas:
                    linhas_contas = "<tr><td colspan='4' style='border:1px solid #ccc; padding:5px;'>Nenhuma conta cadastrada.</td></tr>"
            else:
                cur.execute("SELECT tipo, banco, agencia, numero_conta, saldo FROM contas_bancarias "
                            "WHERE condominio_id = %s ORDER BY tipo, banco", (condominio_id,))
                contas = cur.fetchall()
                total_contas = 0.0
                linhas_contas = ""
                for c in contas:
                    total_contas += float(c["saldo"])
                    linhas_contas += (
                        f"<tr><td style='border:1px solid #ccc; padding:5px;'>{c['banco']}</td>"
                        f"<td style='border:1px solid #ccc; padding:5px;'>{'Corrente' if c['tipo'] == 'corrente' else 'Poupança'}</td>"
                        f"<td style='border:1px solid #ccc; padding:5px;'>Ag {c['agencia'] or '—'} / Conta {c['numero_conta'] or '—'}</td>"
                        f"<td style='border:1px solid #ccc; padding:5px; text-align:right; white-space:nowrap;'>R$ {fmt_br(c['saldo'])}</td></tr>"
                    )
                if not linhas_contas:
                    linhas_contas = "<tr><td colspan='4' style='border:1px solid #ccc; padding:5px;'>Nenhuma conta bancária cadastrada.</td></tr>"

            # ===== TABELAS MENSAIS =====
            html_receitas_mensal = ""
            html_outras_receitas = ""
            html_resumo_receitas = ""
            html_despesas_mensal = ""
            if periodo == "Mensal":
                # 1) Receitas — Taxa de Condomínio/Garagem (apartamentos em ordem numérica)
                cur.execute(
                    f"SELECT l.categoria, l.valor, l.apartamento_id, a.numero, a.bloco "
                    f"FROM lancamentos l JOIN apartamentos a ON a.id = l.apartamento_id "
                    f"WHERE l.condominio_id = %s AND l.tipo = 'receita' AND {filtro_data} "
                    f"ORDER BY CASE WHEN a.numero ~ '^[0-9]+$' THEN a.numero::int ELSE 999999 END, "
                    f"a.numero, a.bloco",
                    (condominio_id, *params_data),
                )
                receitas_taxa = cur.fetchall()
                total_taxa = sum(float(r["valor"]) for r in receitas_taxa)
                linhas_taxa = ""
                for r in receitas_taxa:
                    apto_txt = f"{r['numero']}" + (f" - Bloco {r['bloco']}" if r["bloco"] else "")
                    linhas_taxa += (
                        f"<tr>"
                        f"<td style='border:1px solid #ccc; padding:5px;'>{apto_txt}</td>"
                        f"<td style='border:1px solid #ccc; padding:5px;'>{r['categoria']}</td>"
                        f"<td style='border:1px solid #ccc; padding:5px; text-align:right; white-space:nowrap;'>R$ {fmt_br(r['valor'])}</td>"
                        f"</tr>"
                    )
                if not linhas_taxa:
                    linhas_taxa = "<tr><td colspan='3' style='border:1px solid #ccc; padding:5px;'>Nenhuma receita de taxa no período.</td></tr>"
                linhas_taxa += (
                    "<tr style='background:#e0e0e0; font-weight:700;'>"
                    "<td colspan='2' style='border:1px solid #ccc; padding:5px;'>Total Taxa de Condomínio/Garagem</td>"
                    f"<td style='border:1px solid #ccc; padding:5px; text-align:right; white-space:nowrap;'>R$ {fmt_br(total_taxa)}</td>"
                    "</tr>"
                )
                html_receitas_mensal = f"""
                <h3>1) Receitas — Taxa de Condomínio/Garagem</h3>
                <table style="width:100%; border-collapse:collapse; font-size:0.85em;">
                    <tr style="background:#1f3a5f; color:#fff;">
                        <th style="border:1px solid #ccc; padding:5px; text-align:left;">Apartamento</th>
                        <th style="border:1px solid #ccc; padding:5px; text-align:left;">Categoria</th>
                        <th style="border:1px solid #ccc; padding:5px; text-align:right;">Valor</th>
                    </tr>
                    {linhas_taxa}
                </table>"""

                # 2) Outras Receitas (sem vínculo com apartamento)
                cur.execute(
                    f"SELECT l.categoria, l.descricao, l.valor "
                    f"FROM lancamentos l "
                    f"WHERE l.condominio_id = %s AND l.tipo = 'receita' AND l.apartamento_id IS NULL AND {filtro_data} "
                    f"ORDER BY l.categoria, l.descricao",
                    (condominio_id, *params_data),
                )
                outras_receitas = cur.fetchall()
                total_outras = sum(float(r["valor"]) for r in outras_receitas)
                linhas_outras = ""
                for r in outras_receitas:
                    linhas_outras += (
                        f"<tr>"
                        f"<td style='border:1px solid #ccc; padding:5px;'>{r['categoria']}</td>"
                        f"<td style='border:1px solid #ccc; padding:5px;'>{r['descricao'] or ''}</td>"
                        f"<td style='border:1px solid #ccc; padding:5px; text-align:right; white-space:nowrap;'>R$ {fmt_br(r['valor'])}</td>"
                        f"</tr>"
                    )
                if not linhas_outras:
                    linhas_outras = "<tr><td colspan='3' style='border:1px solid #ccc; padding:5px;'>Nenhuma outra receita no período.</td></tr>"
                linhas_outras += (
                    "<tr style='background:#e0e0e0; font-weight:700;'>"
                    "<td colspan='2' style='border:1px solid #ccc; padding:5px;'>Total Outras Receitas</td>"
                    f"<td style='border:1px solid #ccc; padding:5px; text-align:right; white-space:nowrap;'>R$ {fmt_br(total_outras)}</td>"
                    "</tr>"
                )
                html_outras_receitas = f"""
                <h3>2) Outras Receitas</h3>
                <table style="width:100%; border-collapse:collapse; font-size:0.85em;">
                    <tr style="background:#1f3a5f; color:#fff;">
                        <th style="border:1px solid #ccc; padding:5px; text-align:left;">Categoria</th>
                        <th style="border:1px solid #ccc; padding:5px; text-align:left;">Descrição</th>
                        <th style="border:1px solid #ccc; padding:5px; text-align:right;">Valor</th>
                    </tr>
                    {linhas_outras}
                </table>"""

                # 3) Resumo das Receitas
                html_resumo_receitas = f"""
                <h3>3) Resumo das Receitas</h3>
                <table style="width:60%; border-collapse:collapse; font-size:0.9em;">
                    <tr><td style="padding:5px; border:1px solid #ccc;">Receita Taxa de Condomínio/Garagem</td><td style="text-align:right; padding:5px; border:1px solid #ccc; white-space:nowrap;">R$ {fmt_br(total_taxa)}</td></tr>
                    <tr><td style="padding:5px; border:1px solid #ccc;">Outras Receitas</td><td style="text-align:right; padding:5px; border:1px solid #ccc; white-space:nowrap;">R$ {fmt_br(total_outras)}</td></tr>
                    <tr style="font-weight:bold; background:#e0e0e0;"><td style="padding:5px; border:1px solid #ccc;">Total das Receitas</td><td style="text-align:right; padding:5px; border:1px solid #ccc; white-space:nowrap;">R$ {fmt_br(total_receitas)}</td></tr>
                </table>"""

                # 4) Despesas (categoria em ordem alfabética)
                cur.execute(
                    f"SELECT l.categoria, l.descricao, l.valor "
                    f"FROM lancamentos l "
                    f"WHERE l.condominio_id = %s AND l.tipo = 'despesa' AND {filtro_data} "
                    f"ORDER BY l.categoria, l.descricao",
                    (condominio_id, *params_data),
                )
                despesas_mensal = cur.fetchall()
                linhas_desp = ""
                for d in despesas_mensal:
                    linhas_desp += (
                        f"<tr>"
                        f"<td style='border:1px solid #ccc; padding:5px;'>{d['categoria']}</td>"
                        f"<td style='border:1px solid #ccc; padding:5px;'>{d['descricao'] or ''}</td>"
                        f"<td style='border:1px solid #ccc; padding:5px; text-align:right; white-space:nowrap;'>R$ {fmt_br(d['valor'])}</td>"
                        f"</tr>"
                    )
                if not linhas_desp:
                    linhas_desp = "<tr><td colspan='3' style='border:1px solid #ccc; padding:5px;'>Nenhuma despesa no período.</td></tr>"
                linhas_desp += (
                    "<tr style='background:#e0e0e0; font-weight:700;'>"
                    "<td colspan='2' style='border:1px solid #ccc; padding:5px;'>Total das Despesas</td>"
                    f"<td style='border:1px solid #ccc; padding:5px; text-align:right; white-space:nowrap;'>R$ {fmt_br(total_despesas)}</td>"
                    "</tr>"
                )
                html_despesas_mensal = f"""
                <h3>4) Despesas</h3>
                <table style="width:100%; border-collapse:collapse; font-size:0.85em;">
                    <tr style="background:#1f3a5f; color:#fff;">
                        <th style="border:1px solid #ccc; padding:5px; text-align:left;">Categoria</th>
                        <th style="border:1px solid #ccc; padding:5px; text-align:left;">Descrição</th>
                        <th style="border:1px solid #ccc; padding:5px; text-align:right;">Valor</th>
                    </tr>
                    {linhas_desp}
                </table>"""


                            # ===== BALANCETE ANUAL — MATRIZES POR MÊS =====
            html_tabela_mensal = ""
            if periodo == "Anual":
                def celula(v):
                    return f"<td style='text-align:right; padding:3px; border:1px solid #ccc; white-space:nowrap;'>{fmt_br(v) if v else '—'}</td>"

                def cabecalho_meses(rotulo):
                    cab = "<tr style='background:#1f3a5f; color:#fff;'>"
                    cab += f"<th style='padding:3px; border:1px solid #ccc; text-align:left;'>{rotulo}</th>"
                    for m in range(1, 13):
                        cab += f"<th style='padding:3px; border:1px solid #ccc; text-align:right;'>{MESES_NOMES[m-1][:3]}</th>"
                    cab += "<th style='padding:3px; border:1px solid #ccc; text-align:right;'>Total</th></tr>"
                    return cab

                def linha_total(somas_mes, total_geral):
                    linha = "<tr style='font-weight:bold; background:#eef4fb;'>"
                    linha += "<td style='text-align:left; padding:3px; border:1px solid #ccc;'>Total</td>"
                    for m in range(1, 13):
                        linha += celula(somas_mes[m])
                    linha += f"<td style='text-align:right; padding:3px; border:1px solid #ccc; font-weight:bold; white-space:nowrap;'>{fmt_br(total_geral)}</td></tr>"
                    return linha

                # ----- 1) Receitas — Contribuição por apartamento -----
                cur.execute(
                    "SELECT a.numero, a.bloco, EXTRACT(MONTH FROM l.data_lancamento) AS mes, "
                    "SUM(l.valor) AS total "
                    "FROM lancamentos l JOIN apartamentos a ON a.id = l.apartamento_id "
                    "WHERE l.condominio_id = %s AND l.tipo = 'receita' "
                    "AND EXTRACT(YEAR FROM l.data_lancamento) = %s "
                    "GROUP BY a.numero, a.bloco, mes ORDER BY a.numero, a.bloco, mes",
                    (condominio_id, ano_sel),
                )
                receitas_apto_mes = cur.fetchall()
                cur.execute(
                    "SELECT numero, bloco FROM apartamentos WHERE condominio_id = %s "
                    "ORDER BY numero, bloco",
                    (condominio_id,),
                )
                aptos_bal = cur.fetchall()

                matriz_apto = {}
                for r in receitas_apto_mes:
                    chave = (r["numero"], r["bloco"])
                    matriz_apto.setdefault(chave, {})[int(r["mes"])] = float(r["total"])

                somas_contrib = [0.0] * 13
                total_contrib = 0.0
                linhas_contrib = ""
                for a in aptos_bal:
                    chave = (a["numero"], a["bloco"])
                    meses_apto = matriz_apto.get(chave, {})
                    rotulo = f"{a['numero']}" + (f" - Bloco {a['bloco']}" if a["bloco"] else "")
                    linha = f"<tr><td style='text-align:left; padding:3px; border:1px solid #ccc;'>{rotulo}</td>"
                    total_apto = 0.0
                    for m in range(1, 13):
                        v = meses_apto.get(m, 0.0)
                        total_apto += v
                        somas_contrib[m] += v
                        linha += celula(v)
                    total_contrib += total_apto
                    linha += f"<td style='text-align:right; padding:3px; border:1px solid #ccc; font-weight:bold; white-space:nowrap;'>{fmt_br(total_apto)}</td></tr>"
                    linhas_contrib += linha
                if not linhas_contrib:
                    linhas_contrib = "<tr><td colspan='14' style='padding:3px; border:1px solid #ccc;'>Nenhuma contribuição registrada.</td></tr>"
                linhas_contrib += linha_total(somas_contrib, total_contrib)

                html_tabela_contrib = f"""
                <h3>1) Receitas — Contribuição por apartamento</h3>
                <table style="width:100%; border-collapse:collapse; font-size:0.8em;">
                    {cabecalho_meses("Apartamento")}
                    {linhas_contrib}
                </table>"""

                # ----- 2) Receitas — Outras (sem vínculo) -----
                cur.execute(
                    "SELECT l.categoria, l.descricao, EXTRACT(MONTH FROM l.data_lancamento) AS mes, "
                    "SUM(l.valor) AS total "
                    "FROM lancamentos l "
                    "WHERE l.condominio_id = %s AND l.tipo = 'receita' AND l.apartamento_id IS NULL "
                    "AND EXTRACT(YEAR FROM l.data_lancamento) = %s "
                    "GROUP BY l.categoria, l.descricao, mes ORDER BY l.categoria, l.descricao, mes",
                    (condominio_id, ano_sel),
                )
                outras_mes = cur.fetchall()

                matriz_outras = {}
                for r in outras_mes:
                    rotulo = r["descricao"] or r["categoria"]
                    matriz_outras.setdefault(rotulo, {})[int(r["mes"])] = float(r["total"])

                somas_outras = [0.0] * 13
                total_outras = 0.0
                linhas_outras = ""
                for rotulo in sorted(matriz_outras.keys()):
                    linha = f"<tr><td style='text-align:left; padding:3px; border:1px solid #ccc;'>{rotulo}</td>"
                    total_linha = 0.0
                    for m in range(1, 13):
                        v = matriz_outras[rotulo].get(m, 0.0)
                        total_linha += v
                        somas_outras[m] += v
                        linha += celula(v)
                    total_outras += total_linha
                    linha += f"<td style='text-align:right; padding:3px; border:1px solid #ccc; font-weight:bold; white-space:nowrap;'>{fmt_br(total_linha)}</td></tr>"
                    linhas_outras += linha
                if not linhas_outras:
                    linhas_outras = "<tr><td colspan='14' style='padding:3px; border:1px solid #ccc;'>Nenhuma outra receita registrada.</td></tr>"
                linhas_outras += linha_total(somas_outras, total_outras)

                html_tabela_outras = f"""
                <h3>2) Receitas — Outras</h3>
                <table style="width:100%; border-collapse:collapse; font-size:0.8em;">
                    {cabecalho_meses("Descrição")}
                    {linhas_outras}
                </table>"""

                # ----- 3) Despesas por categoria -----
                cur.execute(
                    "SELECT l.categoria, EXTRACT(MONTH FROM l.data_lancamento) AS mes, "
                    "SUM(l.valor) AS total "
                    "FROM lancamentos l "
                    "WHERE l.condominio_id = %s AND l.tipo = 'despesa' "
                    "AND EXTRACT(YEAR FROM l.data_lancamento) = %s "
                    "GROUP BY l.categoria, mes ORDER BY l.categoria, mes",
                    (condominio_id, ano_sel),
                )
                despesas_mes_cat = cur.fetchall()

                matriz_desp = {}
                for r in despesas_mes_cat:
                    matriz_desp.setdefault(r["categoria"], {})[int(r["mes"])] = float(r["total"])

                somas_desp = [0.0] * 13
                total_desp = 0.0
                linhas_desp = ""
                for cat in sorted(matriz_desp.keys()):
                    linha = f"<tr><td style='text-align:left; padding:3px; border:1px solid #ccc;'>📉 {cat}</td>"
                    total_linha = 0.0
                    for m in range(1, 13):
                        v = matriz_desp[cat].get(m, 0.0)
                        total_linha += v
                        somas_desp[m] += v
                        linha += celula(v)
                    total_desp += total_linha
                    linha += f"<td style='text-align:right; padding:3px; border:1px solid #ccc; font-weight:bold; white-space:nowrap;'>{fmt_br(total_linha)}</td></tr>"
                    linhas_desp += linha
                if not linhas_desp:
                    linhas_desp = "<tr><td colspan='14' style='padding:3px; border:1px solid #ccc;'>Nenhuma despesa registrada.</td></tr>"
                linhas_desp += linha_total(somas_desp, total_desp)

                html_tabela_desp = f"""
                <h3>3) Despesas</h3>
                <table style="width:100%; border-collapse:collapse; font-size:0.8em;">
                    {cabecalho_meses("Categoria")}
                    {linhas_desp}
                </table>"""

                # ----- Totais de receitas/despesas por mês (consolidação) -----
                cur.execute(
                    "SELECT EXTRACT(MONTH FROM data_lancamento) AS mes, "
                    "COALESCE(SUM(valor) FILTER (WHERE tipo='receita'),0) AS rec, "
                    "COALESCE(SUM(valor) FILTER (WHERE tipo='despesa'),0) AS desp "
                    "FROM lancamentos WHERE condominio_id = %s "
                    "AND EXTRACT(YEAR FROM data_lancamento) = %s "
                    "GROUP BY mes ORDER BY mes",
                    (condominio_id, ano_sel),
                )
                totais_mes = cur.fetchall()
                receitas_mes = [0.0] * 13
                despesas_mes = [0.0] * 13
                for t in totais_mes:
                    m = int(t["mes"])
                    receitas_mes[m] = float(t["rec"])
                    despesas_mes[m] = float(t["desp"])

                saldo_anterior_mes = [0.0] * 13
                saldo_mes = [0.0] * 13
                saldo_acum_mes = [0.0] * 13
                try:
                    cur.execute("SELECT valor FROM saldos_iniciais WHERE condominio_id = %s AND mes = 1 AND ano = %s",
                                (condominio_id, ano_sel))
                    si_jan = cur.fetchone()
                    saldo_anterior_mes[1] = float(si_jan["valor"]) if si_jan else 0.0
                except Exception:
                    saldo_anterior_mes[1] = 0.0
                if saldo_anterior_mes[1] == 0.0:
                    saldo_anterior_mes[1] = saldo_acumulado_ate(condominio_id, cur, 12, ano_sel - 1)
                for m in range(1, 13):
                    saldo_mes[m] = receitas_mes[m] - despesas_mes[m]
                    saldo_acum_mes[m] = saldo_anterior_mes[m] + saldo_mes[m]
                    if m < 12:
                        saldo_anterior_mes[m + 1] = saldo_acum_mes[m]

                # ----- 4) Consolidação -----
                def linha_fluxo(rotulo, valores, destaque=False):
                    estilo = "font-weight:bold; background:#eef4fb;" if destaque else ""
                    linha = f"<tr style='{estilo}'><td style='text-align:left; padding:3px; border:1px solid #ccc;'>{rotulo}</td>"
                    for m in range(1, 13):
                        linha += celula(valores[m])
                    linha += f"<td style='text-align:right; padding:3px; border:1px solid #ccc; font-weight:bold; white-space:nowrap;'>{fmt_br(sum(valores[1:13]))}</td></tr>"
                    return linha

                linhas_fluxo = ""
                linhas_fluxo += linha_fluxo("Saldo anterior", saldo_anterior_mes)
                linhas_fluxo += linha_fluxo("(+) Receitas", receitas_mes)
                linhas_fluxo += linha_fluxo("(−) Despesas", despesas_mes)
                linhas_fluxo += linha_fluxo("(=) Saldo do mês", saldo_mes, destaque=True)
                linhas_fluxo += linha_fluxo("Saldo acumulado", saldo_acum_mes, destaque=True)

                html_tabela_fluxo = f"""
                <h3>4) Consolidação</h3>
                <table style="width:100%; border-collapse:collapse; font-size:0.8em;">
                    {cabecalho_meses("Rubrica")}
                    {linhas_fluxo}
                </table>"""

                html_tabela_mensal = html_tabela_contrib + html_tabela_outras + html_tabela_desp + html_tabela_fluxo

            rotulo_resumo = "5) Resumo do período"
            rotulo_dist = "6) Distribuição do saldo por conta"

            data_hoje = date.today().strftime("%d/%m/%Y")
            st.iframe(f"""
            <html><head><meta charset="utf-8"><title>{titulo_doc}</title></head>
            <body style="font-family:Arial,sans-serif; padding:20px;">
                {html_logo()}
                <h2 style="text-align:center;">{titulo_doc}</h2>
                <p style="text-align:center;">{nome_sel} — {titulo_periodo}</p>
                <hr>
                {html_receitas_mensal}
                {html_outras_receitas}
                {html_resumo_receitas}
                {html_despesas_mensal}
                {html_tabela_mensal}
                <h3>{rotulo_resumo}</h3>
                <table style="width:60%; border-collapse:collapse; font-size:0.9em;">
                    <tr><td style="padding:5px; border:1px solid #ccc;">Saldo do mês anterior</td><td style="text-align:right; padding:5px; border:1px solid #ccc; white-space:nowrap;">R$ {fmt_br(saldo_anterior)}</td></tr>
                    <tr><td style="padding:5px; border:1px solid #ccc;">(+) Receitas</td><td style="text-align:right; padding:5px; border:1px solid #ccc; white-space:nowrap;">R$ {fmt_br(total_receitas)}</td></tr>
                    <tr><td style="padding:5px; border:1px solid #ccc;">(−) Despesas</td><td style="text-align:right; padding:5px; border:1px solid #ccc; white-space:nowrap;">R$ {fmt_br(total_despesas)}</td></tr>
                    <tr style="background:#f0f0f0;"><td style="padding:5px; border:1px solid #ccc;">(=) Saldo do mês</td><td style="text-align:right; padding:5px; border:1px solid #ccc; white-space:nowrap;">R$ {fmt_br(saldo_periodo)}</td></tr>
                    <tr style="font-weight:bold; background:#eef4fb;"><td style="padding:5px; border:1px solid #ccc;">Saldo atual</td><td style="text-align:right; padding:5px; border:1px solid #ccc; white-space:nowrap;">R$ {fmt_br(saldo_atual)}</td></tr>
                </table>
                <h3>{rotulo_dist}</h3>
                <p style="font-size:12px; color:#555;">O saldo acumulado (R$ {fmt_br(saldo_atual)}) está distribuído nas contas abaixo.</p>
                <table style="width:100%; border-collapse:collapse; font-size:0.85em;">
                    <tr style="background:#1f3a5f; color:#fff;">
                        <th style="text-align:left; padding:5px; border:1px solid #ccc;">Banco</th>
                        <th style="text-align:left; padding:5px; border:1px solid #ccc;">Tipo</th>
                        <th style="text-align:left; padding:5px; border:1px solid #ccc;">Agência / Conta</th>
                        <th style="text-align:right; padding:5px; border:1px solid #ccc;">Saldo</th>
                    </tr>
                    {linhas_contas}
                    <tr style="font-weight:bold; background:#eef4fb;">
                        <td colspan="3" style="padding:5px; border:1px solid #ccc;">Total distribuído em contas</td>
                        <td style="text-align:right; padding:5px; border:1px solid #ccc; white-space:nowrap;">R$ {fmt_br(total_contas)}</td>
                    </tr>
                </table>
                <hr>
                <p style="text-align:center; font-size:12px;">Emitido em {data_hoje}</p>
                <script>window.print();</script>
            </body></html>""", height=700)

           
               # ===== EXPORTAÇÕES EXCEL / PDF =====
        st.markdown("---")
        st.subheader("📥 Exportar prestação de contas")

        c_exp1, c_exp2 = st.columns(2)
        with c_exp1:
            if st.button("📊 Exportar em Excel (.xlsx)", key="btn_exp_excel"):
                try:
                    gerar_excel_prestacao(
                        cur, conn, condominio_id, filtro_data, params_data,
                        saldo_anterior, total_receitas, total_despesas,
                        saldo_periodo, saldo_atual, titulo_doc, nome_sel,
                        titulo_periodo,
                    )
                except Exception as e:
                    st.error(f"Erro ao exportar Excel: {e}")
        with c_exp2:
            if st.button("📄 Exportar em PDF", key="btn_exp_pdf"):
                try:
                    gerar_pdf_prestacao(
                        cur, conn, condominio_id, filtro_data, params_data,
                        saldo_anterior, total_receitas, total_despesas,
                        saldo_periodo, saldo_atual, titulo_doc, nome_sel,
                        titulo_periodo,
                    )
                except Exception as e:
                    st.error(f"Erro ao exportar PDF: {e}")

        # ===== INADIMPLÊNCIA =====
elif pagina == "Inadimplência":
    banner("📋 Controle de inadimplência", "vermelho")
    if condominio_id is None:
        st.warning("Selecione um condomínio na barra lateral antes de consultar a inadimplência.")
    else:
        conn = get_connection(); cur = conn.cursor()
        hoje = date.today()
        c_m, c_a = st.columns(2)
        with c_m:
            mes_sel = st.selectbox("Mês", list(range(1, 13)), format_func=lambda m: MESES_NOMES[m - 1],
                                   index=hoje.month - 1, key="inad_mes")
        with c_a:
            anos = list(range(2028, 2024, -1))
            idx_ano = anos.index(hoje.year) if hoje.year in anos else 0
            ano_sel = st.selectbox("Ano", anos, index=idx_ano, key="inad_ano")

        cur.execute("SELECT DISTINCT nome FROM categorias WHERE condominio_id = %s AND tipo = 'receita' ORDER BY nome", (condominio_id,))
        cats_receita = [r["nome"] for r in cur.fetchall()]
        opcoes_taxa = list(cats_receita)
        for padrao in ("Taxa de condomínio", "Taxa de garagem"):
            if padrao not in opcoes_taxa:
                opcoes_taxa.append(padrao)
        default_taxa = [c for c in ("Taxa de condomínio", "Taxa de garagem") if c in opcoes_taxa] or [opcoes_taxa[0]]
        taxas_sel = st.multiselect("Categorias consideradas (taxa de condomínio e garagem)", opcoes_taxa,
                                   default=default_taxa, key="inad_taxas")
        if not taxas_sel:
            st.warning("Selecione ao menos uma categoria para o controle.")
            cur.close(); conn.close(); st.stop()

        cur.execute("SELECT id, numero, bloco, proprietario, telefone FROM apartamentos "
                    "WHERE condominio_id = %s ORDER BY numero", (condominio_id,))
        aptos = cur.fetchall()
        placeholders = ",".join(["%s"] * len(taxas_sel))
        cur.execute(f"SELECT apartamento_id, valor, categoria FROM lancamentos "
                    f"WHERE condominio_id = %s AND tipo = 'receita' AND LOWER(categoria) IN ({placeholders}) "
                    f"AND EXTRACT(MONTH FROM data_lancamento) = %s AND EXTRACT(YEAR FROM data_lancamento) = %s "
                    f"AND apartamento_id IS NOT NULL",
                    (condominio_id, *[t.lower() for t in taxas_sel], mes_sel, ano_sel))
        pagamentos = cur.fetchall()
        pagamentos_por_apto = {}
        for p in pagamentos:
            pagamentos_por_apto.setdefault(p["apartamento_id"], []).append(p)
        pagantes = [a for a in aptos if a["id"] in pagamentos_por_apto]
        inadimplentes = [a for a in aptos if a["id"] not in pagamentos_por_apto]
        valor_recebido = sum(float(p["valor"]) for ps in pagamentos_por_apto.values() for p in ps)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Apartamentos", len(aptos))
        c2.metric("Em dia", len(pagantes))
        c3.metric("Inadimplentes", len(inadimplentes))
        c4.metric("Recebido (R$)", fmt_br(valor_recebido))

        st.markdown("---")
        st.subheader(f"🟢 Em dia — {MESES_NOMES[mes_sel - 1]}/{ano_sel}")
        if pagantes:
            for a in pagantes:
                bloco_txt = f" - Bloco {a['bloco']}" if a["bloco"] else ""
                valores = ", ".join(f"R$ {fmt_br(p['valor'])}" for p in pagamentos_por_apto[a["id"]])
                st.write(f"**{a['numero']}**{bloco_txt} — {a['proprietario'] or 'sem proprietário'} — {valores}")
        else:
            st.info("Nenhum apartamento em dia neste mês.")

        st.markdown("---")
        st.subheader(f"🔴 Inadimplentes — {MESES_NOMES[mes_sel - 1]}/{ano_sel}")
        if inadimplentes:
            for a in inadimplentes:
                bloco_txt = f" - Bloco {a['bloco']}" if a["bloco"] else ""
                st.write(f"**{a['numero']}**{bloco_txt} — {a['proprietario'] or 'sem proprietário'} — {a['telefone'] or ''}")
        else:
            st.success("🎉 Todos os apartamentos pagaram as taxas neste mês!")

        st.markdown("---")
        st.subheader("📧 Aviso de cobrança em massa")
        if inadimplentes:
            st.caption(f"{len(inadimplentes)} apartamento(s) inadimplente(s) no mês selecionado.")
            mensagem_cobranca = st.text_area(
                "Mensagem do aviso",
                value=f"Prezado(a) condômino(a),\n\nIdentificamos que a taxa de condomínio referente a "
                      f"{MESES_NOMES[mes_sel - 1]}/{ano_sel} encontra-se em aberto.\n\n"
                      f"Solicitamos a regularização o quanto antes.\n\nAtenciosamente,\nAdministração do condomínio.",
                key="cobranca_msg",
            )
            if st.button("📤 Enviar aviso de cobrança aos inadimplentes", key="btn_cobranca"):
                import smtplib
                from email.mime.text import MIMEText
                from email.mime.multipart import MIMEMultipart

                cur.execute("SELECT email, senha_email FROM condominios WHERE id = %s", (condominio_id,))
                reg_email = cur.fetchone()
                email_rem = reg_email["email"] if reg_email and "email" in reg_email else None
                senha_rem = reg_email["senha_email"] if reg_email and "senha_email" in reg_email else None
                smtp_host = os.getenv("SMTP_HOST", "")
                smtp_port = int(os.getenv("SMTP_PORT", "587"))

                if not smtp_host or not email_rem or not senha_rem:
                    st.error("E-mail/SMTP não configurado. Cadastre o e-mail de comunicação no módulo Condomínio "
                             "e configure SMTP_HOST/SMTP_PORT no .env.")
                else:
                    enviados, falhas = 0, []
                    for a in inadimplentes:
                        cur.execute("SELECT email FROM apartamentos WHERE id = %s", (a["id"],))
                        reg_dest = cur.fetchone()
                        email_dest = reg_dest["email"] if reg_dest and reg_dest["email"] else None
                        if not email_dest:
                            falhas.append(f"Apto {a['numero']}: sem e-mail cadastrado")
                            continue
                        try:
                            msg = MIMEMultipart()
                            msg["From"] = email_rem
                            msg["To"] = email_dest
                            msg["Subject"] = f"Aviso de cobrança — {MESES_NOMES[mes_sel - 1]}/{ano_sel}"
                            msg.attach(MIMEText(mensagem_cobranca, "plain", "utf-8"))
                            with smtplib.SMTP(smtp_host, smtp_port) as server:
                                server.starttls()
                                server.login(email_rem, senha_rem)
                                server.sendmail(email_rem, email_dest, msg.as_string())
                            enviados += 1
                        except Exception as ex:
                            falhas.append(f"Apto {a['numero']}: {ex}")
                    registrar_auditoria(cur, "lancamentos", None, "INSERT",
                                        f"Aviso de cobrança enviado a {enviados} inadimplente(s) de {MESES_NOMES[mes_sel - 1]}/{ano_sel}")
                    conn.commit()
                    if enviados:
                        st.success(f"✅ Aviso enviado para {enviados} inadimplente(s).")
                    if falhas:
                        st.warning("Falhas:\n" + "\n".join(falhas))
        else:
            st.success("🎉 Nenhum inadimplente — nada a cobrar.")

        st.markdown("---")
        if st.button("🖨️ Imprimir Relatório de Inadimplência"):
            linhas_em_dia = ""
            for a in pagantes:
                bloco_txt = f" - Bloco {a['bloco']}" if a["bloco"] else ""
                valores = ", ".join(f"R$ {fmt_br(p['valor'])}" for p in pagamentos_por_apto[a["id"]])
                linhas_em_dia += f"<tr><td>{a['numero']}{bloco_txt}</td><td>{a['proprietario'] or '—'}</td><td>{a['telefone'] or '—'}</td><td style='text-align:right;'>{valores}</td></tr>"
            if not linhas_em_dia:
                linhas_em_dia = "<tr><td colspan='4'>Nenhum apartamento em dia.</td></tr>"
            linhas_inad = ""
            for a in inadimplentes:
                bloco_txt = f" - Bloco {a['bloco']}" if a["bloco"] else ""
                linhas_inad += f"<tr><td>{a['numero']}{bloco_txt}</td><td>{a['proprietario'] or '—'}</td><td>{a['telefone'] or '—'}</td><td style='text-align:right;'>Em atraso</td></tr>"
            if not linhas_inad:
                linhas_inad = "<tr><td colspan='4'>Nenhum apartamento inadimplente.</td></tr>"
            st.iframe(f"""
            <html><head><meta charset="utf-8"><title>Relatório de Inadimplência</title></head>
            <body style="font-family:Arial,sans-serif; padding:20px;">
                {html_logo()}
                <h2 style="text-align:center;">RELATÓRIO DE INADIMPLÊNCIA</h2>
                <p style="text-align:center; font-weight:bold;">{nome_sel}</p>
                <p style="text-align:center;">{MESES_NOMES[mes_sel - 1]} de {ano_sel}</p>
                <p style="text-align:center; font-weight:bold; color:#1f3a5f; font-size:14px;">Data de geração: {date.today().strftime('%d/%m/%Y')}</p>
                <hr>
                <table style="width:100%; border-collapse:collapse; margin-bottom:15px;">
                    <tr style="background:#1f3a5f; color:white;">
                        <th style="padding:8px; border:1px solid #ccc;">Apartamentos</th>
                        <th style="padding:8px; border:1px solid #ccc;">Em dia</th>
                        <th style="padding:8px; border:1px solid #ccc;">Inadimplentes</th>
                        <th style="padding:8px; border:1px solid #ccc;">Recebido (R$)</th>
                    </tr>
                    <tr>
                        <td style="text-align:center; padding:8px; border:1px solid #ccc;">{len(aptos)}</td>
                        <td style="text-align:center; padding:8px; border:1px solid #ccc;">{len(pagantes)}</td>
                        <td style="text-align:center; padding:8px; border:1px solid #ccc;">{len(inadimplentes)}</td>
                        <td style="text-align:center; padding:8px; border:1px solid #ccc;">R$ {fmt_br(valor_recebido)}</td>
                    </tr>
                </table>
                <h3>🟢 Em dia</h3>
                <table style="width:100%; border-collapse:collapse;">
                    <tr style="background:#f0f0f0;"><th style="text-align:left; padding:6px; border:1px solid #ccc;">Apartamento</th><th style="text-align:left; padding:6px; border:1px solid #ccc;">Proprietário</th><th style="text-align:left; padding:6px; border:1px solid #ccc;">Telefone</th><th style="text-align:right; padding:6px; border:1px solid #ccc;">Valor pago</th></tr>
                    {linhas_em_dia}
                </table>
                <h3>🔴 Inadimplentes</h3>
                <table style="width:100%; border-collapse:collapse;">
                    <tr style="background:#f0f0f0;"><th style="text-align:left; padding:6px; border:1px solid #ccc;">Apartamento</th><th style="text-align:left; padding:6px; border:1px solid #ccc;">Proprietário</th><th style="text-align:left; padding:6px; border:1px solid #ccc;">Telefone</th><th style="text-align:right; padding:6px; border:1px solid #ccc;">Situação</th></tr>
                    {linhas_inad}
                </table>
                <hr>
                <p style="text-align:center; font-size:12px;">Emitido em {date.today().strftime('%d/%m/%Y')}</p>
                <table style="width:100%; margin-top:40px;">
                    <tr>
                        <td style="text-align:center; width:50%;"><p style="margin-top:60px; border-top:1px solid #000; display:inline-block; padding-top:6px;">Síndico(a)</p></td>
                        <td style="text-align:center; width:50%;"><p style="margin-top:60px; border-top:1px solid #000; display:inline-block; padding-top:6px;">Administração</p></td>
                    </tr>
                </table>
                <script>window.print();</script>
            </body></html>""", height=700)
        cur.close(); conn.close()

    # ===== USUÁRIOS =====

if perfil_atual != "master":
        st.warning("🔒 Acesso restrito ao usuário Master.")
        st.stop()

elif pagina == "Usuários":
    if perfil_atual != "master":
        st.warning("🔒 Acesso restrito ao usuário Master.")
        st.stop()
    banner("👥 Usuários do sistema", "roxo")
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id, nome FROM condominios ORDER BY nome")
    conds = cur.fetchall()
    opcoes_cond = {c["nome"]: c["id"] for c in conds}

    with st.form("novo_usuario"):
        st.subheader("Cadastrar síndico / operador")
        u_nome = st.text_input("Nome completo *")
        u_usuario = st.text_input("Usuário de login *")
        u_senha = st.text_input("Senha *", type="password",
                                help="Mínimo de 6 caracteres. A senha é gravada como hash SHA-256.")
        u_perfil = st.selectbox("Perfil", ["sindico", "operador"])
        if opcoes_cond:
            u_cond = st.selectbox("Condomínio vinculado *", list(opcoes_cond.keys()))
            u_cond_id = opcoes_cond[u_cond]
        else:
            u_cond_id = None
            st.caption("Cadastre um condomínio antes de criar usuários.")
        salvar_u = st.form_submit_button("Salvar usuário")
    if salvar_u:
        if not u_nome.strip() or not u_usuario.strip() or not u_senha:
            st.error("Preencha nome, usuário e senha.")
        elif len(u_senha) < 6:
            st.error("A senha deve ter pelo menos 6 caracteres.")
        elif u_cond_id is None:
            st.error("Selecione o condomínio vinculado.")
        else:
            try:
                senha_hash = hash_senha(u_senha)
                cur.execute("INSERT INTO usuarios (usuario, senha, nome, perfil, condominio_id, ativo) "
                            "VALUES (%s, %s, %s, %s, %s, TRUE) RETURNING id",
                            (u_usuario.strip(), senha_hash, u_nome.strip(), u_perfil, u_cond_id))
                novo_u_id = cur.fetchone()["id"]
                registrar_auditoria(cur, "usuarios", novo_u_id, "INSERT",
                                    f"Usuário '{u_usuario.strip()}' criado como {u_perfil}")
                conn.commit()
                st.success(f"Usuário '{u_usuario.strip()}' cadastrado como {u_perfil}!")
            except Exception as e:
                conn.rollback(); st.error(f"Erro ao cadastrar: {e}")

    st.markdown("---")
    st.subheader("Usuários cadastrados")
    cur.execute("SELECT u.id, u.usuario, u.nome, u.perfil, u.condominio_id, u.ativo, c.nome AS condominio_nome "
                "FROM usuarios u LEFT JOIN condominios c ON c.id = u.condominio_id "
                "ORDER BY u.perfil, u.nome")
    usuarios = cur.fetchall()
    if usuarios:
        for u in usuarios:
            if u["perfil"] == "master":
                perfil_txt = "👑 Master"
            elif u["perfil"] == "sindico":
                perfil_txt = "🧑‍💼 Síndico"
            else:
                perfil_txt = "🛠️ Operador"
            cond_txt = u["condominio_nome"] or "—"
            status_txt = "✅ Ativo" if u["ativo"] else "⛔ Desativado"
            with st.expander(f"{u['nome']} ({u['usuario']}) — {perfil_txt} — {cond_txt} — {status_txt}"):
                with st.form(f"editar_usuario_{u['id']}"):
                    e_nome = st.text_input("Nome completo", value=u["nome"] or "")
                    e_usuario = st.text_input("Usuário de login", value=u["usuario"] or "")
                    opcoes_perfil = ["master", "sindico", "operador"]
                    idx_perfil = opcoes_perfil.index(u["perfil"]) if u["perfil"] in opcoes_perfil else 1
                    e_perfil = st.selectbox("Perfil", opcoes_perfil, index=idx_perfil)
                    idx_cond = list(opcoes_cond.values()).index(u["condominio_id"]) if u["condominio_id"] in opcoes_cond.values() else 0
                    e_cond = st.selectbox("Condomínio vinculado", list(opcoes_cond.keys()), index=idx_cond)
                    e_senha = st.text_input("Nova senha (deixe em branco para manter a atual)", type="password",
                                            help="Mínimo de 6 caracteres quando preenchida.")
                    e_ativo = st.checkbox("Usuário ativo (pode acessar o sistema)", value=bool(u["ativo"]))
                    col1, col2 = st.columns(2)
                    salvar_e = col1.form_submit_button("💾 Salvar alterações")
                    excluir_e = col2.form_submit_button("🗑️ Excluir usuário")
                if salvar_e:
                    if not e_nome.strip() or not e_usuario.strip():
                        st.error("Nome e usuário de login são obrigatórios.")
                    elif e_senha and len(e_senha) < 6:
                        st.error("A nova senha deve ter pelo menos 6 caracteres.")
                    elif not e_ativo and u["id"] == st.session_state.get("usuario_id"):
                        st.error("Você não pode desativar o próprio usuário logado.")
                    else:
                        novo_cond_id = None if e_perfil == "master" else opcoes_cond[e_cond]
                        try:
                            if e_senha:
                                senha_hash = hash_senha(e_senha)
                                cur.execute("UPDATE usuarios SET nome=%s, usuario=%s, perfil=%s, "
                                            "condominio_id=%s, senha=%s, ativo=%s WHERE id=%s",
                                            (e_nome.strip(), e_usuario.strip(), e_perfil,
                                             novo_cond_id, senha_hash, e_ativo, u["id"]))
                            else:
                                cur.execute("UPDATE usuarios SET nome=%s, usuario=%s, perfil=%s, "
                                            "condominio_id=%s, ativo=%s WHERE id=%s",
                                            (e_nome.strip(), e_usuario.strip(), e_perfil,
                                             novo_cond_id, e_ativo, u["id"]))
                            registrar_auditoria(cur, "usuarios", u["id"], "UPDATE",
                                                f"Usuário '{e_usuario.strip()}' atualizado")
                            conn.commit(); st.success("Usuário atualizado!"); st.rerun()
                        except Exception as ex:
                            conn.rollback(); st.error(f"Erro ao atualizar: {ex}")
                if excluir_e:
                    if u["id"] == st.session_state.get("usuario_id"):
                        st.error("Você não pode excluir o próprio usuário logado.")
                    else:
                        cur.execute("DELETE FROM usuarios WHERE id = %s", (u["id"],))
                        registrar_auditoria(cur, "usuarios", u["id"], "DELETE",
                                            f"Usuário '{u['usuario']}' excluído")
                        conn.commit(); st.success("Usuário excluído!"); st.rerun()
    else:
        st.info("Nenhum usuário cadastrado.")
    cur.close(); conn.close()

# ===== COMUNICAÇÃO =====
elif pagina == "Comunicação":
    banner("📧 Comunicação — envio de documentos", "verde")
    if condominio_id is None:
        st.warning("Selecione um condomínio na barra lateral.")
    else:
        conn = get_connection(); cur = conn.cursor()
        email_cond = None
        senha_cond = None
        try:
            cur.execute("SELECT email, senha_email FROM condominios WHERE id = %s", (condominio_id,))
            reg_cond = cur.fetchone()
            if reg_cond:
                email_cond = reg_cond["email"] if "email" in reg_cond else None
                senha_cond = reg_cond["senha_email"] if "senha_email" in reg_cond else None
        except Exception:
            email_cond = None
            senha_cond = None
        cur.execute("SELECT DISTINCT LOWER(TRIM(email)) AS email, 'Proprietário' AS tipo, numero, bloco, proprietario AS nome "
                    "FROM apartamentos WHERE condominio_id = %s AND email IS NOT NULL AND TRIM(email) <> '' "
                    "UNION "
                    "SELECT DISTINCT LOWER(TRIM(m.email)) AS email, 'Morador principal' AS tipo, a.numero, a.bloco, m.nome "
                    "FROM moradores m JOIN apartamentos a ON a.id = m.apartamento_id "
                    "WHERE a.condominio_id = %s AND m.is_principal = TRUE AND m.email IS NOT NULL AND TRIM(m.email) <> '' "
                    "ORDER BY nome", (condominio_id, condominio_id))
        destinatarios = cur.fetchall()
        cur.close(); conn.close()

        if not email_cond:
            st.warning("Este condomínio não possui e-mail de comunicação cadastrado. "
                       "Cadastre o e-mail e a senha no módulo Condomínio para habilitar o envio.")

        st.markdown("### 1️⃣ Documento a enviar")
        arquivo = st.file_uploader("Anexar documento (PDF, imagem, etc.)",
                                   type=["pdf", "png", "jpg", "jpeg", "docx", "xlsx", "txt"], key="com_arquivo")
        assunto = st.text_input("Assunto do e-mail", value="Comunicado do condomínio", key="com_assunto")
        mensagem = st.text_area("Mensagem",
                                value="Olá,\n\nSegue em anexo o documento.\n\nAtenciosamente,\nAdministração do condomínio.",
                                key="com_mensagem")

        st.markdown("### 2️⃣ Destinatários (proprietários e moradores principais)")
        st.caption("Somente proprietários e moradores principais com e-mail cadastrado.")
        if destinatarios:
            opcoes_dest = {}
            for d in destinatarios:
                opcoes_dest[f"{d['nome']} — Apto {d['numero']}" + (f" Bloco {d['bloco']}" if d["bloco"] else "") +
                            f" ({d['tipo']}) — {d['email']}"] = d["email"]
            selecionados = st.multiselect("Selecione os destinatários", list(opcoes_dest.keys()), key="com_dest")
            st.caption(f"{len(destinatarios)} destinatário(s) cadastrado(s).")
        else:
            selecionados = []
            st.info("Nenhum proprietário/morador principal com e-mail cadastrado.")

        if st.button("📤 Enviar documento por e-mail", key="com_enviar"):
            if arquivo is None:
                st.error("Anexe um documento para enviar.")
            elif not selecionados:
                st.error("Selecione ao menos um destinatário.")
            else:
                import smtplib
                from email import encoders
                from email.mime.base import MIMEBase
                from email.mime.multipart import MIMEMultipart
                from email.mime.text import MIMEText

                smtp_host = os.getenv("SMTP_HOST", "")
                smtp_port = int(os.getenv("SMTP_PORT", "587"))
                smtp_user = email_cond or os.getenv("SMTP_USER", "")
                smtp_pass = senha_cond or os.getenv("SMTP_PASSWORD", "")
                remetente = email_cond or os.getenv("SMTP_FROM", smtp_user)

                if not smtp_host or not smtp_user or not smtp_pass:
                    st.error("E-mail/SMTP não configurado. Cadastre o e-mail e a senha de comunicação no "
                             "módulo Condomínio e configure SMTP_HOST e SMTP_PORT no arquivo .env.")
                else:
                    enviados, falhas = 0, []
                    for rotulo in selecionados:
                        email_dest = opcoes_dest[rotulo]
                        try:
                            msg = MIMEMultipart()
                            msg["From"] = remetente
                            msg["To"] = email_dest
                            msg["Subject"] = assunto
                            msg.attach(MIMEText(mensagem, "plain", "utf-8"))
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(arquivo.getvalue())
                            encoders.encode_base64(part)
                            part.add_header("Content-Disposition", f'attachment; filename="{arquivo.name}"')
                            msg.attach(part)
                            with smtplib.SMTP(smtp_host, smtp_port) as server:
                                server.starttls()
                                server.login(smtp_user, smtp_pass)
                                server.sendmail(remetente, email_dest, msg.as_string())
                            enviados += 1
                        except Exception as ex:
                            falhas.append(f"{email_dest}: {ex}")
                    if enviados:
                        st.success(f"✅ Documento enviado para {enviados} destinatário(s).")
                    if falhas:
                        st.error("Falhas no envio:\n" + "\n".join(falhas))

# ===== BANCOS =====
elif pagina == "Bancos":
    banner("🏦 Contas bancárias", "amarelo")
    if condominio_id is None:
        st.warning("Selecione um condomínio na barra lateral antes de cadastrar contas bancárias.")
    else:
        conn = get_connection(); cur = conn.cursor()
        cur.execute("SELECT tipo, COUNT(*) AS total FROM contas_bancarias WHERE condominio_id = %s GROUP BY tipo", (condominio_id,))
        contagem = {r["tipo"]: r["total"] for r in cur.fetchall()}
        n_corrente = contagem.get("corrente", 0)
        n_poupanca = contagem.get("poupanca", 0)
        st.caption(f"Contas cadastradas: {n_corrente}/3 contas correntes | {n_poupanca}/1 poupança")

        with st.form("nova_conta"):
            st.subheader("Cadastrar conta")
            c_tipo = st.selectbox("Tipo", ["Conta corrente", "Poupança"])
            c_banco = st.text_input("Banco *")
            c_agencia = st.text_input("Agência")
            c_numero = st.text_input("Número da conta")
            c_saldo = st.number_input("Saldo atual (R$)", min_value=0.0, step=100.0, format="%.2f")
            salvar_conta = st.form_submit_button("Salvar conta")
        if salvar_conta:
            tipo_db = "corrente" if c_tipo == "Conta corrente" else "poupanca"
            limite = 3 if tipo_db == "corrente" else 1
            if not c_banco.strip():
                st.error("Informe o nome do banco.")
            elif (n_corrente if tipo_db == "corrente" else n_poupanca) >= limite:
                st.error(f"Limite atingido: máximo de {limite} conta(s) de {c_tipo.lower()}.")
            else:
                try:
                    cur.execute("INSERT INTO contas_bancarias (condominio_id, tipo, banco, agencia, numero_conta, saldo) "
                                "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                                (condominio_id, tipo_db, c_banco.strip(), c_agencia.strip() or None,
                                 c_numero.strip() or None, c_saldo))
                    novo_c_id = cur.fetchone()["id"]
                    registrar_auditoria(cur, "contas_bancarias", novo_c_id, "INSERT",
                                        f"Conta {c_tipo} {c_banco.strip()} criada")
                    conn.commit(); st.success("Conta cadastrada com sucesso!")
                except Exception as e:
                    conn.rollback(); st.error(f"Erro ao cadastrar: {e}")

        st.subheader("Contas cadastradas")
        cur.execute("SELECT id, tipo, banco, agencia, numero_conta, saldo "
                    "FROM contas_bancarias WHERE condominio_id = %s ORDER BY tipo, banco", (condominio_id,))
        contas = cur.fetchall()
        if contas:
            total_geral = 0.0
            for c in contas:
                icone = "🏦" if c["tipo"] == "corrente" else "🐷"
                st.write(f"{icone} **{c['banco']}** ({c['tipo']}) — Ag {c['agencia'] or '—'} "
                         f"Conta {c['numero_conta'] or '—'} — **R$ {fmt_br(c['saldo'])}**")
                total_geral += float(c["saldo"])
            st.write(f"**Total em contas: R$ {fmt_br(total_geral)}**")
        else:
            st.info("Nenhuma conta cadastrada. Cadastre até 3 contas correntes e 1 poupança.")

        if contas:
            st.subheader("Atualizar saldo")
            opcoes_conta = {f"{c['banco']} ({c['tipo']})": c["id"] for c in contas}
            conta_sel = st.selectbox("Conta", list(opcoes_conta.keys()), key="banco_sel")
            conta_id = opcoes_conta[conta_sel]
            conta_atual = next(c for c in contas if c["id"] == conta_id)
            with st.form("atualizar_saldo"):
                novo_saldo = st.number_input("Novo saldo (R$)", min_value=0.0, step=100.0, format="%.2f",
                                             value=float(conta_atual["saldo"] or 0))
                salvar_saldo = st.form_submit_button("Atualizar saldo")
            if salvar_saldo:
                cur.execute("UPDATE contas_bancarias SET saldo = %s, atualizado_em = CURRENT_TIMESTAMP WHERE id = %s",
                            (novo_saldo, conta_id))
                registrar_auditoria(cur, "contas_bancarias", conta_id, "UPDATE",
                                    f"Saldo da conta {conta_atual['banco']} = R$ {fmt_br(novo_saldo)}")
                conn.commit(); st.success("Saldo atualizado!"); st.rerun()
        cur.close(); conn.close()

# ===== AUDITORIA =====

if perfil_atual != "master":
        st.warning("🔒 Acesso restrito ao usuário Master.")
        st.stop()

elif pagina == "Auditoria":
    if perfil_atual != "master":
        st.warning("🔒 Acesso restrito ao usuário Master.")
        st.stop()
    banner("🔍 Log de auditoria", "roxo")
    conn = get_connection(); cur = conn.cursor()
    st.caption("Registro de todas as ações de criação, alteração e exclusão realizadas no sistema.")

    filtro_tabela = st.selectbox("Filtrar por tabela", ["Todas", "condominios", "apartamentos", "moradores",
                                                        "veiculos", "pets", "empregadas", "lancamentos",
                                                        "contas_bancarias", "usuarios", "distribuicao_contas",
                                                        "saldos_iniciais", "categorias", "prestacao_contas"],
                                 key="aud_tabela")
    filtro_acao = st.selectbox("Filtrar por ação", ["Todas", "INSERT", "UPDATE", "DELETE"], key="aud_acao")
    limite = st.selectbox("Quantidade de registros", [50, 100, 200, 500], index=1, key="aud_limite")

    sql = "SELECT id, usuario_nome, tabela, registro_id, acao, detalhes, data_hora FROM auditoria WHERE 1=1"
    params = []
    if filtro_tabela != "Todas":
        sql += " AND tabela = %s"
        params.append(filtro_tabela)
    if filtro_acao != "Todas":
        sql += " AND acao = %s"
        params.append(filtro_acao)
    sql += " ORDER BY data_hora DESC, id DESC LIMIT %s"
    params.append(limite)
    cur.execute(sql, params)
    registros = cur.fetchall()

    if registros:
        st.write(f"**{len(registros)} registro(s) encontrado(s)**")
        for r in registros:
            cor_acao = {"INSERT": "🟢", "UPDATE": "🟡", "DELETE": "🔴"}.get(r["acao"], "⚪")
            st.markdown(
                f"**{cor_acao} {r['acao']}** — `{r['tabela']}` (id {r['registro_id'] or '—'}) — "
                f"{r['usuario_nome']} — {r['data_hora'].strftime('%d/%m/%Y %H:%M')}"
            )
            if r["detalhes"]:
                st.caption(r["detalhes"])
            st.markdown("---")

        if st.button("📥 Exportar auditoria em Excel", key="btn_exp_aud"):
            try:
                import pandas as pd
                df_aud = pd.DataFrame([{
                    "Data/Hora": r["data_hora"],
                    "Usuário": r["usuario_nome"],
                    "Tabela": r["tabela"],
                    "Registro ID": r["registro_id"],
                    "Ação": r["acao"],
                    "Detalhes": r["detalhes"],
                } for r in registros])
                with pd.ExcelWriter("auditoria.xlsx", engine="openpyxl") as writer:
                    df_aud.to_excel(writer, sheet_name="Auditoria", index=False)
                with open("auditoria.xlsx", "rb") as f:
                    st.download_button("💾 Baixar auditoria.xlsx", f.read(),
                                       file_name="auditoria.xlsx",
                                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            except Exception as e:
                st.error(f"Erro ao exportar auditoria: {e}")
    else:
        st.info("Nenhum registro de auditoria encontrado com os filtros selecionados.")
    cur.close(); conn.close()

