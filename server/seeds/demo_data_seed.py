"""
演示数据初始化 — 训练题库 + 推荐配置 + 打卡/练习记录 + 收藏
运行: PYTHONIOENCODING=utf-8 PYTHONPATH=. python seeds/demo_data_seed.py
"""
import random
from datetime import date, datetime, timedelta
from app import create_app
from app.extensions import db
from app.models.training import TrainingItem
from app.models.common import PracticeRecord, UserFavorite, RecommendConfig
from app.models.checkin import CheckinRecord
from app.models.user import User, UserQuota

app = create_app()

# ── 训练题库（24题，4个分类 x 6题） ──
TRAINING_ITEMS = [
    # ===== 基础口才 (basic) =====
    {'category': 'basic', 'sub_category': '朗读', 'title': '晨间新闻跟读',
     'difficulty': 1, 'sort_order': 1, 'tags': ['朗读', '新闻', '入门'],
     'sample_text': '各位听众早上好，今天是2026年6月17日星期一。首先关注国内新闻：我国科技创新再创佳绩，人工智能技术在医疗、教育等领域取得突破性进展。专家表示，未来五年将是AI赋能产业升级的关键时期。'},
    {'category': 'basic', 'sub_category': '朗读', 'title': '经典散文诵读',
     'difficulty': 1, 'sort_order': 2, 'tags': ['朗读', '散文', '文学'],
     'sample_text': '盼望着，盼望着，东风来了，春天的脚步近了。一切都像刚睡醒的样子，欣欣然张开了眼。山朗润起来了，水涨起来了，太阳的脸红起来了。小草偷偷地从土里钻出来，嫩嫩的，绿绿的。'},
    {'category': 'basic', 'sub_category': '发音', 'title': '绕口令基础训练',
     'difficulty': 1, 'sort_order': 3, 'tags': ['绕口令', '发音', '基础'],
     'sample_text': '八百标兵奔北坡，炮兵并排北边跑。炮兵怕把标兵碰，标兵怕碰炮兵炮。吃葡萄不吐葡萄皮，不吃葡萄倒吐葡萄皮。四是四，十是十，十四是十四，四十是四十。'},
    {'category': 'basic', 'sub_category': '表达', 'title': '三分钟自我介绍',
     'difficulty': 1, 'sort_order': 4, 'tags': ['自我介绍', '职场', '基础'],
     'sample_text': '大家好！很高兴有机会在这里介绍自己。我从事互联网行业五年，专注于产品设计方向。平时喜欢阅读和运动，也热衷于学习新技能。今天想和大家分享的是如何在职场中做好有效沟通，希望能对大家有所帮助。'},
    {'category': 'basic', 'sub_category': '表达', 'title': '看图说话练习',
     'difficulty': 2, 'sort_order': 5, 'tags': ['描述', '观察力', '入门'],
     'sample_text': '请描述你记忆中印象最深的一个画面：那是一个秋天的黄昏，金色的阳光洒在老槐树的叶子上，微风拂过，树叶沙沙作响。远处传来孩子们嬉笑的声音，空气中弥漫着桂花的香气。这一幕让我想起了童年的美好时光。'},
    {'category': 'basic', 'sub_category': '逻辑', 'title': '观点表达基本功',
     'difficulty': 2, 'sort_order': 6, 'tags': ['逻辑', '观点', '表达'],
     'sample_text': '选择一个你感兴趣的话题，试着用"观点-理由-举例-总结"的结构来表达。例如：我认为阅读对于个人成长至关重要。首先，阅读可以拓宽视野，让我们接触不同的思想和文化；其次，阅读能提升思维深度，培养独立思考的能力。比如我自己，每天坚持阅读30分钟后，发现在工作中能够更清晰地表达自己的想法。所以建议大家每天抽出时间阅读。'},

    # ===== 演讲实战 (speech) =====
    {'category': 'speech', 'sub_category': '职场', 'title': '项目汇报演讲',
     'difficulty': 3, 'sort_order': 1, 'tags': ['职场', '汇报', '演讲'],
     'sample_text': '各位领导、各位同事，今天我要向大家汇报Q2季度项目的进展。本季度我们完成了三个核心模块的上线，用户满意度提升了15%。取得这些成绩得益于团队的通力合作和敏捷开发流程的优化。当然我们也遇到了一些挑战，比如跨部门协作的效率问题，我们正在通过建立更完善的沟通机制来解决。下个季度我们的重点将是性能优化和用户体验提升。'},
    {'category': 'speech', 'sub_category': '职场', 'title': '竞聘岗位演讲',
     'difficulty': 4, 'sort_order': 2, 'tags': ['竞聘', '职场', '进阶'],
     'sample_text': '尊敬的各位评委，我今天竞聘的是产品总监岗位。在过去的三年中，我主导了五款核心产品的从零到一，积累了丰富的产品规划、团队管理和市场洞察经验。我的优势在于：第一，对用户需求有敏锐的洞察力；第二，擅长跨部门资源整合；第三，具备数据驱动的决策能力。如果能担任这一职务，我将从产品创新和团队建设两个方面重点发力。'},
    {'category': 'speech', 'sub_category': '社交', 'title': '婚礼致辞',
     'difficulty': 2, 'sort_order': 3, 'tags': ['婚礼', '社交', '情感'],
     'sample_text': '各位亲朋好友，今天是一个特别的日子。作为新郎的好友，我见证了他们从相识、相知到相爱的全过程。爱情最美的样子，不是轰轰烈烈，而是在平凡的日子里相互扶持、共同成长。看到你们站在这里，我由衷地为你们感到高兴。愿你们的婚姻如同今天的美酒，越陈越香；愿你们的生活如同今天的阳光，永远明媚灿烂。'},
    {'category': 'speech', 'sub_category': '社交', 'title': '年会脱口秀',
     'difficulty': 3, 'sort_order': 4, 'tags': ['年会', '幽默', '社交'],
     'sample_text': '各位同事大家晚上好！又到了一年一度的年会，看到大家都穿得这么正式，我突然有点不习惯——毕竟平时大家都是T恤牛仔裤的。特别感谢HR部门精心组织了这场晚会，也感谢领导给了我们这么一个放松的机会。在过去的这一年里，我们经历了很多：加班、改需求、再加班、再改需求…但好在我们的产品越做越好，团队也越来越强。新的一年，希望我们继续并肩作战，也祝大家身体健康、升职加薪！'},
    {'category': 'speech', 'sub_category': '比赛', 'title': '即兴演讲挑战',
     'difficulty': 4, 'sort_order': 5, 'tags': ['演讲比赛', '即兴', '挑战'],
     'sample_text': '主题：改变。改变是人生中唯一不变的事情。记得乔布斯在斯坦福演讲中说过："你不能预先把点点滴滴串联起来，只有在回顾时才能看清来龙去脉。"每一次改变都像是一扇门，打开它，你不知道门后面是什么，但正是这种未知，让生命充满了可能性。所以不要害怕改变，拥抱它，因为改变意味着成长的机会。'},
    {'category': 'speech', 'sub_category': '教育', 'title': 'TED风格分享',
     'difficulty': 5, 'sort_order': 6, 'tags': ['TED', '分享', '高阶'],
     'sample_text': '今天我想和大家探讨一个话题：语言的力量。你知道吗？一个人平均每天要说大约一万六千个字。这些词汇不仅仅是在传递信息，它们还在塑造我们的思维、影响他人的情绪、改变我们所处的环境。心理学研究表明，正向的语言暗示可以改变一个人的行为模式。所以从今天开始，让我们重新审视自己说的每一句话，用语言去创造而非破坏，去鼓励而非打击，去连接而非隔离。'},

    # ===== 直播话术 (live) =====
    {'category': 'live', 'sub_category': '带货', 'title': '产品卖点介绍',
     'difficulty': 2, 'sort_order': 1, 'tags': ['带货', '销售', '产品'],
     'sample_text': '家人们，今天给大家带来一款真正好用的蓝牙耳机。第一，它采用了最新的降噪技术，在地铁上也能清晰通话；第二，续航长达36小时，出差一周不用充电；第三，佩戴舒适度极高，入耳设计符合人体工学，戴一天耳朵也不疼。这款耳机原价399，今天直播间只要199，而且还送价值99的保护套。数量有限，需要的家人们抓紧下单！'},
    {'category': 'live', 'sub_category': '带货', 'title': '限时秒杀话术',
     'difficulty': 3, 'sort_order': 2, 'tags': ['秒杀', '节奏', '促销'],
     'sample_text': '倒计时开始！321，上链接！家人们这款面膜今天破价了，平时109一盒，今天三盒只要159！三盒只要159！库存只有200组，卖完真的补不了货。我跟品牌方磨了整整一个星期才拿下这个价格，错过今天就没有了。已经拍了350单了，还有最后50组！手慢无，手慢无！'},
    {'category': 'live', 'sub_category': '互动', 'title': '粉丝互动控场',
     'difficulty': 2, 'sort_order': 3, 'tags': ['互动', '控场', '气氛'],
     'sample_text': '欢迎新进来的宝宝们！没点关注的左上角点个关注，加个粉丝团不迷路。今天直播间人气不错啊，已经有2000人在线了。大家飘个弹幕告诉我你们是从哪里刷到我的，我看看有多少是老粉。飘"1"让我看到你们！好，看到好多熟悉的面孔了。今天我们还准备了福袋，关注+点赞+评论就能参与抽奖。'},
    {'category': 'live', 'sub_category': '知识', 'title': '知识付费讲解',
     'difficulty': 3, 'sort_order': 4, 'tags': ['知识', '教育', '课程'],
     'sample_text': '大家好，欢迎来到今天的直播课。今天我们要讲的主题是"高效学习法"。很多同学问我说老师，为什么我每天学习那么久，效果却不理想？其实问题的关键不在于时间长短，而在于学习方法。今天我会分享三个核心方法：番茄工作法、费曼学习法和间隔重复法。学会这三个方法，你的学习效率至少提升三倍。'},
    {'category': 'live', 'sub_category': '娱乐', 'title': '才艺展示串词',
     'difficulty': 2, 'sort_order': 5, 'tags': ['才艺', '娱乐', '暖场'],
     'sample_text': '来了来了，家人们期待已久的才艺环节到了！我先声明一下，我唱歌的水平嘛，属于那种"勇气可嘉、水平一般"的类型。但是答应了大家的事情一定做到。今天给大家唱一首《起风了》，希望你们喜欢。如果唱得不好，大家轻点喷哈～来，音乐老师请就位，321，走！'},
    {'category': 'live', 'sub_category': '危机', 'title': '直播应急回应',
     'difficulty': 4, 'sort_order': 6, 'tags': ['危机', '应对', '灵活'],
     'sample_text': '我看到有朋友在弹幕里提到了昨天的一个负面评论。首先要感谢这位朋友关注我们，也给了我一个说明的机会。关于产品规格的问题，确实是我们展示时没有标注清楚，这点我们团队已经意识到并正在改进。我们已经在商品详情页更新了所有规格信息。如果已经下单的朋友对规格有疑问，可以联系客服，七天无理由退换。做直播我们一直在学习，感谢大家的包容和监督。'},

    # ===== 即兴表达 (improv) =====
    {'category': 'improv', 'sub_category': '观点', 'title': '一分钟即兴观点',
     'difficulty': 2, 'sort_order': 1, 'tags': ['观点', '短时', '即兴'],
     'sample_text': '话题：远程办公的利与弊。远程办公最大的优点是灵活，节省了通勤时间，让人能更好地平衡工作与生活。但它也有挑战：团队沟通成本增加，自驱力弱的人容易效率低下。我认为未来的趋势是混合办公——结合两者的优势，既能享受自由的便利，又能保持团队的凝聚力。关键不在于在哪办公，而在于如何高效协作。'},
    {'category': 'improv', 'sub_category': '观点', 'title': '热点话题评述',
     'difficulty': 3, 'sort_order': 2, 'tags': ['热点', '评论', '思辨'],
     'sample_text': '最近关于AI是否会取代人类工作的讨论非常热烈。我的看法是：AI不会取代人，但会使用AI的人可能取代不会使用AI的人。历史上每一次技术革命都会带来就业结构的调整，但同时也会创造新的岗位。与其担忧被取代，不如主动学习和适应。真正的竞争力不在于你知道多少知识，而在于你如何利用工具来创造价值。'},
    {'category': 'improv', 'sub_category': '故事', 'title': '关键词编故事',
     'difficulty': 3, 'sort_order': 3, 'tags': ['故事', '创意', '想象力'],
     'sample_text': '请用以下三个关键词编一个故事：手机、雨伞、陌生人。那是一个下着暴雨的傍晚，我撑着雨伞匆忙地走在回家的路上。突然手机响了，是一个陌生号码。我犹豫了一下还是接了，电话那头传来一个焦急的声音，原来是一位老人打错了电话，但他听出了我声音里的关切，开始向我倾诉他的孤独。我们在电话里聊了半小时，挂断后我站在雨中，忽然觉得这场雨也没那么冷了。'},
    {'category': 'improv', 'sub_category': '辩论', 'title': '三分钟微辩论',
     'difficulty': 4, 'sort_order': 4, 'tags': ['辩论', '逻辑', '进阶'],
     'sample_text': '辩题：朋友圈应该三天可见还是一直可见？我支持三天可见。首先，隐私保护是现代人的刚需。过去的动态可能反映了当时的情绪和认知，不代表现在的状态。第二，三天可见鼓励当下的真实分享而非"人设管理"，避免了社交压力。第三，从数据安全角度，所有历史动态都可能被截图、滥用。当然，理解那些希望一直可见的朋友，关键是每个人有选择的权利。'},
    {'category': 'improv', 'sub_category': '沟通', 'title': '高难度沟通模拟',
     'difficulty': 5, 'sort_order': 5, 'tags': ['沟通', '情商', '高阶'],
     'sample_text': '场景：你需要向老板提出加薪申请。这是一个让很多人紧张的对话。我建议这样开口："王总，感谢您给我几分钟时间。我想跟您聊聊我过去一年在公司的工作表现。这一年我主导完成了三个重要项目，每个都超出了预期目标。基于这些成绩和对公司持续的贡献，我希望能够申请薪资调整。我调研了行业水平，整理了一份数据，不知道您方便看看吗？"记住：用事实说话，体现价值，表明诉求，保持尊重。'},
    {'category': 'improv', 'sub_category': '情感', 'title': '真诚感谢表达',
     'difficulty': 2, 'sort_order': 6, 'tags': ['感谢', '情感', '温暖'],
     'sample_text': '今天我想认真地说一声感谢。感谢父母，你们的支持是我前行的底气；感谢身边的朋友，在我低谷时给我力量；感谢工作中遇到的每一位同事和导师，是你们让我不断成长。很多时候我们把感谢放在心上，却忘了开口说出来。所以今天，试着给你想感谢的人发一条消息吧，哪怕只是一句"谢谢你"。表达的温暖，永远不嫌晚。'},
]

# ── 推荐配置 ──
RECOMMEND_SLOTS = [
    {'slot': 1, 'custom_title': '晨间跟读 — 唤醒你的声音', 'refresh_mode': 'daily'},
    {'slot': 2, 'custom_title': '今日挑战 — 即兴表达训练', 'refresh_mode': 'daily'},
    {'slot': 3, 'custom_title': '热门推荐 — 直播话术', 'refresh_mode': 'manual'},
]

# ── 演示用户的打卡记录（过去14天） ──
def generate_checkin_records(users):
    """为每个用户生成过去14天中随机几天的打卡记录"""
    records = []
    for user in users:
        num_days = random.randint(3, 14)
        days = sorted(random.sample(range(14), num_days))
        for d_offset in days:
            task_date = date.today() - timedelta(days=d_offset)
            # 随机完成1-3个任务
            num_completed = random.randint(1, 3)
            completed_tasks = sorted(random.sample([1, 2, 3], num_completed))
            records.append(CheckinRecord(
                user_id=user.id,
                task_date=task_date,
                status='completed',
                completed_tasks=completed_tasks
            ))
    return records

# ── 演示用户的练习记录 ──
def generate_practice_records(users, training_items):
    """为每个用户生成一些录音练习记录"""
    records = []
    comments = [
        '发音标准，语速适中，整体表达流畅！',
        '语调有起伏，感情充沛，继续保持！',
        '部分字词发音不够清晰，建议多做绕口令练习。',
        '语速偏快，注意适当停顿，让听众更好理解。',
        '节奏感很好，重点突出，表达很有感染力！',
        '声音洪亮有自信，内容的逻辑结构也很清晰。',
        '需要加强结尾部分的表达力度，可以更有感染力。',
    ]
    for user in users:
        num_records = random.randint(2, 6)
        selected_items = random.sample(training_items, min(num_records, len(training_items)))
        for i, item in enumerate(selected_items):
            days_ago = random.randint(0, 13)
            score = random.randint(65, 95)
            dims = {
                'pronunciation': random.randint(60, 98),
                'fluency': random.randint(60, 98),
                'completeness': random.randint(60, 98),
                'content': random.randint(60, 98),
                'expressiveness': random.randint(60, 98),
            }
            records.append(PracticeRecord(
                user_id=user.id,
                training_item_id=item.id,
                audio_url=f'/static/demo/audio_{user.id}_{item.id}.mp3',
                duration=random.randint(30, 180),
                ai_score=score,
                dimension_scores=dims,
                ai_feedback=random.choice(comments),
                source=random.choice(['training', 'free_practice', 'checkin']),
                created_at=datetime.utcnow() - timedelta(days=days_ago)
            ))
    return records

# ── 演示用户的收藏记录 ──
def generate_favorites(users, training_items):
    """为每个用户随机收藏一些训练题"""
    favorites = []
    for user in users:
        num_favs = random.randint(1, 5)
        selected_items = random.sample(training_items, num_favs)
        for item in selected_items:
            favorites.append(UserFavorite(
                user_id=user.id,
                item_type='training_item',
                item_id=item.id
            ))
    return favorites

# ── 更新用户统计 ──
def update_user_stats(users, checkin_records, practice_records):
    """根据打卡和练习记录更新用户统计数据"""
    for user in users:
        # 总打卡天数
        user_days = [r for r in checkin_records if r.user_id == user.id]
        user.total_days = len(set(str(r.task_date) for r in user_days))

        # 连续打卡天数（从今天往前算）
        today = date.today()
        continuous = 0
        for i in range(14):
            d = today - timedelta(days=i)
            if any(r.task_date == d and r.user_id == user.id for r in checkin_records):
                continuous += 1
            else:
                break
        user.continuous_days = continuous

        # 总练习分钟数
        user_practices = [r for r in practice_records if r.user_id == user.id]
        user.total_practice_minutes = sum(r.duration for r in user_practices) // 60

        # 根据总天数更新等级
        if user.total_days >= 100:
            user.growth_level = 'master'
        elif user.total_days >= 60:
            user.growth_level = 'expert'
        elif user.total_days >= 30:
            user.growth_level = 'advanced'
        elif user.total_days >= 7:
            user.growth_level = 'beginner'
        else:
            user.growth_level = 'newbie'

        # 能力评分
        user_p = [r for r in practice_records if r.user_id == user.id]
        if user_p:
            avg_scores = {}
            for dim in ['pronunciation', 'fluency', 'completeness', 'content', 'expressiveness']:
                scores = [r.dimension_scores.get(dim, 0) for r in user_p if r.dimension_scores]
                avg_scores[dim] = round(sum(scores) / len(scores)) if scores else 0
            user.ability_score = avg_scores


# ── 主函数 ──
def main():
    with app.app_context():
        db.create_all()

        # 1. 训练题库
        existing_count = TrainingItem.query.count()
        if existing_count == 0:
            for item in TRAINING_ITEMS:
                db.session.add(TrainingItem(**item))
            db.session.commit()
            print(f'✅ 训练题库已初始化（{len(TRAINING_ITEMS)}题）')
        else:
            print(f'ℹ️  训练题库已有 {existing_count} 题，跳过')

        # 2. 推荐配置
        if RecommendConfig.query.count() == 0:
            all_items = TrainingItem.query.all()
            for slot_conf in RECOMMEND_SLOTS:
                candidates = [it for it in all_items
                             if slot_conf['slot'] == 1 and it.category == 'basic'
                             or slot_conf['slot'] == 2 and it.category == 'improv'
                             or slot_conf['slot'] == 3 and it.category == 'live']
                item = candidates[slot_conf['slot'] - 1] if candidates else all_items[slot_conf['slot']]
                db.session.add(RecommendConfig(
                    slot=slot_conf['slot'],
                    training_item_id=item.id,
                    custom_title=slot_conf['custom_title'],
                    refresh_mode=slot_conf['refresh_mode']
                ))
            db.session.commit()
            print(f'✅ 推荐配置已初始化（{len(RECOMMEND_SLOTS)}个位）')
        else:
            print(f'ℹ️  推荐配置已存在，跳过')

        # 3. 演示数据（仅当无打卡/练习记录时生成）
        users = User.query.all()
        training_items = TrainingItem.query.all()

        if CheckinRecord.query.count() == 0 and users:
            checkin_records = generate_checkin_records(users)
            for r in checkin_records:
                db.session.add(r)
            db.session.commit()
            print(f'✅ 演示打卡记录已生成（{len(checkin_records)}条）')
        else:
            checkin_records = CheckinRecord.query.all()
            print(f'ℹ️  打卡记录已存在，跳过')
            # 重新查询以便后续使用
            checkin_records = CheckinRecord.query.all()

        if PracticeRecord.query.count() == 0 and users and training_items:
            practice_records = generate_practice_records(users, training_items)
            for r in practice_records:
                db.session.add(r)
            db.session.commit()
            print(f'✅ 演示练习记录已生成（{len(practice_records)}条）')
        else:
            practice_records = PracticeRecord.query.all()
            print(f'ℹ️  练习记录已存在，跳过')
            practice_records = PracticeRecord.query.all()

        if UserFavorite.query.count() == 0 and users and training_items:
            favorites = generate_favorites(users, training_items)
            for f in favorites:
                db.session.add(f)
            db.session.commit()
            print(f'✅ 演示收藏已生成（{len(favorites)}条）')
        else:
            print(f'ℹ️  收藏已存在，跳过')

        # 4. 更新用户统计数据
        if users:
            checkin_records = CheckinRecord.query.all()
            practice_records = PracticeRecord.query.all()
            update_user_stats(users, checkin_records, practice_records)
            db.session.commit()
            print(f'✅ {len(users)}个用户统计数据已更新')

        print('🎉 演示数据初始化完成！')


if __name__ == '__main__':
    main()
