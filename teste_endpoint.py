"""
Teste simples do endpoint /api/messages
"""
import requests
import json

# Dados de uma mensagem de teste
mensagem = {
    "type": "message",
    "text": "oi",
    "from": {
        "id": "user1",
        "name": "Test User"
    },
    "recipient": {
        "id": "bot1",
        "name": "Bot"
    },
    "channelId": "emulator",
    "conversation": {
        "id": "conv1"
    },
    "serviceUrl": "http://localhost:8000"
}

print("🧪 Testando endpoint /api/messages...")
print(f"📤 Enviando: {mensagem['text']}")

try:
    response = requests.post(
        "http://localhost:8000/api/messages",
        json=mensagem,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\n✅ Status: {response.status_code}")
    print(f"📥 Response: {response.text if response.text else 'Vazio (ok para bot)'}")
    
    if response.status_code == 200:
        print("\n🎉 SUCESSO! O endpoint está funcionando!")
    else:
        print(f"\n⚠️ Erro {response.status_code}")
        
except Exception as e:
    print(f"\n❌ Erro ao conectar: {e}")
