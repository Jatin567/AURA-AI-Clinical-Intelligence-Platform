from app.models.otc import OTCMedicine

OTC_ALLOWLIST: dict[str, OTCMedicine] = {
    "ibuprofen": OTCMedicine(
        name="Ibuprofen",
        common_names=["Advil", "Motrin"],
        # Age limit set conservatively to 12 for MVP. 
        # OTC ibuprofen is approved from 6 months with weight-appropriate dosing,
        # but pediatric dosing guidance is out of scope for this system.
        safe_for_ages_above=12,
        contraindicated_conditions=["Stomach ulcer", "Kidney disease", "Aspirin-sensitive asthma", "Heart disease", "Pregnancy"],
        contraindicated_medications=["Warfarin", "Lithium"],
        max_duration_days=10,
        standard_disclaimer="Do not exceed recommended dose. Take with food if stomach upset occurs."
    ),
    "acetaminophen": OTCMedicine(
        name="Acetaminophen",
        common_names=["Tylenol", "Paracetamol"],
        safe_for_ages_above=0,
        contraindicated_conditions=["Liver disease"],
        contraindicated_medications=["Other products containing acetaminophen"],
        max_duration_days=10,
        standard_disclaimer="Liver warning: This product contains acetaminophen. Severe liver damage may occur if you take more than 4,000 mg in 24 hours."
    ),
    "paracetamol": OTCMedicine(
        name="Acetaminophen",
        common_names=["Tylenol", "Paracetamol"],
        safe_for_ages_above=0,
        contraindicated_conditions=["Liver disease"],
        contraindicated_medications=["Other products containing acetaminophen"],
        max_duration_days=10,
        standard_disclaimer="Liver warning: This product contains acetaminophen. Severe liver damage may occur if you take more than 4,000 mg in 24 hours."
    ),
    "loratadine": OTCMedicine(
        name="Loratadine",
        common_names=["Claritin"],
        safe_for_ages_above=2,
        contraindicated_conditions=["Severe liver disease"],
        contraindicated_medications=[],
        max_duration_days=30,
        standard_disclaimer="May cause drowsiness in some individuals, though usually non-drowsy."
    ),
    "cetirizine": OTCMedicine(
        name="Cetirizine",
        common_names=["Zyrtec"],
        safe_for_ages_above=2,
        contraindicated_conditions=["Kidney disease"],
        contraindicated_medications=[],
        max_duration_days=30,
        standard_disclaimer="May cause drowsiness. Use caution when driving or operating machinery."
    ),
    "diphenhydramine": OTCMedicine(
        name="Diphenhydramine",
        common_names=["Benadryl"],
        # Heightened requirement for conservative triage: limit use to 12+ for self-treatment.
        safe_for_ages_above=12,
        contraindicated_conditions=["Glaucoma", "Prostate enlargement"],
        contraindicated_medications=["Other sedatives"],
        max_duration_days=7,
        standard_disclaimer="Causes significant drowsiness. Avoid alcohol while taking."
    ),
    "omeprazole": OTCMedicine(
        name="Omeprazole",
        common_names=["Prilosec"],
        safe_for_ages_above=18,
        contraindicated_conditions=["Low magnesium levels"],
        contraindicated_medications=["Clopidogrel"],
        max_duration_days=14,
        standard_disclaimer="Use as directed for frequent heartburn (2 or more days a week)."
    ),
    "antacid": OTCMedicine(
        name="Antacid",
        common_names=["Tums", "Rolaids"],
        safe_for_ages_above=12,
        contraindicated_conditions=["Kidney stones", "High calcium levels"],
        contraindicated_medications=["Tetracyclines", "Fluoroquinolones"],
        max_duration_days=14,
        standard_disclaimer="Ask a doctor before use if you are taking prescription drugs."
    ),
    "saline nasal spray": OTCMedicine(
        name="Saline Nasal Spray",
        common_names=["Ocean", "Ayr"],
        safe_for_ages_above=0,
        contraindicated_conditions=[],
        contraindicated_medications=[],
        max_duration_days=365,
        standard_disclaimer="Simple saline solution for symptomatic relief of nasal dryness."
    ),
    "hydrocortisone cream": OTCMedicine(
        name="Hydrocortisone Cream",
        common_names=["Cortizone-10"],
        safe_for_ages_above=2,
        contraindicated_conditions=["Skin infections", "Open wounds"],
        contraindicated_medications=[],
        max_duration_days=7,
        standard_disclaimer="For external use only. Avoid contact with eyes."
    ),
}
