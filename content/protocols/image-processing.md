---
title: "Image Processing Workflow"
date: 2023-10-27
---

Steps for processing cryo-EM images.

1.  **Import micrographs into RELION.**
    - Use the import job type to bring in your raw movie files.
2.  **Perform motion correction.**
    - Use MotionCor2 or RELION's own implementation to correct for beam-induced motion.
3.  **Estimate CTF parameters.**
    - Use CTFFIND4 or Gctf to estimate the contrast transfer function for each micrograph.
4.  **Pick particles and generate initial model.**
    - Pick particles manually or with an automated picker, then use 2D and 3D classification to generate an initial 3D model.