TEX=pdflatex
OUTPUT_DIR=../media/generated_pdfs

all:
	@if [ -z "$(file)" ]; then \
		echo "Error: file variable is not set"; \
		exit 1; \
	else \
		echo "Compiling $(file) into $(OUTPUT_DIR)"; \
		$(TEX) -output-directory=$(OUTPUT_DIR) $(file); \
	fi

clean:
	rm -rf $(OUTPUT_DIR)/*.aux $(OUTPUT_DIR)/*.log $(OUTPUT_DIR)/*.out
