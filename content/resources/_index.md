---
title: "Resources"
og_image: "images/P6-S43-5554.png"
og_image_alt: "Raw cryo-electron microscopy micrograph of protein particles in vitreous ice."
description: "Protocols, software, and the CU Anschutz shared-resource cores the lab relies on."

# Grouped so protocols and software read as separate things rather than one
# mixed grid. Each group renders as its own subsection, in this order.
groups:
  - title: "Protocols"
    description: "Bench procedures we use routinely and are happy to share."
    items:
      - title: "Graphene Oxide Grid Preparation"
        ref: "protocols/go-grids.md"
        description: "Preparing 1–3 layer graphene oxide films on Quantifoil grids for cryo-EM, with 40–80% coverage after vitrification."
      - title: "Papain Antibody Digestion"
        ref: "protocols/mab-digest.md"
        description: "Digesting IgG with papain to generate Fab and Fc fragments for structural work."

  - title: "Software & tools"
    description: "Open-source tools written in the lab, plus resources we maintain for the wider community."
    items:
      - title: "ProteinCHAOS"
        url: "https://github.com/dzyla/ProteinCHAOS"
        description: "MD-inspired generative art tool for visualising protein dynamics."
      - title: "Follow Relion Gracefully"
        url: "https://github.com/dzyla/Follow_Relion_gracefully"
        description: "Browser-based dashboard for monitoring RELION jobs as they run."
      - title: "Semantic Manuscript Search"
        url: "https://www.manuscript-search.org/"
        description: "Search the literature by abstract, title, or idea rather than keyword."

# CU Anschutz School of Medicine shared resources. Instrument lists checked
# against each facility's own page — see README before editing.
cores:
  - name: "Cryo-EM Structural Biology Shared Resource"
    url: "https://medschool.cuanschutz.edu/corefacilities/cryo-em/home"
    summary: "Single-particle cryo-EM from grid screening through automated high-resolution data collection, with remote microscope control."
    instruments:
      - "Talos Arctica 200 kV X-FEG (Autoloader)"
      - "Gatan K3 Summit direct detector"
      - "Talos L120C 120 kV screening TEM"
      - "CETA CMOS camera"
      - "Vitrobot Mark IV"
      - "Gatan Solarus 950 plasma cleaner"
      - "Leginon · Appion · cryoSPARC Live"

  - name: "X-Ray Crystallography"
    url: "https://medschool.cuanschutz.edu/corefacilities/x-ray-crystallography/home"
    summary: "Crystallisation screening and optimisation, in-house diffraction data collection, processing, and structure determination."
    instruments:
      - "Rigaku MicroMax-007 HF microfocus source"
      - "VariMax optics · AFC11 goniometer"
      - "Pilatus 200K area detector"
      - "Oxford Cobra cryo-system"
      - "SPT Labtech mosquito Xtal-3 · Phoenix · Alchemist"
      - "Minstrel imaging · CrystalTrak"
      - "HKL-3000R"

  - name: "Biophysics"
    url: "https://medschool.cuanschutz.edu/corefacilities/biophysics/home"
    summary: "Binding, thermodynamics, oligomeric state, and single-molecule characterisation of proteins and complexes."
    instruments:
      - "Biacore T200 (SPR)"
      - "MicroCal iTC200 (ITC)"
      - "Monolith NT.115 Pico (MST)"
      - "Refeyn TwoMP (mass photometry)"
      - "Beckman Coulter XL-I (AUC)"
      - "JASCO J-815 (CD)"
      - "DynaPro Plate Reader III (DLS)"
      - "LUMICKS C-Trap Dymo-400 (optical tweezers)"

  - name: "NMR"
    url: "https://medschool.cuanschutz.edu/corefacilities/nmr/home"
    summary: "High-field NMR for structure, dynamics, and interaction studies of proteins and nucleic acids."
    instruments:
      - "Bruker Avance Neo 600 MHz"
      - "Varian INOVA 600 MHz (cold probe)"
      - "Varian 900 MHz Direct Drive (cold probe, Z-gradient)"
      - "Varian 800 MHz Direct Drive (at CU Boulder)"

  - name: "Mass Spectrometry — Proteomics"
    url: "https://medschool.cuanschutz.edu/corefacilities/ms-proteomics/home"
    summary: "Protein identification and quantification, plus structural analysis by chemical crosslinking."
    instruments:
      - "Orbitrap Fusion Lumos · Easy-nLC 1200"
      - "Bruker timsTOF Pro · Evosep One"
      - "Bruker timsTOF SCP · nanoElute"
---
