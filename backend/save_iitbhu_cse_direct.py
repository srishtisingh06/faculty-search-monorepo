from database.db_writer import save_faculty_profile
import re

RECORDS = [
    {"name": "Bhaskar Biswas", "designation": "Professor & HoD", "email": "bhaskar.cse@iitbhu.ac.in", "phone": "+91-542-716-5312", "research": ["Data Mining", "Web Mining", "Social Networks"]},
    {"name": "Rajeev Srivastava", "designation": "Professor (HAG)", "email": "rajeev.cse@iitbhu.ac.in", "phone": "+91-542-716-5320", "research": ["Image Processing", "Computer Vision", "AI", "Machine Learning"]},
    {"name": "Ruchir Gupta", "designation": "Professor", "email": "rgupta.cse@iitbhu.ac.in", "phone": "0542-716-5335", "research": ["Game Theory", "Edge Computing", "5G/6G Networks", "ML Algorithms"]},
    {"name": "Ravi Shankar Singh", "designation": "Professor", "email": "ravi.cse@iitbhu.ac.in", "phone": "+91-9935-8835-00", "research": ["Algorithms", "High Performance Computing", "Machine Learning"]},
    {"name": "Sanjay Kumar Singh", "designation": "Professor", "email": "sks.cse@iitbhu.ac.in", "phone": "+91-542-716-5317", "research": ["Computer Vision", "Pattern Recognition", "Machine Learning", "Deep Learning", "Data Science", "Medical Imaging"]},
    {"name": "Anil Kumar Singh", "designation": "Associate Professor", "email": "aksingh.cse@iitbhu.ac.in", "phone": "9648277700", "research": ["Natural Language Processing", "Computational Linguistics", "Information Retrieval"]},
    {"name": "Bidyut Kumar Patra", "designation": "Associate Professor", "email": "bidyut.cse@iitbhu.ac.in", "phone": "9337556928", "research": ["Data Mining", "Recommender System", "Machine Learning", "Educational Technology"]},
    {"name": "Hari Prabhat Gupta", "designation": "Associate Professor", "email": "hariprabhat.cse@iitbhu.ac.in", "phone": "+91-542-716-5344", "research": ["Computer Networks", "Smart Sensing", "IoT", "Wireless Communication"]},
    {"name": "Lakshmanan Kailasam", "designation": "Associate Professor", "email": "lakshmanank.cse@iitbhu.ac.in", "phone": "91-542-716-5328", "research": ["Reinforcement Learning", "LLMs", "Machine Learning"]},
    {"name": "Pratik Chattopadhyay", "designation": "Associate Professor", "email": "pratik.cse@iitbhu.ac.in", "phone": "0542-716-5325", "research": ["Image and Video Processing", "Computer Vision", "Pattern Recognition", "Generative Modelling"]},
    {"name": "Ravindranath Chowdary C", "designation": "Associate Professor", "email": "rchowdary.cse@iitbhu.ac.in", "phone": "+91 542 7165322", "research": ["Information Extraction", "Recommender Systems", "Text Summarization", "Applications of AI"]},
    {"name": "Sukomal Pal", "designation": "Associate Professor", "email": "spal.cse@iitbhu.ac.in", "phone": "+919471191533", "research": ["Information Retrieval", "Recommender Systems", "Text Mining", "Data Science"]},
    {"name": "Tanima Dutta", "designation": "Associate Professor", "email": "tanima.cse@iitbhu.ac.in", "phone": "+91-542-716-5341", "research": ["Artificial Intelligence", "Machine Learning", "Computer Vision", "Cyber Security", "Intelligent IoT"]},
    {"name": "Ajay Pratap", "designation": "Associate Professor", "email": "ajay.cse@iitbhu.ac.in", "phone": "+91-542-7165098", "research": ["IoT", "Blockchain", "UAV", "Cloud/Fog Computing", "Applied AI/ML"]},
    {"name": "Amrita Chaturvedi", "designation": "Associate Professor", "email": "amrita.cse@iitbhu.ac.in", "phone": "0542-716-5314", "research": ["Software Architecture and Design Patterns", "Ontologies", "Artificial Intelligence", "Semantic Web"]},
    {"name": "Aparajita Khan", "designation": "Assistant Professor", "email": "aparajita.cse@iitbhu.ac.in", "phone": "7384850465", "research": ["Machine Learning", "Deep Learning", "Biomedical Data Science", "Cancer Epidemiology", "Medical NLP"]},
    {"name": "Awaneesh Kumar Yadav", "designation": "Assistant Professor", "email": "awaneesh.cse@iitbhu.ac.in", "phone": "", "research": []},
    {"name": "Harsh Kasyap", "designation": "Assistant Professor", "email": "hkasyap.cse@iitbhu.ac.in", "phone": "", "research": ["Privacy Preserving Machine Learning", "Federated Learning", "Machine Learning Security", "Trustworthy AI"]},
    {"name": "Indra Deep Mastan", "designation": "Assistant Professor", "email": "indra.cse@iitbhu.ac.in", "phone": "", "research": ["Deep Learning for Computer Vision", "Unsupervised learning", "Vision and Language Models"]},
    {"name": "Mayank Swarnkar", "designation": "Associate Professor", "email": "mayank.cse@iitbhu.ac.in", "phone": "", "research": ["Network Security", "Network Traffic Classification", "Intrusion Detection Systems"]},
    {"name": "Obbattu Sai Lakshmi Bhavana", "designation": "Assistant Professor", "email": "oslbhavana.cse@iitbhu.ac.in", "phone": "", "research": ["Security and Privacy"]},
    {"name": "Prasenjit Chanak", "designation": "Associate Professor", "email": "prasenjit.cse@iitbhu.ac.in", "phone": "+91-9424346550", "research": ["Wireless Sensor Networks", "Internet of Things (IoT)", "Cyber-Physical Networks (CPN)"]},
    {"name": "Soumitra Ghosh", "designation": "Assistant Professor", "email": "soumitra.cse@iitbhu.ac.in", "phone": "", "research": ["Affective Computing & Emotion Intelligence", "Natural Language Processing", "Large Language Models", "Human-centered AI"]},
    {"name": "Vignesh Sivaraman", "designation": "Assistant Professor", "email": "vignesh.cse@iitbhu.ac.in", "phone": "+91 0542 716 535", "research": ["Quantum Machine Learning", "QML and Generative AI for Network Security", "6G Networks"]},
    {"name": "Vinayak Shrivastava", "designation": "Assistant Professor", "email": "vsrivastava.cse@iitbhu.ac.in", "phone": "+91-542-716-5327", "research": ["Software Engineering", "Software Reengineering"]},
    {"name": "A. K. Agrawal", "designation": "Professor (Retired)", "email": "akagrawal.cse@iitbhu.ac.in", "phone": "", "research": []},
    {"name": "R. B. Mishra", "designation": "Professor (Retired)", "email": "mishravi.cse@iitbhu.ac.in", "phone": "", "research": []},
    {"name": "K. K. Shukla", "designation": "Professor (Retired)", "email": "kkshukla.cse@iitbhu.ac.in", "phone": "", "research": []},
    {"name": "Anil Kumar Tripathi", "designation": "Professor (Retired)", "email": "aktripathi.cse@iitbhu.ac.in", "phone": "", "research": []},
]

def slugify(s):
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")

saved = 0
for r in RECORDS:
    slug = slugify(r["name"])
    profile_url = f"https://www.iitbhu.ac.in/dept/cse/people/{slug}"
    profile = {
        "faculty_name": r["name"],
        "designation": r["designation"],
        "email": r["email"],
        "phone": r["phone"],
        "research_interests": r["research"],
        "profile_url": profile_url,
        "institute_name": "IIT (BHU) Varanasi",
        "institute_type": "IIT",
        "department": "Computer Science & Engineering",
    }
    ok = save_faculty_profile(
        profile,
        institute_url="https://www.iitbhu.ac.in",
        institute_type="IIT",
        city="Varanasi",
        state="Uttar Pradesh"
    )
    if ok:
        saved += 1

print(f"Saved {saved}/{len(RECORDS)} CSE faculty to PostgreSQL!")
