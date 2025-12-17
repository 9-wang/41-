from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.community.models import Post, Comment, Story, Task, UserTask, TaskSubmission, Like, Tag, DanceCompetition, Dance, DanceSubmission, Share
import datetime
import os
import random
import math

bp = Blueprint('community', __name__)

@bp.route('/community/')
def index():
    # 添加分类筛选
    category = request.args.get('category')
    if category:
        posts = Post.query.filter_by(category=category).all()
    else:
        posts = Post.query.all()
    
    # 获取所有任务
    tasks = Task.query.all()
    
    # 如果用户已登录，获取用户任务进度
    user_tasks = {}
    if current_user.is_authenticated:
        user_task_list = UserTask.query.filter_by(user_id=current_user.id).all()
        user_tasks = {ut.task_id: ut for ut in user_task_list}
    
    # 获取所有分类
    categories = db.session.query(Post.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    return render_template('community/community.html', posts=posts, tasks=tasks, user_tasks=user_tasks, categories=categories)

# 任务相关路由
@bp.route('/community/tasks')
def tasks():
    """所有任务列表"""
    # 获取所有任务
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    # 如果用户已登录，获取用户任务进度
    user_tasks = {}
    if current_user.is_authenticated:
        user_task_list = UserTask.query.filter_by(user_id=current_user.id).all()
        user_tasks = {ut.task_id: ut for ut in user_task_list}
    return render_template('community/tasks.html', tasks=tasks, user_tasks=user_tasks)

@bp.route('/community/task/<int:id>')
def task(id):
    """任务详情页"""
    task = Task.query.get_or_404(id)
    # 获取用户的任务进度
    user_task = None
    if current_user.is_authenticated:
        user_task = UserTask.query.filter_by(user_id=current_user.id, task_id=id).first()
    # 获取任务提交记录
    submissions = TaskSubmission.query.filter_by(task_id=id).order_by(TaskSubmission.created_at.desc()).all()
    return render_template('community/task.html', task=task, user_task=user_task, submissions=submissions)

@bp.route('/community/task/create', methods=['GET', 'POST'])
@login_required
def task_create():
    """创建新任务"""
    from app.community.forms import TaskForm
    
    form = TaskForm()
    if form.validate_on_submit():
        # 处理截止日期
        deadline = None
        if form.deadline.data:
            try:
                deadline = datetime.strptime(form.deadline.data, '%Y-%m-%d')
            except ValueError:
                flash('截止日期格式错误，正确格式为YYYY-MM-DD', 'danger')
                return redirect(url_for('community.task_create'))
        
        # 设置默认图标和颜色
        icon_map = {
            'text': 'mdi:file-text',
            'image': 'mdi:image',
            'video': 'mdi:video',
            'document': 'mdi:file-document'
        }
        
        color_map = {
            'text': '#4285F4',
            'image': '#34A853',
            'video': '#FBBC05',
            'document': '#EA4335'
        }
        
        # 创建新任务
        task = Task(
            title=form.title.data,
            description=form.description.data,
            icon=icon_map.get(form.task_type.data, 'mdi:music'),  # 根据任务类型设置图标
            color=color_map.get(form.task_type.data, '#F39C12'),  # 根据任务类型设置颜色
            task_type=form.task_type.data,
            file_required=form.file_required.data,
            file_types=form.file_types.data,
            file_size_limit=int(form.file_size_limit.data) if form.file_size_limit.data else 10,
            deadline=deadline,
            reward=form.reward.data,
            created_by=current_user.id
        )
        
        db.session.add(task)
        db.session.commit()
        
        flash('任务创建成功！', 'success')
        return redirect(url_for('community.tasks'))
    
    return render_template('community/task_create.html', form=form)

@bp.route('/community/task/<int:id>/submit', methods=['GET', 'POST'])
@login_required
def task_submit(id):
    """上传任务提交"""
    task = Task.query.get_or_404(id)
    from app.community.forms import SubmissionForm
    
    # 获取或创建用户任务
    user_task = UserTask.query.filter_by(user_id=current_user.id, task_id=id).first()
    if not user_task:
        user_task = UserTask(user_id=current_user.id, task_id=id)
        db.session.add(user_task)
        db.session.commit()
    
    # 检查是否已经提交过任务
    if user_task.is_completed:
        flash('您已经提交过该任务！', 'info')
        return redirect(url_for('community.task', id=id))
    
    form = SubmissionForm()
    if form.validate_on_submit():
        # 验证任务是否需要文件且文件是否已提供
        if task.file_required and not form.file.data:
            flash('该任务需要上传文件！', 'danger')
            return redirect(url_for('community.task_submit', id=id))
        
        # 处理文件上传
        file_url = None
        if task.file_required and form.file.data:
            # 确保文件名安全
            original_filename = form.file.data.filename
            if not original_filename:
                flash('请选择有效的文件！', 'danger')
                return redirect(url_for('community.task_submit', id=id))
            
            filename = secure_filename(original_filename)
            if not filename:
                flash('不支持的文件名！', 'danger')
                return redirect(url_for('community.task_submit', id=id))
            
            # 确保文件类型安全
            if task.file_types:
                allowed_types = [ext.strip().lower() for ext in task.file_types.split(',')]
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext and file_ext[1:] not in allowed_types:
                    flash(f'文件类型不允许！允许的类型：{task.file_types}', 'danger')
                    return redirect(url_for('community.task_submit', id=id))
            
            # 确保文件大小安全
            file_size = len(form.file.data.read())
            form.file.data.seek(0)  # 重置文件指针
            max_size = task.file_size_limit * 1024 * 1024  # 转换为字节
            if file_size > max_size:
                flash(f'文件大小超过限制！最大允许 {task.file_size_limit}MB', 'danger')
                return redirect(url_for('community.task_submit', id=id))
            
            # 保存文件
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'tasks')
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, filename)
            form.file.data.save(file_path)
            file_url = url_for('static', filename=f'uploads/tasks/{filename}')
        
        # 创建或更新提交
        submission = TaskSubmission.query.filter_by(user_task_id=user_task.id).first()
        if submission:
            # 更新现有提交
            submission.content = form.content.data
            if file_url:
                submission.file_url = file_url
        else:
            # 创建新提交
            submission = TaskSubmission(
                user_task_id=user_task.id,
                user_id=current_user.id,
                task_id=id,
                content=form.content.data,
                file_url=file_url,
                status='pending'
            )
            db.session.add(submission)
        
        # 更新任务进度和状态
        user_task.progress = 100
        user_task.is_completed = True
        user_task.completed_at = datetime.now()
        user_task.submission_id = submission.id
        db.session.commit()
        
        flash('任务提交成功！', 'success')
        return redirect(url_for('community.task', id=id))
    
    return render_template('community/task_submit.html', task=task, form=form)

@bp.route('/community/task/<int:id>/complete', methods=['POST'])
@login_required
def task_complete(id):
    """标记任务为已完成"""
    user_task = UserTask.query.filter_by(user_id=current_user.id, task_id=id).first()
    if not user_task:
        # 创建新的用户任务记录
        user_task = UserTask(
            user_id=current_user.id,
            task_id=id,
            progress=100,
            is_completed=True,
            completed_at=datetime.now()
        )
        db.session.add(user_task)
    else:
        # 更新现有记录
        user_task.progress = 100
        user_task.is_completed = True
        user_task.completed_at = datetime.now()
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': '任务已完成！'})

@bp.route('/community/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    # 增加浏览数
    post.views += 1
    db.session.commit()
    
    comments = Comment.query.filter_by(post_id=id).order_by(Comment.created_at.asc()).all()
    
    # 检查当前用户是否已点赞
    liked = False
    if current_user.is_authenticated:
        liked = Like.query.filter_by(user_id=current_user.id, post_id=id).first() is not None
    
    return render_template('community/post.html', post=post, comments=comments, liked=liked)

@bp.route('/community/comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    if request.method == 'POST':
        content = request.form['content']
        new_comment = Comment(content=content, user_id=current_user.id, post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('community.post', id=post_id))

# 故事评论功能
@bp.route('/community/story/comment/<int:story_id>', methods=['POST'])
@login_required
def add_story_comment(story_id):
    if request.method == 'POST':
        content = request.form['content']
        new_comment = Comment(content=content, user_id=current_user.id, story_id=story_id)
        story = Story.query.get_or_404(story_id)
        story.comments_count += 1
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('community.story', id=story_id))

# 点赞功能（支持帖子和故事）
@bp.route('/community/like/<string:type>/<int:id>', methods=['POST'])
@login_required
def like_item(type, id):
    if type == 'post':
        item = Post.query.get_or_404(id)
        like = Like.query.filter_by(user_id=current_user.id, post_id=id).first()
    elif type == 'story':
        item = Story.query.get_or_404(id)
        like = Like.query.filter_by(user_id=current_user.id, story_id=id).first()
    else:
        return jsonify({'error': 'Invalid item type'}), 400
    
    if like:
        # 取消点赞
        db.session.delete(like)
        item.likes = max(0, item.likes - 1)
        db.session.commit()
        return jsonify({'likes': item.likes, 'liked': False})
    else:
        # 添加点赞
        if type == 'post':
            new_like = Like(user_id=current_user.id, post_id=id)
        else:
            new_like = Like(user_id=current_user.id, story_id=id)
        db.session.add(new_like)
        item.likes += 1
        db.session.commit()
        return jsonify({'likes': item.likes, 'liked': True})

# 分享功能（模拟分享到社交媒体）
@bp.route('/community/share/<string:type>/<int:id>', methods=['POST'])
def share_item(type, id):
    # 实际应用中可以实现真正的分享功能
    return jsonify({'success': True, 'message': '分享成功！'})

# 故事相关路由
@bp.route('/community/stories')
def stories():
    # 添加排序和筛选
    sort_by = request.args.get('sort', 'latest')
    if sort_by == 'popular':
        stories = Story.query.order_by(Story.likes.desc()).limit(10).all()
    else:
        stories = Story.query.order_by(Story.created_at.desc()).limit(10).all()
    return render_template('community/stories.html', stories=stories)

@bp.route('/community/story/<int:id>')
def story(id):
    story = Story.query.get_or_404(id)
    # 增加浏览数
    story.views += 1
    db.session.commit()
    
    comments = Comment.query.filter_by(story_id=id).order_by(Comment.created_at.asc()).all()
    
    # 检查当前用户是否已点赞
    liked = False
    if current_user.is_authenticated:
        liked = Like.query.filter_by(user_id=current_user.id, story_id=id).first() is not None
    
    return render_template('community/story.html', story=story, comments=comments, liked=liked)

@bp.route('/community/story/create', methods=['GET', 'POST'])
@login_required
def create_story():
    from app.community.forms import StoryForm
    form = StoryForm()
    if form.validate_on_submit():
        # 创建新故事
        new_story = Story(
            title=form.title.data,
            content=form.content.data,
            ethnicity=form.ethnicity.data,
            school=form.school.data,
            user_id=current_user.id
        )
        
        db.session.add(new_story)
        db.session.commit()
        flash('故事分享成功！', 'success')
        return redirect(url_for('community.story', id=new_story.id))
    
    return render_template('community/create_story.html', form=form)

@bp.route('/community/post/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    from app.community.forms import PostForm
    post = Post.query.get_or_404(id)
    # 检查是否是帖子作者
    if post.user_id != current_user.id:
        flash('您没有权限修改此帖子', 'danger')
        return redirect(url_for('community.post', id=id))
    
    form = PostForm(obj=post)
    # 获取所有标签
    all_tags = Tag.query.all()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.category = form.category.data
        
        # 处理标签
        post.tags = []
        if form.tags.data:
            tag_names = [tag.strip() for tag in form.tags.data.split(',')]
            tag_names = [tag for tag in tag_names if tag]
            for tag_name in tag_names:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                post.tags.append(tag)
        
        db.session.commit()
        flash('帖子更新成功！', 'success')
        return redirect(url_for('community.post', id=post.id))
    
    # 初始化表单标签
    form.tags.data = ','.join([tag.name for tag in post.tags])
    
    return render_template('community/edit.html', post=post, form=form, all_tags=all_tags)

@bp.route('/community/post/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    post = Post.query.get_or_404(id)
    # 检查是否是帖子作者
    if post.user_id != current_user.id:
        flash('您没有权限删除此帖子', 'danger')
        return redirect(url_for('community.post', id=id))
    
    db.session.delete(post)
    db.session.commit()
    flash('帖子删除成功！', 'success')
    return redirect(url_for('community.index'))

@bp.route('/community/create', methods=['GET', 'POST'])
@login_required
def create():
    from app.community.forms import PostForm
    form = PostForm()
    # 获取所有标签
    all_tags = Tag.query.all()
    if form.validate_on_submit():
        # 创建新帖子
        post = Post(
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            user_id=current_user.id
        )
        
        # 处理标签
        if form.tags.data:
            tag_names = [tag.strip() for tag in form.tags.data.split(',')]
            tag_names = [tag for tag in tag_names if tag]
            for tag_name in tag_names:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                post.tags.append(tag)
        
        db.session.add(post)
        db.session.commit()
        flash('帖子发布成功！', 'success')
        return redirect(url_for('community.post', id=post.id))
    
    return render_template('community/create.html', form=form, all_tags=all_tags)

# 舞蹈比赛相关路由
@bp.route('/community/dance-competitions')
def dance_competitions():
    """舞蹈比赛列表页"""
    competitions = DanceCompetition.query.all()
    return render_template('community/dance_competitions.html', competitions=competitions)

@bp.route('/community/dance-competition/<int:id>')
def dance_competition(id):
    """舞蹈比赛详情页"""
    competition = DanceCompetition.query.get_or_404(id)
    dances = Dance.query.filter_by(competition_id=id).all()
    return render_template('community/dance_competition.html', competition=competition, dances=dances)

@bp.route('/community/dance')
def dance_list():
    """舞蹈列表页"""
    return render_template('community/dance.html')

# 舞蹈作品提交路由
@bp.route('/community/dance/<int:id>')
def dance(id):
    """舞蹈模板详情页，重定向到舞蹈练习页面"""
    # 重定向到舞蹈练习页面
    return redirect(url_for('community.dance_practice', id=id))

@bp.route('/community/dance-start')
def dance_start():
    """舞蹈功能主页面，直接进入舞蹈选择页面"""
    # 重定向到舞蹈选择页面
    return redirect(url_for('community.dance_selection'))

@bp.route('/community/dance/<int:id>/submit', methods=['GET', 'POST'])
@login_required
def submit_dance(id):
    """上传参赛作品"""
    from app import app
    import os
    import uuid
    from app.community.forms import DanceSubmissionForm
    dance = Dance.query.get_or_404(id)
    
    form = DanceSubmissionForm()
    if form.validate_on_submit():
        # 处理视频文件上传
        video_url = form.video_url.data
        from config import allowed_file
        
        # 检查是否上传了文件
        if form.video.data and form.video.data.filename != '':
            video_file = form.video.data
            
            # 检查文件类型
            if video_file and allowed_file(video_file.filename):
                # 生成唯一文件名
                file_ext = video_file.filename.rsplit('.', 1)[1].lower()
                filename = f"submission_{current_user.id}_{id}_{str(uuid.uuid4())[:8]}.{file_ext}"
                # 保存文件到上传目录
                file_path = os.path.join(app.config['DANCE_VIDEOS_FOLDER'], filename)
                video_file.save(file_path)
                # 生成文件URL
                video_url = filename
        
        # 创建参赛作品
        submission = DanceSubmission(
            user_id=current_user.id,
            dance_id=id,
            video_url=video_url,
            status='pending'
        )
        db.session.add(submission)
        db.session.commit()
        
        # 模拟AI评分（实际应用中应该调用AI评分API）
        # 这里添加一个延时，模拟AI评分过程
        flash('参赛作品提交成功！正在进行AI评分，请稍后查看结果。', 'success')
        return redirect(url_for('community.dance_submission', id=submission.id))
    
    return render_template('community/submit_dance.html', dance=dance, form=form)

@bp.route('/community/dance-submission/<int:id>')
@login_required
def dance_submission(id):
    """参赛作品详情页"""
    submission = DanceSubmission.query.get_or_404(id)
    
    # 检查用户权限
    if submission.user_id != current_user.id:
        flash('您没有权限查看此参赛作品', 'danger')
        return redirect(url_for('community.dance_competitions'))
    
    # 如果作品处于待评分状态，模拟AI评分
    if submission.status == 'pending':
        # 模拟AI评分过程，使用update_score方法更新所有评分字段
        score_result = {
            "overall": round(random.uniform(80, 100), 1),
            "dimensions": {
                "accuracy": round(random.uniform(80, 95), 1),
                "rhythm": round(random.uniform(80, 95), 1),
                "expression": round(random.uniform(80, 95), 1),
                "completeness": round(random.uniform(80, 95), 1)
            },
            "feedback": ["动作整体流畅，但手臂动作可以更舒展", "节奏感良好，建议在跳跃动作时加强爆发力"],
            "suggestions": ["注意膝盖伸直，保持身体挺拔", "加强手臂力量训练，提升动作幅度"]
        }
        
        submission.update_score(score_result)
        db.session.commit()
    
    return render_template('community/dance_submission.html', submission=submission)

@bp.route('/community/dance-result-general')
@login_required
def dance_result_general():
    """舞蹈练习结果页（通用）"""
    # 模拟数据，实际应用中应从数据库获取
    overall_score = 88.5
    accuracy_score = 90.2
    rhythm_score = 85.7
    expression_score = 87.3
    completeness_score = 86.8
    video_url = '/static/videos/dance/tibetan-dance.mp4'
    
    # 模拟反馈建议
    strengths = [
        "动作整体流畅，节奏感良好",
        "表现力丰富，情感投入",
        "动作完成度高，细节处理到位"
    ]
    
    areas_for_improvement = [
        "手臂动作可以更舒展",
        "跳跃动作时需要加强爆发力",
        "身体姿态需要保持挺拔"
    ]
    
    training_suggestions = [
        "加强手臂力量训练，提升动作幅度",
        "尝试增加面部表情，增强表现力",
        "注意动作的连贯性，减少停顿"
    ]
    
    return render_template('community/dance_result.html',
                         overall_score=overall_score,
                         accuracy_score=accuracy_score,
                         rhythm_score=rhythm_score,
                         expression_score=expression_score,
                         completeness_score=completeness_score,
                         video_url=video_url,
                         strengths=strengths,
                         areas_for_improvement=areas_for_improvement,
                         training_suggestions=training_suggestions,
                         dance_id=1)

@bp.route('/community/dance-competition/<int:id>/ranking')
def dance_ranking(id):
    """比赛排行榜"""
    competition = DanceCompetition.query.get_or_404(id)
    
    # 获取所有舞蹈模板
    dances = Dance.query.filter_by(competition_id=id).all()
    
    # 获取每个舞蹈的所有评分作品，并按分数降序排列
    rankings = {}
    for dance in dances:
        # 获取所有已评分的作品，按分数降序排列
        submissions = DanceSubmission.query.filter(
            DanceSubmission.dance_id == dance.id, 
            DanceSubmission.status == 'scored',
            DanceSubmission.score.isnot(None)  # 确保只包含有分数的作品
        ).order_by(DanceSubmission.score.desc()).all()
        rankings[dance.id] = submissions
    
    return render_template('community/dance_ranking.html', competition=competition, dances=dances, rankings=rankings)

@bp.route('/community/dance-selection')
def dance_selection():
    """舞蹈选择页面"""
    # 获取所有舞蹈
    dances = Dance.query.all()
    
    # 提取所有可用的分类
    categories = set()
    for dance in dances:
        categories.add(dance.ethnicity)
    categories = sorted(list(categories))
    
    # 转换舞蹈数据格式，适配模板
    dances_data = []
    for dance in dances:
        # 映射难度级别
        difficulty_map = {
            '初级': 'easy',
            '中级': 'medium',
            '高级': 'hard'
        }
        
        dances_data.append({
        'id': dance.id,
        'title': dance.title,
        'description': dance.description,
        'category': dance.ethnicity,
        'difficulty': difficulty_map.get(dance.difficulty, 'medium'),
        'duration': 120,  # 默认值，模型中没有duration字段
        'thumbnail_url': '/static/images/1e025e36bd5827162b1868f84017bc19.png',
        'video_url': '/static/videos/dance/placeholder.html'  # 使用占位符HTML文件作为视频源
    })
    
    return render_template('community/dance_selection.html', dances=dances_data, categories=categories)

@bp.route('/community/dance-practice/<int:id>')
def dance_practice(id):
    """舞蹈练习页面"""
    dance = Dance.query.get_or_404(id)
    
    # 映射难度级别
    difficulty_map = {
        '初级': 'easy',
        '中级': 'medium',
        '高级': 'hard'
    }
    
    # 转换舞蹈数据格式，适配模板
    dance_data = {
        'id': dance.id,
        'title': dance.title,
        'description': dance.description,
        'category': dance.ethnicity,
        'difficulty': difficulty_map.get(dance.difficulty, 'medium'),
        'duration': 120,  # 默认值，模型中没有duration字段
        'thumbnail_url': '/static/images/1e025e36bd5827162b1868f84017bc19.png',
        'video_url': '/static/videos/dance/placeholder.html'  # 使用占位符HTML文件作为视频源
    }
    
    return render_template('community/dance_practice.html', dance=dance_data, is_camera_active=False, is_practicing=False)

@bp.route('/community/dance-result/<int:id>')
def dance_result(id):
    """舞蹈练习结果页面"""
    dance = Dance.query.get_or_404(id)
    
    # 模拟AI评分数据，实际应用中应从数据库获取
    # 生成更真实的随机评分
    overall_score = round(70 + random.uniform(0, 30), 1)
    accuracy_score = round(70 + random.uniform(0, 25), 1)
    rhythm_score = round(70 + random.uniform(0, 25), 1)
    expression_score = round(70 + random.uniform(0, 25), 1)
    completeness_score = round(70 + random.uniform(0, 25), 1)
    
    # 根据总分确定奖项和奖项描述
    award = ""
    award_description = ""
    
    if overall_score >= 90:
        award = "舞蹈大师"
        award_description = "您的表现非常出色，动作准确到位，节奏把握精准！"
    elif overall_score >= 80:
        award = "舞蹈精英"
        award_description = "您的舞蹈水平已经相当不错，继续练习将会更加出色！"
    elif overall_score >= 70:
        award = "舞蹈新秀"
        award_description = "您已经掌握了基础动作，多加练习会有很大的进步！"
    else:
        award = "舞蹈爱好者"
        award_description = "您刚开始接触舞蹈，坚持练习会有明显的提高！"
    
    # 根据评分生成反馈建议
    strengths = [
        "动作整体流畅，节奏感良好",
        "表现力丰富，情感投入",
        "动作完成度高，细节处理到位"
    ]
    
    areas_for_improvement = [
        "手臂动作可以更舒展",
        "跳跃动作时需要加强爆发力",
        "身体姿态需要保持挺拔"
    ]
    
    training_suggestions = [
        "加强手臂力量训练，提升动作幅度",
        "尝试增加面部表情，增强表现力",
        "注意动作的连贯性，减少停顿"
    ]
    
    return render_template('community/dance_result.html',
                         overall_score=overall_score,
                         accuracy_score=accuracy_score,
                         rhythm_score=rhythm_score,
                         expression_score=expression_score,
                         completeness_score=completeness_score,
                         strengths=strengths,
                         areas_for_improvement=areas_for_improvement,
                         training_suggestions=training_suggestions,
                         dance_id=dance.id,
                         award=award,
                         award_description=award_description)

@bp.route('/api/dance/score', methods=['POST'])
def score_dance():
    """AI评分API（模拟）"""
    data = request.get_json()
    video_url = data.get('video_url')
    dance_id = data.get('dance_id')
    submission_id = data.get('submission_id')  # 新增：参赛作品ID
    
    # 模拟AI动作捕捉和评分
    import time
    
    # 模拟动作捕捉过程
    time.sleep(0.5)  # 模拟动作捕捉延迟
    
    # 从AI模型获取实际数据（这里模拟）
    confidence = data.get('confidence', 0.8)
    
    # 计算评分，使用config.py中的权重配置
    from config import Config
    
    # 生成详细的动作评分
    accuracy = round(80 + confidence * 10, 1)  # 动作准确性
    rhythm = round(85, 1)  # 节奏把握
    expression = round(82, 1)  # 表现力
    completeness = round(88, 1)  # 完整性
    technique = round(75 + confidence * 5, 1)  # 技巧难度
    
    # 计算总分
    total_score = round((accuracy + rhythm + expression + completeness + technique) / 5, 1)
    
    # 多维度评分，支持中文字段名
    score_details = {
        '动作准确性': accuracy,
        '节奏把握': rhythm,
        '表现力': expression,
        '完整性': completeness,
        '技巧难度': technique
    }
    
    # 生成AI反馈和建议
    feedback = [
        "动作整体流畅，但手臂动作可以更舒展",
        "节奏感良好，建议在跳跃动作时加强爆发力",
        "表情生动，继续保持",
        "动作完成度高，细节处理到位"
    ]
    
    suggestions = [
        "注意膝盖伸直，保持身体挺拔",
        "加强手臂力量训练，提升动作幅度",
        "尝试增加面部表情，增强表现力",
        "注意动作的连贯性，减少停顿"
    ]
    
    # 生成动作序列数据（用于小人跟跳）
    # 生成更流畅的动作序列，包含动作过渡和节奏变化
    action_sequence = []
    
    # 定义舞蹈动作序列模板，根据舞蹈类型调整动作分布
    dance_templates = {
        "default": [
            {"action": "step", "duration": 8, "weight": 0.3},
            {"action": "wave", "duration": 4, "weight": 0.2},
            {"action": "dance", "duration": 6, "weight": 0.2},
            {"action": "spin", "duration": 3, "weight": 0.1},
            {"action": "pose", "duration": 2, "weight": 0.1},
            {"action": "jump", "duration": 3, "weight": 0.05},
            {"action": "kick", "duration": 2, "weight": 0.03},
            {"action": "twist", "duration": 3, "weight": 0.02},
            {"action": "hips", "duration": 4, "weight": 0.05},  # 新增扭臀动作
            {"action": "raise", "duration": 3, "weight": 0.05}  # 新增抬手动作
        ]
    }
    
    # 根据舞蹈难度调整动作复杂度
    template = dance_templates["default"]
    
    # 生成200个动作帧，提供更流畅的动画
    current_frame = 0
    while current_frame < 200:
        # 根据权重选择动作
        total_weight = sum(action["weight"] for action in template)
        random_value = random.uniform(0, total_weight)
        selected_action = None
        cumulative_weight = 0
        
        for action in template:
            cumulative_weight += action["weight"]
            if random_value <= cumulative_weight:
                selected_action = action
                break
        
        if selected_action:
            # 生成当前动作的多个帧，确保动作流畅
            for i in range(selected_action["duration"]):
                if current_frame >= 200:
                    break
                    
                # 生成更自然的位置变化，避免突变
                base_x = current_frame * 0.2  # 轻微左右移动
                x = round(base_x % 100 - 50 + random.uniform(-10, 10), 2)
                y = round(random.uniform(-20, 10), 2)  # 垂直位置变化较小
                z = round(random.uniform(0, 5), 2)
                
                # 根据动作类型调整旋转
                if selected_action["action"] == "spin":
                    # 旋转动作时，旋转角度随时间变化
                    rotation_y = round((current_frame * 10) % 360, 2)
                elif selected_action["action"] == "twist":
                    # 扭曲动作时，旋转角度在较小范围内变化
                    rotation_y = round(random.uniform(-30, 30), 2)
                elif selected_action["action"] == "hips":
                    # 扭臀动作时，旋转角度随时间变化
                    rotation_y = round(math.sin(current_frame * 0.5) * 30, 2)
                else:
                    # 其他动作时，旋转角度变化较小
                    rotation_y = round(random.uniform(-15, 15), 2)
                
                action_sequence.append({
                    "frame": current_frame,
                    "action": selected_action["action"],
                    "position": {
                        "x": x,
                        "y": y,
                        "z": z
                    },
                    "rotation": {
                        "x": round(random.uniform(-5, 5), 2),  # 上下旋转较小
                        "y": rotation_y,
                        "z": round(random.uniform(-5, 5), 2)   # 左右旋转较小
                    },
                    "timestamp": current_frame * 0.08  # 调整帧率，使动画更流畅
                })
                current_frame += 1
    
    # 生成AI评分结果
    score_result = {
        "overall": total_score,
        "dimensions": score_details,
        "feedback": feedback,
        "suggestions": suggestions
    }
    
    # 如果提供了submission_id，更新数据库
    if submission_id:
        submission = DanceSubmission.query.get(submission_id)
        if submission:
            submission.update_score(score_result)
            db.session.commit()
    
    return jsonify({
        "score": total_score,
        "score_result": score_result,
        "action_sequence": action_sequence,
        "status": "success",
        "message": "动作捕捉和评分完成"
    })


@bp.route('/api/dance/generate_actions', methods=['POST'])
def generate_actions():
    """AI动作序列生成API"""
    data = request.get_json()
    dance_type = data.get('dance_type', 'default')
    difficulty = data.get('difficulty', 'medium')
    duration = data.get('duration', 120)  # 单位：秒
    
    # 生成个性化动作序列
    action_sequence = []
    
    # 根据难度调整动作复杂度
    difficulty_map = {
        '初级': 'easy',
        '中级': 'medium',
        '高级': 'hard',
        'easy': 'easy',
        'medium': 'medium',
        'hard': 'hard'
    }
    difficulty = difficulty_map.get(difficulty, 'medium')  # 默认使用medium难度

    difficulty_factor = {
        'easy': 0.7,
        'medium': 1.0,
        'hard': 1.3
    }[difficulty]
    
    # 生成动作序列
    frame_count = int(duration * 12.5)  # 12.5fps
    current_frame = 0
    
    # 动作类型权重
    action_weights = {
        'step': 0.3,
        'wave': 0.2,
        'dance': 0.2,
        'spin': 0.1,
        'pose': 0.08,
        'jump': 0.06,
        'kick': 0.03,
        'twist': 0.02
    }
    
    # 生成动作序列
    while current_frame < frame_count:
        # 随机选择动作
        total_weight = sum(action_weights.values())
        random_value = random.uniform(0, total_weight)
        selected_action = None
        cumulative_weight = 0
        
        for action, weight in action_weights.items():
            cumulative_weight += weight
            if random_value <= cumulative_weight:
                selected_action = action
                break
        
        if selected_action:
            # 生成当前动作的帧
            for i in range(3):  # 每个动作持续3帧
                if current_frame >= frame_count:
                    break
                    
                # 生成位置和旋转
                x = round(math.sin(current_frame * 0.1) * 20, 2)
                y = round(math.cos(current_frame * 0.1) * 10, 2)
                z = 0
                
                rotation_y = round(random.uniform(-15, 15), 2)
                
                action_sequence.append({
                    "frame": current_frame,
                    "action": selected_action,
                    "position": {
                        "x": x,
                        "y": y,
                        "z": z
                    },
                    "rotation": {
                        "x": 0,
                        "y": rotation_y,
                        "z": 0
                    },
                    "timestamp": current_frame * 0.08
                })
                current_frame += 1
    
    return jsonify({
        "action_sequence": action_sequence,
        "dance_type": dance_type,
        "difficulty": difficulty,
        "duration": duration,
        "status": "success",
        "message": "动作序列生成完成"
    })


@bp.route('/api/dance/recommend', methods=['GET'])
def recommend_dances():
    """AI舞蹈推荐API"""
    user_id = request.args.get('user_id')
    category = request.args.get('category')
    difficulty = request.args.get('difficulty')
    
    # 模拟推荐逻辑
    recommended_dances = [
        {
            "id": 1,
            "title": "藏族舞蹈",
            "ethnicity": "藏族",
            "difficulty": "初级",
            "score": 92,
            "description": "适合初学者的藏族舞蹈，动作简单易学"
        },
        {
            "id": 2,
            "title": "蒙古族舞蹈",
            "ethnicity": "蒙古族",
            "difficulty": "中级",
            "score": 88,
            "description": "具有浓郁蒙古族特色的舞蹈，注重肩部动作"
        },
        {
            "id": 3,
            "title": "维吾尔族舞蹈",
            "ethnicity": "维吾尔族",
            "difficulty": "高级",
            "score": 85,
            "description": "富有活力的维吾尔族舞蹈，包含旋转和跳跃动作"
        }
    ]
    
    return jsonify({
        "recommended_dances": recommended_dances,
        "status": "success",
        "message": "推荐完成"
    })


@bp.route('/api/dance/analyze_pose', methods=['POST'])
def analyze_pose():
    """AI姿态分析API"""
    data = request.get_json()
    pose_data = data.get('pose_data')  # 前端传来的姿态数据
    
    # 模拟姿态分析
    analysis = {
        "pose": "standing",
        "confidence": round(random.uniform(0.8, 0.98), 3),
        "errors": [
            {
                "body_part": "knee",
                "error_type": "bend",
                "severity": "medium",
                "suggestion": "保持膝盖伸直"
            },
            {
                "body_part": "shoulder",
                "error_type": "asymmetry",
                "severity": "low",
                "suggestion": "保持双肩水平"
            }
        ],
        "correction_guide": [
            "注意身体姿态，保持挺胸抬头",
            "手臂自然放松，不要过于僵硬",
            "脚步平稳，保持重心稳定"
        ]
    }
    
    return jsonify({
        "analysis": analysis,
        "status": "success",
        "message": "姿态分析完成"
    })


@bp.route('/api/dance/feedback', methods=['POST'])
def get_feedback():
    """AI舞蹈反馈API"""
    data = request.get_json()
    user_id = data.get('user_id')
    dance_id = data.get('dance_id')
    performance_data = data.get('performance_data')
    
    # 生成个性化反馈
    feedback = {
        "user_id": user_id,
        "dance_id": dance_id,
        "overall_rating": round(random.uniform(80, 95), 1),
        "strengths": [
            "动作流畅，节奏感强",
            "表现力丰富，情感投入",
            "动作完成度高"
        ],
        "areas_for_improvement": [
            "手臂动作可以更舒展",
            "跳跃动作需要加强力量",
            "旋转动作需要更稳定"
        ],
        "training_suggestions": [
            "加强基础训练，提高身体协调性",
            "多练习旋转和跳跃动作",
            "注意动作细节，提升表现力"
        ]
    }
    
    return jsonify({
        "feedback": feedback,
        "status": "success",
        "message": "反馈生成完成"
    })

@bp.route('/api/dance/share', methods=['POST'])
def record_share():
    """记录分享统计"""
    data = request.get_json()
    submission_id = data.get('submission_id')
    platform = data.get('platform', 'copy')
    
    # 更新分享次数
    submission = DanceSubmission.query.get_or_404(submission_id)
    submission.share_count += 1
    
    # 创建分享记录
    share = Share(
        submission_id=submission_id,
        platform=platform,
        ip_address=request.remote_addr
    )
    
    # 如果用户已登录，记录用户ID
    if current_user.is_authenticated:
        share.user_id = current_user.id
    
    db.session.add(share)
    db.session.commit()
    
    return jsonify({
        "status": "success",
        "message": "分享记录成功",
        "share_count": submission.share_count
    })

@bp.route('/community/search')
def search():
    """全局搜索功能"""
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('community.index'))
    
    # 搜索任务
    tasks = Task.query.filter(
        (Task.title.contains(query)) |
        (Task.description.contains(query))
    ).all()
    
    # 搜索故事
    stories = Story.query.filter(
        (Story.title.contains(query)) |
        (Story.content.contains(query))
    ).all()
    
    # 搜索帖子
    posts = Post.query.filter(
        (Post.title.contains(query)) |
        (Post.content.contains(query))
    ).all()
    
    return render_template('community/search.html',
                          query=query,
                          tasks=tasks,
                          stories=stories,
                          posts=posts)