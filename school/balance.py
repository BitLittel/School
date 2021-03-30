# -*- coding: utf-8 -*-
from school import school
from flask import g, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from school.database import Transaction, User, Notice
import re


@school.route('/refill', methods=['GET', 'POST'])
@login_required
def refill():
    error = None
    price = None
    if request.method == "POST":
        price = request.form.get('price')
        print(price)
        if re.search(r'^[0-9]{1,10}$', price) is None:
            error = 'Введите сумму коректно'
            return render_template('refil.html',
                                   error=error,
                                   price=price)
        new_trans = Transaction(transect_user_id=current_user,
                                text='Пополнен баланс на сумму %s' % price,
                                price=int(price))
        g.db.add(new_trans)
        g.db.commit()
        return redirect(url_for('profile'))
    return render_template('refil.html',
                           error=error,
                           price=price)


@school.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    error = None
    user_to_login = None
    price = None
    if request.method == 'POST':
        user_to_login = request.form.get('user_to_login')
        price = request.form.get('price')
        if re.search(r'^[0-9]{1,10}$', price) is None:
            error = 'Введите сумму коректно'
            return render_template('transfer.html',
                                   error=error,
                                   user_to_login=user_to_login,
                                   price=price)
        price = int(price)
        if user_to_login is None or user_to_login == '':
            error = 'Логин введён не верно'
            return render_template('transfer.html',
                                   error=error,
                                   user_to_login=user_to_login,
                                   price=price)
        user_to = g.db.query(User).filter(User.login == user_to_login).first()
        if user_to is None:
            error = 'Пользователя с таким логином не существует'
            return render_template('transfer.html',
                                   error=error,
                                   user_to_login=user_to_login,
                                   price=price)
        if current_user.user_balance() < price:
            error = 'У вас недостаточно средств'
            return render_template('transfer.html',
                                   error=error,
                                   user_to_login=user_to_login,
                                   price=price)
        new_trans_1 = Transaction(transect_user_id=current_user,
                                  text='Перевод средств на сумму: %s. От пользователя: %s' % (price,
                                                                                              current_user.login),
                                  price=price)
        new_trans_2 = Transaction(transect_user_id=user_to,
                                  text='Перевод средств на сумму: %s. Пользователю: %s' % (price,
                                                                                           user_to_login),
                                  price=-price)
        g.db.add(new_trans_1, new_trans_2)
        g.db.commit()
        error = 'Перевод успешно совершон'
        return render_template('transfer.html',
                               error=error,
                               user_to_login=user_to_login,
                               price=price)
    return render_template('transfer.html',
                           error=error,
                           user_to_login=user_to_login,
                           price=price)


@school.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    error = None
    price = ''
    if request.method == 'POST':
        price = request.form.get('price')
        if re.search(r'^[0-9]{3,10}$', price) is None:
            error = 'Данные введены не верно'
            return render_template('withdraw.html',
                                   error=error,
                                   price=price)
        price = int(price)
        if price > current_user.user_balance():
            error = 'У вас не достаточно средств'
            return render_template('withdraw.html',
                                   error=error,
                                   price=price)
        new_trans = Transaction(transect_user_id=current_user,
                                price=-1*int(price),
                                text='Вывод средства на сумму %s поступили на обработку' % price,
                                withdraw=True)
        new_notice = Notice(notice_to_user=current_user,
                            text='Вывод средства на сумму %s в обработке' % price)
        admin = g.db.query(User).filter(User.id == 1).first()
        text = 'Вывод средства на сумму %s от пользователя %s поступили на обработку.' % (price, current_user.login)
        new_notice_for_admin = Notice(notice_to_user=admin,
                                      text=text,
                                      hypertext='http://%s/list_withdraw' % school.config['HOST_AND_PORT'])
        g.db.add(new_trans, new_notice)
        g.db.add(new_notice_for_admin)
        g.db.commit()
        error = 'В течении 24-ёх часов проверят вашу транзакцию'
        return render_template('withdraw.html',
                               error=error,
                               price='')
    return render_template('withdraw.html',
                           error=error,
                           price=price)
