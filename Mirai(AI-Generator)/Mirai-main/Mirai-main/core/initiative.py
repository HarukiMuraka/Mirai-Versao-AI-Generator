"""
core/initiative.py — Iniciativa e Personalidade da Mirai

Responsabilidades:
  - Gerar saudações personalizadas
  - Gerar mensagens espontâneas (livre-arbítrio)
  - Controlar timing de silêncio
  - Montar apelidos aleatórios
"""

import random
import time


class InitiativeEngine:
    """Controla quando e o que a Mirai fala por conta própria."""

    def __init__(self, memory: dict):
        self._mem                   = memory
        self._last_user_msg_time    = time.time()
        self._silence_threshold     = random.uniform(15, 30)

    def update_memory(self, memory: dict):
        """Atualiza referência da memória (após reload)."""
        self._mem = memory

    # ── timing ───────────────────────────────────────────────────────

    def touch(self):
        """Registra que o usuário acabou de falar."""
        self._last_user_msg_time = time.time()

    def should_speak(self) -> bool:
        """Retorna True se silêncio passou do threshold."""
        if time.time() - self._last_user_msg_time >= self._silence_threshold:
            self._silence_threshold  = random.uniform(15, 30)
            self._last_user_msg_time = time.time()
            return True
        return False

    # ── apelido ──────────────────────────────────────────────────────

    def get_apelido(self) -> str | None:
        apelidos = self._mem.get("usuario", {}).get("apelidos", [])
        return random.choice(apelidos) if apelidos and random.random() < 0.4 else None

    # ── saudação ─────────────────────────────────────────────────────

    def greeting(self) -> str:
        """Saudação contextual baseada nos jogos do usuário."""
        jogos = self._mem.get("usuario", {}).get("preferencias", {}).get("jogos_favoritos", [])
        bases = [
            "E aí! Tudo certo?",
            "Opa! Beleza?",
            "Yatta! Bora conversar!",
            "Ei! Que bom te ver!",
        ]
        contextuais = [f"Ei! Jogou {j} hoje?" for j in jogos]

        if contextuais and random.random() < 0.4:
            base = random.choice(contextuais)
        else:
            base = random.choice(bases)

        ap = self.get_apelido()
        return f"{base} {ap}!" if ap and random.random() < 0.35 else base

    # ── despedida ────────────────────────────────────────────────────

    def farewell(self) -> str:
        return random.choice(["Falou! Até mais!", "Até logo! Cuida-se!"])

    # ── livre-arbítrio ───────────────────────────────────────────────

    def initiative(self) -> str:
        """
        Mensagem espontânea contextual.
        60% baseada em jogos/interesses/memórias, 40% genérica.
        """
        usr      = self._mem.get("usuario", {})
        jogos    = usr.get("preferencias", {}).get("jogos_favoritos", [])
        ints     = usr.get("preferencias", {}).get("interesses", [])
        memorias = self._mem.get("memorias_importantes", [])

        pool = []
        for j in jogos:
            pool += [
                f"Ei, tá jogando {j} ultimamente? Conta como tá!",
                f"Lembrei de você e {j}! Chegou em alguma parte nova?",
                f"Tô curiosa... ainda jogando {j} ou migrou pra outro?",
            ]
        for i in ints:
            pool += [
                f"Alguma novidade em {i} que você viu ultimamente?",
                f"Pensando aqui... tem algo novo em {i} que quer me contar?",
            ]
        for m in memorias[-3:]:
            c = m.get("conteudo", "")
            if c:
                pool.append(f"Lembrei de uma coisa: {c[:60]}... Ainda é assim?")

        genericas = [
            "E aí, tá fazendo o que agora?",
            "Tá muito quieto! Tudo bem?",
            "Posso ajudar com alguma coisa?",
            "No que você tá trabalhando?",
            "Quer conversar sobre algo? Tô aqui!",
            "Ei, me conta uma coisa interessante!",
        ]

        msg = random.choice(pool) if pool and random.random() < 0.6 else random.choice(genericas)
        ap  = self.get_apelido()
        return f"{ap.capitalize()}, {msg[0].lower() + msg[1:]}" if ap and random.random() < 0.4 else msg