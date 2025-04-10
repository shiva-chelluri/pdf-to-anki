

# Introduction
This class uses Google's Generative AI API and Datalab's OCR+LLM API to take in PDFs of lecture notes, slides, etc. and generate a CSV file that can be imported to any quizlet software, such as Anki. To use this repository, you must create your own Google AI Studio API key (which has a free tier).

I recommend that users use their GPUs with CUDA support or Google Colaboratory-like GPU environments instead. Due to the heavy usage of LLMS, these provide much faster conversion than traditional CPU runtimes. There is only a single class, and usage of the code is quite self-explanatory due to its simple nature.
