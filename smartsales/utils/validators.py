import re


def validate_full_name(name: str) -> str:
    """
    Valida nome completo com exatamente duas palavras,
    cada uma com pelo menos 3 letras, sem números ou caracteres especiais.
    """
    pattern = r'^[A-Za-z]{3,}\s[A-Za-z]{3,}$'
    if not re.fullmatch(pattern, name):
        raise ValueError(
            f"Nome o '{name}', deve conter duas palavras, sem números ou caracteres especiais."  # noqa: E501
        )
    return name


def validate_cpf(cpf: str) -> str:
    """
    Valida o CPF tanto na formação quanto nos dígitos verificadores
    """
    cpf = ''.join(filter(str.isdigit, cpf))

    if len(cpf) != 11:  # noqa: PLR2004
        raise ValueError('CPF deve conter 11 dígitos')

    # Verifica dígitos repetidos
    if cpf == cpf[0] * 11:
        raise ValueError('CPF inválido')

    # Cálculo dos dígitos verificadores
    for i in range(9, 11):
        value = sum((int(cpf[num]) * ((i + 1) - num) for num in range(0, i)))
        digit = ((value * 10) % 11) % 10
        if digit != int(cpf[i]):
            raise ValueError('CPF inválido')

    return cpf
