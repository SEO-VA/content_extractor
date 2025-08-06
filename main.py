from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

class ContentExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def extract_content(self, url):
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            content_parts = []
            
            # Find main container
            main_container_selectors = ['article', 'main', '.content', '#content', '[role="main"]']
            main_container = None
            for selector in main_container_selectors:
                main_container = soup.select_one(selector)
                if main_container: 
                    break
            
            if not main_container:
                if len(soup.find_all('p')) > 3: 
                    main_container = soup.find_all('p')[0].parent
                else: 
                    main_container = soup.body
            
            # Extract H1 tags
            for h1 in soup.find_all('h1'):
                text = h1.get_text(separator='\n', strip=True)
                if text: 
                    content_parts.append(f'H1: {text}')
            
            # Extract subtitles
            for st_element in soup.select('.sub-title,.subtitle,[class*="sub-title"],[class*="subtitle"]'):
                text = st_element.get_text(separator='\n', strip=True)
                if text: 
                    content_parts.append(f'SUBTITLE: {text}')
            
            # Extract lead paragraphs
            for lead in soup.select('.lead,[class*="lead"]'):
                text = lead.get_text(separator='\n', strip=True)
                if text: 
                    content_parts.append(f'LEAD: {text}')
            
            # Extract main content
            if main_container:
                main_text = main_container.get_text(separator='\n', strip=True)
                if main_text: 
                    content_parts.append(f'CONTENT: {main_text}')
            
            return True, '\n\n'.join(content_parts) or "No content found", None
            
        except requests.RequestException as e:
            return False, None, f"Error fetching URL: {e}"

@app.route('/')
def home():
    return {"status": "Content Extractor API is running", "usage": "POST to /extract with {'url': 'https://example.com'}"}

@app.route('/extract', methods=['POST'])
def extract_content():
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({"success": False, "error": "URL is required"}), 400
        
        url = data['url']
        extractor = ContentExtractor()
        success, content, error = extractor.extract_content(url)
        
        if success:
            return jsonify({
                "success": True,
                "extracted_content": content,
                "content_length": len(content)
            })
        else:
            return jsonify({
                "success": False,
                "error": error
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
