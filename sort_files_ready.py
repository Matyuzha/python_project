import streamlit as st
import os
import shutil
import datetime
from typing import Dict
import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import filedialog

# Настройка страницы
st.set_page_config(
    page_title="Сортировщик файлов для Windows",
    page_icon="📁",
    layout="wide"
)

# Инициализация пути в session_state, если его там еще нет
if 'folder_path' not in st.session_state:
    st.session_state.folder_path = "C:\\test-for-sort" # Начальный путь

# Заголовок приложения
st.title("📁 Сортировщик файлов для Windows")
st.markdown("---")


# Функция для форматирования размера
def format_file_size(size_bytes):
    for unit in ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.0f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.0f} ТБ"


# Функция для открытия диалога выбора папки
def select_folder():
    """Открывает диалог выбора папки в Windows"""
    # Создаем скрытое окно tkinter
    root = tk.Tk()
    root.withdraw()  # Скрываем главное окно
    root.attributes('-topmost', True)  # Окно поверх всех
    
    # Открываем диалог выбора папки
    folder_path = filedialog.askdirectory(
        title="Выберите папку для сортировки",
        initialdir=os.path.expanduser("~")
    )
    
    root.destroy()
    return folder_path

# Функция для получения свободного места на диске
def get_free_space(path):
    """Возвращает свободное место на диске в читаемом формате"""
    try:
        # Получаем информацию о диске для указанного пути
        disk_usage = shutil.disk_usage(path)
        free_space = disk_usage.free
        return format_file_size(free_space)
    except Exception as e:
        return "Ошибка"

# Функция для форматирования размера файла
def format_file_size(size_bytes: int) -> str:
    """Форматирует размер файла в человеко-читаемый формат"""
    for unit in ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.0f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.0f} ТБ"

# Функция для вычисления общего размера
def calculate_total_size(folder_path: str) -> int:
    """Вычисляет общий размер всех файлов в папке"""
    total = 0
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                total += os.path.getsize(file_path)
            except:
                pass
    return total

# Функция создания бэкапа
def create_backup(source_folder):
    """Создает zip-архив папки в безопасном месте"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Создаем путь к папке "Documents" текущего пользователя
    # Это гарантирует наличие прав на запись
    user_docs = os.path.expanduser("C:\Sort_Backups")
    if not os.path.exists(user_docs):
        os.makedirs(user_docs)
        
    backup_name = f"backup_{os.path.basename(source_folder)}_{timestamp}"
    backup_full_path = os.path.join(user_docs, backup_name)
    
    # Создаем архив
    # format='zip' добавит расширение .zip автоматически
    archive_path = shutil.make_archive(backup_full_path, 'zip', source_folder)
    return archive_path

# Функция для создания папок, если они не существуют
def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return True
    return False

# Функция для получения расширения файла
def get_file_extension(filename):
    return os.path.splitext(filename)[1].lower()

# Функция для определения категории файла
def get_file_category(extension, custom_rules=None):
    # Стандартные категории
    categories = {
        'Изображения': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'],
        'Документы': ['.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp', '.rtf', '.csv'],
        'Видео': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg'],
        'Аудио': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'],
        'Архивы': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'],
        'Исполняемые': ['.exe', '.msi', '.bat', '.cmd', '.ps1', '.sh'],
        'Код': ['.py', '.js', '.html', '.css', '.php', '.java', '.cpp', '.c', '.h', '.json', '.xml', '.yaml', '.yml'],
    }
    
    # Добавляем пользовательские правила
    if custom_rules:
        for category, extensions in custom_rules.items():
            if category not in categories:
                categories[category] = []
            categories[category].extend(extensions)
    
    for category, extensions in categories.items():
        if extension in extensions:
            return category
    
    return 'Прочее'

# Функция для создания HTML отчета
def create_html_report(results: Dict, source_folder: str, sort_method: str, start_time: datetime) -> str:
    """Создает красивый HTML отчет о сортировке"""
    
    # Подготовка данных для отчета
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Сбор дополнительной статистики
    total_size = results.get('total_size', 0)
    size_formatted = format_file_size(total_size)
    
    # Генерация HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Отчет о сортировке файлов</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                color: #333;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                text-align: center;
            }}
            
            .header h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
            }}
            
            .header .date {{
                font-size: 1.1em;
                opacity: 0.9;
            }}
            
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                padding: 40px;
                background: #f8f9fa;
            }}
            
            .stat-card {{
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                transition: transform 0.3s;
                text-align: center;
            }}
            
            .stat-card:hover {{
                transform: translateY(-5px);
            }}
            
            .stat-value {{
                font-size: 2.5em;
                font-weight: bold;
                color: #667eea;
                margin: 10px 0;
            }}
            
            .stat-label {{
                color: #666;
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            .stat-icon {{
                font-size: 2em;
                margin-bottom: 10px;
            }}
            
            .section {{
                padding: 40px;
                border-bottom: 1px solid #e0e0e0;
            }}
            
            .section-title {{
                font-size: 1.8em;
                margin-bottom: 20px;
                color: #667eea;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .category-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }}
            
            .category-item {{
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                transition: all 0.3s;
            }}
            
            .category-item:hover {{
                transform: scale(1.05);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }}
            
            .category-name {{
                font-weight: bold;
                font-size: 1.1em;
                margin-bottom: 5px;
            }}
            
            .category-count {{
                font-size: 1.5em;
                font-weight: bold;
                color: #667eea;
            }}
            
            .progress-bar {{
                background: #e0e0e0;
                border-radius: 10px;
                overflow: hidden;
                margin: 10px 0;
            }}
            
            .progress-fill {{
                background: linear-gradient(90deg, #667eea, #764ba2);
                height: 30px;
                border-radius: 10px;
                transition: width 1s;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 0.9em;
            }}
            
            .footer {{
                background: #2c3e50;
                color: white;
                padding: 20px;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Отчет о сортировке файлов</h1>
                <div class="date">
                    {start_time.strftime('%d.%m.%Y %H:%M:%S')} - {end_time.strftime('%d.%m.%Y %H:%M:%S')}
                </div>
                <div class="date">⏱️ Время выполнения: {duration:.2f} секунд</div>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon">📁</div>
                    <div class="stat-value">{results['sorted']}</div>
                    <div class="stat-label">Файлов отсортировано</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">📂</div>
                    <div class="stat-value">{len(results['categories'])}</div>
                    <div class="stat-label">Категорий создано</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">💾</div>
                    <div class="stat-value">{size_formatted}</div>
                    <div class="stat-label">Общий размер</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">⚠️</div>
                    <div class="stat-value">{results['errors']}</div>
                    <div class="stat-label">Ошибок</div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">
                    <span>📊</span>
                    <span>Детальная статистика по категориям</span>
                </div>
                <div class="category-grid">
    """
    
    # Добавляем категории с прогресс-барами
    total_files = results['sorted']
    for category, count in sorted(results['categories'].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_files * 100) if total_files > 0 else 0
        html_content += f"""
                    <div class="category-item">
                        <div class="category-name">{category}</div>
                        <div class="category-count">{count}</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {percentage}%">
                                {percentage:.1f}%
                            </div>
                        </div>
                    </div>
        """
    
    # Добавляем информацию о бэкапе если есть
    if 'backup' in results:
        backup_size = format_file_size(os.path.getsize(results['backup']) if os.path.exists(results['backup']) else 0)
        html_content += f"""
                </div>
            </div>
            <div class="section">
                <div class="section-title">
                    <span>💾</span>
                    <span>Информация о бэкапе</span>
                </div>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon">🗄️</div>
                        <div class="stat-label">Бэкап создан</div>
                        <div class="stat-value">✅</div>
                        <div class="stat-label">Размер: {backup_size}</div>
                        <div class="stat-label">Файл: {os.path.basename(results['backup'])}</div>
                    </div>
                </div>
            </div>
        """
    else:
        html_content += """
                </div>
            </div>
        """
    
    html_content += f"""
            <div class="section">
                <div class="section-title">
                    <span>⚙️</span>
                    <span>Параметры сортировки</span>
                </div>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">Метод сортировки</div>
                        <div class="stat-value" style="font-size: 1.5em;">{sort_method}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Исходная папка</div>
                        <div class="stat-value" style="font-size: 1em; word-break: break-all;">{source_folder}</div>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <p>📅 Отчет создан автоматически системой сортировки файлов</p>
                <p style="margin-top: 10px; font-size: 0.9em;">© 2024 Сортировщик файлов для Windows</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

def save_html_report(report_content: str, output_path: str = None) -> str:
    """Сохраняет HTML отчет в файл"""
    if output_path is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f"sorting_report_{timestamp}.html"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return output_path

# Функция для сортировки файлов
def sort_files_v2(source_folder, sort_by, selected_list, custom_rules=None, make_backup_flag=False):
                start_time = datetime.now()
                results = {'sorted': 0, 'skipped': 0, 'errors': 0, 'categories': {}, 'total_size': 0}
                if make_backup_flag:
                    try:
                        backup_file = create_backup(source_folder)
                        results['backup'] = backup_file # Путь к архиву пойдет в HTML отчет
                    except Exception as e:
                        st.error(f"Не удалось создать бэкап: {e}")
                # Вместо os.walk берем только выбранные файлы из корня папки
                for file in selected_list:
                    file_path = os.path.join(source_folder, file)
                    if not os.path.exists(file_path): continue
                    
                    try:
                        # Логика определения категории (та же, что у вас)
                        if sort_by == 'Тип файла':
                            ext = get_file_extension(file)
                            category = get_file_category(ext, custom_rules)
                        elif sort_by == 'Дата изменения':
                            mod_time = os.path.getmtime(file_path)
                            category = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d')
                        elif sort_by == 'Размер':
                            size = os.path.getsize(file_path)
                            category = 'Мелкие' if size < 1024*1024 else 'Крупные'
                        
                        dest_folder = os.path.join(source_folder, category)
                        create_folder(dest_folder)
                        
                        dest_path = os.path.join(dest_folder, file)
                        # Обработка дубликатов (ваш код)
                        if os.path.exists(dest_path):
                            name, ext = os.path.splitext(file)
                            counter = 1
                            while os.path.exists(dest_path):
                                dest_path = os.path.join(dest_folder, f"{name}_{counter}{ext}")
                                counter += 1
                        
                        shutil.move(file_path, dest_path)
                        results['sorted'] += 1
                        results['categories'][category] = results['categories'].get(category, 0) + 1
                    except Exception as e:
                        results['errors'] += 1
                
                results['total_size'] = calculate_total_size(source_folder)
                report_html = create_html_report(results, source_folder, sort_by, start_time)
                report_path = save_html_report(report_html)
                return results, report_path

with st.sidebar:
    st.header("⚙️ Настройки")
    
    # 1. Инициализация (выполняется один раз)
    if 'folder_path' not in st.session_state:
        st.session_state.folder_path = "C:\\test-for-sort"

    # 2. Функция-колбэк для обновления пути
    def update_path_callback():
        # Важно: эта функция сработает ДО рендера виджетов
        selected_path = select_folder()
        if selected_path:
            st.session_state.folder_path = selected_path

    # 3. Создаем интерфейс
    col_path, col_browse = st.columns([4, 1])
    
    with col_path:
        # Поле ввода привязано к ключу 'folder_path'
        source_folder = st.text_input(
            "📂 Путь к папке для сортировки",
            key="folder_path",
            help="Введите путь вручную или нажмите кнопку поиска"
        )
    
    with col_browse:
        st.write("") 
        st.write("") 
        # Используем on_click вместо проверки нажатия через if button
        st.button("🔍", on_click=update_path_callback, help="Обзор папок")

    # (Далее остальной код настроек...)

    # (Далее ваш остальной код настроек: методы сортировки и т.д.)
    sort_method = st.selectbox(
        "📊 Метод сортировки",
        ["Тип файла", "Дата изменения", "Размер"]
    )
    
    # Дополнительные опции
    st.subheader("🛡️ Дополнительно")
    
    do_backup = st.checkbox(
        "📦 Создать бэкап (ZIP)",
        value=False,
        help="Создаст полную копию папки в ZIP-архиве перед перемещением файлов"
    )

    generate_report = st.checkbox(
        "📊 Создать HTML отчет",
        value=True,
        help="Создает детальный HTML отчет о сортировке"
    )
    
    # Пользовательские правила
    st.subheader("🎯 Пользовательские правила")
    with st.expander("Добавить свои категории"):
        st.markdown("Формат: расширение1,расширение2 -> Название категории")
        custom_rules_input = st.text_area(
            "Пример: .psd,.ai -> Photoshop файлы",
            height=100
        )
        
        if st.button("➕ Добавить правило"):
            st.success("Правило добавлено!")
    
    # Кнопка запуска
    run_button = st.button("🚀 Запустить сортировку", type="primary", use_container_width=True)

# Основная область
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📊 Статус", "Готов к работе", delta=None)

with col2:
    if os.path.exists(source_folder):
        files_count = len([f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))])
        st.metric("📄 Файлов в папке", files_count)
    else:
        st.metric("📄 Файлов в папке", "Папка не найдена")

if os.path.exists(source_folder):
    free_space = get_free_space(source_folder)
    with col3:
        st.metric("💾 Свободно на диске", free_space)
else:
    with col3:
        st.metric("💾 Свободно на диске", "Папка не найдена")

# Предпросмотр файлов
selected_filenames = [] # Список для хранения имен выбранных файлов

if os.path.exists(source_folder):
    st.subheader(f"📋 Выберите файлы для сортировки в {source_folder}")
    
    files_data = []
    for item in os.listdir(source_folder):
        item_path = os.path.join(source_folder, item)
        if os.path.isfile(item_path):
            size = os.path.getsize(item_path)
            mod_time = datetime.fromtimestamp(os.path.getmtime(item_path))
            files_data.append({
                'Выбрать': True,  # По умолчанию выбраны все
                'Имя': item,
                'Размер (КБ)': round(size / 1024, 2),
                'Дата изменения': mod_time.strftime('%Y-%m-%d %H:%M'),
                'Расширение': get_file_extension(item)
            })
    
    if files_data:
        # Создаем редактируемую таблицу
        df = pd.DataFrame(files_data)
        edited_df = st.data_editor(
            df, 
            hide_index=True, 
            column_config={"Выбрать": st.column_config.CheckboxColumn(required=True)},
            use_container_width=True
        )
        
        # Получаем список имен только тех файлов, где стоит галочка
        selected_filenames = edited_df[edited_df['Выбрать'] == True]['Имя'].tolist()
        
        st.write(f"✅ Выбрано файлов: {len(selected_filenames)}")
    else:
        st.info("В папке нет файлов для сортировки")

# Обработка запуска сортировки
if run_button:
    if not os.path.exists(source_folder):
        st.error("❌ Указанная папка не существует!")
    elif not selected_filenames:
        st.warning("⚠️ Выберите хотя бы один файл для сортировки!")
    else:
        # Парсим пользовательские правила
        custom_rules = {}
        if custom_rules_input:
            for line in custom_rules_input.split('\n'):
                if '->' in line:
                    extensions, category = line.split('->')
                    extensions = [ext.strip() for ext in extensions.split(',')]
                    custom_rules[category.strip()] = extensions
        
        with st.spinner("🔄 Сортируем файлы..."):
            # Запускаем сортировку с созданием отчета
            results, report_path = sort_files_v2(
                source_folder, 
                sort_method, 
                selected_filenames, # Передаем список выбранных
                custom_rules,
                make_backup_flag=do_backup
            )
            
            # Показываем результаты
            st.success("✅ Сортировка завершена!")
            
            # Статистика
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📦 Отсортировано", results['sorted'])
            with col2:
                st.metric("⚠️ Ошибок", results['errors'])
            with col4:
                st.metric("📊 Категорий", len(results['categories']))
            
            # Детальная статистика по категориям
            if results['categories']:
                st.subheader("📊 Статистика по категориям")
                
                # Создаем DataFrame для отображения
                df_categories = pd.DataFrame([
                    {'Категория': cat, 'Количество': count}
                    for cat, count in results['categories'].items()
                ])
                st.dataframe(df_categories, use_container_width=True)
            
            
            # Отображаем отчет
            if generate_report and os.path.exists(report_path):
                st.balloons()
                st.success(f"📊 HTML отчет создан: {report_path}")
                
                # Показываем предпросмотр отчета
                with open(report_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                st.markdown("## 📄 Предпросмотр отчета")
                st.components.v1.html(html_content, height=600, scrolling=True)
                
                # Кнопка для скачивания
                with open(report_path, 'rb') as f:
                    st.download_button(
                        label="📥 Скачать HTML отчет",
                        data=f,
                        file_name=os.path.basename(report_path),
                        mime="text/html"
                    )

# Инструкция
with st.expander("ℹ️ Как использовать"):
    st.markdown("""
    ### Инструкция по использованию:
    
    1. **Укажите путь** к папке, которую нужно отсортировать
    2. **Выберите метод сортировки**:
       - По типу файла (картинки, документы, видео и т.д.)
       - По дате изменения
       - По размеру
    3. **Добавьте свои правила** (опционально)
    4. **Нажмите "Запустить сортировку"**
    
    ### Важно:
    - Файлы будут перемещены в подпапки внутри указанной папки
    - Рекомендуется создавать бэкап перед сортировкой
    - Программа не удаляет исходные файлы, только перемещает их
    - HTML отчет сохраняется в папке с программой
    """)

# Footer
st.markdown("---")
st.markdown("© 2026 Сортировщик файлов для Windows | Сделано с ❤️ на Streamlit")