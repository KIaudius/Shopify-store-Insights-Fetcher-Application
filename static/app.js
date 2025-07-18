// Shopify Store Insights Fetcher - Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('scrapeForm');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const includeCompetitors = document.getElementById('includeCompetitors');
    const competitorOptions = document.getElementById('competitorOptions');
    const competitorsTab = document.getElementById('competitors-tab');

    // Toggle competitor options
    includeCompetitors.addEventListener('change', function() {
        if (this.checked) {
            competitorOptions.style.display = 'block';
        } else {
            competitorOptions.style.display = 'none';
        }
    });

    // Form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const storeUrl = document.getElementById('storeUrl').value;
        const includeCompetitorAnalysis = document.getElementById('includeCompetitors').checked;
        const maxCompetitors = parseInt(document.getElementById('maxCompetitors').value);

        // Show loading
        loading.style.display = 'block';
        results.style.display = 'none';
        
        try {
            const response = await fetch('/api/scrape', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    website_url: storeUrl,
                    include_competitor_analysis: includeCompetitorAnalysis,
                    max_competitors: maxCompetitors
                })
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Failed to analyze store');
            }

            // Hide loading and show results
            loading.style.display = 'none';
            results.style.display = 'block';
            
            // Display results
            displayResults(data);
            
            // Show competitors tab if analysis was included
            if (data.competitor_analysis) {
                competitorsTab.style.display = 'block';
            }
            
        } catch (error) {
            loading.style.display = 'none';
            showError(error.message);
        }
    });

    function displayResults(data) {
        const insights = data.data;
        
        // Overview Tab
        displayOverview(insights, data.processing_time);
        
        // Products Tab
        displayProducts(insights);
        
        // Policies Tab
        displayPolicies(insights);
        
        // Contact & Social Tab
        displayContactAndSocial(insights);
        
        // Competitors Tab (if available)
        if (data.competitor_analysis) {
            displayCompetitors(data.competitor_analysis);
        }
    }

    function displayOverview(insights, processingTime) {
        const content = document.getElementById('overviewContent');
        
        const brandContext = insights.brand_context || {};
        
        content.innerHTML = `
            <div class="insight-card">
                <h4><i class="fas fa-store"></i> Store Information</h4>
                <div class="row">
                    <div class="col-md-6">
                        <p><strong>Store Name:</strong> ${insights.store_name || 'N/A'}</p>
                        <p><strong>Store URL:</strong> <a href="${insights.store_url}" target="_blank">${insights.store_url}</a></p>
                        <p><strong>Total Products:</strong> ${insights.total_products}</p>
                        <p><strong>Hero Products:</strong> ${insights.hero_products.length}</p>
                    </div>
                    <div class="col-md-6">
                        <p><strong>Processing Time:</strong> ${processingTime}s</p>
                        <p><strong>Scraped At:</strong> ${new Date(insights.scraped_at).toLocaleString()}</p>
                        <p><strong>Founded:</strong> ${brandContext.founded_year || 'N/A'}</p>
                        <p><strong>Headquarters:</strong> ${brandContext.headquarters || 'N/A'}</p>
                    </div>
                </div>
            </div>
            
            ${brandContext.brand_description ? `
            <div class="insight-card">
                <h4><i class="fas fa-info-circle"></i> Brand Description</h4>
                <p>${brandContext.brand_description}</p>
            </div>
            ` : ''}
            
            ${brandContext.about_us ? `
            <div class="insight-card">
                <h4><i class="fas fa-users"></i> About Us</h4>
                <p>${brandContext.about_us}</p>
            </div>
            ` : ''}
            
            ${brandContext.mission_statement ? `
            <div class="insight-card">
                <h4><i class="fas fa-bullseye"></i> Mission Statement</h4>
                <p>${brandContext.mission_statement}</p>
            </div>
            ` : ''}
            
            <div class="insight-card">
                <h4><i class="fas fa-chart-bar"></i> Quick Stats</h4>
                <div class="row text-center">
                    <div class="col-md-3">
                        <h3 class="text-primary">${insights.total_products}</h3>
                        <p>Total Products</p>
                    </div>
                    <div class="col-md-3">
                        <h3 class="text-success">${insights.hero_products.length}</h3>
                        <p>Hero Products</p>
                    </div>
                    <div class="col-md-3">
                        <h3 class="text-info">${insights.faqs.length}</h3>
                        <p>FAQs</p>
                    </div>
                    <div class="col-md-3">
                        <h3 class="text-warning">${insights.social_handles.length}</h3>
                        <p>Social Handles</p>
                    </div>
                </div>
            </div>
        `;
    }

    function displayProducts(insights) {
        const content = document.getElementById('productsContent');
        
        let html = `
            <div class="insight-card">
                <h4><i class="fas fa-star"></i> Hero Products (${insights.hero_products.length})</h4>
                <div class="product-grid">
        `;
        
        insights.hero_products.forEach(product => {
            const image = product.images.length > 0 ? product.images[0] : 'https://via.placeholder.com/250x150?text=No+Image';
            html += `
                <div class="product-card">
                    <img src="${image}" alt="${product.title}" class="product-image" onerror="this.src='https://via.placeholder.com/250x150?text=No+Image'">
                    <h6>${product.title}</h6>
                    <p class="text-muted">${product.vendor || 'Unknown Vendor'}</p>
                    <p><strong>$${product.price || 'N/A'}</strong></p>
                    ${product.url ? `<a href="${product.url}" target="_blank" class="btn btn-sm btn-outline-primary">View Product</a>` : ''}
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
            
            <div class="insight-card">
                <h4><i class="fas fa-boxes"></i> Product Catalog Summary</h4>
                <p><strong>Total Products:</strong> ${insights.total_products}</p>
                <p><strong>Available Products:</strong> ${insights.product_catalog.filter(p => p.available).length}</p>
                
                <h5>Top Product Types:</h5>
                <div class="row">
        `;
        
        // Get top product types
        const productTypes = {};
        insights.product_catalog.forEach(product => {
            const type = product.product_type || 'Uncategorized';
            productTypes[type] = (productTypes[type] || 0) + 1;
        });
        
        const topTypes = Object.entries(productTypes)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 6);
        
        topTypes.forEach(([type, count]) => {
            html += `
                <div class="col-md-4">
                    <div class="d-flex justify-content-between">
                        <span>${type}</span>
                        <span class="badge bg-primary">${count}</span>
                    </div>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
        
        content.innerHTML = html;
    }

    function displayPolicies(insights) {
        const content = document.getElementById('policiesContent');
        
        const policies = [
            { key: 'privacy_policy', title: 'Privacy Policy', icon: 'fas fa-shield-alt' },
            { key: 'return_policy', title: 'Return Policy', icon: 'fas fa-undo' },
            { key: 'refund_policy', title: 'Refund Policy', icon: 'fas fa-money-bill-wave' },
            { key: 'shipping_policy', title: 'Shipping Policy', icon: 'fas fa-shipping-fast' },
            { key: 'terms_of_service', title: 'Terms of Service', icon: 'fas fa-file-contract' }
        ];
        
        let html = '';
        
        policies.forEach(policy => {
            const policyData = insights[policy.key];
            if (policyData) {
                html += `
                    <div class="insight-card">
                        <h4><i class="${policy.icon}"></i> ${policy.title}</h4>
                        <p>${policyData.content.substring(0, 300)}${policyData.content.length > 300 ? '...' : ''}</p>
                        ${policyData.url ? `<a href="${policyData.url}" target="_blank" class="btn btn-sm btn-outline-primary">View Full Policy</a>` : ''}
                    </div>
                `;
            }
        });
        
        // FAQs
        if (insights.faqs.length > 0) {
            html += `
                <div class="insight-card">
                    <h4><i class="fas fa-question-circle"></i> Frequently Asked Questions (${insights.faqs.length})</h4>
                    <div class="accordion" id="faqAccordion">
            `;
            
            insights.faqs.forEach((faq, index) => {
                html += `
                    <div class="accordion-item">
                        <h2 class="accordion-header" id="faq${index}">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" 
                                    data-bs-target="#collapse${index}" aria-expanded="false">
                                ${faq.question}
                            </button>
                        </h2>
                        <div id="collapse${index}" class="accordion-collapse collapse" 
                             data-bs-parent="#faqAccordion">
                            <div class="accordion-body">
                                ${faq.answer}
                            </div>
                        </div>
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        }
        
        if (!html) {
            html = '<div class="insight-card"><p>No policy information found.</p></div>';
        }
        
        content.innerHTML = html;
    }

    function displayContactAndSocial(insights) {
        const content = document.getElementById('contactContent');
        
        let html = '';
        
        // Contact Information
        if (insights.contact_info) {
            const contact = insights.contact_info;
            html += `
                <div class="insight-card">
                    <h4><i class="fas fa-address-book"></i> Contact Information</h4>
                    <div class="row">
                        <div class="col-md-6">
                            ${contact.email ? `<p><i class="fas fa-envelope"></i> <strong>Email:</strong> <a href="mailto:${contact.email}">${contact.email}</a></p>` : ''}
                            ${contact.phone ? `<p><i class="fas fa-phone"></i> <strong>Phone:</strong> <a href="tel:${contact.phone}">${contact.phone}</a></p>` : ''}
                        </div>
                        <div class="col-md-6">
                            ${contact.address ? `<p><i class="fas fa-map-marker-alt"></i> <strong>Address:</strong> ${contact.address}</p>` : ''}
                            ${contact.support_hours ? `<p><i class="fas fa-clock"></i> <strong>Support Hours:</strong> ${contact.support_hours}</p>` : ''}
                        </div>
                    </div>
                </div>
            `;
        }
        
        // Social Handles
        if (insights.social_handles.length > 0) {
            html += `
                <div class="insight-card">
                    <h4><i class="fas fa-share-alt"></i> Social Media Handles</h4>
                    <div class="row">
            `;
            
            insights.social_handles.forEach(social => {
                const icon = getSocialIcon(social.platform);
                html += `
                    <div class="col-md-4 mb-3">
                        <div class="d-flex align-items-center">
                            <i class="${icon} me-2"></i>
                            <div>
                                <strong>${social.platform}</strong><br>
                                <a href="${social.url}" target="_blank">${social.handle || social.url}</a>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        }
        
        // Important Links
        if (insights.important_links.length > 0) {
            html += `
                <div class="insight-card">
                    <h4><i class="fas fa-link"></i> Important Links</h4>
                    <div class="row">
            `;
            
            insights.important_links.forEach(link => {
                html += `
                    <div class="col-md-6 mb-2">
                        <a href="${link.url}" target="_blank" class="btn btn-outline-primary btn-sm">
                            <i class="fas fa-external-link-alt"></i> ${link.title}
                        </a>
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        }
        
        if (!html) {
            html = '<div class="insight-card"><p>No contact or social information found.</p></div>';
        }
        
        content.innerHTML = html;
    }

    function displayCompetitors(competitorAnalysis) {
        const content = document.getElementById('competitorsContent');
        
        let html = `
            <div class="insight-card">
                <h4><i class="fas fa-chart-line"></i> Competitive Analysis</h4>
                <p>${competitorAnalysis.analysis_summary}</p>
            </div>
            
            <div class="insight-card">
                <h4><i class="fas fa-trophy"></i> Competitive Advantages</h4>
                <ul>
        `;
        
        competitorAnalysis.competitive_advantages.forEach(advantage => {
            html += `<li>${advantage}</li>`;
        });
        
        html += `
                </ul>
            </div>
            
            <div class="insight-card">
                <h4><i class="fas fa-lightbulb"></i> Market Insights</h4>
                <ul>
        `;
        
        competitorAnalysis.market_insights.forEach(insight => {
            html += `<li>${insight}</li>`;
        });
        
        html += `
                </ul>
            </div>
            
            <div class="insight-card">
                <h4><i class="fas fa-users"></i> Competitors Found (${competitorAnalysis.competitors.length})</h4>
                <div class="row">
        `;
        
        competitorAnalysis.competitors.forEach(competitor => {
            html += `
                <div class="col-md-4 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <h6 class="card-title">${competitor.store_name || 'Unknown Store'}</h6>
                            <p class="card-text">
                                <small class="text-muted">${competitor.store_url}</small><br>
                                Products: ${competitor.total_products}<br>
                                Social Handles: ${competitor.social_handles.length}
                            </p>
                            <a href="${competitor.store_url}" target="_blank" class="btn btn-sm btn-outline-primary">
                                Visit Store
                            </a>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
        
        content.innerHTML = html;
    }

    function getSocialIcon(platform) {
        const icons = {
            'instagram': 'fab fa-instagram',
            'facebook': 'fab fa-facebook',
            'twitter': 'fab fa-twitter',
            'tiktok': 'fab fa-tiktok',
            'youtube': 'fab fa-youtube',
            'linkedin': 'fab fa-linkedin',
            'pinterest': 'fab fa-pinterest'
        };
        
        const platformLower = platform.toLowerCase();
        return icons[platformLower] || 'fas fa-link';
    }

    function showError(message) {
        const results = document.getElementById('results');
        results.innerHTML = `
            <div class="error-alert">
                <h4><i class="fas fa-exclamation-triangle"></i> Error</h4>
                <p>${message}</p>
            </div>
        `;
        results.style.display = 'block';
    }
});
