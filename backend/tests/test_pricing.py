from decimal import Decimal
import pytest
from app.services.pricing import (
    calcular_precio,
    calcular_precio_con_config,
    DEFAULT_PRECIO_BN,
    DEFAULT_PRECIO_COLOR,
    DEFAULT_RECARGO_A3,
    DEFAULT_RECARGO_OFICIO,
    DEFAULT_DESCUENTO_DOBLE_FAZ
)
from app.models.precios import PreciosConfig

def test_calcular_precio_a4_bn_simple():
    # 10 pags, 1 copia, BN, A4
    # 25.00 * 1.00 * 1.00 * 10 * 1 = 250.00
    precio = calcular_precio(
        precio_bn_pagina=Decimal("25.00"),
        precio_color_pagina=Decimal("60.00"),
        recargo_a3=Decimal("1.60"),
        recargo_oficio=Decimal("1.15"),
        descuento_doble_faz=Decimal("1.00"),
        color=False,
        tamano="A4",
        paginas=10,
        copias=1,
        doble_faz=False
    )
    assert precio == Decimal("250.00")

def test_calcular_precio_a4_color_copias():
    # 5 pags, 3 copias, Color, A4
    # 60.00 * 1.00 * 1.00 * 5 * 3 = 900.00
    precio = calcular_precio(
        precio_bn_pagina=Decimal("25.00"),
        precio_color_pagina=Decimal("60.00"),
        recargo_a3=Decimal("1.60"),
        recargo_oficio=Decimal("1.15"),
        descuento_doble_faz=Decimal("1.00"),
        color=True,
        tamano="A4",
        paginas=5,
        copias=3,
        doble_faz=False
    )
    assert precio == Decimal("900.00")

def test_calcular_precio_a3_recargo():
    # 10 pags, 1 copia, BN, A3
    # 25.00 * 1.60 * 10 = 400.00
    precio = calcular_precio(
        precio_bn_pagina=Decimal("25.00"),
        precio_color_pagina=Decimal("60.00"),
        recargo_a3=Decimal("1.60"),
        recargo_oficio=Decimal("1.15"),
        descuento_doble_faz=Decimal("1.00"),
        color=False,
        tamano="A3",
        paginas=10,
        copias=1,
        doble_faz=False
    )
    assert precio == Decimal("400.00")

def test_calcular_precio_oficio_recargo():
    # 10 pags, 1 copia, Color, Oficio
    # 60.00 * 1.15 * 10 = 690.00
    precio = calcular_precio(
        precio_bn_pagina=Decimal("25.00"),
        precio_color_pagina=Decimal("60.00"),
        recargo_a3=Decimal("1.60"),
        recargo_oficio=Decimal("1.15"),
        descuento_doble_faz=Decimal("1.00"),
        color=True,
        tamano="Oficio",
        paginas=10,
        copias=1,
        doble_faz=False
    )
    assert precio == Decimal("690.00")

def test_calcular_precio_descuento_doble_faz():
    # Multiplicador 0.90 (10% de descuento sobre el precio por página en doble faz)
    # 10 pags, 2 copias, BN, A4, doble faz
    # 25.00 * 1.00 * 0.90 * 10 * 2 = 450.00
    precio = calcular_precio(
        precio_bn_pagina=Decimal("25.00"),
        precio_color_pagina=Decimal("60.00"),
        recargo_a3=Decimal("1.60"),
        recargo_oficio=Decimal("1.15"),
        descuento_doble_faz=Decimal("0.90"),
        color=False,
        tamano="A4",
        paginas=10,
        copias=2,
        doble_faz=True
    )
    assert precio == Decimal("450.00")

def test_calcular_precio_sin_descuento_cuando_es_simple_faz():
    # Si doble_faz es False, el factor debe ser 1.00 incluso si descuento_doble_faz es 0.85
    precio = calcular_precio(
        precio_bn_pagina=Decimal("25.00"),
        precio_color_pagina=Decimal("60.00"),
        recargo_a3=Decimal("1.60"),
        recargo_oficio=Decimal("1.15"),
        descuento_doble_faz=Decimal("0.85"),
        color=False,
        tamano="A4",
        paginas=10,
        copias=1,
        doble_faz=False
    )
    assert precio == Decimal("250.00")

def test_calcular_precio_con_config_model():
    config = PreciosConfig(
        tenant_id=1,
        precio_bn_pagina=Decimal("30.00"),
        precio_color_pagina=Decimal("70.00"),
        recargo_a3=Decimal("1.50"),
        recargo_oficio=Decimal("1.20"),
        descuento_doble_faz=Decimal("0.95")
    )
    # A3, Color, doble faz, 4 pags, 2 copias
    # 70.00 * 1.50 * 0.95 * 4 * 2 = 798.00
    precio = calcular_precio_con_config(
        precios_config=config,
        color=True,
        tamano="A3",
        paginas=4,
        copias=2,
        doble_faz=True
    )
    assert precio == Decimal("798.00")

def test_calcular_precio_ceros_o_negativos():
    precio = calcular_precio(
        precio_bn_pagina=Decimal("25.00"),
        precio_color_pagina=Decimal("60.00"),
        recargo_a3=Decimal("1.60"),
        recargo_oficio=Decimal("1.15"),
        descuento_doble_faz=Decimal("1.00"),
        color=False,
        tamano="A4",
        paginas=0,
        copias=1
    )
    assert precio == Decimal("0.00")

