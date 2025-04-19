/**
 * Prize documentation for the China Growth Game.
 * 
 * This module provides documentation and tooltips for the prize system
 * in the game UI.
 */

// Prize documentation data
const prizeDocumentation = {
    // GDP Growth Achievement Prize
    gdp_growth: {
        name: "GDP Growth Achievement",
        description: "Awarded to teams that achieve exceptional GDP growth over a sustained period.",
        criteria: "Maintain GDP growth rate above 8% for at least 3 consecutive rounds.",
        effects: {
            tfp_increase: {
                value: "5%",
                description: "Increases Total Factor Productivity (TFP) by 5%, representing improved production efficiency."
            },
            exports_multiplier: {
                value: "1.1x",
                description: "Increases exports by 10%, representing improved international competitiveness."
            }
        },
        strategy_tips: [
            "Focus on capital accumulation in early rounds to boost production capacity.",
            "Invest in human capital to improve labor productivity.",
            "Maintain a high savings rate to support investment."
        ],
        historical_context: "China maintained double-digit GDP growth rates through much of the 1990s and 2000s, becoming known as the 'factory of the world'."
    },
    
    // Technology Leadership Prize
    tech_leadership: {
        name: "Technology Leadership",
        description: "Awarded to teams that achieve technological breakthroughs through R&D investment.",
        criteria: "Invest at least 2.5% of GDP in R&D for 3 consecutive rounds.",
        effects: {
            tfp_increase: {
                value: "8%",
                description: "Increases Total Factor Productivity (TFP) by 8%, representing technological innovation."
            },
            tech_breakthrough_probability: {
                value: "+20%",
                description: "Increases the probability of technology breakthrough events by 20%."
            }
        },
        strategy_tips: [
            "Allocate a consistent portion of your budget to R&D investment.",
            "Balance R&D with other investments to maintain overall growth.",
            "Technology leadership compounds over time, providing long-term benefits."
        ],
        historical_context: "China's transition from 'Made in China' to 'Created in China' has been supported by massive increases in R&D spending, now second only to the United States globally."
    },
    
    // Sustainable Growth Prize
    sustainable_growth: {
        name: "Sustainable Growth",
        description: "Awarded to teams that maintain balanced and sustainable economic growth.",
        criteria: "Maintain positive GDP growth for 5 consecutive rounds with low volatility (standard deviation < 2%).",
        effects: {
            gdp_growth_stability: {
                value: "+30%",
                description: "Reduces the negative impact of economic recession events by 30%."
            },
            foreign_investment_multiplier: {
                value: "1.15x",
                description: "Increases foreign direct investment by 15%, representing increased investor confidence."
            }
        },
        strategy_tips: [
            "Avoid extreme policy changes that could lead to boom-bust cycles.",
            "Diversify your economy to reduce vulnerability to shocks.",
            "Build reserves during good times to weather downturns."
        ],
        historical_context: "China's economic planners have emphasized stable growth ('稳定增长') as a key policy objective, especially since the 2010s."
    },
    
    // Crisis Management Prize
    crisis_management: {
        name: "Crisis Management",
        description: "Awarded to teams that effectively navigate economic crises.",
        criteria: "Recover to pre-crisis GDP levels within 2 rounds after a major economic shock.",
        effects: {
            recession_recovery_boost: {
                value: "+25%",
                description: "Increases recovery speed from future recessions by 25%."
            },
            capital_protection: {
                value: "+20%",
                description: "Reduces capital damage from natural disasters by 20%."
            }
        },
        strategy_tips: [
            "Maintain flexibility in your economic policies to respond to crises.",
            "Build infrastructure that can withstand shocks.",
            "Develop counter-cyclical policy tools to deploy during downturns."
        ],
        historical_context: "China's response to the 2008 global financial crisis included a massive stimulus package that helped maintain growth while other economies contracted."
    },
    
    // Export Champion Prize
    export_champion: {
        name: "Export Champion",
        description: "Awarded to teams that achieve exceptional export growth.",
        criteria: "Maintain export growth above 10% for 3 consecutive rounds and achieve exports > 30% of GDP.",
        effects: {
            foreign_income_multiplier: {
                value: "1.2x",
                description: "Increases income from foreign markets by 20%."
            },
            exchange_rate_advantage: {
                value: "+15%",
                description: "Improves the effectiveness of exchange rate policies by 15%."
            }
        },
        strategy_tips: [
            "Invest in export-oriented industries and infrastructure.",
            "Consider exchange rate policies that support export competitiveness.",
            "Develop trade relationships through strategic policies."
        ],
        historical_context: "China's export-led growth strategy transformed it into the world's largest exporter, with exports reaching over 30% of GDP at their peak."
    }
};

/**
 * Initialize prize documentation tooltips in the UI.
 */
function initializePrizeDocumentation() {
    // Add tooltips to prize elements
    document.querySelectorAll('[data-prize-type]').forEach(element => {
        const prizeType = element.getAttribute('data-prize-type');
        if (prizeDocumentation[prizeType]) {
            const prizeData = prizeDocumentation[prizeType];
            
            // Create tooltip content
            const tooltipContent = `
                <div class="prize-tooltip">
                    <h3>${prizeData.name}</h3>
                    <p><strong>Description:</strong> ${prizeData.description}</p>
                    <p><strong>Criteria:</strong> ${prizeData.criteria}</p>
                    <div class="prize-effects">
                        <h4>Effects:</h4>
                        <ul>
                            ${Object.entries(prizeData.effects).map(([key, effect]) => `
                                <li>
                                    <strong>${key.replace(/_/g, ' ')}:</strong> ${effect.value}
                                    <span class="effect-description">${effect.description}</span>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                    <div class="prize-tips">
                        <h4>Strategy Tips:</h4>
                        <ul>
                            ${prizeData.strategy_tips.map(tip => `<li>${tip}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="historical-context">
                        <h4>Historical Context:</h4>
                        <p>${prizeData.historical_context}</p>
                    </div>
                </div>
            `;
            
            // Initialize tooltip
            new Tooltip(element, {
                title: tooltipContent,
                html: true,
                placement: 'auto',
                trigger: 'hover focus',
                container: 'body'
            });
        }
    });
}

/**
 * Display a notification when a prize is awarded.
 * 
 * @param {string} prizeType - The type of prize awarded.
 * @param {string} teamName - The name of the team that was awarded the prize.
 */
function displayPrizeNotification(prizeType, teamName) {
    if (prizeDocumentation[prizeType]) {
        const prizeData = prizeDocumentation[prizeType];
        
        // Create notification content
        const notificationContent = `
            <div class="prize-notification">
                <h3>${prizeData.name} Awarded!</h3>
                <p>Congratulations! Your team "${teamName}" has been awarded the ${prizeData.name} prize.</p>
                <p>${prizeData.description}</p>
                <div class="prize-effects">
                    <h4>Effects:</h4>
                    <ul>
                        ${Object.entries(prizeData.effects).map(([key, effect]) => `
                            <li>
                                <strong>${key.replace(/_/g, ' ')}:</strong> ${effect.value}
                                <span class="effect-description">${effect.description}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            </div>
        `;
        
        // Display notification
        showNotification(notificationContent, 'success', 10000); // 10 seconds duration
    }
}

/**
 * Create and display the prizes help modal.
 */
function showPrizesHelpModal() {
    // Create modal content
    let modalContent = `
        <div class="prizes-help-modal">
            <h2>China Growth Game: Prize System</h2>
            <p class="lead">The prize system rewards teams for achieving specific economic milestones and implementing successful policies.</p>
            
            <div class="prize-categories">
    `;
    
    // Add each prize category
    Object.entries(prizeDocumentation).forEach(([prizeType, prizeData]) => {
        modalContent += `
            <div class="prize-category">
                <h3>${prizeData.name}</h3>
                <p><strong>Description:</strong> ${prizeData.description}</p>
                <p><strong>Criteria:</strong> ${prizeData.criteria}</p>
                <div class="prize-effects">
                    <h4>Effects:</h4>
                    <ul>
                        ${Object.entries(prizeData.effects).map(([key, effect]) => `
                            <li>
                                <strong>${key.replace(/_/g, ' ')}:</strong> ${effect.value}
                                <span class="effect-description">${effect.description}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
                <div class="prize-tips">
                    <h4>Strategy Tips:</h4>
                    <ul>
                        ${prizeData.strategy_tips.map(tip => `<li>${tip}</li>`).join('')}
                    </ul>
                </div>
                <div class="historical-context">
                    <h4>Historical Context:</h4>
                    <p>${prizeData.historical_context}</p>
                </div>
            </div>
        `;
    });
    
    modalContent += `
            </div>
            
            <div class="prizes-help-footer">
                <h3>General Prize Information</h3>
                <ul>
                    <li>Prizes are evaluated at the end of each round.</li>
                    <li>Multiple prizes can be awarded to the same team.</li>
                    <li>Prize effects are permanent and cumulative.</li>
                    <li>Prizes provide both immediate benefits and long-term advantages.</li>
                    <li>Some prizes make your economy more resilient to negative events.</li>
                </ul>
            </div>
        </div>
    `;
    
    // Display modal
    showModal('Prize System Documentation', modalContent);
}

/**
 * Show a modal with the given title and content.
 * 
 * @param {string} title - The modal title.
 * @param {string} content - The HTML content for the modal body.
 */
function showModal(title, content) {
    // Create modal element if it doesn't exist
    let modal = document.getElementById('prizesHelpModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'prizesHelpModal';
        modal.className = 'modal fade';
        modal.setAttribute('tabindex', '-1');
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-labelledby', 'prizesHelpModalLabel');
        modal.setAttribute('aria-hidden', 'true');
        
        modal.innerHTML = `
            <div class="modal-dialog modal-lg" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="prizesHelpModalLabel">${title}</h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        ${content}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    } else {
        // Update existing modal
        modal.querySelector('.modal-title').textContent = title;
        modal.querySelector('.modal-body').innerHTML = content;
    }
    
    // Show the modal
    $(modal).modal('show');
}

/**
 * Show a notification with the given content.
 * 
 * @param {string} content - The HTML content for the notification.
 * @param {string} type - The notification type (success, info, warning, error).
 * @param {number} duration - The duration in milliseconds to show the notification.
 */
function showNotification(content, type, duration) {
    // Create notification container if it doesn't exist
    let container = document.getElementById('notificationContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notificationContainer';
        container.className = 'notification-container';
        document.body.appendChild(container);
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = content;
    
    // Add close button
    const closeButton = document.createElement('button');
    closeButton.className = 'notification-close';
    closeButton.innerHTML = '&times;';
    closeButton.addEventListener('click', () => {
        container.removeChild(notification);
    });
    notification.appendChild(closeButton);
    
    // Add to container
    container.appendChild(notification);
    
    // Auto-remove after duration
    if (duration) {
        setTimeout(() => {
            if (notification.parentNode === container) {
                container.removeChild(notification);
            }
        }, duration);
    }
}

// Export functions for use in other modules
export {
    prizeDocumentation,
    initializePrizeDocumentation,
    displayPrizeNotification,
    showPrizesHelpModal
};
