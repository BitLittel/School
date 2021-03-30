# -*- coding: utf-8 -*-
import datetime
from flask import g
from flask_login import current_user
from sqlalchemy import func, and_, desc
from school.database import Subscript, Lesson, Course, HomeWork, List

right = {}


def add_role(idr, d):
    right[idr] = d


def check_rights(idr_r):
    # если админ то ваще бог
    if current_user.admin:
        return True
    # получаем подписки пользователя
    if current_user.subscript is None:
        return False
    subs = []
    for sub in current_user.subscript.keys():
        if current_user.subscript[sub][0] < datetime.datetime.now() < \
                current_user.subscript[sub][1]:
            subs.append(sub)
    # получаем права действующих подписок
    sub_u = g.db.query(Subscript.right).filter(Subscript.id.in_(subs)).all()
    for sub_b in sub_u:
        if idr_r in sub_b.right:
            if datetime.datetime.now():
                return True
    return False
