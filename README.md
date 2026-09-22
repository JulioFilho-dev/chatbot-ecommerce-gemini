# 🛍️ Chatbot de E-commerce com RAG e Gemini

Chatbot de atendimento para loja de roupas, capaz de consultar produtos, preços, descrições e estoque em tempo real, usando RAG (Retrieval-Augmented Generation) simples e a LLM Gemini do Google.

## Funcionalidades

- Consulta de produtos, preços, tamanhos e disponibilidade em estoque
- RAG simples com TF-IDF para busca por relevância
- Filtro inteligente por faixa de preço (mais barato, mais caro, até X reais)
- Detecção de pedidos de catálogo completo
- Memória de conversa (entende perguntas de acompanhamento)
- Interface de chat via Streamlit
- Tratamento de erros de disponibilidade e limite de uso da API

## Tecnologias

- Python
- Google Gemini API (`google-genai`)
- scikit-learn (TF-IDF + similaridade de cosseno)
- Streamlit (frontend)

## Como rodar localmente

1. Clone o repositório:
```bash
   git clone <URL_DO_REPOSITORIO>
   cd chatbot-ecommerce
```

2. Crie e ative o ambiente virtual:
```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   source venv/bin/activate  # Mac/Linux
```

3. Instale as dependências:
```bash
   pip install google-genai python-dotenv scikit-learn streamlit
```

4. Crie um arquivo `.env` na raiz com sua chave da API do Gemini: