from sqlalchemy import Integer, String, Column, create_engine, DateTime, ForeignKey, Date
from sqlalchemy.orm import Session, declarative_base
from datetime import datetime, timedelta, timezone
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

DB_PATH = "visitors.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Base = declarative_base()

ACCESS_TOKEN_EXPIRY = 15
REFRESH_TOKEN_EXPIRY = 7 * 24 * 60
SECRET_KEY = "SECRET123"
ALGORITHM = "HS256"


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.now)


class Visitors(Base):
    __tablename__ = "visitors"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    visitor_name = Column(String)
    student_name = Column(String)
    room_no = Column(String)
    purpose = Column(String)
    visit_date = Column(Date)
    created_at = Column(DateTime, default=datetime.now)


Base.metadata.create_all(engine)


def add_user(username, email, password):
    session = Session(engine)
    email = email.lower()
    user_exists = session.query(Users).filter_by(email=email).first()
    if user_exists is not None:
        session.close()
        return False

    user = Users(username=username, email=email, hashed_password=ph.hash(password))
    session.add(user)
    session.commit()
    user_id = user.id
    session.close()
    return user_id


def verify_login(email, password):
    session = Session(engine)
    user = session.query(Users).filter_by(email=email.lower()).first()
    if user is None:
        session.close()
        return False

    try:
        ph.verify(user.hashed_password, password)
    except VerifyMismatchError:
        session.close()
        return False

    user_id = user.id
    session.close()
    access_token = create_token(user_id=user_id, token_type="access")
    refresh_token = create_token(user_id=user_id, token_type="refresh")
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


def create_token(user_id, token_type):
    time = ACCESS_TOKEN_EXPIRY
    if token_type == "refresh":
        time = REFRESH_TOKEN_EXPIRY
    payload = {
        "user_id": user_id,
        "token_type": token_type,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=time),
    }
    return jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token, token_type):
    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return False
    if payload.get("token_type") == token_type:
        return payload.get("user_id")
    return False


def get_visitors(user_id):
    session = Session(engine)
    visitors = session.query(Visitors).filter_by(user_id=user_id).all()
    response = []
    for visitor in visitors:
        response.append(visitor_to_dict(visitor))
    session.close()
    return response


def add_visitor(user_id, visitor_name, student_name, room_no, purpose, visit_date):
    session = Session(engine)
    visitor = Visitors(
        user_id=user_id,
        visitor_name=visitor_name,
        student_name=student_name,
        room_no=room_no,
        purpose=purpose,
        visit_date=visit_date,
    )
    session.add(visitor)
    session.commit()
    response = visitor_to_dict(visitor)
    session.close()
    return response


def visitor_to_dict(visitor: Visitors):
    return {
        "id": visitor.id,
        "user_id": visitor.user_id,
        "visitor_name": visitor.visitor_name,
        "student_name": visitor.student_name,
        "room_no": visitor.room_no,
        "purpose": visitor.purpose,
        "visit_date": str(visitor.visit_date),
        "created_at": str(visitor.created_at),
    }
