import streamlit as st
import psycopg2
import pandas as pd
import base64
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA (TEMA CORPORATIVO) ---
st.set_page_config(page_title="Admin - JR Iluminação", page_icon="💡", layout="centered")

# --- FORÇAR LINGUAGEM PT-BR E CORREÇÃO DE TEXTOS INVISÍVEIS ---
st.markdown("""
    <script>document.documentElement.lang = 'pt-BR';</script>
    <style>
    /* ==========================================
       CORREÇÃO DO BUG DE TEXTO INVISÍVEL (MODO ESCURO)
       Garante que nenhum texto fique branco no fundo claro
       ========================================== */
    .stApp {
        background-color: #f4f7fb !important;
    }
    
    /* Força as labels (nomes em cima dos campos) a ficarem escuras */
    label, .stLabel, [data-testid="stMarkdownContainer"] p {
        color: #0f172a !important;
        font-weight: 600 !important;
    }

    /* Força o texto dentro dos dropdowns (menus) e abas a aparecerem */
    div[data-baseweb="select"] *, button[data-baseweb="tab"] * {
        color: #004aad !important;
    }

    /* Força a cor dos inputs de texto numéricos e campos de arquivo */
    input, textarea, .stFileUploader * {
        color: #1e293b !important;
    }
    
    /* ==========================================
       ESTILOS CORPORATIVOS DO PAINEL
       ========================================== */
    /* Botões Primários */
    .stButton>button[kind="primary"] {
        background-color: #004aad !important;
        color: white !important;
        border: none;
        font-weight: 600;
        border-radius: 6px;
        transition: all 0.3s ease;
    }
    .stButton>button[kind="primary"]:hover {
        background-color: #003377 !important;
        box-shadow: 0 4px 8px rgba(0,74,173,0.3);
    }

    /* Cards Profissionais */
    .card-pro {
        background-color: #ffffff; 
        padding: 18px; 
        border-radius: 8px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.04); 
        margin-bottom: 15px;
        border: 1px solid #e1e8f0; 
        border-left: 5px solid #004aad;
        display: flex; 
        flex-wrap: wrap; 
        gap: 10px; 
        justify-content: space-between; 
        align-items: center;
    }
    
    .card-cliente {
        background-color: #ffffff; 
        padding: 15px; 
        border-radius: 8px;
        border: 1px solid #e1e8f0; 
        border-left: 5px solid #0284c7;
        margin-bottom: 12px; 
        display: flex; 
        align-items: center; 
        gap: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }

    /* Badges de Status - Protegendo a cor branca aqui */
    .badge-status {
        padding: 6px 14px; 
        border-radius: 20px; 
        font-size: 11px; 
        font-weight: bold; 
        text-transform: uppercase; 
        white-space: nowrap;
        letter-spacing: 0.5px;
        color: #ffffff !important;
    }

    /* Métricas do Dashboard */
    .metric-box {
        background-color: #ffffff;
        border: 1px solid #e1e8f0;
        border-top: 4px solid #004aad;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.03);
    }
    
    .metric-title { color: #64748b !important; font-size: 14px; font-weight: 600; text-transform: uppercase; margin-bottom: 5px; }
    .metric-value { color: #0f172a !important; font-size: 26px; font-weight: 800; margin: 0; }

    /* Esconder menus padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- CONEXÃO COM O BANCO DE DADOS (SUPABASE) ---
DB_URL = "postgresql://postgres.bfppcxnxqagpesuyjlhe:An1bal_19691910%40@aws-0-us-west-2.pooler.supabase.com:5432/postgres"

def conectar():
    return psycopg2.connect(DB_URL)

def buscar_dados(query, params=None):
    conn = None
    try:
        conn = conectar()
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")
        return pd.DataFrame()
    finally:
        if conn is not None:
            conn.close()

def executar_comando(query, params=None):
    conn = None
    cur = None
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Erro na execução: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

def cor_do_status(status):
    if status == 'Entregue': return "background-color: #16a34a;"
    if status == 'Cancelado': return "background-color: #dc2626;"
    if status == 'Pendente': return "background-color: #d97706;"
    return "background-color: #004aad;"

def converter_imagem_base64(uploaded_file):
    if uploaded_file is not None:
        b64_str = base64.b64encode(uploaded_file.read()).decode()
        tipo = uploaded_file.type
        return f"data:{tipo};base64,{b64_str}"
    return ""

# --- AUTENTICAÇÃO E SESSÃO ---
if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.markdown("<div style='text-align: center; margin-bottom: 20px;'><h1 style='color: #004aad !important;'>💡 JR Iluminação</h1><h3 style='color: #333 !important;'>Painel Corporativo</h3></div>", unsafe_allow_html=True)
    senha = st.text_input("Credencial de Acesso (Administrador)", type="password")
    if st.button("Autenticar Sistema", type="primary", use_container_width=True):
        if senha == "admin123": 
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Acesso negado: Credencial incorreta.")
    st.stop()

# ==========================================
# HEADER E NAVEGAÇÃO TOPO
# ==========================================
col_logo, col_logout = st.columns([3, 1], vertical_alignment="center")
with col_logo:
    st.markdown("<h2 style='margin:0; color: #004aad !important; font-weight: 700;'>💡 Painel JR</h2>", unsafe_allow_html=True)
with col_logout:
    if st.button("Sair", use_container_width=True):
        st.session_state.logado = False
        st.rerun()

st.write("") # Espaçamento
menu = st.selectbox("📍 Navegação do Sistema", ["Resumo", "Produtos", "Clientes", "Pedidos", "Preditivo"])
st.divider()

# ==========================================
# 1. RESUMO (DASHBOARD FINANCEIRO)
# ==========================================
if menu == "Resumo":
    st.markdown("<h4 style='color: #004aad !important;'>📊 Visão Geral do Negócio</h4>", unsafe_allow_html=True)
    
    df_pedidos = buscar_dados("SELECT total, status FROM pedidos WHERE status != 'Cancelado'")
    receita_total = df_pedidos['total'].sum() if not df_pedidos.empty else 0.0
    qtd_pedidos = len(df_pedidos)
    
    df_clientes = buscar_dados("SELECT count(*) as total FROM clientes")
    total_clientes = int(df_clientes['total'].iloc[0]) if not df_clientes.empty else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='metric-box'><div class='metric-title'>Faturamento</div><div class='metric-value'>R$ {receita_total:,.2f}</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-box'><div class='metric-title'>Vendas</div><div class='metric-value'>{qtd_pedidos}</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-box'><div class='metric-title'>Clientes</div><div class='metric-value'>{total_clientes}</div></div>", unsafe_allow_html=True)
    
    st.divider()
    st.markdown("<h5 style='color: #333 !important;'>Últimos Pedidos Processados</h5>", unsafe_allow_html=True)
    ultimos = buscar_dados("SELECT id, total, status, data_pedido FROM pedidos ORDER BY data_pedido DESC LIMIT 5")
    
    if not ultimos.empty:
        for _, p in ultimos.iterrows():
            data_formatada = pd.to_datetime(p['data_pedido']).strftime("%d/%m/%Y")
            estilo_status = cor_do_status(p['status'])
            
            st.markdown(f"""
            <div class="card-pro">
                <div>
                    <h5 style="margin: 0; color: #1e293b !important; font-weight: 700;">#{p['id']}</h5>
                    <span style="color: #64748b !important; font-size: 13px;">📅 {data_formatada}</span>
                </div>
                <div>
                    <h5 style="margin: 0; color: #004aad !important; font-weight: 800;">R$ {p['total']:.2f}</h5>
                </div>
                <div>
                    <span class="badge-status" style="{estilo_status}">{p['status']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nenhum pedido processado.")

# ==========================================
# 2. PRODUTOS (ESTOQUE)
# ==========================================
elif menu == "Produtos":
    st.markdown("<h4 style='color: #004aad !important;'>📦 Gestão de Estoque</h4>", unsafe_allow_html=True)
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Catálogo", "➕ Adicionar", "✏️ Editar", "🗑️ Excluir"])
    
    with tab1:
        df = buscar_dados("SELECT * FROM produtos ORDER BY id DESC")
        if not df.empty:
            for _, r in df.iterrows():
                with st.container(border=True):
                    col_img, col_txt = st.columns([1, 3], vertical_alignment="center")
                    with col_img:
                        img = str(r.get('imagem', '')).strip()
                        if img and img != 'None' and img != 'placeholder.jpg':
                            st.markdown(f'<img src="{img}" style="width:100%; border-radius:8px; object-fit: cover; border: 1px solid #e1e8f0;">', unsafe_allow_html=True)
                        else:
                            st.markdown("<div style='text-align:center; padding: 20px; background: #f1f5f9; border-radius: 8px; color: #94a3b8;'>Sem foto</div>", unsafe_allow_html=True)
                    with col_txt:
                        st.markdown(f"<h4 style='margin:0; color:#004aad !important; font-size: 17px; font-weight: 700;'>{r['nome']}</h4>", unsafe_allow_html=True)
                        st.markdown(f"<p style='margin:2px 0; color:#64748b !important; font-size: 13px;'>Categoria: <b>{r.get('categoria', 'N/A')}</b></p>", unsafe_allow_html=True)
                        st.markdown(f"<div style='color:#0f172a !important; font-weight: bold; font-size: 15px; margin-top: 5px;'>Valor: R$ {float(r['preco']):.2f} &nbsp;|&nbsp; 📦 Estoque: {int(r['quantidade'])} un.</div>", unsafe_allow_html=True)
        else: 
            st.info("Catálogo vazio.")
            
    with tab2:
        nome = st.text_input("Nome do Produto")
        cat = st.selectbox("Categoria", ["Lâmpadas", "Fitas LED", "Plafons", "Spots", "Outros"])
        col_p, col_q = st.columns(2)
        preco = col_p.number_input("Preço de Venda (R$)", min_value=0.1, format="%.2f")
        qtd = col_q.number_input("Quantidade em Estoque", min_value=0, step=1)
        
        imagem_upload = st.file_uploader("Fazer Upload da Imagem", type=["png", "jpg", "jpeg"])
        
        if st.button("Cadastrar Produto", type="primary", use_container_width=True):
            if nome:
                img_final = converter_imagem_base64(imagem_upload)
                if executar_comando("INSERT INTO produtos (nome, categoria, preco, quantidade, imagem) VALUES (%s, %s, %s, %s, %s)", (nome, cat, preco, qtd, img_final)):
                    st.success("Produto catalogado com sucesso!"); st.rerun()
            else: st.warning("O nome do produto é obrigatório.")

    with tab3:
        df = buscar_dados("SELECT * FROM produtos ORDER BY nome ASC")
        if not df.empty:
            opcoes = {f"#{r['id']} - {r['nome']}": r['id'] for _, r in df.iterrows()}
            prod_id = opcoes[st.selectbox("Selecionar Produto para Edição", list(opcoes.keys()))]
            p = df[df['id'] == prod_id].iloc[0]
            
            e_nome = st.text_input("Nome", value=str(p['nome']))
            e_cat = st.selectbox("Categoria", ["Lâmpadas", "Fitas LED", "Plafons", "Spots", "Outros"], index=["Lâmpadas", "Fitas LED", "Plafons", "Spots", "Outros"].index(p.get('categoria', 'Outros')) if p.get('categoria', 'Outros') in ["Lâmpadas", "Fitas LED", "Plafons", "Spots", "Outros"] else 4)
            col_p, col_q = st.columns(2)
            
            e_preco = col_p.number_input("Preço", min_value=0.1, value=max(0.1, float(p['preco'])), format="%.2f")
            e_qtd = col_q.number_input("Estoque", min_value=0, step=1, value=max(0, int(p['quantidade'])))
            
            e_imagem_upload = st.file_uploader("Atualizar Imagem (Deixe vazio para manter a atual)", type=["png", "jpg", "jpeg"])
            
            if st.button("Salvar Alterações", type="primary", use_container_width=True):
                if e_imagem_upload:
                    img_final = converter_imagem_base64(e_imagem_upload)
                else:
                    img_final = str(p.get('imagem', ''))
                    
                if executar_comando("UPDATE produtos SET nome=%s, categoria=%s, preco=%s, quantidade=%s, imagem=%s WHERE id=%s", (e_nome, e_cat, e_preco, e_qtd, img_final, prod_id)):
                    st.success("Produto atualizado com sucesso!"); st.rerun()

    with tab4:
        df = buscar_dados("SELECT id, nome FROM produtos ORDER BY id DESC")
        if not df.empty:
            opcoes = {f"#{r['id']} - {r['nome']}": r['id'] for _, r in df.iterrows()}
            del_id = opcoes[st.selectbox("Selecionar Produto para Exclusão", list(opcoes.keys()))]
            if st.button("⚠️ Confirmar Exclusão Definitiva", type="primary", use_container_width=True):
                if executar_comando("DELETE FROM produtos WHERE id=%s", (del_id,)):
                    st.success("Produto removido do banco de dados!"); st.rerun()

# ==========================================
# 3. CLIENTES E CONTROLE DE ACESSO
# ==========================================
elif menu == "Clientes":
    st.markdown("<h4 style='color: #004aad !important;'>👥 Aprovação e Controle de Clientes</h4>", unsafe_allow_html=True)
    
    df_clientes = buscar_dados("SELECT * FROM clientes ORDER BY id DESC")
    if not df_clientes.empty:
        st.markdown("<div style='background: white; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 20px;'><b>🔐 Liberação de Acesso</b><p style='font-size: 13px; color: #64748b;'>Aprove contas pendentes para que os clientes possam acessar o e-commerce.</p>", unsafe_allow_html=True)
        
        opcoes_clientes = {f"#{r['id']} - {r['nome']}": r['id'] for _, r in df_clientes.iterrows()}
        cliente_selecionado = st.selectbox("Selecione a conta para aprovação", list(opcoes_clientes.keys()))
        id_cliente_aprovar = opcoes_clientes[cliente_selecionado]
        nome_cliente = cliente_selecionado.split('-')[1].strip()

        if st.button("✅ Aprovar e Liberar Acesso", use_container_width=True, type="primary"):
            try:
                executar_comando("UPDATE clientes SET status = 'Aprovado' WHERE id = %s", (id_cliente_aprovar,))
                st.success(f"Acesso liberado com sucesso para o cliente: {nome_cliente}")
            except Exception as e:
                st.error("Erro ao atualizar status.")
        st.markdown("</div>", unsafe_allow_html=True)
            
        st.divider()
        st.markdown("##### Base de Clientes Cadastrados")
        for _, c in df_clientes.iterrows():
            st.markdown(f"""
            <div class="card-cliente">
                <div style="font-size: 28px; background: #e6f0fa; padding: 10px; border-radius: 50%;">🏢</div>
                <div style="overflow: hidden;">
                    <h5 style="margin: 0; color: #004aad !important; font-weight: 700;">{c['nome']}</h5>
                    <span style="color: #64748b !important; font-size: 13px;">📧 {c['email']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("A base de clientes está vazia.")

# ==========================================
# 4. PEDIDOS
# ==========================================
elif menu == "Pedidos":
    st.markdown("<h4 style='color: #004aad !important;'>🛍️ Gestão de Encomendas</h4>", unsafe_allow_html=True)
    df_pedidos = buscar_dados("""
        SELECT p.id, c.nome as cliente, p.total, p.status, p.data_pedido 
        FROM pedidos p 
        JOIN clientes c ON p.cliente_id = c.id 
        ORDER BY p.data_pedido DESC
    """)
    
    if not df_pedidos.empty:
        st.markdown("<div style='background: white; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 20px;'><b>🔄 Atualização de Status</b>", unsafe_allow_html=True)
        opcoes_pedidos = {f"#{r['id']} - {r['cliente']}": r['id'] for _, r in df_pedidos.iterrows()}
        id_pedido = opcoes_pedidos[st.selectbox("Selecionar Pedido", list(opcoes_pedidos.keys()))]
        novo_status = st.selectbox("Novo Status Operacional", ["Pendente", "Em processamento", "Enviado", "Entregue", "Cancelado"])
        
        if st.button("Confirmar Atualização", type="primary", use_container_width=True):
            if novo_status == "Cancelado":
                itens = buscar_dados("SELECT produto_id, quantidade FROM itens_pedido WHERE pedido_id = %s", (id_pedido,))
                for _, item in itens.iterrows():
                    executar_comando("UPDATE produtos SET quantidade = quantidade + %s WHERE id = %s", (int(item['quantidade']), int(item['produto_id'])))
            if executar_comando("UPDATE pedidos SET status = %s WHERE id = %s", (novo_status, id_pedido)):
                st.success("Status atualizado no sistema!"); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
                
        st.divider()
        st.markdown("<h5 style='color: #333 !important;'>Histórico de Operações</h5>", unsafe_allow_html=True)
        for _, p in df_pedidos.iterrows():
            data_formatada = pd.to_datetime(p['data_pedido']).strftime("%d/%m/%Y às %H:%M")
            estilo_status = cor_do_status(p['status'])
            
            st.markdown(f"""
            <div class="card-pro">
                <div style="flex: 1 1 100%;">
                    <h5 style="margin: 0; color: #004aad !important; font-weight: 700;">Pedido #{p['id']}</h5>
                    <span style="color: #64748b !important; font-size: 13px;">👤 {p['cliente']} | 📅 {data_formatada}</span>
                </div>
                <div style="display: flex; gap: 10px; width: 100%; justify-content: space-between; align-items: center; margin-top: 10px;">
                    <h5 style="margin: 0; color: #0f172a !important; font-weight: 800;">R$ {float(p['total']):.2f}</h5>
                    <span class="badge-status" style="{estilo_status}">{p['status']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Não há pedidos registrados no sistema.")

# ==========================================
# 5. PREDITIVO (INTELIGÊNCIA DE NEGÓCIOS)
# ==========================================
elif menu == "Preditivo":
    st.markdown("<h4 style='color: #004aad !important;'>🧠 Inteligência de Estoque (BI)</h4>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 14px; color: #64748b !important;'>Análise algorítmica de risco de ruptura baseada nas saídas dos últimos 30 dias.</p>", unsafe_allow_html=True)
    
    query = """
        SELECT p.id, p.nome, COALESCE(p.quantidade, 0) as estoque,
               COALESCE(SUM(CASE WHEN ped.status != 'Cancelado' AND ped.data_pedido >= NOW() - INTERVAL '30 days' THEN ip.quantidade ELSE 0 END), 0) as vendido_30d
        FROM produtos p 
        LEFT JOIN itens_pedido ip ON ip.produto_id = p.id
        LEFT JOIN pedidos ped ON ped.id = ip.pedido_id 
        GROUP BY p.id, p.nome, p.quantidade
        ORDER BY estoque ASC
    """
    df = buscar_dados(query)
    
    if not df.empty:
        ordens, status_list, cor_borda_list, cor_fundo_list, cor_texto_list, msg_list = [], [], [], [], [], []
        
        for _, r in df.iterrows():
            estoque = int(r['estoque'])
            vendido = int(r['vendido_30d'])
            
            if estoque == 0:
                status, cor_borda, cor_fundo, cor_texto = "ESGOTADO", "#dc2626", "#fef2f2", "#991b1b"
                msg, ordem = "Ruptura crítica. Acione setor de suprimentos imediatamente.", 1
            elif estoque <= vendido and vendido > 0:
                status, cor_borda, cor_fundo, cor_texto = "ALTO RISCO", "#ea580c", "#fff7ed", "#9a3412"
                msg, ordem = f"Taxa de saída superior ao estoque ({vendido} un./mês). Reposição urgente.", 2
            elif estoque <= 5:
                status, cor_borda, cor_fundo, cor_texto = "ATENÇÃO", "#eab308", "#fefce8", "#854d0e"
                msg, ordem = "Estoque mínimo atingido. Planeje nova compra.", 3
            else:
                status, cor_borda, cor_fundo, cor_texto = "SAUDÁVEL", "#004aad", "#e6f0fa", "#003377"
                msg, ordem = "Nível de armazenamento estabilizado.", 4
                
            ordens.append(ordem)
            status_list.append(status)
            cor_borda_list.append(cor_borda)
            cor_fundo_list.append(cor_fundo)
            cor_texto_list.append(cor_texto)
            msg_list.append(msg)
            
        df['ordem'] = ordens
        df['status'] = status_list
        df['cor_borda'] = cor_borda_list
        df['cor_fundo'] = cor_fundo_list
        df['cor_texto'] = cor_texto_list
        df['msg'] = msg_list
        
        df = df.sort_values(by=['ordem', 'estoque'])
        
        for _, r in df.iterrows():
            st.markdown(f"""
            <div style="background-color: {r['cor_fundo']}; padding: 18px; border-radius: 8px; border-left: 6px solid {r['cor_borda']}; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.03); border-top: 1px solid #e5e7eb; border-right: 1px solid #e5e7eb; border-bottom: 1px solid #e5e7eb;">
                <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 8px; margin-bottom: 12px;">
                    <h5 style="margin: 0; color: #0f172a !important; flex: 1 1 60%; font-weight: 700;">{r['nome']}</h5>
                    <span style="background: {r['cor_borda']}; color: white; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 800; letter-spacing: 0.5px;">{r['status']}</span>
                </div>
                <div style="display: flex; gap: 20px; margin-bottom: 10px; color: #374151 !important; font-size: 14px;">
                    <div style="background: white; padding: 5px 10px; border-radius: 4px; border: 1px solid #e2e8f0;">📦 Estoque: <b>{r['estoque']}</b></div>
                    <div style="background: white; padding: 5px 10px; border-radius: 4px; border: 1px solid #e2e8f0;">📈 Vendido(30d): <b>{r['vendido_30d']}</b></div>
                </div>
                <div style="color: {r['cor_texto']} !important; font-size: 13px; font-weight: 600; margin-top: 8px;">
                    💡 {r['msg']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Sem dados para análise predativa.")
