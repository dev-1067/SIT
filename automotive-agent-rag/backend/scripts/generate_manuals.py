"""Generates the bundled sample manuals shipped with the app.

These are original, synthetically-authored owner's-manual excerpts (not
copied from any real manufacturer manual) so they can be safely bundled and
redistributed with the project as ready-to-search preload content.
"""
import os
from pathlib import Path
from fpdf import FPDF

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "app" / "data" / "manuals"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class PDFManual(FPDF):
    def __init__(self, title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title_text = title

    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, self.title_text, border=False, align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def build_manual(filename: str, title: str, sections: list[tuple[str, str]]):
    pdf = PDFManual(title)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "", 11)

    for heading, content in sections:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, heading, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, content)
        pdf.ln(3)

    output_path = OUTPUT_DIR / filename
    pdf.output(str(output_path))
    print(f"Generated {output_path}")


def volkswagen_taos_2023():
    build_manual(
        "vw_taos_2023.pdf",
        "Volkswagen Taos 2023 - Owner & Service Manual Excerpt",
        [
            (
                "1. Vehicle Identification",
                "Brand: Volkswagen\nModel: Taos\nYear: 2023\nEngine: 1.5L TSI Turbocharged 4-Cylinder\nTransmission: 8-speed Automatic\n",
            ),
            (
                "2. Anti-Theft Alarm System",
                "When will the alarm be triggered?\n"
                "The anti-theft alarm system will be triggered if any of the following unauthorized actions occur while the vehicle is locked:\n"
                "- A mechanically unlocked door is opened with the emergency key without turning on the ignition within 15 seconds.\n"
                "- The engine hood (bonnet) is opened.\n"
                "- The luggage compartment lid (tailgate) is opened.\n"
                "- The ignition is switched on with an unauthorized or unprogrammed key.\n"
                "- Movement is detected inside the vehicle passenger compartment (in vehicles equipped with interior monitoring).\n"
                "- The vehicle is tilted or lifted (in vehicles equipped with anti-tow sensors).\n"
                "To deactivate the alarm: Press the unlock button on the remote control key or switch on the ignition with a valid authorized key.\n",
            ),
            (
                "3. Climate Control and Air Recirculation",
                "When is the air recirculation mode turned off?\n"
                "The air recirculation mode prevents outside air, dust, and odors from entering the vehicle interior.\n"
                "Air recirculation mode is automatically turned off under the following conditions for safety and to prevent window fogging:\n"
                "- When the windshield defrost/defog button (MAX Defrost) is pressed.\n"
                "- When the air distribution control is rotated directly towards the windshield.\n"
                "- Automatically after a pre-determined duration if the interior humidity sensor detects condensation risk.\n"
                "- In reverse gear, recirculation may temporarily engage to prevent exhaust fumes from entering, and switches back to previous mode afterwards.\n",
            ),
            (
                "4. Seat Heating Operating Instructions",
                "When should the seat heating not be turned on?\n"
                "To prevent electrical malfunction, overheating, or damage to the seat upholstery:\n"
                "- Do not turn on the seat heating if the seat is damp, wet, or if liquid has been spilled onto it.\n"
                "- Do not turn on the seat heating if protective covers, blankets, cushions, or child safety seats are placed on the seat surface.\n"
                "- Do not turn on seat heating if sharp or heavy objects are placed on the seat, as this could damage the heating elements inside.\n"
                "- Persons with impaired pain or temperature perception should avoid using seat heating to prevent burns.\n",
            ),
            (
                "5. Engine Cooling & Temperature Warnings",
                "If the engine coolant temperature warning light illuminates in red on the instrument cluster:\n"
                "1. Safely pull over away from traffic and switch off the engine immediately.\n"
                "2. Allow the engine compartment to cool down for at least 20 minutes before opening the hood.\n"
                "3. CAUTION: Never open the coolant expansion tank cap while the engine is hot. Scalding steam or coolant may escape.\n"
                "4. Check the coolant level between the MIN and MAX markings on the translucent reservoir.\n"
                "5. If coolant is low, top up with G12evo or Volkswagen-approved coolant mix (50/50 with distilled water).\n"
                "6. Inspect for visible leaks in the radiator hoses and serpentine belt integrity.\n",
            ),
        ],
    )


def toyota_camry_2023():
    build_manual(
        "toyota_camry_2023.pdf",
        "Toyota Camry 2023 - Owner & Service Manual Excerpt",
        [
            (
                "1. Vehicle Identification",
                "Brand: Toyota\nModel: Camry\nYear: 2023\nEngine: 2.5L Dynamic Force 4-Cylinder\nTransmission: 8-speed Direct Shift Automatic\n",
            ),
            (
                "2. Toyota Safety Sense - Pre-Collision System",
                "When does the Pre-Collision System (PCS) intervene?\n"
                "The Pre-Collision System uses a millimeter-wave radar and camera to detect vehicles or pedestrians ahead.\n"
                "PCS will sound an alert and apply automatic braking when:\n"
                "- The system determines a forward collision is imminent and the driver has not braked.\n"
                "- A pedestrian is detected in the vehicle's path during daylight or well-lit night conditions.\n"
                "PCS may not activate or may be delayed if the sensor is blocked by dirt, snow, or heavy rain, or if the road curves sharply.\n"
                "To keep the system reliable, keep the front grille radar sensor and windshield camera area clean and undamaged.\n",
            ),
            (
                "3. Hybrid Battery & Warning Indicators (Camry Hybrid)",
                "If the hybrid system warning light illuminates:\n"
                "1. Safely stop the vehicle in a location away from traffic as soon as possible.\n"
                "2. Move the Power switch to OFF, then back to ON to see if the warning clears.\n"
                "3. If the warning persists, do not continue driving. Contact a Toyota dealer or roadside assistance.\n"
                "4. Do not attempt to open or service the hybrid battery pack yourself; it operates at high voltage.\n",
            ),
            (
                "4. Climate Control - When Air Recirculation Switches Off",
                "The automatic climate control system will switch out of recirculation mode automatically when:\n"
                "- The defogger/defrost setting is selected to clear the windshield.\n"
                "- The system detects the cabin air quality sensor (on equipped grades) reading elevated CO2 levels for an extended period.\n"
                "- The engine is started from cold in low ambient temperatures, to avoid window fogging during warm-up.\n",
            ),
            (
                "5. Tire Pressure Monitoring System (TPMS)",
                "When will the low tire pressure warning light turn on?\n"
                "The TPMS warning light illuminates when one or more tires is significantly underinflated relative to the placard pressure.\n"
                "Steps to resolve:\n"
                "1. Check all four tires (and spare, if equipped) with a calibrated gauge when tires are cold.\n"
                "2. Inflate to the pressure listed on the driver's door jamb placard, not the number on the tire sidewall.\n"
                "3. After adjusting, the light may take several minutes of driving to reset automatically.\n"
                "4. If the light flashes for 60-90 seconds then stays on solid, the TPMS itself may need service.\n",
            ),
            (
                "6. Seat Heating and Ventilation Precautions",
                "When should seat heating not be used?\n"
                "- Avoid using seat heating on wet or damp seats to prevent electrical short circuits.\n"
                "- Do not place blankets, cushions, or infant seats over the heated seating surface while active.\n"
                "- Individuals with reduced sensitivity to heat or pain (due to medication, disability, or medical condition) should not use seat heating unattended.\n",
            ),
        ],
    )


def honda_civic_2023():
    build_manual(
        "honda_civic_2023.pdf",
        "Honda Civic 2023 - Owner & Service Manual Excerpt",
        [
            (
                "1. Vehicle Identification",
                "Brand: Honda\nModel: Civic\nYear: 2023\nEngine: 2.0L i-VTEC 4-Cylinder / 1.5L VTEC Turbo (available)\nTransmission: CVT\n",
            ),
            (
                "2. Honda Sensing - Collision Mitigation Braking System (CMBS)",
                "When does CMBS activate?\n"
                "CMBS uses a front camera and radar to monitor traffic ahead and will:\n"
                "- Display a visual warning and sound an audible alert when a frontal collision risk is detected.\n"
                "- Apply light automatic braking if the driver does not respond, followed by strong braking if a collision becomes unavoidable.\n"
                "CMBS may be temporarily unavailable if the camera near the rearview mirror or the front radar emblem is obstructed by mud, ice, or stickers.\n",
            ),
            (
                "3. Anti-Theft System and Alarm Triggers",
                "The Civic's anti-theft alarm is triggered when:\n"
                "- A door, hood, or trunk is opened without first unlocking the vehicle with the remote transmitter or key.\n"
                "- An attempt is made to start the engine without a recognized immobilizer-coded key.\n"
                "- The battery is disconnected and reconnected while the system is armed (may require re-arming after unlock).\n"
                "To silence the alarm, press the unlock button on the remote or insert and turn a valid key in the driver's door cylinder.\n",
            ),
            (
                "4. Climate Control - Automatic Recirculation Behavior",
                "Air recirculation is automatically turned off in the following situations:\n"
                "- When MAX defrost mode is selected to clear windshield fog or ice.\n"
                "- When outside temperature is very low and the system prioritizes fresh air to reduce fogging.\n"
                "- When switched to Fresh mode manually by the driver via the recirculation button.\n",
            ),
            (
                "5. Engine Oil and Maintenance Minder",
                "When the Maintenance Minder indicates an oil change is due:\n"
                "1. Use only oil meeting Honda's specification (typically 0W-20 full synthetic) as listed on the oil fill cap.\n"
                "2. Check the oil level with the engine off and the vehicle on level ground, waiting a few minutes after shutdown.\n"
                "3. Reset the Maintenance Minder system only after the service has actually been performed.\n"
                "4. Persistent illumination of the oil pressure warning light (distinct from Maintenance Minder) means stop driving immediately.\n",
            ),
            (
                "6. Seat Heater Safety Precautions",
                "Seat heaters should not be switched on when:\n"
                "- The seat surface is wet, damp, or recently cleaned with liquid upholstery cleaner.\n"
                "- A child safety seat, cushion, or blanket covers the heated area, which can trap excess heat.\n"
                "- The occupant has diabetes, poor circulation, or reduced skin sensitivity, without first consulting a physician.\n",
            ),
        ],
    )


def ford_f150_2023():
    build_manual(
        "ford_f150_2023.pdf",
        "Ford F-150 2023 - Owner & Service Manual Excerpt",
        [
            (
                "1. Vehicle Identification",
                "Brand: Ford\nModel: F-150\nYear: 2023\nEngine: 3.5L EcoBoost V6 / 5.0L Ti-VCT V8 (available)\nTransmission: 10-speed Automatic\n",
            ),
            (
                "2. Pro Trailer Backup Assist",
                "When can Pro Trailer Backup Assist be used?\n"
                "This feature helps steer a trailer while reversing and requires:\n"
                "- A compatible trailer with the trailer reverse steering knob calibrated to the specific trailer.\n"
                "- Vehicle speed kept below approximately 5 mph (8 km/h) while the system is engaged.\n"
                "- The system will disengage automatically if the driver brakes hard, exceeds the speed threshold, or shifts out of Reverse.\n",
            ),
            (
                "3. Anti-Theft Alarm System",
                "The perimeter anti-theft alarm is triggered when, after the vehicle is locked:\n"
                "- A door, hood, or tailgate is opened without unlocking via the key fob or keypad.\n"
                "- The ignition is switched on with a key or fob not recognized by the SecuriLock immobilizer.\n"
                "- Vehicles equipped with the interior motion sensor detect movement inside the cabin.\n"
                "To disarm, unlock a door with the key fob or enter the correct code on the door keypad.\n",
            ),
            (
                "4. Towing and Payload - When Not to Tow",
                "Do not tow a trailer exceeding the vehicle's rated maximum towing capacity for its specific configuration (engine, cab, bed length, and axle ratio).\n"
                "Avoid towing when:\n"
                "- The trailer brake controller has not been properly installed and calibrated for trailers requiring electric brakes.\n"
                "- Total combined weight (vehicle + trailer + cargo + passengers) would exceed the Gross Combined Weight Rating (GCWR) listed on the door jamb placard.\n"
                "- Tires are worn, underinflated, or rated below the load requirement for towing.\n",
            ),
            (
                "5. Climate Control Air Recirculation",
                "Automatic air recirculation is switched off when:\n"
                "- The windshield defrost setting is selected to remove interior fog or frost.\n"
                "- The climate control system detects rising humidity levels that could fog the windshield.\n"
                "- The driver manually presses the recirculation button to select fresh outside air.\n",
            ),
            (
                "6. Seat Heating and Cooling Precautions",
                "Do not activate heated or cooled seats when:\n"
                "- The seat cushion is wet or damp, which can cause an electrical malfunction.\n"
                "- Aftermarket seat covers or thick blankets block normal airflow/heat transfer through the seat surface.\n"
                "- The occupant is unable to sense excessive heat or cold due to a medical condition, without medical guidance.\n",
            ),
        ],
    )


if __name__ == "__main__":
    volkswagen_taos_2023()
    toyota_camry_2023()
    honda_civic_2023()
    ford_f150_2023()
    print("All bundled sample manuals generated.")
