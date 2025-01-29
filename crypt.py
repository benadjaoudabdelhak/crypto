import mysql.connector
import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
 

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "SecureDataCorp"
}
 
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

key = os.urandom(32)  # 256 bits
iv = os.urandom(16)   # IV de 128 bits
 
def encrypt_data(data):
    """Chiffre les données avec AES-256 en mode CBC."""
    if not data:
        return None  # Gère les valeurs NULL
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    # Padding (AES requiert une longueur multiple de 16)
    padded_data = data.ljust(16 * ((len(data) // 16) + 1))
    ciphertext = encryptor.update(padded_data.encode()) + encryptor.finalize()
    return base64.b64encode(iv + ciphertext).decode()

tables_columns = {
    "patients": ["num_secu", "adresse", "telephone"],
    "dossiers_medicaux": ["diagnostic"],
    "facturation": ["ref_assurance"],
    "analyses_labo": ["type_analyse", "resultats"]
}
 
for table, columns in tables_columns.items():
    for column in columns:
        cursor.execute(f"SELECT id, {column} FROM {table}") 
        rows = cursor.fetchall()
 
        for row_id, data in rows:
            encrypted_data = encrypt_data(data)
            if encrypted_data:
                cursor.execute(f"UPDATE {table} SET {column} = %s WHERE id = %s", (encrypted_data, row_id))
 
conn.commit()
conn.close()
print("🔐 Chiffrement terminé avec succès !")
