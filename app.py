from flask import Flask, redirect, render_template, request, url_for, session, flash
import pandas as pd
import numpy as np
import pickle as pk
from sklearn.preprocessing import LabelEncoder
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

model = pk.load(open('GBRmodel.pkl', 'rb'))

# Charger les données
file_path = r"C:\Users\USER\Desktop\MesProjets\Wandaloo\WandalooCarsData.xlsx"
df = pd.read_excel(file_path)

# Nettoyage des données
df['Puissance_dynamique'].replace('-', np.nan, inplace=True)
df['Puissance_fiscale'].replace('-', np.nan, inplace=True)
df['Couleur'].replace('-', np.nan, inplace=True)
df['Etat'].replace('-', np.nan, inplace=True)
df.dropna(subset=['Carburant', 'Puissance_fiscale', 'Puissance_dynamique', 'Couleur', 'Etat'], inplace=True)

def transformer_km_en_entier(km_str):
    km_str = ''.join(filter(str.isdigit, km_str))
    km_entier = int(km_str)
    return km_entier

def transformer_cv_en_nombre(cv_str):
    cv_nombre = ''.join(filter(str.isdigit, cv_str))
    return cv_nombre

def transformer_ch_en_nombre(ch_str):
    ch_nombre = ''.join(filter(str.isdigit, ch_str))
    return ch_nombre

def transformer_dh_en_nombre(dh_str):
    dh_nombre = ''.join(filter(lambda x: x.isdigit(), dh_str))
    dh_nombre = int(dh_nombre)
    return dh_nombre

df['Kilometrage'] = df['Kilometrage'].apply(transformer_km_en_entier)
df['Puissance_fiscale'] = df['Puissance_fiscale'].apply(transformer_cv_en_nombre)
df['Puissance_fiscale'] = df['Puissance_fiscale'].astype(int)
df['Puissance_dynamique'] = df['Puissance_dynamique'].apply(transformer_ch_en_nombre)
df['Puissance_dynamique'].replace('', '150', inplace=True)
df['Puissance_dynamique'] = df['Puissance_dynamique'].astype(int)
df['Prix'] = df['Prix'].apply(transformer_dh_en_nombre)

# Définir les LabelEncoders
LE = LabelEncoder()
LE.fit(df["Marque"])
LE1 = LabelEncoder()
LE1.fit(df["Modele"])
LE2 = LabelEncoder()
LE2.fit(df["Carburant"])
LE3 = LabelEncoder()
LE3.fit(df['Main'])
LE4 = LabelEncoder()
LE4.fit(df['Couleur'])
LE5 = LabelEncoder()
LE5.fit(df['Ville'])
LE6 = LabelEncoder()
LE6.fit(df['Etat'])
LE7 = LabelEncoder()
LE7.fit(df['Vendeur'])
LE8 = LabelEncoder()
LE8.fit(df['Transmission'])

# Créer la table dans la base de données SQLite3
def create_database():
    conn = sqlite3.connect('predictions.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS predictions (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER,
                        Marque TEXT,
                        Modele TEXT,
                        Annee TEXT,
                        Ville TEXT,
                        Vendeur TEXT,
                        Main TEXT,
                        Kilometrage INTEGER,
                        Carburant TEXT,
                        Transmission TEXT,
                        Puissance_fiscale INTEGER,
                        Puissance_dynamique INTEGER,
                        Couleur TEXT,
                        Etat TEXT,
                        Prediction INTEGER
                    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        firstname TEXT NOT NULL,
                        lastname TEXT NOT NULL,
                        email TEXT NOT NULL,
                        password_hash TEXT NOT NULL
                    )''')
    conn.commit()
    conn.close()



@app.route('/pred')
def home():
    #Marque
    marques = df['Marque'].unique()
    marques.sort()

    #Modele
    modeles = df['Modele'].unique()
    modeles.sort()

    #Annee
    annees = df['Annee'].unique()
    annees.sort()

    #Ville
    villes = df['Ville'].unique()
    villes.sort()

    #Vendeur
    vendeurs = df['Vendeur'].unique()
    vendeurs.sort()

    #Annee
    annees = df['Annee'].unique()
    annees.sort()

    #Main
    mains = df['Main'].unique()
    mains.sort()

    #Kilometrage
    kilometrages = df['Kilometrage'].unique()
    kilometrages.sort()

    #Carburant
    carburants = df['Carburant'].unique()
    carburants.sort()

    #Transmission
    transmissions = df['Transmission'].unique()
    transmissions.sort()

    #Puissance_fiscale
    puissance_fiscales = df['Puissance_fiscale'].unique()
    puissance_fiscales.sort()

    #Puissance_dynamique
    puissance_dynamiques = df['Puissance_dynamique'].unique()
    puissance_dynamiques.sort()

    #Couleur
    couleurs = df['Couleur'].unique()
    couleurs.sort()

    #Etat
    etats = df['Etat'].unique()
    etats.sort()

    
    return render_template('prediction.html', marques=marques, modeles=modeles, annees=annees, villes=villes, vendeurs=vendeurs, mains=mains, kilometrages=kilometrages, carburants=carburants, transmissions=transmissions, puissance_fiscales=puissance_fiscales, puissance_dynamiques=puissance_dynamiques, couleurs=couleurs, etats=etats)

from flask import jsonify
@app.route('/get_models', methods=['POST'])
def get_models():
    marque = request.form['Marque']
    filtered_models = df[df['Marque'] == marque]['Modele'].unique().tolist()
    return jsonify({'models': filtered_models})

# Routes pour l'authentification

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        password_hash = generate_password_hash(password)  

        conn = sqlite3.connect('predictions.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password_hash, firstname, lastname, email) VALUES (?, ?, ?, ?, ?)", (username, password_hash, firstname, lastname, email))
        conn.commit()
        conn.close()

        flash('Inscription réussie. Vous pouvez vous connecter maintenant.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('predictions.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[5], password):
            session['user_id'] = user[0]  
            flash('Vous êtes connecté.', 'success')
            return redirect(url_for('accueil'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)  
    flash('Vous êtes déconnecté.', 'success')
    return redirect(url_for('login'))

# Autres routes...

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        # Récupérer l'ID de l'utilisateur à partir de la session
        user_id = session['user_id']
        # Récupérer les données du formulaire
        Marque = request.form['Marque']
        Modele = request.form['Modele']
        Annee = request.form['Annee']
        Ville = request.form['Ville']
        Vendeur = request.form['Vendeur']
        Main = request.form['Main']
        Kilometrage = request.form['Kilometrage']
        Carburant = request.form['Carburant']
        Transmission = request.form['Transmission']
        Puissance_fiscale = request.form['Puissance_fiscale']
        Puissance_dynamique = request.form['Puissance_dynamique']
        Couleur = request.form['Couleur']
        Etat = request.form['Etat']

        # Créer un dictionnaire avec les données
        input_data = {
            'Marque': Marque,
            'Modele': Modele,
            'Annee': Annee,
            'Ville': Ville,
            'Vendeur': Vendeur,
            'Main': Main,
            'Kilometrage': Kilometrage,
            'Carburant': Carburant,
            'Transmission': Transmission,
            'Puissance_fiscale': Puissance_fiscale,
            'Puissance_dynamique': Puissance_dynamique,
            'Couleur': Couleur,
            'Etat': Etat
        }

        # Convertir le dictionnaire en DataFrame
        input_df = pd.DataFrame([input_data])

        # Encoder les données avec les mêmes LabelEncoders utilisés auparavant
        input_df['Marque'] = LE.transform(input_df['Marque'])
        input_df['Modele'] = LE1.transform(input_df['Modele'])
        input_df['Carburant'] = LE2.transform(input_df['Carburant'])
        input_df['Main'] = LE3.transform(input_df['Main'])
        input_df['Couleur'] = LE4.transform(input_df['Couleur'])
        input_df['Ville'] = LE5.transform(input_df['Ville'])
        input_df['Etat'] = LE6.transform(input_df['Etat'])
        input_df['Vendeur'] = LE7.transform(input_df['Vendeur'])
        input_df['Transmission'] = LE8.transform(input_df['Transmission'])

        # Effectuer la prédiction
        prediction = model.predict(input_df)

        # Formater le résultat de la prédiction
        formatted_price = '{:,.0f} DH'.format(prediction[0])

        # Insérer les données dans la base de données
        conn = sqlite3.connect('predictions.db')
        cursor = conn.cursor()
        # Insérer les données dans la base de données avec l'ID de l'utilisateur
        cursor.execute("""INSERT INTO predictions (user_id, Marque, Modele, Annee, Ville, Vendeur, Main, Kilometrage, Carburant, 
                        Transmission, Puissance_fiscale, Puissance_dynamique, Couleur, Etat, Prediction) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (user_id, Marque, Modele, Annee, Ville, Vendeur, Main, Kilometrage, Carburant, Transmission, 
                        Puissance_fiscale, Puissance_dynamique, Couleur, Etat, prediction[0]))
        conn.commit()
        conn.close()

        return formatted_price
    
@app.route('/accueil')
def accueil():
    if 'user_id' in session:
        # Récupérer le nom d'utilisateur, prénom et nom de famille à partir de la session
        user_id = session['user_id']
        conn = sqlite3.connect('predictions.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username, firstname, lastname FROM users WHERE id = ?", (user_id,))
        user_info = cursor.fetchone()
        username = user_info[0]
        firstname = user_info[1]
        lastname = user_info[2]
        conn.close()
        return render_template('accueil.html', username=username, firstname=firstname, lastname=lastname)
    else:
        return redirect(url_for('login'))
    

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' in session:
        user_id = session['user_id']
        
        if request.method == 'POST':
            if 'current_password' in request.form and 'new_password' in request.form and 'confirm_password' in request.form:
                current_password = request.form['current_password']
                new_password = request.form['new_password']
                confirm_password = request.form['confirm_password']
                
                # Fetch user information including password hash from database
                conn = sqlite3.connect('predictions.db')
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                user_info = cursor.fetchone()
                
                if user_info:
                    if check_password_hash(user_info[5], current_password):  # Check current password
                        if new_password == confirm_password:
                            # Update password hash in database
                            new_password_hash = generate_password_hash(new_password)
                            cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_password_hash, user_id))
                            conn.commit()
                            conn.close()
                            flash('Mot de passe mis à jour avec succès.', 'success')
                            return redirect(url_for('profile'))
                        else:
                            flash('Le nouveau mot de passe et la confirmation ne correspondent pas.', 'danger')
                    else:
                        flash('Mot de passe actuel incorrect.', 'danger')
                else:
                    flash('Utilisateur non trouvé.', 'danger')
                conn.close()
            
            else:
                # Handle form submission to update user profile (first name, last name, email)
                firstname = request.form['firstname']
                lastname = request.form['lastname']
                email = request.form['email']
                
                # Update the user information in the database
                conn = sqlite3.connect('predictions.db')
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET firstname=?, lastname=?, email=? WHERE id=?", (firstname, lastname, email, user_id))
                conn.commit()
                conn.close()
                
                flash('Informations mises à jour avec succès.', 'success')
                return redirect(url_for('profile'))
        
        # GET request: Fetch user information from the database
        conn = sqlite3.connect('predictions.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username, firstname, lastname, email FROM users WHERE id = ?", (user_id,))
        user_info = cursor.fetchone()
        username = user_info[0]
        firstname = user_info[1]
        lastname = user_info[2]
        email = user_info[3]
        conn.close()
        
        # Render profile.html with user information
        return render_template('profile.html', username=username, firstname=firstname, lastname=lastname, email=email)
    
    # If user is not logged in, redirect to login page
    return redirect(url_for('login'))




    
@app.route('/historique')
def historique():
    # Ouvrir la connexion à la base de données
    conn = sqlite3.connect('predictions.db')
    cursor = conn.cursor()
    # Récupérer l'ID de l'utilisateur à partir de la session
    user_id = session['user_id']
    cursor.execute("SELECT * FROM predictions WHERE user_id = ?", (user_id,))
    predictions = cursor.fetchall()
    conn.close()
    return render_template('historique.html', predictions=predictions)

@app.route('/delete_prediction/<int:prediction_id>', methods=['POST'])
def delete_prediction(prediction_id):
    # Ouvrir la connexion à la base de données
    conn = sqlite3.connect('predictions.db')
    cursor = conn.cursor()
    # Récupérer l'ID de l'utilisateur à partir de la session
    user_id = session['user_id']
    cursor.execute("DELETE FROM predictions WHERE id = ? AND user_id = ?", (prediction_id, user_id))
    conn.commit()
    conn.close()
    return redirect(url_for('historique'))

@app.route('/delete_user', methods=['POST'])
def delete_user():
    if 'user_id' in session:
        user_id = session['user_id']
        
        # Delete user from the database
        conn = sqlite3.connect('predictions.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        
        # Clear session data
        session.clear()
        
        flash('Votre compte a été supprimé avec succès.', 'success')
        return redirect(url_for('login'))
    
    flash('Erreur lors de la suppression du compte.', 'danger')
    return redirect(url_for('profile'))



if __name__ == '__main__':
    create_database()  # Assurez-vous que la base de données est créée avant de démarrer l'application
    app.run(debug=True)
