# JSCore: A Comprehensive Feature-based Benchmark for JavaScript Unit Test Generation

### Introduction
JSCore is a dataset designed to support research on automated unit test generation for JavaScript and TypeScript. This repository provides a curated benchmark of real-world open-source projects together with a static analysis pipeline for extracting language features, code complexity metrics, and project metadata.

Motivated by the lack of a broadly adopted benchmark for JavaScript test generation, JSCore captures the diversity of real-world projects while providing an extensible pipeline that can be expanded with additional analyses and projects. The dataset is intended to support the evaluation of modern test generation approaches including search-based tools, LLM-based systems, and emerging agentic systems and to contribute toward a standardized benchmark for testing research on dynamically typed languages.
### How to Use

#### 1. Using the Benchmark
The dataset consists of a curated list of JS and TS repositories. All projects are already included under the `Benchmark-Projects` directory. Alternatively, a complete list is provided in `benchmark.txt` for those who wish to clone them manually. You can manage these using the provided scripts:
- **Cloning:** Use `scripts/clone_benchmark.sh` to clone all repositories listed in `benchmark.txt` into the `Benchmark-Projects` directory.
- **Installation & Validation:** Run `scripts/install_benchmark.sh` to perform `npm install` on the benchmarked projects making them ready for test generation evaluation.

#### 2. Running the Evaluation Pipeline
If you wish to execute the pipeline on your own set of repositories or modify the analysis criteria:
1. **Repository Discovery:** Run `scripts/get_gh_repos.py` to populate `repos.txt` with potential GitHub repositories.
2. **Cloning:** Execute `scripts/clone_repos.sh` to clone the discovered repositories.
3. **Feature Analysis:** Run `evaluation_pipeline/evaluate.py` to analyze the complexity and language features of the collected projects.
4. **Filtering:** Use `evaluation_pipeline/analyse_and_filter.py` to apply filtering criteria. The final project list with analysis metrics is stored in `filtered_projects_with_analysis_result.csv`.

#### 3. Explorer
The project includes a web-based explorer to visualize the dataset features. You can access it via `index.html` or the [GitHub Pages](https://sagarut.github.io/dataset-evaluation/) deployment.

### Benchmark Projects
The following projects constitute the core benchmark dataset:
- [AdminLTE](https://github.com/ColorlibHQ/AdminLTE/commit/1a52342ff6165c18c22c7c283428861344bb6e9e)
- [Autoprefixer](https://github.com/postcss/autoprefixer/commit/541295c0e6dd348db2d3f52772b59cd403c59d29)
- [Bower](https://github.com/bower/bower/commit/4e0c3c1181c21624c5b3ab5bdf5d3becdb172b5a)
- [Dropzone](https://github.com/dropzone/dropzone/commit/f50d1828ab5df79a76be00d1306cc320e39a27f4)
- [Express-JWT](https://github.com/auth0/express-jwt/commit/129138815162b00b8017e6944f7fc6f3c5776ded)
- [Extract-Text-Webpack-Plugin](https://github.com/webpack-contrib/extract-text-webpack-plugin/commit/bc6f9f8f61d708352ea89fd4fc9764ce1e4de409)
- [Hoodie](https://github.com/hoodiehq/hoodie/commit/bd1354f10b2bcad154f24c3b35865ce3e05bd83a)
- [JSON-Server](https://github.com/typicode/json-server/commit/6d38bc118c53d02dd9ece9d70afdd53800dc6776)
- [Knex](https://github.com/knex/knex/commit/9bd12999907436c2ef51f786df09a9a7e8931cca)
- [Lodash](https://github.com/lodash/lodash/commit/8a26eb42adb303f4adc7ef56e300f14c5992aa68)
- [Markdown-Here](https://github.com/adam-p/markdown-here/commit/a7dd5c56daf58a278af4f2a05f41807ec6cbbe4a)
- [MDX](https://github.com/mdx-js/mdx/commit/b3351fadcb6f78833a72757b7135dcfb8ab646fe)
- [NeDB](https://github.com/louischatriot/nedb/commit/35be491ca67dbd4c6f75335f5f486307b192f2dc)
- [Release-It](https://github.com/release-it/release-it/commit/183050c371acf290ea57dcea58649a63c16eb9e5)
- [ScrollMagic](https://github.com/janpaepke/ScrollMagic/commit/3ebcb179355fb8e882378f5f5b3b48639cf7e90b)
- [ScrollReveal](https://github.com/jlmakes/scrollreveal/commit/b5f4e01a655812e06b377fff497fc629c02002f3)
- [ShellJS](https://github.com/shelljs/shelljs/commit/4580c00398982618ff075dd4354b0234a1d679dc)
- [Sitespeed.io](https://github.com/sitespeedio/sitespeed.io/commit/4959a247dc488098d433adc5366fa605df809397)
- [Spectacle-Code-Slide](https://github.com/jamiebuilds/spectacle-code-slide/commit/978dffec405d14d135057f99b6306ed2717b46a0)
- [Supertest](https://github.com/forwardemail/supertest/commit/200031e21905b25591ece2111ab2eb56cbf48fa2)
- [Tabulator](https://github.com/olifolkerd/tabulator/commit/952a19e2dba03d4828070246a03ccd527bd85c1e)
- [PostCSS](https://github.com/postcss/postcss/commit/6cb4a6673fb6d8b23eb1ebe66a22b6267ab141de)
- [Puppeteer](https://github.com/puppeteer/puppeteer/commit/0f0882c405878f3b5bca1316f5effb2692f20d81)
- [Tabby](https://github.com/Eugeny/tabby/commit/ef59394b793e203200f8eb6218834358ddc9da9f)
- [Vue-Devtools](https://github.com/vuejs/devtools/commit/01ee48167158178b7a07bed87ece379731267898)
- [Weex-UI](https://github.com/apache/incubator-weex-ui/commit/3a8ce2a21337965a272fea074cb72f92d50761a3)
- [ZY-Player](https://github.com/Hunlongyu/ZY-Player/commit/68fd0d0c6ae79de3d1a7400a85d704f3717e1140)
- [Commander.js](https://github.com/tj/commander.js/commit/395cf7145fe28122f5a69026b310e02df114f907)
- [Express](https://github.com/expressjs/express/commit/b8ab46594da8d2626c59ba36f76264ad980c533d)
- [JavaScript-Algorithms](https://github.com/trekhleb/javascript-algorithms/commit/e40a67b5d1aaf006622a90e2bda60043f4f66679)
- [Crawler-URL-Parser](https://gitlab.com/autokent/crawler-url-parser/-/commit/202c5b25ad693d284804261e2b3815fe66e0723e)
- [Delta](https://github.com/slab/delta/commit/dc17ca03e1d68ee729c8cd1ff790ebf96eb0fbec)
- [Node-Dir](https://github.com/fshost/node-dir/commit/a57c3b1b571dd91f464ae398090ba40f64ba38a2)
- [Node-Glob](https://github.com/isaacs/node-glob/commit/fd61f2410b4356f202f645661cfa175152702ae6)
- [Node-Graceful-FS](https://github.com/isaacs/node-graceful-fs/commit/234379906b7d2f4c9cfeb412d2516f42b0fb4953)
- [Spacl-Core](https://gitlab.com/cptpackrat/spacl-core/commit/fcb8511a0d01bdc206582cfacb3e2b01a0288f6a)
- [Zip-a-folder](https://github.com/maugenst/zip-a-folder/commit/9e7565abf8355c54b654f261a8084b4305e9e119)
- [Beatbump](https://github.com/snuffyDev/Beatbump/commit/d00ed3e10a13ec82a6a006dd02bf9548544d1ab3)
- [Felte](https://github.com/pablo-abc/felte/commit/ab1ae409ec99d36fa08a8cbe1a8de4e2fda84ccf)
- [Pandora](https://github.com/midwayjs/pandora/commit/7105ee3118d273d0fa930d2449d21fc89e6d7616)
- [Xyflow](https://github.com/xyflow/xyflow/commit/3e6bcf51e33b14d85d996145f5273a42f79628bd)

The complete list with specific commit hashes is available in `benchmark.txt`.

### Licenses
This project and its accompanying code are licensed under the MIT License. Individual projects of the benchmark within the `Benchmark-Projects` directory are subject to their respective original licenses.


