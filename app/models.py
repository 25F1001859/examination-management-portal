from datetime import datetime
from app import db
from flask_login import UserMixin
from app import login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default="active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="active")
    examinations = db.relationship("Examination", backref="course", lazy=True)

class Examination(db.Model):
    __tablename__ = "examinations"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    exam_type = db.Column(db.String(30), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    max_marks = db.Column(db.Integer, nullable=False)
    slot_creation_start = db.Column(db.DateTime)
    slot_creation_end = db.Column(db.DateTime)
    booking_start = db.Column(db.DateTime)
    booking_end = db.Column(db.DateTime)
    status = db.Column(db.String(30), default="draft") #draft, slot creation, open booking, closed, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Rubric(db.Model):
    __tablename__ = "rubrics"

    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer,db.ForeignKey("examinations.id"),nullable=False)
    criterion_name = db.Column(db.String(150),nullable=False)
    max_marks = db.Column(db.Float, nullable=False)
    weightage = db.Column(db.Float, default=1.0)
    description = db.Column(db.Text)

    examination = db.relationship("Examination",backref="rubrics")

class Slot(db.Model):
    __tablename__ = "slots"

    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer,db.ForeignKey("examinations.id"),nullable=False)
    examiner_id = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time,nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="available")# available, full, cancelled, completed

    examination = db.relationship("Examination",backref="slots")
    examiner = db.relationship("User", foreign_keys=[examiner_id], backref="created_slots")
    bookings = db.relationship("Booking", backref="slot")


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey("slots.id"), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="booked") # (booked, cancelled, completed)

    student = db.relationship("User", foreign_keys=[student_id], backref="bookings")

class Evaluation(db.Model):
    __tablename__ = "evaluations"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column( db.Integer, db.ForeignKey("bookings.id"), unique=True, nullable=False)
    examiner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    marks = db.Column(db.Float, nullable=False)
    criterion_marks = db.Column(db.JSON)# to store marks against individual rubric criteria.
    remarks = db.Column(db.Text)
    published = db.Column(db.Boolean, default=False)
    evaluated_at = db.Column(db.DateTime, default=datetime.utcnow)

    booking = db.relationship("Booking", backref=db.backref("evaluation", uselist=False))
    examiner = db.relationship("User", foreign_keys=[examiner_id])



@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
