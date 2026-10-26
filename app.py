import streamlit as st
import psycopg2
import pandas as pd
import base64
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA (FOCADA EM MOBILE) ---
st.set_page_config(page_title="App - JR Iluminação", page_icon="📱", layout="centered")

# --- ESTILOS CSS PERSONALIZADOS (MOBILE RESPONSIVO) ---
st.markdown("""
    <style>
    .card-pedido {
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 12px;
        border: 1px solid #e2e8f0; display: flex; flex-wrap: wrap; gap: 10px; justify-content: space-between; align-items: center;
    }
    .card-cliente {
        background-color: #f8fafc; padding: 15px; border-radius: 10px;
        border: 1px solid #e2e8f0; margin-bottom: 10px; display: flex; align-items: center; gap: 15px;
    }
    .badge-status {
        padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; text-transform: uppercase; white-space: nowrap;
    }
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
        st.error(f"Erro na execução (Rollback acionado): {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

def cor_do_status(status):
    if status == 'Entregue': return "background-color: #dcfce7; color: #166534; border: 1px solid #bbf7d0;"
    if status == 'Cancelado': return "background-color: #fee2e2; color: #991b1b; border: 1px solid #fecaca;"
    if status == 'Pendente': return "background-color: #fef9c3; color: #854d0e; border: 1px solid #fef08a;"
    return "background-color: #dbeafe; color: #1e40af; border: 1px solid #bfdbfe;"

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
    st.markdown("<h2 style='text-align: center;'>🔒 Acesso Restrito</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Área exclusiva para a administração do sistema.</p>", unsafe_allow_html=True)
    senha = st.text_input("Senha de Administrador", type="password")
    if st.button("Entrar", type="primary", use_container_width=True):
        if senha == "admin123": 
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Acesso negado: Senha incorreta.")
    st.stop()

# ==========================================
# HEADER E NAVEGAÇÃO TOPO (MOBILE UI)
# ==========================================
col_logo, col_logout = st.columns([3, 1], vertical_alignment="center")
with col_logo:
    st.markdown("<h3 style='margin:0;'>💡 JR Admin</h3>", unsafe_allow_html=True)
with col_logout:
    if st.button("Sair", use_container_width=True):
        st.session_state.logado = False
        st.rerun()

menu = st.radio("Navegação", ["Resumo", "Produtos", "Clientes", "Pedidos", "Preditivo"], horizontal=True, label_visibility="collapsed")
st.divider()

# ==========================================
# 1. RESUMO (DASHBOARD FINANCEIRO)
# ==========================================
if menu == "Resumo":
    st.subheader("📊 Resumo de Vendas")
    
    df_pedidos = buscar_dados("SELECT total, status FROM pedidos WHERE status != 'Cancelado'")
    receita_total = df_pedidos['total'].sum() if not df_pedidos.empty else 0.0
    qtd_pedidos = len(df_pedidos)
    
    df_clientes = buscar_dados("SELECT count(*) as total FROM clientes")
    total_clientes = int(df_clientes['total'].iloc[0]) if not df_clientes.empty else 0
    
    col1, col2 = st.columns(2)
    col1.metric("Faturamento", f"R$ {receita_total:,.2f}")
    col2.metric("Vendas", qtd_pedidos)
    st.metric("Clientes Cadastrados", total_clientes)
    
    st.divider()
    st.markdown("#### Últimos Pedidos")
    ultimos = buscar_dados("SELECT id, total, status, data_pedido FROM pedidos ORDER BY data_pedido DESC LIMIT 5")
    
    if not ultimos.empty:
        for _, p in ultimos.iterrows():
            data_formatada = pd.to_datetime(p['data_pedido']).strftime("%d/%m")
            estilo_status = cor_do_status(p['status'])
            
            st.markdown(f"""
            <div class="card-pedido">
                <div>
                    <h5 style="margin: 0; color: #1e293b;">#{p['id']}</h5>
                    <span style="color: #64748b; font-size: 13px;">📅 {data_formatada}</span>
                </div>
                <div>
                    <h5 style="margin: 0; color: #0f172a;">R$ {p['total']:.2f}</h5>
                </div>
                <div>
                    <span class="badge-status" style="{estilo_status}">{p['status']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nenhum pedido processado.")

# ==========================================
# 2. PRODUTOS (COM UPLOAD DE FOTO)
# ==========================================
elif menu == "Produtos":
    st.subheader("📦 Produtos")
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Lista", "➕ Add", "✏️ Edit", "🗑️ Del"])
    
    with tab1:
        df = buscar_dados("SELECT * FROM produtos ORDER BY id DESC")
        if not df.empty:
            for _, r in df.iterrows():
                with st.container(border=True):
                    col_img, col_txt = st.columns([1, 3], vertical_alignment="center")
                    with col_img:
                        img = str(r.get('imagem', '')).strip()
                        if img and img != 'None' and img != 'placeholder.jpg':
                            st.markdown(f'<img src="{img}" style="width:100%; border-radius:8px; object-fit: cover;">', unsafe_allow_html=True)
                        else:
                            st.markdown("📦 Sem foto")
                    with col_txt:
                        st.markdown(f"<h4 style='margin:0; color:#1e293b; font-size: 16px;'>{r['nome']}</h4>", unsafe_allow_html=True)
                        st.markdown(f"<p style='margin:2px 0; color:#64748b; font-size: 12px;'>Cat: {r.get('categoria', 'N/A')}</p>", unsafe_allow_html=True)
                        st.markdown(f"<div style='color:#0284c7; font-weight: bold;'>R$ {float(r['preco']):.2f} <br> 📦 Estoque: {int(r['quantidade'])}</div>", unsafe_allow_html=True)
        else: 
            st.info("Catálogo vazio.")
            
    with tab2:
        nome = st.text_input("Nome do Produto")
        cat = st.selectbox("Categoria", ["Lâmpadas", "Fitas LED", "Plafons", "Spots", "Outros"])
        col_p, col_q = st.columns(2)
        preco = col_p.number_input("Preço (R$)", min_value=0.1, format="%.2f")
        qtd = col_q.number_input("Estoque", min_value=0, step=1)
        
        # Upload de Imagem
        imagem_upload = st.file_uploader("Fazer Upload da Foto", type=["png", "jpg", "jpeg"])
        
        if st.button("Gravar Produto", type="primary", use_container_width=True):
            if nome:
                img_final = converter_imagem_base64(imagem_upload)
                if executar_comando("INSERT INTO produtos (nome, categoria, preco, quantidade, imagem) VALUES (%s, %s, %s, %s, %s)", (nome, cat, preco, qtd, img_final)):
                    st.success("Inserido com sucesso!"); st.rerun()
            else: st.warning("Nome obrigatório.")

    with tab3:
        df = buscar_dados("SELECT * FROM produtos ORDER BY nome ASC")
        if not df.empty:
            opcoes = {f"#{r['id']} - {r['nome']}": r['id'] for _, r in df.iterrows()}
            prod_id = opcoes[st.selectbox("Selecionar Produto", list(opcoes.keys()))]
            p = df[df['id'] == prod_id].iloc[0]
            
            e_nome = st.text_input("Nome", value=str(p['nome']))
            e_cat = st.selectbox("Categoria", ["Lâmpadas", "Fitas LED", "Plafons", "Spots", "Outros"], index=["Lâmpadas", "Fitas LED", "Plafons", "Spots", "Outros"].index(p.get('categoria', 'Outros')) if p.get('categoria', 'Outros') in ["Lâmpadas", "Fitas LED", "Plafons", "Spots", "Outros"] else 4)
            col_p, col_q = st.columns(2)
            
            # PROTEÇÃO ADICIONADA AQUI (max(val, limite))
            e_preco = col_p.number_input("Preço", min_value=0.1, value=max(0.1, float(p['preco'])), format="%.2f")
            e_qtd = col_q.number_input("Estoque", min_value=0, step=1, value=max(0, int(p['quantidade'])))
            
            # Atualizar Imagem
            e_imagem_upload = st.file_uploader("Trocar Foto (Deixe vazio para manter a atual)", type=["png", "jpg", "jpeg"])
            
            if st.button("Atualizar", type="primary", use_container_width=True):
                if e_imagem_upload:
                    img_final = converter_imagem_base64(e_imagem_upload)
                else:
                    img_final = str(p.get('imagem', ''))
                    
                if executar_comando("UPDATE produtos SET nome=%s, categoria=%s, preco=%s, quantidade=%s, imagem=%s WHERE id=%s", (e_nome, e_cat, e_preco, e_qtd, img_final, prod_id)):
                    st.success("Atualizado!"); st.rerun()

    with tab4:
        df = buscar_dados("SELECT id, nome FROM produtos ORDER BY id DESC")
        if not df.empty:
            opcoes = {f"#{r['id']} - {r['nome']}": r['id'] for _, r in df.iterrows()}
            del_id = opcoes[st.selectbox("Selecionar para excluir", list(opcoes.keys()))]
            if st.button("Confirmar Exclusão", type="primary", use_container_width=True):
                if executar_comando("DELETE FROM produtos WHERE id=%s", (del_id,)):
                    st.success("Removido!"); st.rerun()

# ==========================================
# 3. CLIENTES E CONTROLE DE ACESSO
# ==========================================
elif menu == "Clientes":
    st.subheader("👥 Clientes")
    
    df_clientes = buscar_dados("SELECT * FROM clientes ORDER BY id DESC")
    if not df_clientes.empty:
        st.markdown("**Liberação Rápida**")
        cliente_aprovar = st.selectbox("Usuário pendente", df_clientes['nome'].tolist())
        if st.button("✅ Autorizar", use_container_width=True, type="primary"):
            st.success(f"Acesso liberado para {cliente_aprovar}")
            
        st.divider()
        st.markdown("**Base Cadastrada**")
        for _, c in df_clientes.iterrows():
            st.markdown(f"""
            <div class="card-cliente">
                <div style="font-size: 24px;">👤</div>
                <div style="overflow: hidden;">
                    <h5 style="margin: 0; color: #0f172a; white-space: nowrap; text-overflow: ellipsis;">{c['nome']}</h5>
                    <span style="color: #64748b; font-size: 12px; white-space: nowrap; text-overflow: ellipsis;">{c['email']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nenhum cliente.")

# ==========================================
# 4. PEDIDOS E ROLLBACK DE ESTOQUE
# ==========================================
elif menu == "Pedidos":
    st.subheader("🛍️ Pedidos")
    df_pedidos = buscar_dados("""
        SELECT p.id, c.nome as cliente, p.total, p.status, p.data_pedido 
        FROM pedidos p 
        JOIN clientes c ON p.cliente_id = c.id 
        ORDER BY p.data_pedido DESC
    """)
    
    if not df_pedidos.empty:
        st.markdown("**Alterar Status**")
        opcoes_pedidos = {f"#{r['id']} - {r['cliente']}": r['id'] for _, r in df_pedidos.iterrows()}
        id_pedido = opcoes_pedidos[st.selectbox("Pedido", list(opcoes_pedidos.keys()))]
        novo_status = st.selectbox("Status", ["Pendente", "Em processamento", "Enviado", "Entregue", "Cancelado"])
        
        if st.button("Confirmar", type="primary", use_container_width=True):
            if novo_status == "Cancelado":
                itens = buscar_dados("SELECT produto_id, quantidade FROM itens_pedido WHERE pedido_id = %s", (id_pedido,))
                for _, item in itens.iterrows():
                    executar_comando("UPDATE produtos SET quantidade = quantidade + %s WHERE id = %s", (int(item['quantidade']), int(item['produto_id'])))
            if executar_comando("UPDATE pedidos SET status = %s WHERE id = %s", (novo_status, id_pedido)):
                st.success("Alterado!"); st.rerun()
                
        st.divider()
        st.markdown("**Histórico**")
        for _, p in df_pedidos.iterrows():
            data_formatada = pd.to_datetime(p['data_pedido']).strftime("%d/%m")
            estilo_status = cor_do_status(p['status'])
            
            st.markdown(f"""
            <div class="card-pedido">
                <div style="flex: 1 1 100%;">
                    <h5 style="margin: 0; color: #1e293b;">Pedido #{p['id']}</h5>
                    <span style="color: #64748b; font-size: 13px;">👤 {p['cliente']} | 📅 {data_formatada}</span>
                </div>
                <div style="display: flex; gap: 10px; width: 100%; justify-content: space-between; align-items: center; margin-top: 5px;">
                    <h5 style="margin: 0; color: #0f172a;">R$ {float(p['total']):.2f}</h5>
                    <span class="badge-status" style="{estilo_status}">{p['status']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nenhum pedido.")

# ==========================================
# 5. PREDITIVO (INTELIGÊNCIA DE NEGÓCIOS)
# ==========================================
elif menu == "Preditivo":
    st.subheader("🧠 BI Estoque")
    
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
                msg, ordem = "Ruptura. Acione suprimentos.", 1
            elif estoque <= vendido and vendido > 0:
                status, cor_borda, cor_fundo, cor_texto = "RISCO", "#ea580c", "#fff7ed", "#9a3412"
                msg, ordem = f"Saída alta ({vendido}/mês).", 2
            elif estoque <= 5:
                status, cor_borda, cor_fundo, cor_texto = "ATENÇÃO", "#eab308", "#fefce8", "#854d0e"
                msg, ordem = "Estoque mínimo atingido.", 3
            else:
                status, cor_borda, cor_fundo, cor_texto = "SAUDÁVEL", "#22c55e", "#f0fdf4", "#166534"
                msg, ordem = "Nível estabilizado.", 4
                
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
            <div style="background-color: {r['cor_fundo']}; padding: 15px; border-radius: 8px; border-left: 5px solid {r['cor_borda']}; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); border: 1px solid #e5e7eb;">
                <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-start; gap: 8px; margin-bottom: 10px;">
                    <h5 style="margin: 0; color: #111827; flex: 1 1 60%;">{r['nome']}</h5>
                    <span style="background: {r['cor_borda']}; color: white; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: bold;">{r['status']}</span>
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 8px; color: #374151; font-size: 13px;">
                    <div>Estoque: <b>{r['estoque']}</b></div>
                    <div>Vendido(30d): <b>{r['vendido_30d']}</b></div>
                </div>
                <div style="color: {r['cor_texto']}; font-size: 12px; font-weight: 500;">
                    💡 {r['msg']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Sem dados para análise.")
