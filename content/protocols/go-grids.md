---
title: "Graphene Oxide (GO) Grid Preparation Protocol"
date: 2023-01-01
author: "Dawid Zyla"
---

This protocol describes how to prepare **1-3 layers of semi-amorphous graphene oxide (GO)** on Quantifoil grids, suitable for cryo-EM. GO films demonstrate reduced inelastic scattering and lower background compared to amorphous carbon, which improves phase contrast for imaging smaller complexes. In addition, it allows working with lower protein concentration and avoid prefered orientation. This protocol ensures 40-80% coverage of GO after vitrification, with precise handling steps to minimize aggregation and variation in coverage.

Protocol based on Ban Lab protocol, ETH Zurich.

---

## **Materials and Equipment**
- **Grids:** Quantifoil R2/2 grids mesh 100 or Quantifoil R2/1 grids mesh 200
- **Graphene oxide (GO) dispersion:** Sigma-Aldrich #763705, 2 mg/mL (Lot #MKBX1971V)  
- **MilliQ water**  
- **Eppendorf tubes (1.5 mL)**  
- **Parafilm**  
- **Water sonicator** (100% power)  
- **Centrifuge** (capable of 500 g)  
- **Ethyl acetate**  
- **Tweezers**  
- **Glow discharge unit**  
- **Filter paper**  
- **Glass petri dish**  
- **Pipettes and tips**

---

## **1. Preparation of Grids**

1. **Ethyl Acetate Treatment:** 
   - Place the grids in a **glass petri dish** on filter paper.
   - Add **~1 mL ethyl acetate** to the dish (ensure the grids do not float).  
   - Leave the grids overnight to soak.
   - If needed, dry the grids in a hood the next morning.  

---

## **2. Preparation of GO Dispersion**
1. **Mix the Stock Solution:**
   - Invert the **2 mg/mL GO dispersion** (Sigma-Aldrich #763705) **10 times** to ensure homogeneity.  
   - Use a **1 mL pipette tip** to gently mix the stock. 

2. **Dilute the Stock Solution:**
   - Prepare a **0.2 mg/mL GO dispersion** by diluting the stock in MilliQ water.  
     - Example: For **1.5 mL** of 0.2 mg/mL solution, mix **150 µL stock** with **1.35 mL MilliQ**.  

3. **Sonication of GO Dispersion:**
   - Sonicate the prepared GO solution for **4 minutes at 100% power** using a **water sonicator**. The bath should be filled with water to the level indicated and Eppendorf tubes should be placed in a floating rack.
     - **Note:** Avoid longer sonication times, which can damage the GO sheets.  

4. **Remove Aggregates:**
   - Centrifuge the sonicated GO solution at **500 g for 1 minute**.  
   - Carefully transfer only the **upper half** of the supernatant to a new Eppendorf tube to avoid aggregates. There will be a small pellet at the bottom and dark pellet on a side. Try getting the liquid from the opposite side of the dark pellet.

---

## **3. Coating Grids with GO**
1. **Prepare the Workstation:**
   - Wash the **tweezers** and prepare a sheet of **Parafilm**.  
   - Add **20 µL MilliQ water droplets** to the Parafilm (two droplets per grid).  

2. **Glow Discharge the Grids:**
   - Glow discharge the cleaned grids at **15 mA for 30 seconds**.  
   - **Caution:** Avoid placing the glow-discharged side on filter paper to prevent contamination. Take each grid into the tweezers by the side.

3. **Apply GO Solution to Grids:**
   - Mix the GO dispersion thoroughly by **pipetting up and down** before each use.  
   - Add **3 µL** of GO solution to each grid at **15-second intervals**.  
   - Incubate the grids for **4 minutes** to allow proper coating.

4. **Wash the Grids:**
   - Blot the GO solution off the grid using the **flat part of filter paper**.  
   - Immediately pick up the **MilliQ water droplet** on the Parafilm with the grid to wash it.  
   - Blot the water off with filter paper.  
   - Repeat this washing step for **every grid**.
   - **Note:** Make sure the grid is correctly positioned for GO deposition. Otherwise strange things happen with two CTF rings.
   - (There should be a visible GO in the blotting paper even after water washes)

5. **Drying the Grids:**
   - Let the grids air-dry for **at least 10 minutes**.  
   - Transfer the dried grids to a **metal grid holder** and allow them to rest for **15 minutes** before further use (optional)
   - I usually use them immediately after drying (10min) and never had any issues. 

---

## **4. Checking Coverage and Storage**
1. **Check GO Coverage:**  
   - Use a **TEM** at **~280x magnification** and low intensity with the eyepiece to search for the **charging effect**.  
   - Aim for **60-80% coverage** with **1-4 layers of GO**.  

2. **Storage:**  
   - Don't store the grids. Use and prepare them fresh for best results.
---

## **5. Vitrification of GO Grids**
1. **Vitrification Settings:**
   - Use a **Vitrobot** or similar plunge freezer.  
   - Set wait time to **15 seconds** to allow the sample (3 µL) to interact with the GO surface.  
   - Blot time can be adjusted based on sample thickness; start with **3 seconds**. We usually use 2-4 seconds with blot force 0.  
   - Humidity should be set to **100%** at **4°C**.
   - Drain time after blotting can be set to **0.5 seconds**.

## **6. Notes and Troubleshooting**
- **GO Dispersion:** Always mix the GO stock solution well before dilution to ensure uniformity.
- **Coverage after Vitrification:** Expect **at least 40% coverage** after vitrification. Buffer composition, surfactants, or sample properties can impact the GO layer.  
- **Handling Grids:** Glow-discharged grids are sensitive to contamination—handle with care.  
- **Optimization:** If GO coverage or homogeneity is insufficient, repeat centrifugation and ensure thorough mixing during preparation.

---

This protocol provides reliable preparation of graphene oxide grids with optimal thickness and coverage for cryo-EM experiments.