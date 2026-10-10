import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

DB_FILE = "gomes_duarte.db"

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db(force_reseed=False):
    """Inicializa as tabelas do banco de dados SQLite e popula dados fictícios consistentes (2026)."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if force_reseed:
        cursor.execute("DROP TABLE IF EXISTS movimentacoes")
        cursor.execute("DROP TABLE IF EXISTS clientes")
        cursor.execute("DROP TABLE IF EXISTS tarefas")
        conn.commit()

    # Tabela de Clientes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE,
        nome_empresarial TEXT,
        segmento TEXT,
        servicos TEXT,
        honorario REAL,
        status TEXT,
        data_inicio TEXT,
        responsavel TEXT
    )
    """)

    # Tabela de Movimentações Financeiras
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movimentacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT,
        competencia TEXT,
        descricao TEXT,
        tipo TEXT,
        categoria TEXT,
        cliente_id INTEGER,
        valor REAL,
        situacao TEXT,
        vencimento TEXT,
        FOREIGN KEY (cliente_id) REFERENCES clientes (id)
    )
    """)

    # Tabela de Tarefas e Obrigações Contábeis
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
        FOREIGN KEY (cliente_id) REFERENCES clientes (id)
    )
    """)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM clientes")
    if cursor.fetchone()[0] == 0:
        seed_data(conn)
    conn.close()

def seed_data(conn):
    """Gera base inicial demonstrativa sincronizada para o ano corrente (2026)."""
    cursor = conn.cursor()
    np.random.seed(42)

    # 1. Clientes
    segmentos = ["Comércio", "Serviços", "Indústria", "Tecnologia", "Saúde"]
    responsaveis = ["Carlos Silva", "Fernanda Lima", "Roberto Gomes", "Juliana Duarte"]
    servicos_list = ["Contábil + Fiscal", "Completo (DP+Fiscal+Contábil)", "BPO Financeiro", "Societário"]
    
    clientes_dados = []
    for i in range(1, 49):
        nome = f"Empresa {chr(65 + (i % 26))}{i:02d} Ltda"
        codigo = f"CLI-{i:03d}"
        seg = np.random.choice(segmentos)
        serv = np.random.choice(servicos_list)
        hon = float(np.random.choice([1200, 1800, 2500, 3200, 4500, 6000]))
        st = "Ativo" if i <= 45 else "Inativo"
        dt_ini = f"202{np.random.randint(1, 6)}-{np.random.randint(1, 13):02d}-01"
        resp = np.random.choice(responsaveis)
        
        cursor.execute("""
            INSERT INTO clientes (codigo, nome_empresarial, segmento, servicos, honorario, status, data_inicio, responsavel)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (codigo, nome, seg, serv, hon, st, dt_ini, resp))
    
    conn.commit()

    # 2. Movimentações Financeiras (Ano de 2026)
    cats_receita = ["Honorários Contábeis", "Consultoria", "Serviços Especiais"]
    cats_despesa = ["Pessoal / Folha", "Sistemas & Software", "Aluguel & Infraestrutura", "Impostos & Taxas", "Marketing & Vendas"]
    
    for mes in range(1, 11): # Jan a Out de 2026
        dt_base = datetime(2026, mes, 10)
        comp = f"{mes:02d}/2026"
        
        # Receitas
        for c_id in range(1, 46): # Clientes ativos
            val = float(cursor.execute("SELECT honorario FROM clientes WHERE id=?", (c_id,)).fetchone()[0])
            cursor.execute("""
                INSERT INTO movimentacoes (data, competencia, descricao, tipo, categoria, cliente_id, valor, situacao, vencimento)
                VALUES (?, ?, ?, 'Receita', 'Honorários Contábeis', ?, ?, 'Recebido', ?)
            """, (f"2026-{mes:02d}-10", comp, f"Honorário Mensal - {comp}", c_id, val, f"2026-{mes:02d}-10"))

        # Receitas Avulsas
        for _ in range(3):
            val_extra = float(np.random.randint(1500, 5000))
            cursor.execute("""
                INSERT INTO movimentacoes (data, competencia, descricao, tipo, categoria, cliente_id, valor, situacao, vencimento)
                VALUES (?, ?, 'Consultoria Tributária', 'Receita', 'Consultoria', ?, ?, 'Recebido', ?)
            """, (f"2026-{mes:02d}-15", comp, np.random.randint(1, 45), val_extra, f"2026-{mes:02d}-15"))

        # Despesas
        despesas_base = [
            ("Folha de Pagamento", "Pessoal / Folha", 18000),
            ("Encargos Sociais", "Pessoal / Folha", 6200),
            ("Aluguel do Escritório", "Aluguel & Infraestrutura", 4500),
            ("Licenças de Software Contábil", "Sistemas & Software", 3800),
            ("Marketing Digital", "Marketing & Vendas", 2200),
            ("Energia & Internet", "Aluguel & Infraestrutura", 1200)
        ]
        for desc, cat, v_base in despesas_base:
            v_real = float(v_base + np.random.randint(-300, 500))
            cursor.execute("""
                INSERT INTO movimentacoes (data, competencia, descricao, tipo, categoria, cliente_id, valor, situacao, vencimento)
                VALUES (?, ?, ?, 'Despesa', ?, NULL, ?, 'Pago', ?)
            """, (f"2026-{mes:02d}-05", comp, desc, cat, v_real, f"2026-{mes:02d}-05"))

    conn.commit()

    # 3. Tarefas e Obrigações Contábeis (Sincronizadas com Out/2026)
    cats_obrig = ["Fiscal", "Pessoal (DP)", "Contábil", "Societário"]
    status_opcoes = ["Concluído", "Em Andamento", "Pendente", "Atrasado"]
    prioridades = ["Baixa", "Média", "Alta", "Urgente"]
    
    for i in range(1, 40):
        c_id = np.random.randint(1, 45)
        cat = np.random.choice(cats_obrig)
        prio = np.random.choice(prioridades)
        st = np.random.choice(status_opcoes, p=[0.4, 0.3, 0.15, 0.15])
        resp = np.random.choice(responsaveis)
        
        # Prazos em torno de Outubro/2026
        dia = np.random.randint(1, 28)
        prazo_dt = datetime(2026, 10, dia)
        
        cursor.execute("""
            INSERT INTO tarefas (codigo, cliente_id, categoria, obrigacao, competencia, prazo, prioridade, responsavel, status)
            VALUES (?, ?, ?, ?, '10/2026', ?, ?, ?, ?)
        """, (f"TRF-{i:03d}", c_id, cat, f"Entrega de Declaração / Apuração - {cat}", prazo_dt.strftime("%Y-%m-%d"), prio, resp, st))

    conn.commit()

# --- Funções CRUD e Consultas ---

def carregar_dados_financeiros():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT m.*, c.nome_empresarial as cliente_nome 
        FROM movimentacoes m 
        LEFT JOIN clientes c ON m.cliente_id = c.id
    """, conn)
    conn.close()
    return df

def carregar_clientes():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM clientes", conn)
    conn.close()
    return df

def carregar_tarefas():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT t.*, c.nome_empresarial as cliente_nome 
        FROM tarefas t 
        LEFT JOIN clientes c ON t.cliente_id = c.id
    """, conn)
    conn.close()
    return df

def adicionar_movimentacao(data, competencia, descricao, tipo, categoria, cliente_id, valor, situacao, vencimento):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO movimentacoes (data, competencia, descricao, tipo, categoria, cliente_id, valor, situacao, vencimento)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (data, competencia, descricao, tipo, categoria, cliente_id, valor, situacao, vencimento))
    conn.commit()
    conn.close()

def adicionar_tarefa(codigo, cliente_id, categoria, obrigacao, competencia, prazo, prioridade, responsavel, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tarefas (codigo, cliente_id, categoria, obrigacao, competencia, prazo, prioridade, responsavel, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (codigo, cliente_id, categoria, obrigacao, competencia, prazo, prioridade, responsavel, status))
    conn.commit()
    conn.close()

def atualizar_status_tarefa(tarefa_id, novo_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tarefas SET status=? WHERE id=?", (novo_status, tarefa_id))
    conn.commit()
    conn.close()