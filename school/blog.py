# -*- coding: utf-8 -*-

import copy
from flask import g, redirect, render_template, request, url_for, jsonify
from flask_login import login_required, current_user
from sqlalchemy import and_, asc, desc, func
from school import school
from school.database import Course, User, List, Transaction, Direction, Lesson, Setting, Blog
from school.right import check_rights, add_role


@school.route('/', methods=['GET', 'POST'])
@login_required
def all_blog():
    all_bl = g.db.query(
        Blog.id,
        Blog.subject,
        Blog.text,
        Blog.data,
        Blog.course_id,
        Course.id.label('c_id'),
        Course.name
    ).join(
        Course,
        Course.id == Blog.course_id
    ).filter(
        Course.id.in_(current_user.follow)
    ).all()
    return render_template('all_blog.html',
                           all_blog=all_bl)


@school.route('/follow_course/<int:course_id>', methods=['GET', 'POST'])
@login_required
def follow_school(course_id=None):
    if g.db.query(Course).filter(Course.id == int(course_id)).first() is None:
        return render_template('404.html'), 404
    set_f = copy.copy(current_user.follow)
    if set_f.count(int(course_id)) == 0:
        set_f.append(int(course_id))
        current_user.follow = set_f
        g.db.commit()
    else:
        return render_template('404.html'), 404
    return redirect(url_for('cur_course', course_id=course_id))


@school.route('/un_follow_school/<int:course_id>', methods=['GET', 'POST'])
@login_required
def unfollow_school(course_id=None):
    if g.db.query(Course).filter(Course.id == int(course_id)).first() is None:
        return render_template('404.html'), 404
    if course_id in current_user.follow:
        set_f = copy.copy(current_user.follow)
        if set_f.count(int(course_id)) == 1:
            set_f.remove(course_id)
            current_user.follow = set_f
            g.db.commit()
        else:
            error = 'Вы не подписаны!'
            return render_template('404.html'), 404
    return redirect(url_for('cur_course', course_id=course_id))


@school.route('/blog/<int:blog_id>', methods=['GET', 'POST'])
@login_required
def blog(blog_id=None):
    cur_blog = Blog.get_blog(blog_id)
    if cur_blog is None:
        return redirect(404)
    return render_template('blog.html',
                           cur_blog=cur_blog)


@school.route('/edit_blog/<int:blog_id>', methods=['GET', 'POST'])
@login_required
def edit_blog(blog_id=None):
    error = None
    cur_blog = Blog.get_blog(blog_id)
    if cur_blog is None or cur_blog.user_id != current_user.id or not current_user.admin:
        return redirect(404)
    if request.method == 'POST':
        subject = request.form.get('subject')
        text = request.form.get('text')
        if subject is None or subject == '':
            error = 'Не введена тема'
            return render_template('edit_blog.html',
                                   subject=subject or '',
                                   text=text or '',
                                   error=error)
        if text is None or text == '':
            error = 'Не введено содержимое'
            return render_template('edit_blog.html',
                                   subject=subject or '',
                                   text=text or '',
                                   error=error)
        cur_blog.subject = subject
        cur_blog.text = text
        g.db.commit()
        return redirect(url_for('blog', blog_id=cur_blog.id))
    return render_template('edit_blog.html',
                           subject=cur_blog.subject,
                           text=cur_blog.text,
                           error=error)


@school.route('/add_blog/<int:course_id>', methods=['GET', 'POST'])
@login_required
def add_blog(course_id=None):
    error = None
    subject = None
    text = None
    cur_course = Course.get_cours(course_id)
    if cur_course is None or cur_course.user_id != current_user.id or not current_user.admin:
        return redirect(404)
    if request.method == 'POST':
        subject = request.form.get('subject')
        text = request.form.get('text')
        if subject is None or subject == '':
            error = 'Не введена тема'
            return render_template('add_blog.html',
                                   error=error,
                                   subject=subject or '',
                                   text=text or '')
        if text is None or text == '':
            error = 'Не введено содержимое'
            return render_template('add_blog.html',
                                   error=error,
                                   subject=subject or '',
                                   text=text or '')
        new_blog = Blog(subject=subject,
                        text=text,
                        course_id_blog=cur_course,
                        user_id_blog=current_user)
        g.db.add(new_blog)
        g.db.commit()
        return redirect(url_for('blog', blog_id=new_blog.id))
    return render_template('add_blog.html',
                           error=error,
                           subject=subject or '',
                           text=text or '')
