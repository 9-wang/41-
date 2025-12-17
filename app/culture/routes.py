from flask import Blueprint, render_template, request, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, SelectMultipleField, StringField, SelectField
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
import os
import random
from datetime import datetime
from app import db
from app.culture.models import EthnicImpression, CultureElement, EthnicGroup, CultureEthnicRelation, CulturalPractice, CulturePattern, PatternRecognitionResult
from app.user.models import User
from app.culture.knowledge_graph import KnowledgeGraphManager
from app.culture.pattern_recognition import PatternRecognitionManager
from app.culture.data_manager import CultureDataManager

bp = Blueprint('culture', __name__)

# 初始化管理器实例
knowledge_graph_manager = KnowledgeGraphManager()
pattern_recognition_manager = PatternRecognitionManager()
culture_data_manager = CultureDataManager()

# 定义图像上传表单
class ImageUploadForm(FlaskForm):
    image = FileField('上传图像', validators=[DataRequired()])
    # 文化关键词
    keyword = StringField('文化关键词', default='茶')
    # 民族选择
    ethnic_group = SelectField('民族选择', default='全部')
    # 文化类型选择
    culture_type = SelectField('文化类型', default='全部')
    # 文化内涵选择
    aspect = SelectField('文化内涵', default='全部')
    # 图谱布局选择
    layout = SelectField('图谱布局', default='force', choices=[
        ('force', '力导向布局'),
        ('circular', '环形布局'),
        ('radial', '辐射状布局'),
        ('tree', '树状布局')
    ])
    # 民族选项
    ethnic_options = [
        ('全部', '全部'),
        ('汉族', '汉族'), ('藏族', '藏族'), ('蒙古族', '蒙古族'),
        ('维吾尔族', '维吾尔族'), ('苗族', '苗族'), ('壮族', '壮族'),
        ('满族', '满族'), ('傣族', '傣族'), ('彝族', '彝族'),
        ('回族', '回族'), ('朝鲜族', '朝鲜族'), ('侗族', '侗族'),
        ('瑶族', '瑶族'), ('白族', '白族'), ('土家族', '土家族')
    ]
    # 文化类型选项
    culture_type_options = [
        ('全部', '全部'),
        ('茶', '茶'), ('丝绸', '丝绸'), ('陶瓷', '陶瓷'),
        ('中医药', '中医药'), ('乐器', '乐器'), ('建筑', '建筑'),
        ('服饰', '服饰'), ('饮食', '饮食'), ('工艺', '工艺')
    ]
    # 文化内涵选项
    aspect_options = [
        ('全部', '全部'),
        ('历史渊源', '历史渊源'), ('传统习俗', '传统习俗'),
        ('文化象征', '文化象征'), ('艺术表现', '艺术表现'),
        ('宗教信仰', '宗教信仰'), ('生活方式', '生活方式')
    ]
    ethnic_elements = SelectMultipleField(
        '选择民族文化元素',
        choices=ethnic_options,
        default=['han'],
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput()
    )
    submit = SubmitField('生成民族融合海报')

# 定义收藏表单
class FavoriteForm(FlaskForm):
    """用于收藏海报的表单"""
    pass  # 收藏表单不需要额外字段，仅用于CSRF保护

@bp.route('/culture/engine', methods=['GET', 'POST'])
def engine():
    form = ImageUploadForm()
    
    # 设置表单选项
    form.ethnic_group.choices = ImageUploadForm.ethnic_options
    form.culture_type.choices = ImageUploadForm.culture_type_options
    form.aspect.choices = ImageUploadForm.aspect_options
    
    if form.validate_on_submit():
        try:
            image = form.image.data
            filename = secure_filename(image.filename)
            upload_dir = os.path.join(current_app.root_path, 'static/uploads/culture')
            os.makedirs(upload_dir, exist_ok=True)
            image_path = os.path.join(upload_dir, filename)
            image.save(image_path)
            
            # 模拟AI生成结果
            generated_posters = []
            
            # 处理选中的民族文化元素
            selected_ethnic_elements = form.ethnic_elements.data
            
            # 创建映射字典将元素值转换为中文名称
            ethnic_options_dict = dict(ImageUploadForm.ethnic_options)
            selected_ethnic_labels = [ethnic_options_dict[element] for element in selected_ethnic_elements]
            ethnic_elements_str = ','.join(selected_ethnic_labels)
            
            for i in range(3):
                # AI生成逻辑：模拟不同风格的融合效果
                variation_styles = [
                    '融合了民族服饰与现代设计的创意海报',
                    '展现民族建筑美学与自然景观的融合',
                    '呈现民族传统工艺与时尚元素的完美结合'
                ]
                
                # 保存生成记录到数据库
                generated_poster = EthnicImpression(
                    user_id=current_user.id if current_user.is_authenticated else None,
                    original_image=f'uploads/culture/{filename}',
                    generated_image=f'uploads/culture/{filename.replace(".", f"_var{i+1}.")}',  # 生成不同版本的图像名称
                    title=f'民族融合海报_{i+1}',
                    description=f'融合了{ethnic_elements_str}文化元素的海报设计_{i+1} - {variation_styles[i]}',
                    ethnic_elements=ethnic_elements_str  # 保存到数据库
                )
                db.session.add(generated_poster)
                generated_posters.append(generated_poster)
            
            # 提交数据库会话
            db.session.commit()
            
            # 创建收藏表单
            favorite_form = FavoriteForm()
            
            # 渲染结果页面
            # 调试：打印路径
            print(f"Original Image Path: uploads/culture/{filename}")
            for idx, poster in enumerate(generated_posters):
                print(f"Generated Image {idx+1} Path: {poster.generated_image}")
            return render_template('culture/engine_result.html', original_image=f'uploads/culture/{filename}', posters=generated_posters, form=favorite_form)
        except Exception as e:
            # 处理所有可能的错误
            error_message = f'生成海报时发生错误: {str(e)}'
            return render_template('culture/engine.html', form=form, error=error_message)
    return render_template('culture/engine.html', form=form)


@bp.route('/culture/favorite/<int:id>', methods=['POST'])
@login_required
def favorite(id):
    """收藏/取消收藏生成的海报"""
    ethnic_impression = EthnicImpression.query.get_or_404(id)
    if current_user in ethnic_impression.favorited_by:
        # 取消收藏
        ethnic_impression.favorited_by.remove(current_user)
    else:
        # 添加收藏
        ethnic_impression.favorited_by.append(current_user)
    db.session.commit()
    return redirect(request.referrer)

@bp.route('/culture/share/<int:id>', methods=['GET'])
def share(id):
    """分享海报页面"""
    ethnic_impression = EthnicImpression.query.get_or_404(id)
    return render_template('culture/share.html', poster=ethnic_impression)

@bp.route('/api/culture/graph', methods=['GET'])
def get_culture_graph():
    """
    获取文化知识图谱数据
    支持按关键词、民族和文化类型筛选
    """
    try:
        # 获取查询参数
        keyword = request.args.get('keyword', '茶')
        ethnic_group = request.args.get('ethnic_group', '全部')
        culture_type = request.args.get('culture_type', '全部')
        aspect = request.args.get('aspect', '全部')
        
        # 使用知识图谱管理器获取数据
        graph_data = knowledge_graph_manager.get_culture_graph_data(keyword, ethnic_group, culture_type, aspect)
        
        return jsonify({
            'success': True,
            'data': graph_data
        })
    except Exception as e:
        print(f'获取图谱数据失败: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'获取图谱数据失败: {str(e)}'
        }), 500

@bp.route('/api/culture/patterns', methods=['GET'])
def get_patterns():
    """
    获取文化图案列表
    支持按类别和地域筛选
    """
    try:
        # 获取查询参数
        category = request.args.get('category')
        region = request.args.get('region')
        
        # 使用纹样识别管理器获取数据
        patterns = pattern_recognition_manager.get_culture_patterns(category, region)
        
        return jsonify({
            'success': True,
            'data': patterns
        })
    except Exception as e:
        print(f'获取文化图案列表失败: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'获取文化图案列表失败: {str(e)}'
        }), 500

@bp.route('/api/culture/recognize-pattern', methods=['POST'])
def recognize_pattern():
    """
    纹样识别API
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        # 验证必要字段
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        # 使用纹样识别管理器处理识别请求
        result = pattern_recognition_manager.recognize_pattern(
            user_id=data.get('user_id'),
            input_image=data.get('input_image'),
            recognized_pattern=data.get('recognized_pattern'),
            recognition_score=data.get('recognition_score', 0.0),
            features=data.get('features'),
            similarity_matrix=data.get('similarity_matrix'),
            pattern_id=data.get('pattern_id')
        )
        
        return jsonify(result)
    except Exception as e:
        print(f'纹样识别失败: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'纹样识别失败: {str(e)}'
        }), 500

@bp.route('/api/culture/recognition-results', methods=['GET'])
def get_recognition_results():
    """
    获取纹样识别结果列表
    """
    try:
        # 获取查询参数
        user_id = request.args.get('user_id', type=int)
        limit = request.args.get('limit', type=int, default=10)
        offset = request.args.get('offset', type=int, default=0)
        
        # 使用纹样识别管理器获取结果
        results = pattern_recognition_manager.get_recognition_results(user_id, limit, offset)
        
        return jsonify(results)
    except Exception as e:
        print(f'获取纹样识别结果列表失败: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'获取纹样识别结果列表失败: {str(e)}'
        }), 500

@bp.route('/api/culture/pattern-similarity', methods=['GET'])
def analyze_pattern_similarity():
    """
    分析图案相似度
    """
    try:
        # 获取查询参数
        pattern_id = request.args.get('pattern_id', type=int)
        other_pattern_ids = request.args.getlist('other_pattern_ids', type=int)
        
        if not pattern_id:
            return jsonify({
                'success': False,
                'message': 'pattern_id参数不能为空'
            }), 400
        
        # 使用纹样识别管理器分析相似度
        result = pattern_recognition_manager.analyze_pattern_similarity(pattern_id, other_pattern_ids)
        
        return jsonify(result)
    except Exception as e:
        print(f'分析图案相似度失败: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'分析图案相似度失败: {str(e)}'
        }), 500

@bp.route('/api/culture/combined-data', methods=['GET'])
def get_combined_culture_data():
    """
    获取整合的文化数据，包括知识图谱和纹样数据
    """
    try:
        # 获取查询参数
        keyword = request.args.get('keyword', '')
        category = request.args.get('category')
        region = request.args.get('region')
        
        # 使用数据管理器获取整合数据
        data = culture_data_manager.get_combined_culture_data(keyword, category, region)
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        print(f'获取整合文化数据失败: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'获取整合文化数据失败: {str(e)}'
        }), 500

@bp.route('/api/culture/stats', methods=['GET'])
def get_culture_stats():
    """
    获取文化数据统计信息
    """
    try:
        # 使用数据管理器获取统计信息
        stats = culture_data_manager.get_statistics()
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        print(f'获取文化数据统计信息失败: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'获取文化数据统计信息失败: {str(e)}'
        }), 500

@bp.route('/api/culture/sync-data', methods=['POST'])
def sync_data():
    """
    同步文化数据
    """
    try:
        # 使用数据管理器同步数据
        result = culture_data_manager.sync_data()
        
        return jsonify(result)
    except Exception as e:
        print(f'数据同步失败: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'数据同步失败: {str(e)}'
        }), 500

@bp.route('/api/culture/elements', methods=['GET'])
def get_culture_elements():
    """
    获取所有文化元素列表
    """
    try:
        elements = CultureElement.query.all()
        element_list = [{'name': element.name, 'description': element.description} for element in elements]
        
        return jsonify({
            'success': True,
            'data': element_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取文化元素列表失败: {str(e)}'
        }), 500

@bp.route('/api/culture/ethnic-groups', methods=['GET'])
def get_ethnic_groups():
    """
    获取所有民族列表
    """
    try:
        groups = EthnicGroup.query.all()
        group_list = [{'name': group.name, 'description': group.description} for group in groups]
        
        return jsonify({
            'success': True,
            'data': group_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取民族列表失败: {str(e)}'
        }), 500