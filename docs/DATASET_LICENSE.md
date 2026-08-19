# Demo Dataset License and Production Boundary

The optional local demonstration fixture comes from the [Kolektor Surface-Defect Dataset](https://www.vicos.si/resources/kolektorsdd/), provided by the ViCoS Lab at the University of Ljubljana.

> The KSDD source is licensed under **CC BY-NC-SA 4.0**. The source page asks prospective commercial users to contact the dataset publisher.

Accordingly, **no KSDD imagery is committed to this repository**. `scripts/prepare_ksdd_fixture.py` is an opt-in local selector that expects a user to obtain the official archive and accept its terms. The script creates an ignored, compact local fixture for non-commercial portfolio demonstration only.

For a production deployment, provide company-owned inspection images, a contractually licensed supplier dataset, or a separately approved public dataset. Recalibrate the reference profile and repeat the site-specific evaluation before making any process-control decision.

## Attribution

Tabernik, D., Šela, S., Skvarč, J., and Skočaj, D. *Segmentation-Based Deep-Learning Approach for Surface-Defect Detection*. Journal of Intelligent Manufacturing, 2019. https://prints.vicos.si/publications/370
