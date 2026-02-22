from django.core.management.base import BaseCommand
from academics.models import Subject, Faculty


class Command(BaseCommand):
    help = 'Load JNTUH B.Tech subjects for all departments'

    def handle(self, *args, **kwargs):
        """Load JNTUH B.Tech curriculum subjects."""
        
        subjects_data = [
            # Common Subjects for All Branches (Semester 1 & 2)
            {"code": "MA101", "name": "Mathematics-I", "department": "", "semester": 1, "credits": 4},
            {"code": "PH101", "name": "Applied Physics", "department": "", "semester": 1, "credits": 4},
            {"code": "CH101", "name": "Applied Chemistry", "department": "", "semester": 1, "credits": 4},
            {"code": "EG101", "name": "Engineering Graphics", "department": "", "semester": 1, "credits": 4},
            {"code": "CS101", "name": "Programming for Problem Solving", "department": "", "semester": 1, "credits": 3},
            {"code": "EN101", "name": "English", "department": "", "semester": 1, "credits": 2},
            
            {"code": "MA102", "name": "Mathematics-II", "department": "", "semester": 2, "credits": 4},
            {"code": "PH102", "name": "Applied Physics Lab", "department": "", "semester": 2, "credits": 2},
            {"code": "CH102", "name": "Applied Chemistry Lab", "department": "", "semester": 2, "credits": 2},
            {"code": "ME101", "name": "Engineering Workshop", "department": "", "semester": 2, "credits": 2},
            {"code": "CS102", "name": "Programming for Problem Solving Lab", "department": "", "semester": 2, "credits": 2},
            {"code": "EN102", "name": "English Language Communication Skills Lab", "department": "", "semester": 2, "credits": 1},
            
            # CSE Department
            {"code": "CS201", "name": "Data Structures", "department": "CSE", "semester": 3, "credits": 4},
            {"code": "CS202", "name": "Object Oriented Programming", "department": "CSE", "semester": 3, "credits": 3},
            {"code": "CS203", "name": "Digital Logic Design", "department": "CSE", "semester": 3, "credits": 3},
            {"code": "MA201", "name": "Discrete Mathematics", "department": "CSE", "semester": 3, "credits": 4},
            {"code": "CS204", "name": "Computer Organization", "department": "CSE", "semester": 3, "credits": 3},
            
            {"code": "CS301", "name": "Database Management Systems", "department": "CSE", "semester": 4, "credits": 4},
            {"code": "CS302", "name": "Operating Systems", "department": "CSE", "semester": 4, "credits": 3},
            {"code": "CS303", "name": "Design and Analysis of Algorithms", "department": "CSE", "semester": 4, "credits": 4},
            {"code": "CS304", "name": "Software Engineering", "department": "CSE", "semester": 4, "credits": 3},
            {"code": "CS305", "name": "Computer Networks", "department": "CSE", "semester": 4, "credits": 3},
            
            {"code": "CS401", "name": "Compiler Design", "department": "CSE", "semester": 5, "credits": 3},
            {"code": "CS402", "name": "Theory of Computation", "department": "CSE", "semester": 5, "credits": 3},
            {"code": "CS403", "name": "Machine Learning", "department": "CSE", "semester": 5, "credits": 3},
            {"code": "CS404", "name": "Web Technologies", "department": "CSE", "semester": 5, "credits": 3},
            {"code": "CS405", "name": "Cryptography and Network Security", "department": "CSE", "semester": 5, "credits": 3},
            
            {"code": "CS501", "name": "Mobile Application Development", "department": "CSE", "semester": 6, "credits": 3},
            {"code": "CS502", "name": "Cloud Computing", "department": "CSE", "semester": 6, "credits": 3},
            {"code": "CS503", "name": "Artificial Intelligence", "department": "CSE", "semester": 6, "credits": 3},
            {"code": "CS504", "name": "Big Data Analytics", "department": "CSE", "semester": 6, "credits": 3},
            {"code": "CS505", "name": "Internet of Things", "department": "CSE", "semester": 6, "credits": 3},
            
            {"code": "CS601", "name": "Deep Learning", "department": "CSE", "semester": 7, "credits": 3},
            {"code": "CS602", "name": "Blockchain Technology", "department": "CSE", "semester": 7, "credits": 3},
            {"code": "CS603", "name": "Software Testing", "department": "CSE", "semester": 7, "credits": 3},
            
            # ECE Department
            {"code": "EC201", "name": "Network Analysis", "department": "ECE", "semester": 3, "credits": 4},
            {"code": "EC202", "name": "Electronic Devices and Circuits", "department": "ECE", "semester": 3, "credits": 4},
            {"code": "EC203", "name": "Signals and Systems", "department": "ECE", "semester": 3, "credits": 3},
            {"code": "EC204", "name": "Electronic Circuit Analysis", "department": "ECE", "semester": 3, "credits": 3},
            
            {"code": "EC301", "name": "Analog Communications", "department": "ECE", "semester": 4, "credits": 4},
            {"code": "EC302", "name": "Digital Signal Processing", "department": "ECE", "semester": 4, "credits": 4},
            {"code": "EC303", "name": "Linear IC Applications", "department": "ECE", "semester": 4, "credits": 3},
            {"code": "EC304", "name": "Electromagnetic Theory", "department": "ECE", "semester": 4, "credits": 3},
            
            {"code": "EC401", "name": "Digital Communications", "department": "ECE", "semester": 5, "credits": 4},
            {"code": "EC402", "name": "Microprocessors and Microcontrollers", "department": "ECE", "semester": 5, "credits": 4},
            {"code": "EC403", "name": "VLSI Design", "department": "ECE", "semester": 5, "credits": 3},
            {"code": "EC404", "name": "Control Systems", "department": "ECE", "semester": 5, "credits": 3},
            
            {"code": "EC501", "name": "Wireless Communications", "department": "ECE", "semester": 6, "credits": 3},
            {"code": "EC502", "name": "Embedded Systems", "department": "ECE", "semester": 6, "credits": 3},
            {"code": "EC503", "name": "Optical Communications", "department": "ECE", "semester": 6, "credits": 3},
            {"code": "EC504", "name": "Radar Systems", "department": "ECE", "semester": 6, "credits": 3},
            
            # EEE Department
            {"code": "EE201", "name": "Electrical Circuit Analysis", "department": "EEE", "semester": 3, "credits": 4},
            {"code": "EE202", "name": "Electrical Machines-I", "department": "EEE", "semester": 3, "credits": 4},
            {"code": "EE203", "name": "Electromagnetic Fields", "department": "EEE", "semester": 3, "credits": 3},
            {"code": "EE204", "name": "Electronic Devices and Circuits", "department": "EEE", "semester": 3, "credits": 3},
            
            {"code": "EE301", "name": "Electrical Machines-II", "department": "EEE", "semester": 4, "credits": 4},
            {"code": "EE302", "name": "Power Systems-I", "department": "EEE", "semester": 4, "credits": 4},
            {"code": "EE303", "name": "Control Systems", "department": "EEE", "semester": 4, "credits": 3},
            {"code": "EE304", "name": "Electrical Measurements", "department": "EEE", "semester": 4, "credits": 3},
            
            {"code": "EE401", "name": "Power Electronics", "department": "EEE", "semester": 5, "credits": 4},
            {"code": "EE402", "name": "Power Systems-II", "department": "EEE", "semester": 5, "credits": 4},
            {"code": "EE403", "name": "Microprocessors and Microcontrollers", "department": "EEE", "semester": 5, "credits": 3},
            {"code": "EE404", "name": "Electrical Machine Design", "department": "EEE", "semester": 5, "credits": 3},
            
            {"code": "EE501", "name": "Renewable Energy Systems", "department": "EEE", "semester": 6, "credits": 3},
            {"code": "EE502", "name": "High Voltage Engineering", "department": "EEE", "semester": 6, "credits": 3},
            {"code": "EE503", "name": "Power System Protection", "department": "EEE", "semester": 6, "credits": 3},
            {"code": "EE504", "name": "Electric Drives", "department": "EEE", "semester": 6, "credits": 3},
            
            # MECH Department
            {"code": "ME201", "name": "Engineering Mechanics", "department": "MECH", "semester": 3, "credits": 4},
            {"code": "ME202", "name": "Strength of Materials", "department": "MECH", "semester": 3, "credits": 4},
            {"code": "ME203", "name": "Thermodynamics", "department": "MECH", "semester": 3, "credits": 3},
            {"code": "ME204", "name": "Manufacturing Technology", "department": "MECH", "semester": 3, "credits": 3},
            
            {"code": "ME301", "name": "Kinematics of Machinery", "department": "MECH", "semester": 4, "credits": 4},
            {"code": "ME302", "name": "Fluid Mechanics", "department": "MECH", "semester": 4, "credits": 4},
            {"code": "ME303", "name": "Metallurgy and Material Science", "department": "MECH", "semester": 4, "credits": 3},
            {"code": "ME304", "name": "Thermal Engineering", "department": "MECH", "semester": 4, "credits": 3},
            
            {"code": "ME401", "name": "Design of Machine Elements", "department": "MECH", "semester": 5, "credits": 4},
            {"code": "ME402", "name": "Heat Transfer", "department": "MECH", "semester": 5, "credits": 3},
            {"code": "ME403", "name": "Dynamics of Machinery", "department": "MECH", "semester": 5, "credits": 3},
            {"code": "ME404", "name": "Metrology and Machine Tools", "department": "MECH", "semester": 5, "credits": 3},
            
            {"code": "ME501", "name": "Automobile Engineering", "department": "MECH", "semester": 6, "credits": 3},
            {"code": "ME502", "name": "CAD/CAM", "department": "MECH", "semester": 6, "credits": 3},
            {"code": "ME503", "name": "Refrigeration and Air Conditioning", "department": "MECH", "semester": 6, "credits": 3},
            {"code": "ME504", "name": "Industrial Engineering", "department": "MECH", "semester": 6, "credits": 3},
            
            # CIVIL Department
            {"code": "CE201", "name": "Surveying", "department": "CIVIL", "semester": 3, "credits": 4},
            {"code": "CE202", "name": "Building Materials and Construction", "department": "CIVIL", "semester": 3, "credits": 4},
            {"code": "CE203", "name": "Engineering Mechanics", "department": "CIVIL", "semester": 3, "credits": 3},
            {"code": "CE204", "name": "Strength of Materials", "department": "CIVIL", "semester": 3, "credits": 4},
            
            {"code": "CE301", "name": "Structural Analysis", "department": "CIVIL", "semester": 4, "credits": 4},
            {"code": "CE302", "name": "Fluid Mechanics", "department": "CIVIL", "semester": 4, "credits": 4},
            {"code": "CE303", "name": "Concrete Technology", "department": "CIVIL", "semester": 4, "credits": 3},
            {"code": "CE304", "name": "Geotechnical Engineering", "department": "CIVIL", "semester": 4, "credits": 4},
            
            {"code": "CE401", "name": "Design of RC Structures", "department": "CIVIL", "semester": 5, "credits": 4},
            {"code": "CE402", "name": "Transportation Engineering", "department": "CIVIL", "semester": 5, "credits": 3},
            {"code": "CE403", "name": "Water Resources Engineering", "department": "CIVIL", "semester": 5, "credits": 3},
            {"code": "CE404", "name": "Environmental Engineering", "department": "CIVIL", "semester": 5, "credits": 3},
            
            {"code": "CE501", "name": "Design of Steel Structures", "department": "CIVIL", "semester": 6, "credits": 4},
            {"code": "CE502", "name": "Foundation Engineering", "department": "CIVIL", "semester": 6, "credits": 3},
            {"code": "CE503", "name": "Irrigation Engineering", "department": "CIVIL", "semester": 6, "credits": 3},
            {"code": "CE504", "name": "Estimation and Quantity Surveying", "department": "CIVIL", "semester": 6, "credits": 3},
            
            # IT Department
            {"code": "IT201", "name": "Data Structures", "department": "IT", "semester": 3, "credits": 4},
            {"code": "IT202", "name": "Object Oriented Programming through Java", "department": "IT", "semester": 3, "credits": 3},
            {"code": "IT203", "name": "Digital Logic Design", "department": "IT", "semester": 3, "credits": 3},
            {"code": "IT204", "name": "Computer Organization", "department": "IT", "semester": 3, "credits": 3},
            
            {"code": "IT301", "name": "Database Management Systems", "department": "IT", "semester": 4, "credits": 4},
            {"code": "IT302", "name": "Operating Systems", "department": "IT", "semester": 4, "credits": 3},
            {"code": "IT303", "name": "Computer Networks", "department": "IT", "semester": 4, "credits": 3},
            {"code": "IT304", "name": "Software Engineering", "department": "IT", "semester": 4, "credits": 3},
            
            {"code": "IT401", "name": "Python Programming", "department": "IT", "semester": 5, "credits": 3},
            {"code": "IT402", "name": "Web Technologies", "department": "IT", "semester": 5, "credits": 3},
            {"code": "IT403", "name": "Data Warehousing and Data Mining", "department": "IT", "semester": 5, "credits": 3},
            {"code": "IT404", "name": "Network Security", "department": "IT", "semester": 5, "credits": 3},
            
            {"code": "IT501", "name": "Mobile Computing", "department": "IT", "semester": 6, "credits": 3},
            {"code": "IT502", "name": "Cloud Computing", "department": "IT", "semester": 6, "credits": 3},
            {"code": "IT503", "name": "Machine Learning", "department": "IT", "semester": 6, "credits": 3},
            {"code": "IT504", "name": "Information Retrieval Systems", "department": "IT", "semester": 6, "credits": 3},
        ]
        
        created = 0
        updated = 0
        
        for subject_data in subjects_data:
            subject, is_created = Subject.objects.update_or_create(
                code=subject_data['code'],
                defaults={
                    'name': subject_data['name'],
                    'department': subject_data['department'],
                    'semester': subject_data['semester'],
                    'credits': subject_data['credits']
                }
            )
            if is_created:
                created += 1
            else:
                updated += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✓ JNTUH Subjects loaded successfully!\n'
            f'  Created: {created} subjects\n'
            f'  Updated: {updated} subjects\n'
            f'  Total: {len(subjects_data)} subjects'
        ))
