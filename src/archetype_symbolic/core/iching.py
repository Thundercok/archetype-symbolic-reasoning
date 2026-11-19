"""Deterministic I Ching (Kinh Dịch) symbolic engine over the 6-bit Boolean lattice Z_2^6.

All lines are ordered strictly bottom-to-top:
    index 0 -> Hào 1 (bottom)
    ...
    index 5 -> Hào 6 (top)
where 1 = Yang (solid, —) and 0 = Yin (broken, --).
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

Bit = int
TrigramBits = tuple[int, int, int]
HexagramBits = tuple[int, int, int, int, int, int]


@dataclass(frozen=True)
class Trigram:
    """One of the 8 Bát Quái trigrams with bottom-to-top 3-bit encoding."""

    bits: TrigramBits
    name: str
    symbol: str
    nature: str
    element: str
    attribute: str


# Standard bottom-to-top 3-bit encoding (line 1 = bottom, line 3 = top):
# - Càn (☰): (1, 1, 1) — tam liên
# - Đoài (☱): (1, 1, 0) — thượng khuyết (broken on top)
# - Ly (☲): (1, 0, 1) — trung hư (broken in middle)
# - Chấn (☳): (1, 0, 0) — ngưỡng bồn (solid at bottom)
# - Tốn (☴): (0, 1, 1) — hạ đoạn (broken at bottom)
# - Khảm (☵): (0, 1, 0) — trung mãn (solid in middle)
# - Cấn (☶): (0, 0, 1) — phúc uyển (solid on top)
# - Khôn (☷): (0, 0, 0) — lục đoạn
TRIGRAM_OBJECTS: dict[TrigramBits, Trigram] = {
    (1, 1, 1): Trigram((1, 1, 1), "Càn", "☰", "Trời", "Kim", "Mạnh mẽ, sáng tạo, khởi đầu"),
    (1, 1, 0): Trigram((1, 1, 0), "Đoài", "☱", "Đầm", "Kim", "Vui vẻ, hòa nhã, thu hút"),
    (1, 0, 1): Trigram((1, 0, 1), "Ly", "☲", "Lửa", "Hỏa", "Sáng suốt, văn minh, bám tựa"),
    (1, 0, 0): Trigram((1, 0, 0), "Chấn", "☳", "Sấm", "Mộc", "Hành động, chấn động, thức tỉnh"),
    (0, 1, 1): Trigram((0, 1, 1), "Tốn", "☴", "Gió", "Mộc", "Thuận phục, thấu suốt, khiêm nhu"),
    (0, 1, 0): Trigram((0, 1, 0), "Khảm", "☵", "Nước", "Thủy", "Hiểm trở, thận trọng, trí tuệ"),
    (0, 0, 1): Trigram((0, 0, 1), "Cấn", "☶", "Núi", "Thổ", "Ngăn chặn, tĩnh lặng, dừng lại"),
    (0, 0, 0): Trigram((0, 0, 0), "Khôn", "☷", "Đất", "Thổ", "Nhu thuận, bao dung, thành toàn"),
}

# Tuple view preserving legacy unpack shape (name, symbol, nature, attribute)
TRIGRAMS: dict[TrigramBits, tuple[str, str, str, str]] = {
    bits: (t.name, t.symbol, t.nature, t.attribute) for bits, t in TRIGRAM_OBJECTS.items()
}

TRIGRAM_BY_NAME: dict[str, Trigram] = {t.name: t for t in TRIGRAM_OBJECTS.values()}

# Five-Element (Ngũ Hành) directed cycles
_GENERATES: dict[str, str] = {
    "Kim": "Thủy",
    "Thủy": "Mộc",
    "Mộc": "Hỏa",
    "Hỏa": "Thổ",
    "Thổ": "Kim",
}
_OVERCOMES: dict[str, str] = {
    "Kim": "Mộc",
    "Mộc": "Thổ",
    "Thổ": "Thủy",
    "Thủy": "Hỏa",
    "Hỏa": "Kim",
}

# 64 King Wen Hexagrams in canonical order (1..64):
# (Upper Trigram, Lower Trigram) -> (Name, Summary Meaning, Concise Guidance)
HEXAGRAMS_64: dict[tuple[str, str], tuple[str, str, str]] = {
    ("Càn", "Càn"): (
        "Thuần Càn",
        "Vạn sự hanh thông, long khởi vũ vân",
        "Thời cơ lớn, giữ vững chính đạo và sự tự chủ.",
    ),
    ("Khôn", "Khôn"): (
        "Thuần Khôn",
        "Đức dày chở vật, nhu thuận đại cát",
        "Lắng nghe, kiên nhẫn tích lũy, chớ vội đứng đầu.",
    ),
    ("Khảm", "Chấn"): (
        "Thủy Lôi Truân",
        "Vạn sự khởi đầu nan, mầm non đội đất",
        "Gặp khó bước đầu là tự nhiên, cần định tâm và tìm trợ lực.",
    ),
    ("Cấn", "Khảm"): (
        "Sơn Thủy Mông",
        "Khai mở mông muội, học hỏi tiến bước",
        "Chân thành cầu học, chớ kiêu căng tự mãn.",
    ),
    ("Khảm", "Càn"): (
        "Thủy Thiên Nhu",
        "Chờ thời hành động, mây tụ thành mưa",
        "Kiên nhẫn chờ thời điểm chín muồi, ăn uống vui tươi.",
    ),
    ("Càn", "Khảm"): (
        "Thiên Thủy Tụng",
        "Bất hòa tranh chấp, thận trọng lùi bước",
        "Tránh kiện tụng tranh chấp, dừng lại đúng lúc thì an.",
    ),
    ("Khôn", "Khảm"): (
        "Địa Thủy Sư",
        "Hành quân dụng chúng, kỷ luật nghiêm minh",
        "Cần kỷ luật thép và người lãnh đạo công tâm.",
    ),
    ("Khảm", "Khôn"): (
        "Thủy Địa Tỷ",
        "Gắn kết thân thiện, tìm người đồng chí",
        "Tìm kiếm sự liên minh, giúp đỡ chân thành.",
    ),
    ("Tốn", "Càn"): (
        "Phong Thiên Tiểu Súc",
        "Tích lũy nhỏ bé, gió mây chưa mưa",
        "Tích lũy từng bước nhỏ, chớ vội vàng mưu cầu đại sự.",
    ),
    ("Càn", "Đoài"): (
        "Thiên Trạch Lý",
        "Dẫm đuôi cọp, cẩn trọng điềm tĩnh",
        "Đối diện thế khó bằng thái độ lễ độ, hòa nhã.",
    ),
    ("Khôn", "Càn"): (
        "Địa Thiên Thái",
        "Trời đất giao hòa, thái bình thịnh vượng",
        "Vận khí hanh thông, nắm bắt cơ hội để kiến tạo.",
    ),
    ("Càn", "Khôn"): (
        "Thiên Địa Bĩ",
        "Âm dương bế tắc, thời thế đảo điên",
        "Ẩn nhẫn giữ mình, không thỏa hiệp với cái xấu.",
    ),
    ("Càn", "Ly"): (
        "Thiên Hỏa Đồng Nhân",
        "Đồng lòng hiệp lực, kết giao bạn lành",
        "Làm việc nhóm, mở rộng kết nối với cộng đồng.",
    ),
    ("Ly", "Càn"): (
        "Hỏa Thiên Đại Hữu",
        "Ánh dương rực rỡ, của cải dồi dào",
        "Chia sẻ tài nguyên, khiêm tốn khi đang ở đỉnh cao.",
    ),
    ("Khôn", "Cấn"): (
        "Địa Sơn Khiêm",
        "Núi giấu trong đất, khiêm tốn sinh phúc",
        "Càng giỏi càng khiêm nhường thì vạn sự êm đẹp.",
    ),
    ("Chấn", "Khôn"): (
        "Lôi Địa Dự",
        "Niềm vui dâng trào, chuẩn bị kỹ lưỡng",
        "Tận hưởng niềm vui nhưng luôn phòng ngừa rủi ro.",
    ),
    ("Đoài", "Chấn"): (
        "Trạch Lôi Tùy",
        "Thuận theo thời thế, tùy cơ ứng biến",
        "Lắng nghe dòng chảy tự nhiên, chớ cưỡng cầu.",
    ),
    ("Cấn", "Tốn"): (
        "Sơn Phong Cổ",
        "Chỉnh đốn sửa sai, làm mới việc cũ",
        "Thời điểm tuyệt vời để tái cấu trúc và sửa lỗi quá khứ.",
    ),
    ("Khôn", "Đoài"): (
        "Địa Trạch Lâm",
        "Thế lớn đang tới, mùa xuân đâm chồi",
        "Năng lượng dồi dào, hành động ngay kẻo lỡ thời điểm.",
    ),
    ("Tốn", "Khôn"): (
        "Phong Địa Quan",
        "Quan sát toàn cảnh, thấu hiểu chiều sâu",
        "Lùi lại một bước nhìn bức tranh lớn trước khi quyết định.",
    ),
    ("Ly", "Chấn"): (
        "Hỏa Lôi Phệ Hạp",
        "Cắn đứt trở ngại, thực thi pháp luật",
        "Xử lý dứt điểm điểm nghẽn, không chần chừ do dự.",
    ),
    ("Cấn", "Ly"): (
        "Sơn Hỏa Bí",
        "Trang hoàng thanh nhã, giản dị chân phương",
        "Làm đẹp vẻ ngoài nhưng cốt lõi vẫn phải thực chất.",
    ),
    ("Cấn", "Khôn"): (
        "Sơn Địa Bác",
        "Mòn mỏi sụt lở, thời vận suy vi",
        "Giữ sức, không manh động, chờ đợi chu kỳ mới.",
    ),
    ("Khôn", "Chấn"): (
        "Địa Lôi Phục",
        "Dương khí trở lại, khởi đầu chu kỳ mới",
        "Tia sáng hy vọng xuất hiện, bắt đầu gieo hạt giống mới.",
    ),
    ("Càn", "Chấn"): (
        "Thiên Lôi Vô Vọng",
        "Chân thật tự nhiên, không vọng tưởng",
        "Làm đúng phận sự, chớ toan tính mưu mẹo.",
    ),
    ("Cấn", "Càn"): (
        "Sơn Thiên Đại Súc",
        "Đức hạnh tích chứa, chuẩn bị nghiệp lớn",
        "Học tập nâng cao năng lực, tích lũy kiến thức sâu sắc.",
    ),
    ("Cấn", "Chấn"): (
        "Sơn Lôi Di",
        "Nuôi dưỡng thân tâm, chọn lời cẩn thận",
        "Chú ý lời ăn tiếng nói và việc chăm sóc sức khỏe.",
    ),
    ("Đoài", "Tốn"): (
        "Trạch Phong Đại Quá",
        "Cột nhà oằn cong, gánh nặng quá sức",
        "Giảm tải ngay lập tức, cắt bỏ những thứ thừa thãi.",
    ),
    ("Khảm", "Khảm"): (
        "Thuần Khảm",
        "Hiểm nguy trùng điệp, giữ vững lòng tin",
        "Dũng cảm đối mặt nghịch cảnh, giữ tâm thanh tịnh.",
    ),
    ("Ly", "Ly"): (
        "Thuần Ly",
        "Lửa sáng bám củi, trí tuệ soi đường",
        "Tìm điểm tựa vững chắc, bồi đắp kiến thức chuyên môn.",
    ),
    ("Đoài", "Cấn"): (
        "Trạch Sơn Hàm",
        "Cảm ứng chân thành, tình duyên gắn kết",
        "Lắng nghe trực giác và rung cảm chân thật của trái tim.",
    ),
    ("Chấn", "Tốn"): (
        "Lôi Phong Hằng",
        "Bền vững dài lâu, kiên định mục tiêu",
        "Kiên trì với con đường đã chọn, chớ đứng núi này trông núi nọ.",
    ),
    ("Càn", "Cấn"): (
        "Thiên Sơn Độn",
        "Rút lui chiến lược, bảo toàn lực lượng",
        "Biết lùi đúng lúc là kẻ thông minh, không cố chấp.",
    ),
    ("Chấn", "Càn"): (
        "Lôi Thiên Đại Tráng",
        "Sức mạnh tráng kiện, cẩn thận húc dậu",
        "Có thế mạnh nhưng chớ hung hăng, cần mềm mỏng.",
    ),
    ("Ly", "Khôn"): (
        "Hỏa Địa Tấn",
        "Mặt trời lên cao, thăng tiến rộng mở",
        "Tỏa sáng năng lực, khẳng định giá trị bản thân.",
    ),
    ("Khôn", "Ly"): (
        "Địa Hỏa Minh Di",
        "Ánh sáng vùi trong đất, giấu mình chờ thời",
        "Ẩn mình kín đáo khi xung quanh còn nhiều đố kỵ.",
    ),
    ("Tốn", "Ly"): (
        "Phong Hỏa Gia Nhân",
        "Gia đạo yên vui, trong ấm ngoài êm",
        "Tập trung vun vén nội bộ, gốc rễ gia đình, đội nhóm.",
    ),
    ("Ly", "Đoài"): (
        "Hỏa Trạch Khuê",
        "Bất đồng chia rẽ, hướng đến cái chung",
        "Chấp nhận sự khác biệt, tìm kiếm điểm tương đồng nhỏ.",
    ),
    ("Khảm", "Cấn"): (
        "Thủy Sơn Kiển",
        "Núi cao vực sâu, dừng lại xem xét",
        "Đường cùng chớ bước, quay đầu xem lại phương pháp.",
    ),
    ("Chấn", "Khảm"): (
        "Lôi Thủy Giải",
        "Sấm tan mưa rào, nút thắt cởi mở",
        "Mọi vướng mắc bắt đầu được giải tỏa, hành động dứt khoát.",
    ),
    ("Cấn", "Đoài"): (
        "Sơn Trạch Tổn",
        "Bớt giận kiềm dục, hy sinh trước mắt",
        "Bớt lợi ích vị kỷ cá nhân để đổi lấy thành công lâu dài.",
    ),
    ("Tốn", "Chấn"): (
        "Phong Lôi Ích",
        "Gió sấm trợ lực, thêm tài tăng tiến",
        "Thấy điều tốt thì làm theo, thấy lỗi thì sửa ngay.",
    ),
    ("Đoài", "Càn"): (
        "Trạch Thiên Quải",
        "Quyết đoán dứt khoát, vạch trần cái xấu",
        "Dứt khoát với thói quen xấu, không mập mờ.",
    ),
    ("Càn", "Tốn"): (
        "Thiên Phong Cấu",
        "Tình cờ gặp gỡ, cẩn trọng cám dỗ",
        "Đề phòng những mối quan hệ bất ngờ thiếu minh bạch.",
    ),
    ("Đoài", "Khôn"): (
        "Trạch Địa Tụy",
        "Tụ hội đông đảo, đoàn kết phát triển",
        "Hội tụ tài năng, chung tay vì mục tiêu lớn.",
    ),
    ("Khôn", "Tốn"): (
        "Địa Phong Thăng",
        "Cây mọc vươn cao, tiến bước từ từ",
        "Từng bước thăng tiến đều đặn, dựa vào người có tâm.",
    ),
    ("Đoài", "Khảm"): (
        "Trạch Thủy Khốn",
        "Nước cạn đầm khô, rèn luyện chí khí",
        "Thời điểm thử thách bản lĩnh, lời nói ít người nghe nên hãy im lặng hành động.",
    ),
    ("Khảm", "Tốn"): (
        "Thủy Phong Tỉnh",
        "Giếng nước nuôi dân, nguồn lực vô tận",
        "Bồi đắp nội lực bản thân, nguồn nước trong lành không bao giờ cạn.",
    ),
    ("Đoài", "Ly"): (
        "Trạch Hỏa Cách",
        "Cải cách đổi mới, bỏ cũ lấy mới",
        "Thay đổi tư duy và công cụ cũ, cách tân mang lại vận hội mới.",
    ),
    ("Ly", "Tốn"): (
        "Hỏa Phong Đỉnh",
        "Đúc đỉnh luyện đan, ổn định ngôi vị",
        "Vận thế vững vàng, tài đức tương xứng vị trí.",
    ),
    ("Chấn", "Chấn"): (
        "Thuần Chấn",
        "Sấm vang trăm dặm, giật mình tỉnh ngộ",
        "Tiếng sấm cảnh tỉnh, sửa mình cẩn trọng thì sau bình an.",
    ),
    ("Cấn", "Cấn"): (
        "Thuần Cấn",
        "Núi đứng im lìm, định tâm bất động",
        "Dừng lại mọi suy nghĩ lan man, tĩnh tâm thiền định.",
    ),
    ("Tốn", "Cấn"): (
        "Phong Sơn Tiệm",
        "Tiến bước tuần tự, chim nhạn bay về",
        "Phát triển từ từ, việc gì vội vàng đều dễ hỏng.",
    ),
    ("Chấn", "Đoài"): (
        "Lôi Trạch Quy Muội",
        "Lệch lạc chuẩn mực, chớ nên tiến hành",
        "Chưa đúng thời điểm kết duyên hay ký kết thỏa thuận.",
    ),
    ("Chấn", "Ly"): (
        "Lôi Hỏa Phong",
        "Thịnh vượng sung túc, mặt trời chính ngọ",
        "Đang ở thời cực thịnh, chuẩn bị trước cho chu kỳ đi xuống.",
    ),
    ("Ly", "Cấn"): (
        "Hỏa Sơn Lữ",
        "Khách lạ lữ thứ, cẩn trọng khiêm nhường",
        "Đang ở môi trường mới hoặc đi xa, hòa nhã để tránh rắc rối.",
    ),
    ("Tốn", "Tốn"): (
        "Thuần Tốn",
        "Gió thổi luồn sâu, mềm mại thích ứng",
        "Khéo léo thích nghi như gió thoảng, uốn nắn theo thời cuộc.",
    ),
    ("Đoài", "Đoài"): (
        "Thuần Đoài",
        "Đầm nước tràn trề, cùng nhau học hỏi",
        "Niềm vui sẻ chia, gặp gỡ bạn hiền đàm đạo.",
    ),
    ("Tốn", "Khảm"): (
        "Phong Thủy Hoán",
        "Gió thổi tan mây, giải tỏa ngăn cách",
        "Xóa bỏ hiểu lầm, hòa tan định kiến cũ.",
    ),
    ("Khảm", "Đoài"): (
        "Thủy Trạch Tiết",
        "Chừng mực tiết chế, giữ gìn khuôn phép",
        "Chi tiêu và sinh hoạt có chừng mực, chớ quá trớn.",
    ),
    ("Tốn", "Đoài"): (
        "Phong Trạch Trung Phu",
        "Chân thành tin cậy, trứng nở thành con",
        "Lấy chữ Tín làm đầu, chân thành cảm hóa người khác.",
    ),
    ("Chấn", "Cấn"): (
        "Lôi Sơn Tiểu Quá",
        "Vượt mức chút ít, cẩn trọng chi tiết",
        "Nên giữ việc nhỏ, tránh mưu tính việc quá tầm tay.",
    ),
    ("Khảm", "Ly"): (
        "Thủy Hỏa Ký Tế",
        "Việc đã hoàn thành, cẩn thận giữ gìn",
        "Mục tiêu đã đạt, giữ gìn thành quả quan trọng hơn bành trướng.",
    ),
    ("Ly", "Khảm"): (
        "Hỏa Thủy Vị Tế",
        "Chưa xong việc, cáo nhỏ qua sông",
        "Chu kỳ cũ kết thúc, chu kỳ mới mở ra, tiếp tục kiên trì.",
    ),
}

KING_WEN_INDEX: dict[tuple[str, str], int] = {
    pair: idx for idx, pair in enumerate(HEXAGRAMS_64.keys(), start=1)
}


def validate_bits(lines: list[int] | tuple[int, ...]) -> HexagramBits:
    """Validate and normalize a 6-bit bottom-to-top hexagram vector."""
    if len(lines) != 6 or any(b not in (0, 1) for b in lines):
        raise ValueError("Hexagram must be a sequence of 6 bits (0 or 1), bottom-to-top.")
    return (
        int(lines[0]),
        int(lines[1]),
        int(lines[2]),
        int(lines[3]),
        int(lines[4]),
        int(lines[5]),
    )


def element_relation(source: str, target: str) -> str:
    """Return the Wu Xing (Ngũ Hành) relation from source element to target element."""
    if source == target:
        return "Tỷ Hòa (cùng hành)"
    if _GENERATES.get(source) == target:
        return f"Tương Sinh ({source} sinh {target})"
    if _GENERATES.get(target) == source:
        return f"Được Sinh ({target} sinh {source})"
    if _OVERCOMES.get(source) == target:
        return f"Tương Khắc ({source} khắc {target})"
    if _OVERCOMES.get(target) == source:
        return f"Bị Khắc ({target} khắc {source})"
    raise ValueError(f"Unknown Wu Xing element pair: {source!r}, {target!r}")


def hexagram_from_bits(lines: list[int] | tuple[int, ...]) -> dict[str, Any]:
    """Deterministically resolve a 6-bit bottom-to-top vector into its canonical hexagram state."""
    bits = validate_bits(lines)
    lower = TRIGRAM_OBJECTS[(bits[0], bits[1], bits[2])]
    upper = TRIGRAM_OBJECTS[(bits[3], bits[4], bits[5])]
    key = (upper.name, lower.name)
    name, meaning, advice = HEXAGRAMS_64[key]
    return {
        "king_wen_number": KING_WEN_INDEX[key],
        "name": name,
        "lines": list(bits),
        "upper": upper.name,
        "lower": lower.name,
        "upper_trigram": f"{upper.name} ({upper.nature} {upper.symbol})",
        "lower_trigram": f"{lower.name} ({lower.nature} {lower.symbol})",
        "upper_element": upper.element,
        "lower_element": lower.element,
        "element_relation": element_relation(upper.element, lower.element),
        "meaning": meaning,
        "advice": advice,
    }


def nuclear_bits(lines: list[int] | tuple[int, ...]) -> HexagramBits:
    """Compute Hỗ Quái (nuclear hexagram): lines [2,3,4] lower, [3,4,5] upper (1-indexed)."""
    b = validate_bits(lines)
    return (b[1], b[2], b[3], b[2], b[3], b[4])


def opposite_bits(lines: list[int] | tuple[int, ...]) -> HexagramBits:
    """Compute Thác Quái (opposite / bitwise complement): flip every line."""
    b = validate_bits(lines)
    return (1 - b[0], 1 - b[1], 1 - b[2], 1 - b[3], 1 - b[4], 1 - b[5])


def inverted_bits(lines: list[int] | tuple[int, ...]) -> HexagramBits:
    """Compute Tổng Quái (inverted / upside-down): reverse line order."""
    b = validate_bits(lines)
    return (b[5], b[4], b[3], b[2], b[1], b[0])


def transform_bits(
    lines: list[int] | tuple[int, ...],
    changing_lines: list[int],
) -> HexagramBits:
    """Compute Biến Quái (transformed hexagram) by flipping 1-indexed changing lines."""
    b = list(validate_bits(lines))
    seen: set[int] = set()
    for pos in changing_lines:
        if pos not in (1, 2, 3, 4, 5, 6):
            raise ValueError(f"Changing line index must be in 1..6, got {pos!r}.")
        if pos in seen:
            raise ValueError(f"Duplicate changing line index: {pos}.")
        seen.add(pos)
        b[pos - 1] = 1 - b[pos - 1]
    return validate_bits(b)


def analyze_hexagram(
    lines: list[int] | tuple[int, ...],
    changing_lines: list[int] | None = None,
    question: str = "",
) -> dict[str, Any]:
    """Produce a complete deterministic I Ching state & transformation analysis."""
    bits = validate_bits(lines)
    changes = sorted(changing_lines or [])
    primary = hexagram_from_bits(bits)
    nuclear = hexagram_from_bits(nuclear_bits(bits))
    opposite = hexagram_from_bits(opposite_bits(bits))
    inverted = hexagram_from_bits(inverted_bits(bits))

    transformed_card: dict[str, Any] | None = None
    if changes:
        t_info = hexagram_from_bits(transform_bits(bits, changes))
        transformed_card = {
            "king_wen_number": t_info["king_wen_number"],
            "name": t_info["name"],
            "upper": t_info["upper"],
            "lower": t_info["lower"],
            "upper_element": t_info["upper_element"],
            "lower_element": t_info["lower_element"],
            "element_relation": t_info["element_relation"],
            "meaning": t_info["meaning"],
            "lines": t_info["lines"],
        }

    return {
        "visual_type": "iching",
        "question": question or "Hỏi vận thế tổng quan",
        "king_wen_number": primary["king_wen_number"],
        "hexagram_name": primary["name"],
        "upper_trigram": primary["upper_trigram"],
        "lower_trigram": primary["lower_trigram"],
        "upper_element": primary["upper_element"],
        "lower_element": primary["lower_element"],
        "element_relation": primary["element_relation"],
        "lines": primary["lines"],
        "changing_lines": changes,
        "meaning": primary["meaning"],
        "advice": primary["advice"],
        "transformed": transformed_card,
        "nuclear": {
            "king_wen_number": nuclear["king_wen_number"],
            "name": nuclear["name"],
            "lines": nuclear["lines"],
        },
        "opposite": {
            "king_wen_number": opposite["king_wen_number"],
            "name": opposite["name"],
            "lines": opposite["lines"],
        },
        "inverted": {
            "king_wen_number": inverted["king_wen_number"],
            "name": inverted["name"],
            "lines": inverted["lines"],
        },
    }


def cast_iching(question: str = "", *, seed: int | None = None) -> dict[str, Any]:
    """Cast an I Ching hexagram via the 3-coin method (deterministic when seed is supplied)."""
    rng = random.Random(seed) if seed is not None else random.SystemRandom()
    lines_binary: list[int] = []
    changing_lines: list[int] = []
    raw_lines: list[int] = []

    for i in range(6):
        total = sum(rng.choice((2, 3)) for _ in range(3))
        raw_lines.append(total)
        is_yang = 1 if total in (7, 9) else 0
        lines_binary.append(is_yang)
        if total in (6, 9):
            changing_lines.append(i + 1)

    result = analyze_hexagram(lines_binary, changing_lines=changing_lines, question=question)
    result["raw_coin_sums"] = raw_lines
    return result
