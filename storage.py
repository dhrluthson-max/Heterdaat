# storage.py
import os
import base64
import sqlite3
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Vaste geheime sleutel en zout voor de AES-versleuteling
WAGTWOORD = b"VeiligRuimteGeheimeSleutel2026!"
ZOUT = b"UniekEnVeiligZoutHiertegenSpam"

def genereer_sleutel():
    """Genereert een stabiele AES-sleutel op basis van het wachtwoord."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=ZOUT,
        iterations=100000
    )
    return base64.urlsafe_b64encode(kdf.derive(WAGTWOORD))

# Initialiseer de encryptie-engine
fernet = Fernet(genereer_sleutel())

def krijg_verbinding():
    """Maakt verbinding met de standaard SQLite database."""
    data_dir = os.environ.get('ANDROID_PRIVATE_DATA', '.')
    db_path = os.path.join(data_dir, "veiligruimte_safe.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Sla de tekst op als BLOB of TEXT (versleutelde base64 string)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tekst TEXT NOT NULL,
            datum DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def sla_notitie_op(tekst):
    """Versleutelt de tekst met AES-256 en slaat deze op."""
    try:
        # Versleutel de invoer
        versleutelde_tekst = fernet.encrypt(tekst.encode()).decode()
        
        conn = krijg_verbinding()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notities (tekst) VALUES (?)", (versleutelde_tekst,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("Fout bij opslaan:", e)
        return False

def haal_notities_op():
    """Haalt de notities op en ontsleutelt deze realtime."""
    try:
        conn = krijg_verbinding()
        cursor = conn.cursor()
        cursor.execute("SELECT tekst, datum FROM notities ORDER BY datum DESC")
        resultaten = cursor.fetchall()
        conn.close()
        
        ontsleutelde_lijst = []
        for rij in resultaten:
            try:
                # Ontsleutel de base64 string terug naar platte tekst
                klare_tekst = fernet.decrypt(rij[0].encode()).decode()
                ontsleutelde_lijst.append((klare_tekst, rij[1]))
            except:
                # Als het ontsleutelen faalt (bijv. verkeerde sleutel), sla over
                continue
                
        return ontsleutelde_lijst
    except Exception as e:
        print("Fout bij ophalen:", e)
        return []
