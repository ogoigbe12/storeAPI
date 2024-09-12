from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, create_refresh_token,get_jwt_identity, jwt_required,get_jwt

from db import db
from blocklist import BLOCKLIST
from models import UserModel
from schemas import UserSchema

blp = Blueprint("User", "users", __name__, description="Operations on users")


# @blp.route("/register")
# class UserRegister(MethodView):
#     @blp.arguments(UserSchema)
#     def post(self, user_data):
#         print(user_data)
#         if UserModel.query.filter(UserModel.username == user_data["username"]).first():
#             abort(409, message= "username already exists")
        
        
#         user = UserModel(
#             username=user_data["username"],
#             password=pbkdf2_sha256.hash(user_data["password"])
#         )
#         db.session.add(user)
#         db.session.commit()
#         return {"message": "User created successfully"}, 201

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            return {"access_token": access_token, "refresh_token":  refresh_token}, 200

        abort (401, message="Invalid credentials")

@blp.route("/refresh")
class Token(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"access_token": new_token}, 200

@blp.route("/logout")
class Logout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "successfully logged out."}

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        try:
            user = UserModel(
                username=user_data["username"],
                email=user_data["email"],
                password=pbkdf2_sha256.hash(user_data["password"])
            )
            db.session.add(user)
            db.session.commit()
            return {"message": "User created successfully"}, 201
        
        except IntegrityError:
            db.session.rollback()
            db.session.commit()
            existing_user = UserModel.query.filter(
                (UserModel.username == user_data["username"]) | 
                (UserModel.email == user_data["email"])
            ).first()
            
            if existing_user.username == user_data["username"]:
                abort(400, message="Username already exists")
            elif existing_user.email == user_data["email"]:
                abort(400, message="Account with this email already exists")
            else:
                abort(500, message="An error occurred while creating the user")

    
@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted"}, 200