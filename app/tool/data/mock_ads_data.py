"""
Mock data for Relevance Search API
Contains popular car and motorcycle models in Indonesia
"""

MOCK_ADS_DATA = [
    # Cars - Toyota
    {
        "ad_id": "CAR001",
        "category": 198,  # car
        "title": "Toyota Avanza 1.3 G MT 2019 - Mobil Keluarga Terawat",
        "description": "Toyota Avanza 2019 transmisi manual, kondisi sangat terawat, interior bersih, mesin halus, cocok untuk keluarga",
        "make": "toyota",
        "model": "avanza",
        "transmission": "manual",
        "year": 2019,
        "price": 145_000_000,
        "location": "Jakarta Selatan",
        "mileage": 45000,
        "color": "Silver",
    },
    {
        "ad_id": "CAR002",
        "category": 198,
        "title": "Toyota Avanza 1.3 Veloz AT 2020 - Automatic Istimewa",
        "description": "Toyota Avanza Veloz 2020 automatic, kondisi istimewa, service record lengkap, pajak panjang",
        "make": "toyota",
        "model": "avanza",
        "transmission": "automatic",
        "year": 2020,
        "price": 175_000_000,
        "location": "Bandung",
        "mileage": 32000,
        "color": "White",
    },
    {
        "ad_id": "CAR003",
        "category": 198,
        "title": "Toyota Fortuner 2.4 VRZ AT 2018 - SUV Tangguh",
        "description": "Toyota Fortuner VRZ 2018 diesel automatic, kondisi prima, interior kulit asli, cocok untuk touring",
        "make": "toyota",
        "model": "fortuner",
        "transmission": "automatic",
        "year": 2018,
        "price": 395_000_000,
        "location": "Surabaya",
        "mileage": 68000,
        "color": "Black",
    },
    {
        "ad_id": "CAR004",
        "category": 198,
        "title": "Toyota Innova 2.0 G AT 2017 - MPV Keluarga Nyaman",
        "description": "Toyota Innova Reborn 2017 bensin automatic, AC dingin, mesin terawat, cocok untuk mudik",
        "make": "toyota",
        "model": "innova",
        "transmission": "automatic",
        "year": 2017,
        "price": 265_000_000,
        "location": "Medan",
        "mileage": 75000,
        "color": "Silver",
    },
    # Cars - Honda
    {
        "ad_id": "CAR005",
        "category": 198,
        "title": "Honda Brio 1.2 E MT 2018 - City Car Hemat BBM",
        "description": "Honda Brio 2018 manual, sangat irit BBM, kondisi terawat, cocok untuk harian di kota",
        "make": "honda",
        "model": "brio",
        "transmission": "manual",
        "year": 2018,
        "price": 135_000_000,
        "location": "Yogyakarta",
        "mileage": 52000,
        "color": "Red",
    },
    {
        "ad_id": "CAR006",
        "category": 198,
        "title": "Honda Jazz 1.5 RS CVT 2019 - Hatchback Sporty",
        "description": "Honda Jazz RS 2019 CVT, fitur lengkap, Honda Sensing, kondisi seperti baru",
        "make": "honda",
        "model": "jazz",
        "transmission": "automatic",
        "year": 2019,
        "price": 245_000_000,
        "location": "Jakarta Barat",
        "mileage": 28000,
        "color": "Orange",
    },
    {
        "ad_id": "CAR007",
        "category": 198,
        "title": "Honda CR-V 1.5 Turbo Prestige 2020 - SUV Premium",
        "description": "Honda CR-V Turbo Prestige 2020, sunroof, leather seats, Honda Sensing, kondisi istimewa",
        "make": "honda",
        "model": "cr-v",
        "transmission": "automatic",
        "year": 2020,
        "price": 485_000_000,
        "location": "Semarang",
        "mileage": 25000,
        "color": "White Pearl",
    },
    {
        "ad_id": "CAR008",
        "category": 198,
        "title": "Honda Civic 1.5 Turbo Hatchback RS 2021 - Sporty Hatchback",
        "description": "Honda Civic Hatchback RS 2021, turbo engine, sport mode, kondisi mint condition",
        "make": "honda",
        "model": "civic",
        "transmission": "automatic",
        "year": 2021,
        "price": 495_000_000,
        "location": "Jakarta Utara",
        "mileage": 15000,
        "color": "Championship White",
    },
    # Cars - Daihatsu
    {
        "ad_id": "CAR009",
        "category": 198,
        "title": "Daihatsu Xenia 1.3 R MT 2019 - MPV Ekonomis",
        "description": "Daihatsu Xenia R 2019 manual, 7 seater, hemat BBM, kondisi terawat",
        "make": "daihatsu",
        "model": "xenia",
        "transmission": "manual",
        "year": 2019,
        "price": 155_000_000,
        "location": "Malang",
        "mileage": 42000,
        "color": "Dark Grey",
    },
    {
        "ad_id": "CAR010",
        "category": 198,
        "title": "Daihatsu Ayla 1.2 R AT 2020 - LCGC Automatic",
        "description": "Daihatsu Ayla R 2020 automatic, cocok untuk pemula, parkir mudah, irit BBM",
        "make": "daihatsu",
        "model": "ayla",
        "transmission": "automatic",
        "year": 2020,
        "price": 125_000_000,
        "location": "Bekasi",
        "mileage": 35000,
        "color": "Ice Blue",
    },
    # Cars - Mitsubishi
    {
        "ad_id": "CAR011",
        "category": 198,
        "title": "Mitsubishi Pajero Sport 2.4 Dakar AT 2017 - SUV Adventure",
        "description": "Mitsubishi Pajero Sport Dakar 2017 diesel, 4WD, cocok untuk off-road, kondisi prima",
        "make": "mitsubishi",
        "model": "pajero",
        "transmission": "automatic",
        "year": 2017,
        "price": 365_000_000,
        "location": "Balikpapan",
        "mileage": 85000,
        "color": "Bronze",
    },
    {
        "ad_id": "CAR012",
        "category": 198,
        "title": "Mitsubishi Xpander 1.5 Ultimate AT 2019 - MPV Modern",
        "description": "Mitsubishi Xpander Ultimate 2019 automatic, fitur lengkap, kondisi istimewa",
        "make": "mitsubishi",
        "model": "xpander",
        "transmission": "automatic",
        "year": 2019,
        "price": 235_000_000,
        "location": "Denpasar",
        "mileage": 38000,
        "color": "Red Diamond",
    },
    # Motorcycles - Honda
    {
        "ad_id": "MOTOR001",
        "category": 199,  # motorcycle
        "title": "Honda Vario 125 eSP CBS 2020 - Matic Irit BBM",
        "description": "Honda Vario 125 2020, kondisi mulus, service rutin, surat lengkap, siap pakai",
        "make": "honda",
        "model": "vario",
        "transmission": "automatic",
        "year": 2020,
        "price": 18_500_000,
        "location": "Jakarta Timur",
        "mileage": 15000,
        "color": "Matte Black",
    },
    {
        "ad_id": "MOTOR002",
        "category": 199,
        "title": "Honda Beat Street eSP CBS 2019 - Skutik Stylish",
        "description": "Honda Beat Street 2019, desain sporty, kondisi terawat, cocok untuk anak muda",
        "make": "honda",
        "model": "beat",
        "transmission": "automatic",
        "year": 2019,
        "price": 15_200_000,
        "location": "Bandung",
        "mileage": 22000,
        "color": "Hard Rock Black",
    },
    {
        "ad_id": "MOTOR003",
        "category": 199,
        "title": "Honda Scoopy Fashion 2021 - Skutik Retro Chic",
        "description": "Honda Scoopy Fashion 2021, desain vintage, warna cantik, kondisi seperti baru",
        "make": "honda",
        "model": "scoopy",
        "transmission": "automatic",
        "year": 2021,
        "price": 19_800_000,
        "location": "Surabaya",
        "mileage": 8000,
        "color": "Stylish White",
    },
    {
        "ad_id": "MOTOR004",
        "category": 199,
        "title": "Honda PCX 150 ABS 2020 - Premium Scooter",
        "description": "Honda PCX 150 2020 dengan ABS, keyless, smart key, kondisi istimewa",
        "make": "honda",
        "model": "pcx",
        "transmission": "automatic",
        "year": 2020,
        "price": 32_500_000,
        "location": "Jakarta Selatan",
        "mileage": 12000,
        "color": "Candy Tahitian Blue",
    },
    {
        "ad_id": "MOTOR005",
        "category": 199,
        "title": "Honda CB150R StreetFire 2018 - Naked Bike Garang",
        "description": "Honda CB150R 2018, naked bike sporty, kondisi original, cocok untuk touring",
        "make": "honda",
        "model": "cb150r",
        "transmission": "manual",
        "year": 2018,
        "price": 22_000_000,
        "location": "Yogyakarta",
        "mileage": 28000,
        "color": "Racing Red",
    },
    # Motorcycles - Yamaha
    {
        "ad_id": "MOTOR006",
        "category": 199,
        "title": "Yamaha NMAX 155 Connected ABS 2020 - Smart Scooter",
        "description": "Yamaha NMAX 155 2020, fitur connected, ABS, kondisi prima, service record lengkap",
        "make": "yamaha",
        "model": "nmax",
        "transmission": "automatic",
        "year": 2020,
        "price": 28_500_000,
        "location": "Jakarta Barat",
        "mileage": 18000,
        "color": "Matte Grey",
    },
    {
        "ad_id": "MOTOR007",
        "category": 199,
        "title": "Yamaha Aerox 155 S-Version 2021 - Sport Scooter",
        "description": "Yamaha Aerox 155 2021 S-Version, desain sporty, performa tinggi, kondisi istimewa",
        "make": "yamaha",
        "model": "aerox",
        "transmission": "automatic",
        "year": 2021,
        "price": 25_800_000,
        "location": "Semarang",
        "mileage": 9000,
        "color": "Matte Black",
    },
    {
        "ad_id": "MOTOR008",
        "category": 199,
        "title": "Yamaha Mio M3 125 Blue Core 2019 - Skutik Ekonomis",
        "description": "Yamaha Mio M3 2019, blue core engine, irit BBM, kondisi terawat",
        "make": "yamaha",
        "model": "mio",
        "transmission": "automatic",
        "year": 2019,
        "price": 14_500_000,
        "location": "Medan",
        "mileage": 25000,
        "color": "Energetic Blue",
    },
    {
        "ad_id": "MOTOR009",
        "category": 199,
        "title": "Yamaha R15 V3.0 VVA 2019 - Sport Bike 150cc",
        "description": "Yamaha R15 V3 2019, full fairing, VVA engine, kondisi original, siap track day",
        "make": "yamaha",
        "model": "r15",
        "transmission": "manual",
        "year": 2019,
        "price": 31_000_000,
        "location": "Jakarta Utara",
        "mileage": 15000,
        "color": "Racing Blue",
    },
    # Motorcycles - Suzuki
    {
        "ad_id": "MOTOR010",
        "category": 199,
        "title": "Suzuki Nex II 115 FI 2020 - Skutik Entry Level",
        "description": "Suzuki Nex II 2020, fuel injection, hemat BBM, kondisi terawat",
        "make": "suzuki",
        "model": "nex",
        "transmission": "automatic",
        "year": 2020,
        "price": 13_800_000,
        "location": "Malang",
        "mileage": 20000,
        "color": "Titan Black",
    },
    {
        "ad_id": "MOTOR011",
        "category": 199,
        "title": "Suzuki Burgman 150 ABS 2019 - Maxi Scooter",
        "description": "Suzuki Burgman 150 2019 dengan ABS, desain premium, cocok untuk touring jarak jauh",
        "make": "suzuki",
        "model": "burgman",
        "transmission": "automatic",
        "year": 2019,
        "price": 26_500_000,
        "location": "Denpasar",
        "mileage": 16000,
        "color": "Pearl Glacier White",
    },
    {
        "ad_id": "MOTOR012",
        "category": 199,
        "title": "Suzuki GSX-R150 2018 - Full Fairing Sport",
        "description": "Suzuki GSX-R150 2018, full fairing sport bike, kondisi original, performa tinggi",
        "make": "suzuki",
        "model": "gsx-r150",
        "transmission": "manual",
        "year": 2018,
        "price": 28_500_000,
        "location": "Bandung",
        "mileage": 22000,
        "color": "MotoGP Edition",
    },
    # Motorcycles - Kawasaki
    {
        "ad_id": "MOTOR013",
        "category": 199,
        "title": "Kawasaki Ninja 250 FI 2017 - Sport Bike Legend",
        "description": "Kawasaki Ninja 250 2017, parallel twin engine, kondisi terawat, siap touring",
        "make": "kawasaki",
        "model": "ninja",
        "transmission": "manual",
        "year": 2017,
        "price": 42_000_000,
        "location": "Jakarta Timur",
        "mileage": 35000,
        "color": "Lime Green",
    },
    {
        "ad_id": "MOTOR014",
        "category": 199,
        "title": "Kawasaki KLX 150BF SE 2020 - Trail Adventure",
        "description": "Kawasaki KLX 150 2020 SE edition, trail bike tangguh, cocok untuk adventure",
        "make": "kawasaki",
        "model": "klx",
        "transmission": "manual",
        "year": 2020,
        "price": 35_500_000,
        "location": "Bogor",
        "mileage": 12000,
        "color": "Lime Green",
    },
]


def get_mock_ads_data():
    """Return the mock ads data"""
    return MOCK_ADS_DATA


def filter_ads_by_criteria(
    ad_id=None,
    category=None,
    title=None,
    description=None,
    make=None,
    model=None,
    transmission=None,
    year=None,
    price_min=None,
    price_max=None,
):
    """
    Filter mock ads data based on provided criteria

    Args:
        ad_id (str, optional): Filter by ad ID
        category (int, optional): Filter by category (198=car, 199=motorcycle)
        title (str, optional): Filter by title (case insensitive substring match)
        description (str, optional): Filter by description (case insensitive substring match)
        make (str, optional): Filter by make (case insensitive)
        model (str, optional): Filter by model (case insensitive)
        transmission (str, optional): Filter by transmission (case insensitive)
        year (int, optional): Filter by exact year
        price_min (int, optional): Filter by minimum price in Rupiah
        price_max (int, optional): Filter by maximum price in Rupiah

    Returns:
        list: Filtered list of ads
    """
    filtered_ads = MOCK_ADS_DATA.copy()

    if ad_id:
        filtered_ads = [
            ad for ad in filtered_ads if ad["ad_id"].lower() == ad_id.lower()
        ]

    if category:
        filtered_ads = [ad for ad in filtered_ads if ad["category"] == category]

    if title:
        filtered_ads = [
            ad for ad in filtered_ads if title.lower() in ad["title"].lower()
        ]

    if description:
        filtered_ads = [
            ad
            for ad in filtered_ads
            if description.lower() in ad["description"].lower()
        ]

    if make:
        filtered_ads = [ad for ad in filtered_ads if ad["make"].lower() == make.lower()]

    if model:
        filtered_ads = [
            ad for ad in filtered_ads if ad["model"].lower() == model.lower()
        ]

    if transmission:
        filtered_ads = [
            ad
            for ad in filtered_ads
            if ad["transmission"].lower() == transmission.lower()
        ]

    if year:
        filtered_ads = [ad for ad in filtered_ads if ad["year"] == year]

    if price_min:
        filtered_ads = [ad for ad in filtered_ads if ad["price"] >= price_min]

    if price_max:
        filtered_ads = [ad for ad in filtered_ads if ad["price"] <= price_max]

    return filtered_ads
