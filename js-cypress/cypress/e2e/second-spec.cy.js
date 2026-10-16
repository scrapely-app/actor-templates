describe('second tests suite', () => {
    it('visit Crawlee quick start', () => {
        cy.visit('/js');
        cy.log('Visiting Crawlee for JavaScript, clicking on Get started');
        cy.get('a[href="/js/docs/quick-start"]').contains('Get started').first().click();
        cy.log('Asserting quick start redirect');
        cy.url().should('eq', 'https://crawlee.dev/js/docs/quick-start');
        cy.contains('h1', 'Quick Start').should('be.visible');
    });
});
