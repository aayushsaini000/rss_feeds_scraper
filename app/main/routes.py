from flask import render_template, jsonify, request, redirect, url_for
from app.main import bp
from flask_login import login_required
from datetime import datetime
from app.models import RssFeed
from app import db
from app.main.forms import EmptyForm, RSSFeedForm
from app.utils import getRssFeedXML


@bp.route('/', methods=['GET'])
def index():
    """
    Renders index page with rss feed url listing
    """
    rss_feeds = db.session.query(RssFeed).all()
    return render_template('index.html', rss_feeds=rss_feeds)


@bp.route('/rss-url-list', methods=['GET'])
@login_required
def rss_url_list():
    """
    Renders rss urls listing page
    """
    form = EmptyForm(request.form)
    rss_form = RSSFeedForm(request.form)
    return render_template(
        'rss_url_list.html', title='Home', route="rss_url_list", form=form, rss_form=rss_form)


@bp.route('/ajax-rss-list', methods=['GET'])
@login_required
def ajax_rss_list():
    """
    Ajax request to render rss list table
    """
    date_format = '%d.%m.%Y:%H:%M:%S'
    data = [
        [
            r.id, r.feed_url, r.category, datetime.strftime(r.last, date_format), 
            """
                <a href="#" data-url="{}" class="tableActionIcons editRssFeed" title="Edit">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" 
                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" 
                    class="feather feather-edit-2">
                    <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>
                    </svg>
                </a>
                <a href="#" data-url="{}" class="tableActionIcons deleteRssFeed" title="Delete">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" 
                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" 
                    class="feather feather-trash-2">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    <line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line>
                    </svg>
                </a>""".format(
                    # url_for('main.host_detail', pk=h.id),
                    url_for('main.ajax_rss_edit', pk=r.id), 
                    url_for('main.rss_delete', pk=r.id))
        ] for r in db.session.query(RssFeed).all()]
    response = {'data': data}
    return jsonify(response)


@bp.route('/rss-delete/<int:pk>', methods=['POST'])
@login_required
def rss_delete(pk):
    """
    Delete a rss  and redirects to dashboard
    """
    form = EmptyForm(request.form)
    if request.method == 'POST' and form.validate():
        obj = RssFeed.query.get(pk)
        db.session.delete(obj)
        db.session.commit()
        return redirect(url_for('main.rss_url_list'))


@bp.route('/ajax-rss-edit/<int:pk>', methods=['POST'])
@login_required
def ajax_rss_edit(pk):
    """
    Ajax edit rss feed detail
    """
    form = EmptyForm(request.form)
    if request.method == 'POST' and form.validate():
        feed_url = request.form.get('edit_feed_url').strip()
        category = request.form.get('edit_category').strip()
        obj = RssFeed.query.get(pk)
        current_feed_url = obj.feed_url
        if current_feed_url != feed_url and RssFeed.query.filter_by(feed_url=feed_url).first() is None:
            obj.feed_url = feed_url
            obj.category = category
            db.session.commit()
            msg = "RSS feed edited successfully."
            status = "success"
        else:    
            msg = "RSS feed url already exists."
            status = "error"
        return jsonify({'msg': msg, 'status': status})


@bp.route('/ajax-rss-create', methods=['POST'])
@login_required
def ajax_rss_create():
    """
    Ajax request to create a new rss feed
    """
    feed_urls = request.form.get('feed_url')
    feed_url_list = [url.strip() for url in feed_urls.split(',')]
    # fetch all matching url from RssFeed table
    result = db.session.query(RssFeed).filter(RssFeed.feed_url.in_(feed_url_list)).all()
    category = request.form.get('category')
    # if RssFeed.query.filter_by(feed_url=feed_url).first() is not None:
    if result:
        msg = f"RSS feed urls {[rss.feed_url for rss in result]} already exists."
        status = "error"
    else:
        rssfeeds_to_add = [RssFeed(feed_url=url, category=category) for url in feed_url_list]
        db.session.add_all(rssfeeds_to_add)
        # rss_feed = RssFeed(feed_url=feed_url, category=category)
        # db.session.add(rss_feed)
        db.session.commit()
        msg = "RSS feed created successfully."
        status = "success"
    return jsonify({'msg': msg, 'status': status})


@bp.route('/rss-detail/<int:pk>/rss.xml', methods=['GET'])
def rss_detail(pk):
    """
    fetch rss feed data and renders to rss detail page. 
    """
    feeds = []
    form = EmptyForm(request.form)
    url = RssFeed.query.get(pk).feed_url
    data = getRssFeedXML(url)
    for dict_obj in data['entries']:
        d = dict()
        summary = dict_obj['summary']
        d['summary'] = summary[:summary.find('<img')] if '<img' in summary else summary
        d['published']= dict_obj['published']
        d['title'] = dict_obj['title']
        d['link'] = dict_obj['link']
        feeds.append(d)
    return render_template('rss_detail.html', title='RSS Detail', form=form, data=feeds)
