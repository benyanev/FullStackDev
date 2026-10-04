/**
 * E2E Test — Responsive design (optional requirement 3b).
 *
 * Opens the public pages at an iPhone-sized viewport and checks that nothing
 * is wider than the screen (no sideways scrolling), that the hamburger menu
 * replaces the button row on phones, and that desktop keeps the button row.
 */

const PHONE = [375, 812];
const DESKTOP = [1280, 800];

describe('Responsive layout', () => {
  const pages = ['/', '/users', '/login', '/signup', '/reset-request'];

  pages.forEach((path) => {
    it(`fits a phone screen without horizontal scrolling: ${path}`, () => {
      // Arrange
      cy.viewport(...PHONE);

      // Act
      cy.visit(path);

      // Assert
      cy.document().then((doc) => {
        const { scrollWidth, clientWidth } = doc.documentElement;
        expect(scrollWidth).to.be.at.most(clientWidth);
      });
    });
  });

  it('fits a phone screen on a user profile page', () => {
    // Arrange — open the first user's profile
    cy.viewport(...PHONE);
    cy.request('/api/users?_limit=1').then(({ body }) => {
      // Act
      cy.visit(`/profile/${body[0].id}`);
      cy.contains('followers').should('be.visible');

      // Assert
      cy.document().its('documentElement.scrollWidth').should('be.at.most', PHONE[0]);
    });
  });

  it('shows the admin dashboard as cards with visible buttons on phones', () => {
    // Arrange — fake an admin session and data (no real admin account needed)
    cy.viewport(...PHONE);
    cy.intercept('GET', '/api/me', { user: { id: 1, name: 'Admin', role: 'admin' } });
    cy.intercept('GET', '/api/admin/users', []);
    cy.intercept('GET', '/api/admin/reports', [{
      id: 1, post_id: 2, reason: 'Spam spam spam', created_at: new Date().toISOString(),
      post_title: 'A reported post', post_body: '<p>Body</p>',
      author_id: 3, author_name: 'Gary', author_is_banned: 0, reporter_name: 'Dana',
    }]);

    // Act
    cy.visit('/admin');

    // Assert
    cy.contains('button', 'Delete post').should('be.visible');
    cy.contains('button', 'Dismiss').should('be.visible');
    cy.document().its('documentElement.scrollWidth').should('be.at.most', PHONE[0]);
  });

  it('shows a hamburger menu with the navigation links on phones', () => {
    // Arrange
    cy.viewport(...PHONE);
    cy.visit('/');

    // Act
    cy.get('[aria-label="Open menu"]').should('be.visible').click();

    // Assert
    cy.contains('.MuiDrawer-paper a', 'Users').should('be.visible').click();
    cy.url().should('include', '/users');
  });

  it('keeps the full button row on desktop', () => {
    // Arrange
    cy.viewport(...DESKTOP);

    // Act
    cy.visit('/');

    // Assert
    cy.get('[aria-label="Open menu"]').should('not.be.visible');
    cy.contains('header a', 'Users').should('be.visible');
  });
});
