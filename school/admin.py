# -*- coding: utf-8 -*-

from school import school
import re
from flask import g, redirect, request, url_for, render_template
from flask_login import login_required, current_user
from school.database import Setting, Subscript, User, Direction, Transaction, Notice
from school.right import right


@school.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    error = None
    new_way = None
    commission = None
    if not current_user.admin:
        return redirect(url_for('profile', user_id=current_user.id))
    setting = g.db.query(Setting).filter(Setting.id == 1).first()
    all_ways = g.db.query(Direction).all()
    all_users = g.db.query(User).all()
    if request.method == "POST":
        if request.form.get('commission_1'):
            commission = request.form.get('commission')
            if re.search(r'^[0-9]{1,2}$', commission) is None:
                error = "Данный введены не корректно"
                return render_template('admin.html',
                                       error=error,
                                       setting=setting,
                                       commission=commission or '',
                                       all_ways=all_ways,
                                       new_way=new_way or '',
                                       all_users=all_users)
            setting.commission = int(commission)
            g.db.commit()
        if request.form.get('new_way_2'):
            new_way = request.form.get('new_way')
            if re.search(r'^[а-яА-Я]{1,50}', new_way) is None:
                error = 'Направление введено не коректно'
                return render_template('admin.html',
                                       error=error,
                                       setting=setting,
                                       commission=commission or '',
                                       all_ways=all_ways,
                                       new_way=new_way or '',
                                       all_users=all_users)
            add_new_way = Direction(name=new_way)
            g.db.add(add_new_way)
            g.db.commit()
            return redirect(url_for('admin'))
    return render_template('admin.html',
                           setting=setting,
                           error=error,
                           commission=setting.commission,
                           all_ways=all_ways,
                           new_way=new_way or '',
                           all_users=all_users)


@school.route('/add_sub', methods=['GET', 'POST'])
@login_required
def add_sub():
    error = None
    if current_user.admin:
        if request.method == "POST":
            name_sub = request.form.get('name_sub')
            price = request.form.get('price')
            check_sub_right = request.form.get('check_sub_right')
            about_sub = request.form.get('about_sub')
            new_sub = Subscript(name=name_sub,
                                right=check_sub_right,
                                about_sub=about_sub,
                                price=price)
            g.db.add(new_sub)
            g.db.commit()
            return redirect(url_for('subscript'))
    else:
        return redirect(url_for("index"))
    return render_template('add_sub.html',
                           error=error,
                           right=right)


@school.route('/list_withdraw', methods=['GET', 'POST'])
@login_required
def list_withdraw():
    error = None
    if current_user.admin:
        all_trans = g.db.query(Transaction).filter(Transaction.withdraw == 1).all()
        if request.method == "POST":
            if request.form.get('accept'):
                get_trans = g.db.query(Transaction).filter(
                    Transaction.id == int(request.form.get('accept'))
                ).first()
                get_trans.withdraw = False
                get_user = g.db.query(User).filter(User.id == get_trans.user_id).first()
                # TODO: НУ а тут запелить вывод через api
                new_notice = Notice(notice_to_user=get_user,
                                    text='Ваш последний вывод потверждён')
                g.db.add(new_notice)
            if request.form.get('pass'):
                get_trans = g.db.query(Transaction).filter(
                    Transaction.id == int(request.form.get('pass'))
                ).first()
                get_trans.withdraw = False
                get_user = g.db.query(User).filter(User.id == get_trans.user_id).first()
                new_trans = Transaction(transect_user_id=get_user,
                                        price=-1*get_trans.price,
                                        text='Последний вывод отклонён.')
                new_notice = Notice(notice_to_user=get_user,
                                    text='Извините, но ваш последний вывод отклонён')
                g.db.add(new_trans, new_notice)
            g.db.commit()
            return redirect(url_for('list_withdraw'))
    else:
        return redirect(url_for("index"))
    return render_template('list_withdraw.html',
                           error=error,
                           all_trans=all_trans)
