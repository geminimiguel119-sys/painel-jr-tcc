import base64
import psycopg2
import streamlit as st
import pandas as pd
import urllib.parse
import urllib.request

# ==========================================
# 1. TRAVA TOTAL DE CORES (PRETO & BRANCO)
# ==========================================
st.set_page_config(page_title="JR Admin", page_icon="💡", layout="centered")

st.markdown("""
    <style>
    /* Força fundo branco global e texto preto */
    html, body, [data-testid="stAppViewContainer"], .main {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    .block-container {
        max-width: 480px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 5rem !important;
        margin: 0 auto !important;
    }
    
    /* Remove cabeçalhos, rodapés e tags vazias do Streamlit */
    #MainMenu, header, footer, [data-testid="stToolbar"] { 
        visibility: hidden !important; 
        display: none !important; 
    }
    
    /* Todos os textos e rótulos pretos */
    h1, h2, h3, h4, h5, p, span, label, div {
        color: #000000 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }
    
    /* CORREÇÃO DOS INPUTS: Fundo branco e texto preto bem nítido */
    input, textarea, [data-baseweb="input"], [data-baseweb="base-input"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        border-radius: 8px !important;
    }
    input::placeholder {
        color: #71717a !important;
    }
    
    /* CORREÇÃO DO BOTÃO: Fundo preto e TEXTO BRANCO OBRIGATÓRIO */
    div.stButton > button, div.stButton > button * {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 2px solid #000000 !important;
        border-radius: 8px !important;
        font-weight: 800 !important;
        font-size: 1rem !important;
        min-height: 48px !important;
    }
    div.stButton > button:hover {
        background-color: #27272a !important;
    }

    /* Rádios e abas de navegação */
    div[role="radiogroup"] {
        background-color: #f4f4f5 !important;
        border: 2px solid #000000 !important;
        border-radius: 10px !important;
        padding: 4px !important;
    }
    div[role="radiogroup"] label {
        flex: 1 !important;
        text-align: center !important;
        border-radius: 6px !important;
        padding: 8px 4px !important;
    }
    div[role="radiogroup"] label > div:first-child { display: none !important; }
    div[role="radiogroup"] label[data-checked="true"] {
        background-color: #000000 !important;
    }
    div[role="radiogroup"] label[data-checked="true"] p, 
    div[role="radiogroup"] label[data-checked="true"] span {
        color: #ffffff !important;
        font-weight: bold !important;
    }
    div[role="radiogroup"] label[data-checked="false"] p {
        color: #000000 !important;
    }

    /* Cards e Containers com contorno preto nítido */
    div[data-testid="stMetric"], .mobile-card, .card-detalhe {
        background-color: #ffffff !important;
        border: 2px solid #000000 !important;
        border-radius: 10px !important;
        padding: 14px !important;
        margin-bottom: 12px !important;
        box-shadow: 2px 2px 0px #000000 !important;
    }
    
    /* Selectbox e Menus suspensos */
    div[data-baseweb="select"] * {
        background-color: #ffffff !important;
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

# ==========================================
# 3. TELA DE LOGIN
# ==========================================
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("""
        <div style='text-align: center; margin-top: 2rem; margin-bottom: 1.5rem;'>
            <div style='font-size: 3rem; margin-bottom: 8px;'>💡</div>
            <h1 style='font-size: 1.7rem; color: #000000; margin: 0; font-weight: 900;'>JR Iluminação</h1>
            <p style='color: #4b5563; font-size: 0.95rem; margin-top: 4px;'>Painel de Gestão e Administração</p>
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
        st.markdown("<h3 style='margin:0; font-weight:900;'>💡 JR Admin</h3>", unsafe_allow_html=True)
    with col_logout:
        if st.button("Sair", use_container_width=True):
            st.session_state["autenticado"] = False
            st.rerun()

    st.write("")
    menu_principal = st.radio("Menu", ["📊 Geral", "📦 Produtos", "🛒 Pedidos", "👥 Clientes"], horizontal=True, label_visibility="collapsed")
    st.write("")

    # ABA GERAL
    if menu_principal == "📊 Geral":
        st.markdown("<h4 style='font-weight:900; margin-bottom:12px;'>Métricas da Loja</h4>", unsafe_allow_html=True)
        
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
        st.markdown("<h5 style='font-weight:900;'>Vendas Recentes</h5>", unsafe_allow_html=True)
        df_vendas_data = buscar_dados("SELECT TO_CHAR(data_pedido, 'DD/MM') as dia, SUM(total) as total_dia FROM pedidos GROUP BY dia ORDER BY dia ASC LIMIT 7")
        if not df_vendas_data.empty:
            st.bar_chart(df_vendas_data.set_index('dia')['total_dia'])

    # ABA PRODUTOS
    elif menu_principal == "📦 Produtos":
        st.markdown("<h4 style='font-weight:900; margin-bottom:12px;'>Catálogo e Estoque</h4>", unsafe_allow_html=True)
        acao_prod = st.selectbox("Operação:", ["📋 Listar Produtos", "➕ Cadastrar Produto", "🗑️ Excluir Produto"])
        st.write("")

        if acao_prod == "📋 Listar Produtos":
            df_produtos = buscar_dados("SELECT id, nome, categoria, preco, quantidade FROM produtos ORDER BY id DESC")
            if not df_produtos.empty:
                for _, r in df_produtos.iterrows():
                    st.markdown(f"""
                        <div class="mobile-card">
                            <h4 style="margin:0 0 4px 0;">{r['nome']}</h4>
                            <p style="margin:2px 0;"><strong>Categoria:</strong> {r.get('categoria', 'Geral')}</p>
                            <p style="margin:2px 0;"><strong>Preço:</strong> R$ {float(r['preco']):,.2f} | <strong>Estoque:</strong> {r['quantidade']} un.</p>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nenhum produto cadastrado.")

        elif acao_prod == "➕ Cadastrar Produto":
            novo_nome = st.text_input("Nome do Produto")
            nova_cat = st.selectbox("Categoria", ["Lâmpadas", "Fitas LED", "Spots", "Plafons", "Outros"])
            novo_preco = st.number_input("Preço (R$)", min_value=0.01, step=0.50, format="%.2f")
            nova_qtd = st.number_input("Quantidade", min_value=0, step=1, value=10)
            
            if st.button("Gravar Produto", type="primary", use_container_width=True):
                if novo_nome.strip():
                    if executar_comando("INSERT INTO produtos (nome, categoria, preco, quantidade, imagem) VALUES (%s, %s, %s, %s, 'placeholder.jpg')", 
                                        (novo_nome.strip(), nova_cat, float(novo_preco), int(nova_qtd))):
                        st.success("Produto cadastrado com sucesso!")
                        st.rerun()

        elif acao_prod == "🗑️ Excluir Produto":
            df_produtos = buscar_dados("SELECT id, nome FROM produtos ORDER BY id DESC")
            if not df_produtos.empty:
                opcoes = {f"#{r['id']} - {r['nome']}": r['id'] for _, r in df_produtos.iterrows()}
                del_id = opcoes[st.selectbox("Produto para remover:", list(opcoes.keys()))]
                if st.button("Confirmar Exclusão", type="primary", use_container_width=True):
                    if executar_comando("DELETE FROM produtos WHERE id = %s", (del_id,)):
                        st.success("Removido com sucesso.")
                        st.rerun()

    # ABA PEDIDOS
    elif menu_principal == "🛒 Pedidos":
        st.markdown("<h4 style='font-weight:900; margin-bottom:12px;'>Gestão de Pedidos</h4>", unsafe_allow_html=True)
        acao_ped = st.selectbox("Operação:", ["📋 Listagem Geral", "🔍 Detalhe do Pedido", "📥 Exportar CSV"])
        st.write("")

        if acao_ped == "📋 Listagem Geral":
            pedidos = buscar_dados("SELECT p.id, c.nome as cliente, p.total, p.status, TO_CHAR(p.data_pedido, 'DD/MM/YYYY HH24:MI') as data FROM pedidos p LEFT JOIN clientes c ON p.cliente_id = c.id ORDER BY p.id DESC")
            if not pedidos.empty:
                for _, r in pedidos.iterrows():
                    st.markdown(f"""
                        <div class="mobile-card">
                            <h4 style="margin:0 0 4px 0;">Pedido #{r['id']}</h4>
                            <p style="margin:2px 0;"><strong>Cliente:</strong> {r['cliente']} | <strong>Total:</strong> R$ {float(r['total']):,.2f}</p>
                            <p style="margin:2px 0;"><strong>Status:</strong> {r['status']} | <strong>Data:</strong> {r['data']}</p>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nenhum pedido registrado.")

        elif acao_ped == "🔍 Detalhe do Pedido":
            lista = buscar_dados("SELECT p.id, c.nome, p.total FROM pedidos p JOIN clientes c ON p.cliente_id = c.id ORDER BY p.id DESC")
            if not lista.empty:
                ped_id = st.selectbox("Recibo:", list({f"Nº {r['id']} - {r['nome']} (R$ {r['total']})": r['id'] for _, r in lista.iterrows()}.values()), format_func=lambda x: f"Pedido #{x}")
                info = buscar_dados("SELECT p.id, p.total, p.status, p.data_pedido, c.nome, c.email, c.telefone FROM pedidos p JOIN clientes c ON p.cliente_id = c.id WHERE p.id = %s", (ped_id,))
                if not info.empty:
                    p = info.iloc[0]
                    st.markdown(f"""
                        <div class="card-detalhe">
                            <h4 style="margin:0 0 8px 0; font-weight:900;">🧾 Pedido #{p['id']}</h4>
                            <p style="margin:2px 0;"><strong>Status:</strong> {str(p['status']).upper()}</p>
                            <p style="margin:2px 0;"><strong>Data:</strong> {p['data_pedido']}</p>
                            <hr style="margin:10px 0; border:0; border-top:1px solid #000000;">
                            <p style="margin:2px 0;"><strong>Cliente:</strong> {p['nome']}</p>
                            <p style="margin:2px 0;"><strong>Contato:</strong> {p['telefone'] or 'N/A'} | {p['email']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    itens = buscar_dados("SELECT pr.nome as item, ip.quantidade as qtd, ip.preco_unitario as unitario, (ip.quantidade * ip.preco_unitario) as subtotal FROM itens_pedido ip JOIN produtos pr ON ip.produto_id = pr.id WHERE ip.pedido_id = %s", (ped_id,))
                    if not itens.empty:
                        st.dataframe(itens, use_container_width=True, hide_index=True)

        elif acao_ped == "📥 Exportar CSV":
            df_export = buscar_dados("SELECT p.id, c.nome as cliente, c.email, p.total, p.status, p.data_pedido FROM pedidos p LEFT JOIN clientes c ON p.cliente_id = c.id ORDER BY p.id DESC")
            if not df_export.empty:
                st.download_button(
                    label="📄 Baixar Relatório CSV",
                    data=df_export.to_csv(index=False).encode('utf-8'),
                    file_name="relatorio_pedidos.csv",
                    mime="text/csv",
                    use_container_width=True,
                    type="primary"
                )

    # ABA CLIENTES
    elif menu_principal == "👥 Clientes":
        st.markdown("<h4 style='font-weight:900; margin-bottom:12px;'>Gestão de Usuários</h4>", unsafe_allow_html=True)
        acao_cli = st.selectbox("Operação:", ["📋 Todos os Clientes", "✅ Aprovações Pendentes"])
        st.write("")

        if acao_cli == "📋 Todos os Clientes":
            df_clientes = buscar_dados("SELECT u.id, u.nome, u.email, u.status, COALESCE(TO_CHAR(a.ultimo_login, 'DD/MM/YYYY HH24:MI'), 'Sem Registro') as ultimo_login FROM usuarios u LEFT JOIN autenticacao a ON a.usuario_id = u.id WHERE u.role = 'cliente' ORDER BY u.id DESC")
            if not df_clientes.empty:
                for _, r in df_clientes.iterrows():
                    st.markdown(f"""
                        <div class="mobile-card">
                            <h4 style="margin:0 0 4px 0;">👤 {r['nome']}</h4>
                            <p style="margin:2px 0;"><strong>E-mail:</strong> {r['email']}</p>
                            <p style="margin:2px 0;"><strong>Status:</strong> <strong>{r['status']}</strong></p>
                            <p style="margin:2px 0; font-size:0.85rem; color:#4b5563;">Último Acesso: {r['ultimo_login']}</p>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nenhum cliente cadastrado.")

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
