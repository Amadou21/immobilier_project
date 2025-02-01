
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import pymysql
#from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)


# Configuration de la base de données MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Utilisateur MySQL
app.config['MYSQL_PASSWORD'] = ''  # Mot de passe MySQL
app.config['MYSQL_DB'] = 'customers_base'  # Base de données MySQL
# mysql = MySQL(app)
app.config['SECRET_KEY'] = 'your_secret_key' 
# Initialisation de l'extension MySQL
#mysql = MySQL(app)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:@localhost/customers_base'
#db = SQLAlchemy(app)

methods=['POST', 'PUT', 'GET', 'PATCH', 'DELETE']

def get_db():
    return pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB'],
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/', methods=['GET'])
def list_customers():
    per_page = int(request.args.get('per_page', 10))
    page = int(request.args.get('page', 1))
    offset = (page - 1) * per_page
    
    # Récupération d'une connexion à la base de données && Création d'un curseur pour exécuter des requêtes SQL
    cur = get_db().cursor()
    cur.execute(f"SELECT * FROM client LIMIT {offset}, {per_page}")
    customers = cur.fetchall()

    # Compter le nombre total de lignes
    cur.execute("SELECT COUNT(*) FROM client")
    total_customers = 1000 #cur.fetchone()[0]
    
    total_pages = (total_customers // per_page) + (total_customers % per_page > 0)
    
    return render_template('index.html', customers=customers, page=page, per_page=per_page, total_pages=total_pages)

@app.route('/create', methods=['GET'])
def add_form ():
    return render_template('create.html')

@app.route('/add', methods=['POST'])
def add_client_form ():
    if request.method == 'POST':  # Check if the request method is POST
        nom = request.form['nom']  # Access form field value using dictionary access
        prenom = request.form['prenom']
        cur = get_db().cursor()
        cur.execute("INSERT INTO client(nom, prenom) VALUES (%s, %s)", (nom, prenom))
        cur.connection.commit()
        return redirect(url_for('list_customers'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_form(id, nom = None, prenom = None):
    cur = get_db().cursor()
    if request.method == 'GET':
        cur.execute("SELECT * FROM client WHERE id = %s", (id,))
        customer = cur.fetchone()
        return render_template('edit.html', customer=customer)
    elif request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        cur.execute("UPDATE client SET nom=%s, prenom=%s WHERE id=%s", (nom, prenom, id))
        cur.connection.commit()
        return redirect(url_for('list_customers')) 
    
@app.route('/delete/<int:id>', methods=['GET'])
def delete_customer(id):
    cur = get_db().cursor()
    cur.execute("DELETE FROM client WHERE id = %s", (id))
    cur.connection.commit()
    return redirect(url_for('list_customers'))

#from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import IntegerField, BooleanField, SubmitField, RadioField
import pickle
import os
model_path = os.path.join(os.path.dirname(__file__), 'model', 'model.pkl')
# Charger le modèle
with open(model_path, 'rb') as f:
    lm = pickle.load(f)

class PredictionForm(FlaskForm):
    area = IntegerField('Superficie')
    bedrooms = IntegerField('Chambres')
    bathrooms = IntegerField('Salles de bain')
    stories = IntegerField('Étages')
    mainroad = BooleanField('Accès à la route principale')
    guestroom = BooleanField('Chambre d\'amis')
    basement = BooleanField('Sous-sol')
    hotwaterheating = BooleanField('Chauffage à eau chaude')
    airconditioning = BooleanField('Climatisation')
    parking = IntegerField('Places de parking')
    prefarea = BooleanField('Quartier privilégié')
    # RadioField avec les bonnes valeurs pour semi-furnished et unfurnished
    semi_furnished = RadioField(
        'Meubles',
        choices=[('00', 'Meublé'), ('01', 'Non-meublé'), ('10', 'Semi-meublé')],
        default='01'  # Valeur par défaut "Non-meublé"
    )

    submit = SubmitField('Prédire')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    form = PredictionForm()
    if form.validate_on_submit():
        # Récupérer les données du formulaire
        data = [
            int(form.area.data),
            int(form.bedrooms.data),
            int(form.bathrooms.data),
            int(form.stories.data),
            int(form.mainroad.data),  # Convertir Boolean en entier (0 ou 1)
            int(form.guestroom.data),
            int(form.basement.data),
            int(form.hotwaterheating.data),
            int(form.airconditioning.data),
            int(form.parking.data),
            int(form.prefarea.data)
        ]
        
        # Récupérer la valeur du champ semi_furnished
        semi_furnished_value = form.semi_furnished.data
        
        # Décomposer en semi_furnished_value et unfurnished_value
        if semi_furnished_value == '10':
            data.append(1)  # Semi-meublé -> semi_furnished_value = 1
            data.append(0)  # Non-meublé -> unfurnished_value = 0
        elif semi_furnished_value == '01':
            data.append(0)  # Non-meublé -> semi_furnished_value = 0
            data.append(1)  # Non-meublé -> unfurnished_value = 1
        else:
            data.append(0)  # Meublé -> semi_furnished_value = 0
            data.append(0)  # Meublé -> unfurnished_value = 0

        # Préparer les données pour le modèle
        data = [data]  # Mettre les données dans le format attendu par votre modèle
        
        # Faire la prédiction
        prediction = lm.predict(data)[0]
        
        prediction_fcfa = prediction * 7

        # Insérer les détails dans la base de données
        cur = get_db().cursor()
        cur.execute("""
            INSERT INTO houseDetails (area, bedrooms, bathrooms, stories, mainroad, guestroom, 
                                      basement, hotwaterheating, airconditioning, parking, prefarea, 
                                      semi_furnished, unfurnished, price) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            form.area.data, 
            form.bedrooms.data, 
            form.bathrooms.data, 
            form.stories.data, 
            form.mainroad.data, 
            form.guestroom.data, 
            form.basement.data, 
            form.hotwaterheating.data, 
            form.airconditioning.data, 
            form.parking.data, 
            form.prefarea.data, 
            1 if semi_furnished_value == '10' else 0, 
            1 if semi_furnished_value == '01' else 0, 
            prediction_fcfa
        ))
        cur.connection.commit()

        return render_template('result.html', prediction=prediction)

    return render_template('predict.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)