import uuid
import time
import random
import string
from datetime import datetime
from config import db, firebase

# ============================================================
# ZONES DISPONIBLES
# ============================================================
ZONES = ["Tunis", "Ariana", "Lac", "Manouba"]

# ============================================================
# CATALOGUE PRODUITS — fallback local si Firebase indisponible
# ============================================================
PRODUCTS_CATALOG_DEFAULT = {
    "Smartphone":  {"poids_kg": 0.3,  "prix_base": 15.0},
    "Laptop":      {"poids_kg": 2.5,  "prix_base": 45.0},
    "Livre":       {"poids_kg": 0.6,  "prix_base": 5.0},
    "Vetements":   {"poids_kg": 1.2,  "prix_base": 10.0},
    "Chaussures":  {"poids_kg": 1.8,  "prix_base": 12.0},
}

# Locker -> Zone mapping (fallback)
LOCKER_ZONES = {
    "locker_1": "Tunis",
    "locker_2": "Ariana",
    "locker_3": "Lac",
    "locker_4": "Manouba",
}

# ============================================================
# GÉNÉRATION TOKEN
# ============================================================

def _generate_token_id() -> str:
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"QR-S1-{suffix}"

# ============================================================
# HELPER — DB authentifiée avec le token utilisateur
# ============================================================

def _db(token=None):
    if token:
        return firebase.database()
    return db

# ============================================================
# PRODUCTS — LUS DEPUIS FIREBASE
# ============================================================

def get_products_catalog(token=None) -> dict:
    """
    Lit le catalogue produits depuis Firebase /products.
    Retourne le fallback local si Firebase indisponible.
    """
    try:
        data = db.child("products").get(token)
        if data.val() and isinstance(data.val(), dict):
            return data.val()
        return PRODUCTS_CATALOG_DEFAULT
    except:
        return PRODUCTS_CATALOG_DEFAULT

def identify_product(product_name: str, token=None):
    """
    Cherche le produit dans Firebase (case-insensitive + partial match).
    Retourne (product_key, product_data) ou (None, None) si non trouvé.
    """
    catalog = get_products_catalog(token)
    name_lower = product_name.strip().lower()

    # Exact match
    for key, data in catalog.items():
        if key.lower() == name_lower:
            return key, data

    # Partial match
    for key, data in catalog.items():
        if name_lower in key.lower() or key.lower() in name_lower:
            return key, data

    return None, None

# ============================================================
# UTILISATEURS / PROFILS
# ============================================================

def get_user_role(user_id, token=None):
    try:
        role_data = _db(token).child("users").child(user_id).child("role").get(token)
        return role_data.val() if role_data.val() else None
    except:
        return None

def get_user_profile(user_id, token=None):
    try:
        data = db.child("users").child(user_id).get(token)
        return data.val() if data.val() else {}
    except:
        return {}

def update_user_profile(user_id, updates: dict, token=None):
    try:
        db.child("users").child(user_id).update(updates, token)
        return True
    except Exception as e:
        print(f"[update_user_profile] error: {e}")
        return False

def register_new_user(user_id, email, name, role, token=None):
    ts   = int(time.time() * 1000)
    data = {
        "email":       email,
        "name":        name,
        "role":        role,
        "displayName": name,
        "status":      "active",
        "createdAt":   ts,
        "zone":        ""
    }
    if token:
        db.child("users").child(user_id).set(data, token)
        db.child("profiles").child(user_id).set(data, token)
    else:
        db.child("users").child(user_id).set(data)
        db.child("profiles").child(user_id).set(data)

def get_random_courrier(token=None, zone=None):
    """
    Récupère un courrier aléatoire.
    Si zone fournie → préfère un courrier de cette zone.
    Sinon → prend n'importe quel courrier disponible.
    """
    try:
        all_users = db.child("users").get(token)
        courriers = []
        if all_users.each():
            for user in all_users.each():
                u = user.val()
                if isinstance(u, dict) and u.get("role") == "courrier":
                    courriers.append({"uid": user.key(), **u})

        if zone:
            # Courriers de la même zone en priorité
            zone_courriers = [c for c in courriers if c.get("zone") == zone]
            if zone_courriers:
                return random.choice(zone_courriers)

        # Fallback: n'importe quel courrier
        return random.choice(courriers) if courriers else None

    except Exception as e:
        print(f"[get_random_courrier] erreur: {e}")
        return None

# ============================================================
# LOCKERS
# ============================================================

def get_lockers(token=None):
    try:
        data = db.child("lockers").get(token)
        if data.val():
            result = {}
            for k, v in data.val().items():
                locker = dict(v)
                if "zone" not in locker:
                    locker["zone"] = LOCKER_ZONES.get(k, "Tunis")
                result[k] = locker
            return result
        return {}
    except:
        return {}

def set_locker_reserved(locker_id, booking_id, token=None):
    db.child("lockers").child(locker_id).update({
        "statut":     "reservé",
        "booking_id": booking_id
    }, token)

def set_locker_available(locker_id, token=None):
    db.child("lockers").child(locker_id).update({
        "statut":     "disponible",
        "booking_id": None
    }, token)

# ============================================================
# BOOKINGS
# ============================================================

def create_booking(user_id, user_email, user_name, locker_id, locker_name,
                   produit, description, token=None,
                   product_data=None, locker_zone=None):

    booking_id      = str(uuid.uuid4())[:8].upper()
    timestamp       = datetime.now().strftime("%d/%m/%Y à %H:%M")
    ts              = int(time.time() * 1000)
    locker_zone_val = locker_zone or LOCKER_ZONES.get(locker_id, "Tunis")

    # Courrier assigné selon la zone du locker
    courrier       = get_random_courrier(token, zone=locker_zone_val)
    courrier_id    = courrier["uid"]          if courrier else ""
    courrier_email = courrier.get("email","") if courrier else ""
    courrier_name  = courrier.get("name", courrier_email) if courrier else "N/A"

    poids_kg  = product_data.get("poids_kg", 0)  if product_data else 0
    prix_base = product_data.get("prix_base", 0) if product_data else 0

    booking_data = {
        "booking_id":     booking_id,
        "user_id":        user_id,
        "user_email":     user_email,
        "user_name":      user_name,
        "locker_id":      locker_id,
        "locker_name":    locker_name,
        "locker_zone":    locker_zone_val,
        "produit":        produit,
        "description":    description,
        "poids_kg":       poids_kg,
        "prix":           prix_base,
        "timestamp":      timestamp,
        "statut":         "en_attente",
        "courrier_id":    courrier_id,
        "courrier_email": courrier_email,
        "courrier_name":  courrier_name,
        "createdAt":      ts,
        "updatedAt":      ts
    }

    db.child("bookings").child(booking_id).set(booking_data, token)
    set_locker_reserved(locker_id, booking_id, token)

    token_id = _generate_token_id()
    db.child("qrTokens").child(token_id).set({
        "bookingId":   booking_id,
        "lockerId":    locker_id,
        "lockerName":  locker_name,
        "lockerZone":  locker_zone_val,
        "sectorId":    "S1",
        "purpose":     "COURIER_DROP",
        "issuedToUid": courrier_id,
        "userEmail":   user_email,
        "produit":     produit,
        "timestamp":   timestamp,
        "expiresAt":   ts + 86400000,
        "usedAt":      ""
    }, token)

    return booking_id, booking_data, token_id, courrier

def get_booking_by_id(booking_id, token=None):
    try:
        return db.child("bookings").child(booking_id).get(token).val()
    except:
        return None

def get_user_bookings(user_id, token=None):
    try:
        data = db.child("bookings").order_by_child("user_id").equal_to(user_id).get(token)
        if not data.val():
            return []
        return [{"id": k, **v} for k, v in data.val().items() if isinstance(v, dict)]
    except:
        return []

def get_bookings_for_courrier(token=None):
    try:
        data = db.child("bookings").get(token)
        if not data.val():
            return []
        bookings = []
        for bid, b in data.val().items():
            if isinstance(b, dict) and b.get("statut") in ["en_attente", "en_cours"]:
                bookings.append({"id": bid, **b})
        return sorted(bookings, key=lambda x: x.get("timestamp",""), reverse=True)
    except:
        return []

def get_all_delivered_bookings(token=None):
    try:
        data = db.child("bookings").get(token)
        if not data.val():
            return []
        all_b = [{"id": k, **v} for k, v in data.val().items() if isinstance(v, dict)]
        return [b for b in all_b if b.get("statut") == "livré"]
    except:
        return []

def update_booking_status(booking_id, new_status, token=None):
    db.child("bookings").child(booking_id).update({
        "statut":    new_status,
        "updatedAt": int(time.time() * 1000)
    }, token)

# ============================================================
# QR TOKENS
# ============================================================

def get_courrier_tokens(courrier_id, token=None):
    try:
        data = db.child("qrTokens").order_by_child("issuedToUid").equal_to(courrier_id).get(token)
        if not data.val():
            return {}
        return {k: v for k, v in data.val().items() if isinstance(v, dict)}
    except:
        return {}

def mark_token_used(token_id, booking_id, token=None):
    ts = int(time.time() * 1000)
    db.child("qrTokens").child(token_id).update({"usedAt": ts}, token)
    if booking_id:
        db.child("bookings").child(booking_id).update({
            "statut":    "livré",
            "updatedAt": ts
        }, token)
