import os
import time
from google import genai
from google.genai import errors, types
from dotenv import load_dotenv
from retrieval import carregar_produtos, buscar_produtos_relevantes

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODELO = "gemini-3.5-flash-lite"


def montar_contexto(produtos_encontrados):
    if not produtos_encontrados:
        return "Nenhum produto encontrado na base para essa pergunta."

    linhas = []
    for p in produtos_encontrados:
        status_estoque = "Esgotado" if p["estoque"] == 0 else f"{p['estoque']} unidades disponíveis"
        linhas.append(
            f"- {p['nome']} ({p['categoria']}): {p['descricao']} "
            f"| Preço: R$ {p['preco']} | Tamanhos: {', '.join(p['tamanhos'])} "
            f"| Estoque: {status_estoque}"
        )
    return "\n".join(linhas)


def montar_historico(historico):
    """Transforma o histórico de mensagens em texto para dar contexto ao Gemini."""
    if not historico:
        return "Nenhuma mensagem anterior nesta conversa."

    linhas = []
    for msg in historico[-6:]:
        papel = "Cliente" if msg["role"] == "user" else "Assistente"
        linhas.append(f"{papel}: {msg['content']}")
    return "\n".join(linhas)


def chamar_gemini_com_retry(prompt, tentativas=3, espera_inicial=2):
    for tentativa in range(1, tentativas + 1):
        print(f"[DEBUG] Tentativa {tentativa} iniciada...")
        inicio = time.time()
        try:
            resposta = client.models.generate_content(
                model=MODELO,
                contents=prompt,
                config=types.GenerateContentConfig(
                    http_options=types.HttpOptions(
                        retry_options=types.HttpRetryOptions(attempts=1)
                    )
                ),
            )
            print(f"[DEBUG] Respondeu em {time.time() - inicio:.1f}s")
            return resposta.text
        except errors.ServerError:
            print(f"[DEBUG] Deu 503 depois de {time.time() - inicio:.1f}s")
            if tentativa == tentativas:
                return (
                    "Desculpa, o serviço está com alta demanda no momento e não "
                    "consegui responder. Tenta novamente em alguns instantes! 🙏"
                )
            time.sleep(espera_inicial * tentativa)
        except errors.ClientError as e:
            if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                print("[DEBUG] Cota diária excedida (429)")
                return (
                    "No momento atingi o limite diário de uso gratuito da IA. "
                    "Por favor, tente novamente mais tarde. 🙏"
                )
            raise


def responder(pergunta_usuario, produtos, historico=None):
    encontrados = buscar_produtos_relevantes(pergunta_usuario, produtos)
    contexto = montar_contexto(encontrados)
    historico_texto = montar_historico(historico)

    prompt = f"""Você é um assistente de atendimento de uma loja de roupas.
Responda a pergunta do cliente usando APENAS as informações dos produtos abaixo.
Se o cliente pedir o catálogo completo, liste os produtos de forma resumida (nome e preço),
sem repetir a descrição inteira de cada um.
Se não houver produto relevante, diga educadamente que não encontrou nada parecido no catálogo.
Se a pergunta do cliente fizer referência a algo mencionado antes na conversa
(ex: "esse", "nele", "esse aí"), use o histórico abaixo para entender a que ele se refere.
Se um produto relevante for encontrado mas um detalhe específico (como um tamanho) não
aparecer claramente nas informações abaixo, não afirme que não está disponível -
oriente o cliente a confirmar diretamente na loja.
Seja breve e natural, como um vendedor simpático.

Histórico da conversa:
{historico_texto}

Produtos disponíveis:
{contexto}

Pergunta atual do cliente: {pergunta_usuario}
"""

    return chamar_gemini_com_retry(prompt)


if __name__ == "__main__":
    produtos = carregar_produtos()
    historico = []

    print("🛍️  Bem-vindo ao chatbot da loja! Digite 'sair' para encerrar.\n")

    while True:
        pergunta = input("Você: ")

        if pergunta.strip().lower() in ("sair", "exit", "quit"):
            print("Até mais! 👋")
            break

        resposta = responder(pergunta, produtos, historico)
        print(f"\nBot: {resposta}\n")

        historico.append({"role": "user", "content": pergunta})
        historico.append({"role": "assistant", "content": resposta})