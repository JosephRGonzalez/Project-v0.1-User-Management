# Makefile for PDF generation

# Configuration
LATEX=pdflatex
TEMPLATE_DIR=templates/latex
OUTPUT_DIR=media/generated_pdfs

# Generate PDF from LaTeX template
generate_pdf:
	@mkdir -p $(OUTPUT_DIR)
	@$(LATEX) -output-directory=$(OUTPUT_DIR) $(TEMPLATE_DIR)/$(TEMPLATE)
	@echo "Generated PDF: $(OUTPUT_DIR)/$(basename $(TEMPLATE)).pdf"

# Clean up auxiliary files
clean:
	@rm -f $(OUTPUT_DIR)/*.aux $(OUTPUT_DIR)/*.log $(OUTPUT_DIR)/*.out