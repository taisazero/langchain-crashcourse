# 🦜️🔗 Langchain Crash Course
By: Erfan Al-Hossami

This repository provides an introduction to LLMs and the langchain library used to build LLM applications.

## 📚️ Table of Contents
- [🦜️🔗 Langchain Crash Course](#️-langchain-crash-course)
  - [📚️ Table of Contents](#️-table-of-contents)
  - [What is Langchain?](#what-is-langchain)
  - [Installation](#installation)
  - [Intro to Chains Lab](#intro-to-chains-lab)
  - [Building a Simple Agent Lab](#building-a-simple-agent-lab)
  - [Retrieval-based Question Answering Lab](#retrieval-based-question-answering-lab)
  - [Contact](#contact)
  - [References](#references)

## What is Langchain?
Langchain is a library for building LLM applications. It is built on top of [PyTorch](https://pytorch.org/), [HuggingFace's Transformers](https://github.com/huggingface/transformers) libraries, and language model inference API such as the [OpenAI API](https://openai.com/blog/openai-api).

## Installation
To setup for this crash course, you will need to install the following:
1. Anacoda (or Miniconda) [link](https://docs.conda.io/projects/conda/en/latest/user-guide/install/)
2. Then create a new environment with the following command:
```
conda create -n langchain python=3.8
```
3. Activate the environment:
```
conda activate langchain
```
4. Install Dependencies:
```
pip install -r requirements.txt
```
5. Clone this repository:
```
git clone https://github.com/taisazero/langchain-crashcourse.git
```

## Intro to Chains Lab
Go to the [notebook](https://github.com/taisazero/langchain-crashcourse/blob/main/notebooks/1-intro_to_chains_exercise.ipynb) to access this section of the crash course.

## Building a Simple Agent Lab
Go to the [notebook](https://github.com/taisazero/langchain-crashcourse/blob/main/notebooks/2-simple_agent_exercise.ipynb) to access this section of the crash course.

## Retrieval-based Question Answering Lab
In this small project you will build 🤗**HuggingTutor**, an LLM-based application that can answer questions, help resolve errors, and write tutorials about HuggingFace's Transformers library accurately by retrieving answers from the library's documentation.

Go to the [notebook](https://github.com/taisazero/langchain-crashcourse/blob/main/notebooks/3-retrieval_aug_gen_exercise.ipynb) to access this section of the crash course.

## Contact
If you have any questions, please contact me at [erfan.hossami@gmail.com](mailto:erfan.hossami@gmail.com).

## References
This crash course is based on the following resources:
- [LangChain Handbook](https://www.pinecone.io/learn/series/langchain/langchain-intro/)
- [SamurAI's LangChain Course](https://github.com/SamurAIGPT/langchain-course/)
- [LangChain Documentation](https://python.langchain.com)
- [DeepLearning.AI LangChain Course](https://learn.deeplearning.ai/langchain)
