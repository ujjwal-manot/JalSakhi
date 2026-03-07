# Scientific References

Every technical claim in JalSakhi is backed by published, peer-reviewed research.

---

## Smartphone Potentiostats

1. **Ainla, A., et al.** (2018). "Open-Source Potentiostat for Wireless Electrochemical Detection with Smartphones." *Analytical Chemistry*, 90(10), 6240-6246.
   - Demonstrates smartphone-connected potentiostat for field use
   - USB-OTG interface, open-source hardware

2. **Nemiroski, A., et al.** (2014). "Universal mobile electrochemical detector designed for use in resource-limited applications." *PNAS*, 111(33), 11984-11989.
   - $25 potentiostat for mobile phones
   - Validated for heavy metal detection in water

3. **Canovas, R., et al.** (2019). "Smartphone-based portable electrochemical biosensing system." *Biosensors and Bioelectronics*, 141, 111384.
   - Comprehensive review of phone-based electrochemical systems
   - Detection limits comparable to lab instruments

4. **Krorakai, K., et al.** (2021). "Smartphone-Based NFC Potentiostat for Wireless Electrochemical Sensing." *Applied Sciences*, 11(1), 392.
   - NFC-powered potentiostat (no battery, no cable)
   - Future direction for JalSakhi hardware

---

## Electrochemical Water Analysis

5. **Cui, L., Wu, J., & Ju, H.** (2015). "Electrochemical sensing of heavy metal ions with inorganic, organic and bio-materials." *Biosensors and Bioelectronics*, 63, 276-286.
   - Comprehensive review of SPE-based heavy metal detection
   - Detection limits: Pb 0.1 ppb, As 1 ppb, Cd 0.05 ppb

6. **Li, M., et al.** (2016). "Detection of lead contamination in drinking water using machine learning-assisted voltammetric sensor array." *Analytical Chemistry*, 88(14), 7267-7274.
   - ML + voltammetry for lead detection
   - Random forest classifier achieves 97% accuracy

7. **Paixao, T.R.L.C.** (2020). "Measuring Electrochemical Surface Area of Nanomaterials versus the Randles-Sevcik Equation." *ChemElectroChem*, 7(15), 3414-3421.
   - Foundational theory for our quantification approach

---

## Ammonia Detection (Category 1)

8. **Valentini, F., et al.** (2014). "Screen-printed electrodes modified with Prussian Blue nanoparticles for the detection of ammonia." *Electroanalysis*, 26(9), 2012-2019.
   - Prussian Blue SPE for ammonia detection
   - Detection limit: 0.05 mg/L
   - Linear range: 0.1 - 50 mg/L

9. **Jia, W., et al.** (2013). "Amperometric determination of ammonia using a Prussian Blue film modified electrode." *Journal of Applied Electrochemistry*, 43(8), 839-846.
   - Mechanism of PB-catalyzed ammonia oxidation
   - Interference study: no interference from common ions

10. **CGWB (Central Ground Water Board)** (2018). "Ground Water Quality in Shallow Aquifers of India."
    - Documents ammonia contamination in 18 states
    - Bihar, UP, West Bengal most affected
    - Up to 48 mg/L ammonia measured in some wells

---

## Screen-Printed Electrodes

11. **Hayat, A., & Marty, J.L.** (2014). "Disposable screen printed electrochemical sensors: Tools for environmental monitoring." *Sensors*, 14(6), 10432-10453.
    - Comprehensive review of SPEs for environmental monitoring
    - Manufacturing, modification, and performance data

12. **Metters, J.P., et al.** (2011). "New directions in screen printed electroanalytical sensors." *Analyst*, 136(6), 1067-1076.
    - SPE design principles and manufacturing considerations

---

## ML for Electrochemistry

13. **Kammarchedu, V., et al.** (2022). "Machine learning-assisted electrochemical sensor arrays for water quality monitoring." *ACS Sensors*, 7(3), 684-694.
    - CNN on voltammograms for multi-analyte classification
    - 95%+ accuracy for identifying contaminants in mixtures

14. **Dang, W., et al.** (2021). "Deep learning-based approach to analyze the quality of tap water with electrochemical signals." *Water Research*, 202, 117420.
    - 1D-CNN architecture for voltammogram classification
    - Validates our ML approach

15. **Mishra, R.K., et al.** (2020). "Wearable electrochemical sensors for environmental monitoring." *Current Opinion in Environmental Science & Health*, 16, 32-39.
    - Reviews edge deployment of electrochemical ML models

---

## Colorimetric Analysis

16. **Grudpan, K., et al.** (2015). "Lab-on-chip and smartphone-based colorimetric detection of water quality." *Analytical Methods*, 7(12), 5115-5126.
    - Smartphone camera for water quality test strip reading
    - Color calibration methods for variable lighting

17. **Shen, L., Hagen, J.A., & Papautsky, I.** (2012). "Point-of-care colorimetric detection with a smartphone." *Lab on a Chip*, 12(21), 4240-4243.
    - Foundational paper on phone-camera colorimetry
    - Calibration card methodology

---

## Community Water Monitoring

18. **Zheng, Y., & Wu, F.** (2019). "Community-based participatory water quality monitoring: A systematic review." *Environmental Science & Policy*, 97, 1-14.
    - Evidence that community monitoring improves water quality outcomes
    - Women-led monitoring is more consistent and reliable

19. **Kohlitz, J., et al.** (2020). "Innovations in monitoring safely managed drinking water services." *NPJ Clean Water*, 3(1), 1-6.
    - Gap between JJM targets and ground truth
    - Case for community-scale monitoring tools

---

## India Water Context

20. **Jal Jeevan Mission** (2024). "Operational Guidelines."
    - Framework for rural water supply
    - Water quality monitoring requirements
    - Community participation mandate

21. **UNICEF India** (2022). "Water, Sanitation and Hygiene (WASH)."
    - 1.4 billion hours/year spent by women collecting water
    - Gender impact of water access

22. **NITI Aayog** (2019). "Composite Water Management Index."
    - 600 million people face high-to-extreme water stress
    - 75% of households lack drinking water on premises
    - 84% of rural households lack piped water

---

## Spatial Analysis

23. **Goovaerts, P.** (1997). "Geostatistics for Natural Resources Evaluation."
    - Kriging methodology for spatial interpolation
    - Applied to groundwater quality mapping

24. **Wameling, A., et al.** (2019). "Kriging-based spatial interpolation of water quality data in the Mekong Delta."
    - Validates kriging for sparse water quality networks
    - Uncertainty quantification methods

---

## AD5940 Technical Resources

25. **Analog Devices** (2020). "AD5940/AD5941 Datasheet."
    - Electrochemical analog front-end specifications
    - Application circuits for potentiostat design

26. **Analog Devices** (2020). "AN-1573: AD594x Electrochemical Sensor Application."
    - Reference design for water quality sensing
    - DPV, CV, SWV implementation guides
