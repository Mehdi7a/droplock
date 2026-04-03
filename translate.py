import sys
import os

files = {
    "c:/Users/Dell/Desktop/droplock/auth.py": {
        'st.error("❌ Compte introuvable. Recréez un compte.")': 'st.error("❌ Account not found. Please create an account.")',
        '<div class="subtitle">Connectez-vous à votre compte</div>': '<div class="subtitle">Log in to your account</div>',
        'placeholder="exemple@email.com"': 'placeholder="example@email.com"',
        '("🔑 Mot de passe"': '("🔑 Password"',
        '("🚀 Se connecter"': '("🚀 Log in"',
        '("⚠️ Remplissez tous les champs.")': '("⚠️ Please fill in all fields.")',
        '("❌ Mot de passe incorrect.")': '("❌ Incorrect password.")',
        '("❌ Email introuvable.")': '("❌ Email not found.")',
        '("❌ Trop de tentatives. Réessayez plus tard.")': '("❌ Too many attempts. Try again later.")',
        'f"❌ Erreur connexion : {err}"': 'f"❌ Connection error: {err}"',
        '<div class="separator">─── ou ───</div>': '<div class="separator">─── or ───</div>',
        '("✏️ Créer un compte"': '("✏️ Create an account"',
        '<div class="title">✏️ Créer un compte</div>': '<div class="title">✏️ Create an account</div>',
        '<div class="subtitle">Rejoignez Droplock</div>': '<div class="subtitle">Join Droplock</div>',
        'placeholder="Minimum 6 caractères"': 'placeholder="Minimum 6 characters"',
        '("🔑 Confirmer"': '("🔑 Confirm"',
        '"👤 Je suis..."': '"👤 I am..."',
        '"📦 Utilisateur (je reçois des colis)"': '"📦 User (I receive packages)"',
        '"🚚 Agent Courrier (je livre des colis)"': '"🚚 Courier (I deliver packages)"',
        '("✅ Créer mon compte"': '("✅ Create my account"',
        '("❌ Les mots de passe ne correspondent pas.")': '("❌ Passwords do not match.")',
        '("❌ Minimum 6 caractères.")': '("❌ Minimum 6 characters.")',
        '("❌ Email déjà utilisé.")': '("❌ Email already used.")',
        '("❌ Mot de passe trop faible (min. 6 caractères).")': '("❌ Password too weak (min. 6 characters).")',
        '("❌ Adresse email invalide.")': '("❌ Invalid email address.")',
        'f"❌ Erreur Auth : {err}"': 'f"❌ Auth Error: {err}"',
        '"⚠️ Compte Auth créé mais erreur DB : {str(e)}\\n"': '"⚠️ Auth account created but DB error: {str(e)}\\n"',
        '"Vérifiez les règles Realtime Database Firebase."': '"Check Firebase Realtime Database rules."',
        '("✅ Compte créé ! Connectez-vous.")': '("✅ Account created! Log in.")',
        '("⬅️ Retour au login"': '("⬅️ Back to log in"'
    },
    "c:/Users/Dell/Desktop/droplock/page_courrier.py": {
        '<h2>🚚 Espace Courrier</h2>': '<h2>🚚 Courier Space</h2>',
        '<span class="role-badge badge-courrier">📬 Agent Courrier</span>': '<span class="role-badge badge-courrier">📬 Courier Agent</span>',
        '["🎫 Mes QR Codes", "📦 Livraisons", "✅ Historique"]': '["🎫 My QR Codes", "📦 Deliveries", "✅ History"]',
        '("🚪 Se déconnecter"': '("🚪 Log out"',
        'st.subheader("🎫 Mes QR Codes")': 'st.subheader("🎫 My QR Codes")',
        '("🔄 Actualiser"': '("🔄 Refresh"',
        '("📭 Aucun QR code assigné pour le moment.")': '("📭 No QR code assigned at the moment.")',
        '("Les QR codes apparaissent ici dès qu\\'un utilisateur fait une commande.")': '("QR codes will appear here once a user makes an order.")',
        '("📦 Total"': '("📦 Total"',
        '("✅ Utilisés"': '("✅ Used"',
        '("⏳ En attente"': '("⏳ Pending"',
        '"❌ Déjà utilisé"': '"❌ Already used"',
        '"✅ Non utilisé"': '"✅ Not used"',
        '📦 Booking :': '📦 Booking:',
        '🔒 Locker  :': '🔒 Locker:',
        '👤 Client  :': '👤 Client:',
        '🛍️ Produit :': '🛍️ Product:',
        '📅 Date    :': '📅 Date:',
        'Statut :': 'Status:',
        'caption=f"Token : {token_id}"': 'caption=f"Token: {token_id}"',
        '("✅ Marquer comme utilisé"': '("✅ Mark as used"',
        '✅ Token {token_id} marqué comme utilisé !': '✅ Token {token_id} marked as used!',
        'st.subheader("📦 Commandes en attente")': 'st.subheader("📦 Pending orders")',
        '("✅ Aucune livraison en attente.")': '("✅ No deliveries pending.")',
        '**{len(bookings)} livraison(s) à traiter**': '**{len(bookings)} deliveries to process**',
        '**👤 Client :**': '**👤 Client:**',
        '**📧 Email :**': '**📧 Email:**',
        '**🛍️ Produit :**': '**🛍️ Product:**',
        '**📝 Description :**': '**📝 Description:**',
        '**🔒 Locker :**': '**🔒 Locker:**',
        '**📅 Commande :**': '**📅 Order:**',
        '**🟡 Statut :**': '**🟡 Status:**',
        '**📱 QR Code**': '**📱 QR Code**',
        '("QR indisponible")': '("QR unavailable")',
        '("Installez qrcode[pil]")': '("Install qrcode[pil]")',
        '("🚚 En cours"': '("🚚 In progress"',
        '("✅ Mis à jour !")': '("✅ Updated!")',
        '("✅ Livré"': '("✅ Delivered"',
        '("✅ Livraison confirmée ! Locker libéré.")': '("✅ Delivery confirmed! Locker released.")',
        'st.subheader("✅ Historique des livraisons")': 'st.subheader("✅ Delivery history")',
        '("Aucune livraison terminée.")': '("No completed deliveries.")',
        '**{len(done)} livraison(s) effectuée(s)**': '**{len(done)} delivery(ies) completed**',
        '>Livré<': '>Delivered<'
    }
}

for filepath, replacements in files.items():
    if not os.path.exists(filepath):
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    for old, new in replacements.items():
        content = content.replace(old, new)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
print("Translation complete.")

