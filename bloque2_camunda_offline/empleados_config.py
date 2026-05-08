# empleados_config.py

empleados = {
    "JVG": {
        "nombre": "Juan Vidal García",
        "rol": "DG",
        "jerarquia": 3,
        "conflicto_intereses": True,  # Solo puede hacer T1
        "especialidad": "direccion"
    },
    "HYV": {
        "nombre": "Helena Yuste Vidal",
        "rol": "DR",
        "jerarquia": 2,
        "conflicto_intereses": False,
        "especialidad": "recursos_sanitarios"
    },
    "PGR": {
        "nombre": "Pedro Gómez Ruiz",
        "rol": "DM",
        "jerarquia": 2,
        "conflicto_intereses": False,
        "especialidad": "logistica"
    },
    "MFE": {
        "nombre": "María Fernández Espinosa",
        "rol": "DE",
        "jerarquia": 2,
        "conflicto_intereses": False,
        "especialidad": "tecnico_compras"
    },
    "GTR": {
        "nombre": "Gabriel Torres Ramírez",
        "rol": "TR",
        "jerarquia": 1,
        "conflicto_intereses": False,
        "especialidad": "evaluacion",
        "binding_obligatorio": {  # Si hace T2.1, entonces MDS debe hacer T2.2
            "T2.1": "MDS"
        }
    },
    "LPG": {
        "nombre": "Laura Pérez Gil",
        "rol": "TR",
        "jerarquia": 1,
        "conflicto_intereses": False,
        "especialidad": "administrativa"
    },
    "RGB": {
        "nombre": "Raúl Gómez Blanco",
        "rol": "TR",
        "jerarquia": 1,
        "conflicto_intereses": False,
        "especialidad": "administrativa"
    },
    "BJC": {
        "nombre": "Beatriz Jiménez Calderón",
        "rol": "TR",
        "jerarquia": 1,
        "conflicto_intereses": False,
        "especialidad": "finanzas"
    },
    "MDS": {
        "nombre": "Manuel Díaz Sánchez",
        "rol": "TC",
        "jerarquia": 1,
        "conflicto_intereses": False,
        "especialidad": "legal",
        "binding_destino": ["GTR"]  # Complementario a GTR
    },
    "HJR": {
        "nombre": "Helena Jiménez Ruiz",
        "rol": "PS",
        "jerarquia": 2,
        "conflicto_intereses": False,
        "especialidad": "compras"
    },
    "PTS": {
        "nombre": "Pablo Torres Soto",
        "rol": "PS",
        "jerarquia": 1,
        "conflicto_intereses": False,
        "especialidad": "inventario"
    },
    "IHP": {
        "nombre": "Irene Herrera Pérez",
        "rol": "PS",
        "jerarquia": 1,
        "conflicto_intereses": False,
        "especialidad": "calidad"
    }
}

# Configuración de tareas
tareas = {
    "T1": {
        "nombre": "Requerimiento de compra",
        "roles_permitidos": ["DG", "DR"],
        "jerarquia_minima": 2
    },
    "T2.1": {
        "nombre": "Elaborar prescripciones técnicas",
        "roles_permitidos": ["DG", "DR", "TR"],
        "jerarquia_minima": 1
    },
    "T2.2": {
        "nombre": "Buscar proveedores",
        "roles_permitidos": ["DG", "DR", "TC"],
        "jerarquia_minima": 1
    },
    "T3": {
        "nombre": "Aprobación final",
        "roles_permitidos": ["DG", "DM"],
        "jerarquia_minima": 2
    },
    "T4": {
        "nombre": "Recibir y decidir sobre ofertas",
        "roles_permitidos": ["DG", "DM", "DE", "PS"],
        "jerarquia_minima": 1
    }
}