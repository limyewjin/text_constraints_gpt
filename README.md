# Text Constraints GPT

Text Constraints GPT is a project that enhances the OpenAI GPT model by integrating constraint-based interactions. The goal is to enable users to request the AI model to generate text that adheres to specific constraints such as word count, character limits, or restrictions on punctuation, letters, or word order. The project uses both spaCy and nltk libraries for text processing and validation.

## Features

- User-defined constraints on text generation
- Integration with spaCy and nltk libraries for text processing and validation
- Coherent and relevant text generation based on user input

## Installation

Ensure you have Python 3.6+ installed on your system. Then, install the required libraries:

```bash
pip install spacy nltk openai
```

Download the required spaCy model:

```bash
python -m spacy download en_core_web_trf
```

## Usage
To run the project, execute the main.py script:

```bash
python main.py
```

When prompted, provide a user input with the desired constraints for text generation. For example:

```
User: write a poem about spring using 12 words
```

The AI model will then generate a response that adheres to the specified constraints.

## Commands
Commands allow you to verify whether the generated text meets the given constraints. Use the following syntax to execute commands:

EXECUTE SPACY: for spaCy commands

EXECUTE NLTK: for nltk commands

For example:

```
EXECUTE NLTK: word_count Spring brings about new life, Flowers bloom, birds sing, Warm sunshine, new beginnings.
```

Allowed commands include:

spaCy commands: [list allowed spaCy commands here]
nltk commands: [list allowed nltk commands here]

## License
This project is licensed under the MIT License.
