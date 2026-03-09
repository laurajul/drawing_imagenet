# Drawing ImageNet

*100 hand-drawn images from a thousand-class slice of the world*

This work stages an encounter between two fundamentally different worldviews: the human tradition of art as an intentional, context-driven act, and the computational paradigm that treats visual culture as measurable, optimizable data.

Over the course of this project, 100 classes from the 1000-class ImageNet benchmark have been drawn by hand — each class selected at random, each example image presented at random. The result is a body of drawings that neither annotates nor improves the dataset, but simply looks at it: closely, slowly, and by hand.

---

## An Accidental Archive

ImageNet was announced in 2009 by a team of researchers at Princeton and Stanford Universities, led by Fei-Fei Li. Consisting of over 14 million images organized into approximately 20,000 categories, it was at the time of its creation one of the largest human-annotated image datasets ever assembled [1]. Its categorical backbone was inherited from WordNet — a large database of English words organized into a semantic hierarchy, developed by cognitive psychologist George A. Miller in the 1980s. The WordNet hierarchy gave ImageNet its structure; internet search engines gave it its images. Tens of thousands of workers on Amazon Mechanical Turk, recruited from 167 countries, were paid to verify whether retrieved images matched their assigned category [1] — a task framed as requiring little reflexivity or deliberation, and above all, speed.

The 1000-class subset, used for the ImageNet Large Scale Visual Recognition Challenge (ILSVRC) from 2010 to 2017, is the version the world came to know. When Alex Krizhevsky's deep neural network won the 2012 challenge by a previously unimaginable margin, a field was transformed [1]. ImageNet did not just train models — it trained an entire research community's relationship to data, solidifying large-scale annotated image collections as the central pillar of AI research.

---

## A WEIRD World, Carefully Labeled

ImageNet gives a perspective of a WEIRD society — Western, Educated, Industrialized, Rich, Democratic [5] — at a very specific point in time. It contains and represents, but is also finite and limited by, what is culturally significant to the society it emerged from: football, fishing, barbecuing, pickup trucks. Over a hundred breeds of dog. A handful of raptors dominated by the bald eagle — the only one of the sixty species of eagle that exist globally to feature in the dataset, and not coincidentally the national bird of the United States [4]. Ninety-three classes for mammals. Twenty-seven for insects — despite there being roughly six thousand known mammal species in the world compared to approximately one million known insect species [4].

More than representing the natural world, ImageNet mirrors a human relationship to other creatures: which animals are culturally significant, charismatic, eaten, kept as pets, or hunted for sport. As Denton et al. observe, it is a view that "associates 'bikinis' with women, 'sports' with men, 'trout' with fishing trophies, and 'lobsters' with dinner" [1]. The dataset does not describe the world so much as it describes a specific culture's *relationship* to it — one shaped, as Denton et al. put it, by "digital photography and image sharing practices of the late 2000s, the functionality of web search engines, the imperative for speed, and non-reflexivity designed into the dataset curation process" [1].

This is not merely a limitation — it is what makes ImageNet so fascinating to look at. Its images are "stereotypical, unnatural, and overly simple representations of the class category" [3] — photographs selected precisely because they matched an imagined prototype. Each class is a small, surprisingly specific portrait of how one culture, at one moment, imagined a concept should look.

---

## A Historical Artifact

ImageNet has had a profound impact, and the effects are still unfolding. It remains a standard benchmark for computer vision models today [2], and its taxonomy and cultural inscription continue to shape how contemporary systems are designed and evaluated. The influence extends into generative AI: remarkably, competitive text-to-image models can still be trained on ImageNet *alone*, achieving results that surpass much larger models trained on datasets a thousand times the size [7]. Meanwhile, even LAION-5B — the open-source, billion-scale dataset behind Stable Diffusion — used ImageNet as its quality benchmark during construction, calibrating what counts as a "good" image against the standard ImageNet had established [8]. ImageNet is the foundation beneath the foundation.

Luccioni and Crawford trace what they call the "nine lives" of ImageNet [2]: its multiple official and unofficial versions, its revisions and quiet remediations. In 2019, artist Trevor Paglen and researcher Kate Crawford launched *ImageNet Roulette*, a work that invited the public to submit photographs and receive their classification under ImageNet's "person" subcategories — labels inherited from WordNet that included terms ranging from the archaic to the violently dehumanizing. The project went viral, and within days, the ImageNet team announced the removal of more than half a million images from the dataset [6]. Yet Crawford and Paglen were clear that no technical fix could address the deeper issue: "The whole endeavor of collecting images, categorizing them, and labeling them is itself a form of politics, filled with questions about who gets to decide what images mean and what kinds of social and political work those representations perform." [6]

In a counterfactual scenario, if only a few of these classes had been different — if they had contained different representations, different geographies, different proportions of life — the downstream effects on an entire field could have been profound. What is colloquially called "the ImageNet dataset" is not a single stable object but a multiplicity of image sets, each transmitting an evolving set of values. It has become, in Denton et al.'s terms, a "historically situated artifact" [1] — one that continues to operate as infrastructure while the contingencies of its creation increasingly recede from view.

---

## Drawing as Method

The experiment is simple: 100 drawings, one per class, each class chosen at random from the 1000-class benchmark, each reference image presented at random from within that class. No filtering, no curation beyond what ImageNet itself has already performed.

This promotes a human gaze at the dataset that is not functional — not data annotation — but explores the situated context of each image as interpreted by a human viewer. Where automated recognition moves at computational speed, drawing is slow. Where a classifier outputs a probability score, a drawing carries hesitation, interpretation, and the marks of attention. Human analogue art remains slow and inefficient. Measuring its virtue with mechanistic means, however, may result in absurdity.

What emerges from this slowness are 100 images that characterize ImageNet: showing its absurdity, sometimes its charm, and its narrow cultural lens. They are drawings of images that were themselves selected to be typical, verified to be correct, stripped of the context that would make them particular. They are portraits of a prototype.

---

## Notes

[1] Denton, E., Hanna, A., Amironesei, R., Smart, A., & Nicole, H. (2021). On the genealogy of machine learning datasets: A critical history of ImageNet. *Big Data & Society*. DOI: 10.1177/20539517211035955

[2] Luccioni, A. S., & Crawford, K. (2024). The Nine Lives of ImageNet: A Sociotechnical Retrospective of a Foundation Dataset and the Limits of Automated Essentialism. *Journal of Data-centric Machine Learning Research*. — *[please add URL/DOI]*

[3] Shirali, A., & Hardt, M. (2024). What Makes ImageNet Look Unlike LAION. arXiv:2306.15769v2. — *[please verify URL/DOI]*

[4] Luccioni, A. S., & Rolnick, D. (2023). Bugs in the Data: How ImageNet Misrepresents Biodiversity. *Proceedings of the AAAI Conference on Artificial Intelligence*, 37(12). — *[please add URL/DOI]*

[5] Henrich, J., Heine, S. J., & Norenzayan, A. (2010). The weirdest people in the world? *Behavioral and Brain Sciences*, 33(2–3), 61–83. — *[not in research folder — please add URL/DOI]*

[6] Crawford, K., & Paglen, T. (2019). ImageNet Roulette. *Excavating AI*. As reported in: Cascone, S. artnet News, September 2019. — *[please add canonical URL]*

[7] Degeorge, L., Ghosh, A., Dufour, N., Picard, D., & Kalogeiton, V. (2025). How Far Can We Go With ImageNet for Text-to-Image Generation? arXiv:2502.21318v3. — *[please verify URL/DOI]*

[8] Lehuger, S. et al. (2024). Models All The Way. — *[please add canonical URL/publication details]*

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

After scanning finished drawings and their reference photos on an orange-canvas background:

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
