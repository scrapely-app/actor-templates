describe('first tests suite', () => {
    it('visit Crawlee main page', () => {
        cy.visit('/');
        cy.log('Visiting Crawlee main page');
        cy.title().should('include', 'Crawlee');
        cy.contains('h1', 'Build reliable web scrapers. Fast.').should('be.visible');
    });
});
