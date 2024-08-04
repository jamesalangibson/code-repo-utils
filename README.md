# python.development-tools.utils

Collection of tools developed for working on python projects

## Repository Tools

### Print Repository

When working with large language models to build code, different problems in the development process arise.
1. Sometimes the context window becomes so large that the LLM starts to forget earlier instructions.
2. The LLM may not be able to understand the structure of the code.
3. The LLM may not be able to understand the context of the code.
4. Your code has gone through so many revisions that you can't make sense of the discussion with the LLM and it easier to start from scratch.

This tool is designed to address these problems. 

It generates a text file containing the structure and contents of a Python project. 
It's useful for creating a snapshot of your project's code including the directory tree structure. 

More details are available in the [README.md](./repository_tools/print_repository/README.md) file.
