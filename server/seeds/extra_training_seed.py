"""
扩展训练题库 — 补充分类题量至每类至少15题，并新增短视频/学生场景分类
运行: PYTHONIOENCODING=utf-8 PYTHONPATH=. python seeds/extra_training_seed.py
"""
from collections import Counter

from sqlalchemy import inspect, text

from app import create_app
from app.extensions import db
from app.models.training import TrainingItem

EXTRA_ITEMS = [
    # ===== 基础口才 (basic) — 补9题 =====
    {'category': 'basic', 'sub_category': '朗读', 'title': '天气预报播报',
     'difficulty': 1, 'sort_order': 7, 'tags': ['朗读', '播报', '入门'],
     'sample_text': '观众朋友们大家好，欢迎收看天气预报。今天白天我市晴转多云，最高气温二十八度，东南风三到四级。夜间多云转阴，最低气温十九度。明天白天有小到中雨，请外出携带雨具，注意交通安全。后天起天气转晴，气温逐步回升。'},
    {'category': 'basic', 'sub_category': '发音', 'title': '平翘舌音专项练习',
     'difficulty': 2, 'sort_order': 8, 'tags': ['发音', '平翘舌', '基础'],
     'sample_text': '四是四，十是十，十四是十四，四十是四十。谁要是把四十说成十四，或者把十四说成四十，就请谁再来试一试。知道就说知道，不知道就说不知道，不要知道说不知道，也不要不知道说知道，那样会被人笑话。'},
    {'category': 'basic', 'sub_category': '表达', 'title': '物品一分钟介绍',
     'difficulty': 1, 'sort_order': 9, 'tags': ['描述', '观察', '入门'],
     'sample_text': '请拿起身边任意一件物品，用一分钟向听众介绍它。先说名称和用途，再说材质或特点，最后分享一个与它相关的小故事或使用心得。注意语速平稳、吐字清晰，结尾用一句话总结你对它的评价。'},
    {'category': 'basic', 'sub_category': '逻辑', 'title': '因果表达训练',
     'difficulty': 2, 'sort_order': 10, 'tags': ['逻辑', '因果', '表达'],
     'sample_text': '请用"因为…所以…"的结构，解释一个你最近观察到的生活现象。例如：因为最近雨水增多，所以路边的花草格外茂盛。注意先讲原因再讲结果，中间可以加一句"这就导致"，让逻辑链条更加清晰自然。'},
    {'category': 'basic', 'sub_category': '朗读', 'title': '古诗词朗诵',
     'difficulty': 2, 'sort_order': 11, 'tags': ['古诗词', '朗诵', '文学'],
     'sample_text': '床前明月光，疑是地上霜。举头望明月，低头思故乡。朗诵时注意停顿和情感起伏：前两句平缓叙述，"举头"处稍作上扬，"低头"处放缓下沉，把游子思乡之情自然流露出来，不必刻意煽情。'},
    {'category': 'basic', 'sub_category': '表达', 'title': '复述新闻要点',
     'difficulty': 2, 'sort_order': 12, 'tags': ['复述', '新闻', '概括'],
     'sample_text': '请阅读一段新闻后，用三句话向朋友复述核心内容：第一句说发生了什么，第二句说涉及哪些人或机构，第三句说影响或后续安排。去掉细节和修饰，只保留最关键的信息，训练你的概括能力。'},
    {'category': 'basic', 'sub_category': '发音', 'title': '前后鼻音辨析',
     'difficulty': 2, 'sort_order': 13, 'tags': ['发音', '鼻音', '基础'],
     'sample_text': '姓陈的陈，姓程的程，姓曾的曾，姓郑的郑。陈程曾郑，程陈郑曾。天上飞着一只鹰，地上跑着一只羊，鹰飞羊跑，羊跑鹰飞。练习时放慢速度，感受"n"和"ng"在口腔中的位置差异。'},
    {'category': 'basic', 'sub_category': '逻辑', 'title': '对比表达练习',
     'difficulty': 2, 'sort_order': 14, 'tags': ['对比', '逻辑', '表达'],
     'sample_text': '选择一个你熟悉的话题，用"一方面…另一方面…"的句式进行对比表达。例如：一方面，远程办公节省了通勤时间；另一方面，它也让团队面对面交流的机会减少了。最后给出你的综合看法，让听众感受到你思考的全面性。'},
    {'category': 'basic', 'sub_category': '表达', 'title': '日常见闻分享',
     'difficulty': 1, 'sort_order': 15, 'tags': ['分享', '日常', '入门'],
     'sample_text': '今天路上你看到了什么有趣或触动你的事？用一分钟分享给听众。可以按照"时间、地点、人物、经过、感受"的顺序组织语言，不需要文采飞扬，真实自然、条理清楚就是最好的表达。'},

    # ===== 演讲实战 (speech) — 补9题（含脱敏/沟通主题） =====
    {'category': 'speech', 'sub_category': '脱敏', 'title': '上台前深呼吸放松',
     'difficulty': 1, 'sort_order': 7, 'tags': ['脱敏', '抗紧张', '放松'],
     'sample_text': '站在讲台前，先做三次深呼吸：吸气四秒，屏住四秒，呼气六秒。然后对自己说："我准备充分，听众是友善的，紧张是正常的。"把目光落在后排墙壁上，而非盯着某一张脸，你会发现声音逐渐稳了下来。'},
    {'category': 'speech', 'sub_category': '脱敏', 'title': '模拟观众注视训练',
     'difficulty': 2, 'sort_order': 8, 'tags': ['脱敏', '抗紧张', '模拟'],
     'sample_text': '请想象面前坐着二十位听众，他们的目光都看着你。保持微笑，从左侧开始缓慢扫视全场，每停一秒再继续移动。同时用稳定的声音说："各位好，今天很高兴与大家分享一个话题。"重复三遍，直到不再心慌。'},
    {'category': 'speech', 'sub_category': '脱敏', 'title': '忘词应急话术',
     'difficulty': 3, 'sort_order': 9, 'tags': ['脱敏', '抗紧张', '应急'],
     'sample_text': '演讲中途突然忘词，不要慌张沉默。可以自然地说："说到这里，我想补充一个例子——"给自己争取几秒回忆时间；或者坦诚地说："请允许我整理一下思路。"喝一口水、看一眼提纲，听众反而会给你更多耐心。'},
    {'category': 'speech', 'sub_category': '职场', 'title': '季度总结发言',
     'difficulty': 3, 'sort_order': 10, 'tags': ['职场', '总结', '演讲'],
     'sample_text': '各位同事，本季度我们团队完成了既定目标的百分之一百一十。亮点有三：客户满意度创新高、新产品如期上线、团队协作效率提升。不足是部分项目排期偏紧。下季度重点将放在流程优化和人才培养上，期待与大家继续并肩前行。'},
    {'category': 'speech', 'sub_category': '沟通', 'title': '跨部门协调发言',
     'difficulty': 3, 'sort_order': 11, 'tags': ['沟通', '协调', '职场'],
     'sample_text': '感谢各位抽时间参会。今天想和大家对齐的是新功能上线时间表。我们理解市场部门希望尽快发布，技术侧也需要保证质量。建议分两步走：本周完成核心功能，下周灰度测试后再全量。这样既能抢时间，也能控制风险。'},
    {'category': 'speech', 'sub_category': '社交', 'title': '生日派对致辞',
     'difficulty': 2, 'sort_order': 12, 'tags': ['生日', '社交', '祝福'],
     'sample_text': '亲爱的朋友们，今天我们聚在一起，为寿星庆祝又一个美好的生日。认识他这么多年，我最佩服的是他永远乐观、永远愿意帮助身边的人。愿新的一岁，你所愿皆所得，所行皆坦途。来，让我们一起举杯，祝生日快乐！'},
    {'category': 'speech', 'sub_category': '教育', 'title': '读书分享会开场',
     'difficulty': 2, 'sort_order': 13, 'tags': ['读书', '分享', '教育'],
     'sample_text': '各位书友大家好，欢迎来到今天的读书分享会。本期我们共读的书目是《被讨厌的勇气》。这本书用对话体讲述了阿德勒心理学，告诉我们如何摆脱他人期待的束缚。接下来我会分享三个最触动我的观点，也欢迎大家随时交流讨论。'},
    {'category': 'speech', 'sub_category': '脱敏', 'title': '声音颤抖克服练习',
     'difficulty': 2, 'sort_order': 14, 'tags': ['脱敏', '抗紧张', '声音'],
     'sample_text': '紧张时声音容易发颤，原因是呼吸浅、喉部肌肉紧绷。练习方法：双脚与肩同宽站稳，一只手放在腹部，朗读时感觉腹部鼓起再收缩。从低声区开始，逐渐提高音量，每个字都咬清楚。坚持一周后，上台颤抖会明显减轻。'},
    {'category': 'speech', 'sub_category': '沟通', 'title': '客户提案开场白',
     'difficulty': 4, 'sort_order': 15, 'tags': ['沟通', '提案', '商务'],
     'sample_text': '尊敬的客户，感谢贵司给我们这次交流的机会。在正式开始前，我想先确认一下：您目前最关注的痛点是获客成本还是用户留存？了解您的优先级后，我会有针对性地介绍我们的解决方案，确保接下来的时间用在最关键的问题上。'},

    # ===== 直播话术 (livestream) — 补9题 =====
    {'category': 'livestream', 'sub_category': '带货', 'title': '新品首发预热',
     'difficulty': 2, 'sort_order': 7, 'tags': ['新品', '预热', '带货'],
     'sample_text': '家人们注意了，明天晚上八点，我们直播间将迎来年度重磅新品首发！这款产品是团队打磨了半年的心血之作，提前剧透一下：颜值超高、性能拉满、价格更是打破行业底价。现在点个预约，开播第一时间提醒你，还有专属优惠券可以领！'},
    {'category': 'livestream', 'sub_category': '互动', 'title': '冷场救场话术',
     'difficulty': 3, 'sort_order': 8, 'tags': ['互动', '救场', '控场'],
     'sample_text': '哎呀，感觉今天直播间有点安静啊，是不是大家都在偷偷下单没来得及说话？来，扣个"在"让我看到你们！今天准备了三个福袋，评论"想要"就有机会中奖。不说话的家人们，我可要点名啦——那位叫"快乐小狗"的朋友，你在吗？'},
    {'category': 'livestream', 'sub_category': '带货', 'title': '组合套餐推荐',
     'difficulty': 2, 'sort_order': 9, 'tags': ['套餐', '组合', '销售'],
     'sample_text': '很多姐妹问洗面奶单买划算还是套装划算，我跟大家算笔账：单买洗面奶89、爽肤水99、面霜129，加起来317。今天套装价只要199，相当于买二送一！而且三款是同一系列，成分搭配更温和，敏感肌也能放心用。'},
    {'category': 'livestream', 'sub_category': '知识', 'title': '干货分享引流',
     'difficulty': 2, 'sort_order': 10, 'tags': ['干货', '引流', '知识'],
     'sample_text': '今天免费给大家分享一个我用了三年的时间管理方法，叫做"三只青蛙法则"。每天早上列出三件最重要的事，优先完成它们，其他琐事往后排。坚持一个月，你会发现效率提升不止一倍。想要模板的扣"1"，我发粉丝群。'},
    {'category': 'livestream', 'sub_category': '娱乐', 'title': '直播开场暖场',
     'difficulty': 1, 'sort_order': 11, 'tags': ['开场', '暖场', '娱乐'],
     'sample_text': '哈喽哈喽，欢迎来到我的直播间！刚进来的朋友左上角点个关注，老粉们挥挥手让我看到你们！今天准备了超多福利，不仅有秒杀，还有整点抽奖。先跟大家聊聊最近发生的好玩事儿，等一下八点整准时上链接，千万别走开！'},
    {'category': 'livestream', 'sub_category': '带货', 'title': '售后保障承诺',
     'difficulty': 2, 'sort_order': 12, 'tags': ['售后', '信任', '带货'],
     'sample_text': '家人们放心拍，我们家所有产品支持七天无理由退换，运费险也给大家安排上了。收到不满意，联系客服直接退，不扯皮不推诿。我做直播三年了，靠的就是口碑和回头客，绝不会为了短期销量砸自己招牌。'},
    {'category': 'livestream', 'sub_category': '互动', 'title': '连麦互动引导',
     'difficulty': 3, 'sort_order': 13, 'tags': ['连麦', '互动', '控场'],
     'sample_text': '想连麦的朋友注意了，点击右下角"申请连麦"按钮，我会按顺序接入。连麦可以问我任何关于护肤的问题，也可以让我帮你看肤质。现在已经有五位朋友在排队了，没连上的别着急，评论区提问我一样会回复！'},
    {'category': 'livestream', 'sub_category': '危机', 'title': '差评现场回应',
     'difficulty': 4, 'sort_order': 14, 'tags': ['危机', '差评', '应对'],
     'sample_text': '我看到有朋友反馈上次买的尺码偏小，这个反馈非常重要。我们已经跟厂家沟通，下一批会调整版型并更新尺码表。已经购买的朋友如果穿着不合适，私信客服免费换码。感谢每一位愿意指出问题的家人，是你们帮我们做得更好。'},
    {'category': 'livestream', 'sub_category': '娱乐', 'title': '下播告别话术',
     'difficulty': 1, 'sort_order': 15, 'tags': ['下播', '告别', '粉丝'],
     'sample_text': '时间过得真快，今天的直播马上就要结束了。感谢每一位家人的陪伴，今天成交额突破预期，离不开你们的支持。没抢到的别着急，明天同一时间继续。记得关注不迷路，我们明天见，晚安！'},

    # ===== 即兴表达 (improv) — 补9题（含沟通主题） =====
    {'category': 'improv', 'sub_category': '沟通', 'title': '邻里矛盾调解',
     'difficulty': 3, 'sort_order': 7, 'tags': ['沟通', '调解', '生活'],
     'sample_text': '场景：楼上邻居深夜噪音影响你休息，你需要上门沟通。建议先肯定对方："不好意思打扰您，我知道您也不是故意的。"再说明影响："最近晚上十二点后声音有点大，我第二天要早起上班。"最后提方案："能不能十一点后尽量轻一些？非常感谢！"'},
    {'category': 'improv', 'sub_category': '观点', 'title': '人工智能利弊即兴',
     'difficulty': 3, 'sort_order': 8, 'tags': ['观点', 'AI', '即兴'],
     'sample_text': '话题：人工智能会让我们更聪明还是更懒惰？我认为关键在于如何使用。善用AI的人可以事半功倍，把省下的时间用于深度思考；过度依赖则可能丧失独立思考能力。工具本身无罪，重要的是保持学习能力和批判性思维。'},
    {'category': 'improv', 'sub_category': '故事', 'title': '意外转折讲故事',
     'difficulty': 3, 'sort_order': 9, 'tags': ['故事', '转折', '创意'],
     'sample_text': '请讲一个包含意外转折的故事：我原本以为今天会是最糟糕的一天——迟到、丢伞、被领导批评。但下班时收到一封邮件，原来早上的批评是在考验我，而那封邮件是晋升通知。有时候生活给你关上一扇门，真的会悄悄开一扇窗。'},
    {'category': 'improv', 'sub_category': '沟通', 'title': '拒绝借钱的表达',
     'difficulty': 4, 'sort_order': 10, 'tags': ['沟通', '拒绝', '情商'],
     'sample_text': '朋友向你借钱，你不想借但不想伤感情。可以这样说："兄弟，你的情况我理解，但我最近手头也紧，房贷车贷压力不小。这笔钱我实在帮不上，抱歉。不过你要是需要其他帮忙，比如一起想办法或者介绍资源，我一定尽力。"'},
    {'category': 'improv', 'sub_category': '辩论', 'title': '该不该躺平辩论',
     'difficulty': 3, 'sort_order': 11, 'tags': ['辩论', '社会', '思辨'],
     'sample_text': '辩题：年轻人该不该选择"躺平"？反方观点：躺平不是不努力，而是拒绝无意义的内卷。当付出与回报严重不成正比时，选择降低欲望、追求内心平静是理性之举。与其在焦虑中消耗，不如重新定义什么是值得追求的成功。'},
    {'category': 'improv', 'sub_category': '观点', 'title': '读书还是行路',
     'difficulty': 2, 'sort_order': 12, 'tags': ['观点', '成长', '即兴'],
     'sample_text': '有人说读万卷书不如行万里路，我认为两者并不矛盾。读书让我们站在巨人的肩膀上理解世界，行路让我们用身体感受真实。最好的状态是：读过的书指引你去哪里，走过的路让你读懂那本书。缺了任何一方，认知都不完整。'},
    {'category': 'improv', 'sub_category': '沟通', 'title': '给同事提建议',
     'difficulty': 3, 'sort_order': 13, 'tags': ['沟通', '反馈', '职场'],
     'sample_text': '场景：同事的方案有明显漏洞，你需要善意提醒。建议用"三明治法"：先肯定亮点"整体思路很清晰"，再提建议"如果能在第三部分的预算上再细化一下会更好"，最后鼓励"期待你修改后的版本，有需要随时找我讨论。"'},
    {'category': 'improv', 'sub_category': '情感', 'title': '安慰失落的朋友',
     'difficulty': 2, 'sort_order': 14, 'tags': ['情感', '安慰', '共情'],
     'sample_text': '朋友失恋了，请你安慰。不要说"天涯何处无芳草"这种空话。试着说："我知道你现在很难受，这种感受很正常，不用强迫自己马上好起来。想哭就哭，想骂就骂，我陪着你。等你准备好了，我们再聊聊接下来怎么办。"'},
    {'category': 'improv', 'sub_category': '观点', 'title': '城市生活优缺点',
     'difficulty': 2, 'sort_order': 15, 'tags': ['观点', '生活', '即兴'],
     'sample_text': '话题：大城市生活值得吗？大城市有机会、有资源、有视野，但也意味着高房租、长通勤和孤独感。我的看法是：年轻时在城市积累资本和经验是值得的，但不必把"留在北上广"当作唯一成功标准。适合自己的，才是最好的选择。'},

    # ===== 面试模拟 (interview) — 补9题 =====
    {'category': 'interview', 'sub_category': '自我介绍', 'title': '应届生自我介绍',
     'difficulty': 1, 'sort_order': 7, 'tags': ['应届生', '自我介绍', '面试'],
     'sample_text': '面试官您好，我是李华，XX大学市场营销专业应届毕业生。在校期间担任学生会外联部部长，组织过三场大型活动，锻炼了沟通协调和项目管理能力。实习期间在某互联网公司协助完成用户调研报告，对用户需求分析有初步实践。非常希望能加入贵司，从基础岗位学起。'},
    {'category': 'interview', 'sub_category': '经典问题', 'title': '职业规划怎么答',
     'difficulty': 2, 'sort_order': 8, 'tags': ['职业规划', '经典题', '面试'],
     'sample_text': '我的职业规划分三个阶段：短期一到两年，扎根岗位，熟悉业务，成为团队可靠的一员；中期三到五年，独立负责模块或项目，带小团队；长期希望成为这个领域的专家型人才。我也了解贵司的发展路径，非常认同，希望能在这里长期发展。'},
    {'category': 'interview', 'sub_category': '行为面试', 'title': '团队合作经历',
     'difficulty': 3, 'sort_order': 9, 'tags': ['团队合作', 'STAR', '行为面试'],
     'sample_text': '我分享一次跨部门协作的经历。背景是产品上线前一周发现重大bug。我主动牵头拉通研发和测试，建立每日站会机制，将问题按优先级排序。我负责对外同步进度、对内推动资源。最终提前两天修复上线，项目获得季度最佳团队奖。'},
    {'category': 'interview', 'sub_category': '经典问题', 'title': '如何处理工作压力',
     'difficulty': 2, 'sort_order': 10, 'tags': ['压力', '经典题', '面试'],
     'sample_text': '我认为适度的压力能激发效率。面对高压项目，我会先拆解任务、排优先级，把大目标变成每日可执行的小步骤。同时保持运动习惯，用跑步释放压力。上个月同时负责两个项目时，我就是用这个方法按时交付，且质量没有打折。'},
    {'category': 'interview', 'sub_category': '沟通', 'title': '与上级意见不合',
     'difficulty': 3, 'sort_order': 11, 'tags': ['沟通', '上级', '面试'],
     'sample_text': '如果与上级意见不合，我会先充分理解他的出发点，确认是不是信息差导致的分歧。然后准备数据和方案，在合适的时机私下沟通，用"我担心…因为…建议…"的句式表达。如果最终仍按他的决策执行，我也会全力配合，毕竟对结果共同负责。'},
    {'category': 'interview', 'sub_category': '行为面试', 'title': '失败经历怎么讲',
     'difficulty': 3, 'sort_order': 12, 'tags': ['失败', '反思', '行为面试'],
     'sample_text': '我分享一次失败：曾负责的活动因预估不足导致现场混乱。事后我复盘了三件事：人数预估要留缓冲、应急预案不能省、现场分工要明确。两个月后我用改进后的方案组织了更大规模活动，零事故完成。失败教会我的是敬畏细节。'},
    {'category': 'interview', 'sub_category': '经典问题', 'title': '为什么选择这个行业',
     'difficulty': 2, 'sort_order': 13, 'tags': ['行业', '动机', '面试'],
     'sample_text': '选择互联网行业，是因为我亲身经历了它如何改变生活——从移动支付到在线教育。我看好这个行业的创新活力和用户价值空间。大学期间我系统学习了产品知识，也在实习中验证了兴趣。这不是跟风，而是经过思考后的主动选择。'},
    {'category': 'interview', 'sub_category': '压力面试', 'title': '被质疑能力怎么回',
     'difficulty': 4, 'sort_order': 14, 'tags': ['压力面试', '质疑', '应对'],
     'sample_text': '如果您觉得我经验不足，我完全理解这个顾虑。但我想用两个事实说明：第一，我过去半年独立完成了XX项目，结果是用户增长百分之二十；第二，我的学习曲线一直很陡，入职前两周就能独立上手核心工作。我愿意接受试用期考核，用结果证明自己。'},
    {'category': 'interview', 'sub_category': '自我介绍', 'title': '转行求职者自我介绍',
     'difficulty': 3, 'sort_order': 15, 'tags': ['转行', '自我介绍', '面试'],
     'sample_text': '面试官好，我此前从事教师工作五年，现希望转行做用户运营。教学经历让我擅长把复杂知识讲清楚、善于观察学员反馈，这与运营岗位所需的用户沟通能力高度契合。过去半年我自学了数据分析，并完成两个自媒体账号的从零运营，积累了实操经验。'},

    # ===== 短视频口播 (short_video) — 新12题 =====
    {'category': 'short_video', 'sub_category': '知识', 'title': '三个学习技巧分享',
     'difficulty': 2, 'sort_order': 1, 'tags': ['知识', '学习', '干货'],
     'sample_text': '学习效率低？试试这三个方法：第一，费曼学习法，学完讲给别人听；第二，番茄工作法，二十五分钟专注加五分钟休息；第三，睡前回顾，花五分钟回忆今天学了什么。坚持两周，你会发现记得更牢、学得更快。关注我，下期讲记忆宫殿。'},
    {'category': 'short_video', 'sub_category': '带货', 'title': '好物开箱口播',
     'difficulty': 2, 'sort_order': 2, 'tags': ['开箱', '好物', '种草'],
     'sample_text': '姐妹们，等了一周的包裹终于到了！就是这个便携榨汁杯，颜值也太高了吧。充一次电能用十五次，打果汁三十秒搞定。我刚试了打芒果，细腻无渣，清洗也方便，水一冲就干净。链接放评论区了，不到一百块，性价比绝了！'},
    {'category': 'short_video', 'sub_category': '生活', 'title': '早起Routine分享',
     'difficulty': 1, 'sort_order': 3, 'tags': ['生活', '早起', 'vlog'],
     'sample_text': '五点起床的人都在干什么？六点半起床，喝一杯温水唤醒身体；六点十分做十分钟拉伸；六点半读二十页书；七点吃早餐。坚持早起的第三个月，我发现精力变好了，工作效率也提高了。你也可以从早起十五分钟开始试试。'},
    {'category': 'short_video', 'sub_category': '知识', 'title': '一个心理学效应',
     'difficulty': 2, 'sort_order': 4, 'tags': ['心理学', '知识', '科普'],
     'sample_text': '你知道"锚定效应"吗？第一个出现的数字会影响你的判断。商家标原价三百现价九十九，你会觉得便宜，其实成本可能只有三十。下次购物前，先问自己：如果没有对比价，我还会买吗？认清这个效应，能帮你省下不少冤枉钱。'},
    {'category': 'short_video', 'sub_category': '情感', 'title': '治愈系晚安语录',
     'difficulty': 1, 'sort_order': 5, 'tags': ['情感', '治愈', '晚安'],
     'sample_text': '今天辛苦啦。也许你没完成所有计划，也许有人说了一句让你难受的话，但这些都不否定你的价值。你已经很努力了，真的。放下手机，好好睡一觉，明天太阳升起时，又是崭新的一天。晚安，你值得被温柔对待。'},
    {'category': 'short_video', 'sub_category': '带货', 'title': '平价护肤推荐',
     'difficulty': 2, 'sort_order': 6, 'tags': ['护肤', '平价', '种草'],
     'sample_text': '学生党百元护肤清单来了！洁面选氨基酸的，温和不紧绷；水乳选含烟酰胺的，提亮肤色；防晒选SPF五十的，一年四季不能省。这三样加起来不到两百，坚持一个月皮肤状态肉眼可见变好。详情链接评论区，理性种草哦。'},
    {'category': 'short_video', 'sub_category': '热点', 'title': '热点事件短评',
     'difficulty': 3, 'sort_order': 7, 'tags': ['热点', '评论', '观点'],
     'sample_text': '最近关于"全职儿女"的讨论很火。我觉得不必非黑即白：有人是暂时过渡，有人是逃避现实。关键是看是否在积蓄力量、规划未来。社会多元，选择可以不同，但保持经济独立和精神独立，永远是底气所在。你怎么看？评论区聊聊。'},
    {'category': 'short_video', 'sub_category': '知识', 'title': '一分钟读书推荐',
     'difficulty': 2, 'sort_order': 8, 'tags': ['读书', '推荐', '知识'],
     'sample_text': '如果只能推荐一本书，我选《被讨厌的勇气》。它告诉我：别人的评价是他们的课题，不是我的。不必讨好所有人，也不必为过去的选择后悔。读完这本书，我学会了课题分离，焦虑少了一大半。强烈推荐给内耗严重的你。'},
    {'category': 'short_video', 'sub_category': '生活', 'title': '租房避坑指南',
     'difficulty': 2, 'sort_order': 9, 'tags': ['租房', '生活', '干货'],
     'sample_text': '租房三大坑千万别踩：第一，不交定金前不看合同原件；第二，不核实房东身份和房产证；第三，不拍照记录入住时房屋状况。还有，水电燃气表一定要拍初始读数。这些细节能帮你避免退租时的扯皮，刚毕业的同学尤其要注意。'},
    {'category': 'short_video', 'sub_category': '搞笑', 'title': '职场吐槽段子',
     'difficulty': 2, 'sort_order': 10, 'tags': ['搞笑', '职场', '段子'],
     'sample_text': '老板：这个项目很简单，周五前搞定。我看了看需求文档，发现要对接八个系统。周五早上老板问进度，我说：在做了在做了。翻译一下就是：刚开始看第一页。打工人的"在做了"和"好的"一样，都是自动回复，懂的都懂。'},
    {'category': 'short_video', 'sub_category': '带货', 'title': '零食测评口播',
     'difficulty': 1, 'sort_order': 11, 'tags': ['零食', '测评', '种草'],
     'sample_text': '办公室零食测评第三弹！这款海苔脆，咔嚓一口，咸香适中，不油腻。独立小包装，一包只有五十卡，减肥姐妹也能吃。我一口气吃了三包，停不下来。价格一包不到三块，囤一箱更划算。链接放评论区，先领券再下单！'},
    {'category': 'short_video', 'sub_category': '生活', 'title': '周末独处vlog旁白',
     'difficulty': 1, 'sort_order': 12, 'tags': ['独处', 'vlog', '生活'],
     'sample_text': '周末一个人也可以很充实。睡到自然醒，做一顿简单的早午餐，去附近的公园走一圈，回家看一部收藏已久的电影。没有社交压力，只有属于自己的时光。学会独处，是成年人最重要的功课之一。你的周末一般怎么过？'},

    # ===== 学生场景 (student) — 新12题 =====
    {'category': 'student', 'sub_category': '课堂', 'title': '课堂回答问题',
     'difficulty': 1, 'sort_order': 1, 'tags': ['课堂', '回答', '学生'],
     'sample_text': '老师提问时，先简要复述问题确认理解，再给出自己的观点。例如："老师，您问的是这个现象的原因，我认为主要有三点：第一……第二……第三……以上是我的看法，请老师指正。"条理清晰比长篇大论更重要，说完礼貌坐下即可。'},
    {'category': 'student', 'sub_category': '演讲', 'title': '班会主持开场',
     'difficulty': 2, 'sort_order': 2, 'tags': ['班会', '主持', '学生'],
     'sample_text': '亲爱的老师们、同学们，大家下午好！我是今天班会的主持人张明。本次班会的主题是"青春与梦想"。首先让我们用热烈的掌声欢迎班主任李老师致辞。接下来会有同学分享、小组讨论和互动环节，希望大家积极参与。'},
    {'category': 'student', 'sub_category': '竞选', 'title': '班干部竞选演讲',
     'difficulty': 2, 'sort_order': 3, 'tags': ['竞选', '班干部', '学生'],
     'sample_text': '尊敬的老师、亲爱的同学们，我竞选的是学习委员。过去一年我成绩稳定在前五，也乐于帮助同学答疑。如果当选，我会建立学习小组、整理复习资料、及时传达老师要求。请相信我，给我一个机会，我会用行动证明！请投我一票，谢谢！'},
    {'category': 'student', 'sub_category': '答辩', 'title': '毕业论文答辩开场',
     'difficulty': 3, 'sort_order': 4, 'tags': ['答辩', '毕业', '学生'],
     'sample_text': '各位老师好，我是XX专业XX班王芳，我的毕业论文题目是《社交媒体对大学生消费行为的影响研究》。论文从文献综述、研究设计、数据分析到结论建议共五章。接下来我将用八分钟汇报核心内容，恳请各位老师批评指正。'},
    {'category': 'student', 'sub_category': '社团', 'title': '社团招新宣讲',
     'difficulty': 2, 'sort_order': 5, 'tags': ['社团', '招新', '学生'],
     'sample_text': '同学们好！欢迎了解辩论社。我们是校内历史最悠久的社团之一，曾获省市辩论赛冠军。加入我们能锻炼逻辑思维、表达能力和团队协作。每周一次训练，每学期至少两场正式比赛。不需要经验，只要你热爱思考、敢于表达，辩论社欢迎你！'},
    {'category': 'student', 'sub_category': '课堂', 'title': '小组汇报总结',
     'difficulty': 2, 'sort_order': 6, 'tags': ['汇报', '小组', '学生'],
     'sample_text': '老师们好，我们小组的汇报主题是"绿色出行"。我负责总结部分：通过调研，我们发现百分之六十五的同学每周骑行或公交出行超过三次。建议学校增加共享单车停放点、优化校车班次。以上是我们组的全部内容，感谢聆听，请老师提问。'},
    {'category': 'student', 'sub_category': '竞选', 'title': '学生会主席竞选',
     'difficulty': 3, 'sort_order': 7, 'tags': ['竞选', '学生会', '学生'],
     'sample_text': '各位同学，我竞选学生会主席。过去两年我担任部长，组织了迎新晚会、志愿活动等十二场大型活动。我的理念是：学生会不是管理同学的机构，而是服务同学的平台。若当选，我将推动数字化办事、拓宽意见反馈渠道，让每位同学的声音被听见。'},
    {'category': 'student', 'sub_category': '社交', 'title': '自我介绍（新同学）',
     'difficulty': 1, 'sort_order': 8, 'tags': ['自我介绍', '社交', '学生'],
     'sample_text': '大家好，我是新来的转学生李雷，来自成都。喜欢打篮球和看科幻小说，性格比较开朗，希望尽快融入这个温暖的集体。如果有什么需要帮忙的尽管找我，也请大家多多关照。很高兴认识大家，以后请多指教！'},
    {'category': 'student', 'sub_category': '答辩', 'title': '开题报告陈述',
     'difficulty': 3, 'sort_order': 9, 'tags': ['开题', '答辩', '学生'],
     'sample_text': '老师好，我的开题报告研究的是"短视频对青少年注意力影响"。选题背景是短视频用户低龄化趋势明显；研究意义在于为家庭教育和学校引导提供参考；研究方法采用问卷调查加案例分析；预期成果是一篇八千字论文。请老师指导，谢谢。'},
    {'category': 'student', 'sub_category': '社团', 'title': '活动主持串词',
     'difficulty': 2, 'sort_order': 10, 'tags': ['主持', '活动', '学生'],
     'sample_text': '精彩的节目一个接一个，接下来让我们用掌声欢迎文艺部带来的舞蹈《青春飞扬》！表演结束后不要走开，我们准备了互动游戏，参与就有机会获得精美礼品。没有抽到奖的同学也别灰心，最后一轮还有大奖等着大家！'},
    {'category': 'student', 'sub_category': '课堂', 'title': '英语课口语展示',
     'difficulty': 2, 'sort_order': 11, 'tags': ['英语', '口语', '学生'],
     'sample_text': 'Good morning everyone. Today I\'d like to talk about my favorite hobby — photography. I started taking photos two years ago. It helps me notice beauty in daily life: a sunset, a smiling face, or raindrops on a window. Photography teaches me to slow down and appreciate the moment.'},
    {'category': 'student', 'sub_category': '社交', 'title': '感谢老师致辞',
     'difficulty': 1, 'sort_order': 12, 'tags': ['感谢', '毕业', '学生'],
     'sample_text': '敬爱的老师，感谢您三年的谆谆教诲。您不仅传授知识，更教会我们做人。记得那次我考砸了，是您耐心开导让我重拾信心。师恩难忘，我们会带着您的期望奔赴下一站。请接受我们最诚挚的谢意，祝您身体健康、桃李满天下！'},
]


def ensure_schema():
    """若 training_items 缺少 owner_user_id 列则添加（SQLite ALTER TABLE）。"""
    inspector = inspect(db.engine)
    if 'training_items' not in inspector.get_table_names():
        return
    columns = {c['name'] for c in inspector.get_columns('training_items')}
    if 'owner_user_id' not in columns:
        with db.engine.connect() as conn:
            conn.execute(text(
                'ALTER TABLE training_items ADD COLUMN owner_user_id INTEGER '
                'REFERENCES users(id) ON DELETE CASCADE'
            ))
            conn.commit()
        print('✅ 已添加 training_items.owner_user_id 列')


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        ensure_schema()

        existing_titles = {t.title for t in TrainingItem.query.with_entities(TrainingItem.title).all()}
        added = 0
        for item in EXTRA_ITEMS:
            if item['title'] not in existing_titles:
                db.session.add(TrainingItem(**item))
                existing_titles.add(item['title'])
                added += 1
        db.session.commit()
        print(f'✅ 本次新增 {added} 题，跳过已存在 {len(EXTRA_ITEMS) - added} 题')

        counts = Counter(t.category for t in TrainingItem.query.all())
        target_categories = [
            ('basic', 15), ('speech', 15), ('livestream', 15),
            ('improv', 15), ('interview', 15),
            ('short_video', 12), ('student', 12),
        ]
        print('\n📊 各分类题目数量：')
        for cat, min_count in target_categories:
            n = counts.get(cat, 0)
            status = '✓' if n >= min_count else '⚠'
            print(f'  {status} {cat}: {n} (目标≥{min_count})')
        listed = {c for c, _ in target_categories}
        other = {k: v for k, v in counts.items() if k not in listed}
        if other:
            print(f'  其他: {dict(other)}')
        print(f'\n  合计: {sum(counts.values())} 题')


if __name__ == '__main__':
    main()
