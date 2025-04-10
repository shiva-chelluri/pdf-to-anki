from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.config.parser import ConfigParser
import google.generativeai as genai


class PDFToQACSVConverter:
    """
    Converts a PDF document to a CSV file with Anki
    suitable questions and answers
    """

    def __init__(self, pdf_file_path, gemini_api_key, prompt, model="gemini-2.5-pro-preview-03-25"):
        self.pdf_file_path = pdf_file_path
        self.api_key = gemini_api_key
        self.model = model
        self.prompt = prompt

    def convert_pdf_to_markdown(self) -> str:
        """
        This method converts a PDF document to a Markdown file
        so that it can be parsed into an LLM. It uses Datalab's API
        for using OCR+LLMs to achieve very good performance for
        preserving mathematical notation
        :return: text
        """
        config = {
            "output_format": "markdown",
            "llm_model": self.model,
            "GEMINI_API_KEY": self.api_key
        }
        config_parser = ConfigParser(config)
        converter = PdfConverter(
            config=config_parser.generate_config_dict(),
            artifact_dict=create_model_dict(),
            processor_list=config_parser.get_processors(),
            renderer=config_parser.get_renderer(),
            llm_service=config_parser.get_llm_service()
        )
        text, _, images = converter(self.pdf_file_path)
        return text

    def generate_qa_csv(self, markdown_text):
        prompt = self.prompt
        if prompt is None:
            prompt = (f""" You are an expert AI assistant specializing in creating study materials for advanced 
            university students. The following text was extracted from PDF lecture notes/slides for a third-year 
            Economics course, at a top British University. The student is aiming for a high first-class mark (80%+).
            
            Your task is to generate high-quality question-and-answer pairs suitable for flashcards (like Anki) covering 
            ALL essential concepts, definitions, theorems, proofs, mathematical derivations, formulas, and key examples 
            from the provided text.
            Instructions: 
            1.  **Comprehensiveness:** Cover all core academic content thoroughly. 
            2.  **Conciseness:**  Omit redundant information, introductory/concluding remarks, bibliographies/references 
            (unless critical to understanding a concept, e.g., citing a specific theorem name), and trivial statements. 
            Focus on the substantive material. 
            3.  **Format:** Generate the output STRICTLY as semi-colon-separated values (CSV) data with ONLY two columns
            : "questions" and "answers". Do NOT include a header row. Each row should represent one Q&A pair. 
            4.  **Math Formatting (CRITICAL):** Ensure ALL mathematical formulas, variables, and symbols are correctly 
            enclosed in LaTeX delimiters suitable for Anki: * Use \\( ... \\) for INLINE math (e.g., \\( E[X] = \mu \\)) 
                * Use \\[ ... \\] for DISPLAY/BLOCK equations (e.g., \\[ f(x) =  a_i x^i \\]). 
                * Pay close attention to subscripts, superscripts, Greek letters, fractions, integrals, sums, etc., 
                and ensure they are correctly represented in LaTeX within the delimiters. 
            5.  **Quoting:** If a question or answer contains a comma, enclose the entire field in double quotes . 
            If a field contains double quotes, escape them with another double quote (e.g., "He said ""hello""). 
            Standard CSV quoting rules apply. 
            6.  **Question Style:** Questions should prompt recall or understanding of specific concepts, definitions, 
            formulas, or steps in a derivation. They should be clear and unambiguous. 
            7.  **Answer Style:** Answers should be accurate, concise, and directly address the question. For 
            derivations or proofs, outline the key steps or the final result as appropriate. 
            8. **Prohibited Symbols:** Since this will be a semi-colon separated CSV. DO NOT USE ";" symbol 
            at all.

            **Input Text:**
            ```markdown
            {markdown_text}
            ```
            **Output (CSV format, no header):**
            """)
        else:
            prompt = f"{prompt}+{markdown_text}"
        # Configure the API
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model)

        response = model.generate_content(prompt)
        response_text = response.text

        return response_text

    def process(self, output_csv_path="output.csv"):
        markdown_text, _ = self.convert_pdf_to_markdown()
        csv_content = self.generate_qa_csv(markdown_text)
        with open(output_csv_path, "w") as f:
            f.write(csv_content)
        print(f"CSV file saved to {output_csv_path}")
