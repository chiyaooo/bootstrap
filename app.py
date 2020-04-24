from flask import Flask
from flask import render_template, redirect, request, flash, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
import pymysql
import secrets
#import os

#dbuser = os.environ.get('DBUSER')
#dbpass = os.environ.get('DBPASS')
#dbhost = os.environ.get('DBHOST')
#dbname = os.environ.get('DBNAME')

conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(secrets.dbuser, secrets.dbpass, secrets.dbhost, secrets.dbname)
#conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(dbuser, dbpass, dbhost, dbname)


app = Flask(__name__)
app.config['SECRET_KEY']='SuperSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = conn
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning
db = SQLAlchemy(app)

class cheyguo_pokemonapp(db.Model):
    pokemonId = db.Column(db.Integer, primary_key=True)
    pokemon_name = db.Column(db.String(255))
    maximum_cp = db.Column(db.Integer)

    def __repr__(self):
        return "id: {0} | pokemon name: {1} | maximum cp: {2}".format(self.pokemonId, self.pokemon_name, self.maximum_cp)

class PokemonForm(FlaskForm):
    pokemon_name = StringField('Pokemon Name:', validators=[DataRequired()])
    maximum_cp = IntegerField('Maximum CP:', validators=[DataRequired()])


@app.route('/')
def index():
    all_pokemons = cheyguo_pokemonapp.query.all()
    return render_template('index.html', pokemon=all_pokemons, pageTitle='New Pokemon')

@app.route('/search', methods=['GET','POST'])
def search():
    if request.method == 'POST':
        form=request.form
        search_value=form['search_string']
        search = "%{}%".format(search_value)
        results = cheyguo_pokemonapp.query.filter(cheyguo_pokemonapp.pokemon_name.like(search)).all()
        return render_template('index.html', pokemon=results, pageTitle='Pokemon',legend="Search Result")
    else:
        return redirect('/')




@app.route('/pokemon/new', methods=['GET', 'POST'])
def add_pokemon():
    form = PokemonForm()
    if form.validate_on_submit():
        pokemon = cheyguo_pokemonapp(pokemon_name=form.pokemon_name.data, maximum_cp=form.maximum_cp.data)
        db.session.add(pokemon)
        db.session.commit()
        return redirect('/')

    return render_template('add_pokemon.html', form=form, pageTitle='Add A New Pokemon', legend="Add A New Pokemon")

@app.route('/pokemon/<int:pokemon_Id>', methods=['GET','POST'])
def pokemon(pokemon_Id):
    pokemons = cheyguo_pokemonapp.query.get_or_404(pokemon_Id)
    return render_template('pokemon.html', form=pokemons, pageTitle='Pokemon Details')

@app.route('/pokemon/<int:pokemon_Id>/update', methods=['GET','POST'])
def update_pokemon(pokemon_Id):
    pokemon = cheyguo_pokemonapp.query.get_or_404(pokemon_Id)
    form = PokemonForm()
    if form.validate_on_submit():
        pokemon.pokemon_name = form.pokemon_name.data
        pokemon.maximum_cp = form.maximum_cp.data
        db.session.commit()
        flash('The pokemon has been updated.')
        return redirect(url_for('pokemon', pokemon_Id=pokemon.pokemonId))
    elif request.method == 'GET':
        form.pokemon_name.data = pokemon.pokemon_name
        form.maximum_cp.data = pokemon.maximum_cp


    return render_template('add_pokemon.html', form=form, pageTitle='Update Post', legend="Update A Pokemon")

@app.route('/delete_pokemon/<int:pokemon_Id>', methods=['POST'])
def delete_pokemon(pokemon_Id):
    if request.method == 'POST': #if it's a POST request, delete the friend from the database
        pokemon = cheyguo_pokemonapp.query.get_or_404(pokemon_Id)
        db.session.delete(pokemon)
        db.session.commit()
        flash('Pokemon was successfully deleted!')
        return redirect("/")

    else: #if it's a GET request, send them to the home page
        return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)
