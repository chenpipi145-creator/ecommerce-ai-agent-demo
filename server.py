import json
import os
import re
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parent
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8765"))


KNOWLEDGE_BASE = [
    {
        "id": "listing_prepare",
        "title": "商品上架前准备",
        "category": "上架",
        "content": "商品上架前先检查营业执照、品牌授权、类目资质、运费模板、售后政策、发货时效、禁限售词和平台规则。资质缺失或售后承诺不清晰，会影响审核通过率和后续转化。",
        "keywords": ["上架", "资质", "营业执照", "品牌授权", "运费模板", "售后政策", "审核"],
    },
    {
        "id": "listing_title",
        "title": "标题优化规则",
        "category": "商品信息",
        "content": "标题建议采用品牌词 + 核心品类词 + 核心卖点 + 场景词 + 长尾词。避免堆砌、极限词和无关热词。标题要服务搜索匹配，也要让用户快速理解商品价值。",
        "keywords": ["标题", "关键词", "长尾词", "品牌", "品类", "卖点", "搜索"],
    },
    {
        "id": "listing_assets",
        "title": "主图视频和详情页规则",
        "category": "商品信息",
        "content": "主图要清晰展示商品主体、核心卖点和使用场景；短视频建议 15-30 秒内完成痛点、卖点、场景、信任背书展示。详情页应包含卖点、参数、场景、对比、售后保障和常见疑虑消除。",
        "keywords": ["主图", "视频", "详情页", "卖点", "场景", "疑虑", "转化"],
    },
    {
        "id": "sku_price",
        "title": "SKU 与价格检查",
        "category": "商品信息",
        "content": "SKU 组合要清晰，颜色、尺码、规格、材质不能混乱。价格要与成本、毛利、竞品和平台规则匹配，避免低价引流但高价成交的违规风险。",
        "keywords": ["SKU", "价格", "规格", "颜色", "尺码", "毛利", "定价"],
    },
    {
        "id": "paid_traffic",
        "title": "付费推广引流",
        "category": "推广",
        "content": "直通车适合关键词竞价和精准搜索流量；引力魔方适合推荐场景和人群扩量；淘宝客适合按成交付费冲销量；万相台适合智能投放和多目标优化。投放前要明确目标是测款、拉新、冲量还是利润。",
        "keywords": ["直通车", "引力魔方", "淘宝客", "万相台", "推广", "投放", "引流"],
    },
    {
        "id": "data_optimization",
        "title": "数据监控与优化",
        "category": "运营",
        "content": "搜索词报告用于加否定词和调关键词；人群数据用于调整出价和优化人群包；转化数据用于优化详情页、客服话术、价格、优惠券和售后承诺。优化应按曝光、点击、收藏加购、下单、退款分层诊断。",
        "keywords": ["数据", "搜索词", "人群", "转化", "点击率", "退款率", "优化"],
    },
    {
        "id": "after_sales_quality",
        "title": "质量问题售后规则",
        "category": "售后",
        "content": "质量问题需要用户提供照片或视频凭证。客服确认后可选择补发、换货、退款。高客单商品、恶意风险、重复投诉需要转人工复核。",
        "keywords": ["售后", "质量", "坏了", "破损", "退款", "换货", "补发"],
    },
    {
        "id": "logistics_delay",
        "title": "物流延迟处理规则",
        "category": "物流",
        "content": "物流超过 48 小时无更新，先查询物流节点。如果是揽收后停滞，联系快递催件；如果未揽收，通知仓库核查并给用户安抚话术。",
        "keywords": ["物流", "快递", "延迟", "没更新", "催件", "发货"],
    },
]


PRODUCTS = {
    "P1001": {
        "product_id": "P1001",
        "name": "云朵记忆枕",
        "brand": "眠小云",
        "category": "家居日用 / 枕头",
        "price": 199,
        "cost": 92,
        "gross_margin": 0.42,
        "return_rate": 0.048,
        "stock": 680,
        "search_index": 8600,
        "ctr": 0.036,
        "conversion_rate": 0.028,
        "roas": 2.8,
        "ad_spend_7d": 3200,
        "orders_7d": 146,
        "complaint_rate": 0.012,
        "target_audience": ["办公室久坐人群", "睡眠浅用户", "颈椎不适人群"],
        "selling_points": ["慢回弹支撑", "分区护颈", "可拆洗枕套", "适合午休和夜间睡眠"],
        "assets": {"main_images": 4, "video_seconds": 18, "detail_sections": 7, "has_scene_images": True},
        "qualification": {"business_license": True, "brand_auth": True, "category_license": True},
        "settings": {"shipping_template": True, "after_sales_policy": True, "promise_48h_ship": True},
        "listing": {
            "title": "眠小云记忆枕护颈椎慢回弹枕头成人睡眠专用枕芯",
            "attributes_complete": 0.86,
            "sku_count": 3,
            "risk_words": [],
        },
        "keywords": [
            {"word": "记忆枕", "impressions": 22000, "ctr": 0.042, "cvr": 0.031, "cost": 860},
            {"word": "护颈枕", "impressions": 16400, "ctr": 0.038, "cvr": 0.034, "cost": 720},
            {"word": "治疗颈椎病枕头", "impressions": 3100, "ctr": 0.025, "cvr": 0.004, "cost": 210},
        ],
        "audiences": [
            {"name": "睡眠用品兴趣人群", "ctr": 0.041, "cvr": 0.029, "roas": 2.9},
            {"name": "学生低价人群", "ctr": 0.055, "cvr": 0.011, "roas": 1.2},
        ],
    },
    "P2002": {
        "product_id": "P2002",
        "name": "便携榨汁杯",
        "brand": "鲜活杯",
        "category": "小家电 / 榨汁机",
        "price": 129,
        "cost": 76,
        "gross_margin": 0.35,
        "return_rate": 0.082,
        "stock": 240,
        "search_index": 6300,
        "ctr": 0.029,
        "conversion_rate": 0.018,
        "roas": 1.6,
        "ad_spend_7d": 1800,
        "orders_7d": 62,
        "complaint_rate": 0.031,
        "target_audience": ["健身人群", "学生宿舍", "新手妈妈"],
        "selling_points": ["一键榨汁", "USB 充电", "小巧便携", "杯体可拆洗"],
        "assets": {"main_images": 2, "video_seconds": 0, "detail_sections": 4, "has_scene_images": False},
        "qualification": {"business_license": True, "brand_auth": False, "category_license": True},
        "settings": {"shipping_template": True, "after_sales_policy": False, "promise_48h_ship": False},
        "listing": {
            "title": "便携榨汁杯小型榨汁机家用迷你学生果汁杯",
            "attributes_complete": 0.68,
            "sku_count": 2,
            "risk_words": ["全网最低"],
        },
        "keywords": [
            {"word": "榨汁杯", "impressions": 14800, "ctr": 0.03, "cvr": 0.019, "cost": 530},
            {"word": "便携榨汁机", "impressions": 9000, "ctr": 0.026, "cvr": 0.017, "cost": 420},
        ],
        "audiences": [
            {"name": "健身轻食人群", "ctr": 0.036, "cvr": 0.021, "roas": 1.8},
            {"name": "学生宿舍低价人群", "ctr": 0.044, "cvr": 0.012, "roas": 1.0},
        ],
    },
    "P3003": {
        "product_id": "P3003",
        "name": "夏季防晒衣",
        "brand": "轻野",
        "category": "服饰 / 防晒衣",
        "price": 169,
        "cost": 78,
        "gross_margin": 0.48,
        "return_rate": 0.061,
        "stock": 1200,
        "search_index": 12800,
        "ctr": 0.052,
        "conversion_rate": 0.032,
        "roas": 3.4,
        "ad_spend_7d": 4600,
        "orders_7d": 238,
        "complaint_rate": 0.009,
        "target_audience": ["通勤女性", "户外防晒人群", "亲子出游人群"],
        "selling_points": ["UPF50+", "轻薄透气", "冰感面料", "多色可选"],
        "assets": {"main_images": 5, "video_seconds": 25, "detail_sections": 8, "has_scene_images": True},
        "qualification": {"business_license": True, "brand_auth": True, "category_license": True},
        "settings": {"shipping_template": True, "after_sales_policy": True, "promise_48h_ship": True},
        "listing": {
            "title": "轻野防晒衣女夏季UPF50+冰感透气户外通勤防紫外线外套",
            "attributes_complete": 0.94,
            "sku_count": 12,
            "risk_words": [],
        },
        "keywords": [
            {"word": "防晒衣女", "impressions": 34000, "ctr": 0.057, "cvr": 0.035, "cost": 1260},
            {"word": "冰感防晒衣", "impressions": 18600, "ctr": 0.061, "cvr": 0.041, "cost": 920},
            {"word": "防晒神器", "impressions": 7600, "ctr": 0.049, "cvr": 0.012, "cost": 380},
        ],
        "audiences": [
            {"name": "通勤防晒人群", "ctr": 0.058, "cvr": 0.038, "roas": 3.6},
            {"name": "户外运动人群", "ctr": 0.049, "cvr": 0.028, "roas": 2.7},
        ],
    },
}


ORDERS = {
    "E20260601001": {
        "order_id": "E20260601001",
        "customer": "王女士",
        "product_id": "P1001",
        "product_name": "云朵记忆枕",
        "amount": 199,
        "status": "已发货",
        "paid_at": "2026-06-25 20:18",
        "signed": False,
    },
    "E20260601002": {
        "order_id": "E20260601002",
        "customer": "李先生",
        "product_id": "P2002",
        "product_name": "便携榨汁杯",
        "amount": 129,
        "status": "已签收",
        "paid_at": "2026-06-21 09:12",
        "signed": True,
    },
}


LOGISTICS = {
    "E20260601001": {
        "carrier": "顺丰速运",
        "tracking_no": "SF7300018826",
        "last_node": "上海转运中心已发出",
        "last_update": "2026-06-29 08:40",
        "eta": "2026-06-30",
    },
    "E20260601002": {
        "carrier": "中通快递",
        "tracking_no": "ZT8200099133",
        "last_node": "本人已签收",
        "last_update": "2026-06-23 16:22",
        "eta": "已签收",
    },
}


AFTER_SALES = []


def pct(value):
    return f"{round(value * 100, 1)}%"


def tokenize(text):
    return set(re.findall(r"[A-Za-z0-9]+|[\u4e00-\u9fff]{1,2}", text.lower()))


def rag_search(query, limit=4):
    query_tokens = tokenize(query)
    scored = []
    for doc in KNOWLEDGE_BASE:
        keywords = set(doc["keywords"])
        doc_tokens = tokenize(doc["title"] + doc["content"])
        score = len(query_tokens & doc_tokens) + len(query_tokens & keywords) * 2
        if score:
            scored.append((score, doc))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [doc for _, doc in scored[:limit]] or KNOWLEDGE_BASE[:3]


def detect_intent(message):
    rules = [
        ("listing_generation", ["生成上架", "自动上架", "发布商品", "商品标题", "详情页", "主图", "视频脚本", "卖点", "文案", "SKU"]),
        ("listing_audit", ["上架检查", "上架体检", "审核", "资质", "完整性", "合规", "检查商品", "体检"]),
        ("promotion_plan", ["推广", "投放", "直通车", "引力魔方", "淘宝客", "万相台", "引流", "预算", "放量"]),
        ("data_optimization", ["数据", "复盘", "搜索词", "人群", "转化", "点击率", "ROI", "ROAS", "优化", "降本", "亏损"]),
        ("product_selection", ["选品", "推荐商品", "现有商品", "适合做", "卖什么", "爆款", "毛利", "库存"]),
        ("after_sales", ["退款", "退货", "换货", "坏了", "破损", "售后", "补发", "投诉", "赔付", "差评", "安抚"]),
        ("logistics", ["物流", "快递", "到哪", "到哪里", "哪里了", "没更新", "催件", "发货"]),
        ("marketing", ["营销", "活动", "优惠券", "复购", "转化话术"]),
        ("order_query", ["订单", "付款", "签收", "客户", "金额"]),
    ]
    for intent, words in rules:
        if any(word.lower() in message.lower() for word in words):
            return intent
    if extract_product_id(message):
        return "listing_audit"
    return "business_consulting"


def extract_order_id(message):
    match = re.search(r"E\d{11}", message.upper())
    return match.group(0) if match else None


def extract_product_id(message):
    match = re.search(r"P\d{4}", message.upper())
    if match:
        return match.group(0)
    for product_id, product in PRODUCTS.items():
        if product["name"] in message or product["brand"] in message:
            return product_id
    return None


def choose_product_id(message):
    product_id = extract_product_id(message)
    if product_id:
        return product_id
    ranked = sorted(
        PRODUCTS.values(),
        key=lambda item: (
            item["gross_margin"],
            item["search_index"],
            item["stock"],
            -item["return_rate"],
        ),
        reverse=True,
    )
    return ranked[0]["product_id"]


def audit_product(product_id):
    product = PRODUCTS.get(product_id)
    if not product:
        return {"status": "not_found", "message": f"未找到商品 {product_id}"}

    checks = []

    def add(name, passed, fix, weight=10):
        checks.append({"name": name, "passed": passed, "fix": fix, "weight": weight})

    q = product["qualification"]
    s = product["settings"]
    assets = product["assets"]
    listing = product["listing"]

    add("营业执照", q["business_license"], "补齐店铺主体资质")
    add("品牌授权", q["brand_auth"], "补充品牌授权或改为自有品牌表述")
    add("类目资质", q["category_license"], "补齐类目所需证照")
    add("运费模板", s["shipping_template"], "创建并绑定正确运费模板")
    add("售后政策", s["after_sales_policy"], "明确退换货、质保、发货时效")
    add("标题结构", len(listing["title"]) >= 18, "按品牌+品类+卖点+场景+长尾词重写标题")
    add("主图数量", assets["main_images"] >= 4, "至少准备 4 张主图，覆盖主体、卖点、场景、细节")
    add("短视频", assets["video_seconds"] >= 15, "补 15-30 秒卖点短视频")
    add("详情页模块", assets["detail_sections"] >= 6, "补充痛点、卖点、参数、场景、对比、售后模块")
    add("属性完整度", listing["attributes_complete"] >= 0.85, "补齐颜色、规格、材质、适用人群等属性")
    add("SKU 清晰度", 2 <= listing["sku_count"] <= 16, "SKU 不要过少或过乱，规格命名保持一致")
    add("风险词", not listing["risk_words"], f"删除风险词：{', '.join(listing['risk_words'])}")

    total = sum(item["weight"] for item in checks)
    score = round(sum(item["weight"] for item in checks if item["passed"]) / total * 100)
    missing = [item for item in checks if not item["passed"]]

    return {
        "product_id": product_id,
        "product_name": product["name"],
        "score": score,
        "level": "可上架" if score >= 85 else "需优化后上架" if score >= 70 else "暂不建议上架",
        "checks": checks,
        "missing_count": len(missing),
        "top_fixes": [item["fix"] for item in missing[:5]],
    }


def generate_listing_package(product_id):
    product = PRODUCTS.get(product_id)
    if not product:
        return {"status": "not_found", "message": f"未找到商品 {product_id}"}

    core_points = " ".join(product["selling_points"][:3])
    title_a = f"{product['brand']}{product['name']} {core_points} {product['category'].split('/')[-1].strip()}"
    title_b = f"{product['name']} {product['selling_points'][0]} {product['target_audience'][0]}专用 {product['brand']}官方"

    return {
        "product_id": product_id,
        "product_name": product["name"],
        "title_options": [title_a[:60], title_b[:60]],
        "main_image_plan": [
            "第1张：白底商品主体 + 核心卖点大字",
            "第2张：真实使用场景，突出目标人群",
            "第3张：功能细节或材质细节",
            "第4张：规格/尺寸/对比图",
            "第5张：售后保障和发货承诺",
        ],
        "video_script": [
            "0-3秒：展示用户痛点",
            "3-10秒：展示核心卖点和使用效果",
            "10-20秒：展示细节、材质、规格",
            "20-30秒：价格权益、售后保障、催促下单",
        ],
        "detail_page": [
            "首屏利益点：一句话告诉用户为什么买",
            "痛点场景：用户当前问题",
            "核心卖点：3-5 个图文模块",
            "参数说明：规格、材质、适用人群",
            "竞品对比：突出优势但避免攻击竞品",
            "售后保障：发货、退换、质保、客服响应",
        ],
        "sku_price_advice": {
            "price": product["price"],
            "gross_margin": pct(product["gross_margin"]),
            "advice": "保留主推 SKU 做成交承接，增加一个入门款做低门槛点击，一个高配款提升客单价。",
        },
    }


def plan_promotion(product_id):
    product = PRODUCTS.get(product_id)
    if not product:
        return {"status": "not_found", "message": f"未找到商品 {product_id}"}

    daily_budget = 500 if product["roas"] >= 3 else 260 if product["roas"] >= 2 else 160
    return {
        "product_id": product_id,
        "product_name": product["name"],
        "objective": "先稳转化，再扩人群" if product["roas"] >= 2 else "先测素材和关键词，不急着放量",
        "budget": {
            "daily_total": daily_budget,
            "direct_train": round(daily_budget * 0.45),
            "gravity_cube": round(daily_budget * 0.3),
            "wanxiangtai": round(daily_budget * 0.2),
            "taobao_affiliate": round(daily_budget * 0.05),
        },
        "keyword_actions": [
            "保留高转化核心词，按 ROAS 分层出价",
            "低转化高花费词加入否定或降价",
            "新增场景长尾词，测试低成本精准流量",
        ],
        "audience_actions": [
            "保留高 ROAS 人群包",
            "降低低价泛人群出价",
            "新建相似人群测试包，预算不超过总预算 15%",
        ],
        "creative_actions": [
            "主图 A/B 测试：卖点版 vs 场景版",
            "短视频首 3 秒强化痛点",
            "详情页首屏增加价格权益和售后承诺",
        ],
    }


def analyze_operations(product_id):
    product = PRODUCTS.get(product_id)
    if not product:
        return {"status": "not_found", "message": f"未找到商品 {product_id}"}

    bad_keywords = [item for item in product["keywords"] if item["cost"] > 200 and item["cvr"] < product["conversion_rate"] * 0.7]
    strong_keywords = [item for item in product["keywords"] if item["cvr"] >= product["conversion_rate"]]
    weak_audiences = [item for item in product["audiences"] if item["roas"] < 2]

    diagnosis = []
    if product["ctr"] < 0.035:
        diagnosis.append("点击率偏低，优先优化主图、标题前半段和价格呈现")
    if product["conversion_rate"] < 0.025:
        diagnosis.append("转化率偏低，优先优化详情页首屏、客服话术和售后承诺")
    if product["return_rate"] > 0.07:
        diagnosis.append("退款率偏高，需要检查质量描述、预期管理和售后规则")
    if product["roas"] < 2:
        diagnosis.append("投放回收偏弱，先控预算测素材，不建议放量")
    if not diagnosis:
        diagnosis.append("核心数据健康，可以小步放量并继续做素材 A/B 测试")

    return {
        "product_id": product_id,
        "product_name": product["name"],
        "metrics": {
            "gross_margin": pct(product["gross_margin"]),
            "return_rate": pct(product["return_rate"]),
            "ctr": pct(product["ctr"]),
            "conversion_rate": pct(product["conversion_rate"]),
            "roas": product["roas"],
            "stock": product["stock"],
            "orders_7d": product["orders_7d"],
            "ad_spend_7d": product["ad_spend_7d"],
        },
        "diagnosis": diagnosis,
        "keyword_optimization": {
            "increase": [item["word"] for item in strong_keywords],
            "reduce_or_negative": [item["word"] for item in bad_keywords],
        },
        "audience_optimization": {
            "reduce_bid": [item["name"] for item in weak_audiences],
            "keep_testing": [item["name"] for item in product["audiences"] if item["roas"] >= 2],
        },
        "seven_day_actions": [
            "第1天：调整关键词出价，删除明显低效词",
            "第2天：上线两版主图和一版短视频",
            "第3天：详情页首屏增加核心利益点和售后承诺",
            "第4天：按人群 ROAS 调整预算",
            "第5-7天：复盘点击率、转化率、收藏加购、退款率，再决定是否放量",
        ],
    }


def select_product():
    candidates = []
    for product in PRODUCTS.values():
        score = (
            product["gross_margin"] * 35
            + min(product["search_index"] / 15000, 1) * 25
            + min(product["stock"] / 1000, 1) * 15
            + product["conversion_rate"] * 500
            + product["roas"] * 4
            - product["return_rate"] * 120
        )
        candidates.append(
            {
                "product_id": product["product_id"],
                "name": product["name"],
                "score": round(score, 1),
                "gross_margin": pct(product["gross_margin"]),
                "return_rate": pct(product["return_rate"]),
                "stock": product["stock"],
                "search_index": product["search_index"],
                "roas": product["roas"],
                "reason": "综合毛利、库存、搜索热度、转化和投放回收评分",
            }
        )
    return sorted(candidates, key=lambda item: item["score"], reverse=True)


def tool_get_order(order_id):
    if not order_id:
        return {"status": "missing", "message": "没有识别到订单号"}
    return ORDERS.get(order_id) or {"status": "not_found", "message": f"未找到订单 {order_id}"}


def tool_get_logistics(order_id):
    if not order_id:
        return {"status": "missing", "message": "没有识别到订单号"}
    return LOGISTICS.get(order_id) or {"status": "not_found", "message": f"订单 {order_id} 暂无物流记录"}


def tool_create_after_sales(order_id, message):
    order = ORDERS.get(order_id)
    if not order:
        return {"status": "failed", "message": "创建失败：没有找到订单"}
    ticket = {
        "ticket_id": f"AS{int(time.time())}",
        "order_id": order_id,
        "customer": order["customer"],
        "type": "退款/退货申请",
        "reason": message[:80],
        "status": "待人工复核" if order["amount"] >= 180 else "已自动受理",
    }
    AFTER_SALES.append(ticket)
    return ticket


def run_customer_service_agent(order_id, message):
    order = ORDERS.get(order_id)
    logistics = LOGISTICS.get(order_id) if order_id else None
    lower_message = message.lower()
    issue_type = "售后咨询"
    if any(word in message for word in ["退款", "退货", "不要了"]):
        issue_type = "退款退货"
    elif any(word in message for word in ["换货", "补发", "坏了", "破损", "质量"]):
        issue_type = "质量售后"
    elif any(word in message for word in ["物流", "快递", "没更新", "催件", "到哪里"]):
        issue_type = "物流催件"
    elif any(word in message for word in ["投诉", "差评", "赔付"]):
        issue_type = "投诉安抚"

    risk_level = "低"
    if any(word in message for word in ["投诉", "差评", "赔付", "12315"]):
        risk_level = "高"
    elif order and order.get("amount", 0) >= 180:
        risk_level = "中"

    evidence_needed = []
    if issue_type == "质量售后":
        evidence_needed = ["商品破损/故障照片", "外包装照片", "订单号或收件手机号后四位"]
    elif issue_type == "退款退货":
        evidence_needed = ["退货原因", "商品是否影响二次销售", "是否已签收"]
    elif issue_type == "物流催件":
        evidence_needed = ["物流单号", "最近物流节点", "是否超过 48 小时未更新"]

    decision = "继续跟进"
    if issue_type == "质量售后":
        decision = "先收集凭证，低客单可自动补发/换货，高客单转人工复核"
    elif issue_type == "退款退货":
        decision = "符合七天无理由或质量问题时进入退货退款流程"
    elif issue_type == "物流催件":
        decision = "查询物流节点，超过 48 小时无更新则催快递并同步客户"
    elif issue_type == "投诉安抚":
        decision = "立即安抚客户，标记高优先级，转人工主管复核"

    order_text = "暂未识别到订单"
    if order:
        order_text = f"订单 {order['order_id']}，商品 {order['product_name']}，金额 {order['amount']} 元，状态 {order['status']}"
    logistics_text = "暂无物流信息"
    if logistics:
        logistics_text = f"{logistics['carrier']} {logistics['tracking_no']}，最新节点：{logistics['last_node']}，预计 {logistics['eta']}"

    return {
        "agent": "客服售后 Agent",
        "issue_type": issue_type,
        "risk_level": risk_level,
        "order_context": order_text,
        "logistics_context": logistics_text,
        "decision": decision,
        "evidence_needed": evidence_needed,
        "customer_reply": (
            "亲，已经帮您核实当前情况。我们会优先处理这个问题，"
            "如果需要补充凭证，会一次性告诉您需要哪些照片/信息，避免您反复沟通。"
        ),
        "internal_tasks": [
            "核对订单状态、签收状态和售后期限",
            "按问题类型收集必要凭证",
            "低风险问题自动给出处理方案，高风险问题转人工复核",
            "处理完成后回写售后记录，并在 24 小时内追踪客户反馈",
        ],
        "handoff_required": risk_level == "高" or (order and order.get("amount", 0) >= 180),
    }


def build_listing_agent(product_id):
    audit = audit_product(product_id)
    package = generate_listing_package(product_id)
    if audit.get("status") == "not_found":
        return audit
    product = PRODUCTS.get(product_id)
    publish_status = "可进入发布队列" if audit["score"] >= 85 else "先补齐资料，不建议提交审核"
    if 70 <= audit["score"] < 85:
        publish_status = "可进入预发布，但提交审核前必须完成 P0 修复"

    compliance_tasks = []
    for check in audit.get("checks", []):
        if not check.get("passed"):
            compliance_tasks.append(
                {
                    "task": check["fix"],
                    "owner": "商品运营" if check["name"] not in {"主图数量", "短视频", "详情页模块"} else "设计/内容",
                    "priority": "P0" if check["weight"] >= 10 else "P1",
                }
            )

    return {
        "agent": "商品上架 Agent",
        "product_id": product_id,
        "product_name": product["name"],
        "publish_status": publish_status,
        "audit_score": audit["score"],
        "generated_assets": {
            "title_options": package.get("title_options", []),
            "main_image_plan": package.get("main_image_plan", []),
            "video_script": package.get("video_script", []),
            "detail_page": package.get("detail_page", []),
            "sku_price_advice": package.get("sku_price_advice", {}),
        },
        "compliance_tasks": compliance_tasks[:8],
        "publish_checklist": [
            "确认资质、品牌授权、类目许可齐全",
            "检查标题是否包含品牌、品类、核心卖点、场景词、长尾词",
            "检查主图、短视频、详情页是否覆盖卖点、场景、参数、售后承诺",
            "检查 SKU 命名、价格、库存、运费模板和发货时效",
            "提交审核后记录审核结果，失败原因进入下一轮修复",
        ],
        "automation_boundary": "当前 Demo 只模拟生成与审核，不会向真实平台提交商品。",
    }


def optimize_ad_agent(product_id):
    product = PRODUCTS.get(product_id)
    if not product:
        return {"status": "not_found", "message": f"未找到商品 {product_id}"}
    promotion = plan_promotion(product_id)
    ops = analyze_operations(product_id)
    metrics = ops.get("metrics", {})
    roas = product["roas"]
    conversion = product["conversion_rate"]
    ctr = product["ctr"]

    budget_strategy = "保守测试"
    if roas >= 3 and conversion >= 0.03:
        budget_strategy = "小步放量"
    elif roas < 2:
        budget_strategy = "控预算止损"

    bid_actions = []
    for keyword in product["keywords"]:
        if keyword["cvr"] >= conversion and roas >= 2:
            bid_actions.append({"word": keyword["word"], "action": "加价 10%-15%", "reason": "转化高于商品均值，可承接更多精准流量"})
        elif keyword["cost"] > 200 and keyword["cvr"] < conversion * 0.7:
            bid_actions.append({"word": keyword["word"], "action": "降价 20% 或加入否定词观察", "reason": "花费较高但转化偏弱"})
        else:
            bid_actions.append({"word": keyword["word"], "action": "维持观察", "reason": "样本仍需继续积累"})

    audience_actions = []
    for audience in product["audiences"]:
        action = "保留并扩相似人群" if audience["roas"] >= 2 else "降低出价并限制预算"
        audience_actions.append({"audience": audience["name"], "action": action, "roas": audience["roas"]})

    return {
        "agent": "广告投放/数据优化 Agent",
        "product_id": product_id,
        "product_name": product["name"],
        "budget_strategy": budget_strategy,
        "current_metrics": metrics,
        "budget_plan": promotion.get("budget", {}),
        "bid_actions": bid_actions,
        "audience_actions": audience_actions,
        "creative_tests": [
            "主图 A：卖点大字版；主图 B：真实场景版；48 小时后按点击率淘汰低效版本",
            "短视频首 3 秒突出痛点，结尾加入售后承诺和限时权益",
            "详情页首屏增加价格权益、核心卖点和退换承诺，降低咨询犹豫",
        ],
        "monitoring_rules": [
            "ROAS 连续 2 天低于 1.5：暂停放量，只保留低预算测词",
            "点击率低于 3%：优先换主图和标题前半段",
            "转化率低于 2%：检查价格、详情页首屏、客服话术和售后承诺",
            "退款率高于 7%：暂停放量，先排查商品描述和质量预期差",
        ],
        "automation_boundary": "当前 Demo 只模拟投放优化动作，不会真实修改广告账户。",
    }


def run_tools(intent, message):
    order_id = extract_order_id(message)
    product_id = choose_product_id(message)
    calls = []

    if intent in {"listing_audit", "listing_generation", "promotion_plan", "data_optimization", "marketing"}:
        calls.append({"name": "get_product_snapshot", "input": {"product_id": product_id}, "output": PRODUCTS.get(product_id)})

    if intent == "listing_audit":
        calls.append({"name": "audit_product_listing", "input": {"product_id": product_id}, "output": audit_product(product_id)})
        calls.append({"name": "run_listing_agent", "input": {"product_id": product_id}, "output": build_listing_agent(product_id)})

    if intent == "listing_generation":
        calls.append({"name": "generate_listing_package", "input": {"product_id": product_id}, "output": generate_listing_package(product_id)})
        calls.append({"name": "audit_product_listing", "input": {"product_id": product_id}, "output": audit_product(product_id)})
        calls.append({"name": "run_listing_agent", "input": {"product_id": product_id}, "output": build_listing_agent(product_id)})

    if intent == "promotion_plan" or intent == "marketing":
        calls.append({"name": "plan_paid_promotion", "input": {"product_id": product_id}, "output": plan_promotion(product_id)})
        calls.append({"name": "analyze_operations", "input": {"product_id": product_id}, "output": analyze_operations(product_id)})
        calls.append({"name": "run_ad_optimization_agent", "input": {"product_id": product_id}, "output": optimize_ad_agent(product_id)})

    if intent == "data_optimization":
        calls.append({"name": "analyze_operations", "input": {"product_id": product_id}, "output": analyze_operations(product_id)})
        calls.append({"name": "plan_paid_promotion", "input": {"product_id": product_id}, "output": plan_promotion(product_id)})
        calls.append({"name": "run_ad_optimization_agent", "input": {"product_id": product_id}, "output": optimize_ad_agent(product_id)})

    if intent == "product_selection":
        calls.append({"name": "rank_products_for_campaign", "input": {}, "output": select_product()})
        best_id = select_product()[0]["product_id"]
        calls.append({"name": "plan_paid_promotion", "input": {"product_id": best_id}, "output": plan_promotion(best_id)})
        calls.append({"name": "run_ad_optimization_agent", "input": {"product_id": best_id}, "output": optimize_ad_agent(best_id)})

    if intent in {"order_query", "logistics", "after_sales"}:
        calls.append({"name": "get_order", "input": {"order_id": order_id}, "output": tool_get_order(order_id)})

    if intent in {"logistics", "after_sales"}:
        calls.append({"name": "get_logistics", "input": {"order_id": order_id}, "output": tool_get_logistics(order_id)})
        calls.append({"name": "run_customer_service_agent", "input": {"order_id": order_id, "message": message}, "output": run_customer_service_agent(order_id, message)})

    if intent == "after_sales":
        calls.append(
            {
                "name": "create_after_sales",
                "input": {"order_id": order_id, "reason": message},
                "output": tool_create_after_sales(order_id, message),
            }
        )

    if intent == "order_query":
        calls.append({"name": "run_customer_service_agent", "input": {"order_id": order_id, "message": message}, "output": run_customer_service_agent(order_id, message)})

    if intent == "business_consulting":
        calls.append({"name": "rank_products_for_campaign", "input": {}, "output": select_product()})

    return calls


def fallback_answer(message, intent, docs, tool_calls, reason=None):
    intent_name = {
        "listing_audit": "商品上架体检",
        "listing_generation": "商品上架方案生成",
        "promotion_plan": "付费推广计划",
        "data_optimization": "数据监控与优化",
        "product_selection": "选品分析",
        "after_sales": "售后处理",
        "logistics": "物流查询",
        "marketing": "营销运营",
        "order_query": "订单查询",
        "business_consulting": "电商运营咨询",
    }.get(intent, "电商运营咨询")

    doc_titles = "、".join([doc["title"] for doc in docs])
    tool_names = "、".join([call["name"] for call in tool_calls]) or "暂无工具"
    summary = f"已识别为【{intent_name}】，参考知识库：{doc_titles}，执行工具：{tool_names}。"
    if reason:
        summary = f"Groq 请求未成功（{reason}），当前展示本地结构化分析。{summary}"

    report_sections = [
        {
            "title": "判断",
            "items": [
                f"当前问题属于 {intent_name} 场景。",
                "系统已完成知识库检索和业务工具调用。",
            ],
        },
        {
            "title": "建议",
            "items": [
                "先补齐商品信息和资质，再做投放放量。",
                "投放优化按搜索词、人群、转化三层拆解。",
                "客服话术要承接售后承诺，降低犹豫和退款。",
            ],
        },
    ]

    return {
        "mode": "mock",
        "intent": intent_name,
        "summary": summary,
        "reply": "这是本地兜底分析：已经跑通意图识别、RAG、工具调用和报告生成。配置可用 GROQ_API_KEY 后，会由 Groq 生成更完整的运营诊断。",
        "executive_summary": summary,
        "report_sections": report_sections,
        "scorecards": [],
        "action_plan": [
            {"priority": "P0", "action": "补齐资质、运费模板、售后政策和风险词检查", "owner": "运营", "metric": "审核通过率"},
            {"priority": "P1", "action": "优化标题、主图视频和详情页首屏", "owner": "商品运营", "metric": "点击率/转化率"},
            {"priority": "P2", "action": "按搜索词、人群、转化数据调整投放", "owner": "投手", "metric": "ROAS"},
        ],
        "steps": ["识别意图", "检索知识库", "调用工具", "输出运营报告"],
        "tool_calls": tool_calls,
        "next_actions": ["替换 mock 数据为真实店铺数据", "接入商品、订单、广告接口", "沉淀平台规则知识库"],
        "risk_notes": ["涉及平台规则、品牌授权、退款争议时，建议保留人工复核。"],
    }


def call_groq(message, intent, docs, tool_calls):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None, "未配置 GROQ_API_KEY"

    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    base_url = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/")
    payload = {
        "model": model,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是资深电商运营智能体，擅长商品上架、标题优化、详情页、SKU定价、付费推广、数据复盘、客服售后。"
                    "你现在包含三个子 Agent：客服售后 Agent、商品上架 Agent、广告投放/数据优化 Agent。"
                    "客服售后 Agent 要输出问题分类、风险等级、凭证要求、客户话术和内部处理动作。"
                    "商品上架 Agent 要输出审核结论、标题/主图/视频/详情页/SKU方案、合规修复任务和发布检查清单。"
                    "广告投放/数据优化 Agent 要输出预算策略、关键词出价动作、人群动作、素材测试和监控止损规则。"
                    "你必须使用中文，输出要像运营主管写的执行报告，不要只给普通客服回复。"
                    "你必须严格依据 retrieved_docs 和 tool_calls 的数据，不要编造订单、物流、广告、商品数据。"
                    "如果工具数据不足，要说清楚缺口，并给出需要补充的数据。"
                    "输出严格 JSON，不要 Markdown。"
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "user_message": message,
                        "detected_intent": intent,
                        "retrieved_docs": docs,
                        "tool_calls": tool_calls,
                        "required_json_schema": {
                            "intent": "中文意图名称",
                            "summary": "一句话说明核心结论",
                            "reply": "可给业务方看的完整中文分析，至少 4 段，包含结论、依据、动作、风险",
                            "executive_summary": "运营主管视角总结",
                            "report_sections": [
                                {"title": "模块标题", "items": ["具体分析点，必须可执行"]}
                            ],
                            "scorecards": [
                                {"label": "指标名", "value": "指标值", "status": "好/一般/风险", "note": "解释"}
                            ],
                            "action_plan": [
                                {"priority": "P0/P1/P2", "action": "动作", "owner": "负责人", "metric": "衡量指标"}
                            ],
                            "next_actions": ["下一步动作"],
                            "risk_notes": ["风险提醒"],
                        },
                    },
                    ensure_ascii=False,
                ),
            },
        ],
    }
    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "ecommerce-agent-demo/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=35) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        reason = f"HTTP {error.code}"
        try:
            detail = json.loads(body).get("error", {})
            code = detail.get("code") or detail.get("type")
            error_message = detail.get("message")
            if code or error_message:
                reason = f"{reason} {code or ''}: {error_message or ''}".strip()
        except json.JSONDecodeError:
            if body:
                reason = f"{reason}: {body[:240]}"
        print(f"[groq] failed: {reason}")
        return None, reason
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        print(f"[groq] failed: {error}")
        return None, str(error)

    text = ""
    choices = data.get("choices") or []
    if choices:
        text = (choices[0].get("message") or {}).get("content") or ""

    try:
        result = json.loads(text.strip().removeprefix("```json").removesuffix("```").strip())
    except json.JSONDecodeError:
        result = fallback_answer(message, intent, docs, tool_calls, "Groq 返回内容不是严格 JSON")
        result["summary"] = "Groq 已返回内容，但不是严格 JSON，已使用兜底结构。"
        result["reply"] = text.strip() or result["reply"]
        return result, None

    result["mode"] = "groq"
    result["tool_calls"] = tool_calls
    result.setdefault("summary", "Groq 已生成运营分析。")
    result.setdefault("reply", "")
    result.setdefault("executive_summary", result["summary"])
    result.setdefault("report_sections", [])
    result.setdefault("scorecards", [])
    result.setdefault("action_plan", [])
    result.setdefault("next_actions", [])
    result.setdefault("risk_notes", [])
    return result, None


def enrich_answer(answer, tool_calls):
    tool_map = {call["name"]: call["output"] for call in tool_calls}

    if len(answer.get("report_sections", [])) < 6:
        sections = list(answer.get("report_sections", []))
        audit = tool_map.get("audit_product_listing")
        if audit and audit.get("top_fixes"):
            sections.append(
                {
                    "title": "上架体检缺口",
                    "items": [
                        f"上架评分：{audit.get('score')}，结论：{audit.get('level')}",
                        *audit.get("top_fixes", []),
                    ],
                }
            )
        listing = tool_map.get("generate_listing_package")
        if listing:
            sections.append(
                {
                    "title": "商品信息生成建议",
                    "items": [
                        f"标题方向：{listing.get('title_options', [''])[0]}",
                        *listing.get("main_image_plan", [])[:3],
                    ],
                }
            )
        promotion = tool_map.get("plan_paid_promotion")
        if promotion:
            budget = promotion.get("budget", {})
            sections.append(
                {
                    "title": "推广投放建议",
                    "items": [
                        f"目标：{promotion.get('objective')}",
                        f"日预算建议：{budget.get('daily_total')} 元",
                        *promotion.get("keyword_actions", [])[:2],
                    ],
                }
            )
        ops = tool_map.get("analyze_operations")
        if ops:
            sections.append(
                {
                    "title": "数据诊断",
                    "items": [
                        *ops.get("diagnosis", []),
                        *ops.get("seven_day_actions", [])[:2],
                    ],
                }
            )
        ranking = tool_map.get("rank_products_for_campaign")
        if ranking:
            best = ranking[0]
            sections.append(
                {
                    "title": "活动选品结论",
                    "items": [
                        f"优先推荐：{best.get('name')}，综合评分 {best.get('score')}",
                        f"毛利 {best.get('gross_margin')}，库存 {best.get('stock')}，ROAS {best.get('roas')}",
                        "建议先用高意向关键词和高 ROAS 人群小预算验证，再扩大投放。",
                    ],
                }
            )
        customer_agent = tool_map.get("run_customer_service_agent")
        if customer_agent:
            sections.extend(
                [
                    {
                        "title": "客服售后判断",
                        "items": [
                            f"问题类型：{customer_agent.get('issue_type')}，风险等级：{customer_agent.get('risk_level')}",
                            f"处理决策：{customer_agent.get('decision')}",
                            f"是否转人工：{'需要' if customer_agent.get('handoff_required') else '暂不需要'}",
                        ],
                    },
                    {
                        "title": "订单与物流上下文",
                        "items": [
                            customer_agent.get("order_context", "暂无订单上下文"),
                            customer_agent.get("logistics_context", "暂无物流上下文"),
                            f"客户回复：{customer_agent.get('customer_reply')}",
                        ],
                    },
                    {
                        "title": "客服工单动作",
                        "items": [
                            *(customer_agent.get("evidence_needed") or ["当前场景无需额外凭证"]),
                            *customer_agent.get("internal_tasks", [])[:3],
                        ],
                    },
                ]
            )
        listing_agent = tool_map.get("run_listing_agent")
        if listing_agent:
            sections.append(
                {
                    "title": "商品上架 Agent 执行结果",
                    "items": [
                        f"发布状态：{listing_agent.get('publish_status')}，上架评分：{listing_agent.get('audit_score')}",
                        *listing_agent.get("publish_checklist", [])[:4],
                    ],
                }
            )
        ad_agent = tool_map.get("run_ad_optimization_agent")
        if ad_agent:
            first_bid = ad_agent.get("bid_actions", [{}])[0]
            sections.append(
                {
                    "title": "广告投放优化动作",
                    "items": [
                        f"预算策略：{ad_agent.get('budget_strategy')}",
                        f"关键词动作：{first_bid.get('word', '-')} - {first_bid.get('action', '-')}",
                        *ad_agent.get("monitoring_rules", [])[:3],
                    ],
                }
            )
        answer["report_sections"] = sections

    if len(answer.get("scorecards", [])) < 6:
        scorecards = list(answer.get("scorecards", []))
        snapshot = tool_map.get("get_product_snapshot")
        audit = tool_map.get("audit_product_listing")
        ops = tool_map.get("analyze_operations")
        customer_agent = tool_map.get("run_customer_service_agent")
        listing_agent = tool_map.get("run_listing_agent")
        ad_agent = tool_map.get("run_ad_optimization_agent")
        if audit:
            scorecards.append(
                {
                    "label": "上架评分",
                    "value": str(audit.get("score")),
                    "status": audit.get("level"),
                    "note": f"缺口 {audit.get('missing_count')} 项",
                }
            )
        if snapshot:
            scorecards.extend(
                [
                    {"label": "毛利率", "value": pct(snapshot.get("gross_margin", 0)), "status": "好" if snapshot.get("gross_margin", 0) >= 0.4 else "一般", "note": "用于判断是否适合投放放量"},
                    {"label": "退款率", "value": pct(snapshot.get("return_rate", 0)), "status": "风险" if snapshot.get("return_rate", 0) > 0.07 else "好", "note": "影响利润和投放回收"},
                    {"label": "库存", "value": str(snapshot.get("stock", 0)), "status": "好" if snapshot.get("stock", 0) >= 500 else "一般", "note": "库存不足不建议大促放量"},
                ]
            )
        if ops:
            metrics = ops.get("metrics", {})
            scorecards.extend(
                [
                    {"label": "点击率", "value": metrics.get("ctr", "-"), "status": "好", "note": "判断主图和标题吸引力"},
                    {"label": "转化率", "value": metrics.get("conversion_rate", "-"), "status": "好", "note": "判断详情页和价格承接"},
                    {"label": "ROAS", "value": str(metrics.get("roas", "-")), "status": "好" if metrics.get("roas", 0) >= 2 else "风险", "note": "判断投放回收"},
                ]
            )
        if customer_agent:
            scorecards.extend(
                [
                    {
                        "label": "售后风险",
                        "value": customer_agent.get("risk_level", "-"),
                        "status": "风险" if customer_agent.get("risk_level") == "高" else "一般",
                        "note": customer_agent.get("issue_type", "客服售后"),
                    },
                    {
                        "label": "转人工",
                        "value": "需要" if customer_agent.get("handoff_required") else "不需要",
                        "status": "风险" if customer_agent.get("handoff_required") else "好",
                        "note": "高风险或高客单问题建议人工复核",
                    },
                    {
                        "label": "凭证项",
                        "value": str(len(customer_agent.get("evidence_needed", []))),
                        "status": "一般",
                        "note": "用于判断是否可以自动处理",
                    },
                ]
            )
        if listing_agent:
            scorecards.append(
                {
                    "label": "发布状态",
                    "value": listing_agent.get("publish_status", "-"),
                    "status": "好" if "可进入" in listing_agent.get("publish_status", "") else "风险",
                    "note": "模拟商品上架 Agent 的审核结论",
                }
            )
        if ad_agent:
            scorecards.append(
                {
                    "label": "投放策略",
                    "value": ad_agent.get("budget_strategy", "-"),
                    "status": "风险" if ad_agent.get("budget_strategy") == "控预算止损" else "好",
                    "note": "根据 ROAS、点击率、转化率判断",
                }
            )
        deduped = []
        seen = set()
        for card in scorecards:
            key = card.get("label")
            if key not in seen:
                deduped.append(card)
                seen.add(key)
        answer["scorecards"] = deduped[:6]

    if len(answer.get("action_plan", [])) < 6:
        actions = list(answer.get("action_plan", []))
        audit = tool_map.get("audit_product_listing")
        promotion = tool_map.get("plan_paid_promotion")
        ops = tool_map.get("analyze_operations")
        customer_agent = tool_map.get("run_customer_service_agent")
        listing_agent = tool_map.get("run_listing_agent")
        ad_agent = tool_map.get("run_ad_optimization_agent")
        if audit:
            for fix in audit.get("top_fixes", [])[:3]:
                actions.append({"priority": "P0", "action": fix, "owner": "商品运营", "metric": "上架通过率/转化率"})
        if promotion:
            actions.append({"priority": "P1", "action": "按直通车、引力魔方、万相台拆分预算并做素材测试", "owner": "投手", "metric": "ROAS/点击率"})
        if ops:
            actions.append({"priority": "P1", "action": "按搜索词、人群、转化三层复盘，连续 7 天记录变化", "owner": "运营", "metric": "转化率/退款率"})
        if customer_agent:
            actions.append({"priority": "P0" if customer_agent.get("risk_level") == "高" else "P1", "action": customer_agent.get("decision", "处理客服售后问题"), "owner": "客服主管", "metric": "响应时效/投诉率"})
            for task in customer_agent.get("internal_tasks", [])[:3]:
                actions.append({"priority": "P1", "action": task, "owner": "客服", "metric": "处理时效/满意度"})
        if listing_agent:
            for task in listing_agent.get("compliance_tasks", [])[:2]:
                actions.append({"priority": task.get("priority", "P1"), "action": task.get("task"), "owner": task.get("owner", "商品运营"), "metric": "审核通过率"})
        if ad_agent:
            for item in ad_agent.get("bid_actions", [])[:2]:
                actions.append({"priority": "P1", "action": f"{item.get('word')}：{item.get('action')}", "owner": "投手", "metric": "ROAS/转化率"})
        answer["action_plan"] = actions[:6]

    return answer


def build_agent_response(message):
    docs = rag_search(message)
    intent = detect_intent(message)
    tool_calls = run_tools(intent, message)
    answer, model_error = call_groq(message, intent, docs, tool_calls)
    if not answer:
        answer = fallback_answer(message, intent, docs, tool_calls, model_error)
    answer = enrich_answer(answer, tool_calls)
    answer["retrieved_docs"] = docs
    answer["trace"] = [
        {"name": "意图理解", "detail": intent},
        {"name": "RAG 检索", "detail": "、".join(doc["title"] for doc in docs)},
        {"name": "工具执行", "detail": "、".join(call["name"] for call in tool_calls) or "无需工具"},
        {"name": "反馈生成", "detail": "Groq 生成" if answer["mode"] == "groq" else "本地模拟"},
    ]
    return answer


class DemoHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path):
        content = path.read_bytes()
        content_type = "text/html; charset=utf-8" if path.suffix == ".html" else "application/octet-stream"
        if path.suffix == ".css":
            content_type = "text/css; charset=utf-8"
        if path.suffix == ".js":
            content_type = "application/javascript; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        if self.path == "/":
            self._send_file(ROOT / "web" / "index.html")
            return
        if self.path in {"/agent", "/workbench"}:
            self._send_file(ROOT / "web" / "agent.html")
            return
        if self.path == "/api/demo-data":
            self._send_json({"orders": ORDERS, "products": PRODUCTS, "knowledge": KNOWLEDGE_BASE})
            return
        requested = (ROOT / "web" / self.path.lstrip("/")).resolve()
        if requested.is_file() and ROOT in requested.parents:
            self._send_file(requested)
            return
        self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        if self.path != "/api/chat":
            self._send_json({"error": "Not found"}, 404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON"}, 400)
            return
        message = str(payload.get("message", "")).strip()
        if not message:
            self._send_json({"error": "请输入业务问题"}, 400)
            return
        self._send_json(build_agent_response(message))

    def log_message(self, format, *args):
        print(f"[demo] {self.address_string()} - {format % args}")


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), DemoHandler)
    print(f"电商 AI 智能体 Demo 已启动：http://{HOST}:{PORT}")
    print("配置 GROQ_API_KEY 后将使用 Groq；未配置时使用本地模拟模式。")
    server.serve_forever()
