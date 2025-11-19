# Debug Checklist - Quick Fixes

## 🔍 Issue: Documents Not Showing

### Check 1: MongoDB Connection

```bash
# In Python terminal or add to app.py temporarily:
from rag_engine import check_db_connection
print(check_db_connection())  # Should return True
```

### Check 2: Vector Search Index

1. Go to MongoDB Atlas → Your Cluster → Search tab
2. Verify index named `default` exists
3. Index should have these settings:
   - Collection: `embeddings`
   - Database: `rag_db`
   - Vector field: `embedding`
   - Dimensions: 768

### Check 3: Query Documents Manually

```python
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["rag_db"]
collection = db["embeddings"]

# Check total documents
print(f"Total docs: {collection.count_documents({})}")

# Check sources
sources = collection.distinct("metadata.source")
print(f"Sources found: {sources}")

# View sample document
sample = collection.find_one()
print(f"Sample doc: {sample}")
```

### Check 4: Test Upload

```bash
# Check Flask logs when uploading
# Should see: "Processing file: filename.pdf"
# Should see: "Successfully processed..."
```

## 🔍 Issue: Chat Not Responding

### Check 1: Ollama Running

```bash
# Check Ollama status
ollama list

# Should show:
# llama3.1
# nomic-embed-text

# If not, install:
ollama pull llama3.1
ollama pull nomic-embed-text
```

### Check 2: Test RAG Function

```python
from rag_engine import get_answer

# Test query
result = get_answer("What is this document about?")
print(result)
# Should return: {"answer": "...", "sources": [...]}
```

### Check 3: Browser Console

1. Open browser DevTools (F12)
2. Go to Console tab
3. Send a message in chat
4. Check for JavaScript errors
5. Check Network tab for `/ask` request status

### Check 4: Flask Terminal

Watch for these messages:

```
Processing query: your question
Response: {'answer': '...', 'sources': [...]}
```

## 🔍 Issue: Upload Not Working

### Check 1: File Type

- Only PDF files are supported
- File must have .pdf extension
- Max size: 50MB

### Check 2: Form Submission

```javascript
// Check in browser console
const formData = new FormData();
formData.append("file", yourFile);

fetch("/upload", {
  method: "POST",
  body: formData,
})
  .then((r) => r.json())
  .then(console.log);
```

### Check 3: Flask Logs

Should see:

```
Processing file: document.pdf
Successfully processed 'document.pdf' into X chunks
```

## 🔍 Quick Test Script

Save as `test_system.py`:

```python
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

print("=" * 50)
print("SYSTEM DIAGNOSTIC TEST")
print("=" * 50)

# Test 1: Environment
print("\n1. Environment Variables:")
mongo_uri = os.getenv("MONGO_URI")
print(f"   MONGO_URI: {'✓ Set' if mongo_uri else '✗ Not set'}")

# Test 2: MongoDB Connection
print("\n2. MongoDB Connection:")
try:
    client = MongoClient(mongo_uri)
    client.admin.command('ping')
    print("   Connection: ✓ Success")

    db = client["rag_db"]
    collection = db["embeddings"]
    count = collection.count_documents({})
    print(f"   Documents: {count} found")

    sources = collection.distinct("metadata.source")
    print(f"   Sources: {len(sources)} files")
    for source in sources:
        print(f"      - {source}")
except Exception as e:
    print(f"   Connection: ✗ Failed - {e}")

# Test 3: Ollama Models
print("\n3. Ollama Models:")
import subprocess
try:
    result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
    if 'llama3.1' in result.stdout:
        print("   llama3.1: ✓ Installed")
    else:
        print("   llama3.1: ✗ Not found")

    if 'nomic-embed-text' in result.stdout:
        print("   nomic-embed-text: ✓ Installed")
    else:
        print("   nomic-embed-text: ✗ Not found")
except:
    print("   Ollama: ✗ Not running or not installed")

# Test 4: Vector Search Index
print("\n4. Vector Search Index:")
try:
    indexes = list(collection.list_search_indexes())
    if any(idx['name'] == 'default' for idx in indexes):
        print("   Index 'default': ✓ Found")
    else:
        print("   Index 'default': ✗ Not found - CREATE IT!")
except:
    print("   Index check: ✗ Failed")

print("\n" + "=" * 50)
print("TEST COMPLETE")
print("=" * 50)
```

Run with:

```bash
python test_system.py
```

## 🛠️ Common Fixes

### Fix 1: Recreate Virtual Environment

```bash
rm -rf venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Fix 2: Clear Browser Cache

1. Press Ctrl+Shift+Delete
2. Clear cache and cookies
3. Reload page

### Fix 3: Reset MongoDB Collection

```python
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["rag_db"]
collection = db["embeddings"]

# Clear all documents (WARNING: This deletes all data!)
collection.delete_many({})
print("Collection cleared. Re-upload your documents.")
```

### Fix 4: Check Port Availability

```bash
# Check if port 5000 is in use
lsof -i :5000  # On Mac/Linux
netstat -ano | findstr :5000  # On Windows

# Kill process if needed
kill -9 <PID>  # On Mac/Linux
```

## 📞 Still Having Issues?

1. **Check Flask terminal** for error messages
2. **Check browser console** (F12) for JavaScript errors
3. **Verify `.env` file** has correct MONGO_URI
4. **Test `/health` endpoint**: http://localhost:5000/health
5. **Run test script**: `python test_system.py`

## ✅ Verification Steps

After fixing:

1. Upload a test PDF ✓
2. Check Dashboard shows the document ✓
3. Go to Chat and ask a question ✓
4. Verify you get a response with sources ✓

If all steps pass, your system is working correctly! 🎉
