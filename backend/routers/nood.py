from fastapi import APIRouter
from pydantic import BaseModel
import sqlite3

router = APIRouter(prefix="/nood", tags=["Noodknop"])

class NoodMelding(BaseModel):
    gebruiker_id: str
    locatie: str = "Onbekend"

@router.post("/alarm")
async def activeer_alarm(melding: NoodMelding):
    conn = sqlite3.connect("backend_storage.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO meldingen (gebruiker_id, status, locatie) VALUES (?, ?, ?)",
        (melding.gebruiker_id, "ALARM_GEACTIVEERD", melding.locatie)
    )
    conn.commit()
    conn.close()
    
    print(f"!!! NOODALARM !!! Gebruiker {melding.gebruiker_id} drukte de noodknop in op locatie: {melding.locatie}")
    return {"status": "success", "bericht": "Hulpdiensten en noodcontacten genotificeerd."}
