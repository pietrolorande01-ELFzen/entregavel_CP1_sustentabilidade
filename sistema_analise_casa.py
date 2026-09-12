#   ============================================================
#   SISTEMA DE DIMENSIONAMENTO ENERGÉTICO RESIDENCIAL
#   Implementação completa do backlog PB01 a PB18
#   ============================================================
#
#   PB01 — Cadastro de Usuário            [ALTA]
#   PB02 — Login / acesso à conta         [ALTA]
#   PB03 — Cadastro de imóvel             [ALTA]
#   PB04 — Editar/excluir imóvel          [MÉDIA]
#   PB05 — Cadastro de equipamento        [ALTA]
#   PB06 — Editar/excluir equipamento     [MÉDIA]
#   PB07 — Catálogo pré-cadastrado        [BAIXA]
#   PB08 — Associação imóvel-equipamento  [ALTA]
#   PB09 — Quantidade e tempo de uso      [ALTA]
#   PB10 — Editar/remover associação      [MÉDIA]
#   PB11 — Cálculo consumo mensal/equip.  [ALTA]
#   PB12 — Consumo total mensal do imóvel [ALTA]
#   PB13 — Ranking de consumo             [MÉDIA]
#   PB14 — Resumo do consumo do imóvel    [ALTA]
#   PB15 — Gráfico de distribuição        [BAIXA]
#   PB16 — Validação de dados inconsistentes [ALTA]
#   PB17 — Persistência entre sessões     [ALTA]
#   PB18 — Privacidade e segurança        [ALTA]
#
#   ============================================================

import os
import re
import json
import hashlib

ARQUIVO_DADOS = "dados_sistema.json"

# ------------------------------------------------------------------
# PB17 — Estrutura de dados persistida em arquivo (T01, T02, T03)
# ------------------------------------------------------------------
# Tudo o que precisa sobreviver ao fechamento do programa mora aqui
# dentro e é gravado em disco a cada alteração relevante.

dados = {
    "usuarios": {},        # email -> {nome, telefone, senha_hash}
    "imoveis": {},         # id(str) -> {endereco, numero, apelido, tipo, dono_email}
    "equipamentos": {},    # id(str) -> {nome, categoria, potencia, pre_cadastrado}
    "associacoes": {},     # id(str) -> {imovel_id, equipamento_id, quantidade, tempo_uso}
    "next_ids": {"imovel": 1, "equipamento": 1, "associacao": 1},
}

# Sessão do usuário autenticado (PB02-T05)
sessao = {"email_logado": None}


def salvar_dados():
    """PB17-T01/T02 — grava todo o estado atual no arquivo JSON."""
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def carregar_dados():
    """PB17-T03 — recarrega o estado salvo ao reabrir o sistema."""
    global dados
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
            carregado = json.load(f)
            dados.update(carregado)
    else:
        popular_catalogo_inicial()
        salvar_dados()


def limpar_terminal():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def pausar():
    input("\nPressione ENTER para continuar...")


# ------------------------------------------------------------------
# PB16 — Validações centralizadas (T01, T02, T03, T04)
# ------------------------------------------------------------------

def validar_nao_vazio(valor):
    return valor.strip() != ""


def validar_email_formato(email):
    """PB01-T05 — valida formato básico de e-mail."""
    padrao = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(padrao, email) is not None


def validar_numero_positivo(texto):
    """PB16-T02 — rejeita valores negativos, zero ou não numéricos."""
    try:
        valor = float(texto)
        return valor > 0
    except ValueError:
        return False


def validar_inteiro_positivo(texto):
    """PB09-T04 — quantidade deve ser inteiro positivo."""
    try:
        valor = int(texto)
        return valor > 0
    except ValueError:
        return False


def validar_intervalo_horas(texto):
    """PB09-T05 — tempo de uso deve estar entre 0 e 24h, numérico."""
    try:
        valor = float(texto)
        return 0 <= valor <= 24
    except ValueError:
        return False


# ------------------------------------------------------------------
# PB01 — Cadastro de usuário
# ------------------------------------------------------------------

def cadastro_user():
    print(" ==== CADASTRO DE CONTAS ==== \n")
    print("VAMOS PEDIR O PREENCHIMENTO DE ALGUMAS INFORMAÇÕES PARA O NOSSO CADASTRO...")

    while True:
        nome_user = input("POR FAVOR DIGITE SEU NOME...: ").strip()
        if validar_nao_vazio(nome_user):
            break
        print("ERRO: O campo NOME não pode ficar vazio!")

    while True:
        email = input("\nPOR FAVOR DIGITE O SEU EMAIL...: ").strip()

        if not validar_nao_vazio(email):
            print("ERRO: O campo email não pode ficar vazio!")
            continue

        if not validar_email_formato(email):
            print("ERRO: Formato de e-mail inválido (ex: nome@dominio.com)!")
            continue

        if email in dados["usuarios"]:
            print("ERRO: Este email já está cadastrado! Por favor, faça login.")
            continue

        break

    while True:
        telefone_input = input("\nPOR FAVOR DIGITE SEU NUMERO DE TELEFONE (Apenas números)...: ").strip()

        if not validar_nao_vazio(telefone_input):
            print("ERRO: O campo TELEFONE não pode ficar vazio!")
            continue

        if not telefone_input.isdigit():
            print("ERRO: Digite apenas números no telefone (sem letras ou espaços)!")
            continue

        numero_telefone = telefone_input
        break

    while True:
        senha = input("\nCRIE UMA SENHA PARA SUA CONTA...: ").strip()
        if validar_nao_vazio(senha):
            break
        print("ERRO: A senha não pode ficar vazia!")

    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    dados["usuarios"][email] = {
        "nome": nome_user,
        "telefone": numero_telefone,
        "senha_hash": senha_hash,
    }
    salvar_dados()

    print("\n==== CADASTRO CONCLUÍDO COM SUCESSO ==== ")
    pausar()
    limpar_terminal()


# ------------------------------------------------------------------
# PB02 — Login / acesso à conta (com sessão — T05)
# ------------------------------------------------------------------

def login():
    print()
    print("==== TELA DE LOGIN ====")

    while True:
        email_cadastrado = input("\nPOR FAVOR DIGITE SEU EMAIL CADASTRADO...: ").strip()

        if not validar_nao_vazio(email_cadastrado):
            print("\nERRO: O campo acima não deve ficar vazio")
            continue

        if email_cadastrado in dados["usuarios"]:
            break
        else:
            print("EMAIL NÃO CADASTRADO/ENCONTRADO...")
            print("POR FAVOR, SIGA PARA A PÁGINA DE CADASTRO")
            return False

    usuario = dados["usuarios"][email_cadastrado]
    senha_correta = usuario["senha_hash"]
    nome_usuario = usuario["nome"]

    while True:
        senha_login = input(
            f"\nBEM VINDO DE VOLTA {nome_usuario} | PARA ACESSAR A SUA CONTA DIGITE A SENHA CORRETAMENTE...: "
        ).strip()

        if not validar_nao_vazio(senha_login):
            print("\nERRO: Este Campo não pode se encontrar vazio")
            continue

        if hashlib.sha256(senha_login.encode()).hexdigest() == senha_correta:
            print("==== LOG IN EFETUADO COM SUCESSO ====")
            sessao["email_logado"] = email_cadastrado  # PB02-T05: sessão ativa
            break
        else:
            print("ERRO: Senha incorreta! Tente novamente.")

    pausar()
    limpar_terminal()
    return True


def logout():
    sessao["email_logado"] = None


# ------------------------------------------------------------------
# PB18 — Privacidade: helpers de propriedade (T01, T02, T03)
# ------------------------------------------------------------------

def imoveis_do_usuario_logado():
    """Retorna apenas os imóveis pertencentes ao usuário autenticado."""
    email = sessao["email_logado"]
    return {
        id_imovel: dado
        for id_imovel, dado in dados["imoveis"].items()
        if dado["dono_email"] == email
    }


def imovel_pertence_ao_usuario(id_imovel):
    """PB18-T01/T02/T03 — bloqueia acesso a imóvel de outro usuário."""
    imovel = dados["imoveis"].get(id_imovel)
    if imovel is None:
        return False
    return imovel["dono_email"] == sessao["email_logado"]


def selecionar_imovel_do_usuario(mensagem="Escolha o imóvel pelo número...: "):
    """Lista só os imóveis do usuário logado e retorna o ID escolhido, ou None."""
    meus_imoveis = imoveis_do_usuario_logado()

    if not meus_imoveis:
        print("\nVOCÊ AINDA NÃO TEM NENHUM IMÓVEL CADASTRADO.")
        return None

    print("\n==== SEUS IMÓVEIS ====")
    for id_imovel, dado in meus_imoveis.items():
        print(f"{id_imovel}. {dado['apelido']} — {dado['endereco']}, {dado['numero']} ({dado['tipo']})")

    while True:
        escolha = input(f"\n{mensagem}").strip()
        if escolha in meus_imoveis:
            return escolha
        print("ERRO: Número inválido ou este imóvel não pertence a você.")


# ------------------------------------------------------------------
# PB03 — Cadastro de imóvel (associado ao usuário logado — T06)
# ------------------------------------------------------------------

def cadastro_imovel():
    print("==== CADASTRO DE IMÓVEIS ====\n")
    print("VAMOS PRECISAR DE ALGUMAS INFORMAÇÕES DO IMÓVEL PARA CONTINUAR")
    print()

    while True:
        endereco_imovel = input("\nPOR FAVOR INSIRA O ENDEREÇO DO IMÓVEL...: ").strip()
        if validar_nao_vazio(endereco_imovel):
            break
        print("\nERRO: Campo vazio, por favor preencha com os dados certos")

    while True:
        numero_imovel = input("\nPOR FAVOR DIGITE O NUMERO DA RESIDENCIA...: ").strip()
        if validar_nao_vazio(numero_imovel):
            break
        print("\nERRO: Campo vazio, por favor preencha com os dados certos")

    while True:
        apelido_residencia = input("\nPOR FAVOR DIGITE UM APELIDO PARA A RESIDENCIA...: ").strip()
        if validar_nao_vazio(apelido_residencia):
            break
        print("\nERRO: Campo vazio, por favor preencha com os dados certos")

    while True:
        print("\nQUAL O TIPO DO IMÓVEL...?")
        print("1. Casa")
        print("2. Apartamento")
        print("3. Outro")
        tipo_opcao = input("\nESCOLHA UMA OPÇÃO...: ").strip()
        tipos = {"1": "Casa", "2": "Apartamento", "3": "Outro"}
        if tipo_opcao in tipos:
            tipo_imovel = tipos[tipo_opcao]
            break
        print("ERRO: Escolha 1, 2 ou 3.")

    # PB03-T06: associado diretamente ao usuário da sessão, sem pedir email de novo
    novo_id = str(dados["next_ids"]["imovel"])
    dados["imoveis"][novo_id] = {
        "endereco": endereco_imovel,
        "numero": numero_imovel,
        "apelido": apelido_residencia,
        "tipo": tipo_imovel,
        "dono_email": sessao["email_logado"],
    }
    dados["next_ids"]["imovel"] += 1
    salvar_dados()

    print("\n==== RESIDÊNCIA CADASTRADA COM SUCESSO ====")
    pausar()
    limpar_terminal()


# ------------------------------------------------------------------
# PB04 — Editar/excluir imóvel
# ------------------------------------------------------------------

def modificar_imovel():
    print("==== MODIFICAÇÃO DE IMÓVEL ====\n")

    id_imovel = selecionar_imovel_do_usuario()
    if id_imovel is None:
        pausar()
        limpar_terminal()
        return

    imovel = dados["imoveis"][id_imovel]

    print("\n==== IMÓVEL ENCONTRADO ====")
    print(f"Endereço: {imovel['endereco']}")
    print(f"Número:   {imovel['numero']}")
    print(f"Apelido:  {imovel['apelido']}")
    print(f"Tipo:     {imovel['tipo']}")
    print("===========================\n")

    while True:
        print("GOSTARIA DE ALTERAR QUAL DADO...?")
        print("1. ENDEREÇO")
        print("2. NUMERO")
        print("3. APELIDO")
        print("4. TIPO")
        resposta = input("\nESCOLHA UMA OPÇÃO...: ").strip()
        if resposta in {"1", "2", "3", "4"}:
            break
        print("\nERRO: Escolha 1, 2, 3 ou 4...")

    if resposta == "1":
        while True:
            novo_valor = input(f"\nATUAL: {imovel['endereco']}\nNOVO ENDEREÇO...: ").strip()
            if validar_nao_vazio(novo_valor):
                imovel["endereco"] = novo_valor
                break
            print("\nERRO: Campo não pode ficar vazio...")

    elif resposta == "2":
        while True:
            novo_valor = input(f"\nATUAL: {imovel['numero']}\nNOVO NÚMERO...: ").strip()
            if validar_nao_vazio(novo_valor):
                imovel["numero"] = novo_valor
                break
            print("\nERRO: Campo não pode ficar vazio...")

    elif resposta == "3":
        while True:
            novo_valor = input(f"\nATUAL: {imovel['apelido']}\nNOVO APELIDO...: ").strip()
            if validar_nao_vazio(novo_valor):
                imovel["apelido"] = novo_valor
                break
            print("\nERRO: Campo não pode ficar vazio...")

    elif resposta == "4":
        tipos = {"1": "Casa", "2": "Apartamento", "3": "Outro"}
        while True:
            print(f"\nATUAL: {imovel['tipo']}")
            print("1. Casa  2. Apartamento  3. Outro")
            novo_valor = input("NOVO TIPO...: ").strip()
            if novo_valor in tipos:
                imovel["tipo"] = tipos[novo_valor]
                break
            print("\nERRO: Escolha 1, 2 ou 3...")

    salvar_dados()
    print("\nDADO ATUALIZADO COM SUCESSO...")
    pausar()
    limpar_terminal()


def excluir_imovel():
    """PB04-T04/T05 — exclusão com confirmação, remove associações filhas."""
    print("==== EXCLUSÃO DE IMÓVEL ====\n")

    id_imovel = selecionar_imovel_do_usuario()
    if id_imovel is None:
        pausar()
        limpar_terminal()
        return

    imovel = dados["imoveis"][id_imovel]

    confirmacao = input(
        f"\nTEM CERTEZA QUE DESEJA EXCLUIR '{imovel['apelido']}'? Esta ação também remove "
        f"os equipamentos associados a ele. Digite SIM para confirmar...: "
    ).strip().upper()

    if confirmacao != "SIM":
        print("\nEXCLUSÃO CANCELADA.")
        pausar()
        limpar_terminal()
        return

    # remove associações ligadas a este imóvel
    ids_associacoes_remover = [
        id_assoc for id_assoc, assoc in dados["associacoes"].items()
        if assoc["imovel_id"] == id_imovel
    ]
    for id_assoc in ids_associacoes_remover:
        del dados["associacoes"][id_assoc]

    del dados["imoveis"][id_imovel]
    salvar_dados()

    print("\n==== IMÓVEL EXCLUÍDO COM SUCESSO ====")
    pausar()
    limpar_terminal()


# ------------------------------------------------------------------
# PB07 — Catálogo pré-cadastrado de equipamentos
# ------------------------------------------------------------------

CATALOGO_INICIAL = [
    ("Geladeira", "Cozinha", 133),
    ("Chuveiro elétrico", "Banheiro", 5500),
    ("Televisão", "Sala", 100),
    ("Ar-condicionado", "Quarto", 1200),
    ("Micro-ondas", "Cozinha", 1200),
    ("Ferro de passar", "Lavanderia", 1000),
    ("Máquina de lavar roupa", "Lavanderia", 500),
    ("Computador desktop", "Escritório", 200),
    ("Notebook", "Escritório", 65),
    ("Lâmpada LED", "Geral", 10),
]


def popular_catalogo_inicial():
    """PB07-T02/T03 — cria o catálogo base na primeira execução."""
    for nome, categoria, potencia in CATALOGO_INICIAL:
        novo_id = str(dados["next_ids"]["equipamento"])
        dados["equipamentos"][novo_id] = {
            "nome": nome,
            "categoria": categoria,
            "potencia": potencia,
            "pre_cadastrado": True,
        }
        dados["next_ids"]["equipamento"] += 1


# ------------------------------------------------------------------
# PB05 — Cadastro de equipamento (com opção de partir do catálogo)
# ------------------------------------------------------------------

def cadastro_equipamento():
    print("==== CADASTRO DE EQUIPAMENTO ====\n")
    print("Você pode escolher um item do catálogo (e editar os dados) ou cadastrar um novo.\n")

    catalogo = [
        (id_eq, eq) for id_eq, eq in dados["equipamentos"].items() if eq.get("pre_cadastrado")
    ]

    if catalogo:
        print("==== CATÁLOGO PRÉ-CADASTRADO ====")
        for id_eq, eq in catalogo:
            print(f"{id_eq}. {eq['nome']} ({eq['categoria']}) — {eq['potencia']}W")
        print("0. Cadastrar um equipamento novo do zero")

        while True:
            escolha = input("\nESCOLHA UM NÚMERO...: ").strip()
            if escolha == "0" or escolha in dict(catalogo):
                break
            print("ERRO: Opção inválida.")
    else:
        escolha = "0"

    if escolha != "0":
        eq_base = dados["equipamentos"][escolha]
        nome_padrao, categoria_padrao, potencia_padrao = (
            eq_base["nome"], eq_base["categoria"], eq_base["potencia"]
        )
    else:
        nome_padrao, categoria_padrao, potencia_padrao = "", "", ""

    while True:
        prompt = f"\nNOME DO EQUIPAMENTO [{nome_padrao}] (ENTER para manter)...: " if nome_padrao else "\nNOME DO EQUIPAMENTO...: "
        nome = input(prompt).strip()
        if nome == "" and nome_padrao:
            nome = nome_padrao
        if validar_nao_vazio(nome):
            break
        print("ERRO: O nome não pode ficar vazio!")

    while True:
        prompt = f"\nCATEGORIA [{categoria_padrao}] (ENTER para manter)...: " if categoria_padrao else "\nCATEGORIA...: "
        categoria = input(prompt).strip()
        if categoria == "" and categoria_padrao:
            categoria = categoria_padrao
        if validar_nao_vazio(categoria):
            break
        print("ERRO: A categoria não pode ficar vazia!")

    while True:
        prompt = (
            f"\nPOTÊNCIA EM WATTS [{potencia_padrao}] (ENTER para manter)...: "
            if potencia_padrao != "" else "\nPOTÊNCIA EM WATTS...: "
        )
        potencia_texto = input(prompt).strip()
        if potencia_texto == "" and potencia_padrao != "":
            potencia = float(potencia_padrao)
            break
        # PB05-T05: rejeitar potência <= 0
        if validar_numero_positivo(potencia_texto):
            potencia = float(potencia_texto)
            break
        print("ERRO: Digite um número maior que zero para a potência.")

    novo_id = str(dados["next_ids"]["equipamento"])
    dados["equipamentos"][novo_id] = {
        "nome": nome,
        "categoria": categoria,
        "potencia": potencia,
        "pre_cadastrado": False,
    }
    dados["next_ids"]["equipamento"] += 1
    salvar_dados()

    print("\n==== EQUIPAMENTO CADASTRADO COM SUCESSO ====")
    pausar()
    limpar_terminal()


def listar_equipamentos():
    if not dados["equipamentos"]:
        print("\nNENHUM EQUIPAMENTO CADASTRADO AINDA.")
        return
    print("\n==== EQUIPAMENTOS CADASTRADOS ====")
    for id_eq, eq in dados["equipamentos"].items():
        origem = "(catálogo)" if eq.get("pre_cadastrado") else ""
        print(f"{id_eq}. {eq['nome']} — {eq['categoria']} — {eq['potencia']}W {origem}")


def selecionar_equipamento(mensagem="Escolha o equipamento pelo número...: "):
    listar_equipamentos()
    if not dados["equipamentos"]:
        return None

    while True:
        escolha = input(f"\n{mensagem}").strip()
        if escolha in dados["equipamentos"]:
            return escolha
        print("ERRO: Número inválido.")


# ------------------------------------------------------------------
# PB06 — Editar/excluir equipamento
# ------------------------------------------------------------------

def modificar_equipamento():
    print("==== MODIFICAÇÃO DE EQUIPAMENTO ====\n")

    id_eq = selecionar_equipamento()
    if id_eq is None:
        pausar()
        limpar_terminal()
        return

    eq = dados["equipamentos"][id_eq]

    while True:
        print(f"\nATUAL: {eq['nome']} — {eq['categoria']} — {eq['potencia']}W")
        print("1. Nome  2. Categoria  3. Potência")
        resposta = input("\nESCOLHA UMA OPÇÃO...: ").strip()
        if resposta in {"1", "2", "3"}:
            break
        print("ERRO: Escolha 1, 2 ou 3.")

    if resposta == "1":
        while True:
            novo = input("\nNOVO NOME...: ").strip()
            if validar_nao_vazio(novo):
                eq["nome"] = novo
                break
            print("ERRO: Campo não pode ficar vazio.")

    elif resposta == "2":
        while True:
            novo = input("\nNOVA CATEGORIA...: ").strip()
            if validar_nao_vazio(novo):
                eq["categoria"] = novo
                break
            print("ERRO: Campo não pode ficar vazio.")

    elif resposta == "3":
        while True:
            novo = input("\nNOVA POTÊNCIA (W)...: ").strip()
            if validar_numero_positivo(novo):
                eq["potencia"] = float(novo)
                break
            print("ERRO: Digite um número maior que zero.")

    salvar_dados()
    print("\nEQUIPAMENTO ATUALIZADO COM SUCESSO...")
    pausar()
    limpar_terminal()


def excluir_equipamento():
    """PB06-T04/T05 — avisa se o equipamento está em uso antes de excluir."""
    print("==== EXCLUSÃO DE EQUIPAMENTO ====\n")

    id_eq = selecionar_equipamento()
    if id_eq is None:
        pausar()
        limpar_terminal()
        return

    associacoes_usando = [
        assoc for assoc in dados["associacoes"].values() if assoc["equipamento_id"] == id_eq
    ]

    if associacoes_usando:
        print(f"\nAVISO: Este equipamento está associado a {len(associacoes_usando)} imóvel(is).")
        confirmacao = input(
            "Excluir mesmo assim vai remover essas associações. Digite SIM para confirmar...: "
        ).strip().upper()
        if confirmacao != "SIM":
            print("\nEXCLUSÃO CANCELADA.")
            pausar()
            limpar_terminal()
            return

        ids_remover = [
            id_assoc for id_assoc, assoc in dados["associacoes"].items()
            if assoc["equipamento_id"] == id_eq
        ]
        for id_assoc in ids_remover:
            del dados["associacoes"][id_assoc]

    del dados["equipamentos"][id_eq]
    salvar_dados()

    print("\n==== EQUIPAMENTO EXCLUÍDO COM SUCESSO ====")
    pausar()
    limpar_terminal()


# ------------------------------------------------------------------
# PB08 / PB09 — Associação imóvel-equipamento + quantidade/tempo de uso
# ------------------------------------------------------------------

def associar_equipamento():
    print("==== ASSOCIAR EQUIPAMENTO A UM IMÓVEL ====\n")

    id_imovel = selecionar_imovel_do_usuario()
    if id_imovel is None:
        pausar()
        limpar_terminal()
        return

    id_eq = selecionar_equipamento()
    if id_eq is None:
        pausar()
        limpar_terminal()
        return

    while True:
        qtd_texto = input("\nQUANTIDADE deste equipamento no imóvel...: ").strip()
        if validar_inteiro_positivo(qtd_texto):
            quantidade = int(qtd_texto)
            break
        print("ERRO: Digite um número inteiro maior que zero.")

    while True:
        tempo_texto = input("\nTEMPO DE USO DIÁRIO em horas (0 a 24)...: ").strip()
        if validar_intervalo_horas(tempo_texto):
            tempo_uso = float(tempo_texto)
            break
        print("ERRO: Digite um valor numérico entre 0 e 24.")

    novo_id = str(dados["next_ids"]["associacao"])
    dados["associacoes"][novo_id] = {
        "imovel_id": id_imovel,
        "equipamento_id": id_eq,
        "quantidade": quantidade,
        "tempo_uso": tempo_uso,
    }
    dados["next_ids"]["associacao"] += 1
    salvar_dados()

    print("\n==== EQUIPAMENTO ASSOCIADO COM SUCESSO ====")
    pausar()
    limpar_terminal()


def listar_associacoes_do_imovel(id_imovel):
    return {
        id_assoc: assoc for id_assoc, assoc in dados["associacoes"].items()
        if assoc["imovel_id"] == id_imovel
    }


def selecionar_associacao_do_imovel(id_imovel):
    associacoes = listar_associacoes_do_imovel(id_imovel)
    if not associacoes:
        print("\nNENHUM EQUIPAMENTO ASSOCIADO A ESTE IMÓVEL AINDA.")
        return None

    print("\n==== EQUIPAMENTOS ASSOCIADOS ====")
    for id_assoc, assoc in associacoes.items():
        eq = dados["equipamentos"][assoc["equipamento_id"]]
        print(
            f"{id_assoc}. {eq['nome']} — qtd: {assoc['quantidade']} — "
            f"{assoc['tempo_uso']}h/dia"
        )

    while True:
        escolha = input("\nESCOLHA O NÚMERO DA ASSOCIAÇÃO...: ").strip()
        if escolha in associacoes:
            return escolha
        print("ERRO: Número inválido.")


# ------------------------------------------------------------------
# PB10 — Editar/remover associação imóvel-equipamento
# ------------------------------------------------------------------

def editar_associacao():
    print("==== EDITAR ASSOCIAÇÃO ====\n")

    id_imovel = selecionar_imovel_do_usuario()
    if id_imovel is None:
        pausar()
        limpar_terminal()
        return

    id_assoc = selecionar_associacao_do_imovel(id_imovel)
    if id_assoc is None:
        pausar()
        limpar_terminal()
        return

    assoc = dados["associacoes"][id_assoc]

    while True:
        print(f"\nATUAL — quantidade: {assoc['quantidade']}, tempo de uso: {assoc['tempo_uso']}h/dia")
        print("1. Quantidade  2. Tempo de uso")
        resposta = input("\nESCOLHA UMA OPÇÃO...: ").strip()
        if resposta in {"1", "2"}:
            break
        print("ERRO: Escolha 1 ou 2.")

    if resposta == "1":
        while True:
            novo = input("\nNOVA QUANTIDADE...: ").strip()
            if validar_inteiro_positivo(novo):
                assoc["quantidade"] = int(novo)
                break
            print("ERRO: Digite um número inteiro maior que zero.")
    else:
        while True:
            novo = input("\nNOVO TEMPO DE USO (0 a 24h)...: ").strip()
            if validar_intervalo_horas(novo):
                assoc["tempo_uso"] = float(novo)
                break
            print("ERRO: Digite um valor entre 0 e 24.")

    salvar_dados()
    print("\nASSOCIAÇÃO ATUALIZADA COM SUCESSO...")
    pausar()
    limpar_terminal()


def remover_associacao():
    print("==== REMOVER EQUIPAMENTO DO IMÓVEL ====\n")

    id_imovel = selecionar_imovel_do_usuario()
    if id_imovel is None:
        pausar()
        limpar_terminal()
        return

    id_assoc = selecionar_associacao_do_imovel(id_imovel)
    if id_assoc is None:
        pausar()
        limpar_terminal()
        return

    confirmacao = input("\nCONFIRMA A REMOÇÃO? Digite SIM para confirmar...: ").strip().upper()
    if confirmacao != "SIM":
        print("\nREMOÇÃO CANCELADA.")
        pausar()
        limpar_terminal()
        return

    del dados["associacoes"][id_assoc]
    salvar_dados()

    print("\n==== ASSOCIAÇÃO REMOVIDA COM SUCESSO ====")
    pausar()
    limpar_terminal()


# ------------------------------------------------------------------
# PB11 — Cálculo do consumo mensal por equipamento
# ------------------------------------------------------------------

def calcular_consumo_associacao(assoc):
    """
    PB11-T02/T03 — fórmula do MVP:
    consumo = potência (W) x quantidade x tempo de uso diário (h) x 30 dias / 1000 -> kWh/mês
    PB11-T04 — se faltar algum dado, retorna 0.0 em vez de quebrar.
    """
    eq = dados["equipamentos"].get(assoc["equipamento_id"])
    if eq is None:
        return 0.0

    potencia = eq.get("potencia")
    quantidade = assoc.get("quantidade")
    tempo_uso = assoc.get("tempo_uso")

    if potencia is None or quantidade is None or tempo_uso is None:
        return 0.0

    consumo_wh_mes = potencia * quantidade * tempo_uso * 30
    consumo_kwh_mes = consumo_wh_mes / 1000
    return consumo_kwh_mes


# ------------------------------------------------------------------
# PB12 — Consumo total mensal do imóvel
# ------------------------------------------------------------------

def consumo_total_imovel(id_imovel):
    associacoes = listar_associacoes_do_imovel(id_imovel)
    if not associacoes:
        return 0.0
    return sum(calcular_consumo_associacao(a) for a in associacoes.values())


# ------------------------------------------------------------------
# PB13 — Ranking de consumo por equipamento
# ------------------------------------------------------------------

def ranking_consumo_imovel(id_imovel):
    associacoes = listar_associacoes_do_imovel(id_imovel)
    itens = []
    for assoc in associacoes.values():
        eq = dados["equipamentos"][assoc["equipamento_id"]]
        consumo = calcular_consumo_associacao(assoc)
        itens.append((eq["nome"], consumo))
    itens.sort(key=lambda item: item[1], reverse=True)
    return itens


def exibir_ranking():
    print("==== RANKING DE CONSUMO ====\n")

    id_imovel = selecionar_imovel_do_usuario()
    if id_imovel is None:
        pausar()
        limpar_terminal()
        return

    ranking = ranking_consumo_imovel(id_imovel)
    if not ranking:
        print("\nESTE IMÓVEL NÃO TEM EQUIPAMENTOS ASSOCIADOS.")
    else:
        print(f"\n==== RANKING — {dados['imoveis'][id_imovel]['apelido']} ====")
        for posicao, (nome, consumo) in enumerate(ranking, start=1):
            print(f"{posicao}º {nome} — {consumo:.2f} kWh/mês")

    pausar()
    limpar_terminal()


# ------------------------------------------------------------------
# PB14 — Resumo do consumo do imóvel
# ------------------------------------------------------------------

def exibir_resumo_imovel():
    print("==== RESUMO DO IMÓVEL ====\n")

    id_imovel = selecionar_imovel_do_usuario()
    if id_imovel is None:
        pausar()
        limpar_terminal()
        return

    imovel = dados["imoveis"][id_imovel]
    associacoes = listar_associacoes_do_imovel(id_imovel)
    total = consumo_total_imovel(id_imovel)

    print(f"\n==== RESUMO — {imovel['apelido']} ====")
    print(f"Endereço: {imovel['endereco']}, {imovel['numero']}")
    print(f"Tipo: {imovel['tipo']}")
    print(f"Quantidade de equipamentos: {len(associacoes)}")
    print(f"Consumo total estimado: {total:.2f} kWh/mês\n")

    if associacoes:
        print("Consumo por equipamento:")
        for assoc in associacoes.values():
            eq = dados["equipamentos"][assoc["equipamento_id"]]
            consumo = calcular_consumo_associacao(assoc)
            print(f"  - {eq['nome']}: {consumo:.2f} kWh/mês")
    else:
        print("Nenhum equipamento associado ainda.")

    pausar()
    limpar_terminal()


# ------------------------------------------------------------------
# PB15 — Gráfico de distribuição do consumo (ASCII, ambiente terminal)
# ------------------------------------------------------------------

def exibir_grafico_consumo():
    print("==== GRÁFICO DE DISTRIBUIÇÃO DO CONSUMO ====\n")

    id_imovel = selecionar_imovel_do_usuario()
    if id_imovel is None:
        pausar()
        limpar_terminal()
        return

    ranking = ranking_consumo_imovel(id_imovel)
    if not ranking:
        print("\nESTE IMÓVEL NÃO TEM EQUIPAMENTOS ASSOCIADOS.")
        pausar()
        limpar_terminal()
        return

    maior_consumo = max(consumo for _, consumo in ranking) or 1
    largura_maxima = 40

    print(f"\n==== CONSUMO — {dados['imoveis'][id_imovel]['apelido']} (kWh/mês) ====\n")
    for nome, consumo in ranking:
        tamanho_barra = int((consumo / maior_consumo) * largura_maxima) if maior_consumo else 0
        barra = "█" * tamanho_barra
        print(f"{nome:<25} {barra} {consumo:.2f}")

    pausar()
    limpar_terminal()


# ------------------------------------------------------------------
# Testes automatizados leves (cobrem os critérios de aceite numéricos
# de PB11/PB12/PB13 sem depender de input() — PB11-T06, PB13-T04)
# ------------------------------------------------------------------

def rodar_testes_calculo():
    print("==== RODANDO TESTES AUTOMATIZADOS DE CÁLCULO ====\n")

    # PB11: potência x quantidade x tempo x 30 / 1000
    assert calcular_consumo_associacao(
        {"equipamento_id": "__t1", "quantidade": 2, "tempo_uso": 5}
    ) == 0.0  # equipamento inexistente -> trata como incompleto (PB11-T04)

    dados["equipamentos"]["__t1"] = {"nome": "Teste", "categoria": "Teste", "potencia": 100, "pre_cadastrado": False}
    resultado = calcular_consumo_associacao(
        {"equipamento_id": "__t1", "quantidade": 2, "tempo_uso": 5}
    )
    assert abs(resultado - 30.0) < 1e-9, f"Esperado 30.0, obtido {resultado}"

    # PB12: soma de várias associações, incluindo imóvel vazio
    dados["associacoes"]["__a1"] = {"imovel_id": "__im_teste", "equipamento_id": "__t1", "quantidade": 1, "tempo_uso": 1}
    dados["associacoes"]["__a2"] = {"imovel_id": "__im_teste", "equipamento_id": "__t1", "quantidade": 1, "tempo_uso": 2}
    total = consumo_total_imovel("__im_teste")
    esperado = calcular_consumo_associacao(dados["associacoes"]["__a1"]) + calcular_consumo_associacao(dados["associacoes"]["__a2"])
    assert abs(total - esperado) < 1e-9

    assert consumo_total_imovel("__im_vazio") == 0.0

    # PB13: ranking decrescente e lista vazia
    ranking = ranking_consumo_imovel("__im_teste")
    assert ranking[0][1] >= ranking[1][1]
    assert ranking_consumo_imovel("__im_vazio") == []

    # limpeza dos dados de teste
    del dados["equipamentos"]["__t1"]
    del dados["associacoes"]["__a1"]
    del dados["associacoes"]["__a2"]

    print("TODOS OS TESTES PASSARAM COM SUCESSO. ✔")
    pausar()
    limpar_terminal()


# ------------------------------------------------------------------
# Menus
# ------------------------------------------------------------------

def menu_equipamentos():
    while True:
        print(" ==== EQUIPAMENTOS DO IMÓVEL ==== \n")
        print("1. Cadastrar equipamento")
        print("2. Listar equipamentos")
        print("3. Editar equipamento")
        print("4. Excluir equipamento")
        print("5. Associar equipamento a um imóvel")
        print("6. Editar associação (quantidade/tempo de uso)")
        print("7. Remover associação")
        print("8. Voltar")

        resposta = ler_opcao_inteira(1, 8)

        if resposta == 1:
            limpar_terminal(); cadastro_equipamento()
        elif resposta == 2:
            listar_equipamentos(); pausar(); limpar_terminal()
        elif resposta == 3:
            limpar_terminal(); modificar_equipamento()
        elif resposta == 4:
            limpar_terminal(); excluir_equipamento()
        elif resposta == 5:
            limpar_terminal(); associar_equipamento()
        elif resposta == 6:
            limpar_terminal(); editar_associacao()
        elif resposta == 7:
            limpar_terminal(); remover_associacao()
        elif resposta == 8:
            limpar_terminal()
            break


def menu_economia():
    while True:
        print(" ==== ECONOMIA DO IMÓVEL ==== \n")
        print("1. Resumo do imóvel")
        print("2. Ranking de consumo por equipamento")
        print("3. Gráfico de distribuição do consumo")
        print("4. Voltar")

        resposta = ler_opcao_inteira(1, 4)

        if resposta == 1:
            limpar_terminal(); exibir_resumo_imovel()
        elif resposta == 2:
            limpar_terminal(); exibir_ranking()
        elif resposta == 3:
            limpar_terminal(); exibir_grafico_consumo()
        elif resposta == 4:
            limpar_terminal()
            break


def ler_opcao_inteira(minimo, maximo):
    """Helper central para leitura de opções de menu (reduz repetição)."""
    while True:
        texto = input(f"\nPOR FAVOR DIGITE UMA OPÇÃO ({minimo}-{maximo})...: ").strip()
        if texto == "":
            print("ERRO: O campo não pode ficar vazio!")
            continue
        try:
            valor = int(texto)
        except ValueError:
            print("ERRO: Digite apenas números.")
            continue
        if minimo <= valor <= maximo:
            return valor
        print(f"ERRO: Escolha um número entre {minimo} e {maximo}.")


def menu_residencia():
    while True:
        print(" ==== SISTEMA DE RESIDÊNCIAS ==== \n")
        print("O QUE GOSTARIA DE FAZER...?\n")
        print("1. CADASTRO IMÓVEL")
        print("2. MODIFICAR INFORMAÇÕES DO IMÓVEL")
        print("3. EXCLUIR IMÓVEL")
        print("4. ADICIONAR/GERENCIAR EQUIPAMENTOS")
        print("5. ECONOMIA DO IMÓVEL")
        print("6. VOLTAR AO MENU PRINCIPAL")

        resposta = ler_opcao_inteira(1, 6)

        if resposta == 1:
            limpar_terminal(); cadastro_imovel()
        elif resposta == 2:
            limpar_terminal(); modificar_imovel()
        elif resposta == 3:
            limpar_terminal(); excluir_imovel()
        elif resposta == 4:
            limpar_terminal(); menu_equipamentos()
        elif resposta == 5:
            limpar_terminal(); menu_economia()
        elif resposta == 6:
            limpar_terminal()
            break


def iniciar_user():
    while True:
        print(" ==== SISTEMA DE CADASTRO DE USUÁRIOS ==== \n")
        print("O QUE GOSTARIA DE FAZER...?\n")
        print("1. CADASTRO DE CONTA")
        print("2. LOG IN")
        print("3. RODAR TESTES DE CÁLCULO (QA)")
        print("4. SAIR DO SISTEMA")

        resposta = ler_opcao_inteira(1, 4)

        if resposta == 1:
            limpar_terminal()
            cadastro_user()

        elif resposta == 2:
            limpar_terminal()
            logado_com_sucesso = login()

            if logado_com_sucesso:
                print("\n====  BEM VINDO AO SISTEMA DE IMÓVEIS ====\n")
                menu_residencia()
                logout()  # PB02/PB18: encerra a sessão ao voltar ao menu principal
            else:
                pausar()
                limpar_terminal()

        elif resposta == 3:
            limpar_terminal()
            rodar_testes_calculo()

        elif resposta == 4:
            limpar_terminal()
            print("Até a próxima!")
            break


if __name__ == "__main__":
    carregar_dados()
    iniciar_user()