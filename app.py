from flask import Flask, make_response, request, jsonify, session, redirect, url_for
from flask_mongoengine import MongoEngine
from app_password import mongodb_password
from flask_marshmallow import Marshmallow
from functools import wraps
from mongoengine.queryset.visitor import Q
import datetime
import uuid

app = Flask(__name__)

app.secret_key = "super secret key"
app.config["SESSION_TYPE"] = "filesystem"

dbName = "APP"
DB_URI = "mongodb+srv://ekrem:{}@cluster0.ifjup.mongodb.net/{}?" \
         "retryWrites=true&w=majority".format(mongodb_password, dbName)
app.config["MONGODB_HOST"] = DB_URI

db = MongoEngine()
db.init_app(app)
ma = Marshmallow(app)

# Kullanıcı Giriş Kontrol Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return make_response("Erişim Yetkiniz Yok. Lütfen Giriş Yapın.", 404)
    return decorated_function


class Users(db.Document):
    user_id = db.StringField(default=str(uuid.uuid4()))
    name = db.StringField()
    email = db.EmailField(unique=True)
    password = db.StringField()
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField()

    def to_json(self):
        return {
            "user_id":self.user_id,
            "name":self.name,
            "email":self.email,
            "password":self.password,
            "created_at":self.created_at,
            "updated_at":self.updated_at
        }

class UserSchema(ma.Schema):
    class Meta:
        fields = ("name", "email", "created_at", "updated_at")

user_schema = UserSchema()
users_schema = UserSchema(many=True)

@app.route('/app/register', methods=['POST'])
def app_register():
    content = request.json
    user_obj = Users.objects(email=content["email"]).first()
    if user_obj:
        return make_response("Girdiğiniz Mail Adresi Kullanılmaktadır")
    else:
        user = Users(name=content["name"],
                     email=content["email"],
                     password=content["password"],
                     updated_at=datetime.datetime.now)
        user.save()
        return make_response("Kayıt Başarılı", 201)

@app.route('/app/login', methods=['GET', 'POST'])
def app_login():
    if request.method == 'POST':
        content = request.json
        user_email = content["email"]
        password = content["password"]
        check_user = Users.objects(email=user_email).first()
        if check_user:
            check_password = check_user['password']
            if check_password == password:

                # board_obj = Boards.objects(created_by=check_user["user_id"]).first()
                # print(board_obj["name"])
                session["logged_in"] = True
                session["email"] = user_email
                session["user_id"] = check_user["user_id"]

                return redirect(url_for("app_boards"))
                #return make_response("Giriş Başarılı", 201)
            else:
                return make_response("Hatalı Parola", 404)
        else:
            return make_response("Hatalı Kullanıcı Adı", 404)

@app.route('/app/users', methods=['GET', 'PUT', 'DELETE'])
@login_required
def app_each_user():
    user_id = session["user_id"]
    if request.method == 'GET':
        user_obj = Users.objects(user_id=user_id).first()

        return make_response(user_schema.jsonify(user_obj.to_json()), 200)



    elif request.method == 'PUT':
        content = request.json
        user_obj = Users.objects(user_id=user_id).first()
        # user_obj.update(name=content['name'], email=content['email'], password=content['password'], updated_at=datetime.datetime.now)
        user_obj.name = content['name']
        user_obj.email=content['email']
        user_obj.password=content['password']
        user_obj.updated_at=datetime.datetime.now
        user_obj.save()
        return make_response("Güncelleme Başarılı", 204)

    elif request.method == 'DELETE':
        user_obj = Users.objects(user_id=user_id).first()
        user_obj.delete()
        return make_response("", 204)


STATUS_BOARD = ("Aktif", "Arşivlenmiş")

#board_id = db.StringField(default=str(uuid.uuid4()))
class Boards(db.Document):
    board_id = db.StringField(default=str(uuid.uuid4()))
    name = db.StringField()
    status = db.StringField(choices=STATUS_BOARD, default="Aktif")
    created_by = db.StringField()
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField()

    def to_json(self):
        return {
            "board_id":self.board_id,
            "name":self.name,
            "status":self.status,
            "created_by":self.created_by,
            "created_at":self.created_at,
            "updated_at":self.updated_at
        }

class BoardSchema(ma.Schema):
    class Meta:
        fields = ("name", "status", "created_by", "created_at")

board_schema = BoardSchema()
boards_schema = BoardSchema(many=True)


@app.route('/app/boards', methods=['GET', 'POST'])
@login_required
def app_boards():
    created_by = session["user_id"]
    if request.method == 'GET':
        boards = []
        board_obj = Boards.objects(created_by=created_by)
        if board_obj:
            for board in board_obj:
                boards.append(board)
            return make_response(boards_schema.jsonify(boards), 200)
        else:
            return make_response("Kayıtlı Board Yoktur", 404)

    elif request.method == 'POST':
        content = request.json
        board = Boards(name=content["name"], status=content["status"], created_by=created_by)
        board.save()
        return make_response("Kayıt Başarılı", 201)


@app.route('/app/boards/<board_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def app_each_boards(board_id):
    created_by = session["user_id"]
    if request.method == 'GET':
        board_obj = Boards.objects(board_id=board_id, created_by=created_by).first()
        if board_obj:
            return make_response(board_schema.jsonify(board_obj.to_json()), 200)
        else:
            return make_response("Kayıt Bulunamadı", 404)

    elif request.method == 'PUT':
        content = request.json
        board_obj = Boards.objects(board_id=board_id, created_by=created_by).first()
        if board_obj:
            board_obj.update(name=content["name"], status=content["status"], updated_at=datetime.datetime.now)

            return make_response("Güncelleme Tamamlandı", 204)

        else:
            return make_response("Kayıt Bulunamadı", 404)

    elif request.method == 'DELETE':
        board_obj = Boards.objects(board_id=board_id, created_by=created_by).first()
        if board_obj:
            board_obj.delete()

            return make_response("Kayıt Silindi", 204)

        else:
            return make_response("Kayıt Bulunamadı", 404)

STATUS_CARD = ["Alındı", "Başladı", "Kontrolde", "Tamamlandı"]

class Cards(db.Document):
    card_id = db.StringField(default=str(uuid.uuid4()))
    title = db.StringField()
    content = db.StringField()
    status = db.StringField(choices=STATUS_CARD, default="Aktif")
    assignee = db.ListField()
    created_by = db.StringField()
    board = db.StringField()
    start_date = db.DateTimeField()
    due_date = db.DateTimeField()
    finished_at = db.DateTimeField()
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField()

    def to_json(self):
        return {
            "card_id":self.card_id,
            "title":self.title,
            "content":self.content,
            "status":self.status,
            "assignee":self.assignee,
            "created_by":self.created_by,
            "board":self.board,
            "start_date":self.start_date,
            "due_date":self.due_date,
            "finished_at":self.finished_at,
            "created_at":self.created_at,
            "updated_at":self.updated_at
        }

class CardSchema(ma.Schema):
    class Meta:
        fields = ("title", "content", "status", "assignee", "created_by", "board", "start_date",
                  "due_date", "finished_at", "created_at", "updated_at")


card_schema = CardSchema()
cards_schema = CardSchema(many=True)


@app.route('/app/cards', methods=['GET', 'POST'])
@login_required
def app_cards():
    user_id = session["user_id"]
    if request.method == 'GET':
        cards = []
        card_obj = Cards.objects(Q(created_by=user_id) | Q(assignee=user_id))
        if card_obj:
            for card in card_obj:
                cards.append(card)
            return make_response(cards_schema.jsonify(cards), 200)
        else:
            return make_response("Kayıt Bulunamadı", 404)

    elif request.method == 'POST':
        content = request.json
        card = Cards(title=content["title"], content=content["content"], status=content["status"],
                     assignee=content["assignee"], created_by=user_id, board=content["board"],
                     start_date=content["start_date"], due_date=content["due_date"],
                     updated_at=datetime.datetime.now)
        card.save()
        return make_response("Kayıt Başarılı", 201)


@app.route('/app/cards/<card_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def app_each_cards(card_id):
    user_id = session["user_id"]
    if request.method == 'GET':
        card_obj = Cards.objects.filter(Q(car_id=card_id) and (Q(created_by=user_id) or Q(assignee=user_id))).first()
        if card_obj:
            return make_response(card_schema.jsonify(card_obj.to_json()), 200)
        else:
            return make_response("Kayıt Bulunamadı", 404)

    elif request.method == 'PUT':
        content = request.json
        card_obj = Cards.objects(Q(card_id=card_id) and (Q(created_by=user_id) or Q(assignee=user_id))).first()
        if card_obj:
            card_obj.update(title=content["title"],
                            content=content["content"],
                            status=content["status"],
                            assignee=content["assignee"],
                            start_date=content["start_date"],
                            due_date=content["due_date"],
                            updated_at=datetime.datetime.now)

            return make_response("Güncelleme Başarılı", 204)
        else:
            return make_response("Kayıt Bulunamadı", 404)
    elif request.method == 'DELETE':
        card_obj = Cards.objects(Q(card_id=card_id) and (Q(created_by=user_id) or Q(assignee=user_id))).first()
        if card_obj:
            card_obj.delete()
            return make_response("Kayıt Silindi", 204)
        else:
            return make_response("Kayıt Bulunamadı", 404)

class Comments(db.Document):
    comment_id = db.StringField(default=str(uuid.uuid4()))
    content = db.StringField()
    created_by = db.StringField()
    card = db.StringField()
    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField()

    def to_json(self):
        return {
            "comment_id":self.comment_id,
            "content":self.content,
            "created_by":self.created_by,
            "card":self.card,
            "created_at":self.created_at,
            "updated_at":self.updated_at
        }

class CommentSchema(ma.Schema):
    class Meta:
        fields = ("content", "created_by", "card", "created_at")

comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)


@app.route('/app/comments', methods=['GET', 'POST'])
@login_required
def app_comments():
    if request.method == 'GET':
        comments = []
        for comment in Comments.objects:
            comments.append(comment)
        return make_response(comment_schema.jsonify(comments), 200)

    elif request.method == 'POST':
        content = request.json
        comment = Comments(content=content["content"],
                           created_by=content["created_by"],
                           card=content["card"],
                           updated_at=datetime.datetime.now)

        comment.save()
        return make_response("Yorum Başarıyla Eklendi", 201)

@app.route('/app/comments/<comment_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def app_each_comments(comment_id):
    user_id = session["user_id"]
    if request.method == 'GET':
        #card_obj = Cards.object(Q(created_by=user_id) | Q(assignee__in=user_id))
        comment_obj = Comments.objects(Q(created_by=user_id) & Q(comment_id=comment_id)).first()
        if comment_obj:
            return make_response(comment_schema.jsonify(comment_obj.to_json()), 200)
        else:
            return make_response("Yorum Bulunamadı", 404)

    elif request.method == 'PUT':
        content = request.json
        comment_obj = Comments.objects(Q(created_by=user_id) & Q(comment_id=comment_id)).first()
        comment_obj.update(content=content["content"],
                           updated_at=datetime.datetime.now)

        return make_response("", 204)

    elif request.method == 'DELETE':
        comment_obj = Comments.objects(Q(created_by=user_id) & Q(comment_id=comment_id)).first()
        comment_obj.delete()
        return make_response("", 204)


if __name__ == "__main__":
    app.run()