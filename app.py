from flask import Flask, render_template, request, jsonify
from rag_engine import process_document, get_answer, get_all_documents
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/documents')
def documents():
    docs = get_all_documents()
    return render_template('documents.html', docs=docs)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        if file and file.filename.endswith('.pdf'):
            try:
                num_chunks = process_document(file, file.filename)
                return jsonify({"message": f"Successfully processed {file.filename} into {num_chunks} chunks."}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        else:
            return jsonify({"error": "Only PDF files are supported in this MVP"}), 400
            
    return render_template('upload.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    query = data.get('query')
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        response = get_answer(query)
        return jsonify(response)
    except Exception as e:
        print(e)
        return jsonify({"error": "Error processing request"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)