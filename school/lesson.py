# -*- coding: utf-8 -*-

import re
import datetime
from flask import g, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from sqlalchemy import and_, asc, desc
from school import school
from school.database import Course, User, Lesson, HomeWork, List, Notice, TestInDay
from school.course import check_sub_curs


def check_homework_wait(lesson_id, course_id):
    return g.db.query(HomeWork).filter(and_(HomeWork.lessons_id == int(lesson_id),
                                            HomeWork.courses_id == int(course_id),
                                            HomeWork.user_id == current_user.id)).order_by(desc(HomeWork.data)).first()


def check_homework_done(course_id, lesson_number):
    if current_user.admin or Course.get_cours(course_id).user_id == current_user.id:
        return True
    else:
        check_lesson = g.db.query(Lesson).filter(and_(Lesson.cours_id == int(course_id),
                                                      Lesson.number == int(lesson_number) - 1,
                                                      Lesson.ban == 0)).first()
        if check_lesson is None:
            return True
        else:
            if check_homework_wait(check_lesson.id, course_id) is None:
                return False
            if check_homework_wait(check_lesson.id, course_id).done:
                return True
            else:
                return False


@school.route('/add_lesson/<int:course_id>', methods=['GET', 'POST'])
@login_required
def add_lesson(course_id=None):
    error = None
    name = None
    homework = None
    questions_result = None
    persent_for_test = None
    homework_type = None
    content = None
    test_in_day = None
    gc = Course.get_cours(course_id)
    if gc is None or gc.user_id != current_user.id:
        return redirect(url_for('course'))
    if request.method == 'POST':
        name = request.form.get('name')
        content = request.form.get('content')
        homework_type = request.form.get('homework_type')
        if name == '' or name is None:
            error = 'Название не введено'
            return render_template('add_lesson.html',
                                   error=error,
                                   name=name or '',
                                   test_in_day=test_in_day or '',
                                   persent_for_test=persent_for_test or '',
                                   homework_type=homework_type or '',
                                   content=content or '')
        if 5 > len(name) > 100:
            error = 'Название урока должно быть от 5 до 100 символов'
            return render_template('add_lesson.html',
                                   error=error,
                                   name=name or '',
                                   test_in_day=test_in_day or '',
                                   persent_for_test=persent_for_test or '',
                                   homework_type=homework_type or '',
                                   content=content or '')
        if content == '' or content is None:
            error = 'Содержимое не введено'
            return render_template('add_lesson.html',
                                   error=error,
                                   name=name or '',
                                   test_in_day=test_in_day or '',
                                   persent_for_test=persent_for_test or '',
                                   homework_type=homework_type or '',
                                   content=content or '')
        if homework_type == 'homework':
            homework = request.form.get('homework')
            if homework == '' or homework is None:
                error = 'Домашнее задание не введено'
                return render_template('add_lesson.html',
                                       error=error,
                                       name=name or '',
                                       test_in_day=test_in_day or '',
                                       persent_for_test=persent_for_test or '',
                                       homework_type=homework_type or '',
                                       content=content or '')
        elif homework_type == 'test':
            test_in_day = request.form.get('test_in_day')
            persent_for_test = request.form.get('persent_for_test')
            questions_result = []
            quest = request.form.getlist("quest")
            for i in range(len(quest)):
                questions_result.append(dict(quest=quest[i],
                                             answers=request.form.getlist("answer_%s" % i),
                                             right=request.form.get("right_%s" % i)
                                             ))
            if quest == '' or quest is None:
                error = 'Тест не введён'
                return render_template('add_lesson.html',
                                       error=error,
                                       name=name or '',
                                       test_in_day=test_in_day or '',
                                       persent_for_test=persent_for_test or '',
                                       homework_type=homework_type or '',
                                       content=content or '')
            if re.search(r'[0-9]{1,3}$', test_in_day) is None:
                error = 'Кол-во попыток в день не введено'
                return render_template('add_lesson.html',
                                       error=error,
                                       name=name or '',
                                       test_in_day=test_in_day or '',
                                       persent_for_test=persent_for_test or '',
                                       homework_type=homework_type or '',
                                       content=content or '')
            if re.search(r'[0-9]{1,3}$', persent_for_test) is None:
                error = 'Процент для теста не введён или введён не верно'
                return render_template('add_lesson.html',
                                       error=error,
                                       name=name or '',
                                       test_in_day=test_in_day or '',
                                       persent_for_test=persent_for_test or '',
                                       homework_type=homework_type or '',
                                       content=content or '')
        elif homework_type == 'free':
            error = None
        else:
            error = 'Тип выбран не верно'
            return render_template('add_lesson.html',
                                   error=error,
                                   name=name or '',
                                   test_in_day=test_in_day or '',
                                   persent_for_test=persent_for_test or '',
                                   homework_type=homework_type or '',
                                   content=content or '')
        get_all_lesson_in_course = g.db.query(Lesson.number).filter(and_(Lesson.cours_id == int(course_id),
                                                                         Lesson.ban == 0)).all()
        if get_all_lesson_in_course == [] or get_all_lesson_in_course is None:
            next_num = 1
        else:
            next_num = max(get_all_lesson_in_course).number + 1
        new_lesson = Lesson(name=name,
                            number=next_num,
                            content=content,
                            homework_type=homework_type,
                            homework=homework,
                            test=questions_result,
                            persent_for_test=persent_for_test,
                            test_in_day=test_in_day,
                            lessons_course_id=gc)
        g.db.add(new_lesson)
        g.db.commit()
        return redirect(url_for('lesson', course_id=int(course_id), lesson_id=new_lesson.id))
    return render_template('add_lesson.html',
                           error=error,
                           name=name or '',
                           persent_for_test=persent_for_test or '',
                           homework_type=homework_type or '',
                           content=content or '')


@school.route('/course/<int:course_id>/<int:lesson_id>', methods=['GET', 'POST'])
@login_required
def lesson(course_id=None, lesson_id=None):
    homework = ''
    error = None
    gc = Course.get_cours(course_id)
    if gc is None:
        return redirect(url_for('course'))
    gl = Lesson.get_lesson(lesson_id)
    if gl is None or not check_sub_curs(int(course_id)) or not check_homework_done(int(course_id), int(gl.number)):
        return redirect(url_for('cur_course', course_id=course_id))
    check_test = g.db.query(TestInDay).filter(and_(TestInDay.user_id == current_user.id,
                                                   TestInDay.lesson_id == gl.id,
                                                   TestInDay.ban == 0)).first()
    if request.method == 'POST':
        change_list = g.db.query(List).filter(and_(List.user_id == current_user.id,
                                                   List.courses_id == gc.id)).first()
        if gl.homework_type == 'homework':
            homework = request.form.get('homework')
            if homework == '' or homework is None:
                error = 'Вы не ввели домашнее задание'
                return render_template('lesson.html',
                                       lesson=gl,
                                       course=gc,
                                       homework=homework,
                                       error=error,
                                       chcl=check_homework_wait(lesson_id, course_id))
            else:
                change_list.lessons_number = gl.number + 1
                new_homework = HomeWork(homework_num=gl,
                                        course_user=gc,
                                        wait=True,
                                        text=homework,
                                        done=False,
                                        user_homework=current_user)
                new_notice = Notice(notice_to_user=User.get_user(gc.user_id),
                                    text='Пришла домашня работа на проверку от %s' % current_user.login,
                                    hypertext='http://%s/list_homework/%s' % (school.config['HOST_AND_PORT'], gc.id),
                                    read=False)
                g.db.add(new_homework, new_notice)
                g.db.commit()
                return redirect(url_for('cur_course', course_id=int(course_id)))
        if gl.homework_type == 'free':
            change_list.lessons_number = gl.number + 1
            new_homework = HomeWork(homework_num=gl,
                                    course_user=gc,
                                    wait=False,
                                    done=True,
                                    user_homework=current_user)
            g.db.add(new_homework)
            g.db.commit()
            return redirect(url_for('cur_course', course_id=int(course_id)))
        if gl.homework_type == 'test':
            if check_test is not None:
                if check_test.data[0] < datetime.datetime.now() < check_test.data[1]:
                    if check_test.count == gl.test_in_day:
                        error = "У вас закончились попытки, приходите завтра"
                        return render_template('lesson.html',
                                               lesson=gl,
                                               course=gc,
                                               error=error,
                                               chcl=check_homework_wait(lesson_id, course_id))
                if check_test.data[1] < datetime.datetime.now():
                    check_test.ban = True
                    g.db.commit()
                    check_test = None
            change_list.lessons_number = gl.number + 1
            right_answer_user = 0
            for number in range(len(gl.test)):
                if int(request.form.get('right_%s' % number)) == int(gl.test[number]['right']):
                    right_answer_user += 1
            persent_right_answer_user = (right_answer_user/len(gl.test)) * 100
            if gl.persent_for_test <= persent_right_answer_user:
                if check_test is not None:
                    check_test.ban = True
                new_homework = HomeWork(homework_num=gl,
                                        course_user=gc,
                                        wait=False,
                                        done=True,
                                        user_homework=current_user)
                g.db.add(new_homework)
                g.db.commit()
                return redirect(url_for('cur_course', course_id=int(course_id)))
            else:
                if check_test is None:
                    new_testinday = TestInDay(user_test_in_day=current_user,
                                              test_lesson=gl,
                                              count=1,
                                              data=[datetime.datetime.now(),
                                                    datetime.datetime.now() + datetime.timedelta(days=1)])
                    g.db.add(new_testinday)
                    g.db.commit()
                    error = "Вы не прошли тест. Попробуйте пройти тест ещё раз. " \
                            "Осталось попыток(в день): %s" % (gl.test_in_day - 1)
                    return render_template('lesson.html',
                                           course=gc,
                                           lesson=gl,
                                           error=error,
                                           chcl=check_homework_wait(lesson_id, course_id))
                else:
                    check_test.count = check_test.count + 1
                    g.db.commit()
                    error = "Вы не прошли тест. Попробуйте пройти тест ещё раз. " \
                            "Осталось попыток(в день): %s" % (gl.test_in_day - check_test.count)
                    return render_template('lesson.html',
                                           course=gc,
                                           lesson=gl,
                                           error=error,
                                           chcl=check_homework_wait(lesson_id, course_id))
    return render_template('lesson.html',
                           course=gc,
                           lesson=gl,
                           homework=homework,
                           error=error,
                           chcl=check_homework_wait(lesson_id, course_id))


@school.route('/list_homework/<int:course_id>', methods=['GET', 'POST'])
@login_required
def list_homework(course_id=None):
    error = None
    gc = Course.get_cours(course_id)
    if gc is None or current_user.id != gc.user_id:
        return redirect(url_for('cur_course', course_id=int(course_id)))
    get_all_homework = g.db.query(
        HomeWork.id,
        HomeWork.wait,
        HomeWork.lessons_id,
        HomeWork.courses_id,
        HomeWork.text,
        Lesson.name,
        Lesson.number,
        User.login,
    ).join(
        User,
        User.id == HomeWork.user_id
    ).join(
        Lesson,
        Lesson.id == HomeWork.lessons_id
    ).filter(
        and_(
            HomeWork.courses_id == gc.id,
            HomeWork.wait == 1,
        )
    ).all()
    if request.method == 'POST':
        if request.form.get('accept'):
            accept = request.form.get('accept')
            change_homework = g.db.query(HomeWork).filter(HomeWork.id == int(accept)).first()
            change_homework.done = 1
            change_homework.wait = 0
            new_notice = Notice(notice_to_user=User.get_user(change_homework.user_id),
                                text='Вы успено прошли урок %s курса %s' % (
                                Lesson.get_lesson(change_homework.lessons_id).name,
                                Course.get_cours(change_homework.courses_id).name),
                                read=False)
            g.db.add(new_notice)
        if request.form.get('digress'):
            digress = request.form.get('digress')
            change_homework = g.db.query(HomeWork).filter(HomeWork.id == int(digress)).first()
            change_homework.done = 0
            change_homework.wait = 0
            new_notice = Notice(notice_to_user=User.get_user(change_homework.user_id),
                                text='Извините, но вы не прошли урок %s курса %s' % (
                                    Lesson.get_lesson(change_homework.lessons_id).name,
                                    Course.get_cours(change_homework.courses_id).name),
                                read=False)
            g.db.add(new_notice)
        g.db.commit()
        return redirect(url_for('list_homework', course_id=int(course_id)))
    return render_template('list_homework.html',
                           error=error,
                           get_all_homework=get_all_homework)


@school.route('/edit_lesson/<int:course_id>/<int:lesson_id>', methods=['GET', 'POST'])
@login_required
def edit_lesson(course_id=None, lesson_id=None):
    error = None
    gt = Course.get_cours(course_id)
    if gt is None:
        return redirect(url_for('course'))
    gl = Lesson.get_lesson(lesson_id)
    print(gl.homework_type)
    if gl is None:
        return redirect(url_for('cur_course', course_id=int(course_id)))
    if gt.user_id != current_user.id or not current_user.admin:
        return redirect(url_for('cur_course', course_id=int(course_id)))
    if request.method == 'POST':
        if request.form.get('del'):
            gl.ban = True
            g.db.commit()
            number = 1
            get_all_less = g.db.query(Lesson).filter(and_(Lesson.cours_id == gt.id, Lesson.ban == False)).all()
            for gal in get_all_less:
                get_all_less[gal].number = number
                number += 1
            g.db.commit()
            return redirect(url_for('cur_course', course_id=int(course_id)))
        name = request.form.get('name')
        edit_content = request.form.get('edit_content')
        # homework_type = request.form.get('homework_type')
        if name != gl.name and name != '' and name is not None:
            gl.name = name
        if edit_content != gl.content and edit_content != '' and edit_content is not None:
            gl.content = edit_content
        # if homework_type != gl.homework_type and homework_type != '' and homework_type is not None:
        #     gl.homework_type = homework_type
        # print(homework_type)
        if gl.homework_type == 'homework':
            edit_homework = request.form.get('edit_homework')
            if edit_homework != gl.homework and edit_homework != '' and edit_homework is not None:
                gl.homework = edit_homework
        if gl.homework_type == 'test':
            test_in_day = request.form.get('test_in_day')
            if re.search(r'[0-9]{1,3}$', test_in_day) is None:
                error = 'Пожалуйста введите попытки для теста'
                return render_template('edit_lesson.html',
                                       lesson=gl,
                                       name=gl.name or '',
                                       edit_content=gl.content or '',
                                       homework_type=gl.homework_type or '',
                                       edit_homework=gl.homework or '',
                                       error=error)
            persent_for_test = request.form.get('persent_for_test')
            if re.search(r'[0-9]{1,3}$', persent_for_test) is None:
                error = 'Пожалуйста введите процент прохождения теста'
                return render_template('edit_lesson.html',
                                       lesson=gl,
                                       name=gl.name or '',
                                       edit_content=gl.content or '',
                                       homework_type=gl.homework_type or '',
                                       edit_homework=gl.homework or '',
                                       error=error)
            questions_result = []
            quest = request.form.getlist("quest")
            for i in range(len(quest)):
                questions_result.append(dict(quest=quest[i],
                                             answers=request.form.getlist("answer_%s" % i),
                                             right=request.form.get("right_%s" % i)
                                             ))
            gl.test = questions_result
        g.db.commit()
    return render_template('edit_lesson.html',
                           lesson=gl,
                           name=gl.name or '',
                           edit_content=gl.content or '',
                           homework_type=gl.homework_type or '',
                           edit_homework=gl.homework or '',
                           error=error)


@school.route('/list_students/<int:course_id>/<int:lesson_number>', methods=['GET', 'POST'])
@login_required
def list_students_lesson(course_id=None, lesson_number=None):
    course = Course.get_cours(course_id)
    if not current_user.admin and current_user.id != course.user_id:
        return redirect(url_for('cur_course', course_id=int(course_id)))
    get_all_user_in_list = g.db.query(
        List.id,
        List.courses_id,
        List.ban,
        List.user_id,
        User.login,
        User.email
    ).join(
        User,
        User.id == List.user_id
    ).filter(
        and_(
            List.courses_id == course.id,
            List.lessons_number == int(lesson_number),
            List.ban == 0
        )
    ).all()
    get_lesson = g.db.query(Lesson).filter(and_(Lesson.cours_id == course.id,
                                                Lesson.number == int(lesson_number))).first()
    return render_template('list_student_lesson.html',
                           get_all_user_in_list=get_all_user_in_list,
                           get_course=course,
                           get_lesson=get_lesson)
