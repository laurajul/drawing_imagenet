# Drawing ImageNet

## Abstract

Assembled at a specific historical moment by a situated group of contributors and filtered through the infrastructure and aesthetics of Web 2.0, ImageNet is one of the most consequential taxonomies produced by computational culture. Its 1000-class benchmark helped shape the field of computer vision and continues to influence how datasets are filtered, how computer vision tasks are posed and how models are trained, evaluated, and benchmarked. More than a technical dataset, ImageNet is also an ethnographic artefact of a mainly WEIRD society at a specific point in history, capturing a world frozen in time. The particular algorithmic lens emerging from this dataset continues to shape contemporary computer vision, and its cultural inscription persists in the generative AI systems that inherit and reproduce it.

*Drawing ImageNet* slowly and inefficiently approaches a taxonomy that is meant to be primarily performative, for benchmarking, evaluation, and filtering, with its actual content rarely looked at, apart from data annotators with a specific and imposed task. As an exercise, *Drawing ImageNet* coaxes out situatedness and cultural assumptions embedded in individual images through a human lens. One hundred classes were randomly selected and drawn this way, using a script that selects an unvisited class at random and presents a random image from within it as a drawing reference. The resulting drawings characterize ImageNet itself, revealing the dataset as both systematic and idiosyncratic: sometimes absurd, sometimes charming, and shaped by a distinctly narrow cultural lens. By translating algorithmic taxonomy into slow, analogue drawings, the project stages an encounter between two fundamentally different worldviews: the human tradition of art as an intentional, context-driven act, and the computational paradigm that treats visual culture as measurable, optimizable data.

## A Consequential Dataset

ImageNet was announced in 2009 by a team of researchers at Princeton and Stanford Universities, led by Fei-Fei Li. Its categorical backbone was inherited from WordNet, a large database of English words organized into a semantic hierarchy, developed by cognitive psychologist George A. Miller in the 1980s. The WordNet hierarchy gave ImageNet its structure, and internet search engines gave it its images.[1] What resulted was less a neutral inventory of the visible world than a taxonomy: a hierarchical classification whose categories reflect the assumptions, values, and cultural context of those who built it, a fact that grew more consequential as the dataset did.

The 1000-class subset, used for the ImageNet Large Scale Visual Recognition Challenge (ILSVRC) from 2010 to 2017, is the version the world came to know. When Alex Krizhevsky's deep neural network won the 2012 challenge by a previously unimaginable margin, a field was transformed.[1] ImageNet did not just train models. It shaped the algorithmic lens through which datasets are filtered and models benchmarked, establishing a particular way of seeing as the default infrastructure of computer vision.

## An Artefact from a WEIRD World

ImageNet gives a perspective of a WEIRD society, Western, Educated, Industrialized, Rich, Democratic[5], at a very specific point in time. It is shaped by a narrow demographic and a very specific cultural context: its visual representations are drawn overwhelmingly from Americana and subsequently filtered through the lens of Web2. It contains dogs, war machinery, transportation devices, and prosaic domestic objects such as football, fishing gear, barbecue equipment, pickup trucks and military artefacts. It contains the bald eagle, the only one of sixty species of eagle that exist globally, and not coincidentally the national bird of the United States.[4]

ImageNet contains a myriad of classes referencing the natural world. Yet this world appears through a distinctly human lens. Ninety-three classes for mammals; twenty-seven for insects, despite there being roughly one million known insect species to every six thousand mammals.[4] Among its many animal categories, nearly half are different dog breeds, often depicted restrained on leashes or in the context of dog competitions. The class of bird house is represented, in one instance, by two individuals penetrating the entrance of a bird house with a stick. A myriad of classes for different kinds of fishes exist, but often these are not represented swimming in their natural habitat, but lifeless held by men, proudly presenting the catch of the day.

As Denton et al. observe, it is a view that "associates 'bikinis' with women, 'sports' with men, 'trout' with fishing trophies, and 'lobsters' with dinner."[1] The dataset does not describe the world so much as it describes a specific culture's relationship to it, one shaped by "digital photography and image sharing practices of the late 2000s, the functionality of web search engines, the imperative for speed, and non-reflexivity designed into the dataset curation process."[1]

This is not merely a limitation. It is what makes ImageNet so fascinating to look at. Its images are "stereotypical, unnatural, and overly simple representations of the class category"[3], photographs selected precisely because they matched an imagined prototype, verified by annotators operating under the assumption that visual recognition is decontextualized, universal, and self-evident. Each class is a small, surprisingly specific portrait of how one culture, at one moment, imagined a concept should look.

ImageNet is a historically situated artifact[1], assembled at a specific historical moment by a situated group of contributors and filtered through the infrastructure and aesthetics of Web 2.0. Its cultural inscription does not end there. It is still used for benchmarking models today [2] and its taxonomy continues to impact how contemporary models are designed and what data they are trained on. Generative AI has inherited and reproduces the cultural taxonomies embedded in this world frozen in time. In a counterfactual scenario, if only a few of these classes had been different, if they had contained different representations, different geographies, different proportions of life, the downstream effects on an entire field could have been profound.

Luccioni and Crawford trace what they call the "nine lives" of ImageNet[2]: its multiple official and unofficial versions, and its quiet remediations. In 2019, artist Trevor Paglen and researcher Kate Crawford launched *ImageNet Roulette*, a work that exposed ImageNet's "person" subcategories, labels inherited from WordNet ranging from the archaic to the violently dehumanizing. The project went viral, and within days, the ImageNet team removed more than half a million images from the dataset.[6] Yet Crawford and Paglen were clear that no technical fix could reach the deeper issue: "The whole endeavor of collecting images, categorizing them, and labeling them is itself a form of politics, filled with questions about who gets to decide what images mean and what kinds of social and political work those representations perform."[6]

LAION-5B, the billion-scale dataset behind Stable Diffusion and other text-to-image models, used ImageNet as its quality benchmark during construction.[8] 

## Tracing Cultural the Inscriptions, Charme and Absurdity of ImageNet trough drawing

*Drawing ImageNet* slowly and inefficiently approaches a taxonomy that is meant to be primarily performative, for benchmarking, evaluation, and filtering, with its actual content rarely looked at, apart from data annotators with a specific and imposed task. The experiment is simple: 100 drawings, one per class, each class chosen at random from the 1000-class benchmark, each reference image presented at random from within that class.

This exercise coaxes out situatedness and cultural assumptions embedded in individual images through a human lens. Where automated recognition moves at computational speed, drawing is slow. Human analogue art remains slow and inefficient, and measuring its virtue with mechanistic means may result in absurdity. What emerges from this slow experiment are 100 images that characterize ImageNet: showing its absurdity, sometimes celebrating its charme, and its narrow cultural lens. 

## Notes

[1] Denton, E., Hanna, A., Amironesei, R., Smart, A., & Nicole, H. (2021). On the genealogy of machine learning datasets: A critical history of ImageNet. *Big Data & Society*. DOI: 10.1177/20539517211035955

[2] Luccioni, A. S., & Crawford, K. (2024). The Nine Lives of ImageNet. *Journal of Data-centric Machine Learning Research*.

[3] Shirali, A., & Hardt, M. (2024). What Makes ImageNet Look Unlike LAION. arXiv:2306.15769v2.

[4] Luccioni, A. S., & Rolnick, D. (2023). Bugs in the Data: How ImageNet Misrepresents Biodiversity. *Proceedings of AAAI 2023*.

[5] Henrich, J., Heine, S. J., & Norenzayan, A. (2010). The weirdest people in the world? *Behavioral and Brain Sciences*, 33(2–3), 61–83.

[6] Crawford, K., & Paglen, T. (2019). ImageNet Roulette. *Excavating AI*. Via artnet News, September 2019.

[7] Degeorge, L. et al. (2025). How Far Can We Go With ImageNet for Text-to-Image Generation? arXiv:2502.21318v3.

[8] Lehuger, S. et al. (2024). Models All The Way.


---

## Repository

### Overview

```
drawing_imagenet/
├── scripts/
│   ├── download.py           # download the dataset from Kaggle
│   ├── show_and_save.py      # interactive drawing session tool
│   ├── remove_background.py  # core background-removal library
│   ├── process_drawings.py   # batch-process raw drawing scans
│   ├── process_photos.py     # batch-process raw reference photo scans
│   └── resize_outputs.py     # proportional resize pipeline
├── data/
│   ├── imagenet_class_index.json   # class id → (wnid, name) mapping
│   ├── imagenet-mini/train/        # dataset (after download)
│   ├── raw/drawings/               # raw scans of finished drawings
│   ├── raw/photos/                 # raw scans of reference photos
│   ├── drawings_raw/               # background-removed drawings (intermediate)
│   ├── scans_raw/                  # background-removed scans (intermediate)
│   ├── drawings/                   # final resized drawings (used by website)
│   └── scans/                      # final resized scans (used by website)
├── website/
│   └── index.html            # project website
└── misc/
    └── index.txt             # log of already-visited classes
```

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install kagglehub numpy pillow scipy
```

### Workflow

**1. Download the dataset**

```bash
python scripts/download.py
```

Downloads [`imagenetmini-1000`](https://www.kaggle.com/datasets/ifigotin/imagenetmini-1000) from Kaggle via `kagglehub` into `data/`. This is a 1000-class subset of ImageNet with a smaller number of images per class, sufficient for reference drawing purposes.

---

**2. Run a drawing session**

```bash
python scripts/show_and_save.py
```

The core tool for the drawing practice. On each run it:
- Picks a random unvisited class from the 1000 available
- Opens a random image from that class in the system image viewer
- Records a start timestamp
- Waits for input: `yes` (done drawing), `skip` (show another image from the same class), or `quit`
- On `yes`: saves the reference image and a `.json` metadata file (class name, filename, start/end timestamps, elapsed seconds) to `data/selection/`
- Logs the visited class to `misc/index.txt` so it is never repeated

---

**3. Process scans**

After scanning finished drawings and their reference photos on an  colored canvas background:

```bash
python scripts/process_drawings.py   # → data/drawings_raw/
python scripts/process_photos.py     # → data/scans_raw/
```

Both scripts call `remove_background.process_folder()` with parameters tuned for their respective material. The background removal works by:
1. Sampling the canvas colour from the image corners
2. Flood-filling from the border through pixels similar to the canvas colour (border-connected only, so colour inside a drawing is never removed)
3. Applying a soft alpha falloff through the transition zone
4. Cropping to the non-transparent bounding box

Parameters differ between drawings and scans — drawings use a higher threshold (55) and moderate edge desaturation to preserve coloured marks near the paper edge; scans use a wider edge zone and stronger shadow desaturation to eliminate orange bleed-through.

---

**4. Resize for the website**

```bash
python scripts/resize_outputs.py     # → data/drawings/ + data/scans/
```

A two-pass pipeline that preserves *relative subject size* across all drawings:

- **Pass 1** — measures the non-transparent content bounding box of every drawing. A small harvestman has a small bounding box; a large stork has a large one.
- **Pass 2** — pins the largest bounding box to `MAX_PX` (750 px) and scales all others proportionally, so size differences are visible on the page rather than flattened to a uniform display width.

Each scan is resized to exactly match the pixel dimensions of its paired drawing.

Output is written to `data/drawings/` and `data/scans/` as WebP files, which are referenced directly by `website/index.html`.
