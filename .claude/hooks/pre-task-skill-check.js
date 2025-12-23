#!/usr/bin/env node
/**
 * Pre-Task Skill Check Hook
 * 
 * Validates that agents check for relevant skills before executing tasks.
 * This hook runs before tool execution to enforce skill-checking requirements.
 * 
 * Usage: Called automatically by hooks system before task execution
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Find repo root
function findRepoRoot() {
    let current = __dirname;
    for (let i = 0; i < 5; i++) {
        const agentsPath = path.join(current, 'AGENTS.md');
        if (fs.existsSync(agentsPath)) {
            return current;
        }
        current = path.dirname(current);
    }
    return path.dirname(__dirname);
}

// Extract available skills from AGENTS.md
function extractAvailableSkills(agentsPath) {
    if (!fs.existsSync(agentsPath)) {
        return [];
    }
    
    const content = fs.readFileSync(agentsPath, 'utf-8');
    const pattern = /<name>([^<]+)<\/name>/g;
    const skills = [];
    let match;
    
    while ((match = pattern.exec(content)) !== null) {
        const skillName = match[1].trim();
        if (skillName) {
            skills.push(skillName);
        }
    }
    
    return skills;
}

// Check if text contains evidence of skill checking
function checkSkillMention(text) {
    const textLower = text.toLowerCase();
    const skillCheckPatterns = [
        /openskills read/i,
        /I've read the .+ skill/i,
        /Using .+ skill/i,
        /Skill read:/i,
        /Reading:/i,
        /invoked.*skill/i,
        /checking.*skill/i,
        /relevant skill/i,
    ];
    
    return skillCheckPatterns.some(pattern => pattern.test(textLower));
}

// Validate skill check in conversation context
function validateSkillCheck(context) {
    const repoRoot = findRepoRoot();
    const agentsPath = path.join(repoRoot, 'AGENTS.md');
    const availableSkills = extractAvailableSkills(agentsPath);
    
    // Get the most recent user message and agent response
    const userMessage = context.userMessage || '';
    const agentResponse = context.agentResponse || '';
    const conversationHistory = context.conversationHistory || [];
    
    // Combine all text to check
    const allText = [
        userMessage,
        agentResponse,
        ...conversationHistory.map(msg => msg.content || '')
    ].join('\n').toLowerCase();
    
    // Check if skill check occurred
    const hasSkillCheck = checkSkillMention(allText);
    
    // Check for task triggers that should require skill checks
    const taskTriggers = [
        /implement/i,
        /create/i,
        /build/i,
        /add/i,
        /fix/i,
        /update/i,
        /modify/i,
        /write/i,
        /design/i,
        /plan/i,
        /debug/i,
        /test/i,
    ];
    
    const hasTaskTrigger = taskTriggers.some(trigger => trigger.test(userMessage));
    
    // If there's a task trigger but no skill check, it's a violation
    if (hasTaskTrigger && !hasSkillCheck) {
        return {
            continue: false,
            reason: 'Skill check required before task execution',
            warnings: [
                'Task detected but no evidence of skill check',
                'Please check for relevant skills using: openskills read <skill-name>',
                `Available skills: ${availableSkills.slice(0, 5).join(', ')}...`
            ],
            metadata: {
                hasTaskTrigger: true,
                hasSkillCheck: false,
                availableSkillsCount: availableSkills.length
            }
        };
    }
    
    return {
        continue: true,
        reason: 'Skill check validated',
        metadata: {
            hasTaskTrigger,
            hasSkillCheck,
            availableSkillsCount: availableSkills.length
        }
    };
}

// Main hook execution
function main() {
    try {
        // Get context from environment or stdin
        let context = {};
        
        // Try to get context from environment variables
        if (process.env.HOOK_CONTEXT) {
            try {
                context = JSON.parse(process.env.HOOK_CONTEXT);
            } catch (e) {
                console.error('Failed to parse HOOK_CONTEXT:', e.message);
            }
        }
        
        // Try to get from stdin if available
        if (process.stdin.isTTY === false) {
            let stdinData = '';
            process.stdin.on('data', (chunk) => {
                stdinData += chunk.toString();
            });
            process.stdin.on('end', () => {
                if (stdinData) {
                    try {
                        context = { ...context, ...JSON.parse(stdinData) };
                    } catch (e) {
                        // Not JSON, ignore
                    }
                }
                executeHook(context);
            });
            return;
        }
        
        // Execute immediately if no stdin
        executeHook(context);
    } catch (error) {
        console.error('Hook execution error:', error.message);
        // Fail open - allow execution if hook fails
        process.exit(0);
    }
}

function executeHook(context) {
    const result = validateSkillCheck(context);
    
    if (!result.continue) {
        console.error('❌ Skill check validation failed:');
        console.error(`   ${result.reason}`);
        if (result.warnings) {
            result.warnings.forEach(warning => {
                console.error(`   ⚠️  ${warning}`);
            });
        }
        process.exit(1);
    } else {
        if (process.env.DEBUG) {
            console.log('✓ Skill check validated');
            console.log(`   Metadata:`, JSON.stringify(result.metadata, null, 2));
        }
        process.exit(0);
    }
}

// Export for use as module
if (require.main === module) {
    main();
} else {
    module.exports = { validateSkillCheck, checkSkillMention };
}
