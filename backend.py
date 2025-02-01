from flask import Flask, request, jsonify
import pymysql

backend = Flask(__name__)

# Configuration de la base de données MySQL
backend.config['MYSQL_HOST'] = 'localhost'
backend.config['MYSQL_USER'] = 'root'  # Utilisateur MySQL
backend.config['MYSQL_PASSWORD'] = ''  # Mot de passe MySQL
backend.config['MYSQL_DB'] = 'customers_base'  # Base de données MySQL

# Méthodes HTTP autorisées
methods = ['POST', 'PUT', 'GET', 'PATCH', 'DELETE']

# Fonction pour se connecter à la base de données
def get_db():
    return pymysql.connect(
        host=backend.config['MYSQL_HOST'],
        user=backend.config['MYSQL_USER'],
        password=backend.config['MYSQL_PASSWORD'],
        db=backend.config['MYSQL_DB'],
        cursorclass=pymysql.cursors.DictCursor
    )

# Route pour récupérer toutes les données de reporting
@backend.route('/index', methods=['GET'])
def index():
    try:
        # Connexion à la base de données
        cur = get_db().cursor()
        
        # Requête SQL pour récupérer toutes les données de la table `reporting`
        cur.execute("""
            SELECT id, type_bien, type_transaction, week, month, year, predicted_price
            FROM reporting
        """)
        
        # Récupération des résultats
        reportings = cur.fetchall()
        
        # Fermeture du curseur
        cur.close()
        
        # Retourner les données au format JSON
        return jsonify(reportings)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route pour récupérer une entrée spécifique par son ID
@backend.route('/data/<int:id>', methods=['GET'])
def get_reporting(id):
    try:
        # Connexion à la base de données
        cur = get_db().cursor()
        
        # Requête SQL pour récupérer une entrée spécifique
        cur.execute("""
            SELECT id, type_bien, type_transaction, week, month, year, predicted_price
            FROM reporting
            WHERE id = %s
        """, (id,))
        
        # Récupération du résultat
        reporting = cur.fetchone()
        
        # Fermeture du curseur
        cur.close()
        
        # Vérifier si l'entrée existe
        if reporting:
            return jsonify(reporting)
        else:
            return jsonify({'message': 'Entrée non trouvée'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route pour ajouter une nouvelle entrée (POST)
@backend.route('/data', methods=['POST'])
def add_reporting():
    try:
        # Récupérer les données du corps de la requête
        data = request.json
        type_bien = data.get('type_bien')
        type_transaction = data.get('type_transaction')
        week = data.get('week')
        month = data.get('month')
        year = data.get('year')
        predicted_price = data.get('predicted_price')
        
        # Vérifier que toutes les données sont présentes
        if not all([type_bien, type_transaction, week, month, year, predicted_price]):
            return jsonify({'error': 'Tous les champs sont obligatoires'}), 400
        
        # Connexion à la base de données
        cur = get_db().cursor()
        
        # Requête SQL pour insérer une nouvelle entrée
        cur.execute("""
            INSERT INTO reporting (type_bien, type_transaction, week, month, year, predicted_price)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (type_bien, type_transaction, week, month, year, predicted_price))
        
        # Valider la transaction
        cur.connection.commit()
        
        # Fermeture du curseur
        cur.close()
        
        return jsonify({'message': 'Entrée ajoutée avec succès'}), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route pour mettre à jour une entrée (PUT)
@backend.route('/data/<int:id>', methods=['PUT'])
def update_reporting(id):
    try:
        # Récupérer les données du corps de la requête
        data = request.json
        type_bien = data.get('type_bien')
        type_transaction = data.get('type_transaction')
        week = data.get('week')
        month = data.get('month')
        year = data.get('year')
        predicted_price = data.get('predicted_price')
        
        # Vérifier que toutes les données sont présentes
        if not all([type_bien, type_transaction, week, month, year, predicted_price]):
            return jsonify({'error': 'Tous les champs sont obligatoires'}), 400
        
        # Connexion à la base de données
        cur = get_db().cursor()
        
        # Requête SQL pour mettre à jour une entrée
        cur.execute("""
            UPDATE reporting
            SET type_bien = %s, type_transaction = %s, week = %s, month = %s, year = %s, predicted_price = %s
            WHERE id = %s
        """, (type_bien, type_transaction, week, month, year, predicted_price, id))
        
        # Valider la transaction
        cur.connection.commit()
        
        # Fermeture du curseur
        cur.close()
        
        return jsonify({'message': 'Entrée mise à jour avec succès'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route pour supprimer une entrée (DELETE)
@backend.route('/data/<int:id>', methods=['DELETE'])
def delete_reporting(id):
    try:
        # Connexion à la base de données
        cur = get_db().cursor()
        
        # Requête SQL pour supprimer une entrée
        cur.execute("DELETE FROM reporting WHERE id = %s", (id,))
        
        # Valider la transaction
        cur.connection.commit()
        
        # Fermeture du curseur
        cur.close()
        
        return jsonify({'message': 'Entrée supprimée avec succès'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Démarrer l'application Flask
if __name__ == '__main__':
    backend.run(debug=True)