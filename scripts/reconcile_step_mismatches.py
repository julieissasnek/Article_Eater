import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

class CeilingDecisionReconciler:
    """Reconcile ceiling decisions with template mechanism chains using content matching."""
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.data_dir = os.path.join(repo_path, 'data')
        self.templates_dir = os.path.join(self.data_dir, 'templates')
        self.decisions_file = os.path.join(self.data_dir, 'ceiling_decisions.json')
        self.mapping_file = os.path.join(self.data_dir, 'ceiling_decisions_template_mapping.json')
        
        self.decisions = None
        self.mapping = None
        self.templates_cache = {}
        self.reconciliation_results = {
            'resolved_by_content_match': [],
            'unresolvable': [],
            'already_exact': [],
            'summary': {
                'total_unapplied': 0,
                'resolved': 0,
                'unresolvable': 0
            }
        }
    
    def load_data(self):
        """Load decisions and mapping."""
        with open(self.decisions_file, 'r') as f:
            data = json.load(f)
        self.decisions = data['decisions']
        
        with open(self.mapping_file, 'r') as f:
            self.mapping = json.load(f)
    
    def load_template(self, filename: str) -> Optional[Dict]:
        """Load a template file from cache or disk."""
        if filename in self.templates_cache:
            return self.templates_cache[filename]
        
        fpath = os.path.join(self.templates_dir, filename)
        if os.path.exists(fpath):
            with open(fpath, 'r') as f:
                tmpl = json.load(f)
            self.templates_cache[filename] = tmpl
            return tmpl
        return None
    
    def get_mapping_for_template(self, template_id: str) -> Optional[Dict]:
        """Get mapping entry for a template ID."""
        return next(
            (m for m in self.mapping['template_mappings'] if m['template_id'] == template_id),
            None
        )
    
    def match_decision_to_step(self, decision: Dict, step: Dict) -> float:
        """
        Score how well a decision matches a step.
        Uses warrant type, confidence, and description similarity.
        """
        score = 0.0
        weights_sum = 0.0
        
        # 1. Warrant type match (weight: 0.4)
        decision_warrant = decision.get('current_warrant')
        step_justification = step.get('justification', {})
        step_desc = (step.get('description', '') or '') + (step.get('step_name', '') or '')
        
        if decision_warrant and decision_warrant in step_desc:
            score += 0.4
        elif decision_warrant in ['MECHANISM', 'EMPIRICAL_ASSOCIATION']:
            # Loosely match if mechanism or covariance keywords appear
            if any(kw in step_desc.lower() for kw in ['mechanism', 'covariance', 'pathway', 'evidence']):
                score += 0.3
        weights_sum += 0.4
        
        # 2. Confidence proximity (weight: 0.3)
        decision_conf = decision.get('confidence')
        step_conf = step.get('confidence')
        if decision_conf and step_conf:
            conf_diff = abs(decision_conf - step_conf)
            if conf_diff < 0.1:
                score += 0.3
            elif conf_diff < 0.2:
                score += 0.15
        weights_sum += 0.3
        
        # 3. Keyword matching from rationale (weight: 0.3)
        decision_rationale = (decision.get('rationale') or '').lower()
        key_terms = ['replicability', 'biological plausibility', 'multiple pathways', 'well-supported', 'consistent']
        
        matches = sum(1 for term in key_terms if term in decision_rationale)
        if matches > 0:
            score += (matches / len(key_terms)) * 0.3
        weights_sum += 0.3
        
        # Normalize if weights_sum > 0
        if weights_sum > 0:
            score = score / weights_sum
        
        return score
    
    def find_content_match(self, decision: Dict, mechanism_chain: List[Dict]) -> Optional[Tuple[Dict, float]]:
        """
        Find best matching step in mechanism chain for a decision.
        Returns (step, score) or None if no good match.
        """
        best_match = None
        best_score = 0.0
        
        for step in mechanism_chain:
            score = self.match_decision_to_step(decision, step)
            if score > best_score:
                best_score = score
                best_match = step
        
        # Only return if score is above threshold
        if best_score > 0.3:  # Threshold for considering a match
            return (best_match, best_score)
        
        return None
    
    def apply_decision_to_step(self, step: Dict, decision: Dict) -> Dict:
        """Apply a ceiling decision to a step."""
        modified = step.copy()
        
        # Add ceiling override
        modified['ceiling_override_rationale'] = decision.get('rationale')
        modified['ceiling_override_confidence'] = decision.get('confidence')
        modified['ceiling_override_ceiling'] = decision.get('ceiling')
        modified['ceiling_override_delta'] = decision.get('delta')
        modified['ceiling_override_decision'] = decision.get('decision')
        
        # If warrant upgrade is requested
        if decision.get('new_warrant'):
            modified['warrant_type_upgrade'] = decision.get('new_warrant')
        
        return modified
    
    def reconcile(self):
        """Main reconciliation process."""
        self.load_data()
        
        # Group decisions by template_id
        decisions_by_template = {}
        for dec in self.decisions:
            template_id = dec.get('template_id')
            if template_id not in decisions_by_template:
                decisions_by_template[template_id] = []
            decisions_by_template[template_id].append(dec)
        
        print(f"\nReconciling {len(decisions_by_template)} template groups...")
        print(f"Total decisions: {len(self.decisions)}\n")
        
        unapplied_count = 0
        resolved_count = 0
        unresolvable_count = 0
        
        for template_id, template_decisions in sorted(decisions_by_template.items()):
            mapping_entry = self.get_mapping_for_template(template_id)
            if not mapping_entry:
                print(f"  [SKIP] {template_id}: No mapping entry")
                continue
            
            print(f"\n  Template: {template_id}")
            print(f"    Decisions: {len(template_decisions)}")
            
            # Try each resolved file
            for resolved_file in mapping_entry['resolved_files']:
                template = self.load_template(resolved_file)
                if not template:
                    print(f"    [WARN] Could not load {resolved_file}")
                    continue
                
                mechanism_chain = template.get('mechanism_chain', [])
                step_nums = [s.get('step_number') for s in mechanism_chain]
                
                for decision in template_decisions:
                    step_num = decision.get('step')
                    
                    # First check for exact match
                    exact_step = next(
                        (s for s in mechanism_chain if s.get('step_number') == step_num),
                        None
                    )
                    
                    if exact_step:
                        # Exact match found
                        self.reconciliation_results['already_exact'].append({
                            'template_id': template_id,
                            'step': step_num,
                            'template_file': resolved_file,
                            'confidence': decision.get('confidence'),
                            'warrant': decision.get('current_warrant')
                        })
                        resolved_count += 1
                    else:
                        # Try content matching (only if mechanism chain is not empty)
                        if mechanism_chain:
                            match = self.find_content_match(decision, mechanism_chain)
                            if match:
                                matched_step, score = match
                                matched_step_num = matched_step.get('step_number')
                                self.reconciliation_results['resolved_by_content_match'].append({
                                    'template_id': template_id,
                                    'requested_step': step_num,
                                    'matched_step': matched_step_num,
                                    'match_score': round(score, 3),
                                    'template_file': resolved_file,
                                    'confidence': decision.get('confidence'),
                                    'warrant': decision.get('current_warrant'),
                                    'matched_step_name': matched_step.get('step_name'),
                                    'decision_rationale': decision.get('rationale')
                                })
                                resolved_count += 1
                            else:
                                # Unresolvable
                                self.reconciliation_results['unresolvable'].append({
                                    'template_id': template_id,
                                    'step': step_num,
                                    'template_file': resolved_file,
                                    'confidence': decision.get('confidence'),
                                    'warrant': decision.get('current_warrant'),
                                    'rationale': decision.get('rationale'),
                                    'template_steps_available': step_nums,
                                    'reason': 'No content match found in mechanism chain'
                                })
                                unresolvable_count += 1
                                unapplied_count += 1
                        else:
                            # Empty chain
                            self.reconciliation_results['unresolvable'].append({
                                'template_id': template_id,
                                'step': step_num,
                                'template_file': resolved_file,
                                'confidence': decision.get('confidence'),
                                'warrant': decision.get('current_warrant'),
                                'rationale': decision.get('rationale'),
                                'template_steps_available': [],
                                'reason': 'Template has no mechanism chain'
                            })
                            unresolvable_count += 1
                            unapplied_count += 1
        
        # Update summary
        self.reconciliation_results['summary'] = {
            'total_decisions': len(self.decisions),
            'unapplied_count': unapplied_count,
            'resolved_by_content_match': len(self.reconciliation_results['resolved_by_content_match']),
            'already_exact': len(self.reconciliation_results['already_exact']),
            'total_resolved': resolved_count,
            'unresolvable': len(self.reconciliation_results['unresolvable'])
        }
        
        return self.reconciliation_results
    
    def save_results(self, output_file: str):
        """Save reconciliation results to a JSON file."""
        with open(output_file, 'w') as f:
            json.dump(self.reconciliation_results, f, indent=2)
        print(f"\nResults saved to {output_file}")

# Main execution
if __name__ == '__main__':
    repo_path = '/sessions/practical-zen-darwin/mnt/REPOS/Article_Eater_PostQuinean_v1'
    
    reconciler = CeilingDecisionReconciler(repo_path)
    results = reconciler.reconcile()
    
    # Save results
    output_file = os.path.join(repo_path, 'scripts', 'reconciliation_results.json')
    reconciler.save_results(output_file)
    
    # Print summary
    print("\n" + "="*70)
    print("RECONCILIATION SUMMARY")
    print("="*70)
    summary = results['summary']
    print(f"Total decisions: {summary['total_decisions']}")
    print(f"Resolved by content matching: {summary['resolved_by_content_match']}")
    print(f"Already had exact matches: {summary['already_exact']}")
    print(f"Total resolved: {summary['total_resolved']}")
    print(f"Unresolvable: {summary['unresolvable']}")
    print(f"Unapplied (no match found): {summary['unapplied_count']}")
    
    if results['unresolvable']:
        print(f"\nUNRESO LVABLE DECISIONS ({len(results['unresolvable'])} total):")
        for i, unres in enumerate(results['unresolvable'][:15]):
            print(f"\n  [{i+1}] Template: {unres['template_id']}")
            print(f"      Step: {unres['step']}")
            print(f"      Warrant: {unres['warrant']}")
            print(f"      Confidence: {unres['confidence']}")
            print(f"      Template file: {unres['template_file']}")
            print(f"      Available steps: {unres.get('template_steps_available', [])}")
            print(f"      Reason: {unres['reason']}")

