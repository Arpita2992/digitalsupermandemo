// Debug test for cost optimization data

// Test the extractCostSavings function
function testCostSavings() {
    console.log('=== Testing Cost Savings Extraction ===');
    
    // Test cases
    const testCases = [
        { input: null, expected: 0 },
        { input: undefined, expected: 0 },
        { input: { estimated_savings: '€305-1175' }, expected: 740 },
        { input: { estimated_savings: '€1,200' }, expected: 1200 },
        { input: { estimated_savings: 500 }, expected: 500 },
        { input: { estimated_savings: 'N/A' }, expected: 0 },
        { input: {}, expected: 0 }
    ];
    
    testCases.forEach((testCase, index) => {
        const result = digitalSuperman.extractCostSavings(testCase.input);
        console.log(`Test ${index + 1}: Input=${JSON.stringify(testCase.input)}, Expected=${testCase.expected}, Got=${result}, Pass=${result === testCase.expected}`);
    });
}

// Test the processing summary structure
function testProcessingSummary() {
    console.log('=== Testing Processing Summary ===');
    
    // Simulate what we expect from backend
    const mockSummary = {
        components_found: 8,
        policy_compliance: {
            compliant: true,
            violations_count: 0,
            fixes_applied: 2
        },
        cost_optimization: {
            recommendations_count: 8,
            estimated_savings: 'N/A',
            framework_applied: 'Microsoft Well-Architected Framework'
        },
        code_generation: {
            files_generated: 11
        }
    };
    
    console.log('Mock summary:', mockSummary);
    digitalSuperman.updateResultsSummary(mockSummary);
}

// Auto-run tests when loaded
if (typeof digitalSuperman !== 'undefined') {
    setTimeout(() => {
        testCostSavings();
        testProcessingSummary();
    }, 1000);
}
