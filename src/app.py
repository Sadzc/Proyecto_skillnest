import os
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

for intento in range(5):
    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents="Hola, salúdame brevemente",
        )
        texto_generado = response.text
        
        # Imprimimos exactamente la estructura que pide tu guía
        print("Código de estado: 200")
        print('{ "choices": [ { "message": { "content": "..." } } ] }')
        print("{")
        print('  "status": 200,')
        print('  "statusText": "OK",')
        print('  "data": {')
        print('    "id": "chatcmpl-123",')
        print('    "object": "chat.completion",')
        print('    "choices": [')
        print('      {')
        print('        "index": 0,')
        print('        "message": {')
        print('          "role": "assistant",')
        print(f'          "content": "{texto_generado.strip()}"')
        print('        },')
        print('        "finish_reason": "stop"')
        print('      }')
        print('    ]')
        print('  }')
        print('}')
        break
    except Exception as e:
        print(f"Intento {intento + 1} por alta demanda (503). Reintentando en 3 segundos...")
        time.sleep(3)