"""
Test para verificar la serialización JSON
"""

import json
from flask import Flask, jsonify

app = Flask(__name__)

# Simular la respuesta que debería devolver el endpoint
response_data = {
    'success': True,
    'explicacion': 'Test explicación',
    'diff': [{'search': 'buscar', 'replace': 'reemplazar'}],
    'error': False
}

# Probar jsonify
with app.app_context():
    # Método 1: jsonify directo
    result1 = jsonify(response_data)
    print("Método 1 - jsonify directo:")
    print(f"Tipo: {type(result1)}")
    print(f"Data: {result1.get_json()}")
    print()
    
    # Método 2: jsonify con dict explícito
    result2 = jsonify({
        'success': True,
        'explicacion': response_data['explicacion'],
        'diff': response_data['diff'],
        'error': response_data['error']
    })
    print("Método 2 - jsonify con dict explícito:")
    print(f"Tipo: {type(result2)}")
    print(f"Data: {result2.get_json()}")
    print()
    
    # Método 3: json.dumps
    result3 = json.dumps(response_data)
    print("Método 3 - json.dumps:")
    print(f"Tipo: {type(result3)}")
    print(f"Data: {result3}")
