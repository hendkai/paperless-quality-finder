import requests
from tqdm import tqdm

# Konfiguration
API_URL = 'http://yourpaperlessserver:port/api'
API_TOKEN = 'YOURPAPERLESSAPITOKEN'
LIMIT = 20  # Limit der Dokumente pro Anfrage
SEARCH_QUERY = 'Entgelt'  # Suchanfrage

# Lade die Wortliste
with open('german.dic', 'r', encoding='iso-8859-1') as file:
    valid_words = set(word.strip().lower() for word in file.readlines())

def fetch_all_tags():
    headers = {'Authorization': f'Token {API_TOKEN}'}
    response = requests.get(f'{API_URL}/tags/', headers=headers)
    if response.status_code == 200:
        return response.json()['results']
    else:
        print(f"Fehler beim Abrufen der Tags, Statuscode: {response.status_code}")
        return []

def select_tag(tags):
    print("Verfügbare Tags:")
    for tag in tags:
        print(f"ID: {tag['id']}, Name: {tag['name']}")
    tag_id = int(input("Bitte geben Sie die ID des Tags ein, den Sie verwenden möchten: "))
    return tag_id

def get_document_content(document_id):
    headers = {'Authorization': f'Token {API_TOKEN}'}
    response = requests.get(f'{API_URL}/documents/{document_id}/text/', headers=headers)
    if response.status_code == 200:
        try:
            content = response.json().get('text', '')
            return content
        except ValueError:
            print(f"Kein JSON-Inhalt gefunden für Dokument {document_id}. Möglicherweise ist der Textinhalt leer.")
            return ""
    else:
        print(f"Fehler beim Abrufen des Inhalts für Dokument {document_id}, Statuscode: {response.status_code}")
        return ""

def is_content_valid(content, valid_words):
    words = content.lower().split()
    total_word_count = len(words)
    valid_word_count = sum(1 for word in words if word in valid_words)
    
    # Das Dokument soll getaggt werden, wenn mehr als 50% der Wörter ungültig sind
    return valid_word_count / total_word_count < 0.5 if total_word_count > 0 else False

def tag_document_as_low_quality(document_id, tag_id):
    headers = {'Authorization': f'Token {API_TOKEN}', 'Content-Type': 'application/json'}
    data = {"tags": [tag_id]}
    response = requests.patch(f'{API_URL}/documents/{document_id}/', json=data, headers=headers)
    if response.status_code != 200:
        print(f"Fehler beim Taggen des Dokuments {document_id}, Statuscode: {response.status_code}")

def get_documents(page, search_query):
    headers = {'Authorization': f'Token {API_TOKEN}'}
    params = {'limit': LIMIT, 'offset': (page - 1) * LIMIT, 'query': search_query}
    response = requests.get(f'{API_URL}/documents/', headers=headers, params=params, timeout=30)
    if response.status_code == 200:
        data = response.json()
        print(f"Seite {page} erfolgreich abgerufen, {len(data['results'])} Dokumente gefunden.")
        return data['results']
    else:
        print(f"Fehler beim Abrufen der Dokumente, Statuscode: {response.status_code}")
        return []

def process_documents(tag_id, valid_words):
    page = 1
    while True:
        documents = get_documents(page, SEARCH_QUERY)
        if not documents:
            print("Keine weiteren Dokumente zum Analysieren gefunden.")
            break
        for doc in tqdm(documents, desc=f"Seite {page} verarbeiten"):
            doc_id = doc["id"]
            content = get_document_content(doc_id)
            if not is_content_valid(content, valid_words):
                tag_document_as_low_quality(doc_id, tag_id)
        page += 1

def main():
    tags = fetch_all_tags()
    if tags:
        tag_id = select_tag(tags)
        print(f"Sie haben den Tag mit der ID {tag_id} ausgewählt.")
        process_documents(tag_id, valid_words)
    else:
        print("Keine Tags verfügbar.")

if __name__ == '__main__':
    main()
