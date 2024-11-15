headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
              'image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    'origin': 'https://www.xiaohongshu.com',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.xiaohongshu.com/',
    'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
}

cookies = {
    "a1": "",
    "web_session": "",
}

url_list = {
    "profile_index_url": "https://www.xiaohongshu.com/user/profile/{}",
    "captcha_info_url": "https://edith.xiaohongshu.com/api/redcaptcha/v2/captcha/register",
}

lookup = [
    "Z", "m", "s", "e", "r", "b", "B", "o", "H", "Q", "t", "N", "P", "+", "w", "O", "c", "z", "a", "/", "L", "p", "n",
    "g", "G", "8", "y", "J", "q", "4", "2", "K", "W", "Y", "j", "0", "D", "S", "f", "d", "i", "k", "x", "3", "V", "T",
    "1", "6", "I", "l", "U", "A", "F", "M", "9", "7", "h", "E", "C", "v", "u", "R", "X", "5",
]

xn = 'A4NjFqYu5wPHsO0XTdDgMa2r1ZQocVte9UJBvk6/7=yRnhISGKblCWi+LpfE8xzm3'
xn64 = xn[64]

replacements = {
    'undefined': 'null',
    "'": '"',
    'True': 'true',
    'False': 'false',
    'None': 'null'
}

bg_nums = {
    "bg_s194524363": 1,
    "bg_s193244778": 2,
    "bg_s195624698": 3,
    "bg_s191365064": 4,
    "bg_s192694768": 5,
    "bg_s192085789": 6,
    "bg_s192200636": 7,
    "bg_s195509343": 8,
    "bg_s193040574": 9,
    "bg_s195395761": 10,
    "bg_s193359578": 11,
    "bg_s194094381": 12,
    "bg_s193389063": 13,
    "bg_s191914975": 14,
    "bg_s193564614": 15,
    "bg_s194466167": 16,
    "bg_s194889102": 17,
    "bg_s192000355": 18,
    "bg_s195537850": 19,
    "bg_s193923309": 20,
    "bg_s194743905": 21,
    "bg_s194207856": 22,
    "bg_s194179654": 23,
    "bg_s195596161": 24,
    "bg_s193733237": 25,
    "bg_s192665415": 26,
    "bg_s191565440": 27,
    "bg_s191971631": 28,
    "bg_s194552882": 29,
    "bg_s194265897": 30,
    "bg_s191800896": 31,
    "bg_s191943367": 32,
    "bg_s191279944": 33,
    "bg_s194773163": 34,
    "bg_s193216164": 35,
    "bg_s193705323": 36,
    "bg_s195452993": 37,
    "bg_s192866076": 38,
    "bg_s191741751": 39,
    "bg_s194581561": 40,
    "bg_s192752472": 41,
    "bg_s195005473": 42,
    "bg_s195205284": 43,
    "bg_s192517398": 44,
    "bg_s193129858": 45,
    "bg_s194667524": 46,
    "bg_s194037562": 47,
    "bg_s192922609": 48,
    "bg_s191712186": 49,
    "bg_s194918805": 50,
    "bg_s195092181": 51,
    "bg_s191506334": 52,
    "bg_s191885384": 53,
    "bg_s193418585": 54,
    "bg_s192314313": 55,
    "bg_s193620197": 56,
    "bg_s194407812": 57,
    "bg_s192114588": 58,
    "bg_s193273224": 59,
    "bg_s194123345": 60,
    "bg_s191682031": 61,
    "bg_s193786598": 62,
    "bg_s194350808": 63,
    "bg_s193865422": 64,
    "bg_s193952261": 65,
    "bg_s193506253": 66,
    "bg_s194495982": 67,
    "bg_s191221912": 68,
    "bg_s191135361": 69,
    "bg_s193842739": 70,
    "bg_s195261978": 71,
    "bg_s192605538": 72,
    "bg_s193894063": 73,
    "bg_s195424225": 74,
    "bg_s194379587": 75,
    "bg_s194638127": 76,
    "bg_s193100324": 77,
    "bg_s193302811": 78,
    "bg_s195652929": 79,
    "bg_s192057690": 80,
    "bg_s195291458": 81,
    "bg_s194948003": 82,
    "bg_s191535750": 83,
    "bg_s193759062": 84,
    "bg_s192981488": 85,
    "bg_s194236289": 86,
    "bg_s192257695": 87,
    "bg_s192487942": 88,
    "bg_s195367032": 89,
    "bg_s191421158": 90,
    "bg_s194151868": 91,
    "bg_s194322677": 92,
    "bg_s192894579": 93,
    "bg_s191165625": 94,
    "bg_s194065864": 95,
    "bg_s192723792": 96,
    "bg_s191250628": 97,
    "bg_s193010657": 98,
    "bg_s193447841": 99,
    "bg_s192811628": 100,
    "bg_s193814968": 101,
    "bg_s191623846": 102,
    "bg_s192575692": 103,
    "bg_s191594766": 104,
    "bg_s194010476": 105,
    "bg_s192839400": 106,
    "bg_s191308755": 107,
    "bg_s191770265": 108,
    "bg_s193676693": 109,
    "bg_s194976426": 110,
    "bg_s192029348": 111,
    "bg_s191828123": 112,
    "bg_s191477896": 113,
    "bg_s194695905": 114,
    "bg_s194436314": 115,
    "bg_s193332060": 116,
    "bg_s191449247": 117,
    "bg_s191653611": 118,
    "bg_s193981528": 119,
    "bg_s195566767": 120,
    "bg_s192172897": 121,
    "bg_s192635723": 122,
    "bg_s192430696": 123,
    "bg_s192950920": 124,
    "bg_s194831337": 125,
    "bg_s193070659": 126,
    "bg_s194859375": 127,
    "bg_s193187745": 128,
    "bg_s195121451": 129,
    "bg_s192782314": 130,
    "bg_s195339499": 131,
    "bg_s192546435": 132,
    "bg_s194802377": 133,
    "bg_s191392968": 134,
    "bg_s195681032": 135,
    "bg_s191856752": 136,
    "bg_s191194952": 137,
    "bg_s195232832": 138,
    "bg_s193648538": 139,
    "bg_s193159175": 140,
    "bg_s193591168": 141,
    "bg_s193535178": 142,
    "bg_s192229250": 143,
    "bg_s195736718": 144,
    "bg_s192143984": 145,
    "bg_s192343159": 146,
    "bg_s194609964": 147,
    "bg_s195149918": 148,
    "bg_s194294999": 149,
    "bg_s193477260": 150,
    "bg_s192400893": 151,
    "bg_s192460011": 152,
    "bg_s195178449": 153,
    "bg_s192286381": 154,
    "bg_s195708863": 155,
    "bg_s195063273": 156,
    "bg_s195034660": 157,
    "bg_s192371978": 158,
    "bg_s195481120": 159,
    "bg_s191337493": 160
}

ie = [
    0, 1996959894, 3993919788, 2567524794,124634137,1886057615,3915621685,2657392035,249268274,2044508324,
    3772115230,2547177864,162941995,2125561021,3887607047,2428444049,498536548,1789927666,4089016648,
    2227061214,450548861,1843258603,4107580753,2211677639,325883990,1684777152,4251122042,2321926636,
    335633487,1661365465,4195302755,2366115317,997073096,1281953886,3579855332,2724688242,1006888145,
    1258607687,3524101629,2768942443,901097722,1119000684,3686517206,2898065728,853044451,1172266101,
    3705015759,2882616665,651767980,1373503546,3369554304,3218104598,565507253,1454621731,3485111705,
    3099436303,671266974,1594198024,3322730930,2970347812,795835527,1483230225,3244367275,3060149565,
    1994146192,31158534,2563907772,4023717930,1907459465,112637215,2680153253,3904427059,2013776290,
    251722036,2517215374,3775830040,2137656763,141376813,2439277719,3865271297,1802195444,476864866,
    2238001368,4066508878,1812370925,453092731,2181625025,4111451223,1706088902,314042704,2344532202,
    4240017532,1658658271,366619977,2362670323,4224994405,1303535960,984961486,2747007092,3569037538,
    1256170817,1037604311,2765210733,3554079995,1131014506,879679996,2909243462,3663771856,1141124467,
    855842277,2852801631,3708648649,1342533948,654459306,3188396048,3373015174,1466479909,544179635,
    3110523913,3462522015,1591671054,702138776,2966460450,3352799412,1504918807,783551873,3082640443,
    3233442989,3988292384,2596254646,62317068,1957810842,3939845945,2647816111,81470997,1943803523,
    3814918930,2489596804,225274430,2053790376,3826175755,2466906013,167816743,2097651377,4027552580,
    2265490386,503444072,1762050814,4150417245,2154129355,426522225,1852507879,4275313526,2312317920,
    282753626,1742555852,4189708143,2394877945,397917763,1622183637,3604390888,2714866558,953729732,
    1340076626,3518719985,2797360999,1068828381,1219638859,3624741850,2936675148,906185462,1090812512,
    3747672003,2825379669,829329135,1181335161,3412177804,3160834842,628085408,1382605366,3423369109,
    3138078467,570562233,1426400815,3317316542,2998733608,733239954,1555261956,3268935591,3050360625,
    752459403,1541320221,2607071920,3965973030,1969922972,40735498,2617837225,3943577151,1913087877,
    83908371,2512341634,3803740692,2075208622,213261112,2463272603,3855990285,2094854071,198958881,
    2262029012,4057260610,1759359992,534414190,2176718541,4139329115,1873836001,414664567,2282248934,
    4279200368,1711684554,285281116,2405801727,4167216745,1634467795,376229701,2685067896,3608007406,
    1308918612,956543938,2808555105,3495958263,1231636301,1047427035,2932959818,3654703836,1088359270,
    936918000,2847714899,3736837829,1202900863,817233897,3183342108,3401237130,1404277552,615818150,
    3134207493,3453421203,1423857449,601450431,3009837614,3294710456,1567103746,711928724,3020668471,
    3272380065,1510334235,755167117
]
