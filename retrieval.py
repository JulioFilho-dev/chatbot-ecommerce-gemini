import os
import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def carregar_produtos(caminho=None):
    if caminho is None:
        caminho = os.path.join(BASE_DIR, "data", "produtos.json")
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def montar_texto_busca(produto):
    """Junta os campos relevantes do produto em um único texto para comparação."""
    tamanhos_texto = " ".join(produto.get("tamanhos", []))
    return f"{produto['nome']} {produto['categoria']} {produto['descricao']} tamanho {tamanhos_texto}"


PALAVRAS_CATALOGO_COMPLETO = [
    "catálogo", "catalogo", "produtos", "o que vocês tem", "o que voces tem",
    "o que tem", "quais produtos", "quais itens", "tudo que tem",
    "lista de produtos", "o que vende", "o que vocês vendem"
]


def eh_pergunta_generica(pergunta):
    """Detecta se o usuário está pedindo a lista completa, não um produto específico."""
    pergunta_lower = pergunta.lower()
    return any(termo in pergunta_lower for termo in PALAVRAS_CATALOGO_COMPLETO)


def filtrar_por_preco(pergunta, produtos, top_k=3):
    """Detecta perguntas sobre preço (mais barato, mais caro, faixa de valor) e filtra/ordena os produtos."""
    pergunta_lower = pergunta.lower()

    if "mais barato" in pergunta_lower or "menor preço" in pergunta_lower or "menor preco" in pergunta_lower:
        ordenado = sorted(produtos, key=lambda p: p["preco"])
        return ordenado[:top_k]

    if "mais caro" in pergunta_lower or "maior preço" in pergunta_lower or "maior preco" in pergunta_lower:
        ordenado = sorted(produtos, key=lambda p: p["preco"], reverse=True)
        return ordenado[:top_k]

    match_ate = re.search(r"(?:até|ate|abaixo de|menos de)\s*r?\$?\s*(\d+)", pergunta_lower)
    if match_ate:
        valor = float(match_ate.group(1))
        filtrados = [p for p in produtos if p["preco"] <= valor]
        return sorted(filtrados, key=lambda p: p["preco"])

    match_acima = re.search(r"(?:acima de|mais de|superior a)\s*r?\$?\s*(\d+)", pergunta_lower)
    if match_acima:
        valor = float(match_acima.group(1))
        filtrados = [p for p in produtos if p["preco"] >= valor]
        return sorted(filtrados, key=lambda p: p["preco"])

    return None  # não é uma pergunta sobre preço


def buscar_produtos_relevantes(pergunta, produtos, top_k=3):
    """Retorna os top_k produtos mais relevantes para a pergunta do usuário."""

    if eh_pergunta_generica(pergunta):
        return produtos

    filtro_preco = filtrar_por_preco(pergunta, produtos, top_k=top_k)
    if filtro_preco is not None:
        return filtro_preco

    textos = [montar_texto_busca(p) for p in produtos]
    textos.append(pergunta)

    vectorizer = TfidfVectorizer()
    matriz = vectorizer.fit_transform(textos)

    similaridades = cosine_similarity(matriz[-1], matriz[:-1])[0]

    indices_ordenados = similaridades.argsort()[::-1][:top_k]

    resultados = []
    for i in indices_ordenados:
        if similaridades[i] > 0:
            resultados.append(produtos[i])

    return resultados


if __name__ == "__main__":
    produtos = carregar_produtos()
    pergunta = "vocês tem calça jeans?"
    encontrados = buscar_produtos_relevantes(pergunta, produtos)

    for p in encontrados:
        print(f"- {p['nome']} | R$ {p['preco']} | Estoque: {p['estoque']}")