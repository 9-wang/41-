from flask import Blueprint, render_template
from app import db
from app.user.models import User
from app.community.models import Post, Comment, Story, Task, UserTask
from datetime import datetime, timedelta

bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard/')
def index():
    # 获取总用户数
    total_users = User.query.count()
    
    # 获取30天内活跃用户数
    thirty_days_ago = datetime.now() - timedelta(days=30)
    active_users = User.query.filter(User.created_at >= thirty_days_ago).count()
    
    # 获取社区故事数量
    total_stories = Story.query.count()
    
    # 获取任务相关统计
    total_tasks = Task.query.count()
    total_user_tasks = UserTask.query.count()
    completed_tasks = UserTask.query.filter_by(is_completed=True).count()
    
    # 计算任务完成率
    task_completion_rate = round((completed_tasks / total_user_tasks * 100) if total_user_tasks > 0 else 0, 1)
    
    # 计算情感指数（模拟数据，可根据实际需求调整）
    sentiment_index = round(80 + (total_stories * 0.1) + (completed_tasks * 0.05), 1)
    sentiment_index = min(sentiment_index, 100)  # 上限100
    
    # 计算活跃用户百分比，上限100%
    active_users_percent = min(active_users / total_users * 100, 100) if total_users > 0 else 0
    
    # 计算社区故事分享百分比，上限100%
    total_stories_percent = min(total_stories / 5000 * 100, 100) if total_stories > 0 else 0
    
    # 获取正向内容占比（模拟数据）
    positive_content_ratio = 94
    
    # 获取关键词数据（模拟数据）
    keywords = [
        {"name": "民族团结", "value": 10000},
        {"name": "石榴籽", "value": 6181},
        {"name": "文化交融", "value": 4386},
        {"name": "共同繁荣", "value": 4055},
        {"name": "和谐共处", "value": 2467},
        {"name": "中华文化", "value": 2244},
        {"name": "多元一体", "value": 1898},
        {"name": "民族精神", "value": 1484},
        {"name": "手足情深", "value": 1200},
        {"name": "共同发展", "value": 980}
    ]
    
    return render_template('dashboard/dashboard.html', 
                          total_users=total_users,
                          active_users=active_users,
                          total_stories=total_stories,
                          sentiment_index=sentiment_index,
                          positive_content_ratio=positive_content_ratio,
                          task_completion_rate=task_completion_rate,
                          keywords=keywords,
                          active_users_percent=active_users_percent,
                          total_stories_percent=total_stories_percent)
