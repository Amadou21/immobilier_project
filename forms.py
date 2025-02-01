from flask_wtf import FlaskForm
from wtforms import IntegerField, BooleanField, SubmitField

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
    semi_furnished = BooleanField('Semi-meublé')
    unfurnished = BooleanField('Non meublé')
    submit = SubmitField('Prédire')