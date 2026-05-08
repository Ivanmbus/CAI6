# generar_certificados_correctos.py
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
import os

def generar_certificados_para_roles():
    """Genera certificados para cada rol en el formato que espera el broker"""
    
    # Crear directorio de certificados
    os.makedirs("certificados", exist_ok=True)
    
    roles = ["medico", "enfermero", "admin", "empleado"]
    
    for rol in roles:
        # Generar clave privada ECC P-256
        private_key = ec.generate_private_key(ec.SECP256R1())
        
        # Guardar clave privada (formato que espera el cliente)
        priv_path = f"certificados/{rol}_privada.pem"
        with open(priv_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Guardar clave pública (formato que espera el broker)
        public_key = private_key.public_key()
        pub_path = f"certificados/{rol}_publica.pem"
        with open(pub_path, "wb") as f:
            f.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
        
        print(f"✅ Certificados generados para rol: {rol}")
        print(f"   - Privada: {priv_path}")
        print(f"   - Pública: {pub_path}")
    
    # También mantener el archivo empleado_certificado_publico.pem por compatibilidad
    if os.path.exists("certificados/medico_publica.pem"):
        import shutil
        shutil.copy("certificados/medico_publica.pem", "certificados/empleado_certificado_publico.pem")
        print(f"\n📋 Copia de seguridad creada: empleado_certificado_publico.pem")

if __name__ == "__main__":
    print("=" * 50)
    print("🔐 Generando certificados para todos los roles")
    print("=" * 50)
    generar_certificados_para_roles()
    print("\n✅ Listo. Ahora el broker y cliente pueden funcionar correctamente.")