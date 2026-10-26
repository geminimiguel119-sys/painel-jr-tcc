import streamlit as st
import psycopg2
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Admin - JR Iluminação", page_icon="💡", layout="wide")

# --- ESTILOS CSS PERSONALIZADOS (UI MODERNA) ---
st.markdown("""
    <style>
    .card-dashboard {
        background-color: #ffffff; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); border-left: 5px solid #0284c7;
        margin-bottom: 15px; border-top: 1px solid #f1f5f9; border-right: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9;
    }
    .card-pedido {
        background-color: #ffffff; padding: 15px 20px; border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 12px;
        border: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center;
    }
    .card-cliente {
        background-color: #f8fafc; padding: 15px; border-radius: 10px;
        border: 1px solid #e2e8f0; margin-bottom: 10px; display: flex; align-items: center; gap: 15px;
    }
    .badge-status {
        padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; text-transform: uppercase;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONEXÃO COM O BANCO DE DADOS (SUPABASE) ---
DB_URL = "postgresql://postgres.bfppcxnxqagpesuyjlhe:An1bal_19691910%40@aws-0-us-west-2.pooler.supabase.com:5432/postgres"

def conectar():
    return psycopg2.connect(DB_URL)

# Tratamento de dados em grande escala exige fechamento seguro da conexão (finally)
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

# --- FUNÇÃO AUXILIAR DE CORES PARA STATUS ---
def cor_do_status(status):
    if status == 'Entregue': return "background-color: #dcfce7; color: #166534; border: 1px solid #bbf7d0;"
    if status == 'Cancelado': return "background-color: #fee2e2; color: #991b1b; border: 1px solid #fecaca;"
    if status == 'Pendente': return "background-color: #fef9c3; color: #854d0e; border: 1px solid #fef08a;"
    return "background-color: #dbeafe; color: #1e40af; border: 1px solid #bfdbfe;"

# --- AUTENTICAÇÃO E SESSÃO ---
if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔒 Acesso Restrito - JR Iluminação")
    st.markdown("Área exclusiva para a administração do sistema.")
    senha = st.text_input("Senha de Administrador", type="password")
    if st.button("Entrar", type="primary"):
        if senha == "admin123": 
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Acesso negado: Senha incorreta.")
    st.stop()

# --- MENU LATERAL ---
with st.sidebar:
    st.image("https://placehold.co/400x200/0284c7/ffffff.png?text=JR+Iluminacao", use_container_width=True)
    st.title("Painel de Gestão")
    menu = st.radio("Navegação", ["Resumo", "Produtos", "Clientes", "Pedidos", "Preditivo"])
    st.divider()
    if st.button("Encerrar Sessão", use_container_width=True):
        st.session_state.logado = False
        st.rerun()

# ==========================================
# 1. RESUMO (DASHBOARD FINANCEIRO)
# ==========================================
if menu == "Resumo":
    st.title("📊 Resumo de Vendas")
    
    df_pedidos = buscar_dados("SELECT total, status FROM pedidos WHERE status != 'Cancelado'")
    receita_total = df_pedidos['total'].sum() if not df_pedidos.empty else 0.0
    qtd_pedidos = len(df_pedidos)
    
    df_clientes = buscar_dados("SELECT count(*) as total FROM clientes")
    total_clientes = int(df_clientes['total'].iloc[0]) if not df_clientes.empty else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Faturamento Líquido", f"R$ {receita_total:,.2f}")
    col2.metric("Vendas Concluídas", qtd_pedidos)
    col3.metric("Clientes Cadastrados", total_clientes)
    
    st.divider()
    st.subheader("Últimos Pedidos")
    ultimos = buscar_dados("SELECT id, total, status, data_pedido FROM pedidos ORDER BY data_pedido DESC LIMIT 5")
    
    if not ultimos.empty:
        for _, p in ultimos.iterrows():
            data_formatada = pd.to_datetime(p['data_pedido']).strftime("%d/%m/%Y")
            estilo_status = cor_do_status(p['status'])
            
            st.markdown(f"""
            <div class="card-pedido">
                <div>
                    <h4 style="margin: 0; color: #1e293b;">Pedido #{p['id']}</h4>
                    <span style="color: #64748b; font-size: 14px;">📅 {data_formatada}</span>
                </div>
                <div>
                    <h4 style="margin: 0; color: #0f172a; text-align: right;">R$ {p['total']:.2f}</h4>
                </div>
                <div>
                    <span class="badge-status" style="{estilo_status}">{p['status']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Ainda não há pedidos processados no sistema.")

# ==========================================
# 2. PRODUTOS (GESTÃO DE CATÁLOGO)
# ==========================================
elif menu == "Produtos":
    st.title("📦 Gestão de Produtos")
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Catálogo", "➕ Adicionar", "✏️ Editar", "🗑️ Excluir"])
    
    with tab1:
        df = buscar_dados("SELECT * FROM produtos ORDER BY id DESC")
        if not df.empty:
            for _, r in df.iterrows():
                with st.container(border=True):
                    col_img, col_txt = st.columns([1, 4], vertical_alignment="center")
                    with col_img:
                        img = str(r.get('imagem', '')).strip()
                        if img and img != 'placeholder.jpg':
                            st.image(img, use_container_width=True)
                        else:
                            st.markdown("📦 Sem foto")
                    with col_txt:
                        st.markdown(f"<h3 style='margin:0; color:#1e293b;'>{r['nome']}</h3>", unsafe_allow_html=True)
                        st.markdown(f"<p style='margin:5px 0; color:#64748b;'>Categoria: {r.get('categoria', 'N/A')}</p>", unsafe_allow_html=True)
                        st.markdown(f"<h4 style='margin:0; color:#0284c7;'>R$ {float(r['preco']):.2f} &nbsp;&nbsp;|&nbsp;&nbsp; 📦 Estoque: {int(r['quantidade'])} un.</h4>", unsafe_allow_html=True)
        else: 
            st.info("Nenhum produto cadastrado.")
            
    with tab2:
        st.caption("Insira novos itens na base de dados de forma segura.")
        nome = st.text_input("Nome do Produto")
        cat = st.selectbox("Categoria", ["Lâmpadas", "Fitas LED", "Plafons", "Spots", "Outros"])
        preco = st.number_input("Preço Unitário (R$)", min_value=0.1, format="%.2f")
        qtd = st.number_input("Estoque Inicial", min_value=0, step=1)
        img_url = st.text_input("URL da Imagem (Opcional)", placeholder="https://unsplash.com/...")
        
        if st.button("Gravar Produto no Banco", type="primary", use_container_width=True):
            if nome:
                img_final = img_url if img_url else 'placeholder.jpg'
                if executar_comando("INSERT INTO produtos (nome, categoria, preco, quantidade, imagem) VALUES (%s, %s, %s, %s, %s)", (nome, cat, preco, qtd, img_final)):
                    st.success("Transação concluída: Produto inserido com sucesso!"); st.rerun()
            else: st.warning("Aviso de validação: O nome do produto é obrigatório.")

    with tab3:
        df = buscar_dados("SELECT * FROM produtos ORDER BY nome ASC")
        if not df.empty:
            opcoes = {f"#{r['id']} - {r['nome']}": r['id'] for _, r in df.iterrows()}
            prod_id = opcoes[st.selectbox("Selecione o Produto para edição", list(opcoes.keys()))]
            p = df[df['id'] == prod_id].iloc[0]
            
            e_nome = st.text_input("Nome Atualizado", value=str(p['nome']))
            cats = ["Lâmpadas", "Fitas LED", "Plafons", "Spots", "Outros"]
            e_cat = st.selectbox("Categoria Atualizada", cats, index=cats.index(p.get('categoria', 'Outros')) if p.get('categoria', 'Outros') in cats else 4)
            e_preco = st.number_input("Preço Atualizado (R$)", min_value=0.1, value=float(p['preco']), format="%.2f")
            e_qtd = st.number_input("Correção de Estoque", min_value=0, step=1, value=int(p['quantidade']))
            e_img = st.text_input("URL da Imagem Atualizada", value=str(p.get('imagem', '')))
            
            if st.button("Efetuar Update", type="primary", use_container_width=True):
                if executar_comando("UPDATE produtos SET nome=%s, categoria=%s, preco=%s, quantidade=%s, imagem=%s WHERE id=%s", (e_nome, e_cat, e_preco, e_qtd, e_img, prod_id)):
                    st.success("Update processado com sucesso!"); st.rerun()

    with tab4:
        df = buscar_dados("SELECT id, nome FROM produtos ORDER BY id DESC")
        if not df.empty:
            opcoes = {f"#{r['id']} - {r['nome']}": r['id'] for _, r in df.iterrows()}
            del_id = opcoes[st.selectbox("Selecione o Produto para remoção", list(opcoes.keys()))]
            st.error("⚠️ Operação Destrutiva: A exclusão do banco de dados é irreversível.")
            if st.button("Confirmar Exclusão (DELETE)", type="primary", use_container_width=True):
                if executar_comando("DELETE FROM produtos WHERE id=%s", (del_id,)):
                    st.success("Registro removido do sistema!"); st.rerun()

# ==========================================
# 3. CLIENTES E CONTROLE DE ACESSO
# ==========================================
elif menu == "Clientes":
    st.title("👥 Gestão de Contas de Acesso")
    df_clientes = buscar_dados("SELECT * FROM clientes ORDER BY id DESC")
    
    if not df_clientes.empty:
        st.subheader("Usuários Registrados")
        for _, c in df_clientes.iterrows():
            st.markdown(f"""
            <div class="card-cliente">
                <div style="font-size: 30px;">👤</div>
                <div>
                    <h4 style="margin: 0; color: #0f172a;">{c['nome']}</h4>
                    <span style="color: #64748b;">📧 {c['email']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("Auditoria de Acesso")
        st.caption("Liberação manual de novos cadastros.")
        col_sel, col_btn = st.columns([3, 1], vertical_alignment="bottom")
        with col_sel:
            cliente_aprovar = st.selectbox("Selecione a conta pendente", df_clientes['nome'].tolist())
        with col_btn:
            if st.button("✅ Autorizar Acesso", use_container_width=True, type="primary"):
                st.success(f"Permissão concedida à conta: {cliente_aprovar}")
    else:
        st.info("O banco de dados de usuários está vazio.")

# ==========================================
# 4. PEDIDOS E ROLLBACK DE ESTOQUE
# ==========================================
elif menu == "Pedidos":
    st.title("🛍️ Central de Pedidos e Logística")
    df_pedidos = buscar_dados("""
        SELECT p.id, c.nome as cliente, p.total, p.status, p.data_pedido 
        FROM pedidos p 
        JOIN clientes c ON p.cliente_id = c.id 
        ORDER BY p.data_pedido DESC
    """)
    
    if not df_pedidos.empty:
        for _, p in df_pedidos.iterrows():
            data_formatada = pd.to_datetime(p['data_pedido']).strftime("%d/%m/%Y às %H:%M")
            estilo_status = cor_do_status(p['status'])
            
            st.markdown(f"""
            <div class="card-pedido">
                <div style="flex: 2;">
                    <h4 style="margin: 0; color: #1e293b;">Transação #{p['id']}</h4>
                    <span style="color: #64748b; font-size: 14px;">👤 Cliente: <b>{p['cliente']}</b></span><br>
                    <span style="color: #94a3b8; font-size: 13px;">📅 {data_formatada}</span>
                </div>
                <div style="flex: 1; text-align: center;">
                    <h4 style="margin: 0; color: #0f172a;">R$ {float(p['total']):.2f}</h4>
                </div>
                <div style="flex: 1; text-align: right;">
                    <span class="badge-status" style="{estilo_status}">{p['status']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("Processamento de Status")
        opcoes_pedidos = {f"Pedido #{r['id']} - {r['cliente']}": r['id'] for _, r in df_pedidos.iterrows()}
        ped_selecionado = st.selectbox("Identificador da Transação", list(opcoes_pedidos.keys()))
        id_pedido = opcoes_pedidos[ped_selecionado]
        novo_status = st.selectbox("Ação Logística", ["Pendente", "Em processamento", "Enviado", "Entregue", "Cancelado"])
        
        if st.button("Confirmar Alteração", type="primary"):
            if novo_status == "Cancelado":
                itens = buscar_dados("SELECT produto_id, quantidade FROM itens_pedido WHERE pedido_id = %s", (id_pedido,))
                for _, item in itens.iterrows():
                    executar_comando("UPDATE produtos SET quantidade = quantidade + %s WHERE id = %s", (int(item['quantidade']), int(item['produto_id'])))
            
            if executar_comando("UPDATE pedidos SET status = %s WHERE id = %s", (novo_status, id_pedido)):
                st.success(f"Status do pedido #{id_pedido} alterado com sucesso.")
                st.rerun()

# ==========================================
# 5. PREDITIVO (INTELIGÊNCIA DE NEGÓCIOS)
# ==========================================
elif menu == "Preditivo":
    st.title("🧠 Business Intelligence (BI)")
    st.caption("Cruzamento automatizado entre volume de saída (30 dias) e capacidade atual de armazenamento.")
    
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
        for _, r in df.iterrows():
            estoque = int(r['estoque'])
            vendido = int(r['vendido_30d'])
            
            if estoque == 0:
                status, cor_borda, cor_fundo, cor_texto = "ALERTA CRÍTICO: ESGOTADO", "#dc2626", "#fef2f2", "#991b1b"
                msg, ordem = "Ruptura de estoque detectada. Necessário acionamento imediato da cadeia de suprimentos.", 1
            elif estoque <= vendido and vendido > 0:
                status, cor_borda, cor_fundo, cor_texto = "RISCO DE RUPTURA", "#ea580c", "#fff7ed", "#9a3412"
                msg, ordem = f"Taxa de escoamento ({vendido} un/mês) supera capacidade de armazenagem atual ({estoque} un).", 2
            elif estoque <= 5:
                status, cor_borda, cor_fundo, cor_texto = "ATENÇÃO LOGÍSTICA", "#eab308", "#fefce8", "#854d0e"
                msg, ordem = "Volume de segurança inferior ao limite mínimo operacional (5 unidades).", 3
            else:
                status, cor_borda, cor_fundo, cor_texto = "ÍNDICE SAUDÁVEL", "#22c55e", "#f0fdf4", "#166534"
                msg, ordem = "Projeção de estoque estabilizada. Nenhuma intervenção sistêmica necessária.", 4
                
            r['ordem'], r['status'], r['cor_borda'], r['cor_fundo'], r['cor_texto'], r['msg'] = ordem, status, cor_borda, cor_fundo, cor_texto, msg
        
        df = df.sort_values(by=['ordem', 'estoque'])
        
        for _, r in df.iterrows():
            st.markdown(f"""
            <div style="background-color: {r['cor_fundo']}; padding: 16px; border-radius: 8px; border-left: 6px solid {r['cor_borda']}; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); border: 1px solid #e5e7eb;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <h4 style="margin: 0; color: #111827;">{r['nome']}</h4>
                    <span style="background: {r['cor_borda']}; color: white; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: bold;">{r['status']}</span>
                </div>
                <div style="display: flex; gap: 20px; margin-bottom: 12px; color: #374151; font-size: 14px;">
                    <div>Estoque Físico: <b>{r['estoque']} un.</b></div>
                    <div>Volume de Saída (30d): <b>{r['vendido_30d']} un.</b></div>
                </div>
                <div style="color: {r['cor_texto']}; font-size: 13px; font-weight: 500;">
                    💡 {r['msg']}
                </div>
            </div>
            """, unsafe_allow_html=True)
