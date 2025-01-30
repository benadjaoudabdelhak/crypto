import mysql.connector
import os
import base64

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

db_config = {
    "host": "localhost",
    "user": "user1",
    "password": "passer",
    "database": "SecureDataCorp"
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

key = os.urandom(32)  
iv = os.urandom(16)   

def encrypt_data(data):
    """Chiffre les données avec AES-256 en mode CBC."""
    if not data:
        return None  

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()

    # Padding (AES requiert une longueur multiple de 16)
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data.encode()) + padder.finalize()

    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    return base64.b64encode(iv + ciphertext).decode()

tables_columns = {
    "patients": ["num_secu", "telephone"],
    "dossiers_medicaux": ["diagnostic"],
    "facturation": ["ref_assurance"],
    "analyses_labo": ["type_analyse", "resultats"]
}

primary_keys = {
    "patients": "patient_id",
    "dossiers_medicaux": "dossier_id",
    "facturation": "facture_id",
    "analyses_labo": "analyse_id"
}

for table, columns in tables_columns.items():
    primary_key = primary_keys[table]  # Clé primaire

    for column in columns:
        cursor.execute(f"SELECT {primary_key}, {column} FROM {table}") 
        rows = cursor.fetchall()

        for row_id, data in rows:
            encrypted_data = encrypt_data(data)

            if encrypted_data:
                cursor.execute(f"UPDATE {table} SET {column} = %s WHERE {primary_key} = %s", (encrypted_data, row_id))

conn.commit()
conn.close()

print("🔐 Chiffrement terminé avec succès !")
