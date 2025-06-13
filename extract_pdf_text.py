import PyPDF2

# Path to the PDF file
pdf_path = r"c:\Users\Fahd\Desktop\ai agent\Unlocking Seamless Supplier Onboarding_ A Step-by-Step AI Agent Blueprint.pdf"

# Open the PDF file
with open(pdf_path, "rb") as file:
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

# Save the extracted text to a file
with open(r"c:\Users\Fahd\Desktop\ai agent\blueprint_extracted.txt", "w", encoding="utf-8") as out_file:
    out_file.write(text)

print("Extraction complete. Text saved to blueprint_extracted.txt.")
cont