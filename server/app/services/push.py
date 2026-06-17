"""
微信订阅消息推送服务

流程：
1. get_access_token() — 获取/缓存 access_token（2小时有效）
2. send() — 调用 subscribeMessage.send 发送给单个用户
3. send_batch() — 批量发送（逐个调用，记录成功/失败数）
"""
import os
import time
import requests
import logging

logger = logging.getLogger(__name__)

WX_TOKEN_URL = 'https://api.weixin.qq.com/cgi-bin/token'
WX_SEND_URL = 'https://api.weixin.qq.com/cgi-bin/message/subscribe/send'


class PushService:
    """微信订阅消息推送服务"""

    def __init__(self):
        self._access_token = None
        self._token_expires_at = 0

    def get_access_token(self) -> str:
        """获取微信 access_token（缓存2小时）"""
        now = time.time()
        if self._access_token and now < self._token_expires_at - 300:
            return self._access_token

        appid = os.environ.get('WECHAT_APPID', '')
        secret = os.environ.get('WECHAT_SECRET', '')

        if not appid or not secret or appid.startswith('your-'):
            logger.warning('微信 AppID/Secret 未配置，无法获取 access_token')
            return ''

        try:
            resp = requests.get(WX_TOKEN_URL, params={
                'grant_type': 'client_credential',
                'appid': appid,
                'secret': secret
            }, timeout=10)
            data = resp.json()

            if 'access_token' in data:
                self._access_token = data['access_token']
                self._token_expires_at = now + data.get('expires_in', 7200)
                logger.info('微信 access_token 获取成功')
                return self._access_token
            else:
                logger.error(f"获取 access_token 失败: {data}")
                return ''
        except Exception as e:
            logger.error(f'获取 access_token 异常: {e}')
            return ''

    def send(self, user_openid: str, template_id: str, data: dict,
             page: str = '') -> dict:
        """
        发送一条订阅消息

        Returns: {'success': bool, 'error': str}
        """
        access_token = self.get_access_token()
        if not access_token:
            return {'success': False, 'error': 'access_token 获取失败'}

        if not template_id:
            return {'success': False, 'error': 'wx_template_id 未配置'}

        payload = {
            'touser': user_openid,
            'template_id': template_id,
            'page': page,
            'data': data,
            'miniprogram_state': 'formal',
        }

        try:
            resp = requests.post(
                WX_SEND_URL,
                params={'access_token': access_token},
                json=payload,
                timeout=10
            )
            result = resp.json()

            if result.get('errcode') == 0:
                return {'success': True, 'error': ''}
            else:
                errcode = result.get('errcode', -1)
                errmsg = result.get('errmsg', '未知错误')
                return {'success': False, 'error': f'[{errcode}] {errmsg}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def send_batch(self, users: list, template_id: str, data_builder,
                   page: str = '') -> dict:
        """
        批量发送订阅消息

        Args:
            users: User 对象列表
            template_id: 模板 ID
            data_builder: 函数 (user) -> dict
            page: 跳转页面

        Returns: {'total': int, 'success': int, 'failed': int}
        """
        total = len(users)
        success = 0
        failed = 0

        for user in users:
            if not user.openid or not user.subscribe_status:
                failed += 1
                continue

            data = data_builder(user)
            result = self.send(user.openid, template_id, data, page)

            if result['success']:
                success += 1
            else:
                failed += 1
                logger.warning(f'推送失败 user={user.id} error={result["error"]}')

            if success + failed < total:
                time.sleep(0.1)

        return {'total': total, 'success': success, 'failed': failed}

    # ── 业务封装 ──

    def send_daily_remind(self, user, template_id: str = '') -> dict:
        """每日练习提醒"""
        from datetime import date
        data = {
            'thing1': {'value': '每日口才练习'},
            'time2': {'value': f'{date.today()} 20:00'},
            'thing3': {'value': '快来完成今日打卡任务！'},
        }
        return self.send(user.openid, template_id, data,
                        page='pages/checkin/index')

    def send_checkin_success(self, user, template_id: str = '') -> dict:
        """打卡成功通知"""
        data = {
            'thing1': {'value': '今日打卡已完成'},
            'number2': {'value': str(user.continuous_days or 1)},
            'thing3': {'value': '再接再厉，明天继续加油！'},
        }
        return self.send(user.openid, template_id, data,
                        page='pages/home/index')

    def send_new_material(self, user, template_id: str = '', title: str = '') -> dict:
        """新素材上线通知"""
        data = {
            'thing1': {'value': title or '新训练素材已上线'},
            'thing2': {'value': '口才训练营'},
            'thing3': {'value': '点击查看最新训练内容！'},
        }
        return self.send(user.openid, template_id, data,
                        page='pages/training/index')


# 单例
push_service = PushService()
