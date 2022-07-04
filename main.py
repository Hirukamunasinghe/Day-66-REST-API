from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self,column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")

#GET RANDOM CAFE INFO
@app.route("/random")
def random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    return jsonify(cafe=random_cafe.to_dict())

#GET ALL CAFE
@app.route("/all")
def get_all_cafes():
    all_cafes = db.session.query(Cafe).all()
    return jsonify(all_cafes=[cafe.to_dict() for cafe in all_cafes ])

#SEARCH FOR CAFE LOCATION
@app.route("/search")
def search_cafe():
    query_location = request.args.get("loc")
    cafe = db.session.query(Cafe).filter_by(location=query_location).first()
    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(error={"Not found":"Sorry,we do not have a cafe at that location"})

#ADD CAFE
@app.route("/add",methods=["POST"])
def post_new_cafe():
    new_cafe = Cafe(
        name = request.form.get("name"),
        map_url = request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats = request.form.get("seats"),
        coffee_price = request.form.get("coffee_price")
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success":"successfully added"})

#EDIT CAFE PRICE
@app.route('/update-price/<cafe_id>',methods=["GET","PATCH"])
def change_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        return jsonify(response={"Success":"Successfully updated the price"})
    else:
        return jsonify(reponse={"Error":"Could not update the price"})

#DELETE CAFES
@app.route('/report-closed/<cafe_id>')
def delete(cafe_id):
    api_key = request.args.get("api-key")
    if api_key=="TopSecretAPIKey":
        cafe = db.session.query(Cafe).get(cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(reponse={"Success":"Successfully deleted cafe from the database"})
        return jsonify(response={"Error":"sorry, a cafe with that id was not found to be deleted"})
    else:
        return jsonify(response={"Forbidden":"Sorry, that api key is invalid"})



if __name__ == '__main__':
    app.run(debug=True)
