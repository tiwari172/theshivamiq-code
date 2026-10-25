# Batch 2 (A-011 .. A-020) – SIRF 10 REELS (har case 5 suspect), naye niyam ke saath (RULES section 13).
# Kahani/saboot/answer batch2_data se; 5 suspect ki lines dobara likhi: kaatil ki line baaki jitni, same banawat, koi "!" nahi,
# masoom ki line maut ke time par sach ho sake, sirf EK line galat. Card number badalte rahe (3,5,2,4,1,5,3,2,4,1).
import copy, re
import batch2_data as _B
BATCH = 2
MIN_TAGS = True

def S(dev, shak_dev, line_dev, rom, shak_rom, line_rom, look):
    return (dev, shak_dev, line_dev, rom, shak_rom, line_rom, look, "")

NEW = {
 11: dict(killer=3, galat=4, suspects=[
  S("बेटा अंकित", "जायदाद का झगड़ा", "मैं आठ बजे पापा से मिला, वो हॉल में बैठकर अख़बार पढ़ रहे थे।", "Beta Ankit", "jaaydaad ka jhagda", "Main 8 baje papa se mila, wo hall mein baithkar akhbaar padh rahe the.", "Indian man about 32, formal shirt"),
  S("नौकर रघु", "चाय उसी ने बनाई", "मैंने साढ़े सात बजे साहब को चाय दी, वो टीवी देख रहे थे।", "Naukar Raghu", "chai usi ne banayi", "Maine saadhe 7 baje sahab ko chai di, wo TV dekh rahe the.", "Indian male servant, gamchha"),
  S("पड़ोसी रमाकांत", "", "मैं साढ़े आठ बजे साहब से मिला, उनकी सोने की घड़ी चमक रही थी।", "Padosi Ramakant", "", "Main saadhe 8 baje sahab se mila, unki sone ki ghadi chamak rahi thi.", "Older Indian man, glasses"),
  S("ड्राइवर जग्गा", "जाली के पास जूते के निशान", "मैंने सात बजे साहब को घर छोड़ा, वो बहुत थके हुए लग रहे थे।", "Driver Jagga", "jaali ke paas joote ke nishaan", "Maine 7 baje sahab ko ghar chhoda, wo bahut thake hue lag rahe the.", "Indian driver, car key"),
  S("बहू कविता", "", "मैंने शाम छह बजे पापा जी को फ़ोन किया, वो ठीक थे।", "Bahu Kavita", "", "Maine shaam 6 baje papa ji ko phone kiya, wo theek the.", "Indian woman, pink suit")],
  hook=("{d} लोग। सबने उन्हें ज़िंदा देखा था... एक झूठ बोल रहा है।", "{r} log. Sabne unhe zinda dekha tha... ek jhooth bol raha hai.", "EK JHOOTH")),
 12: dict(killer=5, galat=4, suspects=[
  S("पत्नी शोभा", "बीमा इनके नाम", "मैं छह बजे मंदिर गई थी, आठ बजे लौटी।", "Patni Shobha", "beema inke naam", "Main 6 baje mandir gayi thi, 8 baje lauti.", "Indian woman about 60, saree"),
  S("पेपरवाला पिंटू", "", "मैंने सवा छह बजे गेट पर अख़बार डाला और निकल गया।", "Paperwala Pintu", "", "Maine sawa 6 baje gate par akhbaar daala aur nikal gaya.", "Indian delivery boy, red cap"),
  S("दूधवाला बल्लू", "", "मैंने छह बजे दूध रखा, साहब तब बगीचे में टहल रहे थे।", "Doodhwala Ballu", "", "Maine 6 baje doodh rakha, sahab tab bagiche mein tahal rahe the.", "Indian milkman, milk can"),
  S("माली केशव", "डंडा इसी का", "मैं सात बजे तक पीछे के बगीचे में पानी दे रहा था।", "Mali Keshav", "danda isi ka", "Main 7 baje tak peeche ke bagiche mein paani de raha tha.", "Old gardener, straw hat, shears"),
  S("भतीजा मनोज", "", "मैं सात बजे आया, चाचा जी ने अख़बार पढ़कर मुझे दिया।", "Bhatija Manoj", "", "Main 7 baje aaya, chacha ji ne akhbaar padhkar mujhe diya.", "Indian man, brown jacket")],
  hook=("सुबह की धुंध... और {d} लोगों के {d} बयान।", "Subah ki dhundh... aur {r} logon ke {r} bayaan.", "KAATIL KAUN?")),
 13: dict(killer=2, galat=4, suspects=[
  S("बेटा विक्रांत", "गद्दी का झगड़ा", "मैं दस से ग्यारह बजे तक नीचे दरबार हॉल में मेहमानों के साथ था।", "Beta Vikrant", "gaddi ka jhagda", "Main 10 se 11 baje tak neeche darbar hall mein mehmaanon ke saath tha.", "Rajasthani man, sherwani, red turban"),
  S("भतीजा रणवीर", "", "मैं दस बजे से छत पर था, काका सा के सिर पर वार हुआ।", "Bhatija Ranveer", "", "Main 10 baje se chhat par tha, kaka sa ke sar par vaar hua.", "Young man, yellow kurta"),
  S("डॉक्टर मेहता", "लाश सबसे पहले इन्होंने देखी", "मुझे ग्यारह बजे बुलाया, मैंने जाँच करके कमरा बंद करवा दिया।", "Doctor Mehta", "laash sabse pehle inhone dekhi", "Mujhe 11 baje bulaya, maine jaanch karke kamra band karwa diya.", "Indian doctor, white coat"),
  S("मुनीम गिरधारी", "हिसाब में गड़बड़ी", "मैं दस से ग्यारह बजे तक अपने कमरे में खाते मिला रहा था।", "Munim Girdhari", "hisaab mein gadbadi", "Main 10 se 11 baje tak apne kamre mein khaate mila raha tha.", "Older Indian man, cream shirt"),
  S("रसोइया कल्लू", "", "मैंने दस बजे दूध का गिलास दिया था, तब काका सा ठीक थे।", "Rasoiya Kallu", "", "Maine 10 baje doodh ka glass diya tha, tab kaka sa theek the.", "Rajasthani man, red turban, dhoti")],
  hook=("एक बंद कमरा। {d} लोग। और एक ग़लती।", "Ek band kamra. {r} log. Aur ek galti.", "EK GALTI")),
 14: dict(killer=4, galat=2, suspects=[
  S("पत्नी अंजलि", "तलाक़ का केस", "मैं नौ से दस बजे तक अपनी बहन के घर पर थी।", "Patni Anjali", "talaaq ka case", "Main 9 se 10 baje tak apni behen ke ghar par thi.", "Indian woman, red saree"),
  S("स्टूडेंट तनिष्का", "डायरी में इसका नाम", "मैं नौ बजे क्लास के बाद निकली और सीधे घर गई।", "Student Tanishka", "diary mein iska naam", "Main 9 baje class ke baad nikli aur seedhe ghar gayi.", "Indian girl, pink suit"),
  S("चौकीदार रामसिंह", "", "मैं नौ से दस बजे तक गार्ड रूम में बैठा था।", "Chowkidar Ramsingh", "", "Main 9 se 10 baje tak guard room mein baitha tha.", "Indian guard, khaki, lathi"),
  S("पुराना दोस्त हिमांशु", "", "मैं नौ से दस बजे तक छत पर तारे देख रहा था।", "Purana dost Himanshu", "", "Main 9 se 10 baje tak chhat par taare dekh raha tha.", "Indian man, blue jacket"),
  S("डिलीवरी बॉय अमन", "", "मैंने सवा नौ बजे गेट पर खाना दिया और लौट गया।", "Delivery boy Aman", "", "Maine sawa 9 baje gate par khaana diya aur laut gaya.", "Delivery boy, red cap, wet")],
  hook=("{d} लोग। एक रात। सिर्फ़ एक झूठ।", "{r} log. Ek raat. Sirf ek jhooth.", "{r} LOG")),
 15: dict(killer=1, galat=2, suspects=[
  S("क्लाइंट विनय", "", "मैं नौ बजे गेट से बाहर निकल गया, गार्ड ने रजिस्टर में लिखा।", "Client Vinay", "", "Main 9 baje gate se bahar nikal gaya, guard ne register mein likha.", "Indian man, shirt and tie"),
  S("पार्टनर पंकज", "कंपनी के पैसे का झगड़ा", "मैं नौ बजकर पाँच मिनट पर गेट से बाहर निकल गया था।", "Partner Pankaj", "company ke paise ka jhagda", "Main 9 bajkar 5 minute par gate se bahar nikal gaya tha.", "Indian man, white shirt"),
  S("गार्ड बहादुर", "", "मैं नौ से साढ़े नौ बजे तक पूरे वक़्त गेट पर बैठा था।", "Guard Bahadur", "", "Main 9 se saadhe 9 baje tak poore waqt gate par baitha tha.", "Nepali guard, khaki, lathi"),
  S("डिलीवरी बॉय सोनू", "", "मैं नौ बजकर दस मिनट पर खाना देने गया, किसी ने दरवाज़ा नहीं खोला।", "Delivery boy Sonu", "", "Main 9 bajkar 10 minute par khaana dene gaya, kisi ne darwaza nahi khola.", "Young man, red t-shirt"),
  S("पड़ोसी मिश्रा जी", "पार्किंग का झगड़ा", "मैं नौ से साढ़े नौ बजे तक अपने फ़्लैट में खाना खा रहा था।", "Padosi Mishra ji", "parking ka jhagda", "Main 9 se saadhe 9 baje tak apne flat mein khaana kha raha tha.", "Indian man, green kurta")],
  hook=("एक सोसाइटी। एक गेट। {d} लोग।", "Ek society. Ek gate. {r} log.", "KILLER KAUN?")),
 16: dict(killer=5, galat=2, suspects=[
  S("बेटा दिग्विजय", "जायदाद का झगड़ा", "मैं क्लब में दोस्तों के साथ ताश खेल रहा था।", "Beta Digvijay", "jaaydaad ka jhagda", "Main club mein doston ke saath taash khel raha tha.", "Rajasthani man, kurta"),
  S("बहू मीनाक्षी", "गहनों का डब्बा इनके कमरे का", "मैं अपने कमरे में सो रही थी, सिर में दर्द था।", "Bahu Meenakshi", "gehno ka dabba inke kamre ka", "Main apne kamre mein so rahi thi, sar mein dard tha.", "Indian woman, maroon saree"),
  S("नौकर रामू", "चाबियाँ इसी के पास", "मैं रसोई में रात के बर्तन धो रहा था।", "Naukar Ramu", "chaabiyan isi ke paas", "Main rasoi mein raat ke bartan dho raha tha.", "Old Indian servant, white clothes"),
  S("पोती दिव्या", "", "मैं हॉस्टल में थी, सहेली से फ़ोन पर बात कर रही थी।", "Poti Divya", "", "Main hostel mein thi, saheli se phone par baat kar rahi thi.", "Indian girl, jeans, phone"),
  S("ड्राइवर सूरज", "", "मैं गेट के बाहर गाड़ी में बैठकर सो रहा था।", "Driver Suraj", "", "Main gate ke bahar gaadi mein baithkar so raha tha.", "Indian driver, blue shirt")],
  hook=("कातिल का नाम सामने था... किसी ने ध्यान नहीं दिया।", "Kaatil ka naam saamne tha... kisi ne dhyaan nahi diya.", "NAAM SAAMNE HAI")),
 17: dict(killer=3, galat=4, suspects=[
  S("पत्नी लक्ष्मी", "बीमा इनके नाम", "मैं दो से तीन बजे तक मंदिर में थी, वहाँ भजन चल रहे थे।", "Patni Lakshmi", "beema inke naam", "Main 2 se 3 baje tak mandir mein thi, wahan bhajan chal rahe the.", "Tamil woman, silk saree"),
  S("पार्टनर मुरली", "कंपनी हड़पना चाहता था", "मैं दो से तीन बजे तक ऑफ़िस में मीटिंग में था, क्लाइंट भी साथ थे।", "Partner Murali", "company hadapna chahta tha", "Main 2 se 3 baje tak office mein meeting mein tha, client bhi saath the.", "Older Indian man, suit"),
  S("भतीजा अरुण", "", "मैं दो से तीन बजे तक टेस्ट मैच में था, फ़्री हिट पर छक्का लगा।", "Bhatija Arun", "", "Main 2 se 3 baje tak Test match mein tha, free hit par chhakka laga.", "Young man, light blue shirt"),
  S("बिलियर्ड्स कोच रवि", "टूटा क्यू इसका", "मैं दो से तीन बजे तक दूसरे हॉल में बच्चों को बिलियर्ड्स सिखा रहा था।", "Billiards coach Ravi", "toota cue iska", "Main 2 se 3 baje tak doosre hall mein bachchon ko billiards sikha raha tha.", "Indian man, green t-shirt"),
  S("बेटी कीर्ति", "", "मैं दो से तीन बजे तक कॉलेज में परीक्षा दे रही थी, पेपर लंबा था।", "Beti Keerthi", "", "Main 2 se 3 baje tak college mein pariksha de rahi thi, paper lamba tha.", "Indian girl, orange kurti")],
  hook=("{d} लोग। {d} जगह। एक जगह झूठी।", "{r} log. {r} jagah. Ek jagah jhoothi.", "EK JHOOTH")),
 18: dict(killer=2, galat=3, suspects=[
  S("बेटा जॉर्जी", "कारोबार पर क़ब्ज़ा", "मैं ग्यारह से साढ़े ग्यारह बजे तक गोदाम में स्टॉक गिन रहा था।", "Beta Georgy", "kaarobaar par kabza", "Main 11 se saadhe 11 baje tak godaam mein stock gin raha tha.", "Young man, teal t-shirt"),
  S("पार्टनर रशीद", "", "मैं दुबई में था, वहाँ साढ़े बारह बजे थॉमस को वीडियो कॉल किया।", "Partner Rasheed", "", "Main Dubai mein tha, wahan saadhe 12 baje Thomas ko video call kiya.", "Indian man, white shirt"),
  S("नाव वाला कुट्टन", "गीले पैर", "मैं दस बजे नाव बाँधकर अपने घर चला गया था।", "Naav wala Kuttan", "geele pair", "Main 10 baje naav baandhkar apne ghar chala gaya tha.", "Boatman, gamchha"),
  S("पत्नी मरियम", "बीमा इनके नाम", "मैं ग्यारह बजे तक पड़ोसन के घर पर बैठी थी।", "Patni Mariam", "beema inke naam", "Main 11 baje tak padosan ke ghar par baithi thi.", "Indian woman about 55, saree"),
  S("नौकरानी शांति", "चाय इसी ने बनाई", "मैंने साढ़े दस बजे दो गिलास चाय बनाई और सो गई।", "Naukrani Shanti", "chai isi ne banayi", "Maine saadhe 10 baje do glass chai banayi aur so gayi.", "Indian maid, green saree")],
  hook=("आधी रात से पहले... {d} लोग, {d} कहानियाँ।", "Aadhi raat se pehle... {r} log, {r} kahaniyan.", "{r} KAHANIYAN")),
 19: dict(killer=4, galat=2, suspects=[
  S("बेटा अनुराग", "दुकान का झगड़ा", "मैं दस बजे तक दुकान पर बैठकर हिसाब कर रहा था।", "Beta Anurag", "dukaan ka jhagda", "Main 10 baje tak dukaan par baithkar hisaab kar raha tha.", "Indian man, green kurta"),
  S("बुनकर मुन्ना", "पैसे नहीं मिले थे", "मैं दस बजे तक अपने करघे पर काम कर रहा था।", "Bunkar Munna", "paise nahi mile the", "Main 10 baje tak apne karghe par kaam kar raha tha.", "Young man, vest"),
  S("पत्नी सरला", "", "मैं दस बजे तक पड़ोसन के घर पर बैठी थी।", "Patni Sarla", "", "Main 10 baje tak padosan ke ghar par baithi thi.", "Indian woman, red saree"),
  S("भाई सुधीर", "", "मैंने मुंबई से दस बजे माँ को व्हाट्सऐप वीडियो कॉल किया।", "Bhai Sudhir", "", "Maine Mumbai se 10 baje maa ko WhatsApp video call kiya.", "Indian man, beard, phone"),
  S("मुनीम दुबे", "तिजोरी की चाबी", "मैं नौ बजे ही दुकान बंद करके घर चला गया था।", "Munim Dubey", "tijori ki chaabi", "Main 9 baje hi dukaan band karke ghar chala gaya tha.", "Older man, yellow kurta, dhoti")],
  hook=("एक पुरानी फ़ाइल। {d} लोग। सच अब तक छुपा था।", "Ek purani file. {r} log. Sach ab tak chhupa tha.", "PURANI FILE")),
 20: dict(killer=1, galat=2, suspects=[
  S("ट्रस्टी बिहारीलाल", "", "मैं छह से सात बजे तक मंदिर में सूर्य ग्रहण की पूजा में था।", "Trustee Biharilal", "", "Main 6 se 7 baje tak mandir mein surya grahan ki pooja mein tha.", "Older man, cream shirt"),
  S("पुजारी शास्त्री जी", "दान पेटी की चाबी", "मैं छह से सात बजे तक मंदिर में संध्या आरती करवा रहा था।", "Pujari Shastri ji", "daan peti ki chaabi", "Main 6 se 7 baje tak mandir mein sandhya aarti karwa raha tha.", "Older man, glasses"),
  S("बेटा मुरारी", "ट्रस्ट का पैसा", "मैं छह से सात बजे तक अपनी दुकान पर ग्राहकों के साथ था।", "Beta Murari", "trust ka paisa", "Main 6 se 7 baje tak apni dukaan par grahakon ke saath tha.", "Indian man, white shirt"),
  S("पत्नी राधा", "खीर इन्होंने रखी", "मैं छह से सात बजे तक छत पर पूजा के लिए खीर रख रही थी।", "Patni Radha", "kheer inhone rakhi", "Main 6 se 7 baje tak chhat par pooja ke liye kheer rakh rahi thi.", "Indian woman, yellow salwar, thali"),
  S("भतीजा कन्हैया", "", "मैं छह से सात बजे तक दोस्तों के साथ यमुना किनारे था।", "Bhatija Kanhaiya", "", "Main 6 se 7 baje tak doston ke saath Yamuna kinare tha.", "Young man, black t-shirt")],
  hook=("आँगन में दीये... और {d} लोगों के {d} सच।", "Aangan mein diye... aur {r} logon ke {r} sach.", "KAATIL KAUN?")),
}

CASES = []
for _c in copy.deepcopy(_B.CASES):
    _o = NEW[_c["n"]]
    _c["suspects"], _c["killer"] = _o["suspects"], _o["killer"]
    _g = _c["galat"]; _c["galat"] = (_g[0], _g[1], _o["galat"])
    _c["hook"] = tuple(x.format(d="पाँच", r=5) for x in _o["hook"])
    _c["answer"] = re.sub(r"\(no\. \d+\)", f"(no. {_o['killer']})", _c["answer"])
    CASES.append(_c)
# naam badle (purani image ke hisaab se) – galat-ishara line aur answer mein bhi
for _c in CASES:
    if _c["n"] == 13: _c["setup"] = [_c["setup"][0], ("मौत रात दस से ग्यारह के बीच। डॉक्टर ने आते ही लाश को चादर से ढककर कमरा बंद करवा दिया।", "Maut: raat 10 se 11. Doctor ne aate hi laash ko chadar se dhakkar kamra band karwa diya.", _c["setup"][1][2])]
    if _c["n"] == 13: _c["galat"] = ("हिसाब में गड़बड़ी... मुनीम जी?", "Hisaab mein gadbadi... munim ji?", 4)
    if _c["n"] == 14: _c["answer"] = _c["answer"].replace(", baaki sab bheege", "")
    if _c["n"] == 18: _c["answer"] = _c["answer"].replace("Leela", "Shanti")
SHORTS = [(c["n"], [1, 2, 3, 4, 5], c["hook"]) for c in CASES]

REUSE = {
 ("V",11):"C08-004_MR_RATHI", ("V",12):"C04-008_GUPTA_SLUMPED", ("V",14):"C04-010_ARJUN", ("V",15):"C002_ARYAN",
 ("V",16):"G_V_MAN_SHERWANI_CUT", ("V",17):"C001_VIKAS", ("V",18):"G_V_MAN_BLUE_CUT", ("V",19):"C08-007_KAPOOR", ("V",20):"C17-001_SETH",
 ("S",11,1):("C007_NIKHIL",None,None), ("S",11,2):("G_M_GAMCHHA_CUT",None,None), ("S",11,3):("G_M_OLD_GLASSES_CUT",None,None),
 ("S",11,4):("C005_VICKY_KEY_CUT",None,None), ("S",11,5):("G_W_PINK_SUIT_CUT",None,None),
 ("S",12,1):("C004_MAA",None,None), ("S",12,2):("G_PINTU",None,None), ("S",12,3):("C06-007_BALLU",None,None),
 ("S",12,4):("C015_GARDENER",None,None), ("S",12,5):("C006_RAJAT",None,None),
 ("S",13,1):("C004_PADOSI",None,None), ("S",13,2):("C003_SURAJ_CUT",None,None), ("S",13,3):("C16-001_DRMEHTA",None,None),
 ("S",13,4):("G_M_OLD_NOGLASSES_CUT",None,None), ("S",13,5):("G_KALLU_CUT",None,None),
 ("S",14,1):("C001_ANJALI",None,None), ("S",14,2):("C002_RIYA_CUT",None,None), ("S",14,3):("G_M_GUARD_CUT",None,None),
 ("S",14,4):("G_M_BLUE_JACKET_A_CUT",None,None), ("S",14,5):("C005_PINTU_WET",None,None),
 ("S",15,1):("C011_TOM",None,None), ("S",15,2):("C10-008_KARAN",None,None), ("S",15,3):("G_BAHADUR",None,None),
 ("S",15,4):("G_CIVIL_RED_CUT",None,None), ("S",15,5):("C010_MAHESH",None,None),
 ("S",16,1):("G_M_ARCHER_B_CUT",None,None), ("S",16,2):("G_W_MAROON_SAREE_CUT",None,None), ("S",16,3):("G_RAMU",None,None),
 ("S",16,4):("C004_BEHEN",None,None), ("S",16,5):("G_M_BLUE_SHIRT_CUT",None,None),
 ("S",17,1):("C010_SUNITA",None,None), ("S",17,2):("C009_JOSHI",None,None), ("S",17,3):("C10-004_DEEPAK",None,None),
 ("S",17,4):("G_CIVIL_GREEN_CUT",None,None), ("S",17,5):("G_W_ORANGE_KURTI_CUT",None,None),
 ("S",18,1):("G_M_CHAI_CUT",None,None), ("S",18,2):("G_SAMEER",None,None), ("S",18,3):("G_M_GAMCHHA_CUT",None,None),
 ("S",18,4):("C004_MAA",None,None), ("S",18,5):("G_SHANTI",None,None),
 ("S",19,1):("C12-010_MAHESH",None,None), ("S",19,2):("C18-003_PRATEEK",None,None), ("S",19,3):("C010_SUNITA",None,None),
 ("S",19,4):("C008_AJAY",None,None), ("S",19,5):("G_M_YELLOW_KURTA_CUT",None,None),
 ("S",20,1):("G_M_OLD_NOGLASSES_CUT",None,None), ("S",20,2):("G_M_OLD_GLASSES_CUT",None,None), ("S",20,3):("C10-008_KARAN",None,None),
 ("S",20,4):("C002_POOJA",None,None), ("S",20,5):("C002_KUNAL",None,None),
 # saboot: purane props
 ("P",11,"P_A011_LOCKER"):"P_ALMARI_KHULI", ("P",11,"P_A011_CUPS"):"P_DO_CHAI_UP", ("P",11,"P_A011_JAALI"):"P_WINDOW_BROKEN", ("P",11,"P_A011_VASE"):"P_KAANCH_TUKDE",
 ("P",12,"P_A012_CHAI"):"P_CHAI_TRAY", ("P",12,"P_A012_GAMLA"):"P_CACTUS", ("P",12,"P_A012_DOODH"):"P_MATKI",
 ("P",13,"P_A013_DOODH"):"P_GLASS_SHARBAT_CUT", ("P",13,"P_A013_CHITTHI"):"P_LETTER", ("P",13,"P_A013_JHAROKHA"):"P_DOOR_WOOD",
 ("P",14,"P_A014_DIARY"):"P_NOTE", ("P",14,"P_A014_CUP"):"P_DO_CHAI_UP",
 ("P",15,"P_A015_WALL"):"P_ROOFTOP", ("P",15,"P_A015_FILES"):"P_REGISTER", ("P",15,"P_A015_PEN"):"P_NOTE", ("P",15,"P_A015_SHOES"):"P_SHOES",
 ("P",16,"P_A016_GLASS"):"P_GLASS_SHARBAT_CUT", ("P",16,"P_A016_DABBA"):"P_JEWELBOX", ("P",16,"P_A016_CHABI"):"P_KEY_RED",
 ("P",17,"P_A017_TROPHY"):"P_TROPHY", ("P",17,"P_A017_COFFEE"):"P_CHAI_TRAY", ("P",17,"P_A017_CHEQUE"):"P_REGISTER_TORN", ("P",17,"P_A017_SHOE"):"P_SHOES",
 ("P",18,"P_A018_CHEST"):"P_CASHBOX", ("P",18,"P_A018_FOOTPRINT"):"P_MUD_MARKS", ("P",18,"P_A018_TEA"):"P_DO_CHAI_UP",
 ("P",19,"P_A019_SAREE"):"P_CLOTHES_PINK", ("P",19,"P_A019_TIJORI"):"P_TIJORI", ("P",19,"P_A019_LOTA"):"P_MATKA_CUT", ("P",19,"P_A019_PHOTO"):"P_PORTRAIT",
 ("P",14,"P_A014_HARMONIUM"):"P_DHOL", ("P",16,"P_A016_RADIO"):"P_TV", ("P",18,"P_A018_SACKS"):"P_BAG", ("P",20,"P_A020_KHEER"):"P_THALI_CUT",
 ("P",20,"P_A020_DAANPETI"):"P_DONATION_BOX_CUT", ("P",20,"P_A020_CHAPPAL"):"P_SHOES",
}
