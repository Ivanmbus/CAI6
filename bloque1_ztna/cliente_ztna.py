import socket
import json
import datetime
import subprocess
import argparse  # Añadido para manejar argumentos de línea de comandos
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes

class ClienteZTNA:
    def __init__(self, broker_url, certificado_privado_path, rol="medico"):
        self.broker_url = broker_url
        self.rol = rol
        self.certificado_privado = self.cargar_clave_privada(certificado_privado_path)
        
    def cargar_clave_privada(self, path):
        try:
            with open(path, "rb") as f:
                return serialization.load_pem_private_key(f.read(), password=None)
        except FileNotFoundError:
            print(f"❌ Error: No se encuentra el archivo {path}")
            print("   Certificados disponibles:")
            import os
            if os.path.exists("certificados"):
                for file in os.listdir("certificados"):
                    if "privada" in file:
                        print(f"     - certificados/{file}")
            exit(1)
    
    def obtener_ip_local(self):
        return socket.gethostbyname(socket.gethostname())
    
    def verificar_postura_seguridad(self):
        postura = {
            "antivirus": self.check_antivirus(),
            "firewall": self.check_firewall(),
            "so_actualizado": True
        }
        return postura
    
    def check_antivirus(self):
        try:
            result = subprocess.run(["powershell", "Get-MpComputerStatus"], 
                                   capture_output=True, text=True, timeout=5)
            return "AMRunningMode" in result.stdout
        except:
            return False
    
    def check_firewall(self):
        try:
            result = subprocess.run(["powershell", "Get-NetFirewallProfile | Select-Object Enabled"], 
                                   capture_output=True, text=True, timeout=5)
            return "True" in result.stdout
        except:
            return False
    
    def obtener_contexto(self):
        return {
            "rol": self.rol,
            "ubicacion": self.obtener_ip_local(),
            "timestamp": datetime.datetime.now().isoformat(),
            "horario": datetime.datetime.now().strftime("%H:%M"),
            "postura": self.verificar_postura_seguridad()
        }
    
    def firmar_nonce(self, nonce):
        signature = self.certificado_privado.sign(
            nonce.encode(),
            ec.ECDSA(hashes.SHA256())
        )
        return signature.hex()
    
    def solicitar_acceso(self, recurso):
        print(f"\n🔍 Solicitando acceso como '{self.rol}' a: {recurso}")
        
        # Verificar conexión con el broker
        try:
            response_test = requests.get(f"{self.broker_url}/solicitar_nonce", timeout=3)
        except requests.exceptions.ConnectionError:
            print(f"❌ Error: No se puede conectar al broker en {self.broker_url}")
            print("   Asegúrate de ejecutar: python broker_ztna.py en otra terminal")
            return None, None
        
        # Obtener contexto
        contexto = self.obtener_contexto()
        print(f"📊 Contexto: rol={contexto['rol']}, hora={contexto['horario']}, ip={contexto['ubicacion']}")
        
        # Solicitar nonce
        try:
            response = requests.get(f"{self.broker_url}/solicitar_nonce", timeout=5)
            if response.status_code != 200:
                print(f"❌ Error al solicitar nonce: HTTP {response.status_code}")
                return None, None
            
            data = response.json()
            nonce = data.get("nonce")
            print(f"🔑 Nonce recibido: {nonce[:30]}...")
        except Exception as e:
            print(f"❌ Error al solicitar nonce: {e}")
            return None, None
        
        # Firmar nonce
        firma = self.firmar_nonce(nonce)
        print(f"✍️ Firma generada: {firma[:30]}...")
        
        # Enviar solicitud de acceso
        payload = {
            "contexto": contexto,
            "nonce": nonce,
            "firma": firma,
            "recurso": recurso
        }
        
        try:
            respuesta = requests.post(f"{self.broker_url}/acceder", 
                                     json=payload, 
                                     timeout=10)
            return respuesta.status_code, respuesta.json()
        except Exception as e:
            print(f"❌ Error al enviar solicitud: {e}")
            return None, None
    
    def ejecutar(self, recurso="/historias_clinicas/paciente_123"):
        status, resultado = self.solicitar_acceso(recurso)
        
        if status == 200:
            print(f"\n✅ ACCESO CONCEDIDO (HTTP {status})")
            print(f"   {resultado.get('mensaje', 'Acceso autorizado')}")
            if 'datos' in resultado:
                print(f"   Datos: {resultado['datos']}")
        elif status == 403:
            print(f"\n❌ ACCESO DENEGADO (HTTP {status})")
            print(f"   Razón: {resultado.get('error', 'No autorizado')}")
        else:
            print(f"\n⚠️ Error inesperado: {status}")


# ============ NUEVA SECCIÓN PRINCIPAL MODIFICADA ============

if __name__ == "__main__":
    # Configurar el parser de argumentos
    parser = argparse.ArgumentParser(description='Cliente ZTNA para acceso a historias clínicas')
    parser.add_argument('--rol', '-r', 
                        choices=['medico', 'enfermero', 'admin', 'empleado'],
                        default='medico',
                        help='Rol del usuario (determina qué certificado usar)')
    parser.add_argument('--recurso', '-u', 
                        default='/historias_clinicas/paciente_123',
                        help='Recurso al que se quiere acceder')
    parser.add_argument('--broker', '-b', 
                        default='http://localhost:5000',
                        help='URL del broker ZTNA')
    
    args = parser.parse_args()
    
    # Mapeo de roles a rutas de certificados
    certificados_por_rol = {
        "medico": "certificados/medico_privada.pem",
        "enfermero": "certificados/enfermero_privada.pem",
        "admin": "certificados/admin_privada.pem",
        "empleado": "certificados/empleado_privada.pem"
    }
    
    # Verificar si existe el certificado para el rol elegido
    cert_path = certificados_por_rol.get(args.rol)
    
    if not cert_path:
        print(f"❌ Rol '{args.rol}' no válido")
        print("   Roles disponibles: medico, enfermero, admin, empleado")
        exit(1)
    
    print("=" * 60)
    print(f"🖥️ Cliente ZTNA - INSEGUS")
    print(f"   Rol: {args.rol.upper()}")
    print(f"   Certificado: {cert_path}")
    print(f"   Broker: {args.broker}")
    print(f"   Recurso: {args.recurso}")
    print("=" * 60)
    
    # Crear y ejecutar cliente
    cliente = ClienteZTNA(args.broker, cert_path, rol=args.rol)
    cliente.ejecutar(recurso=args.recurso)