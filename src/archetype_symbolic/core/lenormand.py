"""Deterministic 36-card Lenormand oracle deck and spread generator."""

from __future__ import annotations

import random
from typing import Any

LENORMAND_36: tuple[dict[str, str], ...] = (
    {
        "num": "1",
        "name": "Kỵ Sĩ (Rider)",
        "icon": "🏇",
        "meaning": "Tin tức nhanh chóng, khách ghé thăm, sự khởi đầu mới mẻ.",
    },
    {
        "num": "2",
        "name": "Cỏ 4 Lá (Clover)",
        "icon": "🍀",
        "meaning": "May mắn bất ngờ, cơ hội nhỏ nhưng chớp nhoáng, niềm vui tức thì.",
    },
    {
        "num": "3",
        "name": "Con Tàu (Ship)",
        "icon": "⛵",
        "meaning": "Hành trình, du lịch, khoảng cách địa lý hoặc công việc giao thương.",
    },
    {
        "num": "4",
        "name": "Ngôi Nhà (House)",
        "icon": "🏡",
        "meaning": "Tổ ấm, sự an toàn, gia đình, nền móng vững chắc.",
    },
    {
        "num": "5",
        "name": "Cái Cây (Tree)",
        "icon": "🌳",
        "meaning": "Sức khỏe, sự trưởng thành lâu dài, nguồn cội, năng lượng bền bỉ.",
    },
    {
        "num": "6",
        "name": "Mây Mù (Clouds)",
        "icon": "☁️",
        "meaning": "Sự mơ hồ, hiểu lầm tạm thời, bối rối chưa có lời giải.",
    },
    {
        "num": "7",
        "name": "Con Rắn (Snake)",
        "icon": "🐍",
        "meaning": "Sự phức tạp, phản trắc ngầm, đường vòng, cần hết sức thận trọng.",
    },
    {
        "num": "8",
        "name": "Quan Tài (Coffin)",
        "icon": "⚰️",
        "meaning": "Sự chấm dứt một giai đoạn, buông bỏ để tái sinh, thay đổi lớn.",
    },
    {
        "num": "9",
        "name": "Bó Hoa (Bouquet)",
        "icon": "💐",
        "meaning": "Món quà bất ngờ, lời khen ngợi, sự trân trọng và hạnh phúc.",
    },
    {
        "num": "10",
        "name": "Lưỡi Hái (Scythe)",
        "icon": "🌾",
        "meaning": "Quyết định cắt đứt nhanh chóng, đột ngột, nguy cơ va chạm nhẹ.",
    },
    {
        "num": "11",
        "name": "Roi Da & Chổi (Whip)",
        "icon": "⚔️",
        "meaning": "Tranh cãi, lặp đi lặp lại, xung đột hoặc rèn luyện thể chất căng thẳng.",
    },
    {
        "num": "12",
        "name": "Đôi Chim (Birds)",
        "icon": "🦉",
        "meaning": "Trò chuyện, tin nhắn qua lại, sự lo âu lặt vặt ngắn hạn.",
    },
    {
        "num": "13",
        "name": "Đứa Trẻ (Child)",
        "icon": "👶",
        "meaning": "Sự ngây thơ, dự án mới tinh, bắt đầu từ con số không.",
    },
    {
        "num": "14",
        "name": "Con Cáo (Fox)",
        "icon": "🦊",
        "meaning": "Công việc hàng ngày, mưu trí mưu sinh, đề phòng bẫy ngầm.",
    },
    {
        "num": "15",
        "name": "Con Gấu (Bear)",
        "icon": "🐻",
        "meaning": "Tài chính, sếp/người bảo trợ, quyền lực, sự che chở vững vàng.",
    },
    {
        "num": "16",
        "name": "Ngôi Sao (Stars)",
        "icon": "⭐",
        "meaning": "Hy vọng, dẫn lối, giấc mơ sáng tỏ, cảm hứng dồi dào.",
    },
    {
        "num": "17",
        "name": "Chim Cò (Stork)",
        "icon": "🪶",
        "meaning": "Sự chuyển dịch, đổi mới không gian sống hoặc thăng tiến tích cực.",
    },
    {
        "num": "18",
        "name": "Chú Chó (Dog)",
        "icon": "🐶",
        "meaning": "Bạn bè trung thành, sự ủng hộ đáng tin cậy, tri kỷ.",
    },
    {
        "num": "19",
        "name": "Tòa Tháp (Tower)",
        "icon": "🏰",
        "meaning": "Cơ quan nhà nước, trường học, sự độc lập hoặc cô đơn tạm thời.",
    },
    {
        "num": "20",
        "name": "Khu Vườn (Garden)",
        "icon": "⛲",
        "meaning": "Cộng đồng, sự kiện công cộng, mạng xã hội, giao lưu đông vui.",
    },
    {
        "num": "21",
        "name": "Ngọn Núi (Mountain)",
        "icon": "⛰️",
        "meaning": "Vật cản lớn, sự trì hoãn, thách thức cần kiên trì vượt qua.",
    },
    {
        "num": "22",
        "name": "Ngã Ba Đường (Crossroads)",
        "icon": "🛤️",
        "meaning": "Ngã rẽ cuộc đời, nhiều lựa chọn, cần đưa ra quyết định.",
    },
    {
        "num": "23",
        "name": "Đàn Chuột (Mice)",
        "icon": "🐭",
        "meaning": "Tổn thất nhỏ giọt, căng thẳng gặm nhấm, hao mòn năng lượng.",
    },
    {
        "num": "24",
        "name": "Trái Tim (Heart)",
        "icon": "❤️",
        "meaning": "Tình cảm chân thành, niềm đam mê, hòa hợp yêu thương.",
    },
    {
        "num": "25",
        "name": "Chiếc Nhẫn (Ring)",
        "icon": "💍",
        "meaning": "Cam kết, hợp đồng, hôn ước, sự gắn bó tuần hoàn.",
    },
    {
        "num": "26",
        "name": "Cuốn Sách (Book)",
        "icon": "📖",
        "meaning": "Bí mật chưa mở, nghiên cứu học tập, kiến thức chuyên sâu.",
    },
    {
        "num": "27",
        "name": "Lá Thư (Letter)",
        "icon": "✉️",
        "meaning": "Văn bản, email, tài liệu giấy tờ chính thức đến tay.",
    },
    {
        "num": "28",
        "name": "Người Nam (Man)",
        "icon": "👨",
        "meaning": "Nhân vật nam quan trọng hoặc năng lượng hành động nam tính.",
    },
    {
        "num": "29",
        "name": "Người Nữ (Woman)",
        "icon": "👩",
        "meaning": "Nhân vật nữ quan trọng hoặc năng lượng trực giác nữ tính.",
    },
    {
        "num": "30",
        "name": "Hoa Loa Kèn (Lily)",
        "icon": "⚜️",
        "meaning": "Sự thuần khiết, bình an tuổi già, kinh nghiệm từng trải, đạo đức.",
    },
    {
        "num": "31",
        "name": "Mặt Trời (Sun)",
        "icon": "☀️",
        "meaning": "Chiến thắng vang dội, năng lượng tràn đầy, sự thành công rực rỡ.",
    },
    {
        "num": "32",
        "name": "Mặt Trăng (Moon)",
        "icon": "🌙",
        "meaning": "Danh tiếng, cảm xúc sâu kín, trực giác tâm linh, nghệ thuật.",
    },
    {
        "num": "33",
        "name": "Chiếc Chìa Khóa (Key)",
        "icon": "🔑",
        "meaning": "Chìa khóa mở nút thắt, giải pháp quan trọng, tính tất yếu.",
    },
    {
        "num": "34",
        "name": "Đàn Cá (Fish)",
        "icon": "🐟",
        "meaning": "Dòng tiền trôi chảy, kinh doanh buôn bán, sự dồi dào sung túc.",
    },
    {
        "num": "35",
        "name": "Mỏ Neo (Anchor)",
        "icon": "⚓",
        "meaning": "Sự ổn định lâu dài, bến đỗ bình an, kiên định không dời.",
    },
    {
        "num": "36",
        "name": "Cây Thánh Giá (Cross)",
        "icon": "✝️",
        "meaning": "Thử thách nhân quả, gánh nặng tâm lý cần vượt qua, bài học định mệnh.",
    },
)


def draw_lenormand(
    question: str = "",
    count: int = 3,
    *,
    seed: int | None = None,
) -> dict[str, Any]:
    """Draw a Lenormand spread (1..5 distinct cards; deterministic when seed is supplied)."""
    count = max(1, min(5, count))
    rng = random.Random(seed) if seed is not None else random.SystemRandom()
    chosen = rng.sample(LENORMAND_36, count)
    slots = (
        ["Quá khứ / Nguyên nhân", "Hiện tại / Tiêu điểm", "Tương lai / Lời khuyên"]
        if count == 3
        else [f"Lá {i + 1}" for i in range(count)]
    )

    cards = [
        {
            "slot": slots[i] if i < len(slots) else f"Vị trí {i + 1}",
            "number": card["num"],
            "name": card["name"],
            "icon": card["icon"],
            "meaning": card["meaning"],
        }
        for i, card in enumerate(chosen)
    ]

    summary = (
        f"Bộ 3 lá bài mở ra thông điệp: Bắt đầu từ [{chosen[0]['name']}], "
        f"tâm điểm hiện tại là [{chosen[1]['name']}], "
        f"hướng tới tương lai với [{chosen[2]['name']}]."
        if count == 3
        else "Kết quả rút bài Lenormand."
    )

    return {
        "visual_type": "lenormand",
        "question": question or "Hỏi xu hướng sự việc",
        "cards": cards,
        "summary": summary,
    }
