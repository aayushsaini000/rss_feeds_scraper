from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, SearchForm
from app.models import User, RssFeed
from app.utils.rss_scrapper import getRssFeed


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('auth.admin')
        return redirect(next_page)
    print('show form')
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    form = SearchForm(request.form)
    if request.method == 'POST' and form.validate():
        q = request.form.get('q')
        print('search', q)
        res_dict = getRssFeed(q)
        feeds = res_dict['data']
        if feeds:
            # insert feeds to rss_feed table
            db.session.bulk_insert_mappings(RssFeed, feeds)
            db.session.commit()
            return redirect(url_for('main.index'))
        else:
            return render_template('auth/admin.html', form=form, q=q, error=res_dict['message'])
    return render_template('auth/admin.html', form=form)