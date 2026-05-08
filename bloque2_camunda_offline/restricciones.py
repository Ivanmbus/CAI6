# restricciones.py

from empleados_config import empleados, tareas

class RestriccionesSoD:
    """Separation of Duties (SoD)"""
    
    @staticmethod
    def sod_t21_t22(asignacion):
        """T2.1 y T2.2 deben ser personas distintas"""
        return asignacion["T2.1"] != asignacion["T2.2"]
    
    @staticmethod
    def sod_t3_t4(asignacion):
        """T3 y T4 deben ser personas distintas"""
        return asignacion["T3"] != asignacion["T4"]

class RestriccionesBinding:
    """Binding de deberes"""
    
    @staticmethod
    def binding_gtr_mds(asignacion):
        """Si GTR hace T2.1, entonces MDS debe hacer T2.2"""
        if asignacion["T2.1"] == "GTR":
            return asignacion["T2.2"] == "MDS"
        return True

class RestriccionesConflicto:
    """Conflicto de intereses"""
    
    @staticmethod
    def conflicto_jvg(asignacion):
        """JVG solo puede hacer T1"""
        for tarea, empleado in asignacion.items():
            if empleado == "JVG" and tarea != "T1":
                return False
        return True

class RestriccionesJerarquia:
    """Jerarquía de roles"""
    
    @staticmethod
    def puede_asignar(empleado_id, tarea_id):
        empleado = empleados[empleado_id]
        tarea = tareas[tarea_id]
        
        # Verificar rol permitido

        if not any(rol in tarea["roles_permitidos"] for rol in empleado["rol"]):
            return False
        
        # Verificar jerarquía mínima
        if empleado["jerarquia"] < tarea["jerarquia_minima"]:
            return False
        
        # Verificar conflicto de intereses específico
        if empleado["conflicto_intereses"] and tarea_id != "T1":
            return False
        
        return True
    
    @staticmethod
    def validar_todas_asignaciones(asignacion):
        for tarea, empleado in asignacion.items():
            if not RestriccionesJerarquia.puede_asignar(empleado, tarea):
                return False
        return True

class RestriccionesFairness:
    
    def __init__(self, empleados_ids, max_diferencia=3):
        self.empleados_ids = empleados_ids
        self.carga = {emp: 0 for emp in empleados_ids}
        self.max_diferencia = max_diferencia
        # Precalcular elegibilidad una sola vez
        self.elegibles_por_empleado = {
            emp: sum(
                1 for t in tareas.keys()
                if RestriccionesJerarquia.puede_asignar(emp, t)
            )
            for emp in empleados_ids
        }


    def empleado_menos_cargado(self, candidatos): 
        if not candidatos:
            return None
        
        def carga_normalizada(emp_id):
            elegibles = self.elegibles_por_empleado.get(emp_id, 1)
            return self.carga[emp_id] / max(elegibles, 1)

        scores = {emp: carga_normalizada(emp) for emp in candidatos}

        return min(candidatos, key=carga_normalizada)

    def actualizar_carga(self, asignacion):
        for empleado in asignacion.values():
            self.carga[empleado] += 1
    