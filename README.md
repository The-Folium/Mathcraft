# Компілятор мови Mathcraft
Цей репозиторій містить вихідний код і виконуваний файл компілятора мови Mathcraft.

# Як швидко запустити компілятор на локальній Windows машині?
*Це не дозволить перевірити інтеграцію, проте дозволить швидко запустити і протестувати компілятор.*
1. Скачайте з цього репозиторію архів `test.zip` і розпакуйте його в будь-якому місці.
2. Запустіть файл `compiler.exe`. Це запустить компіляцію вихідного файлу `source.txt`. Ви можете вносити зміни у цей файл.
3. Після компіляції в робочому каталозі з'являться файли `result.csv` і `result.txt`, які містять CSV- і TXT-подання створених завдань відповідно. Ці файли містять текст у кодуванні Unicode. \
**! Зверніть увагу, що запуск `*.exe`-файлу може відбутись із затримкою, якщо у вас є антивірусна програма.**

# Як розгорнути на локальній машині увесь проєкт з вихідного коду?
*Це дозволить отримати повний доступ до налаштувань і використовувати інтеграцію з Google Forms*\
Пояснення надаються для ОС Windows.
1. Переконайтесь, що на локальній машині встановлений python 3.12 або новіший. Переконатись в цьому можна, запустивши в консолі (`Win+R` -> `cmd`) команду `python --version`. Сумісність зі старішими версіями python можлива, але не гарантується. За необхідності встановіть python з [офіційного сайту](https://www.python.org/).
2. Створіть рабочій каталог на вашій локальній машині, наприклад, `Mathcraft\`.
3. Перенесіть вміст репозиторію в цю папку.
4. Відкрийте консоль (`Win+R` -> `cmd`)
5. Перейдіть в консолі в робочу папку (`cd $path_to_Mathcraft$\Mathcraft`)
6. Створіть віртуальне середовище командою
   ```
   python -m venv venv
   ```
7. Активуйте віртуальне середовище командою
   ```
   venv\Scripts\activate
   ```
8. Установіть необхідні модулі і залежності:
   ```
   pip install -r requirements.txt
   ```
9. Тепер можна запускати компілятор командою
   ```
   python compiler.py
   ```
Налаштування доступні у файлі `settings.py`

# Як налаштувати Google акаунт для підключення інтеграції з Google Forms?
Для того, щоб використовувати інтеграцію із Google Forms, ваш Google-акаунт має бути відповідним чином налаштований.

## Частина 1. Налаштування Google Drive API
1. Залогіньтесь у бажаний Google-акаунт.
2. Перейдіть у [Google Cloud Platform](https://console.cloud.google.com/).
3. Створіть новий проєкт:
![image](https://github.com/user-attachments/assets/cc1d1e36-6d27-4c58-bcff-4d7b248addab)
![image](https://github.com/user-attachments/assets/597c0d95-83d2-455b-942d-81b76bc571d7)
![image](https://github.com/user-attachments/assets/e9fa1e2d-54ac-43f1-8645-f08d4630ce8d)
4. Коли проєкт створиться, переконайтесь, що він обраний як активний:
![image](https://github.com/user-attachments/assets/696ca673-6689-4f20-b28a-62d0223939fa)
5. Перейдіть до розділу `APIs & Services`:
![image](https://github.com/user-attachments/assets/9fd45517-94e9-4393-8a3d-0b8ef3434b25)
   або через бокове меню:
![image](https://github.com/user-attachments/assets/74f525de-e3bc-483d-bd0b-5d87c1d9a52e)
6. Перейдіть у розділ `Library`:   
![image](https://github.com/user-attachments/assets/d5b5a27f-f031-4523-ac86-69e16e5a4108)
7. Знайдіть у бібліотеці Google Drive API і активуйте його:
![image](https://github.com/user-attachments/assets/7f6ee9d6-ded8-432e-a66d-97e4b6b505d1)
![image](https://github.com/user-attachments/assets/73ccb3cb-45f7-415d-863c-dd28e9bfc919)
8. Створіть Service Account:\
![image](https://github.com/user-attachments/assets/a63861ff-558d-41f9-90da-d47806ba7bd2)
![image](https://github.com/user-attachments/assets/f301fbf8-2d8b-4df9-994e-df4216175065)
![image](https://github.com/user-attachments/assets/d00d2fea-ba9b-4c2e-83f1-2fccc6aa12d1)
9. Створіть ключ для цього акаунту:
![image](https://github.com/user-attachments/assets/70e76b3c-3874-47c0-8ca4-df2b54307fc9)
![image](https://github.com/user-attachments/assets/a3bc8ae1-d256-4c94-92db-651f76410050)
10. Завантажений ключ (файл `*.json`) збережіть і розмістіть у папці проєкту у підпапці `key\`.\
Шлях до цього файлу пропишіть у файлі `settings.py` разом із папкою `key\`. Також вкажіть електронну пошту Google-акаунту і змініть параметр `send_to_drive` на `True`.\
Файл `settings.py` має виглядати приблизно так:
   ```
   source_file = "source/source3.txt"      # Source file to compile
   output_filename = "result"              # Without extension
   
   # Compile log settings
   preprocessed_source_log = True
   tokenized_source_log = True
   wait_before_console_quit = True
   
   # Output settings
   csv_output = True                       # for Google Forms integration
   txt_output = True                       # for pretty print
   console_output = True
   
   # Upload settings
   send_to_drive = True                   # upload via Google Drive API
   
   # Sharing settings:
   e_mail = "your_address@gmail.com"
   credentials_file = "key/something_something_something.json"
   ```

## Частина 2. Налаштування Google APPS Script
1. Зайдіть в Google Drive і натисніть кнопку `New`:
![image](https://github.com/user-attachments/assets/f1b72906-b022-4cca-b095-c395fc40a61d)

2. Оберіть створення нового Google Apps Script:
![image](https://github.com/user-attachments/assets/c2dfac80-fe49-438c-84ff-2785829ff320)

3. За потреби погодьтесь із застереженням:
![image](https://github.com/user-attachments/assets/4b4bb0c1-a336-43c1-a171-0ea392456af8)

4. Назвіть проєкт і вставте у редактор код скрипту:
   ```
   function createFormFromLatestCSV() {
     const fileName = "task.csv"; // Стандартна назва файлу із завданням
     const files = DriveApp.searchFiles(`title = '${fileName}' and trashed = false`);
     
     let latestFile = null;
     let latestTime = 0;
   
     // Пошук найновішого файлу з потрібним іменем
     while (files.hasNext()) {
       const file = files.next();
       if (file.getLastUpdated().getTime() > latestTime) {
         latestFile = file;
         latestTime = file.getLastUpdated().getTime();
       }
     }
   
     if (!latestFile) {
       Logger.log('Файл з даними для створення форми не знайдено.');
       return;
     }
   
     Logger.log(`Обробка файлу: ${latestFile.getName()} оновленого ${latestFile.getLastUpdated()}`);
   
     const csvContent = latestFile.getBlob().getDataAsString();
     const rows = Utilities.parseCsv(csvContent);
   
     if (!rows || rows.length === 0) {
       Logger.log('CSV файл порожній або містить некоректні дані.');
       return;
     }
   
     // Створення форми
     const date = new Date();
     const formattedDate = Utilities.formatDate(date, Session.getScriptTimeZone(), "dd-MM-yyyy");
     const form = FormApp.create(`Завдання з математики (${formattedDate})`);
     Logger.log(`Форму створено: ${form.getEditUrl()}`);
   
     rows.forEach((row, index) => {
       if (row.length < 2) return; // Skip rows with insufficient data
   
       const questionText = row[0];
       const answerChoices = row.slice(1);
   
       const item = form.addMultipleChoiceItem();
       item.setTitle(questionText)
           .setChoices(answerChoices.map(choice => item.createChoice(choice)))
           .setRequired(true);
     });
   
     Logger.log('Задачу зі створення форми за даними з CSV файлу успішно виконано.');
   }
   ```
5. Збережіть проєкт:
![image](https://github.com/user-attachments/assets/7fa94b56-1270-49c4-8622-4f61104581e7)
6. Запустіть компілятор:
   ```
   python compiler.py
   ```
   Дочекайтесь, поки завантаження результату компіляції на диск закінчиться (зазвичай це декілька секунд)\
   **!!! Увага, Gmail може відправити перший CSV-файл із завданням у спам, отже це треба перевірити і, у випадку, якщо таке сталось, натиснути кнопку `Not spam`.**
7. Натисніть кнопку `Run`. При першому запуску необхідно надати дозволи:\
![image](https://github.com/user-attachments/assets/019c0848-cc2e-4060-99df-b6140973db66)
![image](https://github.com/user-attachments/assets/fd57506b-8fea-4315-85c4-eab9ed510f10)
![image](https://github.com/user-attachments/assets/951b8d2d-9e63-4d57-be43-46a2e3be19f3)
![image](https://github.com/user-attachments/assets/bcd91e58-4fe1-4718-8b11-2da1e7689b57)
8. Далі скрипт починає працювати і створює форму із завданнями:
![image](https://github.com/user-attachments/assets/d7836280-bbab-423e-a954-992078e79ab8)
9. Ви можете пройти за посиланням на форму, або знайти її серед форм на своєму акаунті:
![image](https://github.com/user-attachments/assets/6fa02f26-365a-4c3a-b7d6-c49f4ee3a1c8)
![image](https://github.com/user-attachments/assets/498fe039-c395-47e0-9bb4-81e663a5e425)
10. Можна налаштувати тригер скрипта на певний період часу, або запускати його вручну.
11. Тепер можна створювати безліч завдань, скрипт завжди буде обробляти найновіший файл.



























   
