import iss_ai

print("Configuration de la clé Groq")
print("")
key = input("Colle ta clé : ").strip()

if key.startswith("gsk_"):
    iss_ai.set_api_key(key)
    print("✅ Clé enregistrée !")
    print(iss_ai.test())
else:
    print("❌ Clé invalide (doit commencer par gsk_)")
