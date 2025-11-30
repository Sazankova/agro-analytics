import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# Настройка страницы
st.set_page_config(
    page_title="Аналитика Растениеводства",
    page_icon="🌾",
    layout="wide"
)

# Заголовок приложения
st.title('🌾 Аналитический сервис: Растениеводство в России')
st.markdown("**Актуальные цены и объемы предложения**")

# Генерация тестовых данных
@st.cache_data
def load_data():
    # Создаем реалистичные данные
    companies = ['РусАгро', 'Мираторг', 'ЭкоНива', 'АФГ Националь', 'Продимекс']
    products = ['Пшеница', 'Ячмень', 'Подсолнечник', 'Картофель', 'Соя']
    activity_types = ['производитель', 'дистрибьютор']
    
    data = []
    start_date = datetime(2023, 1, 1)
    
    # Базовые цены для каждого товара
    base_prices = {
        'Пшеница': 15000,
        'Ячмень': 12000,
        'Подсолнечник': 25000,
        'Картофель': 20000,
        'Соя': 30000
    }
    
    for i in range(500):
        company = companies[i % len(companies)]
        product = products[i % len(products)]
        activity = activity_types[i % len(activity_types)]
        
        # Создаем реалистичную динамику цен
        days_passed = (i * 7) % 365  # Данные за год с недельным интервалом
        date = start_date + timedelta(days=days_passed)
        
        # Сезонные колебания + случайный шум
        seasonal_factor = np.sin(days_passed / 365 * 2 * np.pi) * 0.2
        random_factor = np.random.normal(0, 0.1)
        company_factor = (companies.index(company) * 0.05)
        
        base_price = base_prices[product]
        price = base_price * (1 + seasonal_factor + random_factor + company_factor)
        volume = 1000 + (i * 50) % 2000
        
        data.append({
            'company_name': company,
            'product': product,
            'activity_type': activity,
            'date': date,
            'price': round(price, 2),
            'volume': volume,
            'data_source': 'генератор данных'
        })
    
    return pd.DataFrame(data)

# Загрузка данных
df = load_data()

# Боковая панель с фильтрами
st.sidebar.header("🔍 Фильтры")

# Выбор товара
selected_product = st.sidebar.selectbox(
    'Выберите товар:',
    options=sorted(df['product'].unique())
)

# Фильтр компаний по выбранному товару
companies_for_product = df[df['product'] == selected_product]['company_name'].unique()

selected_company = st.sidebar.selectbox(
    'Выберите компанию:',
    options=sorted(companies_for_product)
)

# Основная область
col1, col2 = st.columns([3, 1])

with col1:
    st.header(f"📊 Анализ: {selected_product} - {selected_company}")
    
    # Фильтрация данных
    filtered_df = df[
        (df['product'] == selected_product) &
        (df['company_name'] == selected_company)
    ].sort_values('date')

    if filtered_df.empty:
        st.warning("По выбранным фильтрам данных не найдено.")
    else:
        # График цен
        st.subheader("📈 Динамика цен")
        fig_price = px.line(
            filtered_df, 
            x='date', 
            y='price',
            title=f'Цена {selected_product}',
            labels={'price': 'Цена, руб/т', 'date': 'Дата'},
            markers=True
        )
        st.plotly_chart(fig_price, use_container_width=True)

        # График объемов
        st.subheader("📦 Динамика объемов предложения")
        fig_volume = px.line(
            filtered_df, 
            x='date', 
            y='volume',
            title=f'Объем предложения {selected_product}',
            labels={'volume': 'Объем, т', 'date': 'Дата'},
            markers=True
        )
        st.plotly_chart(fig_volume, use_container_width=True)

with col2:
    st.header("📋 Детали")
    
    if not filtered_df.empty:
        # Последние данные
        latest_data = filtered_df.iloc[-1]
        st.metric(
            label=f"💰 Последняя цена",
            value=f"{latest_data['price']:,.0f} руб/т",
            delta=f"{latest_data['date'].strftime('%d.%m.%Y')}"
        )
        st.metric(
            label=f"📊 Последний объем",
            value=f"{latest_data['volume']:,.0f} т"
        )
        
        # Статистика
        st.subheader("📊 Статистика")
        st.write(f"**Средняя цена:** {filtered_df['price'].mean():,.0f} руб/т")
        st.write(f"**Мин. цена:** {filtered_df['price'].min():,.0f} руб/т")
        st.write(f"**Макс. цена:** {filtered_df['price'].max():,.0f} руб/т")
        st.write(f"**Записей:** {len(filtered_df)}")

# Секция сравнения компаний
st.sidebar.markdown("---")
st.sidebar.header("📊 Сравнение компаний")

compare_companies = st.sidebar.multiselect(
    'Сравнить компании:',
    options=sorted(companies_for_product),
    default=[selected_company]
)

if len(compare_companies) > 1:
    st.header("📊 Сравнение компаний")
    
    compare_df = df[
        (df['product'] == selected_product) &
        (df['company_name'].isin(compare_companies))
    ]
    
    if not compare_df.empty:
        fig_compare = px.line(
            compare_df, 
            x='date', 
            y='price', 
            color='company_name',
            title=f'Сравнение цен на {selected_product}',
            labels={'price': 'Цена, руб/т', 'date': 'Дата'},
            markers=True
        )
        st.plotly_chart(fig_compare, use_container_width=True)

# Таблица с данными
st.header("📋 Исторические данные")
if not filtered_df.empty:
    display_df = filtered_df[['date', 'price', 'volume', 'data_source']].sort_values('date', ascending=False)
    display_df['date'] = display_df['date'].dt.strftime('%d.%m.%Y')
    st.dataframe(display_df, use_container_width=True, height=300)

# Информация в сайдбаре
st.sidebar.markdown("---")
st.sidebar.info("""
**📖 Инструкция:**
1. Выберите товар
2. Выберите компанию  
3. Анализируйте графики
4. Сравнивайте компании
""")

# Футер
st.markdown("---")
st.markdown("*Прототип аналитического сервиса для рынка растениеводства*")
