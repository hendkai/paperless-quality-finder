
# Paperless Quality Finder

[![GitHub issues](https://img.shields.io/github/issues/hendkai/paperless-quality-finder)](https://github.com/hendkai/paperless-quality-finder/issues)
[![GitHub stars](https://img.shields.io/github/stars/hendkai/paperless-quality-finder)](https://github.com/hendkai/paperless-quality-finder/stargazers)
[![GitHub license](https://img.shields.io/github/license/hendkai/paperless-quality-finder)](https://github.com/hendkai/paperless-quality-finder/blob/main/LICENSE)

A tool to tag low-quality documents in a Paperless NG or Paperless-NGX instance based on the content quality.

## Features

- Tags low-quality documents based on content quality.
- Uses a German dictionary to check the quality of text content.
- Customizable threshold for tagging documents.

## Getting Started

To get started, follow these steps:

1. Clone this repository:

   ```bash
   git clone https://github.com/hendkai/paperless-quality-finder.git
   ```

2. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure the script by editing the `config.py` file.

4. Run the script:

   ```bash
   python main.py
   ```

5. Follow the prompts to select a tag and set the threshold.

## Configuration

In the `config.py` file, you can configure the following settings:

- `API_URL`: The URL of your Paperless NG or Paperless-NGX instance.
- `API_TOKEN`: Your API token for authentication.
- `TAG_ID_FOR_LOW_QUALITY`: The ID of the tag to apply to low-quality documents.
- `THRESHOLD`: The threshold percentage for tagging documents.
- `SEARCH_QUERY`: The search query to find documents for analysis.
- `LIMIT`: The limit of documents to retrieve per request.

## Usage

The script will analyze the content of documents and tag them if the percentage of non-German words exceeds the threshold. You can customize the threshold and the tag to apply.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
