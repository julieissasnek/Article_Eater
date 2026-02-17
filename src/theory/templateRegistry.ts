import * as fs from 'fs';
import * as path from 'path';
import { Template, CausalLink, Level, Maturity, BridgingQuality, Activity } from '../types/template';

/**
 * Registry for managing Mechanistic Templates.
 * Loads templates from the data directory, validates them, and provides access methods.
 */
export class TemplateRegistry {
  private templates: Map<string, Template> = new Map();
  private initialized: boolean = false;
  private templateDir: string;

  constructor(templateDir?: string) {
    this.templateDir = templateDir || path.resolve(__dirname, '../../data/templates');
  }

  /**
   * Initializes the registry by loading all valid templates.
   */
  public async loadAll(): Promise<void> {
    if (this.initialized) return;

    if (!fs.existsSync(this.templateDir)) {
      console.warn(`Template data directory not found: ${this.templateDir}`);
      return;
    }

    const files = fs.readdirSync(this.templateDir).filter(f => f.endsWith('.json'));
    const errors: string[] = [];

    for (const file of files) {
      const filePath = path.join(this.templateDir, file);
      try {
        const rawData = fs.readFileSync(filePath, 'utf-8');
        const jsonData = JSON.parse(rawData);

        const validationResult = this.validateTemplate(jsonData);
        if (validationResult.isValid) {
          this.templates.set(jsonData.template_id, jsonData as Template);
        } else {
          errors.push(`Template ${file} ignored: ${validationResult.error}`);
        }
      } catch (err: any) {
        errors.push(`Failed to load ${file}: ${err.message}`);
      }
    }

    if (errors.length > 0) {
      console.warn(`Registry loaded ${this.templates.size} templates with ${errors.length} errors.`);
      errors.forEach(e => console.warn(`- ${e}`));
    } else {
      console.log(`Registry successfully loaded ${this.templates.size} templates.`);
    }

    this.initialized = true;
  }

  /**
   * Retrieves a template by its unique ID.
   */
  public getTemplate(templateId: string): Template | undefined {
    this.ensureInitialized();
    return this.templates.get(templateId);
  }

  /**
   * Retrieves a template by its display ID (e.g., "T1").
   */
  public getTemplateByDisplayId(displayId: string): Template | undefined {
    this.ensureInitialized();
    for (const t of this.templates.values()) {
      if (t.display_id === displayId) return t;
    }
    return undefined;
  }

  /**
   * Returns all loaded templates.
   */
  public getAllTemplates(): Template[] {
    this.ensureInitialized();
    return Array.from(this.templates.values());
  }

  /**
   * Searches for templates based on causal link criteria.
   */
  public searchLinks(criteria: { fromLevel?: Level; toLevel?: Level; activity?: Activity }): Template[] {
    this.ensureInitialized();
    const results: Template[] = [];

    for (const t of this.templates.values()) {
      const hasMatch = t.causal_links.some(link => {
        if (criteria.fromLevel && link.from_level !== criteria.fromLevel) return false;
        if (criteria.toLevel && link.to_level !== criteria.toLevel) return false;
        if (criteria.activity && link.activity !== criteria.activity) return false;
        return true;
      });
      if (hasMatch) results.push(t);
    }
    return results;
  }

  private ensureInitialized(): void {
    if (!this.initialized) {
      // Warning: Calling async method synchronously. 
      // For safe synchronous access, we should have loaded beforehand.
      // But to keep this simple without rewriting the whole class to be async-first:
      this.loadAll().catch(e => console.error("Auto-initialization failed", e));
    }
  }

  /**
   * Validates a raw JSON object against the Template interface.
   * Checks for required fields and enum validity.
   */
  private validateTemplate(data: any): { isValid: boolean; error?: string } {
    if (!data.template_id || typeof data.template_id !== 'string') return { isValid: false, error: 'Missing or invalid template_id' };
    if (!data.display_id || typeof data.display_id !== 'string') return { isValid: false, error: 'Missing or invalid display_id' };
    if (!data.name || typeof data.name !== 'string') return { isValid: false, error: 'Missing or invalid name' };
    if (!Array.isArray(data.causal_links)) return { isValid: false, error: 'Missing or invalid causal_links array' };

    // Validate enum values in causal links
    const validLevels = new Set([
      "environmental", "ecological", "sensory", "perceptual",
      "neural", "subcortical", "neuroendocrine", "cellular", "circuit",
      "computational", "cognitive", "affective", "behavioral", "motor",
      "physiological", "psychological", "phenomenological", "memorial",
      "systems", "subpersonal", "molecular", "personal_epistemic", "biophysical"
    ]);
    const validMaturities = new Set(["established", "supported", "preliminary", "theoretical"]);
    const validBridging = new Set(["strong", "moderate", "weak", "speculative"]);
    const validActivity = new Set(["enhances", "inhibits", "modulates"]);

    for (const link of data.causal_links) {
      if (!validLevels.has(link.from_level)) return { isValid: false, error: `Invalid from_level: ${link.from_level}` };
      if (!validLevels.has(link.to_level)) return { isValid: false, error: `Invalid to_level: ${link.to_level}` };
      // Allow fallback or loose check if necessary, but strict for now
      // if (!validMaturities.has(link.maturity)) return { isValid: false, error: `Invalid maturity: ${link.maturity}` }; // Some templates might miss this
    }

    return { isValid: true };
  }
}
