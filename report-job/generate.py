import os, json
from reportlab.pdfgen import canvas
from azure.storage.blob import BlobServiceClient
from azure.identity import ManagedIdentityCredential

order_id = os.environ["ORDER_ID"]
order = json.loads(os.environ["ORDER_JSON"])
storage_url = os.environ.get("STORAGE_ACCOUNT_URL")
client_id = os.environ.get("AZURE_CLIENT_ID")

pdf_path = f"/tmp/{order_id}.pdf"
c = canvas.Canvas(pdf_path)
c.drawString(100, 800, f"Order Report: {order_id}")
c.drawString(100, 780, f"Items: {len(order['items'])}")
y = 750
for i, item in enumerate(order["items"]):
    c.drawString(100, y, f"  {item['sku']}  x{item['qty']}")
    y -= 20
c.save()

credential = ManagedIdentityCredential(client_id=client_id)
svc = BlobServiceClient(account_url=storage_url, credential=credential)
blob = svc.get_blob_client(container="reports", blob=f"{order_id}.pdf")
with open(pdf_path, "rb") as f:
    blob.upload_blob(f, overwrite=True)
print(f"Uploaded {order_id}.pdf to reports container")
