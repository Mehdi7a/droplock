import pyrebase

# ============================================================
# CONFIGURATION FIREBASE
# ============================================================
firebaseConfig = {
    "apiKey": "AIzaSyAU5wXJk-NZBgaYAEJ1Uw9bhsAyGQPyAd0",
    "authDomain": "droplock-b2d6a.firebaseapp.com",
    "databaseURL": "https://droplock-b2d6a-default-rtdb.europe-west1.firebasedatabase.app/",
    "projectId": "droplock-b2d6a",
    "storageBucket": "droplock-b2d6a.firebasestorage.app",
    "messagingSenderId": "1066803026351",
    "appId": "1:1066803026351:web:69035a441d86e0e03ff75a",
    "measurementId": "G-G70SLWBK4L"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()

# ============================================================
# CONFIGURATION GMAIL DROPLOCK
# ============================================================
GMAIL_SENDER   = "droplock.app@gmail.com"
GMAIL_APP_PASS = "vtkf lbgq wkwi crnh"
