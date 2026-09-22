import base64
import psycopg2
import streamlit as st
import pandas as pd

# ==========================================
# 1. CONFIGURAÇÃO E DESIGN MOBILE-FIRST
# ==========================================
st.set_page_config(page_title="JR Admin", page_icon="💡", layout="centered")

st.markdown("""
    <style>
    .block-container {
        max-width: 480px !important;
        padding-top: 2rem !important;
        padding-bottom: 6rem !important;
        margin: 0 auto !important;
    }
    #MainMenu, header, footer { visibility: hidden; }
    h1, h2, h3, h4 { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: #0f172a; }
    
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #ffffff, #f8fafc);
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-bottom: 10px;
    }
    div[data-testid="stMetricLabel"] p { font-size: 0.85rem !important; color: #64748b !important; font-weight: 700 !important; text-transform: uppercase; }
    div[data-testid="stMetricValue"] div { font-size: 1.6rem !important; color: #0284c7 !important; font-weight: 800 !important; }

    div[role="radiogroup"] { background-color: #f1f5f9; border-radius: 14px; padding: 6px; display: flex; gap: 4px; border: 1px solid #e2e8f0; }
    div[role="radiogroup"] label { background: transparent; border-radius: 10px; padding: 10px 4px; flex: 1; text-align: center; cursor: pointer; transition: all 0.3s ease; margin: 0 !important; }
    div[role="radiogroup"] label > div:first-child { display: none !important; }
    div[role="radiogroup"] label[data-checked="true"] { background-color: #ffffff !important; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); }
    div[role="radiogroup"] label[data-checked="true"] p { color: #0284c7 !important; font-weight: 800 !important; }
    div[role="radiogroup"] label p { font-size: 0.8rem !important; color: #64748b; font-weight: 600; margin: 0; }

    div.stButton > button { border-radius: 12px; font-weight: 600; min-height: 50px; font-size: 1rem; transition: all 0.2s; }
    div.stButton > button[kind="primary"] { background-color: #0284c7; border-color: #0284c7; }
    div.stButton > button[kind="primary"]:hover { background-color: #0369a1; box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3); }

    /* Correção de Contraste para Auditoria (Teste 5) */
    .card-detalhe { background: #ffffff !important; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
    .card-detalhe p, .card-detalhe strong, .card-detalhe h4, .card-detalhe h5, .card-detalhe span { color: #0f172a !important; }
    
    /* Cartões Mobile para Listagens (Obs 3) */
    .mobile-card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.03); }
    .mobile-card h4 { margin: 0 0 8px 0; color: #0284c7; font-size: 1.15rem; }
    .mobile-card p { margin: 4px 0; color: #475569; font-size: 0.95rem; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONEXÃO SUPABASE (FUSO DE BRASÍLIA)
# ==========================================
def get_db_connection():
    conn = psycopg2.connect(
        host="aws-0-us-west-2.pooler.supabase.com",
        port="5432",
        database="postgres",
        user="postgres.bfppcxnxqagpesuyjlhe",
        password="An1bal_19691910@",
        sslmode="require"
    )
    cursor = conn.cursor()
    cursor.execute("SET TIME ZONE 'America/Sao_Paulo';") # Teste 4: GMT-3
    conn.commit()
    cursor.close()
    return conn

@st.cache_data(ttl=5)
def buscar_dados(query, params=None):
    try:
        conn = get_db_connection()
        df = pd.read_sql(query, conn, params=params) if params else pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return pd.DataFrame()

def executar_comando(query, params=None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params) if params else cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()
        st.cache_data.clear()
        return True
    except Exception as e:
        return False

executar_comando("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'Pendente';")
executar_comando("ALTER TABLE produtos ADD COLUMN IF NOT EXISTS categoria VARCHAR(50) DEFAULT 'Outros';")

# ==========================================
# 3. AUTENTICAÇÃO
# ==========================================
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("""
        <div style='text-align: center; margin-top: 3rem; margin-bottom: 2rem;'>
            <div style='font-size: 3.5rem; margin-bottom: 10px;'>💡</div>
            <h1 style='font-size: 1.8rem; color: #0284c7; margin-bottom: 4px;'>JR Iluminação</h1>
            <p style='color: #64748b; font-size: 0.95rem; margin: 0;'>Acesso Administrativo Restrito</p>
        </div>
    """, unsafe_allow_html=True)
    
    usuario = st.text_input("Administrador", placeholder="admin")
    senha = st.text_input("Senha", type="password", placeholder="••••••")
    st.write("")
    
    if st.button("Entrar no Sistema", use_container_width=True, type="primary"):
        if usuario == "admin" and senha == "123456":
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Credenciais inválidas.")

# ==========================================
# 4. PAINEL PRINCIPAL
# ==========================================
else:
    col_logo, col_logout = st.columns([3, 1], vertical_alignment="center")
    with col_logo:
        st.markdown("<h2 style='margin: 0; font-size: 1.4rem; color: #0284c7;'>💡 JR Admin</h2>", unsafe_allow_html=True)
    with col_logout:
        if st.button("Sair", use_container_width=True):
            st.session_state["autenticado"] = False
            st.rerun()

    st.write("")
    menu_principal = st.radio("Navegação:", ["📊 Geral", "📦 Produtos", "🛒 Pedidos", "👥 Clientes"], horizontal=True, label_visibility="collapsed")
    st.write("")

    if menu_principal == "📊 Geral":
        st.markdown("<h4 style='color: #1e293b; margin-bottom: 16px;'>Visão Geral da Loja</h4>", unsafe_allow_html=True)
        
        df_prod = buscar_dados("SELECT SUM(quantidade) as total_estoque FROM produtos;")
        df_ped = buscar_dados("SELECT COUNT(id) as total_pedidos, SUM(total) as faturamento FROM pedidos;")
        df_cli = buscar_dados("SELECT COUNT(id) as total_clientes FROM usuarios WHERE role='cliente';")
        
        estoque_total = df_prod['total_estoque'].iloc[0] if not df_prod.empty and pd.notna(df_prod['total_estoque'].iloc[0]) else 0
        pedidos_total = df_ped['total_pedidos'].iloc[0] if not df_ped.empty else 0
        faturamento = df_ped['faturamento'].iloc[0] if not df_ped.empty and pd.notna(df_ped['faturamento'].iloc[0]) else 0
        clientes_total = df_cli['total_clientes'].iloc[0] if not df_cli.empty else 0

        c1, c2 = st.columns(2)
        c1.metric("Faturamento", f"R$ {float(faturamento):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        c2.metric("Total Pedidos", str(pedidos_total))
        c3, c4 = st.columns(2)
        c3.metric("Estoque Total", f"{int(estoque_total)} un.")
        c4.metric("Clientes", str(clientes_total))

    elif menu_principal == "📦 Produtos":
        st.markdown("<h4 style='color: #1e293b; margin-bottom: 12px;'>Catálogo & Estoque</h4>", unsafe_allow_html=True)
        acao_prod = st.selectbox("Selecione a operação:", ["📋 Listar Produtos", "➕ Cadastrar Produto", "✏️ Editar Produto", "🗑️ Excluir Produto"])
        st.write("")

        if acao_prod == "📋 Listar Produtos":
            df_produtos = buscar_dados("SELECT id, nome, categoria, preco, quantidade, imagem FROM produtos ORDER BY id DESC")
            if not df_produtos.empty:
                termo_busca = st.text_input("🔍 Pesquisar Produto")
                if termo_busca:
                    df_produtos = df_produtos[df_produtos['nome'].str.contains(termo_busca, case=False, na=False)]
                
                # Obs 3: Cartões em vez de Tabela apertada
                for _, r in df_produtos.iterrows():
                    st.markdown(f"""
                        <div class="mobile-card">
                            <h4>{r['nome']}</h4>
                            <p><strong>Categoria:</strong> {r.get('categoria', 'Outros')}</p>
                            <p><strong>Preço:</strong> R$ {float(r['preco']):,.2f} | <strong>Estoque:</strong> {r['quantidade']} un.</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("##### 📸 Pré-visualizar Imagem")
                opcoes_ver = {f"#{r['id']} - {r['nome']}": r['imagem'] for _, r in df_produtos.iterrows()}
                escolhido_ver = st.selectbox("Escolha um produto:", list(opcoes_ver.keys()))
                img_url = opcoes_ver[escolhido_ver]
                if img_url and img_url.strip() != '' and img_url != 'placeholder.jpg':
                    try: st.image(img_url, width=250)
                    except: st.warning("Imagem inválida.")
            else:
                st.info("O catálogo está vazio.")

        elif acao_prod == "➕ Cadastrar Produto":
            novo_nome = st.text_input("Nome do Produto")
            nova_cat = st.selectbox("Categoria", ["Lâmpadas", "Fitas LED", "Spots", "Plafons", "Outros"])
            novo_preco = st.number_input("Preço de Venda (R$)", min_value=0.01, step=0.50, format="%.2f")
            nova_qtd = st.number_input("Quantidade em Estoque", min_value=0, step=1, value=10)
            nova_desc = st.text_area("Descrição Técnica")
            
            tipo_envio = st.radio("Imagem:", ["Link / URL da Imagem", "Ficheiro do Dispositivo"], horizontal=True)
            imagem_final = "placeholder.jpg"
            if tipo_envio == "Ficheiro do Dispositivo":
                uploaded_file = st.file_uploader("Carregar foto:", type=["jpg", "jpeg", "png", "webp"])
                if uploaded_file:
                    bytes_data = uploaded_file.read()
                    imagem_final = f"data:{uploaded_file.type};base64,{base64.b64encode(bytes_data).decode()}"
                    st.image(uploaded_file, width=200)
            else:
                url_digitada = st.text_input("URL pública")
                if url_digitada.strip(): imagem_final = url_digitada.strip()
            
            st.write("")
            if st.button("Gravar Produto", type="primary", use_container_width=True):
                if novo_nome.strip():
                    # Teste 6: Impede Duplicados
                    existe = buscar_dados("SELECT id FROM produtos WHERE LOWER(nome) = LOWER(%s)", (novo_nome.strip(),))
                    if not existe.empty:
                        st.error("⚠️ Já existe um produto registado com este nome.")
                    else:
                        if executar_comando("INSERT INTO produtos (nome, categoria, preco, quantidade, descricao, imagem) VALUES (%s, %s, %s, %s, %s, %s)", 
                                            (novo_nome.strip(), nova_cat, float(novo_preco), int(nova_qtd), nova_desc.strip(), imagem_final)):
                            st.success("Adicionado com sucesso!")
                            st.rerun()
                else:
                    st.warning("O nome é obrigatório.")

        elif acao_prod == "✏️ Editar Produto":
            df_produtos = buscar_dados("SELECT id, nome, categoria, preco, quantidade, descricao, imagem FROM produtos ORDER BY nome ASC")
            if not df_produtos.empty:
                opcoes = {f"#{r['id']} - {r['nome']}": r['id'] for _, r in df_produtos.iterrows()}
                prod_id = opcoes[st.selectbox("Produto para alterar:", list(opcoes.keys()))]
                prod_atual = df_produtos[df_produtos['id'] == prod_id].iloc[0]
                
                e_nome = st.text_input("Nome", value=str(prod_atual['nome']))
                categorias_lista = ["Lâmpadas", "Fitas LED", "Spots", "Plafons", "Outros"]
                cat_atual = str(prod_atual.get('categoria', 'Outros'))
                e_cat = st.selectbox("Categoria", categorias_lista, index=categorias_lista.index(cat_atual) if cat_atual in categorias_lista else 4)
                e_preco = st.number_input("Preço (R$)", min_value=0.01, value=float(prod_atual['preco']), format="%.2f")
                e_qtd = st.number_input("Estoque", min_value=0, value=int(prod_atual['quantidade']))
                e_desc = st.text_area("Descrição", value=str(prod_atual['descricao'] or ""))
                
                nova_img = st.text_input("URL da Nova Imagem", value=str(prod_atual['imagem'] or 'placeholder.jpg'))
                
                st.write("")
                if st.button("Salvar Alterações", type="primary", use_container_width=True):
                    if executar_comando("UPDATE produtos SET nome=%s, categoria=%s, preco=%s, quantidade=%s, descricao=%s, imagem=%s WHERE id=%s", 
                                        (e_nome.strip(), e_cat, float(e_preco), int(e_qtd), e_desc.strip(), nova_img, prod_id)):
                        st.success("Atualizado!")
                        st.rerun()
            else:
                st.info("Nenhum produto.")

        elif acao_prod == "🗑️ Excluir Produto":
            df_produtos = buscar_dados("SELECT id, nome FROM produtos ORDER BY id DESC")
            if not df_produtos.empty:
                opcoes = {f"#{r['id']} - {r['nome']}": r['id'] for _, r in df_produtos.iterrows()}
                del_id = opcoes[st.selectbox("Produto para remover:", list(opcoes.keys()))]
                if st.button("Confirmar Exclusão", type="primary", use_container_width=True):
                    if executar_comando("DELETE FROM produtos WHERE id = %s", (del_id,)):
                        st.success("Removido.")
                        st.rerun()

    elif menu_principal == "🛒 Pedidos":
        st.markdown("<h4 style='color: #1e293b; margin-bottom: 12px;'>Gestão Logística</h4>", unsafe_allow_html=True)
        acao_ped = st.selectbox("Operação:", ["📋 Painel Geral", "🔍 Auditoria de Compra", "🔄 Atualizar Status"])
        st.write("")

        if acao_ped == "📋 Painel Geral":
            pedidos = buscar_dados("SELECT p.id, c.nome as cliente, p.total, p.status, TO_CHAR(p.data_pedido, 'DD/MM/YYYY HH24:MI') as data FROM pedidos p LEFT JOIN clientes c ON p.cliente_id = c.id ORDER BY p.id DESC")
            if not pedidos.empty:
                for _, r in pedidos.iterrows():
                    st.markdown(f"""
                        <div class="mobile-card">
                            <h4>📦 Pedido #{r['id']}</h4>
                            <p><strong>Cliente:</strong> {r['cliente']} | <strong>Valor:</strong> R$ {float(r['total']):,.2f}</p>
                            <p><strong>Status:</strong> {r['status']} | <strong>Data:</strong> {r['data']}</p>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Não há encomendas.")

        elif acao_ped == "🔍 Auditoria de Compra":
            lista = buscar_dados("SELECT p.id, c.nome, p.total FROM pedidos p JOIN clientes c ON p.cliente_id = c.id ORDER BY p.id DESC")
            if not lista.empty:
                ped_id = st.selectbox("Recibo:", list({f"Nº {r['id']} - {r['nome']} (R$ {r['total']})": r['id'] for _, r in lista.iterrows()}.values()), format_func=lambda x: f"Pedido #{x}")
                info = buscar_dados("SELECT p.id, p.total, p.status, p.data_pedido, c.nome, c.email, c.telefone FROM pedidos p JOIN clientes c ON p.cliente_id = c.id WHERE p.id = %s", (ped_id,))
                if not info.empty:
                    p = info.iloc[0]
                    # Teste 5: Card de auditoria corrigido
                    st.markdown(f"""
                        <div class="card-detalhe">
                            <h4 style="margin:0 0 8px 0; color:#0284c7 !important;">🧾 Fatura #{p['id']}</h4>
                            <p style="margin:2px 0;"><strong>Status:</strong> {str(p['status']).upper()}</p>
                            <p style="margin:2px 0;"><strong>Data:</strong> {p['data_pedido']}</p>
                            <hr style="margin:12px 0; border:0; border-top:1px dashed #cbd5e1;">
                            <h5 style="margin:0 0 8px 0; color:#334155 !important;">👤 Comprador:</h5>
                            <p style="margin:2px 0;"><strong>Nome:</strong> {p['nome']}</p>
                            <p style="margin:2px 0;"><strong>Tel:</strong> {p['telefone'] or 'N/A'} | <strong>E-mail:</strong> {p['email']}</p>
                        </div>
                    """, unsafe_allow_html=True)

                    itens = buscar_dados("SELECT pr.nome as produto, ip.quantidade, ip.preco_unitario, (ip.quantidade * ip.preco_unitario) as subtotal FROM itens_pedido ip JOIN produtos pr ON ip.produto_id = pr.id WHERE ip.pedido_id = %s", (ped_id,))
                    st.markdown("##### 📦 Itens")
                    if not itens.empty:
                        st.dataframe(itens.rename(columns={"produto": "Item", "quantidade": "Qtd", "preco_unitario": "Preço Unit.", "subtotal": "Subtotal"}), use_container_width=True, hide_index=True)
                        st.success(f"Valor Final Faturado: R$ {float(p['total']):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        elif acao_ped == "🔄 Atualizar Status":
            pendentes = buscar_dados("SELECT id, status FROM pedidos ORDER BY id DESC")
            if not pendentes.empty:
                opcoes = {f"#{r['id']} (Atual: {r['status']})": r['id'] for _, r in pendentes.iterrows()}
                ped_id = opcoes[st.selectbox("Pedido:", list(opcoes.keys()))]
                novo_status = st.selectbox("Mover para:", ["Pendente", "Em processamento", "Enviado", "Entregue", "Concluído", "Cancelado"])
                if st.button("Gravar Alteração", type="primary", use_container_width=True):
                    if executar_comando("UPDATE pedidos SET status = %s WHERE id = %s", (novo_status, ped_id)):
                        st.success("Atualizado!")
                        st.rerun()

    elif menu_principal == "👥 Clientes":
        st.markdown("<h4 style='color: #1e293b; margin-bottom: 12px;'>Auditoria de Contas</h4>", unsafe_allow_html=True)
        acao_cli = st.selectbox("Painel:", ["📋 Base de Clientes", "✅ Aprovar Registros", "➕ Novo Cliente", "📜 Histórico"])
        st.write("")

        if acao_cli == "📋 Base de Clientes":
            df_clientes = buscar_dados("SELECT u.id, u.nome, u.email, u.status, COALESCE(TO_CHAR(a.ultimo_login, 'DD/MM/YYYY HH24:MI'), 'Sem Registo') as ultimo_login FROM usuarios u LEFT JOIN autenticacao a ON a.usuario_id = u.id WHERE u.role = 'cliente' ORDER BY u.id DESC")
            if not df_clientes.empty:
                termo = st.text_input("🔍 Procurar E-mail ou Nome")
                if termo: df_clientes = df_clientes[df_clientes['nome'].str.contains(termo, case=False) | df_clientes['email'].str.contains(termo, case=False)]
                
                # Obs 3: Cards Mobile
                for _, r in df_clientes.iterrows():
                    cor = "#15803d" if r['status'] == "Aprovado" else "#b91c1c"
                    st.markdown(f"""
                        <div class="mobile-card">
                            <h4 style="margin: 0 0 4px 0;">👤 {r['nome']}</h4>
                            <p style="margin: 2px 0;"><strong>E-mail:</strong> {r['email']}</p>
                            <p style="margin: 2px 0;"><strong>Status:</strong> <span style="color:{cor}; font-weight:bold;">{r['status']}</span></p>
                            <p style="margin: 2px 0; font-size: 0.85rem; color: #64748b;">⏳ Último Login: {r['ultimo_login']}</p>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nenhuma conta.")

        elif acao_cli == "✅ Aprovar Registros":
            pendentes = buscar_dados("SELECT id, nome, email FROM usuarios WHERE status = 'Pendente' AND role = 'cliente'")
            if not pendentes.empty:
                st.warning(f"⚠️ {len(pendentes)} conta(s) aguardando aprovação.")
                opcoes = {f"#{r['id']} - {r['nome']} ({r['email']})": r['id'] for _, r in pendentes.iterrows()}
                user_id = opcoes[st.selectbox("Selecionar conta:", list(opcoes.keys()))]
                if st.button("Liberar Acesso", type="primary", use_container_width=True):
                    if executar_comando("UPDATE usuarios SET status = 'Aprovado' WHERE id = %s", (user_id,)):
                        st.success("Conta aprovada!")
                        st.rerun()
            else:
                st.success("Tudo em dia! Sem pendências.")

        elif acao_cli == "➕ Novo Cliente":
            nome_cli = st.text_input("Nome")
            email_cli = st.text_input("E-mail")
            if st.button("Salvar", type="primary", use_container_width=True):
                if nome_cli and email_cli:
                    if executar_comando("INSERT INTO usuarios (nome, email, role, status) VALUES (%s, %s, 'cliente', 'Aprovado')", (nome_cli, email_cli)):
                        st.success("Registado e aprovado.")
                        st.rerun()

        elif acao_cli == "📜 Histórico":
            df_clientes = buscar_dados("SELECT id, nome FROM clientes ORDER BY nome ASC")
            if not df_clientes.empty:
                opcoes = {f"#{r['id']} - {r['nome']}": r['id'] for _, r in df_clientes.iterrows()}
                cli_id = opcoes[st.selectbox("Cliente:", list(opcoes.keys()))]
                pedidos_cli = buscar_dados("SELECT id, total, status, TO_CHAR(data_pedido, 'DD/MM/YYYY') as data FROM pedidos WHERE cliente_id = %s ORDER BY id DESC", (cli_id,))
                if not pedidos_cli.empty:
                    st.markdown(f"<div style='padding: 10px; background: #f1f5f9; border-radius: 8px; margin-bottom: 10px;'><strong>Acumulado:</strong> R$ {float(pedidos_cli['total'].sum()):,.2f}</div>", unsafe_allow_html=True)
                    for _, r in pedidos_cli.iterrows():
                        st.markdown(f"<div class='mobile-card' style='padding:12px;'><h4 style='font-size:1rem;margin-bottom:4px;'>🧾 Fatura #{r['id']}</h4><p style='margin:0;font-size:0.9rem;'><strong>Data:</strong> {r['data']} | <strong>Status:</strong> {r['status']}</p><p style='margin:0;font-size:0.9rem;color:#0284c7;'><strong>Valor: R$ {float(r['total']):,.2f}</strong></p></div>", unsafe_allow_html=True)
                else:
                    st.info("Sem transações.")
