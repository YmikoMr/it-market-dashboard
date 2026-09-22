import streamlit as st
import pandas as pd
import ast
import matplotlib.pyplot as plt

# 1. Настройка веб-страницы
st.set_page_config(page_title="ИТ-Аналитика", layout="wide", page_icon="📊")

st.title("📊 Интерактивный дашборд анализа ИТ-рынка труда")
st.write("Продукт разработан для помощи старшеклассникам в выборе актуального ИТ-направления.")

# 2. Загрузка данных
@st.cache_data
def load_data():
    return pd.read_csv("it_vacancies.csv")

df = load_data()

# 3. Боковая панель (Фильтры)
st.sidebar.header("⚙️ Настройки поиска")

profession = st.sidebar.selectbox(
    "Выберите ИТ-направление:",
    ["Python", "Golang", "Data", "QA / Тестировщик", "Frontend", "C++"]
)

# 4. Фильтрация данных по выбору пользователя
search_term = 'QA|Тестировщик' if profession == 'QA / Тестировщик' else profession
filtered_df = df[df['Name'].str.contains(search_term, case=False, na=False, regex=True)].copy()

st.subheader(f"🔍 Результаты анализа для направления: {profession}")

if filtered_df.empty:
    st.warning("Вакансий по данному направлению в датасете не найдено. Попробуйте другой фильтр.")
else:
    # 5. Вывод главных метрик (Зарплата и количество)
    col1, col2 = st.columns(2)
    
    active_salaries = filtered_df["From"].dropna()
    if not active_salaries.empty:
        mean_salary = int(active_salaries.mean())
        col1.metric(label="Средняя стартовая зарплата", value=f"{mean_salary:,} руб.")
    else:
        col1.metric(label="Средняя стартовая зарплата", value="Не указана")
        
    col2.metric(label="Всего найдено вакансий в базе", value=f"{len(filtered_df)}")

    # 6. Расчет ключевых навыков
    skills_list = []
    for keys_raw in filtered_df["Keys"].dropna():
        try:
            skills = ast.literal_eval(keys_raw)
            if isinstance(skills, list):
                skills_list.extend(skills)
        except:
            continue

    if skills_list:
        skills_series = pd.Series(skills_list)
        top_skills = skills_series.value_counts().head(10)

        st.write("### 🎯 Топ-10 востребованных навыков и технологий:")
        
        # 7. СТРОИМ НАДЁЖНЫЙ ГРАФИК ЧЕРЕЗ MATPLOTLIB
        # Создаем фигуру с фиксированным размером, чтобы график не растягивался
        fig, ax = plt.subplots(figsize=(10, 4.5), facecolor = 'none')
        ax.set_facecolor('none')
        
        # Рисуем горизонтальные бары лавандового цвета (#BDB5D5) с аккуратной черной рамкой
        top_skills.plot(kind="barh", color="#BDB5D5", edgecolor="#6F687D", ax=ax)
        
        # Настраиваем внешний вид (все надписи горизонтальные, самый популярный навык — сверху)
        ax.invert_yaxis()  
        ax.tick_params(colors='white',labelsize=10)
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.set_xlabel("Количество упоминаний в вакансиях", fontsize=10)
        ax.set_ylabel("Технологии", fontsize=10)
        ax.grid(axis="x", linestyle="--", alpha=0.2,color='white') # Легкая сетка
        
        # Убираем лишние рамки графика для современного вида
        for spine in ["top", "right",'left','bottom']:
            ax.spines[spine].set_visible(False)
            
        plt.tight_layout()
        
        # Магия Streamlit: выводим готовый график Matplotlib на страницу сайта!
        st.pyplot(fig)
        
    else:
        st.info("В описании этих вакансий не были заполнены теги ключевых навыков.")

    # 8. Показываем примеры реальных вакансий в таблице
    st.write("### 📋 Примеры вакансий из датасета:")
    st.dataframe(filtered_df[["Name", "Employer", "From", "Experience"]].head(10), use_container_width=True)
