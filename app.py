import os
import hmac
import base64
import logging
import psycopg2
import streamlit as st
import pandas as pd
import urllib.parse
import urllib.request

logging.basicConfig(level=logging.ERROR)

# ==========================================
# 1. CONFIGURAÇÃO VISUAL SIMPLIFICADA
# ==========================================
st.set_page_config(page_title="JR Admin", page_icon="💡", layout="centered")

st.markdown("""
    <style>
    .block-container { max-width: 500px !important; padding-top: 2rem !important; }
    #MainMenu, header, footer { display: none !important; }
    
    .mobile-card {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .badge-critico { background:#fee2e2; color:#991b1b; padding:4px 8px; border-radius:4px; font-weight:bold; font-size:0.8rem; }
    .badge-atencao { background:#fef3c7; color:#92400e; padding:4px 8px; border-radius:4px; font-weight:bold; font-size:0.8rem; }
    .badge-ok { background:#dcfce7; color:#166534; padding:4px 8px; border-radius:4px; font-weight:bold; font-size:0.8rem; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONEXÃO SEGURA COM O BANCO DE DADOS
# ==========================================
def obter_config(chave, padrao=None):
    if os.getenv(chave): return os.getenv(chave)
    try:
        if chave in st.secrets: return str(st.secrets[chave])
    except: pass
    return padrao

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=obter_config("DB_HOST"),
            port=obter_config("DB_PORT", "5432"),
            database=obter_config("DB_NAME", "postgres"),
            user=obter_config("DB_USER"),
            password=obter_config("DB_PASS"),
            sslmode="require"
        )
        conn.cursor().execute("SET TIME ZONE 'America/Sao_Paulo';")
        conn.commit()
        return conn
    except Exception as e:
        st.error(f"Erro de conexão: Verifique as variáveis de ambiente (Secrets).")
        st.stop()

@st.cache_data(ttl=5)
def buscar_dados(query, params=None):
    try:
        conn = get_db_connection()
        df = pd.read_sql(query, conn, params=params) if params else pd.read_sql(query, conn)
        conn.close()
        return df
    except: return pd.DataFrame()

def executar_comando(query, params=None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params) if params else cursor.execute(query)
        conn.commit()
        conn.close()
        st.cache_data.clear()
        return True
    except: return False

def validar_login(usuario, senha):
    au, ap = obter_config("ADMIN_USER", "admin"), obter_config("ADMIN_PASS", "123456")
    return hmac.compare_digest(usuario.strip(), au) and hmac.compare_digest(senha, ap)

# ==========================================
# 3. TELA DE LOGIN
# ==========================================
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h2 style='text-align:center;'>💡 JR Iluminação</h2><p style='text-align:center;'>Painel de Gestão</p>", unsafe_allow_html=True)
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    
    if st.button("Entrar", type="primary", use_container_width=True):
        if validar_login(usuario, senha):
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Credenciais inválidas.")

# ==========================================
# 4. PAINEL PRINCIPAL
# ==========================================
else:
    c1, c2 = st.columns([3, 1])
    c1.markdown("### 💡 JR Admin")
    if c2.button("Sair", use_container_width=True):
        st.session_state["autenticado"] = False
        st.rerun()

    menu = st.radio("Navegação", ["Resumo", "Produtos", "Preditivo", "Pedidos", "Clientes"], horizontal=True, label_visibility="collapsed")
    st.write("---")

    # --- RESUMO ---
    if menu == "Resumo":
        st.subheader("Métricas da Loja")
        df_ped = buscar_dados("SELECT COUNT(id) as qtd, SUM(total) as fat FROM pedidos WHERE status != 'Cancelado'")
        df_prod = buscar_dados("SELECT SUM(quantidade) as est FROM produtos")
        
        col1, col2 = st.columns(2)
        col1.metric("Faturamento", f"R$ {float(df_ped['fat'].iloc[0] or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        col2.metric("Total de Pedidos", str(df_ped['qtd'].iloc[0] or 0))
        
        col3, col4 = st.columns(2)
        col3.metric("Estoque Total", f"{int(df_prod['est'].iloc[0] or 0)} un.")
        col4.metric("Status do Sistema", "Online 🟢")

    # --- PRODUTOS ---
    elif menu == "Produtos":
        st.subheader("Gerenciar Estoque")
        acao = st.selectbox("Ação", ["Listar", "Adicionar"])
        
        if acao == "Listar":
            df = buscar_dados("SELECT * FROM produtos ORDER BY id DESC")
            for _, r in df.iterrows():
                st.markdown(f"<div class='mobile-card'><b>{r['nome']}</b><br>Preço: R$ {r['preco']:.2f} | Estoque: {r['quantidade']} un.</div>", unsafe_allow_html=True)
                
        elif acao == "Adicionar":
            nome = st.text_input("Nome")
            cat = st.selectbox("Categoria", ["Lâmpadas", "Fitas LED", "Plafons", "Spots", "Outros"])
            preco = st.number_input("Preço (R$)", min_value=0.1)
            qtd = st.number_input("Quantidade", min_value=0, step=1)
            if st.button("Salvar Produto", type="primary"):
                if nome:
                    executar_comando("INSERT INTO produtos (nome, categoria, preco, quantidade, imagem) VALUES (%s, %s, %s, %s, 'placeholder.jpg')", (nome, cat, preco, qtd))
                    st.success("Produto cadastrado!"); st.rerun()

    # --- PREDITIVO SIMPLIFICADO ---
    elif menu == "Preditivo":
        st.subheader("Controle Inteligente de Estoque")
        st.caption("Cálculo direto de Ponto de Reposição e Alertas de Ruptura.")
        
        dias = st.slider("Analisar vendas dos últimos X dias:", 7, 60, 30)
        lead_time = 5 # Tempo que o fornecedor demora a entregar
        
        query = """
            SELECT p.id, p.nome, COALESCE(p.quantidade, 0) as estoque,
                   COALESCE(SUM(CASE WHEN ped.status != 'Cancelado' AND ped.data_pedido >= NOW() - (%s * INTERVAL '1 day') THEN ip.quantidade ELSE 0 END), 0) as vendido
            FROM produtos p
            LEFT JOIN itens_pedido ip ON ip.produto_id = p.id
            LEFT JOIN pedidos ped ON ped.id = ip.pedido_id
            GROUP BY p.id, p.nome, p.quantidade
            ORDER BY estoque ASC
        """
        df = buscar_dados(query, params=(dias,))
        
        if not df.empty:
            df['consumo_diario'] = df['vendido'] / dias
            df['dias_restantes'] = df.apply(lambda r: int(r['estoque'] / r['consumo_diario']) if r['consumo_diario'] > 0 else 999, axis=1)
            df['ponto_reposicao'] = (df['consumo_diario'] * lead_time).round().astype(int) + 2
            
            df = df.sort_values(by='dias_restantes', ascending=True)
            
            for _, r in df.iterrows():
                if r['dias_restantes'] <= lead_time: badge = f"<span class='badge-critico'>🚨 Crítico ({r['dias_restantes']} dias)</span>"
                elif r['dias_restantes'] <= 15: badge = f"<span class='badge-atencao'>⚠️ Atenção ({r['dias_restantes']} dias)</span>"
                else: badge = f"<span class='badge-ok'>✅ Saudável</span>"
                
                st.markdown(f"""
                    <div class='mobile-card'>
                        <div style='display:flex; justify-content:space-between; margin-bottom:8px;'>
                            <b>{r['nome']}</b> {badge}
                        </div>
                        <span style='font-size: 0.9rem;'>
                            Estoque Atual: <b>{r['estoque']} un.</b> | Vendidos: <b>{int(r['vendido'])} un.</b><br>
                            Repor quando o estoque chegar a: <b style='color:#b91c1c;'>{r['ponto_reposicao']} un.</b>
                        </span>
                    </div>
                """, unsafe_allow_html=True)

    # --- PEDIDOS ---
    elif menu == "Pedidos":
        st.subheader("Gestão de Pedidos")
        acao = st.selectbox("Ação", ["Listar", "Atualizar Status"])
        
        if acao == "Listar":
            df = buscar_dados("SELECT p.id, c.nome, p.status, p.total FROM pedidos p JOIN clientes c ON p.cliente_id = c.id ORDER BY p.id DESC")
            for _, r in df.iterrows():
                st.markdown(f"<div class='mobile-card'><b>Pedido #{r['id']} - {r['nome']}</b><br>Status: {r['status']} | Total: R$ {r['total']:.2f}</div>", unsafe_allow_html=True)
                
        elif acao == "Atualizar Status":
            df = buscar_dados("SELECT id, status FROM pedidos ORDER BY id DESC")
            if not df.empty:
                opcoes = {f"Pedido #{r['id']} (Atual: {r['status']})": r['id'] for _, r in df.iterrows()}
                ped_id = opcoes[st.selectbox("Selecione o Pedido", list(opcoes.keys()))]
                novo_status = st.selectbox("Novo Status", ["Pendente", "Em processamento", "Enviado", "Entregue", "Cancelado"])
                if st.button("Atualizar"):
                    executar_comando("UPDATE pedidos SET status = %s WHERE id = %s", (novo_status, ped_id))
                    st.success("Atualizado!"); st.rerun()

    # --- CLIENTES ---
    elif menu == "Clientes":
        st.subheader("Aprovação de Clientes")
        df = buscar_dados("SELECT id, nome, email FROM usuarios WHERE status = 'Pendente' AND role = 'cliente'")
        if not df.empty:
            for _, r in df.iterrows():
                st.markdown(f"<div class='mobile-card'><b>{r['nome']}</b><br>{r['email']}</div>", unsafe_allow_html=True)
                if st.button(f"Aprovar Conta #{r['id']}", key=f"btn_{r['id']}"):
                    executar_comando("UPDATE usuarios SET status = 'Aprovado' WHERE id = %s", (r['id'],))
                    st.success("Aprovado!"); st.rerun()
        else:
            st.info("Nenhuma conta pendente de aprovação.")
