import datetime
import json
import uuid
from flask import Flask, request, jsonify
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
import ipaddress


app = Flask(__name__)

class BrokerZTNA:
    def __init__(self, politica_path, certificados_ca_path):
        self.politica = self.cargar_politica(politica_path)
        self.certificados_ca = self.cargar_certificados_ca(certificados_ca_path)
        self.nonces_activos = {}  # nonce: timestamp
        
    def cargar_politica(self, path):
        with open(path, "r") as f:
            return json.load(f)
    
    def cargar_certificados_ca(self, path):
        # Cargar certificados de CA confiables para validar certificados de empleados
        pass
    
    def validar_horario(self, horario_str, horario_permitido):
        hora_actual = int(horario_str.split(":")[0])
        inicio = int(horario_permitido["inicio"].split(":")[0])
        fin = int(horario_permitido["fin"].split(":")[0])
        return inicio <= hora_actual <= fin
    
    def validar_ubicacion(self, ip_str, redes_permitidas):
        ip = ipaddress.ip_address(ip_str)
        for red in redes_permitidas:
            if ip in ipaddress.ip_network(red):
                return True
        return False
    
    def validar_postura(self, postura, postura_requerida):
        for key, required_value in postura_requerida.items():
            if postura.get(key) != required_value:
                return False
        return True
    
    def evaluar_politica(self, contexto, recurso):
        for recurso_config in self.politica["recursos"]:
            if self.coincide_recurso(recurso, recurso_config["uri"]):
                politica = recurso_config["politica"]
                
                # Validar rol
                if contexto["rol"] not in politica["roles_permitidos"]:
                    return False, "Rol no permitido"
                
                # Validar ubicación
                if not self.validar_ubicacion(contexto["ubicacion"], politica["ubicaciones_permitidas"]):
                    return False, "Ubicación no permitida"
                
                # Validar horario
                if not self.validar_horario(contexto["horario"], politica["horario_permitido"]):
                    return False, "Horario no permitido"
                
                # Validar postura de seguridad
                if not self.validar_postura(contexto["postura"], politica["postura_requerida"]):
                    return False, "Postura de seguridad insuficiente"
                
                return True, "Acceso concedido"
        
        return False, "Recurso no configurado"
    
    def coincide_recurso(self, recurso_solicitado, patron):
        # Implementar coincidencia de patrones con wildcard (*)
        if patron.endswith("*"):
            return recurso_solicitado.startswith(patron[:-1])
        return recurso_solicitado == patron
    
    def verificar_firma(self, nonce, firma_hex, certificado_empleado_path):
        # Cargar certificado público del empleado
        with open(certificado_empleado_path, "rb") as f:
            public_key = serialization.load_pem_public_key(f.read())
        
        firma_bytes = bytes.fromhex(firma_hex)
        try:
            public_key.verify(
                firma_bytes,
                nonce.encode(),
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except:
            return False

broker = BrokerZTNA("politica_acceso.json", "certificados/ca")

@app.route('/solicitar_nonce', methods=['GET'])
def solicitar_nonce():
    nonce = str(uuid.uuid4())
    broker.nonces_activos[nonce] = datetime.datetime.now()
    return jsonify({"nonce": nonce})

@app.route('/acceder', methods=['POST'])
def acceder():
    data = request.json
    contexto = data["contexto"]
    nonce = data["nonce"]
    firma = data["firma"]
    recurso = data["recurso"]
    
    # Verificar que el nonce está activo
    if nonce not in broker.nonces_activos:
        return jsonify({"error": "Nonce inválido o expirado"}), 403
    
    # Verificar firma (requiere certificado del empleado asociado al rol)
    # Por simplicidad, aquí se asume que el certificado se obtiene del contexto
    if not broker.verificar_firma(nonce, firma, f"certificados/{contexto['rol']}_publica.pem"):
        return jsonify({"error": "Firma inválida"}), 403
    
    # Evaluar política CBAC
    acceso, mensaje = broker.evaluar_politica(contexto, recurso)
    
    if acceso:
        # Reenviar al recurso protegido (Reverse Proxy)
        return jsonify({"mensaje": mensaje, "datos": "Contenido de la historia clínica"}), 200
    else:
        return jsonify({"error": mensaje}), 403

if __name__ == '__main__':
    app.run(debug=True, port=5000)