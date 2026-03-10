import uuid
from datetime import datetime
from config import db

# ============================================================
# UTILISATEURS
# ============================================================
def get_user_role(user_id):
    """Récupère le rôle d'un utilisateur depuis Firebase."""
    try:
        role_data = db.child("users").child(user_id).child("role").get()
        return role_data.val() if role_data.val() else None
    except:
        return None

def register_new_user(user_id, email, name, role):
    """Enregistre un nouvel utilisateur dans Firebase."""
    db.child("users").child(user_id).set({
        "email": email,
        "name": name,
        "role": role
    })

# ============================================================
# LOCKERS
# ============================================================
def get_lockers():
    """Récupère tous les lockers depuis Firebase."""
    try:
        data = db.child("lockers").get()
        if data.val():
            return {k: v for k, v in data.val().items()}
        return {}
    except:
        return {}

def set_locker_reserved(locker_id, booking_id):
    """Met un locker en statut réservé."""
    db.child("lockers").child(locker_id).update({
        "statut": "reservé",
        "booking_id": booking_id
    })

def set_locker_available(locker_id):
    """Libère un locker — le remet disponible."""
    db.child("lockers").child(locker_id).update({
        "statut": "disponible",
        "booking_id": None
    })

# ============================================================
# BOOKINGS (COMMANDES)
# ============================================================
def create_booking(user_id, user_email, user_name, locker_id, locker_name, produit, description):
    """Crée une réservation et met à jour le locker."""
    booking_id = str(uuid.uuid4())[:8].upper()
    timestamp = datetime.now().strftime("%d/%m/%Y à %H:%M")

    booking_data = {
        "booking_id": booking_id,
        "user_id": user_id,
        "user_email": user_email,
        "user_name": user_name,
        "locker_id": locker_id,
        "locker_name": locker_name,
        "produit": produit,
        "description": description,
        "timestamp": timestamp,
        "statut": "en_attente"
    }

    db.child("bookings").child(booking_id).set(booking_data)
    set_locker_reserved(locker_id, booking_id)

    return booking_id, booking_data

def get_booking_by_id(booking_id):
    """Récupère une commande par son ID."""
    try:
        return db.child("bookings").child(booking_id).get().val()
    except:
        return None

def get_user_bookings(user_id):
    """Récupère toutes les commandes d'un utilisateur."""
    try:
        data = db.child("bookings").order_by_child("user_id").equal_to(user_id).get()
        if not data.val():
            return []
        return [{"id": k, **v} for k, v in data.val().items() if isinstance(v, dict)]
    except:
        return []

def get_bookings_for_courrier():
    """Récupère toutes les commandes en attente ou en cours."""
    try:
        data = db.child("bookings").get()
        if not data.val():
            return []
        bookings = []
        for bid, b in data.val().items():
            if isinstance(b, dict) and b.get("statut") in ["en_attente", "en_cours"]:
                bookings.append({"id": bid, **b})
        return sorted(bookings, key=lambda x: x.get("timestamp", ""), reverse=True)
    except:
        return []

def get_all_delivered_bookings():
    """Récupère toutes les commandes livrées (historique)."""
    try:
        data = db.child("bookings").get()
        if not data.val():
            return []
        all_b = [{"id": k, **v} for k, v in data.val().items() if isinstance(v, dict)]
        return [b for b in all_b if b.get("statut") == "livré"]
    except:
        return []

def update_booking_status(booking_id, new_status):
    """Met à jour le statut d'une commande."""
    db.child("bookings").child(booking_id).update({"statut": new_status})
