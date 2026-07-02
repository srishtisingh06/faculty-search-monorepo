from database.db_writer import save_faculty_profile

RECORDS = [
    {"name": "Amrit B. Sahu", "designation": "Assistant Professor", "email": "amritbsahu@iitbbs.ac.in", "phone": "", "research": ["Clean Combustion Technology", "Sustainable Fuels", "Propulsion", "Optical Diagnostics", "Energy"]},
    {"name": "Anirban Bhattacharya", "designation": "Associate Professor", "email": "anirban@iitbbs.ac.in", "phone": "+91 9886557225", "research": ["Solidification and microstructure modelling", "Additive manufacturing", "Energy"]},
    {"name": "Arun Kumar Pradhan", "designation": "Professor", "email": "akpradhan@iitbbs.ac.in", "phone": "674-713-7112", "research": ["Composite Materials & Structures", "Smart Materials & Structures", "Solid Mechanics", "Fracture"]},
    {"name": "Chetan", "designation": "Assistant Professor", "email": "chetan@iitbbs.ac.in", "phone": "674-713-7134", "research": ["Sustainable Machining", "Micro-Machining", "Surface Engineering", "Tribology in Manufacturing"]},
    {"name": "Divyansh Patel", "designation": "Assistant Professor", "email": "dspatel@iitbbs.ac.in", "phone": "06747137162", "research": ["Advanced manufacturing processes", "Post processing of additively manufactured components"]},
    {"name": "Gaurav Bartarya", "designation": "Associate Professor", "email": "bartarya@iitbbs.ac.in", "phone": "674-713-7114", "research": ["Conventional Machining of hard material", "Modeling and simulation of Machining process"]},
    {"name": "Madhusmita Mallick", "designation": "Assistant Professor", "email": "mmallick@iitbbs.ac.in", "phone": "", "research": []},
    {"name": "Mahendaran Uchimali", "designation": "Assistant Professor", "email": "mahendaran@iitbbs.ac.in", "phone": "", "research": ["Computational Solid Mechanics", "Discrete Element Modelling", "Shape Memory Alloys", "Thermal"]},
    {"name": "Manas Mohan Mahapatra", "designation": "Professor", "email": "mmmahapatra@iitbbs.ac.in", "phone": "+91 674 713-7116", "research": ["Welding Residual Stress & Distortion control", "Friction Stir Welding Tool Design", "Friction"]},
    {"name": "Manas Ranjan Pattnayak", "designation": "Assistant Professor", "email": "mrpattnayak@iitbbs.ac.in", "phone": "+91 674 713 7169", "research": ["Lubrication science", "Bearing design", "Vibrations and Rotordynamics", "Air lubrication"]},
    {"name": "Maneesh Punetha", "designation": "Assistant Professor", "email": "maneeshp@iitbbs.ac.in", "phone": "", "research": ["Clean Energy", "Hydrogen Safety", "Nuclear Energy Safety", "Thermal Hydraulics", "Heat Transfer"]},
    {"name": "Mihir Kumar Das", "designation": "Professor", "email": "mihirdas@iitbbs.ac.in", "phone": "674-713-7118", "research": ["Two Phase Heat Transfer", "Electronic Cooling", "Phase Change Material", "Thermal Management"]},
    {"name": "Mihir Kumar Pandit", "designation": "Professor", "email": "mihir@iitbbs.ac.in", "phone": "+91 674-713 7120", "research": ["Design and Solid Mechanics", "Composite Materials", "Sandwich Structures", "Finite Element"]},
    {"name": "Pattabhi Ramaiah Budarapu", "designation": "Associate Professor", "email": "pattabhi@iitbbs.ac.in", "phone": "+91-674-7137124", "research": ["Multiscale methods for fracture", "molecular dynamics", "fracture in multiphysics problems"]},
    {"name": "Prasenjit Rath", "designation": "Associate Professor", "email": "prath@iitbbs.ac.in", "phone": "+91 674 713-7126", "research": ["Numerical Transport Phenomena", "Ultra Fast Radiation Heat Transfer", "CFD/HT"]},
    {"name": "Rahul Kumar", "designation": "Assistant Professor", "email": "kumarr@iitbbs.ac.in", "phone": "+91 674 713 7170", "research": ["Stochastic Modelling & Uncertainty Quantification", "Nonlinear"]},
    {"name": "Sasidhar Kondaraju", "designation": "Associate Professor", "email": "sasidhar@iitbbs.ac.in", "phone": "0674-713-7132", "research": ["Microfluidics", "Surface wettability", "Interfacial Science", "Micro/Nanoscale Heat and Fluid"]},
    {"name": "Satish Dhandole", "designation": "Associate Professor", "email": "satish@iitbbs.ac.in", "phone": "+91 674 713 7136", "research": ["Dynamic Design", "Vibro-Acoustic", "Experimental Modal Analysis", "Mechanism Design"]},
    {"name": "Satish Kumar Panda", "designation": "Assistant Professor", "email": "skpanda@iitbbs.ac.in", "phone": "", "research": ["Biomedical Engineering", "Medical Image Processing", "Artificial Intelligence", "Deep Learning"]},
    {"name": "Satyanarayan Panigrahi", "designation": "Associate Professor", "email": "psatyan@iitbbs.ac.in", "phone": "+91 674 713 7138", "research": ["Technical Acoustics", "Industrial Noise Control", "Automotive noise control", "Acoustic"]},
    {"name": "Soham Roychowdhury", "designation": "Assistant Professor", "email": "soham@iitbbs.ac.in", "phone": "674-713-7110", "research": ["Computational Solid Mechanics", "Mechanics of Inflatable Structures", "Nonlinear Elasticiy"]},
    {"name": "Soumya Ranjan Sahoo", "designation": "Assistant Professor", "email": "soumyasahoo@iitbbs.ac.in", "phone": "06747137106", "research": ["Computational Solid Mechanics", "Smart Composite Structures", "Active Vibration Control"]},
    {"name": "Srinivasa Ramanujam Kannan", "designation": "Associate Professor", "email": "sramanujam@iitbbs.ac.in", "phone": "0674-7137140", "research": ["Thermal Radiation", "Inverse problems in heat transfer", "Stochastic optimization", "Algorithms"]},
    {"name": "Suman Deb", "designation": "Assistant Professor", "email": "sumandeb@iitbbs.ac.in", "phone": "+91 674 713 7181", "research": ["Advanced metal forming", "Bulk and sheet metal forming", "Roll forming", "Microforming"]},
    {"name": "Suvradip Mullick", "designation": "Associate Professor", "email": "suvradip@iitbbs.ac.in", "phone": "674-713-7142", "research": ["Laser material processing", "Non-conventional machining"]},
    {"name": "Swarup Kumar Mahapatra", "designation": "Professor", "email": "swarup@iitbbs.ac.in", "phone": "+91 674 713 7144", "research": ["Thermal Radiation Modelling", "Conjugate Heat and Mass Transfer", "Bio-Heat Transfer"]},
    {"name": "V. Pandu Ranga", "designation": "Professor", "email": "pandu@iitbbs.ac.in", "phone": "674-713-7122", "research": ["Robotics", "Manufacturing", "Soft Computing"]},
    {"name": "Venugopal Arumuru", "designation": "Associate Professor", "email": "venugopal@iitbbs.ac.in", "phone": "06747137146", "research": ["Fluid Structure Interaction and unsteady Aero-Hydrodynamics", "CFD", "Turbulence and Flow"]},
    {"name": "Vimalesh Muralidharan", "designation": "Assistant Professor", "email": "vimalesh@iitbbs.ac.in", "phone": "0674-713-7177", "research": ["Robots and Mechanisms", "Serial and Parallel Manipulators", "Bio-inspired"]},
    {"name": "Yogesh G. Bhumkar", "designation": "Associate Professor", "email": "bhumkar@iitbbs.ac.in", "phone": "+91-674-713-7148", "research": ["High Accuracy, High-Performance Computing", "Computational Aeroacoustics", "DNS and LES"]},
]

import re
def slugify(s):
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")

saved = 0
for r in RECORDS:
    slug = slugify(r["name"])
    profile_url = f"https://old.iitbbs.ac.in/school-people-faculty.php?code=ms#{slug}"
    profile = {
        "faculty_name": r["name"],
        "designation": r["designation"],
        "email": r["email"],
        "phone": r["phone"],
        "research_interests": r["research"],
        "profile_url": profile_url,
        "institute_name": "IIT Bhubaneswar",
        "institute_type": "IIT",
        "department": "Mechanical Engineering",
    }
    ok = save_faculty_profile(
        profile,
        institute_url="https://www.iitbbs.ac.in",
        institute_type="IIT",
        city="Bhubaneswar",
        state="Odisha"
    )
    if ok:
        saved += 1

print(f"Saved {saved}/{len(RECORDS)} ME faculty to PostgreSQL!")
