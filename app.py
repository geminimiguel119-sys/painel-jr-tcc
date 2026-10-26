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
# 1. CONFIGURAÇÃO E CSS DE ALTO CONTRASTE TOTAL
# ==========================================
st.set_page_config(page_title="JR Admin", page_icon="💡", layout="centered")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], .main, .block-container, [data-testid="stHeader"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    .block-container {
        max-width: 500px !important;
        padding-top: 1.2rem !important;
        padding-bottom: 5rem !important;
        margin: 0 auto !important;
    }
    #MainMenu, header, footer, [data-testid="stToolbar"] { 
        visibility: hidden !important; 
        display: none !important; 
    }
    h1, h2, h3, h4, h5, h6, p, label, small, strong {
        color: #000000 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }
    input, textarea, select, [data-baseweb="input"], [data-baseweb="base-input"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        border: 2px solid #000000 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    [data-testid="stNumberInput"] input,
    [data-testid="stTextInput"] input {
        background-color: #ffffff !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }
    [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 2px solid #000000 !important;
        border-radius: 8px !important;
    }
    [data-baseweb="select"] span, [data-baseweb="select"] div {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }
    ul[role="listbox"], [data-baseweb="popover"], [data-baseweb="menu"] {
        background-color: #ffffff !important;
        border: 2px solid #000000 !important;
    }
    li[role="option"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }
    li[role="option"]:hover, li[aria-selected="true"] {
        background-color: #000000 !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    li[role="option"]:hover *, li[aria-selected="true"] * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    [data-baseweb="input"] button, [data-baseweb="input"] svg,
    button[aria-label="Show password"], button[aria-label="Hide password"] {
        background-color: transparent !important;
        color: #000000 !important;
        fill: #000000 !important;
        border: none !important;
    }
    div.stButton > button, div.stDownloadButton > button {
        background-color: #000000 !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: 2px solid #000000 !important;
        border-radius: 8px !important;
        font-weight: 800 !important;
        font-size: 1rem !important;
        min-height: 48px !important;
    }
    div.stButton > button:hover {
        background-color: #27272a !important;
    }
    div.stButton > button p, div.stButton > button span, div.stButton > button div,
    div.stDownloadButton > button p, div.stDownloadButton > button span {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    div[role="radiogroup"] {
        background-color: #f4f4f5 !important;
        border: 2px solid #000000 !important;
        border-radius: 10px !important;
        padding: 4px !important;
        display: flex !important;
        gap: 4px !important;
        overflow-x: auto !important;
    }
    div[role="radiogroup"] label {
        flex: 1 !important;
        text-align: center !important;
        border-radius: 6px !important;
        padding: 8px 4px !important;
        background: transparent !important;
        white-space: nowrap !important;
    }
    div[role="radiogroup"] label > div:first-child { display: none !important; }
    div[role="radiogroup"] label[data-checked="true"] {
        background-color: #000000 !important;
    }
    div[role="radiogroup"] label[data-checked="true"] p, div[role="radiogroup"] label[data-checked="true"] span {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-weight: 800 !important;
    }
    div[role="radiogroup"] label[data-checked="false"] p, div[role="radiogroup"] label[data-checked="false"] span {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetric"], .mobile-card, .card-detalhe {
        background-color: #ffffff !important;
        border: 2px solid #000000 !important;
        border-radius: 10px !important;
        padding: 14px !important;
        margin-bottom: 12px !important;
        box-shadow: 3px 3px 0px #000000 !important;
    }
    div[data-testid="stMetricLabel"] p {
        font-size: 0.85rem !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-weight: 800 !important;
    }
    div[data-testid="stMetricValue"] div {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-weight: 900 !important;
    }
    [data-testid="stDataFrame"] {
        border: 2px solid #000000 !important;
        border-radius: 8px !important;
        background-color: #ffffff !important;
    }
    .brand-logo-img {
        width: 80px;
        height: 80px;
        object-fit: contain;
        border-radius: 12px;
        border: 2px solid #000000;
        margin-bottom: 12px;
        background: #ffffff;
    }
    
    /* Novo Estilo para Etiquetas da Curva ABC */
    .badge-abc-a { background:#fef08a; color:#854d0e; padding:3px 8px; border-radius:4px; font-weight:900; font-size:0.8rem; border:1px solid #eab308; }
    .badge-abc-b { background:#e5e7eb; color:#374151; padding:3px 8px; border-radius:4px; font-weight:800; font-size:0.8rem; }
    .badge-abc-c { background:#fed7aa; color:#9a3412; padding:3px 8px; border-radius:4px; font-weight:700; font-size:0.8rem; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CARREGAMENTO DE VARIÁVEIS E LOGO
# ==========================================
def obter_config(chave, padrao=None):
    valor = os.getenv(chave)
    if valor: return valor
    try:
        if chave in st.secrets: return str(st.secrets[chave])
    except Exception: pass
    return padrao

def obter_logo_html():
    possiveis_caminhos = ["TCC_V2/img/logo.jpg", "img/logo.jpg", "TCC_V2/img/logo.png", "img/logo.png"]
    for caminho in possiveis_caminhos:
        if os.path.exists(caminho):
            try:
                with open(caminho, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                    return f"<img class='brand-logo-img' src='data:image/jpeg;base64,{b64}' alt='Logo JR'>"
            except Exception: pass
    return "<div style='font-size: 3.5rem; margin-bottom: 8px;'>💡</div>"

# ==========================================
# 3. CONEXÃO SEGURA AO SUPABASE
# ==========================================
def get_db_connection():
    db_host = obter_config("DB_HOST")
    db_port = obter_config("DB_PORT", "5432")
    db_name = obter_config("DB_NAME", "postgres")
    db_user = obter_config("DB_USER")
    db_pass = obter_config("DB_PASS")

    if not db_host or not db_user or not db_pass:
        st.error("⚠️ Configuração pendente: DB_HOST, DB_USER e DB_PASS ausentes nas variáveis de ambiente.")
        st.stop()

    conn = psycopg2.connect(host=db_host, port=db_port, database=db_name, user=db_user, password=db_pass, sslmode="require")
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
        logging.error(f"Erro SQL em buscar_dados: {e}")
        st.error("Falha ao carregar os dados do banco de dados.")
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
        logging.error(f"Erro SQL em executar_comando: {e}")
        return False

def enviar_telegram_aviso(msg):
    token = obter_config("TELEGRAM_BOT_TOKEN")
    chat_id = obter_config("TELEGRAM_CHAT_ID")
    if not token or not chat_id: return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = urllib.parse.urlencode({"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}).encode()
        urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=4)
    except Exception: pass

def upload_imagem_supabase(arquivo):
    supabase_url = obter_config("SUPABASE_URL")
    storage_key = obter_config("SUPABASE_STORAGE_KEY")
    if not supabase_url or not storage_key or arquivo.size > 5 * 1024 * 1024:
        return "placeholder.jpg"
    try:
        nome_ext = arquivo.name.split('.')[-1].lower()
        if nome_ext not in ["jpg", "jpeg", "png"]: return "placeholder.jpg"
        nome_arquivo = f"prod_{os.urandom(4).hex()}.{nome_ext}"
        upload_url = f"{supabase_url.rstrip('/')}/storage/v1/object/produtos/{nome_arquivo}"
        headers = {"Authorization": f"Bearer {storage_key}", "Content-Type": arquivo.type}
        req = urllib.request.Request(upload_url, data=arquivo.getvalue(), headers=headers, method="POST")
        with urllib.request.urlopen(req) as resp:
            if resp.status in [200, 201]:
                return f"{supabase_url.rstrip('/')}/storage/v1/object/public/produtos/{nome_arquivo}"
    except Exception: pass
    return "placeholder.jpg"

def validar_credenciais_admin(usuario_input, senha_input):
    au = obter_config("ADMIN_USER")
    ap = obter_config("ADMIN_PASS")
    if au and ap and hmac.compare_digest(usuario_input.strip(), au.strip()) and hmac.compare_digest(senha_input, ap):
        return True
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
        conn.commit()
        cursor.execute("""
            SELECT u.id FROM usuarios u JOIN autenticacao a ON a.usuario_id = u.id
            WHERE (LOWER(u.email) = LOWER(%s) OR LOWER(u.nome) = LOWER(%s))
              AND u.role = 'admin' AND u.status = 'Aprovado' AND a.senha = crypt(%s, a.senha) LIMIT 1;
        """, (usuario_input.strip(), usuario_input.strip(), senha_input))
        valido = cursor.fetchone() is not None
        cursor.close()
        conn.close()
        return valido
    except Exception: return False

# ==========================================
# 4. TELA DE LOGIN
# ==========================================
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
if "tentativas" not in st.session_state: st.session_state["tentativas"] = 0

if not st.session_state["autenticado"]:
    st.markdown(f"<div style='text-align: center; margin-top: 2rem; margin-bottom: 1.5rem;'>{obter_logo_html()}<h1 style='font-size: 1.7rem; margin: 0; font-weight: 900;'>JR Iluminação</h1><p style='color: #27272a; font-size: 0.95rem; font-weight: 600;'>Painel de Gestão e Inteligência</p></div>", unsafe_allow_html=True)
    usuario = st.text_input("Usuário ou e-mail")
    senha = st.text_input("Senha", type="password")
    st.write("")
    
    if st.button("Acessar o Painel", use_container_width=True, type="primary"):
        if st.session_state["tentativas"] >= 5:
            st.error("Bloqueio de segurança. Recarregue a página.")
        elif not usuario.strip() or not senha:
            st.warning("Preencha as credenciais.")
        elif validar_credenciais_admin(usuario, senha):
            st.session_state["tentativas"] = 0
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.session_state["tentativas"] += 1
            st.error("Acesso negado.")

# ==========================================
# 5. PAINEL PRINCIPAL
# ==========================================
else:
    col_logo, col_logout = st.columns([3, 1], vertical_alignment="center")
    with col_logo: st.markdown("<h3 style='margin:0; font-weight:900;'>💡 JR Admin</h3>", unsafe_allow_html=True)
    with col_logout:
        if st.button("Sair", use_container_width=True):
            st.session_state["autenticado"] = False
            st.rerun()

    st.write("")
    menu_principal = st.radio("Menu", ["📊 Geral", "📦 Produtos", "🔮 BI Preditivo", "🛒 Pedidos", "👥 Clientes"], horizontal=True, label_visibility="collapsed")
    st.write("")

    # ------------------ ABA GERAL ------------------
    if menu_principal == "📊 Geral":
        st.markdown("<h4 style='font-weight:900; margin-bottom:12px;'>Métricas da Loja</h4>", unsafe_allow_html=True)
        df_prod = buscar_dados("SELECT SUM(quantidade) as total_estoque FROM produtos;")
        df_ped = buscar_dados("SELECT COUNT(id) as total_pedidos, SUM(total) as fat FROM pedidos WHERE status != 'Cancelado';")
        df_cli = buscar_dados("SELECT COUNT(id) as total_clientes FROM usuarios WHERE role='cliente';")
        
        c1, c2 = st.columns(2)
        c1.metric("Faturamento", f"R$ {float(df_ped['fat'].iloc[0] if not df_ped.empty and pd.notna(df_ped['fat'].iloc[0]) else 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        c2.metric("Total Pedidos", str(df_ped['total_pedidos'].iloc[0] if not df_ped.empty else 0))
        c3, c4 = st.columns(2)
        c3.metric("Estoque Total", f"{int(df_prod['total_estoque'].iloc[0] if not df_prod.empty and pd.notna(df_prod['total_estoque'].iloc[0]) else 0)} un.")
        c4.metric("Clientes", str(df_cli['total_clientes'].iloc[0] if not df_cli.empty else 0))

        st.markdown("---")
        st.markdown("<h5 style='font-weight:900;'>Vendas Recentes</h5>", unsafe_allow_html=True)
        df_vendas_data = buscar_dados("SELECT TO_CHAR(DATE(data_pedido), 'DD/MM') AS dia, DATE(data_pedido) AS data_ordem, SUM(total) AS total_dia FROM pedidos WHERE status != 'Cancelado' GROUP BY DATE(data_pedido) ORDER BY data_ordem DESC LIMIT 7;")
        if not df_vendas_data.empty:
            st.bar_chart(df_vendas_data.sort_values('data_ordem', ascending=True).set_index('dia')['total_dia'])
        else:
            st.info("Sem histórico de vendas recente.")

    # ------------------ ABA PRODUTOS ------------------
    elif menu_principal == "📦 Produtos":
        st.markdown("<h4 style='font-weight:900; margin-bottom:12px;'>Catálogo e Estoque</h4>", unsafe_allow_html=True)
        acao_prod = st.selectbox("Operação:", ["📋 Listar Produtos", "➕ Cadastrar Produto", "✏️ Editar Produto", "🗑️ Excluir Produto"])
        st.write("")

        if acao_prod == "📋 Listar Produtos":
            df_produtos = buscar_dados("SELECT id, nome, categoria, preco, quantidade, imagem FROM produtos ORDER BY id DESC")
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
            nova_cat = st.selectbox("Categoria:", ["Lâmpadas", "Fitas LED", "Spots", "Plafons", "Outros"])
            novo_preco = st.number_input("Preço de Venda (R$)", min_value=0.01, format="%.2f")
            nova_qtd = st.number_input("Quantidade em Estoque", min_value=0, step=1, value=10)
            nova_desc = st.text_area("Descrição Técnica")
            arquivo_foto = st.file_uploader("Foto (Opcional)", type=["jpg", "jpeg", "png"])
            
            if st.button("Gravar Produto", type="primary", use_container_width=True):
                if novo_nome.strip():
                    img = upload_imagem_supabase(arquivo_foto) if arquivo_foto else "placeholder.jpg"
                    if executar_comando("INSERT INTO produtos (nome, categoria, preco, quantidade, descricao, imagem) VALUES (%s, %s, %s, %s, %s, %s)", (novo_nome.strip(), nova_cat, float(novo_preco), int(nova_qtd), nova_desc.strip(), img)):
                        st.success("Cadastrado com sucesso!"); st.rerun()
                else: st.warning("Informe o nome do produto.")

        elif acao_prod == "✏️ Editar Produto":
            df_p = buscar_dados("SELECT * FROM produtos ORDER BY nome ASC")
            if not df_p.empty:
                opcoes = {f"#{r['id']} - {r['nome']}": r['id'] for _, r in df_p.iterrows()}
                prod_id = opcoes[st.selectbox("Selecione o Produto:", list(opcoes.keys()))]
                p = df_p[df_p['id'] == prod_id].iloc[0]
                
                e_nome = st.text_input("Nome", value=str(p['nome']))
                cat_lista = ["Lâmpadas", "Fitas LED", "Spots", "Plafons", "Outros"]
                e_cat = st.selectbox("Categoria", cat_lista, index=cat_lista.index(p.get('categoria', 'Outros')) if p.get('categoria', 'Outros') in cat_lista else 4)
                e_preco = st.number_input("Preço (R$)", min_value=0.01, value=float(p['preco']), format="%.2f")
                e_qtd = st.number_input("Estoque", min_value=0, value=int(p['quantidade']))
                e_desc = st.text_area("Descrição", value=str(p['descricao'] or ""))
                arquivo_foto = st.file_uploader("Substituir Foto", type=["jpg", "jpeg", "png"])
                
                if st.button("Salvar Alterações", type="primary", use_container_width=True):
                    img = upload_imagem_supabase(arquivo_foto) if arquivo_foto else p['imagem']
                    if executar_comando("UPDATE produtos SET nome=%s, categoria=%s, preco=%s, quantidade=%s, descricao=%s, imagem=%s WHERE id=%s", (e_nome.strip(), e_cat, float(e_preco), int(e_qtd), e_desc.strip(), img, prod_id)):
                        st.success("Produto atualizado com sucesso!"); st.rerun()

        elif acao_prod == "🗑️ Excluir Produto":
            df_p = buscar_dados("SELECT id, nome FROM produtos ORDER BY id DESC")
            if not df_p.empty:
                opcoes = {f"#{r['id']} - {r['nome']}": r['id'] for _, r in df_p.iterrows()}
                del_id = opcoes[st.selectbox("Produto para remover:", list(opcoes.keys()))]
                if st.button("Confirmar Exclusão", type="primary", use_container_width=True):
                    if executar_comando("DELETE FROM produtos WHERE id = %s", (del_id,)):
                        st.success("Produto removido com sucesso!"); st.rerun()

    # ------------------ ABA BI PREDITIVO (NOVO) ------------------
    elif menu_principal == "🔮 BI Preditivo":
        st.markdown("<h4 style='font-weight:900; margin-bottom:4px;'>Inteligência de Suprimentos</h4>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.85rem; color:#475569; margin-bottom:16px;'>Cálculo com Análise de Tendência, Curva ABC e Ponto de Reposição.</p>", unsafe_allow_html=True)

        c_slider, c_lead = st.columns([2,1])
        with c_slider: dias_analise = st.slider("Dias Analisados (Média):", min_value=7, max_value=60, value=30)
        with c_lead: lead_time_dias = st.number_input("Lead Time (Dias)", value=5, min_value=1)
        
        # SQL Inteligente: Traz vendas atuais e do período anterior para calcular Tendência e Curva ABC
        query_bi = """
            SELECT 
                p.id,
                p.nome,
                COALESCE(p.quantidade, 0) AS estoque_atual,
                p.preco,
                -- Vendas da janela atual
                COALESCE(SUM(CASE WHEN ped.id IS NOT NULL AND ped.status != 'Cancelado' AND ped.data_pedido >= NOW() - make_interval(days => %s) THEN ip.quantidade ELSE 0 END), 0) AS total_atual,
                -- Vendas da janela anterior idêntica (para tendência)
                COALESCE(SUM(CASE WHEN ped.id IS NOT NULL AND ped.status != 'Cancelado' AND ped.data_pedido >= NOW() - make_interval(days => %s * 2) AND ped.data_pedido < NOW() - make_interval(days => %s) THEN ip.quantidade ELSE 0 END), 0) AS total_anterior,
                -- Faturamento do item na janela atual (para Curva ABC)
                COALESCE(SUM(CASE WHEN ped.id IS NOT NULL AND ped.status != 'Cancelado' AND ped.data_pedido >= NOW() - make_interval(days => %s) THEN (ip.quantidade * ip.preco_unitario) ELSE 0 END), 0) AS fat_produto
            FROM produtos p
            LEFT JOIN itens_pedido ip ON ip.produto_id = p.id
            LEFT JOIN pedidos ped ON ped.id = ip.pedido_id
            GROUP BY p.id, p.nome, p.quantidade, p.preco
        """
        
        df_bi = buscar_dados(query_bi, params=(int(dias_analise), int(dias_analise), int(dias_analise), int(dias_analise)))

        if not df_bi.empty:
            # 1. Matemática da Curva ABC
            df_bi = df_bi.sort_values(by='fat_produto', ascending=False)
            total_vendas_loja = df_bi['fat_produto'].sum()
            if total_vendas_loja > 0:
                df_bi['pct_fat'] = df_bi['fat_produto'] / total_vendas_loja
                df_bi['cum_pct'] = df_bi['pct_fat'].cumsum()
                df_bi['curva_abc'] = df_bi['cum_pct'].apply(lambda x: 'A' if x <= 0.80 else ('B' if x <= 0.95 else 'C'))
            else:
                df_bi['curva_abc'] = 'C'

            # 2. Matemática de Consumo e Tendência
            df_bi['cmd'] = df_bi['total_atual'] / float(dias_analise)
            df_bi['cmd_ant'] = df_bi['total_anterior'] / float(dias_analise)
            
            def calc_tendencia(atual, ant):
                if ant == 0 and atual > 0: return 100.0
                if ant == 0 and atual == 0: return 0.0
                return ((atual - ant) / ant) * 100.0
                
            df_bi['tendencia_pct'] = df_bi.apply(lambda row: calc_tendencia(row['total_atual'], row['total_anterior']), axis=1)

            # 3. Matemática de Ruptura
            df_bi['dias_restantes'] = df_bi.apply(lambda r: int(r['estoque_atual'] / r['cmd']) if r['cmd'] > 0 else 999, axis=1)
            df_bi['ponto_reposicao'] = (df_bi['cmd'] * lead_time_dias).round().astype(int) + 2

            # Ordenação de Risco (Ruptura em Curva A aparece primeiro)
            df_bi = df_bi.sort_values(by=['dias_restantes', 'curva_abc'], ascending=[True, True])

            # DASHBOARD EXECUTIVO - RESUMO
            criticos = df_bi[df_bi['dias_restantes'] <= lead_time_dias]
            criticos_curva_a = len(criticos[criticos['curva_abc'] == 'A'])
            
            mc1, mc2 = st.columns(2)
            mc1.metric("Itens em Ruptura Iminente", len(criticos), delta=f"{criticos_curva_a} na Curva A (Urgente)" if criticos_curva_a > 0 else None, delta_color="inverse")
            mc2.metric("Valor Faturado (Período)", f"R$ {total_vendas_loja:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            st.markdown("---")

            # LISTAGEM INTELIGENTE DOS ITENS
            st.markdown("<h5 style='font-weight:900;'>Ações Prioritárias de Reposição</h5>", unsafe_allow_html=True)
            
            for _, r in df_bi.iterrows():
                # Etiqueta Curva ABC
                badge_abc = f"<span class='badge-abc-{str(r['curva_abc']).lower()}'>Curva {r['curva_abc']}</span>"
                
                # Etiqueta Tendência
                if r['tendencia_pct'] > 0: tend_html = f"<span style='color:#16a34a; font-weight:bold; font-size:0.8rem;'>📈 +{r['tendencia_pct']:.0f}% vs ant.</span>"
                elif r['tendencia_pct'] < 0: tend_html = f"<span style='color:#dc2626; font-weight:bold; font-size:0.8rem;'>📉 {r['tendencia_pct']:.0f}% vs ant.</span>"
                else: tend_html = f"<span style='color:#6b7280; font-weight:bold; font-size:0.8rem;'>➖ Estável</span>"

                # Status de Saúde e Barra de Progresso Visual
                if r['dias_restantes'] <= lead_time_dias:
                    badge_status = f"<span style='background:#fee2e2; color:#991b1b; padding:3px 8px; border-radius:4px; font-weight:bold; font-size:0.8rem;'>🚨 Crítico ({r['dias_restantes']} dias)</span>"
                    cor_barra = "#dc2626"
                    pct_barra = max(0, min(100, (r['dias_restantes'] / lead_time_dias) * 100))
                elif r['dias_restantes'] <= 20:
                    badge_status = f"<span style='background:#fef3c7; color:#92400e; padding:3px 8px; border-radius:4px; font-weight:bold; font-size:0.8rem;'>⚠️ Atenção ({r['dias_restantes']} dias)</span>"
                    cor_barra = "#eab308"
                    pct_barra = 100
                else:
                    dias_txt = "+30 dias" if r['dias_restantes'] >= 999 else f"{r['dias_restantes']} dias"
                    badge_status = f"<span style='background:#dcfce7; color:#166534; padding:3px 8px; border-radius:4px; font-weight:bold; font-size:0.8rem;'>✓ Saudável ({dias_txt})</span>"
                    cor_barra = "#16a34a"
                    pct_barra = 100

                st.markdown(f"""
                    <div class="mobile-card">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:6px;">
                            <h4 style="margin:0; font-size:1rem;">{r['nome']} {badge_abc}</h4>
                            {badge_status}
                        </div>
                        <div style="width:100%; background-color:#e5e7eb; border-radius:4px; height:6px; margin-bottom:10px;">
                            <div style="width:{pct_barra}%; background-color:{cor_barra}; height:6px; border-radius:4px;"></div>
                        </div>
                        <div style="display:flex; justify-content:space-between; font-size:0.85rem; color:#1f2937;">
                            <div>
                                <p style="margin:2px 0;"><strong>Estoque Atual:</strong> {r['estoque_atual']} un.</p>
                                <p style="margin:2px 0;"><strong>Consumo:</strong> {r['cmd']:.1f} un./dia {tend_html}</p>
                            </div>
                            <div style="text-align:right;">
                                <p style="margin:2px 0;"><strong>Vendas ({dias_analise}d):</strong> {int(r['total_atual'])} un.</p>
                                <p style="margin:2px 0;"><strong>Ponto Reposição:</strong> <span style="font-weight:900; color:#000;">{r['ponto_reposicao']} un.</span></p>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Dados insuficientes para calcular o modelo preditivo.")

    # ------------------ ABA PEDIDOS ------------------
    elif menu_principal == "🛒 Pedidos":
        st.markdown("<h4 style='font-weight:900; margin-bottom:12px;'>Gestão de Pedidos</h4>", unsafe_allow_html=True)
        acao_ped = st.selectbox("Operação:", ["📋 Listagem Geral", "🔍 Detalhe do Pedido", "🔄 Atualizar Status", "📥 Exportar CSV"])
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
                st.info("Nenhum pedido registrado no banco de dados.")

        elif acao_ped == "🔍 Detalhe do Pedido":
            lista = buscar_dados("SELECT p.id, c.nome, p.total FROM pedidos p JOIN clientes c ON p.cliente_id = c.id ORDER BY p.id DESC")
            if not lista.empty:
                ped_id = st.selectbox("Recibo:", list({f"Nº {r['id']} - {r['nome']}": r['id'] for _, r in lista.iterrows()}.values()), format_func=lambda x: f"Pedido #{x}")
                info = buscar_dados("SELECT p.id, p.total, p.status, p.data_pedido, c.nome, c.email, c.telefone FROM pedidos p JOIN clientes c ON p.cliente_id = c.id WHERE p.id = %s", (ped_id,))
                if not info.empty:
                    p = info.iloc[0]
                    st.markdown(f"""
                        <div class="card-detalhe">
                            <h4 style="margin:0 0 8px 0; font-weight:900;">🧾 Pedido #{p['id']}</h4>
                            <p style="margin:2px 0;"><strong>Status:</strong> {str(p['status']).upper()}</p>
                            <p style="margin:2px 0;"><strong>Cliente:</strong> {p['nome']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    itens = buscar_dados("SELECT pr.nome as item, ip.quantidade as qtd, ip.preco_unitario as unitario, (ip.quantidade * ip.preco_unitario) as subtotal FROM itens_pedido ip JOIN produtos pr ON ip.produto_id = pr.id WHERE ip.pedido_id = %s", (ped_id,))
                    if not itens.empty: st.dataframe(itens, use_container_width=True, hide_index=True)

        elif acao_ped == "🔄 Atualizar Status":
            pendentes = buscar_dados("SELECT id, status FROM pedidos ORDER BY id DESC")
            if not pendentes.empty:
                opcoes = {f"#{r['id']} (Atual: {r['status']})": r['id'] for _, r in pendentes.iterrows()}
                ped_id = opcoes[st.selectbox("Pedido:", list(opcoes.keys()))]
                novo_status = st.selectbox("Novo Status:", ["Pendente", "Em processamento", "Enviado", "Entregue", "Concluído", "Cancelado"])
                if st.button("Atualizar", type="primary", use_container_width=True):
                    if executar_comando("UPDATE pedidos SET status = %s WHERE id = %s", (novo_status, ped_id)):
                        st.success("Status atualizado!"); st.rerun()

        elif acao_ped == "📥 Exportar CSV":
            df_export = buscar_dados("SELECT p.id, c.nome as cliente, c.email, p.total, p.status, p.data_pedido FROM pedidos p LEFT JOIN clientes c ON p.cliente_id = c.id ORDER BY p.id DESC")
            if not df_export.empty:
                st.download_button("📄 Baixar Relatório CSV", data=df_export.to_csv(index=False).encode('utf-8'), file_name="relatorio_pedidos.csv", mime="text/csv", use_container_width=True)

    # ------------------ ABA CLIENTES ------------------
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
                            <p style="margin:2px 0;"><strong>E-mail:</strong> {r['email']} | <strong>Status:</strong> {r['status']}</p>
                        </div>
                    """, unsafe_allow_html=True)

        elif acao_cli == "✅ Aprovações Pendentes":
            pendentes = buscar_dados("SELECT id, nome, email FROM usuarios WHERE status = 'Pendente' AND role = 'cliente'")
            if not pendentes.empty:
                opcoes = {f"#{r['id']} - {r['nome']} ({r['email']})": r['id'] for _, r in pendentes.iterrows()}
                user_id = opcoes[st.selectbox("Conta:", list(opcoes.keys()))]
                if st.button("Aprovar Conta", type="primary", use_container_width=True):
                    reg = pendentes[pendentes['id'] == user_id].iloc[0]
                    if executar_comando("UPDATE usuarios SET status = 'Aprovado' WHERE id = %s", (user_id,)):
                        enviar_telegram_aviso(f"✅ *Conta Aprovada pelo Admin!*\n\n👤 *Cliente:* {reg['nome']}\n📧 *E-mail:* {reg['email']}\n🔓 Acesso autorizado.")
                        st.success("Conta liberada com sucesso!"); st.rerun()
            else:
                st.success("Sem contas pendentes de aprovação.")
