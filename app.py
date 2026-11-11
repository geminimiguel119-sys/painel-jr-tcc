import os
import streamlit as st
import psycopg2
import pandas as pd
import base64
from datetime import datetime

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA E TEMA
# ==========================================
st.set_page_config(page_title="Painel ERP - JR Iluminação", page_icon="💡", layout="wide", initial_sidebar_state="expanded")

def forcar_tema_claro():
    if not os.path.exists(".streamlit"):
        os.makedirs(".streamlit")
    config_path = ".streamlit/config.toml"
    config_content = """[theme]
base="light"
primaryColor="#004aad"
backgroundColor="#f4f7fb"
secondaryBackgroundColor="#ffffff"
textColor="#0f172a"
"""
    try:
        with open(config_path, "r") as f:
            if f.read().strip() == config_content.strip(): return
    except: pass
    with open(config_path, "w") as f:
        f.write(config_content)

forcar_tema_claro()

# ==========================================
# 2. BLINDAGEM CSS E DESIGN PREMIUM
# ==========================================
st.markdown("""
    <script>document.documentElement.lang = 'pt-BR';</script>
    <style>
    /* Fundo Geral */
    .stApp { background-color: #f8fafc !important; }
    
    /* Fontes e Textos */
    .stSelectbox label p, .stTextInput label p, .stNumberInput label p, .stFileUploader label p, .stTabs [data-baseweb="tab"] p {
        color: #004aad !important; font-weight: 700 !important;
    }
    div[data-baseweb="select"] span { color: #0f172a !important; font-weight: 600 !important; }
    ul[role="listbox"] li { color: #0f172a !important; background-color: #ffffff !important; }
    input[type="text"], input[type="number"], input[type="password"] { color: #0f172a !important; background-color: #ffffff !important; border-radius: 8px !important; }
    
    /* Prevenir teclado no mobile para dropdowns */
    div[data-baseweb="select"] input { pointer-events: none !important; caret-color: transparent !important; }

    /* Botões Premium */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #004aad, #0284c7) !important;
        color: white !important; border: none; font-weight: bold; border-radius: 8px;
        transition: all 0.3s ease; padding: 10px 0; box-shadow: 0 4px 6px rgba(0, 74, 173, 0.2);
    }
    .stButton>button[kind="primary"]:hover {
        transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0, 74, 173, 0.3);
    }
    
    /* Cartões Modernos com Efeito Hover */
    .card-pro, .card-cliente, .metric-box, .card-preditivo {
        background-color: #ffffff; padding: 20px; border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02); margin-bottom: 15px;
        border: 1px solid #e2e8f0; transition: all 0.3s ease;
    }
    .card-pro:hover, .card-cliente:hover, .metric-box:hover, .card-preditivo:hover {
        box-shadow: 0 10px 20px rgba(0,0,0,0.08); transform: translateY(-3px); border-color: #cbd5e1;
    }
    
    /* Layout Interno dos Cartões */
    .card-pro { border-left: 5px solid #004aad; display: flex; flex-wrap: wrap; gap: 15px; justify-content: space-between; align-items: center; }
    .card-cliente { border-left: 5px solid #0284c7; display: flex; align-items: center; gap: 20px; }
    .metric-box { border-top: 4px solid #004aad; text-align: center; }
    
    /* Badges e Textos */
    .badge-status { padding: 6px 14px; border-radius: 20px; font-size: 11px; font-weight: bold; text-transform: uppercase; white-space: nowrap; color: #ffffff !important; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .metric-title { color: #64748b !important; font-size: 13px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.5px; }
    .metric-value { color: #0f172a !important; font-size: 32px; font-weight: 900; margin: 0; }

    /* Ocultar elementos nativos desnecessários */
   #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. CONEXÃO SUPABASE E FUNÇÕES AUXILIARES
# ==========================================
DB_URL = "postgresql://postgres.bfppcxnxqagpesuyjlhe:An1bal_19691910%40@aws-0-us-west-2.pooler.supabase.com:5432/postgres"

def conectar():
    return psycopg2.connect(DB_URL)

def buscar_dados(query, params=None):
    conn = None
    try:
        conn = conectar()
        return pd.read_sql_query(query, conn, params=params)
    except Exception as e:
        st.error(f"Erro no banco: {e}")
        return pd.DataFrame()
    finally:
        if conn: conn.close()

def executar_comando(query, params=None):
    conn = None; cur = None
    try:
        conn = conectar(); cur = conn.cursor()
        cur.execute(query, params); conn.commit()
        return True
    except Exception as e:
        st.error(f"Erro: {e}")
        if conn: conn.rollback()
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

def cor_do_status(status):
    cores = {'Entregue': '#16a34a', 'Cancelado': '#dc2626', 'Pendente': '#d97706', 'Aprovado': '#059669', 'Recusado': '#ef4444'}
    return f"background-color: {cores.get(status, '#004aad')};"

def converter_imagem_base64(uploaded_file):
    if uploaded_file:
        b64 = base64.b64encode(uploaded_file.read()).decode()
        return f"data:{uploaded_file.type};base64,{b64}"
    return ""

# ==========================================
# 4. TELA DE LOGIN (DESIGN CENTRALIZADO)
# ==========================================
if "logado" not in st.session_state: st.session_state.logado = False

if not st.session_state.logado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<div style='text-align: center; background: white; padding: 40px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
        st.markdown("<h1 style='color: #004aad !important; margin-bottom: 5px; font-weight: 900;'>💡 JR Iluminação</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748b; font-size: 15px; margin-bottom: 30px;'>Acesso Restrito ao Painel Administrativo</p>", unsafe_allow_html=True)
        
        senha = st.text_input("🔑 Senha de Acesso", type="password", placeholder="Digite a senha admin")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Entrar no Sistema", type="primary", use_container_width=True):
            if senha == "admin123":
                st.session_state.logado = True
                st.rerun()
            else:
                st.error("❌ Credencial incorreta. Tente novamente.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==========================================
# 5. SIDEBAR (MENU LATERAL PROFISSIONAL)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color: #004aad !important; font-weight: 900; text-align: center; margin-bottom: 30px;'>💡 Painel ERP</h2>", unsafe_allow_html=True)
    menu = st.radio(
        "Navegação",
        ["📊 Dashboard (Resumo)", "📦 Estoque & Catálogo", "👥 Clientes & Acessos", "🛍️ Gestão de Pedidos", "🧠 BI Preditivo"],
        label_visibility="hidden"
    )
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    if st.button("🚪 Sair do Sistema", use_container_width=True):
        st.session_state.logado = False
        st.rerun()

# ==========================================
# 6. MÓDULOS DO SISTEMA
# ==========================================

# --- MÓDULO 1: DASHBOARD ---
if "Dashboard" in menu:
    st.markdown("<h3 style='color: #0f172a !important; font-weight: 800;'>📊 Visão Geral do Negócio</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b;'>Resumo financeiro e operacional em tempo real.</p>", unsafe_allow_html=True)
    
    df_pedidos = buscar_dados("SELECT total FROM pedidos WHERE status != 'Cancelado'")
    df_cli = buscar_dados("SELECT count(*) as total FROM clientes")
    
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='metric-box'><div class='metric-title'>💰 Faturamento Bruto</div><div class='metric-value'>R$ {df_pedidos['total'].sum() if not df_pedidos.empty else 0:,.2f}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-box'><div class='metric-title'>🛍️ Vendas Concluídas</div><div class='metric-value'>{len(df_pedidos)}</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-box'><div class='metric-title'>👥 Base de Clientes</div><div class='metric-value'>{int(df_cli['total'].iloc[0]) if not df_cli.empty else 0}</div></div>", unsafe_allow_html=True)
    
    st.markdown("<br><h4 style='color: #0f172a !important;'>Últimos Pedidos Processados</h4>", unsafe_allow_html=True)
    ultimos = buscar_dados("SELECT id, total, status, data_pedido FROM pedidos ORDER BY data_pedido DESC LIMIT 5")
    
    if not ultimos.empty:
        for _, p in ultimos.iterrows():
            data = pd.to_datetime(p['data_pedido']).strftime("%d/%m/%Y às %H:%M")
            st.markdown(f"""
            <div class="card-pro">
                <div><h4 style="margin: 0; color: #1e293b !important; font-weight: 800;">Pedido #{p['id']}</h4>
                     <span style="color: #64748b !important; font-size: 13px;">📅 {data}</span></div>
                <div><h4 style="margin: 0; color: #004aad !important; font-weight: 900;">R$ {p['total']:.2f}</h4></div>
                <div><span class="badge-status" style="{cor_do_status(p['status'])}">{p['status']}</span></div>
            </div>""", unsafe_allow_html=True)
    else: st.info("Nenhum pedido registrado ainda.")

# --- MÓDULO 2: ESTOQUE ---
elif "Estoque" in menu:
    st.markdown("<h3 style='color: #0f172a !important; font-weight: 800;'>📦 Gestão de Estoque e Catálogo</h3>", unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["📋 Ver Catálogo", "➕ Novo Produto", "✏️ Atualizar", "🗑️ Remover"])
    
    with t1:
        df = buscar_dados("SELECT * FROM produtos ORDER BY id DESC")
        if not df.empty:
            for _, r in df.iterrows():
                st.markdown(f"""
                <div class="card-pro" style="justify-content: flex-start; gap: 25px;">
                    <div style="width: 80px; height: 80px; background-color: #f1f5f9; border-radius: 10px; overflow: hidden; display: flex; align-items: center; justify-content: center; border: 1px solid #e2e8f0;">
                        {f'<img src="{r.get("imagem", "")}" style="width:100%; height:100%; object-fit:cover;">' if r.get('imagem') and r.get('imagem') not in ['None', 'placeholder.jpg'] else '📷'}
                    </div>
                    <div>
                        <h4 style="margin:0; color:#004aad !important; font-weight: 800;">{r['nome']} <span style="font-size: 12px; color: #94a3b8;">(#{r['id']})</span></h4>
                        <p style="margin:2px 0; color:#64748b !important; font-size: 13px;">Categoria: <b>{r.get('categoria', 'N/A')}</b></p>
                        <div style="color:#0f172a !important; font-weight: bold; font-size: 16px; margin-top: 5px;">
                            💵 R$ {float(r['preco']):.2f} &nbsp;&nbsp;|&nbsp;&nbsp; 📦 Estoque: {int(r['quantidade'])} un.
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)
        else: st.info("Seu catálogo está vazio.")
            
    with t2:
        with st.container(border=True):
            n = st.text_input("Nome do Produto")
            c = st.selectbox("Categoria", ["Lâmpadas", "Fitas LED", "Plafons", "Spots", "Outros"])
            c1, c2 = st.columns(2)
            p = c1.number_input("Preço (R$)", min_value=0.1, format="%.2f")
            q = c2.number_input("Quantidade Inicial", min_value=0, step=1)
            img = st.file_uploader("Foto do Produto", type=["png", "jpg", "jpeg"])
            if st.button("💾 Cadastrar Produto Novo", type="primary", use_container_width=True):
                if n and executar_comando("INSERT INTO produtos (nome, categoria, preco, quantidade, imagem) VALUES (%s, %s, %s, %s, %s)", (n, c, p, q, converter_imagem_base64(img))):
                    st.toast("✅ Produto cadastrado com sucesso!", icon="🎉")
                    st.rerun()

    with t3:
        df = buscar_dados("SELECT * FROM produtos ORDER BY nome ASC")
        if not df.empty:
            opcs = {f"#{r['id']} - {r['nome']}": r['id'] for _, r in df.iterrows()}
            pid = opcs[st.selectbox("Selecione o Produto para Edição", list(opcs.keys()))]
            prod = df[df['id'] == pid].iloc[0]
            
            with st.container(border=True):
                en = st.text_input("Nome", value=str(prod['nome']))
                ec = st.selectbox("Categoria", ["Lâmpadas", "Fitas LED", "Plafons", "Spots", "Outros"], index=0)
                c1, c2 = st.columns(2)
                ep = c1.number_input("Preço (R$)", value=float(prod['preco']), format="%.2f")
                eq = c2.number_input("Estoque Atual", value=int(prod['quantidade']), step=1)
                eimg = st.file_uploader("Trocar Imagem (Opcional)", type=["png", "jpg", "jpeg"])
                
                if st.button("🔄 Salvar Alterações", type="primary", use_container_width=True):
                    img_final = converter_imagem_base64(eimg) if eimg else str(prod.get('imagem', ''))
                    if executar_comando("UPDATE produtos SET nome=%s, categoria=%s, preco=%s, quantidade=%s, imagem=%s WHERE id=%s", (en, ec, ep, eq, img_final, pid)):
                        st.toast("✅ Produto atualizado perfeitamente!", icon="🔄")
                        st.rerun()

    with t4:
        df = buscar_dados("SELECT id, nome FROM produtos ORDER BY id DESC")
        if not df.empty:
            opcs = {f"#{r['id']} - {r['nome']}": r['id'] for _, r in df.iterrows()}
            del_id = opcs[st.selectbox("Escolha o Produto para Excluir", list(opcs.keys()))]
            st.error("⚠️ Atenção: Esta ação não pode ser desfeita.")
            if st.button("🗑️ Excluir Produto Definitivamente", type="primary", use_container_width=True):
                if executar_comando("DELETE FROM produtos WHERE id=%s", (del_id,)):
                    st.toast("🗑️ Produto excluído da base.", icon="✅")
                    st.rerun()

# --- MÓDULO 3: CLIENTES ---
elif "Clientes" in menu:
    st.markdown("<h3 style='color: #0f172a !important; font-weight: 800;'>👥 Gestão de Clientes e Acessos</h3>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("<h5 style='margin-bottom: 5px;'>🔐 Aprovar Cadastro Manual</h5><p style='font-size: 13px; color: #64748b;'>Liberar clientes que estão aguardando aprovação pelo site.</p>", unsafe_allow_html=True)
        df_pend = buscar_dados("SELECT * FROM usuarios WHERE status = 'Pendente' AND role = 'cliente'")
        
        if not df_pend.empty:
            opc = {f"#{r['id']} - {r['nome']} ({r['email']})": r['id'] for _, r in df_pend.iterrows()}
            cid = opc[st.selectbox("Clientes Pendentes:", list(opc.keys()))]
            if st.button("✅ Aprovar e Liberar Acesso ao Site", type="primary", use_container_width=True):
                if executar_comando("UPDATE usuarios SET status = 'Aprovado' WHERE id = %s", (cid,)):
                    st.toast("✅ Cliente liberado para compras!", icon="🎉")
                    st.rerun()
        else: st.success("Nenhum cliente aguardando aprovação no momento.")
    
    st.markdown("<br><h4 style='color: #0f172a !important;'>🏢 Base Completa de Clientes</h4>", unsafe_allow_html=True)
    df_cli = buscar_dados("SELECT * FROM clientes ORDER BY id DESC")
    if not df_cli.empty:
        for _, c in df_cli.iterrows():
            st.markdown(f"""
            <div class="card-cliente">
                <div style="font-size: 32px; background: #e6f0fa; padding: 12px; border-radius: 50%; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">👤</div>
                <div>
                    <h4 style="margin: 0; color: #004aad !important; font-weight: 800;">{c['nome']}</h4>
                    <span style="color: #64748b !important; font-size: 14px; font-weight: 600;">📧 {c['email']}</span>
                </div>
            </div>""", unsafe_allow_html=True)
    else: st.info("Nenhum cliente cadastrado.")

# --- MÓDULO 4: PEDIDOS ---
elif "Pedidos" in menu:
    st.markdown("<h3 style='color: #0f172a !important; font-weight: 800;'>🛍️ Gestão de Encomendas</h3>", unsafe_allow_html=True)
    df_ped = buscar_dados("SELECT p.id, c.nome as cliente, p.total, p.status, p.data_pedido FROM pedidos p JOIN clientes c ON p.cliente_id = c.id ORDER BY p.data_pedido DESC")
    
    if not df_ped.empty:
        with st.container(border=True):
            st.markdown("<h5>🔄 Atualizar Status do Pedido</h5>", unsafe_allow_html=True)
            opc = {f"Pedido #{r['id']} - {r['cliente']}": r['id'] for _, r in df_ped.iterrows()}
            pid = opc[st.selectbox("Localizar Encomenda:", list(opc.keys()))]
            nst = st.selectbox("Mover para:", ["Pendente", "Em processamento", "Enviado", "Entregue", "Cancelado"])
            
            if st.button("Gravar Novo Status", type="primary", use_container_width=True):
                if nst == "Cancelado":
                    itens = buscar_dados("SELECT produto_id, quantidade FROM itens_pedido WHERE pedido_id = %s", (pid,))
                    for _, it in itens.iterrows(): executar_comando("UPDATE produtos SET quantidade = quantidade + %s WHERE id = %s", (int(it['quantidade']), int(it['produto_id'])))
                if executar_comando("UPDATE pedidos SET status = %s WHERE id = %s", (nst, pid)):
                    st.toast("✅ Linha do tempo atualizada com sucesso!", icon="🚚")
                    st.rerun()
                    
        st.markdown("<br><h4 style='color: #0f172a !important;'>Histórico de Operações</h4>", unsafe_allow_html=True)
        for _, p in df_ped.iterrows():
            st.markdown(f"""
            <div class="card-pro">
                <div style="flex: 1 1 100%;">
                    <h4 style="margin: 0; color: #004aad !important; font-weight: 800;">Pedido #{p['id']}</h4>
                    <span style="color: #64748b !important; font-size: 14px;">👤 {p['cliente']} &nbsp;|&nbsp; 📅 {pd.to_datetime(p['data_pedido']).strftime("%d/%m/%Y %H:%M")}</span>
                </div>
                <div style="display: flex; width: 100%; justify-content: space-between; align-items: center; margin-top: 5px;">
                    <h3 style="margin: 0; color: #0f172a !important; font-weight: 900;">R$ {float(p['total']):.2f}</h3>
                    <span class="badge-status" style="{cor_do_status(p['status'])}">{p['status']}</span>
                </div>
            </div>""", unsafe_allow_html=True)
    else: st.info("Sem pedidos no momento.")

# --- MÓDULO 5: BI PREDITIVO ---
elif "Preditivo" in menu:
    st.markdown("<h3 style='color: #0f172a !important; font-weight: 800;'>🧠 Inteligência de Estoque (BI)</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b !important; font-size: 15px;'>Análise algorítmica de risco de ruptura baseada nas saídas (últimos 30 dias).</p>", unsafe_allow_html=True)
    
    query = """
        SELECT p.id, p.nome, COALESCE(p.quantidade, 0) as estoque,
               COALESCE(SUM(CASE WHEN ped.status != 'Cancelado' AND ped.data_pedido >= NOW() - INTERVAL '30 days' THEN ip.quantidade ELSE 0 END), 0) as vendido
        FROM produtos p LEFT JOIN itens_pedido ip ON ip.produto_id = p.id LEFT JOIN pedidos ped ON ped.id = ip.pedido_id 
        GROUP BY p.id, p.nome, p.quantidade ORDER BY estoque ASC
    """
    df = buscar_dados(query)
    
    if not df.empty:
        ordens, status_list, cor_borda, cor_fundo, cor_texto, msg = [], [], [], [], [], []
        for _, r in df.iterrows():
            est, ven = int(r['estoque']), int(r['vendido'])
            if est == 0:
                s, cb, cf, ct, m, o = "ESGOTADO", "#dc2626", "#fef2f2", "#991b1b", "🚨 Ruptura total. Reposição imediata exigida.", 1
            elif est <= ven and ven > 0:
                s, cb, cf, ct, m, o = "ALTO RISCO", "#ea580c", "#fff7ed", "#9a3412", f"⚠️ Saída supera o estoque (Vendido: {ven}/mês).", 2
            elif est <= 5:
                s, cb, cf, ct, m, o = "ATENÇÃO", "#eab308", "#fefce8", "#854d0e", "⚠️ Estoque mínimo atingido. Planeje compra.", 3
            else:
                s, cb, cf, ct, m, o = "SAUDÁVEL", "#004aad", "#e6f0fa", "#003377", "✅ Nível de armazenamento seguro e estabilizado.", 4
            ordens.append(o); status_list.append(s); cor_borda.append(cb); cor_fundo.append(cf); cor_texto.append(ct); msg.append(m)
            
        df['ordem'] = ordens; df['status'] = status_list; df['cor_borda'] = cor_borda; df['cor_fundo'] = cor_fundo; df['cor_texto'] = cor_texto; df['msg'] = msg
        df = df.sort_values(by=['ordem', 'estoque'])
        
        for _, r in df.iterrows():
            st.markdown(f"""
            <div class="card-preditivo" style="background-color: {r['cor_fundo']}; border-left: 6px solid {r['cor_borda']}; border-color: {r['cor_borda']}40;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <h4 style="margin: 0; color: #0f172a !important; font-weight: 800;">{r['nome']}</h4>
                    <span style="background: {r['cor_borda']}; color: white; padding: 5px 12px; border-radius: 6px; font-size: 11px; font-weight: 900; letter-spacing: 0.5px; box-shadow: 0 2px 4px {r['cor_borda']}40;">{r['status']}</span>
                </div>
                <div style="display: flex; gap: 15px; margin-bottom: 15px;">
                    <div style="background: white; padding: 6px 12px; border-radius: 6px; border: 1px solid #e2e8f0; font-size: 14px; font-weight: 600; color: #334155;">📦 Em Estoque: <span style="color: #0f172a; font-size: 16px;">{r['estoque']}</span></div>
                    <div style="background: white; padding: 6px 12px; border-radius: 6px; border: 1px solid #e2e8f0; font-size: 14px; font-weight: 600; color: #334155;">📈 Saída (30d): <span style="color: #0f172a; font-size: 16px;">{r['vendido']}</span></div>
                </div>
                <div style="color: {r['cor_texto']} !important; font-size: 14px; font-weight: 700; background: white; padding: 10px; border-radius: 6px; border-left: 3px solid {r['cor_borda']};">
                    {r['msg']}
                </div>
            </div>""", unsafe_allow_html=True)
    else: st.info("Sem dados comerciais suficientes para análise.")
