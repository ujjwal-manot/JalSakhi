# Competition Prototype Budget

## Hard Limit: INR 4,000

This is a competition prototype. Not a startup. Not a product launch.

## Bill of Materials

| Item | Cost (INR) | Source |
|------|-----------|--------|
| ESP32 dev board (BLE + WiFi + DAC + ADC) | 500 | Amazon India / Robu.in |
| Water test strips (16-in-1, 100 pack) | 400 | Amazon India |
| LM358 op-amps (x2) | 30 | Local electronics shop |
| Breadboard | 150 | Amazon / local |
| Jumper wires kit | 100 | Amazon / local |
| Resistor assortment | 100 | Local |
| Silver wire 5cm (reference electrode) | 200 | Jewellery supply / Amazon |
| Ammonia solution (demo spiking) | 100 | Pharmacy |
| Salt / KCl (electrolyte) | 50 | Pharmacy / chem lab |
| Calibration card printing | 10 | Home printer |
| Poster / prints | 200 | Print shop |
| **Total** | **~1,840** | |
| **Buffer** | **~2,160** | For unexpected expenses |

## What We Don't Buy

- No AD5940 eval board (too expensive)
- No Nordic nRF52 dev kit (ESP32 has BLE built in)
- No commercial SPE strips from DropSens (too expensive per strip)

## Electrodes: DIY (Free)

- Working Electrode: 0.5mm HB pencil graphite rod
- Counter Electrode: Another pencil graphite rod
- Reference Electrode: Silver wire + bleach (AgCl coating)
- Published technique: pencil graphite as carbon electrode (Electrochimica Acta)

## Demo Strategy

1. Colorimetric mode: commercial test strips + phone camera + AI (INR 400)
2. Electrochemical mode: ESP32 + op-amp breadboard + pencil electrodes (INR 1,000)
3. Dashboard: web app with simulated multi-village data (free)
