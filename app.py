import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Admin - JR Iluminação", page_icon="💡", layout="wide")

# --- CONEXÃO COM O BANCO DE DADOS (SUPABASE) ---
# Substitua a string abaixo pela sua URL do Supabase se não estiver usando o secrets
DB_URL = st.secrets["DB_URL"] if "DB_URL" in st.secrets else "postgresql://postgres:sua_senha@seu_host:5432/postgres"

def conectar():
    return psycopg2.connect(DB_URL)

def buscar_dados(query, params=None):
    try:
        conn = conectar()
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro no banco de dados: {e}")
        return pd.DataFrame()

def executar_comando(query, params=None):
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro ao executar comando: {e}")
        return False

# --- AUTENTICAÇÃO SIMPLES (SEGURANÇA DO PAINEL) ---
if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔒 Acesso Restrito - JR Iluminação")
    st.markdown("Área exclusiva para a administração do sistema.")
    senha = st.text_input("Senha de Administrador", type="password")
    if st.button("Entrar", type="primary"):
        if senha == "admin123": # Senha fictícia para a apresentação do TCC
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Senha incorreta.")
    st.stop()

# --- MENU LATERAL ---
with st.sidebar:
    st.image("https://placehold.co/400x200/0284c7/ffffff.png?text=JR+Iluminacao", use_container_width=True)
    st.title("Painel de Gestão")
    menu = st.radio("Navegação", ["Resumo", "Produtos", "Clientes", "Pedidos", "Preditivo"])
    st.divider()
    if st.button("Sair / Encerrar Sessão", use_container_width=True):
        st.session_state.logado = False
        st.rerun()

# ==========================================
# 1. RESUMO (DASHBOARD)
# ==========================================
if menu == "Resumo":
    st.title("📊 Resumo de Vendas")
    
    df_pedidos = buscar_dados("SELECT total, status FROM pedidos WHERE status != 'Cancelado'")
    receita_total = df_pedidos['total'].sum() if not df_pedidos.empty else 0
    qtd_pedidos = len(df_pedidos)
    
    df_clientes = buscar_dados("SELECT count(*) as total FROM clientes")
    total_clientes = df_clientes['total'].iloc[0] if not df_clientes.empty else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Faturamento Líquido", f"R$ {receita_total:,.2f}")
    col2.metric("Vendas Concluídas", qtd_pedidos)
    col3.metric("Clientes Cadastrados", total_clientes)
    
    st.divider()
    st.subheader("Últimos Pedidos")
    ultimos = buscar_dados("SELECT id, total, status, data_pedido FROM pedidos ORDER BY data_pedido DESC LIMIT 5")
    if not ultimos.empty:
        st.dataframe(ultimos, use_container_width=True, hide_index=True)
    else:
        st.info("Ainda não há pedidos cadastrados no sistema.")

# ==========================================
# 2. PRODUTOS (COM RENDERIZAÇÃO DE IMAGEM)
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
                        if pd.notna(r.get('imagem')) and str(r['imagem']).strip() != '' and r['imagem'] != 'placeholder.jpg':
                            st.image(str(r['imagem']), use_container_width=True)
                        else:
                            st.markdown("📦 Sem foto")
                            
                    with col_txt:
                        st.markdown(f"**{r['nome']}**")
                        st.caption(f"Categoria: {r.get('categoria', 'N/A')} | R$ {r['preco']:.2f} | Estoque: {r['quantidade']} un.")
        else: 
            st.info("Nenhum produto no catálogo.")
            
    with tab2:
        st.caption("Cadastre um novo item para venda na loja virtual.")
        nome = st.text_input("Nome do Produto", help="Nome que aparecerá na loja para o cliente.")
        cat = st.selectbox("Categoria", ["Lâmpadas", "Fitas LED", "Plafons", "Spots", "Outros"])
        preco = st.number_input("Preço Unitário (R$)", min_value=0.1, format="%.2f")
        qtd = st.number_input("Estoque Inicial", min_value=0, step=1)
        img_url = st.text_input("URL da Imagem (Opcional)", placeholder="https://link-da-foto.com/img.jpg")
        
        if st.button("Salvar Produto", type="primary", use_container_width=True):
            if nome:
                img_final = img_url if img_url else 'placeholder.jpg'
                if executar_comando("INSERT INTO produtos (nome, categoria, preco, quantidade, imagem) VALUES (%s, %s, %s, %s, %s)", (nome, cat, preco, qtd, img_final)):
                    st.success("Produto cadastrado com sucesso!"); st.rerun()
            else: st.warning("O nome do produto é obrigatório.")

    with tab3:
        df = buscar_dados("SELECT * FROM produtos ORDER BY nome ASC")
        if not df.empty:
            opcoes = {f"#{r['id']} - {r['nome']}": r['id'] for _, r in df.iterrows()}
            prod_id = opcoes[st.selectbox("Selecione o Produto para editar", list(opcoes.keys()))]
            p = df[df['id'] == prod_id].iloc[0]
            
            e_nome = st.text_input("Novo Nome", value=str(p['nome']))
            cats = ["Lâmpadas", "Fitas LED", "Plafons", "Spots", "Outros"]
            e_cat = st.selectbox("Nova Categoria", cats, index=cats.index(p.get('categoria', 'Outros')) if p.get('categoria', 'Outros') in cats else 4)
            e_preco = st.number_input("Novo Preço (R$)", min_value=0.1, value=float(p['preco']), format="%.2f")
            e_qtd = st.number_input("Ajustar Estoque", min_value=0, step=1, value=int(p['quantidade']))
            e_img = st.text_input("URL da Imagem", value=str(p.get('imagem', '')))
            
            if st.button("Atualizar Dados", type="primary", use_container_width=True):
                if executar_comando("UPDATE produtos SET nome=%s, categoria=%s, preco=%s, quantidade=%s, imagem=%s WHERE id=%s", (e_nome, e_cat, e_preco, e_qtd, e_img, prod_id)):
                    st.success("Produto atualizado!"); st.rerun()
        else: st.info("Sem produtos para editar.")

    with tab4:
        df = buscar_dados("SELECT id, nome FROM produtos ORDER BY id DESC")
        if not df.empty:
            opcoes = {f"#{r['id']} - {r['nome']}": r['id'] for _, r in df.iterrows()}
            del_id = opcoes[st.selectbox("Selecione o Produto para remover", list(opcoes.keys()))]
            st.error("⚠️ Atenção: Esta ação é definitiva e não pode ser desfeita.")
            if st.button("Excluir Permanentemente", type="primary", use_container_width=True):
                if executar_comando("DELETE FROM produtos WHERE id=%s", (del_id,)):
                    st.success("Produto excluído!"); st.rerun()
        else: st.info("Sem produtos para excluir.")

# ==========================================
# 3. CLIENTES (COM CONTROLE DE ACESSO)
# ==========================================
elif menu == "Clientes":
    st.title("👥 Gestão de Clientes")
    df_clientes = buscar_dados("SELECT * FROM clientes ORDER BY id DESC")
    
    if not df_clientes.empty:
        st.dataframe(df_clientes, use_container_width=True)
        
        st.subheader("Aprovar Acesso Rápido")
        st.caption("Cenário de demonstração para a banca (Aprovação de novo cliente).")
        col_sel, col_btn = st.columns([3, 1], vertical_alignment="bottom")
        with col_sel:
            cliente_aprovar = st.selectbox("Selecione o cliente recém-cadastrado", df_clientes['nome'].tolist())
        with col_btn:
            if st.button("✅ Aprovar Acesso", use_container_width=True):
                st.success(f"Acesso concedido a {cliente_aprovar} com sucesso!")
    else:
        st.info("Nenhum cliente cadastrado.")

# ==========================================
# 4. PEDIDOS (COM ESTORNO AUTOMÁTICO SIMULADO)
# ==========================================
elif menu == "Pedidos":
    st.title("🛍️ Gestão de Pedidos")
    df_pedidos = buscar_dados("""
        SELECT p.id, c.nome as cliente, p.total, p.status, p.data_pedido 
        FROM pedidos p 
        JOIN clientes c ON p.cliente_id = c.id 
        ORDER BY p.data_pedido DESC
    """)
    
    if not df_pedidos.empty:
        st.dataframe(df_pedidos, use_container_width=True, hide_index=True)
        
        st.subheader("Atualizar Status do Pedido")
        opcoes_pedidos = {f"Pedido #{r['id']} - {r['cliente']}": r['id'] for _, r in df_pedidos.iterrows()}
        ped_selecionado = st.selectbox("Selecione o pedido para atualizar", list(opcoes_pedidos.keys()))
        id_pedido = opcoes_pedidos[ped_selecionado]
        
        novo_status = st.selectbox("Novo Status", ["Pendente", "Em processamento", "Enviado", "Entregue", "Cancelado"])
        
        if st.button("Atualizar Status", type="primary"):
            # Lógica de estorno para a gravação: Se cancelar o pedido, devolve o estoque ao produto
            if novo_status == "Cancelado":
                itens = buscar_dados("SELECT produto_id, quantidade FROM itens_pedido WHERE pedido_id = %s", (id_pedido,))
                for _, item in itens.iterrows():
                    executar_comando("UPDATE produtos SET quantidade = quantidade + %s WHERE id = %s", (int(item['quantidade']), int(item['produto_id'])))
            
            if executar_comando("UPDATE pedidos SET status = %s WHERE id = %s", (novo_status, id_pedido)):
                st.success(f"Pedido #{id_pedido} atualizado para {novo_status}!")
                st.rerun()
    else:
        st.info("Nenhum pedido cadastrado.")

# ==========================================
# 5. PREDITIVO (SIMPLIFICADO E DIRETO)
# ==========================================
elif menu == "Preditivo":
    st.title("🧠 Inteligência de Estoque")
    st.caption("O sistema cruza o estoque atual com as vendas dos últimos 30 dias para gerar alertas automáticos.")
    
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
            
            # Regra Simplificada e Didática para TCC
            if estoque == 0:
                status = "ESGOTADO"
                cor_borda, cor_fundo, cor_texto = "#dc2626", "#fef2f2", "#991b1b"
                msg = "O produto zerou. Compre imediatamente com o fornecedor."
                ordem = 1
            elif estoque <= vendido and vendido > 0:
                status = "RISCO DE FALTA"
                cor_borda, cor_fundo, cor_texto = "#ea580c", "#fff7ed", "#9a3412"
                msg = f"Você vendeu {vendido} un. no último mês, mas só tem {estoque} un. Faça um pedido em breve."
                ordem = 2
            elif estoque <= 5:
                status = "ATENÇÃO"
                cor_borda, cor_fundo, cor_texto = "#eab308", "#fefce8", "#854d0e"
                msg = "O estoque está muito baixo, independentemente das vendas."
                ordem = 3
            else:
                status = "SAUDÁVEL"
                cor_borda, cor_fundo, cor_texto = "#22c55e", "#f0fdf4", "#166534"
                msg = "Quantidade segura na prateleira. Nenhuma ação necessária."
                ordem = 4
                
            r['ordem'] = ordem
            r['status'] = status
            r['cor_borda'] = cor_borda
            r['cor_fundo'] = cor_fundo
            r['cor_texto'] = cor_texto
            r['msg'] = msg
        
        # Ordenar para os piores casos (Esgotados e Risco) aparecerem primeiro no topo
        df = df.sort_values(by=['ordem', 'estoque'])
        
        for _, r in df.iterrows():
            st.markdown(f"""
            <div style="background-color: {r['cor_fundo']}; padding: 16px; border-radius: 8px; border-left: 6px solid {r['cor_borda']}; margin-bottom: 12px; border-top: 1px solid #e5e7eb; border-right: 1px solid #e5e7eb; border-bottom: 1px solid #e5e7eb;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <h4 style="margin: 0; color: #111827;">{r['nome']}</h4>
                    <span style="background: {r['cor_borda']}; color: white; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: bold; letter-spacing: 1px;">{r['status']}</span>
                </div>
                <div style="display: flex; gap: 20px; margin-bottom: 12px; color: #374151; font-size: 14px;">
                    <div>Estoque atual: <b>{r['estoque']} un.</b></div>
                    <div>Vendas (30 dias): <b>{r['vendido_30d']} un.</b></div>
                </div>
                <div style="color: {r['cor_texto']}; font-size: 13px; font-weight: 500; display: flex; align-items: center; gap: 6px;">
                    💡 {r['msg']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nenhum produto cadastrado para análise.")
