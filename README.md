<a name="readme-top"></a>
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/achouhan93/LexDrafter">
    <img src="images/legal-document.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">LexDrafter: Terminology Drafting for Legislative Documents using Retrieval Augmented Generation</h3>

  <p align="center">
   Ashish Chouhan and Michael Gertz 
   
   Heidelberg University
   
   Contact us at: [`{chouhan, gertz}@informatik.uni-heidelberg.de`](mailto:chouhan@informatik.uni-heidelberg.de)
    <br />
    <br />
    <a href="https://github.com/achouhan93/LexDrafter/issues">Report Bug</a>
    ·
    <a href="https://github.com/achouhan93/LexDrafter/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project
A [pre-print](https://arxiv.org/abs/xxxxx) of our work is available; it has also been accepted for the main conference of LREC-COLING 2024. The conference proceedings will be available in May 2024.

### Abstract
With the increase in legislative documents at the EU, the number of new terms and their definitions is increasing as well. As per Joint Practical Guide, terms used in legal documents shall be consistent, and identical concepts
shall be expressed without departing from their meaning in ordinary, legal, or technical language. Thus, while drafting a new legislative document, having a framework that provides insights about existing definitions and
helps define new terms based on a document’s context will support such harmonized legal definitions across different regulations and thus avoid ambiguities. In this paper, we present LexDrafter, a framework that assists in drafting Definitions articles for legislative documents using retrieval augmented generation (RAG) and existing term definitions present in different legislative documents. For this, definition elements are built by extracting definitions from existing documents. Using definition elements and RAG, a Definitions article can be suggested on demand for a legislative document that is being drafted. We demonstrate and evaluate the functionality of LexDrafter using a collection of EU documents from the energy domain. The code for LexDrafter framework is available at https://github.com/achouhan93/LexDrafter.
<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

This section should list any major frameworks/libraries used to bootstrap your project. Leave any add-ons/plugins for the acknowledgements section. Here are a few examples.

* [![Next][Next.js]][Next-url]
* [![React][React.js]][React-url]
* [![Vue][Vue.js]][Vue-url]
* [![Angular][Angular.io]][Angular-url]
* [![Svelte][Svelte.dev]][Svelte-url]
* [![Laravel][Laravel.com]][Laravel-url]
* [![Bootstrap][Bootstrap.com]][Bootstrap-url]
* [![JQuery][JQuery.com]][JQuery-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

Install all necessary dependencies by running

```
python3 -m pip install -r requirements.txt
```
after cloning this repository.

This code base provides necessary scripts for the dataset collection process (`code/1. dataset_collection`), followed by the schema creation process, i.e., storage of the document content in schema (`code/2. schema_creation`). Once document content is extracted and stored in the schema, the next step is to create a definition corpus using an approach similar to the one proposed by [Damaratskaya 2023](https://mediatum.ub.tum.de/1656157?query=Anastasiya&show_id=1715461). The created definition corpus comprises the existing definitions present in energy domain documents at [EUR-Lex platform](https://eur-lex.europa.eu/search.html?name=browse-by%3Alegislation-in-force&type=named&displayProfile=allRelAllConsDocProfile&qid=1710260444909&CC_1_CODED=12). This also act as a ground-truth dataset for the evaluation of the retrieval augmented generation (RAG) pipeline.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* npm
  ```sh
  npm install npm@latest -g
  ```

### Installation

_Below is an example of how you can instruct your audience on installing and setting up your app. This template doesn't rely on any external dependencies or services._

1. Get a free API Key at [https://example.com](https://example.com)
2. Clone the repo
   ```sh
   git clone https://github.com/your_username_/Project-Name.git
   ```
3. Install NPM packages
   ```sh
   npm install
   ```
4. Enter your API in `config.js`
   ```js
   const API_KEY = 'ENTER YOUR API';
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CITATION -->
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

<!-- LICENSE -->
## License

### License Information
Copyright for the editorial content of EUR-Lex website, the EU legislative document content owned by the EU, are licensed under the [Creative Commons Attribution 4.0 International licence](https://creativecommons.org/licenses/by/4.0/), i.e., CC BY 4.0 as mentioned on the official [EUR-Lex website](https://eur-lex.europa.eu/content/legal-notice/legal-notice.html#2.%20droits).  Any data artifacts remain licensed under the CC BY 4.0 license.

### License for software component
Per the recommendation of Creative Commons, we apply a separate license to the software component of this repository. We use the standard [MIT](https://choosealicense.com/licenses/mit/) license for code artifacts.
See `license/LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/achouhan93/LexDrafter.svg?style=for-the-badge
[contributors-url]: https://github.com/achouhan93/LexDrafter/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/achouhan93/LexDrafter.svg?style=for-the-badge
[forks-url]: https://github.com/achouhan93/LexDrafter/network/members
[stars-shield]: https://img.shields.io/github/stars/achouhan93/LexDrafter.svg?style=for-the-badge
[stars-url]: https://github.com/achouhan93/LexDrafter/stargazers
[issues-shield]: https://img.shields.io/github/issues/achouhan93/LexDrafter.svg?style=for-the-badge
[issues-url]: https://github.com/achouhan93/LexDrafter/issues
[license-shield]: https://img.shields.io/github/license/achouhan93/LexDrafter.svg?style=for-the-badge
[license-url]: https://github.com/achouhan93/LexDrafter/blob/master/LICENSE.txt
