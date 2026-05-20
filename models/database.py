from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Date, DateTime, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'school.db')

engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # Admin, Comptable, Secrétaire
    full_name = Column(String(100))
    email = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime)


class Class(Base):
    __tablename__ = 'classes'
    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)
    level = Column(String(20))
    monthly_fee = Column(Float, default=0)
    teacher_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
    students = relationship('Student', back_populates='class_')


class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    student_code = Column(String(20), unique=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    photo = Column(String(255))
    gender = Column(String(10))
    birth_date = Column(Date)
    address = Column(Text)
    parent_name = Column(String(100))
    parent_phone = Column(String(20))
    emergency_phone = Column(String(20))
    class_id = Column(Integer, ForeignKey('classes.id'))
    class_ = relationship('Class', back_populates='students')
    registration_date = Column(Date, default=datetime.now)
    has_transport = Column(Boolean, default=False)
    insurance_paid = Column(Boolean, default=False)
    monthly_fee = Column(Float, default=0)
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    payments = relationship('Payment', back_populates='student')
    created_at = Column(DateTime, default=datetime.now)


class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    student = relationship('Student', back_populates='payments')
    payment_type = Column(String(20))  # monthly, insurance, transport
    amount = Column(Float, nullable=False)
    month = Column(Integer)
    year = Column(Integer)
    payment_date = Column(DateTime, default=datetime.now)
    receipt_number = Column(String(30))
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey('users.id'))


class Receipt(Base):
    __tablename__ = 'receipts'
    id = Column(Integer, primary_key=True)
    receipt_number = Column(String(30), unique=True, nullable=False)
    student_id = Column(Integer, ForeignKey('students.id'))
    payment_id = Column(Integer, ForeignKey('payments.id'))
    amount = Column(Float)
    payment_type = Column(String(20))
    pdf_path = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)
    created_by = Column(Integer, ForeignKey('users.id'))


class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    employee_type = Column(String(20))  # teacher, staff, driver
    subject = Column(String(50))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    hire_date = Column(Date)
    base_salary = Column(Float, default=0)
    is_active = Column(Boolean, default=True)
    salaries = relationship('Salary', back_populates='employee')
    created_at = Column(DateTime, default=datetime.now)


class Salary(Base):
    __tablename__ = 'salaries'
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    employee = relationship('Employee', back_populates='salaries')
    amount = Column(Float, nullable=False)
    bonus = Column(Float, default=0)
    month = Column(Integer)
    year = Column(Integer)
    paid_date = Column(DateTime)
    is_paid = Column(Boolean, default=False)
    notes = Column(Text)


class Expense(Base):
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    category = Column(String(50))
    amount = Column(Float, nullable=False)
    expense_type = Column(String(20))  # fixed, variable
    expense_date = Column(Date, default=datetime.now)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.now)


class Bus(Base):
    __tablename__ = 'buses'
    id = Column(Integer, primary_key=True)
    bus_number = Column(String(20), unique=True)
    plate = Column(String(20))
    capacity = Column(Integer)
    driver_id = Column(Integer, ForeignKey('employees.id'))
    route = Column(String(100))
    monthly_fee = Column(Float, default=0)
    is_active = Column(Boolean, default=True)


class Schedule(Base):
    __tablename__ = 'schedules'
    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey('classes.id'))
    employee_id = Column(Integer, ForeignKey('employees.id'))
    subject = Column(String(50))
    day_of_week = Column(Integer)  # 0=Mon, 6=Sun
    start_time = Column(String(10))
    end_time = Column(String(10))
    room = Column(String(20))


class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    doc_type = Column(String(30))
    student_id = Column(Integer, ForeignKey('students.id'), nullable=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
    file_path = Column(String(255))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    created_by = Column(Integer, ForeignKey('users.id'))


class Setting(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    key = Column(String(50), unique=True, nullable=False)
    value = Column(Text)
    updated_at = Column(DateTime, default=datetime.now)


def init_db():
    Base.metadata.create_all(engine)
    session = Session()
    
    # Create default admin
    from hashlib import sha256
    admin = session.query(User).filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            password=sha256('admin123'.encode()).hexdigest(),
            role='Admin',
            full_name='Administrateur'
        )
        session.add(admin)
    
    # Create default classes
    classes = ['PS','MS','GS','CP','CE1','CE2','CM1','CM2','6EME','1AC','2AC','3AC','TC','1BAC','2BAC']
    for cls_name in classes:
        existing = session.query(Class).filter_by(name=cls_name).first()
        if not existing:
            session.add(Class(name=cls_name, monthly_fee=500))
    
    # Default settings
    defaults = {
        'school_name': 'Le Schéma',
        'school_address': 'Maroc',
        'school_phone': '+212 000 000 000',
        'school_email': 'contact@leschema.ma',
        'transport_fee': '300',
        'insurance_fee': '200',
        'currency': 'MAD',
        'receipt_counter': '0',
    }
    for k, v in defaults.items():
        existing = session.query(Setting).filter_by(key=k).first()
        if not existing:
            session.add(Setting(key=k, value=v))
    
    session.commit()
    session.close()
