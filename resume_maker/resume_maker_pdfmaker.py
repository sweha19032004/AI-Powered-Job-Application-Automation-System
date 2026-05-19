import pdfkit
import docx
import os

class DocxToPDF:
    def __init__(self):
        self.wkhtmltopdf_path =os.getenv(wkhtmltopdfpath)
        self.config = pdfkit.configuration(wkhtmltopdf=self.wkhtmltopdf_path)

    def docx_to_html(self, docx_path):
        """Convert DOCX content to simple HTML."""
        if not os.path.exists(docx_path):
            raise FileNotFoundError(f"File not found: {docx_path}")

        doc = docx.Document(docx_path)
        html_content = "<html><body>"
        for para in doc.paragraphs:
            html_content += f"<p>{para.text}</p>"
        html_content += "</body></html>"

        html_path = "temp_doc.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        return html_path

    def convert_to_pdf(self, docx_path, output_pdf):
        """Convert DOCX to PDF."""
        html_path = self.docx_to_html(docx_path)
        pdfkit.from_file(html_path, output_pdf, configuration=self.config)
        os.remove(html_path)
