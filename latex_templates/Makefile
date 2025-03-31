TEX=pdflatex
OUTPUT_DIR=../media/generated_pdfs

all: thesis withdrawal

# Generate thesis PDF only if the corresponding .tex file exists
thesis:
	@if ls thesis_filled_*.tex 1> /dev/null 2>&1; then \
		$(TEX) -output-directory=$(OUTPUT_DIR) thesis_filled_*.tex; \
	else \
		echo "No thesis form to process."; \
	fi

# Generate withdrawal PDF only if the corresponding .tex file exists
withdrawal:
	@if ls withdrawal_filled_*.tex 1> /dev/null 2>&1; then \
		$(TEX) -output-directory=$(OUTPUT_DIR) withdrawal_filled_*.tex; \
	else \
		echo "No withdrawal form to process."; \
	fi

clean:
	rm -rf $(OUTPUT_DIR)/*.aux $(OUTPUT_DIR)/*.log $(OUTPUT_DIR)/*.out
