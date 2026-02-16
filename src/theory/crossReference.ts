
import * as fs from 'fs';
import * as path from 'path';
import { AttributeDomain } from '../types/attribute';

/**
 * CrossReferenceIndex (Mechanism Index)
 * Maps Attribute Domains and specific Attributes to Mechanistic Templates.
 */
export class CrossReferenceIndex {
    private domains: Map<string, AttributeDomain> = new Map();
    private initialized: boolean = false;
    private attributesPath: string;

    constructor(attributesPath?: string) {
        this.attributesPath = attributesPath || path.join(process.cwd(), 'data', 'attributes');
    }

    /**
     * Loads all Attribute Domains from the data directory.
     */
    public async loadAll(): Promise<void> {
        if (this.initialized) return;

        if (!fs.existsSync(this.attributesPath)) {
            console.warn(`Attribute directory not found: ${this.attributesPath}`);
            return;
        }

        const files = fs.readdirSync(this.attributesPath).filter(f => f.endsWith('.json'));

        for (const file of files) {
            const filePath = path.join(this.attributesPath, file);
            try {
                const content = fs.readFileSync(filePath, 'utf-8');
                const domain = JSON.parse(content) as AttributeDomain;
                this.domains.set(domain.domain_id, domain);
            } catch (error) {
                console.error(`Error loading attribute domain ${file}:`, error);
            }
        }

        this.initialized = true;
        console.log(`Loaded ${this.domains.size} attribute domains.`);
    }

    /**
     * Returns all loaded Attribute Domains.
     */
    public getAllDomains(): AttributeDomain[] {
        return Array.from(this.domains.values());
    }

    /**
     * Returns the templates mapped to a specific Attribute Domain.
     */
    public getTemplatesForDomain(domainId: string): string[] {
        const domain = this.domains.get(domainId);
        // Map back to string[] to maintain backward compatibility for now, 
        // or update return type to TemplateMapping[].
        // Given upstream api.ts expects DomainTemplateMapping which extends TemplateMapping,
        // we should probably expose the full objects.
        // But this method signature is string[]. Let's keep it string[] for this specific method
        // if it's used by legacy code, or update it.
        // The error log didn't mention this file failing on return type, but on import.
        // However, if I changed AttributeDomain, this access will be valid (returning object[]),
        // but the return type annotation string[] will cause a compile error.
        return domain ? domain.mapped_templates.map(m => m.template_id) : [];
    }

    /**
     * Returns the full template mappings for a domain.
     */
    public getTemplateMappingsForDomain(domainId: string): import('../types/attribute').TemplateMapping[] {
        const domain = this.domains.get(domainId);
        return domain ? domain.mapped_templates : [];
    }

    /**
     * Returns the templates mapped to a specific Attribute ID across all domains.
     * Note: Currently the JSONs map templates at the Domain level, but future
     * iterations could map at the Attribute level.
     */
    // public getTemplatesForAttribute(attributeId: string): string[] { ... }
}
