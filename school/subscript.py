# -*- coding: utf-8 -*-

import copy, re, datetime
from flask import g, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from sqlalchemy import and_, or_, func
from school import school
from school.database import Course, Blog, User, List, Subscript, Transaction
from school.right import check_rights, add_role


@school.route('/subscript', methods=['GET', 'POST'])
@login_required
def subscript():
    all_subs = g.db.query(Subscript).filter(Subscript.ban == False).all()
    return render_template('subscript.html',
                           all_subs=all_subs)


@school.route('/subscript/<int:sub_id>', methods=['GET', 'POST'])
@login_required
def subscript_id(sub_id=None):
    error = None
    month = None
    current_sub = g.db.query(Subscript).filter(Subscript.id == int(sub_id)).first()
    if current_sub is None:
        return redirect(url_for('subscript'))
    if request.method == 'POST':
        month = request.form.get('month')
        if re.search(r'^[0-9]{1,2}$', month) is None:
            error = u"Вы не ввели данные или данные были не корректно введены"
            return render_template('subscript_id.html',
                                   error=error,
                                   current_sub=current_sub,
                                   month=month or '')
        day = int(month) * 30.5
        admin = g.db.query(User).filter(User.id == 1).first()
        check_sub = current_user.subscript.get(current_sub.id)
        if current_user.user_balance() < (current_sub.price * int(month)):
            error = u"На вашем счету недостаточно средств"
            return render_template('subscript_id.html',
                                   error=error,
                                   current_sub=current_sub,
                                   month=month or '')
        if check_sub:
            if check_sub[0] < datetime.datetime.now() < check_sub[1]:
                dic_key = copy.copy(current_user.subscript)
                dic_key.update(
                    [[current_sub.id, [datetime.datetime.now(), (check_sub[1] + datetime.timedelta(days=day))]]]
                )
                current_user.subscript = dic_key
                new_trans = Transaction(transect_user_id=current_user,
                                        text='Продлена подписка %s на %s месяц' % (current_sub.name, month),
                                        price=-1 * current_sub.price * int(month))
                new_trans_admin = Transaction(transect_user_id=admin,
                                              text='%s продлил подписку %s на %s месяц' % (current_user.login,
                                                                                           current_sub.name,
                                                                                           month),
                                              price=current_sub.price * int(month))
                g.db.add(new_trans, new_trans_admin)
                g.db.commit()
                return redirect(url_for('profile'))
        else:
            dic_key = copy.copy(current_user.subscript) or {}
            dic_key.update(
                [[current_sub.id, [datetime.datetime.now(), (datetime.datetime.now() + datetime.timedelta(days=day))]]]
            )
            current_user.subscript = dic_key
            new_trans = Transaction(transect_user_id=current_user,
                                    text='Приобретена подписка %s на %s месяц' % (current_sub.name, month),
                                    price=-1 * current_sub.price * int(month))
            new_trans_admin = Transaction(transect_user_id=g.db.query(User).filter(User.id == 1).first(),
                                          text='%s преобрёл подписку %s на %s месяц' % (current_user.login,
                                                                                        current_sub.name,
                                                                                        month),
                                          price=current_sub.price * int(month))
            g.db.add(new_trans, new_trans_admin)
            g.db.commit()
            return redirect(url_for('profile'))
    return render_template('subscript_id.html',
                           error=error,
                           current_sub=current_sub,
                           month=month or '')
