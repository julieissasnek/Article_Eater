
import { TheoryAPI } from '../src/api/index';

type ConvergentChannel = {
    name: string;
    template_link?: string;
};

type TemplateWithChannels = {
    convergent_channels?: ConvergentChannel[];
};

async function testMAT4() {
    console.log("Starting MAT4 Round-Trip Test...");

    const api = new TheoryAPI();
    await api.initialize();

    const mat4 = api.getTemplate('NATURAL_MATERIAL_CONVERGENCE_001');
    if (!mat4) {
        console.error("FAIL: MAT4 template not found.");
        process.exit(1);
    }

    console.log("PASS: MAT4 template loaded.");

    const channels = (mat4 as unknown as TemplateWithChannels).convergent_channels ?? [];

    // Validate Convergent Channels
    if (channels.length === 0) {
        console.error("FAIL: MAT4 missing convergent_channels.");
        process.exit(1);
    }

    const expectedChannels = [
        { name: 'visual_fractal', link: 'PP_SPECTRAL_MATCH_001' },
        { name: 'haptic_thermal', link: 'CT_AFFECTIVE_TOUCH_001' },
        { name: 'acoustic', link: 'BRECVEMA_ARCH_001' },
        { name: 'olfactory', link: undefined },
        { name: 'ecological', link: undefined }
    ];

    let channelErrors = 0;
    expectedChannels.forEach(expected => {
        const found = channels.find(c => c.name === expected.name);
        if (!found) {
            console.error(`FAIL: Missing channel '${expected.name}'`);
            channelErrors++;
        } else if (expected.link && found.template_link !== expected.link) {
            console.error(`FAIL: Channel '${expected.name}' linked to '${found.template_link}', expected '${expected.link}'`);
            channelErrors++;
        } else {
            console.log(`PASS: Channel '${expected.name}' verified.`);
        }
    });

    // Validate Cross-Reference Existence
    const linkedTemplates = ['PP_SPECTRAL_MATCH_001', 'CT_AFFECTIVE_TOUCH_001', 'BRECVEMA_ARCH_001'];
    let linkErrors = 0;
    linkedTemplates.forEach(tid => {
        if (!api.getTemplate(tid)) {
            console.error(`FAIL: Linked template '${tid}' not found in registry.`);
            linkErrors++;
        } else {
            console.log(`PASS: Linked template '${tid}' exists.`);
        }
    });

    if (channelErrors > 0 || linkErrors > 0) {
        console.error(`\nTest FAILED with ${channelErrors + linkErrors} errors.`);
        process.exit(1);
    }

    console.log("\nMAT4 Round-Trip Test PASSED.");
    process.exit(0);
}

testMAT4().catch(err => {
    console.error("Test crashed:", err);
    process.exit(1);
});
