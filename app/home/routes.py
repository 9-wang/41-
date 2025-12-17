from flask import Blueprint, render_template

bp = Blueprint('home', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/font-demo')
def font_demo():
    return render_template('integrated_font_demo.html')