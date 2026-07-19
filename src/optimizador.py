"""
Optimizador de pedidos - Hotel Austral
=======================================
Dado un listado de productos requeridos, decide a que proveedor pedir cada uno,
buscando minimizar la cantidad de proveedores distintos.

Regla de negocio (definida por el usuario):
1. Si un producto tiene un solo proveedor -> se le pide a ese.
2. Si tiene varios proveedores, se ordena por precio.
3. Si la diferencia entre el mas barato y el segundo es <= 15%,
   entra en desempate:
     a) gana el proveedor que cubre mas productos del pedido total
     b) si sigue empatado, gana el que tenga "Cuenta Corriente"
        (mejor para el flujo de caja del hotel) por sobre "Contado".
4. Si la diferencia es > 15%, gana directamente el mas barato.

Esta logica es 100% codigo (determinística) - el LLM solo redacta la
respuesta final en lenguaje natural a partir del resultado de esta funcion.
"""

from dataclasses import dataclass, field
import pandas as pd
import unicodedata

DIFERENCIA_MAXIMA = 0.15  # 15%
PRIORIDAD_PAGO = {
    "cuenta corriente": 1,
    "cta cte": 1,
    "contado": 0,
    "desconocida": -1,
}


def _normalizar(texto: str) -> str:
    """minusculas, sin tildes, espacios -> guion bajo. Para matchear contra la columna 'clave'."""
    texto = texto.strip().lower()
    texto = "".join(
        c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn"
    )
    return texto.replace(" ", "_")


def claves_disponibles(precios: pd.DataFrame) -> list[str]:
    """Lista de claves de producto validas - util para que el agente/LLM sepa que valores puede pasar."""
    return sorted(precios["clave"].unique().tolist())


@dataclass
class LineaPedido:
    producto: str
    proveedor: str
    precio: float
    unidad: str
    motivo: str


@dataclass
class ResultadoOptimizacion:
    lineas: list = field(default_factory=list)
    productos_sin_proveedor: list = field(default_factory=list)

    def pedido_por_proveedor(self) -> dict:
        agrupado = {}
        for linea in self.lineas:
            agrupado.setdefault(linea.proveedor, []).append(linea)
        return agrupado

    def cantidad_proveedores(self) -> int:
        return len(self.pedido_por_proveedor())

    def total_estimado(self) -> float:
        return sum(l.precio for l in self.lineas)


def cargar_datos(ruta_precios: str, ruta_proveedores: str):
    precios = pd.read_csv(ruta_precios)
    proveedores = pd.read_csv(ruta_proveedores)
    return precios, proveedores


def optimizar_pedido(
    productos_requeridos: list[str], precios: pd.DataFrame, proveedores: pd.DataFrame
) -> ResultadoOptimizacion:
    condicion_por_proveedor = dict(zip(proveedores["proveedor"], proveedores["condicion_pago"]))

    resultado = ResultadoOptimizacion()

    # Paso 1: para cada producto, encontrar candidatos (proveedor, precio) por clave exacta
    candidatos_por_producto = {}
    for producto in productos_requeridos:
        clave = _normalizar(producto)
        filas = precios[precios["clave"] == clave]
        if filas.empty:
            resultado.productos_sin_proveedor.append(producto)
            continue
        candidatos_por_producto[producto] = filas.sort_values("precio").to_dict("records")

    # Paso 2: contar en cuantos productos aparece cada proveedor (para el desempate por cobertura)
    conteo_proveedor = {}
    for candidatos in candidatos_por_producto.values():
        proveedores_unicos = {c["proveedor"] for c in candidatos}
        for p in proveedores_unicos:
            conteo_proveedor[p] = conteo_proveedor.get(p, 0) + 1

    # Paso 3: decidir proveedor por producto
    for producto, candidatos in candidatos_por_producto.items():
        if len(candidatos) == 1:
            c = candidatos[0]
            resultado.lineas.append(
                LineaPedido(producto, c["proveedor"], c["precio"], c["unidad"], "unico proveedor disponible")
            )
            continue

        mas_barato = candidatos[0]
        diff = None
        empatados = [mas_barato]
        for c in candidatos[1:]:
            d = (c["precio"] - mas_barato["precio"]) / mas_barato["precio"]
            if d <= DIFERENCIA_MAXIMA:
                empatados.append(c)

        if len(empatados) == 1:
            resultado.lineas.append(
                LineaPedido(
                    producto, mas_barato["proveedor"], mas_barato["precio"], mas_barato["unidad"],
                    f"mas barato, diferencia > {int(DIFERENCIA_MAXIMA*100)}% con el resto",
                )
            )
            continue

        # Desempate 1: cobertura (cuantos productos del pedido total cubre el proveedor)
        empatados.sort(key=lambda c: conteo_proveedor.get(c["proveedor"], 0), reverse=True)
        max_cobertura = conteo_proveedor.get(empatados[0]["proveedor"], 0)
        finalistas = [c for c in empatados if conteo_proveedor.get(c["proveedor"], 0) == max_cobertura]

        if len(finalistas) == 1:
            elegido = finalistas[0]
            motivo = f"diferencia <= {int(DIFERENCIA_MAXIMA*100)}%, gana por cubrir mas productos del pedido"
        else:
            # Desempate 2: condicion de pago (Cuenta Corriente > Contado)
            finalistas.sort(
                key=lambda c: PRIORIDAD_PAGO.get(
                    str(condicion_por_proveedor.get(c["proveedor"], "desconocida")).lower(), -1
                ),
                reverse=True,
            )
            elegido = finalistas[0]
            motivo = f"diferencia <= {int(DIFERENCIA_MAXIMA*100)}%, misma cobertura, gana por mejor condicion de pago"

        resultado.lineas.append(
            LineaPedido(producto, elegido["proveedor"], elegido["precio"], elegido["unidad"], motivo)
        )

    return resultado


if __name__ == "__main__":
    precios, proveedores = cargar_datos(
        "../data/procesados/precios.csv", "../data/procesados/proveedores.csv"
    )
    print("Claves disponibles:", claves_disponibles(precios))
    pedido = ["papel_higienico", "aceite", "leche", "queso_barra", "pan_blanco"]
    r = optimizar_pedido(pedido, precios, proveedores)
    for proveedor, lineas in r.pedido_por_proveedor().items():
        print(f"\n{proveedor}:")
        for l in lineas:
            print(f"  - {l.producto}: ${l.precio} ({l.motivo})")
    print(f"\nTotal proveedores: {r.cantidad_proveedores()}")
    print(f"Total estimado: ${r.total_estimado():,.2f}")
    if r.productos_sin_proveedor:
        print(f"Sin proveedor encontrado: {r.productos_sin_proveedor}")
