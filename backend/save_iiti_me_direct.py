from database.db_writer import save_faculty_profile
import re

RECORDS = [
    {"name": "Suhas S. Joshi", "designation": "Director", "research": ["Mechanical Engineering"]},
    {"name": "Devendra Deshmukh", "designation": "Professor", "research": ["Combustion", "CFD", "Sprays"]},
    {"name": "Pavan Kumar Kankar", "designation": "Professor", "research": ["Fault Diagnosis of Mechanical Components", "Condition Monitoring"]},
    {"name": "Santosh Kumar Sahu", "designation": "Professor", "research": ["Engineering", "Energy", "Chemical Engineering", "Physics"]},
    {"name": "Ritunesh Kumar", "designation": "Professor", "research": ["Engineering", "Energy", "Environmental Science", "Chemistry"]},
    {"name": "Anand Parey", "designation": "Professor", "research": ["Condition monitoring", "Noise and vibration isolation"]},
    {"name": "Dhinakaran Shanmugam", "designation": "Professor", "research": ["Computational Fluid Dynamics and Heat Transfer"]},
    {"name": "Iyamperumal Anand Palani", "designation": "Professor", "research": ["Laser assisted micro-manufacturing", "Surface processing"]},
    {"name": "Bhupesh Kumar Lad", "designation": "Professor", "research": ["Engineering", "Computer Science", "Business Management"]},
    {"name": "Ankur Miglani", "designation": "Associate Professor", "research": ["Mechanical Engineering"]},
    {"name": "Shailesh Kundalwal", "designation": "Associate Professor", "research": ["Mechanics of Nanostructures", "Nanomechanics", "Micromechanics"]},
    {"name": "Satyanarayan Patel", "designation": "Associate Professor", "research": ["Mechanical Engineering"]},
    {"name": "Kazi Sabiruddin", "designation": "Associate Professor", "research": ["Materials Science", "Engineering Physics", "Astronomy"]},
    {"name": "Satyajit Chatterjee", "designation": "Associate Professor", "research": ["Materials Science", "Physics and Astronomy", "Engineering"]},
    {"name": "Aman Khurana", "designation": "Assistant Professor (Grade-II)", "research": ["Mechanics of Soft Active Materials", "Finite Element Methods"]},
    {"name": "Vijai Laxmi", "designation": "Assistant Professor (Grade-II)", "research": ["Microfluidics", "Thermal and Fluid Engineering"]},
    {"name": "Mayank Chouksey", "designation": "Assistant Professor (Grade-II)", "research": ["Mechanics"]},
    {"name": "Janakiraman S", "designation": "Assistant Professor (Grade-II)", "research": ["Synthesis and Characterization of Separator Electrodes"]},
    {"name": "Ashish Rajak", "designation": "Assistant Professor (Grade-II)", "research": []},
    {"name": "Krishna Mohan Kumar", "designation": "Assistant Professor (Grade-I)", "research": []},
    {"name": "Dan Sathiaraj", "designation": "Assistant Professor", "research": ["Mechanical Engineering"]},
    {"name": "Vibhor Pandhare", "designation": "Assistant Professor", "research": ["Cyber-Physical Systems", "Industrial Artificial Intelligence"]},
    {"name": "Harekrishna Yadav", "designation": "Assistant Professor", "research": ["Mechanical Engineering"]},
    {"name": "Indrasen Singh", "designation": "Assistant Professor", "research": ["Computational solid mechanics", "Metallic glass", "Nanotechnology"]},
    {"name": "Girish Chandra Verma", "designation": "Assistant Professor", "research": ["Mechanical Engineering"]},
    {"name": "Yuvraj Kumar Madhukar", "designation": "Assistant Professor", "research": ["Laser Material Processing", "Water Assisted Laser Processing"]},
    {"name": "Neelesh Kumar Jain", "designation": "Professor (HAG)", "research": ["Additive Manufacturing", "3D-Printing", "Gear Finishing"]},
]

def slugify(s):
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")

saved = 0
for r in RECORDS:
    slug = slugify(r["name"])
    profile_url = f"https://iiti.irins.org/faculty/index/Department+of+Mechanical+Engineering#{slug}"
    profile = {
        "faculty_name": r["name"],
        "designation": r["designation"],
        "email": "",
        "phone": "",
        "research_interests": r["research"],
        "profile_url": profile_url,
        "institute_name": "IIT Indore",
        "institute_type": "IIT",
        "department": "Mechanical Engineering",
    }
    ok = save_faculty_profile(
        profile,
        institute_url="https://www.iiti.ac.in",
        institute_type="IIT",
        city="Indore",
        state="Madhya Pradesh"
    )
    if ok:
        saved += 1

print(f"Saved {saved}/{len(RECORDS)} ME faculty to PostgreSQL!")
