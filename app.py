import streamlit as st
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from PIL import Image
import io
import base64

# Sayfa yapılandırması
st.set_page_config(
    page_title="Word Cloud Generator",
    page_icon="☁️",
    layout="wide"
)

# Başlık
st.title("☁️ Word Cloud Generator")
st.markdown("### Verilerinizden profesyonel kelime bulutları oluşturun!")

# Sidebar - Dosya yükleme ve ayarlar
with st.sidebar:
    st.header("📁 Veri Yükleme")
    
    uploaded_file = st.file_uploader(
        "Dosyanızı yükleyin",
        type=['csv', 'txt', 'xlsx', 'xls'],
        help="CSV, TXT veya Excel dosyası yükleyebilirsiniz"
    )
    
    st.markdown("---")
    
    # Özelleştirme ayarları
    st.header("🎨 Özelleştirme")
    
    color_scheme = st.selectbox(
        "Renk Şeması",
        ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 
        'Reds', 'Blues', 'Greens', 'Purples', 'Oranges']
    )
    
    bg_color = st.color_picker("Arka Plan Rengi", "#ffffff")
    
    max_words = st.slider("Maksimum Kelime Sayısı", 50, 500, 200)
    
    col1, col2 = st.columns(2)
    with col1:
        min_font = st.number_input("Min Font Boyutu", 10, 50, 15)
    with col2:
        max_font = st.number_input("Max Font Boyutu", 50, 300, 100)
    
    word_orientation = st.radio(
        "Kelime Yönelimi",
        ['Yatay', 'Karışık', 'Dikey']
    )
    
    language = st.selectbox("Stopword Dili", ['Türkçe', 'İngilizce', 'Her İkisi'])
    
    custom_stopwords = st.text_area(
        "Özel Stopwords (virgülle ayırın)",
        placeholder="ve, veya, ile, gibi"
    )

# Ana içerik alanı
if uploaded_file is not None:
    try:
        # Dosya okuma
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.txt'):
            text = uploaded_file.read().decode('utf-8')
            df = pd.DataFrame({'text': [text]})
        else:  # Excel
            df = pd.read_excel(uploaded_file)
        
        # Veri önizleme
        st.subheader("📊 Veri Önizleme")
        st.dataframe(df.head(), use_container_width=True)
        
        # Metin kolonu seçimi (TXT hariç)
        if not uploaded_file.name.endswith('.txt'):
            text_column = st.selectbox(
                "Metin içeren kolonu seçin:",
                df.columns.tolist()
            )
            
            # Tüm metinleri birleştir
            text = ' '.join(df[text_column].dropna().astype(str))
        else:
            text = df['text'][0]
        
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
        
        # Kelime yönelimi ayarı
        if word_orientation == 'Yatay':
            prefer_horizontal = 1.0
        elif word_orientation == 'Dikey':
            prefer_horizontal = 0.0
        else:
            prefer_horizontal = 0.7
        
        # Word Cloud oluştur butonu
        if st.button("✨ Word Cloud Oluştur", type="primary", use_container_width=True):
            with st.spinner("Word cloud oluşturuluyor..."):
                # Word cloud oluşturma
                wordcloud = WordCloud(
                    width=1600,
                    height=800,
                    background_color=bg_color,
                    stopwords=stopwords,
                    max_words=max_words,
                    min_font_size=min_font,
                    max_font_size=max_font,
                    colormap=color_scheme,
                    prefer_horizontal=prefer_horizontal,
                    relative_scaling=0.5,
                    collocations=False
                ).generate(text)
                
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
                    wordcloud.to_image().save(buf, format='PNG')
                    btn = st.download_button(
                        label="📥 PNG olarak indir",
                        data=buf.getvalue(),
                        file_name="wordcloud.png",
                        mime="image/png"
                    )
                
                # JPG
                with col2:
                    buf = io.BytesIO()
                    wordcloud.to_image().save(buf, format='JPEG')
                    btn = st.download_button(
                        label="📥 JPG olarak indir",
                        data=buf.getvalue(),
                        file_name="wordcloud.jpg",
                        mime="image/jpeg"
                    )
                
                # Yüksek çözünürlük PNG
                with col3:
                    wordcloud_hd = WordCloud(
                        width=3200,
                        height=1600,
                        background_color=bg_color,
                        stopwords=stopwords,
                        max_words=max_words,
                        min_font_size=min_font*2,
                        max_font_size=max_font*2,
                        colormap=color_scheme,
                        prefer_horizontal=prefer_horizontal,
                        relative_scaling=0.5,
                        collocations=False
                    ).generate(text)
                    
                    buf = io.BytesIO()
                    wordcloud_hd.to_image().save(buf, format='PNG')
                    btn = st.download_button(
                        label="📥 HD PNG indir",
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
    st.info("👈 Başlamak için sol menüden bir dosya yükleyin!")
    
    st.markdown("""
    ### 📝 Nasıl Kullanılır?
    
    1. **Dosya Yükleyin:** CSV, TXT veya Excel dosyanızı yükleyin
    2. **Kolonu Seçin:** (CSV/Excel için) Metin içeren kolonu seçin
    3. **Özelleştirin:** Renk, boyut ve diğer ayarları yapın
    4. **Oluşturun:** "Word Cloud Oluştur" butonuna tıklayın
    5. **İndirin:** PNG, JPG veya HD formatında indirin
    
    ### ✨ Özellikler
    
    - 📊 Çoklu format desteği (CSV, TXT, Excel)
    - 🎨 10+ renk şeması
    - 🔤 Türkçe ve İngilizce stopword desteği
    - ⚙️ Gelişmiş özelleştirme seçenekleri
    - 💾 Çoklu format indirme (PNG, JPG, HD)
    - 🚀 Hızlı ve kullanımı kolay
    """)

# Footer
st.markdown("---")
st.markdown("Kuantum Araştırma ❤️ QmindLab")