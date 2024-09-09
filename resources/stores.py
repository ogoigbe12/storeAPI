from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required,get_jwt
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import StoreModel
from schemas import StoreSchema, ItemSchema


blp = Blueprint("Stores", __name__, description="Operations on stores")


@blp.route("/store/<int:store_id>")
class Store(MethodView):
    @jwt_required()
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store
    
    @jwt_required()
    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return {"message": "Store Deleted"}


@blp.route("/store")
class StoreList(MethodView):
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    @jwt_required()
    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):
        store_name = store_data.get('name')
    
        existing_store = StoreModel.query.filter_by(name=store_name).first()
    
        if existing_store:
            abort(400, message="A store with that name already exists.")
    
        store = StoreModel(**store_data)
    
        try:
            db.session.add(store)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred creating the store.")
    
        return store


    # def post(self, store_data):
    #     store = StoreModel(**store_data)
    #     try:
    #         db.session.add(store)
    #         db.session.commit()
    #     except IntegrityError:
    #         abort(
    #             400,
    #             message="A store with that name already exists.",
    #         )
    #     except SQLAlchemyError:
    #         abort(500, message="An error occurred creating the store.")

    #     return store