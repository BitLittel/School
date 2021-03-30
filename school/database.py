# -*- coding: utf-8 -*-

from hashlib import md5
from sqlalchemy import Column, Integer, create_engine, DateTime, ForeignKey, Text, Unicode, PickleType, Boolean, \
    DECIMAL, Enum
from sqlalchemy.sql import func, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm.scoping import scoped_session
from school import school
from flask import g

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    login = Column(Unicode(255, collation='utf8_unicode_ci'))
    password = Column(Unicode(128, collation='utf8_unicode_ci'))
    email = Column(Unicode(255, collation='utf8_unicode_ci'))
    wallet = Column(Unicode(255, collation='utf8_unicode_ci'))
    about_us = Column(Text(collation="utf8_unicode_ci"))
    photo = relationship('Photo', backref='photo_user', lazy='dynamic')
    comment = relationship('Comment', backref='comment_user', lazy='dynamic')
    message = relationship('MessageUser', backref='user_id_mess', lazy='dynamic')
    course_id = relationship('Course', backref='user_id_course', lazy='dynamic')
    homework = relationship('HomeWork', backref='user_homework', lazy='dynamic')
    user_list = relationship('List', backref='user_to_list', lazy='dynamic')
    blog = relationship('Blog', backref='user_id_blog', lazy='dynamic')
    transact = relationship('Transaction', backref='transect_user_id', lazy='dynamic')
    notice = relationship('Notice', backref='notice_to_user', lazy='dynamic')
    test_in_user = relationship('TestInDay', backref='user_test_in_day', lazy='dynamic')
    subscript = Column(PickleType, default={})
    sub_course = Column(PickleType, default={})
    follow = Column(PickleType, default=list())
    admin = Column(Boolean, default=False)
    ban = Column(Boolean, default=False)

    def user_photo(self):
        return g.db.query(Photo).filter(Photo.user_id == self.id).first()

    def user_balance(self):
        b = g.db.query(func.sum(Transaction.price).label('sum')).filter(Transaction.user_id == self.id).first()
        if b.sum is None:
            return 0.0
        else:
            return int(b.sum)

    def get_user(user_id):
        return g.db.query(User).filter(and_(User.id == int(user_id), User.ban == 0)).first()

    def is_authenticated(self):
        return True

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/' + md5(self.email.encode('utf-8')).hexdigest() + '?d=mm&s=' + str(size)

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def __repr__(self):
        return "<User(%r, %r, %r)>" % (self.id, self.login, self.password)


class Setting(Base):
    __tablename__ = 'setting'
    id = Column(Integer, primary_key=True)
    commission = Column(Integer)


class Photo(Base):
    __tablename__ = 'photo'
    id = Column(Integer, primary_key=True)
    photo = Column(Unicode(255, collation="utf8_unicode_ci"))
    photo_small = Column(Unicode(255, collation="utf8_unicode_ci"))
    user_id = Column(Integer, ForeignKey(User.id))
    ban = Column(Boolean, default=False)


class Subscript(Base):
    __tablename__ = 'subscript'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255, collation='utf8_unicode_ci'))
    right = Column(PickleType)
    price = Column(Integer)
    about_sub = Column(Text(collation='utf8_unicode_ci'))
    ban = Column(Boolean, default=False)


class Direction(Base):
    __tablename__ = 'direction'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255, collation='utf8_unicode_ci'))
    ban = Column(Boolean, default=False)


class Course(Base):
    __tablename__ = 'course'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255, collation='utf8_unicode_ci'))
    text = Column(Text(collation='utf8_unicode_ci'))
    direction_name = Column(Unicode(255, collation='utf8_unicode_ci'))
    price = Column(Integer)
    infinity = Column(Boolean)
    user_id = Column(Integer, ForeignKey(User.id))
    lessons = relationship('Lesson', backref='lessons_course_id', lazy='dynamic')
    course_id = relationship('List', backref='user_to_course_list', lazy='dynamic')
    homework_id = relationship('HomeWork', backref='course_user', lazy='dynamic')
    blog_id = relationship('Blog', backref='course_id_blog', lazy='dynamic')
    ban = Column(Boolean, default=False)

    def get_cours(course_id):
        return g.db.query(Course).filter(and_(Course.id == int(course_id), Course.ban == 0)).first()


class MessageUser(Base):
    __tablename__ = 'message'
    id = Column(Integer, primary_key=True)
    text = Column(Text(collation="utf8_unicode_ci"))
    time = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey(User.id))
    user_to = Column(Integer)
    wait = Column(Boolean, default=True)
    now = Column(Boolean, default=True)
    id_to_dialog = relationship('Dialog', backref='message_id_dialog', lazy='dynamic')
    ban = Column(Boolean, default=False)


class Dialog(Base):
    __tablename__ = 'dialog'
    id = Column(Integer, primary_key=True)
    user_login = Column(Unicode(255, collation='utf8_unicode_ci'))
    user = Column(Unicode(255, collation='utf8_unicode_ci'))
    message_id = Column(Integer, ForeignKey(MessageUser.id))
    ban = Column(Boolean, default=False)


class Lesson(Base):
    __tablename__ = 'lesson'
    id = Column(Integer, primary_key=True)
    number = Column(Integer, default=1)
    name = Column(Unicode(255, collation='utf8_unicode_ci'))
    homework = Column(Text(collation='utf8_unicode_ci'), default=None)
    test = Column(PickleType, default=list())
    persent_for_test = Column(Integer, default=50)
    test_in_day = Column(Integer, default=3)
    homework_type = Column(Enum('test', 'homework', 'free'), default='homework')
    content = Column(Text(collation='utf8_unicode_ci'))
    cours_id = Column(Integer, ForeignKey(Course.id))
    ban = Column(Boolean, default=False)
    homework_num = relationship('HomeWork', backref='homework_num', lazy='dynamic')
    test_i_d = relationship('TestInDay',  backref='test_lesson', lazy='dynamic')

    def get_lesson(lesson_id):
        return g.db.query(Lesson).filter(and_(Lesson.id == int(lesson_id), Lesson.ban == 0)).first()


class HomeWork(Base):
    __tablename__ = 'homework'
    id = Column(Integer, primary_key=True)
    lessons_id = Column(Integer, ForeignKey(Lesson.id))
    courses_id = Column(Integer, ForeignKey(Course.id))
    comments = Column(Text(collation='utf8_unicode_ci'), default=None)
    wait = Column(Boolean)
    text = Column(Text(collation='utf8_unicode_ci'))
    done = Column(Boolean)
    user_id = Column(Integer, ForeignKey(User.id))
    data = Column(DateTime, server_default=func.now())
    ban = Column(Boolean, default=False)


class TestInDay(Base):
    __tablename__ = 'testinday'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    lesson_id = Column(Integer, ForeignKey(Lesson.id))
    count = Column(Integer, default=0)
    data = Column(PickleType, default=list())
    ban = Column(Boolean, default=False)


class List(Base):
    __tablename__ = 'list'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    lessons_number = Column(Integer)
    courses_id = Column(Integer, ForeignKey(Course.id))
    teacher = Column(Boolean, default=False)
    ban = Column(Boolean, default=False)


class Blog(Base):
    __tablename__ = 'blog'
    id = Column(Integer, primary_key=True)
    subject = Column(Unicode(255, collation='utf8_unicode_ci'))
    text = Column(Text(collation='utf8_unicode_ci'))
    data = Column(DateTime, server_default=func.now())
    course_id = Column(Integer, ForeignKey(Course.id))
    user_id = Column(Integer, ForeignKey(User.id))
    comments_user = relationship('Comment', backref='blog_id_user', lazy='dynamic')
    ban = Column(Boolean, default=False)

    def get_blog(blog_id):
        return g.db.query(Blog).filter(and_(Blog.id == int(blog_id), Blog.ban == 0)).first()


class Comment(Base):
    __tablename__ = 'comment'
    id = Column(Integer, primary_key=True)
    comment = Column(Text(collation="utf8_unicode_ci"))
    user_id = Column(Integer, ForeignKey(User.id))
    user_name = Column(Unicode(255, collation='utf8_unicode_ci'))
    blog_id = Column(Integer, ForeignKey(Blog.id))
    data = Column(DateTime, server_default=func.now())
    ban = Column(Boolean, default=False)


class Transaction(Base):
    __tablename__ = 'transaction'
    id = Column(Integer, primary_key=True)
    price = Column(DECIMAL(10, 2))
    user_id = Column(Integer, ForeignKey(User.id))
    text = Column(Text(collation="utf8_unicode_ci"))
    withdraw = Column(Boolean, default=False)
    data = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return '<Transaction %r, %r>' % (self.price, self.text)


class Notice(Base):
    __tablename__ = 'notice'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    text = Column(Text(collation="utf8_unicode_ci"))
    hypertext = Column(Unicode(255, collation='utf8_unicode_ci'), default='')
    read = Column(Boolean, default=False)
    data = Column(DateTime, server_default=func.now())
    ban = Column(Boolean, default=False)


engine = create_engine('mysql://%s:%s@%s/%s?charset=utf8' % (school.config['DATABASE_USER'],
                                                             school.config['DATABASE_PASSWORD'],
                                                             school.config['DATABASE_IP'],
                                                             school.config['DATABASE_NAME']),
                       encoding='utf8', echo=False)
Base.metadata.create_all(engine)

Session = scoped_session(sessionmaker())
Session.configure(bind=engine)
