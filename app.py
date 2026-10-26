import os
import hmac
import psycopg2
import streamlit as st
import pandas as pd

# ==========================================
# 1. CONFIGURAÇÃO BASE (SEM CONFLITOS DE COR)
# ==========================================
st.set_page_config(page_title="JR Admin", page_icon="💡", layout="centered")

# CSS focado apenas nos Cartões, respeitando o tema do Streamlit para o resto
st.markdown("""
    <style>
    .block-container { padding-top: 2rem !important; max-width: 600px !important; }
    #MainMenu, header, footer { display: none !important; }
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
        st.error("Erro de conexão com o Banco de Dados. Verifique os Secrets.")
        st.stop()

@st.cache_data(ttl=5)
def buscar_dados(query, params=None):
    try:
        conn = get_db_connection()
        df = pd.read_sql(query, conn, params=params) if params else pd.read_sql(query, conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

def executar_comando(query, params=None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params) if params else cursor.execute(query)
        conn.commit()
        conn.close()
        st.cache_data.clear()
        return True
    except:
        return False

def validar_login(usuario, senha):
    au, ap = obter_config("ADMIN_USER", "admin"), obter_config("ADMIN_PASS", "123456")
    return hmac.compare_digest(usuario.strip(), au) and hmac.compare_digest(senha, ap)

# ==========================================
# 3. TELA DE LOGIN
# ==========================================
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.title("💡 JR Iluminação")
    st.caption("Painel de Gestão e Inteligência")
    
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    
    if st.button("Entrar no Sistema", type="primary", use_container_width=True):
        if validar_login(usuario, senha):
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Credenciais inválidas.")

# ==========================================
# 4. PAINEL PRINCIPAL
# ==========================================
else:
    c1, c2 = st.columns([3, 1], vertical_alignment="center")
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
        col1.metric("Faturamento", f"R$ {float(df_ped['fat'].iloc[0] if not df_ped.empty and pd.notna(df_ped['fat'].iloc[0]) else 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        col2.metric("Total de Pedidos", str(df_ped['qtd'].iloc[0] if not df_ped.empty else 0))
        
        col3, col4 = st.columns(2)
        col3.metric("Estoque Total", f"{int(df_prod['est'].iloc[0] if not df_prod.empty and pd.notna(df_prod['est'].iloc[0]) else 0)} un.")
        col4.metric("Status do Sistema", "Online 🟢")

    # --- PRODUTOS ---
    elif menu == "Produtos":
        st.subheader("Gerenciar Estoque")
        acao = st.selectbox("Ação", ["Listar Todos", "Adicionar Novo"])
        
        if acao == "Listar Todos":
            df = buscar_dados("SELECT * FROM produtos ORDER BY id DESC")
            if not df.empty:
                for _, r in df.iterrows():
                    with st.container(border=True):
                        st.markdown(f"**{r['nome']}**")
                        st.caption(f"Preço: R$ {r['preco']:.2f} | Estoque: {r['quantidade']} unidades")
            else:
                st.info("Nenhum produto cadastrado.")
                
        elif acao == "Adicionar Novo":
            nome = st.text_input("Nome do Produto")
            cat = st.selectbox("Categoria", ["Lâmpadas", "Fitas LED", "Plafons", "Spots", "Outros"])
            preco = st.number_input("Preço (R$)", min_value=0.1)
            qtd = st.number_input("Quantidade em Estoque", min_value=0, step=1)
            if st.button("Salvar Produto", type="primary"):
                if nome:
                    if executar_comando("INSERT INTO produtos (nome, categoria, preco, quantidade, imagem) VALUES (%s, %s, %s, %s, 'placeholder.jpg')", (nome, cat, preco, qtd)):
                        st.success("Produto cadastrado com sucesso!"); st.rerun()
                else:
                    st.warning("Preencha o nome do produto.")

    # --- PREDITIVO DINÂMICO E VISUAL ---
    elif menu == "Preditivo":
        st.subheader("Inteligência de Suprimentos")
        st.caption("Previsão de ruptura baseada no ritmo real de vendas da loja.")
        
        col_dias, col_lead = st.columns(2)
        with col_dias: dias = st.slider("Histórico (dias):", 7, 60, 30)
        with col_lead: lead_time = st.number_input("Prazo do Fornecedor (dias):", 1, 30, 5)
        
        query = """
            SELECT p.id, p.nome, COALESCE(p.quantidade, 0) as estoque,
                   COALESCE(SUM(CASE WHEN ped.status != 'Cancelado' AND ped.data_pedido >= NOW() - (%s * INTERVAL '1 day') THEN ip.quantidade ELSE 0 END), 0) as vendido
            FROM produtos p
            LEFT JOIN itens_pedido ip ON ip.produto_id = p.id
            LEFT JOIN pedidos ped ON ped.id = ip.pedido_id
            GROUP BY p.id, p.nome, p.quantidade
        """
        df = buscar_dados(query, params=(dias,))
        
        if not df.empty:
            df['consumo_diario'] = df['vendido'] / dias
            df['dias_restantes'] = df.apply(lambda r: int(r['estoque'] / r['consumo_diario']) if r['consumo_diario'] > 0 else 999, axis=1)
            df['ponto_reposicao'] = (df['consumo_diario'] * lead_time).round().astype(int) + 2
            
            # Ordena para os mais críticos aparecerem primeiro
            df = df.sort_values(by='dias_restantes', ascending=True)
            
            for _, r in df.iterrows():
                # Definição de Cores Contrastantes baseada no risco
                if r['dias_restantes'] <= lead_time:
                    cor_borda, cor_fundo, status = "#dc2626", "#fef2f2", "🚨 Crítico"
                    acao_msg = f"Comprar hoje! O estoque vai zerar antes do fornecedor entregar."
                elif r['dias_restantes'] <= lead_time + 7:
                    cor_borda, cor_fundo, status = "#f59e0b", "#fffbeb", "⚠️ Atenção"
                    acao_msg = f"Fazer pedido em breve. Ao chegar em {r['ponto_reposicao']} un. inicie a compra."
                else:
                    cor_borda, cor_fundo, status = "#10b981", "#ecfdf5", "✅ Saudável"
                    acao_msg = f"Estoque seguro. Nenhuma ação necessária no momento."

                texto_dias = f"{r['dias_restantes']} dias" if r['dias_restantes'] != 999 else "+ de 1 ano"

                # HTML do Cartão Preditivo Dinâmico (Cores que não conflitam)
                st.markdown(f"""
                <div style="background-color: {cor_fundo}; padding: 16px; border-radius: 8px; border-left: 6px solid {cor_borda}; margin-bottom: 15px; border-right: 1px solid #e5e7eb; border-top: 1px solid #e5e7eb; border-bottom: 1px solid #e5e7eb;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <h4 style="margin: 0; color: #111827;">{r['nome']}</h4>
                        <span style="background: {cor_borda}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;">{status}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                        <div style="text-align: left;">
                            <p style="margin: 0; font-size: 12px; color: #6b7280; text-transform: uppercase;">Estoque</p>
                            <p style="margin: 0; font-size: 18px; font-weight: 800; color: #1f2937;">{r['estoque']} un.</p>
                        </div>
                        <div style="text-align: center;">
                            <p style="margin: 0; font-size: 12px; color: #6b7280; text-transform: uppercase;">Ritmo</p>
                            <p style="margin: 0; font-size: 18px; font-weight: 800; color: #1f2937;">{r['consumo_diario']:.1f} /dia</p>
                        </div>
                        <div style="text-align: right;">
                            <p style="margin: 0; font-size: 12px; color: #6b7280; text-transform: uppercase;">Zera em</p>
                            <p style="margin: 0; font-size: 18px; font-weight: 800; color: {cor_borda};">{texto_dias}</p>
                        </div>
                    </div>
                    <div style="background: rgba(255,255,255,0.6); padding: 8px; border-radius: 6px; font-size: 14px; color: #374151;">
                        💡 <b>Ação:</b> {acao_msg}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nenhum produto cadastrado para calcular.")

    # --- PEDIDOS ---
    elif menu == "Pedidos":
        st.subheader("Gestão de Pedidos")
        acao = st.selectbox("Ação", ["Listar Todos", "Atualizar Status"])
        
        if acao == "Listar Todos":
            df = buscar_dados("SELECT p.id, c.nome, p.status, p.total FROM pedidos p JOIN clientes c ON p.cliente_id = c.id ORDER BY p.id DESC")
            if not df.empty:
                for _, r in df.iterrows():
                    with st.container(border=True):
                        st.markdown(f"**Pedido #{r['id']} - {r['nome']}**")
                        st.caption(f"Status: {r['status']} | Total: R$ {r['total']:.2f}")
            else:
                st.info("Nenhum pedido encontrado.")
                
        elif acao == "Atualizar Status":
            df = buscar_dados("SELECT id, status FROM pedidos ORDER BY id DESC")
            if not df.empty:
                opcoes = {f"Pedido #{r['id']} (Atual: {r['status']})": r['id'] for _, r in df.iterrows()}
                ped_id = opcoes[st.selectbox("Selecione o Pedido", list(opcoes.keys()))]
                novo_status = st.selectbox("Novo Status", ["Pendente", "Em processamento", "Enviado", "Entregue", "Cancelado"])
                if st.button("Atualizar Status", type="primary"):
                    if executar_comando("UPDATE pedidos SET status = %s WHERE id = %s", (novo_status, ped_id)):
                        st.success("Pedido atualizado com sucesso!"); st.rerun()
            else:
                st.info("Nenhum pedido para atualizar.")

    # --- CLIENTES ---
    elif menu == "Clientes":
        st.subheader("Aprovação de Clientes")
        df = buscar_dados("SELECT id, nome, email FROM usuarios WHERE status = 'Pendente' AND role = 'cliente'")
        if not df.empty:
            for _, r in df.iterrows():
                with st.container(border=True):
                    st.markdown(f"**{r['nome']}**")
                    st.caption(f"E-mail: {r['email']}")
                    if st.button(f"Aprovar Conta", key=f"btn_{r['id']}", type="primary"):
                        if executar_comando("UPDATE usuarios SET status = 'Aprovado' WHERE id = %s", (r['id'],)):
                            st.success("Conta aprovada!"); st.rerun()
        else:
            st.success("Tudo certo! Nenhuma conta pendente de aprovação.")
