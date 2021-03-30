# -*- coding: utf-8 -*-

import sys
import datetime
import os
import hashlib
import re
from PIL import Image
from school import school
from flask import render_template, g, request, redirect, url_for, jsonify
from flask_login import current_user, login_required, login_user, logout_user
from school.database import User, Setting, Subscript, Transaction, Photo, Notice, Dialog, MessageUser, Course
from sqlalchemy import and_, or_, desc
from flask_mail import Message, Mail
from school.course import check_sub_curs

mail = Mail(school)


def send_message(subject, recipients, body, html=None):
    msg = Message(subject=subject,
                  sender=school.config['MAIL_USERNAME'],
                  recipients=[recipients],
                  body=body,
                  html=html)
    mail.send(msg)
    return 'OK'


def sum_all_notice():
    notice = g.db.query(
        Notice
    ).filter(
        and_(
            Notice.user_id == current_user.id,
            Notice.ban == 0,
            Notice.read == 0
        )
    ).count()
    return notice


def wait_mess():
    mess = g.db.query(
        MessageUser
    ).filter(
        and_(MessageUser.user_to == current_user.id,
             MessageUser.wait == 1,
             MessageUser.ban == 0)
    ).count()
    return mess


@school.route('/reg_user', methods=['GET', 'POST'])
def reg_user():
    error = None
    email = None
    if request.method == 'POST':
        email = request.form.get('email')
        if g.db.query(User).filter(User.email == email).first():
            error = 'Эта почта занята'
            return render_template('reg_user.html',
                                   error=error,
                                   email=email)
        if re.search(r'^([a-z0-9_-]+\.)*[a-z0-9_-]+@[a-z0-9_-]+(\.[a-z0-9_-]+)*\.[a-z]{2,6}$', email) is None:
            error = 'Почта введена не верно'
            return render_template('reg_user.html',
                                   error=error,
                                   email=email)
        h = hashlib.new('sha1')
        h.update(email.encode('utf-8'))
        text = u'Регистрация http://%s/reg_user_end/%s' % (school.config['HOST_AND_PORT'], h.hexdigest())
        new_user = User(login=None,
                        email=email,
                        password=None)
        photo = Photo(photo_user=new_user, photo="1.png", photo_small="2.png")
        g.db.add(new_user, photo)
        g.db.commit()
        if new_user.id == 1:
            new_setting = Setting(commission=10)
            g.db.add(new_setting)
            new_user.admin = True
            g.db.commit()
        send_message('Регистрация', u''+email, text)
        error = 'Сообщение успешно отправлено на почту'
        return render_template('reg_user.html',
                               error=error,
                               email=email)
    return render_template('reg_user.html',
                           error=error,
                           email=email)


@school.route('/reg_user_end/<hash_email>', methods=['GET', 'POST'])
def reg_user_end(hash_email):
    error = None
    user_login = None
    pass_1 = None
    pass_2 = None
    user = g.db.query(User).filter(User.password == None).all()
    for s in range(len(user)):
        h = hashlib.new('sha1')
        h.update(user[s].email.encode('utf-8'))
        if h.hexdigest() == hash_email:
            right_user = user[s]
            break
    else:
        return redirect(url_for('login'))
    if request.method == 'POST':
        user_login = request.form.get('login')
        if re.search(r'^[a-zA-Z0-9-_.]{5,20}$', user_login) is None:
            error = 'Логин введён не коректно.'
            return render_template('reg_user.html',
                                   error=error,
                                   user_login=user_login,
                                   pass_1=pass_1,
                                   pass_2=pass_2)
        if g.db.query(User).filter(User.login == user_login).first():
            error = 'Этот логин уже занят'
            return render_template('reg_user.html',
                                   error=error,
                                   user_login=user_login,
                                   pass_1=pass_1,
                                   pass_2=pass_2)
        pass_1 = request.form.get('password')
        if re.search(r'^[a-zA-Z0-9_.]{5,16}$', pass_1) is None:
            error = 'Пароль введён не коректно. Пароль должен быть от 5 до 16 символов латинского алфавита'
            return render_template('reg_user.html',
                                   error=error,
                                   user_login=user_login,
                                   pass_1=pass_1,
                                   pass_2=pass_2)
        pass_2 = request.form.get('password_2')
        if pass_1 != pass_2:
            error = 'Пароли не совподают'
            return render_template('reg_user.html',
                                   error=error,
                                   user_login=user_login,
                                   pass_1=pass_1,
                                   pass_2=pass_2)
        h = hashlib.new('sha1')
        h.update(pass_1.encode('utf-8'))
        right_user.login = user_login
        right_user.password = h.hexdigest()
        g.db.commit()
        login_user(right_user, remember=True)
        return redirect(url_for('index'))
    return render_template('reg_user_end.html',
                           error=error,
                           user_login=user_login,
                           pass_1=pass_1,
                           pass_2=pass_2)


@school.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user_email = request.form.get('email')
        password = request.form.get('password')
        h = hashlib.new('sha1')
        h.update(password.encode('utf-8'))
        user = g.db.query(User).filter(and_(User.email == user_email,
                                            User.password == h.hexdigest(),
                                            User.ban == 0
                                            )).first()
        if user:
            login_user(user, remember=True)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('index'))
        else:
            error = "Неправильно введён логин или пароль"
            return render_template('login.html', error=error)
    return render_template('login.html', error=error)


@school.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    error = None
    all_trans = g.db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(
        desc(Transaction.data)
    ).all()
    courses = []
    subscripts = []
    for one in current_user.sub_course.keys():
        if check_sub_curs(one):
            courses.append(one)
    if courses:
        subscripts = g.db.query(
            Course.id,
            Course.name,
            Course.infinity,
            Course.user_id
        ).filter(
            Course.id.in_(courses)
        ).all()
    tarif_id = []
    for one in current_user.subscript.keys():
        if current_user.subscript[one][0] < datetime.datetime.now() < current_user.subscript[one][1]:
            tarif_id.append(one)
    if tarif_id:
        tarif = g.db.query(Subscript).filter(Subscript.id.in_(tarif_id)).first()
    else:
        tarif = None
    return render_template('profile.html',
                           error=error,
                           transactions=all_trans,
                           tarif=tarif or [],
                           subscripts=subscripts,
                           courses=courses)


@school.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    error = None
    photo = None
    about_us = None
    new_login = None
    if request.method == 'POST':
        password = request.form.get('password')
        about_us = request.form.get('about_us')
        new_login = request.form.get('new_login')
        photo = request.files.get('photo')
        if re.search(r'^[a-zA-Z0-9_]{5,16}$', password) is None and current_user.password != password:
            error = 'Пароль был введён не верно'
            return render_template('edit_profile.html',
                                   error=error,
                                   about_us=about_us or '',
                                   new_login=new_login or '',
                                   photo=photo or '')
        if about_us != '':
            current_user.about_us = about_us
        if new_login != '':
            if re.search(r'^[a-zA-Z0-9_]{5,16}$', new_login) is None:
                error = 'Логин введён не коректно. Логин должен быть от 5 до 16 символов латинского алфавита'
                return render_template('edit_profile.html',
                                       error=error,
                                       about_us=about_us or '',
                                       new_login=new_login or '',
                                       photo=photo or '')
            if g.db.query(User).filter(User.login == new_login).first():
                error = 'Этот логин уже занят'
                return render_template('edit_profile.html',
                                       error=error,
                                       about_us=about_us or '',
                                       new_login=new_login or '',
                                       photo=photo or '')
            current_user.login = new_login
        if photo.filename != '':
            path = sys.path[0]
            photo.save(os.path.join(path, "school", "static", "img", "250", photo.filename))
            im = Image.open(os.path.join(path, "school", "static", "img", "250", photo.filename))
            im.crop(
                (round(im.size[0] / 2) - round(im.size[1] / 2),
                 0,
                 round(im.size[0] / 2) + round(im.size[1] / 2),
                 im.size[1])
            ).save(os.path.join(path, "school", "static", "img", "250", photo.filename))
            img = Image.open(os.path.join(path, "school", "static", "img", "250", photo.filename))
            img.thumbnail((250, 250))
            img.save(os.path.join(path, "school", "static", "img", "250", photo.filename))
            photo_small = Image.open(os.path.join(path, "school", "static", "img", "250", photo.filename))
            small = photo_small.resize((40, 40))
            small.save(os.path.join(path, "school", "static", "img", "40", photo.filename))
            new_photo = g.db.query(Photo).filter(Photo.user_id == current_user.id).first()
            new_photo.photo = photo.filename
            new_photo.photo_small = photo.filename
        g.db.commit()
        return redirect(url_for('profile'))
    return render_template('edit_profile.html',
                           error=error,
                           about_us=about_us or '',
                           new_login=new_login or '',
                           photo=photo or '')


@school.route('/chang_pass', methods=['GET', 'POST'])
@login_required
def chang_pass():
    error = None
    cur_pass = None
    new_pass_1 = None
    new_pass_2 = None
    if request.method == 'POST':
        cur_pass = request.form.get('cur_pass')
        new_pass_1 = request.form.get('new_pass_1')
        new_pass_2 = request.form.get('new_pass_2')
        h = hashlib.new('sha1')
        h.update(cur_pass.encode('utf-8'))
        if h.hexdigest() != current_user.password:
            error = 'Введёный вами "текущий пароль" не верен'
            return render_template('chang_pass.html',
                                   error=error,
                                   cur_pass=cur_pass or '',
                                   new_pass_1=new_pass_1 or '',
                                   new_pass_2=new_pass_2 or '')
        if re.search(r'^[a-zA-Z0-9_]{5,16}$', new_pass_1) is None:
            error = 'новый пароль не соответствует формату'
            return render_template('chang_pass.html',
                                   error=error,
                                   cur_pass=cur_pass or '',
                                   new_pass_1=new_pass_1 or '',
                                   new_pass_2=new_pass_2 or '')
        if new_pass_2 != new_pass_1:
            error = 'Новые пароли не совподают'
            return render_template('chang_pass.html',
                                   error=error,
                                   cur_pass=cur_pass or '',
                                   new_pass_1=new_pass_1 or '',
                                   new_pass_2=new_pass_2 or '')
        hh = hashlib.new('sha1')
        hh.update(new_pass_1.encode('utf-8'))
        current_user.password = hh.hexdigest()
        g.db.commit()
        return redirect(url_for('profile'))
    return render_template('chang_pass.html',
                           error=error,
                           cur_pass=cur_pass or '',
                           new_pass_1=new_pass_1 or '',
                           new_pass_2=new_pass_2 or '')


@school.route('/message', methods=['GET', 'POST'])
@login_required
def message():
    get_all_dialog = g.db.query(
        Dialog.user_login,
        Dialog.user,
        MessageUser.text,
        MessageUser.wait,
        MessageUser.time
    ).join(
        MessageUser,
        MessageUser.id == Dialog.message_id
    ).filter(
        or_(
            and_(
                Dialog.user_login == current_user.login,
                Dialog.ban == 0
            ),
            and_(
                Dialog.user == current_user.login,
                Dialog.ban == 0
            )
        )
    ).order_by(desc(Dialog.id)).all()
    return render_template('message.html',
                           all_dialog=get_all_dialog)


def sql_to_dict_mess(item):
    return dict(
        cur_user_login=current_user.login,
        cur_user_id=current_user.id,
        text=item.text,
        user_id=item.user_id,
        user_to=item.user_to,
        datatime=item.time
    )


@school.route('/message/<user_login>', methods=['GET', 'POST'])
@login_required
def dialog(user_login=None):
    error = None
    check_user = g.db.query(User).filter(and_(User.login == user_login, User.ban == 0)).first()
    if check_user is None:
        return redirect(404)
    mess_get = request.args.get('mess_get')
    ajax = request.args.get('ajax')
    get_all_mes = g.db.query(
        MessageUser
    ).filter(
        or_(
            and_(
                MessageUser.user_id == current_user.id,
                MessageUser.user_to == check_user.id,
                MessageUser.ban == 0
            ),
            and_(
                MessageUser.user_id == check_user.id,
                MessageUser.user_to == current_user.id,
                MessageUser.ban == 0
            )
        )
    ).all()
    for k in range(len(get_all_mes)):
        if get_all_mes[k].user_to == current_user.id and get_all_mes[k].wait is True:
            get_all_mes[k].wait = False
    g.db.commit()
    if mess_get:
        if mess_get == '' or mess_get is None or mess_get == []:
            return False
        new_mess = MessageUser(text=mess_get,
                               user_id_mess=current_user,
                               user_to=check_user.id)
        check_dialog = g.db.query(
            Dialog
        ).filter(
            or_(
                and_(
                    Dialog.user_login == current_user.login,
                    Dialog.user == check_user.login,
                    Dialog.ban == 0
                ),
                and_(
                    Dialog.user_login == check_user.login,
                    Dialog.user == current_user.login,
                    Dialog.ban == 0
                )
            )
        ).first()
        g.db.add(new_mess)
        g.db.commit()
        if check_dialog is None:
            new_dialog = Dialog(user_login=current_user.login,
                                user=check_user.login,
                                message_id_dialog=new_mess)
            g.db.add(new_dialog)
            g.db.commit()
        else:
            check_dialog.user_login = current_user.login
            check_dialog.user = check_user.login
            check_dialog.message_id = new_mess.id
            g.db.commit()
    if ajax:
        all_mes = g.db.query(
            MessageUser
        ).filter(
            or_(
                and_(
                    MessageUser.user_id == current_user.id,
                    MessageUser.user_to == check_user.id,
                    MessageUser.ban == 0
                ),
                and_(
                    MessageUser.user_id == check_user.id,
                    MessageUser.user_to == current_user.id,
                    MessageUser.ban == 0
                )
            )
        ).all()
        for k in range(len(all_mes)):
            if all_mes[k].user_to == current_user.id and all_mes[k].wait is True:
                all_mes[k].wait = False
        g.db.commit()
        all_mes = list(map(sql_to_dict_mess, all_mes))
        return jsonify(all_mes=all_mes)
    # if request.method == 'POST':
    #     mess = request.form.get('mess')
    #     if mess == '' or mess is None:
    #         error = 'Вы не ввели сообщение'
    #         return render_template('dialog.html',
    #                                all_mes=get_all_mes,
    #                                check_user=check_user,
    #                                error=error)
    #     new_mess = MessageUser(text=mess,
    #                            user_id_mess=current_user,
    #                            user_to=check_user.id)
    #     check_dialog = g.db.query(
    #         Dialog
    #     ).filter(
    #         or_(
    #             and_(
    #                 Dialog.user_login == current_user.login,
    #                 Dialog.user == check_user.login,
    #                 Dialog.ban == 0
    #             ),
    #             and_(
    #                 Dialog.user_login == check_user.login,
    #                 Dialog.user == current_user.login,
    #                 Dialog.ban == 0
    #             )
    #         )
    #     ).first()
    #     g.db.add(new_mess)
    #     g.db.commit()
    #     if check_dialog is None:
    #         new_dialog = Dialog(user_login=current_user.login,
    #                             user=check_user.login,
    #                             message_id_dialog=new_mess)
    #         g.db.add(new_dialog)
    #         g.db.commit()
    #     else:
    #         check_dialog.user_login = current_user.login
    #         check_dialog.user = check_user.login
    #         check_dialog.message_id = new_mess.id
    #         g.db.commit()
    #     return redirect(url_for('dialog', user_login=user_login))
    return render_template('dialog.html',
                           all_mes=get_all_mes,
                           check_user=check_user,
                           error=error,
                           cur_user_avatar=current_user.avatar(50),
                           user_avatar=check_user.avatar(50))


def sql_to_dict(item):
    return dict(
        login=item.login,
        email=item.email,
        avatar=item.avatar(50)
    )


@school.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    search_arg = request.args.get('search')
    if search_arg:
        search_arg = search_arg.split(' ')
        all_user = g.db.query(
            User
        ).filter(
            and_(
                or_(
                    and_(*map(lambda x: User.login.like('%%%s%%' % x), search_arg)),
                    and_(*map(lambda x: User.email.like('%%%s%%' % x), search_arg))
                ),
                User.ban == 0
            )
        ).all()
        all_user = list(map(sql_to_dict, all_user))
        return jsonify(all_user=all_user)
    return render_template('search.html')


@school.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

