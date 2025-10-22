import streamlit as st
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import io
import base64
from docx import Document
import PyPDF2
import numpy as np

# Sayfa yapılandırması
st.set_page_config(
    page_title="Word Cloud Generator",
    page_icon="☁️",
    layout="wide"
)

# Başlık
st.title("☁️ Word Cloud Generator")
st.markdown("### Verilerinizden profesyonel kelime bulutları oluşturun!")

# Metin çıkarma fonksiyonları
def extract_text_from_docx(file):
    """Word dosyasından metin çıkar"""
    doc = Document(file)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return '\n'.join(full_text)

def extract_text_from_pdf(file):
    """PDF dosyasından metin çıkar"""
    pdf_reader = PyPDF2.PdfReader(file)
    full_text = []
    for page in pdf_reader.pages:
        text = page.extract_text()
        if text:
            full_text.append(text)
    return '\n'.join(full_text)

def create_shape_mask(shape, width=1600, height=800):
    """Şekil maskesi oluştur"""
    if shape == 'Dikdörtgen (Geniş)':
        # Zaten dikdörtgen, mask yok
        return None
    
    # L mode (grayscale) kullan - RGB yerine
    mask = Image.new('L', (width, height), 255)  # 255 = beyaz (arka plan)
    draw = ImageDraw.Draw(mask)
    
    if shape == 'Daire':
        # Daire çiz
        center_x, center_y = width // 2, height // 2
        radius = min(width, height) // 2 - 50
        draw.ellipse(
            [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
            fill=0  # 0 = siyah (kelime alanı)
        )
    
    elif shape == 'Oval (Yatay)':
        # Oval (Yatay) çiz
        center_x, center_y = width // 2, height // 2
        radius_x = width // 3 - 50 # Geniş
        radius_y = height // 2 - 50 # Dar
        draw.ellipse(
            [center_x - radius_x, center_y - radius_y, center_x + radius_x, center_y + radius_y],
            fill=0  # 0 = siyah (kelime alanı)
        )
    
    elif shape == 'Kare':
        # Kare çiz
        size = min(width, height) - 100
        left = (width - size) // 2
        top = (height - size) // 2
        draw.rectangle([left, top, left + size, top + size], fill=0)
    
    elif shape == 'Yıldız':
        # Yıldız çiz (5 köşeli)
        center_x, center_y = width // 2, height // 2
        outer_radius = min(width, height) // 2 - 50
        inner_radius = outer_radius // 2.5
        
        points = []
        for i in range(10):
            angle = i * 36 - 90  # 36 derece aralıklarla (360/10)
            radius = outer_radius if i % 2 == 0 else inner_radius
            x = center_x + radius * np.cos(np.radians(angle))
            y = center_y + radius * np.sin(np.radians(angle))
            points.append((x, y))
        
        draw.polygon(points, fill=0)
    
    elif shape == 'Kalp':
        # Kalp çiz
        center_x, center_y = width // 2, height // 2
        size = min(width, height) // 2 - 30
        
        points = []
        for t in range(0, 360, 2):
            angle = np.radians(t)
            x = center_x + size * (16 * np.sin(angle)**3)
            y = center_y - size * (13 * np.cos(angle) - 5 * np.cos(2*angle) - 2 * np.cos(3*angle) - np.cos(4*angle))
            points.append((x, y))
        
        draw.polygon(points, fill=0)
    
    elif shape == 'Bulut':
        # Bulut şekli çiz - daha büyük ve geniş
        center_x, center_y = width // 2, height // 2
        
        # Ana büyük elips (ortada)
        draw.ellipse([center_x - 300, center_y - 150, center_x + 300, center_y + 150], fill=0)
        # Sol üst küçük daire
        draw.ellipse([center_x - 400, center_y - 100, center_x - 100, center_y + 200], fill=0)
        # Sağ üst küçük daire
        draw.ellipse([center_x + 100, center_y - 100, center_x + 400, center_y + 200], fill=0)

    elif shape == 'Ampul':
        # Ampul şekli çiz
        center_x, center_y = width // 2, height // 2
        
        # Gövde (Elips)
        body_width = width // 4
        body_height = height // 2
        draw.ellipse(
            [center_x - body_width, center_y - body_height, center_x + body_width, center_y + body_height * 0.7],
            fill=0
        )
        
        # Duy kısmı (Dikdörtgenler)
        duy_top = center_y + body_height * 0.65
        duy_bottom = center_y + body_height * 0.9
        
        # Boyun
        draw.rectangle(
            [center_x - body_width * 0.2, duy_top, center_x + body_width * 0.2, duy_top + 30],
            fill=0
        )
        # Alt kısım 1
        draw.rectangle(
            [center_x - body_width * 0.25, duy_top + 30, center_x + body_width * 0.25, duy_bottom - 20],
            fill=0
        )
        # Alt kısım 2
        draw.rectangle(
            [center_x - body_width * 0.2, duy_bottom - 20, center_x + body_width * 0.2, duy_bottom],
            fill=0
        )
        # Uç
        draw.rectangle(
            [center_x - body_width * 0.15, duy_bottom, center_x + body_width * 0.15, duy_bottom + 10],
            fill=0
        )
    
    return np.array(mask)

# Sidebar - Dosya yükleme ve ayarlar
with st.sidebar:
    st.header("📁 Veri Yükleme")
    
    uploaded_file = st.file_uploader(
        "Dosyanızı yükleyin",
        type=['csv', 'txt', 'xlsx', 'xls', 'docx', 'pdf'],
        help="CSV, TXT, Excel, Word veya PDF dosyası yükleyebilirsiniz"
    )
    
    # Veri formatı seçeneği
    data_format = st.radio(
        "Veri Formatı",
        ['Normal Metin (Kelime bazlı)', 'Her Satır Ayrı İfade'],
        help="'Her Satır Ayrı İfade': Her satırdaki cümle/ifadeyi tek birim olarak sayar (örn: 'Finansal fayda')"
    )
    
    st.markdown("---")
    
    # Özelleştirme ayarları
    st.header("🎨 Özelleştirme")
    
    # Şekil seçimi - YENİ ŞEKİLLER EKLENDİ
    shape = st.selectbox(
        "Şekil",
        ['Dikdörtgen (Geniş)', 'Daire', 'Oval (Yatay)', 'Kare', 'Yıldız', 'Kalp', 'Bulut', 'Ampul']
    )
    
    # Font seçimi
    font_selection = st.selectbox(
        "Yazı Tipi",
        ['Varsayılan', 'Roboto', 'Open Sans', 'Montserrat']
    )
    
    # Font path mapping
    font_map = {
        'Varsayılan': None,
        'Roboto': 'fonts/Roboto-Regular.ttf',
        'Open Sans': 'fonts/OpenSans-Regular.ttf',
        'Montserrat': 'fonts/Montserrat-Regular.ttf'
    }
    
    color_scheme = st.selectbox(
        "Renk Şeması",
        ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 
        'Reds', 'Blues', 'Greens', 'Purples', 'Oranges',
        'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 
        'BuPu', 'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn',
        'copper', 'autumn', 'spring', 'summer', 'winter',
        'hot', 'cool', 'bone', 'pink', 'gray']
    )
    
    bg_color = st.color_picker("Arka Plan Rengi", "#ffffff")
    
    max_words = st.slider(
        "Maksimum Kelime Sayısı", 
        30, 300, 150,
        help="Word cloud'da görünecek maksimum kelime sayısı. Az kelime = temiz görünüm"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        min_font = st.number_input(
            "Min Font Boyutu", 
            8, 30, 12,
            help="En küçük kelimelerin font boyutu (daha küçük = daha fazla kelime sığar)"
        )
    with col2:
        max_font = st.number_input(
            "Max Font Boyutu", 
            40, 200, 80,
            help="En büyük kelimelerin font boyutu"
        )
    
    word_orientation = st.radio(
        "Kelime Yönelimi",
        ['Yatay', 'Karışık', 'Dikey'],
        help="Yatay: Tüm kelimeler yatay, Dikey: Tüm kelimeler dikey, Karışık: Her ikisi de"
    )
    
    language = st.selectbox("Stopword Dili", ['Türkçe', 'İngilizce', 'Her İkisi'])
    
    custom_stopwords = st.text_area(
        "Özel Stopwords (virgülle ayırın)",
        placeholder="ve, veya, ile, gibi"
    )

# Ana içerik alanı
if uploaded_file is not None:
    try:
        text = ""
        df = None
        phrases = []
        
        # Dosya tipine göre okuma
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'csv':
            df = pd.read_csv(uploaded_file)
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file)
        elif file_extension == 'txt':
            text = uploaded_file.read().decode('utf-8')
        elif file_extension == 'docx':
            with st.spinner('Word dosyası okunuyor...'):
                text = extract_text_from_docx(uploaded_file)
        elif file_extension == 'pdf':
            with st.spinner('PDF dosyası okunuyor...'):
                text = extract_text_from_pdf(uploaded_file)
        
        # Veri önizleme (sadece Excel/CSV için)
        if df is not None:
            st.subheader("📊 Veri Önizleme")
            st.dataframe(df.head(), use_container_width=True)
            
            # Metin kolonu seçimi
            text_column = st.selectbox(
                "Metin içeren kolonu seçin:",
                df.columns.tolist()
            )
            
            # Veri formatına göre işle
            if data_format == 'Her Satır Ayrı İfade':
                # Her satırı ayrı ifade olarak al
                phrases = df[text_column].dropna().astype(str).tolist()
                # Boşlukları alt çizgi ile değiştir
                text = ' '.join([phrase.replace(' ', '_').replace(',', '').replace('.', '') for phrase in phrases])
            else:
                # Normal metin olarak birleştir
                text = ' '.join(df[text_column].dropna().astype(str))
        
        # Metin önizleme (Word, PDF, TXT için)
        else:
            st.subheader("📄 Metin Önizleme")
            
            # Her satır ayrı ifade formatı için
            if data_format == 'Her Satır Ayrı İfade':
                phrases = [line.strip() for line in text.split('\n') if line.strip()]
                preview_text = '\n'.join(phrases[:20])
                st.text_area(
                    f"İlk 20 ifade (Toplam {len(phrases)} ifade):",
                    preview_text,
                    height=200,
                    disabled=True
                )
                # Boşlukları alt çizgi ile değiştir
                text = ' '.join([phrase.replace(' ', '_').replace(',', '').replace('.', '') for phrase in phrases])
            else:
                preview_length = min(500, len(text))
                st.text_area(
                    "İlk 500 karakter:",
                    text[:preview_length] + ("..." if len(text) > 500 else ""),
                    height=150,
                    disabled=True
                )
            
            st.info(f"📝 Toplam karakter sayısı: {len(text):,}")
        
        # Stopwords ayarlama
        stopwords = set(STOPWORDS)
        
        # Türkçe stopwords
        turkish_stopwords = {
            've', 'veya', 'ile', 'ancak', 'fakat', 'ama', 'lakin', 'ki', 'de', 'da',
            'bir', 'bu', 'şu', 'o', 'ben', 'sen', 'biz', 'siz', 'onlar',
            'mi', 'mı', 'mu', 'mü', 'için', 'gibi', 'kadar', 'daha', 'çok',
            'her', 'bazı', 'hiç', 'birçok', 'tüm', 'bütün', 'var', 'yok',
            'ne', 'nasıl', 'neden', 'niçin', 'nerede', 'ne zaman', 'kim',
            'diye', 'olarak', 'göre', 'karşı', 'üzere', 'dolayı', 'sonra',
            'önce', 'iken', 'başka', 'diğer', 'aynı', 'şey', 'ise', 'idi',
            'olan', 'olduğu', 'oldu', 'olur', 'olsa', 'bile'
        }
        
        if language == 'Türkçe':
            stopwords.update(turkish_stopwords)
        elif language == 'Her İkisi':
            stopwords.update(turkish_stopwords)
        
        # Özel stopwords ekleme
        if custom_stopwords:
            custom_stops = [word.strip() for word in custom_stopwords.split(',')]
            stopwords.update(custom_stops)
        
        # Kelime yönelimi ayarı - DÜZELTİLDİ
        # prefer_horizontal: 0.0 = tamamen dikey, 1.0 = tamamen yatay
        if word_orientation == 'Yatay':
            prefer_horizontal = 1.0
        elif word_orientation == 'Dikey':
            prefer_horizontal = 0.0
        else:  # Karışık
            prefer_horizontal = 0.5
        
        # Şekil maskesi oluştur
        mask = create_shape_mask(shape)
        
        # Word Cloud oluştur butonu
        if st.button("✨ Word Cloud Oluştur", type="primary", use_container_width=True):
            if not text or len(text.strip()) < 10:
                st.error("❌ Yeterli metin bulunamadı. Lütfen dosyanızı kontrol edin.")
            else:
                with st.spinner("Word cloud oluşturuluyor..."):
                    # Word cloud parametreleri
                    wc_params = {
                        'width': 1600,
                        'height': 800,
                        'background_color': bg_color,
                        'stopwords': stopwords,
                        'max_words': max_words,
                        'min_font_size': min_font,
                        'max_font_size': max_font,
                        'colormap': color_scheme,
                        'prefer_horizontal': prefer_horizontal,
                        'relative_scaling': 0.4,
                        'collocations': False,
                        'random_state': 42,
                        'margin': 2
                    }
                    
                    # Font path ekle (eğer varsayılan değilse)
                    if font_map[font_selection] is not None:
                        import os
                        font_path = font_map[font_selection]
                        if os.path.exists(font_path):
                            wc_params['font_path'] = font_path
                        else:
                            st.warning(f"⚠️ Font dosyası bulunamadı: {font_path}. Varsayılan font kullanılacak.")
                            st.info("💡 Font dosyalarının 'fonts/' klasöründe olduğundan emin olun.")
                    
                    # Mask varsa ekle
                    if mask is not None:
                        wc_params['mask'] = mask
                    
                    # Word cloud oluştur
                    wordcloud = WordCloud(**wc_params).generate(text)
                    
                    # Her satır ayrı ifade modundaysa, alt çizgileri geri boşluğa çevir
                    if data_format == 'Her Satır Ayrı İfade':
                        # Görselleştirme için kelimeleri düzenle
                        words_freq = wordcloud.words_
                        new_words_freq = {word.replace('_', ' '): freq for word, freq in words_freq.items()}
                        
                        # Yeni word cloud oluştur
                        wordcloud = WordCloud(**wc_params).generate_from_frequencies(new_words_freq)
                    
                    # Görselleştirme
                    fig, ax = plt.subplots(figsize=(16, 8))
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis('off')
                    plt.tight_layout(pad=0)
                    
                    st.pyplot(fig)
                    
                    # İndirme butonları
                    st.subheader("💾 İndir")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    # PNG
                    with col1:
                        buf = io.BytesIO()
                        # Ekrandaki görseli olduğu gibi kaydet
                        fig.savefig(buf, format='PNG', dpi=100, bbox_inches='tight', pad_inches=0)
                        btn = st.download_button(
                            label="📥 PNG olarak indir (1600x800)",
                            data=buf.getvalue(),
                            file_name="wordcloud.png",
                            mime="image/png"
                        )
                    
                    # JPG
                    with col2:
                        buf = io.BytesIO()
                        # Ekrandaki görseli olduğu gibi kaydet
                        fig.savefig(buf, format='JPEG', dpi=100, bbox_inches='tight', pad_inches=0)
                        btn = st.download_button(
                            label="📥 JPG olarak indir (1600x800)",
                            data=buf.getvalue(),
                            file_name="wordcloud.jpg",
                            mime="image/jpeg"
                        )
                    
                    # Yüksek çözünürlük PNG
                    with col3:
                        buf = io.BytesIO()
                        # Ekrandaki görseli yüksek DPI ile kaydet
                        fig.savefig(buf, format='PNG', dpi=200, bbox_inches='tight', pad_inches=0)
                        btn = st.download_button(
                            label="📥 HD PNG indir (3200x1600)",
                            data=buf.getvalue(),
                            file_name="wordcloud_hd.png",
                            mime="image/png"
                        )
                    
                    st.success("✅ Word cloud başarıyla oluşturuldu!")
    
    except Exception as e:
        st.error(f"❌ Hata oluştu: {str(e)}")
        st.info("Lütfen dosya formatını kontrol edin ve tekrar deneyin.")

else:
    # Hoş geldin ekranı
    st.info("👈 Başlamak için sol menüden bir dosya yükleyin")
    
    st.markdown("""
    ### 📝 Nasıl Kullanılır?
    
    1. **Dosya Yükleyin:** CSV, TXT, Excel, Word veya PDF dosyanızı yükleyin
    2. **Veri Formatı Seçin:** - **Normal Metin:** Kelime bazlı analiz
       - **Her Satır Ayrı İfade:** Çok kelimelik ifadeleri tek birim olarak sayar (örn: "Finansal fayda")
    3. **Kolonu Seçin:** (CSV/Excel için) Metin içeren kolonu seçin
    4. **Şekil Seçin:** Dikdörtgen, Daire, **Oval (Yatay)**, Kare, Yıldız, Kalp, Bulut, **Ampul**
    5. **Özelleştirin:** Renk, boyut ve diğer ayarları yapın
    6. **Oluşturun:** "Word Cloud Oluştur" butonuna tıklayın
    7. **İndirin:** PNG, JPG veya HD formatında indirin
    
    ###  Özellikler
    
    -  **Çoklu format desteği** (CSV, TXT, Excel, Word, PDF)
    -  **Her satır ayrı ifade modu** - Çok kelimelik ifadeleri korur!
    -  **8 farklı şekil** (Dikdörtgen, Daire, **Oval (Yatay)**, Kare, Yıldız, Kalp, Bulut, **Ampul**)
    -  **4 farklı yazı tipi** (Varsayılan, Roboto, Open Sans, Montserrat)
    -  **32+ renk şeması**
    -  **Türkçe ve İngilizce stopword desteği**
    -  **Yüksek çözünürlük indirme** (3200x1600 HD)
    -  **Hızlı ve kullanımı kolay**
    
    ###  İpuçları
    
    - **Maksimum Kelime Sayısı:** Daha fazla kelime görmek isterseniz artırın
    - **Font Boyutu:** Min/Max aralığını ayarlayarak kelime boyut dengesini kontrol edin
    - **Karışık Yönelim:** Hem yatay hem dikey kelimelerin karışımını sağlar
    - **Her Satır Ayrı İfade:** "Finansal fayda", "Müşteri memnuniyeti" gibi ifadeleri tek birim olarak sayar
    """)

# Footer
st.markdown("---")
st.markdown("Kuantum Araştırma 🦾 QmindLab")