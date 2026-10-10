import io
import os
import base64
import sqlite3
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# =============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA E CSS DE ALTO CONTRASTE SOBRE A IMAGEM DE FUNDO
# =============================================================================
st.set_page_config(
    page_title="Gomes Duarte | Gestão Contábil",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def buscar_e_converter_imagem_fundo():
    """Busca o arquivo da imagem de fundo (.jpg, .jpeg, .png)."""
    for nome_arquivo in ["fundo.jpg", "fundo.jpeg", "fundo.png", "image_db8b8c3.jpeg"]:
        if os.path.exists(nome_arquivo):
            with open(nome_arquivo, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode("utf-8")
    return None

fundo_b64 = buscar_e_converter_imagem_fundo()

# CSS Ajustado para Leitura Nítida
bg_css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }}

    /* Imagem de Fundo com Overlay Escuro para Contraste Impecável */
    .stApp {{
        background: {'linear-gradient(rgba(15, 23, 42, 0.85), rgba(15, 23, 42, 0.85)), url("data:image/jpeg;base64,' + fundo_b64 + '")' if fundo_b64 else '#0F172A'} !important;
        background-size: cover !important;
        background-position: center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
        color: #F8FAFC !important;
    }}

    /* Textos Principais em Branco de Alto Contraste */
    h1, h2, h3, p, span, label {{
        color: #F8FAFC !important;
    }}

    /* Sidebar Limpa e Profissional */
    [data-testid="stSidebar"] {{
        background-color: #0B0F19 !important;
        border-right: 1px solid #1E293B !important;
    }}
    [data-testid="stSidebar"] * {{
        color: #F8FAFC !important;
    }}
    [data-testid="stSidebar"] .stRadio label {{
        color: #E2E8F0 !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        padding: 6px 0 !important;
    }}

    .brand-header {{
        text-align: center;
        padding: 10px 0 15px 0;
        border-bottom: 1px solid #1E293B;
        margin-bottom: 15px;
    }}

    .brand-logo-circle {{
        width: 110px;
        height: 110px;
        background: #1E293B;
        border: 2px solid #10B981;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin: 0 auto 10px auto;
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.25);
    }}
    .brand-logo-title {{
        font-size: 0.45rem;
        font-weight: 800;
        color: #FFFFFF !important;
        letter-spacing: 0.5px;
    }}
    .brand-logo-gd {{
        font-size: 1.8rem;
        font-weight: 900;
        color: #10B981 !important;
        line-height: 1;
        letter-spacing: -1px;
    }}
    .brand-logo-sub {{
        font-size: 0.4rem;
        font-weight: 700;
        color: #94A3B8 !important;
    }}

    /* Cards Indicadores Nítidos */
    .saas-card {{
        background-color: rgba(30, 41, 59, 0.9) !important;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px 22px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        margin-bottom: 15px;
    }}
    .saas-card-label {{
        font-size: 0.78rem;
        font-weight: 700;
        color: #CBD5E1 !important;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 8px;
    }}
    .saas-card-value {{
        font-size: 1.85rem;
        font-weight: 800;
        color: #FFFFFF !important;
        letter-spacing: -0.5px;
        margin-bottom: 8px;
    }}
    .badge-success {{
        display: inline-block;
        background-color: rgba(16, 185, 129, 0.2);
        color: #34D399 !important;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 700;
    }}
    .badge-danger {{
        display: inline-block;
        background-color: rgba(239, 68, 68, 0.2);
        color: #F87171 !important;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 700;
    }}

    /* Expanders e Formulários */
    .stExpander {{
        background-color: rgba(30, 41, 59, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
    }}

    /* Tabelas */
    .stDataFrame {{
        background-color: rgba(30, 41, 59, 0.9) !important;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}

    /* Botões */
    .stButton>button, .stDownloadButton>button {{
        background-color: #10B981 !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        padding: 8px 20px !important;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
        transition: all 0.2s ease;
    }}
    .stButton>button:hover, .stDownloadButton>button:hover {{
        background-color: #059669 !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.5);
    }}
    </style>
"""
st.markdown(bg_css, unsafe_allow_html=True)

# =============================================================================
# 2. BANCO DE DADOS PERSISTENTE (SQLITE)
# =============================================================================
DB_NAME = "gomes_duarte_saas.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(force_reseed=False):
    conn = get_db_connection()
    cursor = conn.cursor()

    if force_reseed:
        cursor.execute("DROP TABLE IF EXISTS movimentacoes")
        cursor.execute("DROP TABLE IF EXISTS clientes")
        cursor.execute("DROP TABLE IF EXISTS tarefas")
        conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE,
        tipo TEXT,
        nome_empresarial TEXT,
        nome_fantasia TEXT,
        cpf_cnpj TEXT UNIQUE,
        ie_im TEXT,
        email TEXT,
        telefone TEXT,
        whatsapp TEXT,
        endereco TEXT,
        segmento TEXT,
        servicos TEXT,
        honorario REAL,
        vencimento_dia INTEGER,
        situacao TEXT,
        responsavel TEXT,
        data_inicio TEXT,
        observacoes TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movimentacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT,
        competencia TEXT,
        descricao TEXT,
        tipo TEXT,
        categoria TEXT,
        cliente_id INTEGER,
        fornecedor TEXT,
        valor REAL,
        situacao TEXT,
        vencimento TEXT,
        data_pagamento TEXT,
        conta_financeira TEXT,
        forma_pagamento TEXT,
        observacoes TEXT,
        FOREIGN KEY (cliente_id) REFERENCES clientes (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tarefas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE,
        cliente_id INTEGER,
        categoria TEXT,
        obrigacao TEXT,
        competencia TEXT,
        prazo TEXT,
        prioridade TEXT,
        responsavel TEXT,
        status TEXT,
        data_conclusao TEXT,
        observacoes TEXT,
        FOREIGN KEY (cliente_id) REFERENCES clientes (id)
    )
    """)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM clientes")
    if cursor.fetchone()[0] == 0:
        seed_initial_data(conn)

    conn.close()

def seed_initial_data(conn):
    cursor = conn.cursor()
    np.random.seed(42)

    segmentos = ["Simples Nacional", "Lucro Presumido", "Saúde & Médicos", "Advogados", "Comércio", "Tecnologia"]
    responsaveis = ["Carlos Silva", "Fernanda Lima", "Roberto Gomes", "Juliana Duarte"]
    servicos_list = ["Contábil + Fiscal", "Completo (DP+Fiscal+Contábil)", "BPO Financeiro", "Consultoria Tributária"]

    for i in range(1, 16):
        nome = f"Empresa {chr(65 + i)} Ltda"
        codigo = f"CLI-{i:03d}"
        doc = f"{np.random.randint(10,99)}.383.683/0001-{i:02d}"
        cursor.execute("""
            INSERT INTO clientes (codigo, tipo, nome_empresarial, nome_fantasia, cpf_cnpj, ie_im, email, telefone, whatsapp, endereco, segmento, servicos, honorario, vencimento_dia, situacao, responsavel, data_inicio, observacoes)
            VALUES (?, 'PJ', ?, ?, ?, 'ISENTO', ?, '(24) 99240-8530', '(24) 99240-8530', 'Resende - RJ', ?, ?, ?, 10, 'Ativo', ?, '2024-01-15', 'Cliente base demonstrativa')
        """, (codigo, nome, f"Fantasia {chr(65+i)}", doc, f"contato@empresa{i}.com", np.random.choice(segmentos), np.random.choice(servicos_list), float(np.random.choice([1800, 2500, 3800, 5200])), np.random.choice(responsaveis)))

    conn.commit()

    meses_2026 = ["01/2026", "02/2026", "03/2026", "04/2026", "05/2026", "06/2026", "07/2026", "08/2026", "09/2026", "10/2026", "11/2026", "12/2026"]
    
    for m in meses_2026:
        mes_num, ano_num = m.split("/")
        for c_id in range(1, 16):
            val = float(cursor.execute("SELECT honorario FROM clientes WHERE id=?", (c_id,)).fetchone()[0])
            st_rec = "Recebido" if int(mes_num) < 10 else ("Recebido" if np.random.rand() > 0.2 else "Pendente")
            cursor.execute("""
                INSERT INTO movimentacoes (data, competencia, descricao, tipo, categoria, cliente_id, valor, situacao, vencimento, conta_financeira, forma_pagamento)
                VALUES (?, ?, 'Honorário Mensal Contábil', 'Receita', 'Honorários Contábeis', ?, ?, ?, ?, 'Banco Itaú', 'PIX / Boleto')
            """, (f"{ano_num}-{mes_num}-10", m, c_id, val, st_rec, f"{ano_num}-{mes_num}-10"))

        despesas_fixas = [
            ("Folha de Pagamento da Equipe", "Pessoal / Folha", 18500),
            ("Encargos e Impostos do Escritório", "Impostos & Taxas", 6200),
            ("Sistemas Contábeis & Licenças Software", "Sistemas & Software", 4100),
            ("Aluguel & Condomínio da Sede", "Infraestrutura", 4800),
            ("Marketing Digital & Vendas", "Marketing", 2500)
        ]
        for desc, cat, val_base in despesas_fixas:
            v_real = float(val_base + np.random.randint(-200, 400))
            cursor.execute("""
                INSERT INTO movimentacoes (data, competencia, descricao, tipo, categoria, valor, situacao, vencimento, conta_financeira, forma_pagamento)
                VALUES (?, ?, ?, 'Despesa', ?, ?, 'Pago', ?, 'Banco Itaú', 'Transferência')
            """, (f"{ano_num}-{mes_num}-05", m, desc, cat, v_real, f"{ano_num}-{mes_num}-05"))

    conn.commit()

    cats_obrig = ["Gestão Contábil", "Departamento Pessoal", "Planejamento Tributário", "Abertura & Legalização", "Imposto de Renda"]
    status_opcoes = ["Concluído", "Em Andamento", "Pendente", "Atrasado"]
    
    for i in range(1, 31):
        c_id = np.random.randint(1, 16)
        cat = np.random.choice(cats_obrig)
        st_t = np.random.choice(status_opcoes, p=[0.45, 0.3, 0.15, 0.10])
        cursor.execute("""
            INSERT INTO tarefas (codigo, cliente_id, categoria, obrigacao, competencia, prazo, prioridade, responsavel, status)
            VALUES (?, ?, ?, ?, '10/2026', ?, 'Média', ?, ?)
        """, (f"TRF-{i:03d}", c_id, cat, f"Entrega de Declaração / Rotina - {cat}", f"2026-10-{np.random.randint(1,28):02d}", np.random.choice(responsaveis), st_t))

    conn.commit()

def db_carregar_clientes():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM clientes ORDER BY id DESC", conn)
    conn.close()
    return df

def db_carregar_movimentacoes():
    conn = get_db_connection()
    df = pd.read_sql_query("""
        SELECT m.*, c.nome_empresarial as cliente_nome 
        FROM movimentacoes m 
        LEFT JOIN clientes c ON m.cliente_id = c.id
        ORDER BY m.vencimento DESC
    """, conn)
    conn.close()
    return df

def db_carregar_tarefas():
    conn = get_db_connection()
    df = pd.read_sql_query("""
        SELECT t.*, c.nome_empresarial as cliente_nome 
        FROM tarefas t 
        LEFT JOIN clientes c ON t.cliente_id = c.id
        ORDER BY t.prazo ASC
    """, conn)
    conn.close()
    return df

def db_salvar_cliente(dados):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO clientes (codigo, tipo, nome_empresarial, nome_fantasia, cpf_cnpj, ie_im, email, telefone, whatsapp, endereco, segmento, servicos, honorario, vencimento_dia, situacao, responsavel, data_inicio, observacoes)
        VALUES (:codigo, :tipo, :nome_empresarial, :nome_fantasia, :cpf_cnpj, :ie_im, :email, :telefone, :whatsapp, :endereco, :segmento, :servicos, :honorario, :vencimento_dia, :situacao, :responsavel, :data_inicio, :observacoes)
    """, dados)
    conn.commit()
    conn.close()

def db_salvar_movimentacao(dados):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO movimentacoes (data, competencia, descricao, tipo, categoria, cliente_id, fornecedor, valor, situacao, vencimento, conta_financeira, forma_pagamento, observacoes)
        VALUES (:data, :competencia, :descricao, :tipo, :categoria, :cliente_id, :fornecedor, :valor, :situacao, :vencimento, :conta_financeira, :forma_pagamento, :observacoes)
    """, dados)
    conn.commit()
    conn.close()

def db_salvar_tarefa(dados):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tarefas (codigo, cliente_id, categoria, obrigacao, competencia, prazo, prioridade, responsavel, status, observacoes)
        VALUES (:codigo, :cliente_id, :categoria, :obrigacao, :competencia, :prazo, :prioridade, :responsavel, :status, :observacoes)
    """, dados)
    conn.commit()
    conn.close()

init_db()

# =============================================================================
# 3. SIDEBAR COM LOGO E MENU
# =============================================================================

if os.path.exists("logo.png"):
    col_l1, col_l2, col_l3 = st.sidebar.columns([1, 3, 1])
    with col_l2:
        st.image("logo.png", use_container_width=True)
    st.sidebar.markdown("""
        <div style="text-align: center; padding-bottom: 15px; border-bottom: 1px solid #1E293B; margin-bottom: 15px;">
            <p style="margin: 0; font-size: 0.85rem; font-weight: 700; color: #FFFFFF !important;">Gomes Duarte HQ</p>
            <p style="margin: 2px 0 0 0; font-size: 0.72rem; color: #94A3B8 !important;">Resende - RJ</p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("""
        <div class="brand-header">
            <div class="brand-logo-circle">
                <div class="brand-logo-title">GOMES DUARTE</div>
                <div class="brand-logo-gd">GD</div>
                <div class="brand-logo-sub">CONTABILIDADE</div>
            </div>
            <p style="margin: 0; font-size: 0.85rem; font-weight: 700; color: #FFFFFF !important;">Gomes Duarte HQ</p>
            <p style="margin: 2px 0 0 0; font-size: 0.72rem; color: #94A3B8 !important;">Resende - RJ</p>
        </div>
    """, unsafe_allow_html=True)

modulo = st.sidebar.radio(
    "Menu de Navegação:",
    [
        "Visão Geral Executiva",
        "Carteira de Clientes (CRM)",
        "Gestão Financeira",
        "Indicadores Analytics",
        "Central de Obrigações",
        "Exportação de Relatórios"
    ]
)

st.sidebar.divider()

df_cli_raw = db_carregar_clientes()
df_mov_raw = db_carregar_movimentacoes()
df_tar_raw = db_carregar_tarefas()

competencias_disponiveis = sorted(list(df_mov_raw["competencia"].unique()), reverse=True)
if not competencias_disponiveis:
    competencias_disponiveis = ["10/2026"]

mes_sel = st.sidebar.selectbox("Competência de Referência:", competencias_disponiveis, index=0)

st.sidebar.write("")
if st.sidebar.button("Restaurar Base Demo"):
    init_db(force_reseed=True)
    st.sidebar.success("Base de dados restaurada!")
    st.rerun()

st.sidebar.markdown("""
    <div style="font-size: 0.72rem; color: #64748B !important; line-height: 1.5; padding-top: 15px;">
        CNPJ: 65.383.683/0001-59<br/>
        Tel: (24) 99240-8530
    </div>
""", unsafe_allow_html=True)

# =============================================================================
# 4. CONTEÚDO DOS MÓDULOS
# =============================================================================

# --- VISÃO GERAL EXECUTIVA ---
if modulo == "Visão Geral Executiva":
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <h1 style="margin:0; font-size: 1.85rem; color: #FFFFFF !important; font-weight: 800;">Painel de Indicadores Contábeis</h1>
            <p style="margin: 4px 0 0 0; color: #CBD5E1 !important; font-size: 0.95rem; font-weight: 500;">Gomes Duarte Assessoria e Contabilidade Resende — Visão executiva em tempo real.</p>
        </div>
    """, unsafe_allow_html=True)

    df_mes = df_mov_raw[df_mov_raw["competencia"] == mes_sel]
    rec_total = df_mes[df_mes["tipo"] == "Receita"]["valor"].sum()
    desp_total = df_mes[df_mes["tipo"] == "Despesa"]["valor"].sum()
    saldo_liquido = rec_total - desp_total
    margem_liq = (saldo_liquido / rec_total * 100) if rec_total > 0 else 0
    inadimplente_val = df_mes[(df_mes["tipo"] == "Receita") & (df_mes["situacao"] == "Pendente")]["valor"].sum()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
            <div class="saas-card">
                <div class="saas-card-label">Faturamento Total</div>
                <div class="saas-card-value">R$ {rec_total:,.2f}</div>
                <div class="badge-success">Receita Realizada / Prevista</div>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
            <div class="saas-card">
                <div class="saas-card-label">Despesas Operacionais</div>
                <div class="saas-card-value">R$ {desp_total:,.2f}</div>
                <div class="saas-card-label" style="margin-top:2px;">Custos do Período</div>
            </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
            <div class="saas-card">
                <div class="saas-card-label">Resultado Líquido</div>
                <div class="saas-card-value" style="color: {'#34D399' if saldo_liquido>=0 else '#F87171'} !important;">R$ {saldo_liquido:,.2f}</div>
                <div class="badge-success">Margem Líquida: {margem_liq:.1f}%</div>
            </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
            <div class="saas-card">
                <div class="saas-card-label">Títulos Pendentes</div>
                <div class="saas-card-value" style="color: #F87171 !important;">R$ {inadimplente_val:,.2f}</div>
                <div class="badge-danger">Aguardando Pagamento</div>
            </div>
        """, unsafe_allow_html=True)

    st.write("")

    g1, g2 = st.columns([2, 1])

    with g1:
        st.subheader("Evolução Financeira (Receitas x Despesas)")
        df_evol = df_mov_raw.groupby(["competencia", "tipo"])["valor"].sum().unstack(fill_value=0).reset_index()
        if "Receita" not in df_evol.columns: df_evol["Receita"] = 0
        if "Despesa" not in df_evol.columns: df_evol["Despesa"] = 0

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_evol["competencia"], y=df_evol["Receita"], name="Receitas",
            line=dict(color="#10B981", width=3.5),
            fill='tonexty', fillcolor='rgba(16, 185, 129, 0.08)'
        ))
        fig.add_trace(go.Scatter(
            x=df_evol["competencia"], y=df_evol["Despesa"], name="Despesas",
            line=dict(color="#EF4444", width=3)
        ))
        fig.update_layout(
            paper_bgcolor='rgba(15, 23, 42, 0.75)',
            plot_bgcolor='rgba(15, 23, 42, 0.75)',
            font=dict(color='#F8FAFC', size=12, family="Plus Jakarta Sans"),
            height=340,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='#F8FAFC', size=11))
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='#F8FAFC', size=11))
        st.plotly_chart(fig, use_container_width=True)

    with g2:
        st.subheader("Status das Obrigações")
        df_st = df_tar_raw["status"].value_counts().reset_index()
        fig_p = px.pie(
            df_st, values="count", names="status", hole=0.5,
            color="status",
            color_discrete_map={
                "Concluído": "#10B981",
                "Em Andamento": "#3B82F6",
                "Pendente": "#F59E0B",
                "Atrasado": "#EF4444"
            }
        )
        fig_p.update_layout(
            paper_bgcolor='rgba(15, 23, 42, 0.75)',
            plot_bgcolor='rgba(15, 23, 42, 0.75)',
            font=dict(color='#F8FAFC', size=12, family="Plus Jakarta Sans"),
            height=340,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02)
        )
        st.plotly_chart(fig_p, use_container_width=True)

# --- CARTEIRA DE CLIENTES (CRM) ---
elif modulo == "Carteira de Clientes (CRM)":
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <h1 style="margin:0; font-size: 1.85rem; color: #FFFFFF !important; font-weight: 800;">Carteira de Clientes (CRM Contábil)</h1>
            <p style="margin: 4px 0 0 0; color: #CBD5E1 !important; font-size: 0.95rem; font-weight: 500;">Gerenciamento de contratos e dados dos clientes da Gomes Duarte.</p>
        </div>
    """, unsafe_allow_html=True)
    st.divider()

    with st.expander("➕ Cadastrar Novo Cliente", expanded=False):
        with st.form("form_novo_cliente"):
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                tipo = st.selectbox("Tipo de Pessoa:", ["PJ - Pessoa Jurídica", "PF - Pessoa Física"])
                nome_emp = st.text_input("Razão Social / Nome Completo:*")
                nome_fant = st.text_input("Nome Fantasia:")
                cpf_cnpj = st.text_input("CPF / CNPJ:*")
            with col_f2:
                email = st.text_input("E-mail de Contato:")
                tel = st.text_input("Telefone / WhatsApp:")
                segmento = st.selectbox("Regime / Segmento:", ["Simples Nacional", "Lucro Presumido", "Saúde & Médicos", "Advogados", "Comércio", "Tecnologia"])
                servicos = st.selectbox("Serviço Contratado:", ["Contábil + Fiscal", "Completo (DP+Fiscal+Contábil)", "BPO Financeiro", "Consultoria Tributária"])
            with col_f3:
                honorario = st.number_input("Honorário Mensal (R$):*", min_value=0.0, value=2500.0, step=100.0)
                venc_dia = st.number_input("Dia de Vencimento:", min_value=1, max_value=31, value=10)
                responsavel = st.selectbox("Responsável Interno:", ["Carlos Silva", "Fernanda Lima", "Roberto Gomes", "Juliana Duarte"])
                situacao = st.selectbox("Situação Inicial:", ["Ativo", "Em Implantação", "Inativo"])

            obs = st.text_area("Observações Internas do Cliente:")

            submit_cli = st.form_submit_button("Salvar Cliente")
            if submit_cli:
                if not nome_emp or not cpf_cnpj:
                    st.error("Preencha os campos obrigatórios (Razão Social e CPF/CNPJ).")
                else:
                    cod_novo = f"CLI-{len(df_cli_raw)+1:03d}"
                    dados_c = {
                        "codigo": cod_novo, "tipo": tipo[:2], "nome_empresarial": nome_emp,
                        "nome_fantasia": nome_fant, "cpf_cnpj": cpf_cnpj, "ie_im": "ISENTO",
                        "email": email, "telefone": tel, "whatsapp": tel, "endereco": "Resende - RJ",
                        "segmento": segmento, "servicos": servicos, "honorario": honorario,
                        "vencimento_dia": venc_dia, "situacao": situacao, "responsavel": responsavel,
                        "data_inicio": datetime.now().strftime("%Y-%m-%d"), "observacoes": obs
                    }
                    db_salvar_cliente(dados_c)
                    st.success(f"Cliente {nome_emp} cadastrado com sucesso!")
                    st.rerun()

    st.subheader("Clientes Cadastrados")
    f_busca = st.text_input("Pesquisar cliente por Nome, Código ou CPF/CNPJ:")

    df_cli_filtrado = df_cli_raw.copy()
    if f_busca:
        df_cli_filtrado = df_cli_filtrado[
            df_cli_filtrado["nome_empresarial"].str.contains(f_busca, case=False, na=False) |
            df_cli_filtrado["codigo"].str.contains(f_busca, case=False, na=False) |
            df_cli_filtrado["cpf_cnpj"].str.contains(f_busca, case=False, na=False)
        ]

    st.dataframe(
        df_cli_filtrado[["codigo", "tipo", "nome_empresarial", "cpf_cnpj", "segmento", "servicos", "honorario", "situacao", "responsavel"]],
        use_container_width=True, hide_index=True
    )

# --- GESTÃO FINANCEIRA ---
elif modulo == "Gestão Financeira":
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <h1 style="margin:0; font-size: 1.85rem; color: #FFFFFF !important; font-weight: 800;">Gestão Financeira & Lançamentos</h1>
            <p style="margin: 4px 0 0 0; color: #CBD5E1 !important; font-size: 0.95rem; font-weight: 500;">Lançamentos de receitas e despesas operacionais.</p>
        </div>
    """, unsafe_allow_html=True)
    st.divider()

    with st.expander("➕ Registrar Nova Movimentação Financeira", expanded=False):
        with st.form("form_nova_mov"):
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                tipo_mov = st.selectbox("Tipo de Operação:", ["Receita", "Despesa"])
                desc_mov = st.text_input("Descrição do Lançamento:*")
                val_mov = st.number_input("Valor (R$):*", min_value=0.0, value=1500.0, step=100.0)
            with col_m2:
                cat_mov = st.selectbox("Categoria:", ["Honorários Contábeis", "Consultoria", "Pessoal / Folha", "Sistemas & Software", "Infraestrutura", "Impostos & Taxas"])
                cli_opts = ["Nenhum"] + list(df_cli_raw["nome_empresarial"].unique())
                cli_sel_mov = st.selectbox("Cliente Vinculado:", cli_opts)
            with col_m3:
                data_venc = st.date_input("Data de Vencimento:")
                st_mov = st.selectbox("Situação:", ["Recebido", "Pago", "Pendente", "Atrasado"])
                conta_mov = st.selectbox("Conta Financeira:", ["Banco Itaú", "Banco do Brasil", "Caixa Geral"])

            submit_mov = st.form_submit_button("Salvar Movimentação")
            if submit_mov:
                if not desc_mov or val_mov <= 0:
                    st.error("Informe uma descrição válida e valor maior que zero.")
                else:
                    c_id_val = None
                    if cli_sel_mov != "Nenhum":
                        c_id_val = int(df_cli_raw[df_cli_raw["nome_empresarial"] == cli_sel_mov]["id"].values[0])
                    
                    dt_venc_str = data_venc.strftime("%Y-%m-%d")
                    comp_str = data_venc.strftime("%m/%Y")
                    
                    dados_m = {
                        "data": dt_venc_str, "competencia": comp_str, "descricao": desc_mov,
                        "tipo": tipo_mov, "categoria": cat_mov, "cliente_id": c_id_val,
                        "fornecedor": "", "valor": val_mov, "situacao": st_mov,
                        "vencimento": dt_venc_str, "conta_financeira": conta_mov,
                        "forma_pagamento": "PIX / Boleto", "observacoes": "Lançado via painel"
                    }
                    db_salvar_movimentacao(dados_m)
                    st.success("Movimentação registrada com sucesso!")
                    st.rerun()

    st.subheader("Lançamentos do Mês Selecionado")
    df_mov_filtrado = df_mov_raw[df_mov_raw["competencia"] == mes_sel]
    
    st.dataframe(
        df_mov_filtrado[["data", "tipo", "descricao", "categoria", "cliente_nome", "valor", "situacao", "conta_financeira"]],
        use_container_width=True, hide_index=True
    )

# --- INDICADORES ANALYTICS ---
elif modulo == "Indicadores Analytics":
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <h1 style="margin:0; font-size: 1.85rem; color: #FFFFFF !important; font-weight: 800;">Indicadores Analytics & DRE</h1>
        </div>
    """, unsafe_allow_html=True)
    st.divider()

    df_dre = df_mov_raw.groupby(["competencia", "tipo"])["valor"].sum().unstack(fill_value=0).reset_index()
    if "Receita" not in df_dre.columns: df_dre["Receita"] = 0
    if "Despesa" not in df_dre.columns: df_dre["Despesa"] = 0

    df_dre["Resultado_Liquido"] = df_dre["Receita"] - df_dre["Despesa"]
    df_dre["Margem_%"] = (df_dre["Resultado_Liquido"] / df_dre["Receita"] * 100).fillna(0).round(1)

    c_a1, c_a2 = st.columns(2)
    with c_a1:
        st.subheader("Margem de Lucro Mensal (%)")
        fig_m = px.bar(df_dre, x="competencia", y="Margem_%", color_discrete_sequence=["#10B981"])
        fig_m.update_layout(paper_bgcolor='rgba(15, 23, 42, 0.75)', plot_bgcolor='rgba(15, 23, 42, 0.75)', font=dict(color='#F8FAFC'))
        fig_m.update_xaxes(tickfont=dict(color='#F8FAFC'))
        fig_m.update_yaxes(tickfont=dict(color='#F8FAFC'))
        st.plotly_chart(fig_m, use_container_width=True)

    with c_a2:
        st.subheader("Resultado Líquido Acumulado (R$)")
        fig_r = px.area(df_dre, x="competencia", y="Resultado_Liquido", color_discrete_sequence=["#3B82F6"])
        fig_r.update_layout(paper_bgcolor='rgba(15, 23, 42, 0.75)', plot_bgcolor='rgba(15, 23, 42, 0.75)', font=dict(color='#F8FAFC'))
        fig_r.update_xaxes(tickfont=dict(color='#F8FAFC'))
        fig_r.update_yaxes(tickfont=dict(color='#F8FAFC'))
        st.plotly_chart(fig_r, use_container_width=True)

    st.subheader("Demonstrativo do Resultado (DRE Simplificado)")
    st.dataframe(df_dre, use_container_width=True, hide_index=True)

# --- CENTRAL DE OBRIGAÇÕES ---
elif modulo == "Central de Obrigações":
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <h1 style="margin:0; font-size: 1.85rem; color: #FFFFFF !important; font-weight: 800;">Central de Obrigações Contábeis</h1>
        </div>
    """, unsafe_allow_html=True)
    st.divider()

    with st.expander("➕ Criar Nova Obrigação Contábil", expanded=False):
        with st.form("form_nova_tarefa"):
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                cli_t_opts = list(df_cli_raw["nome_empresarial"].unique()) if not df_cli_raw.empty else ["Nenhum"]
                cli_t_sel = st.selectbox("Cliente:", cli_t_opts)
                cat_t = st.selectbox("Categoria:", ["Gestão Contábil", "Departamento Pessoal", "Planejamento Tributário", "Abertura & Legalização", "Imposto de Renda"])
                obrig_desc = st.text_input("Descrição da Obrigação:*")
            with col_t2:
                prazo_t = st.date_input("Prazo de Vencimento:")
                prio_t = st.selectbox("Prioridade:", ["Alta", "Média", "Baixa"])
                resp_t = st.selectbox("Responsável:", ["Carlos Silva", "Fernanda Lima", "Roberto Gomes", "Juliana Duarte"])

            submit_t = st.form_submit_button("Salvar Obrigação")
            if submit_t:
                c_id_t = int(df_cli_raw[df_cli_raw["nome_empresarial"] == cli_t_sel]["id"].values[0]) if cli_t_sel != "Nenhum" else None
                cod_t = f"TRF-{len(df_tar_raw)+1:03d}"
                dados_t = {
                    "codigo": cod_t, "cliente_id": c_id_t, "categoria": cat_t,
                    "obrigacao": obrig_desc, "competencia": prazo_t.strftime("%m/%Y"),
                    "prazo": prazo_t.strftime("%Y-%m-%d"), "prioridade": prio_t,
                    "responsavel": resp_t, "status": "Pendente", "observacoes": "Gerado via painel"
                }
                db_salvar_tarefa(dados_t)
                st.success("Obrigação criada com sucesso!")
                st.rerun()

    st.subheader("Obrigações Cadastradas")
    st.dataframe(
        df_tar_raw[["codigo", "cliente_nome", "categoria", "obrigacao", "prazo", "prioridade", "responsavel", "status"]],
        use_container_width=True, hide_index=True
    )

# --- EXPORTAÇÃO DE RELATÓRIOS ---
elif modulo == "Exportação de Relatórios":
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <h1 style="margin:0; font-size: 1.85rem; color: #FFFFFF !important; font-weight: 800;">Exportação de Relatórios Consolidados</h1>
        </div>
    """, unsafe_allow_html=True)
    st.divider()

    out = io.BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
        df_mov_raw.to_excel(writer, sheet_name='Financeiro', index=False)
        df_cli_raw.to_excel(writer, sheet_name='Clientes', index=False)
        df_tar_raw.to_excel(writer, sheet_name='Obrigacoes', index=False)

    st.download_button(
        label="Baixar Relatório Consolidado para Excel (.xlsx)",
        data=out.getvalue(),
        file_name=f"Gomes_Duarte_Relatorio_{mes_sel.replace('/', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )