"""
Test script pour le flow LMNP Liasse
Lance l'authentification puis la génération de la liasse fiscale
"""
import requests
import json
import time

# Configuration hardcodée
BASE_URL = "http://localhost:8000"
EMAIL = "outrunner@live.fr"
PASSWORD = "Password123"
FISCAL_YEAR = 2025

def main():
    print("=" * 60)
    print("TEST FLOW LMNP LIASSE")
    print("=" * 60)
    print()
    
    # ÉTAPE 1 : Authentification
    print("🔐 Étape 1 : Authentification...")
    auth_url = f"{BASE_URL}/api/authenticate"
    auth_payload = {
        "email": EMAIL,
        "password": PASSWORD,
        "create": False
    }
    
    try:
        auth_response = requests.post(auth_url, json=auth_payload)
        auth_response.raise_for_status()
        auth_data = auth_response.json()
        
        if not auth_data.get("success"):
            print(f"❌ Échec de l'authentification : {auth_data}")
            return
        
        token = auth_data.get("token")
        print(f"✅ Authentification réussie")
        print(f"   Action : {auth_data.get('action')}")
        print(f"   Token : {token[:50]}...")
        print()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de l'authentification : {e}")
        return
    
    # ÉTAPE 2 : Génération de la liasse
    print("📄 Étape 2 : Génération de la liasse fiscale...")
    liasse_url = f"{BASE_URL}/api/lmnp/data/{FISCAL_YEAR}/generate-liasse-direct"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        liasse_response = requests.post(liasse_url, headers=headers)
        liasse_response.raise_for_status()
        liasse_data = liasse_response.json()
        
        print(f"📊 Résultat :")
        print(json.dumps(liasse_data, indent=2, ensure_ascii=False))
        print()
        
        if liasse_data.get("success"):
            print(f"✅ PDF généré : {liasse_data.get('cerfa_2031')}")
        else:
            print(f"❌ Échec : {liasse_data.get('error', 'Unknown')}")
        
        print("="*60)
        print("✅ TEST TERMINÉ")
        print("="*60)
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la génération : {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Détails : {e.response.text}")
        return

if __name__ == "__main__":
    main()
