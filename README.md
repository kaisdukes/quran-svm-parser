# Quran SVM Parser

*Join us on a new journey! Visit the [Corpus 2.0 upgrade project](https://github.com/kaisdukes/quranic-corpus) for new work on the Quranic Arabic Corpus.*

## What's in this Repo?

The original Quranic Arabic Corpus parser using SVM-based machine learning, from [Dukes & Habash's 2011 paper](https://github.com/kaisdukes/quran-svm-parser/blob/main/W11-2912.pdf). 

With contributions from volunteer Machine Learning engineers and Data Scientists, we've separated the parser code from the main Quranic Arabic Corpus codebase and released this as open source. The original SVM parser is now a standalone, lightweight module, converted from Java code written in 2011 to modern Python. To work with this codebase, you will need a strong background in Artificial Intelligence applied to Quranic Research, specifically in the fields of Computational Linguistics and Natural Language Processing (NLP).

The purpose of this repo is to serve as a baseline for new neural AI models, with the aim of more accurate, deeper linguistic analysis of the original Classical Arabic text of the Quran, in combination with expert human review and supervision.

For a deeper understanding of the existing SVM parser, we recommend Chapters 9 and 10 of Dr. Dukes’ PhD thesis: *[Statistical Parsing by Machine Learning from a Classical Arabic Treebank](https://arxiv.org/pdf/1510.07193.pdf)*.

## Please Use Official APIs and Avoid Distributing Draft Data

The Quranic Arabic Corpus provides comprehensive linguistic annotation for each word in the Quran based on authentic traditional sources, while respecting its deep cultural significance. Linguistic analysis of the Quran requires expert knowledge and is subject to continual refinement and improvement. The code in this repository uses official Corpus APIs to locally cache the Quranic Treebank. Given the constant refinement by our Linguistic Team and our partner universities, we kindly ask to avoid redistributing this draft data. Please promote the use of official APIs to ensure users alway have the most up-to-date and accurate data available.

## Getting Started

This project uses [Poetry](https://python-poetry.org) to manage package dependencies.

First, clone the repository:

```
git clone https://github.com/kaisdukes/quran-svm-parser.git
cd quran-svm-parser
```

Install Poetry using [Homebrew](https://brew.sh):

```
brew install poetry
```

Next, install project dependencies:

```
poetry install
```

All dependencies, such as [Requests](https://requests.readthedocs.io/en/latest) and [Pydantic](https://github.com/pydantic/pydantic), are installed in the virtual environment.

Use the Poetry shell:

```
poetry shell
```

Test the parser:

```
python tests/parser_test.py
```