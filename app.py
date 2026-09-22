import streamlit as st
from chatbot import responder
from retrieval import carregar_produtos

st.set_page_config(page_title="Loja Estilo - Atendimento", page_icon="🛍️")

AVATAR_BOT = "🧑‍💼"
AVATAR_USER = "🙂"
NOME_BOT = "Sofia"

st.title("🛍️ Loja Estilo")
st.caption(f"Atendimento virtual com {NOME_BOT} · powered by Gemini")

if "produtos" not in st.session_state:
    st.session_state.produtos = carregar_produtos()

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []
    st.session_state.mensagens.append({
        "role": "assistant",
        "content": f"Oi! Eu sou a {NOME_BOT} 👋 Posso te ajudar a encontrar produtos, "
                    f"ver preços, tamanhos e estoque. O que você está procurando hoje?"
    })

for msg in st.session_state.mensagens:
    avatar = AVATAR_BOT if msg["role"] == "assistant" else AVATAR_USER
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

if len(st.session_state.mensagens) == 1:
    st.write("Sugestões:")
    col1, col2, col3 = st.columns(3)
    sugestao_clicada = None

    with col1:
        if st.button("📋 Ver catálogo"):
            sugestao_clicada = "Qual é o catálogo de produtos?"
    with col2:
        if st.button("💰 Mais barato"):
            sugestao_clicada = "Qual o produto mais barato?"
    with col3:
        if st.button("👖 Calças jeans"):
            sugestao_clicada = "Vocês têm calça jeans?"
else:
    sugestao_clicada = None

pergunta = st.chat_input("Digite sua pergunta...")

pergunta_final = sugestao_clicada or pergunta

if pergunta_final:
    st.session_state.mensagens.append({"role": "user", "content": pergunta_final})
    with st.chat_message("user", avatar=AVATAR_USER):
        st.markdown(pergunta_final)

    with st.chat_message("assistant", avatar=AVATAR_BOT):
        with st.spinner(f"{NOME_BOT} está digitando..."):
            historico_anterior = st.session_state.mensagens[:-1]
            resposta = responder(pergunta_final, st.session_state.produtos, historico_anterior)
        st.markdown(resposta)

    st.session_state.mensagens.append({"role": "assistant", "content": resposta})
    st.rerun()  