"""
Servidor mínimo para probar el problema de serialización
"""

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/test1')
def test1():
    """Devuelve estructura simple"""
    return jsonify({
        'success': True,
        'explicacion': 'Test explicación',
        'diff': [{'search': 'buscar', 'replace': 'reemplazar'}]
    })

@app.route('/test2')
def test2():
    """Devuelve estructura anidada"""
    return jsonify({
        'success': True,
        'suggestion': {
            'explicacion': 'Test explicación anidada',
            'diff': [{'search': 'buscar', 'replace': 'reemplazar'}]
        }
    })

if __name__ == '__main__':
    print("Servidor de prueba en http://localhost:5003")
    app.run(port=5003, debug=False)
