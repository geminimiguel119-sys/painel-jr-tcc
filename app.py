import base64
import psycopg2
import streamlit as st
import pandas as pd
import urllib.parse
import urllib.request

# ==========================================
# 1. DESIGN MONOCROMÁTICO (PRETO E BRANCO)
# ==========================================
st.set_page_config(page_title="JR Admin", page_icon="💡", layout="centered")

st.markdown("""
    <style>
    /* Estilos Globais */
    .stApp {
        background-color: #f8f9fa !important;
        color: #000000 !important;
    }
    .block-container {
        max-width: 480px !important;
        padding-top: 2rem !important;
        padding-bottom: 6rem !important;
        margin: 0 auto !important;
    }
    #MainMenu, header, footer { visibility: hidden; }
    h1, h2, h3, h4, h5, p, span, label { 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important; 
        color: #000000 !important; 
    }
    
    /* Cartões de Métricas */
    div[data-testid="stMetric"] {
        background: #ffffff !important;
        border: 2px solid #000000 !important;
        border-radius: 12px !important;
        padding: 16px !important;
        box-shadow: 2px 2px 0px #000000 !important;
        margin-bottom: 10px !important;
    }
    div[data-testid="stMetricLabel"] p { 
        font-size: 0.85rem !important; 
        color: #333333 !important; 
        font-weight: 800 !important; 
        text-transform: uppercase; 
    }
    div[data-testid="stMetricValue"] div { 
        font-size: 1.6rem !important; 
        color: #000000 !important; 
        font-weight: 900 !important; 
    }

    /* Navegação por Abas (Radio) */
    div[role="radiogroup"] { 
        background-color: #e9ecef !important; 
        border-radius: 12px !important; 
        padding: 4px !important; 
        display: flex !important; 
        gap: 4px !important; 
        border: 2px solid #000000 !important; 
    }
    div[role="radiogroup"] label { 
        background: transparent !important; 
        border-radius: 8px !important; 
        padding: 10px 4px !important; 
        flex: 1 !important; 
        text-align: center !important; 
        cursor: pointer !important; 
        margin: 0 !important; 
    }
    div[role="radiogroup"] label > div:first-child { display: none !important; }
    div[role="radiogroup"] label[data-checked="true"] { 
        background-color: #000000 !important; 
    }
    div[role="radiogroup"] label[data-checked="true"] p { 
        color: #ffffff !important; 
        font-weight: 800 !important; 
    }
    div[role="radiogroup"] label p { 
        font-size: 0.85rem !important; 
        color: #333333 !important; 
        font-weight: 700 !important; 
    }

    /* Botões Principais */
    div.stButton > button { 
        border-radius: 10px !important; 
        font-weight: 700 !important; 
        min-height: 48px !important; 
        font-size: 1rem !important; 
        border: 2px solid #000000 !important;
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    div.stButton > button[kind="primary"] { 
        background-color: #000000 !important; 
        color: #ffffff !important; 
        border: 2px solid #000000 !important; 
    }
    div.stButton > button:hover { 
        background-color: #333333 !important; 
        color: #ffffff !important; 
    }

    /* Cartões de Lista e Fatura */
    .mobile-card { 
        background: #ffffff !important; 
        border: 1.5px solid #000000 !important; 
        border-radius: 10px !important; 
        padding: 14px !important; 
        margin-bottom: 12px !important; 
        box-shadow: 2px 2px 0px rgba(0,0,0,0.15) !important;
    }
    .mobile-card h4 { 
        margin: 0 0 6px 0 !important; 
        color: #000000 !important; 
        font-size: 1.1rem !important; 
        font-weight: 800 !important;
    }
    .mobile-card p { 
        margin: 4px 0 !important; 
        color: #212529 !important; 
        font-size: 0.95rem !important; 
    }

    .card-detalhe { 
        background: #ffffff !important; 
        border: 2px solid #000000 !important; 
        border-radius: 10px !important; 
        padding: 16px !important; 
        margin-bottom: 16px !important; 
    }
    .card-detalhe p, .card-detalhe strong, .card-detalhe h4, .card-detalhe h5, .card-detalhe span { 
        color: #000000 !important; 
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONEXÃO AO SUPABASE (GMT-3)
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
    cursor.execute("SET TIME ZONE 'America/Sao_Paulo';")
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
        st.error(f"Erro: {e}")
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
    except Exception:
        return False

def enviar_telegram_aviso(msg):
    token = "8700166269:AAE43sggx-efi75G0N97-ZHHrJf0xMye4m4"
    chat_id = "5034813131"
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = urllib.parse.urlencode({"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}).encode()
        req = urllib.request.Request(url, data=data)
        urllib.request.urlopen(req, timeout=4)
    except:
        pass

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
            <h1 style='font-size: 1.8rem; color: #000000; margin-bottom: 4px; font-weight: 900;'>JR Iluminação</h1>
            <p style='color: #495057; font-size: 0.95rem; margin: 0;'>Painel de Gestão e Administração</p>
        </div>
    """, unsafe_allow_html=True)
    
    usuario = st.text_input("Usuário", placeholder="admin")
    senha = st.text_input("Senha", type="password", placeholder="••••••")
    st.write("")
    
    if st.button("Aceder ao Painel", use_container_width=True, type="primary"):
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
        st.markdown("<h2 style='margin: 0; font-size: 1.4rem; color: #000000; font-weight: 900;'>💡 JR Admin</h2>", unsafe_allow_html=True)
    with col_logout:
        if st.button("Sair", use_container_width=True):
            st.session_state["autenticado"] = False
            st.rerun()

    st.write("")
    menu_principal = st.radio("Navegação:", ["📊 Geral", "📦 Produtos", "🛒 Pedidos", "👥 Clientes"], horizontal=True, label_visibility="collapsed")
    st.write("")

    # TAB 1: GERAL
    if menu_principal == "📊 Geral":
        st.markdown("<h4 style='color: #000000; font-weight: 800; margin-bottom: 16px;'>Métricas da Loja</h4>", unsafe_allow_html=True)
        
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

        st.markdown("---")
        st.markdown("<h5 style='font-weight: 800;'>Desempenho Geral</h5>", unsafe_allow_html=True)

        df_vendas_data = buscar_dados("SELECT TO_CHAR(data_pedido, 'DD/MM') as dia, SUM(total) as total_dia FROM pedidos GROUP BY dia ORDER BY dia ASC LIMIT 7")
        if not df_vendas_data.empty:
            df_vendas_data = df_vendas_data.set_index('dia')
            st.caption("Faturamento Recente (R$):")
            st.bar_chart(df_vendas_data['total_dia'])

        df_cat_estoque = buscar_dados("SELECT categoria, SUM(quantidade) as estoque FROM produtos GROUP BY categoria")
        if not df_cat_estoque.empty:
            df_cat_estoque = df_cat_estoque.set_index('categoria')
            st.caption("Estoque por Categoria (unidades):")
            st.bar_chart(df_cat_estoque['estoque'])

    # TAB 2: PRODUTOS
    elif menu_principal == "📦 Produtos":
        st.markdown("<h4 style='color: #000000; font-weight: 800; margin-bottom: 12px;'>Catálogo e Estoque</h4>", unsafe_allow_html=True)
        acao_prod = st.selectbox("Selecione a operação:", ["📋 Listar Produtos", "➕ Cadastrar Produto", "✏️ Editar Produto", "🗑️ Excluir Produto"])
        st.write("")

        if acao_prod == "📋 Listar Produtos":
            df_produtos = buscar_dados("SELECT id, nome, categoria, preco, quantidade, imagem FROM produtos ORDER BY id DESC")
            if not df_produtos.empty:
                termo_busca = st.text_input("🔍 Pesquisar Produto")
                if termo_busca:
                    df_produtos = df_produtos[df_produtos['nome'].str.contains(termo_busca, case=False, na=False)]
                
                for _, r in df_produtos.iterrows():
                    st.markdown(f"""
                        <div class="mobile-card">
                            <h4>{r['nome']}</h4>
                            <p><strong>Categoria:</strong> {r.get('categoria', 'Outros')}</p>
                            <p><strong>Preço:</strong> R$ {float(r['preco']):,.2f} | <strong>Estoque:</strong> {r['quantidade']} un.</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<h5 style='font-weight: 800; margin-top: 15px;'>Visualizar Imagem</h5>", unsafe_allow_html=True)
                opcoes_ver = {f"#{r['id']} - {r['nome']}": r['imagem'] for _, r in df_produtos.iterrows()}
                escolhido_ver = st.selectbox("Escolha um produto:", list(opcoes_ver.keys()))
                img_url = opcoes_ver[escolhido_ver]
                if img_url and img_url.strip() != '' and img_url != 'placeholder.jpg':
                    try: st.image(img_url, width=250)
                    except: st.warning("Imagem indisponível.")
            else:
                st.info("Nenhum produto cadastrado.")

        elif acao_prod == "➕ Cadastrar Produto":
            novo_nome = st.text_input("Nome do Produto")
            nova_cat = st.selectbox("Categoria", ["Lâmpadas", "Fitas LED", "Spots", "Plafons", "Outros"])
            novo_preco = st.number_input("Preço de Venda (R$)", min_value=0.01, step=0.50, format="%.2f")
            nova_qtd = st.number_input("Quantidade em Estoque", min_value=0, step=1, value=10)
            nova_desc = st.text_area("Descrição")
            
            tipo_envio = st.radio("Imagem:", ["Link / URL da Imagem", "Arquivo do Dispositivo"], horizontal=True)
            imagem_final = "placeholder.jpg"
            if tipo_envio == "Arquivo do Dispositivo":
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
                    existe = buscar_dados("SELECT id FROM produtos WHERE LOWER(nome) = LOWER(%s)", (novo_nome.strip(),))
                    if not existe.empty:
                        st.error("Já existe um produto com este nome.")
                    else:
                        if executar_comando("INSERT INTO produtos (nome, categoria, preco, quantidade, descricao, imagem) VALUES (%s, %s, %s, %s, %s, %s)", 
                                            (novo_nome.strip(), nova_cat, float(novo_preco), int(nova_qtd), nova_desc.strip(), imagem_final)):
                            st.success("Produto cadastrado com sucesso!")
                            st.rerun()
                else:
                    st.warning("Preencha o nome do produto.")

        elif acao_prod == "✏️ Editar Produto":
            df_produtos = buscar_dados("SELECT id, nome, categoria, preco, quantidade, descricao, imagem FROM produtos ORDER BY nome ASC")
            if not df_produtos.empty:
                opcoes = {f"#{r['id']} - {r['nome']}": r['id'] for _, r in df_produtos.iterrows()}
                prod_id = opcoes[st.selectbox("Produto:", list(opcoes.keys()))]
                prod_atual = df_produtos[df_produtos['id'] == prod_id].iloc[0]
                
                e_nome = st.text_input("Nome", value=str(prod_atual['nome']))
                categorias_lista = ["Lâmpadas", "Fitas LED", "Spots", "Plafons", "Outros"]
                cat_atual = str(prod_atual.get('categoria', 'Outros'))
                e_cat = st.selectbox("Categoria", categorias_lista, index=categorias_lista.index(cat_atual) if cat_atual in categorias_lista else 4)
                e_preco = st.number_input("Preço (R$)", min_value=0.01, value=float(prod_atual['preco']), format="%.2f")
                e_qtd = st.number_input("Estoque", min_value=0, value=int(prod_atual['quantidade']))
                e_desc = st.text_area("Descrição", value=str(prod_atual['descricao'] or ""))
                nova_img = st.text_input("URL Imagem", value=str(prod_atual['imagem'] or 'placeholder.jpg'))
                
                st.write("")
                if st.button("Salvar Alterações", type="primary", use_container_width=True):
                    if executar_comando("UPDATE produtos SET nome=%s, categoria=%s, preco=%s, quantidade=%s, descricao=%s, imagem=%s WHERE id=%s", 
                                        (e_nome.strip(), e_cat, float(e_preco), int(e_qtd), e_desc.strip(), nova_img, prod_id)):
                        st.success("Alterações salvas!")
                        st.rerun()

        elif acao_prod == "🗑️ Excluir Produto":
            df_produtos = buscar_dados("SELECT id, nome FROM produtos ORDER BY id DESC")
            if not df_produtos.empty:
                opcoes = {f"#{r['id']} - {r['nome']}": r['id'] for _, r in df_produtos.iterrows()}
                del_id = opcoes[st.selectbox("Produto:", list(opcoes.keys()))]
                if st.button("Confirmar Exclusão", type="primary", use_container_width=True):
                    if executar_comando("DELETE FROM produtos WHERE id = %s", (del_id,)):
                        st.success("Produto removido.")
                        st.rerun()

    # TAB 3: PEDIDOS
    elif menu_principal == "🛒 Pedidos":
        st.markdown("<h4 style='color: #000000; font-weight: 800; margin-bottom: 12px;'>Gestão de Pedidos</h4>", unsafe_allow_html=True)
        acao_ped = st.selectbox("Operação:", ["📋 Listagem Geral", "🔍 Auditoria de Fatura", "🔄 Atualizar Status", "📥 Exportar Relatório CSV"])
        st.write("")

        if acao_ped == "📋 Listagem Geral":
            pedidos = buscar_dados("SELECT p.id, c.nome as cliente, p.total, p.status, TO_CHAR(p.data_pedido, 'DD/MM/YYYY HH24:MI') as data FROM pedidos p LEFT JOIN clientes c ON p.cliente_id = c.id ORDER BY p.id DESC")
            if not pedidos.empty:
                for _, r in pedidos.iterrows():
                    st.markdown(f"""
                        <div class="mobile-card">
                            <h4>Pedido #{r['id']}</h4>
                            <p><strong>Cliente:</strong> {r['cliente']} | <strong>Total:</strong> R$ {float(r['total']):,.2f}</p>
                            <p><strong>Status:</strong> {r['status']} | <strong>Data:</strong> {r['data']}</p>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nenhum pedido registrado.")

        elif acao_ped == "🔍 Auditoria de Fatura":
            lista = buscar_dados("SELECT p.id, c.nome, p.total FROM pedidos p JOIN clientes c ON p.cliente_id = c.id ORDER BY p.id DESC")
            if not lista.empty:
                ped_id = st.selectbox("Recibo:", list({f"Nº {r['id']} - {r['nome']} (R$ {r['total']})": r['id'] for _, r in lista.iterrows()}.values()), format_func=lambda x: f"Pedido #{x}")
                info = buscar_dados("SELECT p.id, p.total, p.status, p.data_pedido, c.nome, c.email, c.telefone FROM pedidos p JOIN clientes c ON p.cliente_id = c.id WHERE p.id = %s", (ped_id,))
                if not info.empty:
                    p = info.iloc[0]
                    st.markdown(f"""
                        <div class="card-detalhe">
                            <h4 style="margin:0 0 8px 0; font-weight:900;">🧾 Fatura #{p['id']}</h4>
                            <p style="margin:2px 0;"><strong>Status:</strong> {str(p['status']).upper()}</p>
                            <p style="margin:2px 0;"><strong>Data:</strong> {p['data_pedido']}</p>
                            <hr style="margin:12px 0; border:0; border-top:1px solid #000000;">
                            <h5 style="margin:0 0 8px 0; font-weight:800;">Cliente:</h5>
                            <p style="margin:2px 0;"><strong>Nome:</strong> {p['nome']}</p>
                            <p style="margin:2px 0;"><strong>Contato:</strong> {p['telefone'] or 'N/A'} | {p['email']}</p>
                        </div>
                    """, unsafe_allow_html=True)

                    itens = buscar_dados("SELECT pr.nome as item, ip.quantidade as qtd, ip.preco_unitario as unitario, (ip.quantidade * ip.preco_unitario) as subtotal FROM itens_pedido ip JOIN produtos pr ON ip.produto_id = pr.id WHERE ip.pedido_id = %s", (ped_id,))
                    if not itens.empty:
                        st.dataframe(itens, use_container_width=True, hide_index=True)
                        st.markdown(f"""
                            <div style="background:#000000; color:#ffffff; padding:12px; border-radius:8px; text-align:center; font-weight:900; font-size:1.1rem; margin-top:8px;">
                                Total Faturado: R$ {float(p['total']):,.2f}
                            </div>
                        """, unsafe_allow_html=True)

        elif acao_ped == "🔄 Atualizar Status":
            pendentes = buscar_dados("SELECT id, status FROM pedidos ORDER BY id DESC")
            if not pendentes.empty:
                opcoes = {f"#{r['id']} (Atual: {r['status']})": r['id'] for _, r in pendentes.iterrows()}
                ped_id = opcoes[st.selectbox("Pedido:", list(opcoes.keys()))]
                novo_status = st.selectbox("Status:", ["Pendente", "Em processamento", "Enviado", "Entregue", "Concluído", "Cancelado"])
                if st.button("Atualizar Status", type="primary", use_container_width=True):
                    if executar_comando("UPDATE pedidos SET status = %s WHERE id = %s", (novo_status, ped_id)):
                        st.success("Status atualizado!")
                        st.rerun()

        elif acao_ped == "📥 Exportar Relatório CSV":
            st.markdown("<h5 style='font-weight:800;'>Relatório Consolidado</h5>", unsafe_allow_html=True)
            df_export = buscar_dados("SELECT p.id, c.nome as cliente, c.email, p.total, p.status, p.data_pedido FROM pedidos p LEFT JOIN clientes c ON p.cliente_id = c.id ORDER BY p.id DESC")
            if not df_export.empty:
                csv_data = df_export.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📄 Descarregar Arquivo CSV",
                    data=csv_data,
                    file_name="relatorio_jr_iluminacao.csv",
                    mime="text/csv",
                    use_container_width=True,
                    type="primary"
                )

    # TAB 4: CLIENTES
    elif menu_principal == "👥 Clientes":
        st.markdown("<h4 style='color: #000000; font-weight: 800; margin-bottom: 12px;'>Gestão de Usuários</h4>", unsafe_allow_html=True)
        acao_cli = st.selectbox("Painel:", ["📋 Todos os Clientes", "✅ Aprovações Pendentes", "➕ Adicionar Cliente"])
        st.write("")

        if acao_cli == "📋 Todos os Clientes":
            df_clientes = buscar_dados("SELECT u.id, u.nome, u.email, u.status, COALESCE(TO_CHAR(a.ultimo_login, 'DD/MM/YYYY HH24:MI'), 'Sem Registo') as ultimo_login FROM usuarios u LEFT JOIN autenticacao a ON a.usuario_id = u.id WHERE u.role = 'cliente' ORDER BY u.id DESC")
            if not df_clientes.empty:
                for _, r in df_clientes.iterrows():
                    st.markdown(f"""
                        <div class="mobile-card">
                            <h4>{r['nome']}</h4>
                            <p><strong>E-mail:</strong> {r['email']}</p>
                            <p><strong>Status:</strong> <strong>{r['status']}</strong></p>
                            <p style="font-size: 0.85rem; color: #555555;">Último Acesso: {r['ultimo_login']}</p>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nenhum cliente registrado.")

        elif acao_cli == "✅ Aprovações Pendentes":
            pendentes = buscar_dados("SELECT id, nome, email FROM usuarios WHERE status = 'Pendente' AND role = 'cliente'")
            if not pendentes.empty:
                opcoes = {f"#{r['id']} - {r['nome']} ({r['email']})": r['id'] for _, r in pendentes.iterrows()}
                user_id = opcoes[st.selectbox("Conta:", list(opcoes.keys()))]
                
                if st.button("Aprovar Conta", type="primary", use_container_width=True):
                    reg = pendentes[pendentes['id'] == user_id].iloc[0]
                    if executar_comando("UPDATE usuarios SET status = 'Aprovado' WHERE id = %s", (user_id,)):
                        msg = f"✅ *Conta Aprovada pelo Admin!*\n\n👤 *Cliente:* {reg['nome']}\n📧 *E-mail:* {reg['email']}\n🔓 Acesso autorizado."
                        enviar_telegram_aviso(msg)
                        st.success("Conta liberada com sucesso!")
                        st.rerun()
            else:
                st.success("Sem contas pendentes de aprovação.")

        elif acao_cli == "➕ Adicionar Cliente":
            nome_cli = st.text_input("Nome")
            email_cli = st.text_input("E-mail")
            if st.button("Cadastrar", type="primary", use_container_width=True):
                if nome_cli and email_cli:
                    if executar_comando("INSERT INTO usuarios (nome, email, role, status) VALUES (%s, %s, 'cliente', 'Aprovado')", (nome_cli, email_cli)):
                        st.success("Cliente cadastrado!")
                        st.rerun()
