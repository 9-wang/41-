from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, BooleanField, FileField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from datetime import datetime

# 登录表单
class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

# 注册表单
class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    password2 = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    ethnicity = SelectField('民族', choices=[
        ('藏族', '藏族'),
        ('蒙古族', '蒙古族'),
        ('维吾尔族', '维吾尔族'),
        ('汉族', '汉族'),
        ('其他', '其他')
    ], validators=[DataRequired()])
    school = StringField('学校', validators=[DataRequired()])
    submit = SubmitField('注册')

# 个人资料表单
class ProfileForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    ethnicity = SelectField('民族', choices=[
        ('藏族', '藏族'),
        ('蒙古族', '蒙古族'),
        ('维吾尔族', '维吾尔族'),
        ('汉族', '汉族'),
        ('其他', '其他')
    ])
    school = StringField('学校')
    bio = TextAreaField('简介')
    submit = SubmitField('更新')

# 任务表单
class TaskForm(FlaskForm):
    title = StringField('任务标题', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('任务描述', validators=[DataRequired()])
    task_type = SelectField('任务类型', choices=[
        ('text', '文字任务'),
        ('image', '图片任务'),
        ('video', '视频任务'),
        ('document', '文档任务')
    ], validators=[DataRequired()])
    deadline = StringField('截止日期', validators=[Optional()])
    file_required = BooleanField('需要上传文件')
    file_types = StringField('允许类型', validators=[Optional()])
    file_size_limit = StringField('文件大小限制(MB)', validators=[Optional()])
    reward = StringField('任务奖励', validators=[Optional()])
    submit = SubmitField('发布任务')

# 任务提交表单
class SubmissionForm(FlaskForm):
    content = TextAreaField('提交内容', validators=[Optional()])
    file = FileField('上传文件', validators=[Optional()])
    submit = SubmitField('提交任务')

# 舞蹈提交表单
class DanceSubmissionForm(FlaskForm):
    video = FileField('上传舞蹈视频', validators=[Optional()])
    video_url = StringField('视频URL', validators=[Optional()])
    submit = SubmitField('提交参赛作品')
    
    def validate(self):
        if not super(DanceSubmissionForm, self).validate():
            return False
        
        # 至少需要提供视频文件或视频URL
        if not self.video.data and not self.video_url.data:
            self.video.errors.append('请上传视频文件或输入视频URL')
            return False
        return True

# 故事表单
class StoryForm(FlaskForm):
    title = StringField('故事标题', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('故事内容', validators=[DataRequired()])
    ethnicity = SelectField('民族', choices=[
        ('藏族', '藏族'),
        ('蒙古族', '蒙古族'),
        ('维吾尔族', '维吾尔族'),
        ('汉族', '汉族'),
        ('其他', '其他')
    ], validators=[DataRequired()])
    school = StringField('学校', validators=[DataRequired()])
    submit = SubmitField('分享故事')

# 帖子表单
class PostForm(FlaskForm):
    title = StringField('帖子标题', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('帖子内容', validators=[DataRequired()])
    category = SelectField('分类', choices=[
        ('文化交流', '文化交流'),
        ('学习分享', '学习分享'),
        ('生活感悟', '生活感悟'),
        ('活动通知', '活动通知'),
        ('问题讨论', '问题讨论')
    ], validators=[DataRequired()])
    tags = StringField('标签（用逗号分隔）', validators=[Optional()])
    submit = SubmitField('发布帖子')
