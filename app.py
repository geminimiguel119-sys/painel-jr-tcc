import os
import hmac
import psycopg2
import streamlit as st
import pandas as pd

# ==========================================
# 1. CONFIGURAÇÃO BASE E ESTILOS
# ==========================================
st.set_page_config(page_title="JR Admin", page_icon="💡", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 2rem !important; max-width: 650px !important; }
    #MainMenu, header, footer { display: none !important; }
    div[data-testid="stTabs"] { margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONEXÃO COM BANCO DE DADOS
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
            host=obter_config("DB_HOST"), port=obter_config("DB_PORT", "5432"),
            database=obter_config("DB_NAME", "postgres"), user=obter_config("DB_USER"),
            password=obter_config("DB_PASS"), sslmode="require"
        )
        conn.cursor().execute("SET TIME ZONE 'America/Sao_Paulo';")
        conn.commit()
        return conn
    except Exception as e:
        st.error("Erro de conexão com o Banco de Dados. Verifique os Secrets.")
        st.stop()

@st.cache_data(ttl=2)
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
    except Exception as e:
        st.error(f"Erro na operação: {e}")
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
    st.caption("Painel Administrativo e Inteligência de Negócio")
    
    usuario = st.text_input("Usuário de Acesso", placeholder="Ex: admin")
    senha = st.text_input("Senha", type="password", placeholder="Sua senha secreta")
    
    if st.button("Entrar no Sistema", type="primary", use_container_width=True):
        if validar_login(usuario, senha):
            st.session_state["autenticado"] = True
            st.rerun()
        else: st.error("Credenciais inválidas. Tente novamente.")

# ==========================================
# 4. PAINEL PRINCIPAL
# ==========================================
else:
    c1, c2 = st.columns([4, 1], vertical_alignment="center")
    c1.markdown("### 💡 Visão Administrativa")
    if c2.button("Sair", use_container_width=True):
        st.session_state["autenticado"] = False
        st.rerun()

    menu = st.radio("Menu Principal", ["Resumo", "Produtos", "Preditivo", "Pedidos", "Clientes"], horizontal=True, label_visibility="collapsed")
    st.write("---")

    # ------------------ RESUMO ------------------
    if menu == "Resumo":
        st.subheader("Desempenho Geral")
        st.caption("Métricas atualizadas em tempo real com base no banco de dados.")
        
        df_ped = buscar_dados("SELECT COUNT(id) as qtd, SUM(total) as fat FROM pedidos WHERE status != 'Cancelado'")
        df_prod = buscar_dados("SELECT SUM(quantidade) as est FROM produtos")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Faturamento Líquido", f"R$ {float(df_ped['fat'].iloc[0] or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            st.metric("Estoque Global", f"{int(df_prod['est'].iloc[0] or 0)} unidades")
        with col2:
            st.metric("Vendas Concluídas", str(df_ped['qtd'].iloc[0] or 0))
            st.metric("Status da Conexão", "Sistema Online 🟢")

    # ------------------ PRODUTOS ------------------
    elif menu == "Produtos":
        st.subheader("Catálogo e Estoque")
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Catálogo", "➕ Adicionar", "✏️ Editar", "🗑️ Excluir"])
        
        with tab1:
            df = buscar_dados("SELECT * FROM produtos ORDER BY id DESC")
            if not df.empty:
                for _, r in df.iterrows():
                    with st.container(border=True):
                        st.markdown(f"**{r['nome']}**")
                        st.caption(f"Categoria: {r.get('categoria', 'N/A')} | R$ {r['preco']:.2f} | Estoque: {r['quantidade']} un.")
            else: st.info("Nenhum produto no catálogo.")
                
        with tab2:
            st.caption("Cadastre um novo item para venda na loja virtual.")
            nome = st.text_input("Nome do Produto", help="Nome que aparecerá na loja para o cliente.")
            cat = st.selectbox("Categoria", ["Lâmpadas", "Fitas LED", "Plafons", "Spots", "Outros"])
            preco = st.number_input("Preço Unitário (R$)", min_value=0.1)
            qtd = st.number_input("Estoque Inicial", min_value=0, step=1, help="Quantidade física disponível na prateleira.")
            if st.button("Salvar Produto", type="primary", use_container_width=True):
                if nome:
                    if executar_comando("INSERT INTO produtos (nome, categoria, preco, quantidade, imagem) VALUES (%s, %s, %s, %s, 'placeholder.jpg')", (nome, cat, preco, qtd)):
                        st.success("Produto cadastrado!"); st.rerun()
                else: st.warning("O nome é obrigatório.")

        with tab3:
            df = buscar_dados("SELECT * FROM produtos ORDER BY nome ASC")
            if not df.empty:
                opcoes = {f"#{r['id']} - {r['nome']}": r['id'] for _, r in df.iterrows()}
                prod_id = opcoes[st.selectbox("Selecione o Produto para editar", list(opcoes.keys()))]
                p = df[df['id'] == prod_id].iloc[0]
                
                e_nome = st.text_input("Novo Nome", value=str(p['nome']))
                cats = ["Lâmpadas", "Fitas LED", "Plafons", "Spots", "Outros"]
                e_cat = st.selectbox("Nova Categoria", cats, index=cats.index(p.get('categoria', 'Outros')) if p.get('categoria', 'Outros') in cats else 4)
                e_preco = st.number_input("Novo Preço (R$)", min_value=0.1, value=float(p['preco']))
                e_qtd = st.number_input("Ajustar Estoque", min_value=0, step=1, value=int(p['quantidade']))
                if st.button("Atualizar Dados", type="primary", use_container_width=True):
                    if executar_comando("UPDATE produtos SET nome=%s, categoria=%s, preco=%s, quantidade=%s WHERE id=%s", (e_nome, e_cat, e_preco, e_qtd, prod_id)):
                        st.success("Produto atualizado!"); st.rerun()
            else: st.info("Sem produtos para editar.")

        with tab4:
            df = buscar_dados("SELECT id, nome FROM produtos ORDER BY id DESC")
            if not df.empty:
                opcoes = {f"#{r['id']} - {r['nome']}": r['id'] for _, r in df.iterrows()}
                del_id = opcoes[st.selectbox("Selecione o Produto para remover", list(opcoes.keys()))]
                st.error("⚠️ Atenção: Esta ação não pode ser desfeita.")
                if st.button("Excluir Permanentemente", type="primary", use_container_width=True):
                    if executar_comando("DELETE FROM produtos WHERE id=%s", (del_id,)):
                        st.success("Produto excluído!"); st.rerun()
            else: st.info("Sem produtos para excluir.")

    # ------------------ PREDITIVO ------------------
    elif menu == "Preditivo":
        st.subheader("Inteligência de Suprimentos")
        st.caption("Veja automaticamente quais produtos precisam de reposição urgente baseando-se no ritmo de vendas.")
        
        col_dias, col_lead = st.columns(2)
        with col_dias: dias = st.slider("Histórico de Vendas (dias):", 7, 60, 30, help="Quantos dias para trás o sistema deve analisar para calcular a média de vendas.")
        with col_lead: lead_time = st.number_input("Prazo do Fornecedor (dias):", 1, 30, 5, help="Quantos dias seu fornecedor demora para entregar um novo pedido.")
        
        query = """
            SELECT p.id, p.nome, COALESCE(p.quantidade, 0) as estoque,
                   COALESCE(SUM(CASE WHEN ped.status != 'Cancelado' AND ped.data_pedido >= NOW() - (%s * INTERVAL '1 day') THEN ip.quantidade ELSE 0 END), 0) as vendido
            FROM produtos p LEFT JOIN itens_pedido ip ON ip.produto_id = p.id
            LEFT JOIN pedidos ped ON ped.id = ip.pedido_id GROUP BY p.id, p.nome, p.quantidade
        """
        df = buscar_dados(query, params=(dias,))
        
        if not df.empty:
            df['consumo_diario'] = df['vendido'] / dias
            df['dias_restantes'] = df.apply(lambda r: int(r['estoque'] / r['consumo_diario']) if r['consumo_diario'] > 0 else 999, axis=1)
            df['ponto_reposicao'] = (df['consumo_diario'] * lead_time).round().astype(int) + 2
            df = df.sort_values(by='dias_restantes', ascending=True)
            
            for _, r in df.iterrows():
                if r['dias_restantes'] <= lead_time:
                    cor_borda, cor_fundo, status = "#dc2626", "#fef2f2", "🚨 Crítico"
                    acao_msg = "Comprar hoje! O estoque vai zerar antes do fornecedor entregar."
                elif r['dias_restantes'] <= lead_time + 7:
                    cor_borda, cor_fundo, status = "#f59e0b", "#fffbeb", "⚠️ Atenção"
                    acao_msg = f"Fazer pedido em breve. Ao chegar em {r['ponto_reposicao']} un. inicie a compra."
                else:
                    cor_borda, cor_fundo, status = "#10b981", "#ecfdf5", "✅ Saudável"
                    acao_msg = "Estoque seguro. Nenhuma ação necessária no momento."

                texto_dias = f"{r['dias_restantes']} dias" if r['dias_restantes'] != 999 else "+ de 1 ano"

                st.markdown(f"""
                <div style="background-color: {cor_fundo}; padding: 16px; border-radius: 8px; border-left: 6px solid {cor_borda}; margin-bottom: 15px; border: 1px solid #e5e7eb; border-left-width: 6px;">
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
                        💡 <b>Recomendação:</b> {acao_msg}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else: st.info("Nenhum produto cadastrado para análise.")

    # ------------------ PEDIDOS ------------------
    elif menu == "Pedidos":
        st.subheader("Controle de Vendas")
        tab1, tab2, tab3 = st.tabs(["📦 Listar Pedidos", "🔄 Mudar Status", "🗑️ Cancelar/Excluir"])
        
        with tab1:
            df = buscar_dados("SELECT p.id, c.nome, p.status, p.total FROM pedidos p JOIN clientes c ON p.cliente_id = c.id ORDER BY p.id DESC")
            if not df.empty:
                for _, r in df.iterrows():
                    with st.container(border=True):
                        st.markdown(f"**Pedido #{r['id']} - {r['nome']}**")
                        st.caption(f"Status atual: {r['status']} | Valor: R$ {r['total']:.2f}")
            else: st.info("Ainda não há vendas registradas.")
                
        with tab2:
            st.caption("Avance as etapas do pedido (Ex: De Pendente para Enviado).")
            df = buscar_dados("SELECT id, status FROM pedidos ORDER BY id DESC")
            if not df.empty:
                opcoes = {f"Pedido #{r['id']} (Atual: {r['status']})": r['id'] for _, r in df.iterrows()}
                ped_id = opcoes[st.selectbox("Qual pedido deseja atualizar?", list(opcoes.keys()))]
                novo_status = st.selectbox("Mudar para:", ["Pendente", "Em processamento", "Enviado", "Entregue", "Cancelado"])
                if st.button("Confirmar Mudança", type="primary", use_container_width=True):
                    if executar_comando("UPDATE pedidos SET status = %s WHERE id = %s", (novo_status, ped_id)):
                        st.success(f"O pedido foi marcado como {novo_status}!"); st.rerun()
            else: st.info("Nenhum pedido disponível.")

        with tab3:
            df = buscar_dados("SELECT p.id, c.nome FROM pedidos p JOIN clientes c ON p.cliente_id = c.id ORDER BY p.id DESC")
            if not df.empty:
                opcoes = {f"Pedido #{r['id']} - {r['nome']}": r['id'] for _, r in df.iterrows()}
                del_id = opcoes[st.selectbox("Qual pedido remover?", list(opcoes.keys()))]
                st.error("Ao excluir, o histórico desta venda apagará do sistema.")
                if st.button("Excluir Permanentemente", type="primary", use_container_width=True):
                    executar_comando("DELETE FROM itens_pedido WHERE pedido_id = %s", (del_id,))
                    if executar_comando("DELETE FROM pedidos WHERE id = %s", (del_id,)):
                        st.success("Pedido excluído!"); st.rerun()
            else: st.info("Nenhum pedido para excluir.")

    # ------------------ CLIENTES ------------------
    elif menu == "Clientes":
        st.subheader("Central de Usuários")
        tab1, tab2, tab3 = st.tabs(["⏳ Pendentes", "👥 Ver Todos", "⚙️ Gerenciar"])
        
        with tab1:
            st.caption("Aprove clientes que se cadastraram pela loja virtual.")
            df = buscar_dados("SELECT id, nome, email FROM usuarios WHERE status = 'Pendente' AND role = 'cliente'")
            if not df.empty:
                for _, r in df.iterrows():
                    with st.container(border=True):
                        st.markdown(f"**{r['nome']}**")
                        st.caption(f"E-mail: {r['email']}")
                        if st.button(f"✅ Aprovar Acesso", key=f"btn_{r['id']}", type="primary"):
                            if executar_comando("UPDATE usuarios SET status = 'Aprovado' WHERE id = %s", (r['id'],)):
                                st.success(f"Acesso liberado para {r['nome']}!"); st.rerun()
            else: st.success("Nenhuma conta pendente na fila.")

        with tab2:
            df = buscar_dados("SELECT id, nome, email, status, role FROM usuarios ORDER BY id DESC")
            if not df.empty:
                for _, r in df.iterrows():
                    with st.container(border=True):
                        st.markdown(f"**{r['nome']}**")
                        st.caption(f"E-mail: {r['email']} | Nível: {r['role'].upper()} | Status: {r['status']}")
            else: st.info("Nenhum usuário cadastrado.")

        with tab3:
            st.caption("Edite ou exclua um usuário existente.")
            df = buscar_dados("SELECT id, nome, email, status FROM usuarios WHERE role != 'admin' ORDER BY nome ASC")
            if not df.empty:
                opcoes = {f"#{r['id']} - {r['nome']}": r['id'] for _, r in df.iterrows()}
                cli_id = opcoes[st.selectbox("Selecionar Cliente", list(opcoes.keys()))]
                c = df[df['id'] == cli_id].iloc[0]
                
                e_status = st.selectbox("Status da Conta", ["Aprovado", "Pendente", "Recusado"], index=["Aprovado", "Pendente", "Recusado"].index(c['status']))
                
                col_up, col_del = st.columns(2)
                if col_up.button("Atualizar Status", type="primary", use_container_width=True):
                    if executar_comando("UPDATE usuarios SET status=%s WHERE id=%s", (e_status, cli_id)):
                        st.success("Conta atualizada!"); st.rerun()
                
                if col_del.button("Excluir Cliente", use_container_width=True):
                    executar_comando("DELETE FROM autenticacao WHERE usuario_id=%s", (cli_id,))
                    if executar_comando("DELETE FROM usuarios WHERE id=%s", (cli_id,)):
                        st.success("Cliente removido!"); st.rerun()
            else: st.info("Sem clientes gerenciar.")
