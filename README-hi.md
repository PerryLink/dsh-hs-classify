# dsh-hs-classify — माल वर्गीकरण रजिस्टर के पदानुक्रम की संगति की जाँच

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-hs-classify` एक वर्गीकरण रजिस्टर — घोषणाकर्ता का हेडर और प्रत्येक मद की एक पंक्ति — पढ़ता है और उसमें दर्ज संख्याओं की संरचना की जाँच करता है: क्या माल-कोड दस अंकों का है, क्या उसका अध्याय, हेडिंग और उप-हेडिंग उस कोड के क्रमिक पूर्व-खंड हैं, क्या स्तर मोटे से बारीक की ओर जाते हैं, क्या हर पंक्ति में वर्गीकरण का आधार दर्ज है, क्या हेडर उस टैरिफ़ संस्करण की घोषणा करता है जिससे ये कोड संबंधित हैं, क्या मद-क्रमांक रजिस्टर में अद्वितीय हैं, और क्या मद के नाम में कोई बदला न गया प्लेसहोल्डर शेष है।

## आउटपुट कैसा दिखता है

![Terminal demo of dsh-hs-classify: real output over its HC-001 fixture](https://raw.githubusercontent.com/PerryLink/dsh-hs-classify/main/docs/assets/dsh-hs-classify-demo.png)

इस प्लगइन का अपने ही `HC-001` टेस्ट फ़िक्स्चर पर वास्तविक आउटपुट — कोई नकली चित्र नहीं। नियम-पैक उद्धरण नहीं गढ़ता, इसलिए हर निष्कर्ष लागू किए गए खंड का नाम और यह भी बताता है कि उसका मूल पाठ इस बार प्राप्त नहीं हुआ।

## यह किन सवालों का जवाब देता है

| आपका सवाल | इसका जवाब |
|---|---|
| हमारे रजिस्टर में कुछ कोड आठ अंकों के हैं और एक के अंत में अक्षर है। क्या ये दर्ज होंगे? | हाँ। `HC-001` हर भरे हुए `hsCode` की तुलना नियम-पैक के `pattern` (`^[0-9]{10}$`) से करता है और उस पंक्ति को उस मान के साथ दर्ज करता है जो उसने पढ़ा। यह केवल अंकों की संख्या और अक्षरों की जाँच करता है, यह कभी नहीं कि माल उसी कोड के अंतर्गत आता है। खाली कोड सेल छोड़ दिया जाता है, इसलिए यह गलत आकार के कोड को दर्ज करता है, अनुपस्थित कोड को नहीं। दस अंक नियम-पैक की सेटिंग है: वार्षिक टैरिफ़ से लंबाई बदले तो `pattern` बदलें, कोड नहीं। |
| किसी पंक्ति के 章, 品目 और 子目 उसके 商品编号 से मेल नहीं खाते। क्या यह पकड़ में आता है? | हाँ। `HC-002` स्तर-कॉलमों को मोटे से बारीक क्रम में पढ़ता है — 章, 品目, 子目, नियम-पैक के अपने उदाहरण में दो, चार और छह अंक — और वह स्तर दर्ज करता है जो पढ़े गए `hsCode` का पूर्व-खंड (prefix) नहीं है, या जो अपने पिछले स्तर से अधिक बारीक नहीं है। यह केवल उस पूर्व-खंड संबंध और उस क्रम की जाँच करता है: कोड उस माल पर लागू होता है या नहीं, यह सीमा-शुल्क का निर्णय है जिसके लिए टैरिफ़ और वर्गीकरण निर्णय चाहिए, जिन्हें यह प्लगइन नहीं देखता। खाली छोड़ा गया स्तर-कॉलम तुलना में नहीं आता। |
| एक पंक्ति में 归类依据 खाली है। | `HC-003` उस पंक्ति को दर्ज करता है: जिन पंक्तियों में यह कॉलम है, उनमें `basis` भरा होना चाहिए। यह देखता है कि कुछ लिखा है या नहीं, यह नहीं कि उद्धृत टैरिफ़ प्रावधान, अध्याय-टिप्पणी, वर्गीकरण निर्णय या अग्रिम निर्णय मौजूद है या उस वर्गीकरण का समर्थन करता है — यह प्लगइन इनमें से कुछ भी नहीं देखता। यदि रजिस्टर में `basis` कॉलम ही न हो, तो `HC-003` चुपचाप पास होने के बजाय `skipped` में यह बताते हुए आता है कि सामग्री में वह कॉलम नहीं है। |
| हेडर यह नहीं बताता कि कोड टैरिफ़ के किस संस्करण के हैं। | `HC-004` अपेक्षा करता है कि हेडर `tariffVersion` घोषित करे, और हेडर में वह खाली होने पर रजिस्टर को दर्ज करता है। यह देखता है कि घोषणा मौजूद है, यह नहीं कि बताया गया संस्करण इन्हीं कोड का है: यह नियम कोड नहीं पढ़ता, और संस्करणों के बीच कोड बँटते और जुड़ते हैं। इसकी `fields` सूची नियम-पैक की सेटिंग है: हेडर में घोषणाकर्ता भी दर्ज हो तो `declarant` जोड़ दें। |
| 项号 5 दो पंक्तियों में आया है। | `HC-005` बाद वाली पंक्ति को पहली की दोहराई हुई बताता है, क्योंकि एक ही रजिस्टर में `itemNo` अद्वितीय होना चाहिए; तुलना में खाली जगह नहीं गिनी जाती, इसलिए `5` और ` 5 ` एक ही मद-क्रमांक हैं। यह केवल अद्वितीयता की जाँच करता है। एक ही माल कई पंक्तियों में (जैसे भिन्न विशिष्टताओं के साथ) घोषित हो तो हर पंक्ति में अलग मद-क्रमांक चाहिए। सारे क्रमांक अलग होने पर भी `HC-005` `skipped` में रहता है: तब यह कारण दर्ज होता है कि सामग्री ने इस जाँच की पूर्व-शर्तें पूरी कीं और कोई भिन्न प्रविष्टि नहीं मिली — जो उस कारण से अलग है जो कॉलम न होने पर जाँच न चल पाने की स्थिति में दिया जाता है। |
| 品名 कॉलम में अब भी टेम्पलेट के 【】 या 待填 पड़े हैं। | `HC-006` उस पंक्ति और मिले हुए प्लेसहोल्डर को दर्ज करता है। नियम-पैक 【, 】, {{, }}, XXX, xxx, 待填, 待补充, TBD, todo और 示例 खोजता है, और `terms` को अपने टेम्पलेट के अनुसार घटाया-बढ़ाया जा सकता है। यह केवल बदले न गए प्लेसहोल्डर खोजता है: यह नहीं आँकता कि नाम सही है, और यह भी नहीं माँगता कि कॉलम भरा हो — खाली `description` सेल से इसका कोई अंतर दर्ज नहीं होता, और इस नियम-पैक का कोई अन्य नियम भी इसे नहीं माँगता। |

## यह किन मानकों पर आधारित है

| दस्तावेज़ | संख्यांक | इन्हें उद्धृत करने वाले नियम |
|---|---|---|
| 《中华人民共和国进出口税则》 | 现行版本本次未核实 | HC-001, HC-004, HC-005, HC-006 |
| 《商品名称及编码协调制度》 | 现行版本本次未核实 | HC-002 |
| 《中华人民共和国进出口关税条例》 | 国务院令第392号（2003年11月23日公布；根据2011年1月8日、2013年12月7日、2016年2月6日三次《国务院关于修改（废止）部分行政法规的决定》修订） | HC-003 |

**Boundary:** this plugin checks a **商品归类台账** for the *structure* of the numbers it records — that a
commodity code is ten digits, that its chapter, heading and subheading are successive prefixes of it, that the
levels get progressively finer, that a classification basis is recorded, that the tariff version is declared,
that item numbers are unique, and that no placeholder survives. It does **not** decide which code goods should
be classified under.

> ### ⚠️ It checks the shape of a code, never whether the code is right
>
> **Classification is a customs determination**, turning on the goods' material, function and degree of
> processing together with the tariff's section and chapter notes and any classification decisions or advance
> rulings. **This plugin does not consult the tariff, does not consult classification decisions, and does not
> consult rulings.** So:
>
> - it **can** find "this row's code disagrees with the chapter, heading and subheading the same row states";
> - it **cannot** find "this row's code does not match the goods", because that needs the tariff itself.
>
> A register with a structurally perfect code for the wrong goods passes this plugin. That is the documented
> limit, stated in the header, in `HC-002`'s note, and in the troubleshooting section.
>
> **Every `excerpt` in the rule pack says, in so many words, that the clause text was not obtained.** The
> regime lives in 《中华人民共和国进出口税则》— whose codes are ten digits, the first six being the WCO
> Harmonized System — and 《中华人民共和国进出口关税条例》. The verification pass could not retrieve
> verbatim clause text, so the pack states the gap in the `excerpt` field itself and keeps every rule at
> `warn` or `info`. **When the texts are in hand, replace each `excerpt` with the real clause and raise `kind`
> to `direct`.** The ten-digit assumption is a `pattern` in the rule pack, so an annual tariff change needs a
> rule-pack edit, not a code change.

## Compatibility

| सतह | स्थिति |
|---|---|
| Harness | peer रेंज `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — `0.2.0-rc.2` और `0.2.1-alpha.1` दोनों को स्वीकार करने के लिए सत्यापित। **`engines.dsh` जानबूझकर घोषित नहीं**: इसका कोई पाठक नहीं और यह किसी होस्ट को अस्वीकार नहीं कर सकता |
| Node | `^22.19.0 || >=24.0.0` |
| प्लेटफ़ॉर्म | सभी (शुद्ध ESM; कोई नेटिव कोड नहीं, कोई नेटवर्क नहीं, कोई मॉडल कॉल नहीं) |
| टूल मोड | `native`, `ptc` और `both` में काम करता है; पूरे फ़ोल्डर के लिए `ptc` चुनें |

## What it does

नियम-सूची, फ़ील्ड और विस्तृत व्यवहार [README.md](README.md#what-it-does) (अंग्रेज़ी मुख्य संस्करण) में हैं। यह प्लगइन केवल उद्धृत धाराओं के सामने शाब्दिक अंतर सूचीबद्ध करता है और हर न चल पाई जाँच को `skipped` में बताता है।

## Install

```sh
dsh plugin --profile <name> add dsh-hs-classify
dsh --profile <name> --dump-config | grep 'dsh-hs-classify'
```

## Configuration

सभी समायोज्य पैरामीटर `src/config.ts` की Schemastery स्कीमा में हैं, इसलिए कोड बदले बिना `cordis.yml` से बदले जा सकते हैं; प्रति-नियम सीमाएँ `rules/` के नियम-पैक में हैं।

| कुंजी | प्रकार | डिफ़ॉल्ट | विवरण |
|---|---|---|---|
| `rulesFile` | string | `rules/hs-classify.yaml` | नियम-पैक का पथ, पैकेज रूट के सापेक्ष |
| `disabledRules` | string[] | `[]` | बंद करने वाले नियम id; प्रत्येक `skipped` में दिखता है |
| `onlyRules` | string[] | `[]` | केवल ये नियम चलाएँ; खाली होने पर सभी नियम चलते हैं |
| `skipNotes` | string | `""` | हर `skipped` कारण के आगे जोड़ी जाने वाली टिप्पणी |
| `timeoutMs` | number | `120000` | उपकरण का सहकारी समय-सीमा बजट |

## Material format

JSON या YAML स्वीकार्य है। पूरा फ़ील्ड उदाहरण [README.md](README.md#material-format) (अंग्रेज़ी मुख्य संस्करण) में है। पढ़ने की परत में फ़ील्ड वैकल्पिक हैं और जाँच इंजन उन्हें सत्यापित करता है, इसलिए आंशिक निर्यात पर क्रैश के बजाय "अनुपस्थित" श्रेणी के निष्कर्ष मिलते हैं।

## Rule sources

नियम-डेटा कोड से अलग है: प्रत्येक नियम में दस्तावेज़, संख्या, स्रोत की अपनी क्रमांकन-प्रणाली के अनुसार धारा, शब्दशः उद्धरण और स्रोत URL होता है। लोडर लागू करता है कि उद्धरण कम से कम आठ अक्षरों का वास्तविक उद्धरण हो, और जिस जाँच का आधार केवल सामान्य सिद्धांत (`kind: derived-from-principle`, अधिकतम `warn`) या स्थानीय नीति (`kind: institutional-configuration`, अधिकतम `info`) हो, उसे कभी `error` घोषित न किया जाए।

सत्यापित सीमाएँ और जान-बूझकर **न** कहे गए निष्कर्ष [README.md](README.md#rule-sources) (अंग्रेज़ी मुख्य संस्करण) और `rules/evidence/` में हैं।

## Troubleshooting

- **प्लगइन इंस्टॉल हो गया पर टूल दिखता नहीं**: जाँचें कि `main` `lib/index.mjs` पर जाता है और `pnpm run build` ने उसे बनाया है।
- **`dsh plugin add` असंगत बताकर मना करता है**: peer range `0.1.x` और `0.2.x` दोनों को कवर करती है; बाहर होने पर स्पष्ट छूट दें: `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`।
- **कोई नियम नहीं चला**: `skipped` सरणी देखें।
- **`check` में `manifest-peers` विफल दिखता है**: यह `dsh-plugin-dev` की ज्ञात अपस्ट्रीम समस्या है; रनटाइम इंस्टॉल के समय अनुकूलता लागू करता है।
- **समय खिसका हुआ लगता है**: सारी गणना दिए गए स्ट्रिंग पर वॉल-क्लॉक है।

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-hs-classify
```

अंतिम कमांड `../_shared` का साझा किट `src/shared/` में कॉपी करता है; हर साझा बदलाव के बाद इसे दोबारा चलाएँ।

## License

[Apache License 2.0](LICENSE) © 2026 dsh-hs-classify contributors.
