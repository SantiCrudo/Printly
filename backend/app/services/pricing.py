from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
from app.models.precios import PreciosConfig

DEFAULT_PRECIO_BN = Decimal("25.00")
DEFAULT_PRECIO_COLOR = Decimal("60.00")
DEFAULT_RECARGO_A3 = Decimal("1.60")
DEFAULT_RECARGO_OFICIO = Decimal("1.15")
DEFAULT_DESCUENTO_DOBLE_FAZ = Decimal("1.00")

def to_decimal(val, default: Decimal) -> Decimal:
    if val is None:
        return default
    if isinstance(val, Decimal):
        return val
    return Decimal(str(val))

def calcular_precio_unitario_pagina(
    precio_bn_pagina: Decimal,
    precio_color_pagina: Decimal,
    recargo_a3: Decimal,
    recargo_oficio: Decimal,
    descuento_doble_faz: Decimal,
    color: bool,
    tamano: str,
    doble_faz: bool = False
) -> Decimal:
    """
    Calcula el precio unitario por página antes de multiplicar por páginas y copias.
    """
    precio_base = precio_color_pagina if color else precio_bn_pagina

    tamano_norm = (tamano or "A4").strip().upper()
    if tamano_norm == "A3":
        recargo_tamano = recargo_a3
    elif tamano_norm in ("OFICIO", "LEGAL"):
        recargo_tamano = recargo_oficio
    else:
        recargo_tamano = Decimal("1.00")

    factor_doble_faz = descuento_doble_faz if doble_faz else Decimal("1.00")

    return precio_base * recargo_tamano * factor_doble_faz

def calcular_precio(
    precio_bn_pagina: Decimal,
    precio_color_pagina: Decimal,
    recargo_a3: Decimal,
    recargo_oficio: Decimal,
    descuento_doble_faz: Decimal,
    color: bool,
    tamano: str,
    paginas: int,
    copias: int,
    doble_faz: bool = False
) -> Decimal:
    """
    Función pura que calcula el precio total de una impresión con Decimal.
    Aplica multiplicadores de tamaño y descuento_doble_faz (multiplicador, 1.00 = sin descuento).
    """
    if paginas <= 0 or copias <= 0:
        return Decimal("0.00")

    precio_por_pagina = calcular_precio_unitario_pagina(
        precio_bn_pagina=precio_bn_pagina,
        precio_color_pagina=precio_color_pagina,
        recargo_a3=recargo_a3,
        recargo_oficio=recargo_oficio,
        descuento_doble_faz=descuento_doble_faz,
        color=color,
        tamano=tamano,
        doble_faz=doble_faz
    )

    total = precio_por_pagina * Decimal(paginas) * Decimal(copias)
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def calcular_precio_con_config(
    precios_config: Optional[PreciosConfig],
    color: bool,
    tamano: str,
    paginas: int,
    copias: int,
    doble_faz: bool = False
) -> Decimal:
    """
    Calcula precio a partir de un modelo PreciosConfig (o defaults si es None).
    """
    if precios_config:
        precio_bn = to_decimal(precios_config.precio_bn_pagina, DEFAULT_PRECIO_BN)
        precio_color = to_decimal(precios_config.precio_color_pagina, DEFAULT_PRECIO_COLOR)
        recargo_a3 = to_decimal(precios_config.recargo_a3, DEFAULT_RECARGO_A3)
        recargo_oficio = to_decimal(precios_config.recargo_oficio, DEFAULT_RECARGO_OFICIO)
        descuento_df = to_decimal(precios_config.descuento_doble_faz, DEFAULT_DESCUENTO_DOBLE_FAZ)
    else:
        precio_bn = DEFAULT_PRECIO_BN
        precio_color = DEFAULT_PRECIO_COLOR
        recargo_a3 = DEFAULT_RECARGO_A3
        recargo_oficio = DEFAULT_RECARGO_OFICIO
        descuento_df = DEFAULT_DESCUENTO_DOBLE_FAZ

    return calcular_precio(
        precio_bn_pagina=precio_bn,
        precio_color_pagina=precio_color,
        recargo_a3=recargo_a3,
        recargo_oficio=recargo_oficio,
        descuento_doble_faz=descuento_df,
        color=color,
        tamano=tamano,
        paginas=paginas,
        copias=copias,
        doble_faz=doble_faz
    )

