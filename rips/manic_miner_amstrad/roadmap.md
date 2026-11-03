Dune gibi bir sinema filmi ile Amstrad'daki Manic Miner gibi bir piksel sanatının (pixel art) doğası birbirine taban tabana zıttır. İşin teorisine baktığımızda, film pikselleri birbirine geçişli ve organikken, 8-bit/16-bit retro oyun grafikleri keskin matematiksel sınırlara sahiptir. Bu yüzden VapourSynth tarafında film için kurduğumuz tüm mimari doğruları retro oyunlar için tamamen tersyüz edeceğiz.

Temel mimari farklılıkları dört ana başlıkta toplayabiliriz:

**1. Yeniden Boyutlandırma (Scaling Algorithm)**
Dune'da pikselleri yumuşakça küçültmek/büyütmek için `Bicubic` algoritmalarını kullandık. Ancak piksel sanatında Bicubic, Lanczos veya Spline gibi algoritmalar keskin hatları bulanıklaştırır ve görüntüyü çamurlaştırır. Retro oyunlarda piksellerin o jilet gibi keskin kare formunu korumak için "Point" (Nearest Neighbor) algoritması kullanmak zorundayız. Ayrıca bu büyütme işlemi mutlaka tamsayı katları (Integer Scaling - 2x, 3x, 4x) şeklinde olmalı, küsuratlı oranlardan kaçınılmalıdır.

**2. Renk Uzayı ve Örnekleme (Chroma Subsampling)**
Sinema filmleri ve modern videolar boyuttan tasarruf etmek için neredeyse her zaman 4:2:0 (YUV420) formatındadır. Ancak Amstrad'ın o parlak macenta, cyan ve sarı renklerinin keskin siyah sınırlarla buluştuğu yerlerde 4:2:0 formatı renk kanamasına (color bleeding) neden olur. Kırmızı bir piksel, yanındaki siyah piksele taşar. OBS ile kayıt alırken ve VapourSynth'te işlerken ideal olarak 4:4:4 veya doğrudan RGB uzayında kalmak, o keskin retro görünümünü korumanın temel anahtarıdır.

**3. Sıkıştırma Karakteristiği (Compression Artifacts)**
H.265 (HEVC) algoritması gerçek dünya görüntüleri ve organik dokular için tasarlanmıştır. Düz renk blokları (flat colors) ve keskin çizgilerle karşılaştığında, kodlayıcı serbest bırakılırsa piksellerin etrafında "mosquito noise" denilen kirlenmeler yaratır. Sinemadaki gibi gren korumak yerine, düz renk alanlarını tamamen pürüzsüz tutacak ve kenar keskinliğini bozmayacak (örneğin deblocking filtrelerinin kapatıldığı veya çok farklı ayarlandığı) bir kodlayıcı parametre yapısına ihtiyaç duyacağız.

**4. Kare Hızı ve Akıcılık (Framerate & Pacing)**
Amstrad CPC ve Amiga, donanımsal olarak genelde 50Hz (PAL) sinyal üretir. Eğer emülatörde veya OBS tarafında kayıt 60fps olarak alındıysa, ekranın sağa/sola kaydığı (scrolling) sahnelerde mikro takılmalar (judder/stutter) oluşur. VapourSynth'te dosyanın ham kare yapısını analiz edip, orijinal hareket akıcılığını (frame pacing) sağlayacak bir altyapı kurmamız gerekebilir.