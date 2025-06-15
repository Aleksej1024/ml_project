import torch
from inference import convert_video
import streamlit as st
import os



# Настройка страницы
st.set_page_config(page_title="Удаление фона из видео", layout="wide")

# Создаем папку для видео
os.makedirs("videos", exist_ok=True)

# Заголовок приложения
st.title("Инструмент для удаления фона")

# Секция загрузки видео
st.header("1. Загрузка видео")
uploaded_file = st.file_uploader("Выберете видео-файл", type=["mp4", "avi", "mov"])


if uploaded_file is not None:
    # Создаем папку для этого видео
    video_name = os.path.splitext(uploaded_file.name)[0]
    video_dir = os.path.join("videos", video_name)
    os.makedirs(video_dir, exist_ok=True)
    
    # Сохраняем оригинальное видео
    input_path = os.path.join(video_dir, uploaded_file.name)
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if st.button("Обработать видео"):
        # Генерируем пути для выходных файлов
        output_com = os.path.join(video_dir, f"com_{video_name}.mp4")
        output_alpha = os.path.join(video_dir, f"pha_{video_name}.mp4")
        output_foreground = os.path.join(video_dir, f"fgr_{video_name}.mp4")
        
        # Создаем элементы интерфейса для отображения прогресса
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Функция для обновления прогресса в Streamlit
        def update_progress(current, total):
            progress = int((current / total) * 100)
            progress_bar.progress(progress)
            status_text.text(f"Processing: {progress}% complete")
        
        # Запускаем обработку
        with st.spinner("Обработка видео..."):
            try:
                convert_video(
                    input_source=input_path,
                    output_composition=output_com,
                    output_alpha=output_alpha,
                    output_foreground=output_foreground,
                    progress=True,  # Включаем tqdm прогресс-бар
                )
        
                st.success("Обработка завершилась успешно!")
            except Exception as e:
                st.error(f"При обработке вознмкла ошибка: {str(e)}")

# Просмотр обработанных видео
st.header("2. Просмотр обработанных видео")

# Получаем список папок с видео
video_folders = [f for f in os.listdir("videos") if os.path.isdir(os.path.join("videos", f))]

if not video_folders:
    st.info("Пока обработанных видео нет")
else:
    selected_folder = st.selectbox("Выберете папку с видео", video_folders)
    folder_path = os.path.join("videos", selected_folder)
    
    # Показываем содержимое папки
    st.subheader(f"Набор файлов '{selected_folder}'")
    
    # Получаем список файлов в папке
    files = os.listdir(folder_path)
    
    # Группируем файлы
    original_video = next((f for f in files if not f.startswith(("com_", "pha_", "fgr_")) and f.endswith((".mp4", ".avi", ".mov"))), None)
    composition = next((f for f in files if f.startswith("com_")), None)
    alpha = next((f for f in files if f.startswith("pha_")), None)
    foreground = next((f for f in files if f.startswith("fgr_")), None)
    
    # Отображаем видео в колонках
    col1, col2 = st.columns(2)
    
    if original_video:
        with col1:
            st.write("**Исходник**")
            st.video(os.path.join(folder_path, original_video))
    
    if composition:
        with col2:
            st.write("**Composition**")
            st.video(os.path.join(folder_path, composition))
    
    if alpha:
        with col1:
            st.write("**Alpha Channel**")
            st.video(os.path.join(folder_path, alpha))
    
    if foreground:
        with col2:
            st.write("**Foreground**")
            st.video(os.path.join(folder_path, foreground))

# Стили для улучшения внешнего вида
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-color: green;
    }
    .stSpinner > div {
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)