# generar_asignaciones.py

import random
import csv
from collections import defaultdict
from empleados_config import empleados, tareas
from restricciones import RestriccionesJerarquia, RestriccionesSoD, RestriccionesBinding, RestriccionesConflicto, RestriccionesFairness

class GeneradorInstancias:
    def __init__(self, num_instancias=20):
        self.num_instancias = num_instancias
        self.empleados_ids = list(empleados.keys())
        self.instancias = []
        
    def obtener_candidatos(self, tarea_id, exclude=[]):
        """Retorna lista de empleados que pueden hacer una tarea"""
        candidatos = []
        for emp_id in self.empleados_ids:
            if emp_id in exclude:
                continue
            if RestriccionesJerarquia.puede_asignar(emp_id, tarea_id):
                candidatos.append(emp_id)
        return candidatos
    
    def asignar_t1(self):
        candidatos = self.obtener_candidatos("T1")
        # JVG solo puede T1, darle prioridad si está disponible
        if "JVG" in candidatos:
            return "JVG"
        return random.choice(candidatos)
    
    def asignar_t21_t22(self, fairness):
        # Asignar T2.1 y T2.2 con SoD y binding
        candidatos_t21 = self.obtener_candidatos("T2.1")
        
        # Forzar binding si GTR es candidato (probabilidad 30%)
        if "GTR" in candidatos_t21 and random.random() < 0.3:
            t21 = "GTR"
            # Binding: T2.2 debe ser MDS
            if "MDS" in self.obtener_candidatos("T2.2", exclude=[t21]):
                t22 = "MDS"
            else:
                # Fallback: cualquier otro excepto GTR
                candidatos_t22 = self.obtener_candidatos("T2.2", exclude=[t21])
                t22 = fairness.empleado_menos_cargado(candidatos_t22) if candidatos_t22 else None
        else:
            t21 = fairness.empleado_menos_cargado(candidatos_t21)
            candidatos_t22 = self.obtener_candidatos("T2.2", exclude=[t21])
            t22 = fairness.empleado_menos_cargado(candidatos_t22)
        
        return t21, t22
    
    def asignar_t3_t4(self, fairness, exclude_t21_t22):
        candidatos_t3 = self.obtener_candidatos("T3", exclude=exclude_t21_t22)
        t3 = fairness.empleado_menos_cargado(candidatos_t3)
        
        exclude_t3 = exclude_t21_t22 + [t3]
        candidatos_t4 = self.obtener_candidatos("T4", exclude=exclude_t3)
        t4 = fairness.empleado_menos_cargado(candidatos_t4)
        
        return t3, t4
    
    def generar_instancia(self, fairness):
        asignacion = {}
        
        # T1
        asignacion["T1"] = self.asignar_t1()
        
        # T2.1 y T2.2
        t21, t22 = self.asignar_t21_t22(fairness)
        asignacion["T2.1"] = t21
        asignacion["T2.2"] = t22
        
        # T3 y T4 (excluyendo a los ya usados en T2)
        exclude = [asignacion["T2.1"], asignacion["T2.2"]]
        t3, t4 = self.asignar_t3_t4(fairness, exclude)
        asignacion["T3"] = t3
        asignacion["T4"] = t4
        
        return asignacion
    
    def validar_asignacion(self, asignacion):
        """Valida todas las restricciones"""
        checks = [
            RestriccionesSoD.sod_t21_t22(asignacion),
            RestriccionesSoD.sod_t3_t4(asignacion),
            RestriccionesBinding.binding_gtr_mds(asignacion),
            RestriccionesConflicto.conflicto_jvg(asignacion),
            RestriccionesJerarquia.validar_todas_asignaciones(asignacion)
        ]
        return all(checks)
    
    def generar(self):
        fairness = RestriccionesFairness(self.empleados_ids, max_diferencia=3)
        
        for i in range(self.num_instancias):
            intentos = 0
            while intentos < 10:  # Máximo 10 intentos por instancia
                asignacion = self.generar_instancia(fairness)
                if self.validar_asignacion(asignacion):
                    # Actualizar carga para fairness
                    for emp in asignacion.values():
                        fairness.carga[emp] += 1
                    self.instancias.append(asignacion)
                    break
                intentos += 1
            
            if intentos >= 10:
                print(f"Advertencia: No se encontró asignación válida en instancia {i+1}")
                self.instancias.append(None)
        
        return self.instancias
    
    def exportar_csv(self, filename="salida/asignaciones_compras.csv"):
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Instancia', 'T1', 'T2.1', 'T2.2', 'T3', 'T4'])
            
            for idx, inst in enumerate(self.instancias, 1):
                if inst:
                    writer.writerow([
                        idx,
                        f"{inst['T1']} ({empleados[inst['T1']]['nombre']})",
                        f"{inst['T2.1']} ({empleados[inst['T2.1']]['nombre']})",
                        f"{inst['T2.2']} ({empleados[inst['T2.2']]['nombre']})",
                        f"{inst['T3']} ({empleados[inst['T3']]['nombre']})",
                        f"{inst['T4']} ({empleados[inst['T4']]['nombre']})"
                    ])
                else:
                    writer.writerow([idx, 'ERROR', 'ERROR', 'ERROR', 'ERROR', 'ERROR'])
        
        print(f"✅ Archivo generado: {filename}")
    
    def mostrar_resumen_carga(self):
        carga = defaultdict(int)
        for inst in self.instancias:
            if inst:
                for emp in inst.values():
                    carga[emp] += 1
        
        print("\n📊 Resumen de carga por empleado:")
        for emp in sorted(carga.keys(), key=lambda e: carga[e], reverse=True):
            print(f"  - {emp} ({empleados[emp]['nombre']}): {carga[emp]} tareas")

if __name__ == "__main__":
    print("🚀 Generando 20 instancias de asignaciones...")
    generador = GeneradorInstancias(num_instancias=20)
    generador.generar()
    generador.exportar_csv()
    generador.mostrar_resumen_carga()