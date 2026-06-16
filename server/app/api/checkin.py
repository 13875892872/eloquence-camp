"""
打卡模块 — 今日任务 / 完成任务 / 日历 / 成长目标
"""
from flask import Blueprint, request
from ..utils import ok, fail
from datetime import date

bp = Blueprint('checkin', __name__)


@bp.route('/today', methods=['GET'])
def get_today_status():
    """获取今日打卡状态（含3个任务）"""
    # TODO: 从 daily_task_config 读取配置 + 随机抽取训练题
    # TODO: 查询用户今日完成进度
    return ok({
        'date': str(date.today()),
        'is_checked_in': False,
        'tasks': [],
        'all_completed': False,
        'stats': {}
    })


@bp.route('/complete-task', methods=['POST'])
def complete_task():
    """完成单个打卡任务"""
    data = request.get_json()
    # TODO: 校验+标记+检查是否全部完成→触发打卡
    return ok({'task_completed': True, 'all_completed': False})


@bp.route('/calendar', methods=['GET'])
def get_calendar():
    """获取打卡日历"""
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    # TODO: 查询用户当月打卡记录
    return ok({'year': year, 'month': month, 'days': [], 'summary': {}})


@bp.route('/growth-progress', methods=['GET'])
def growth_progress():
    """成长目标进度"""
    # TODO: 从 growth_goal_config 读取 + 用户当前进度
    return ok({'current_level': 'newbie', 'goals': []})
