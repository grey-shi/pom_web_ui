import hashlib

text = "morphogo123"
sha256_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
print(sha256_hash)