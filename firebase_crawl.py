import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd

# --- 1. INITIALIZE FIREBASE ADMIN SDK ---
cred = credentials.Certificate("service-account.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# --- 2. DEFINE YOUR QUERY ---
# Example: Get all users from the 'users' collection where 'country' is 'USA'
docs = db.collection('cart').stream()

# --- 3. PROCESS DOCUMENTS AND CREATE A PANDAS DATAFRAME ---
data = []
for doc in docs:
    doc_data = doc.to_dict()
    doc_data['id'] = doc.id  # Add the document ID to the dictionary
    data.append(doc_data)

if not data:
    print("No documents found.")
else:
    df = pd.DataFrame(data)

    # --- 4. SAVE THE DATAFRAME TO A CSV FILE ---
    file_name = 'firestore_export_order.csv'
    df.to_csv(file_name, index=False)
    print(f"✅ Data successfully exported to {file_name}")