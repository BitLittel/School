# -*- coding: utf-8 -*-

import hashlib
from school import school
from flask import render_template, g, request, redirect, url_for, jsonify
from flask_login import current_user, login_required, login_user, LoginManager
from school.database import User, Session, Notice, Blog, Course, MessageUser
from sqlalchemy import and_, or_, desc
from school import user, right, admin, course, balance, subscript, lesson, blog
from school.user import sum_all_notice, wait_mess


login_manager = LoginManager()
login_manager.init_app(school)


@school.before_request
def before_request():
    g.db = Session()


@login_manager.user_loader
def load_user(uid):
    return g.db.query(User).filter_by(id=uid).first()


@login_manager.unauthorized_handler
def unauth():
    return redirect(url_for("login", next=request.path))


@school.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404


@school.errorhandler(500)
def internal_error(error):
    g.db.rollback()
    return render_template('500.html'), 500


@school.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@school.context_processor
def main_context():
    return dict(
        sum_all_notice=sum_all_notice,
        wait_mess=wait_mess
    )


# def new_mess_alarm(item):
#     return dict(
#         count=int(item)
#     )


@school.route('/new_message', methods=['GET', 'POST'])
def new_message_alert():
    check = False
    new_mess = request.args.get('new_mess')
    if new_mess:
        check_new_mess = g.db.query(
            MessageUser
        ).filter(
            and_(MessageUser.user_to == current_user.id,
                 MessageUser.wait == 1,
                 MessageUser.ban == 0,
                 MessageUser.now == 1)
        ).all()
        for cnm in range(len(check_new_mess)):
            if check_new_mess[cnm].now == 1:
                check_new_mess[cnm].now = 0
                check = True
        g.db.commit()
        # new_mess = list(map(new_mess_alarm, wait_mess()))
        return jsonify({'check': check})
    else:
        return False


@school.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html')


@school.route('/notice', methods=['GET', 'POST'])
@login_required
def notice():
    all_notice = g.db.query(
        Notice
    ).filter(
        and_(
            Notice.user_id == current_user.id,
            Notice.ban == False
        )
    ).order_by(
        desc(Notice.data)
    ).all()
    for l in range(len(all_notice)):
        if all_notice[l].read is False:
            all_notice[l].read = True
    g.db.commit()
    return render_template('notice.html',
                           all_notice=all_notice)


