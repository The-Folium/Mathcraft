from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io
from settings import *

# Налаштування Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = credentials_file
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)


# Файлові операції
def create_folder(folder_name, parent_folder_id=None):
    """Створення папки на Google диску"""
    folder_metadata = {
        'name': folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        'parents': [parent_folder_id] if parent_folder_id else []
    }
    created_folder = drive_service.files().create(
        body=folder_metadata,
        fields='id'
    ).execute()
    print(f'Created Folder ID: {created_folder["id"]}')
    return created_folder["id"]


def list_folder(parent_folder_id=None, delete=False):
    """Список файлів і папок у робочій папці на Google диску"""
    results = drive_service.files().list(
        q=f"'{parent_folder_id}' in parents and trashed=false" if parent_folder_id else None,
        pageSize=1000,
        fields="nextPageToken, files(id, name, mimeType)"
    ).execute()
    items = results.get('files', [])
    if not items:
        print("No folders or files found in Google Drive.")
    else:
        print("Folders and files in Google Drive:")
        for item in items:
            print(f"Name: {item['name']}, ID: {item['id']}, Type: {item['mimeType']}")
            if delete:
                delete_files(item['id'])


def delete_files(file_or_folder_id):
    """Видалення файлу чи папки на Google диску"""
    try:
        drive_service.files().delete(fileId=file_or_folder_id).execute()
        print(f"Successfully deleted file/folder with ID: {file_or_folder_id}")
    except Exception as e:
        print(f"Error deleting file/folder with ID: {file_or_folder_id}")
        print(f"Error details: {str(e)}")


def download_file(file_id, destination_path):
    """Завантаження файлу з Google диску"""
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(destination_path, mode='wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%.")


def upload_file(file_path, file_name, mime_type='text/plain', parent_folder_id=None):
    """Завантаження файлу на Google диску"""
    file_metadata = {
        'name': file_name,
        'parents': [parent_folder_id] if parent_folder_id else []
    }
    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
    file = drive_service.files().create(
        body=file_metadata, media_body=media, fields='id').execute()
    file_id = file.get('id')
    print(f"Uploaded file with ID: {file_id}")
    return file_id


def share_file(drive_service, file_id, user_email):
    """Відкриття доступу до файлу з акаунту користувача"""
    permission = {'type': 'user',
                  'role': 'writer',
                  'emailAddress': user_email}
    drive_service.permissions().create(fileId=file_id, body=permission).execute()


# Основна функція, яка викликається з компілятора
def upload_and_share(file_path, file_name, mime_type='text/plain', parent_folder_id=None):
    file_id = upload_file(file_path, file_name)
    share_file(drive_service, file_id, e_mail)
