import re
import json

def construct_ie_dpt_templates(source_file):
    with open(source_file, 'r') as f:
        content = f.read()
    
    # Simple regex to split the text by "## T_IE_XXX"
    sections = re.split(r'## (T_IE_\d{3}):\s*(.*)', content)
    
    templates = []
    
    # sections[0] is the text before the first template
    for i in range(1, len(sections), 3):
        template_id = sections[i]
        template_name = sections[i+1].strip()
        body = sections[i+2]
        
        # Stop processing if we hit PART V
        if '# PART V' in body:
            body = body.split('# PART V')[0]
            
        template_data = {
            "template_id": template_id,
            "display_id": template_id,
            "template_name": template_name,
            "tier": "Tier 1",
            "theory_keys": ["IE_DPT"],
            "constructs": []
        }
        
        # Extract Antecedent conditions
        antecedent_match = re.search(r'\*\*Antecedent conditions\*\*:(.*?)\n\n', body, re.DOTALL)
        if antecedent_match:
            template_data["antecedent_conditions"] = antecedent_match.group(1).strip()
            
        # Extract Predicted outcome
        outcome_match = re.search(r'\*\*Predicted outcome\*\*:(.*?)\n\n\*\*', body, re.DOTALL)
        if outcome_match:
            template_data["predicted_outcome"] = outcome_match.group(1).strip()
            
        # Extract Moderating variables
        mod_match = re.search(r'\*\*Moderating variables\*\*:(.*?)\n\n\*\*', body, re.DOTALL)
        if mod_match:
            template_data["moderating_variables"] = mod_match.group(1).strip()
            
        # Extract Expected effect sizes
        effect_match = re.search(r'\*\*Expected effect sizes\*\*:(.*?)\n\n\*\*', body, re.DOTALL)
        if effect_match:
            template_data["expected_effect_sizes"] = effect_match.group(1).strip()

        # Try to extract the architectural/neural content (varies by template)
        neural_match = re.search(r'\*\*Neural signature\*\*: *(.*?)\n', body)
        if neural_match:
            template_data["neural_signature"] = neural_match.group(1).strip()
            
        arch_test_match = re.search(r'\*\*Architectural test case\*\*: *(.*?)\n', body)
        if arch_test_match:
            template_data["architectural_test_case"] = arch_test_match.group(1).strip()
            
        arch_cons_match = re.search(r'\*\*Architectural consequence\*\*: *(.*?)\n', body)
        if arch_cons_match:
            template_data["architectural_consequence"] = arch_cons_match.group(1).strip()
            
        arch_imp_match = re.search(r'\*\*Architectural implication\*\*: *(.*?)\n', body)
        if arch_imp_match:
            template_data["architectural_consequence"] = arch_imp_match.group(1).strip()

        # Infer basic constructs from the text (very rudimentary)
        text_full = body.lower()
        if "complexity" in text_full: template_data["constructs"].append("Visual Complexity")
        if "expertise" in text_full: template_data["constructs"].append("Domain Expertise")
        if "aesthetic" in text_full: template_data["constructs"].append("Aesthetic Judgment")
        if "predict" in text_full: template_data["constructs"].append("Prediction Error")
        if "memory" in text_full: template_data["constructs"].append("Working Memory")
        if "stress" in text_full or "anxiety" in text_full: template_data["constructs"].append("Stress/Anxiety")
        if "attention" in text_full: template_data["constructs"].append("Attention")
        
        # Deduplicate constructs
        template_data["constructs"] = list(set(template_data["constructs"]))

        # Check for potential overlaps with existing templates
        overlap_notes = []
        if template_id == "T_IE_001":
            overlap_notes.append("Overlaps significantly with Berlyne's Complexity Goldilocks (Template 2: PP_COMPLEXITY_GOLDILOCKS_002). Ensure distinction is clear (IE sets the activity frame that *shifts* the Berlyne optimum).")
        if template_id == "T_IE_003":
            overlap_notes.append("Overlaps with Placebo Architecture (T_IE_006) and cognitive override mechanisms in Biophilia/Prospect-Refuge.")
        if template_id == "T_IE_005":
            overlap_notes.append("Relates to Expected Value of Control (EVC) processing. Check for overlap with Cognitive Control (Panel IV) templates.")
        if template_id == "T_IE_008":
            overlap_notes.append("Overlaps with PTSD/Stress Tier 1.5 reductions (e.g., STRESS_I panel outputs like Enclosure/Safety).")
        if template_id == "T_IE_010":
            overlap_notes.append("Strong overlap with Spatial Navigation (SN) Tier 1 features and Spatial Config (SC) Tier 2 templates (e.g., isovist legibility vs. mystery).")

        if overlap_notes:
            template_data["overlap_analysis"] = overlap_notes

        templates.append(template_data)
        
    return templates

if __name__ == "__main__":
    templates = construct_ie_dpt_templates('docs/IE_DPT_Full_T1_Specification.md')
    for t in templates:
        outfile = f"data/templates/{t['template_id']}.json"
        with open(outfile, 'w') as f:
            json.dump(t, f, indent=2)
        print(f"Wrote {outfile}")
    print(f"Total templates extracted: {len(templates)}")
