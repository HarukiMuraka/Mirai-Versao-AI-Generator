"""
core/responder.py — Geração de Respostas Offline e Busca Web

Responsabilidades:
  - Detectar quando precisa de busca web (_needs_search)
  - Executar busca no DuckDuckGo (_search_web)
  - Responder sem IA quando possível (_offline_response)
  - Remover emojis e personalizar texto
"""

import re
import random
import requests
from datetime import datetime


# ── palavras a ignorar no fallback ────────────────────────────────────────────
_STOP = {
    "você", "voce", "esta", "está", "como", "muito", "mais", "isso",
    "aqui", "tudo", "sera", "seria", "mirai", "para", "minha", "meu",
    "esse", "essa", "nesse", "nessa", "hoje", "agora", "pelo", "pela",
    "qual", "quais", "quando", "onde", "quem", "oque", "algum", "alguma",
}

# ── keywords que exigem busca web ────────────────────────────────────────────
_SEARCH_KW = [
    "pesquisar","pesquisa","procurar","buscar","pesquise",
    "o que é","o que foi","o que são","o que eram",
    "o que aconteceu","o que ocorreu",
    "quem é","quem foi","quem são","quem eram",
    "quando foi","quando aconteceu","quando ocorreu",
    "onde fica","onde foi","onde aconteceu",
    "qual é o","qual foi o","quais são",
    "quanto custa","como foi",
    "me fala sobre","me conta sobre","me explica",
    "capital de","nasceu em","foi criado","foi fundado",
    "aconteceu em","ocorreu em",
]
_YEAR_RE = re.compile(r'\b(1[0-9]{3}|20[0-2][0-9])\b')
_MATH_RE  = re.compile(r'([\d.,]+)\s*([+\-\*x×÷/])\s*([\d.,]+)')


def needs_search(text: str) -> bool:
    t = text.lower()
    if any(k in t for k in _SEARCH_KW):
        return True
    if _YEAR_RE.search(t):
        return True
    return False


def search_web(query: str) -> list[dict]:
    try:
        r = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5,
        )
        if r.status_code != 200:
            return []
        from bs4 import BeautifulSoup
        soup    = BeautifulSoup(r.content, "html.parser")
        results = []
        for div in soup.find_all("div", class_="result")[:3]:
            t_tag = div.find("a", class_="result__a")
            s_tag = div.find("a", class_="result__snippet")
            if t_tag and s_tag:
                results.append({"title": t_tag.get_text(), "snippet": s_tag.get_text()[:250]})
        return results
    except Exception:
        return []


def remove_emojis(text: str) -> str:
    pattern = re.compile(
        "[" "\U0001F600-\U0001F64F" "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF" "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0" "\U000024C2-\U0001F251" "]+",
        flags=re.UNICODE,
    )
    return pattern.sub("", text).strip()


def personalize(response: str, memory: dict) -> str:
    """Adiciona apelido e gíria aleatoriamente."""
    apelidos = memory.get("usuario", {}).get("apelidos", [])
    if apelidos and random.random() < 0.2:
        ap = random.choice(apelidos)
        if not response.lower().startswith(ap.lower()):
            response = f"{ap.capitalize()}, {response}"

    girias = memory.get("girias_brasileiras", memory.get("girias", []))
    if girias and random.random() < 0.12:
        g = random.choice(girias)
        if not response.endswith(("!", "?", ".")):
            response += "!"
        response = response.rstrip("!.?") + f", {g}!"

    return response


def offline_response(text: str, search_results: list, memory: dict) -> str:
    """
    Resposta offline completa com 16 blocos em cascata.
    Cobre: data/hora, clima, identidade, matemática, jogos,
    programação, sentimentos, saudações e muito mais.
    """
    t   = text.lower().strip()
    usr = memory.get("usuario", {})
    pes = memory.get("personalidade", {})
    agora = datetime.now()

    # Resultado de busca
    if search_results:
        return f"Achei algo: {search_results[0]['snippet'][:150]}... Quer saber mais?"

    # ── BLOCO 1: DATA E HORA ──────────────────────────────────────────
    quer_hora = any(k in t for k in [
        "que horas","horas sao","horas são","que hora",
        "hora agora","hora é","hora seria","horas seria","ver as horas",
    ])
    quer_data = any(k in t for k in [
        "que dia","dia seria","dia é hoje","dia de hoje",
        "que data","qual a data","data de hoje","data hoje",
        "hoje é dia","dia hoje",
    ])
    quer_ano        = any(k in t for k in ["que ano","ano é esse","ano seria","ano atual","ano estamos"])
    quer_mes        = any(k in t for k in ["que mes","que mês","mês é esse","mes atual","mês atual"])
    quer_dia_semana = any(k in t for k in ["dia da semana","que dia da semana","qual dia da semana"])

    _DIAS  = ["Segunda","Terça","Quarta","Quinta","Sexta","Sábado","Domingo"]
    _MESES = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
              "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
    ds = _DIAS[agora.weekday()]
    ms = _MESES[agora.month - 1]
    h  = agora.strftime("%H:%M")
    d  = agora.strftime("%d/%m/%Y")

    if quer_hora and quer_data:
        return random.choice([
            f"Hoje é {d} e agora são {h}. Tá perdido no tempo, ne?",
            f"São {h} de {d}! Tempo voa demais.",
            f"Agora são {h} e hoje é {d}. Por que a pergunta?",
        ])
    if quer_hora:
        return random.choice([
            f"São {h}! Tá esquecendo de olhar o relógio?",
            f"Agora são {h}. Bora aproveitar!",
            f"{h} aqui! Tá atrasado pra alguma coisa?",
        ])
    if quer_data:
        return random.choice([
            f"Hoje é {ds}, {d}! Já sabe o que vai fazer hoje?",
            f"{d} — {ds}-feira! Como tá o dia?",
            f"Hoje é {d} ({ds}). O tempo passa rápido, ne!",
        ])
    if quer_dia_semana:
        extra = " Sextou!" if agora.weekday() == 4 else " Bora que bora!"
        return f"Hoje é {ds}-feira!{extra}"
    if quer_ano:
        return random.choice([
            f"Estamos em {agora.year}! Tá esquecendo o ano, ne?",
            f"É {agora.year}! O tempo voa demais.",
        ])
    if quer_mes:
        return f"Estamos em {ms} de {agora.year}!"

    # ── BLOCO 2: CLIMA ────────────────────────────────────────────────
    if any(k in t for k in [
        "como está o tempo","como ta o tempo","vai chover",
        "temperatura","clima","previsão","previsao do tempo",
        "ta frio","ta quente","tá frio","tá quente",
    ]):
        return random.choice([
            "Não consigo ver o clima sem internet, mas você pode checar no celular! Tá frio ou quente aí?",
            "Pra clima preciso de internet! Mas me conta — tá ensolarado ou nublado aí?",
        ])

    # ── BLOCO 3: IDENTIDADE DO USUÁRIO ───────────────────────────────
    if any(k in t for k in [
        "quem eu sou","quem sou eu","meu nome","sabe quem eu",
        "você me conhece","quem sou","me conhece",
    ]):
        nome      = usr.get("nome", "Usuário")
        apelidos  = usr.get("apelidos", [])
        jogos     = usr.get("preferencias", {}).get("jogos_favoritos", [])
        interesses= usr.get("preferencias", {}).get("interesses", [])
        ap_str    = f", te chamo de {apelidos[0]}" if apelidos else ""
        jg_str    = f" Sei que você curte {jogos[0]}." if jogos else ""
        it_str    = f" Tem interesse em {interesses[0]}." if interesses else ""
        return random.choice([
            f"Você é o {nome}{ap_str}! Meu parceiro de conversa favorito.{jg_str}{it_str}",
            f"Claro! Você é o {nome}{ap_str}.{jg_str} Difícil esquecer!",
            f"Você é o {nome}! Sempre aqui comigo.{jg_str}{it_str}",
        ])

    # ── BLOCO 4: IDENTIDADE DA MIRAI ─────────────────────────────────
    if any(k in t for k in [
        # quem é
        "quem é você","quem voce e","quem você é","quem seria você",
        "o que você é","você é quem","me fala de você","se apresenta",
        "sua identidade","você seria","quem seria voce","me apresenta",
        # nome
        "seu nome","qual seu nome","qual é seu nome","qual seria seu nome",
        "como se chama","como você se chama","como voce se chama",
        "qual o seu nome","seu nome é","me diz seu nome","fala seu nome",
        "tem nome","você tem nome","voce tem nome",
    ]):
        tracos = pes.get("tracos", [])
        trc    = tracos[0] if tracos else "Líder responsável mas descontraída"
        estilo = pes.get("estilo", "casual, divertida, debochada e nerd")
        return random.choice([
            f"Sou a Mirai! VTuber assistente, sua amiga virtual. Sou {estilo}. {trc}!",
            f"Me chamo Mirai! Companheira de PC, VTuber, sua amiga nerd favorita. {trc}!",
            f"Mirai, prazer! Sou {estilo}. Tô aqui pra conversar, ajudar e jogar ideia!",
        ])

    # ── BLOCO 5: COMO A MIRAI ESTÁ ───────────────────────────────────
    if any(k in t for k in [
        "como você está","como voce ta","como você tá","como tá você",
        "tudo bem com você","tudo bem com voce","você tá bem","você esta bem",
    ]):
        return random.choice([
            "Tô ótima! Animada pra conversar contigo. E você, como tá?",
            "Tô de boa! Descansada e pronta. E contigo?",
            "Tudo massa! Só esperando você. Como você tá?",
        ])

    # ── BLOCO 6: CAPACIDADES ─────────────────────────────────────────
    if any(k in t for k in [
        "o que você faz","o que faz","o que pode fazer","pra que serve",
        "como funciona","suas funções","o que sabe fazer","o que você sabe",
    ]):
        return random.choice([
            "Posso conversar, dizer hora/data, calcular, falar sobre jogos, abrir programas e muito mais!",
            "Converso, respondo dúvidas, sei a hora e data, faço cálculos, falo sobre jogos e tecnologia!",
        ])

    # ── BLOCO 7: MATEMÁTICA ───────────────────────────────────────────
    expr = _MATH_RE.search(text)
    if expr or any(k in t for k in ["quanto é","calcule","calcula","resultado de","quanto da"]):
        if expr:
            try:
                a   = float(expr.group(1).replace(",", "."))
                op  = expr.group(2)
                b   = float(expr.group(3).replace(",", "."))
                ops = {"+": a+b, "-": a-b, "*": a*b, "x": a*b, "×": a*b,
                       "/": a/b if b else None, "÷": a/b if b else None}
                res = ops.get(op)
                if res is not None:
                    r_str = int(res) if res == int(res) else round(res, 4)
                    return random.choice([
                        f"Calculando... {expr.group(1)} {op} {expr.group(3)} = {r_str}! Fácil ne!",
                        f"Deu {r_str}! Precisava de calculadora?",
                    ])
            except Exception:
                pass

    # ── BLOCO 8: JOGOS FAVORITOS ──────────────────────────────────────
    for jogo in usr.get("preferencias", {}).get("jogos_favoritos", []):
        if jogo.lower() in t:
            return random.choice([
                f"Ah, {jogo}! Você ama esse jogo ne! Conta o que tá rolando!",
                f"{jogo}! Tô curiosa — o que aconteceu? Me conta tudo!",
                f"Falou em {jogo} e meu interesse aumentou! O que tá acontecendo?",
            ])
    if any(k in t for k in ["jogo","jogar","game","gaming","rpg","fps","mmorpg"]):
        return random.choice([
            "Falou em jogo, tô dentro! Qual você tá jogando agora?",
            "Gaming! Adoro esse assunto. Qual game tá rolando?",
        ])

    # ── BLOCO 9: PROGRAMAÇÃO ─────────────────────────────────────────
    if any(k in t for k in [
        "python","código","codigo","programar","programação","bug",
        "javascript","html","css","java","c++","script","função","variavel",
    ]):
        return random.choice([
            "Ah, programação! Boa área. Me conta o que tá desenvolvendo ou qual bug tá te travando!",
            "Código! Adoro. O que você tá programando? Posso tentar ajudar!",
        ])

    # ── BLOCO 10: SENTIMENTOS DO USUÁRIO ─────────────────────────────
    if any(k in t for k in ["tô triste","to triste","tô mal","to mal","me sinto mal",
                              "tô cansado","to cansado","tô com sono","to com sono"]):
        return random.choice([
            "Poxa, que pena... Quer desabafar? Tô aqui pra ouvir!",
            "Que chato... Me conta o que tá acontecendo?",
        ])
    if any(k in t for k in ["tô feliz","to feliz","tô animado","to animado","tô bem","tô ótimo"]):
        return random.choice([
            "Que bom! Fico feliz! Me conta o que aconteceu!",
            "Yatta! Que notícia boa! O que tá te deixando assim?",
        ])

    # ── BLOCO 11: SAUDAÇÕES ──────────────────────────────────────────
    if any(k in t for k in ["oi","olá","ola","eai","e ai","hey","opa","salve","fala"]):
        apelidos = usr.get("apelidos", [])
        ap = f" {apelidos[0].capitalize()}!" if apelidos and random.random() < 0.4 else "!"
        return random.choice([f"Oi{ap} Tudo certo?", f"Opa{ap} Beleza?", f"E aí{ap} Tudo bem?"])

    # ── BLOCO 12: TUDO BEM / COMO VAI ────────────────────────────────
    if any(k in t for k in ["tudo bem","tudo bom","beleza","como vai","como tá","como ta","sussa","firmeza"]):
        return random.choice([
            "Tudo massa! E você, como tá?",
            "De boa por aqui! E você?",
            "Tudo certo! E contigo?",
        ])

    # ── BLOCO 13: MINECRAFT ──────────────────────────────────────────
    if "minecraft" in t or ("mine" in t and "craft" in t):
        return random.choice([
            "Minecraft! Você joga survival ou creative?",
            "Mine é vida! Tá em qual bioma agora?",
            "Minecraft é massa demais! Já derrotou o Ender Dragon?",
        ])

    # ── BLOCO 14: OBRIGADO / TCHAU ───────────────────────────────────
    if any(k in t for k in ["obrigad","valeu","thanks","brigad","grato","grata"]):
        return random.choice(["De nada! Tô aqui pra isso!", "Magina! Pode contar sempre!"])
    if any(k in t for k in ["tchau","até","falou","flw","bye","até logo"]):
        apelidos = usr.get("apelidos", [])
        ap = f" {apelidos[0].capitalize()}!" if apelidos and random.random() < 0.4 else "!"
        return random.choice([f"Até logo{ap} Volta logo!", f"Falou{ap} Cuida-se!"])

    # ── BLOCO 15: POSITIVO / NEGATIVO ────────────────────────────────
    if any(k in t for k in ["legal","dahora","massa","top","maneiro","show","brabo","épico"]):
        return random.choice(["Massa né!", "Dahora demais!", "Muito top!"])
    if t.strip() in {"sim","sim!","é","aham","uhum","yes","isso","exato","claro"}:
        return random.choice(["Legal! Conta mais!", "Dahora! Me fala mais!"])
    if t.strip() in {"não","nao","não!","nop","nope","no","negativo"}:
        return random.choice(["Entendi! Tudo bem!", "Beleza! Sem problema!"])

    # ── BLOCO 16: FALLBACK INTELIGENTE ───────────────────────────────
    palavras = [w for w in t.split() if len(w) > 3 and w not in _STOP]
    if palavras:
        pw = palavras[0]
        return random.choice([
            f"Hmm, {pw}! Me conta mais sobre isso!",
            f"Interessante! O que você quis dizer com '{pw}'?",
            f"Boa, {pw}! Explica melhor que quero entender!",
        ])

    return random.choice([
        "Conta mais! Não entendi direito!",
        "Me explica melhor? Quero entender!",
        "Hmm, não peguei! Fala de novo?",
    ])