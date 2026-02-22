# -*- coding: utf-8 -*-
"""
Country codes, names and flags mapping
"""

COUNTRY_DATA = {
    '1': ('USA/Canada', '🇺🇸', '🇨🇦'),
    '7': ('Russia/Kazakhstan', '🇷🇺', '🇰🇿'),
    '20': ('Egypt', '🇪🇬'),
    '27': ('South Africa', '🇿🇦'),
    '30': ('Greece', '🇬🇷'),
    '31': ('Netherlands', '🇳🇱'),
    '32': ('Belgium', '🇧🇪'),
    '33': ('France', '🇫🇷'),
    '34': ('Spain', '🇪🇸'),
    '36': ('Hungary', '🇭🇺'),
    '39': ('Italy', '🇮🇹'),
    '40': ('Romania', '🇷🇴'),
    '41': ('Switzerland', '🇨🇭'),
    '43': ('Austria', '🇦🇹'),
    '44': ('United Kingdom', '🇬🇧'),
    '45': ('Denmark', '🇩🇰'),
    '46': ('Sweden', '🇸🇪'),
    '47': ('Norway', '🇳🇴'),
    '48': ('Poland', '🇵🇱'),
    '49': ('Germany', '🇩🇪'),
    '51': ('Peru', '🇵🇪'),
    '52': ('Mexico', '🇲🇽'),
    '53': ('Cuba', '🇨🇺'),
    '54': ('Argentina', '🇦🇷'),
    '55': ('Brazil', '🇧🇷'),
    '56': ('Chile', '🇨🇱'),
    '57': ('Colombia', '🇨🇴'),
    '58': ('Venezuela', '🇻🇪'),
    '60': ('Malaysia', '🇲🇾'),
    '61': ('Australia', '🇦🇺'),
    '62': ('Indonesia', '🇮🇩'),
    '63': ('Philippines', '🇵🇭'),
    '64': ('New Zealand', '🇳🇿'),
    '65': ('Singapore', '🇸🇬'),
    '66': ('Thailand', '🇹🇭'),
    '81': ('Japan', '🇯🇵'),
    '82': ('South Korea', '🇰🇷'),
    '84': ('Vietnam', '🇻🇳'),
    '86': ('China', '🇨🇳'),
    '90': ('Turkey', '🇹🇷'),
    '91': ('India', '🇮🇳'),
    '92': ('Pakistan', '🇵🇰'),
    '93': ('Afghanistan', '🇦🇫'),
    '94': ('Sri Lanka', '🇱🇰'),
    '95': ('Myanmar', '🇲🇲'),
    '98': ('Iran', '🇮🇷'),
    '211': ('South Sudan', '🇸🇸'),
    '212': ('Morocco', '🇲🇦'),
    '213': ('Algeria', '🇩🇿'),
    '216': ('Tunisia', '🇹🇳'),
    '218': ('Libya', '🇱🇾'),
    '220': ('Gambia', '🇬🇲'),
    '221': ('Senegal', '🇸🇳'),
    '222': ('Mauritania', '🇲🇷'),
    '223': ('Mali', '🇲🇱'),
    '224': ('Guinea', '🇬🇳'),
    '225': ("Côte d'Ivoire", '🇨🇮'),
    '226': ('Burkina Faso', '🇧🇫'),
    '227': ('Niger', '🇳🇪'),
    '228': ('Togo', '🇹🇬'),
    '229': ('Benin', '🇧🇯'),
    '230': ('Mauritius', '🇲🇺'),
    '231': ('Liberia', '🇱🇷'),
    '232': ('Sierra Leone', '🇸🇱'),
    '233': ('Ghana', '🇬🇭'),
    '234': ('Nigeria', '🇳🇬'),
    '235': ('Chad', '🇹🇩'),
    '236': ('Central African Republic', '🇨🇫'),
    '237': ('Cameroon', '🇨🇲'),
    '238': ('Cape Verde', '🇨🇻'),
    '239': ('Sao Tome and Principe', '🇸🇹'),
    '240': ('Equatorial Guinea', '🇬🇶'),
    '241': ('Gabon', '🇬🇦'),
    '242': ('Congo', '🇨🇬'),
    '243': ('DR Congo', '🇨🇩'),
    '244': ('Angola', '🇦🇴'),
    '245': ('Guinea-Bissau', '🇬🇼'),
    '248': ('Seychelles', '🇸🇨'),
    '249': ('Sudan', '🇸🇩'),
    '250': ('Rwanda', '🇷🇼'),
    '251': ('Ethiopia', '🇪🇹'),
    '252': ('Somalia', '🇸🇴'),
    '253': ('Djibouti', '🇩🇯'),
    '254': ('Kenya', '🇰🇪'),
    '255': ('Tanzania', '🇹🇿'),
    '256': ('Uganda', '🇺🇬'),
    '257': ('Burundi', '🇧🇮'),
    '258': ('Mozambique', '🇲🇿'),
    '260': ('Zambia', '🇿🇲'),
    '261': ('Madagascar', '🇲🇬'),
    '263': ('Zimbabwe', '🇿🇼'),
    '264': ('Namibia', '🇳🇦'),
    '265': ('Malawi', '🇲🇼'),
    '266': ('Lesotho', '🇱🇸'),
    '267': ('Botswana', '🇧🇼'),
    '268': ('Eswatini', '🇸🇿'),
    '269': ('Comoros', '🇰🇲'),
    '290': ('Saint Helena', '🇸🇭'),
    '291': ('Eritrea', '🇪🇷'),
    '297': ('Aruba', '🇦🇼'),
    '298': ('Faroe Islands', '🇫🇴'),
    '299': ('Greenland', '🇬🇱'),
    '350': ('Gibraltar', '🇬🇮'),
    '351': ('Portugal', '🇵🇹'),
    '352': ('Luxembourg', '🇱🇺'),
    '353': ('Ireland', '🇮🇪'),
    '354': ('Iceland', '🇮🇸'),
    '355': ('Albania', '🇦🇱'),
    '356': ('Malta', '🇲🇹'),
    '357': ('Cyprus', '🇨🇾'),
    '358': ('Finland', '🇫🇮'),
    '359': ('Bulgaria', '🇧🇬'),
    '370': ('Lithuania', '🇱🇹'),
    '371': ('Latvia', '🇱🇻'),
    '372': ('Estonia', '🇪🇪'),
    '373': ('Moldova', '🇲🇩'),
    '374': ('Armenia', '🇦🇲'),
    '375': ('Belarus', '🇧🇾'),
    '376': ('Andorra', '🇦🇩'),
    '377': ('Monaco', '🇲🇨'),
    '378': ('San Marino', '🇸🇲'),
    '380': ('Ukraine', '🇺🇦'),
    '381': ('Serbia', '🇷🇸'),
    '382': ('Montenegro', '🇲🇪'),
    '385': ('Croatia', '🇭🇷'),
    '386': ('Slovenia', '🇸🇮'),
    '387': ('Bosnia and Herzegovina', '🇧🇦'),
    '389': ('North Macedonia', '🇲🇰'),
    '420': ('Czech Republic', '🇨🇿'),
    '421': ('Slovakia', '🇸🇰'),
    '423': ('Liechtenstein', '🇱🇮'),
    '501': ('Belize', '🇧🇿'),
    '502': ('Guatemala', '🇬🇹'),
    '503': ('El Salvador', '🇸🇻'),
    '504': ('Honduras', '🇭🇳'),
    '505': ('Nicaragua', '🇳🇮'),
    '506': ('Costa Rica', '🇨🇷'),
    '507': ('Panama', '🇵🇦'),
    '509': ('Haiti', '🇭🇹'),
    '590': ('Guadeloupe', '🇬🇵'),
    '591': ('Bolivia', '🇧🇴'),
    '592': ('Guyana', '🇬🇾'),
    '593': ('Ecuador', '🇪🇨'),
    '595': ('Paraguay', '🇵🇾'),
    '597': ('Suriname', '🇸🇷'),
    '598': ('Uruguay', '🇺🇾'),
    '673': ('Brunei', '🇧🇳'),
    '675': ('Papua New Guinea', '🇵🇬'),
    '676': ('Tonga', '🇹🇴'),
    '677': ('Solomon Islands', '🇸🇧'),
    '678': ('Vanuatu', '🇻🇺'),
    '679': ('Fiji', '🇫🇯'),
    '685': ('Samoa', '🇼🇸'),
    '689': ('French Polynesia', '🇵🇫'),
    '852': ('Hong Kong', '🇭🇰'),
    '853': ('Macau', '🇲🇴'),
    '855': ('Cambodia', '🇰🇭'),
    '856': ('Laos', '🇱🇦'),
    '880': ('Bangladesh', '🇧🇩'),
    '886': ('Taiwan', '🇹🇼'),
    '960': ('Maldives', '🇲🇻'),
    '961': ('Lebanon', '🇱🇧'),
    '962': ('Jordan', '🇯🇴'),
    '963': ('Syria', '🇸🇾'),
    '964': ('Iraq', '🇮🇶'),
    '965': ('Kuwait', '🇰🇼'),
    '966': ('Saudi Arabia', '🇸🇦'),
    '967': ('Yemen', '🇾🇪'),
    '968': ('Oman', '🇴🇲'),
    '970': ('Palestine', '🇵🇸'),
    '971': ('United Arab Emirates', '🇦🇪'),
    '972': ('Israel', '🇮🇱'),
    '973': ('Bahrain', '🇧🇭'),
    '974': ('Qatar', '🇶🇦'),
    '975': ('Bhutan', '🇧🇹'),
    '976': ('Mongolia', '🇲🇳'),
    '977': ('Nepal', '🇳🇵'),
    '992': ('Tajikistan', '🇹🇯'),
    '993': ('Turkmenistan', '🇹🇲'),
    '994': ('Azerbaijan', '🇦🇿'),
    '995': ('Georgia', '🇬🇪'),
    '996': ('Kyrgyzstan', '🇰🇬'),
    '998': ('Uzbekistan', '🇺🇿'),
}

# Name → flag quick lookup (for all countries in COUNTRY_DATA)
_NAME_TO_FLAG = {}
for _code, _data in COUNTRY_DATA.items():
    _name = _data[0].upper()
    _flag = _data[1]
    _NAME_TO_FLAG[_name] = _flag
    # Also map individual names in combined entries like "USA/Canada"
    for part in _name.split('/'):
        _NAME_TO_FLAG[part.strip()] = _flag


def get_country_flag(country_name: str) -> str:
    """
    Get flag emoji for a country name.
    Tries name-based lookup first, then phone-number prefix lookup.
    """
    country_upper = country_name.upper().strip()

    # 1. Direct name match
    if country_upper in _NAME_TO_FLAG:
        return _NAME_TO_FLAG[country_upper]

    # 2. Partial name match
    for name, flag in _NAME_TO_FLAG.items():
        if country_upper in name or name in country_upper:
            return flag

    # 3. If the input looks like a phone number, detect by prefix
    digits = ''.join(filter(str.isdigit, country_name))
    if digits:
        flag = get_flag_by_phone(digits)
        if flag != '🏴‍☠️':
            return flag

    return '🏴‍☠️'  # Default pirate flag


def get_flag_by_phone(phone_number: str) -> str:
    """
    Detect country flag from a phone number by matching dial code prefix.
    Tries longest prefix first (3 digits → 2 → 1).
    """
    # Remove leading + or 00
    number = phone_number.lstrip('+').lstrip('0')

    for length in (3, 2, 1):
        prefix = number[:length]
        if prefix in COUNTRY_DATA:
            data = COUNTRY_DATA[prefix]
            return data[1]  # Return first flag

    return '🏴‍☠️'


def get_country_by_phone(phone_number: str):
    """
    Get (country_name, flag) from a phone number.
    Returns ('Unknown', '🏴‍☠️') if not found.
    """
    number = phone_number.lstrip('+').lstrip('0')
    for length in (3, 2, 1):
        prefix = number[:length]
        if prefix in COUNTRY_DATA:
            data = COUNTRY_DATA[prefix]
            name = data[0]
            flags = ' '.join(data[1:])
            return name, flags
    return 'Unknown', '🏴‍☠️'


def get_country_by_code(country_code: str):
    """Get country name and flag by dial code string."""
    if country_code in COUNTRY_DATA:
        data = COUNTRY_DATA[country_code]
        name = data[0]
        flags = ' '.join(data[1:])
        return name, flags
    return 'Unknown', '🏴‍☠️'
