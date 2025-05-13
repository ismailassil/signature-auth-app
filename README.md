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

- Python 3.10 or Python 3.11 (3.11 is recommended)
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

---

## How It Works

The Signature Authentication App uses advanced AI and machine learning techniques to verify the authenticity of signatures. Here's an overview of the process:

1. **Preprocessing**:

    - Uploaded signature images are resized to a standard resolution (e.g., 50x50 pixels) to ensure uniformity.
    - Noise and artifacts are removed to enhance the quality of the image.

2. **Feature Extraction**:

    - The AI model extracts unique features from the signature, such as stroke patterns, pressure points, and overall structure.
    - These features are compared against a database of authentic signatures.

3. **Forgery Detection**:

    - The model uses a combination of convolutional neural networks (CNNs) and statistical analysis to identify discrepancies between the uploaded signature and authentic samples.
    - Key factors include:
        - Shape and alignment differences.
        - Variations in stroke consistency.
        - Unnatural patterns indicative of forgery.

4. **Verification**:
    - The app provides a confidence score indicating the likelihood of the signature being authentic.
    - If the score falls below a certain threshold, the signature is flagged as potentially forged.

---

## AI Model for Forgery Detection

The AI model is trained on a diverse dataset of real and forged signatures. The training process involves:

- **Data Augmentation**: Enhancing the dataset with variations in rotation, scaling, and noise to improve model robustness.
- **Supervised Learning**: Using labeled data to teach the model to distinguish between real and forged signatures.
- **Evaluation**: Testing the model on unseen data to ensure high accuracy and reliability.

By leveraging these techniques, the app achieves a high level of precision in detecting forged signatures, making it a reliable tool for authentication.

## Using the Signature Verification App

1. **Launch the App**: Start the application to access the dashboard.

2. **Upload a Signature**: Click the "Upload Image" button to select a signature image from your device. Ensure the image is in PNG, JPG, or JPEG format.

3. **Verify the Signature**: Once the image is uploaded, click the "Verify with DB" button. The app will compare the uploaded signature against the database of authentic and forged signatures.

4. **View Results**: The app will display whether the signature is authentic, forged, or unknown, along with a confidence score.

5. **User Guide**: If needed, click the "User Guide" button for detailed instructions.

6. **About**: Click the "?" button to view information about the app creators.
