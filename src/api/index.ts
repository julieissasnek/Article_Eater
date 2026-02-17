
import { TemplateRegistry } from '../theory/templateRegistry';
import { ReductionRegistry } from '../theory/reductionRegistry';
import { CrossReferenceIndex } from '../theory/crossReference';
import { Template } from '../types/template';
import { ReductionClaim } from '../types/reduction';
import { AttributeDomain } from '../types/attribute';

/**
 * Unified API for accessing the Article Eater Theory Layer.
 * Manages TemplateRegistry, ReductionRegistry, and CrossReferenceIndex.
 */
export class TheoryAPI {
    private templateRegistry: TemplateRegistry;
    private reductionRegistry: ReductionRegistry;
    private crossReferenceIndex: CrossReferenceIndex;
    private initialized: boolean = false;

    constructor(
        templatePath?: string,
        reductionPath?: string,
        attributePath?: string
    ) {
        this.templateRegistry = new TemplateRegistry(templatePath);
        this.reductionRegistry = new ReductionRegistry(reductionPath);
        this.crossReferenceIndex = new CrossReferenceIndex(attributePath);
    }

    /**
     * Initializes all registries and indices.
     */
    public async initialize(): Promise<void> {
        if (this.initialized) return;

        await Promise.all([
            this.templateRegistry.loadAll(),
            this.reductionRegistry.loadAll(),
            this.crossReferenceIndex.loadAll()
        ]);

        this.initialized = true;
        console.log("TheoryAPI initialized.");
    }

    // --- Template Access ---

    public getTemplate(id: string): Template | undefined {
        return this.templateRegistry.getTemplate(id);
    }

    public getAllTemplates(): Template[] {
        return this.templateRegistry.getAllTemplates();
    }

    public getTemplatesByFramework(frameworkId: string): Template[] {
        return this.templateRegistry
            .getAllTemplates()
            .filter(t => Array.isArray(t.framework_ids) && t.framework_ids.includes(frameworkId));
    }

    public getTemplateByDisplayId(displayId: string): Template | undefined {
        return this.templateRegistry.getTemplateByDisplayId(displayId);
    }

    // --- Reduction Access ---

    public getReduction(id: string): ReductionClaim | undefined {
        return this.reductionRegistry.getReduction(id);
    }

    public getAllReductions(): ReductionClaim[] {
        return this.reductionRegistry.getAllReductions();
    }

    // --- Cross-Reference Access ---

    public getAttributeDomain(id: string): AttributeDomain | undefined {
        // We need to implement getDomain in CrossReferenceIndex or access map directly
        // Ideally CrossReferenceIndex should have a getDomain method. 
        // For now, let's look at the implementation of CrossReferenceIndex again.
        // It has getAllDomains(). We can find it there.
        return this.crossReferenceIndex.getAllDomains().find(d => d.domain_id === id);
    }

    public getAllAttributeDomains(): AttributeDomain[] {
        return this.crossReferenceIndex.getAllDomains();
    }

    /**
     * Returns templates relevant to a specific attribute domain.
     */
    public getTemplatesForAttributeDomain(domainId: string): Template[] {
        const templateIds = this.crossReferenceIndex.getTemplatesForDomain(domainId);
        return templateIds
            .map(id => this.getTemplate(id))
            .filter((t): t is Template => t !== undefined);
    }
}
