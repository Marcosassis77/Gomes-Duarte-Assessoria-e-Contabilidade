import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def gerar_dados_financeiros():
    """Gera histórico mensal de receitas e despesas para o ano de 2024."""
    datas = pd.date_range(start="2024-01-01", end="2024-12-01", freq="MS")
    
    np.random.seed(42)
    
    receitas = np.random.randint(45000, 85000, size=len(datas))
    despesas = np.random.randint(20000, 45000, size=len(datas))
    
    df = pd.DataFrame({
        "Data": datas,
        "Mês": datas.strftime("%b/%Y"),
        "Receita": receitas,
        "Despesa": despesas,
        "Lucro": receitas - despesas
    })
    
    df["Crescimento_Receita_%"] = df["Receita"].pct_change() * 100
    df["Crescimento_Receita_%"] = df["Crescimento_Receita_%"].fillna(0).round(2)
    
    return df

def gerar_dados_operacionais():
    """Gera lista de pendências e tarefas contábeis."""
    categorias = ["Fiscal", "Pessoal (DP)", "Contábil", "Societário"]
    status_lista = ["Concluído", "Em Andamento", "Atrasado", "Pendente"]
    clientes = [f"Empresa {chr(i)} Ltda" for i in range(65, 75)]
    
    np.random.seed(42)
    
    dados = []
    for i in range(1, 31):
        cliente = np.random.choice(clientes)
        cat = np.random.choice(categorias)
        status = np.random.choice(status_lista, p=[0.4, 0.3, 0.15, 0.15])
        prazo = datetime.now() + timedelta(days=int(np.random.randint(-10, 20)))
        
        dados.append({
            "ID": f"TRF-{i:03d}",
            "Cliente": cliente,
            "Categoria": cat,
            "Obrigação / Tarefa": f"Entrega de Declaração - {cat}",
            "Prazo": prazo.strftime("%d/%m/%Y"),
            "Status": status
        })
        
    return pd.DataFrame(dados)