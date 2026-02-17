
import * as fs from 'fs';
import * as path from 'path';
import { ReductionClaim } from '../types/reduction';

/**
 * Registry for managing ReductionClaims.
 * Loads JSON definitions from data/reductions, validates them, and provides access.
 */
export class ReductionRegistry {
    private reductions: Map<string, ReductionClaim> = new Map();
    private initialized: boolean = false;
    private reductionsPayloadPath: string;

    constructor(reductionsPath?: string) {
        this.reductionsPayloadPath = reductionsPath || path.join(process.cwd(), 'data', 'reductions');
    }

    /**
     * Loads all ReductionClaims from the data directory.
     */
    public async loadAll(): Promise<void> {
        if (this.initialized) return;

        if (!fs.existsSync(this.reductionsPayloadPath)) {
            console.warn(`Reduction directory not found: ${this.reductionsPayloadPath}`);
            return;
        }

        const files = fs.readdirSync(this.reductionsPayloadPath).filter(f => f.endsWith('.json'));

        for (const file of files) {
            const filePath = path.join(this.reductionsPayloadPath, file);
            try {
                const content = fs.readFileSync(filePath, 'utf-8');
                const reduction = JSON.parse(content) as ReductionClaim;

                if (this.validateReduction(reduction)) {
                    this.reductions.set(reduction.claim_id, reduction);
                } else {
                    console.warn(`Skipping invalid reduction claim: ${file}`);
                }
            } catch (error) {
                console.error(`Error loading reduction claim ${file}:`, error);
            }
        }

        this.initialized = true;
        console.log(`Loaded ${this.reductions.size} reduction claims.`);
    }

    /**
     * Validates a ReductionClaim against the schema requirements.
     * @param reduction The reduction claim to validate
     */
    private validateReduction(reduction: ReductionClaim): boolean {
        if (!reduction.claim_id) {
            console.error("Reduction missing claim_id");
            return false;
        }

        if (!reduction.tier2_theory || !reduction.tier2_construct) {
            console.error(`Reduction ${reduction.claim_id} missing theory/construct identifiers`);
            return false;
        }

        // Ensure required arrays exist
        if (!reduction.reduction_edges || !Array.isArray(reduction.reduction_edges)) {
            console.error(`Reduction ${reduction.claim_id} missing reduction_edges array`);
            return false;
        }

        return true;
    }

    /**
     * Retrieves a reduction claim by ID.
     * @param id The reduction ID (e.g., 'RC_ART_SOFT_FASCINATION_002')
     */
    public getReduction(id: string): ReductionClaim | undefined {
        return this.reductions.get(id);
    }

    /**
     * Returns all loaded reduction claims.
     */
    public getAllReductions(): ReductionClaim[] {
        return Array.from(this.reductions.values());
    }
}
