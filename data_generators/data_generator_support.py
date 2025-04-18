import json
import os
import csv
import argparse
import ollama
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit
from tqdm import tqdm
import random
from datetime import datetime

OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_text(prompt):
    try:
        response = ollama.chat(model="llama3.2:1b", messages=[{"role": "user", "content": prompt}])
        return response.get("message", {}).get("content", "No response generated.").strip()
    except Exception as e:
        print(f"ERROR: Can't generate response for prompt '{prompt}'. Reason: {e}")
        return "Error generating text."

def generate_product_ideas(num_products):
    idea_prompt = f"Generate {num_products} unique, realistic home appliance product names. Provide only the names, separated by commas, with no extra text."
    ideas_text = generate_text(idea_prompt)
    ideas = [idea.strip() for idea in ideas_text.split(",") if idea.strip()]

    if len(ideas) < num_products:
        print("Warning: AI did not generate enough product names. Filling with placeholders.")
        ideas += [f"Product {i}" for i in range(len(ideas) + 1, num_products + 1)]

    return ideas[:num_products]

def create_pdf(text, filename):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    margin = 50
    line_height = 14

    lines = simpleSplit(text, "Helvetica", 12, width - 2 * margin)
    y = height - margin
    c.setFont("Helvetica", 12)
    c.drawString(margin, y, "Product description")
    y -= line_height * 2

    for line in lines:
        if y < margin:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = height - margin
        c.drawString(margin, y, line)
        y -= line_height

    c.save()

def create_csv(data, filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Product Name", "Category", "Price", "Stock"])
        for row in data:
            writer.writerow(row)
    print(f"CSV dataset saved as '{filepath}'")

def generate_data(generate_pdfs=True, generate_csv=True, num_products=5):
    print("Generating product ideas...")
    product_ideas = generate_product_ideas(num_products)
    csv_data = []

    for i, product_name in enumerate(tqdm(product_ideas, desc="Processing Products"), start=1):
        product_description = generate_text(f"Generate a concise and realistic product description for: {product_name}")

        if generate_pdfs:
            pdf_filename = os.path.join(OUTPUT_DIR, f"utility_product_{i}.pdf")
            create_pdf(product_description, filename=pdf_filename)

        if generate_csv:
            csv_row = [product_name, "Appliances", f"${round(99 + i * 10, 2)}", i * 5]
            csv_data.append(csv_row)

    if generate_csv:
        create_csv(csv_data, "salesforce_export.csv")
    print("Product data generation complete.")

def generate_support_requests(num_requests=10):
    print("Generating customer support requests...")
    support_requests = []
    priorities = ["Low", "Medium", "High"]

    for i in range(1, num_requests + 1):
        ticket_id = f"TICKET-{1000 + i}"
        customer_id = f"CUST-{random.randint(1000, 9999)}"
        timestamp = datetime.now().isoformat()
        priority = random.choice(priorities)

        prompt = (
            "Generate a realistic customer support request with a subject and detailed description. "
            "Provide a short subject line on the first line and a detailed description on subsequent lines."
        )
        generated_text = generate_text(prompt)
        lines = generated_text.split("\n")
        if len(lines) >= 2:
            subject = lines[0].strip()
            description = "\n".join(line.strip() for line in lines[1:] if line.strip())
        else:
            subject = generated_text[:50]
            description = generated_text

        support_request = {
            "ticket_id": ticket_id,
            "customer_id": customer_id,
            "timestamp": timestamp,
            "priority": priority,
            "subject": subject,
            "description": description
        }
        support_requests.append(support_request)

    return support_requests

def save_support_requests_json(support_requests, filename="support_requests.json"):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(support_requests, f, indent=4)
    print(f"Support requests JSON dataset saved as '{filepath}'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate PDFs and CSV datasets for random utility products, and JSON customer support requests."
    )
    parser.add_argument("--pdf", action="store_true", help="Generate PDFs for product descriptions")
    parser.add_argument("--csv", action="store_true", help="Generate CSV dataset for products")
    parser.add_argument("--json", action="store_true", help="Generate JSON dataset for customer support requests")
    parser.add_argument("--num", type=int, default=5, help="Number of products to generate")
    parser.add_argument("--requests", type=int, default=10, help="Number of customer support requests to generate")

    args = parser.parse_args()

    generate_data(generate_pdfs=args.pdf, generate_csv=args.csv, num_products=args.num)

    if args.json:
        support_requests = generate_support_requests(num_requests=args.requests)
        save_support_requests_json(support_requests)