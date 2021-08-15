import uuid
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, Integer, ARRAY, ForeignKeyConstraint, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = Column(UUID, primary_key=True, default=str(uuid.uuid4()))
    phone = Column(BigInteger)
    email = Column(String)
    alias = Column(String(20), nullable=False)
    name = Column(String)
    password = Column(String)
    insert_dt = Column(DateTime(timezone=True), default=datetime.utcnow())
    workplace = Column(String)
    promo_code = Column(String, ForeignKey('promos.code'), default='default')
    is_in_leaderboard = Column(Boolean, default=False)

    promo_ = relationship("PromoCode", foreign_keys=[promo_code], backref="users_with_promo_")
    role_ = relationship("Role", uselist=False)


class Role(db.Model):
    __tablename__ = 'roles'

    user_id = Column(UUID, ForeignKey(User.id), primary_key=True)
    role = Column(String, nullable=False)


class Request(db.Model):
    __tablename__ = 'requests'

    id = Column(UUID, primary_key=True, default=str(uuid.uuid4()))
    user_id = Column(UUID, ForeignKey('users.id'), primary_key=True)
    request_email = Column(String)
    short_id = Column(String)
    request_type = Column(String(10))
    custom_code = Column(BigInteger)
    product_type = Column(String)
    doc_type = Column(String)
    validity_period = Column(Integer)
    add_info = Column(String)
    status = Column(Integer, nullable=False, default=0)
    files = Column(ARRAY(String), default=[])
    # operator_id = Column(UUID, ForeignKey('users.id'))
    date = Column('insert_dt', DateTime(timezone=True), nullable=False, default=datetime.utcnow())
    update_dt = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow())

    user_ = relationship("User", foreign_keys=[user_id], backref="requests_")


class Job(db.Model):
    __tablename__ = 'projects'

    id = Column(UUID, primary_key=True, default=str(uuid.uuid4()))
    user_id = Column(UUID, ForeignKey('users.id'), primary_key=True)
    request_id = Column(UUID, ForeignKey(Request.id))
    customer_agreement = Column(String, default=False, nullable=False)
    agent_agreement = Column(String, default=False, nullable=False)
    acts = Column(String, default=False, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    custom_code = Column(BigInteger, nullable=False)
    client_price = Column(Integer, nullable=False)
    cost_price = Column(Integer, nullable=False)
    date = Column("insert_dt", DateTime(timezone=True), nullable=False, default=datetime.utcnow())
    is_paid = Column(Boolean, nullable=False, default=False)

    user_ = relationship("User", foreign_keys=[user_id], backref="jobs_")


class AdditionalRequestInfo(db.Model):
    __tablename__ = 'add_request_info'

    request_id = Column(UUID, primary_key=True)
    user_id = Column(UUID)
    required_files = Column(ARRAY(String))
    price = Column(Integer)
    duration = Column(Integer)
    description = Column(String)
    recommended_price = Column(Integer)

    __table_args__ = (ForeignKeyConstraint([request_id, user_id], [Request.id, Request.user_id]),)

    request_ = relationship("Request", backref=backref("answer_", uselist=False))


class Organization(db.Model):
    __tablename__ = 'organizations'

    id = Column(UUID, primary_key=True)
    name = Column(String, nullable=False)
    phones = Column(ARRAY(BigInteger))
    email = Column(String)
    contact_person = Column(String)
    docs_path = Column(String, nullable=False)


class PromoCode(db.Model):
    __tablename__ = 'promos'

    code = Column(String, primary_key=True)
    expert_id = Column(UUID, ForeignKey(User.id))
    organization_id = Column(UUID, ForeignKey(Organization.id))
    reward = Column(Integer)

    expert_user_ = relationship(User, foreign_keys=[expert_id], backref=backref("expert_promo_", uselist=False))
    organization_ = relationship(Organization, backref=backref("organization_promo_", uselist=False))
    # _users_with_promo = relationship(User, back_populates="_promo")


class Leader(db.Model):
    __tablename__ = 'leaderboard'

    user_id = Column(UUID, ForeignKey(User.id), primary_key=True)
    name = Column(String)
    margin = Column(BigInteger)
    full_price = Column(BigInteger)
    workplace = Column(String)
    alias = Column(String(20), nullable=False)
    user_ = relationship(User, uselist=False)


class Margin(db.Model):
    __tablename__ = 'margin'

    user_id = Column(UUID, ForeignKey(User.id), primary_key=True)
    margin = Column(BigInteger)
    full_price = Column(BigInteger)

    user_ = relationship(User, uselist=False)


class Payment(db.Model):
    __tablename__ = 'payments'

    user_id = Column(UUID, ForeignKey(User.id), primary_key=True)
    account_number = Column(BigInteger, nullable=False)
    projects = Column(ARRAY(UUID), nullable=False)
    amount = Column(Integer, nullable=False)


class StatisticView(db.Model):
    __tablename__ = 'statistic_view'

    id = Column(UUID, primary_key=True)
    req_started = Column(BigInteger)
    req_ended = Column(BigInteger)
    req_new = Column(BigInteger)
    job_self = Column(BigInteger)
    job_req = Column(BigInteger)
    balance = Column(BigInteger)
