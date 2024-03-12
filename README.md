# LexDrafter: Terminology Drafting for Legislative Documents using Retrieval Augmented Generation

Ashish Chouhan and Michael Gertz  
Heidelberg University
contact us at: [`{chouhan, gertz}@informatik.uni-heidelberg.de`](mailto:chouhan@informatik.uni-heidelberg.de)

A [pre-print](https://arxiv.org/abs/xxxxx) of our work is available; it has also been accepted for the main conference of LREC-COLING 2024. The conference proceedings will be available in May 2024.

## Installation
Install all necessary dependencies by running

```
python3 -m pip install -r requirements.txt
```
 after cloning this repository.

This code base provides necessary scripts for the dataset collection process (`code/1. dataset_collection`), followed by the schema creation process, i.e., storage of the document content in schema (`code/2. schema_creation`). Once document content is extracted and stored in the schema, the next step is to create a definition corpus using an approach similar to the one proposed by [Damaratskaya 2023](https://mediatum.ub.tum.de/1656157?query=Anastasiya&show_id=1715461). The created definition corpus comprises the existing definitions present in energy domain documents at [EUR-Lex platform](https://eur-lex.europa.eu/search.html?name=browse-by%3Alegislation-in-force&type=named&displayProfile=allRelAllConsDocProfile&qid=1710260444909&CC_1_CODED=12). This also act as a ground-truth dataset for the evaluation of the retrieval augmented generation (RAG) pipeline.

## Comparison to Related Work


## Cite our work
If you use the dataset or other parts of this code base, please use the following citation for attribution:

```
@misc{chouhan2024lreccoling,
      title={LexDrafter: Terminology Drafting for Legislative Documents using Retrieval Augmented Generation}, 
      author={Ashish Chouhan and Michael Gertz},
      year={2024},
      eprint={xxxxx.xxxx},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```

## License Information
Copyright for the editorial content of EUR-Lex website, the EU legislative document content owned by the EU, are licensed under the [Creative Commons Attribution 4.0 International licence](https://creativecommons.org/licenses/by/4.0/), i.e., CC BY 4.0 as mentioned on the official [EUR-Lex website](https://eur-lex.europa.eu/content/legal-notice/legal-notice.html#2.%20droits).  Any data artifacts remain licensed under the CC BY 4.0 license.

## License for software component
Per the recommendation of Creative Commons, we apply a separate license to the software component of this repository. We use the standard [MIT](https://choosealicense.com/licenses/mit/) license for code artifacts.
