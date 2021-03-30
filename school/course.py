# -*- coding: utf-8 -*-

import copy
import re
import datetime
from flask import g, redirect, render_template, request, url_for, jsonify
from flask_login import login_required, current_user
from sqlalchemy import and_, asc
from school import school
from school.database import Course, User, List, Transaction, Direction, Lesson, Setting, Blog
from school.right import check_rights, add_role

add_role('add_course', u"Создание курсов")


def check_sub_curs(course_id):
    if current_user.admin or g.db.query(Course).filter(and_(Course.user_id == current_user.id,
                                                            Course.id == int(course_id),
                                                            Course.ban == 0)).first():
        return True
    for key in current_user.sub_course.keys():
        if int(course_id) == key and current_user.sub_course[key][0] < datetime.datetime.now() < \
                current_user.sub_course[key][1]:
            return True
    return False


def sql_to_dict(item):
    return dict(
        name=item.name,
        id=item.id
    )


@school.route('/course', methods=['GET', 'POST'])
@login_required
def course():
    change_way = request.args.get('way')
    all_course = g.db.query(Course).filter(Course.ban == 0).all()
    my_course = g.db.query(Course).filter(and_(Course.ban == 0, Course.user_id == current_user.id)).all()
    all_ways = g.db.query(Direction).filter(Direction.ban == 0).all()
    courses = []
    sub_course = []
    for one in current_user.sub_course.keys():
        if check_sub_curs(one):
            courses.append(one)
    if courses:
        sub_course = g.db.query(
            Course.id,
            Course.name,
            Course.infinity
        ).filter(
            Course.id.in_(courses)
        ).all()
    if change_way:
        all_course = g.db.query(Course).filter(and_(Course.ban == 0, Course.direction_name == change_way)).all()
        all_course = list(map(sql_to_dict, all_course))
        return jsonify(all_course=all_course)
    return render_template('course.html',
                           all_course=all_course,
                           my_course=my_course,
                           sub_course=sub_course,
                           all_ways=all_ways)


@school.route('/add_course', methods=['GET', 'POST'])
@login_required
def add_course():
    error = None
    name = ''
    text = ''
    price = ''
    if not check_rights('add_course'):
        return redirect(url_for('subscript'))
    else:
        all_ways = g.db.query(Direction).all()
        if request.method == 'POST':
            name = request.form.get('name')
            text = request.form.get('text')
            direction_name = request.form.get('direction_name')
            price = request.form.get('price')
            infinity = request.form.get('infinity')
            if 5 > len(name) > 100:
                error = 'Название курса не должно быть меньше 5 и более 100 символов'
                return render_template('add_course.html',
                                       error=error,
                                       name=name,
                                       text=text,
                                       price=price,
                                       all_ways=all_ways)
            if text == '' or text is None:
                error = 'Описание курса не введено'
                return render_template('add_course.html',
                                       error=error,
                                       name=name,
                                       text=text,
                                       price=price,
                                       all_ways=all_ways)
            if direction_name == '' or direction_name is None:
                error = 'Напаравление не выбранно'
                return render_template('add_course.html',
                                       error=error,
                                       name=name,
                                       text=text,
                                       price=price,
                                       all_ways=all_ways)
            if re.search(r'^[0-9]{1,10}$', price) is None:
                error = 'Цена была введена не коректно'
                return render_template('add_course.html',
                                       error=error,
                                       name=name,
                                       text=text,
                                       price=price,
                                       all_ways=all_ways)
            if infinity == '1':
                infinity = True
            else:
                infinity = False
            new_course = Course(name=name,
                                text=text,
                                direction_name=direction_name,
                                price=int(price),
                                infinity=infinity,
                                user_id_course=current_user)
            g.db.add(new_course)
            g.db.commit()
            dic_key = copy.copy(current_user.sub_course) or {}
            dic_key[new_course.id] = [datetime.datetime.now(),
                                      (datetime.datetime.now() + datetime.timedelta(days=999999))]
            current_user.sub_course = dic_key
            set_f = copy.copy(current_user.follow)
            set_f.append(int(new_course.id))
            current_user.follow = set_f
            g.db.commit()
            return redirect(url_for('cur_course', course_id=new_course.id))
    return render_template('add_course.html',
                           error=error,
                           name=name,
                           text=text,
                           price=price,
                           all_ways=all_ways)


@school.route('/course/<int:course_id>', methods=['GET', 'POST'])
@login_required
def cur_course(course_id=None):
    list_lesson = request.args.get('list')
    error = None
    c_course = Course.get_cours(course_id)
    if not c_course:
        return redirect(url_for('course'))
    all_blog = g.db.query(Blog).filter(and_(Blog.course_id == c_course.id,
                                            Blog.ban == 0)).all()
    all_lesson_cur_course = g.db.query(Lesson).filter(and_(Lesson.cours_id == c_course.id,
                                                           Lesson.ban == 0)).order_by(asc(Lesson.number)).all()
    if list_lesson:
        new_list = list_lesson.split(',')
        for num in range(len(new_list)):
            gl = g.db.query(Lesson).filter(and_(Lesson.id == int(new_list[num]),
                                                Lesson.cours_id == int(course_id))).first()
            gl.number = num + 1
            g.db.commit()
    return render_template('cur_course.html',
                           error=error,
                           c_course=c_course,
                           all_lesson_cur_course=all_lesson_cur_course,
                           check=check_sub_curs(c_course.id),
                           all_blog=all_blog)


@school.route('/edit_course/<int:id_course>', methods=['GET', 'POST'])
@login_required
def edit_course(id_course=None):
    error = None
    course_for_edit = g.db.query(
        Course
    ).filter(
        and_(
            Course.id == int(id_course),
            Course.user_id == current_user.id,
            Course.ban == 0
        )
    ).first()
    if not current_user.admin and course_for_edit is None:
        return redirect(url_for('course'))
    else:
        if request.method == 'POST':
            name = request.form.get('name')
            text = request.form.get('text')
            price = request.form.get('price')
            infinity = request.form.get('infinity')
            if name != course_for_edit.name and name != '':
                course_for_edit.name = name
            if text != course_for_edit.text and text != '':
                course_for_edit.text = text
            if int(price) != course_for_edit.price and price != '':
                if re.search(r'^[0-9]{1,10}$', price) is None:
                    error = 'Цена введена не правильно'
                    return render_template('edit_course.html',
                                           error=error,
                                           course_for_edit=course_for_edit,
                                           name=name,
                                           text=text,
                                           price=price,
                                           infinity=infinity)
                else:
                    course_for_edit.price = int(price)
            if int(infinity) != course_for_edit.infinity and infinity != '':
                course_for_edit.infinity = int(infinity)
            g.db.commit()
            return redirect(url_for('cur_course', course_id=course_for_edit.id))
    return render_template('edit_course.html',
                           error=error,
                           course_for_edit=course_for_edit,
                           name=course_for_edit.name,
                           text=course_for_edit.text,
                           price=course_for_edit.price,
                           infinity=course_for_edit.infinity)


@school.route('/buy_course/<int:id_course>', methods=['GET', 'POST'])
def buy_course(id_course=None):
    error = None
    month = None
    cur_buy_course = Course.get_cours(id_course)
    if cur_buy_course is None:
        return redirect(url_for('course'))
    else:
        if request.method == 'POST':
            # prime peremen's
            check_user_sub_course = current_user.sub_course.get(cur_buy_course.id)
            setting = g.db.query(Setting).filter(Setting.id == 1).first()
            set_f = copy.copy(current_user.follow)
            # admin = g.db.query(User).filter(User.id == 1).first()
            # admin_course = g.db.query(User).filter(and_(User.id == cur_buy_course.user_id, User.ban == 0)).first()
            if cur_buy_course.infinity:
                if current_user.user_balance() < cur_buy_course.price:
                    error = 'У вас не достаточно средств'
                    return render_template('buy_course.html',
                                           error=error,
                                           cur_buy_course=cur_buy_course,
                                           month=month or '')
                if check_user_sub_course is None:
                    dic_key = copy.copy(current_user.sub_course) or {}
                    dic_key[cur_buy_course.id] = [datetime.datetime.now(),
                                                  (datetime.datetime.now() + datetime.timedelta(days=999999))]
                    current_user.sub_course = dic_key
                    new_trans = Transaction(transect_user_id=current_user,
                                            text='Приобретена пожизненая подписка %s' % cur_buy_course.name,
                                            price=-cur_buy_course.price)
                    new_user_to_list = List(user_to_list=current_user,
                                            lessons_number=1,
                                            user_to_course_list=cur_buy_course)
                    new_trans_admin = Transaction(transect_user_id=User.get_user(1),
                                                  text='Коммисия с приобритения курса %s' % cur_buy_course.name,
                                                  price=cur_buy_course.price * (setting.commission / 100))
                    new_trans_direc = Transaction(transect_user_id=User.get_user(cur_buy_course.user_id),
                                                  text='%s купил курс %s на всегда' % (current_user.login,
                                                                                       cur_buy_course.name),
                                                  price=cur_buy_course.price - (
                                                      cur_buy_course.price * (setting.commission / 100)))
                    if set_f.count(int(cur_buy_course.id)) == 0:
                        set_f.append(int(cur_buy_course.id))
                        current_user.follow = set_f
                    g.db.add(new_trans, new_user_to_list)
                    g.db.add(new_trans_admin, new_trans_direc)
                    g.db.commit()
                    return redirect(url_for('cur_course', course_id=cur_buy_course.id))
                else:
                    error = 'У вас уже куплен этот пожизненый курс'
                    return render_template('buy_course.html',
                                           error=error,
                                           cur_buy_course=cur_buy_course,
                                           month=month or '')
            else:
                month = request.form.get('month')
                if re.search(r'^[0-9]{1,3}$', month) is None:
                    error = 'Количество месяцев введено не верно'
                    return render_template('buy_course.html',
                                           error=error,
                                           cur_buy_course=cur_buy_course,
                                           month=month or '')
                day = int(month) * 30.5
                price_mount = cur_buy_course.price * int(month)
                if current_user.user_balance() < price_mount:
                    error = 'У вас не достаточно средств'
                    return render_template('buy_course.html',
                                           error=error,
                                           cur_buy_course=cur_buy_course,
                                           month=month or '')
                if check_user_sub_course is None:
                    dic_key = copy.copy(current_user.sub_course)
                    dic_key[cur_buy_course.id] = [datetime.datetime.now(),
                                                  (datetime.datetime.now() + datetime.timedelta(days=day))]
                    current_user.sub_course = dic_key
                    new_trans = Transaction(transect_user_id=current_user,
                                            text='Приобрёл подписка %s на %s месяц' % (cur_buy_course.name, month),
                                            price=-price_mount)
                    new_user_to_list = List(user_to_list=current_user,
                                            lessons_number=1,
                                            user_to_course_list=cur_buy_course)
                    new_trans_director = Transaction(transect_user_id=User.get_user(cur_buy_course.user_id),
                                                     text='%s приобрёл подписку на курс %s на %s' % (current_user.login,
                                                                                                     cur_buy_course.name,
                                                                                                     month),
                                                     price=price_mount - (price_mount * (setting.commission / 100)))
                    new_trans_admin = Transaction(transect_user_id=User.get_user(1),
                                                  text='Процент от курса %s ' % cur_buy_course.name,
                                                  price=price_mount * (setting.commission / 100))
                    if set_f.count(int(cur_buy_course.id)) == 0:
                        set_f.append(int(cur_buy_course.id))
                        current_user.follow = set_f
                    g.db.add(new_trans, new_trans_director)
                    g.db.add(new_trans_admin, new_user_to_list)
                    g.db.commit()
                    return redirect(url_for('cur_course', course_id=cur_buy_course.id))
                else:
                    dic_key = copy.copy(current_user.sub_course) or {}
                    dic_key.update(
                        [cur_buy_course.id,
                         [datetime.datetime.now(), (check_user_sub_course[1] + datetime.timedelta(days=day))]]
                    )
                    current_user.sub_course = dic_key
                    new_trans = Transaction(transect_user_id=current_user,
                                            text='Продлил подписка %s на %s месяц' % (cur_buy_course.name, month),
                                            price=-price_mount)
                    new_trans_director = Transaction(transect_user_id=User.get_user(cur_buy_course.user_id),
                                                     text='%s продлил подписку на курс %s на %s' % (current_user.login,
                                                                                                    cur_buy_course.name,
                                                                                                    month),
                                                     price=price_mount - (
                                                         price_mount * (setting.commission / 100)))
                    new_trans_admin = Transaction(transect_user_id=User.get_user(1),
                                                  text='Процент от курса %s' % cur_buy_course.name,
                                                  price=price_mount * (setting.commission / 100))
                    g.db.add(new_trans, new_trans_director)
                    g.db.add(new_trans_admin)
                    g.db.commit()
                    return redirect(url_for('cur_course', course_id=cur_buy_course.id))
    return render_template('buy_course.html',
                           error=error,
                           cur_buy_course=cur_buy_course,
                           month=month or '')


@school.route('/list_students/<int:course_id>', methods=['GET', 'POST'])
@login_required
def list_students_course(course_id=None):
    if Course.get_cours(course_id) is None or current_user.id != Course.get_cours(course_id).user_id:
        return redirect(url_for('course'))
    get_all_user_in_list = g.db.query(
        List.id,
        List.courses_id,
        List.ban,
        List.user_id,
        User.login,
        User.email,
    ).join(
        User,
        User.id == List.user_id
    ).filter(
        and_(
            List.courses_id == Course.get_cours(course_id).id,
            List.ban == 0
        )
    ).all()
    return render_template('list_students_course.html',
                           get_all_user_in_list=get_all_user_in_list,
                           get_course=Course.get_cours(course_id))
