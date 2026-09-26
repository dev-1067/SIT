import os
from fpdf import FPDF

class PDFManual(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 14)
        self.cell(0, 10, 'Volkswagen Taos 2023 - Owner & Service Manual Excerpt', border=False, align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

def create_manual():
    pdf = PDFManual()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font('Helvetica', '', 11)

    sections = [
        ("1. Vehicle Identification", 
         "Brand: Volkswagen\nModel: Taos\nYear: 2023\nEngine: 1.5L TSI Turbocharged 4-Cylinder\nTransmission: 8-speed Automatic\n"),
        
        ("2. Anti-Theft Alarm System", 
         "When will the alarm be triggered?\n"
         "The anti-theft alarm system will be triggered if any of the following unauthorized actions occur while the vehicle is locked:\n"
         "- A mechanically unlocked door is opened with the emergency key without turning on the ignition within 15 seconds.\n"
         "- The engine hood (bonnet) is opened.\n"
         "- The luggage compartment lid (tailgate) is opened.\n"
         "- The ignition is switched on with an unauthorized or unprogrammed key.\n"
         "- Movement is detected inside the vehicle passenger compartment (in vehicles equipped with interior monitoring).\n"
         "- The vehicle is tilted or lifted (in vehicles equipped with anti-tow sensors).\n"
         "To deactivate the alarm: Press the unlock button on the remote control key or switch on the ignition with a valid authorized key.\n"),

        ("3. Climate Control and Air Recirculation",
         "When is the air recirculation mode turned off?\n"
         "The air recirculation mode prevents outside air, dust, and odors from entering the vehicle interior.\n"
         "Air recirculation mode is automatically turned off under the following conditions for safety and to prevent window fogging:\n"
         "- When the windshield defrost/defog button (MAX Defrost) is pressed.\n"
         "- When the air distribution control is rotated directly towards the windshield.\n"
         "- Automatically after a pre-determined duration if the interior humidity sensor detects condensation risk.\n"
         "- In reverse gear, recirculation may temporarily engage to prevent exhaust fumes from entering, and switches back to previous mode afterwards.\n"),

        ("4. Seat Heating Operating Instructions",
         "When should the seat heating not be turned on?\n"
         "To prevent electrical malfunction, overheating, or damage to the seat upholstery:\n"
         "- Do not turn on the seat heating if the seat is damp, wet, or if liquid has been spilled onto it.\n"
         "- Do not turn on the seat heating if protective covers, blankets, cushions, or child safety seats are placed on the seat surface.\n"
         "- Do not turn on seat heating if sharp or heavy objects are placed on the seat, as this could damage the heating elements inside.\n"
         "- Persons with impaired pain or temperature perception should avoid using seat heating to prevent burns.\n"),

        ("5. Engine Cooling & Temperature Warnings",
         "If the engine coolant temperature warning light illuminates in red on the instrument cluster:\n"
         "1. Safely pull over away from traffic and switch off the engine immediately.\n"
         "2. Allow the engine compartment to cool down for at least 20 minutes before opening the hood.\n"
         "3. CAUTION: Never open the coolant expansion tank cap while the engine is hot. Scalding steam or coolant may escape.\n"
         "4. Check the coolant level between the MIN and MAX markings on the translucent reservoir.\n"
         "5. If coolant is low, top up with G12evo or Volkswagen-approved coolant mix (50/50 with distilled water).\n"
         "6. Inspect for visible leaks in the radiator hoses and serpentine belt integrity.\n")
    ]

    for title, content in sections:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 8, title, new_x='LMARGIN', new_y='NEXT')
        pdf.set_font('Helvetica', '', 10)
        pdf.multi_cell(0, 5, content)
        pdf.ln(3)

    output_path = "sample_volkswagen_taos_2023_manual.pdf"
    pdf.output(output_path)
    print(f"Sample PDF created successfully at {output_path}")

if __name__ == "__main__":
    create_manual()
