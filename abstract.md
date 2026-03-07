# JalSakhi: Smartphone-Based Electrochemical Water Forensics and Intelligent Treatment Advisory for Women-Led Rural Communities

## Abstract

A woman in rural Bihar suspects her borewell water is contaminated. The nearest NABL-accredited laboratory is 53 kilometres away. The test costs Rs. 500, and results take ten days. Her family drinks the water while they wait. Across India, 2,200 laboratories serve 1.9 million habitations, a ratio that guarantees most contamination goes undetected, unreported, and untreated.

JalSakhi closes this measurement gap by converting an ordinary smartphone into a field water analysis instrument. The system operates in two modes. In electrochemical mode, a low-cost potentiostat circuit connected via Bluetooth performs voltammetric scans on disposable screen-printed electrodes dipped in a water sample. Different dissolved contaminants, including ammonia, lead, arsenic, nitrate, iron, and fluoride, produce distinct current-voltage signatures at characteristic potentials. A 1D convolutional neural network running on the phone classifies these signatures and estimates concentrations within 60 seconds, fully offline. In colorimetric mode, commercially available multi-parameter test strips are photographed against a printed calibration card, and a trained model extracts concentrations from colour response after correcting for phone camera and lighting variation.

Beyond detection, JalSakhi prescribes the minimum effective treatment for each result. This includes calculated chlorination dosage for moderate ammonia, activated carbon advisory for organic contamination, or a redirect to the nearest safe source on the community map when levels are dangerous. This prevents both over-treatment and under-treatment at the household level.

The deployment architecture uses India's existing network of 12 million women Self-Help Groups under NRLM. Designated members test community water sources weekly, generating spatiotemporal contamination data that aggregates into district-level heatmaps for Jal Jeevan Mission infrastructure planning. At Rs. 25 per test against Rs. 500 to 2,000 for laboratory analysis, monitoring frequency increases from annual to weekly while placing women at the centre of the water safety data chain, not as users, but as its infrastructure. A working prototype built for under Rs. 2,000 demonstrates both sensing modes with real-time contaminant identification.

Keywords: electrochemical sensing, voltammetry, screen-printed electrodes, water quality, convolutional neural network, community health, Self-Help Groups
