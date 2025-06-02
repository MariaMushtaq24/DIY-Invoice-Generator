import streamlit as st
import uuid
from fpdf import FPDF

st.set_page_config(page_title="DIY Invoice Generator", page_icon="🧾")

# Session-based invoice list
if "invoices" not in st.session_state:
    st.session_state.invoices = []

# PDF export function
def export_pdf(invoice):
    # Custom size: width=130mm, height=150mm
    pdf = FPDF(unit="mm", format=(130, 160))
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    # Colors and styles
    heading_color = (0, 51, 102)
    bg_color = (245, 245, 245)

    # Title section
    pdf.set_fill_color(*bg_color)
    pdf.set_text_color(*heading_color)
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 12, f"Invoice #{invoice['id']}", ln=True, align="C", fill=True)

    pdf.ln(5)

    def add_row(label, value):
        pdf.set_font("Helvetica", 'B', 11)
        pdf.set_text_color(50, 50, 50)
        pdf.cell(35, 8, f"{label}", ln=0)
        pdf.set_font("Helvetica", '', 11)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 8, f"{value}")

    add_row("Client:", invoice['client'])
    add_row("Service:", invoice['description'])
    add_row("Quantity:", f"{invoice['quantity']} {invoice.get('unit', '')}")
    add_row("Rate per Unit:", f"{invoice['currency']} {invoice['rate']}")

    # Highlighted total
    pdf.ln(3)
    pdf.set_font("Helvetica", 'B', 11)
    pdf.set_fill_color(230, 230, 250)
    pdf.cell(35, 8, "Total:", fill=True)
    pdf.cell(0, 8, f"{invoice['currency']} {invoice['total']}", fill=True, ln=True)

    # Footer note
    pdf.set_y(135)  # Place near bottom (custom height = 150)
    pdf.set_font("Helvetica", 'I', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "Thank you!", ln=True, align='C')


    filename = f"invoice_{invoice['id']}.pdf"
    pdf.output(filename)
    return filename

st.title("🧾 DIY Invoice Generator")

# Currency options
currency_options = ["USD", "PKR", "EUR", "GBP", "CAD", "JPY", "INR"]
default_currency = "PKR"

# Invoice Form
with st.form("invoice_form"):
    client = st.text_input("Client Name")
    description = st.text_input("Service Description")
    unit = st.text_input("Unit (e.g., hours, words, articles, items)")
    quantity = st.number_input("Quantity", min_value=1.0, value=1.0)
    rate = st.number_input("Rate per unit", min_value=0.0, value=0.0)
    currency = st.selectbox("Currency", currency_options, index=currency_options.index(default_currency))
    submitted = st.form_submit_button("Generate Invoice")

    if submitted:
        if client and description:
            total = quantity * rate
            invoice_id = str(uuid.uuid4())[:8]
            invoice = {
                "id": invoice_id,
                "client": client,
                "description": description,
                "unit": unit,
                "quantity": quantity,
                "rate": rate,
                "currency": currency,
                "total": total
            }
            st.session_state.invoices.append(invoice)
            st.success(f"Invoice #{invoice_id} created!")
        else:
            st.error("Please enter all fields.")

# Display Invoices
if st.session_state.invoices:
    st.header("📜 Generated Invoices")
    for inv in reversed(st.session_state.invoices):
        with st.expander(f"Invoice #{inv['id']} — {inv['client']} — {inv['currency']} {inv['total']}"):
            st.text(f"Client: {inv['client']}")
            st.text(f"Description: {inv['description']}")
            st.text(f"Quantity: {inv['quantity']} {inv.get('unit', '')}")
            st.text(f"Rate per Unit: {inv['currency']} {inv['rate']}")
            st.text(f"Total: {inv['currency']} {inv['total']}")

            # Export to PDF
            if st.button("📄 Export as PDF", key=inv["id"] + "_pdf"):
                filename = export_pdf(inv)
                with open(filename, "rb") as f:
                    st.download_button(
                        label="Download PDF",
                        data=f,
                        file_name=filename,
                        mime="application/pdf"
                    )

            # Print View
            if st.button("🖨️ Print-Friendly View", key=inv["id"] + "_print"):
                st.markdown(f"""
                <iframe srcdoc='
                    <html>
                    <head>
                    <style>
                        body {{
                            font-family: "Segoe UI", sans-serif;
                            background-color: #f2f2f2;
                            padding: 40px;
                            color: #333;
                        }}
                        .invoice {{
                            background-color: #fff;
                            border: 1px solid #ddd;
                            padding: 30px;
                            max-width: 600px;
                            margin: auto;
                            border-radius: 5px;
                            box-shadow: 0 0 5px rgba(0,0,0,0.05);
                        }}
                        h2 {{
                            color: #003366;
                            text-align: center;
                            margin-bottom: 20px;
                        }}
                        p {{
                            line-height: 1.6;
                        }}
                        strong {{
                            display: inline-block;
                            width: 120px;
                        }}
                    </style>
                </head>
                <body>
                    <div class="invoice">
                        <h2>Invoice #{inv["id"]}</h2>
                        <p><strong>Client:</strong> {inv["client"]}</p>
                        <p><strong>Description:</strong> {inv["description"]}</p>
                        <p><strong>Quantity:</strong> {inv["quantity"]} {inv.get("unit", "")}</p>
                        <p><strong>Rate per Unit:</strong> {inv["currency"]} {inv["rate"]}</p>
                        <p><strong>Total:</strong> {inv["currency"]} {inv["total"]}</p>
                    </div>
                </body>
                </html>' width="100%" height="500"></iframe>
                """, unsafe_allow_html=True)

else:
    st.info("No invoices yet. Fill the form to create one.")