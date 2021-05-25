from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from sqlalchemy.sql.expression import false
from app import db
from app.main.forms import SearchForm
from app.models import User, RssFeed
from app.main import bp
from sqlalchemy import desc


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
# @login_required
def index():
    page = request.args.get('page', 1, type=int)
    
    feeds = RssFeed.query.order_by(desc(RssFeed.datetime)).paginate(page=page, 
    per_page=current_app.config['POSTS_PER_PAGE'])
    return render_template('index.html', title='Home', feeds=feeds)
