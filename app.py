import streamlit as st
import pandas as pd

# 1. CONFIGURAÇÃO DA PÁGINA (MOBILE-FIRST)
st.set_page_config(page_title="JR Admin", page_icon="💡", layout="centered")

# 2. ESTILO CSS PARA O TEMA MOBILE
st.markdown("""
    <style>
    .block-container { max-width: 440px !important; padding-top: 3.2rem !important; padding-bottom: 6rem !important; margin: 0 auto !important; }
    #MainMenu, header, footer { visibility: hidden; }
    h1, h2, h3, h4 { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    div[data-testid="stMetric"] { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 12px 14px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04); margin-bottom: 8px; }
    div[data-testid="stMetricLabel"] p { font-size: 0.8rem !important; color: #64748b !important; font-weight: 600 !important; text-transform: uppercase; }
    div[data-testid="stMetricValue"] div { font-size: 1.35rem !important; color: #0f172a !important; font-weight: 700 !important; }
    div.stButton > button { border-radius: 10px; font-weight: 600; min-height: 46px; font-size: 0.95rem; }
    </style>
""", unsafe_allow_html=True)

# 3. BASE DE DADOS EM MEMÓRIA (SIMULAÇÃO ESTÁVEL PARA TCC)
if "produtos_db" not in st.session_state:
    st.session_state["produtos_db"] = pd.DataFrame([
        {"id": 1, "nome": "Lâmpada LED 10W", "preco": 45.50, "quantidade": 100},
        {"id": 2, "nome": "Fita LED RGB 5m", "preco": 89.90, "quantidade": 50},
        {"id": 3, "nome": "Spot LED Branco", "preco": 35.00, "quantidade": 75}
    ])

if "pedidos_db" not in st.session_state:
    st.session_state["pedidos_db"] = pd.DataFrame([
        {"id": 101, "cliente": "Miguel Aníbal", "total": 135.40, "status": "Pendente", "data": "2026-09-22 10:00"},
        {"id": 100, "cliente": "Julia Maria", "total": 89.90, "status": "Enviado", "data": "2026-09-21 15:30"}
    ])

if "clientes_db" not in st.session_state:
    st.session_state["clientes_db"] = pd.DataFrame([
        {"id": 1, "nome": "Miguel Aníbal", "email": "miguel@email.com", "telefone": "(11) 99999-9999", "ultimo_login": "22/09/2026 09:30"},
        {"id": 2, "nome": "Julia Maria", "email": "julia@email.com", "telefone": "(11) 98888-8888", "ultimo_login": "21/09/2026 14:15"}
    ])

# 4. CONTROLE DE SESSÃO DO ADMIN
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

# ==========================================
# ECRÃ DE LOGIN
# ==========================================
if not st.session_state["autenticado"]:
    st.markdown("""
        <div style='text-align: center; margin-top: 1.5rem; margin-bottom: 2rem;'>
            <div style='font-size: 2.8rem;'>💡</div>
            <h1 style='font-size: 1.6rem; color: #0F4C81; margin-bottom: 4px;'>JR Iluminação</h1>
            <p style='color: #64748b; font-size: 0.9rem; margin: 0;'>Painel de Gestão Administrativa</p>
        </div>
    """, unsafe_allow_html=True)
    
    usuario = st.text_input("Utilizador", placeholder="admin")
    senha = st.text_input("Palavra-passe", type="password", placeholder="••••••")
    st.write("")
    
    if st.button("Entrar no Painel", use_container_width=True, type="primary"):
        if usuario == "admin" and senha == "123456":
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Credenciais inválidas. Use admin / 123456")

# ==========================================
# PAINEL PRINCIPAL
# ==========================================
else:
    col_logo, col_logout = st.columns([3, 1], vertical_alignment="center")
    with col_logo:
        st.markdown("<h2 style='margin: 0; font-size: 1.3rem; color: #0F4C81;'>💡 JR Admin</h2>", unsafe_allow_html=True)
    with col_logout:
        if st.button("Sair", use_container_width=True):
            st.session_state["autenticado"] = False
            st.rerun()

    st.write("")
    menu_principal = st.radio("Navegação:", ["📊 Geral", "📦 Produtos", "🛒 Pedidos", "👥 Clientes"], horizontal=True, label_visibility="collapsed")
    st.divider()

    if menu_principal == "📊 Geral":
        st.markdown("<h4 style='color: #1e293b; margin-bottom: 12px;'>Resumo em Tempo Real</h4>", unsafe_allow_html=True)
        faturamento = st.session_state["pedidos_db"]["total"].sum()
        c1, c2 = st.columns(2)
        c1.metric("Faturamento", f"R$ {float(faturamento):,.2f}")
        c2.metric("Total Pedidos", str(len(st.session_state["pedidos_db"])))
        c3, c4 = st.columns(2)
        c3.metric("Estoque Total", f'{int(st.session_state["produtos_db"]["quantidade"].sum())} un.')
        c4.metric("Clientes", str(len(st.session_state["clientes_db"])))

    elif menu_principal == "📦 Produtos":
        st.markdown("<h4 style='color: #1e293b; margin-bottom: 8px;'>Catálogo de Produtos</h4>", unsafe_allow_html=True)
        acao = st.selectbox("Ação:", ["📋 Listar", "➕ Novo Produto"])
        if acao == "📋 Listar":
            st.dataframe(st.session_state["produtos_db"], use_container_width=True, hide_index=True)
        else:
            p_nome = st.text_input("Nome")
            p_preco = st.number_input("Preço", min_value=0.01)
            p_qtd = st.number_input("Estoque", min_value=0)
            if st.button("Salvar Produto", type="primary", use_container_width=True):
                novo_df = pd.DataFrame([{"id": len(st.session_state["produtos_db"])+1, "nome": p_nome, "preco": p_preco, "quantidade": p_qtd}])
                st.session_state["produtos_db"] = pd.concat([st.session_state["produtos_db"], novo_df], ignore_index=True)
                st.success("Produto salvo!")
                st.rerun()

    elif menu_principal == "🛒 Pedidos":
        st.markdown("<h4 style='color: #1e293b; margin-bottom: 8px;'>Gestão de Pedidos</h4>", unsafe_allow_html=True)
        st.dataframe(st.session_state["pedidos_db"], use_container_width=True, hide_index=True)

    elif menu_principal == "👥 Clientes":
        st.markdown("<h4 style='color: #1e293b; margin-bottom: 8px;'>Auditoria de Clientes</h4>", unsafe_allow_html=True)
        st.dataframe(st.session_state["clientes_db"], use_container_width=True, hide_index=True)