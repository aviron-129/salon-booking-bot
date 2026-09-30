from dataclasses import dataclass
from datetime import time


@dataclass(frozen=True)
class Category:
    id: str
    ru: str
    en: str
    emoji: str


@dataclass(frozen=True)
class Service:
    id: int
    category: str
    ru: str
    en: str
    price: int
    minutes: int


@dataclass(frozen=True)
class Master:
    id: int
    ru: str
    en: str
    about_ru: str
    about_en: str
    categories: tuple[str, ...]
    weekly_off: tuple[int, ...]  # 0 = Monday


SALON = {
    "name": "Lavanda Beauty",
    "address_ru": "Ташкент, ул. Шота Руставели, 12 (демо-адрес)",
    "address_en": "12 Shota Rustaveli St, Tashkent (demo address)",
    "phone": "+998 90 000-00-00",
    "lat": 41.2885,
    "lon": 69.2725,
    "opens": time(10, 0),
    "closes": time(20, 0),
    "currency_ru": "сум",
    "currency_en": "UZS",
}

SLOT_STEP_MIN = 30
BOOKING_DAYS_AHEAD = 14

CATEGORIES = [
    Category("hair", "Стрижки", "Haircuts", "✂️"),
    Category("color", "Окрашивание", "Coloring", "🎨"),
    Category("style", "Укладки", "Styling", "💫"),
    Category("barber", "Барбер", "Barber", "🧔"),
    Category("nails", "Маникюр и педикюр", "Nails", "💅"),
]

SERVICES = [
    Service(1, "hair", "Женская стрижка", "Women's haircut", 150_000, 60),
    Service(2, "hair", "Стрижка чёлки", "Fringe trim", 50_000, 30),
    Service(3, "hair", "Детская стрижка", "Kids' haircut", 80_000, 30),
    Service(4, "color", "Окрашивание в один тон", "Single-tone color", 350_000, 120),
    Service(5, "color", "Мелирование", "Highlights", 450_000, 150),
    Service(6, "color", "Тонирование", "Toning", 250_000, 90),
    Service(7, "style", "Укладка", "Blow-dry styling", 120_000, 60),
    Service(8, "style", "Вечерняя причёска", "Evening updo", 300_000, 90),
    Service(9, "barber", "Мужская стрижка", "Men's haircut", 100_000, 60),
    Service(10, "barber", "Стрижка + борода", "Haircut + beard", 150_000, 90),
    Service(11, "barber", "Оформление бороды", "Beard trim", 60_000, 30),
    Service(12, "nails", "Маникюр с покрытием", "Gel manicure", 150_000, 90),
    Service(13, "nails", "Педикюр", "Pedicure", 180_000, 90),
]

MASTERS = [
    Master(1, "Дильноза", "Dilnoza", "Топ-стилист, окрашивание и сложные стрижки",
           "Top stylist, coloring and complex cuts", ("hair", "color", "style"), (0,)),
    Master(2, "Анна", "Anna", "Стрижки и вечерние причёски", "Haircuts and evening styles",
           ("hair", "style"), (2,)),
    Master(3, "Тимур", "Timur", "Барбер: мужские стрижки и борода", "Barber: men's cuts and beards",
           ("barber",), (6,)),
    Master(4, "Малика", "Malika", "Маникюр и педикюр", "Manicure and pedicure", ("nails",), (1,)),
]

SERVICE_BY_ID = {s.id: s for s in SERVICES}
MASTER_BY_ID = {m.id: m for m in MASTERS}
CATEGORY_BY_ID = {c.id: c for c in CATEGORIES}


def masters_for(service: Service) -> list[Master]:
    return [m for m in MASTERS if service.category in m.categories]


def name(obj, lang: str) -> str:
    return getattr(obj, lang if lang in ("ru", "en") else "ru")
