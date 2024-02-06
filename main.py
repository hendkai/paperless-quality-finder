import requests
import re
from tqdm import tqdm

# Configuration
API_URL = 'http://yourpaperlessserver:port/api'
API_TOKEN = 'YOURPAPERLESSAPITOKEN'
LIMIT = 1  # Limit of documents per request
SEARCH_QUERY = 'Entgelt'  # Search query
VALID_PERCENTAGE_THRESHOLD = 50.0  # Adjust the threshold as needed

def load_word_list(file_path):
    with open(file_path, 'r', encoding='iso-8859-1') as file:
        total_lines = sum(1 for line in file)
        file.seek(0)  # Reset the file pointer to the beginning
        valid_words = set(tqdm((word.strip().lower() for word in file), total=total_lines, desc="Loading word list"))
    return valid_words

valid_words = load_word_list('german.dic')

def fetch_all_tags():
    headers = {'Authorization': f'Token {API_TOKEN}'}
    response = requests.get(f'{API_URL}/tags/', headers=headers)
    return response.json()['results'] if response.status_code == 200 else []

def select_tag(tags):
    print("Available tags:")
    for tag in tags:
        print(f"ID: {tag['id']}, Name: {tag['name']}")
    tag_id = int(input("Please enter the ID of the tag you want to use: "))
    return tag_id

def get_document_content(document_id):
    headers = {'Authorization': f'Token {API_TOKEN}'}
    url = f'{API_URL}/documents/{document_id}/'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        content = data.get('content', '')
        tags = data.get('tags', [])
        return content, tags, None if content else "No content available"
    else:
        return "", [], f"Error fetching content for document {document_id}, status code: {response.status_code}"

# Check if the document content is valid based on the word list
def is_content_valid(content, valid_words):
    if not content:
        return False, 0.0  # Content is empty

    # Split the content into words and remove punctuation and whitespace
    words = re.findall(r'\b\w+\b', content.lower())

    # Calculate the percentage of valid words
    total_words = len(words)
    valid_count = sum(1 for word in words if word in valid_words)
    valid_percentage = (valid_count / total_words) * 100 if total_words > 0 else 0.0

    # Determine if the content is valid based on the percentage threshold
    is_valid = valid_percentage >= VALID_PERCENTAGE_THRESHOLD

    return is_valid, valid_percentage

# Tag a document as low quality if it doesn't meet the criteria
def tag_document_as_low_quality(document_id, tag_id, existing_tags):
    if tag_id in existing_tags:
        print(f"Document {document_id} already has the selected tag.")
        return
    headers = {'Authorization': f'Token {API_TOKEN}', 'Content-Type': 'application/json'}
    data = {"tags": existing_tags + [tag_id]}
    response = requests.patch(f'{API_URL}/documents/{document_id}/', json=data, headers=headers)
    if response.status_code == 200:
        original_file_name = response.json().get('original_file_name', 'N/A')
        print(f"Document {document_id} ({original_file_name}) is matched and tagged.")
    else:
        print(f"Failed to tag document {document_id} as 'low quality'.")

def get_documents(offset, search_query):
    headers = {'Authorization': f'Token {API_TOKEN}'}
    params = {'limit': LIMIT, 'offset': offset, 'query': search_query}
    response = requests.get(f'{API_URL}/documents/', headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return data['results'], data.get('next')
    else:
        print(f"Error fetching documents, status code: {response.status_code}")
        return [], None

# Process documents and tag them if they don't meet the criteria
def process_documents(tag_id, valid_words):
    offset = 0  # Start at the beginning
    more_documents = True  # Flag to keep the loop running

    while more_documents:
        documents, next_offset = get_documents(offset, SEARCH_QUERY)
        if documents:
            for doc in documents:
                document_id = doc["id"]
                content, existing_tags, error_message = get_document_content(document_id)
                if error_message:
                    print(error_message)  # Display error message
                    continue  # Skip to the next document
                is_valid, valid_percentage = is_content_valid(content, valid_words)
                if not is_valid:
                    tag_document_as_low_quality(document_id, tag_id, existing_tags)
                else:
                    # Get the original file name and print it
                    original_file_name = doc.get('original_file_name', 'N/A')
                    print(f"Document {document_id} ({original_file_name}) is matched and tagged.")
            offset += len(documents)  # Update offset based on the number of documents processed
        else:
            more_documents = False  # Stop the loop if no documents are returned

def main():
    tags = fetch_all_tags()
    if tags:
        tag_id = select_tag(tags)
        print(f"You have selected tag with ID {tag_id}.")
        process_documents(tag_id, valid_words)
    else:
        print("No tags available.")

if __name__ == '__main__':
    main()
