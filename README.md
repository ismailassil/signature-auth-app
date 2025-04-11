# Signature Authentication App

This application allows users to verify the authenticity of handwritten and electronic signatures using AI and hash-based verification techniques.

---

## Features

- **Handwritten Signature Verification**: Compares uploaded signatures against a database of authentic signatures.
- **E-Signature Verification**: Checks the authenticity of electronic signatures using cryptographic hash comparison.
- **User-Friendly Interface**: Simple and intuitive UI for uploading and verifying signatures.

---

## Installation

### Prerequisites

- Python 3.10 or higher
- Virtual environment (optional but recommended)
- Required Python libraries (see below)

### Steps

1. Clone the repository:

```bash
git clone https://github.com/ismailassil/signature-auth-app.git
cd signature-auth-app

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python main.py
```

### Note

In the `db_signatures` folder put authentic, high-quality images of the signatures in either PNG or JPEG format.
